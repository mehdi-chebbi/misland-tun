<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import { negative, positive } from "src/Services/notifications"
//pinia
import { storeToRefs } from "pinia";
import { useAuthUserStore } from "src/stores/auth_user_store"; // auth user store
const { getAuthUserDetails } = storeToRefs(useAuthUserStore()); // get authenticated user from store
const { fetchAuthUserDetails } = useAuthUserStore()
export default {
  name: 'MainLayout',
  data() {
    return {

      language: "English", // holds the selected language
    }
  },

  computed: {
    getCurrentRoute() {
      return this.$route.params;
    },
    getAuthUserDetails() {
      return getAuthUserDetails.value
    },
  },
  components:{
    HomePageNav: defineAsyncComponent(()=>import("src/components/HomePage/NavBar.vue"))
  },
  watch: {
    getCurrentRoute: {
      immediate: true,
      handler(val) {
        if (!val) return;
        const action = val.action
        if (action === 'activate') return this.activate();// run user account activation
      }
    }
  },
  mounted() {
    // fetch authenticated user
    fetchAuthUserDetails()
  },
  methods: {
    toggleLeftDrawer() {
      this.left_drawer_open = !this.left_drawer_open
    },
    // activate user account
    async activate() {
      try {
        const { action, code, token } = this.getCurrentRoute;
        if (action != "activate") return;
        const response = await this.$api.get(
          `/api/${action}/${code}/${token}`
        );
        positive({
          message: response.data.message,
          position: "center",
          multiLine: true,
          color: "green"
        });
        this.$router.push("/geoservice");
      } catch (error) {
        if (process.env.DEV) console.log("Error: Could not activate user ",  error.response.data);
        let message= "Error: could not activate user"
        if(error.response.data?.message) {
          message = error.response.data.message
        }
        negative({
          message:message,
          position: "center",
          multiLine: true,
          color: "red"
        });
      }
    },
    // logout logged in user
    logout() {
      localStorage.removeItem("oss_auth_token");
      location.reload();
    },
  }
}
</script>

<style lang="scss" scoped>
.header-grey-links {
  color: #4A5219;
}

.gt-1280 {
  @media (max-width: 1279px) {
    display: none;
  }
}

.lt-1280 {
  @media (min-width: 1280px) {
    display: none;
  }
}

.show-more-btn-label {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 10px;
  line-height: 12px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #404715;
}



.tool-bar {
  // background: #FFFFFF;
  // border: 1px solid #A3B2CA;
}

.login-button {
  background-color: #74B281;
  border-radius: 10px;

  @media (min-width: $breakpoint-md-min) {}

  @media (max-width: $breakpoint-sm-max) {
    width: 150px
  }
}

.tool-bar-link {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 20px;
  letter-spacing: -0.02em;
  text-decoration: none;

}


</style>


<style lang="scss">
.language-selection-options {
  font-family: 'Inter';
  font-weight: 400;
  font-size: 16px;
  letter-spacing: -0.02em;
}
</style>
