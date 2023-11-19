<template>
  <div class="d-flex .justify-center">
    <v-chip 
      class="ma-2" 
      disabled 
      label 
      color="white" 
      font-weight="700" 
      text-color="black"
    >
      <strong>Annotator {{ parseInt(annotator) + 1 }}:</strong>
    </v-chip>
    <v-chip-group 
      id="review-bank" 
      v-model="currentCluster" 
      :value="currentCluster" 
      active-class="primary--text"
      mandatory 
      show-arrows
    >
      <v-chip 
        v-if="reviewBankClusters.length == 0" 
        text-color="purple" 
        color="#F7EFFF" 
        small 
        @click="newCluster"
      >
        <v-icon 
          dark
        >
          mdi-plus
        </v-icon>
      </v-chip>
      <v-chip 
        v-for="cluster in reviewBankClusters" 
        :key="cluster.id" 
        :value="cluster.id" 
        label 
        small 
        color="#F7EFFF"
        text-color="purple" 
        @click="candidateSelected(cluster.id)"
      >
        {{ cluster.text }}
      </v-chip>
    </v-chip-group>
    <v-divider />
  </div>
</template>


<script>


export default {
  name: "ReviewBank",
  components: {
    // VMain
    // VChip,
    // VChipGroup,
  },
  props: {
    clusters: {type: Object, required: true},
    annotator: {type: String, default: "0"},
    suggestedReviewerClusters: {type: Set, default: {}},
    selectedCluster: {type: String, required: true}
  },
  data: function () {
    return {
      currentCluster: this.selectedCluster.toString()
    };
  },
  computed: {
    reviewBankClusters: function () {
      return Object.values(this.clusters)
        .filter((c) => this.suggestedReviewerClusters.has(c.id));
    }
  },
  methods: {
    candidateSelected: function (cId) {
      this.$emit("candidateSelected", cId);
    },
    newCluster: function () {
      this.$emit("newCluster");
    }
  }
}

</script>

<style scoped>
</style> 