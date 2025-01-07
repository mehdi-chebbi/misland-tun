<template>
  <div class="cursor-pointer flex" @click="showStatistics">
    <img src="~assets/png/chart_icons/chart.png" style="width:30px">
    <div class="statistics-label">Statistics</div>
  </div>
</template>
<script>
export default {
  props:{
    statistics_data:[String, Object]
  },
methods:{
  showStatistics(){
 if(!this.statistics_data) return
 this.$emit('show_statistics_component')
  }
}
}
</script>
<style lang="scss" scoped>
.statistics-label {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 16px;
  color: #838C48;
  margin-left: 10px;
}
</style>
