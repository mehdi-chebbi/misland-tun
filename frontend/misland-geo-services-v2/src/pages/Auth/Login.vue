<template >
  <q-page class="q-pa-md flex flex-center" style="background-color: #E5E5E5;">
    <div class="login-container">
      <div class="signin-title">Sign In</div>
      <form @submit.prevent="login">
        <!-- email  -->
        <div class="  q-pa-xs">
          <div class="form-input-label">E-mail*</div>
          <q-input outlined dense v-model="login_form.email" input-class="form-input"
            placeholder="example@missland.org" />
          <!-- show validation error message -->
          <div class="text-red  q-mt-xs" v-if="v$.login_form.email.$error">
            {{ v$.login_form.email.$errors[0].$message }}
          </div>
        </div>
        <!-- password -->
        <div class=" q-pa-xs">
          <div class="form-input-label">Password*</div>
          <q-input dense outlined v-model="login_form.password" input-class="form-input"
            placeholder="Enter your password" type="password" />
          <!-- show validation error message -->
          <div class="text-red  q-mt-xs" v-if="v$.login_form.password.$error">
            {{ v$.login_form.password.$errors[0].$message }}
          </div>
        </div>
        <!-- link to forget password  -->
        <div class="q-pa-xs">
          <router-link to="/forgot-password" class="forgot-password-link">Forgot your password?</router-link>
        </div>
        <!-- action button -->
        <div class="q-my-md">
          <q-btn unelevated class="signin-btn text-white" type="submit" no-caps>Sign in </q-btn>
        </div>
      </form>
      <!-- register call to action section -->
      <div class="register-cta-container">
        <div class="">Not registered yet?</div>
        <div class="q-my-md">Set up an account with us to get notifications on
          alerts you set up</div>
        <div class="q-my-md">
          <q-btn unelevated class="register-cta-btn text-white" to="/register" no-caps>Register now</q-btn>
        </div>
      </div>
    </div>
  </q-page>
</template>
<script>
import useVuelidate from "@vuelidate/core";
import { required, helpers, sameAs, minLength, email } from "@vuelidate/validators";
import { negative, positive } from "src/Services/notifications"
//pinia
import { storeToRefs } from "pinia";
import { useAuthUserStore } from "src/stores/auth_user_store"; // auth user store
const { getAuthUserDetails } = storeToRefs(useAuthUserStore()); // get authenticated user from store
const { fetchAuthUserDetails } = useAuthUserStore()
export default {
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      login_form: {
        email: "",
        password: ""
      }
    }
  },
  validations() {
    return {
      login_form: {
        email: {
          required: helpers.withMessage("Email address is required", required),
          email: helpers.withMessage("Email mst be valid", email)
        },
        password: {
          required: helpers.withMessage("Password is required", required),
          minLength: helpers.withMessage("Password is must be atleast 8 characters long", minLength(8)),
        },
      },
    };
  },
  methods: {
    async login() {
      try {
        this.v$.$touch(); //validate the form
        if (this.v$.$error) return; // return if for has errors
        const response = await this.$api.post("/api/login/", {
          ...this.login_form
        });
        if (process.env.DEV) console.log("register response data ", response.data);
        localStorage.setItem("oss_auth_token", response.data.token);
     
        const message = response.data.message
        if (message) positive({
          message, color: "green", position: 'top'
        })
        fetchAuthUserDetails(); // get user details
        this.$router.push("/geoservice").then(()=>this.$router.go())
      } catch (error) {
        if (process.env.DEV) console.log("error while registering ", error)
        const non_field_errors = error.response?.data?.non_field_errors;
        if (non_field_errors) negative({
          message: non_field_errors,
          color: 'red',
          position: 'top'
        })

      }
    }
  },
}
</script>
<style lang="scss" scoped>
.login-container {
  @media (min-width: $breakpoint-md-min) {
    min-width: 500px;
  }

  @media (max-width: $breakpoint-sm-max) {}
}

.signin-title {
  color: #2E2E2E;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 34px;
  text-align: center;
  margin-bottom: 30px;
}

.form-input-label {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 16px;
  color: #838C48;
  margin: 2px 0px
}

.forgot-password-link {
  text-decoration: none;
  color: #74B281;
  font-size: 16px;
  font-weight: 500;
}

.signin-btn {
  background-color: #74B281;
  border-radius: 7px;
  width: 100%;
}

.register-cta-container {
  background-color: #FFFFFF;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.12);
  border-radius: 11px;
  padding: 20px 20px 10px 20px;
}

.register-cta-btn {
  background-color: #74B281;
  border-radius: 7px;
  width: 100%;
}
</style>

