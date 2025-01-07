<template>
  <div class="chart-container q-my-lg">
    <!-- ff -->
    <div v-show="!request_pending">
      <div class="flex justify-between">
        <div class="indicator-chart-title">{{ getRenderedCustomGeometryData?.name }} forest carbon </div>
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
                <div class="q-my-xs">
                  <div class="label q-py-xs">SELECT DATA SOURCE</div>
                  <q-select hide-dropdown-icon outlined dense v-model="data_source" behavior="menu"
                    :options="dataSources">
                    <template v-slot:append>
                      <q-icon name="keyboard_arrow_down" color="grey-6" />
                    </template>
                  </q-select>
                </div>
                <!-------------------------------- reporting period selection ------------------------------->
                <div class="q-my-xs">
                  <div class="label q-py-xs">SELECT YEAR</div>
                  <q-select hide-dropdown-icon outlined dense v-model="end_year" behavior="menu"
                    popup-content-class="computation-year-selection" :options="years">
                    <template v-slot:append>
                      <q-icon name="keyboard_arrow_down" color="grey-6" />
                    </template>
                  </q-select>
                </div>
                <!-------------------------------- advanced selection trigger ------------------------------->
                <div class="flex items-center justify-between" @click="show_advance_selections = true;"
                  v-show="!show_advance_selections">
                  <div class="q-pa-xs">Advanced Parameters</div>
                  <q-icon name="settings" color="orange" class="cursor-pointer" size="20px" />
                </div>
                <!-------------------- show advanced parameters ----------------------->
                <div v-if="show_advance_selections">
                  <div class="flex justify-between q-py-xs">
                    <div class="q-pa-xs">Hide Parameters</div>
                    <q-icon name="close" color="red" size="sm" class="cursor-pointer"
                      @click="show_advance_selections = false" />
                  </div>
                  <!--------------------------------- minimum forest units --------------------------------->
                  <div class="q-my-xs">
                    <div class="text-uppercase q-ml-xs">MINIMUM FOREST UNIT (px)</div>
                    <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1"
                      v-model.number="mfu" />
                  </div>
                  <!--------------------------------- tree cover threshold - --------------------------------->
                  <div class="q-my-xs">
                    <div class="text-uppercase q-ml-xs">TREE COVER THRESHOLD (%)</div>
                    <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1" max="100"
                      v-model.number="mfu_forest_threshold" />
                  </div>
                  <!--------------------------------- forest carbon stock --------------------------------->
                  <div class="q-my-xs">
                    <div class="text-uppercase q-ml-xs">FOREST CARBON STOCK (tC/ha)</div>
                    <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1" max="100"
                      v-model.number="carbon_stock" />
                  </div>
                  <!--------------------------------- forest carbon stock --------------------------------->
                  <div class="q-my-xs">
                    <div class="text-uppercase q-ml-xs"> PROPORTION % (tC/ha) EMITTED BY DEGRADATION</div>
                    <q-input class="col-xs-12 col-md-6 q-ml-xs" outlined dense type="number" min="1" max="100"
                      v-model.number="degradation_emission_proportion" />
                  </div>
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
import { getPercentage, getStatValue } from 'src/Services/summaryData'
//download csv
import { downloadCSV } from "src/Services/downloadCSV";
//pinia
import { storeToRefs } from "pinia";
import { useComputationYearsStore } from "src/stores/computation_year_store"; // computation years store
import { usePrecomputationYearsStore } from "src/stores/precomputation_year_store"; // precomputation years store
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
const { fetchComputationYears } = useComputationYearsStore(); // action to fetch computation years
const { fetchPrecomputationYears } = usePrecomputationYearsStore(); // action to fetch precomputed years
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected gemotry data from the store store
const { setDashboardChartData } = useChartDataStore() //action to set chart data to the store
const colors = [

  {
    "color": "red",
    "change_type": 2,
  },

];
export default {

  data() {
    return {
      show_advance_selections: false, //toggles show advanced selections
      current_chart_type: "bar_chart", // pie_chart
      years: [], //years
      show_selection_form: false,
      data_source: {
        label: "Global Forest change Maps",
        value: "global_forest_change_maps"
      },
      start_year: 2000,
      mfu: 3,
      mfu_forest_threshold: 30,
      carbon_stock: 0.2522,
      degradation_emission_proportion: 30,
      veg_index: "NDVI",
      end_year: 2020,
      indicator: {
        label: "Forest Carbon Emission",
        value: "forest_carbon_emission",
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
    dataSources() {
      return [
        {
          label: "Global Forest change Maps",
          value: "global_forest_change_maps"
        }
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
    //generate chart id
    randChartId(type) {
      const id = (Math.random() + 1).toString(36).substring(7)
      this.chart_type_ids[type] = id
      return id
    },
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
      this.years = await fetchComputationYears("Forest Carbon Emission")
      //test precomputaion end point
      fetchPrecomputationYears("Forest Carbon Emission")

    },
    // submit results for analysis
    async submit() {
      try {
        let payload = {
          start_year: this.end_year,
          end_year: this.end_year,
          cached: true,
          show_change: 0,
          muf: this.mfu,
          mfu_forest_threshold: this.mfu_forest_threshold,
          degradation_emission_proportion: this.degradation_emission_proportion,
          carbon_stock: this.carbon_stock,
          computation_type: "Forest Carbon Emission",
          dashboard_context: 1,
        }
        //reset data
        this.summary_html = "";
        this.chart_data = "";
        // make analysis request
        const uri = `/api/carbonemission/`; // build the request url
        this.request_pending = true
        const results = await requestAnalysis({ uri, payload, caller: 'state', indicator: this.indicator, hide_loading_progress: true });// request analysis
        this.chart_data = chartData.changeDataProcessor({ results, indicator: this.indicator }); // create chart data for change indicators
        this.request_pending = false;
        setDashboardChartData({
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
      this.summary_html = this.$t("summaries.forest_carbon_emission", [
        this.start_year,
        getRenderedCustomGeometryData.value?.name,
        getPercentage(getStatValue({ change_type: 3 })),
        getPercentage(getStatValue({ change_type: 2 })),
        getPercentage(getStatValue({ change_type: 1 }))
      ]);
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
