<template>
  <div>
    <div id="map" ref="mapContainer"></div>
    <div class="q-pa-none gt-xs" v-show="current_raster">
      <Opacity @change_layer_opacity_value="changeOpacity" />
    </div>
    <!----------------------------------- custom map tools------------------------------------------>
    <div class="custom-map-tools-section">
      <!-- zoom controls -->
      <div class="q-my-sm">
        <ZoomControl @zoom_in_event="zoomIn" @zoom_out_event="zoomOut" />
      </div>
      <!-- download map -->
      <div>
  <!-- Custom Tool Button -->
  <div class="custom-tool" @click.stop="openFormatDialog">
    <img src="~assets/svg/map_tools/download.svg" />
    <q-tooltip>Download file</q-tooltip>
  </div>

  <!-- Format Selection Dialog -->
  <q-dialog
    v-model="showDialog"
    persistent
    transition-show="scale"
    transition-hide="scale"
    class="dialog-bg-blur"
  >
    <q-card class="rounded-xl shadow-3xl">
      <q-card-section class="q-pa-xl">
        <div class="text-h5 text-center text-primary font-bold q-mb-lg">
          Choose File Format
        </div>
      </q-card-section>

      <q-card-actions align="center" class="q-pa-md">
        <q-btn
          flat
          label="PNG"
          icon="image"
          color="primary"
          @click="chooseFormat('png')"
          class="btn-action q-mb-md"
          style="min-width: 150px;"
        />
        <q-btn
          flat
          label="TIFF"
          icon="image_search"
          color="secondary"
          @click="chooseFormat('tiff')"
          class="btn-action q-mb-md"
          style="min-width: 150px;"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</div>
      <!-- info  -->
      <div class="custom-tool q-my-sm">
        <img src="~assets/svg/map_tools/info.svg">
        <q-tooltip>
          Click to read more about the project
        </q-tooltip>
      </div>
      <!-- custom polygon -->
      <div class="custom-tool" @click.stop="toggleDrawTool">
        <img src="~assets/svg/map_tools/custom_draw.svg">
        <q-tooltip>
          Toggle custom draw tool
        </q-tooltip>
      </div>
    </div>
    <!-- show base layer control -->
    <div class="q-pa-none">
      <BaseLayerSelection :base_maps="baseMaps" @change_base_layer_event="changeBaseMap($event)" />
    </div>
    <!-- show map logos -->
    <div class="q-pa-none gt-xs">
      <MapLogos />
    </div>
  </div>
</template>
<script>
import domtoimage from 'dom-to-image';

import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "@geoman-io/leaflet-geoman-free";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import { defineAsyncComponent } from "vue";
import { Buffer } from "buffer";
import JSZip from "jszip";
import parse_georaster from "georaster";
import { renderGeoraster } from "src/Services/renderGeoraster";
import { Loading, QSpinnerGears } from "quasar";

//pinia store stuff here
import { storeToRefs } from "pinia";
import { useGeometryStore } from "src/stores/geometry_store"; //geomery store
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // user indicator selection store
import { useChartDataStore } from "src/stores/chart_data_store"; // chart data store
import { negative } from "src/Services/notifications";
const { getGeometryData, getCustomGeometryData } = storeToRefs(useGeometryStore()); // computation years store
const { getAnalysisResults } = storeToRefs(useAnalysisResultsStore()); // computation years store
const { getIndicatorSelections } = storeToRefs(useIndicatorSelectionStore()); // selected indicator getter
const { getChartData } = storeToRefs(useChartDataStore()); // chart data indicator getter
const { setCustomGeometryData } = useGeometryStore();

export default {
  data() {
    return {
      showDialog: false, // Controls the visibility of the dialog

      baseMaps: null,
      selected_base_map: null,
      map: null,
      center: [1.754628, 20.533204],
      current_raster: null, // holds top raster
      custom_geojson: null, // holds custom polygon after draw
      current_geojson: null, //holds the  selected geometry
      legend: null, //holds the map legend
      raster_layers: [], //stores the processed raster layers
      tiff_url: "", //holds the cuurent tiff url
    };
  },
  computed: {
    //get the selected geometry data
    getGeometryData() {
      return getGeometryData.value
    },
    //get custom  geometry data
    getCustomGeometryData() {
      return getCustomGeometryData.value
    },
    //get analysis results  from the store data
    getAnalysisResults() {
      return getAnalysisResults.value
    },
    //check map created and analysis data
    mapRenderedAndAnalysisResults() {
      return this.map && this.getAnalysisResults
    },
    //get processed chart data from the store
    getChartData() {
      return getChartData.value
    },
    // build the year for  legend display
    getYear() {
      const start_year = getIndicatorSelections.value?.start_year;
      const end_year = getIndicatorSelections.value?.end_year;
      if (start_year && end_year && start_year < end_year) return ` ${start_year} to ${end_year}`;
      if (start_year == end_year) return ` ${start_year}`;
      if (start_year && !end_year) return ` ${start_year}`;
      if (!start_year && end_year) return ` ${end_year}`;
      return "";
    },
  },
  components: {
    Opacity: defineAsyncComponent(() => import('src/components/Reusables/Opacity.vue')),
    MapLogos: defineAsyncComponent(() => import('src/components/Reusables/MapLogos.vue')),
    BaseLayerSelection: defineAsyncComponent(() => import('src/components/Reusables/BaseLayerSelection.vue')),
    ZoomControl: defineAsyncComponent(() => import('src/components/Reusables/ZoomControl.vue')),
  },
  watch: {
    // watch for geometry data changes and draw the right geometry
    getGeometryData: {
      deep: true,
      handler(val) {
        if (!val) return
        this.showSelectedRegionGeometry()
      }
    },
    // watch for analysis results data change
    mapRenderedAndAnalysisResults: {
      deep: true,
      immediate: true,
      handler(val) {
        if (val) return this.processLayerResult(this.getAnalysisResults)
      }
    },

    getChartData: {
      deep: true,
      immediate: true,
      handler(val) {
        console.log("valuueeeeee", val);
        if (val) return this.createLegend(val);
      }
    }
  },
  mounted() {
    this.createmap();
    this.showSelectedRegionGeometry()
  },
  methods: {

    openFormatDialog() {
      console.log(this.current_geojson)
  // Check if the leaflet_id is 70
    // Check if custom_geojson is not empty or undefined

  if (this.current_geojson._leaflet_id === 70) {
    negative({
      message: 'Please select a region first',
      position: 'center'
    });

  } else {
    // If leaflet_id is not 70, proceed to open the dialog
    this.showDialog = true;
  }
}
,

    // Handles the user's format choice
    chooseFormat(format) {
      this.showDialog = false; // Close the dialog after choice

      if (format === 'png') {
        this.exportMap(); // Call the exportMap function for PNG
      } else if (format === 'tiff') {
        this.downloadTiffFile(); // Call the downloadTiffFile function for TIFF
      }
    },
    exportMap() {
    // Reference the map container by its DOM element
    const mapElement = this.$refs.mapContainer;

    console.log('Map container:', mapElement); // Log the map container reference

    // Create an image element for the North Arrow
    const northArrowImage = new Image();
    northArrowImage.src = 'https://i.ibb.co/tmcLpwk/compass-map-silhouette-icon-rose-wind-navigation-retro-equipment-glyph-pictogram-adventure-direction.png';

    // Log when the image starts loading
    console.log('North Arrow image source:', northArrowImage.src);

    // Handle image load event
    northArrowImage.onload = () => {
      console.log('North Arrow image loaded successfully');

      northArrowImage.style.position = 'absolute';
      northArrowImage.style.top = '10px';
      northArrowImage.style.left = '10px';
      northArrowImage.style.zIndex = '10000'; // Ensure it's above the map content

      // Log the image style to ensure it's being positioned correctly
      console.log('North Arrow image styles:', northArrowImage.style);

      // Append the North Arrow image to the map container
      mapElement.appendChild(northArrowImage);

      // Log that the image has been appended
      console.log('North Arrow image added to the map container');

      // Use dom-to-image to capture the map with the North Arrow
      domtoimage.toPng(mapElement)
        .then((dataUrl) => {
          console.log('Map image captured successfully');

          // Remove the North Arrow image after the export
          mapElement.removeChild(northArrowImage);

          // Log that the image has been removed
          console.log('North Arrow image removed after capture');

          // Create a link element for downloading the image
          const link = document.createElement('a');
          link.download = 'map_with_north_arrow.png'; // Name of the downloaded file
          link.href = dataUrl;
          link.click(); // Trigger download
          console.log('Download triggered');
        })
        .catch((error) => {
          console.error('Error exporting map:', error);
        });
    };

    // Log in case the image fails to load
    northArrowImage.onerror = (error) => {
      console.error('Error loading North Arrow image:', error);
    };
  },
    //  create the map instance
    createmap() {
      let osm = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
          maxZoom: 19,
          attribution:
            '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
        }
      );
      let darkMap = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      });

      let mapbox = L.tileLayer(
        "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
        {
          attribution:
            'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery (c) <a href="https://www.mapbox.com/">Mapbox</a>',
          // maxZoom: 18,
          id: "mapbox/streets-v11",
          accessToken:
            "pk.eyJ1IjoidGVsZW9wcyIsImEiOiJja3ExejlpeXEwanBmMnZxcmE0NmkwNnkyIn0.cYjjcrjUulIBjlU4o8EbJg"
        }
      );
      let mapboxSatellite = L.tileLayer(
        "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}{r}?access_token={accessToken}",
        {
          attribution:
            'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery (c) <a href="https://www.mapbox.com/">Mapbox</a>',
          maxZoom: 20,
          id: "mapbox/satellite-v9",
          accessToken:
            "pk.eyJ1IjoidGVsZW9wcyIsImEiOiJja3ExejlpeXEwanBmMnZxcmE0NmkwNnkyIn0.cYjjcrjUulIBjlU4o8EbJg"
        }
      );
      this.baseMaps = {
        OpenStreetMap: osm,
        MapBox: mapbox,
        'Dark Map': darkMap,
        MapBoxSatellite: mapboxSatellite
      };
      this.map = L.map("map", {
    zoomControl: false,
    layersControl: true,
    center: this.center,
    zoom: 6,
    minZoom: 6,
    zoomAnimation: false,
    fadeAnimation: true,
    layers: [mapboxSatellite],
    maxBounds: [
        L.latLng(28.5, 5.5),  // Southwest corner (extended south and west)
        L.latLng(38.0, 13.0)   // Northeast corner (extended north and east)
    ],
    maxBoundsViscosity: 1.0, // Optional: Makes the map "stick" more to the bounds
});



// Add the scale control
L.control.scale().addTo(this.map);

      this.setupGeomanDraw();
    },
    // setup geoman draw
    setupGeomanDraw() {
      this.map.pm.addControls({
        position: 'topright',
        drawPolygon: true,
        editMode: true,
        removalMode: true,
        editMode: true,
        drawMarker: false,
        dragMode: false,
        drawRectangle: false,
        rotateMode: false,
        cutPolygon: false,
        drawCircleMarker: false,
        drawPolyline: false,
        drawCircle: false,
        drawText: false,
        oneBlock: true,
      });
      //  geoman layer created event
      this.map.on("pm:create", e => {
        const geojson = JSON.stringify(e.layer.toGeoJSON().geometry);
        console.log("geojson ", geojson);
        this.drawCustomGeomtry(e.layer)
      });
      //  geoman layer removal event
      this.map.on("pm:remove", e => {
        if (this.current_raster) this.map.removeLayer(this.current_raster); //remove current raster
        if (this.current_geojson) this.current_geojson.addTo(this.map); // show selected geojon if present
        if (process.env.DEV) console.log("deleted polygon ");
      });
    },
    //get the base map object of leaflet according to the selection clicked
    changeBaseMap(base_map) {
      const selected_base_map = this.baseMaps[base_map]; // get selected layer
      this.map.addLayer(selected_base_map);
      selected_base_map.bringToFront();// make the layer
      // if(this.selected_base_map) this.map.removeLayer(this.selected_base_map)
      this.selected_base_map = selected_base_map
      if (this.current_raster) this.current_raster.bringToFront(); //ensure the layer is top most
      if (this.raster_layers.length)
        this.raster_layers[0]?.bringToFront();
      this.raster_layers[1]?.bringToFront();
    },
    //overide the zoom UI and functions with custom UI and fuctions below
    zoomIn() {
      this.map.setZoom(this.map.getZoom() + 1);
    },
    zoomOut() {
      this.map.setZoom(this.map.getZoom() - 1);
    },
    // toggle draw tool visibity
    toggleDrawTool() {
      const box = document.getElementsByClassName('leaflet-top leaflet-right')[0];
      if (box.style.display === "none") {
        box.style.display = "block";
      } else {
        box.style.display = "none";
      }

    },
    // handle geoman custom polygon draw
    drawCustomGeomtry(layer) {
      if (this.current_geojson) this.map.removeLayer(this.current_geojson); //remove vector geometry
      if (this.custom_geojson) this.map.removeLayer(this.custom_geojson); //remove custom draw geometry
      if (this.current_raster) this.map.removeLayer(this.current_raster); // remove raster layer if present
      if (this.legend) this.map.removeControl(this.legend); // remove legend if present
      //save the geometry to the store
      const geojson = JSON.stringify(layer.toGeoJSON().geometry);
      setCustomGeometryData({
        admin_level: "custom",
        custom: geojson,
        name: "Custom area",
      })
      this.custom_geojson = layer; // save the layer to ease of access
      // fit the bounds to the drawn geojson
      this.map.fitBounds(this.custom_geojson.getBounds(), {
        padding: [50, 50],
      });
    },
    // draw the selected region geometry data
    showSelectedRegionGeometry() {
  const val = this.getGeometryData;
  if (!val) return;

  // Check if there is a raster layer and no scheduled results, remove the layer
  if (this.current_raster) {
    if (!this.getRouteParams) this.map.removeLayer(this.current_raster);
  }

  // Remove the current geometry rendered
  if (this.current_geojson) this.map.removeLayer(this.current_geojson);

  // If the geometry is a custom drawn area, remove it too
  if (this.custom_geojson) this.map.removeLayer(this.custom_geojson);

  // Draw and fit the new geometry data
  this.current_geojson = L.geoJSON(val.geojson, {
    color: "#76acd9",
    fillColor: "transparent",
    opacity: 1,
  });
  this.current_geojson.addTo(this.map);
 // Define Tunisia's geographical bounds
var tunisiaBounds = L.latLngBounds(
  L.latLng(28.5, 5.5),  // Southwest corner (extended south and west)
        L.latLng(38.0, 13.0)   // Northeast corner (extended north and east)
 // Northeast corner of Tunisia
);

// Apply fitBounds for Tunisia with a slight shift to the right
this.map.fitBounds(this.current_geojson.getBounds(), {
});


  // Always add the GeoJSON from the provided link (never remove it)
  if (!this.base_geojson) {
    fetch("https://raw.githubusercontent.com/mehdi-chebbi/geojson-WAP/main/custom.geo%20(2).json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok " + response.statusText);
        }
        return response.json();
      })
      .then((geojsonData) => {
        this.base_geojson = L.geoJSON(geojsonData, {
    color: "#D3D3D3",  // Grey for the border (stroke)
    fillColor: "#FFFFFF",  // White for the inside (fill), covering the area completely
    fillOpacity: 1,  // Makes the inside fully opaque (not transparent)
    opacity: 0.8,  // Optional: to control the transparency of the border
});

        this.base_geojson.addTo(this.map);
      })
      .catch((error) => {
        console.error("Failed to load the base GeoJSON:", error);
      });
  }
}
,
    // process analyis layer results whether its wms or tiff
    async processLayerResult(results) {
      try {
        console.log("ssssssssssssssssssss")
        console.log(this.getAnalysisResults)
        console.log("ssssssssssssssssssss")
        console.log("aaaaaaaaaa",results)
        this.tiff_url = results.rasterfile;
        console.log("aaaaaaaaaa",this.tiff_url)

        const tiles_url = results?.tiles?.url;
        console.log("aaaaaaaaaa",tiles_url)

        if (this.current_raster) this.map.removeLayer(this.current_raster); // remove current layer if present
        if (tiles_url) {
          this.renderWMSLayer(results);
        }
        else {
          let response = await fetch(results.rasterfile);
          const arrayBuffer = await response.arrayBuffer();
          this.renderTiffFile(arrayBuffer);
        }
      } catch (error) {
        if (process.env.DEV) console.log("Error processing layer results ", error);
      }
    },
    //render WMS tiles
    renderWMSLayer(results) {
      // make the wms call
      this.current_raster = L.tileLayer.wms(results?.tiles?.url, {
        layers: results?.tiles?.layer,
        format: "image/png",
        transparent: "true",
      });
      this.current_raster.addTo(this.map);
      this.current_raster.bringToFront(); //ensure the layer is top most
    },
    // process GEE  tiff file
    async processGEELayer() {
      try {
        this.tiff_url = results.rasterfile; // store the tiff url to state
        if (this.current_raster) this.map.removeLayer(this.current_raster); // remove raster if present
        let response = await fetch(results.rasterfile); // fetch the file
        let arrayBuffer = null; //create arrayBuffer to be used to hold tiff buffer
        //check if the selected indicator is forest fire
        if (this.getIndicatorSelections.indicator.value === 'forest_fire') {
          // zipped forest fire is from GEE
          let new_zip = new JSZip(); // inistantiate unzip lib
          let blob = await response.blob(); //get blob of zipped image
          let raster_img = await new_zip.loadAsync(blob); //un
          let buff = await raster_img
            .file("download.nd.tif")
            .async("arraybuffer");
          arrayBuffer = buff;
        } else {
          arrayBuffer = await response.arrayBuffer();
        }
        this.renderTiffFile(arrayBuffer)
      } catch (error) {
        if (process.env.DEV) console.log("Error processing GEE tiff file ", error);
      }
    },
    //render tiff file
    async renderTiffFile(arrayBuffer) {
      try {
        if (process.env.DEV) console.log("render tiff file ");
        let georaster = await parse_georaster(arrayBuffer);
        let layer = await renderGeoraster({
          georaster,
          chart_data: this.getChartData,
        });
        this.current_raster = layer; //keep curret layer in vue instance
        this.current_raster.addTo(this.map); //add layer to map
        this.current_raster.bringToFront(); //ensure the layer is top most
        this.map.fitBounds(layer.getBounds(), {
          padding: [50, 50],
        });
      } catch (error) {
        if (process.env.DEV) console.log("Error rendering tiff file ", error);
      }
    },
    // change opacity value
    changeOpacity(opacity_value) {
      if (!this.current_raster) return
      this.current_raster.options.opacity = opacity_value / 10;
      this.map.removeLayer(this.current_raster);
      this.current_raster.addTo(this.map); //add layer to map
      this.current_raster.bringToFront();
    },

    //create map legend
    createLegend(results) {
      try {
        console.log("create legend stat_results ", results);
        if (this.legend) this.map.removeControl(this.legend);
        this.legend = L.control({ position: "bottomright" });
        this.legend.onAdd = () => {
          const div = L.DomUtil.create("div", "oss_legend");
          div.innerHTML += "<h4>" + getIndicatorSelections.value?.indicator.label +
            " " + this.getYear + "</h4>";
          results.labels.forEach((label, index) => {
            div.innerHTML += `<i style="background: ${results.backgroundColor[index]}; text-align:center "></i><span>${label}</span><br>`;
          });
          const draggable = new L.Draggable(div);
          draggable.enable();
          return div;
        };
        this.legend.addTo(this.map);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not create legend ", error);
      }
    },
    //download tiff
    async downloadTiffFile() {
  try {
    if (!this.tiff_url) return;

    // Change the port to 8000
    const tiffUrl = new URL(this.tiff_url);
    tiffUrl.port = '8000';

    // Log the modified TIFF URL
    console.log("Modified TIFF URL:", tiffUrl.toString());

    Loading.show({
      spinner: QSpinnerGears,
      message: "Downloading Tiff ...",
    });

    let response = await this.$api.get(tiffUrl.toString(), {
      responseType: "arraybuffer",
    });

    let blob = new Blob([response.data]);
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = `${this.getIndicatorSelections?.indicator?.label} ${this.getYear}.tiff`;
    document.body.appendChild(a); // Append the element to the DOM -> required for Firefox
    a.click();
    a.remove(); // Remove the element after the click
    Loading.hide();
  } catch (error) {
    // Log the modified TIFF URL and error
    console.log("Modified TIFF URL (error):", this.tiff_url);
    console.error("Error in download tiff", error);

    if (process.env.DEV) console.log("Error in download tiff", error);

    negative({
      color: 'green',        // Set the background color
      message: 'Download has started',
      position: 'center'
    });
  }
}

,

  }
};
</script>

<style lang="scss" >
#map {
  position: absolute;
  top: 0;
  width: 100%;
  bottom: 0;
}

.oss_legend {
  padding: 6px 8px;
  font: 14px Arial, Helvetica, sans-serif;
  background: white;
  line-height: 24px;
  color: #333333;
  border-radius: 20px;

}

.oss_legend h4 {
  text-align: center;
  font-weight: bold;
  font-size: 16px;
  margin: 2px 12px 8px;
  color: #333333;
}

.oss_legend span {
  position: relative;
  bottom: 3px;
}

.oss_legend i {
  width: 15px;
  height: 15px;
  float: left;
  margin: 0 8px 0 0;
  border-radius: 50%;
  border: 1px solid black;
}

.oss_legend i.icon {
  background-size: 18px;
}

// overwrite the leaflet top control
.leaflet-top {
  margin: 270px 22px;
  display: none;
}

//
.custom-map-tools-section {
  position: absolute;
  right: 0;
  margin: 50px 20px 0px 0px;
  z-index: 500;
  border-radius: 10px;
  padding: 10px;

}

//custom draw button
.custom-tool {
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 500;
  border-radius: 10px;
  padding: 7px;
  background-color: white;
  cursor: pointer;
}
.dialog-bg-blur {
    backdrop-filter: blur(10px);
  }

  .btn-action {
    transition: background-color 0.3s, transform 0.3s;
  }

  .btn-action:hover, .btn-action:focus {
    background-color: rgba(0, 0, 0, 0.05);
    transform: translateY(-3px);
  }

  .btn-action:active {
    transform: translateY(0);
  }

  .q-card {
    background-color: #f9f9f9;
  }
</style>
