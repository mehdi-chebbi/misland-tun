import { api } from "src/boot/axios";
//pinia store stuff here
import { storeToRefs } from "pinia";
import { useGeometryStore } from "src/stores/geometry_store"; // geometry data store
import { useAnalysisResultsStore } from "src/stores/analysis_results_store"; // analysis results store
import { useIndicatorSelectionStore } from "src/stores/indicator_selection_store"; // user indicator selection store
import { negative, positive } from "./notifications";
const { getGeometryData, getCustomGeometryData } = storeToRefs(useGeometryStore()); // computation years store
const { getIndicatorSelections, getExpansionItems } = storeToRefs(useIndicatorSelectionStore()); // get selected gemotry data from the store store
//method to set analysis results to the store
const { setAnalysisResults } = useAnalysisResultsStore()

const token = localStorage.getItem("oss_auth_token");

// post request
const requestAnalysis = async ({ payload, uri, caller, indicator, hide_loading_progress = false }) => {
  try {
    const common_fields = processGeometryPayload()
    payload = {
      ...payload, ...common_fields,
      user_selections: {
        indicator_selections: getIndicatorSelections.value,
        expansion_items: getExpansionItems.value,
        geometry_data: getGeometryData.value,
        custom_geometry_data: getCustomGeometryData.value
      }
    }
    const response = await api.post(uri, payload, {
      headers: {
        Authorization: token ? "Bearer " + token : "",
      },
      hide_loading_progress, // hide loading progress
    });

    if (process.env.DEV) console.log("Analysis response ", response.data);
    //check if we have error or success  is false
    if (response.data.error || response.data.success === "false") return negative({
      message: response.data.error || response.data.message,
      position: "center",
      multiLine: true,
      color: "red"
    });
    // check if response is a message
    if (response.data.hasOwnProperty('message')) return positive({
      message: response.data.message,
      color: 'green',
      position: 'center'
    })
    setAnalysisResults({ ...response.data, indicator }); // set the analysis results to the store
    return response.data

  } catch (error) {
    if (process.env.DEV) console.log("Caller:", caller, " resquest analysis error ", error);
    negative({
      message: "There was an error while making analysis request",
      position: 'center',
      time: 3000,
    })
  }
}
// get request
const get = async ({ query, url }) => {
  try {

  } catch (error) {

  }
}
// process common geometry fields
const processGeometryPayload = () => {
  const custom = getCustomGeometryData.value?.custom
  // let custom =  {"type":"Polygon","coordinates":[[[10.150595,36.885868],[10.148449,36.879209],[10.155916,36.880239],[10.15789,36.887653],[10.150595,36.885868]]]}
  //   custom =  JSON.stringify(custom)
  const { geojson, name, ...geometry_request_payload } = getGeometryData.value
  return {
    custom_coords: custom ? custom : undefined,
    admin_0: getGeometryData.value?.admin0,
    ...geometry_request_payload,
  }
}

export { requestAnalysis, get }
