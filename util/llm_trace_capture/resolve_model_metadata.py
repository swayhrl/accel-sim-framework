#!/usr/bin/env python3
"""Resolve only Hugging Face model metadata; never request a model file."""
from __future__ import annotations
import argparse, json, os, re
EXPECTED="4e20de362430cd3b72f300e6b0f18e50e7166e08"; MODEL="meta-llama/Llama-3.2-1B"
def main():
    p=argparse.ArgumentParser();p.add_argument("--dry-run",action="store_true");p.add_argument("--output");a=p.parse_args()
    if a.dry_run: print(json.dumps({"model_id":MODEL,"expected_revision":EXPECTED,"token_source":"HF_TOKEN environment only","downloads_weights":False},sort_keys=True));return
    from huggingface_hub import HfApi
    info=HfApi(token=os.environ.get("HF_TOKEN")).model_info(MODEL,expand=["config"])
    if not re.fullmatch(r"[0-9a-f]{40}",info.sha or ""):raise RuntimeError("metadata response omitted immutable revision")
    result={"model_id":MODEL,"revision":info.sha,"expected_revision":EXPECTED,"matches_expected":info.sha==EXPECTED,"declared_torch_dtype":(info.config or {}).get("torch_dtype","UNKNOWN"),"weights_downloaded":False}
    if a.output: open(a.output,"w",encoding="utf-8").write(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True));
if __name__=="__main__":main()
