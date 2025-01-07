<template>
  <div class="">
    <q-select outlined class="bg-white search-admin-input" dense v-model="search_term" use-input
      :placeholder="search_term ? '' : 'Search country/region'"
      :options="search_results" input-debounce="500" behavior="menu" @filter="fetchOptions"
      @update:model-value="fetchGeoJson" popup-content-class="address-selections">
      <template v-slot:option="scope">
        <q-item v-bind="scope.itemProps">
          <div class="q-mr-sm">
            <q-icon name="place" color="grey" size="30px" />
          </div>
          <q-item-section>
            <q-item-label>{{ scope.opt.label }}</q-item-label>
            <q-item-label caption>{{ scope.opt.name }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-select>
  </div>
</template>

<script>
import axios from "axios"
import { negative } from 'src/Services/notifications'
import { storeToRefs } from "pinia";
import { useGeometryStore } from "src/stores/geometry_store";
const { getGeometryData } = storeToRefs(useGeometryStore()); // computation years store
const { setGeometryData } = useGeometryStore();

export default {
  data() {
    return {
      search_term: "", // holds the search term
      search_results: [], // holds the search results
      cancelToken: undefined, // cancel token for axios
    }
  },
  methods: {
    async fetchOptions(search_term, update) {
      if (search_term === '') {
        update();
        return;
      }

      const response = await this.searchRegion(search_term);
      if (!response?.success) return;

      // Filter the results to only include places related to Tunisia
      this.search_results = response.results?.filter(region => {
        // Check if the region name contains "Tunisia"
        return region.name.toLowerCase().includes("tunisia");
      }).map(region => {
        return {
          ...region,
          label: region?.name
        };
      });

      update();
    },

    // Make search per input
    async searchRegion(search_term) {
      try {
        if (search_term.length < 2) return;
        // Check if there are any previous pending requests
        if (typeof this.cancelToken != typeof undefined) {
          this.cancelToken.cancel("Operation canceled due to new request.");
        }
        // Save the cancel token for the current request
        this.cancelToken = axios.CancelToken.source();
        const response = await this.$api.get(`/api/search/`, {
          hide_loading_progress: true, // hide loading progress
          cancelToken: this.cancelToken.token,
          params: {
            query: search_term,
          }
        });
        return { results: response.data.data, success: true };
      } catch (error) {
        if (process.env.DEV) console.log("error searching region ", error);
        return { success: false };
      }
    },

    // Fetch the geometry
    async fetchGeoJson(selected_region) {
      try {
        if (!selected_region) return;
        const level = selected_region.level;
        const geometry_response = await this.$api.get(
          `/api/${this.adminLevel(level)}/${selected_region?.id}`
        );
        // Store the geometry in the store
        setGeometryData({
          geojson: geometry_response.data,
          ...selected_region,
          admin_level: level,
          name: selected_region?.name,
          vector: selected_region.id
        });
      } catch (error) {
        if (process.env.DEV) console.log("error fetching geoJson  ", error);
      }
    },

    // Method to transform level to vector
    adminLevel(level) {
      if (level === 0) return 'vect0';
      if (level === 1) return 'vect1';
      if (level === 2) return 'vect2';
    },
  }
}
</script>

<style lang="scss" scoped>
.search-admin-input {
  border-radius: 10px;
  width: 350px;
  padding: 0px;
}
</style>

<style lang="scss">
.address-selections {
  max-height: 350px;
  width: 350px;
}
</style>
