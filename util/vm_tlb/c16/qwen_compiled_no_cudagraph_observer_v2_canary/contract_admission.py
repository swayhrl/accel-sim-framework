#!/usr/bin/env python3
"""Exact Lane6 contract admission. No CUDA import or GPU lock."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1"
COMMIT="eaaa2e66befa872ce7c8f47011e9fe7cdf8921d9"
TREE="f2d9d3a46ca3774a82eaeb2175b01a6cdbec9d2f"
BRANCH="origin/hrl/c16-qwen-compiled-no-cudagraph-observer-v2-contract-174new-v1"
BASE="docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CONTRACT_174NEW_V1/"
CONTRACT=BASE+"C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1.json"
CONTRACT_SHA="bf5584db66cf66d076e49d5fbbe9053d9a614c88eccaf514518137ee3812ef68"
SOURCE_PREFIX="util/vm_tlb/c16/qwen_compiled_no_cudagraph_observer_v2/"

def git(*args):return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def blob(commit,path):return subprocess.check_output(["git","-C",str(ROOT),"show",f"{commit}:{path}"])
def sha(data):return hashlib.sha256(data).hexdigest()

def admit():
    raw=blob(COMMIT,CONTRACT)
    contract=json.loads(raw)
    correct=json.loads(blob(COMMIT,BASE+"CORRECTNESS_AND_NEUTRALITY_CONTRACT.json"))
    final=json.loads(blob(COMMIT,BASE+"FINAL_DECISION.json"))
    manifest={line.split("  ",1)[1]:line.split("  ",1)[0] for line in blob(COMMIT,BASE+"SHA256SUMS").decode().splitlines()}
    checks={
        "branch_exact":git("rev-parse",BRANCH)==COMMIT,
        "commit_exact":git("rev-parse",COMMIT)==COMMIT,
        "tree_exact":git("rev-parse",COMMIT+"^{tree}")==TREE,
        "contract_sha_exact":sha(raw)==CONTRACT_SHA==manifest[CONTRACT],
        "manifest_all_exact":all(sha(blob(COMMIT,path))==digest for path,digest in manifest.items()),
        "status_authorized":contract["status"]=="AUTHORIZED_BY_PROJECT_REVIEW" and contract["execution_authorized"] is True,
        "finalized":final["status"]=="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CONTRACT_FINALIZED" and final["execution_authorized"] is True,
        "node_exact":contract["node"]=="109" and contract["gpu"]=="RTX4080_SM89",
        "upstream_mode_canary":contract["authority"]["mode_b_runtime_pass_commit"]=="9122fac5c50dbf19706636fc03978a356ffd800f",
        "observer_source":contract["authority"]["observer_v2_source_commit"]=="f63d39c8d90ced038445c264fa8242c524a1aa6f",
        "scope_exact":contract["scope"]["points_in_order"]==["MP02","MP03"] and contract["scope"]["MP02"]["batch"]==1 and contract["scope"]["MP03"]["batch"]==4 and contract["scope"]["dtype"]=="bfloat16",
        "mode_b_exact":contract["mode_b_required_identity"]["enforce_eager"] is False and contract["mode_b_required_identity"]["compilation_config_python"]=="CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)" and contract["mode_b_required_identity"]["effective_compilation_mode"]=="VLLM_COMPILE" and contract["mode_b_required_identity"]["backend"]=="inductor" and contract["mode_b_required_identity"]["effective_cudagraph_mode"]=="NONE" and contract["mode_b_required_identity"]["capture_replay_count"]==0,
        "correctness_frozen":correct["sampled_logprob"]["atol"]==0.05 and correct["sampled_logprob"]["rtol"]==0.01 and correct["sampled_logprob"]["relaxation_allowed"] is False and correct["generated_tokens"]=="exact per frozen row and step",
        "neutrality_frozen":correct["neutrality_primary"]=="request_cuda_event_ms" and correct["native_protocol"]["sample_order"]==["OFF","ON","ON","OFF","OFF","ON"] and correct["native_protocol"]["warmup_per_arm"]==1 and correct["native_protocol"]["samples_per_arm"]==3,
        "observer_semantic_exact":contract["observer_v2"]["per_occurrence_cuda_event_constructors"]==0 and contract["observer_v2"]["expected_modules"]==144 and contract["observer_v2"]["expected_semantic_occurrences_per_request"]==4608 and contract["observer_v2"]["expected_ordinals"]=="0..4607" and contract["observer_v2"]["semantic_sequence_revision_after_results"] is False,
        "budget_exact":contract["budget"]["total_gpu_active_seconds_cap"]<=180 and contract["budget"]["per_point_seconds_cap"]=={"MP02":75,"MP03":105} and contract["budget"]["unused_point_time_transfer"] is False,
        "source_runner_sha_exact":sha(blob(COMMIT,SOURCE_PREFIX+"runner.py"))==contract["source_identity"]["runner_sha256"],
        "source_observer_sha_exact":sha(blob(COMMIT,SOURCE_PREFIX+"observer_v2.py"))==contract["source_identity"]["observer_sha256"],
        "expected_sequence_sha_exact":sha(blob(COMMIT,BASE+"EXPECTED_SEMANTIC_SEQUENCE.tsv"))==contract["source_identity"]["expected_sequence_sha256"],
        "mode_a_c_excluded":"MODE_A" in contract["scope"]["excluded"] and "MODE_C_HISTORICAL_FAILED" in contract["scope"]["excluded"],
        "nsys_bounded":contract["structural_nsys"]["max_captures_per_point"]==1 and contract["structural_nsys"]["command_trace"]=="nsys --trace=cuda,nvtx",
        "automatic_next_goal_false":contract["automatic_tier0_rerun"] is False,
    }
    result={"status":"PASS" if all(checks.values()) else "CONTRACT_AUTHORITY_FAILURE",
            "commit":COMMIT,"tree":TREE,"contract_path":CONTRACT,"contract_sha256":sha(raw),
            "source_runner_sha256":sha(blob(COMMIT,SOURCE_PREFIX+"runner.py")),
            "source_observer_sha256":sha(blob(COMMIT,SOURCE_PREFIX+"observer_v2.py")),
            "expected_sequence_sha256":sha(blob(COMMIT,BASE+"EXPECTED_SEMANTIC_SEQUENCE.tsv")),
            "checks":checks,"cuda_initialized":False,"gpu_lock_acquired":False}
    PACK.mkdir(parents=True,exist_ok=True)
    (PACK/"CONTRACT_AUTHORITY.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if result["status"]!="PASS":
        raise RuntimeError("CONTRACT_AUTHORITY_FAILURE")
    return contract

if __name__=="__main__":
    result=admit()
    print(json.dumps({"status":"PASS","goal":result["goal"],"checks":22}))
