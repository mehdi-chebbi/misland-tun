<template>
  <div class="row q-my-xl " style="flex-direction: reverse">
    <div class="col-md col-xs-12">
      <div class="faq-title">FAQ</div>
      <!-- faqs -->
      <div class="q-pa-sm" v-for="(faq, i) in Faqs" :key="faq.question_text">
        <q-expansion-item group="somegroup" expand-separator :label="`${i + 1}. ${faq.question_text}`"
          header-class="faq-question">
          <div class="faq-answer">
            {{ faq.answer }}
          </div>
        </q-expansion-item>
      </div>
    </div>
    <div class="col-xs-12 col-md">
      <img src="~assets/png/dashboard.png" style="width: 100%; max-height: 400px;">
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      selected_question_index: null,
      Faqs: []
    };
  },
  mounted() {
    this.selected_question_index = this.$route.params.index;
    this.getFaqs();
  },
  methods: {
    gotTo(route) {
      this.$router.push(route);
    },
    async getFaqs() {
      try {
        let response = await this.$api.get("/api/faq/");
        this.Faqs = response.data;
        if (response) {
          if (process.env.DEV) console.log("Faq response", this.Faqs);
        }
      } catch (error) {
        if (process.env.DEV)
          console.log("Error getting frequently asked questions");
      }
    }
  }
}
</script>
<style lang="scss" scoped>
.faq-title {
  color: #838C48;
  font-weight: 700;
  font-size: 40px;
  margin-left: 20px;
}
.faq-answer {
  color: #838C48;
  font-weight: 500;
font-size: 16px;
padding: 1px 20px;
}
</style>

<style lang="scss">
.faq-question {
  color: #838C48;
  font-weight: 700;
  font-size: 20px;
}

</style>
