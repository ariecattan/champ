import json 
import jsonlines 
import sys 
import networkx as nx 
from itertools import permutations
import numpy as np 


class Evaluation:
  def __init__(self, gold_path, system_path, topics=None):
    with jsonlines.open(gold_path, "r") as f:
      self.gold = {x["topic"]: x for x in f}
    with jsonlines.open(system_path, "r") as f:
      self.system = {x["topic"]: x for x in f}
    
    if topics is None:
      self.gold = {k:v for k,v in self.gold.items() if k in self.system}
      self.system = {k:v for k,v in self.system.items() if k in self.gold}
    else:
      self.gold = {k:v for k,v in self.gold.items() if k in topics}
      self.system = {k:v for k,v in self.system.items() if k in topics}

  def _cast_to_number(self, topic):
    clusters = {int(k): v for k,v in topic["clusters"].items()}
    kps = {int(k): v for k, v in topic["kps"].items()}
    return {
      "topic": topic["topic"],
      "kps": kps,
      "clusters": clusters,
      "relations": topic["relations"]
    }

  def evaluate(self, return_raw_scores=False):
    results = []
    for topic_id in self.gold.keys():
      if topic_id not in self.system:
        continue
      results.append(self.evaluate_topic(topic_id))

    scores = {
      "recall": round(np.average([x["recall"] for x in results]), 4),
      "precision": round(np.average([x["precision"] for x in results]), 4),
      "f1": round(np.average([x["f1"] for x in results]), 4),
    }

    if return_raw_scores:
      scores["per_topic"] = results 

    return scores

  def evaluate_topic(self, topic_id):
    if topic_id not in self.gold or topic_id not in self.system:
      raise ValueError(topic_id)

    gold_topic = self.gold[topic_id]
    sys_topic = self.system[topic_id]

    gold_tree = self._get_topic_graph(gold_topic)
    system_tree = self._get_topic_graph(sys_topic)

    m2c_gold = self._get_mention2cluster(gold_topic)
    m2c_system = self._get_mention2cluster(sys_topic)


    tp, tn, fp, fn = 0, 0, 0, 0

    for a, b in permutations(list(range(len(gold_topic["kps"]))), 2):
      # same cluster in both gold and system 
      is_gold_link = m2c_gold[a] == m2c_gold[b] or nx.has_path(gold_tree, m2c_gold[a], m2c_gold[b])
      is_sys_link = m2c_system[a] == m2c_system[b] or nx.has_path(system_tree, m2c_system[a], m2c_system[b])

      if is_gold_link and is_sys_link:
        tp += 1 
      elif is_gold_link and not is_sys_link:
        fn += 1
      elif not is_gold_link and is_sys_link:
        fp += 1
      else:
        tn += 1


    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    return {
      "topic_id": topic_id,
      "precision": precision,
      "recall": recall,
      "f1": 2 * precision * recall / (precision + recall)
    }
      

  def _get_mention2cluster(self, topic):
    mention2cluster = {}
    for cluster_id, cluster in enumerate(topic["clusters"]):
      for kp in cluster:
        mention2cluster[kp] = cluster_id

    return mention2cluster
    

  def _get_topic_graph(self, topic):
    G = nx.DiGraph()
    G.add_nodes_from(list(range(len(topic["clusters"]))))
    G.add_edges_from(topic["relations"])
    return G 



  
  



if __name__=="__main__":
  if (len(sys.argv) <= 2):
    raise ValueError(f"The args should be at least two files")

  topics = None if len(sys.argv) == 3 else sys.argv[3:]
  print(topics)

  evaluation = Evaluation(sys.argv[1], sys.argv[2], topics)
  results = evaluation.evaluate()
  print(results)
