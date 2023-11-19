<template>
  <v-main>
    <div v-if="mode=='reviewer' || mode=='doubleReview'" class="d-flex .justify-center">

      <v-chip-group class="mx 2">
        <v-chip class="mx 2" color="white" bold text-color="red" v-if="this.isDisagreement">
          <v-icon>mdi-thumb-down</v-icon>
        </v-chip>
      </v-chip-group>

      <ReviewBank v-for="(suggestion, annotator) in this.suggestedReviewerClusters" :key="annotator"
        :clusters="clusters" :annotator="annotator" :suggestedReviewerClusters="suggestion"
        :selectedCluster.sync="selectedCluster" v-on:candidateSelected="candidateSelected"
        v-on:newCluster="newCluster(true)">
      </ReviewBank>





    </div>
    <v-divider v-if="mode=='reviewer' || mode=='doubleReview'"></v-divider>
    <v-chip-group active-class="primary--text" mandatory show-arrows v-model="currentCluster">
      <v-chip small @click="newCluster">
        <v-icon color="#2d9cdb" dark>mdi-plus</v-icon>
      </v-chip>
      <v-chip v-for="cluster in clusters" :key="cluster.id" :value="cluster.id" @click="candidateSelected(cluster.id)"
        label small>{{ cluster.text }}</v-chip>
    </v-chip-group>



  </v-main>
</template>



<script>
import { VMain, VDivider, VChip, VChipGroup, VIcon } from "vuetify/lib";
import ReviewBank from "./ReviewBank.vue";

export default {
  name: "ClusterBank",
  components: {
    VMain,
    VDivider,
    VChip,
    VChipGroup,
    ReviewBank,
    VIcon
  },
  props: {
    clusters: Object,
    suggestedReviewerClusters: Object,
    selectedCluster: String,
    mode: String,
    lastMention: Boolean,
    withHypernym: Boolean
  },
  data: function () {
    return {
      currentCluster: this.selectedCluster.toString(),
      finished: false,
      appear: this.lastMention
    };
  },
  computed: {
    isDisagreement: function () {
      for (const x in Object.values(this.suggestedReviewerClusters)) {
        for (const y in Object.values(this.suggestedReviewerClusters)) {
          if (x != y && !(this.setAreEquals(
            this.filterSuggestions(this.suggestedReviewerClusters[x]),
            this.filterSuggestions(this.suggestedReviewerClusters[y])))) {
            this.addDisagreement();
            return true;
          }
        }
      }
      return false;
    }
  },
  watch: {
    // whenever question changes, this function will run
    selectedCluster: function (newCluster) {
      this.currentCluster = newCluster;
    },
  },
  methods: {
    filterSuggestions: function (suggestions) {
      return Object.values(this.clusters)
        .filter((c) => suggestions.has(c.id));
    },
    setAreEquals: function (a, b) {
      if (a.length !== b.length) {
        return false;
      }
      return a.every(element => {
        return b.includes(element);
      })
    },
    newCluster: function () {
      this.$emit("newCluster");
    },
    candidateSelected: function (cId) {
      this.$emit("candidateSelected", cId);
    },
    addDisagreement: function () {
      this.$emit("addDisagreement");
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
