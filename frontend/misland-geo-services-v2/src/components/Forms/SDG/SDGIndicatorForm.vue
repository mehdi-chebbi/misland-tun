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
    <div class="flex items-center" @click="show_advance_selections = !show_advance_selections">
      <div class="q-pa-xs">Advanced Parameters</div>
      <q-icon name="settings" color="orange" size="20px" />
    </div>

    <!-------------------------------------------------------- advanced selections section ------------------------------------------------>
    <div class="" v-if="show_advance_selections">
      <!-------------------------------- vegetation indices selection ------------------------------->
      <div class="">
        <div class="label q-py-xs">SELECT VEGETATION INDEX</div>
        <q-select hide-dropdown-icon outlined dense v-model="veg_index" class="q-mx-xs" behavior="menu"
          :options="vegetationIndices">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!-------------------------------- ecological data source selection ------------------------------->
      <div class="">
        <div class="label q-py-xs">ECOLOGICAL DATA SOURCE</div>
        <q-select hide-dropdown-icon outlined dense v-model="eco_unit" class="q-mx-xs" behavior="menu"
          :options="ecoUnits">

          <template v-slot:append>
            <q-icon name="keyboard_arrow_down" color="grey-6" />
          </template>
        </q-select>
      </div>
      <!-------------------------------- sco ref selection ------------------------------->
      <div class="">
        <div class="label q-py-xs">SOC REFERENCE</div>
        <q-select hide-dropdown-icon outlined dense v-model="soc_ref" class="q-mx-xs" behavior="menu"
          :options="socRefs">

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
      years: [],
      veg_index: "NDVI",
      eco_unit: "2000",
      data_source: { label: "Modis", value: "Modis" },
      cached: false,
      soc_ref: "2000",
      end_year: "",
      start_year: 2001,
      data_sources: [
        { label: "Modis", value: "Modis" },
        { label: "Landsat", value: "Landsat 7" }
      ],
      indicator: { value: "land_degradation", label: "Land Degradation", colors },
      show_advance_selections: false

    }
  },
  computed: {
    vegetationIndices() {
      if (this.data_source?.value === "Modis") return ["NDVI"];
      return ["MSAVI", "SAVI", "NDVI"];
    },
    ecoUnits() {
      return ["2000", "2001", "2002"];
    },
    socRefs() {
      return ["2000", "2001", "2002"]
    },
    //render if has ecological units
    hasEcoUnit() {
      const eco_units = ["performance", "productivity"];
      return eco_units.includes(this.indicator?.value);
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
    // fetch computation years
    async fetchYears() {
      this.years = await fetchComputationYears("Land Degradation")
    },
    // submit restults for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached,
          veg_index: this.veg_index,
          raster_type: 1,
          raster_source: this.data_source?.value,
          show_change: true,
          reference_eco_units: 49,
          reference_raster: 12,
        }
        setIndicatorSelections({
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached, // controls if results
        })
        setIndicatorNotes(this.indicator.value)
        // make analysis request
        const uri = `/api/degradation/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'lulc' });// request analysis
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
        this.processStatsSummary()//process summary statistics

      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
    // set the summary  according to the sub indicator selected
    processStatsSummary() {
      const summary_html = this.$t("summaries.land_degradation", [
        getRenderedCustomGeometryData.value?.label,
        this.start_year,
        this.end_year,
        getPercentage(getStatValue({ label: "Degraded", change_type: 2 })),
        getPercentage(getStatValue({ label: "Not degraded", change_type: 1 })),

      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
  }
}
</script>

<style lang="scss" scoped></style>
