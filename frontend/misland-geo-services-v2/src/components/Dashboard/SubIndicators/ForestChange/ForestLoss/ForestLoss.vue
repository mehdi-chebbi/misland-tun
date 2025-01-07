<template>
  <div class="chart-container q-my-lg">
    <!-- ff -->
    <div v-show="!request_pending">
      <div class="flex justify-between">
        <div class="indicator-chart-title">{{ getRenderedCustomGeometryData?.name }} forest loss </div>
        <!---------------------------------------  chart actions ----------------------------------------->
        <div class="chart-actions flex">
          <!-- download chart data -->
          <div flat class="q-ma-xs cursor-pointer">
            <q-btn flat dense>
              <img src="~assets/png/chart_icons/download.png" @click="downloadCSV">
              <q-tooltip>
                Download CSV
              </q-tooltip>
            </q-btn>
          </div>
          <!-- download chart png image -->
          <div flat class="q-ma-xs cursor-pointer">
            <q-btn flat dense>
              <img src="~assets/png/chart_icons/image.png" @click="downloadChartPng">
              <q-tooltip>
                Download chart image
              </q-tooltip>
            </q-btn>
          </div>
          <!-- link to information -->
          <div flat class="q-ma-xs cursor-pointer">
            <a href="https://misland.readthedocs.io/en/latest/Service/Calculate_SDG.html#landcover-change" target="_blank"
              rel="noopener noreferrer">
              <q-btn flat dense>
                <img src="~assets/png/chart_icons/information.png" alt="">
                <q-tooltip>
                  Click for more information
                </q-tooltip>
              </q-btn>
            </a>
          </div>
          <!-- change chart type -->
          <div class="q-ma-xs cursor-pointer">
            <q-btn flat dense>
              <img src="~assets/png/chart_icons/toggle.png" @click="changeChartType">
              <q-tooltip>
                Change chart type
              </q-tooltip>
            </q-btn>
          </div>
          <!-- change chart type -->
          <div class="q-ma-xs cursor-pointer relative-position">
            <q-btn flat dense>
              <img src="~assets/png/chart_icons/settings.png" @click="show_selection_form = !show_selection_form">
              <q-tooltip>
                show selections
              </q-tooltip>
            </q-btn>

            <!----------------------------------- menu form "----------------------------------->
            <div class="dashboard-form-menu" v-show="show_selection_form">
              <!-------------------- close button ---------------->
              <div class="absolute-right">
                <q-btn flat dense icon="cancel" color="grey" @click="show_selection_form = false" />
              </div>
              <div class="dashboard-product-selections">
                <!-------------------------------- data source selection ------------------------------->
                <div class="q-my-sm">
                  <div class="label q-py-sm">SELECT DATA SOURCE</div>
                  <q-select hide-dropdown-icon outlined dense v-model="raster_source" behavior="menu"
                    :options="rasterSources">
                    <template v-slot:append>
                      <q-icon name="keyboard_arrow_down" color="grey-6" />
                    </template>
                  </q-select>
                </div>
                <!-------------------------------- reporting period selection ------------------------------->
                <div class="q-my-sm">
                  <div class="label q-py-sm">SELECT YEAR</div>
                  <q-select hide-dropdown-icon outlined dense v-model="end_year" behavior="menu"
                    popup-content-class="computation-year-selection" :options="years">
                    <template v-slot:append>
                      <q-icon name="keyboard_arrow_down" color="grey-6" />
                    </template>
                  </q-select>
                </div>

                <div class="q-mt-md">
                  <q-btn unelevated dense class="indicator-selction-form-btn full-width" @click="submit"
                    no-caps>Submit</q-btn>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- summary data -->
      <div class="summary q-my-sm" v-html="summary_html">
      </div>
      <BarChart id="bar_chart" :chart_data="chartData" :chart_id="randChartId('bar_chart')"
        v-if="chartData && current_chart_type === 'bar_chart'" />
      <PieChart id="pie_chart" :chart_data="chartData" :chart_id="randChartId('pie_chart')"
        v-if="chartData && current_chart_type === 'pie_chart'" />

      <LineChart id="line_chart" :chart_data="chartData" :chart_id="randChartId('line_chart')" ref="line_chart"
        v-show="chartData && current_chart_type === 'line_chart'" />
    </div>
    <!-- loading -->
    <div class="flex flex-center  relative-position" v-show="request_pending" style="min-height: 200px;">
      <div class="">
        <q-inner-loading :showing="request_pending" label="Please wait..." label-class="text-teal"
          label-style="font-size: 1.1em" />
      </div>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
import { requestAnalysis } from 'src/Services/requests'
import chartData from 'src/Services/chartData'
// import { getPercentage, getStatValue } from 'src/Services/summaryData'
//download csv
import { downloadCSV } from "src/Services/downloadCSV";
//pinia
import { storeToRefs } from "pinia";
import { useComputationYearsStore } from "src/stores/computation_year_store"; // computation years store
import { usePrecomputationYearsStore } from "src/stores/precomputation_year_store"; // precomputation years store
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // selected indicator store
const { fetchComputationYears } = useComputationYearsStore(); // action to fetch computation years
const { fetchPrecomputationYears } = usePrecomputationYearsStore(); // action to fetch precomputed years
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected gemotry data from the store store
const { setDashboardChartData } = useChartDataStore() //action to set chart data to the store
const { setIndicatorSelections } = useIndicatorSelectionStore() //action to set chart data to the store
const colors = [

  {
    "color": "red",
    "change_type": 2,
  },

];
export default {

  data() {
    return {
      current_chart_type: "bar_chart", // pie_chart
      years: [], //years
      show_selection_form: false,
      raster_source: { label: "Hansen", value: "Hansen" },
      start_year: 2000,
      veg_index: "NDVI",
      end_year: 2019,
      indicator: {
        label: "Forest Loss",
        value: "forest_loss",
        colors
      },
      chart_data: undefined, // holds chart data
      request_pending: true,
      summary_html: "", // holds the summary data
      chart_type_ids: {}, // holds chart type by id
    }
  },
  computed: {
    //data sources
    rasterSources() {
      return [
        { label: "Hansen", value: "Hansen" }
      ]
    },

    //
    chartData() {
      return this.chart_data
    },
    //
    getRenderedCustomGeometryData() {
      return getRenderedCustomGeometryData.value
    },
    // build the year for  chart title
    getYear() {
      const startYear = this.start_year;
      const endYear = this.end_year;
      if (startYear && endYear) return `from ${startYear} to ${endYear}`;
      if (startYear && !endYear) return ` ${startYear}`;
      if (!startYear && endYear) return ` ${endYear}`;
      return "";
    },

  },
  components: {
    BarChart: defineAsyncComponent(() => import('src/components/Charts/Bar.vue')),
    PieChart: defineAsyncComponent(() => import('src/components/Charts/Pie.vue')),
    LineChart: defineAsyncComponent(() => import('src/components/Charts/Line.vue')),
  },
  watch: {
    getRenderedCustomGeometryData: {
      immediate: true,
      handler(val) {
        if (!val) return;
        this.submit()
      }
    }
  },

  mounted() {
    //get computation years
    this.fetchYears()
  },
  methods: {
    //generate chart id
    randChartId(type) {
      const id = (Math.random() + 1).toString(36).substring(7)
      this.chart_type_ids[type] = id
      return id
    },
    // controls the switching of chart by type
    changeChartType() {
      if (this.current_chart_type === 'bar_chart') {
        this.current_chart_type = "pie_chart";
        this.$refs['pie_chart']?.render(this.chartData)
      }
      else if (this.current_chart_type === 'pie_chart') {
        this.current_chart_type = "line_chart"
        this.$refs['line_chart']?.render(this.chartData)
      }
      else {
        this.current_chart_type = "bar_chart";
        this.$refs['bar_chart']?.render(this.chartData)
      }
    },
    // fetch computation years
    async fetchYears() {
      this.years = await fetchComputationYears("Forest Change")
      //test precomputaion end point
      fetchPrecomputationYears("Forest Change")
    },
    // submit results for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.start_year,
          end_year: this.end_year,
          cached: true,
          raster_type: 6,
          raster_source: "Hansen",
          computation_type: "Forest Change",
          dashboard_context: 1,
        }
        //reset data
        this.summary_html = "";
        this.chart_data = "";
        // make analysis request
        const uri = `/api/forestchange/`; // build the request url
        this.request_pending = true
        const results = await requestAnalysis({ uri, payload, caller: 'state', indicator: this.indicator, hide_loading_progress: true });// request analysis
        this.chart_data = this.processChartData(results) // create chart data for change indicators
        this.request_pending = false;

        setDashboardChartData({
          chart_data: this.chart_data,
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached,
        });
        setIndicatorSelections({
          chart_data: this.chart_data,
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.end_year,
          cached: this.cached,
        });

        this.processStatsSummary()
      } catch (error) {
        if (process.env.DEV) console.log("error requesting analysis ", error);
        this.request_pending = false
      }
    },
    // set the summary  according to the sub indicator selected
    processStatsSummary() {
      const forest_loss_value = this.chart_data.values[0]; //
      const total_area = this.chart_data.total_area;
      const percentage = Math.floor(100 * forest_loss_value / total_area)
      // summary for state
      this.summary_html = this.$t("summaries.forest_loss", [
        this.end_year,
        forest_loss_value,
        getRenderedCustomGeometryData.value?.name,
        `<strong >${percentage} % </strong>`,
        this.start_year,
        this.end_year,
      ]);
    },
    // process stat results here since forest loss data needs to be handled differently
    processChartData(results) {
      const handsen_stats = results?.stats?.stats[0]?.stats;
      let stat_year = handsen_stats.find(stat => {
        return stat.key === (this.end_year - this.start_year)
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
    },
    // download chart image
    downloadChartPng() {
      const canvas = document.getElementById(this.chart_type_ids[this.current_chart_type])
      const chartImg = canvas.toDataURL("image/png");
      const name = `${this.indicator.label} ${this.getYear}`
      let filename, link;
      filename = name
      link = document.createElement("a");
      link.setAttribute("href", chartImg);
      link.setAttribute("download", filename);
      document.body.appendChild(link); // Required for FF
      link.click();
      document.body.removeChild(link);
    },
    //download chart
    downloadCSV() {
      let csv_data = [];
      this.chart_data.values.forEach((data, i) => {
        csv_data.push({
          label: this.chart_data.labels[i],
          color:
            this.chart_data.backgroundColor[i]?.split("#")[1] ||
            this.chart_data.backgroundColor[i],
          value: data
        });
      });
      const name = `${this.indicator.label} ${this.getYear}`
      downloadCSV({ filename: name, data: csv_data });
    },
  }
}
</script>

<style lang="scss" scoped>
.chart-container {
  border: 1px solid #808080;
  border-radius: 23px;
  padding: 20px;
}

.indicator-chart-title {
  color: #404715;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 800;
  font-size: 16px;
  text-transform: uppercase;
}




.summary {
  color: #4A5219;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 16px;
}
</style>
