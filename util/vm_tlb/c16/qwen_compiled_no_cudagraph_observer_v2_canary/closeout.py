#!/usr/bin/env python3
"""CPU-only failure closeout, receipt validation and SHA manifest generation."""
import fcntl
import hashlib
import json
import subprocess
from pathlib import Path

from run_guard import LOCK,gpu_query

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1"
PREP=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_PREP_109_V1"
EXACT=ROOT/"util/vm_tlb/c16/qwen_compiled_no_cudagraph_observer_v2"
HERE=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")

def manifest(pack):
    files=sorted(p for p in pack.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (pack/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    return len(files)

def main():
    final=json.loads((PACK/"FINAL_DECISION.json").read_text())
    assert final["decision"]=="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
    raw=Path(final["raw_local"])
    native=json.loads((raw/"MP02_NATIVE.json").read_text())
    assert native["gate_status"]==final["decision"] and native["error"]=="semantic coverage count 0 != frozen 4608"
    semantic=native["semantic_failure_receipts"][0]
    assert len(semantic["semantic_order"])==len(semantic["semantic_ranges"])==0
    assert not any(raw.glob("MP03_*")) and not any(raw.glob("*.nsys-rep"))
    expected=Path("/data/c16/qwen_compiled_no_cudagraph_observer_v2_canary_v1/contract_gate/EXPECTED_SEMANTIC_SEQUENCE.tsv")
    save(PACK/"MP02_IDENTITY_FAILURE_DETAIL.json",{
        "status":"COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL",
        "first_failure":"MP02_OBSERVER_ON_WARMUP_SEMANTIC_COVERAGE",
        "expected_semantic_occurrences_per_request":4608,"actual_semantic_occurrences":0,
        "semantic_receipt_sha256":semantic["semantic_order_sha256"],
        "expected_sequence_sha256":sha(expected),
        "effective_mode_b_config_pre_request":"SOURCE_CONTROL_FLOW_GATE_REACHED_AND_PASSED",
        "observer_on_compiled_call_path":"UNRESOLVED_AFTER_SEMANTIC_FAILURE",
        "native_six_samples":"NOT_STARTED","off_on_output_correctness":"NOT_EVALUATED",
        "neutrality":"NOT_EVALUATED","kernel_inventory":"NOT_COLLECTED",
        "mp03":"NOT_RUN_MP02_GATE_FAIL","nsys":"NOT_RUN_MP02_NATIVE_GATE_FAIL",
        "inference":"Python module hooks did not emit ranges in this compiled execution; mechanism beyond this observed failure is not claimed."})
    save(PACK/"CORRECTNESS_NEUTRALITY_STATUS.json",{
        "point":"MP02","correctness":"NOT_EVALUATED_SIX_NATIVE_SAMPLES_NOT_STARTED",
        "neutrality_primary_cuda_event_median":"NOT_EVALUATED",
        "neutrality_host_crosscheck":"NOT_EVALUATED",
        "mp03_four_rows":"NOT_RUN_MP02_GATE_FAIL"})
    save(PACK/"KERNEL_INVENTORY_STATUS.json",{"MP02":"NOT_COLLECTED_SEMANTIC_WARMUP_FAILED",
                                               "MP03":"NOT_RUN","off_on_exact":"NOT_EVALUATED"})
    save(PACK/"NSYS_STRUCTURE.json",{"status":"NOT_RUN_MP02_NATIVE_GATE_FAIL","capture_count":0,
                                     "trace_domains":[],"structural_result":"NOT_EVALUATED"})
    source={name:sha(EXACT/name) for name in ("runner.py","observer_v2.py","build_expected_sequence.py","validate_static.py")}
    save(PACK/"SOURCE_INTEGRATION.json",{"lane6_contract_commit":"eaaa2e66befa872ce7c8f47011e9fe7cdf8921d9",
         "lane6_source_exact_sha256":source,"expected_sequence_sha256":sha(expected),
         "mode_b_correctness_authority":"9122fac5c50dbf19706636fc03978a356ffd800f",
         "observer_v2_source_authority":"f63d39c8d90ced038445c264fa8242c524a1aa6f",
         "historical_mode_c_stop_preserved":True})
    with LOCK.open("a+") as f:
        fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        fcntl.flock(f,fcntl.LOCK_UN)
    post=gpu_query()
    assert post["compute_processes"]==[]
    save(PACK/"GPU_POSTFLIGHT.json",{"lock_reacquired_and_released":True,"gpu":post,
                                      "unknown_compute_processes":0})
    contract=json.loads((PACK/"CONTRACT_AUTHORITY.json").read_text())
    budget=json.loads((PACK/"GPU_ACTIVE_BUDGET.json").read_text())
    publish=json.loads((PACK/"PUBLISH_RECEIPT.json").read_text())
    assert contract["status"]=="PASS" and budget["within_all_caps"] and publish["status"]=="PASS_DURABLE_PUBLISH_AND_COPYBACK"
    assert publish["remote_verify"]["status"]==publish["copyback_verify"]["status"]=="PASS"
    assert budget["by_point_seconds"]["MP03"]==0 and budget["total_gpu_active_seconds_conservative_wall"]<75
    test_outputs={}
    commands={
      "source_compile":["python3","-m","py_compile",str(EXACT/"runner.py"),str(EXACT/"observer_v2.py")],
      "lane6_static":["python3",str(EXACT/"validate_static.py"),"--vllm-repo","/data/c16/runtime_environment_audit_v1/source/vllm-v0.30.0","--model-config","/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1/config.json"],
      "exact_synthetic":["python3",str(HERE/"test_exact.py")],
    }
    for name,cmd in commands.items():
        result=subprocess.run(cmd,capture_output=True,text=True,check=True)
        test_outputs[name]=result.stdout.strip() or "PASS"
    save(PACK/"TESTS.json",{"status":"PASS_CPU_VALIDATION","checks":test_outputs,
                            "raw_remote_sha_pass":True,"raw_copyback_sha_pass":True,
                            "gpu_additional_execution":False})
    final.update({"mp02_native_samples_completed":0,"mp03_executed":False,"nsys_capture_count":0,
                  "semantic_expected":4608,"semantic_observed":0,"correctness_evaluated":False,
                  "neutrality_evaluated":False,"kernel_inventory_evaluated":False,
                  "historical_mode_c_stop_preserved":True,"automatic_next_goal":False})
    save(PACK/"FINAL_DECISION.json",final)
    (PACK/"README.md").write_text(f"""# Qwen compiled/no-CUDA-Graph Observer V2 canary on node 109

Final decision: `COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL`.

The exact Lane6 contract is commit `eaaa2e66befa872ce7c8f47011e9fe7cdf8921d9`, tree `f2d9d3a46ca3774a82eaeb2175b01a6cdbec9d2f`, contract SHA256 `bf5584db66cf66d076e49d5fbbe9053d9a614c88eccaf514518137ee3812ef68`. `CONTRACT_AUTHORITY.json` validates the authorization, bound sources, frozen gates and budgets. The exact Lane6 runner and Observer V2 files were imported without modification; `SOURCE_INTEGRATION.json` records their hashes.

MP02 failed at the first Observer ON warmup: the semantic receipt contained **0** occurrences against the frozen **4,608**. This is the first identity gate failure. The six native OFF/ON samples were never started, so output correctness, the CUDA-event neutrality median, host cross-check and OFF/ON kernel inventory were not evaluated. MP03 and NSYS were not run. `MP02_IDENTITY_FAILURE_DETAIL.json`, `CORRECTNESS_NEUTRALITY_STATUS.json`, `KERNEL_INVENTORY_STATUS.json` and `NSYS_STRUCTURE.json` state each boundary. The source runner reached and passed its effective Mode B configuration check before the semantic error, but it did not emit a final per-arm compiled-path receipt; no fully qualified ON identity is claimed.

Conservative GPU-active time was {budget['total_gpu_active_seconds_conservative_wall']:.6f} seconds, all in MP02 and under its 75-second and the total 180-second caps. The lock was released and postflight found no compute process. Raw stdout, stderr and runner JSON are at `{raw}` and were published to `{publish['durable_path']}`; per-file SHA and copy-back checks passed. `RAW_INDEX.tsv` and `PUBLISH_RECEIPT.json` provide provenance. `SHA256SUMS` covers this pack.

Historical Mode C MP02/MP03 `STOP_POINT_CORRECTNESS` remains unchanged. No Tier0 rerun, NCU, holdout, MODE_A, MODE_C, mechanism, or automatic next goal was executed.\n""")
    (PACK/"OPEN_ISSUES.md").write_text("# Open issues\n\nThe frozen Observer V2 semantic sequence did not appear under compiled Mode B. This identity failure stops this canary. Any change to the observer or execution identity requires a separate project decision.\n")
    (PREP/"CONTRACT_POLL.tsv").replace(PACK/"CONTRACT_POLL.tsv")
    (PREP/"CONTRACT_AVAILABLE.json").replace(PACK/"CONTRACT_AVAILABLE.json")
    count=manifest(PACK)
    print(json.dumps({"status":"FAIL_CLOSED_AND_PUBLISHED","decision":final["decision"],"pack_files":count}))

if __name__=="__main__":main()
