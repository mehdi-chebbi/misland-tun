<template>
  <div class="q-pa-sm">
    <form @submit.prevent="submit">
      <!-- normal selections -->
      <div v-if="!show_advance_selections">
        <!---------------------------------------- select tree cover loss data source ---------------------------------------->
        <div class="q-my-sm">
          <div class="text-uppercase q-ml-xs">TREE COVER LOSS DATA SOURCE</div>
          <q-select hide-dropdown-icon outlined dense v-model="form_data.data_source" class="q-mx-xs" behavior="menu"
            :options="dataSources">
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
        <!-------------------------------- advanced selection trigger ------------------------------->
        <div class="flex items-center" @click="show_advance_selections = true;">
          <div class="q-pa-xs">Advanced Parameters</div>
          <q-icon name="settings" color="orange" class="cursor-pointer" size="20px" />
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

      </div>
      <!-- show advanced parameters -->
      <div v-if="show_advance_selections">
        <div class="flex justify-end">
          <q-icon name="close" size="sm" class="cursor-pointer" @click="show_advance_selections = false" />
        </div>
        <!--------------------------------- minimum forest units --------------------------------->
        <div class="q-my-xs">
          <div class="text-uppercase q-ml-xs">MINIMUM FOREST UNIT (px)</div>
          <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1"
            v-model.number="form_data.mfu" />
        </div>
        <!--------------------------------- tree cover threshold - --------------------------------->
        <div class="q-my-xs">
          <div class="text-uppercase q-ml-xs">TREE COVER THRESHOLD (%)</div>
          <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1" max="100"
            v-model.number="form_data.mfu_forest_threshold" />
        </div>
        <!--------------------------------- forest carbon stock --------------------------------->
        <div class="q-my-xs">
          <div class="text-uppercase q-ml-xs">FOREST CARBON STOCK (tC/ha)</div>
          <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1" max="100"
            v-model.number="form_data.carbon_stock" />
        </div>
        <!--------------------------------- forest carbon stock --------------------------------->
        <div class="q-my-xs">
          <div class="text-uppercase q-ml-xs"> PROPORTION % (tC/ha) EMITTED BY DEGRADATION</div>
          <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1" max="100"
            v-model.number="form_data.degradation_emission_proportion" />
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
export default {
  data() {
    return {
      form_data: {
        years: [],
        end_year: "",
        data_source: {
          label: "Global Forest change Maps",
          value: "global_forest_change_maps"
        },
        mfu: 3,
        mfu_forest_threshold: 30,
        carbon_stock: 0.2522,
        degradation_emission_proportion: 30,
        cached: false, // controls of results returned are cached or new
        indicator: {
          label: "Forest Carbon Emission",
          value: "forest_carbon_emission",
          colors,
        },
      },
      show_advance_selections: false, //toggles show advanced selections
    }
  },
  computed: {
    dataSources() {
      return [
        {
          label: "Global Forest change Maps",
          value: "global_forest_change_maps"
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
    this.fetchYears()
  },
  methods: {
    // fetch computation years
    async fetchYears() {
      this.form_data.years = await fetchComputationYears("Forest Carbon Emission")
    },
    //make the request
    async submit() {
      try {
        let payload = {
          start_year: this.form_data.end_year,
          end_year: this.form_data.end_year,
          cached: this.form_data.cached,
          show_change: 0,
          muf: this.form_data.mfu,
          mfu_forest_threshold: this.form_data.mfu_forest_threshold,
          degradation_emission_proportion: this.form_data.degradation_emission_proportion,
          carbon_stock: this.form_data.carbon_stock,
        };
        // set the indicators to store
        setIndicatorSelections({
          ...this.form_data
        })
        setIndicatorNotes(this.form_data.indicator.value); //set notes to show  to store
        const uri = `/api/carbonemission/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'Forest Carbon' });// request analysis
        this.handleAnalysisResults(results)
      } catch (error) {
        console.log("error requesting analysis ", error);
      }
    },
    // set the summary note according to the sub indicator selected
    processStatSummary() {
      const indicator = `summaries.${this.form_data.indicator.value}`
      const summary_html = this.$t(indicator, [
        this.form_data.start_year,
        getRenderedCustomGeometryData.value?.name,
        getPercentage(getStatValue({ change_type: 3 })),
        getPercentage(getStatValue({ change_type: 2 })),
        getPercentage(getStatValue({ change_type: 1 }))
      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },
    //handle selected indicator either lulc or lulc change
    handleQueuedResults(val) {
      const results = val.result;
      this.form_data.indicator = val.args?.user_selections?.indicator_selections?.indicator;
      this.form_data.start_year = val.args.start_year;
      this.form_data.end_year = val.args.end_year;
      setIndicatorSelections(val.args?.user_selections?.indicator_selections)
      this.handleAnalysisResults(results);
    },
    //handle results from direct response or from queued results
    handleAnalysisResults(results) {
      try {
        setIndicatorNotes(this.form_data?.indicator.value)
        const chart_data = chartData.changeDataProcessor({ results, indicator: this.form_data.indicator }); // create chart data from results
        setChartData(chart_data); //store the processed chart data
        this.processStatSummary()//process summary statistics
      } catch (error) {
        console.log("error processing analysis results", error);
      }
    },
  }
}
</script>

<style lang="">

</style>
