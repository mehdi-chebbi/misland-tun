<template>
  <!--  indicator sections-->
  <div class="">
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
    <div class="" v-if="selected_sub_indicator.value === 'cvi'">
      <CVI />
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
export default {
  data() {
    return {
      selected_sub_indicator: { value: "cvi", label: this.$t('sub_indicators.coastal_ersoion.cvi') }, // holds the selected sub indicator
    };
  },
  computed: {
    subIndicatorsTabs() {
      return [
        { value: "cvi", label:  this.$t('sub_indicators.coastal_ersoion.cvi')},
      ]
    },
  },
  components: {

       // indicators panels
       CVI: defineAsyncComponent(() => import('src/components/Dashboard/SubIndicators/CoastalErosion/CVI.vue')),
  },
  methods: {
    handleSelectedSubIndicator(indicator) {
      this.selected_sub_indicator = indicator; // set the selected indicator to the state
      console.log("handleSelectedSubIndicator ***********************  ", indicator);
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
