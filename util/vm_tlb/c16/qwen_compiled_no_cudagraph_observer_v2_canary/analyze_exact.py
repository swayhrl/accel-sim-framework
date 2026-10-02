#!/usr/bin/env python3
"""Independent CPU-only gate over the exact Lane6 native runner output."""
import csv
import json
import statistics
import sys
from pathlib import Path

ORDER=["OFF","ON","ON","OFF","OFF","ON"]
SOURCES=[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)]

def expected_for(path,point):
    with path.open(newline="") as f:
        return [row for row in csv.DictReader(f,delimiter="\t") if row["point_id"]==point]

def semantic_ok(receipt,expected):
    if receipt is None or len(receipt.get("semantic_order",[]))!=4608:
        return False
    for row,target in zip(receipt["semantic_order"],expected):
        if row["ordinal"]!=int(target["ordinal"]) or row["module"]!=target["module_name"]:
            return False
        if row["input_shape"]!=json.loads(target["expected_input_shape"]) or row["output_shape"]!=json.loads(target["expected_output_shape"]):
            return False
    return True

def row_checks(reference,candidate,point):
    sources=SOURCES[:1 if point=="MP02" else 4]
    if len(reference)!=len(candidate) or len(reference)!=len(sources):return False,[]
    rows=[]
    for i,source in enumerate(sources):
        a,b=reference[i],candidate[i]
        mapping=a["batch_row"]==b["batch_row"]==i and a["source_id"]==b["source_id"]==source
        shape=a["prompt_token_count"]==b["prompt_token_count"]==512 and len(a["tokens"])==len(b["tokens"])==len(a["sampled_logprobs"])==len(b["sampled_logprobs"])==32
        for j in range(32):
            token=shape and a["tokens"][j]==b["tokens"][j]
            delta=abs(a["sampled_logprobs"][j]-b["sampled_logprobs"][j]) if shape else None
            tol=0.05+0.01*abs(a["sampled_logprobs"][j]) if shape else None
            logprob=delta is not None and delta<=tol
            rows.append({"point":point,"row":i,"source_id":source,"step":j,"mapping":mapping,"shape":shape,
                         "token":token,"logprob":logprob,"abs_delta":delta,"tolerance":tol})
    return all(x["mapping"] and x["shape"] and x["token"] and x["logprob"] for x in rows),rows

def error_decision(run):
    explicit=run.get("gate_status")
    if explicit in ("COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CORRECTNESS_FAIL","COMPILED_NO_CUDAGRAPH_OBSERVER_V2_NEUTRALITY_FAIL","COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL","CANARY_ENGINEERING_STOP"):
        return explicit
    error=(run.get("error") or "").lower()
    if any(term in error for term in ("semantic","compiled","backend","cuda graph","mode_b","module census","kernel inventory")):
        return "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
    if "neutrality" in error:
        return "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_NEUTRALITY_FAIL"
    if any(term in error for term in ("logprob","correctness","token","row")):
        return "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CORRECTNESS_FAIL"
    return "CANARY_ENGINEERING_STOP"

def analyze(run,expected_path):
    point=run["point"]
    if run.get("status")!="PASS":
        return {"point":point,"status":"FAIL","decision":error_decision(run),"error":run.get("error"),
                "gate_status":run.get("gate_status"),"semantic_failure_receipt_count":len(run.get("semantic_failure_receipts",[]))}
    expected=expected_for(expected_path,point)
    measured=run["measured"]
    config=run["config"]
    identity=run["runtime_identity"]
    checks={
        "warmups_both_arms":set(run["warmups"])=={"OFF","ON"},
        "native_order_exact":[x["arm"] for x in measured]==ORDER,
        "mode_b_compiled":config=={"enforce_eager":False,"compilation_mode":"VLLM_COMPILE","backend":"inductor","cudagraph_mode":"NONE"} and identity["compiled_qwen2model"] is True and identity["skip_compiled_seen"] is False and identity["capture_count"]==0,
        "backend_exact":identity["attention_impl"]==["FlashAttentionImpl"] and identity["linear_method"]==["UnquantizedLinearMethod"],
        "semantic_warmup_on":semantic_ok(run["warmups"]["ON"]["semantic"],expected),
        "semantic_all_on":all(semantic_ok(x["semantic"],expected) for x in measured if x["arm"]=="ON"),
        "off_has_no_semantic":all(x["semantic"] is None for x in measured if x["arm"]=="OFF"),
    }
    reference=next(x["rows"] for x in measured if x["arm"]=="OFF")
    by_step=[]
    for i,sample in enumerate(measured):
        passed,rows=row_checks(reference,sample["rows"],point)
        by_step += [{"sample_index":i,"arm":sample["arm"],**row} for row in rows]
        checks[f"correctness_sample_{i}"]=passed
    off=[x for x in measured if x["arm"]=="OFF"]
    on=[x for x in measured if x["arm"]=="ON"]
    cuda_off=statistics.median(x["request_cuda_event_ms"] for x in off)
    cuda_on=statistics.median(x["request_cuda_event_ms"] for x in on)
    host_off=statistics.median(x["host_wall_ms"] for x in off)
    host_on=statistics.median(x["host_wall_ms"] for x in on)
    cuda_limit=max(5.0,0.10*cuda_off)
    host_limit=max(5.0,0.10*host_off)
    checks["neutrality_primary"]=abs(cuda_on-cuda_off)<=cuda_limit
    checks["host_crosscheck"]=abs(host_on-host_off)<=host_limit
    inventory=run["kernel_inventory"]
    checks["kernel_inventory_exact"]=set(inventory)=={"OFF","ON"} and inventory["OFF"]["kernel_count"]==inventory["ON"]["kernel_count"] and inventory["OFF"]["kernel_inventory_sha256"]==inventory["ON"]["kernel_inventory_sha256"]
    if checks["kernel_inventory_exact"]:
        names=list(inventory["OFF"]["kernel_inventory"])
        checks["bf16_kernel_family"]=any("bf16" in x.lower() and ("gemm" in x.lower() or "gemvx" in x.lower()) for x in names)
    else:checks["bf16_kernel_family"]=False
    if all(checks.values()):
        decision="NATIVE_NEUTRALITY_PASS";status="NATIVE_NEUTRALITY_PASS"
    elif not all(checks[k] for k in checks if k.startswith("correctness_")):
        decision="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CORRECTNESS_FAIL";status="FAIL"
    elif not checks["neutrality_primary"]:
        decision="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_NEUTRALITY_FAIL";status="FAIL"
    elif not checks["host_crosscheck"]:
        decision="CANARY_ENGINEERING_STOP";status="FAIL"
    else:
        decision="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL";status="FAIL"
    return {"point":point,"status":status,"decision":decision,"checks":checks,
            "semantic_range_count_per_on":[len(x["semantic"]["semantic_order"]) for x in measured if x["arm"]=="ON"],
            "correctness_by_step":by_step,
            "neutrality":{"primary_field":"request_cuda_event_ms","median_off_ms":cuda_off,"median_on_ms":cuda_on,"abs_delta_ms":abs(cuda_on-cuda_off),"limit_ms":cuda_limit,
                          "host_crosscheck_median_off_ms":host_off,"host_crosscheck_median_on_ms":host_on,"host_abs_delta_ms":abs(host_on-host_off),"host_limit_ms":host_limit,
                          "duration_role":"OBSERVER_QUALIFICATION_ONLY_NOT_STAGEA_SCIENCE"}}

if __name__=="__main__":
    raw=json.loads(Path(sys.argv[1]).read_text())
    result=analyze(raw,Path(sys.argv[2]))
    Path(sys.argv[3]).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"point":result["point"],"status":result["status"],"decision":result["decision"]}))
