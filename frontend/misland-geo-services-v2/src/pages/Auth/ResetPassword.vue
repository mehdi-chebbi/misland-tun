<template >
  <div class="q-pa-md">
    <div class="row">
      <!-- image section -->
      <div class="col-md-6 col-xs-12">
        <img src="~assets/jpg/oss_oasis.jpg" style="width:100%">
      </div>
      <!---------------------------- regiter form  ----------------------------->
      <div class="col-md-6 col-xs-12 register-form-area ">
        <div class="flex items-center q-my-sm" style="padding-right:46px">
          <img src="~assets/svg/misland_logo.svg" alt="">
          <div class="misland-title">MISLAND</div>
        </div>
        <div class="q-my-sm">
          <div class="login-title">Reset password</div>
        </div>
        <div class="q-my-sm">
          <div class="login-text">Tell us a bit about yourself. We just need the basics.</div>
        </div>
        <form @submit.prevent="resetPassword">
          <!-- new_password -->
          <div class=" q-pa-xs">
            <div class="form-input-label">new password*</div>
            <q-input dense outlined v-model="reset_pass_form.new_password" input-class="form-input"
              placeholder="Enter your new_password" type="password" />
            <!-- show validation error message -->
            <div class="text-red  q-mt-xs" v-if="v$.reset_pass_form.new_password.$error">
              {{ v$.reset_pass_form.new_password.$errors[0].$message }}
            </div>
          </div>
          <!-- confirm new_password  -->
          <div class=" q-pa-xs">
            <div class="form-input-label">confirm password*</div>
            <q-input dense outlined v-model="reset_pass_form.confirm_password" input-class="form-input"
              placeholder="Enter your confirm_password" type="password" />
            <!-- show validation error message -->
            <div class="text-red  q-mt-xs" v-if="v$.reset_pass_form.confirm_password.$error">
              {{ v$.reset_pass_form.confirm_password.$errors[0].$message }}
            </div>
          </div>
          <!-- action button -->
          <div class="q-my-md">
            <q-btn unelevated class="full-width" color="primary" type="submit">Submit</q-btn>
          </div>
          <div class="q-my-md text-center">
            <span>Don't have an account?</span>
            <router-link to="/register" class="register-link"> Register</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
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
      reset_pass_form: {
        new_password: "",
        confirm_password: ""
      }

    }
  },
  computed:{
    getRouteParams() {
      return this.$route.params;
    },
  },
  validations() {
    return {
      reset_pass_form: {
        new_password: {
          required: helpers.withMessage("Password is required", required),
          minLength: helpers.withMessage("Password is must be atleast 8 characters long", minLength(8)),
        },
        confirm_password: {
          required: helpers.withMessage("You need to confirm password", required),
          sameAs: helpers.withMessage(
            "Passwords must match ",
            sameAs(this.reset_pass_form.new_password)
          ),
        },
      },
    };
  },
  watch: {
    getRouteParams:{
      immediate:true,
      handler(val){
        if(!val) return;
        const action =  val.action
       if(process.env.DEV) console.log(action, " getCurrentRoute *********** ", this.getRouteParams);

      }
    }
  },
  methods: {
    async resetPassword() {
      try {
        this.v$.$touch(); //validate the form
        if (this.v$.$error) return; // return if for has errors
        const response = await this.$api.post("/api/resetpwd/", {
          ...this.reset_pass_form,
          uid: this.getRouteParams.code,
          token: this.getRouteParams.token,
        });
        if (process.env.DEV) console.log("register response data ", response.data);
        localStorage.setItem("oss_auth_token", response.data.token);
        this.$router.push("/geoservice");
        const message = response.data.message
        if (message) positive({
          message, color: "green", position: 'top'
        })
      } catch (error) {
        if (process.env.DEV) console.log("error while registering ", error)
        if(error.response?.data?.message){
          negative({
            message: error.response?.data?.message,
            color: 'red',
            position: 'top'
          })
        }

      }
    }
  },
}
</script>
<style lang="scss" scoped>
.register-form-area {
  @media (min-width: $breakpoint-md-min) {
    padding: 1px 30px;
  }

  @media (max-width: $breakpoint-sm-max) {}
}

.form-input-label {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 16px;
  color: #838C48;
  margin: 2px 0px
}

.misland-title {
  font-family: 'Inter';
  font-weight: 900;
  font-size: 40px;
  color: #404715;
}

.login-title {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 30px;
  color: #2E2E2E;
}

.login-text {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  color: #2E2E2E;

}

.register-link {
  text-decoration: none;
  color: #74B281;
}
</style>

<style lang="scss">
.form-input {}
</style>
