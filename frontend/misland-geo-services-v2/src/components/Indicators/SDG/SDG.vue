<template>
  <div class="flex">
    <q-list dense padding class="rounded-borders">
      <q-item clickable v-for="(sub_indicator, index) in sub_indicators" :key="index"
        @click="active_sub_indicator_value = sub_indicator.value">
        <q-item-section>
          <div class="indicator-title"
            :class="active_sub_indicator_value === sub_indicator?.value ? '' : 'text-grey-5'">
            {{ sub_indicator?.title }}</div>
        </q-item-section>
        <q-item-section top side>
          <div class="q-gutter-xs ">
            <q-btn flat round dense v-for="([key, value], i) in Object.entries(sub_indicator.icons)" :key="i">
              <img :src="setIcon(sub_indicator?.value, value)" style="width:25px"
                @click="setActiveButton(sub_indicator.value, value, key)">
            </q-btn>
          </div>
        </q-item-section>
      </q-item>
    </q-list>
    <!------------------------------------- show  form for the selected indicator ------------------------------------->
    <div class="" v-if="active_button_key === 'settings'">
      <!------------------------------------- land cover form ------------------------------------->
      <SelectionForm v-if="active_sub_indicator_value === 'landcover'">
        <LandCoverForm />
      </SelectionForm>
      <!------------------------------------- land productivity form ------------------------------------->
      <SelectionForm v-if="active_sub_indicator_value === 'land_productivity'">
        <LandProductivityForm />
      </SelectionForm>
      <!------------------------------------- carbon stock form ------------------------------------->
      <SelectionForm v-if="active_sub_indicator_value === 'carbon_Stock_Change'">
        <CarbonStockForm />
      </SelectionForm>
      <!------------------------------------- sdg indicator form ------------------------------------->
      <SelectionForm v-if="active_sub_indicator_value === 'land_degradation'">
        <SDGIndicatorForm />
      </SelectionForm>

    </div>

  </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
// unselected button images
import unselected_opacity from "src/assets/svg/indicators/action_icons/opacity_unselected.svg"
import unselected_settings from "src/assets/svg/indicators/action_icons/settings_unselected.svg"
import unselected_eye from "src/assets/svg/indicators/action_icons/eye_unselected.svg"
// selected button images
import selected_opacity from "src/assets/svg/indicators/action_icons/opacity.svg"
import selected_settings from "src/assets/svg/indicators/action_icons/settings.svg"
import selected_eye from "src/assets/svg/indicators/action_icons/eye.svg"
// active buttons
import active_opacity from "src/assets/svg/indicators/action_icons/active_opacity.svg"
import active_settings from "src/assets/svg/indicators/action_icons/active_settings.svg"
import active_eye from "src/assets/svg/indicators/action_icons/active_eye.svg"
//pinia
import { storeToRefs } from "pinia";
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
const { getQueuedResults } = storeToRefs(useAnalysisResultsStore()); // get chart data from store
const button_icons = {
  opacity: {
    selected: selected_opacity,
    unselected: unselected_opacity,
    active: active_opacity,
  },
  settings: {
    selected: selected_settings,
    unselected: unselected_settings,
    active: active_settings,
  },
  eye: {
    selected: selected_eye,
    unselected: unselected_eye,
    active: active_eye,

  },
}
export default {
  data() {
    return {
      active_sub_indicator_value: "landcover", //holds the selected sub indicator
      active_button_icon: "", // holds the clicked button
      active_button_key: "", // holds  action button key either opacity, settings or visibility
      sub_indicators: {
        land_productivity: {
          title: 'Land Productivity', value: 'land_productivity', icons: { ...button_icons }
        },
        landcover: { title: 'Land Cover', value: 'landcover', icons: { ...button_icons } },
        carbon_Stock_Change: { title: 'Carbon Stock', value: 'carbon_Stock_Change', icons: { ...button_icons } },
        land_degradation: { title: 'SDG Indicator', value: 'land_degradation', icons: { ...button_icons } },
      },
    }
  },
  computed: {
    // get queued results from the store
    getQueuedResults() {
      return getQueuedResults.value
    }
  },
  components: {
    SelectionForm: defineAsyncComponent(() => import('src/components/Reusables/SelectionForm.vue')),
    LandCoverForm: defineAsyncComponent(() => import("src/components/Forms/SDG/LandCoverForm.vue")),
    LandProductivityForm: defineAsyncComponent(() => import("src/components/Forms/SDG/LandProductivityForm.vue")),
    CarbonStockForm: defineAsyncComponent(() => import("src/components/Forms/SDG/CarbonStockForm.vue")),
    SDGIndicatorForm: defineAsyncComponent(() => import("src/components/Forms/SDG/SDGIndicatorForm.vue")),
  },

  watch: {
    getQueuedResults: {
      immediate: true,
      deep: true,
      handler(val) {
        if (!val) return;
        this.setActiveSubIndicator()
      }
    }
  },
  methods: {
    // process the icon to show
    setIcon(sub_indicator_value, icon) {
      if (sub_indicator_value === this.active_sub_indicator_value) {
        if (this.active_button_icon === icon.active) return icon.active;
        return icon.selected;
      }
      return icon.unselected
    },
    // set the active button
    setActiveButton(sub_indicator_value, icon_value, icon_key) {
      this.active_sub_indicator_value = sub_indicator_value
      this.active_button_icon = icon_value.active;
      this.active_button_key = icon_key
    },
    // set the selected sub indicator
    setActiveSubIndicator() {
      const selected_sub_indicator = this.getQueuedResults?.args?.user_selections?.indicator_selections?.indicator?.value;
      if (process.env.DEV) console.log(" sdg setActiveIndicator ", selected_sub_indicator);
      this.active_sub_indicator_value = this.handeSubIndicators(selected_sub_indicator); // set the sub_indicator
      this.active_button_key = "settings" // set the action to show: settings opens up the form
    },
    // handle land productivity
    handeSubIndicators(selected_sub_indicator) {
      const land_productivity_sub_indicators = ['trajectory', 'state', 'performance', 'productivity']; // land productivity
      const land_cover_sub_indicators = ['land_cover_change', 'landcover']
      //check if land productivity
      if (land_productivity_sub_indicators.includes(selected_sub_indicator)) {
        return 'land_productivity'
      }
      //check land cover
      if (land_cover_sub_indicators.includes(selected_sub_indicator)) {
        return 'landcover'
      }
      return selected_sub_indicator
    },
  }
}
</script>

<style lang="scss"></style>
