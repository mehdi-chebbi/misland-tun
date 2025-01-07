<template>
  <div class="bg-white row  ">

    <!-- core team  -->
    <div class=" flex ">
      <div class="main-logo-container">
        <img src="~assets/png/core_team_logos/OSS.png" class="main-logo-sizes">
      </div>
      <div class="main-logo-container">
        <img src="~assets/png/core_team_logos/gmes.png" class="main-logo-sizes">
      </div>
      <div class="main-logo-container">
        <img src="~assets/png/core_team_logos/AU.png" class="main-logo-sizes">
      </div>
      <div class="main-logo-container">
        <img src="~assets/png/core_team_logos/EU.png" class="main-logo-sizes" style="width:60px">
      </div>
    </div>
    <q-separator vertical inset class="q-mx-sm" />
   <div class="full-width lt-md"> <q-separator inset class=" q-my-sm" /></div>
    <!-- partners -->
    <div class=" flex">
      <img src="~assets/png/partners/craste_lf.png" class="partner-logos">
      <img src="~assets/png/partners/crtean.png" class="partner-logos">
      <img src="~assets/png/partners/cnct.png" class="partner-logos">
      <img src="~assets/png/partners/dsc.png" class="partner-logos">
      <img src="~assets/png/partners/world.png" class="partner-logos">
      <img src="~assets/png/partners/una.png" class="partner-logos">
      <img src="~assets/png/partners/tanmiya.png" class="partner-logos">
    </div>
  </div>
</template>
<script>
export default {

}
</script>
<style lang="scss" scoped>
.partner-logos {
  width: 60px;
  object-fit: contain;
  @media (min-width: $breakpoint-md-min) {
    margin: 10px 30px;
  }
  @media (max-width: $breakpoint-sm-max) {
    margin: 0px 5px;
  }
}



.main-logo-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  @media (min-width: $breakpoint-md-min) {
    padding: 0px 20px;
  }
  @media (max-width: $breakpoint-sm-max) {
    width: 100%;

  }

}

.main-logo-sizes {
  object-fit: contain;
  @media (max-width: $breakpoint-sm-max) {
    width: 100%;
    padding: 0px 10px;
  }
}
</style>
