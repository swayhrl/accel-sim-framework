#!/usr/bin/env python3
"""CPU-only evidence closeout for compiled artifact attribution feasibility."""
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"
PRIOR=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1"
OBSERVER=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1"
VLLM_REPO=Path("/data/c16/runtime_environment_audit_v1/source/vllm-v0.30.0")
VLLM_INSTALLED=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/lib/python3.12/site-packages/vllm")

def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def git(repo,*args):return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def save(name,value):(PACK/name).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def main():
    authority=json.loads((PACK/"COMPILE_CACHE_AUTHORITY.json").read_text())
    provenance=json.loads((PACK/"PROVENANCE_ANALYSIS.json").read_text())
    with (PACK/"ARTIFACT_INVENTORY.tsv").open(newline="") as f:
        inventory=list(csv.DictReader(f,delimiter="\t"))
    with (PACK/"KERNEL_TO_SEMANTIC_FAMILY.tsv").open(newline="") as f:
        kernels=list(csv.DictReader(f,delimiter="\t"))
    assert all(x["content_identity_matches_9122"] and x["raw_runtime_sha_and_config_match_9122_git_receipts"] for x in authority["roots"])
    assert provenance["unique_layer_semantic_family_pairs"]=={"MP02":144,"MP03":144}
    assert provenance["runtime_kernel_rows"]==96 and provenance["direct_family_only_rows"]==1 and provenance["unresolved_rows"]==95
    assert len(inventory)==24 and set(x["status"] for x in inventory)<={"PRESENT","ABSENT","UNREADABLE"}
    assert len(kernels)==96
    source=subprocess.check_output(["git","-C",str(VLLM_REPO),"show","ced6857afa0ea7b2e3f0846a62e1394e90f15607:vllm/model_executor/models/qwen2.py"])
    installed=VLLM_INSTALLED/"model_executor/models/qwen2.py"
    vllm_source={"commit":"ced6857afa0ea7b2e3f0846a62e1394e90f15607",
                 "git_object_available":git(VLLM_REPO,"cat-file","-t","ced6857afa0ea7b2e3f0846a62e1394e90f15607")=="commit",
                 "pinned_qwen2_git_sha256":sha_bytes(source),
                 "installed_qwen2_sha256":sha(installed),
                 "installed_qwen2_matches_pinned":sha_bytes(source)==sha(installed),
                 "installed_compilation_py_sha256":sha(VLLM_INSTALLED/"config/compilation.py")}
    save("SOURCE_AUTHORITY.json",{
        "mode_b_correctness_commit":"9122fac5c50dbf19706636fc03978a356ffd800f",
        "mode_b_correctness_tree":git(ROOT,"rev-parse","9122fac5c50dbf19706636fc03978a356ffd800f^{tree}"),
        "observer_failure_commit":"c48331a9ea5a3f381741aad4bae91dfb0eefc2c2",
        "observer_failure_tree":git(ROOT,"rev-parse","c48331a9ea5a3f381741aad4bae91dfb0eefc2c2^{tree}"),
        "vllm_source":vllm_source,
        "cache_read_only":True,"model_not_loaded":True})
    mp03=next(x for x in authority["roots"] if x["point"]=="MP03" and x["mode"]=="B")
    factors_path=Path(mp03["cache_path"])/"cache_key_factors.json"
    factors=json.loads(factors_path.read_text())
    save("CACHE_KEY_FACTORS_SUMMARY.json",{
        "point":"MP03","mode":"B","recorded_cache_key":mp03["cache_key"],
        "factors_path":str(factors_path),"factors_sha256":sha(factors_path),
        "code_hash":factors.get("code_hash"),"compiler_hash":factors.get("compiler_hash"),
        "config_hash":factors.get("config_hash"),"env_field_count":len(factors.get("env",{})),
        "compile_cache_save_format":factors.get("env",{}).get("VLLM_COMPILE_CACHE_SAVE_FORMAT"),
        "module_path_to_kernel_mapping_in_manifest":False})
    counts=Counter((x["point"],x["direct_provenance_status"]) for x in kernels)
    summary=[{"point":point,"status":status,"count":count} for (point,status),count in sorted(counts.items())]
    c483_inventory=json.loads((OBSERVER/"KERNEL_INVENTORY_STATUS.json").read_text())
    save("RUNTIME_INVENTORY_CROSSCHECK.json",{
        "source":"9122 BACKEND_KERNEL_IDENTITY.tsv, Mode B names only; no duration consumed",
        "mp02_distinct_runtime_names":sum(x["point"]=="MP02" for x in kernels),
        "mp03_distinct_runtime_names":sum(x["point"]=="MP03" for x in kernels),
        "mp02_generated_symbol_exact_matches":provenance["mp02_generated_symbol_matches"],
        "point_status_counts":summary,"observer_failure_inventory":c483_inventory,
        "artifact_generated_identity_full_closure":False,"duration_used_for_science":False})
    (PACK/"LAYER_STEP_IDENTIFIABILITY.md").write_text("""# Layer and decode-step identifiability

The exact 9122 cache roots still match their original per-file content identities. The MP02 B AOT pickle safely exposes a serialized FX GraphModule and embedded Inductor output-code sources; MP03 B has a readable `computation_graph.py`. Across each point, FX source contains all 36 layer indices and 144 unique `(layer, target family)` pairs. This identifies static graph nodes and their parameter paths.

Runtime evidence from 9122 is a distinct-name kernel inventory. It contains no per-launch callsite IDs, per-request kernel sequence, layer ordinal, or D0-D31 step tag. The MP02 B output code embeds six generated Triton symbols that match runtime names; only one has a direct single-target-family join. External cuBLAS/CUTLASS GEMM/GEMV names can serve attention QKV/O, gate/up, or down projections, and the recorded names do not identify which `extern_kernels.mm/addmm` call produced an instance. MP03 B's exact cache path has no point-bound generated output code at all. Other global cache directories cannot be assigned to this run by resemblance.

The AOT output code describes static call order for a graph and FX paths identify layers, but this does not recover the actual runtime instance-to-layer or repeated-forward-to-step mapping. Decode may reuse one dynamic compiled graph and the same kernel symbols across layers and D1-D31. The prior Mode B receipt does not retain ordered per-instance launch correlation. Therefore no `LEVEL_2_EXACT` claim is supported. A full `LEVEL_1_FAMILY_ONLY` claim is also unsupported because projection and external attention kernels remain unresolved.\n""")
    (PACK/"DQ4A_IDENTIFIABILITY.md").write_text("""# DQ4a compiled-path producer→consumer boundary

The FX graphs preserve a static dependency chain such as layer gate/up linear → SiLU/slice/multiply → down linear, and source-node comments preserve pieces of Inductor's generated call order. This proves a *static graph relationship*, not the observed runtime producer→consumer boundary for each layer and decode step.

The 9122 runtime inventory retains kernel names without launch instance order or callsite correlation. Generic external GEMM kernels are shared by several projection roles, generated symbols can repeat across all 36 layers and 32 forwards, and combo/fused kernels can remove intermediate launch boundaries. No hook-free artifact here uniquely identifies where a particular runtime producer ended and its consumer began.

Decision: `DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED`. No duration is allocated by operation count or theoretical FLOPs.\n""")
    reasons=[
        "9122 exact cache bytes remain available, so artifact authority itself is not unavailable",
        "FX node-to-layer/module provenance exists, but only 1 of 96 Mode B distinct runtime kernel names has a direct single-target-family join",
        "generic external GEMM/GEMV kernels lack launch-to-projection-call correlation; MP03 B lacks point-bound generated output code",
        "runtime inventory contains no kernel instance/layer/step identity; static graph order cannot reconstruct D0-D31 boundaries",
        "fused/combo and boundary kernels cannot be apportioned among families from these artifacts",
    ]
    attribution={"goal":"C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1",
        "authority_level":"LEVEL_0_UNRESOLVED","decision":"COMPILED_ATTRIBUTION_LEVEL_0_UNRESOLVED",
        "reasons":reasons,"dq4a":"DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED",
        "fusion_policy":"MULTI_FAMILY_FUSED kept joint or unsplittable; no arbitrary timing split",
        "gpu_used":False,"gpu_lock_acquired":False,"model_loaded":False,
        "torch_vllm_imported":False,"cache_modified":False,"duration_science_claim":False}
    save("ATTRIBUTION_AUTHORITY_DECISION.json",attribution)
    before={"source":"initial task-start nvidia-smi query","uuid":"GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59",
            "name":"NVIDIA GeForce RTX 4080","memory_used_mib":35,"compute_processes":[]}
    gpu=subprocess.check_output(["nvidia-smi","--query-gpu=uuid,name,memory.used","--format=csv,noheader,nounits"],text=True).strip().split(",")
    processes=subprocess.check_output(["nvidia-smi","--query-compute-apps=pid,process_name","--format=csv,noheader"],text=True).strip()
    after={"source":"final task nvidia-smi query","uuid":gpu[0].strip(),"name":gpu[1].strip(),
           "memory_used_mib":int(gpu[2].strip()),"compute_processes":processes.splitlines() if processes else []}
    assert before["uuid"]==after["uuid"] and not after["compute_processes"]
    save("GPU_NONUSE_RECEIPT.json",{"before":before,"after":after,"new_compute_processes_observed":False,
                                    "gpu_used":False,"gpu_lock_acquired":False,"model_loaded":False,
                                    "cuda_initialized":False,"nsys_ncu_nvbit_sass_accelsim_executed":False})
    save("FINAL_DECISION.json",{"goal":attribution["goal"],"decision":attribution["decision"],
                                 "authority_level":"LEVEL_0_UNRESOLVED","dq4a":attribution["dq4a"],
                                 "gpu_used":False,"automatic_next_goal":False,"stop":True})
    (PACK/"OPEN_ISSUES.md").write_text("# Open issues\n\nA future, separately authorized runtime correlation source would be required to bind generic external GEMM/attention launch instances to FX callsites and layer/step boundaries. This CPU-only feasibility goal authorizes no capture or recompile.\n")
    (PACK/"IMPLEMENTATION_CHANGELOG.md").write_text("""# Implementation and provenance

The branch `hrl/c16-compiled-path-artifact-attribution-feasibility-109-v1` starts at the accepted Observer V2 failure commit `c48331a9ea5a3f381741aad4bae91dfb0eefc2c2`. Its earlier Mode B correctness authority is `9122fac5c50dbf19706636fc03978a356ffd800f`; the installed vLLM source matches `ced6857afa0ea7b2e3f0846a62e1394e90f15607` for the Qwen2 model file.

New stdlib-only analysis code under `util/vm_tlb/c16/compiled_path_artifact_attribution/` reads the pinned raw runtime JSON, cache file bytes and existing kernel-name inventory. `survey.py` verifies original and current cache identities; `pickle_scan.py` and `nested_scan.py` inspect pickle opcodes without deserializing; `provenance_map.py` joins FX/module paths, generated output-code comments and runtime names; `inventory.py` records explicit artifact presence; `validate.py` independently checks hashes, joins and decision gates; `closeout.py` emits this review pack. No runtime, model, cache or simulator source file was modified.

Review evidence begins at `README.md`; `ARTIFACT_FILE_INDEX.tsv` is the raw cache index by path/size/SHA. No large cache blob is committed. Git commit history for the branch remains the authoritative change log.\n""")
    (PACK/"README.md").write_text("""# Compiled-path artifact attribution feasibility on node 109

Decision: `COMPILED_ATTRIBUTION_LEVEL_0_UNRESOLVED`. DQ4a: `DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED`.

The 9122 Mode B correctness PASS and c483 Observer V2 identity failure are the upstream authorities. `COMPILE_CACHE_AUTHORITY.json` restores all four actual A/B cache keys/configurations from the 9122 raw runtime JSON and proves that every current cache root still matches its original content SHA. `ARTIFACT_FILE_INDEX.tsv` records 1,040 files by size and SHA. MP02 B has a pinned AOT pickle, generated Inductor output code and lowered Triton IR; MP03 B's recorded path has a readable FX graph and key factors but no point-bound generated output code.

Read `ARTIFACT_INVENTORY.tsv` for explicit PRESENT/ABSENT/UNREADABLE status. `FX_IR_PROVENANCE_MAP.tsv` records direct FX node→module/layer evidence for all 36 layers. Safe `pickletools` scans (`AOT_PICKLE_OPCODE_SCAN.json`, `AOT_NESTED_PROVENANCE_SCAN.json`) locate the embedded graph/output code without unpickling or importing torch. `OUTPUT_CODE_SOURCE_NODE_MAP.tsv` joins generated symbols to source-node comments; `KERNEL_TO_SEMANTIC_FAMILY.tsv` tests each of 96 existing Mode B runtime names against that provenance. Only the MP02 activation symbol has a direct family-only join; generic external projection kernels and MP03 B kernel instances are unresolved. `FUSION_AMBIGUITY.tsv` keeps combo/boundary work unsplit.

`LAYER_STEP_IDENTIFIABILITY.md` and `DQ4A_IDENTIFIABILITY.md` explain why static graph layer paths do not recover dynamic launch instance, layer and decode-step boundaries. `ATTRIBUTION_AUTHORITY_DECISION.json` records the conservative level. No kernel duration was used for a science claim.

The work was CPU/storage/source-only. No model load, torch/vLLM import, CUDA initialization, GPU lock, NSYS, NCU, NVBit, SASS or Accel-Sim was performed. `GPU_NONUSE_RECEIPT.json` records the task-start and final `nvidia-smi` checks. `IMPLEMENTATION_CHANGELOG.md` lists source anchors and changed files. `SHA256SUMS` covers this pack.\n""")
    from validate import validate
    validate()
    files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"status":"PASS","decision":attribution["decision"],"pack_files":len(files),"gpu_used":False}))

if __name__=="__main__":main()
