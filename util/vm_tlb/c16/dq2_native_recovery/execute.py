#!/usr/bin/env python3
"""Bounded four-arm DQ2 native execution after exact PREEXEC push/fetch-back."""
import csv
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import time
import traceback
from datetime import datetime,timezone
from pathlib import Path

from analysis import validate_point
from cache_check import check as check_cache
from preexec import verify_current_authority

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"
RAW_BASE=Path("/data/c16/dq2_native_recovery_v1/raw")
VENV=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python")
MODEL=Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1")
LOCK=Path("/data/c16/locks/c16_gpu_campaign.lock")
BRANCH="hrl/c16-dq2-native-recovery-109-v1"
ORDER=(("MP02","A"),("MP02","B"),("MP03","A"),("MP03","B"))

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def git(*args):return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def gpu_query():
    row=subprocess.check_output(["nvidia-smi","--query-gpu=uuid,name,memory.used,driver_version","--format=csv,noheader,nounits"],text=True).strip().split(",")
    apps=subprocess.check_output(["nvidia-smi","--query-compute-apps=pid,process_name,used_gpu_memory","--format=csv,noheader,nounits"],text=True).strip()
    return {"uuid":row[0].strip(),"name":row[1].strip(),"memory_used_mib":int(row[2].strip()),
            "driver_version":row[3].strip(),"compute_processes":apps.splitlines() if apps else []}

def acquire_lock(cap_seconds):
    f=LOCK.open("a+");start=time.monotonic()
    while time.monotonic()-start<cap_seconds:
        try:
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            q=gpu_query()
            if q["compute_processes"]:
                fcntl.flock(f,fcntl.LOCK_UN)
            else:
                return f,time.monotonic()-start,q
        except BlockingIOError:pass
        time.sleep(10)
    f.close();raise RuntimeError("DQ2_GPU_RESOURCE_BLOCKED")

def run_arm(point,mode,contract,raw,history):
    cap=contract["gpu_budget"]["per_arm_seconds_cap"]
    root=contract["cache_authority"][f"{point}_{mode}"]["path"]
    output=raw/f"{point}_{mode}.json"
    cmd=[str(VENV),str(HERE/"runner.py"),"--point",point,"--mode",mode,"--model",str(MODEL),
         "--expected-cache-path",root,"--output",str(output)]
    env=os.environ.copy();env.update({"VLLM_ENABLE_V1_MULTIPROCESSING":"0","HF_HUB_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    start=time.monotonic()
    with (raw/f"{point}_{mode}.stdout").open("wb") as out,(raw/f"{point}_{mode}.stderr").open("wb") as err:
        process=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,start_new_session=True)
        try:
            code=process.wait(timeout=cap-3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL);process.wait()
            code=-1
    elapsed=time.monotonic()-start
    history.append({"point":point,"mode":mode,"command":cmd,"exit_code":code,
                    "gpu_active_seconds_conservative_wall":elapsed,"cap_seconds":cap})
    if elapsed>cap:raise RuntimeError(f"arm GPU budget exceeded {point}_{mode}")
    if code!=0:raise RuntimeError(f"arm process failed {point}_{mode} exit={code}")
    if not output.exists() or json.loads(output.read_text()).get("status")!="PASS":
        raise RuntimeError(f"arm receipt failed {point}_{mode}")

def main():
    contract=json.loads((PACK/"PREEXEC_CONTRACT.json").read_text())
    verify_current_authority(contract)
    if git("rev-parse","HEAD")!=git("rev-parse",f"origin/{BRANCH}") or git("status","--porcelain"):
        raise RuntimeError("PREEXEC not pushed/fetched back or worktree dirty")
    head=git("rev-parse","HEAD");tree=git("rev-parse","HEAD^{tree}")
    if head==contract["base_commit"]:raise RuntimeError("PREEXEC commit missing")
    run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw=RAW_BASE/run_id;raw.mkdir(parents=True,exist_ok=False)
    before=check_cache("BEFORE")
    save(raw/"CACHE_IDENTITY_BEFORE.json",before)
    if before["status"]!="PASS":raise RuntimeError("accepted compile cache changed before GPU")
    identity={"run_id":run_id,"goal":"C16_DQ2_NATIVE_RECOVERY_109_V1","branch":BRANCH,
              "preexec_commit":head,"preexec_tree":tree,"contract_sha256":sha(PACK/"PREEXEC_CONTRACT.json"),
              "mode_order":[f"{p}_{m}" for p,m in ORDER],"model_path":str(MODEL),
              "runtime_environment":str(VENV.parent.parent),"raw_path":str(raw),"started_utc":datetime.now(timezone.utc).isoformat()}
    save(raw/"RUN_IDENTITY.json",identity)
    history=[];point_results=[];decision="DQ2_NATIVE_RECOVERY_PARTIAL";error=None
    lock_receipt={"path":str(LOCK),"acquired":False,"released":False}
    lock_file=None
    try:
        lock_file,wait_seconds,baseline=acquire_lock(contract["gpu_budget"]["lock_wait_seconds_cap"])
        lock_receipt.update({"acquired":True,"wait_seconds":wait_seconds,"baseline":baseline})
        if baseline["uuid"]!=contract["gpu"]["uuid"] or baseline["memory_used_mib"]>256:
            raise RuntimeError("GPU UUID or memory baseline mismatch")
        for point in ("MP02","MP03"):
            for mode in ("A","B"):
                run_arm(point,mode,contract,raw,history)
                if sum(x["gpu_active_seconds_conservative_wall"] for x in history)>contract["gpu_budget"]["total_seconds_cap"]:
                    raise RuntimeError("goal GPU-active cap exceeded")
            result=validate_point(point,raw,contract)
            point_results.append(result)
            save(raw/f"{point}_CORRECTNESS_IDENTITY.json",result)
            if not result["identity_pass"]:
                decision="DQ2_EXECUTION_IDENTITY_FAIL";break
            if not result["correctness_pass"]:
                decision="DQ2_CORRECTNESS_FAIL";break
        else:decision="DQ2_NATIVE_RECOVERY_COMPLETE"
    except Exception as e:
        error=f"{type(e).__name__}: {e}"
        if "DQ2_GPU_RESOURCE_BLOCKED" in str(e):decision="DQ2_GPU_RESOURCE_BLOCKED"
        elif "identity" in str(e).lower() or "compile" in str(e).lower() or "graph" in str(e).lower():decision="DQ2_EXECUTION_IDENTITY_FAIL"
        else:decision="DQ2_NATIVE_RECOVERY_PARTIAL"
        save(raw/"EXECUTION_ERROR.json",{"error":error,"traceback":traceback.format_exc()})
    finally:
        try:
            after=check_cache("AFTER")
        except Exception as cache_error:
            after={"phase":"AFTER","status":"UNREADABLE","error":f"{type(cache_error).__name__}: {cache_error}"}
            if decision=="DQ2_NATIVE_RECOVERY_COMPLETE":decision="DQ2_EXECUTION_IDENTITY_FAIL"
        save(raw/"CACHE_IDENTITY_AFTER.json",after)
        if lock_file is not None:
            fcntl.flock(lock_file,fcntl.LOCK_UN);lock_file.close();lock_receipt["released"]=True
        lock_receipt["after"]=gpu_query()
        save(raw/"GPU_USAGE_RECEIPT.json",{"history":history,"total_gpu_active_seconds_conservative_wall":sum(x["gpu_active_seconds_conservative_wall"] for x in history),
            "total_cap_seconds":contract["gpu_budget"]["total_seconds_cap"],"lock":lock_receipt})
        if after["status"]!="PASS" and decision=="DQ2_NATIVE_RECOVERY_COMPLETE":decision="DQ2_EXECUTION_IDENTITY_FAIL"
        save(raw/"EXECUTION_STATUS.json",{"decision":decision,"error":error,
             "completed_arms":[f"{x['point']}_{x['mode']}" for x in history if x["exit_code"]==0],
             "point_results":[{"point":r["point"],"identity_pass":r["identity_pass"],"correctness_pass":r["correctness_pass"]} for r in point_results],
             "cache_before_status":before["status"],"cache_after_status":after["status"]})
    print(json.dumps({"decision":decision,"run_id":run_id,"raw":str(raw),"completed_arms":len(history)}))

if __name__=="__main__":main()
