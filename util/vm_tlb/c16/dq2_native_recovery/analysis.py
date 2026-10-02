#!/usr/bin/env python3
"""CPU-only frozen correctness/identity gates and deterministic DQ2 formulas."""
import json
import statistics
from pathlib import Path

POINTS=("MP02","MP03")
MODES=("A","B")
STABLE_COUNTERS=("num_backend_compilations","num_cudagraph_captured","num_inductor_compiles",
                 "num_eager_compiles","num_cache_entries_updated","num_compiled_artifacts_saved",
                 "num_aot_compiles","num_aot_artifacts_saved")

def load(path):return json.loads(Path(path).read_text())

def compare_rows(a,b,point,source_ids):
    if len(a)!=len(source_ids) or len(b)!=len(source_ids):return False,[{"reason":"ROW_COUNT"}]
    detail=[]
    for i,source in enumerate(source_ids):
        x,y=a[i],b[i]
        mapping=x["batch_row"]==y["batch_row"]==i and x["source_id"]==y["source_id"]==source
        shape=x["prompt_token_count"]==y["prompt_token_count"]==512 and len(x["tokens"])==len(y["tokens"])==len(x["sampled_logprobs"])==len(y["sampled_logprobs"])==32
        for step in range(32):
            token=shape and x["tokens"][step]==y["tokens"][step]
            delta=abs(x["sampled_logprobs"][step]-y["sampled_logprobs"][step]) if shape else None
            tolerance=0.05+0.01*abs(x["sampled_logprobs"][step]) if shape else None
            prob=delta is not None and delta<=tolerance
            detail.append({"point":point,"row":i,"source_id":source,"step":step,
                           "mapping_pass":mapping,"shape_pass":shape,"token_pass":token,"sampled_logprob_pass":prob,
                           "abs_delta":delta,"tolerance":tolerance})
    return all(x.get("mapping_pass") and x.get("shape_pass") and x.get("token_pass") and x.get("sampled_logprob_pass") for x in detail),detail

def identity(arm,point,mode,contract):
    if arm.get("status")!="PASS":return False,{"runner_status":arm.get("status"),"error":arm.get("error")}
    cfg=arm["runtime"]
    expected=contract["points"][point]
    cache=contract["cache_authority"][f"{point}_{mode}"]["path"]
    actual=(arm["point"]==point and arm["mode"]==mode and arm["model_revision"]==contract["model"]["revision"]
            and arm["batch_size"]==expected["batch"] and arm["real_single_batch_call"] is True
            and [x["source_id"] for x in arm["input_bindings"]]==expected["source_ids"]
            and cfg["enforce_eager"] is False and cfg["compilation_mode"]=="VLLM_COMPILE" and cfg["backend"]=="inductor"
            and cfg["cudagraph_mode"]==("FULL_AND_PIECEWISE" if mode=="A" else "NONE")
            and cfg["cache_path_after_warmup"]==cache and cfg["skip_compiled"] is False
            and cfg["source_sha256"]==contract["vllm_installed_source_sha256"]
            and cfg["gpu"]["uuid"]==contract["gpu"]["uuid"]
            and arm["backend"]["attention_impl"]==["FlashAttentionImpl"]
            and arm["backend"]["linear_method"]==["UnquantizedLinearMethod"])
    active=arm.get("compiled_qwen2model_after_warmup",[])
    actual &= any(x["class"]=="Qwen2Model" and not x["do_not_compile"] and (x["compiled"] or x["aot_compiled_fn"]) for x in active)
    actual &= len(arm["warmups"])==2 and len(arm["formal_samples"])==5
    formal_checks=[]
    for row in arm["formal_samples"]:
        stable=not row["new_graph_descriptors"] and all(row["compilation_counter_before"][k]==row["compilation_counter_after"][k] for k in STABLE_COUNTERS)
        graph=(row["graph_replay_count"]>0 and row["graph_count_before"]>0 and row["graph_count_after"]==row["graph_count_before"]) if mode=="A" else (row["graph_replay_count"]==0 and row["graph_count_before"]==row["graph_count_after"]==0)
        compiled=any(x["class"]=="Qwen2Model" and not x["do_not_compile"] and (x["compiled"] or x["aot_compiled_fn"]) for x in row["compiled_modules"])
        formal_checks.append({"stable_compile_capture":stable,"graph_identity":graph,"compiled_qwen":compiled,
                              "graph_replay_count":row["graph_replay_count"],"descriptors":row["graph_replay_descriptors"]})
    actual &= all(all(x[k] for k in ("stable_compile_capture","graph_identity","compiled_qwen")) for x in formal_checks)
    return bool(actual),{"formal_checks":formal_checks,"cache_path":cfg["cache_path_after_warmup"],
                          "source_sha256":cfg["source_sha256"],"gpu_uuid":cfg["gpu"]["uuid"]}

def validate_point(point,raw_root,contract):
    arms={m:load(Path(raw_root)/f"{point}_{m}.json") for m in MODES}
    ids=contract["points"][point]["source_ids"]
    ids_ok={};ids_detail={}
    for mode in MODES:
        ids_ok[mode],ids_detail[mode]=identity(arms[mode],point,mode,contract)
    accepted=load(contract["accepted_outputs"][f"{point}_A"]["path"])["formal_rows"]
    pair_rows=[];checks=[]
    for role,index in [("WARMUP",i) for i in range(2)]+[("FORMAL",i) for i in range(5)]:
        a=arms["A"]["warmups" if role=="WARMUP" else "formal_samples"][index]["rows"]
        b=arms["B"]["warmups" if role=="WARMUP" else "formal_samples"][index]["rows"]
        ab,rows=compare_rows(a,b,point,ids)
        aa,_=compare_rows(accepted,a,point,ids)
        bb,_=compare_rows(accepted,b,point,ids)
        checks.append({"role":role,"index":index,"a_b_pass":ab,"accepted_a_pass":aa,"accepted_b_pass":bb})
        pair_rows += [{"role":role,"index":index,**x} for x in rows]
    correctness=all(x["a_b_pass"] and x["accepted_a_pass"] and x["accepted_b_pass"] for x in checks)
    return {"point":point,"identity_pass":all(ids_ok.values()),"identity_by_mode":ids_ok,"identity_detail":ids_detail,
            "correctness_pass":correctness,"correctness_checks":checks,"correctness_by_row_step":pair_rows,
            "timing_science_valid":correctness and all(ids_ok.values())}

def median_and_mad(values):
    center=statistics.median(values)
    return {"raw_ms":values,"median_ms":center,"min_ms":min(values),"max_ms":max(values),
            "mad_ms":statistics.median(abs(x-center) for x in values),"sample_count":len(values)}

def metrics(raw_root,point_results):
    if not all(x["timing_science_valid"] for x in point_results):
        return {"status":"NOT_SCIENCE_VALID","reason":"point correctness/identity gate failed"}
    timing={}
    for point,batch in (("MP02",1),("MP03",4)):
        for mode in MODES:
            arm=load(Path(raw_root)/f"{point}_{mode}.json")
            values=[x["request_gpu_elapsed_ms"] for x in arm["formal_samples"]]
            timing[f"{point}_{mode}"]={**median_and_mad(values),"batch":batch,"generated_tokens":batch*32,
                                       "ms_per_generated_token":statistics.median(values)/(batch*32)}
    scale={mode:4*timing[f"MP02_{mode}"]["median_ms"]/timing[f"MP03_{mode}"]["median_ms"] for mode in MODES}
    response={point:{"B_over_A_ratio":timing[f"{point}_B"]["median_ms"]/timing[f"{point}_A"]["median_ms"],
                     "A_vs_B_time_reduction":1-timing[f"{point}_A"]["median_ms"]/timing[f"{point}_B"]["median_ms"]} for point in POINTS}
    return {"status":"DQ2_NATIVE_RECOVERY_COMPLETE","timing":timing,"throughput_scale":scale,
            "mode_response":response,"scale_interaction":{"absolute_difference":abs(scale["A"]-scale["B"]),
                                                             "A_over_B_ratio":scale["A"]/scale["B"]},
            "estimator":"median of exactly five formal request-level CUDA Event elapsed times; warmups excluded",
            "dispersion":"median absolute deviation; five samples are not statistical significance",
            "interpretation":"frozen B1→B4 batch/shape throughput response and Mode A↔B response only"}
