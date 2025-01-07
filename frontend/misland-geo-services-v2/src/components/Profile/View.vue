<template>
  <div class="q-pa-none">
    <!-- first name and last name -->
    <div class=" profile-row-items full-width q-my-md">
      <div class="q-pa-xs">
        <div class="profile-title">First name</div>
        <div class="profile-value">
          <div class="">{{ getAuthUserDetails?.first_name }}</div>
        </div>
      </div>
      <div class="q-pa-xs">
        <div class="profile-title">Last name</div>
        <div class="profile-value">
          <div class="">{{ getAuthUserDetails?.last_name }}</div>
        </div>
      </div>
    </div>

    <!-- enail and profession -->
    <div class="profile-row-items q-my-md">
      <div class="q-pa-xs">
        <div class="profile-title">Email </div>
        <div class="profile-value">
          <div class="">{{ getAuthUserDetails?.email }}</div>
        </div>
      </div>
      <div class="q-pa-xs">
        <div class="profile-title">Profession</div>
        <div class="profile-value">
          <div class="">{{ getAuthUserDetails?.profession }}</div>
        </div>
      </div>
    </div>
    <!-- institution and title -->
    <div class="profile-row-items q-my-md">
      <div class="q-pa-xs ">
        <div class="profile-title">Institution </div>
        <div class="profile-value">
          <div class="">{{ getAuthUserDetails?.institution }}</div>
        </div>
      </div>
      <div class="q-pa-xs">
        <div class="profile-title">Title</div>
        <div class="profile-value">
          <div class="">{{ getAuthUserDetails?.title }}</div>
        </div>
      </div>
    </div>
    <!-- update link button -->
    <div class="q-pa-xs">
      <q-btn unelevated class="update-data-btn text-white" no-caps to="/profile/update">Edit details</q-btn>
    </div>

  </div>
</template>
<script>
//pinia
import { storeToRefs } from "pinia";
import { useAuthUserStore } from "src/stores/auth_user_store"; // auth user store
const { getAuthUserDetails } = storeToRefs(useAuthUserStore()); // get authenticated user from store
export default {
  data() {
    return {

    }
  },
  computed: {
    getAuthUserDetails() {
      return getAuthUserDetails.value
    }
  },

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

.profile-value {
  border: 1px solid #828766;
  border-radius: 7px;
  padding: 5px 10px;

  @media (min-width: $breakpoint-md-min) {
    width: 300px;
  }

  @media (max-width: $breakpoint-sm-max) {
    width: 100%
  }
}


.update-data-btn {
  background-color: #74B281;
  border-radius: 5px;
  min-width: 130px;
}
</style>
