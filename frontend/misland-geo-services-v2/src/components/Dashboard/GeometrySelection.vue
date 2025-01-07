<template>
  <div class="geometry-selection-container flex items-center">
    <h2 class="dashboard-title">Dashboard for Tunisia</h2>

    <!-- Region within Tunisia selection -->
    <q-select
      borderless
      v-model="selected_region"
      :options="regions"
      use-input
      clearable
      :placeholder="selected_region ? '' : 'Region'"
      @update:model-value="handleSelectedRegion"
      popup-content-class="geometry-popup-class"
      behavior="menu"
      class="geometry-selection"
    ></q-select>

    <!-- Sub-region within a region selection -->
    <q-select
      borderless
      v-model="selected_sub_region"
      :options="sub_regions"
      use-input
      clearable
      :placeholder="selected_sub_region ? '' : 'Sub Region'"
      @update:model-value="handleSelectedSubRegion"
      popup-content-class="geometry-popup-class"
      behavior="menu"
      class="geometry-selection"
    ></q-select>

    <!-- Submit button -->
    <q-btn
      :disable="loading"
      :loading="loading"
      color="primary"
      label="Submit"
      @click="fetchGeoJson"
      class="geometry-submit-button"
    ></q-btn>
  </div>
</template>

<script>
import { useGeometryStore } from "src/stores/geometry_store";

export default {
  data() {
    return {
      selected_region: null,
      selected_sub_region: null,
      current_geometry_selection: null,
      regions: [],
      sub_regions: [],
      loading: false, // Loading state for Submit button
      country_tunisia: {
        label: "Tunisia",
        value: 1,
        id: 1,
        gid_0: "TUN",
        name_0: "Tunisia",
        level: 0,
      }, // Tunisia pre-defined
    };
  },
  mounted() {
    this.fetchRegions(); // Fetch Tunisia's regions on mount
    this.fetchInitialGeoJson(); // Fetch GeoJSON for Tunisia initially
  },
  methods: {
    async fetchRegions() {
      try {
        const response = await this.$api.get("/api/vect1/", {
          params: { pid: this.country_tunisia.value },
        });

        this.regions = response.data?.map((region) => ({
          label: region.name_1,
          value: region.id,
          ...region,
          level: 1,
        }));
      } catch (error) {
        console.error("ERROR: could not fetch regions", error);
      }
    },
    async fetchSubregions() {
      try {
        const response = await this.$api.get("/api/vect2/", {
          params: { pid: this.selected_region?.value },
        });

        this.sub_regions = response.data?.map((sub_region) => ({
          label: sub_region.name_2,
          value: sub_region.id,
          ...sub_region,
          level: 2,
        }));
      } catch (error) {
        console.error("ERROR: could not fetch subregions", error);
      }
    },
    handleSelectedRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.country_tunisia;
        this.sub_regions = [];
        return;
      }

      this.fetchSubregions();
      this.selected_sub_region = null;
      this.current_geometry_selection = val;
    },
    handleSelectedSubRegion(val) {
      if (!val) {
        this.current_geometry_selection = this.selected_region;
        return;
      }

      this.current_geometry_selection = val;
    },
    adminLevel(level) {
      if (level === 0) return "vect0";
      if (level === 1) return "vect1";
      if (level === 2) return "vect2";
    },
    async fetchInitialGeoJson() {
      // Fetch GeoJSON for Tunisia when the component is mounted
      try {
        this.loading = true;
        const geometry_response = await this.$api.get(
          `/api/vect0/${this.country_tunisia.id}`
        );

        useGeometryStore().setGeometryData({
          geojson: geometry_response.data,
          ...this.country_tunisia,
          admin_level: 0,
          admin_0: this.country_tunisia?.id,
          name: this.country_tunisia?.label,
          vector: this.country_tunisia.id,
        });
      } catch (error) {
        console.error("ERROR: could not fetch GeoJSON for Tunisia", error);
      } finally {
        this.loading = false;
      }
    },
    async fetchGeoJson() {
    // Validate region and sub-region selection
    if (!this.selected_region) {
      this.$q.notify({
        type: "negative",
        message: "Please select a region.",
        position: "top",
        timeout: 3000,
      });
      return;
    }

    if (!this.selected_sub_region) {
      this.$q.notify({
        type: "negative",
        message: "Please select a sub-region.",
        position: "top",
        timeout: 3000,
      });
      return;
    }

    try {
      this.loading = true;
      const level = this.current_geometry_selection.level;
      const geometry_response = await this.$api.get(
        `/api/${this.adminLevel(level)}/${this.current_geometry_selection?.id}`
      );

      useGeometryStore().setGeometryData({
        geojson: geometry_response.data,
        ...this.current_geometry_selection,
        admin_level: level,
        admin_0: this.country_tunisia?.id,
        name: this.current_geometry_selection?.label,
        vector: this.current_geometry_selection.id,
      });
    } catch (error) {
      console.error("ERROR: could not fetch GeoJSON", error);
    } finally {
      this.loading = false;
    }
  },
  },
};
</script>


<style lang="scss" scoped>
.geometry-selection-container {
  background: #f8f9f4;
  border-radius: 12px;
  padding: 0px 10px;
  color: #a8af7f;
  width: 100%;
}

.geometry-selection {
  flex: 1;
  padding: 0;
}

.geometry-submit-button {
  margin-left: 10px;
  padding: 5px 15px;
  font-family: "Inter";
  font-size: 14px;
  font-weight: 500;
  background: #007bff; /* Customize button color */
  color: #ffffff;
  border-radius: 8px;
}

.geometry-popup-class {
  color: #a8af7f;
  font-family: "Inter";
  font-size: 16px;
}

.selected-geometry-class {
  color: #a8af7f;
  font-family: "Inter";
  font-size: 16px;
  font-weight: 500;
}
.dashboard-title {
margin-left: 90px;
    font-weight: bold;
}

</style>
