<template>
  <div class="bg-white q-pa-sm" style="border-radius:20px">
    <div class="flex justify-between q-px-sm q-pt-sm">
      <div class="flex items-center">
        <img src="~assets/png/chart_icons/chart.png" style="width:40px">
        <div class="statistics-header-title">Statistics</div>
      </div>
      <div class="">
        <img src="~assets/png/chart_icons/close.png" @click="closeStatistics" style="width:30px" class="cursor-pointer">
      </div>
    </div>
    <!-- show analysis summary -->
    <AnalysisSummary />

    <!---------------------------------- BAR CHART AREA ------------------------------------->
    <div class="q-my-sm">
      <div class="flex justify-between">
        <!---------------------------------------  chart title ----------------------------------------->
        <div class="chart-title">{{ chartTitle }}</div>
        <!---------------------------------------  chart actions ----------------------------------------->
        <div class="chart-actions flex">
          <!-- download chart data -->
          <div flat class="q-ma-xs cursor-pointer">
            <img src="~assets/png/chart_icons/download.png" @click="downloadCSV">
            <q-tooltip>
              Download CSV
            </q-tooltip>
          </div>
          <!-- download chart png image -->
          <div flat class="q-ma-xs cursor-pointer">
            <img src="~assets/png/chart_icons/image.png" @click="downloadChartPng">
            <q-tooltip>
              Download chart image
            </q-tooltip>
          </div>
          <!-- link to information -->
          <div flat class="q-ma-xs cursor-pointer">
            <a href="https://misland.readthedocs.io/en/latest/Service/Calculate_SDG.html#landcover-change"
              target="_blank" rel="noopener noreferrer">
              <img src="~assets/png/chart_icons/information.png" alt="">
              <q-tooltip>
                Click for more information
              </q-tooltip>
            </a>
          </div>
          <!-- change chart type -->
          <div class="q-ma-xs cursor-pointer">
            <img src="~assets/png/chart_icons/toggle.png" @click="changeChartType">
            <q-tooltip>
              Change chart type
            </q-tooltip>
          </div>
        </div>
      </div>
      <!-- show bar chart -->
      <div v-show="current_chart_type === 'bar-chart'">
        <BarChart :chart_data="getChartData" :chart_id="'bar-chart'" />
      </div>
      <!-- show pie chart -->
      <div v-show="current_chart_type === 'pie-chart'">
        <PieChart :chart_data="getChartData" :chart_id="'pie-chart'" />
      </div>
      <!-- show line chart -->
      <div v-show="current_chart_type === 'line-chart'">
        <LineChart :chart_data="getChartData" :chart_id="'line-chart'" />
      </div>
    </div>
    <!-------------------------------------------------------------------------------------->
    <!-- show selected indicator notes -->
    <ProductNotes v-if="getChartData" />
  </div>
</template>

<script>

//pinia
import { storeToRefs } from "pinia";
import { downloadCSV } from "src/Services/downloadCSV";
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // user indicator selection store
const { getChartData } = storeToRefs(useChartDataStore()); // get chart data from store
const { getRenderedCustomGeometryData } = storeToRefs(useGeometryStore()); // get selected geometry data from the store store
const { getIndicatorSelections } = storeToRefs(useIndicatorSelectionStore()); // get selected indicators
const { setChartData } = useChartDataStore() //action to set chart data to the store
import { defineAsyncComponent } from "vue";
export default {
  data() {
    return {
      current_chart_type: 'pie-chart', // holds the current chart to display [line-chart,pie-chart,bar-chart]
      chart_type_tracking_index: 0, // chart type tracking index
      chart_types: [
        'bar-chart',
        'pie-chart',
        'line-chart',
      ]
    }
  },
  computed: {
    getChartData() {
      return getChartData.value
    },
    // build the year for  chart title
    getYear() {
      const startYear = getIndicatorSelections.value?.start_year;
      const endYear = getIndicatorSelections.value?.end_year;
      if (startYear && endYear) return `from ${startYear} to ${endYear}`;
      if (startYear && !endYear) return ` ${startYear}`;
      if (!startYear && endYear) return ` ${endYear}`;
      return "";
    },
    // generate chart title
    chartTitle() {
      const name = getRenderedCustomGeometryData.value.label;
      const indicator = getIndicatorSelections.value?.indicator?.label
      return `${name} ${indicator} ${this.getYear}`
    }
  },
  components: {
    BarChart: defineAsyncComponent(() => import('src/components/Charts/Bar.vue')),
    PieChart: defineAsyncComponent(() => import('src/components/Charts/Pie.vue')),
    LineChart: defineAsyncComponent(() => import('src/components/Charts/Line.vue')),
    // summary component
    AnalysisSummary: defineAsyncComponent(() => import('src/components/Reusables/AnalysisSummary.vue')),
    // selected indicator products notes
    ProductNotes: defineAsyncComponent(() => import('src/components/Reusables/ProductNotes.vue')),
  },

  methods: {
    // method to download chart image
    changeChartType() {
      const indicator = getIndicatorSelections.value.indicator.value
      let chart_type;
      if (indicator != 'forest_loss') {
        if (this.chart_type_tracking_index > 1) this.chart_type_tracking_index = 0
        chart_type = this.chart_types[this.chart_type_tracking_index]
        this.current_chart_type = chart_type;
      } else {
        chart_type = this.chart_types[this.chart_type_tracking_index]
        this.current_chart_type = chart_type;
      }
      this.chart_type_tracking_index++
      if (this.chart_type_tracking_index > 2) this.chart_type_tracking_index = 0
      if (process.env.DEV) console.log("charts rotated +++++++++++++++++ ", this.current_chart_type);
    },
    // close the statics tab
    closeStatistics() {
      this.$emit("show_indicator_selections")
    },
    // download chart image
    downloadChartPng() {
      const chartImg = document.getElementById(this.current_chart_type).toDataURL("image/png");
      const name = `${getIndicatorSelections.value.indicator.label} ${this.getYear}`
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
      if (process.env.DEV) console.log("downloadcsv ", this.getChartData);
      this.getChartData.values.forEach((data, i) => {
        csv_data.push({
          label: this.getChartData.labels[i],
          color:
            this.getChartData.backgroundColor[i]?.split("#")[1] ||
            this.getChartData.backgroundColor[i],
          value: data
        });
      });
      const name = `${getIndicatorSelections.value.indicator.label} ${this.getYear}`
      downloadCSV({ filename: name, data: csv_data });
    },

  },
}
</script>

<style lang="scss" scoped>
.statistics-header-title {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 20px;
  color: #838C48;
  margin-left: 10px;
}
</style>
