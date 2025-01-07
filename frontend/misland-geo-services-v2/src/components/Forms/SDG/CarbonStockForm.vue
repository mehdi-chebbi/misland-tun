<template>
  <form @submit.prevent="submit">
    <!-------------------------------- data source selection ------------------------------->
    <div class="q-my-sm">
      <div class="label">SELECT DATA SOURCE</div>
      <q-select hide-dropdown-icon outlined dense v-model="data_source" class="q-mx-xs" behavior="menu"
        :options="data_sources">
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
        <div class="label q-py-xs">SOC Reference</div>
        <q-select hide-dropdown-icon outlined dense v-model="soc_ref" class="q-mx-xs" behavior="menu"
          :options="soc_refs">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
    </div>
    <!-------------------------------- reporting period selection ------------------------------->
    <div class="q-my-sm">
      <div class="label ">REPORTING YEAR</div>
      <q-select hide-dropdown-icon outlined dense v-model="end_year" class="q-mx-xs" behavior="menu"
        popup-content-class="computation-year-selection" :options="years">

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
      indicator: { value: "carbon_Stock_Change", label: "Carbon Stock Change", colors },
      cached: false, // controls if cached results are shown
      soc_refs: ["2000", "2001", "2002"],
      options: ["2000", "2001", "2002"],
      eco_unit: "2000",
      data_source: { label: "ESA CCI-LC", value: "modis" },
      start_year: 2000,
      soc_ref: 2000,
      end_year: "",
      data_sources: [{ label: "ESA CCI-LC", value: "modis" }],
      show_advance_selections: false, //toggles show advanced selections

    }
  },
  computed: {

    //render if has ecological units
    hasEcoUnit() {
      const eco_units = ["performance", "productivity"];
      return eco_units.includes(this.indicator?.value);
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
    //handle selected indicator 
    handleQueuedResults(val) {
      const results = val.result;
      this.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      this.start_year = val.args.start_year;
      this.end_year = val.args.end_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    // fetch computation years
    async fetchYears() {
      this.years = await fetchComputationYears("SOC")
    },
    // submit restults for analysis
    async submit() {
      try {
        let payload = {
          start_year: 2000,
          end_year: this.end_year,
          cached: this.cached,
          raster_type: 1,
          reference_soc: 12,
          reference_raster: 12,
          show_change: true,
        }
        setIndicatorSelections({
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached, // controls if results
        })

        // make analysis request
        const uri = `/api/soc/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'carbon_stock_change' });// request analysis
        this.handleAnalysisResults(results);


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
      const summary_html = this.$t("summaries.carbon_Stock_Change", [
      getRenderedCustomGeometryData.value?.label,
        this.start_year,
        this.end_year,
        getPercentage(getStatValue({ label: "'Potential Degradation", change_type: 2 })),
        getPercentage(getStatValue({ label: "Potential Improvement", change_type: 1 })),
        getPercentage(getStatValue({ label: "Stable", change_type: 0 })),
      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
  }
}
</script>

<style lang="scss" scoped></style>
