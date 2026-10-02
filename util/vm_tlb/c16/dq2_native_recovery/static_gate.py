#!/usr/bin/env python3
"""CPU-only source gate for accepted Stage A V1 observer-OFF CUDA Event endpoint."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"
STAGE_COMMIT="82788c2d587e86f94791d65aaa2bde28929f9303"
STAGE_PATH="util/vm_tlb/c16/stagea_dense_first_tier0/runner.py"
STAGE_SHA="e5d0c14d008b80d54e3606c98946778fd3954f2c6c07ba8da558b01ba5a17379"

def ordered(source,terms):
    at=-1
    for term in terms:
        i=source.find(term,at+1)
        if i<0:return False
        at=i
    return True

def main():
    stage=subprocess.check_output(["git","-C",str(ROOT),"show",f"{STAGE_COMMIT}:{STAGE_PATH}"])
    runner=(HERE/"runner.py").read_bytes()
    stage_text=stage.decode();new_text=runner.decode()
    stage_ast=ast.parse(stage_text);new_ast=ast.parse(new_text)
    marker=("torch.cuda.synchronize()","torch.cuda.Event(enable_timing=True)",
            "torch.cuda.Event(enable_timing=True)","start.record()","llm.generate(","stop.record()",
            "torch.cuda.synchronize()","start.elapsed_time(stop)")
    checks={
      "accepted_stage_runner_sha":hashlib.sha256(stage).hexdigest()==STAGE_SHA,
      "stage_native_arm_off":"samples = [invoke(False, False) for _ in range(3)]" in stage_text,
      "stage_endpoint_order":ordered(stage_text[stage_text.index("def invoke("):],marker),
      "new_endpoint_order":ordered(new_text[new_text.index("def request("):],marker),
      "new_event_pair_only_request":new_text.count("torch.cuda.Event(enable_timing=True)")==2,
      "new_no_semantic_hooks":not any(term in new_text for term in ("HookSession","register_forward_pre_hook","register_forward_hook","torch.cuda.nvtx","torch.profiler")),
      "mode_a_no_eager":"enforce_eager=False" in new_text,
      "mode_b_compile_without_graph":"CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)" in new_text,
      "two_warmups_five_formal":"for i in range(2)" in new_text and "for i in range(5)" in new_text,
      "frozen_sampling":"temperature=0.0,top_p=1.0,max_tokens=32,ignore_eos=True,detokenize=False,logprobs=20" in new_text,
      "no_custom_op_or_qwen_edit":"torch.ops." not in new_text and "model.forward" not in new_text,
      "no_graph_program_mutation":"ModelCudaGraphManager.run_fullgraph" in new_text and "self.graphs[" not in new_text,
    }
    result={"status":"PASS" if all(checks.values()) else "DQ2_TIMING_AUTHORITY_UNRESOLVED",
            "checks":checks,"accepted_stage_runner_commit":STAGE_COMMIT,"accepted_stage_runner_sha256":hashlib.sha256(stage).hexdigest(),
            "new_runner_sha256":hashlib.sha256(runner).hexdigest(),
            "endpoint":"torch.cuda.synchronize; start/stop CUDA Event around one llm.generate; post-sync; start.elapsed_time(stop)",
            "identity_counter":"manager-level run_fullgraph call count; no semantic module hooks or compiled-graph edit",
            "cuda_initialized":False,"gpu_lock_acquired":False}
    PACK.mkdir(parents=True,exist_ok=True)
    (PACK/"TIMING_AUTHORITY.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"checks":len(checks)}))
    if result["status"]!="PASS":raise SystemExit(2)

if __name__=="__main__":main()
