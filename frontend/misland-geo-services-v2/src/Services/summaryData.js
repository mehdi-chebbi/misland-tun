//pinia
import { storeToRefs } from "pinia";
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // selected indicator store
const { getAnalysisResults } = storeToRefs(useAnalysisResultsStore()); // get analysis results
const { getIndicatorSelections } = storeToRefs(useIndicatorSelectionStore()); // get selected indicators


//  get the percentage  of a given value overally
const getPercentage = (value, results) => {
  results = results || getAnalysisResults.value.stats
  let total_area = undefined
  //get the results for land cover which is placed inside stats
  if (getIndicatorSelections.value?.indicator?.value === 'landcover') {
    results = getAnalysisResults.value.stats.stats[0].stats
    total_area = results.reduce((a, b) => a + +b.value, 0);
  } else {
    total_area = results.reduce((a, b) => a + +b.area, 0);
  }
  const percentage = ((value / total_area) * 100).toFixed(2);
  if (isNaN(percentage)) return "0%"; // return 0%  if value is not a number
  if (percentage < 1 && percentage > 0) return `<strong >(less than 1%) </strong>`; // if value less than 1 and greater than 0
  return `<strong >${percentage} % </strong>`; // return the actual percentage
};
// get the stat value given the change type or label
const getStatValue = ({ label, change_type, results }) => {
  results = results || getAnalysisResults.value.stats;
  //get the results for land cover which is placed inside stats
  if (getIndicatorSelections.value?.indicator?.value === 'landcover') {
    results = getAnalysisResults.value.stats.stats[0].stats
  }
  let stat = null
  // find stat value by change type
  if (change_type) {
    stat = results.find(result => result.change_type === change_type);
    if (stat) return stat.area || stat?.value
  }
  if (process.env.DEV) console.log("summary results ======= ", results,"getAnalysisResults ", getAnalysisResults.value);
  // find stat value by label
  if (label) {
    stat = results.find(result => result.label === label);
    if (stat) return stat.area || stat?.value
  }

}
export { getPercentage, getStatValue }


