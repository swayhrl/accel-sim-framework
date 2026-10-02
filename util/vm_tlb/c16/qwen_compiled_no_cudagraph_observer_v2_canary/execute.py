#!/usr/bin/env python3
"""Exact-contract, fail-closed MP02 then conditional MP03 GPU campaign."""
import hashlib
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime,timezone
from pathlib import Path

from analyze_exact import analyze
from contract_admission import admit
from nsys_structural import check as check_nsys
from publish import publish
from run_guard import GpuGuard, MAX_POINT, MAX_TOTAL, LOCK, gpu_query

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
EXACT=ROOT/"util/vm_tlb/c16/qwen_compiled_no_cudagraph_observer_v2"
PACK=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1"
PREP=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_PREP_109_V1"
RAW_BASE=Path("/data/c16/qwen_compiled_no_cudagraph_observer_v2_canary_v1/raw")
MODEL=Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1")
EXPECTED=Path("/data/c16/qwen_compiled_no_cudagraph_observer_v2_canary_v1/contract_gate/EXPECTED_SEMANTIC_SEQUENCE.tsv")
PYTHON=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python")
VLLM_REPO=Path("/data/c16/runtime_environment_audit_v1/source/vllm-v0.30.0")
SOURCE_SHA={"runner.py":"aeba460a688dd2c2d250d13a34f0df8fe797043fd4100b2e4de27f51df41d239",
            "observer_v2.py":"1f94f3997b21aa38b171adb7c2159ef26100b705a714994c11ca207cb9c2caeb"}

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")

def cpu_entry():
    contract=admit()
    prep=json.loads((PREP/"ASSET_INPUT_PREP.json").read_text())
    if prep["status"]!="PASS":raise RuntimeError("ASSET_INPUT_PREP_FAILED")
    if sha(EXPECTED)!="f07ad87e7c018fbcb2c8b2950b41c343edaa8df07922557cc977ef754ea748c7":
        raise RuntimeError("EXPECTED_SEMANTIC_SEQUENCE_SHA_MISMATCH")
    for name,digest in SOURCE_SHA.items():
        if sha(EXACT/name)!=digest:raise RuntimeError(f"EXACT_SOURCE_SHA_MISMATCH_{name}")
    subprocess.run(["python3",str(EXACT/"validate_static.py"),"--vllm-repo",str(VLLM_REPO),"--model-config",str(MODEL/"config.json")],check=True,capture_output=True,text=True)
    return contract

def source_command(point,arm,remaining,output,qualification=None):
    cmd=[str(PYTHON),str(EXACT/"runner.py"),"--point",point,"--arm",arm,
         "--model",str(MODEL),"--expected-sequence",str(EXPECTED),
         "--remaining-point-seconds",f"{remaining:.6f}","--output",str(output)]
    if qualification is not None:cmd.extend(["--qualification-receipt",str(qualification)])
    return cmd

def remaining(guard,point):
    return min(MAX_POINT[point]-guard.by_point[point],MAX_TOTAL-guard.total)

def env():
    result=os.environ.copy()
    result.update({"VLLM_ENABLE_V1_MULTIPROCESSING":"0","HF_HUB_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    return result

def run_point(guard,point,raw):
    native=raw/f"{point}_NATIVE.json"
    qual=PACK/f"{point}_NATIVE_QUALIFICATION.json"
    command=source_command(point,"NATIVE",remaining(guard,point),native)
    process_error=None
    try:
        guard.run(point,"NATIVE",command,raw/f"{point}_NATIVE.stdout",raw/f"{point}_NATIVE.stderr",env())
    except Exception as e:
        process_error=str(e)
        if not native.exists():
            return {"point":point,"status":"FAIL","decision":"CANARY_ENGINEERING_STOP","error":str(e),"native_raw_exists":False}
    result=analyze(json.loads(native.read_text()),EXPECTED)
    if process_error is not None and result["status"]=="NATIVE_NEUTRALITY_PASS":
        result={"point":point,"status":"FAIL","decision":"CANARY_ENGINEERING_STOP",
                "error":process_error,"native_receipt_status":"PASS_BUT_PROCESS_OR_BUDGET_FAILED"}
    save(qual,result)
    if result["status"]!="NATIVE_NEUTRALITY_PASS":return result
    structural=raw/f"{point}_STRUCTURAL.json"
    ns_prefix=raw/f"{point}_STRUCTURAL"
    command=source_command(point,"STRUCTURAL",remaining(guard,point),structural,qual)
    ns_cmd=["nsys","profile","--trace=cuda,nvtx","--sample=none","--cpuctxsw=none",
            "--output",str(ns_prefix),*command]
    try:
        guard.run(point,"NSYS_STRUCTURE",ns_cmd,raw/f"{point}_NSYS.stdout",raw/f"{point}_NSYS.stderr",env())
    except Exception as e:
        return {"point":point,"status":"FAIL","decision":"CANARY_ENGINEERING_STOP","error":str(e),"native":result}
    report=Path(str(ns_prefix)+".nsys-rep")
    if not report.exists():
        return {"point":point,"status":"FAIL","decision":"CANARY_ENGINEERING_STOP","error":"NSYS_REPORT_MISSING","native":result}
    sqlite=Path(str(ns_prefix)+".sqlite")
    try:
        with (raw/f"{point}_NSYS_EXPORT.stdout").open("wb") as out,(raw/f"{point}_NSYS_EXPORT.stderr").open("wb") as err:
            subprocess.run(["nsys","export","--type=sqlite","--output",str(sqlite),str(report)],check=True,stdout=out,stderr=err)
        structure=check_nsys(sqlite,point,structural,EXPECTED)
    except Exception as e:
        return {"point":point,"status":"FAIL","decision":"CANARY_ENGINEERING_STOP","error":f"NSYS_STRUCTURAL_POSTPROCESS:{e}","native":result}
    save(PACK/f"{point}_NSYS_STRUCTURE.json",structure)
    if structure["status"]!="PASS":
        return {"point":point,"status":"FAIL","decision":"COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL","native":result,"nsys_structure":structure}
    return {"point":point,"status":"PASS","decision":"POINT_QUALIFIED","native":result,"nsys_structure":structure}

def main():
    PACK.mkdir(parents=True,exist_ok=True)
    cpu_entry()
    run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw=RAW_BASE/run_id
    raw.mkdir(parents=True,exist_ok=False)
    points=[]
    decision="CANARY_ENGINEERING_STOP"
    lock_receipt={"lock":str(LOCK),"acquired":False,"released":False}
    budget={"total_gpu_active_seconds_conservative_wall":0.0,"by_point_seconds":{"MP02":0.0,"MP03":0.0},
            "total_cap_seconds":180,"point_caps_seconds":MAX_POINT,"history":[],"duration_role":"OBSERVER_QUALIFICATION_ONLY_NOT_STAGEA_SCIENCE"}
    error=None
    try:
        with GpuGuard() as guard:
            lock_receipt.update({"acquired":True,"gpu_baseline":guard.baseline})
            try:
                for point in ("MP02","MP03"):
                    point_result=run_point(guard,point,raw)
                    points.append(point_result)
                    if point_result["status"]!="PASS":
                        decision=point_result["decision"]
                        break
                else:
                    decision="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_PASS"
            finally:
                budget.update({"total_gpu_active_seconds_conservative_wall":guard.total,
                               "by_point_seconds":guard.by_point,"history":guard.history,
                               "within_all_caps":guard.total<=MAX_TOTAL and all(guard.by_point[p]<=MAX_POINT[p] for p in MAX_POINT)})
        lock_receipt["released"]=True
        lock_receipt["gpu_after"]=gpu_query()
    except Exception as e:
        error=f"{type(e).__name__}: {e}"
        lock_receipt["released"]=True
        save(raw/"ORCHESTRATOR_ERROR.json",{"error":error,"traceback":traceback.format_exc()})
    save(PACK/"GPU_LOCK_RECEIPT.json",lock_receipt)
    save(PACK/"GPU_ACTIVE_BUDGET.json",budget)
    save(PACK/"FINAL_DECISION.json",{"goal":"C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1",
         "decision":decision,"points":points,"error":error,"automatic_next_goal":False,
         "tier0_ncu_holdout_executed":False,"raw_local":str(raw),
         "gpu_active_seconds":budget["total_gpu_active_seconds_conservative_wall"]})
    try:
        publish(raw,PACK)
    except Exception as e:
        save(PACK/"PUBLISH_ERROR.json",{"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()})
        decision="CANARY_ENGINEERING_STOP"
        final=json.loads((PACK/"FINAL_DECISION.json").read_text())
        final["decision"]=decision
        final["publish_failed"]=True
        save(PACK/"FINAL_DECISION.json",final)
    print(json.dumps({"decision":decision,"raw":str(raw),"gpu_active_seconds":budget["total_gpu_active_seconds_conservative_wall"]}))

if __name__=="__main__":
    if sys.argv[1:]==["--cpu-entry-only"]:
        contract=cpu_entry()
        print(json.dumps({"status":"CPU_ENTRY_PASS","goal":contract["goal"],"cuda_initialized":False}))
    else:
        main()
