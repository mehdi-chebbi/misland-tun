import { boot } from 'quasar/wrappers'
import axios from 'axios'
import { Loading, QSpinnerGears } from "quasar";

let baseURL;
if (process.env.DEV) {
  // baseURL = 'http://41.227.30.139:1337/' //oss
 // baseURL = 'http://41.227.30.136:1337/' //oss
  baseURL = 'http://192.168.127.133:8000/'
  // baseURL = 'http://misland.oss-online.org:1337/' //oss
  // baseURL = 'http://194.163.176.189:1337/' //contabo
}
else {
  baseURL = 'http://41.227.30.136:1337/' //oss
  // baseURL = 'http://194.163.176.189:1337/' //contabo
  // baseURL = 'http://41.227.30.139:1337/' //oss
  // baseURL = 'http://misland.oss-online.org:1337/' //oss
}

const api = axios.create({ baseURL })

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api;

  //check request
  let pending_requests = 0;
  api.interceptors.request.use((config) => {

    const hide_loading_progress = config.hide_loading_progress; //check if loader is shown or hidden
    pending_requests++;
    if (!hide_loading_progress) Loading.show({
      spinner: QSpinnerGears,
      // message: "Requesting ...",
      spinnerColor: "primary"
    });
    return config;
  }, (error) => {
    pending_requests--;
    setTimeout(() => {
      Loading.hide();
    }, 1000)
    return Promise.reject(error);
  });
  //check response
  api.interceptors.response.use((config) => {
    pending_requests--;
    if (pending_requests <= 0) {
      setTimeout(() => {
        Loading.hide();
      }, 1000)
    }
    return config;
  }, (error) => {

    pending_requests--;
    if (pending_requests <= 0) {
      setTimeout(() => {
        Loading.hide();
      }, 1000)
    }
    return Promise.reject(error);
  });


})

export { api, baseURL }
