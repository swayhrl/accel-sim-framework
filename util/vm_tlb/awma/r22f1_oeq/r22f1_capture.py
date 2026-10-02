#!/usr/bin/env python3
"""One non-timed real OAM-S energy/force run capturing all OEQ TP call inputs and VJPs."""

import datetime as dt
import fcntl
import hashlib
import json
import os
import subprocess
import traceback
from pathlib import Path

import numpy as np

ROOT = Path("/data/c16/awma/r22f1_oeq_lowoverhead_replay_20261002")
RAW = ROOT / "raw"
TENSORS = ROOT / "tensors"
PARENT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
MODEL = PARENT / "model/NequIP-OAM-S-0.1.nequip.zip"
GRAPH = PARENT / "raw/DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz"
LOCK = Path("/data/c16/locks/c16_gpu_campaign.lock")


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(8<<20),b""):
            h.update(block)
    return h.hexdigest()


def tensor_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def write_json(path,value):
    Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,default=str)+"\n")


def first_bad(ref,observed):
    if ref.shape!=observed.shape:
        return {"reference_shape":list(ref.shape),"observed_shape":list(observed.shape)}
    mask=~np.isfinite(observed) | ~np.isclose(ref,observed,atol=5e-5,rtol=5e-5)
    if not np.any(mask): return None
    idx=tuple(int(v) for v in np.argwhere(mask)[0])
    return {"index":idx,"reference":float(ref[idx]),"observed":str(observed[idx])}


def check_authority():
    if sha(MODEL)!="63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa":
        raise RuntimeError("Model package SHA drift")
    if sha(GRAPH)!="f1e0eb6bafa2d8e528e58bc3296e2d808907862b8e6425808112cbc54ae00104":
        raise RuntimeError("Accepted sorted graph SHA drift")
    commits={"nequip":"27d9d2182da918ab7be0017d8300e53278f5e00e",
             "OpenEquivariance":"dc9979099c65113adcc016977c5c60974f9ddafb"}
    for repo,expected in commits.items():
        actual=subprocess.check_output(["git","-C",str(PARENT/"source"/repo),"rev-parse","HEAD"],text=True).strip()
        if actual!=expected: raise RuntimeError(f"Source drift: {repo}")


def main():
    check_authority()
    RAW.mkdir(parents=True,exist_ok=True)
    TENSORS.mkdir(parents=True,exist_ok=True)
    status_path=RAW/"TP_CAPTURE_STATUS.json"
    if status_path.exists():
        raise RuntimeError("Exact TP capture already attempted; preserve first result")
    lock_path=RAW/"LOCK_CAPTURE.json"
    receipt={"stage":"AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1","mode":"capture",
             "lock_path":str(LOCK),"pid":os.getpid(),"wait_begin_utc":utc()}
    with LOCK.open("a+") as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        receipt["acquired_utc"]=utc();write_json(lock_path,receipt)
        status={"status":"STARTED","model_sha256":sha(MODEL),"sorted_graph_sha256":sha(GRAPH),
                "capture_source":"official packaged OAM-S eager plus enable_OpenEquivariance atomic modifier; sorted accepted graph",
                "first_mismatch":None,"records":[]}
        write_json(status_path,status)
        try:
            os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR",str(ROOT/"cache/inductor"))
            os.environ.setdefault("TRITON_CACHE_DIR",str(ROOT/"cache/triton"))
            os.environ.setdefault("CUDA_CACHE_PATH",str(ROOT/"cache/cuda"))
            import torch
            import openequivariance
            from openequivariance import TensorProductConv
            from nequip.data import AtomicDataDict
            from nequip.model import ModelFromPackage, modify
            torch.set_default_dtype(torch.float32)
            torch.backends.cuda.matmul.allow_tf32=False
            torch.backends.cudnn.allow_tf32=False
            torch.set_float32_matmul_precision("highest")
            with np.load(GRAPH,allow_pickle=False) as graph_npz:
                input_cpu={k:torch.from_numpy(graph_npz[k].copy()) for k in graph_npz.files if k!=AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY}
            refs=[]
            for i in range(5):
                with np.load(PARENT/f"raw/REFERENCE_DATA_RUN_{i}.npz",allow_pickle=False) as z:
                    refs.append((z["energy"].copy(),z["forces"].copy()))
            ref_e=np.mean(np.stack([x[0] for x in refs]),axis=0)
            ref_f=np.mean(np.stack([x[1] for x in refs]),axis=0)
            package=ModelFromPackage(str(MODEL),compile_mode="eager")
            modified=modify(package,modifiers=[{"modifier":"enable_OpenEquivariance"}])
            model=modified["sole_model"].eval()
            for p in model.parameters(): p.requires_grad_(False)
            model=model.to("cuda")
            modules=[(name,module) for name,module in model.named_modules() if isinstance(module,TensorProductConv)]
            status["registered_TP_modules"]=[name for name,_ in modules]
            if not modules:
                raise RuntimeError("No real OEQ TensorProductConv callsites")
            capture=[]
            handles=[]
            def make_hook(callsite):
                def hook(module,inputs,output):
                    if len(inputs)<5 or not isinstance(output,torch.Tensor):
                        raise RuntimeError(f"Unexpected TP call signature {callsite}")
                    X,Y,W,rows,cols=inputs[:5]
                    record={"call_index":len(capture),"callsite":callsite,"module":module,
                            "inputs":{"X":X.detach().clone(),"Y":Y.detach().clone(),"W":W.detach().clone(),
                                      "rows":rows.detach().clone(),"cols":cols.detach().clone()},
                            "requires_grad":{"X":bool(X.requires_grad),"Y":bool(Y.requires_grad),"W":bool(W.requires_grad)},
                            "forward_output":output.detach().clone(),"upstream_list":[]}
                    capture.append(record)
                    if not output.requires_grad:
                        raise RuntimeError(f"TP output missing force-path autograd {callsite}")
                    def grad_hook(grad):
                        record["upstream_list"].append(grad.detach().clone())
                        return grad
                    output.register_hook(grad_hook)
                return hook
            for name,module in modules:
                handles.append(module.register_forward_hook(make_hook(name)))
            data=AtomicDataDict.to_(input_cpu,device=torch.device("cuda"))
            output=model(data)
            torch.cuda.synchronize()
            for handle in handles: handle.remove()
            energy=output[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
            forces=output[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
            model_out=RAW/"CAPTURE_MODEL_ENERGY_FORCES.npz"
            np.savez_compressed(model_out,energy=energy,forces=forces)
            bad_e,bad_f=first_bad(ref_e,energy),first_bad(ref_f,forces)
            status.update({"full_model_output_path":str(model_out),"full_model_output_sha256":sha(model_out),
                           "full_model_energy_first_mismatch":bad_e,"full_model_forces_first_mismatch":bad_f,
                           "observed_call_count":len(capture),"first_mismatch":bad_e or bad_f})
            write_json(status_path,status)
            if bad_e or bad_f: raise RuntimeError("Real OAM-S capture run failed original energy/force contract")
            if len(capture)==0: raise RuntimeError("No TP runtime calls")
            for record in capture:
                mod=record["module"]
                cfg=json.loads(mod.kernel_string)
                arrays={k:t.detach().cpu().numpy().copy() for k,t in record["inputs"].items()}
                for grad_index,grad in enumerate(record["upstream_list"]):
                    arrays[f"upstream_{grad_index}"]=grad.detach().cpu().numpy().copy()
                arrays["forward_output"]=record["forward_output"].detach().cpu().numpy().copy()
                path=TENSORS/f"TP_CALL_{record['call_index']:02d}.npz"
                np.savez_compressed(path,**arrays)
                identity={"call_index":record["call_index"],"callsite":record["callsite"],
                          "OEQ_JIT_hash":int(mod.hash),"OEQ_kernel_string_sha256":hashlib.sha256(mod.kernel_string.encode()).hexdigest(),
                          "OEQ_problem_repr":repr(mod.input_args["problem"]),
                          "OEQ_problem_type":type(mod.input_args["problem"]).__name__,
                          "deterministic":bool(mod.input_args["deterministic"]),
                          "kahan":bool(mod.input_args["kahan"]),"torch_op":bool(mod.input_args["torch_op"]),
                          "workspace_size_bytes":int(mod.workspace_size),
                          "forward_config":cfg["forward_config"],"backward_config":cfg["backward_config"],
                          "kernel_prop":cfg["kernel_prop"],"requires_grad":record["requires_grad"],
                          "tensor_shapes":{k:list(v.shape) for k,v in arrays.items()},
                          "tensor_dtypes":{k:str(v.dtype) for k,v in arrays.items()},
                          "tensor_sha256":{k:tensor_sha(v) for k,v in arrays.items()},
                          "payload_path":str(path),"payload_sha256":sha(path),
                          "upstream_gradient_observation_count":len(record["upstream_list"])}
                status["records"].append(identity)
                write_json(status_path,status)
            if any(len(record["upstream_list"])!=1 for record in capture):
                raise RuntimeError("Exact one real force-path upstream gradient per call not closed; all captured inputs and observed gradients persisted")
            status["status"]="TP_CAPTURE_QUALIFIED"
            write_json(status_path,status)
            receipt["terminal_status"]=status["status"]
            print(json.dumps({"status":status["status"],"calls":len(capture),
                              "callsites":[x["callsite"] for x in status["records"]]},sort_keys=True),flush=True)
        except Exception as exc:
            status.update({"status":"TP_CAPTURE_FAILED","error_type":type(exc).__name__,"error":str(exc),
                           "traceback_tail":traceback.format_exc()[-12000:]})
            write_json(status_path,status)
            receipt.update({"terminal_status":"FAILED","error_type":type(exc).__name__,"error":str(exc)})
            raise
        finally:
            receipt["released_utc"]=utc();write_json(lock_path,receipt)
            fcntl.flock(lock.fileno(),fcntl.LOCK_UN)


if __name__=="__main__": main()
