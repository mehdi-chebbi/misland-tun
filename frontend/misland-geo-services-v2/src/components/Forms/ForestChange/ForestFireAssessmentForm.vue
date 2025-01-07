<template>
  <div class="q-pa-sm">
    <form @submit.prevent="submit">
      <!---------------------------------------- pre fire date range ---------------------------------------->
      <div class="">
        <div class="q-ml-xs">PRE-FIRE DATE RANGE</div>
        <div class="flex no-wrap">
          <div class="q-pa-xs">
            <div class="text-grey q-ml-xs">Start-Date</div>
            <input type="date" class="full-width" v-model="form_data.forest_fire.prefire_start"
              @focus="$event => $event.target.showPicker()" style="width: 100px" />
          </div>
          <div class="q-pa-xs">
            <div class="text-grey q-ml-xs">End-Date</div>
            <input type="date" class="full-width" v-model="form_data.forest_fire.prefire_end"
              @focus="$event => $event.target.showPicker()" style="width: 100px"
              :min="form_data.forest_fire.prefire_start" />
          </div>
        </div>
      </div>
      <!---------------------------------------- post fire date range ---------------------------------------->
      <div class="q-my-sm">
        <div class="q-ml-xs">POST FIRE DATE RANGE</div>
        <div class="flex no-wrap">
          <div class="q-pa-xs">
            <div class="text-grey q-ml-xs">Start-Date</div>
            <input type="date" class="full-width" v-model="form_data.forest_fire.postfire_start"
              :min="form_data.forest_fire.prefire_end" @focus="$event => $event.target.showPicker()"
              style="width: 100px" />
          </div>
          <div class="q-pa-xs">
            <div class="text-grey q-ml-xs">End-Date</div>
            <input type="date" class="full-width" v-model="form_data.forest_fire.postfire_end"
              @focus="$event => $event.target.showPicker()" :min="form_data.forest_fire.postfire_start"
              style="width: 100px" />
          </div>
        </div>
      </div>
      <!---------------------------------------- select  year  ---------------------------------------->
      <div class="q-my-sm">
        <div class="text-uppercase q-ml-xs">SELECT DATA SOURCE</div>
        <q-select hide-dropdown-icon outlined dense v-model="form_data.forest_fire.raster_source" class="q-mx-xs"
          behavior="menu" :options="rasterSources" popup-content-class="year-selection-popup">
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
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
const { fetchComputationYears } = useComputationYearsStore(); // action to fetch computation years
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
const getStatValue = (class_name, stats) => {
  return stats.find((stat) => stat.class === class_name) || ""
}


export default {
  data() {
    return {
      form_data: {
        forest_fire: {
          postfire_end: "",
          postfire_start: "",
          prefire_end: "",
          prefire_start: "",
          raster_source: { label: "Landsat", value: "Landsat 8" },
        },
        indicator: {
          label: "Forest Fire", value: "forest_fire",
          colors
        },
        cached: true,
      },
      chart_data: "", // holds the chart data results
    }
  },
  computed: {
    rasterSources() {
      return [
        { label: "Sentinel 2", value: "Sentinel 2" },
        { label: "Landsat", value: "Landsat 8" },
      ]
    }
  },
  methods: {
    async submit() {
      try {
        let payload = {
          postfire_end: this.form_data.forest_fire.postfire_end,
          postfire_start: this.form_data.forest_fire.postfire_start,
          prefire_end: this.form_data.forest_fire.prefire_end,
          prefire_start: this.form_data.forest_fire.prefire_start,
          raster_source: this.form_data.forest_fire.raster_source.value,
          raster_type: 1,
          show_change: 1,
          cached: this.form_data.cached,

        }
        // set the indicators to store
        setIndicatorSelections({
          ...this.form_data
        })
        setIndicatorNotes(this.form_data.indicator.value); //set notes to show  to store
        const uri = `/api/forestfire/`; // build the request url
        const results = await requestAnalysis({ uri, payload, caller: 'Forest Fire Assessment' });// request analysis
        if (!results) return;
        // dummy the data here below
        // const results =  this.dummyResults()
        this.chart_data = this.processChartData(results) // create chart data for change indicatorssetChartData(chart_data); //store the processed chart data
        setChartData(this.chart_data); //store the processed chart data
        this.processStatSummary(results);
        setAnalysisResults(""); // reset analysis data
        setAnalysisResults(results); // set the resuts to store
      } catch (error) {
        if (process.env.DEV) console.log("error requesting analysis ", error);
      }
    },
    //process  results
    processChartData(results) {
      let stats = results.stats
      if (process.env.DEV) console.log("forestfirestats ", stats)
      const keys = [
        { color: "#768833", value: "Enhanced Regrowth", api_name: "Enhanced Regrowth, Low" },
        { color: "#0ce244", value: "Unburned", api_name: "Unburned" },
        { color: "#f5fe0c", value: "Low Severity", api_name: "Low Severity" },
        { color: "#fa671a", value: "Moderate Severity", api_name: "Moderate-high Severity" },
        { color: "#a500d2", value: "High Severity", api_name: "High Severity" },
      ]
      const validStats = stats.filter(({ class: val1 }) => keys.some(({ api_name: val2 }) => val1 === val2)) //filter stats to get only ones we need
      if (process.env.DEV) console.log("validStats ", validStats)
      let backgroundColor = []
      let labels = []
      let values = []
      keys.forEach(key => {
        backgroundColor.push(key.color)
        labels.push(key.value)
      })
      validStats.reverse().forEach(stat => {
        values.push(stat.hectares)
      });
      // get raster colors
      const raster_colors = stats.map((stat, i) => {
        return { val: stat.change_type, color: backgroundColor[i], label: labels[i] }
      });
      if (process.env.DEV) console.log("results ", { backgroundColor, labels, values, indicator: 'forest_fire' });
      return { backgroundColor, labels, values, raster_colors, indicator: 'forest_fire' }
    },
    // create summary
    processStatSummary(results) {
      const stats = results.stats;
      const indicator = `summaries.${this.form_data.indicator.value}`
      const summary_html = this.$t(indicator, [
        this.form_data.forest_fire.prefire_start,
        this.form_data.forest_fire.postfire_end,
        getRenderedCustomGeometryData.value?.name || "custom",
        getStatValue("Enhanced Regrowth, Low", stats)?.hectares,
        getStatValue("Enhanced Regrowth, Low", stats)?.percentage + '%',

        getStatValue("Unburned", stats)?.hectares,
        getStatValue("Unburned", stats)?.percentage + '%',

        getStatValue("Low Severity", stats)?.hectares,
        getStatValue("Low Severity", stats)?.percentage + '%',

        getStatValue("Moderate-low Severity", stats)?.hectares,
        getStatValue("Moderate-low Severity", stats)?.percentage + '%',

        getStatValue("High Severity", stats)?.hectares,
        getStatValue("High Severity", stats)?.percentage + '%',

      ]);
      //store the summary to store
      setDataSummary(summary_html)
    },

    // dummy data
    dummyResults() {
      const data = {
        "prefire_start": "2022-12-05",
        "prefire_end": "2022-12-17",
        "postfire_start": "2023-01-12",
        "rasterfile": "http://misland.oss-online.org:1337/media/forestfire20230125074614136284.tif",
        "nodata": null,
        "stats": [
          {
            "class": "NA",
            "pixels": 0,
            "hectares": 0,
            "percentage": 0
          },
          {
            "class": "High Severity",
            "pixels": 0,
            "hectares": 0,
            "percentage": 0
          },
          {
            "class": "Moderate-high Severity",
            "pixels": 32,
            "hectares": 2.88,
            "percentage": 0.13
          },
          {
            "class": "Moderate-low Severity",
            "pixels": 101,
            "hectares": 9.09,
            "percentage": 0.4
          },
          {
            "class": "Low Severity",
            "pixels": 1233,
            "hectares": 110.97,
            "percentage": 4.87
          },
          {
            "class": "Unburned",
            "pixels": 10024,
            "hectares": 902.16,
            "percentage": 39.63
          },
          {
            "class": "Enhanced Regrowth, Low",
            "pixels": 9080,
            "hectares": 817.2,
            "percentage": 35.89
          },
          {
            "class": "Enhanced Regrowth, High",
            "pixels": 4827,
            "hectares": 434.43,
            "percentage": 19.08
          }
        ]
      };
      return data
    }
  }
}
</script>
<style lang="">

</style>
