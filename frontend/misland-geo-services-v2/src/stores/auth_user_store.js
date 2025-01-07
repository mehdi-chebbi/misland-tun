import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';


export const useAuthUserStore = defineStore('auth_user_store', {
  state: () => ({
    auth_user_details: "", //holds authenticated user's details
  }),
  getters: {
    getAuthUserDetails: (state) => state.auth_user_details, // get auth user details
  },
  actions: {
    // fetch auth user details
    async fetchAuthUserDetails() {
      const token = localStorage.getItem('oss_auth_token');
      if(!token) return
      try {
        const response = await api.get("/api/user/", {
          headers: {
            Authorization: token ? `Bearer ${token}` : ''
          }
        });
        this.auth_user_details = response.data.data[0]
      } catch (error) {
        localStorage.removeItem('oss_auth_token')
        if (process.env.DEV) console.log("Error fetching auth  user details ", error);
      }
    },
  },
});


