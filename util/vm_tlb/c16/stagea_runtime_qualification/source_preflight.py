#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); tools=a.repo/"util/vm_tlb/c16/stagea_runtime_qualification"
    runner=tools/"runner.py"; locked=tools/"run_locked.sh"; post=tools/"postprocess.py"
    for path in (runner,post): ast.parse(path.read_text())
    text=locked.read_text().lower(); runner_text=runner.read_text()
    pack=a.output_dir
    checks={
        "authority_pass":json.loads((pack/"CANARY_AUTHORITY.json").read_text())["status"]=="PASS",
        "assets_pass":json.loads((pack/"ASSET_VISIBILITY_AND_SHA.json").read_text())["status"]=="PASS",
        "awq_repack_pass":json.loads((pack/"AWQ_REPACK_CANONICAL_RECEIPT.json").read_text())["status"]=="PASS",
        "thresholds_frozen":json.loads((pack/"CORRECTNESS_AND_NEUTRALITY_THRESHOLDS.json").read_text())["status"]=="FROZEN_BEFORE_GPU_RESULTS",
        "target_scope_exact":json.loads((pack/"GPU_CANARY_PLAN.json").read_text())["target_order"]==["QWEN_BF16","QWEN_AWQ","OLMOE"],
        "single_lock":text.count("flock -w 2700")==1,
        "budget_240": "240-used" in text and "gpu_active_cap_seconds\":240" in text,
        "forbidden_tools_absent":all(token not in text for token in ("nsys","ncu","nvbit","sass","accel-sim")),
        "no_cpu_offload": "cpu_offload_gb=0" in runner_text,
        "no_fallback_model_impl": 'model_impl="vllm"' in runner_text,
        "frozen_shapes": '"max_model_len": 544' in runner_text and "max_num_seqs=1" in runner_text,
        "qualification_profiler_only": "torch.profiler" in runner_text,
    }
    result={"status":"PASS" if all(checks.values()) else "SOURCE_PREFLIGHT_FAILED","checks":checks,
            "runner_sha256":sha(runner),"run_locked_sha256":sha(locked),"postprocess_sha256":sha(post),
            "runtime":"/data/c16/envs/c16-vllm-v0.30.0-sm89-v1","gpu_active_cap_seconds":240,
            "capture_boundary":"qualification-only torch CUDA activity inventory; no NSYS/NCU/NVBit/SASS"}
    (pack/"SOURCE_PREFLIGHT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    if result["status"]!="PASS": raise SystemExit(2)


if __name__=="__main__": main()
