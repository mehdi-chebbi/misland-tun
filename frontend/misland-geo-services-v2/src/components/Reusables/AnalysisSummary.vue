<template>
  <div>
     <div class="q-p" v-html="summary"></div>
  </div>
</template>
<script>
//pinia
import { storeToRefs } from "pinia";
import { useChartDataStore } from "src/stores/chart_data_store"; // user indicator selection store
const { getDataSummary } = storeToRefs(useChartDataStore()); // get selected gemotry data from the store store
export default {

  computed: {
    summary() {
      return getDataSummary.value
    }
  }

}
</script>
<style lang="scss" scoped>
.summary-text {
  font-family: 'Inter';
font-style: normal;
font-weight: 500;
font-size: 13.5px;
line-height: 155.02%;
}

</style>
