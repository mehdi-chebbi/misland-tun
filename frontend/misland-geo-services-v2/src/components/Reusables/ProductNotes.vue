<template>
  <div class="q-pa-sm">
    <div class="label text-weight-bolder">Note:</div>
    <div v-html="productInformation"></div>
  </div>
</template>
<script>
import { storeToRefs } from "pinia";
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // user indicator selection store
const { getIndicatorNoteKey } = storeToRefs(useIndicatorSelectionStore()); // get chart data from store

export default {
  computed: {
    productInformation() {
      const product = getIndicatorNoteKey.value;
      console.log("product ", product);
      const path = "notes."+product
       return this.$t(path)
    },
  }
}
</script>
<style lang="">

</style>
