<template>
  <div>
    <v-chip
      class="ma-2"
      disabled
      label
      color="white"
      font-weight="700"
      text-color="black"
    >
      <strong>Hierarchy:</strong>
    </v-chip>
    <v-btn class="mx-2 reset" small append color="#B0BEC5" @click="reset()"
      >Reset</v-btn
    >

    <v-btn class="mx-2 sort" small append color="#71bfec" @click="sort()"
      >Sort</v-btn
    >

    <v-btn
      class="mx-2 add"
      v-if="this.addingNode"
      small
      append
      color="#EAC0FF"
      @click="addNode()"
    >
      Add Node
    </v-btn>

    <vue-tree-list
      class="hypernym"
      ref="package"
      :model="clusterTree"
      :selectedCluster="selectedCluster"
      @click="selectCluster"
      @change-name="onChangeName"
      @start-focus="onStartInput"
      @drop-after="afterDrop"
      @drop-before="afterDrop"
      @drop="afterDrop"
      default-tree-node-name="new node"
      default-leaf-node-name="new leaf"
      v-bind:default-expanded="true"
    >
      <template v-slot:leafNameDisplay="slotProps">
        <span
          :class="{
            selected: selectedCluster == slotProps.model.id,
            parent:
              currentParentId == slotProps.model.id && clusterList.length > 1,
          }"
        >
          {{ slotProps.model.text }}
          <span class="muted">#{{ slotProps.model.id }}</span>
        </span>
      </template>
    </vue-tree-list>
  </div>
</template>


<script>
// import { VButton } from "vuetify/lib";
import { VueTreeList, Tree, TreeNode } from "vue-tree-list";
export default {
  name: "Hypernym",
  components: {
    VueTreeList,
  },
  props: {
    clusterList: Array,
    hierarchy: Object,
    mentions: Array,
    addingNode: Boolean,
    annotator: Number,
    selectedCluster: String,
  },
  data() {
    return {
      newTree: {},
      clusterTree: {},
      rendering: false,
      assignedMentions: [],
    };
  },
  computed: {
    currentNode: function () {
      return this.dfs(this.selectedCluster);
    },

    currentParentId: function () {
      return this.currentNode.pid;
    },
    flatHierarchy: function () {
      let clustersIds = [];
      this.clusterTree.children.forEach((child) => {
        clustersIds.push(this.flatClusterTree(child));
      });
      return clustersIds.flat(Infinity);
    },
  },
  created() {
    if (Object.keys(this.hierarchy).length === 0) {
      Object.values(this.clusterList[this.annotator]).forEach((value) => {
        value.addTreeNodeDisabled = true;
        value.addLeafNodeDisabled = true;
        value.editNodeDisabled = false;
        value.delNodeDisabled = true;
        value.name = value.text;
      });
      this.clusterTree = new Tree(
        Object.values(this.clusterList[this.annotator])
      );
    } else {
      this.clusterTree = new Tree(this.hierarchy.children);
    }
  },

  watch: {
    deep: true,
    mentions: function (newVal, oldVal) {
      if (!this.arrayEquals(newVal, oldVal)) {
        this.assignedMentions = newVal;
      }
      this.assignedMentions = newVal;
    },

    clusterList: function (newVal, oldVal) {
      let newAnnotatorClusterList = newVal[this.annotator];
      let oldAnnotatorClusterList = oldVal[this.annotator];

      let oldClusters = Object.keys(oldAnnotatorClusterList);
      let newClusters = Object.keys(newAnnotatorClusterList);

      let intersection = oldClusters.filter((x) => newClusters.includes(x));
      let toBeDeleted = oldClusters.filter((x) => !intersection.includes(x));
      let toBeAdded = newClusters.filter((x) => !intersection.includes(x));

      // check whether to add or to delete a node from the hypernyms
      if (toBeDeleted.length > 0) {
        let clusterToBeDeleted = oldAnnotatorClusterList[toBeDeleted];
        let [start, end] = clusterToBeDeleted.id.split("-");

        let newCluster = this.getClusterMention(start, end);
        this.deleteExtraNode(
          oldAnnotatorClusterList[toBeDeleted].id,
          newCluster
        );
      }
      if (toBeAdded.length > 0) {
        let clusterId = this.getOldCluster(oldAnnotatorClusterList, toBeAdded);
        let destination = this.clusterTree;
        if (clusterId) {
          let offsets = clusterId.split("-");
          let newCluster = this.getClusterMention(offsets[0], offsets[1]);
          destination = this.dfs(newCluster).parent;
        }
        
        this.addMissingNode(
          this.clusterList[this.annotator][toBeAdded],
          destination
        );
      }

      this.updateNodeName(oldAnnotatorClusterList, newAnnotatorClusterList);
    },
  },
  methods: {
    getOldCluster: function (oldClusterList, clustId) {
      let mentionToClustId = {};
      for (const [cluster, fields] of Object.entries(oldClusterList)) {
        fields.mentions.forEach((mention) => {
          mentionToClustId[mention] = cluster;
        });
      }
      return mentionToClustId[clustId];
    },
    flatClusterTree: function (child) {
      let clusterIds = [];
      clusterIds.push(child.id);
      if (child.children != undefined) {
        child.children.forEach((x) => {
          clusterIds.push(this.flatClusterTree(x));
        });
      }
      return clusterIds;
    },
    afterDrop: function () {
      this.$emit("nodeSelected");
    },
    sort: function () {
      let stack = [];
      let explored = new Set();
      stack.push(this.clusterTree);

      explored.add(this.clusterTree);

      while (!stack.length == 0) {
        let t = stack.pop();
        explored.add(t);

        if (t.children) {
          t.children.sort((a, b) => a.text.localeCompare(b.text));
          t.children.forEach((element) => {
            stack.push(element);
            explored.add(element);
          });
        }
      }
    },
    updateNodeName: function (oldClusters, newClusters) {
      for (const [clustId, fields] of Object.entries(newClusters)) {
        if (
          clustId in oldClusters &&
          oldClusters[clustId].text != fields.text
        ) {
          var node = this.dfs(clustId);
          node.text = fields.text;
          node.name = fields.text;
          node.originalName = fields.text;
        }
      }
    },
    onStartInput: function () {
      this.$emit("deactivateEvents");
    },
    onChangeName: function (params) {
      if (params.newName.startsWith(params.oldName.trim())) {
        var node = this.dfs(params.id);
        node.name = params.newName;
        node.text = params.newName;
      }

      this.$emit("activateEvents");
    },

    reset: function () {
      let flatHierarchy = Array();

      for (var clusterId in this.clusterList[this.annotator]) {
        var oldNode = this.dfs(clusterId);
        var newNode = {};
        for (var k in oldNode) {
          if (k !== "children" && k !== "parent") {
            newNode[k] = oldNode[k];
          }
        }
        flatHierarchy.push(newNode);
      }

      this.clusterTree = new Tree(flatHierarchy);
    },

    forceRerender: function () {
      this.$emit("forceRerender");
    },

    getClusterMention(start, end) {
      let mention = this.assignedMentions.find(
        (x) => x.start == start && x.end == end
      );
      return mention.clustId[this.annotator];
    },

    arrayEquals(a, b) {
      return (
        Array.isArray(a) &&
        Array.isArray(b) &&
        a.length === b.length &&
        a.every((val, index) => val == b[index])
      );
    },

    dfs(nodeName) {
      let stack = [];
      let explored = new Set();
      stack.push(this.clusterTree);

      explored.add(this.clusterTree);

      // find with dfs the node to delete
      while (!stack.length == 0) {
        let t = stack.pop();
        explored.add(t);

        if (t.id == nodeName) {
          return t;
        }
        // add the children in the stack (for the dfs)
        if (t.children) {
          t.children.forEach((element) => {
            stack.push(element);
            explored.add(element);
          });
        }
      }
    },

    deleteExtraNode(nodeName, clusterDest) {
      let deleted = this.dfs(nodeName);
      let dest = this.dfs(clusterDest);

      if (dest == undefined) {
        dest = this.dfs(deleted.pid);
      }

      let children = [];
      if (deleted.children != null && deleted.children.length > 0) {
        deleted.children.forEach((x) => children.push(x.id));
      }

      // if a node was merged with its child node, move it under the parent of the deleted and delete it
      // then for each other child, move it under the newDest
      if (children.includes(dest.id)) {
        let tmpDest = this.dfs(deleted.parent.id);
        tmpDest.addChildren(dest);
        // dest = tmpDest;
      }

      if (deleted.children) {
        deleted.children.forEach((child) => {
          if (child.id != clusterDest) {
            dest.addChildren(child);
          }
        });
      }

      deleted.remove();
    },

    arrayMove(arr, fromIndex, toIndex) {
      var element = arr[fromIndex];
      arr.splice(fromIndex, 1);
      arr.splice(toIndex, 0, element);
    },

    addMissingNode(nodeName, destination) {
      if (nodeName) {
        nodeName.addTreeNodeDisabled = true;
        nodeName.addLeafNodeDisabled = true;
        nodeName.delNodeDisabled = true;
        nodeName.editNodeDisabled = false;
        nodeName.name = nodeName.text;

        var node = new TreeNode(nodeName);
        
        destination.addChildren(node);

        if (destination.id == 0) {
          let start = parseInt(nodeName.id.split("-")[0]);
          for (var i = 0; i < this.clusterTree.children.length; i++) {
            let child = this.clusterTree.children[i];
            let childStart = parseInt(child.id.split("-")[0]);
            if (start < childStart) {
              break;
            }
          }

          if (i < this.clusterTree.children.length) {
            this.clusterTree.children[
              this.clusterTree.children.length - 1
            ].insertBefore(this.clusterTree.children[i]);
          }
        }

      }
    },

    create_UUID() {
      var dt = new Date().getTime();
      var uuid = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
        /[xy]/g,
        function (c) {
          var r = (dt + Math.random() * 16) % 16 | 0;
          dt = Math.floor(dt / 16);
          return (c == "x" ? r : (r & 0x3) | 0x8).toString(16);
        }
      );
      return uuid;
    },

    addNode() {
      var node = new TreeNode({
        name: "new node",
        id: this.create_UUID(),
        isLeaf: false,
        editNodeDisabled: false,
        addTreeNodeDisabled: true,
        addLeafNodeDisabled: true,
        delNodeDisabled: true,
      });
      if (!this.clusterTree.children) this.clusterTree.children = [];
      this.clusterTree.addChildren(node);
    },

    selectCluster(params) {
      return this.$emit("candidateSelected", params.id);
    },
  },
};
</script>


<style lang="less" rel="stylesheet/less">
.vtl {
  .vtl-drag-disabled {
    background-color: #cfd0d0;

    &:hover {
      background-color: #d0cfcf;
    }
  }

  .selectedNode {
    background-color: coral;
  }

  .vtl-disabled {
    background-color: #d0cfcf;
  }

  .vtl-active {
    outline: 2px dashed pink;
  }
}
</style>

<style lang="less" rel="stylesheet/less" scoped>
.icon {
  &:hover {
    cursor: pointer;
    color: #71bfec;
  }
}

.selected {
  color: #0f80c2;
  font-weight: 500;
}

.parent {
  color: purple;
  font-weight: 500;
}

.muted {
  color: gray;
  font-size: 80%;
  display: none;
}
</style>