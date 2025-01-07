<template>
  <div class="">
    <canvas :id="chart_id" height="200" style="max-height: 200px;"></canvas>
  </div>
</template>
<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables);
export default {
  props: {
    chart_data: [String, Object],
    chart_id: {
      type: [String],
      default: 'pie-chart'
    }
  },
  data() {
    return {
      chart_instance: null, // holds the chart instance
    };
  },
  computed: {
    // checks chart data from the store
    chartData() {
      return this.chart_data
    }
  },
  watch: {
    chartData: {
      handler(val) {
        if (!val) return;
        this.render(val)
      }
    },
  },
  mounted() {
    if (this.chartData) this.render(this.chartData)
  },
  methods: {
    render({ values, labels, backgroundColor }) {
      const data = {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor,
            borderWidth: 2,
            borderRadius: 2,
          }
        ]
      };
      const config = {
        type: 'pie',
        data: data,
        options: {
          maintainAspectRatio: false,
          responsive: true,
          plugins: {
            legend: {
              display: true,
              position: "right",
              labels: {
                fontColor: "black"
              }
            }
          },

        }
      };
      
      let chart_instance = Chart.getChart(this.chart_id); // <canvas> id
      if (chart_instance != undefined) {
        chart_instance.destroy();
      };
      const ctx = document.getElementById(this.chart_id);
      if (!ctx) return
      chart_instance = new Chart(ctx, config);
    }
  }
};
</script>
<style lang="scss" scoped>
.chart-title {}
</style>
