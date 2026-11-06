"""Print the Yosys cell statistics and critical path of one synthesized
design from its log in results/synth/.  Usage: python synth_report.py trunc_k8"""
import os
import re
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "trunc_k8"
path = os.path.join(os.path.dirname(__file__), "..", "results", "synth", f"{name}.log")
log = open(path).read()

stat = log[log.rfind("Printing statistics."):]
stat = stat[:stat.find("\n\n", stat.find("cells"))]
print(f"--- results/synth/{name}.log ---")
for line in stat.splitlines():
    if line.strip() and "+---" not in line and line.strip() != "|":
        print(line)
print(re.findall(r"Longest topological path.*", log)[-1])
