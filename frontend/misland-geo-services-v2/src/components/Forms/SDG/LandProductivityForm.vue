<template>
  <form @submit.prevent="submit">
    <!-------------------------------- indicator selection ------------------------------->
    <div class="q-my-sm">
      <div class="label q-py-sm">PRODUCTIVITY INDICATOR</div>
      <q-select hide-dropdown-icon outlined dense v-model="indicator" class="q-mx-xs" behavior="menu"
        :options="indicators" @update:model-value="handleIndicatorSelection">
        <template v-slot:append>
          <q-icon name="keyboard_arrow_down" color="grey-6" />
        </template>
      </q-select>
    </div>
    <!-------------------------------- data source selection ------------------------------->
    <div class="q-my-sm">
      <div class="label q-py-sm">SELECT DATA SOURCE</div>
      <q-select hide-dropdown-icon outlined dense v-model="data_source" class="q-mx-xs" behavior="menu"
        :options="data_sources" @update:model-value="handleDataSourceSelection">

        <template v-slot:append>
          <q-icon name="keyboard_arrow_down" color="grey-6" />
        </template>
      </q-select>
    </div>
    <!-------------------------------- advanced selection trigger ------------------------------->
    <div class="flex items-center" @click="show_advance_selections = !show_advance_selections;"
      v-if="data_source.value != 'Modis'">
      <div class="q-pa-xs">Advanced Parameters</div>
      <q-icon name="settings" color="orange" size="20px" />
    </div>

    <!-------------------------------------------------------- advanced selections section ------------------------------------------------>
    <div class="" v-if="show_advance_selections">
      <!-------------------------------- data source selection ------------------------------->
      <div class="">
        <div class="label q-py-xs">SELECT VEGETATION INDEX</div>
        <q-select hide-dropdown-icon outlined dense v-model="veg_index" class="q-mx-xs" behavior="menu"
          :options="vegetationIndices">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
    </div>
    <!-------------------------------- reporting period selection ------------------------------->
    <div class="q-my-sm">
      <div class="label q-py-sm">REPORTING PERIOD</div>
      <q-select hide-dropdown-icon outlined dense v-model="end_year" class="q-mx-xs" behavior="menu"
        popup-content-class="computation-year-selection" :options="years"
        @update:model-value="handleDataSourceSelection">

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
      years: [], // holds computation years
      indicator: { label: "State", value: "state", colors }, // default indicator
      cached: false, // controls if cached results are shown
      veg_index: "NDVI",
      eco_unit: "2000",
      data_source: { label: "Modis", value: "Modis" },
      start_year: 2000,
      end_year: "",
      data_sources: [
        { label: "Modis", value: "Modis" },
        // { label: "Landsat", value: "landsat" }
        { label: "Landsat", value: "Landsat 7" }
      ],
      show_advance_selections: false, //toggles show advanced selections

    }
  },
  computed: {
    // indicator options
    indicators() {
      return [
        { label: "State", value: "state", colors },
        { label: "Trajectory", value: "trajectory", colors },
        { label: "Performance", value: "performance", colors },
        { label: "Land productivity", value: "productivity", colors }
      ]
    },
    //render if has ecological units
    hasEcoUnit() {
      const eco_units = ["performance", "productivity"];
      return eco_units.includes(this.indicator?.value);
    },
    //
    vegetationIndices() {
      if (this.data_source?.value === "modis") return ["NDVI"];
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
    this.fetchYears()
  },
  methods: {
    //handle selected indicator
    handleQueuedResults(val) {
      const results = val.result;
      this.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      this.start_year = val.args.start_year;
      this.end_year = val.args.end_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    //
    async handleIndicatorSelection(indicator) {
      const { value } = indicator;
      let computation_type = ""
      if (value === 'state') computation_type = 'Productivity State';
      if (value === 'trajectory') computation_type = 'Productivity Trajectory';
      if (value === 'performance') computation_type = 'Productivity Performance';
      if (value === 'productivity') computation_type = 'Productivity';
      this.years = await fetchComputationYears(computation_type)
    },
    handleDataSourceSelection() { },
    // fetch computation years
    async fetchYears() {
      this.years = await fetchComputationYears("Productivity State")
    },
    // submit restults for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached,
          raster_type: 1,
          show_change: 1,
          transform: "area",
          reference_eco_units: 49,
          reference_raster: 12,
          veg_index: this.veg_index,
          raster_type: 3,
          raster_source: this.data_source?.value,
          computation_type: this.indicator.computation_type,
        }
        setIndicatorSelections({
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached, // controls if results
        })
        setIndicatorNotes(this.indicator.value)
        // make analysis request
        const uri = `/api/${this.indicator.value}/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'lulc' });// request analysis
        this.handleAnalysisResults(results);
        console.log("aaaaaa",results)
      } catch (error) {
        if (process.env.DEV) console.log("error requesting analysis ", error);
      }
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        setIndicatorNotes(this.indicator.value)
        let chart_data = undefined;
        chart_data = chartData.changeDataProcessor({ results, indicator: this.indicator }); // create chart data for change indicators
        setChartData(chart_data); //store the processed chart data
        this.processStatsSummary()//process summary statistics for LULC change

      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
    // set the summary  according to the sub indicator selected
    processStatsSummary() {

      let summary_html = "";
      const indicator = this.indicator.value
      // summary for state
      if (indicator === 'state') {
        summary_html = this.$t("summaries.state", [
          getRenderedCustomGeometryData.value?.label,
          this.start_year,
          this.end_year,
          getPercentage(getStatValue({ label: "'Potential Degradation", change_type: 2 })),
          getPercentage(getStatValue({ label: "Potential Improvement", change_type: 1 })),
          getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
        ]);
      }
      // summary for trajectory
      if (indicator === 'trajectory') {
        summary_html = this.$t("summaries.trajectory", [
          getRenderedCustomGeometryData.value?.label,
          this.start_year,
          this.end_year,
          getPercentage(getStatValue({ label: "'Potential Degradation", change_type: 2 })),
          getPercentage(getStatValue({ label: "Potential Improvement", change_type: 1 })),
          getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
        ]);
      }
      // summary for performance
      if (indicator === 'performance') {
        summary_html = this.$t("summaries.performance", [
          getRenderedCustomGeometryData.value?.label,
          this.start_year,
          this.end_year,
          getPercentage(getStatValue({ label: "'Degradation", change_type: 2 })),
          getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
          getPercentage(getStatValue({ label: "Improvement", change_type: 1 })),
        ]);
      }
      // summary for performance
      if (indicator === 'productivity') {
        summary_html = this.$t("summaries.land_productivity", [
          getRenderedCustomGeometryData.value?.name,
          this.start_year,
          this.end_year,
          getPercentage(getStatValue({ label: "'Degradation", change_type: 2 })),
          getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
          getPercentage(getStatValue({ label: "Improvement", change_type: 1 })),
        ]);
      }


      //store the summary to store
      setDataSummary(summary_html)
    },
  }
}
</script>

<style lang="scss" scoped></style>
