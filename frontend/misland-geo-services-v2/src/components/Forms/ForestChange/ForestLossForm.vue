<template>
  <div class="q-pa-sm">
    <form @submit.prevent="submit">
      <!---------------------------------------- select data source ---------------------------------------->
      <div class="q-my-sm">
        <div class="text-uppercase q-ml-xs">Select Data Source</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.raster_source" class="q-mx-xs" behavior="menu"
          :options="rasterSources">
          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!---------------------------------------- select  year  ---------------------------------------->
      <div class="q-my-sm">
        <div class="text-uppercase q-ml-xs">Select Year</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.end_year" class="q-mx-xs" behavior="menu"
          :options="form_data.years" popup-content-class="year-selection-popup">

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
    "color": "red",
    "change_type": 2,
  },
]
export default {
  data() {
    return {
      form_data: {
        indicator: {
          label: "Forest Loss",
          value: "forest_loss",
          colors
        },
        years: [], // published years
        start_year: 2000, // default start year
        end_year: "", // holds selected end year
        raster_source: { label: "Hansen", value: "Hansen" }, // default raster source
        cached: false, // controls of results returned are cached or new
      },
      //
      chart_data: "", // holds the chart data results
    }
  },
  computed: {
    // raster sources
    rasterSources() {
      return [{ label: "Hansen", value: "Hansen" }]
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
      this.form_data.end_year = val.args.end_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    // fetch computation years
    async fetchYears() {
      this.form_data.years = await fetchComputationYears("Forest Change")
    },
    //make the request
    async submit() {
      try {
        let payload = {
          start_year: this.form_data.start_year,
          end_year: this.form_data.end_year,
          cached: this.form_data.cached,
          raster_type: 6,
          raster_source: "Hansen",
        };
        // set the indicators to store
        setIndicatorSelections({
          ...this.form_data
        })
        setIndicatorNotes(this.form_data.indicator.value); //set notes to show  to store
        const uri = `/api/forestchange/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'veg loss gain' });// request analysis
        this.handleAnalysisResults(results)
      } catch (error) {
        console.log("error requesting analysis ", error);
      }
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        setIndicatorNotes(this.form_data.indicator.value)
        this.chart_data = this.processChartData(results) // create chart data for change indicators
        setChartData(this.chart_data); //store the processed chart data
        this.processForestLossStatSummary();

      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
    // set the summary  according to the sub indicator selected
    processForestLossStatSummary() {
      const forest_loss_value = this.chart_data.values[0]; //
      const total_area = this.chart_data.total_area;
      const percentage = Math.floor(100 * forest_loss_value / total_area)

      const summary_html = this.$t("summaries.forest_loss", [
        this.form_data.end_year,
        forest_loss_value,
        getRenderedCustomGeometryData.value?.label,
        `<strong >${percentage} % </strong>`,
        this.form_data.start_year,
        this.form_data.end_year,
      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
    // process stat results here since forest loss data needs to be handled differently
    processChartData(results) {
      const handsen_stats = results?.stats?.stats[0]?.stats;
      let stat_year = handsen_stats.find(stat => {
        return stat.key === (this.form_data.end_year - this.form_data.start_year)
      })
      if (!stat_year) stat_year = { key: 0, value: 0 }
      //
      const datasets = [];
      const label = results.label || "forest loss";
      const data = handsen_stats.map(stat => stat.value);
      const borderColor = results.borderColor || "red";
      //
      datasets.push({
        label,
        data,
        borderColor,
        fill: false,
      });
      //
      const line_labels = handsen_stats.map(stat => `${stat.key + results.base}`);
      const total_area = handsen_stats.reduce((a, b) => a + +b.value, 0);
      const others = total_area - stat_year?.value
      const labels = ["Forest Loss"];
      const backgroundColor = ["red", "blue"]
      return {
        backgroundColor: 'red',
        labels: ['loss'],
        values: [stat_year?.value, others],
        raster_colors: [{ val: stat_year.key, color: "red", label: "loss" }],
        start_year: results.base,
        end_year: results.target,
        total_area,
        //  line data stuff
        indicator: 'forest_loss',
        datasets, line_labels, labels, backgroundColor, start_year: results.base,
        end_year: results.target,

      }

    }
  }
}
</script>

<style lang="">

</style>
