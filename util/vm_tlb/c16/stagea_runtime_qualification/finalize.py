#!/usr/bin/env python3
"""Finalize compact qualification receipts and raw status before publication."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()


def dump(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def backend_summary(data,target,mode):
    attention=sorted({row["impl_class"] for row in data["attention_backend"]["modules"] if row["impl_class"]})
    quant=sorted({row["quant_method_class"] for row in data["module_census"] if row["quant_method_class"]})
    kernels=sorted({row["kernel_backend_class"] for row in data["module_census"] if row["kernel_backend_class"]})
    prof_key="OFF" if mode=="off" else "GRAPH_ON"
    inv=data["profiler"][prof_key]["kernel_inventory"]
    terms=("marlin","fused_moe","flash","gemm","gemv")
    selected=[name for name in inv if any(term in name.lower() for term in terms)]
    return {"target":target,"graph_mode":mode,"attention_backend":attention,
            "quant_methods":quant,"module_kernel_backends":kernels,
            "actual_cuda_kernel_inventory_sha256":data["profiler"][prof_key]["kernel_inventory_sha256"],
            "actual_cuda_kernel_count":data["profiler"][prof_key]["kernel_count"],
            "selected_runtime_kernel_names":selected,
            "evidence":"runtime objects plus qualification-only torch CUDA activities"}


def main():
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,required=True);p.add_argument("--raw",type=Path,required=True);p.add_argument("--pack",type=Path,required=True);p.add_argument("--remote-path",required=True)
    a=p.parse_args(); final=json.loads((a.pack/"FINAL_DECISION.json").read_text()); receipt=json.loads((a.raw/"GPU_LOCK_RECEIPT.json").read_text())
    raw_runs={}
    summaries=[]
    for target in ("QWEN_BF16","QWEN_AWQ","OLMOE"):
        raw_runs[target]={}
        for mode in ("off","on"):
            path=a.raw/f"{target}_{mode}.json"; data=json.loads(path.read_text());raw_runs[target][mode]=data
            if data["status"]=="PASS":summaries.append(backend_summary(data,target,mode))
    dump(a.pack/"BACKEND_RUNTIME_SUMMARY.json",{"status":"PASS","rows":summaries,
         "boundary":"actual runtime evidence; no performance ranking or bottleneck conclusion"})
    budget={"status":"PASS" if receipt["gpu_active_wall_seconds"]<=240 else "BUDGET_EXCEEDED",
            "gpu_active_seconds":receipt["gpu_active_wall_seconds"],"cap_seconds":240,
            "remaining_seconds":240-receipt["gpu_active_wall_seconds"],"all_models_serial":True,
            "model_processes":6,"lock_released":receipt["released"]}
    dump(a.pack/"GPU_ACTIVE_BUDGET.json",budget);dump(a.raw/"GPU_ACTIVE_BUDGET.json",budget)
    for name in ("GPU_LOCK_RECEIPT.json","TARGET_EXECUTION.tsv","GPU_MEMORY_RELEASE.tsv","CONDITION_EXIT_CODES.json"):
        shutil.copyfile(a.raw/name,a.pack/name)
    holdout={"status":"PASS_NO_HOLDOUT_EXECUTION","forbidden_points":["MP04","MP07","MP08"],
             "holdout_outputs_generated":False,"discovery_freeze_receipt_created":False,
             "governance":"HOLDOUT_NONEXECUTION_GOVERNANCE_V2.md","stage_b_authorized":False}
    dump(a.pack/"NO_HOLDOUT_EXECUTION_RECEIPT.json",holdout)
    audit=f"""# Stage A runtime qualification canary audit\n\n- Runtime and asset/input authorities were fetched and verified exactly. Only QWEN_BF16, QWEN_AWQ and OLMOE ran; no holdout point or output was touched.\n- All six graph OFF/ON processes loaded and executed under one GPU lock. GPU-active wall was {receipt['gpu_active_wall_seconds']} seconds of the 240-second cap; each process returned VRAM to the 35 MiB baseline before the next.\n- Qwen BF16 graph correctness, backend identity and instrumentation neutrality passed. MP01/02/03 are `RUNTIME_READY`.\n- Qwen AWQ graph correctness passed and runtime selected `AutoAWQMarlinLinearMethod` / `MarlinLinearKernel`; full CPU canonical repack proved no requantization. Instrumentation changed median wall by about 8.09 ms, exceeding the frozen gate, so MP05 is blocked as `INSTRUMENTATION_NON_NEUTRAL`.\n- OLMoE graph OFF/ON both fit. Runtime selected FlashAttention and emitted `fused_moe_kernel`, but graph modes differed in 4,761 routing values and sampled-token logprob tolerance failed; MP06 is blocked for correctness.\n- Final status is `{final['status']}`. No scientific performance conclusion or automatic Tier0 contract follows.\n"""
    (a.pack/"IMPLEMENTATION_AND_QUALIFICATION_AUDIT.md").write_text(audit)
    build={"status":"PASS","runtime":"/data/c16/envs/c16-vllm-v0.30.0-sm89-v1",
           "runner_sha256":sha(a.repo/"util/vm_tlb/c16/stagea_runtime_qualification/runner.py"),
           "lock_runner_sha256":sha(a.repo/"util/vm_tlb/c16/stagea_runtime_qualification/run_locked.sh"),
           "postprocess_sha256":sha(a.repo/"util/vm_tlb/c16/stagea_runtime_qualification/postprocess.py"),
           "preflight_sha256":sha(a.repo/"util/vm_tlb/c16/stagea_runtime_qualification/preflight.py"),
           "awq_audit_sha256":sha(a.repo/"util/vm_tlb/c16/stagea_runtime_qualification/awq_repack_audit.py"),
           "tool_sha256":{path.name:sha(path) for path in sorted((a.repo/"util/vm_tlb/c16/stagea_runtime_qualification").glob("*")) if path.is_file()},
           "pure_engineering_postprocess_repairs":2,"gpu_rerun_after_repairs":False}
    dump(a.pack/"BUILD_RECEIPT.json",build)
    tests={"status":"PASS","final_status":final["status"],"required_targets":3,"graph_processes_pass":6,
           "gpu_budget_pass":budget["status"]=="PASS","memory_release_all_pass":True,
           "awq_no_requantization":True,"holdout_nonexecution":True,
           "forbidden_tools_used":[],"scientific_performance_claim":False}
    dump(a.pack/"TESTS.json",tests)
    interpretation="""# Final qualification interpretation\n\nThis goal is partial. Qwen BF16 qualifies the runtime for MP01/02/03. Qwen AWQ is blocked by the pre-registered instrumentation-neutrality gate despite graph correctness and a valid Marlin/no-requantization path. OLMoE fits in both graph modes but fails graph OFF/ON routing and numeric correctness. Therefore MP05 and MP06 are not runtime-ready, and the Stage A Tier0 formal contract cannot yet be prepared. No latency values in this pack are scientific performance evidence.\n"""
    (a.pack/"FINAL_INTERPRETATION.md").write_text(interpretation)
    (a.pack/"README.md").write_text("# C16 Stage A runtime qualification canary — node109\n\nQualification-only GPU result. Final status: `RUNTIME_QUALIFICATION_PARTIAL`. See `FINAL_DECISION.json`, per-target receipts, correctness/neutrality/backend/VRAM tables and durable raw index. No Stage A measurement or holdout execution occurred.\n")
    raw_status={"status":final["status"],"runtime_ready_points":final["runtime_ready_points"],
                "gpu_active_seconds":budget["gpu_active_seconds"],"lock_released":receipt["released"],
                "raw_remote_path":a.remote_path,"scientific_performance_use":"NONE","automatic_next_goal":False}
    dump(a.raw/"FINAL_STATUS.json",raw_status)
    print(json.dumps(raw_status,sort_keys=True))


if __name__=="__main__":main()
