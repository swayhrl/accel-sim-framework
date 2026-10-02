#!/usr/bin/env python3
"""CPU-only directed validation of exact Lane6 result analysis."""
import copy
import csv
import json
from pathlib import Path

from analyze_exact import analyze

EXPECTED=Path("/data/c16/qwen_compiled_no_cudagraph_observer_v2_canary_v1/contract_gate/EXPECTED_SEMANTIC_SEQUENCE.tsv")

def make(point):
    batch=1 if point=="MP02" else 4
    with EXPECTED.open(newline="") as f:
        expected=[r for r in csv.DictReader(f,delimiter="\t") if r["point_id"]==point]
    semantic={"semantic_order":[{"ordinal":int(r["ordinal"]),"module":r["module_name"],
                                 "input_shape":json.loads(r["expected_input_shape"]),
                                 "output_shape":json.loads(r["expected_output_shape"])} for r in expected]}
    rows=[{"batch_row":i,"source_id":f"TRAIN_A_DISCOVERY_{i:02d}","prompt_token_count":512,
           "tokens":list(range(32)),"sampled_logprobs":[-0.1]*32} for i in range(batch)]
    measured=[]
    for arm in ("OFF","ON","ON","OFF","OFF","ON"):
        measured.append({"arm":arm,"rows":copy.deepcopy(rows),"semantic":copy.deepcopy(semantic) if arm=="ON" else None,
                         "request_cuda_event_ms":10.5 if arm=="ON" else 10.0,
                         "host_wall_ms":11.0 if arm=="ON" else 10.0})
    return {"point":point,"status":"PASS","warmups":{"OFF":{"rows":copy.deepcopy(rows),"semantic":None},
             "ON":{"rows":copy.deepcopy(rows),"semantic":copy.deepcopy(semantic)}},"measured":measured,
            "config":{"enforce_eager":False,"compilation_mode":"VLLM_COMPILE","backend":"inductor","cudagraph_mode":"NONE"},
            "runtime_identity":{"compiled_qwen2model":True,"skip_compiled_seen":False,"capture_count":0,
                                "attention_impl":["FlashAttentionImpl"],"linear_method":["UnquantizedLinearMethod"]},
            "kernel_inventory":{"OFF":{"kernel_count":1,"kernel_inventory_sha256":"same","kernel_inventory":{"bf16_gemm":1}},
                                "ON":{"kernel_count":1,"kernel_inventory_sha256":"same","kernel_inventory":{"bf16_gemm":1}}}}

def main():
    for point in ("MP02","MP03"):
        base=make(point)
        assert analyze(base,EXPECTED)["status"]=="NATIVE_NEUTRALITY_PASS"
        x=copy.deepcopy(base);x["measured"][1]["rows"][0]["tokens"][0]=-1
        assert analyze(x,EXPECTED)["decision"]=="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CORRECTNESS_FAIL"
        x=copy.deepcopy(base);x["measured"][1]["semantic"]["semantic_order"][0]["ordinal"]=-1
        assert analyze(x,EXPECTED)["decision"]=="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
        x=copy.deepcopy(base)
        for arm in x["measured"]:
            if arm["arm"]=="ON":arm["request_cuda_event_ms"]=30.0
        assert analyze(x,EXPECTED)["decision"]=="COMPILED_NO_CUDAGRAPH_OBSERVER_V2_NEUTRALITY_FAIL"
        x=copy.deepcopy(base)
        for arm in x["measured"]:
            if arm["arm"]=="ON":arm["host_wall_ms"]=30.0
        assert analyze(x,EXPECTED)["decision"]=="CANARY_ENGINEERING_STOP"
    print("10 exact-contract synthetic gates PASS")

if __name__=="__main__":main()
