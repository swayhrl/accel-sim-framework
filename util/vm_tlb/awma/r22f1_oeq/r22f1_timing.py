#!/usr/bin/env python3
"""No-profiler CUDA-event bundled same-input OEQ TP forward/backward replay."""

import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import time
import traceback
from pathlib import Path

import numpy as np

from r22f1_qualify import load_payloads,setup_modules,tensor_inputs,oe_call,first_bad,sha,write_json

ROOT=Path("/data/c16/awma/r22f1_oeq_lowoverhead_replay_20261002")
RAW=ROOT/"raw"
PACK=Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f1-oeq-lowoverhead-replay-109-v1/docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1")
PARENT=Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
LOCK=Path("/data/c16/locks/c16_gpu_campaign.lock")


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()


def do_forward_bundle(torch,mod,arm,item,arrays,perm,count):
    t=tensor_inputs(torch,item,arrays)
    torch.cuda.synchronize()
    start,end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
    wall0=time.perf_counter_ns();start.record()
    output=None
    for _ in range(count): output=oe_call(mod,arm,t,perm)
    end.record();torch.cuda.synchronize()
    wall_ms=(time.perf_counter_ns()-wall0)/1e6
    elapsed_ms=start.elapsed_time(end)
    return {"wall_per_replay_us":wall_ms*1000/count,"event_per_replay_us":elapsed_ms*1000/count,
            "output":output.detach().cpu().numpy().copy()}


def do_backward_bundle(torch,mod,arm,item,arrays,perm,count):
    active=[key for key in ("X","Y","W") if item["requires_grad"][key]]
    pending=[]
    for _ in range(count):
        t=tensor_inputs(torch,item,arrays)
        output=oe_call(mod,arm,t,perm)
        pending.append((output,t))
    torch.cuda.synchronize()
    start,end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
    wall0=time.perf_counter_ns();start.record()
    gradients=None
    for output,t in pending:
        gradients=torch.autograd.grad(output,[t[key] for key in active],grad_outputs=t["upstream_0"],allow_unused=False)
    end.record();torch.cuda.synchronize()
    wall_ms=(time.perf_counter_ns()-wall0)/1e6
    elapsed_ms=start.elapsed_time(end)
    values={f"grad_{key}":grad.detach().cpu().numpy().copy() for key,grad in zip(active,gradients)}
    del pending
    return {"wall_per_replay_us":wall_ms*1000/count,"event_per_replay_us":elapsed_ms*1000/count,
            "outputs":values}


def main():
    status_path=RAW/"REPLAY_TIMING_STATUS.json"
    if status_path.exists(): raise RuntimeError("Formal replay timing already attempted; no repetition")
    qualify=json.loads((RAW/"REPLAY_QUALIFICATION_STATUS.json").read_text())
    freeze=json.loads((PACK/"BACKWARD_MODE_FREEZE.json").read_text())
    if qualify["status"]!="REPLAY_QUALIFIED" or freeze["mode"]!=qualify["backward_bundle_mode"]:
        raise RuntimeError("Same-input correctness/backward mode gate absent")
    if (PACK/"REPLAY_MEASUREMENT_CONTRACT.md").stat().st_mtime >= (RAW/"REPLAY_QUALIFICATION_STATUS.json").stat().st_mtime:
        raise RuntimeError("Replay measurement contract not frozen before timing")
    records=load_payloads()
    with np.load(PARENT/"raw/DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz",allow_pickle=False) as z:
        perm_array=z["edge_transpose_perm"].copy()
    backward_count=32 if freeze["mode"]=="BUNDLE32" else 1
    backward_samples=8 if freeze["mode"]=="BUNDLE32" else 20
    status={"status":"STARTED","capture_sha256":sha(RAW/"TP_CAPTURE_STATUS.json"),
            "qualification_sha256":sha(RAW/"REPLAY_QUALIFICATION_STATUS.json"),
            "backward_mode":freeze["mode"],"forward_bundle":32,"backward_bundle":backward_count,
            "planned_forward_samples":len(records)*2*5*8,
            "planned_backward_samples":len(records)*2*5*backward_samples,
            "rows":[],"first_mismatch":None}
    receipt={"mode":"timing","lock_path":str(LOCK),"pid":os.getpid(),"wait_begin_utc":utc()}
    with LOCK.open("a+") as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        receipt["acquired_utc"]=utc();write_json(RAW/"LOCK_TIMING.json",receipt)
        write_json(status_path,status)
        try:
            os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR",str(ROOT/"cache/inductor"))
            os.environ.setdefault("TRITON_CACHE_DIR",str(ROOT/"cache/triton"))
            os.environ.setdefault("CUDA_CACHE_PATH",str(ROOT/"cache/cuda"))
            import torch
            import openequivariance
            from openequivariance import TensorProductConv
            torch.set_default_dtype(torch.float32)
            torch.backends.cuda.matmul.allow_tf32=False
            torch.backends.cudnn.allow_tf32=False
            torch.set_float32_matmul_precision("highest")
            model,arms=setup_modules(torch,TensorProductConv,records)
            perm=torch.from_numpy(perm_array).to("cuda")
            for phase in ("forward","backward"):
                count=32 if phase=="forward" else backward_count
                formal_per_group=8 if phase=="forward" else backward_samples
                for item,arrays in records:
                    expected={}
                    for arm in ("Aorder","Dready"):
                        with np.load(RAW/f"REPLAY_QUAL_CALL_{item['call_index']:02d}_{arm}.npz",allow_pickle=False) as z:
                            expected[arm]={key:z[key].copy() for key in z.files if (phase=="forward" and key=="output") or (phase=="backward" and key.startswith("grad_"))}
                    for arm in ("Aorder","Dready"):
                        mod=arms[item["call_index"]][arm]
                        for warmup in range(10):
                            result=do_forward_bundle(torch,mod,arm,item,arrays,perm,count) if phase=="forward" else do_backward_bundle(torch,mod,arm,item,arrays,perm,count)
                            values={"output":result["output"]} if phase=="forward" else result["outputs"]
                            mismatch={key:first_bad(expected[arm][key],value) for key,value in values.items()}
                            if any(v is not None for v in mismatch.values()):
                                failure=RAW/f"REPLAY_WARMUP_FAILURE_{phase}_C{item['call_index']}_{arm}_{warmup}.npz"
                                np.savez_compressed(failure,**values)
                                status.update({"status":"WARMUP_NUMERIC_FAILURE","first_mismatch":mismatch,
                                               "failed_output_path":str(failure),"failed_output_sha256":sha(failure)})
                                write_json(status_path,status)
                                raise RuntimeError("Warmup same-input numeric failure")
                    for group in range(5):
                        order=("Aorder","Dready") if group%2==0 else ("Dready","Aorder")
                        for arm in order:
                            mod=arms[item["call_index"]][arm]
                            for sample in range(formal_per_group):
                                result=do_forward_bundle(torch,mod,arm,item,arrays,perm,count) if phase=="forward" else do_backward_bundle(torch,mod,arm,item,arrays,perm,count)
                                values={"output":result["output"]} if phase=="forward" else result["outputs"]
                                output_path=RAW/f"REPLAY_{phase.upper()}_C{item['call_index']}_{arm}_G{group}_S{sample}.npz"
                                np.savez_compressed(output_path,**values)
                                mismatch={key:first_bad(expected[arm][key],value) for key,value in values.items()}
                                row={"phase":phase,"call_index":item["call_index"],"callsite":item["callsite"],
                                     "arm":arm,"group":group,"sample":sample,"order":",".join(order),
                                     "bundle_count":count,"event_per_replay_us":result["event_per_replay_us"],
                                     "wall_per_replay_us":result["wall_per_replay_us"],
                                     "numeric_pass":all(v is None for v in mismatch.values()),
                                     "first_mismatch":mismatch,"output_path":str(output_path),"output_sha256":sha(output_path)}
                                status["rows"].append(row)
                                if not (math.isfinite(row["event_per_replay_us"]) and row["event_per_replay_us"]>0):
                                    status.update({"status":"TIMER_INVALID","failed_row":row})
                                    write_json(status_path,status)
                                    raise RuntimeError("Invalid CUDA event timer")
                                if not row["numeric_pass"]:
                                    status.update({"status":"FORMAL_NUMERIC_FAILURE","first_mismatch":mismatch,"failed_row":row})
                                    write_json(status_path,status)
                                    raise RuntimeError("Formal replay output/gradient mismatch")
                                write_json(status_path,status)
            for phase in ("forward","backward"):
                rows=[r for r in status["rows"] if r["phase"]==phase]
                fields=["phase","call_index","callsite","arm","group","sample","order","bundle_count",
                        "event_per_replay_us","wall_per_replay_us","numeric_pass","output_path","output_sha256"]
                with (RAW/f"{phase.upper()}_TIMING.tsv").open("w",newline="") as stream:
                    writer=csv.DictWriter(stream,fieldnames=fields,delimiter="\t",lineterminator="\n")
                    writer.writeheader();writer.writerows({key:row[key] for key in fields} for row in rows)
            status["status"]="REPLAY_TIMING_COMPLETE"
            write_json(status_path,status)
            receipt["terminal_status"]=status["status"]
            print(json.dumps({"status":status["status"],"forward_samples":len([r for r in status["rows"] if r["phase"]=="forward"]),
                              "backward_samples":len([r for r in status["rows"] if r["phase"]=="backward"]),
                              "backward_mode":freeze["mode"]},sort_keys=True),flush=True)
        except Exception as exc:
            if status["status"]=="STARTED": status["status"]="REPLAY_TIMING_FAILED"
            status.update({"error_type":type(exc).__name__,"error":str(exc),"traceback_tail":traceback.format_exc()[-12000:]})
            write_json(status_path,status)
            receipt.update({"terminal_status":"FAILED","error_type":type(exc).__name__,"error":str(exc)})
            raise
        finally:
            receipt["released_utc"]=utc();write_json(RAW/"LOCK_TIMING.json",receipt)
            fcntl.flock(lock.fileno(),fcntl.LOCK_UN)


if __name__=="__main__": main()
