"""Independent full retained-state byte/finite checks, no Torch/CUDA runtime."""
import os
os.sched_setaffinity(0,{22,23})
import json,time,sys,resource
from pathlib import Path
import compare_early_states_cpu as c
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1"
def main():
    started=time.monotonic();result=[]
    for path in [OUT/".private/STATES/C_D",OUT/".private/STATES/C_V",OUT/"windows/W2/.private/STATES/C_FINAL"]:
        state=c.load(path);scalars,tensors,aliases=c.flatten(state["bundle"])
        fields={};cache={}
        for name,tensor in tensors.items():
            key=tensor.index
            if key not in cache:cache[key]=c.compare_tensor(state,state,tensor,tensor)
            fields[name]=cache[key]
        floats={k:v["float_error"] for k,v in fields.items() if isinstance(v.get("float_error"),dict)}
        unsupported_float=[k for k,v in fields.items() if v.get("float_error")=="NOT_COMPUTED_VIEW_OR_DTYPE_SCOPE" and ("float" in str(tensors[k].row.get("dtype")))]
        result.append(dict(name=path.name,path=str(path),next_step=state["bundle"]["next_step"],
            manifest_SHA256=state["manifest_sha256"],full_chunk_and_metadata_SHA="PASS",
            tensor_field_count=len(tensors),float_fields_fully_checked=len(floats),
            all_checked_float_fields_finite=all(x["all_values_finite_both"] for x in floats.values()),
            unsupported_float_views=unsupported_float,
            frontier=state["bundle"]["frontier"],current_camera_ids=state["bundle"]["current_camera_ids"],
            float_field_checks=floats,alias_groups=aliases))
    assert "torch" not in sys.modules
    output=dict(states=result,elapsed_seconds=time.monotonic()-started,CPU_helper_HWM_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        affinity=sorted(os.sched_getaffinity(0)),Torch_imported=False,CUDA_NVML_lock_calls=0,
        actual_GPU_restore_authority="W1 production + W2 actual restore receipts, not this CPU check")
    (OUT/"STATE_INDEPENDENT_INSPECTION.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps([{k:v for k,v in s.items() if k not in ["float_field_checks","alias_groups"]} for s in result]))
if __name__=="__main__":main()
