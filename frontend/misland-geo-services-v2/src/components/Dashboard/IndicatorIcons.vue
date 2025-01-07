<template>
  <div class=" indicator-icons-container flex justify-around items-center" style="flex:1; border-radius: 10px;">
    <div class="flex items-center q-pa-sm cursor-pointer" v-for="(indicator, index) in indicators" :key="index"
      @click="showSelectedForm(indicator)"
      :class="Selected_indicator?.value === indicator?.value ? 'active-indicator' : 'indicator-name'">
      <img :src="indicator?.image">
      <div class="q-ml-sm ">{{ indicator?.name }}</div>
    </div>
  </div>
</template>
<script>
import sdg_svg from 'src/assets/svg/indicators/SDG.svg'
import veg_loss_gain_svg from 'src/assets/svg/indicators/veg.svg'
import forest_change_svg from 'src/assets/svg/indicators/forest_change.svg'
import desert_svg from 'src/assets/svg/indicators/desert.svg'
import soil_erosion_svg from 'src/assets/svg/indicators/soil_erosion.svg'
import coastal_svg from 'src/assets/svg/indicators/coastal.svg'
export default {
  data() {
    return {
      Selected_indicator: { value: 'sdg', image: sdg_svg, name: this.$t('main_indicators.sdg') },
    }
  },
  computed: {
    indicators() {
      return [
        { value: 'sdg', image: sdg_svg, name: this.$t('main_indicators.sdg') },
        { value: 'veg_loss_gain', image: veg_loss_gain_svg, name: this.$t('main_indicators.veg_loss_gain') },
        { value: 'forest_change', image: forest_change_svg, name: this.$t('main_indicators.forest_change') },
        { value: 'desert', image: desert_svg, name: this.$t('main_indicators.desert') },
        { value: 'soil_erosion', image: soil_erosion_svg, name: this.$t('main_indicators.soil_erosion') },
        { value: 'coastal_erosion', image: coastal_svg, name: this.$t('main_indicators.coastal_erosion') },
      ]
    }
  },

  methods: {
    showSelectedForm(indicator) {
      this.Selected_indicator = indicator
      this.$emit('emit_selected_indicator', indicator.value)
    }
  }
}
</script>

<style lang="scss" scoped>
.indicator-icons-container {
  border: 1.5px solid #74B281;
  border-radius: 18px;
  padding: 5px;

  @media (min-width: $breakpoint-md-min) {}

  @media (max-width: $breakpoint-sm-max) {}
}

.indicator-name {
  font-family: 'Inter';
  // font-style: normal;
  font-weight: 700;
  font-size: 16px;
  color: #404715;
}

.active-indicator {
  background: #F3F9F5;
  border-radius: 7px;
  color: #74B281;
  font-weight: 700;
  font-size: 16px;
}
</style>
