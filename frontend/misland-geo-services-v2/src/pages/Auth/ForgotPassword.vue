<template >
  <q-page class="flex flex-center q-pa-md">
    <div class="form-container">
      <div class="forgot-password-title">Forgot Password</div>
      <form @submit.prevent="requestPasswordReset">
        <!-- email  -->
        <div class="  q-pa-xs">
          <div class="form-input-label">E-mail*</div>
          <q-input outlined dense v-model="forgot_pass_form.email" input-class="form-input"
            placeholder="example@missland.org" />
          <!-- show validation error message -->
          <div class="text-red  q-mt-xs" v-if="v$.forgot_pass_form.email.$error">
            {{ v$.forgot_pass_form.email.$errors[0].$message }}
          </div>
        </div>

        <!-- action button -->
        <div class="q-my-md">
          <q-btn unelevated class="signup-btn text-white" type="submit" no-caps>Submit</q-btn>
        </div>
        <div class="q-my-md text-center">
          <span>Don't have an account?</span>
          <router-link to="/register" class="register-link"> Register</router-link>
        </div>
      </form>
    </div>
  </q-page>
</template>
<script>
import useVuelidate from "@vuelidate/core";
import { required, helpers, sameAs, minLength, email } from "@vuelidate/validators";
import { negative, positive } from "src/Services/notifications"
export default {
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      forgot_pass_form: {
        email: "",
      }

    }
  },
  validations() {
    return {
      forgot_pass_form: {
        email: {
          required: helpers.withMessage("Email address is required", required),
          email: helpers.withMessage("Email mst be valid", email)
        },

      },
    };
  },
  methods: {
    async requestPasswordReset() {
      try {
        this.v$.$touch(); //validate the form
        if (this.v$.$error) return; // return if for has errors
        const response = await this.$api.post("/api/requestpwdreset/", {
          ...this.forgot_pass_form
        });
        if (process.env.DEV) console.log("request password response data ", response.data);
        localStorage.setItem("oss_auth_token", response.data.token);

        const message = response.data.message
        if (message) positive({
          message, color: "green", position: 'top'
        })
        this.$router.push("/");
      } catch (error) {
        if (process.env.DEV) console.log("error while requesting passord reset ", error)

      }
    }
  },
}
</script>
<style lang="scss" scoped>
.form-container {
  @media (min-width: $breakpoint-md-min) {
    min-width: 500px;
  }

  @media (max-width: $breakpoint-sm-max) {}
}

.forgot-password-title {
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

.register-link {
  text-decoration: none;
  color: #74B281;
}
.signup-btn {
  background-color: #74B281;
  border-radius: 7px;
  width: 100%;
}
</style>

\
