<template>
  <q-page>
    <NavBar />
    <!-- show map -->
    <div class="">
      <Map />
    </div>
    <!-- show search -->
    <div class="q-pa-none search-region">
      <div class="flex" style="gap:0px 10px">
        <Search />
        <q-btn icon="filter_list" class="filter-region-btn"
          @click="show_region_selection_filter = !show_region_selection_filter"></q-btn>
      </div>
      <!-- region filter selection -->
      <div class="region-selection-filter" v-show="show_region_selection_filter">
        <RegionSelection @close_region_selection_filter="show_region_selection_filter = false" />
      </div>
    </div>
    <!-- show stats button    -->
    <div class="statistics-button" v-show="getChartData && active_component === 'indicator-selections'">
      <StatisticsButton :statistics_data="getChartData" @show_statistics_component="active_component = 'statistics'" />
    </div>
    <!---------------------- show indicator selections----------------------------->
    <div class="analysis-container">
      <!--------------- show the indicator selection---------------->
      <IndicatorSelection :active_indicator_selection="active_indicator_selection"
        v-show="active_component === 'indicator-selections'" />
      <!------------- show chart, summary and notes-------------->
      <div class="flex">
        <div class="flex">
          <IndicatorsCondensed @emit_selected_form="expandFormItems" v-show="active_component === 'statistics'" />
        </div>
        <div class="" style="flex:1">
          <ChartArea v-show="active_component === 'statistics'"
            @show_indicator_selections="active_component = 'indicator-selections'" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import indicator_svg from 'src/assets/svg/indicators/map.svg'
import { defineAsyncComponent } from "vue";
//pinia
import { storeToRefs } from "pinia";
import { useGeometryStore } from "src/stores/geometry_store";
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
const { getChartData } = storeToRefs(useChartDataStore()); // get chart data from store
const { setQueuedResults } = useAnalysisResultsStore()
const { setGeometryData, setCustomGeometryData } = useGeometryStore();
export default {
  data() {
    return {
      active_component: "indicator-selections", // statistics or selection-forms
      indicator_svg,
      active_indicator_selection: null,
      show_region_selection_filter: false
    };
  },
  computed: {
    //
    getChartData() {
      return getChartData.value
    },
    getRouteParams() {
      return this.$route.params
    },

  },
  components: {
    Search: defineAsyncComponent(() => import('src/components/GeoService/Search.vue')),
    RegionSelection: defineAsyncComponent(() => import('src/components/GeoService/RegionSelection.vue')),
    StatisticsButton: defineAsyncComponent(() => import('src/components/GeoService/StatisticsButton.vue')),
    Map: defineAsyncComponent(() => import('src/components/Reusables/Map.vue')),
    IndicatorSelection: defineAsyncComponent(() => import('src/components/Reusables/IndicatorSelection.vue')),
    IndicatorsCondensed: defineAsyncComponent(() => import('src/components/Reusables/IndicatorsCondensed.vue')),
    NavBar: defineAsyncComponent(() => import("src/components/NavBar.vue")),
    // charts
    ChartArea: defineAsyncComponent(() => import('src/components/Reusables/Chart.vue')),
  },
  watch: {
    getChartData: {
      handler(val) {
        if (!val) return
        this.active_component = "statistics"
      }
    }
  },
  async mounted() {
    if (this.getRouteParams?.type === "results") return this.fetchQueuedResults(); // fetch queued results if we have results in the route
    await this.fetchContinentalGeometry(); // fetch continental geometry
    this.fetchRegionalVectors(); //  fetch regional vectors
  },
  methods: {
    // fetch continental geometry
    async fetchContinentalGeometry() {
  try {
    // Load the GeoJSON from the raw GitHub URL
    const rawGeoJsonUrl = "https://raw.githubusercontent.com/mehdi-chebbi/geojson-WAP/main/custom.geo%20(2).json";
    const vector_response = await this.$api.get(rawGeoJsonUrl); // Replace this.$api with fetch if necessary
    console.log("vector response", vector_response.data);

    const name = vector_response.data?.features?.[0]?.properties?.name || "Unknown"; // Adjust the path to match GeoJSON properties

    // Set geometry data
    setGeometryData({
      geojson: vector_response.data,
      admin_level: -2,
      name: name,
      vector: null // Set to null if no id is needed
    });
  } catch (error) {
    if (process.env.DEV) {
      console.log("Error fetching GeoJSON:", error);
    } else {
      console.error("An error occurred while fetching GeoJSON.");
    }
  }
}
  ,
    // fetch regional vectors
    async fetchRegionalVectors() {
      try {
        const vector_response = await this.$api.get('/api/vectregional/');
        console.log("regional vector response ", vector_response.data);

      } catch (error) {
        if (process.env.DEV) console.log("error fetching regional vectors  ", error);
      }
    },
    // swap stats and form
    expandFormItems(expansion_item) {
      this.active_indicator_selection = expansion_item
      this.active_component = "indicator-selections"
    },
    // handle queued results
    async fetchQueuedResults() {
      try {
        if (!this.$route.params.id) return;
        const id = this.$route.params.id;
        const token = localStorage.getItem("auth_token");
        const response = await this.$api.get("/api/tasks/" + id, {
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        });
        const geometry_data =  response?.data?.args?.user_selections?.geometry_data;
        if (process.env.DEV) console.log("queued results response ", response.data);
        // if (process.env.DEV) console.log("queued results response geometry_data ", geometry_data);
        setQueuedResults(response.data)
        setGeometryData(geometry_data)
      } catch (error) {
        if (process.env.DEV) console.log("error fetching regional vectors  ", error);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
// search input style
.search-region {
  z-index: 500;
  position: absolute;
  left: 0;
  margin: 10px 20px;
}

.filter-region-btn {
  width: 38px;
  // height: 38px;
  border-radius: 11px;
  background: #FFF;
  box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.12);

  @media (min-width: $breakpoint-md-min) {}

  @media (max-width: $breakpoint-sm-max) {}
}

.region-selection-filter {
  position: relative;

  @media (min-width: $breakpoint-md-min) {
    margin-left: 70px;
    margin-top: 10px;
  }

  @media (max-width: $breakpoint-sm-max) {}
}

.statistics-button {
  z-index: 500;
  position: absolute;
  left: 380px;
  background-color: white;
  padding: 5px 20px;
  border-radius: 10px;
  margin: 10px 0px 0px 0px
}

// indicator section container class
.analysis-container {
  z-index: 500;
  position: absolute;

  @media (min-width: $breakpoint-sm-min) {
    margin: 80px 0px 0px 20px;
    max-width: 500px;
  }

  @media (max-width: $breakpoint-xs-max) {
    margin: 80px 0px 0px 0px;
    width: 100%;
  }

}
</style>
