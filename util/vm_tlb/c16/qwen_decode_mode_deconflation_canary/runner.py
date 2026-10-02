#!/usr/bin/env python3
"""One warmup and one free-running correctness request in one Qwen decode mode."""
import argparse
import hashlib
import json
import os
import time
import traceback
from pathlib import Path

os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch
from torch.profiler import ProfilerActivity, profile
from vllm import LLM, SamplingParams
from vllm.config.compilation import CUDAGraphMode, CompilationConfig
from vllm.compilation.cuda_graph import CUDAGraphWrapper
from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
from vllm.forward_context import get_forward_context, is_forward_context_available
from vllm.v1.worker.gpu.cudagraph_utils import ModelCudaGraphManager

ROOT = Path(__file__).resolve().parents[4]
ASSET_PACK = ROOT / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"

def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def get_model(model_runner):
    return model_runner.get_model() if hasattr(model_runner, "get_model") else model_runner.model

def extract_rows(outputs, sources):
    if len(outputs) != len(sources):
        raise RuntimeError("output batch size mismatch")
    rows = []
    for i, (response, source) in enumerate(zip(outputs, sources)):
        if len(response.outputs) != 1:
            raise RuntimeError("unexpected completions per request")
        output = response.outputs[0]
        tokens = list(output.token_ids)
        sampled = []
        for step, token in enumerate(tokens):
            values = output.logprobs[step]
            if token not in values:
                raise RuntimeError(f"sampled token missing from logprobs at {source} {step}")
            sampled.append(float(values[token].logprob))
        rows.append({"batch_row":i,"source_id":source,"request_id":str(response.request_id),
                     "prompt_token_count":len(response.prompt_token_ids),"tokens":tokens,
                     "sampled_logprobs":sampled})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--point", choices=["MP02","MP03"], required=True)
    ap.add_argument("--mode", choices=["A","B"], required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = {"point":args.point,"mode":args.mode,"status":"RUNNING"}
    phase = ["init"]
    graph = {"replay":0,"capture":0,"shapes":[]}
    original_call = CUDAGraphWrapper.__call__
    original_fullgraph = ModelCudaGraphManager.run_fullgraph

    def tracked_fullgraph(self, descriptor):
        value = original_fullgraph(self, descriptor)
        if phase[0] == "formal":
            graph["replay"] += 1
            graph["shapes"].append(str(descriptor))
        return value

    ModelCudaGraphManager.run_fullgraph = tracked_fullgraph

    def tracked_call(self, *a, **kw):
        before = None
        descriptor = None
        runtime_mode = None
        if phase[0] == "formal" and is_forward_context_available():
            ctx = get_forward_context()
            descriptor = ctx.batch_descriptor
            runtime_mode = ctx.cudagraph_runtime_mode
            if descriptor is not None:
                before = self.concrete_cudagraph_entries.get(descriptor)
        value = original_call(self, *a, **kw)
        if phase[0] == "formal" and descriptor is not None and runtime_mode == self.runtime_mode and runtime_mode != CUDAGraphMode.NONE:
            if before is not None and before.cudagraph is not None:
                graph["replay"] += 1
                graph["shapes"].append(str(descriptor))
            elif self.concrete_cudagraph_entries.get(descriptor) is not None:
                graph["capture"] += 1
                graph["shapes"].append(str(descriptor))
        return value

    CUDAGraphWrapper.__call__ = tracked_call
    try:
        sources = [f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(1 if args.point == "MP02" else 4)]
        prompts = []
        for source in sources:
            ids = json.loads((ASSET_PACK / "token_ids/QWEN_BF16" / f"{source}.json").read_text())
            if len(ids) != 512 or not all(type(x) is int for x in ids):
                raise RuntimeError("invalid frozen token input")
            prompts.append({"prompt_token_ids":ids})
        cache_root = Path(os.environ.get("VLLM_CACHE_ROOT", str(Path.home()/".cache/vllm")))
        construct = dict(model=str(args.model), tokenizer=str(args.model), skip_tokenizer_init=True,
                         dtype="bfloat16", quantization=None, model_impl="vllm", enforce_eager=False,
                         tensor_parallel_size=1, max_model_len=544, max_num_seqs=len(prompts),
                         max_num_batched_tokens=len(prompts)*544, gpu_memory_utilization=0.92,
                         cpu_offload_gb=0, enable_prefix_caching=False, seed=0, disable_log_stats=True)
        if args.mode == "B":
            construct["compilation_config"] = CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)
        existing_cache_dirs = {str(p) for p in cache_root.rglob("*") if p.is_dir()} if cache_root.exists() else set()
        llm = LLM(**construct)
        engine = llm.llm_engine
        runner = engine.model_executor.driver_worker.model_runner
        config = runner.vllm_config
        cc = config.compilation_config
        model = get_model(runner)
        model_calls = {"formal":0,"skip_compiled":False,"compiled_at_call":False}
        model_class = type(model)
        original_model_call = model_class.__call__
        def tracked_model_call(self, *a, **kw):
            if phase[0] == "formal":
                model_calls["formal"] += 1
                if is_forward_context_available():
                    model_calls["skip_compiled"] |= bool(get_forward_context().skip_compiled)
                model_calls["compiled_at_call"] |= bool(getattr(self,"compiled",False) or getattr(self,"aot_compiled_fn",None) is not None)
            return original_model_call(self,*a,**kw)
        model_class.__call__ = tracked_model_call
        model_modules = list(model.named_modules())
        attention = sorted({type(getattr(m,"impl")).__name__ for _,m in model_modules if getattr(m,"impl",None) is not None and type(getattr(m,"impl")).__name__.endswith("AttentionImpl")})
        linear = sorted({type(getattr(m,"quant_method")).__name__ for _,m in model_modules if getattr(m,"quant_method",None) is not None and type(getattr(m,"quant_method")).__name__.endswith("LinearMethod")})
        sampling = SamplingParams(temperature=0.0,top_p=1.0,max_tokens=32,ignore_eos=True,detokenize=False,logprobs=20)
        phase[0] = "warmup"
        warmup = llm.generate(prompts, sampling, use_tqdm=False)
        warmup_rows = extract_rows(warmup,sources)
        phase[0] = "formal"
        with profile(activities=[ProfilerActivity.CPU,ProfilerActivity.CUDA],record_shapes=False,profile_memory=False,with_stack=False) as prof:
            formal = llm.generate(prompts, sampling, use_tqdm=False)
        phase[0] = "done"
        model_class.__call__ = original_model_call
        formal_rows = extract_rows(formal,sources)
        compiled_modules = [{"name":name,"class":type(module).__name__,
                             "do_not_compile":bool(getattr(module,"do_not_compile",True)),
                             "compiled":bool(getattr(module,"compiled",False)),
                             "aot_compiled_fn":getattr(module,"aot_compiled_fn",None) is not None}
                            for name,module in model_modules if isinstance(module,TorchCompileWithNoGuardsWrapper)]
        active_compiled_modules = [m for m in compiled_modules if not m["do_not_compile"] and (m["compiled"] or m["aot_compiled_fn"])]
        kernel_names = sorted({e.name for e in prof.events() if getattr(e,"device_type",None) == torch.autograd.DeviceType.CUDA})
        cache_path = getattr(cc,"local_cache_dir",None)
        cache_path = str(cache_path) if cache_path else str(cache_root / "torch_compile_cache")
        cache_dir = Path(cache_path)
        result.update({
            "status":"PASS","batch_size":len(prompts),"warmup_rows":warmup_rows,"formal_rows":formal_rows,
            "config":{
                "enforce_eager":config.model_config.enforce_eager,
                "compilation_mode":cc.mode.name if cc.mode else None,
                "cudagraph_mode":cc.cudagraph_mode.name if cc.cudagraph_mode is not None else None,
                "optimization_level":str(getattr(config,"optimization_level",None)),
                "backend":cc.backend,"torch_compile_disable":os.environ.get("TORCH_COMPILE_DISABLE"),
                "breakable_cg_env":{k:v for k,v in os.environ.items() if "BREAKABLE" in k and "CUDAGRAPH" in k},
                "mode_argument":"UNSET" if args.mode == "B" else "DEFAULT",
                "backend_argument":"UNSET" if args.mode == "B" else "DEFAULT",
            },
            "runtime_identity":{
                "compiled_model":bool(active_compiled_modules),
                "do_not_compile":not bool(active_compiled_modules),
                "compiled_modules":compiled_modules,
                "skip_compiled_seen":model_calls["skip_compiled"],
                "formal_model_call_count":model_calls["formal"],
                "compiled_at_formal_call":model_calls["compiled_at_call"],
                "formal_graph_replay_count":graph["replay"],
                "formal_graph_capture_count":graph["capture"],
                "formal_graph_shapes":sorted(set(graph["shapes"])),
                "attention_impl":attention,"linear_method":linear,
                "compile_cache_path":cache_path,
                "compile_cache_preexisted":cache_path in existing_cache_dirs,
                "model_class":type(model).__name__,
                "graph_wrapper_class":type(runner.model).__name__,
                "graph_manager_class":type(runner.cudagraph_manager).__name__ if getattr(runner,"cudagraph_manager",None) is not None else None,
            },
            "kernel_names":kernel_names,
            "cuda_device":{"name":torch.cuda.get_device_name(0),"capability":list(torch.cuda.get_device_capability(0))},
        })
    except BaseException as e:
        result.update({"status":"ERROR","error_type":type(e).__name__,"error":str(e),"traceback":traceback.format_exc()})
    finally:
        CUDAGraphWrapper.__call__ = original_call
        ModelCudaGraphManager.run_fullgraph = original_fullgraph
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
        print(json.dumps({k:result.get(k) for k in ("point","mode","status","error_type")}))
    if result["status"] != "PASS":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
