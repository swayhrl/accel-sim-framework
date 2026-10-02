#!/usr/bin/env python3
"""CPU/source-only MP03_B cache-lifecycle root cause and continuation PREEXEC."""
import ast
import difflib
import hashlib
import json
import subprocess
from pathlib import Path

from continuation_cache_lifecycle import EXPECTED_AOT,EXPECTED_FINAL,PINNED_QWEN2_SHA,tree_identity,aot_source_binding,pre_warmup_gate,after_warmup_gate

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_MP03B_CONTINUATION_109_V1"
OLD_PACK=ROOT/"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1"
VLLM_REPO=Path("/data/c16/runtime_environment_audit_v1/source/vllm-v0.30.0")
VLLM_INSTALLED=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/lib/python3.12/site-packages/vllm")
PREEXEC="cfa3ba1f5cb5c236b0000ba0f5656e75e2e05b79"
RESULT="a12bbfa4609ece57fadde107f9fd2e3bc0380cdf"
SOURCE="ced6857afa0ea7b2e3f0846a62e1394e90f15607"
EXPECTED_AOT_SHA="49c6e49f1d66ae080e8c4a216b0398882d8a608eb801c884700ef9dc098d8620"
EXPECTED_FINAL_SHA="3f78b16332bcf03c17977fae96aa1bdf6e68cbcf7634681d303a50e5d2c8e397"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def git(repo,*args):return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def at(repo,commit,path):return subprocess.check_output(["git","-C",str(repo),"show",f"{commit}:{path}"])
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def node(source,name):return next(x for x in ast.walk(ast.parse(source)) if isinstance(x,ast.FunctionDef) and x.name==name)

def build():
    PACK.mkdir(parents=True,exist_ok=True)
    assert git(ROOT,"rev-parse",RESULT)==RESULT and git(ROOT,"rev-parse",RESULT+"^{tree}")=="7830be7533c4169ab1a79478bc7d259f1f6f7752"
    assert git(ROOT,"rev-parse",PREEXEC)==PREEXEC
    old_final=json.loads(at(ROOT,RESULT,"docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1/FINAL_DECISION.json"))
    assert old_final["decision"]=="DQ2_NATIVE_RECOVERY_PARTIAL" and old_final["failed_arm"]=="MP03_B"
    old_runner=at(ROOT,PREEXEC,"util/vm_tlb/c16/dq2_native_recovery/runner.py").decode()
    new_runner=(HERE/"runner.py").read_text()
    previous=at(ROOT,"9122fac5c50dbf19706636fc03978a356ffd800f","util/vm_tlb/c16/qwen_decode_mode_deconflation_canary/runner.py").decode()
    old_raw_path=Path(old_final["raw_local"])/"MP03_B.json"
    old_raw=json.loads(old_raw_path.read_text())
    assert old_raw["error"].endswith(str(EXPECTED_AOT)) and old_raw["warmups"]==[] and old_raw["formal_samples"]==[]
    old_raw_index=json.loads((OLD_PACK/"RAW_INDEX.json").read_text())
    assert sha(old_raw_path)==next(x["sha256"] for x in old_raw_index if x["local_path"]==str(old_raw_path))
    vllm={}
    for rel in ("compilation/decorators.py","compilation/backends.py","config/compilation.py","compilation/caching.py"):
        pinned=at(VLLM_REPO,SOURCE,"vllm/"+rel)
        installed=VLLM_INSTALLED/rel
        vllm[rel]={"pinned_sha256":hashlib.sha256(pinned).hexdigest(),"installed_sha256":sha(installed),
                   "bytes_exact":hashlib.sha256(pinned).hexdigest()==sha(installed)}
    assert all(x["bytes_exact"] for x in vllm.values())
    decorators=(VLLM_INSTALLED/"compilation/decorators.py").read_text()
    backends=(VLLM_INSTALLED/"compilation/backends.py").read_text()
    compilation=(VLLM_INSTALLED/"config/compilation.py").read_text()
    checks={
        "old_9122_reads_after_formal":previous.index('formal_rows = extract_rows(formal,sources)')<previous.index('cache_path = getattr(cc,"local_cache_dir",None)'),
        "old_dq2_checks_before_warmup":old_runner.index('if cc.local_cache_dir is not None')<old_runner.index('for i in range(2)'),
        "decorators_aot_root_stage":"self.compilation_config.local_cache_dir = cache_dir" in decorators and '"torch_aot_compile"' in decorators,
        "decorators_aot_cache_hit_early_return":"self.aot_compiled_fn = loaded_fn" in decorators and "return output" in decorators[decorators.index("self.aot_compiled_fn = loaded_fn"):decorators.index("if self.compiled:")],
        "backends_final_rank_backbone_stage":"self.compilation_config.local_cache_dir = local_cache_dir" in backends and 'f"rank_{rank}_{dp_rank}"' in backends and 'self.prefix' in backends,
        "hash_ignores_local_cache_dir":"\"local_cache_dir\"," in compilation[compilation.index("ignored_factors = {"):compilation.index("return hash_factors(factors)",compilation.index("ignored_factors = {"))],
        "request_timing_ast_unchanged":ast.dump(node(old_runner,"request"),include_attributes=False)==ast.dump(node(new_runner,"request"),include_attributes=False),
        "LLM_constructor_unchanged":ast.dump(next(x for x in ast.walk(ast.parse(old_runner)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="LLM"),include_attributes=False)==ast.dump(next(x for x in ast.walk(ast.parse(new_runner)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="LLM"),include_attributes=False),
        "sampling_constructor_unchanged":ast.dump(next(x for x in ast.walk(ast.parse(old_runner)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="SamplingParams"),include_attributes=False)==ast.dump(next(x for x in ast.walk(ast.parse(new_runner)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="SamplingParams"),include_attributes=False),
    }
    if not all(checks.values()):raise RuntimeError(f"CPU source root-cause check failed: {[k for k,v in checks.items() if not v]}")
    aot=tree_identity(EXPECTED_AOT);binding=aot_source_binding(EXPECTED_AOT)
    accepted=tree_identity(EXPECTED_FINAL)
    assert aot["content_identity_sha256"]==EXPECTED_AOT_SHA and binding["status"]=="PASS" and binding["embedded_pinned_qwen2_source_sha256"]==PINNED_QWEN2_SHA
    assert accepted["content_identity_sha256"]==EXPECTED_FINAL_SHA
    assert pre_warmup_gate(EXPECTED_AOT,EXPECTED_AOT_SHA)["status"]=="PASS"
    assert pre_warmup_gate(EXPECTED_FINAL,EXPECTED_AOT_SHA)["status"]!="PASS"
    assert after_warmup_gate(EXPECTED_FINAL,EXPECTED_FINAL_SHA)["status"]=="PASS"
    assert after_warmup_gate(EXPECTED_AOT,EXPECTED_FINAL_SHA)["status"]!="PASS"
    diff="".join(difflib.unified_diff(old_runner.splitlines(keepends=True),new_runner.splitlines(keepends=True),fromfile=f"{PREEXEC}:runner.py",tofile="continuation:runner.py"))
    diff="\n".join(line.rstrip() for line in diff.splitlines())+"\n"
    (PACK/"RUNNER_SURGICAL_DIFF.patch").write_text(diff)
    audit={"status":"PASS_CPU_SOURCE_ONLY","original_result_commit":RESULT,"original_preexec_commit":PREEXEC,
           "old_mp03_b_raw_path":str(old_raw_path),"old_mp03_b_raw_sha256":sha(old_raw_path),
           "old_error":old_raw["error"],"old_result_status_is_valid_partial":True,
           "source_commit":SOURCE,"installed_pinned_source_sha":vllm,"checks":checks,
           "pre_warmup_aot":{"tree_sha256":aot["content_identity_sha256"],"file_count":aot["file_count"],
                             "model_pickle_sha256":binding["model_sha256"],"embedded_qwen2_source_sha256":PINNED_QWEN2_SHA,
                             "source_binding":binding["status"]},
           "accepted_after_warmup":{"path":str(EXPECTED_FINAL),"tree_sha256":accepted["content_identity_sha256"],
                                    "file_count":accepted["file_count"]},
           "conditional_path_note":"Pinned decorators.py returns early on an AOT cache hit. Inductor's second path assignment is conditional, so post-warmup convergence must be observed; it is not asserted from source alone.",
           "gpu_used":False,"gpu_lock_acquired":False}
    save(PACK/"CACHE_PATH_LIFECYCLE_SOURCE_AUDIT.json",audit)
    (PACK/"CACHE_PATH_LIFECYCLE_ROOT_CAUSE.md").write_text(f"""# MP03_B cache-path lifecycle root cause

The original PREEXEC (`{PREEXEC}`) and PARTIAL result (`{RESULT}`) remain valid and unchanged. The original runner correctly stopped before warmup when its *then-frozen* gate compared the pre-warmup AOT path `{EXPECTED_AOT}` with the 9122 **final** path `{EXPECTED_FINAL}`. The problem is that this gate equated two distinct lifecycle stages.

The 9122 runner reads `cc.local_cache_dir` after warmup/formal, not before. In pinned `decorators.py`, `TorchCompileWithNoGuardsWrapper.__call__` first assigns `torch_compile_cache/torch_aot_compile/<hash>`; the hash includes environment/config/model factors (`aot_compile_hash_factors` plus `_model_hash_key`). In pinned `backends.py`, Inductor may later assign `rank_<rank>_<dp_rank>/backbone`. Pinned `compilation.py` excludes `local_cache_dir` from compiled graph hash factors. All four installed source files match `vllm-project/vllm@{SOURCE}` byte for byte.

The pre-warmup AOT directory exists with {aot['file_count']} files and content identity `{EXPECTED_AOT_SHA}`. Its non-executing pickle scan finds the pinned Qwen2 source bytes (SHA `{PINNED_QWEN2_SHA}`) and `Qwen2Model.forward`; the failed original MP03_B process computed this path after passing its model/config/backend checks. The accepted 9122 final path still has content identity `{EXPECTED_FINAL_SHA}`.

One important condition remains: pinned `decorators.py` can load a preexisting AOT artifact and **return before Inductor's second assignment**. Thus source alone does not guarantee a transition to `{EXPECTED_FINAL}`. The continuation records the AOT path/content/source binding before warmup and requires the accepted final path/content after exactly two warmups. If it does not converge, the arm stops before any formal sample. No cache deletion, environment change, recompile, Qwen/vLLM edit or alternate path policy is authorized.\n""")
    code_files=("runner.py","continuation_cache_lifecycle.py","continuation_execute.py","continuation_preexec.py","analysis.py","cache_check.py","publish.py","verify_raw.py")
    code_sha={name:sha(HERE/name) for name in code_files}
    contract={"schema":"C16_DQ2_MP03B_CONTINUATION_PREEXEC_V1","goal":"C16_DQ2_NATIVE_RECOVERY_109_V1_MP03B_CONTINUATION",
              "status":"FROZEN_PREEXEC_AUTHORIZED_BY_USER","branch":"hrl/c16-dq2-native-recovery-109-v1",
              "original_preexec_commit":PREEXEC,"original_result_commit":RESULT,"old_raw":str(Path(old_final["raw_local"])),
              "only_new_arm":"MP03_B","no_old_arm_rerun":["MP02_A","MP02_B","MP03_A"],
              "model_source_sampler_timing_correctness_formulas":"EXACTLY_UNCHANGED_FROM_ORIGINAL_PREEXEC",
              "model_revision":"aa8e72537993ba99e69dfaafa59ed015b17504d1",
              "point":{"id":"MP03","batch":4,"source_ids":[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)],"prompt_tokens_per_row":512,"decode_steps":32},
              "mode":{"id":"B","enforce_eager":False,"compilation_mode":"VLLM_COMPILE","backend":"inductor","cudagraph_mode":"NONE","capture_replay_count":0},
              "aot_pre_warmup":{"path":str(EXPECTED_AOT),"content_sha256":EXPECTED_AOT_SHA,"file_count":aot["file_count"],
                                "model_pickle_sha256":binding["model_sha256"],"embedded_qwen2_source_sha256":PINNED_QWEN2_SHA,
                                "path_stage":"PINNED_AOT_HASH_ROOT_DERIVED_FROM_ENV_CONFIG_MODEL_FACTORS"},
              "after_warmup_final":{"path":str(EXPECTED_FINAL),"content_sha256":EXPECTED_FINAL_SHA,
                                    "compiled_qwen2model_required":True,"graph_capture_replay_required":0,
                                    "attention":"FlashAttentionImpl","linear":"UnquantizedLinearMethod"},
              "execution":{"fresh_process":True,"warmups":2,"second_warmup":"CORRECTNESS_CANARY_NOT_SCIENCE","formal_samples":5,
                           "no_result_directed_repeat":True},
              "timing_endpoint":"STAGEA_V1_OBSERVER_OFF_REQUEST_CUDA_EVENT_PAIR_UNCHANGED",
              "correctness_tolerance":{"atol":0.05,"rtol":0.01,"tokens":"exact","row_mapping":"exact"},
              "gpu_budget":{"arm_seconds_cap":60,"lock_wait_seconds_cap":600},"gpu":{"uuid":"GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"},
              "stop_if_after_warmup_not_final":True,"no_cache_clear_recompile_env_or_source_change":True,
              "automatic_next_goal":False,"code_sha256":code_sha}
    save(PACK/"CONTINUATION_PREEXEC_CONTRACT.json",contract)
    (PACK/"CONTINUATION_PREEXEC.md").write_text("# MP03_B surgical continuation PREEXEC\n\nOnly MP03_B may run. The original PREEXEC and PARTIAL result commits remain immutable; MP02_A, MP02_B and MP03_A are referenced by SHA and will not be run. The sole gate change is pre-warmup AOT path/content/source binding followed by strict post-warmup equality to the 9122 final MP03_B cache. All model, input, runtime, Mode B compile/no-graph identity, request CUDA Event boundary, two warmups, five formal samples, correctness tolerance and DQ2 formulas are unchanged. An AOT cache hit may prevent convergence; if the accepted final path is not reached after warmup, STOP before formal. No cache repair or policy revision is authorized.\n")
    save(PACK/"PREEXEC_TESTS.json",{"status":"PASS_CPU_ONLY","checks":checks,"lifecycle_positive_negative_fixtures":"PASS",
                                    "aot_source_binding":binding["status"],"gpu_used":False})
    (PACK/"README.md").write_text("# MP03_B continuation PREEXEC\n\nRead `CACHE_PATH_LIFECYCLE_ROOT_CAUSE.md`, then `CONTINUATION_PREEXEC_CONTRACT.json`. This CPU-only freeze adds no GPU result. It preserves the original PARTIAL evidence and limits new execution to one fresh MP03_B process.\n")
    files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"status":"CONTINUATION_PREEXEC_FROZEN","files":len(files),"gpu_used":False}))

if __name__=="__main__":build()
