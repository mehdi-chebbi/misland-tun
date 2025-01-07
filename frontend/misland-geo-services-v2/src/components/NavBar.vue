<template>
  <q-header>
    <q-toolbar class="tool-bar bg-white q-py-sm">
      <div class="flex items-center">
        <div class="flex items-center" style="padding-right:46px">
          <img src="~assets/svg/misland_logo.svg" alt="">
          <div class="misland_title text-primary"> {{ $t("logo.title") }}</div>
        </div>
        <div class="q-mx-md gt-xs">
          <img src="~assets/svg/oss_logo.svg" style="width: 85px">
        </div>
        <div class="q-mx-md gt-xs">
          <img src="~assets/svg/gmes_logo.svg" style="width: 121.8px;height: 34.08px;">
        </div>
      </div>
      <q-space />
      <div class="flex items-center">

        <router-link to="/" :active-class="routeName === 'home' ? 'text-green-5' : ''"
          class="q-mx-md  gt-1280 tool-bar-link header-grey-links">{{
            $t("nav_bar.home") }} </router-link>

        <router-link to="/dashboard" exact :active-class="routeName === 'dashboard' ? 'text-green-5' : ''"
          class="q-mx-md  gt-1280 tool-bar-link header-grey-links">{{
            $t("nav_bar.dashboard") }}</router-link>

        <router-link to="/geoservice" :active-class="routeName === 'geoservice' ? 'text-green-5' : ''" exact
          class="q-mx-md  gt-1280 tool-bar-link header-grey-links">{{ $t("nav_bar.geo_service") }}</router-link>

        <router-link to="/mapographics" :active-class="routeName === 'mapographics' ? 'text-green-5' : ''"
          class="q-mx-md  gt-1280 tool-bar-link header-grey-links header-grey-links">{{ $t("nav_bar.mapographics")
          }}</router-link>
        <router-link to="/privacy-policy" :active-class="routeName === 'privacy-policy' ? 'text-green-5' : ''"
          class="q-mx-md  gt-1280 tool-bar-link header-grey-links header-grey-links">{{
            $t("nav_bar.privacy_policy")
          }}</router-link>

        <!-- select language selection -->
        <div class="q-mx-xs">
          <LanguageSelection :selected_item_class="'language-selected header-grey-links'" />
        </div>
        <div class="q-mx-md  gt-1280">
          <q-btn unelevated no-caps class="login-button" to="/login" v-show="!getAuthUserDetails">Login</q-btn>
          <div class="q-pa-xs" v-show="getAuthUserDetails">
            <router-link to="/profile" class="no-link-decoration text-h6 header-grey-links"> Hello, <span
                class="text-capitalize"> {{ getAuthUserDetails?.first_name }}</span></router-link>
          </div>
        </div>
        
      </div>
      <div class="lt-1280">
        <q-btn flat dense round color="black" aria-label="Menu" @click="toggleLeftDrawer">
          <!-- <div class="q-mr-sm show-more-btn-label">More</div> -->
          <q-icon name="menu" />
        </q-btn>
      </div>
    </q-toolbar>
  </q-header>
  <!--------------------------------------- show drawer for screens below 1280 ----------------------------------------------->
  <q-drawer v-model="left_drawer_open" :breakpoint="1280" side="right">
    <div class="q-pl-lg column">
      <div class="flex column">
        <div class="q-my-lg">
          <q-btn unelevated no-caps class="login-button" to="/login" v-show="!getAuthUserDetails">Login</q-btn>
          <div class="q-pa-xs" v-show="getAuthUserDetails">
            <router-link to="/profile" class="no-link-decoration text-h6 header-grey-links"> Hello, <span
                class="text-capitalize"> {{ getAuthUserDetails?.first_name }}</span></router-link>
          </div>
        </div>
        <router-link to="/" class=" tool-bar-link header-grey-links q-my-lg"
          :active-class="routeName === 'home' ? 'text-green-5' : ''">Home</router-link>
        <!-- <router-link to="/" class=" tool-bar-link header-grey-links q-my-lg">Dashboard</router-link> -->
        <router-link to="/geoservice" class="q-my-lg tool-bar-link header-grey-links"
          :active-class="routeName === 'geoservice' ? 'text-green-5' : ''">Geo-Service</router-link>

        <router-link to="/dashboard" class=" tool-bar-link q-my-lg header-grey-links"
          :active-class="routeName === 'dashboard' ? 'text-green-5' : ''">Dashboard</router-link>
        <router-link to="/mapographics" class=" tool-bar-link q-my-lg header-grey-links"
          :active-class="routeName === 'mapographics' ? 'text-green-5' : ''">Mapographics</router-link>
        <router-link to="//privacy-policy" class=" tool-bar-link q-my-lg header-grey-links"
          :active-class="routeName === 'privacy-policy' ? 'text-green-5' : ''">Privacy policy</router-link>
          <a href="" target="blank" class="tool-bar-link q-my-lg header-grey-links" no-caps>Download app</a>
          <a href="https://plugins.qgis.org/plugins/MISLAND/" target="blank" class="tool-bar-link q-my-lg header-grey-links" no-caps> QGIS
            PLUGIN</a>
      </div>
    </div>
  </q-drawer>
</template>

<script>
import { defineAsyncComponent } from 'vue'
//pinia
import { storeToRefs } from "pinia";
import { useAuthUserStore } from "src/stores/auth_user_store"; // auth user store
const { getAuthUserDetails } = storeToRefs(useAuthUserStore()); // get authenticated user from store
const { fetchAuthUserDetails } = useAuthUserStore()
export default {
  data() {
    return {
      left_drawer_open: false,
      language: "English", // holds the selected language
    }
  },
  computed: {
    getAuthUserDetails() {
      return getAuthUserDetails.value
    },
    routeName() {
      return this.$route?.name
    }
  },
  components: {
    LanguageSelection: defineAsyncComponent(() => import("src/components/LanguageSelection.vue"))
  },
  methods: {
    toggleLeftDrawer() {
      this.left_drawer_open = !this.left_drawer_open
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

.language-selected {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 20px;
  // letter-spacing: -0.02em;
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
