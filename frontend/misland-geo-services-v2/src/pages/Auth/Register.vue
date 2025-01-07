<template >
  <q-page class="q-pa-md flex flex-center">
    <div class="register-container">
      <div class="signup-title">Register</div>
      <form @submit.prevent="register">
        <!-- first name and last name row -->
        <div class="row">
          <div class="col-xs-12 col-sm-6 col-md-6   q-pa-xs">
            <div class="form-input-label">First name*</div>
            <q-input outlined dense v-model="register_form.first_name" input-class="form-input"
              placeholder="Enter your first name " />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.first_name.$error">
              {{ v$.register_form.first_name.$errors[0].$message }}
            </div>
          </div>
          <div class="col-xs-12  col-sm-6 col-md-6 q-pa-xs">
            <div class="form-input-label">Last name*</div>
            <q-input outlined dense v-model="register_form.last_name" input-class="form-input"
              placeholder="Enter your last name " />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.last_name.$error">
              {{ v$.register_form.last_name.$errors[0].$message }}
            </div>
          </div>
        </div>
        <!-- email and profession  row -->
        <div class="row">
          <div class="col-xs-12 col-sm-6 col-md-6   q-pa-xs">
            <div class="form-input-label">E-mail*</div>
            <q-input outlined dense v-model="register_form.email" input-class="form-input"
              placeholder="example@missland.org" />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.email.$error">
              {{ v$.register_form.email.$errors[0].$message }}
            </div>
          </div>
          <div class="col-xs-12  col-sm-6 col-md-6 q-pa-xs">
            <div class="form-input-label">Profession*</div>
            <q-input outlined dense v-model="register_form.profile.profession" input-class="form-input"
              placeholder="Enter your profession/sector" />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.profile.profession.$error">
              {{ v$.register_form.profile.profession.$errors[0].$message }}
            </div>
          </div>
        </div>
        <!-- institution and title row -->
        <div class="row">
          <div class="col-xs-12 col-sm-6 col-md-6   q-pa-xs">
            <div class="form-input-label">Institution*</div>
            <q-input outlined dense v-model="register_form.profile.institution" input-class="form-input"
              placeholder="Name of your institution" />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.profile.institution.$error">
              {{ v$.register_form.profile.institution.$errors[0].$message }}
            </div>
          </div>
          <div class="col-xs-12  col-sm-6 col-md-6 q-pa-xs">
            <div class="form-input-label">Title</div>
            <q-input outlined dense v-model="register_form.profile.title" input-class="form-input"
              placeholder="Enter your title " />
          </div>
        </div>
        <!-- password and confirm password row -->
        <div class="row">
          <div class="col-xs-12 col-sm-6 col-md-6   q-pa-xs">
            <div class="form-input-label">Password*</div>
            <q-input dense outlined v-model="register_form.password" input-class="form-input"
              placeholder="Enter your password" />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.password.$error">
              {{ v$.register_form.password.$errors[0].$message }}
            </div>
          </div>
          <div class="col-xs-12  col-sm-6 col-md-6 q-pa-xs">
            <div class="form-input-label">Confirm Password*</div>
            <q-input outlined dense v-model="register_form.password2" input-class="form-input"
              placeholder="Re-enter your password" />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.register_form.password2.$error">
              {{ v$.register_form.password2.$errors[0].$message }}
            </div>
          </div>
        </div>
        <!-- action button -->
        <div class="q-my-md">
          <q-btn unelevated class="signup-btn text-white" type="submit" no-caps>Sign up</q-btn>
        </div>
        <div class="q-my-md text-center">
          <span>Already have an account?</span>
          <router-link to="/login" class="login-link"> Login</router-link>
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
      register_form: {
        first_name: "",
        last_name: "",
        email: "",
        profile: {
          profession: "",
          institution: "",
          title: ""
        },
        password: "",
        password2: ""
      }

    }
  },
  validations() {
    return {
      register_form: {
        profile: {
          profession: {
            required: helpers.withMessage("Profession is required", required),
          },
          institution: {
            required: helpers.withMessage("Institution  is required", required),
          }
        },
        first_name: {
          required: helpers.withMessage("First name is required", required),
        },
        last_name: {
          required: helpers.withMessage("Last name is required", required),
        },
        email: {
          required: helpers.withMessage("Email address is required", required),
          email: helpers.withMessage("Email mst be valid", email)
        },
        password: {
          required: helpers.withMessage("Password is required", required),
          minLength: helpers.withMessage("Password is must be atleast 8 characters long", minLength(8)),
        },
        password2: {
          required: helpers.withMessage("You need to confirm password", required),
          sameAs: helpers.withMessage(
            "Passwords must match ",
            sameAs(this.register_form.password)
          ),
        },
      },
    };
  },
  mounted() {
    if (process.env.DEV) {
      this.register_form = {
        first_name: "first_name_test",
        last_name: "last_name_test",
        email: "sekowad674@sunetoa.com",
        profile: {
          profession: "gegis",
          institution: "locateit",
          title: "gis expert"
        },
        password: "mimimimi",
        password2: "mimimimi"
      }
    }
  },
  methods: {
    async register() {
      try {
        this.v$.$touch(); //validate the form
        if (this.v$.$error) return; // return if for has errors
        const response = await this.$api.post("/api/signup/", {
          ...this.register_form
        });
        if (process.env.DEV) console.log("register response data ", response.data);
        const message = response.data.message
        if (message) positive({
          message, color: "green", position: 'top'
        })
      } catch (error) {
        let error_message  = error?.response?.data;
        if (error_message && typeof error_message === 'object') {
          error_message = Object.values(error?.response?.data).map(err => {
            return err[0]
          })
        }
        if (process.env.DEV) console.log("error while registering ", error)

        negative({
          message: error_message || 'could not complete signup at this time',
          position: 'center'
        })

      }
    }
  },
}
</script>
<style lang="scss" scoped>
.register-container {
  @media (min-width: $breakpoint-md-min) {
    width: 500px;
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

.signup-title {
  color: #2E2E2E;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 34px;
  text-align: center;
  margin-bottom: 30px;
}

.signup-btn {
  background-color: #74B281;
  border-radius: 7px;
  width: 100%;
}

.login-link {
  text-decoration: none;
  color: #74B281;
}
</style>
