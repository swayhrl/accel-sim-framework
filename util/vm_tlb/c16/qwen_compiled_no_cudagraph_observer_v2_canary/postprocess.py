#!/usr/bin/env python3
"""CPU-only, fail-closed Observer V2 native qualification gates."""
import json
import statistics
import sys
from pathlib import Path

ORDER=("OFF","ON","ON","OFF","OFF","ON")
SOURCES=[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)]
ATOL=0.05
RTOL=0.01

def identity(run):
    c=run["runtime"]
    b=run["backend"]
    compiled=any(x["class"]=="Qwen2Model" and not x["do_not_compile"] and (x["compiled"] or x["aot_compiled_fn"]) for x in b["compiled_modules"])
    return (c["enforce_eager"] is False and c["compilation_mode"]=="VLLM_COMPILE" and
            c["backend"]=="inductor" and c["cudagraph_mode"]=="NONE" and
            c["torch_compile_disable"] not in ("1","true","True") and
            c["graph_count"]==0 and c["full_graph_replays"]==0 and compiled and
            b["attention_impl"]==["FlashAttentionImpl"] and
            b["linear_method"]==["UnquantizedLinearMethod"] and
            run["observer_v2"]["per_occurrence_cuda_events"]==0)

def compare_rows(reference,candidate,point):
    expected=SOURCES[:1 if point=="MP02" else 4]
    if len(reference)!=len(expected) or len(candidate)!=len(expected):
        return False,[]
    details=[]
    for i,source in enumerate(expected):
        a,b=reference[i],candidate[i]
        mapping=a["batch_row"]==b["batch_row"]==i and a["source_id"]==b["source_id"]==source
        shape=a["prompt_token_count"]==b["prompt_token_count"]==512 and len(a["tokens"])==len(b["tokens"])==len(a["sampled_logprobs"])==len(b["sampled_logprobs"])==32
        for j in range(32):
            token=a["tokens"][j]==b["tokens"][j] if shape else False
            delta=abs(a["sampled_logprobs"][j]-b["sampled_logprobs"][j]) if shape else None
            tolerance=ATOL+RTOL*abs(a["sampled_logprobs"][j]) if shape else None
            probability=delta is not None and delta<=tolerance
            details.append({"row":i,"source_id":source,"step":j,"mapping_pass":mapping,"shape_pass":shape,
                            "token_pass":token,"logprob_pass":probability,"abs_logprob_delta":delta,"tolerance":tolerance})
    return all(x["mapping_pass"] and x["shape_pass"] and x["token_pass"] and x["logprob_pass"] for x in details),details

def gate(run):
    point=run["point"]
    arms=run["native_arms"]
    checks={"point_allowlisted":point in ("MP02","MP03"),
            "protocol_native":run["protocol"]=="native",
            "native_order_exact":[x["arm"] for x in arms]==list(ORDER),
            "real_batch":run["batch_size"]==(1 if point=="MP02" else 4) and run["real_single_batch_call"] is True,
            "mode_backend_identity":identity(run)}
    if not checks["native_order_exact"]:
        return {"status":"FAIL","checks":checks,"reason":"NATIVE_ORDER_INVALID"}
    reference=arms[0]["rows"]
    correctness=[]
    for i,arm in enumerate(arms):
        passed,details=compare_rows(reference,arm["rows"],point)
        correctness.extend({"arm_index":i,"arm":arm["arm"],**x} for x in details)
        checks[f"arm_{i}_correctness"]=passed
        checks[f"arm_{i}_semantic_off"]=(arm["semantic"] is None) if arm["arm"]=="OFF" else arm["semantic"] is not None
    sequences=[x["semantic"]["semantic_order"] for x in arms if x["arm"]=="ON"]
    checks["semantic_nonempty"]=all(bool(x) for x in sequences)
    checks["semantic_sequence_exact"]=len(sequences)==3 and all(x==sequences[0] for x in sequences[1:])
    checks["semantic_ordinals_exact"]=all([x["ordinal"] for x in seq]==list(range(len(seq))) for seq in sequences)
    checks["semantic_shapes_present"]=all(x["input_shape"] is not None and x["output_shape"] is not None for seq in sequences for x in seq)
    off=[x["host_wall_ms"] for x in arms if x["arm"]=="OFF"]
    on=[x["host_wall_ms"] for x in arms if x["arm"]=="ON"]
    med_off=statistics.median(off)
    med_on=statistics.median(on)
    delta=abs(med_on-med_off)
    tolerance=max(5.0,0.10*med_off)
    checks["neutrality"]=delta<=tolerance
    inv=run["kernel_inventory"]
    checks["kernel_inventory_exact"]=set(inv)=={"OFF","ON"} and inv["OFF"]["kernel_counts"]==inv["ON"]["kernel_counts"]
    if checks["kernel_inventory_exact"]:
        inv_correct,_=compare_rows(inv["OFF"]["rows"],inv["ON"]["rows"],point)
        checks["inventory_output_correctness"]=inv_correct
    else:
        checks["inventory_output_correctness"]=False
    result={"status":"PASS" if all(checks.values()) else "FAIL","point":point,"checks":checks,
            "correctness_rows":correctness,"semantic_range_count_per_on":[len(x) for x in sequences],
            "neutrality":{"endpoint":"host_wall_ms","median_off_ms":med_off,"median_on_ms":med_on,
                          "abs_delta_ms":delta,"tolerance_ms":tolerance,"pass":checks["neutrality"],
                          "duration_role":"QUALIFICATION_DIAGNOSTIC_ONLY"}}
    return result

def main():
    run=json.loads(Path(sys.argv[1]).read_text())
    result=gate(run)
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"point":result["point"],"status":result["status"],"failed":[k for k,v in result["checks"].items() if not v]}))
    if result["status"]!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
