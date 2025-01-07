<template>
  <div>
    <form @submit.prevent="submit">
      <div class="q-my-sm">
        <!-------------------------------- indicator selection ------------------------------->
        <div class="label q-py-sm">LANDCOVER ANALYSIS OPTIONS</div>
        <q-select hide-dropdown-icon outlined dense v-model="indicator" class="q-mx-xs" behavior="menu"
          :options="indicators">
          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!--------------------------------- select data sources --------------------------------->
      <div class="q-my-sm">
        <div class="label">Select Data Source</div>
        <q-select hide-dropdown-icon outlined dense v-model="data_source" behavior="menu" class="q-mx-xs"
          :options="data_sources">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!---------------------------------baseline reporting years --------------------------------->
      <div class="q-my-sm flex justify-between">
        <!-- baseline year -->
        <div class="" style="flex:1">
          <q-select hide-dropdown-icon outlined dense popup-content-class="computation-year-selection" behavior="menu"
            v-model="start_year" class="q-mx-xs" :options="years">

            <template v-slot:append>
              <q-icon name="keyboard_arrow_down" color="grey-6" />
            </template>
          </q-select>
        </div>
        <!-- reporting year -->
        <div class="" v-show="showTwoYears" style="flex:1">
          <q-select hide-dropdown-icon outlined dense popup-content-class="computation-year-selection" behavior="menu"
            class="q-mx-xs" v-model="end_year" :options="years">

            <template v-slot:append>
              <q-icon name="keyboard_arrow_down" color="grey-6" />
            </template>
          </q-select>
        </div>

      </div>
      <!--------------------------------- action buttons --------------------------------->
      <div class="flex items-center justify-between q-mt-md full-width">
        <div class="">
          <q-checkbox v-model="cached" dense left-label label="Cached" />
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
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected geometry data from the store store
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
      // holds the selected indicator defaulted to land cover
      indicator: {
        label: "Land Cover",
        value: "landcover",
      },
      data_source: { label: "ESA CCI-LC", value: "Modis" }, // default data source
      start_year: "2015", //holds the start year defaulted to 2015
      end_year: "", // holds the end year
      years: [], // holds the years pulled from the backend
      cached: false, // controls if results
      data_sources: [{ label: "ESA CCI-LC", value: "Modis" }], //data sources
    }
  },
  computed: {
    indicators() {
      return [
        {
          label: "Land Cover",
          value: "landcover",
        },
        {
          label: "Land Cover Change",
          value: "land_cover_change",
          colors: colors,
        },
      ]
    },
    // controls if baseline and reporting years are shown
    showTwoYears() {
      return this.indicator?.value === "land_cover_change";
    },
    // get queued results from the store
    getQueuedResults() {
      return getQueuedResults.value
    }

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
    this.fetchYears()

  },
  methods: {
    // fetch computation years
    async fetchYears() {
      this.years = await fetchComputationYears("LULC")
    },
    //handle selected indicator either lulc or lulc change
    handleQueuedResults(val) {
      const results = val.result;
      this.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    // submit restults for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached,
          raster_type: 1,
          show_change: this.showTwoYears ? 1 : 0,
          computation_type: this.indicator.computation_type,
        }
        setIndicatorSelections({
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached, // controls if results
        })
        // make analysis request
        const uri = `/api/lulc/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'lulc' });// request analysis
        this.handleAnalysisResults(results);

      } catch (error) {
        console.log("error requesting analysis ", error);
      }
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        setIndicatorNotes(this.indicator.value)
        let chart_data = undefined;
        if (this.showTwoYears) chart_data = chartData.changeDataProcessor({ results, indicator: this.indicator }); // create chart data for change indicators
        if (!this.showTwoYears) chart_data = chartData.dataProcessor({ results, indicator: this.indicator }); // create chart data from results
        setChartData(chart_data); //store the processed chart data
        if (this.showTwoYears) this.processLULCChangeStatsSummary()//process summary statistics for LULC change
        if (!this.showTwoYears) this.processLULCStatsSummary()//process summary statistics for LULC
      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
    // set the summary note according to the sub indicator selected
    processLULCStatsSummary() {
      const summary_html = this.$t("summaries.landcover", [
        this.start_year,
        getRenderedCustomGeometryData.value?.label,
        getPercentage(getStatValue({ label: "Forest", val: 7 })),
        getPercentage(getStatValue({ label: "Grassland", val: 6 })),
        getPercentage(getStatValue({ label: "Wetland", val: 5 })),
        getPercentage(getStatValue({ label: "Bareland", val: 4 })),
        getPercentage(getStatValue({ label: "Artificial", val: 3 })),
        getPercentage(getStatValue({ label: "Cropland", val: 2 })),
        getPercentage(getStatValue({ label: "Water", val: 1 })),
      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
    // set the summary  according to the sub indicator selected
    processLULCChangeStatsSummary() {

      const summary_html = this.$t("summaries.land_Cover_Change", [
      getRenderedCustomGeometryData.value?.label,
        this.start_year,
        getPercentage(getStatValue({ label: "'Degradation", change_type: 2 })),
        getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
        getPercentage(getStatValue({ label: "Improvement", change_type: 1 })),

      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
  }
}
</script>

<style lang="">

</style>
