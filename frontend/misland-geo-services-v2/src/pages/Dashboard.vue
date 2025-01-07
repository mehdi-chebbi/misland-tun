<template>
  <q-page class="row q-pa-md ">
    <NavBar />
    <!-- show map -->
    <div class="col-xs-12 col-md-5  flex justify-center  dashboard-map-container">
      <DashboardMap style="border-radius:20px" />
    </div>
    <div class="col-xs-12 col-md-7 dashboard-content">
      <!-- geometry selection -->
      <div class="dashboard-geometry-selection">
        <GeometrySelection />
        <div class="q-my-lg">
          <IndicatorIcons @emit_selected_indicator="selected_indicator = $event" />
        </div>
      </div>
      <!-- Indicator Icons -->
      <!-- <div class="q-my-lg">
        <IndicatorIcons @emit_selected_indicator="selected_indicator = $event" />
      </div> -->
      <!-- indicator selections -->
      <div class="q-my-lg">
        <SDG v-if="selected_indicator === 'sdg'" />
        <VegLossGain v-if="selected_indicator === 'veg_loss_gain'" />
        <ForestChange v-if="selected_indicator === 'forest_change'" />
        <Desert v-if="selected_indicator === 'desert'" />
        <SoilErosion v-if="selected_indicator === 'soil_erosion'" />
        <CoastalErosion v-if="selected_indicator === 'coastal_erosion'" />
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineAsyncComponent } from "vue";
export default {
  data() {
    return {
      selected_indicator: "sdg", // holds the selected inndicator
    };
  },
  components: {
    DashboardMap: defineAsyncComponent(() => import('src/components/Reusables/DashboardMap.vue')),
    GeometrySelection: defineAsyncComponent(() => import('src/components/Dashboard/GeometrySelection.vue')),
    IndicatorIcons: defineAsyncComponent(() => import('src/components/Dashboard/IndicatorIcons.vue')),
    // main  indicator imports
    SDG: defineAsyncComponent(() => import('src/components/Dashboard/Indicators/SDG.vue')),
    VegLossGain: defineAsyncComponent(() => import('src/components/Dashboard/Indicators/VegLossGain.vue')),
    ForestChange: defineAsyncComponent(() => import('src/components/Dashboard/Indicators/ForestChange.vue')),
    Desert: defineAsyncComponent(() => import('src/components/Dashboard/Indicators/Desert.vue')),
    SoilErosion: defineAsyncComponent(() => import('src/components/Dashboard/Indicators/SoilErosion.vue')),
    CoastalErosion: defineAsyncComponent(() => import('src/components/Dashboard/Indicators/CoastalErosion.vue')),
    // nav bar
    NavBar: defineAsyncComponent(() => import("src/components/NavBar.vue")),
  },

};
</script>

<style lang="scss" scoped>
.dashboard-map-container {
  position: relative;

  @media (min-width: $breakpoint-md-min) {
    max-height: calc(100vh - 80px);

  }

  @media (max-width: $breakpoint-sm-max) {
    height: 600px;
    margin-bottom: 20px;
  }
}

// dahboard content class
.dashboard-content {
  @media (min-width: $breakpoint-md-min) {
    overflow-y: auto;
    height: calc(100vh - 80px);
    padding: 0px 30px;
  }

  // set padding for large screens
  @media (min-width: $breakpoint-xl-min) {
    padding: 0px 50px 0px 100px;
    height: calc(100vh - 80px);
  }

  @media (max-width: $breakpoint-sm-max) {}
}

.dashboard-geometry-selection {
  position: sticky;
  background-color: white;
  padding: 0px 5px;
  top: -5px;
  z-index: 1;
}
</style>
