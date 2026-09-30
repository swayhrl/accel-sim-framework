#!/usr/bin/env python3
"""Validate timeline closure and build the Git-safe producer review pack."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()


def load(path): return json.loads(path.read_text())


def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--pack",type=Path,required=True);args=p.parse_args()
    raw,pack=args.raw,args.pack;pack.mkdir(parents=True,exist_ok=True)
    neutrality=load(raw/"INSTRUMENTATION_NEUTRALITY.json"); formal=load(raw/"FORMAL_SANITY.json"); assertions=load(raw/"RAW_ASSERTIONS.json"); lock=load(raw/"GPU_LOCK_RECEIPT.json"); publish=load(raw/"PUBLISH_RECEIPT.json"); facts=load(raw/"IMPLEMENTATION_FACTS.json")
    if neutrality["status"]!="PASS" or formal["status"]!="PASS": raise RuntimeError("neutrality/formal sanity failed")
    if assertions["status"]!="PASS" or assertions["semantic_range_count"]!=560 or assertions["projection_missing_activity"]!=0: raise RuntimeError("timeline closure failed")
    if lock["exit_code"]!=0 or lock["wall_seconds"]>1200: raise RuntimeError("GPU lock/budget receipt failed")
    if publish["status"]!="PASS_DURABLE_PUBLISH_AND_COPYBACK": raise RuntimeError("durable publish failed")
    copies=("SEMANTIC_RANGE_MAP.tsv","CUDA_CORRELATION.tsv","GPU_ACTIVITY.tsv","FFN_LAYER_ACTIVITY.tsv","FFN_LAYER_WINDOWS.tsv","GATE_UP_RELATION.tsv","DECODE_WALL_INTERVAL.tsv","OUTPUT_CHECKS.tsv","INSTRUMENTATION_NEUTRALITY.json","FORMAL_SANITY.json","RAW_ASSERTIONS.json","IMPLEMENTATION_FACTS.json","GPU_LOCK_RECEIPT.json","PUBLISH_RECEIPT.json","RUN_MANIFEST.json","COMMANDS.tsv")
    for name in copies: shutil.copyfile(raw/name,pack/name)
    index=[]
    for path in sorted(x for x in raw.iterdir() if x.is_file()):
        index.append((path.name,str(path),path.stat().st_size,sha(path),path.name if path.name in copies else "INDEX_ONLY",str(Path(publish["remote_path"])/path.name)))
    with (pack/"RAW_INDEX.tsv").open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t",lineterminator="\n");w.writerow(("artifact","node109_path","bytes","sha256","committed_copy","node164_path"));w.writerows(index)
    runner_runs=[]
    for label in ("canary_off","canary_on","formal"):
        d=load(raw/f"{label}.json")
        runner_runs.append({"label":label,"generated_token_ids":d["generated_token_ids_D0_D3"],"decode_step_ms":d["decode_step_ms"],"call_order_count":len(d["call_order"]),"occurrence_count":len(d["occurrences"]),"json_sha256":sha(raw/f"{label}.json")})
    sanity={"status":"PASS","profile_perturbed":False,"kernel_count_each":neutrality["left_kernel_count"],"kernel_sequence_sha256":neutrality["left_kernel_sequence_sha256"],"runs":runner_runs,"semantic_ranges":assertions,"headroom_computed":False}
    (pack/"NATIVE_SANITY.json").write_text(json.dumps(sanity,indent=2,sort_keys=True)+"\n")
    final={"status":"TIMELINE_AUTHORITY_CAPTURE_PASS","exact_natural_scenario_reproduced":True,"layers":28,"decode_steps":4,"layer_decode_windows":facts["layer_decode_windows"],"gate_up_overlap_observed_count":facts["gate_up_overlap_observed_count"],"activation_implementation":facts["activation_implementation"],"multiply_implementation":facts["multiply_implementation"],"correlation_authority_sufficient":True,"instrumentation_neutral":True,"profile_perturbed":False,"durable_raw_path":publish["remote_path"],"headroom_computed":False}
    (pack/"FINAL_STATUS.json").write_text(json.dumps(final,indent=2,sort_keys=True)+"\n")
    lines=[]
    for path in sorted(x for x in pack.rglob("*") if x.is_file() and x.name!="SHA256SUMS" and "__pycache__" not in x.parts): lines.append(f"{sha(path)}  {path.relative_to(pack)}")
    (pack/"SHA256SUMS").write_text("\n".join(lines)+"\n")
    print(json.dumps(final,sort_keys=True))


if __name__=="__main__": main()
