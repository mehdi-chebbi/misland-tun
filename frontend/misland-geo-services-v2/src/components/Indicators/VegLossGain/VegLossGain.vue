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
      <SelectionForm v-if="active_sub_indicator_value === 'vegetation_loss_gain'">
        <VegLossGain />
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
      active_sub_indicator_value: "vegetation_loss_gain", //holds the selected sub indicator
      active_button_icon: "", // holds the clicked button
      active_button_key: "", // holds  action button key either opacity, settings or visibility
      sub_indicators: {
        vegetation_loss_gain: { title: 'Vegetation Loss/Gain', value: 'vegetation_loss_gain', icons: { ...button_icons } },
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
    VegLossGain: defineAsyncComponent(() => import("src/components/Forms/VegetationLossGain/VegLossGain.vue")),
  },

  watch: {
    getQueuedResults: {
      immediate: true,
      deep: true,
      handler(val) {
        if (!val) return;
        const selected_sub_indicator = this.getQueuedResults?.args?.user_selections?.indicator_selections?.indicator?.value;
        if (process.env.DEV) console.log("veglossgain setActiveIndicator ", selected_sub_indicator);
        this.active_sub_indicator_value = selected_sub_indicator; // set the sub_indicator
        this.active_button_key = "settings" // set the action to show: settings opens up the form
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
    }

  }
}
</script>

<style lang="scss"></style>
