<template >
  <div class="flex column q-mr-xs">
    <div class="q-pa-sm q-mb-xs  bg-white" style=" border-radius: 10px;" >
      <img :src="indicator_svg" alt="" class="q-ma-xs">
    </div>
    <div class="flex bg-white column justify-around items-center" style="flex:1; border-radius: 10px;">
      <div class="" v-for="(indicator, index) in indicators" :key="index">
        <img :src="indicator?.image" class="cursor-pointer" @click="showSelectedForm(indicator)">
      </div>
    </div>
  </div>
</template>
<script>
import indicator_svg from 'src/assets/svg/indicators/map.svg'
import sdg_svg from 'src/assets/svg/indicators/SDG.svg'
import veg_loss_gain_svg from 'src/assets/svg/indicators/veg.svg'
import forest_chaneg_svg from 'src/assets/svg/indicators/forest_change.svg'
import desert_svg from 'src/assets/svg/indicators/desert.svg'
import soil_erosion_svg from 'src/assets/svg/indicators/soil_erosion.svg'
import coastal_svg from 'src/assets/svg/indicators/coastal.svg'
export default {
  data() {
    return {
      indicator_svg,
    }
  },
  computed: {
    indicators() {
      return [
        { expansion_item: 'expand_sdg', image: sdg_svg },
        { expansion_item: 'expand_veg_loss_gain', image: veg_loss_gain_svg },
        { expansion_item: 'expand_forest_change', image: forest_chaneg_svg },
        { expansion_item: 'expand_desert', image: desert_svg },
        { expansion_item: 'expand_soil_erosion', image: soil_erosion_svg },
        { expansion_item: 'expand_coastal_erosion', image: coastal_svg },
      ]
    }
  },
  methods:{
    showSelectedForm(indicator){
      this.$emit('emit_selected_form', indicator.expansion_item)
    }
  }
}
</script>
<style lang="">

</style>
