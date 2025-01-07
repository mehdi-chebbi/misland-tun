<template >
  <div class="zoom-control">
   <div class="cursor-pointer q-pa-xs"  @click="zoomIn">
    <img src="~assets/svg/map_tools/zoom_in.svg" class="">
   </div>
   <div class="q-pa-xs cursor-pointer" @click="zoomOut">
    <img src="~assets/svg/map_tools/zoom_out.svg"  >
   </div>
  </div>
</template>
<script>
export default {
 methods:{
  zoomIn(){
    this.$emit('zoom_in_event')
  },
  zoomOut(){
    this.$emit('zoom_out_event')
  },
 }
}
</script>
<style lang="scss" scoped>
.zoom-control {

  border-radius: 10px;
  padding:5px;
  background-color: white;
}
</style>

