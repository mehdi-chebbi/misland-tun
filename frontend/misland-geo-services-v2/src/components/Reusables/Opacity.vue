<template>
  <div class="opacity-control cursor-pointer q-pa-xs">
    <div class="flex">
      <div class="flex items-center q-mr-xs">
        <img src="~assets/svg/opacity.svg" alt="">
      </div>
      <div class="q-mx-xs flex items-center q-pr-md " style="flex:1">
        <q-slider color="black" v-model="opacity_value" :min="0" :max="10" style="width:100%" @update:model-value="updateOpacity" />
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      opacity_value: 100
    }
  },
  methods:{
    updateOpacity(value){
      console.log("opacity slider value ", value);
      this.$emit('change_layer_opacity_value', value)
    }
  }
}
</script>
<style lang="scss" scoped>
.opacity-control {
  position: absolute;
  right: 0;
  margin: 10px 280px 0px 0px;
  z-index: 500;
  background-color: white;
  width: 200px;
  border-radius: 10px;
}
</style>
