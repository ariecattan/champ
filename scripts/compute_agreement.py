from evaluate import Evaluation
from itertools import combinations
import os
import pandas as pd 
import sys
from tabulate import tabulate
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("--annotators", nargs='+', help='list of data files')
parser.add_argument("--topics", nargs='+', default=None, help="compute agreement only on a specific topic id")
args = parser.parse_args()

agreement = {}

for x, y in combinations(args.annotators, 2):
  evaluation = Evaluation(x, y, args.topics)
  results = evaluation.evaluate()

  agreement[(x, y)] = results["f1"]

data = {}
for x in args.annotators:
  row = []
  for y in args.annotators:
    if x == y:
      row.append(1)
    else:
      row.append(agreement[(x, y)] if (x, y) in agreement else agreement[(y, x)])
  data[x] = row


df = pd.DataFrame.from_dict(data, orient="index", columns=args.annotators)
print(tabulate(df, headers='keys', tablefmt='psql'))

