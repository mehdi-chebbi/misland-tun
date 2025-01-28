<template >
  <q-page class="contact-container">
    <div class=" page-width relative-position ">
      <!-- contact us box section -->
      <div class="contact-us-box">
        <div class="contact-title">  {{ $t("contact_component.title") }}</div>
        <div class="contact-description">  {{ $t("contact_component.description") }}</div>
      </div>
      <!--------------------------------------- contact us form container --------------------------------------->
      <div class="contact-us-form-container">
        <form @submit.prevent="handleContactUs">
          <!-- email -->
          <div class="">
            <div class="contact-label">{{ $t("contact_component.email_label") }}</div>
            <q-input outlined dense v-model="contact_us_form.email" input-class="contact-input"
              placeholder="example@missland.org" />
            <!-- show validation error message -->
            <div class="text-red q-ml-md q-mt-xs" v-if="v$.contact_us_form.email.$error">
              {{ v$.contact_us_form.email.$errors[0].$message }}
            </div>
          </div>
          <!-- title -->
          <div class="">
            <div class="contact-label">{{ $t("contact_component.title_label") }}</div>
            <q-input outlined dense v-model="contact_us_form.title" input-class="contact-input"
              :placeholder="$t(`contact_component.title_placeholder`)" />
          </div>
          <!-- message -->
          <div class="">
            <div class="contact-label">{{ $t("contact_component.message_label") }}</div>
            <q-input outlined dense autogrow type="textarea" input-class="contact-input"
              v-model="contact_us_form.message" input-style="min-height:100px" />
          </div>
          <!-- action -->
          <div class="q-mt-lg q-mb-sm">
            <q-btn unelevated class="contact-submit-btn" type="submit">{{ $t("contact_component.submit_btn_label") }}</q-btn>
          </div>
        </form>
      </div>

    </div>

  </q-page>
</template>
<script>
import useVuelidate from "@vuelidate/core";
import { required, helpers, email } from "@vuelidate/validators";
export default {
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      contact_us_form: {
        email: "",
        title: "",
        message: "",
      }
    }
  },
  validations() {
    return {
      contact_us_form: {
        email: {
          required: helpers.withMessage("Email address is required", required),
          email: helpers.withMessage("Email mst be valid", email)
        },
      }

    }
  },
  methods: {
    async handleContactUs() {
      try {
        this.v$.$touch(); //validate the form
        if (this.v$.$error) return; // return if for has errors
        console.log("contact_us_form ", this.contact_us_form);
        let url = `https://api.github.com/repos/LocateIT/MISLAND-issue-tracker/issues`;
        let data = {
          title: `Contact title: ${this.contact_us_form.title} ${this.user_email ? "by" : ""} ${this.contact_us_form.email
            }`,
          body: this.contact_us_form.message,
        };
        if (process.env.DEV) console.log("text body ", this.feeback_text);
        // return
        let response = await this.$api.post(url, data, {
          headers: {
            // Authorization: `Bearer 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` //note5mn
            Authorization: `Bearer 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`, // locatit
          },
        });
        if (response) {
          this.$q.notify({
            message: "Thank you for contacting us",
            color: "green-4",
            textColor: "white",
            icon: "thumb_up",
          });
        }
      } catch (error) {
        if (process.env.DEV) console.log("Error sending contact ", error);
        this.$q.notify({
            message: "An error occured",
            color: "red-4",
            textColor: "white",
            icon: "sentiment_dissatisfied",
          });
      }
    }
  },
}
</script>
<style lang="scss" scoped>
.contact-container {
  padding: 20px;
  background-repeat: no-repeat;
  background-size: cover;
  background-image: url('/png/tunisia.jpg');

  @media (max-width: $breakpoint-sm-max) {}
}

.contact-us-box {
  border-radius: 24px;
  background-color: rgba(1, 3, 37, 0.2);
  backdrop-filter: blur(12px);
  padding: 20px;

  @media (min-width: $breakpoint-md-min) {
    max-width: 425px;
    position: absolute;
    top: 50px;
  }

  @media (max-width: $breakpoint-sm-max) {
    margin: 40px 0px;
  }
}

.contact-title {
  color: #A8AF7F;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-size: 40px;
}

.contact-description {
  color: #FCFDFF;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
}

.contact-us-form-container {

  padding: 20px 30px;
  border-radius: 25px;
  background: rgba(1, 3, 37, 0.2);
  backdrop-filter: blur(12px);

  @media (min-width: $breakpoint-md-min) {
    position: absolute;
    width: 500px;
    top: 50px;
    right: 30px;
  }

  @media (max-width: $breakpoint-sm-max) {
    margin: 40px 0px;
  }

}

.contact-label {
  color: #F0F1E9;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  margin: 20px 0px 5px 0px
}

.contact-submit-btn {
  background: #74B281;
  color: #F8F9F4;
  border-radius: 11px;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  width: 150px;
}
</style>

<style lang="scss">
.contact-input {
  color: #F0F1E9;
}
</style>
