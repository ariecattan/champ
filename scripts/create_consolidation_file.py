import json 
from itertools import chain
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("--input", nargs='+', help="path of annotation files")
parser.add_argument("--output", type=str, help="output path")
args = parser.parse_args()

data = []
for path in args.input:
  print(path)
  with open(path, "r") as f:
    data.append(json.load(f))

mention2cluster = {}
for i, mention in enumerate(data[0]["mentions"]):
  mention2cluster[i] = mention["clustId"][:1] + \
      list(chain.from_iterable([annotator["mentions"][i]["clustId"][:1] 
      for annotator in data[1:]]))

mentions = data[0]["mentions"].copy()
for i, mention in enumerate(mentions):
  mention["clustId"] = mention2cluster[i]

champ = {
  "id": data[0]["id"],
  "reassignable": True,
  "hierarchy": True,
  "local": True,
  "showHypernym": False,
  "done": False,
  "mode": "reviewer",
  "selectedCluster": data[0]["mentions"][0]["clustId"][0], 
  "tokens": data[0]["tokens"],
  "mentions": mentions,
  "tree": [annotation["tree"][0] for annotation in data]
}


with open(args.output, "w") as f:
  json.dump(champ, f, indent=4)