<template>
  <div>
    <form @submit.prevent="submit">
      <div class="q-my-sm">
        <!-------------------------------- indicator selection ------------------------------->
        <div class="label q-py-sm">SELECT DATA SOURCE</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.data_source" class="q-mx-xs" behavior="menu"
          :options="dataSources">
          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!-------------------------------- advanced selection trigger ------------------------------->
      <div class="flex items-center" @click="form_data.show_advance_selections = !form_data.show_advance_selections;"
        v-if="form_data.data_source.value != 'Modis'">
        <div class="q-pa-xs">Advanced Parameters</div>
        <q-icon :name="form_data.show_advance_selections ? 'cancel' : 'settings'" color="orange" size="20px" />
      </div>
      <!------------------------------------------ show advanced selections ------------------------------------------>
      <div class="" v-if="form_data.show_advance_selections">
        <div class="label q-py-xs">SELECT VEGETATION INDEX</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.veg_index" class="q-mx-xs" behavior="menu"
          :options="vegetationIndices">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!--------------------------------start year  --------------------------------->
      <div class="q-my-sm">
        <div class="label">REPORTING PERIOD</div>
        <q-select hide-dropdown-icon outlined dense popup-content-class="computation-year-selection" behavior="menu"
          v-model="form_data.start_year" class="q-mx-xs" :options="form_data.years">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>

      <!--------------------------------- action buttons --------------------------------->
      <div class="flex items-center justify-between q-mt-md full-width">
        <div class="">
          <q-checkbox v-model="form_data.cached" dense left-label label="Cached" />
        </div>
        <div class="">
          <q-btn unelevated dense class="indicator-selction-form-btn" type="submit" no-caps>Submit</q-btn>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { requestAnalysis } from 'src/Services/requests'
import chartData from 'src/Services/chartData'
import { getPercentage, getStatValue } from 'src/Services/summaryData'
//pinia
import { storeToRefs } from "pinia";
import { useComputationYearsStore } from "src/stores/computation_year_store"; // computation years store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // user indicator selection store
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
const { fetchComputationYears } = useComputationYearsStore(); // action to fetch computation years
const { setIndicatorSelections, setIndicatorNotes } = useIndicatorSelectionStore(); // action to set user form selections to the store
const { setChartData, setDataSummary } = useChartDataStore() //action to set chart data to the store
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected gemotry data from the store store
const { getQueuedResults } = storeToRefs(useAnalysisResultsStore()); // get chart data from store
const colors = [
  {
    "color": "#f4f1da",
    "change_type": 0,
  },
  {
    "color": "green",
    "change_type": 1,
  },
  {
    "color": "red",
    "change_type": 2,
  },

];
export default {
  data() {
    return {
      form_data: {
        // holds the selected indicator defaulted to land cover
        indicator: {
          label: "Vegetation Gain and Loss",
          value: "vegetation_loss_gain",
          colors
        },
        data_source: { label: "Modis", value: "Modis" }, // default data source
        start_year: 2001, //holds the start year defaulted to 2001
        end_year: "", // holds the end year
        years: [], // holds the years pulled from the backend
        cached: false, // controls if results
        veg_index: "NDVI", // vegetation index defaulted to NDVI
        show_advance_selections: false, //toggles show advanced selections
      }
    }
  },
  computed: {
    //
    dataSources() {
      return [
        { label: "Modis", value: "Modis" },
        { label: "Landsat", value: "Landsat 7" }
      ]
    },
    // return the vegetation indices options
    vegetationIndices() {
      return ["MSAVI", "SAVI", "NDVI"];
    },
    // controls if baseline and reporting years are shown
    showTwoYears() {
      return this.indicator?.value === "land_cover_change";
    },
    // get queued results from the store
    getQueuedResults() {
      return getQueuedResults.value
    },
  },
  watch: {
    //handle queued results
    getQueuedResults: {
      immediate: true,
      deep: true,
      handler(val) {
        if (!val) return;
        this.handleQueuedResults(val)
      }
    },
  },
  mounted() {
    //get computation years
    this.fetchYears();
  },
  methods: {
    //handle selected indicator
    handleQueuedResults(val) {
      const results = val.result;
      this.form_data.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      this.form_data.start_year = val.args.start_year;
      this.form_data.end_year = val.args.end_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    // fetch computation years
    async fetchYears() {
      this.form_data.years = await fetchComputationYears("Productivity State")
    },
    // submit selections for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.form_data.start_year,
          end_year: this.form_data.start_year,
          cached: this.form_data.cached,
          raster_type: 1,
          veg_index: this.form_data.veg_index,
          raster_source: this.form_data.data_source?.value,
        };
        // set the indicators to store
        setIndicatorSelections({
          ...this.form_data
        })
        setIndicatorNotes(this.form_data.indicator.value)
        // make analysis request
        const uri = `/api/state/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'veg loss gain' });// request analysis
        this.handleAnalysisResults(results);
      } catch (error) {
        console.log("error requesting analysis ", error);
      }
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        setIndicatorNotes(this.form_data.indicator.value)
        let chart_data = chartData.changeDataProcessor({ results, indicator: this.form_data.indicator }); // create chart data for change indicators
        setChartData(chart_data); //store the processed chart data
        this.processLULCChangeStatsSummary()//process summary statistics for LULC change

      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },

    // set the summary  according to the sub indicator selected
    processLULCChangeStatsSummary() {
      const summary_html = this.$t("summaries.vegetation_loss_gain", [
        getRenderedCustomGeometryData.value?.label,
        this.start_year,

        getPercentage(getStatValue({ label: "'Potential Degradation", change_type: 2 })),
        getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
        getPercentage(getStatValue({ label: "Potential Improvement", change_type: 1 })),

      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
  }
}
</script>

<style lang="">

</style>
