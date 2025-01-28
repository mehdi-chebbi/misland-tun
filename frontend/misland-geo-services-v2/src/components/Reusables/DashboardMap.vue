<template>
  <div id="map">
    <!-- show opacity control -->
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
      <div class="custom-tool" @click.stop="downloadTiffFile">
        <img src="~assets/svg/map_tools/download.svg">
        <q-tooltip>
          Download tiff file
        </q-tooltip>
      </div>
      <!-- info  -->
      <div class="custom-tool q-my-sm">
        <img src="~assets/svg/map_tools/info.svg">
        <q-tooltip>
          Click to read more about the project
        </q-tooltip>
      </div>
      <!-- custom polygon -->
      <!-- <div class="custom-tool" @click.stop="toggleDrawTool">
        <img src="~assets/svg/map_tools/custom_draw.svg">
        <q-tooltip>
          Toggle custom draw tool
        </q-tooltip>
      </div> -->
    </div>
    <!-- show base layer control -->
    <div class="q-pa-none">
      <BaseLayerSelection :base_maps="baseMaps" @change_base_layer_event="changeBaseMap($event)" />
    </div>
    <!-- show map logos -->
    <div class="q-pa-none gt-xs">
      <MapLogos />
    </div>
    <!-- layer selection -->
    <div class="dashboard-layer-selection" v-show="this.raster_layers.length">
      <div class="" v-for="(layer, index) in raster_layers" :key="index">
        <q-radio v-model="current_raster" :val="layer" :label="layer?.options?.meta?.indicator?.label"
          @update:model-value="showSelectedLayer(index)" />
      </div>
    </div>
  </div>
</template>
<script>

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
const { getAnalysisResults, getResetResultsStatus } = storeToRefs(useAnalysisResultsStore()); // computation years store
const { getIndicatorSelections } = storeToRefs(useIndicatorSelectionStore()); // selected indicator getter
const { getChartData, getDashboardChartData } = storeToRefs(useChartDataStore()); // chart data indicator getter
const { setCustomGeometryData } = useGeometryStore();

export default {
  data() {
    return {
      baseMaps: null,
      selected_base_map: null,
      map: null,
      center: [1.754628, 20.533204],
      current_raster: null, // holds top raster
      custom_geojson: null, // holds custom polygon after draw
      current_geojson: null, //holds the  selected geometry
      legend: null, //holds the map legend
      tiff_url: "", //holds the cuurent tiff url
      raster_layers: [], // holds array of layers
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
    //get dashboard data
    getDashboardChartData() {
      return getDashboardChartData.value
    },
    getResetResultsStatus() {
      return getResetResultsStatus.value
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
    getDashboardChartData: {
      deep: true,
      immediate: true,
      handler(val) {
        if (val.length) return this.createLegend(val[val.length - 1])
      }
    },
    //
    getResetResultsStatus: {
      deep: true,
      immediate: true,
      handler(val) {
        if(process.env.DEV) console.log("reset result status ======= ", val);
        if (val) {
          if (this.legend) this.map.removeControl(this.legend);
          for (let index = this.raster_layers.length; index--;) {
            let layer = this.raster_layers[index]
            this.map.removeLayer(layer)
            this.raster_layers.splice(index, 1)
          }
        }
      }
    },
    //
  },
  mounted() {
    this.createmap();
    this.showSelectedRegionGeometry()
  },
  methods: {
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
        zoom: 3.5,
        zoomAnimation: false, fadeAnimation: true,
        // layers: [darkMap, osm, mapbox, mapboxSatellite]
        layers: [mapboxSatellite]
      });
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
        // custom
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
      const val = this.getGeometryData
      if (!val) return;
      //check if there is a raster layer and not scheduled results, remove the layer
      if (this.current_raster) {
        if (!this.getRouteParams) this.map.removeLayer(this.current_raster);
      };
      // remove the current geometry rendered
      if (this.current_geojson) this.map.removeLayer(this.current_geojson);
      //if the  geometry is a custom drawn area, remove it too
      if (this.custom_geojson) this.map.removeLayer(this.custom_geojson);
      // draw and fit the new geometry data
      this.current_geojson = L.geoJSON(val.geojson, {
        color: "#76acd9",
        fillColor: "transparent",
        opacity: 1,
      });
      this.current_geojson.addTo(this.map);
      this.map.fitBounds(this.current_geojson.getBounds(), {
        // padding: [50, 50],
      });
    },
    // process analyis layer results whether its wms or tiff
    async processLayerResult(results) {
      try {
        this.tiff_url = results.rasterfile;
        const tiles_url = results?.tiles?.url;
        if (this.current_raster) this.map.removeLayer(this.current_raster); // remove current layer if present
        if (tiles_url) {
          this.renderWMSLayer(results);
        }
        else {
          let response = await fetch(results.rasterfile);
          const arrayBuffer = await response.arrayBuffer();
          this.renderTiffFile(arrayBuffer, results);
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
        meta: results
      });
      this.current_raster.addTo(this.map);
      this.current_raster.bringToFront(); //ensure the layer is top most
      //check if layer has been
      const layer_index = this.raster_layers.findIndex(layer => {
        return layer.options.meta.indicator.value === this.current_raster.options.meta.indicator.value
      })
      if (layer_index != -1) {
       const layer =  this.raster_layers[layer_index]
       this.map.removeLayer(layer)
        this.raster_layers.splice(layer_index, 1)
      }
      this.raster_layers.push(this.current_raster)
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
    async renderTiffFile(arrayBuffer, results) {
      try {
        if (process.env.DEV) console.log("render tiff file ************* ", getIndicatorSelections.value);
        let georaster = await parse_georaster(arrayBuffer);
        let layer = await renderGeoraster({
          georaster,
          chart_data: this.getChartData || getIndicatorSelections.value,
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
    // build the year for  legend display
    getYear({ start_year, end_year }) {
      if (start_year && end_year && start_year < end_year ) return ` ${start_year} to ${end_year}`;
      if (start_year == end_year ) return ` ${start_year}`;
      if (start_year && !end_year) return ` ${start_year}`;
      if (!start_year && end_year) return ` ${end_year}`;
      return "";
    },
    //create map legend
    createLegend(results) {
      try {
        if (process.env.DEV) console.log("create legend stat_results ", results);
        let chart_data = results?.chart_data;
        if (this.legend) this.map.removeControl(this.legend);
        this.legend = L.control({ position: "bottomright" });
        this.legend.onAdd = () => {
          const div = L.DomUtil.create("div", "oss_legend");
          div.innerHTML += "<h4>" + results?.indicator?.label +
            " " + this.getYear({ start_year: results.start_year, end_year: results?.end_year }) + "</h4>";
          chart_data.labels.forEach((label, index) => {
            div.innerHTML += `<i style="background: ${chart_data.backgroundColor[index]}; text-align:center "></i><span>${label}</span><br>`;
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
        if (!this.current_raster) return;
        Loading.show({
          spinner: QSpinnerGears,
          message: "Downloading  Tiff ...",
        });
        const meta = this.current_raster?.options?.meta
        console.log("download tiff file dashboard === ", meta);
        const raster_url = meta?.rasterfile;
        const start_year = meta?.base;
        const end_year = meta?.target;
        let response = await this.$api.get(raster_url, {
          responseType: "arraybuffer",
        });
        let blob = new Blob([response.data]);
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement("a");
        a.href = url;
        a.download = `${meta?.indicator?.label} ${this.getYear({ start_year, end_year })}.tiff`;
        document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
        a.click();
        a.remove(); //afterwards we remove the element again
        Loading.hide();
      } catch (error) {
        if (process.env.DEV) console.log("Error in download tiff", error);
        negative({
          message: 'Could not download tiff file',
          position: 'center'
        })
      }
    },
    //
    showSelectedLayer(index) {
      if (!this.map.hasLayer(this.raster_layers[index])) this.raster_layers[index].addTo(this.map);
      this.current_raster = this.raster_layers[index]
      this.current_raster.bringToFront();
      const indicator_value = this.raster_layers[index].options?.meta?.indicator?.value;
      const results = this.getDashboardChartData.find(data => data.indicator.value === indicator_value);
      this.createLegend(results)
    }

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

//
.dashboard-layer-selection {
  min-width: 100px;
  background-color: white;
  min-height: 20px;
  position: absolute;
  left: 20px;
  bottom: 90px;
  z-index: 401;
  border-radius: 10px;
  padding: 10px;
}
</style>
