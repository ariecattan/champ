import json
import os
from itertools import chain, combinations, permutations
import jsonlines
import collections
import networkx as nx
import sys
import argparse
from tqdm import tqdm


def get_binary_relations(hypernyms, cluster2id):
    binary_relations = []
    if 'children' not in hypernyms:
        raise ValueError(hypernyms)
    stack = hypernyms['children'].copy()

    while stack:
        node = stack.pop()

        if 'children' in node:
            node_relations = []
            for child in node['children']:
                node_relations.append((node['id'], child['id']))
                stack.append(child.copy())
            binary_relations.append(node_relations)

    # exclude links with the ZZZ node
    all_relations, bad_kps = [], set()
    for x, y in list(chain.from_iterable(binary_relations)):
        if x in cluster2id and y in cluster2id:
            all_relations.append((cluster2id[x], cluster2id[y]))
        else:
            bad_kps.add(cluster2id[y]) # add bad kps under the ZZZ

    return all_relations, bad_kps


def get_domain(topic_id):
    if topic_id.lower().startswith("austin"):
        return "austin"
    elif topic_id.lower().startswith("pc"):
        return "amazon"
    return "yelp"

def get_topic_data(dir_path):
    topic_data = []
    for topic in tqdm(os.listdir(dir_path)):
        path = os.path.join(dir_path, topic)
        if not path.endswith("json"):
            continue
        print(topic)
        with open(path, "r") as f:
            data = json.load(f)

        # add kps
        tokens = [x["text"] for x in data["tokens"]]

        # add clusters
        clusters = collections.defaultdict(list)

        kps = []

        # ignoring the first dummy mentions (ZZZ)
        for kp in data["mentions"][1:]:
            kps.append(" ".join(tokens[kp["start"]:kp["end"]+1]))
            clusters[kp["clustId"][0]].append(int(kp["m_id"]) - 1) # -1 because ZZZ = 0
        cluster2id = {cluster: i for i, cluster in enumerate(clusters)}

        # relations
        relations, bad_kps = get_binary_relations(data['tree'][0], cluster2id)
        all_clusters = list(clusters.values())
        
        topic_data.append({
            "topic": data["id"],
            "domain": get_domain(data["id"]),
            "kps": kps,
            "clusters": all_clusters,
            "relations": relations,
            "bad_kps": list(chain.from_iterable([all_clusters[x] for x in bad_kps])),
            "description": data.get("description", "")
        })

    return topic_data


def get_stat(data):
    bidirectional, unidirectional = 0, 0

    mention2cluster = {}
    for cluster_id, cluster in enumerate(data["clusters"]):
        for kp in cluster:
            mention2cluster[kp] = cluster_id

    G = nx.DiGraph()
    G.add_nodes_from(list(range(len(data["clusters"]))))
    G.add_edges_from(data["relations"])
    for a, b in permutations(range(len(data["kps"])), 2):
        cluster_a, cluster_b = mention2cluster[a], mention2cluster[b]
        if cluster_a == cluster_b:
            bidirectional += 1
        elif nx.has_path(G, cluster_a, cluster_b) or nx.has_path(G, cluster_b, cluster_a):
            unidirectional += 1

    return bidirectional, unidirectional


def get_child_viz(level, child):
    viz = "\t" * level + ("|- " if level != 0 else "") + child["name"] + "\n"
    if "children" in child:
        for x in child["children"]:
            viz += get_child_viz(level + 1, x)
    return viz


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str, default=None)
    parser.add_argument("--viz", action="store_true")
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = args.input_dir

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    topic_data = get_topic_data(args.input_dir)
    with jsonlines.open(os.path.join(args.output_dir, "data.jsonl"), "w") as f:
        f.write_all(topic_data)
    bi, uni = zip(*[get_stat(topic) for topic in topic_data])
    print(f"bidirectionall: {sum(bi)}\nunidrectional: {sum(uni)}")

    if args.viz:
        viz_output_dir = os.path.join(args.output_dir, "visualization")
        if not os.path.exists(viz_output_dir):
            os.makedirs(viz_output_dir)

        for topic in os.listdir(args.input_dir):
            if not topic.endswith("json"):
                continue
            with open(os.path.join(args.input_dir, topic), "r") as f:
                data = json.load(f)
            viz = "".join([get_child_viz(0, x)
                          for x in data["tree"][0]["children"]])
            with open(os.path.join(viz_output_dir, f"{data['id']}.txt"), "w") as f:
                f.write(viz)
