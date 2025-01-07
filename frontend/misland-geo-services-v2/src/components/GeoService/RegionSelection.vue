<template>
  <SelectionForm>
    <!-- region -->
    <div class="q-my-sm">
      <div class="">Region</div>
      <q-select
        v-model="selected_region"
        dense
        outlined
        :options="regions"
        clearable
        @clear="handleSelectedRegion"
        @update:model-value="handleSelectedRegion"
      ></q-select>
    </div>
    <!-- sub region -->
    <div class="q-my-sm">
      <div class="">Sub region</div>
      <q-select
        v-model="selected_sub_region"
        dense
        outlined
        :options="sub_regions"
        clearable
        @clear="handleSelectedSubRegion"
        @update:model-value="handleSelectedSubRegion"
      ></q-select>
    </div>
    <div class="q-mt-md flex justify-end">
      <q-btn unelevated color="primary" style="border-radius: 4px;" no-caps @click="fetchGeoJson">
        Load geometry
      </q-btn>
    </div>
  </SelectionForm>
</template>

<script>
import { defineAsyncComponent } from "vue";
import { useGeometryStore } from "src/stores/geometry_store";
const { setGeometryData } = useGeometryStore();

export default {
  data() {
    return {
      selected_country: {
        label: "Tunisia",
        value: 1,
        id: 1,
        gid_0: "TUN",
        name_0: "Tunisia",
        level: 0,
      }, // Preselected Tunisia
      selected_region: "",
      selected_sub_region: "",
      countries: [], // Optional: Keep for reference but not used
      regions: [], // Holds list of regions
      sub_regions: [], // Holds list of subregions
      current_geometry_selection: "", // Holds the currently selected
    };
  },
  components: {
    SelectionForm: defineAsyncComponent(() => import("src/components/Reusables/SelectionForm.vue")),
  },
  mounted() {
    // Fetch regions and subregions for Tunisia on mount
    this.fetchRegions();
  },
  methods: {
    // Fetch all regions within Tunisia
    async fetchRegions() {
      try {
        const response = await this.$api.get("/api/vect1/", {
          params: {
            pid: this.selected_country.value, // Preselected Tunisia ID
          },
        });
        this.regions = response.data?.map((region) => {
          return {
            label: region.name_1,
            value: region.id,
            ...region,
            level: 1,
          };
        });
        if (process.env.DEV) console.log("Regions of Tunisia: ", this.regions);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not get regions of Tunisia", error);
      }
    },
    // Fetch all subregions within a selected region
    async fetchSubregions() {
      try {
        const response = await this.$api.get("/api/vect2/", {
          params: {
            pid: this.selected_region.value, // Region ID
          },
        });
        this.sub_regions = response.data?.map((sub_region) => {
          return {
            label: sub_region.name_2,
            value: sub_region.id,
            ...sub_region,
            level: 2,
          };
        });
        if (process.env.DEV) console.log("Subregions: ", this.sub_regions);
      } catch (error) {
        if (process.env.DEV) console.log("ERROR: could not get subregions", error);
      }
    },
    // Handle the selected region within Tunisia
    handleSelectedRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_country;
        this.selected_sub_region = null;
        return;
      }
      this.fetchSubregions();
      this.selected_sub_region = null;
      this.current_geometry_selection = val;
    },
    // Handle the selected subregion within the selected region
    handleSelectedSubRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_region;
        return;
      }
      this.current_geometry_selection = val;
    },
    // Fetch the geometry
    async fetchGeoJson() {
      try {
        if (!this.current_geometry_selection) return;
        if (process.env.DEV)
          console.log("Current geometry selection: ", this.current_geometry_selection);
        const level = this.current_geometry_selection.level;
        const geometry_response = await this.$api.get(
          `/api/${this.adminLevel(level)}/${this.current_geometry_selection?.id}`
        );
        // Store the geometry in the store
        setGeometryData({
          geojson: geometry_response.data,
          ...this.current_geometry_selection,
          admin_level: level,
          admin_0: this.selected_country?.id,
          name: this.current_geometry_selection?.name,
          vector: this.current_geometry_selection.id,
        });
        this.$emit("close_region_selection_filter", true);
      } catch (error) {
        if (process.env.DEV) console.log("Error fetching geoJson: ", error);
      }
    },
    // Method to transform level to vector
    adminLevel(level) {
      if (level === 0) return "vect0";
      if (level === 1) return "vect1";
      if (level === 2) return "vect2";
    },
  },
};
</script>
