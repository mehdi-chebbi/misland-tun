import { defineStore } from 'pinia';


export const useGeometryStore = defineStore('geometry_store', {
  state: () => ({
    geomtry_data: "", //holds selected geometry
    custom_geometry_data: "",// holds selected custom geometry data
    rendered_geometry: "", // holds the currently displayed geometry
  }),
  getters: {
    getGeometryData: (state) => state.geomtry_data, // get  geometry data
    getCustomGeometryData: (state) => state.custom_geometry_data, // get custom geometry data
    getRenderedCustomGeometryData: (state) => state.rendered_geometry, // get rendered geometry data
  },
  actions: {
    // store the selected geometry data to the store
    setGeometryData(geomtry_data) {
      this.geomtry_data = geomtry_data;
      this.rendered_geometry = geomtry_data;
    },
    // store custom geometry data
    setCustomGeometryData(custom_geometry_data) {
      this.custom_geometry_data = custom_geometry_data;
      this.rendered_geometry = custom_geometry_data;
    }

  },
});


