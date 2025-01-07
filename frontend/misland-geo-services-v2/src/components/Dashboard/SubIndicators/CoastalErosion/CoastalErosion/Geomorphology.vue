<template>
  <div class="chart-container q-my-lg">
    <!-- ff -->
    <div v-show="!request_pending">
      <div class="flex justify-between">
        <div class="indicator-chart-title">{{ getRenderedCustomGeometryData?.name }} Geomorphology </div>
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
            <a href="https://misland.readthedocs.io/en/latest/Service/Calculate_coastal.html" target="_blank"
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
                  <div class="label q-py-sm">WIND EROSION FACTORS</div>
                  <q-select hide-dropdown-icon outlined dense v-model="indicator" behavior="menu"
                    :options="qualityIndices">
                    <template v-slot:append>
                      <q-icon name="keyboard_arrow_down" color="grey-6" />
                    </template>
                  </q-select>
                </div>
                <!-------------------------------- reporting period selection ------------------------------->
                <div class="q-my-sm">
                  <div class="label q-py-sm">REPORTING PERIOD</div>
                  <q-select hide-dropdown-icon outlined dense v-model="start_year" behavior="menu"
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
import { getPercentage, getStatValue } from 'src/Services/summaryData';
//download csv
import { downloadCSV } from "src/Services/downloadCSV";
//pinia
import { storeToRefs } from "pinia";
import { useComputationYearsStore } from "src/stores/computation_year_store"; // computation years store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // selected indicator store
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
const { fetchComputationYears } = useComputationYearsStore(); // action to fetch computation years
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected gemotry data from the store store
const { setDashboardChartData } = useChartDataStore() //action to set chart data to the store
const { setIndicatorSelections } = useIndicatorSelectionStore() //action to set chart data to the store

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
      current_chart_type: "bar_chart", // pie_chart
      show_selection_form: false,
      years: [], //years     
      start_year: 2019,
      indicator: {
        label: "Geomorphology",
        value: "geomorphology",
        colors: colors,
        computation_type: "Geomorphology"
      },
      chart_data: undefined, // holds chart data
      request_pending: true,
      cached: true, // controls if cached results are shown
      summary_html: "", // holds the summary data
      chart_type_ids: {}, // holds chart type by id
    }
  },
  computed: {
    //quality indices sources
    qualityIndices() {
      return [
        {
          label: "Geomorphology",
          value: "geomorphology",
          colors: colors,
          computation_type: "Geomorphology"
        },

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
    // controls the switching of chart by type
    changeChartType() {
      if (this.current_chart_type === 'bar_chart') {
        this.current_chart_type = "pie_chart"
      } else {
        this.current_chart_type = "bar_chart"
      }
    },
    // fetch computation years
    async fetchYears() {
      this.years = await fetchComputationYears("Coastal Vulnerability Index");
      this.star_year = this.years[this.years.length - 1]
    },
    // submit results for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.start_year,
          end_year: this.start_year,
          cached: this.cached,
          raster_type: 1,
          computation_type: this.indicator.computation_type,
          dashboard_context: 1, // to inform backend its from dashboard
        }
        //reset data
        this.summary_html = "";
        this.chart_data = "";
        // make analysis request
        const uri = `/api/cvi/`; // build the request url
        this.request_pending = true
        const results = await requestAnalysis({ uri, payload, caller: 'cvi', indicator: this.indicator, hide_loading_progress: true });// request analysis
        this.chart_data = chartData.changeDataProcessor({ results, indicator: this.indicator }); // create chart data for change indicators
        this.request_pending = false;
        setDashboardChartData({
          chart_data: this.chart_data,
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.start_year,
          cached: this.cached,
        });
        setIndicatorSelections({
          chart_data: this.chart_data,
          indicator: this.indicator,
          start_year: this.start_year,
          end_year: this.start_year,
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
      // summary for state
      const indicator = `summaries.${this.indicator.value}`
      this.summary_html = this.$t(indicator, [
        this.start_year,
        getRenderedCustomGeometryData.value?.name,
        getPercentage(getStatValue({ change_type: 5 })),
        getPercentage(getStatValue({ change_type: 4 })),
        getPercentage(getStatValue({ change_type: 3 })),
        getPercentage(getStatValue({ change_type: 2 })),
        getPercentage(getStatValue({ change_type: 1 }))

      ]);
    },
    //generate chart id
    randChartId(type) {
      const id = (Math.random() + 1).toString(36).substring(7)
      this.chart_type_ids[type] = id
      return id
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
