import { defineStore } from 'pinia';

export const useAnalysisResultsStore = defineStore('analysis_results_store', {
  state: () => ({
    results: "", //holds  analysis results
    queued_results: "", // holds the queued results
    reset_dashboard_results: false
  }),
  getters: {
    getAnalysisResults: (state) => state.results, // get analysis results
    getQueuedResults: (state) => state.queued_results, // get analysis results
    getResetResultsStatus: (state) => state.reset_dashboard_results, // get analysis results
  },
  actions: {
    // store the requested analysis results
    setAnalysisResults(results) {
      this.results = results
    },
    // store the scheduled task results
    setQueuedResults(queued_results) {
      this.queued_results = queued_results
      this.results = queued_results?.result
    },
    //store dashboard results
    resetResultsStatus(value) {
      this.reset_dashboard_results = value;
    },
  },
});


