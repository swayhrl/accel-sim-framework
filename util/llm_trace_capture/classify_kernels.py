#!/usr/bin/env python3
"""Make non-destructive full and compute-only kernel manifests from kernelslist.g."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
NCCL=re.compile(r"(?:nccl|allreduce|all_gather|reduce_scatter|broadcast)",re.I)
def classify(name:str)->str:
    if NCCL.search(name): return "NCCL_COLLECTIVE"
    if not name.strip() or name.lstrip().startswith("#"): return "UNKNOWN_OTHER"
    return "COMPUTE"
def build(lines:list[str])->list[dict]: return [{"index":i,"raw":line,"classification":classify(line)} for i,line in enumerate(lines)]
def main():
    p=argparse.ArgumentParser();p.add_argument("--kernelslist",type=Path);p.add_argument("--output-dir",type=Path);p.add_argument("--self-test",action="store_true");a=p.parse_args()
    if a.self_test:
        rows=build(["gemm", "ncclAllReduceKernel", ""]);assert [r["classification"] for r in rows]==["COMPUTE","NCCL_COLLECTIVE","UNKNOWN_OTHER"];print("PASS kernel classifier self-test");return
    if not a.kernelslist or not a.output_dir:p.error("--kernelslist and --output-dir are required")
    raw=a.kernelslist.read_text().splitlines();rows=build(raw);a.output_dir.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(a.kernelslist.read_bytes()).hexdigest();manifest={"schema_version":"m4a-kernel-classification-v1","source":str(a.kernelslist),"source_sha256":digest,"rules":{"NCCL_COLLECTIVE":NCCL.pattern,"COMPUTE":"non-empty line not matching NCCL","UNKNOWN_OTHER":"empty/comment"},"kernels":rows}
    (a.output_dir/"full-kernel-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    compute="\n".join(row["raw"] for row in rows if row["classification"]=="COMPUTE")+"\n";(a.output_dir/"compute-only-kernelslist.g").write_text(compute)
    (a.output_dir/"classification-command.txt").write_text(" ".join(__import__("sys").argv)+"\n")
    print(f"PASS raw_retained={a.kernelslist} full_manifest={a.output_dir/'full-kernel-manifest.json'} compute_only={a.output_dir/'compute-only-kernelslist.g'}")
if __name__=="__main__":main()
