#!/usr/bin/env python3
"""Derive factual per-layer windows and gate/up relations without headroom analysis."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def write(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(rows)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--layer-activity",type=Path,required=True); p.add_argument("--output-dir",type=Path,required=True); args=p.parse_args()
    rows=list(csv.DictReader(args.layer_activity.open(newline=""),delimiter="\t"))
    by=defaultdict(dict)
    for r in rows: by[(int(r["decode_step"]),int(r["layer"]))][r["semantic_role"]]=r
    relations=[]; windows=[]
    for (step,layer),roles in sorted(by.items()):
        if set(roles)!={"gate_proj","up_proj","activation","multiply","down_proj"}: raise RuntimeError("role closure failure")
        gate,up,down=roles["gate_proj"],roles["up_proj"],roles["down_proj"]
        gs,ge,us,ue=int(gate["earliest_gpu_start"]),int(gate["last_gpu_end"]),int(up["earliest_gpu_start"]),int(up["last_gpu_end"])
        overlap=max(0,min(ge,ue)-max(gs,us))
        relations.append({"decode_step":step,"layer":layer,"gate_start":gs,"gate_end":ge,"up_start":us,"up_end":ue,"overlap_ns":overlap,"overlap_observed":overlap>0})
        windows.append({"decode_step":step,"layer":layer,"earliest_producer_start":min(gs,us),"gate_start":gs,"gate_end":ge,"up_start":us,"up_end":ue,
                        "activation_start":roles["activation"]["earliest_gpu_start"],"activation_end":roles["activation"]["last_gpu_end"],
                        "multiply_start":roles["multiply"]["earliest_gpu_start"],"multiply_end":roles["multiply"]["last_gpu_end"],
                        "down_start":down["earliest_gpu_start"],"down_end":down["last_gpu_end"],"last_consumer_completion":int(down["last_gpu_end"])})
    write(args.output_dir/"GATE_UP_RELATION.tsv",tuple(relations[0]),relations)
    write(args.output_dir/"FFN_LAYER_WINDOWS.tsv",tuple(windows[0]),windows)
    kernels={role:sorted(set(k for r in rows if r["semantic_role"]==role for k in r["kernel_names"].split("|") if k)) for role in ("gate_proj","up_proj","activation","multiply","down_proj")}
    facts={"status":"PASS","layer_decode_windows":len(windows),"gate_up_overlap_observed_count":sum(r["overlap_observed"] for r in relations),
           "gate_up_nonoverlap_count":sum(not r["overlap_observed"] for r in relations),
           "activation_implementation":"DISTINCT_GPU_ACTIVITY" if all(r["gpu_activity_count"]=="1" for r in rows if r["semantic_role"]=="activation") else "MIXED",
           "multiply_implementation":"DISTINCT_GPU_ACTIVITY" if all(r["gpu_activity_count"]=="1" for r in rows if r["semantic_role"]=="multiply") else "MIXED",
           "kernel_names_by_role":kernels,"headroom_computed":False}
    (args.output_dir/"IMPLEMENTATION_FACTS.json").write_text(json.dumps(facts,indent=2,sort_keys=True)+"\n")
    print(json.dumps(facts,sort_keys=True))


if __name__=="__main__": main()
