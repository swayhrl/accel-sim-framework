#!/usr/bin/env python3
"""Deterministic CPU-only verifier of artifact attribution receipts."""
import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"

def read_json(name):return json.loads((PACK/name).read_text())
def read_tsv(name):
    with (PACK/name).open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def validate():
    authority=read_json("COMPILE_CACHE_AUTHORITY.json")
    provenance=read_json("PROVENANCE_ANALYSIS.json")
    decision=read_json("ATTRIBUTION_AUTHORITY_DECISION.json")
    final=read_json("FINAL_DECISION.json")
    gpu=read_json("GPU_NONUSE_RECEIPT.json")
    source=read_json("SOURCE_AUTHORITY.json")
    files=read_tsv("ARTIFACT_FILE_INDEX.tsv")
    fx=read_tsv("FX_IR_PROVENANCE_MAP.tsv")
    kernels=read_tsv("KERNEL_TO_SEMANTIC_FAMILY.tsv")
    inventory=read_tsv("ARTIFACT_INVENTORY.tsv")
    fusion=read_tsv("FUSION_AMBIGUITY.tsv")
    checks={
       "raw_runtime_authority_exact":all(x["raw_runtime_sha_and_config_match_9122_git_receipts"] for x in authority["roots"]),
       "all_four_cache_roots_unchanged":all(x["content_identity_matches_9122"] for x in authority["roots"]),
       "file_count_1040":len(files)==1040,
       "all_cache_file_hashes_exact":all(Path(x["cache_path"],x["relative_path"]).stat().st_size==int(x["size_bytes"]) and sha(Path(x["cache_path"],x["relative_path"]))==x["sha256"] for x in files),
       "fx_layer_family_pairs_144_each":all(len({(x["layer"],x["semantic_family"]) for x in fx if x["point"]==point})==144 for point in ("MP02","MP03")),
       "runtime_kernel_rows_96":len(kernels)==96 and sum(x["point"]=="MP02" for x in kernels)==49 and sum(x["point"]=="MP03" for x in kernels)==47,
       "direct_family_only_one":sum(x["direct_provenance_status"]=="DIRECT_FAMILY_ONLY" for x in kernels)==1,
       "unresolved_95":sum(x["semantic_family"]=="UNRESOLVED" for x in kernels)==95,
       "no_instance_layer_step_claims":all(x["layer_unique"]=="False" and x["step_unique"]=="False" for x in kernels),
       "inventory_status_allowed":len(inventory)==24 and all(x["status"] in ("PRESENT","ABSENT","UNREADABLE") for x in inventory),
       "fusion_unsplit":bool(fusion) and all("SPLIT" in x["allocation"] or "JOINT" in x["allocation"] or "UNSPLITTABLE" in x["allocation"] for x in fusion),
       "vllm_source_exact":source["vllm_source"]["installed_qwen2_matches_pinned"],
       "level_zero":decision["decision"]==final["decision"]=="COMPILED_ATTRIBUTION_LEVEL_0_UNRESOLVED",
       "dq4a_unresolved":decision["dq4a"]==final["dq4a"]=="DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED",
       "gpu_nonuse":gpu["gpu_used"] is False and gpu["gpu_lock_acquired"] is False and not gpu["before"]["compute_processes"] and not gpu["after"]["compute_processes"],
       "no_duration_science":decision["duration_science_claim"] is False,
    }
    for path in HERE.glob("*.py"):
        tree=ast.parse(path.read_text())
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports += [x.name for x in node.names]
            elif isinstance(node,ast.ImportFrom) and node.module:imports.append(node.module)
        checks[f"no_torch_vllm_import_{path.name}"]=not any(x=="torch" or x.startswith("torch.") or x=="vllm" or x.startswith("vllm.") for x in imports)
    result={"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"gpu_used":False,
            "cache_files_verified":len(files),"runtime_kernel_names_checked":len(kernels)}
    (PACK/"TESTS.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if result["status"]!="PASS":raise AssertionError([k for k,v in checks.items() if not v])
    return result

if __name__=="__main__":
    x=validate();print(json.dumps({"status":x["status"],"checks":len(x["checks"])}))
