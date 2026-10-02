#!/usr/bin/env python3
"""CPU-only source admission and synthetic Observer V2 hook fixture."""
import ast
import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PACK = ROOT / "docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_PREP_109_V1"
COMMIT = "f63d39c8d90ced038445c264fa8242c524a1aa6f"
REL = "util/vm_tlb/c16/stagea_runtime_qualification/runner.py"
SOURCE_SHA = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"
NAMES = ("sha_json", "select_semantic_modules", "HookSession")

def nodes(source):
    return {node.name:node for node in ast.parse(source).body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in NAMES}

def fixture(generated):
    class Tensor:
        def __init__(self,shape): self.shape=shape
    class NVTX:
        def __init__(self): self.stack=[];self.labels=[]
        def range_push(self,label): self.stack.append(label);self.labels.append(label)
        def range_pop(self): self.stack.pop()
    class CUDA:
        def __init__(self): self.nvtx=NVTX()
        def Event(self,*args,**kwargs): raise AssertionError("per-occurrence CUDA Event forbidden")
    fake_torch=types.SimpleNamespace(Tensor=Tensor,cuda=CUDA())
    selected_nodes=nodes(generated)
    tree=ast.Module(body=[selected_nodes[n] for n in NAMES],type_ignores=[])
    ns={"torch":fake_torch,"hashlib":hashlib,"json":json}
    exec(compile(ast.fix_missing_locations(tree),"observer_v2_fixture","exec"),ns)
    class Handle:
        def remove(self): pass
    class Module:
        def __init__(self): self.pre=None;self.post=None
        def register_forward_pre_hook(self,hook): self.pre=hook;return Handle()
        def register_forward_hook(self,hook): self.post=hook;return Handle()
        def forward(self):
            x=Tensor((4,1,128));y=Tensor((4,1,128))
            self.pre(self,(x,));self.post(self,(x,),y)
    modules=[(f"model.layers.0.{suffix}",Module()) for suffix in ("self_attn","mlp.gate_up_proj","mlp.act_fn","mlp.down_proj")]
    class Model:
        def named_modules(self): return iter(modules)
    selected=ns["select_semantic_modules"](Model(),"QWEN_BF16")
    assert len(selected)==4
    session=ns["HookSession"](selected,True).install()
    for _,module in selected: module.forward()
    session.remove()
    receipt=session.receipt()
    assert [x["ordinal"] for x in receipt["semantic_order"]]==list(range(4))
    assert [x["module"] for x in receipt["semantic_order"]]==[name for name,_ in selected]
    assert all(x["input_shape"]==[4,1,128] and x["output_shape"]==[4,1,128] for x in receipt["semantic_order"])
    assert fake_torch.cuda.nvtx.stack==[]
    assert len(fake_torch.cuda.nvtx.labels)==4
    return {"selected_modules":len(selected),"ranges":len(receipt["semantic_ranges"]),"ordinals":[x["ordinal"] for x in receipt["semantic_order"]],"nvtx_balanced":True,"cuda_events_constructed":0}

def main():
    source=subprocess.check_output(["git","-C",str(ROOT),"show",f"{COMMIT}:{REL}"]).decode()
    generated=(HERE/"observer_v2.py").read_text()
    runner=(HERE/"runner.py").read_text()
    source_nodes,generated_nodes=nodes(source),nodes(generated)
    checks={
        "source_commit_exact":subprocess.check_output(["git","-C",str(ROOT),"rev-parse",COMMIT],text=True).strip()==COMMIT,
        "source_sha_exact":hashlib.sha256(source.encode()).hexdigest()==SOURCE_SHA,
        "semantic_names_exact":set(source_nodes)==set(generated_nodes)==set(NAMES),
        "semantic_ast_exact":all(ast.dump(source_nodes[name],include_attributes=False)==ast.dump(generated_nodes[name],include_attributes=False) for name in NAMES),
        "hooksession_cuda_event_calls_zero":"torch.cuda.Event" not in ast.get_source_segment(generated,generated_nodes["HookSession"]),
        "nvtx_push_pop_present":"torch.cuda.nvtx.range_push" in ast.get_source_segment(generated,generated_nodes["HookSession"]) and "torch.cuda.nvtx.range_pop" in ast.get_source_segment(generated,generated_nodes["HookSession"]),
        "mode_b_explicit_none":"CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)" in runner,
        "enforce_eager_false":"enforce_eager=False" in runner,
        "native_order_exact":"NATIVE_ORDER = (\"OFF\", \"ON\", \"ON\", \"OFF\", \"OFF\", \"ON\")" in runner,
        "mode_backend_args_unset":"CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)" in runner and "CompilationConfig(mode=" not in runner and "CompilationConfig(backend=" not in runner,
    }
    fixture_result=fixture(generated)
    checks["synthetic_fixture"]=fixture_result["cuda_events_constructed"]==0 and fixture_result["nvtx_balanced"]
    result={"status":"PASS" if all(checks.values()) else "FAIL","source_commit":COMMIT,"source_sha256":hashlib.sha256(source.encode()).hexdigest(),"generated_module_sha256":hashlib.sha256(generated.encode()).hexdigest(),"checks":checks,"fixture":fixture_result,"cuda_initialized":False,"gpu_lock_acquired":False}
    PACK.mkdir(parents=True,exist_ok=True)
    (PACK/"STATIC_QUALIFICATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"checks":len(checks)}))
    if result["status"]!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
