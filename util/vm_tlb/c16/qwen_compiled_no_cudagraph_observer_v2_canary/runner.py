#!/usr/bin/env python3
"""Qwen BF16 compiled/no-CUDA-Graph Observer V2 qualification process.

This script is imported by no CPU preflight. CUDA is initialized only when
the authorized orchestrator launches this process after contract admission.
"""
import argparse
import hashlib
import json
import os
import time
import traceback
from collections import Counter
from pathlib import Path

os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch
from torch.profiler import ProfilerActivity, profile
from vllm import LLM, SamplingParams
from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
from vllm.config.compilation import CUDAGraphMode, CompilationConfig
from vllm.v1.worker.gpu.cudagraph_utils import ModelCudaGraphManager

from observer_v2 import HookSession, select_semantic_modules

ROOT = Path(__file__).resolve().parents[4]
ASSET = ROOT / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"
NATIVE_ORDER = ("OFF", "ON", "ON", "OFF", "OFF", "ON")

def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def rows_receipt(outputs, sources):
    if len(outputs) != len(sources):
        raise RuntimeError("request batch size mismatch")
    rows=[]
    for i,(response,source) in enumerate(zip(outputs,sources)):
        if len(response.outputs) != 1 or len(response.prompt_token_ids) != 512:
            raise RuntimeError("request shape mismatch")
        completion=response.outputs[0]
        tokens=[int(x) for x in completion.token_ids]
        logprobs=[]
        for j,token in enumerate(tokens):
            item=completion.logprobs[j].get(token)
            if item is None:
                raise RuntimeError(f"sampled-token logprob missing: row={i} step={j}")
            logprobs.append(float(item.logprob))
        rows.append({"batch_row":i,"source_id":source,"request_id":str(response.request_id),
                     "prompt_token_count":len(response.prompt_token_ids),"tokens":tokens,
                     "sampled_logprobs":logprobs})
    return rows

def backend_receipt(model):
    modules=list(model.named_modules())
    attention=sorted({type(m.impl).__name__ for _,m in modules if getattr(m,"impl",None) is not None and type(m.impl).__name__.endswith("AttentionImpl")})
    linear=sorted({type(m.quant_method).__name__ for _,m in modules if getattr(m,"quant_method",None) is not None and type(m.quant_method).__name__.endswith("LinearMethod")})
    compiled=[{"name":name,"class":type(module).__name__,"do_not_compile":bool(getattr(module,"do_not_compile",True)),
               "compiled":bool(getattr(module,"compiled",False)),"aot_compiled_fn":getattr(module,"aot_compiled_fn",None) is not None}
              for name,module in modules if isinstance(module,TorchCompileWithNoGuardsWrapper)]
    return {"attention_impl":attention,"linear_method":linear,"compiled_modules":compiled}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--point",choices=("MP02","MP03"),required=True)
    p.add_argument("--protocol",choices=("native","structural"),required=True)
    p.add_argument("--model",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--inventory-after-native",action="store_true")
    args=p.parse_args()
    result={"point":args.point,"protocol":args.protocol,"status":"RUNNING"}
    graph_counter={"formal_full_replay":0}
    phase=["init"]
    original_fullgraph=ModelCudaGraphManager.run_fullgraph
    def tracked_fullgraph(self,descriptor):
        value=original_fullgraph(self,descriptor)
        if phase[0] in ("native","inventory","structural"):
            graph_counter["formal_full_replay"]+=1
        return value
    ModelCudaGraphManager.run_fullgraph=tracked_fullgraph
    try:
        sources=[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(1 if args.point=="MP02" else 4)]
        prompts=[]
        for source in sources:
            ids=json.loads((ASSET/"token_ids/QWEN_BF16"/f"{source}.json").read_text())
            if len(ids)!=512 or not all(type(x) is int for x in ids):
                raise RuntimeError("frozen input invalid")
            prompts.append({"prompt_token_ids":ids})
        llm=LLM(model=str(args.model),tokenizer=str(args.model),skip_tokenizer_init=True,
                dtype="bfloat16",quantization=None,model_impl="vllm",enforce_eager=False,
                tensor_parallel_size=1,max_model_len=544,max_num_seqs=len(prompts),
                max_num_batched_tokens=len(prompts)*544,gpu_memory_utilization=0.92,
                cpu_offload_gb=0,enable_prefix_caching=False,seed=0,disable_log_stats=True,
                compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE))
        runner=llm.llm_engine.model_executor.driver_worker.model_runner
        model=runner.get_model()
        selected=select_semantic_modules(model,"QWEN_BF16")
        if not selected:
            raise RuntimeError("semantic module census empty")
        cc=runner.vllm_config.compilation_config
        sampling=SamplingParams(temperature=0.0,top_p=1.0,max_tokens=32,ignore_eos=True,detokenize=False,logprobs=20)
        def request(arm,collect=True,measure=True):
            hooks=HookSession(selected,collect).install() if arm=="ON" else None
            if arm=="ON":
                torch.cuda.nvtx.range_push(f"C16_QWEN_OBSERVER_V2_{args.point}_{args.protocol}")
            torch.cuda.synchronize()
            start=stop=None
            if measure:
                start=torch.cuda.Event(enable_timing=True)
                stop=torch.cuda.Event(enable_timing=True)
                start.record()
            host_start=time.perf_counter_ns()
            outputs=llm.generate(prompts,sampling,use_tqdm=False)
            if measure:
                stop.record()
            torch.cuda.synchronize()
            host_end=time.perf_counter_ns()
            if arm=="ON":
                torch.cuda.nvtx.range_pop()
            semantic=None
            if hooks:
                hooks.remove()
                semantic=hooks.receipt()
            return {"arm":arm,"rows":rows_receipt(outputs,sources),"semantic":semantic,
                    "host_wall_ms":(host_end-host_start)/1e6 if measure else None,
                    "outer_cuda_event_ms":float(start.elapsed_time(stop)) if measure else None,
                    "duration_role":"QUALIFICATION_DIAGNOSTIC_ONLY"}
        phase[0]="warmup"
        warmup=request("OFF",collect=False,measure=False)
        native=[]
        inventories={}
        if args.protocol=="native":
            phase[0]="native"
            for arm in NATIVE_ORDER:
                native.append(request(arm,collect=True,measure=True))
            if args.inventory_after_native:
                phase[0]="inventory"
                for arm in ("OFF","ON"):
                    with profile(activities=[ProfilerActivity.CPU,ProfilerActivity.CUDA],record_shapes=False,profile_memory=False,with_stack=False) as prof:
                        inventory_output=request(arm,collect=False,measure=False)
                    names=[e.name for e in prof.events() if getattr(e,"device_type",None)==torch.autograd.DeviceType.CUDA]
                    inventories[arm]={"rows":inventory_output["rows"],"kernel_counts":dict(sorted(Counter(names).items())),
                                      "kernel_names_sha256":sha_json(names),"kernel_counts_sha256":sha_json(dict(sorted(Counter(names).items())))}
        else:
            phase[0]="structural"
            native.append(request("ON",collect=True,measure=False))
        phase[0]="done"
        backends=backend_receipt(model)
        cache_path=getattr(cc,"local_cache_dir",None)
        result.update({"status":"PASS","batch_size":len(prompts),"real_single_batch_call":True,
                       "sources":sources,"warmup":warmup,"native_arms":native,"kernel_inventory":inventories,
                       "backend":backends,"semantic_module_names":[name for name,_ in selected],
                       "runtime":{"enforce_eager":runner.vllm_config.model_config.enforce_eager,
                                  "compilation_mode":cc.mode.name if cc.mode is not None else None,
                                  "cudagraph_mode":cc.cudagraph_mode.name if cc.cudagraph_mode is not None else None,
                                  "backend":cc.backend,"optimization_level":str(getattr(runner.vllm_config,"optimization_level",None)),
                                  "torch_compile_disable":os.environ.get("TORCH_COMPILE_DISABLE"),
                                  "breakable_cg_env":{k:v for k,v in os.environ.items() if "BREAKABLE" in k and "CUDAGRAPH" in k},
                                  "cache_path":str(cache_path) if cache_path else None,
                                  "graph_manager":type(runner.cudagraph_manager).__name__ if runner.cudagraph_manager is not None else None,
                                  "graph_count":len(runner.cudagraph_manager.graphs) if runner.cudagraph_manager is not None else None,
                                  "full_graph_replays":graph_counter["formal_full_replay"]},
                       "observer_v2":{"source_commit":"f63d39c8d90ced038445c264fa8242c524a1aa6f",
                                      "per_occurrence_cuda_events":0}})
    except BaseException as e:
        result.update({"status":"ERROR","error_type":type(e).__name__,"error":str(e),"traceback":traceback.format_exc()})
    finally:
        ModelCudaGraphManager.run_fullgraph=original_fullgraph
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
        print(json.dumps({k:result.get(k) for k in ("point","protocol","status","error_type")}))
    if result["status"]!="PASS":
        raise SystemExit(2)

if __name__=="__main__":
    main()
