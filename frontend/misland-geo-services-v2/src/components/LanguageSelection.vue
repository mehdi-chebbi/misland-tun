<template>
  <div class="">
    <q-select borderless v-model="selected_language" :options="languages" popup-content-class="language-selection-options"
      behavior="menu" @update:model-value="setLanguage" @popup-show="handle_arrow_icon(true)" @popup-hide="handle_arrow_icon(false)">
      <template v-slot:selected-item="scope">
        <div :class="selected_item_class">{{ scope.opt.label }}</div>
      </template>
      <!-- <template v-slot:prepend>
        <q-icon :name="arrow_type" />
      </template> -->
    </q-select>
  </div>
</template>

<script>
export default {
  props:{
     selected_item_class: [String]
  },
  data() {
    return {
      arrow_type: "keyboard_arrow_down",
      selected_language:{ label: "English", value: "en-us" },
      languages: [
        { label: "English", value: "en-US" },
        { label: "Français", value: "fr" },
      ],
    };
  },
  mounted() {
    // this.$q.iconSet.arrow.dropdown = "";
  },
  methods: {
    handle_arrow_icon(value) {
      this.arrow_type = value ? "keyboard_arrow_up" : "keyboard_arrow_down";
    },
    setLanguage(locale) {
      console.log(this.$i18n, "  ************ ", locale);
      this.$i18n.locale = locale.value;
      localStorage.setItem("language", JSON.stringify(locale));
    },
  },
};
</script>

<style lang="scss" scoped>
.header-grey-links {
  color: #4A5219;
}
.language-selected {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 20px;
}
</style>
