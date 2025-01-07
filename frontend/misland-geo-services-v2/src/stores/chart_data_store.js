import { defineStore } from 'pinia';

export const useChartDataStore = defineStore('chart_data_store', {
  state: () => ({
    chart_data: "", //holds chart data processed from results
    summary: "", //holds  analysis summary text
    dashboard_chart_data: [], // holds dashboard chart data
  }),
  getters: {
    getChartData: (state) => state.chart_data, // get chart data
    getDataSummary: (state) => state.summary, // get data summary text
    getDashboardChartData: (state) => state.dashboard_chart_data, // get data summary text
  },
  actions: {
    // store the chart data in the store
    setChartData(chart_data) {
      this.chart_data = chart_data
    },
    // store the data summary text
    setDataSummary(summary) {
      this.summary = summary
    },
    // store the dashboard chart data
    setDashboardChartData(chart_data) {
      this.dashboard_chart_data.push(chart_data)
      console.log("chart data", chart_data)
    },
  },
});


