<template>
  <div class="">
    <div class="indicator-expansion-container bg-white">
      <!----------------------------------------- SDG INDICATORS ----------------------------------------------->
      <q-expansion-item group="indicatorgroup" v-model="indicator_expansions.expand_sdg"
        @update:model-value="updateUserSelection">
        <template v-slot:header>
          <q-item-section avatar>
            <img src="~assets/svg/indicators/SDG.svg" alt="" srcset="">
          </q-item-section>
          <q-item-section class="indicator-header">
            SDG
          </q-item-section>
        </template>
        <q-card>
          <SDG />
        </q-card>
      </q-expansion-item>
      <q-separator />
      <!---------------------------------------- VEGETATION LOSS GAIN INDICATORS ----------------------------------->
      <q-expansion-item group="indicatorgroup" v-model="indicator_expansions.expand_veg_loss_gain"
        @update:model-value="updateUserSelection">
        <template v-slot:header>
          <q-item-section avatar>
            <img src="~assets/svg/indicators/veg.svg" alt="" srcset="">
          </q-item-section>
          <q-item-section class="indicator-header">
            {{ $t('main_indicators.veg_loss_gain') }}
          </q-item-section>
        </template>
        <q-card>
          <VegLossGain />
        </q-card>
      </q-expansion-item>
      <q-separator />
      <!---------------------------------------- FOREST CHANGE INDICATORS ----------------------------------->
      <q-expansion-item group="indicatorgroup" v-model="indicator_expansions.expand_forest_change"
        @update:model-value="updateUserSelection">
        <template v-slot:header>
          <q-item-section avatar>
            <img src="~assets/svg/indicators/forest_change.svg" alt="" srcset="">
          </q-item-section>
          <q-item-section class="indicator-header">
            {{ $t('main_indicators.forest_change') }}
          </q-item-section>
        </template>
        <q-card>
          <ForestChange />
        </q-card>
      </q-expansion-item>
      <q-separator />
      <!---------------------------------------- DESERT INDICATORS ----------------------------------->
      <q-expansion-item group="indicatorgroup" v-model="indicator_expansions.expand_desert"
        @update:model-value="updateUserSelection">
        <template v-slot:header>
          <q-item-section avatar>
            <img src="~assets/svg/indicators/desert.svg" alt="" srcset="">
          </q-item-section>
          <q-item-section class="indicator-header">
            {{ $t('main_indicators.desert') }}
          </q-item-section>
        </template>
        <q-card>
          <Desert />
        </q-card>
      </q-expansion-item>
      <q-separator />

      <!---------------------------------------- SOIL EROSION INDICATORS ----------------------------------->
      <q-expansion-item group="indicatorgroup" v-model="indicator_expansions.expand_soil_erosion"
        @update:model-value="updateUserSelection">
        <template v-slot:header>
          <q-item-section avatar>
            <img src="~assets/svg/indicators/soil_erosion.svg" alt="" srcset="">
          </q-item-section>
          <q-item-section class="indicator-header">
            {{ $t('main_indicators.soil_erosion') }}
          </q-item-section>
        </template>
        <q-card>
          <SoilErosion />
        </q-card>
      </q-expansion-item>
      <q-separator />
      <!---------------------------------------- SOIL EROSION INDICATORS ----------------------------------->
      <q-expansion-item group="indicatorgroup" v-model="indicator_expansions.expand_coastal_erosion"
        @update:model-value="updateUserSelection">
        <template v-slot:header>
          <q-item-section avatar>
            <img src="~assets/svg/indicators/coastal.svg" alt="" srcset="">
          </q-item-section>
          <q-item-section class="indicator-header">
            {{ $t('main_indicators.coastal_erosion') }}
          </q-item-section>
        </template>
        <q-card>
          <CoastalErosion />
        </q-card>
      </q-expansion-item>
    </div>
  </div>
</template>
<script>
import { defineAsyncComponent } from "vue";
//pinia
import { storeToRefs } from "pinia";
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // user indicator selection store
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
const { getQueuedResults } = storeToRefs(useAnalysisResultsStore()); // get chart data from store
const { setExpansionItemSelections } = useIndicatorSelectionStore(); // action to set user form selections to the store
export default {
  props: {
    active_indicator_selection: String, // holds the selected expansion item name
  },
  data() {
    return {
      indicator_expansions: {
        expand_sdg: false,
        expand_veg_loss_gain: false,
        expand_forest_change: false,
        expand_coastal_erosion: false,
        expand_desert: false,
        expand_soil_erosion: false,
      }
    }
  },
  computed: {
    // get queued results from the store
    getQueuedResults() {
      return getQueuedResults.value
    }
  },
  components: {
    SDG: defineAsyncComponent(() => import('src/components/Indicators/SDG/SDG.vue')),
    VegLossGain: defineAsyncComponent(() => import('src/components/Indicators/VegLossGain/VegLossGain.vue')),
    CoastalErosion: defineAsyncComponent(() => import('src/components/Indicators/CoastalErosion/CoastalErosion.vue')),
    ForestChange: defineAsyncComponent(() => import('src/components/Indicators/ForestChange/ForestChange.vue')),
    Desert: defineAsyncComponent(() => import('src/components/Indicators/Desert/Desert.vue')),
    SoilErosion: defineAsyncComponent(() => import('src/components/Indicators/SoilErosion/SoilErosion.vue')),
  },
  watch: {
    active_indicator_selection: {
      handler(val) {
        if (!val) return;
        this.indicator_expansions[val] = true
      }
    },
    getQueuedResults: {
      immediate: true,
      deep:true,
      handler(val) {
        if (!val) return;
        const expansion_items = val?.args?.user_selections?.expansion_items;
        let selected_expansion_items;
        console.log("get queued results indicator selection ", val, "selected_expansion_items ", expansion_items);
        for (const [key, value] of Object.entries(expansion_items)) {
          if (value) {
            selected_expansion_items = key
            break
          }
        }
        this.indicator_expansions[selected_expansion_items] = true
      }
    }
  },
  methods: {
    // save  the expansion items to store
    updateUserSelection() {
      console.log("update user selection  ========= ", this.indicator_expansions);
      setExpansionItemSelections(this.indicator_expansions)
    }
  },
}
</script>
<style lang="scss" scoped>
.indicator-menu-label {
  margin-left: 10px;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 12px;
  line-height: 15px;
  color: #000000;

}

.indicator-expansion-container {
  background-color: #FFFFFF;
  border: 0.5px solid #CCCCCC;
  box-shadow: 0px 1.4px 3px rgba(0, 0, 0, 0.1);
  border-radius: 11px;
  padding: 10px;

  @media (min-width: $breakpoint-sm-min) {
    width: 350px;
  }

  @media (max-width: $breakpoint-xs-max) {
    width: 85vw;
    margin: auto;
  }
}

.indicator-header {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 12px;
  color: #838C48;
  line-height: 124.02%;
}
</style>

<style></style>
