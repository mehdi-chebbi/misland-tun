import { defineStore } from 'pinia';
import { api } from "src/boot/axios";

export const usePrecomputationYearsStore = defineStore('precomputation_year_store', {
  state: () => ({
    precomputation_years: "", //holds the computation years
  }),
  getters: {
    getPrecomputationYears: (state) => state.precomputation_years, // get computation years
  },
  actions: {
    // fetch computation years
    async fetchPrecomputationYears(computation_type) {
      try {
        let precomputation_years = this.precomputation_years;
        if (precomputation_years) return filterYears({ computation_type, precomputation_years })
        const response = await api.get('/api/precomputations');
        this.precomputation_years = response.data
        precomputation_years = response.data
        return filterYears({ computation_type, precomputation_years })
      } catch (error) {
        if (process.env.DEV) console.log("fetchPrecomputationYears error", error);
      }
    },

  },
});

const filterYears = ({ computation_type, precomputation_years }) => {
  let years = precomputation_years?.find(computation => computation.computation_type === computation_type);
  years = years?.published_years?.sort((a, b) => b - a)
  return years
}
