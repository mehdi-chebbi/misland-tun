<template>
  <div class="row ">
    <div class="col-md-4 q-py-xl flex flex-center" v-for="(indicator, index) in indicators" :key="index">
      <div class="indicator-card">
        <div class="indicator-image-container">
          <img :src="indicator?.image" class="indicator-image">
        </div>
        <!-- indicator title  -->
        <div class="indicator-title-container">
          <img :src="indicator?.title_icon" class="indicator-title-icon">
          <div class="indicator-title">{{ indicator?.title }}</div>
        </div>
        <!-- indicator description -->
        <div class="indicator-description">
          {{ indicator?.description }}
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import sdg_indicator_map from 'src/assets/svg/home_page/sdg_indicator_map.svg';
import sdg_title_icon from 'src/assets/svg/home_page/sdg_title_icon.svg';
import forest_change_map from 'src/assets/svg/home_page/forest_change_map.svg';
import forest_change_title_icon from 'src/assets/svg/home_page/forest_change_title_icon.svg';
import veg_loss_map from 'src/assets/svg/home_page/veg_loss_map.svg';
import veg_loss_title_icon from 'src/assets/svg/home_page/veg_loss_title_icon.svg';
import coastal_erosion_map from 'src/assets/svg/home_page/coastal_erosion_map.svg';
import coastal_erosion_title_icon from 'src/assets/svg/home_page/coastal_erosion_title_icon.svg';
import desertification_map from 'src/assets/svg/home_page/desertification_map.svg';
import desertification_title_icon from 'src/assets/svg/home_page/desertification_title_icon.svg';
import soil_erosion_map from 'src/assets/svg/home_page/soil_erosion_map.svg';
import soil_erosion_title_icon from 'src/assets/svg/home_page/soil_erosion_title_icon.svg';
export default {
  computed: {
    indicators() {
      return [
        {
          image: sdg_indicator_map,
          title_icon: sdg_title_icon,
          title: this.$t('sdg_15_3_1.title'),
          description:this.$t('sdg_15_3_1.description'),
        },
        {
          image: forest_change_map,
          title_icon: forest_change_title_icon,
          title: this.$t('forest_change.title'),
          description:this.$t('forest_change.description'),
        },
        {
          image: veg_loss_map,
          title_icon: veg_loss_title_icon,
          title: this.$t('veg_loss.title'),
          description:this.$t('veg_loss.description'),
        },
        {
          image: coastal_erosion_map,
          title_icon: coastal_erosion_title_icon,
          title: this.$t('coastal_erosion.title'),
          description:this.$t('coastal_erosion.description'),
        },
        {
          image: desertification_map,
          title_icon: desertification_title_icon,
          title: this.$t('desertification.title'),
          description:this.$t('desertification.description'),
        },
        {
          image: soil_erosion_map,
          title_icon: soil_erosion_title_icon,
          title: this.$t('soil_erosion.title'),
          description:this.$t('soil_erosion.description'),
        },

      ]
    }
  }
}
</script>
<style lang="scss" scoped>
.indicator-card {
  background-color: #DFE8D1;
  border-radius: 21px;
  height: 100%;

  @media (min-width: $breakpoint-md-min) {
    max-width: 400px;
    // margin: 30px 0px;
  }

  @media (max-width: $breakpoint-sm-max) {}

}

.indicator-image-container {
  padding: 20px;
}

.indicator-image {
  width: 100%;
  max-height: 150px;
  object-fit: cover;
  border-radius: 20px;
}

.indicator-title-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 0px;
}

.indicator-title-icon {
  width: 30px;
  height: 40px;
}

.indicator-title {
  color: #697523;
  font-family: 'Inter';
  font-weight: 600;
  font-size: 22px;
  margin-left: 20px;
}

.indicator-description {
  padding: 20px 20px;
  color: #000000;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
}
</style>
