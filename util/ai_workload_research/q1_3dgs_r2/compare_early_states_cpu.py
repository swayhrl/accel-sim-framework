"""Independent metadata/token/raw-byte state comparison; CPU only, no Torch."""
import os
os.sched_setaffinity(0,{22,23})
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import resource
import numpy as np
from checkpoint_inspection import MetadataOnly,TensorToken,NumpyValueToken,NumpyDtypeToken,summary,sha,member


def load(path):
    mfpath=member(path,"MANIFEST.json")
    mf=json.loads(mfpath.read_text())
    assert mf["complete"] and mf["schema"]=="AIARCH_Q1_CHUNKED_STATE_V1"
    meta=member(path,"bundle.pkl")
    assert meta.stat().st_size==mf["metadata_bytes"]
    assert sha(meta)==mf["metadata_sha256"]
    total=0
    for storage in mf["storages"]:
        offset=0
        for chunk in storage["chunks"]:
            f=member(path,chunk["name"])
            assert chunk["offset"]==offset and f.stat().st_size==chunk["nbytes"]
            assert sha(f)==chunk["sha256"]
            offset+=chunk["nbytes"]
        assert offset==storage["nbytes"];total+=offset
    assert total==mf["total_storage_bytes"]
    bundle=MetadataOnly(meta.read_bytes(),mf).load()
    return dict(path=path,manifest=mf,bundle=bundle,
                manifest_sha256=sha(mfpath))


def flatten(bundle):
    scalars={};tensors={};aliases={};containers={}
    def visit(value,path):
        if isinstance(value,TensorToken):
            tensors[path]=value
            aliases.setdefault(("storage",value.row["storage"]),[]).append(path)
            aliases.setdefault(("tensor",value.index),[]).append(path)
        elif isinstance(value,(NumpyValueToken,NumpyDtypeToken)):
            scalars[path]=summary(value)
        elif isinstance(value,(dict,list)):
            key=("container",id(value))
            aliases.setdefault(key,[]).append(path)
            if id(value) in containers:
                return
            containers[id(value)]=path
            scalars[path+"#type"]=type(value).__name__
            if isinstance(value,dict):
                for k,v in value.items():
                    if isinstance(k,TensorToken):
                        key_name="tensor-key:"+str(k.index)
                    else:key_name=str(k)
                    visit(v,path+"/"+key_name)
            else:
                for i,v in enumerate(value):visit(v,path+"/"+str(i))
        elif isinstance(value,tuple):
            scalars[path+"#type"]="tuple"
            for i,v in enumerate(value):visit(v,path+"/"+str(i))
        elif isinstance(value,(bytes,bytearray)):
            scalars[path]={"bytes":len(value),"sha256":hashlib.sha256(value).hexdigest()}
        elif isinstance(value,float):
            scalars[path]={"python_float_hex":value.hex()}
        else:scalars[path]=value
    visit(bundle,"")
    groups={kind:sorted(sorted(paths) for (k,_),paths in aliases.items()
                       if k==kind and len(paths)>1)
            for kind in ["container","tensor","storage"]}
    return scalars,tensors,groups


def parts(state,token):
    row=token.row;storage=state["manifest"]["storages"][row["storage"]]
    for chunk in storage["chunks"]:
        with member(state["path"],chunk["name"]).open("rb") as stream:
            while True:
                data=stream.read(4*1024**2)
                if not data:break
                yield data


def compare_tensor(left,right,lt,rt):
    lrow,rrow=lt.row,rt.row
    layout_keys=["dtype","shape","stride","offset","requires_grad","parameter",
                 "device","pinned","attached_grad_requires_explicit_bundle_field"]
    layout={k:[lrow.get(k),rrow.get(k)] for k in layout_keys
            if lrow.get(k)!=rrow.get(k)}
    ls=left["manifest"]["storages"][lrow["storage"]]
    rs=right["manifest"]["storages"][rrow["storage"]]
    result={"layout_equal":not layout,"layout_differences":layout,
            "left_storage_bytes":ls["nbytes"],"right_storage_bytes":rs["nbytes"]}
    if layout or ls["nbytes"]!=rs["nbytes"]:
        result["bytes_equal"]=False;result["float_error"]="NOT_COMPARED_LAYOUT_MISMATCH"
        return result
    # Full storage hashes include alias backing bytes. Numerical error is only
    # assigned to actual tensors whose metadata proves complete dense coverage.
    dtype={"torch.float16":"<f2","torch.float32":"<f4","torch.float64":"<f8"}.get(lrow["dtype"])
    n=1
    for extent in lrow["shape"]:n*=extent
    expected=1;dense=True
    for stride,extent in sorted((s,n) for s,n in zip(lrow["stride"],lrow["shape"]) if n>1):
        if stride!=expected:dense=False
        expected*=extent
    full=dtype is not None and lrow["offset"]==0 and dense and n*np.dtype(dtype).itemsize==ls["nbytes"]
    equal=True;different_bytes=0;maxabs=0.;sumabs=0.;differing_values=0;values=0
    for lb,rb in zip(parts(left,lt),parts(right,rt)):
        assert len(lb)==len(rb)
        if lb!=rb:
            equal=False
            differing=np.frombuffer(lb,dtype=np.uint8)!=np.frombuffer(rb,dtype=np.uint8)
            different_bytes+=int(np.count_nonzero(differing))
        if full:
            la=np.frombuffer(lb,dtype=dtype).astype(np.float64)
            ra=np.frombuffer(rb,dtype=dtype).astype(np.float64)
            assert np.isfinite(la).all() and np.isfinite(ra).all()
            delta=np.abs(la-ra)
            if delta.size:maxabs=max(maxabs,float(delta.max()))
            sumabs+=float(delta.sum());differing_values+=int(np.count_nonzero(la!=ra));values+=la.size
    result.update(bytes_equal=equal,different_raw_storage_bytes=different_bytes,
                  comparison_scope="EXACT_RAW_STORAGE_BITS")
    if full:
        result["float_error"]={"scope":"EXACT_DENSE_FULL_STORAGE_VIEW",
            "values":values,"different_numeric_values":differing_values,
            "max_abs":maxabs,"mean_abs":sumabs/values if values else 0.,
            "tolerance_applied":None,"all_values_finite_both":True}
    else:result["float_error"]="NOT_COMPUTED_VIEW_OR_DTYPE_SCOPE"
    return result


def compare(left,right):
    ls,lt,la=flatten(left["bundle"]);rs,rt,ra=flatten(right["bundle"])
    paths=sorted(set(lt)&set(rt))
    cache={};tensor_results={}
    for path in paths:
        a,b=lt[path],rt[path]
        key=(a.row["storage"],b.row["storage"],a.index,b.index)
        if key not in cache:cache[key]=compare_tensor(left,right,a,b)
        tensor_results[path]=cache[key]
    diffs={p:{"left":ls.get(p),"right":rs.get(p)}
           for p in sorted(set(ls)|set(rs)) if p not in ls or p not in rs or ls[p]!=rs[p]}
    exact=(not diffs and set(lt)==set(rt) and la==ra
           and all(v["bytes_equal"] and v["layout_equal"] for v in tensor_results.values()))
    return {"left":left["path"].name,"right":right["path"].name,
        "classification":"ALL_CAPTURED_STATE_EXACT" if exact else "CAPTURED_STATE_DIFFERENCES_OBSERVED",
        "scalar_field_differences":diffs,
        "tensor_paths_missing_left":sorted(set(rt)-set(lt)),
        "tensor_paths_missing_right":sorted(set(lt)-set(rt)),
        "alias_topology_equal":la==ra,
        "alias_topology_differences":None if la==ra else {"left":la,"right":ra},
        "tensor_comparisons":tensor_results,
        "no_tolerance_or_numeric_pass_invented":True}


def main():
    started=time.monotonic()
    parser=argparse.ArgumentParser()
    parser.add_argument("--historical",required=True,type=Path)
    parser.add_argument("--a1",required=True,type=Path)
    parser.add_argument("--a2",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--candidate-provenance",default="FAILED_JOB_ORPHANED_COMPLETE_STORAGE_NOT_RESTORE_QUALIFIED",choices=["FAILED_JOB_ORPHANED_COMPLETE_STORAGE_NOT_RESTORE_QUALIFIED","COMPLETED_JOB_SAVED_STATE_GPU_RESTORE_VERIFIED"])
    args=parser.parse_args()
    states=[load(p) for p in [args.historical,args.a1,args.a2]]
    result={"scope":"EARLY_SAME_SOURCE_SAME_INPUT_COMPLETE_ENDPOINT_STATES_ONLY",
        "method":"HASH_VERIFIED_TOKEN_METADATA_AND_STREAMED_REAL_STORAGE_BITS",
        "torch_imported":False,"cuda_calls":0,"nvml_calls":0,"lock_calls":0,
        "python_immutable_memo_identity":"NOT_A_VALUE_OR_TENSOR_ALIAS_DIFFERENCE",
        "states":[{"name":s["path"].name,"path":str(s["path"]),
            "manifest_sha256":s["manifest_sha256"],
            "next_step":s["bundle"]["next_step"],"provenance_class":"HISTORICAL_SAVED_STATE" if s is states[0] else args.candidate_provenance, "sidecar_present":s["path"].with_suffix(".sidecar.json").exists()} for s in states],
        "comparisons":[compare(states[0],states[1]),compare(states[1],states[2])],
        "performance_or_late_qualification":"NOT_ESTABLISHED_BY_EARLY_COMPARISON"}
    result["cpu_helper_resource_scope"]={"elapsed_seconds":time.monotonic()-started,"self_ru_maxrss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"affinity":sorted(os.sched_getaffinity(0)),"scope":"THIS_SINGLE_CPU_PROCESS_HWM_NOT_GOAL_TREE_OR_CGROUP_PEAK","buffer":"4MiB raw per stream; NumPy comparison temporaries bounded to stream blocks"}
    assert "torch" not in sys.modules
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps([{"pair":[r["left"],r["right"]],"classification":r["classification"],
                      "scalar_diff_count":len(r["scalar_field_differences"]),
                      "alias_topology_equal":r["alias_topology_equal"]}
                     for r in result["comparisons"]]))


if __name__=="__main__":main()
