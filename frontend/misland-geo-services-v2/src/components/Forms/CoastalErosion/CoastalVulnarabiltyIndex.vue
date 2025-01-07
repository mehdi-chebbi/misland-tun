<template>
  <div>
    <form @submit.prevent="submit">
      <div class="q-my-sm">
        <!-------------------------------- indicator selection ------------------------------->
        <div class="label q-py-sm">COASTAL EROSION INDICES</div>
        <q-select hide-dropdown-icon outlined dense v-model="indicator" popup-content-class="computation-year-selection"
          behavior="menu" :options="qualityIndices">
          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!--------------------------------- reporting period --------------------------------->
      <div class="q-my-sm">
        <div class="label">REPORTING PERIOD</div>
        <q-select hide-dropdown-icon outlined dense popup-content-class="computation-year-selection" behavior="menu"
          v-model="start_year" :options="years">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
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
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected gemotry data from the store store
const { getQueuedResults } = storeToRefs(useAnalysisResultsStore()); // get chart data from store

const colors = [
  {
    color: "#267300",
    change_type: 1
  },
  {
    color: "#a8a800",
    change_type: 2
  },
  {
    color: "#55ff00",
    change_type: 3
  },
  {
    color: "#ffebaf",
    change_type: 4
  },
  {
    color: "#ff7f7f",
    change_type: 5
  }
];
export default {
  data() {
    return {
      indicator: "", // holds the selected indicator
      start_year: "", //holds the start year
      years: [], // holds the years pulled from the backend
      cached: false, // controls if results
    }
  },
  computed: {
    qualityIndices() {
      return [
        {
          label: "Geomorphology",
          value: "geomorphology",
          colors: colors,
          computation_type: "Geomorphology"
        },
        {
          label: "Coastal Slope",
          value: "coastal_slope",
          colors: colors,
          computation_type: "Coastal Slope"
        },
        {
          label: "Sea-Level Rise ",
          value: "sea_level_rise",
          colors: colors,
          computation_type: "Sea Level Change"
        },
        {
          label: "Shoreline Change",
          value: "shoreline_change",
          colors: colors,
          computation_type: "Shoreline Erosion"
        },
        {
          label: "Mean Tide Range",
          value: "mean_tide_range",
          colors: colors,
          computation_type: "Mean Tide Range"
        },
        {
          label: "Mean Wave Height",
          value: "mean_wave_height",
          colors: colors,
          computation_type: "Mean Wave Height"
        },
        {
          label: "Coastal Vulnerability Index",
          value: "coastal_vulnerability_index",
          colors: colors,
          computation_type: "Coastal Vulnerability Index"
        }
      ]
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
    //handle selected indicator
    handleQueuedResults(val) {
      const results = val.result;
      this.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      this.start_year = val.args.start_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    async fetchYears() {
      this.years = await fetchComputationYears("Coastal Vulnerability Index")
    },
    // submit restults for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.start_year,
          end_year: this.start_year,
          cached: this.cached,
          raster_type: 1,
          computation_type: this.indicator.computation_type,
        }
        setIndicatorSelections({
          indicator: this.indicator,
          start_year: this.start_year,
          cached: this.cached, // controls if results
        })
        setIndicatorNotes(this.indicator.value)
        // make analysis request
        const uri = `/api/cvi/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'coastal_erosion' });// request analysis
        this.handleAnalysisResults(results);

      } catch (error) {
        if (process.env.DEV) console.log("error requesting analysis ", error);
      }
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        console.log("coastal erision results ====== ", results);
        // setIndicatorNotes('medalus')
        const chart_data = chartData.changeDataProcessor({ results, indicator: this.indicator }); // create chart data from results
        setChartData(chart_data); //store the processed chart data
        this.processStatSummary()//process summary statistics

      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
    // set the summary note according to the sub indicator selected
    processStatSummary() {
      const indicator = `summaries.${this.indicator.value}`
      const summary_html = this.$t(indicator, [
        this.start_year,
        getRenderedCustomGeometryData.value?.label,
        getPercentage(getStatValue({ label: "Very High", change_type: 5 })),
        getPercentage(getStatValue({ label: "High", change_type: 4 })),
        getPercentage(getStatValue({ label: "Moderate", change_type: 3 })),
        getPercentage(getStatValue({ label: "Low", change_type: 2 })),
        getPercentage(getStatValue({ label: "Very Low", change_type: 1 }))
      ]);
      //store the summary to store
      setDataSummary(summary_html)
    }
  }
}
</script>

<style lang="">

</style>
