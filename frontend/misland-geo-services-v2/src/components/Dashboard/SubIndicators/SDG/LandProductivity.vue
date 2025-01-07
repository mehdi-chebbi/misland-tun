<template>
  <div class="q-pa-none">
    <!-- chart goes here -->
    <div class="q-my-md">
      <!----------------------------------------------------- trajectory  ----------------------------------------------------->
      <Trajectory />
      <!-------------------------------------------------------- state  ------------------------------------------------------->
      <State />
      <!----------------------------------------------------- performance  ---------------------------------------------------->
      <Performance />
      <!---------------------------------------------------- productivity  ---------------------------------------------------->
      <LandProductivity />
    </div>
    <!-- Note goes here -->
    <div class="q-my-lg">
      <div class="indicator-note-title">Note:</div>
      <div class="q-my-xs indicator-note-text">
        The Sustainable Development Goal (SDG) 15 aims to: “Protect, restore and promote sustainable use of terrestrial
        ecosystems, sustainably manage forest, combat desertification, and halt and reverse land degradation and halt
        biodiversity loss”. Target 15.3 aims to: “By 2030, combat desertification, restore degraded land and soil,
        including land affected by desertification, drought, floods, and strive to achieve land degradation-neutral
        world.

        <div class="q-my-md">
          The Sustainable Development Goal (SDG) 15 aims to: “Protect, restore and promote sustainable use of
          terrestrial
          ecosystems, sustainably manage forest, combat desertification, and halt and reverse land degradation and halt
          biodiversity loss”. Target 15.3 aims to: “By 2030, combat desertification, restore degraded land and soil,
          including land affected by desertification, drought, floods, and strive to achieve land degradation-neutral
          world.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
const { resetResultsStatus } = useAnalysisResultsStore()
export default {
  components: {
    Trajectory: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/LandProductivity/Trajectory.vue')),
    State: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/LandProductivity/State.vue')),
    Performance: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/LandProductivity/Performance.vue')),
    LandProductivity: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/LandProductivity/LandProductivity.vue')),
  },
  beforeUnmount() {
    resetResultsStatus(true)
  },
  mounted() {
    resetResultsStatus(false)
  },

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

.indicator-note-title {
  color: #838C48;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 800;
  font-size: 20px;
}

.indicator-note-text {
  color: #6d7344;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 16px;
}

.summary {
  color: #4A5219;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-size: 16px;
}
</style>
