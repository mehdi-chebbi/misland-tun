<template>
  <div class="">
    <canvas :id="chart_id" height="200"  style="max-height: 200px;"></canvas>
  </div>
</template>
<script>
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);
export default {
  props: {
    chart_data: [String, Object],
    chart_id: {
      type: [String],
      default: 'line_chart_id'
    },
  },
  data() {
    return {
      chart_instance: null, // holds the chart instance
    };
  },
  computed: {
    // checks chart data from the store
    chartData() {
      return this.chart_data;
    },
  },
  watch: {
    chartData: {
      immediate: true,
      handler(val) {
        if (!val) return;
        if (process.env.DEV) console.log(this.chart_instance, "Id ",this.chart_id, "  line  data ", val);
        this.render(val);
      },
    },
  },
  methods: {
    render({ line_labels, datasets, indicator }) {
      const has_line_chart = ["forest_fire_risk", "forest_loss"];
      if (!has_line_chart.includes(indicator)) return;
      const data = {
        labels: line_labels,
        datasets,
      };
      const config = {
        type: "line",
        data: data,
        options: {
          maintainAspectRatio: false,
          responsive: true,
          // indexAxis: "y",
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            x: {
              grid: {
                display: false,
                drawBorder: true,
                drawOnChartArea: true,
                drawTicks: true,
              },
            },
            y: {
              grid: {
                display: true,
                borderDash: [8, 4],
              },
            },
          },
        },
      };


      let chart_instance = Chart.getChart(this.chart_id); // <canvas> id
      if (chart_instance != undefined) {
        chart_instance.destroy();
      };
      const ctx = document.getElementById(this.chart_id);
      // console.log("linechart ctx ====", ctx);
      if (!ctx) return
      chart_instance = new Chart(ctx, config);

    },
  },
};
</script>
<style lang="scss"></style>
