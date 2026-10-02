#!/usr/bin/env python3
"""One fresh-process Qwen BF16 native timing arm under the frozen DQ2 contract."""
import argparse
import csv
import dataclasses
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch
import vllm
from vllm import LLM, SamplingParams
from vllm.compilation.counter import compilation_counter
from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
from vllm.config.compilation import CUDAGraphMode, CompilationConfig, CompilationMode
from vllm.v1.worker.gpu.cudagraph_utils import ModelCudaGraphManager

ROOT=Path(__file__).resolve().parents[4]
ASSET=ROOT/"docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"
EXPECTED_REVISION="aa8e72537993ba99e69dfaafa59ed015b17504d1"
EXPECTED_UUID="GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"
EXPECTED_SOURCE={"compilation.py":"c9cec5c7200e8e559810ec8c30113ad61dab6780f9f7fb3c116bd0d9b5a43065",
                 "qwen2.py":"eb2f0eeb13c57a28bbc06bc64afff18cd8865f89fbe9ff2a3cf3a896f037cfe9"}
STABLE_COUNTERS=("num_backend_compilations","num_cudagraph_captured","num_inductor_compiles",
                 "num_eager_compiles","num_cache_entries_updated","num_compiled_artifacts_saved",
                 "num_aot_compiles","num_aot_artifacts_saved")

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def sha_ids(ids):
    return hashlib.sha256(json.dumps(ids,sort_keys=True,separators=(",", ":")).encode()).hexdigest()

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")
    tmp.replace(path)

def input_rows(point):
    sources=[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(1 if point=="MP02" else 4)]
    with (ASSET/"TOKENIZATION_RECEIPTS.tsv").open(newline="") as f:
        receipt={(r["model_key"],r["source_text_id"]):r for r in csv.DictReader(f,delimiter="\t")}
    prompts=[];bindings=[]
    for source in sources:
        p=ASSET/"token_ids/QWEN_BF16"/f"{source}.json"
        ids=json.loads(p.read_text())
        r=receipt[("QWEN_BF16",source)]
        if len(ids)!=512 or not all(type(x) is int for x in ids) or sha(p)!=r["token_id_file_sha256"] or sha_ids(ids)!=r["token_ids_sha256"]:
            raise RuntimeError(f"frozen input identity invalid: {source}")
        if r["model_revision"]!=EXPECTED_REVISION or r["tokenizer_revision"]!=EXPECTED_REVISION:
            raise RuntimeError("frozen tokenizer/model revision invalid")
        prompts.append({"prompt_token_ids":ids})
        bindings.append({"source_id":source,"token_file":str(p),"token_file_sha256":sha(p),"token_ids_sha256":sha_ids(ids),"token_count":len(ids)})
    return sources,prompts,bindings

def output_rows(outputs,sources):
    if len(outputs)!=len(sources):raise RuntimeError("batch row count changed")
    rows=[]
    for index,(response,source) in enumerate(zip(outputs,sources)):
        if len(response.outputs)!=1 or len(response.prompt_token_ids)!=512:
            raise RuntimeError("response row/prompt shape changed")
        completion=response.outputs[0]
        ids=[int(x) for x in completion.token_ids]
        if len(ids)!=32 or completion.logprobs is None or len(completion.logprobs)!=32:
            raise RuntimeError("D0-D31 completion length changed")
        sampled=[]
        for step,token in enumerate(ids):
            if token not in completion.logprobs[step]:raise RuntimeError(f"sampled logprob absent D{step}")
            sampled.append(float(completion.logprobs[step][token].logprob))
        rows.append({"batch_row":index,"source_id":source,"prompt_token_count":len(response.prompt_token_ids),
                     "request_id":str(response.request_id),"tokens":ids,"sampled_logprobs":sampled})
    return rows

def compiled_receipt(model):
    return [{"name":name,"class":type(module).__name__,"do_not_compile":bool(getattr(module,"do_not_compile",True)),
             "compiled":bool(getattr(module,"compiled",False)),"aot_compiled_fn":getattr(module,"aot_compiled_fn",None) is not None}
            for name,module in model.named_modules() if isinstance(module,TorchCompileWithNoGuardsWrapper)]

def gpu_metadata():
    gpu=subprocess.check_output(["nvidia-smi","--query-gpu=uuid,name,driver_version","--format=csv,noheader"],text=True).strip().split(",")
    return {"uuid":gpu[0].strip(),"name":gpu[1].strip(),"driver_version":gpu[2].strip(),
            "capability":list(torch.cuda.get_device_capability(0))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--point",choices=("MP02","MP03"),required=True)
    p.add_argument("--mode",choices=("A","B"),required=True)
    p.add_argument("--model",type=Path,required=True)
    p.add_argument("--expected-cache-path",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result={"schema":"C16_DQ2_NATIVE_ARM_RAW_V1","point":args.point,"mode":args.mode,"status":"RUNNING",
            "timing_endpoint":"STAGEA_V1_OBSERVER_OFF_REQUEST_CUDA_EVENT_PAIR","warmup_count_required":2,
            "formal_count_required":5,"warmups":[],"formal_samples":[],"process_id":os.getpid()}
    phase=["INIT"]
    current_graph=[]
    original_fullgraph=ModelCudaGraphManager.run_fullgraph
    def graph_counted(self,descriptor):
        value=original_fullgraph(self,descriptor)
        if phase[0] in ("WARMUP","FORMAL"):
            current_graph.append(str(descriptor))
        return value
    ModelCudaGraphManager.run_fullgraph=graph_counted
    try:
        if args.model.name!=EXPECTED_REVISION:raise RuntimeError("model revision path mismatch")
        source_root=Path(vllm.__file__).resolve().parent
        source_hashes={"compilation.py":sha(source_root/"config/compilation.py"),
                       "qwen2.py":sha(source_root/"model_executor/models/qwen2.py")}
        if source_hashes!=EXPECTED_SOURCE:raise RuntimeError("installed vLLM source SHA mismatch")
        sources,prompts,bindings=input_rows(args.point)
        batch=len(prompts)
        construct=dict(model=str(args.model),tokenizer=str(args.model),skip_tokenizer_init=True,
                       dtype="bfloat16",quantization=None,model_impl="vllm",enforce_eager=False,
                       tensor_parallel_size=1,max_model_len=544,max_num_seqs=batch,
                       max_num_batched_tokens=batch*544,gpu_memory_utilization=0.92,cpu_offload_gb=0,
                       enable_prefix_caching=False,seed=0,disable_log_stats=True)
        if args.mode=="B":construct["compilation_config"]=CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)
        llm=LLM(**construct)
        runner=llm.llm_engine.model_executor.driver_worker.model_runner
        config=runner.vllm_config
        cc=config.compilation_config
        model=runner.get_model()
        manager=runner.cudagraph_manager
        if config.model_config.enforce_eager or cc.mode!=CompilationMode.VLLM_COMPILE or cc.backend!="inductor":
            raise RuntimeError("compiled Mode A/B identity invalid")
        if cc.cudagraph_mode!=(CUDAGraphMode.NONE if args.mode=="B" else CUDAGraphMode.FULL_AND_PIECEWISE):
            raise RuntimeError("effective CUDA Graph mode changed")
        if os.environ.get("TORCH_COMPILE_DISABLE") in ("1","true","True"):
            raise RuntimeError("torch compile disabled")
        if cc.local_cache_dir is not None and str(cc.local_cache_dir)!=str(args.expected_cache_path):
            raise RuntimeError(f"compile cache path changed before warmup: {cc.local_cache_dir}")
        if bool(getattr(runner,"is_encoder_decoder",False)):
            raise RuntimeError("unexpected encoder-decoder skip_compiled path")
        modules=list(model.named_modules())
        attention=sorted({type(m.impl).__name__ for _,m in modules if getattr(m,"impl",None) is not None and type(m.impl).__name__.endswith("AttentionImpl")})
        linear=sorted({type(m.quant_method).__name__ for _,m in modules if getattr(m,"quant_method",None) is not None and type(m.quant_method).__name__.endswith("LinearMethod")})
        if attention!=["FlashAttentionImpl"] or linear!=["UnquantizedLinearMethod"]:
            raise RuntimeError("attention/linear backend changed")
        sampling=SamplingParams(temperature=0.0,top_p=1.0,max_tokens=32,ignore_eos=True,detokenize=False,logprobs=20)
        gpu=gpu_metadata()
        if gpu["uuid"]!=EXPECTED_UUID:raise RuntimeError("GPU UUID changed")
        result.update({"model_revision":args.model.name,"model_path":str(args.model),"input_bindings":bindings,
                       "runtime":{"python":platform.python_version(),"torch":torch.__version__,"vllm":vllm.__version__,
                                  "source_sha256":source_hashes,"gpu":gpu,"enforce_eager":config.model_config.enforce_eager,
                                  "compilation_mode":cc.mode.name,"backend":cc.backend,"cudagraph_mode":cc.cudagraph_mode.name,
                                  "cache_path":str(cc.local_cache_dir),"optimization_level":str(getattr(config,"optimization_level",None)),
                                  "skip_compiled":False,"skip_compiled_source_rule":"decoder-only Qwen; vllm/v1/worker/gpu/model_runner.py encoder-input guard"},
                       "backend":{"attention_impl":attention,"linear_method":linear},"batch_size":batch,
                       "real_single_batch_call":True,"max_model_len":544,"seed":0,
                       "sampling":{"temperature":0.0,"top_p":1.0,"max_tokens":32,"ignore_eos":True,"detokenize":False,"logprobs":20}})
        save(args.output,result)

        def request(role,index):
            phase[0]=role
            current_graph.clear()
            graphs_before={str(key) for key in manager.graphs}
            counters_before=dataclasses.asdict(compilation_counter.clone())
            # Exact accepted Stage A V1 observer-OFF request CUDA Event boundary.
            torch.cuda.synchronize()
            start=torch.cuda.Event(enable_timing=True)
            stop=torch.cuda.Event(enable_timing=True)
            start.record()
            host_start=time.perf_counter_ns()
            outputs=llm.generate(prompts,sampling,use_tqdm=False)
            stop.record()
            torch.cuda.synchronize()
            host_end=time.perf_counter_ns()
            elapsed=float(start.elapsed_time(stop))
            graphs_after={str(key) for key in manager.graphs}
            counters_after=dataclasses.asdict(compilation_counter.clone())
            row={"role":role,"index":index,"request_gpu_elapsed_ms":elapsed,
                 "host_wall_ms":(host_end-host_start)/1e6,"rows":output_rows(outputs,sources),
                 "graph_replay_count":len(current_graph),"graph_replay_descriptors":sorted(set(current_graph)),
                 "graph_count_before":len(graphs_before),"graph_count_after":len(graphs_after),
                 "new_graph_descriptors":sorted(graphs_after-graphs_before),
                 "compilation_counter_before":counters_before,"compilation_counter_after":counters_after,
                 "compiled_modules":compiled_receipt(model),
                 "timing_role":"SCIENCE_FORMAL" if role=="FORMAL" else "INLINE_CORRECTNESS_CANARY_NOT_SCIENCE"}
            return row

        for i in range(2):
            row=request("WARMUP",i)
            result["warmups"].append(row)
            save(args.output,result)
        if str(cc.local_cache_dir)!=str(args.expected_cache_path):
            raise RuntimeError(f"compile cache path changed after warmup: {cc.local_cache_dir}")
        active=[item for item in compiled_receipt(model) if item["class"]=="Qwen2Model" and not item["do_not_compile"] and (item["compiled"] or item["aot_compiled_fn"])]
        if not active:raise RuntimeError("Qwen2Model compiled path inactive after warmup")
        if args.mode=="B" and manager.graphs:raise RuntimeError("Mode B graph state present after warmup")
        result["runtime"]["cache_path_after_warmup"]=str(cc.local_cache_dir)
        result["compiled_qwen2model_after_warmup"]=active
        save(args.output,result)
        for i in range(5):
            row=request("FORMAL",i)
            result["formal_samples"].append(row)
            save(args.output,result)
            if any(row["compilation_counter_after"][key]!=row["compilation_counter_before"][key] for key in STABLE_COUNTERS) or row["new_graph_descriptors"]:
                raise RuntimeError("unexpected formal compile or graph capture")
            if args.mode=="A" and not row["graph_replay_count"]:
                raise RuntimeError("Mode A formal request did not use accepted CUDA Graph path")
            if args.mode=="B" and (row["graph_replay_count"] or row["graph_count_after"]):
                raise RuntimeError("Mode B graph capture/replay occurred")
        result["status"]="PASS"
        result["final_compiled_modules"]=compiled_receipt(model)
        save(args.output,result)
    except BaseException as e:
        result.update({"status":"ERROR","error_type":type(e).__name__,"error":str(e),"traceback":traceback.format_exc()})
        save(args.output,result)
    finally:
        ModelCudaGraphManager.run_fullgraph=original_fullgraph
    print(json.dumps({"point":args.point,"mode":args.mode,"status":result["status"],"formal_samples":len(result["formal_samples"])}))
    if result["status"]!="PASS":raise SystemExit(2)

if __name__=="__main__":main()
