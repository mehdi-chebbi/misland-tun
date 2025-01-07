<template >
  <q-page class="flex justify-center q-pa-md  profile-page">
    <div class="flex">
      <!-- user user or notification -->
      <div class="profile-selection-container flex justify-center">
        <div class="">
          <div class="account-settings-title">Account settings</div>
          <div class="q-my-md">
            <q-btn unelevated class="selection-btn" no-caps>Your account</q-btn>
          </div>
          <!-- <div class="q-my-md">
            <q-btn unelevated class="selection-btn" no-caps>Notifications</q-btn>
          </div> -->
        </div>
      </div>
      <!-- user data for to view and edit -->
      <div class="user-data-container bg-white">
        <!-- user data tite -->
        <div class="text-h6 text-weight-bold q-my-md">User data</div>
        <!-- profile picture -->
        <div class="flex items-center q-my-md">
          <div class="">
            <q-avatar round size="100px" color="orange">
              <div class="text-white">J</div>
            </q-avatar>
          </div>
        </div>
        <!-- user data with input section -->
        <div class="q-my-md">
          <View v-if="currentComponent === ''" />
          <UpdateForm v-if="currentComponent === 'update'" />
          <!-- logout -->
          <div class="q-pa-xs">
            <q-btn unelevated class="logout-btn " no-caps @click="logout">Log out</q-btn>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>
<script>
import { defineAsyncComponent } from 'vue'
export default {
  computed: {
    currentComponent() {
      return this.$route.params.component
    }
  },
  components: {
    View: defineAsyncComponent(() => import("src/components/Profile/View.vue")),
    UpdateForm: defineAsyncComponent(() => import("src/components/Profile/UpdateForm.vue")),
  },
  methods: {
    async logout() {
      await localStorage.removeItem("oss_auth_token");
      await this.$router.replace("/");
      window.location.reload(true);
    }
  },
}
</script>
<style lang="scss" scoped>
.profile-page {
  background-color: #f8faf9;
  padding: 20px 0px 0px 0px;
}

.profile-selection-container {
  @media (min-width: $breakpoint-md-min) {
    min-width: 500px;
    padding: 10px;
  }

  @media (max-width: $breakpoint-sm-max) {
    width: 100%;
    padding: 10px;
  }

}

.account-settings-title {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-size: 25px;
  color: #2E2E2E;
}

.user-data-container {
  @media (min-width: $breakpoint-md-min) {
    min-width: 500px;
    padding: 10px 40px;
  }

  @media (max-width: $breakpoint-sm-max) {
    width: 100%;
    padding: 10px;
  }
}

.logout-btn {
  border: 1px solid #CCCCCC;
  border-radius: 11px;
  border-radius: 5px;
  color: #74B281;
  margin-top: 10px;

}

.selection-btn {
  margin: 0px 0px 10px 0px;
  min-width: 150px;
  background-color: beige;
}
</style>
