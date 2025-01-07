<template>
  <form @submit.prevent="updateUserProfile" class="q-pa-none">
    <!-- first name and last name -->
    <div class="profile-row-items full-width q-my-md">
      <div class="q-pa-xs ">
        <div class="profile-title">First name</div>
        <div class="profile-input">
          <q-input dense outlined v-model="user_details.first_name" />
        </div>
      </div>
      <div class="q-pa-xs">
        <div class="profile-title">Last name</div>
        <div class="profile-input">
          <q-input dense outlined v-model="user_details.last_name" />
        </div>
      </div>
    </div>

    <!-- enail and profession -->
    <div class="profile-row-items full-width q-my-md">
      <div class="q-pa-xs">
        <div class="profile-title">Email </div>
        <div class="profile-input">
          <q-input dense outlined v-model="user_details.email" />
        </div>
      </div>
      <div class="q-pa-xs">
        <div class="profile-title">Profession</div>
        <div class="profile-input">
          <q-input dense outlined v-model="user_details.profile.profession" />
        </div>
      </div>
    </div>
    <!-- institution and title -->
    <div class="profile-row-items full-width q-my-md">
      <div class="q-pa-xs ">
        <div class="profile-title">Institution </div>
        <div class="profile-input">
          <q-input dense outlined v-model="user_details.profile.institution" />
        </div>
      </div>
      <div class="q-pa-xs">
        <div class="profile-title">Title</div>
        <div class="profile-input">
          <q-input dense outlined v-model="user_details.profile.title" />
        </div>
      </div>
    </div>
    <!-- update link button -->
    <div class="profile-button-container">
      <q-btn unelevated class="update-data-btn text-white" no-caps type="submit">Save information</q-btn>
    </div>
  </form>
</template>
<script>
//pinia
import { storeToRefs } from "pinia";
import { positive } from "src/Services/notifications";
import { useAuthUserStore } from "src/stores/auth_user_store"; // auth user store
const { getAuthUserDetails } = storeToRefs(useAuthUserStore()); // get authenticated user from store
export default {
  data() {
    return {
      user_details: {
        first_name: "",
        last_name: "",
        email: "",
        profile: {
          profession: "",
          institution: "",
          title: "",
        }
      }
    }
  },
  computed: {
    getAuthUserDetails() {
      return getAuthUserDetails.value
    }
  },
  mounted() {
    this.populateForm()
  },
  methods: {
    // populate form data
    populateForm() {

      this.user_details.first_name = this.getAuthUserDetails.first_name;
      this.user_details.last_name = this.getAuthUserDetails.last_name;
      this.user_details.email = this.getAuthUserDetails.email;
      this.user_details.profile.institution = this.getAuthUserDetails.institution;
      this.user_details.profile.profession = this.getAuthUserDetails.profession;
      this.user_details.profile.title = this.getAuthUserDetails.title;


      console.log("populate ****** ", this.user_details);
    },
    async updateUserProfile() {
      try {
        const token = localStorage.getItem("oss_auth_token");
        const response = await this.$api.post('/api/updateuser/', this.user_details, {
          headers: {
            Authorization: token ? "Bearer " + token : "",

          }
        })
        console.log("update user data response ", response.data);
        positive({
          message
        })
      } catch (error) {
        console.log("error updating user profile ", error);
      }
    }
  }
}
</script>
<style lang="scss" scoped>
.profile-row-items {
  @media (min-width: $breakpoint-md-min) {
    display: flex;
    justify-content: space-between;
  }

  @media (max-width: $breakpoint-sm-max) {}
}

.profile-title {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  color: #808080;
}

.profile-input {
  @media (min-width: $breakpoint-md-min) {
    width: 300px;
  }

  @media (max-width: $breakpoint-sm-max) {
    width: 100%
  }
}

.profile-button-container {
  @media (min-width: $breakpoint-md-min) {
    display: flex;
    justify-content: center;

  }

  @media (max-width: $breakpoint-sm-max) {}
}

.update-data-btn {
  background-color: #74B281;
  border-radius: 5px;

  @media (min-width: $breakpoint-md-min) {
    margin-top: 10px;
    width: 100%;
  }

  @media (max-width: $breakpoint-sm-max) {
    width: 100%;
    margin-top: 10px;
  }
}
</style>
