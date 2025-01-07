<template>
  <div class="baselayer-control gt-xs">
    <q-select borderless v-model="selected_base_layer" dense :options="baseLayers" behavior="menu"
    @update:model-value="showbaselayer" style="width:180px" >
      <template v-slot:prepend>
        <q-avatar class="q-ml-sm">
          <img src="~assets/png/basemaps/satellite.png">
        </q-avatar>
      </template>
      <template v-slot:selected-item="scope">
        <div class="q-ml-sm">{{ scope.opt }}</div>
      </template>
    </q-select>
  </div>
</template>
<script>
export default {
  props:{
    base_maps:[Object]
  },
  data() {
    return {
      selected_base_layer: "MapBoxSatellite"
    }
  },
  computed: {
    baseLayers() {
      if(!this.base_maps)return
      let base_maps=[];
      for(let [key, value] of  Object.entries(this.base_maps)){
        base_maps.push(key)
      }
      return base_maps
    }
  },
  methods:{
    showbaselayer(selected_base_layer){
      this.$emit('change_base_layer_event',selected_base_layer )
    }
  }
}
</script>
<style lang="scss">
.baselayer-control {
  position: absolute;
  right: 0;
  margin: 10px 30px 0px 0px;
  z-index: 500;
  background-color: white;
  border-radius: 10px;
  min-width: 150px;
}
</style>
