<template>
  <div class="q-pa-sm">
    <form @submit.prevent="submit">
      <!---------------------------------------- select start date ---------------------------------------->
      <div class="q-my-sm">

        <div class="text-uppercase ">Start-Date</div>
        <input type="date" class="full-width" v-model="form_data.start_date"
          @focus="$event => $event.target.showPicker()" style="width: 150px" />
      </div>
      <!---------------------------------------- select end date ---------------------------------------->
      <div class="q-my-sm">
        <div class="text-uppercase ">End-Date</div>
        <input type="date" class="full-width" v-model="form_data.end_date" style="width: 150px"
          :min="form_data.start_date" @focus="$event => $event.target.showPicker()" />
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
import { format, addDays } from 'date-fns'
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
const { getQueuedResults } = storeToRefs(useAnalysisResultsStore()); // get chart data from store
const { setIndicatorSelections, setIndicatorNotes } = useIndicatorSelectionStore(); // action to set user form selections to the store
const { setChartData, setDataSummary } = useChartDataStore() //action to set chart data to the store
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected gemotry data from the store store
//method to set analysis results to the store
const { setAnalysisResults } = useAnalysisResultsStore()
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

export default {
  data() {
    return {
      form_data: {
        start_date: "", //holds  start date
        end_date: "", //holds  end date
        indicator: {
          label: "Forest Fire Risk",
          value: "forest_fire_risk",
          colors
        },
        cached: false,
      },
      chart_data: "", //
    }
  },
  computed: {
    getQueuedResults() {
      return getQueuedResults.value
    }
  },
  mounted() {
    if (this.getQueuedResults) return this.processQueuedResults();
  },
  methods: {
    showPicker(el) {
      el.target.showPicker()
    },
    async submit() {
      try {
        let payload = {
          end_date: this.form_data.end_date,
          start_date: this.form_data.start_date,
          transform: "area",
          cached: this.form_data.cached,

        }
        // set the indicators to store
        setIndicatorSelections({
          ...this.form_data
        })
        setIndicatorNotes(this.form_data.indicator.value); //set notes to show  to store
        const uri = `/api/forestfirerisk/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'Forest Fire Risk' });// request analysis
        console.log("forest fire risk results ", results);
        if (!results) return;
        this.chart_data = this.processChartData(results)
        // const chart_data = chartData.changeDataProcessor({ results, indicator: this.form_data.indicator }); // create chart data from results
        setChartData(this.chart_data); //store the processed chart data
        setAnalysisResults(results); // set the resuts to store

      } catch (error) {
        if (process.env.DEV) console.log("error requesting analysis ", error);
      }
    },
    //process queued results
    processQueuedResults() {
      this.form_data = {
        ...this.form_data,
        ...this.getQueuedResults?.args?.user_selections?.indicator_selections
      };
      // set the indicators to store
      setIndicatorSelections({
        ...this.form_data
      });
      setIndicatorNotes(this.form_data.indicator.value); //set notes to show  to store
      const results = this.getQueuedResults.result
      this.chart_data = this.processChartData(results)
      setChartData(this.chart_data); //store the processed chart data
      setAnalysisResults(results); // set the resuts to store
      this.processStatSummary(results);
    },
    //process  results
    processChartData(results) {
      let stats = results.stats
      if (process.env.DEV) console.log("forest fire risk stats", stats)
      const keys = [
        { color: "#768833", value: "Enhanced Regrowth", api_name: "Enhanced Regrowth, Low" },
        { color: "#0ce244", value: "Unburned", api_name: "Unburned" },
        { color: "#f5fe0c", value: "Low Severity", api_name: "Low Severity" },
        { color: "#fa671a", value: "Moderate Severity", api_name: "Moderate-high Severity" },
        { color: "#a500d2", value: "High Severity", api_name: "High Severity" },
      ]

      let backgroundColor = []
      let labels = []
      let values = []
      stats.forEach((stat, i) => {
        backgroundColor.push("red")
        labels.push(stat.day)
        values.push(stat.count)
      })
      // get raster colors
      const raster_colors = stats.map((stat, i) => {
        return { val: stat.count, color: backgroundColor[i], label: labels[i] }
      });
      if (process.env.DEV) console.log("results ", { backgroundColor, labels, values, indicator: 'forest_fire_risk' });
      return { backgroundColor, labels, values, raster_colors, indicator: 'forest_fire_risk' }
    },
    //process  results
    processChartData(results) {
      let stats = results.stats
      let backgroundColor = []
      let labels = []
      let values = []
      stats.forEach(stat => {
        backgroundColor.push("red")
        labels.push(stat.day),
          values.push(stat.count)
      })
      // get raster colors
      const raster_colors = stats.map((stat, i) => {
        return { val: stat.change_type, color: backgroundColor[i], label: labels[i] }
      });
      if (process.env.DEV) console.log("results ", { backgroundColor, labels, values, indicator: 'forest_fire_risk' });
      return { backgroundColor, labels, values, raster_colors, indicator: 'forest_fire_risk' }
    },
    // create summary
    processStatSummary(results) {
      const stats = results.stats;
      const indicator = `summaries.${this.form_data.indicator.value}`
      const summary_html = this.$t(indicator, [
        getRenderedCustomGeometryData.value?.name,
        this.forestStatsSummaryS(stats),
        this.form_data.start_date,
        this.form_data.end_date,
      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
    // forest fire risk summary status
    forestStatsSummaryS(stats) {
      return stats.reduce((a, c) => a + c.count, 0);
    },
  }
}
</script>

<style lang="">

</style>
