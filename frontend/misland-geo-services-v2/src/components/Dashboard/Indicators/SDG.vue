<template>
  <!--  indicator sections-->
  <div class="q-my-lg">
    <!-- indicator selection buttons -->
    <div class="flex justify-between q-mb-lg" style="gap:40px">
      <div class="col" v-for="(sub_indicator, index) in subIndicatorsTabs" :key="index">
        <q-btn unelevated class="full-width"
          :class="selected_sub_indicator?.value === sub_indicator?.value ? 'active-indicator-btn' : 'indicator-btn'"
          @click="handleSelectedSubIndicator(sub_indicator)" no-caps>{{ sub_indicator?.label }}</q-btn>
      </div>
    </div>
    <!-- indicator explation  text -->
    <div class="indicator-explation-text q-my-lg">
      Easily explore the interactive charts and maps which can be readily customized, shared, and
      downloaded for offline use.
    </div>
    <!-------------------------------------------------------------------   indicator  ------------------------------------------------------------------->
    <!-------------- land productivity ---------------------->
    <div class="" v-if="selected_sub_indicator.value === 'land-productivity'">
      <LandProductivityPanel />
    </div>
    <!-------------- land cover ---------------------->
    <div class="" v-if="selected_sub_indicator.value === 'land-cover'">
      <LandCover />
    </div>
    <!-------------- carbon stock ---------------------->
    <div class="" v-if="selected_sub_indicator.value === 'carbon-stock'">
      <CarbonStock />
    </div>
    <!-------------- sdg-indicator ---------------------->
    <div class="" v-if="selected_sub_indicator.value === 'sdg-indicator'">
      <SDGIndicator />
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
export default {
  data() {
    return {
      tab: "land-productivity",
      selected_sub_indicator: { value: "land-cover", label: "land cover" }, // holds the selected sub indicator
      selected_indicator: "", // holds the selected inndicator
    };
  },
  computed: {
    subIndicatorsTabs() {
      return [
        { value: "land-productivity", label: this.$t('sub_indicators.sdg.land_productivity') },
        { value: "land-cover", label: this.$t('sub_indicators.sdg.land_cover') },
        { value: "carbon-stock", label: this.$t('sub_indicators.sdg.carbon_stock') },
        { value: "sdg-indicator", label: this.$t('sub_indicators.sdg.sdg_indicator') },
      ]
    },
  },
  components: {
    // indicators panels
    LandProductivityPanel: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/LandProductivity.vue')),
    LandCover: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/LandCover.vue')),
    CarbonStock: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/CarbonStock.vue')),
    SDGIndicator: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/SDG/SDGIndicator.vue')),
  },
  methods: {
    handleSelectedSubIndicator(indicator) {
      this.selected_sub_indicator = indicator; // set the selected indicator to the state
      if (process.env.DEV) console.log("handleSelectedSubIndicator ***********************  ", indicator);
    }
  }
}
</script>

<style lang="scss" scoped>
.active-indicator-btn {
  background: #74B281;
  border-radius: 10px;
  color: #F8F9F4;
  font-weight: 600;
  font-size: 18px;
  font-family: 'Inter';
  font-style: normal;

}

.indicator-btn {
  background: #F8F9F4;
  border-radius: 10px;
  color: #74B281;
  font-weight: 600;
  font-size: 18px;
  font-family: 'Inter';
  font-style: normal;

}

.indicator-explation-text {
  color: #4A5219;
  font-weight: 400;
  font-size: 16px;
  font-family: 'Inter';
  font-style: normal;

}
</style>
