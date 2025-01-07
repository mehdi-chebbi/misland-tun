<template >
  <div>
    <NavBar />
    <div class="full-width">
        <!-- PDF Viewer -->
    <iframe :src="pdfUrl" class="pdf-iframe" frameborder="0">
      Your browser does not support iframes. Please download the PDF from the link below.
      <a :href="pdfUrl" target="_blank">Download PDF</a>
    </iframe>
    </div>
  </div>
</template>
<script>
import { defineAsyncComponent } from "vue";
export default {

  data() {
    return {
 pdfUrl:"http://misland-africa.oss-online.org:1337/media/Misland_MapoGraphic_Final.pdf"
    }
  },
  components:{
    NavBar: defineAsyncComponent(() => import("src/components/NavBar.vue")),
  }
}
</script>
<style lang="scss" scoped>
.pdf-iframe {
  width: 100%;
  height: calc(100dvh - 85px);
}
</style>
