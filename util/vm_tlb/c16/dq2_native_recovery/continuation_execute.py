#!/usr/bin/env python3
"""One fresh MP03_B process under the pushed continuation PREEXEC contract."""
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

from cache_check import check as check_four
from continuation_cache_lifecycle import EXPECTED_AOT,tree_identity
from execute import acquire_lock,gpu_query
from preexec import verify_current_authority

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_MP03B_CONTINUATION_109_V1"
OLD=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"
RAW_BASE=Path("/data/c16/dq2_native_recovery_v1/continuation_raw")
MODEL=Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1")
VENV=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python")
BRANCH="hrl/c16-dq2-native-recovery-109-v1"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def git(*args):return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def verify_old_raw():
    old_run=json.loads((OLD/"RUN_IDENTITY.json").read_text())
    old_raw=Path(old_run["raw_path"])
    index=json.loads((OLD/"RAW_INDEX.json").read_text())
    by_path={x["local_path"]:x["sha256"] for x in index}
    for name in ("MP02_A.json","MP02_B.json","MP03_A.json"):
        path=old_raw/name
        if sha(path)!=by_path[str(path)]:raise RuntimeError(f"accepted old arm SHA changed: {name}")
    return {"old_raw":str(old_raw),"old_result_commit":"a12bbfa4609ece57fadde107f9fd2e3bc0380cdf",
            "old_arm_sha256":{name:by_path[str(old_raw/name)] for name in ("MP02_A.json","MP02_B.json","MP03_A.json")}}

def main():
    contract=json.loads((PACK/"CONTINUATION_PREEXEC_CONTRACT.json").read_text())
    old_contract=json.loads((OLD/"PREEXEC_CONTRACT.json").read_text())
    verify_current_authority(old_contract)
    if git("rev-parse","HEAD")!=git("rev-parse",f"origin/{BRANCH}") or git("status","--porcelain"):
        raise RuntimeError("continuation PREEXEC not pushed/fetched back or worktree dirty")
    head=git("rev-parse","HEAD")
    if head=="a12bbfa4609ece57fadde107f9fd2e3bc0380cdf":raise RuntimeError("continuation PREEXEC commit missing")
    old=verify_old_raw()
    four_before=check_four("CONTINUATION_BEFORE")
    aot_before=tree_identity(EXPECTED_AOT)
    if four_before["status"]!="PASS" or aot_before["content_identity_sha256"]!=contract["aot_pre_warmup"]["content_sha256"]:
        raise RuntimeError("continuation cache authority changed before GPU")
    run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw=RAW_BASE/run_id;raw.mkdir(parents=True,exist_ok=False)
    save(raw/"CACHE_BEFORE.json",{"four_bound_roots":four_before,"pre_warmup_aot_root":aot_before})
    save(raw/"RUN_IDENTITY.json",{"goal":"C16_DQ2_NATIVE_RECOVERY_109_V1_MP03B_CONTINUATION","run_id":run_id,
         "continuation_preexec_commit":head,"continuation_preexec_tree":git("rev-parse","HEAD^{tree}"),
         "continuation_contract_sha256":sha(PACK/"CONTINUATION_PREEXEC_CONTRACT.json"),
         "old_result_commit":old["old_result_commit"],"old_raw":old["old_raw"],"old_arm_sha256":old["old_arm_sha256"],
         "only_new_arm":"MP03_B","raw_path":str(raw),"started_utc":datetime.now(timezone.utc).isoformat()})
    lock_file=None;lock_receipt={"acquired":False,"released":False}
    history=[];decision="DQ2_EXECUTION_IDENTITY_FAIL";error=None
    try:
        lock_file,wait,baseline=acquire_lock(contract["gpu_budget"]["lock_wait_seconds_cap"])
        lock_receipt.update({"acquired":True,"wait_seconds":wait,"baseline":baseline})
        if baseline["uuid"]!=contract["gpu"]["uuid"]:raise RuntimeError("GPU UUID changed")
        output=raw/"MP03_B.json"
        cmd=[str(VENV),str(HERE/"runner.py"),"--point","MP03","--mode","B","--model",str(MODEL),
             "--expected-cache-path",contract["after_warmup_final"]["path"],
             "--continuation-mp03b","--expected-aot-cache-path",contract["aot_pre_warmup"]["path"],
             "--expected-aot-content-sha",contract["aot_pre_warmup"]["content_sha256"],"--output",str(output)]
        env=os.environ.copy();env.update({"VLLM_ENABLE_V1_MULTIPROCESSING":"0","HF_HUB_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
        start=time.monotonic()
        with (raw/"MP03_B.stdout").open("wb") as out,(raw/"MP03_B.stderr").open("wb") as err:
            process=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,start_new_session=True)
            try:code=process.wait(timeout=contract["gpu_budget"]["arm_seconds_cap"]-3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=2)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                code=-1
        elapsed=time.monotonic()-start
        history.append({"arm":"MP03_B","exit_code":code,"gpu_active_seconds_conservative_wall":elapsed,
                        "cap_seconds":contract["gpu_budget"]["arm_seconds_cap"],"command":cmd})
        if elapsed>contract["gpu_budget"]["arm_seconds_cap"]:raise RuntimeError("continuation arm GPU cap exceeded")
        if code!=0:raise RuntimeError(f"MP03_B runner stopped exit={code}")
        if json.loads(output.read_text())["status"]!="PASS":raise RuntimeError("MP03_B runner receipt failed")
        decision="PENDING_CPU_CORRECTNESS_AND_DURABILITY"
    except Exception as e:
        error=f"{type(e).__name__}: {e}"
        if "DQ2_GPU_RESOURCE_BLOCKED" in str(e):decision="DQ2_GPU_RESOURCE_BLOCKED"
        save(raw/"EXECUTION_ERROR.json",{"error":error,"traceback":traceback.format_exc()})
    finally:
        try:
            four_after=check_four("CONTINUATION_AFTER")
            aot_after=tree_identity(EXPECTED_AOT)
        except Exception as e:
            four_after={"status":"UNREADABLE","error":str(e)};aot_after={"status":"UNREADABLE"}
            if decision=="PENDING_CPU_CORRECTNESS_AND_DURABILITY":decision="DQ2_EXECUTION_IDENTITY_FAIL"
        save(raw/"CACHE_AFTER.json",{"four_bound_roots":four_after,"pre_warmup_aot_root":aot_after})
        if lock_file is not None:
            fcntl.flock(lock_file,fcntl.LOCK_UN);lock_file.close();lock_receipt["released"]=True
        lock_receipt["after"]=gpu_query()
        save(raw/"GPU_USAGE_RECEIPT.json",{"history":history,"total_gpu_active_seconds_conservative_wall":sum(x["gpu_active_seconds_conservative_wall"] for x in history),"lock":lock_receipt})
        runner_receipt=json.loads((raw/"MP03_B.json").read_text()) if (raw/"MP03_B.json").exists() else None
        save(raw/"EXECUTION_STATUS.json",{"decision":decision,"error":error,
             "runner_status":runner_receipt.get("status") if runner_receipt else None,
             "pre_warmup_cache_gate":runner_receipt.get("cache_lifecycle",{}).get("pre_warmup",{}).get("status") if runner_receipt else None,
             "after_warmup_cache_gate":runner_receipt.get("cache_lifecycle",{}).get("after_warmup",{}).get("status") if runner_receipt else None,
             "new_formal_sample_count":len(runner_receipt.get("formal_samples",[])) if runner_receipt else 0,
             "old_three_arms_rerun":False})
    print(json.dumps({"decision":decision,"run_id":run_id,"raw":str(raw),"gpu_active_seconds":sum(x["gpu_active_seconds_conservative_wall"] for x in history)}))

if __name__=="__main__":main()
