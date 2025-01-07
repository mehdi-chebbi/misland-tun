import { defineStore } from 'pinia';
import { api } from "src/boot/axios";

export const useComputationYearsStore = defineStore('computation_year_store', {
  state: () => ({
    computation_years: "", //holds the computation years
  }),
  getters: {
    getComputationYears: (state) => state.computation_years, // get computation years
  },
  actions: {
    // fetch computation years
    async fetchComputationYears(computation_type) {
      try {
        let computation_years = this.computation_years;
        if (computation_years) return filterYears({ computation_type, computation_years })
        const response = await api.get('/api/computationyears');
        this.computation_years = response.data
        computation_years = response.data
        return filterYears({ computation_type, computation_years })
      } catch (error) {
        if (process.env.DEV) console.log("fetchComputationYears error", error);
      }
    },

  },
});

const filterYears = ({ computation_type, computation_years }) => {
  let years = computation_years?.find(computation => computation.computation_type === computation_type);
  years = years?.published_years?.sort((a, b) => b - a)
  return years
}
