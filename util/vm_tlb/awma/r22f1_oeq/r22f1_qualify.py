#!/usr/bin/env python3
"""Reconstruct exact OEQ arms, qualify same-input forward/VJP, freeze backward mode."""

import datetime as dt
import fcntl
import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np

ROOT=Path("/data/c16/awma/r22f1_oeq_lowoverhead_replay_20261002")
RAW=ROOT/"raw"
TENSORS=ROOT/"tensors"
PARENT=Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
PACK=Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f1-oeq-lowoverhead-replay-109-v1/docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1")
LOCK=Path("/data/c16/locks/c16_gpu_campaign.lock")


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(8<<20),b""):
            h.update(block)
    return h.hexdigest()


def write_json(path,value): Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,default=str)+"\n")


def first_bad(ref,observed):
    if ref.shape!=observed.shape: return {"reference_shape":list(ref.shape),"observed_shape":list(observed.shape)}
    mask=~np.isfinite(observed)|~np.isclose(ref,observed,atol=5e-5,rtol=5e-5)
    if not np.any(mask): return None
    idx=tuple(int(i) for i in np.argwhere(mask)[0])
    return {"index":idx,"reference":float(ref[idx]),"observed":str(observed[idx])}


def load_payloads():
    capture=json.loads((RAW/"TP_CAPTURE_STATUS.json").read_text())
    if capture["status"]!="TP_CAPTURE_QUALIFIED" or not capture["records"]:
        raise RuntimeError("Exact real TP capture missing")
    records=[]
    for item in capture["records"]:
        path=Path(item["payload_path"])
        if sha(path)!=item["payload_sha256"]: raise RuntimeError("Capture payload hash drift")
        with np.load(path,allow_pickle=False) as z:
            arrays={k:z[k].copy() for k in z.files}
        for key,array in arrays.items():
            if hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()!=item["tensor_sha256"][key]:
                raise RuntimeError(f"Captured tensor hash drift {item['callsite']} {key}")
        if item["upstream_gradient_observation_count"]!=1 or "upstream_0" not in arrays:
            raise RuntimeError("Exact captured VJP missing")
        records.append((item,arrays))
    return records


def setup_modules(torch,OEQ,records):
    from nequip.model import ModelFromPackage,modify
    package=ModelFromPackage(str(PARENT/"model/NequIP-OAM-S-0.1.nequip.zip"),compile_mode="eager")
    modified=modify(package,modifiers=[{"modifier":"enable_OpenEquivariance"}])
    model=modified["sole_model"].eval()
    for p in model.parameters(): p.requires_grad_(False)
    model=model.to("cuda")
    found={name:mod for name,mod in model.named_modules() if isinstance(mod,OEQ)}
    if set(found)!={item["callsite"] for item,_ in records}:
        raise RuntimeError(f"OEQ callsite set changed {set(found)}")
    arms={}
    for item,_ in records:
        atomic=found[item["callsite"]]
        if int(atomic.hash)!=item["OEQ_JIT_hash"] or hashlib.sha256(atomic.kernel_string.encode()).hexdigest()!=item["OEQ_kernel_string_sha256"]:
            raise RuntimeError(f"Atomic TPProblem/JIT identity drift {item['callsite']}")
        args=dict(atomic.input_args)
        if args["deterministic"] is not False: raise RuntimeError("Atomic baseline changed")
        det=OEQ(args["problem"],deterministic=True,kahan=args.get("kahan",False),
                torch_op=args["torch_op"],use_opaque=args["use_opaque"])
        arms[item["call_index"]]={"Aorder":atomic,"Dready":det}
    return model,arms


def tensor_inputs(torch,item,arrays):
    tensors={}
    for key in ("X","Y","W"):
        tensors[key]=torch.from_numpy(arrays[key].copy()).to("cuda")
        tensors[key].requires_grad_(item["requires_grad"][key])
    for key in ("rows","cols","upstream_0"):
        tensors[key]=torch.from_numpy(arrays[key].copy()).to("cuda")
    return tensors


def oe_call(mod,arm,t,perm):
    args=(t["X"],t["Y"],t["W"],t["rows"],t["cols"])
    return mod(*args,perm) if arm=="Dready" else mod(*args)


def forward_vjp(torch,mod,arm,item,arrays,perm):
    t=tensor_inputs(torch,item,arrays)
    out=oe_call(mod,arm,t,perm)
    active=[key for key in ("X","Y","W") if item["requires_grad"][key]]
    grads=torch.autograd.grad(out,[t[key] for key in active],grad_outputs=t["upstream_0"],allow_unused=False)
    torch.cuda.synchronize()
    return {"output":out.detach().cpu().numpy().copy(),**{f"grad_{key}":grad.detach().cpu().numpy().copy() for key,grad in zip(active,grads)}}


def backward_bundle_canary(torch,mod,arm,item,arrays,perm,expected):
    pending=[]
    active=[key for key in ("X","Y","W") if item["requires_grad"][key]]
    for _ in range(32):
        t=tensor_inputs(torch,item,arrays)
        out=oe_call(mod,arm,t,perm)
        pending.append((out,t))
    torch.cuda.synchronize()
    first=None
    for out,t in pending:
        grads=torch.autograd.grad(out,[t[key] for key in active],grad_outputs=t["upstream_0"],allow_unused=False)
        if first is None: first={f"grad_{key}":grad.detach().cpu().numpy().copy() for key,grad in zip(active,grads)}
    torch.cuda.synchronize()
    return {key:first_bad(expected[key],value) for key,value in first.items()}


def main():
    if (RAW/"REPLAY_QUALIFICATION_STATUS.json").exists():
        raise RuntimeError("Same-input qualification already attempted; preserve first result")
    records=load_payloads()
    with np.load(PARENT/"raw/DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz",allow_pickle=False) as z:
        perm_array=z["edge_transpose_perm"].copy()
        edge_index=z["edge_index"].copy()
    for item,arrays in records:
        if not np.array_equal(arrays["rows"],edge_index[0]) or not np.array_equal(arrays["cols"],edge_index[1]):
            raise RuntimeError(f"Captured exact sorted topology drift: {item['callsite']}")
        if not np.array_equal(np.sort(perm_array),np.arange(len(perm_array))):
            raise RuntimeError("Accepted sender permutation invalid")
    receipt={"mode":"qualify","lock_path":str(LOCK),"pid":os.getpid(),"wait_begin_utc":utc()}
    status={"status":"STARTED","capture_status_sha256":sha(RAW/"TP_CAPTURE_STATUS.json"),
            "record_count":len(records),"first_mismatch":None,"rows":[],"backward_bundle_mode":"NOT_FROZEN"}
    with LOCK.open("a+") as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        receipt["acquired_utc"]=utc();write_json(RAW/"LOCK_QUALIFY.json",receipt)
        write_json(RAW/"REPLAY_QUALIFICATION_STATUS.json",status)
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
            for item,arrays in records:
                results={}
                for arm in ("Aorder","Dready"):
                    mod=arms[item["call_index"]][arm]
                    values=forward_vjp(torch,mod,arm,item,arrays,perm)
                    result_path=RAW/f"REPLAY_QUAL_CALL_{item['call_index']:02d}_{arm}.npz"
                    np.savez_compressed(result_path,**values)
                    results[arm]=values
                    status["rows"].append({"call_index":item["call_index"],"callsite":item["callsite"],
                        "arm":arm,"OEQ_hash":int(mod.hash),"kernel_string_sha256":hashlib.sha256(mod.kernel_string.encode()).hexdigest(),
                        "workspace_size_bytes":int(mod.workspace_size),"input_args":{k:v for k,v in mod.input_args.items() if k!="problem"},
                        "problem_repr_sha256":hashlib.sha256(repr(mod.input_args["problem"]).encode()).hexdigest(),
                        "output_path":str(result_path),"output_sha256":sha(result_path),
                        "tensor_sha256":{key:hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest() for key,value in values.items()}})
                    write_json(RAW/"REPLAY_QUALIFICATION_STATUS.json",status)
                comparison={key:first_bad(results["Aorder"][key],results["Dready"][key]) for key in results["Aorder"]}
                capture_match=first_bad(arrays["forward_output"],results["Aorder"]["output"])
                status["rows"].append({"call_index":item["call_index"],"callsite":item["callsite"],
                                       "comparison":"same_input_Aorder_vs_Dready","first_mismatch":comparison,
                                       "Aorder_vs_real_capture_forward_first_mismatch":capture_match})
                write_json(RAW/"REPLAY_QUALIFICATION_STATUS.json",status)
                if capture_match is not None or any(value is not None for value in comparison.values()):
                    status["first_mismatch"]={"call_index":item["call_index"],"comparison":comparison,"capture_match":capture_match}
                    status["status"]="REPLAY_NUMERICS_NOT_QUALIFIED"
                    write_json(RAW/"REPLAY_QUALIFICATION_STATUS.json",status)
                    raise RuntimeError("Same-input forward/VJP numerical contract failed")
            feasibility=[]
            bundle_clean=True
            for item,arrays in records:
                for arm in ("Aorder","Dready"):
                    mod=arms[item["call_index"]][arm]
                    with np.load(RAW/f"REPLAY_QUAL_CALL_{item['call_index']:02d}_{arm}.npz",allow_pickle=False) as z:
                        expected={key:z[key].copy() for key in z.files if key.startswith("grad_")}
                    try:
                        mismatches=backward_bundle_canary(torch,mod,arm,item,arrays,perm,expected)
                        good=all(value is None for value in mismatches.values())
                        feasibility.append({"call_index":item["call_index"],"arm":arm,"clean":good,"first_mismatch":mismatches})
                        bundle_clean &= good
                    except Exception as exc:
                        feasibility.append({"call_index":item["call_index"],"arm":arm,"clean":False,
                                            "error_type":type(exc).__name__,"error":str(exc)})
                        bundle_clean=False
                        torch.cuda.empty_cache()
            status["backward_bundle_feasibility"]=feasibility
            status["backward_bundle_mode"]="BUNDLE32" if bundle_clean else "SINGLE20"
            status["status"]="REPLAY_QUALIFIED"
            write_json(RAW/"REPLAY_QUALIFICATION_STATUS.json",status)
            write_json(PACK/"BACKWARD_MODE_FREEZE.json",{"mode":status["backward_bundle_mode"],
                "selected_before_any_timing":True,"capture_status_sha256":status["capture_status_sha256"],
                "feasibility":feasibility})
            receipt["terminal_status"]=status["status"]
            print(json.dumps({"status":status["status"],"calls":len(records),"backward_mode":status["backward_bundle_mode"]},sort_keys=True),flush=True)
        except Exception as exc:
            if status["status"]=="STARTED": status["status"]="REPLAY_QUALIFICATION_FAILED"
            status.update({"error_type":type(exc).__name__,"error":str(exc),"traceback_tail":traceback.format_exc()[-12000:]})
            write_json(RAW/"REPLAY_QUALIFICATION_STATUS.json",status)
            receipt.update({"terminal_status":"FAILED","error_type":type(exc).__name__,"error":str(exc)})
            raise
        finally:
            receipt["released_utc"]=utc();write_json(RAW/"LOCK_QUALIFY.json",receipt)
            fcntl.flock(lock.fileno(),fcntl.LOCK_UN)


if __name__=="__main__": main()
