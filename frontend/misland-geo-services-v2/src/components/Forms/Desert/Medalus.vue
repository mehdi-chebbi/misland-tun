<template>
  <div class="q-pa-sm">
    <form @submit.prevent="submit">
      <!---------------------------------------- select data source ---------------------------------------->
      <div class="q-my-sm">
        <div class="text-uppercase q-ma-xs">SELECT QUALITY INDEX</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.indicator" class="q-mx-xs" behavior="menu"
          :options="qualityIndices">
          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!---------------------------------------- select reporting period ---------------------------------------->
      <div class="q-my-sm">
        <div class="text-uppercase q-ml-xs">REPORTING PERIOD</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.start_year" class="q-mx-xs" behavior="menu"
          :options="form_data.years">

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
    color: "green",
    change_type: 1
  },
  {
    color: "#f4f1da",
    change_type: 2
  },
  {
    color: "red",
    change_type: 3
  },

];
const esai_colors = [
  {
    color: "#F20015",
    change_type: 1
  },
  {
    color: "#FA6FEC",
    change_type: 2
  },
  {
    color: "#FEE300",
    change_type: 3
  },
  {
    color: "#D6FFA1",
    change_type: 4
  },
  {
    color: "#30C700",
    change_type: 5
  },
  {
    color: "#0E7A02",
    change_type: 6
  },
  {
    color: "#01F7F6",
    change_type: 7
  },
  {
    color: "#0178A3",
    change_type: 8
  },

]
export default {
  data() {
    return {
      form_data: {
        start_year: "", // holds selected start year
        years: [], // holds the published years
        // default indicator
        indicator: {
          label: "Climate",
          value: "climatequality",
          colors: colors,
          computation_type: "Climate Quality Index"
        },
        cached: false, // controls type of results to be received
      },
      chart_data: "", // holds chart data results
    }
  },
  computed: {
    qualityIndices() {
      return [
        {
          label: "Climate",
          value: "climatequality",
          colors: colors,
          computation_type: "Climate Quality Index"
        },
        {
          label: "Vegetation",
          value: "vegetationquality",
          colors: colors,
          computation_type: "Vegetation Quality Index"
        },
        {
          label: "Soil",
          value: "soilquality",
          colors: colors,
          computation_type: "Soil Quality Index"
        },
        {
          label: "Management",
          value: "managementquality",
          colors: colors,
          computation_type: "Management Quality Index"
        },
        {
          label: "Environmental Sensitive Areas",
          value: "esai",
          colors: esai_colors,
          computation_type: "ESAI"
        },

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
    this.fetchYears()
  },
  methods: {
    //handle selected indicator
    handleQueuedResults(val) {
      const results = val.result;
      this.form_data.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      this.form_data.start_year = val.args.start_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    // fetch computation years
    async fetchYears() {
      this.form_data.years = await fetchComputationYears("Climate Quality Index")
    },
    async submit() {
      try {
        let payload = {
          start_year: this.form_data.start_year,
          end_year: this.form_data.start_year,
          cached: this.form_data.cached,
          raster_type: 1,
          computation_type: this.form_data.indicator.computation_type,
        };
        // set the indicators to store
        setIndicatorSelections({
          ...this.form_data
        })
        setIndicatorNotes(this.form_data.indicator.value); //set notes to show  to store
        const uri = `/api/${this.form_data.indicator.value}/`// build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'medalus' });// request analysis
        this.handleAnalysisResults(results);
      } catch (error) {
        if (process.env.DEV) console.log("error making request ", error);
      }
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        setIndicatorNotes('medalus')
        const chart_data = chartData.changeDataProcessor({ results, indicator: this.form_data.indicator }); // create chart data from results
        setChartData(chart_data); //store the processed chart data
        this.processStatSummary()//process summary statistics

      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
    // set the summary note according to the sub indicator selected
    processStatSummary() {
      const indicator = `summaries.${this.form_data.indicator.value}`
      const summary_html = this.$t(indicator, [
        getRenderedCustomGeometryData.value?.name,
        this.form_data.start_year,
        getPercentage(getStatValue({ change_type: 3 })),
        getPercentage(getStatValue({ change_type: 1 })),
        getPercentage(getStatValue({ change_type: 2 })),

      ]);
      //store the summary to store
      setDataSummary(summary_html)
    }
  },
}
</script>

<style lang="scss"></style>
