<template>
  <div class="">
    <HomePageNav/>
    <!------------------ Hero Page --------------------->
    <Hero />
    <!------------------ End of hero Page --------------------->
    <!------------------ start of what is MISLAND --------------------->
    <div class="flex q-py-lg q-my-xl  q-pa-md page-width">
      <div class="col-md flex justify-center">
        <div class="what-is-misland"> {{ $t("what_is_misland_africa.title") }}</div>
      </div>
      <div class="col-md what-is-misland-description flex column justify-center">
        <div class="q-my-sm">
          {{ $t("what_is_misland_africa.paragraph_1") }}
        </div>
        <div class="q-my-sm">
          {{ $t("what_is_misland_africa.paragraph_2") }}
        </div>
      </div>
    </div>
    <!------------------ End of what is MISLAND --------------------->
    <!------------------ Start of MISLAND Indicator tabs --------------------->
    <div class="q-py-xl q-my-xl q-px-lg" style="background-color:#f8f9f4">
      <MislandIndicators class="page-width" />
    </div>
    <!------------------ End of MISLAND Indicator tabs --------------------->
    <!------------------ Start of misland north africa training  --------------------->
    <div class="misland-training-container page-width">
      <div class="row">
        <div class="col-md col-xs-12">
          <div class="misland-training-north-africa">  {{ $t("trainings.title") }}</div>
          <!-- description -->
          <div class="misland-training-description">
            <div class="q-my-sm">
              {{ $t("trainings.paragraph_1") }}
            </div>
            <div class="q-my-sm">
              {{ $t("trainings.paragraph_2") }}
            </div>
          </div>
        </div>
        <div class="col-md col-xs-12  q-pa-sm">
          <div class="full-height">
            <q-video style="height: 100%"
              src="https://res.cloudinary.com/dv3id0zrx/video/upload/v1639495393/Presentation1_egnwzn.mp4" />
          </div>
        </div>
      </div>
    </div>
    <!------------------ End of misland north africa training  --------------------->
    <!------------------ Start of contact form  --------------------->
    <div class="">
      <ContactForm />
    </div>
    <!------------------ End of contact form  --------------------->
    <!------------------ Start of faq  --------------------->
    <div class="page-width q-my-lg q-pa-md">
      <Faq />
    </div>
    <!------------------ End of faq --------------------->
    <!------------------ Start of contacts and links --------------------->
    <div class="page-width q-my-lg">
      <ContactsAndLinks />
    </div>
    <!------------------ End of contacts and links --------------------->
    <!------------------ start of footer  --------------------->
    <div class="q-my-lg page-width">
      <q-separator inset class="q-my-md" />
      <Footer />
    </div>
    <!------------------ end of footer  --------------------->
  </div>
</template>
<script>
import { defineAsyncComponent } from "vue";
export default {
  data() {
    return {

    }
  },
  components: {
    Hero: defineAsyncComponent(() => import('src/components/HomePage/Hero.vue')),
    MislandIndicators: defineAsyncComponent(() => import('src/components/HomePage/MislandIndicators.vue')),
    ContactForm: defineAsyncComponent(() => import('src/components/HomePage/ContactForm.vue')),
    Faq: defineAsyncComponent(() => import('src/components/HomePage/Faq.vue')),
    ContactsAndLinks: defineAsyncComponent(() => import('src/components/HomePage/ContactsAndLinks.vue')),
    HomePageNav: defineAsyncComponent(()=>import("src/components/HomePage/NavBar.vue")),
    Footer: defineAsyncComponent(() => import('src/components/Footer.vue')),
  }
}
</script>
<style lang="scss" scoped>
.what-is-misland {
  font-family: 'Inter';
  font-weight: 700;
  font-size: 40px;
  color: #838C48;

  @media (max-width: $breakpoint-sm-max) {
    font-size: 30px;
  }
}

.what-is-misland-description {
  font-family: 'Inter';
  font-weight: 600;
  font-size: 20px;
  color: #404715;

  @media (max-width: $breakpoint-sm-max) {
    font-size: 16px;
  }
}

.misland-training-container {
  padding: 30px;
  margin-top: 60px;
  margin-bottom: 60px;

}

.misland-training-north-africa {
  color: #838C48;
  font-family: 'Inter';
  font-weight: 700;
  font-size: 40px;
}

.misland-training-description {
  color: #404715;
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  max-width: 700px;
}
</style>
