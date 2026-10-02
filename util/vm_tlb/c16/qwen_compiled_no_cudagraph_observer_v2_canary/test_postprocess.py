#!/usr/bin/env python3
"""Synthetic CPU-only directed gates for MP02 and true B4 MP03 receipts."""
from copy import deepcopy
from postprocess import gate, ORDER, SOURCES

def fixture(point):
    batch=1 if point=="MP02" else 4
    rows=[{"batch_row":i,"source_id":SOURCES[i],"prompt_token_count":512,
           "tokens":list(range(32)),"sampled_logprobs":[-0.1]*32} for i in range(batch)]
    semantic=[{"ordinal":i,"module":f"model.layers.0.module_{i}","input_shape":[batch,1,128],"output_shape":[batch,1,128]} for i in range(4)]
    arms=[]
    for i,arm in enumerate(ORDER):
        arms.append({"arm":arm,"rows":deepcopy(rows),"semantic":{"semantic_order":deepcopy(semantic)} if arm=="ON" else None,
                     "host_wall_ms":10.5 if arm=="ON" else 10.0})
    return {"point":point,"protocol":"native","batch_size":batch,"real_single_batch_call":True,
            "native_arms":arms,
            "kernel_inventory":{"OFF":{"kernel_counts":{"bf16_gemm":32},"rows":deepcopy(rows)},
                                "ON":{"kernel_counts":{"bf16_gemm":32},"rows":deepcopy(rows)}},
            "runtime":{"enforce_eager":False,"compilation_mode":"VLLM_COMPILE","backend":"inductor",
                       "cudagraph_mode":"NONE","torch_compile_disable":None,"graph_count":0,"full_graph_replays":0},
            "backend":{"attention_impl":["FlashAttentionImpl"],"linear_method":["UnquantizedLinearMethod"],
                       "compiled_modules":[{"class":"Qwen2Model","do_not_compile":False,"compiled":False,"aot_compiled_fn":True}]},
            "observer_v2":{"per_occurrence_cuda_events":0}}

def main():
    for point in ("MP02","MP03"):
        base=fixture(point)
        assert gate(base)["status"]=="PASS"
        broken=deepcopy(base);broken["native_arms"][1]["rows"][0]["tokens"][0]=-1
        assert gate(broken)["status"]=="FAIL"
        broken=deepcopy(base);broken["native_arms"][2]["semantic"]["semantic_order"][1]["ordinal"]=99
        assert gate(broken)["status"]=="FAIL"
        broken=deepcopy(base)
        for arm in broken["native_arms"]:
            if arm["arm"]=="ON": arm["host_wall_ms"]=30.0
        assert gate(broken)["status"]=="FAIL"
        broken=deepcopy(base);broken["kernel_inventory"]["ON"]["kernel_counts"]={"other":32}
        assert gate(broken)["status"]=="FAIL"
    print("8 directed synthetic gates PASS")

if __name__=="__main__": main()
