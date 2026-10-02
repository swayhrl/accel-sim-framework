#!/usr/bin/env python3
"""Read-only stdlib survey of the exact 9122 compile cache identities."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"
PRIOR=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def write_json(name,value):
    PACK.mkdir(parents=True,exist_ok=True)
    (PACK/name).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def main():
    prior=json.loads((PRIOR/"COMPILE_CACHE_IDENTITY.json").read_text())
    with (PRIOR/"MODE_RUNTIME_IDENTITY.tsv").open(newline="") as f:
        runtime={(r["point"],r["mode"]):r for r in csv.DictReader(f,delimiter="\t")}
    with (PRIOR/"RAW_INDEX.tsv").open(newline="") as f:
        raw_index={r["local_path"]:r for r in csv.DictReader(f,delimiter="\t")}
    final=json.loads((PRIOR/"FINAL_DECISION.json").read_text())
    raw_root=Path(final["raw_local"])
    index=[];roots=[]
    for entry in prior:
        point,mode=entry["point"],entry["mode"]
        root=Path(entry["path"])
        files=sorted((p for p in root.rglob("*") if p.is_file()),key=lambda p:str(p.relative_to(root))) if root.is_dir() else []
        triples=[]
        for p in files:
            relative=str(p.relative_to(root))
            size=p.stat().st_size
            digest=sha(p)
            triples.append((relative,size,digest))
            index.append({"point":point,"mode":mode,"cache_path":str(root),"relative_path":relative,
                          "size_bytes":size,"sha256":digest,"suffix":p.suffix or "NO_SUFFIX"})
        actual_identity=hashlib.sha256(json.dumps(triples,separators=(",", ":")).encode()).hexdigest() if root.is_dir() else None
        suffixes=dict(sorted(Counter(p.suffix or "NO_SUFFIX" for p in files).items()))
        landmarks={name:{"path":str(root/name),"status":"PRESENT" if (root/name).is_file() else "ABSENT",
                         "sha256":sha(root/name) if (root/name).is_file() else None}
                   for name in ("rank_0_0/model","computation_graph.py","cache_key_factors.json",
                                "rank_0_0/backbone/computation_graph.py","rank_0_0/backbone/cache_key_factors.json")}
        run=runtime[(point,mode)]
        raw_file=raw_root/f"{point}_{mode}.json"
        raw_payload=json.loads(raw_file.read_text())
        raw_sha=sha(raw_file)
        raw_match=(raw_sha==raw_index[str(raw_file)]["sha256"] and
                   raw_payload["runtime_identity"]["compile_cache_path"]==str(root) and
                   raw_payload["config"]["compilation_mode"]==run["compilation_mode"] and
                   raw_payload["config"]["cudagraph_mode"]==run["cudagraph_mode"] and
                   raw_payload["config"]["backend"]==run["backend"])
        roots.append({"point":point,"mode":mode,"cache_path":str(root),"cache_key":root.name if len(root.name)==64 else root.parts[-3] if len(root.parts)>=3 else root.name,
                      "raw_runtime_json_path":str(raw_file),"raw_runtime_json_sha256":raw_sha,
                      "raw_runtime_sha_and_config_match_9122_git_receipts":raw_match,
                      "root_status":"PRESENT" if root.is_dir() else "ABSENT",
                      "file_count_at_9122":entry["file_count"],"file_count_now":len(files),
                      "total_bytes_at_9122":entry["total_bytes"],"total_bytes_now":sum(p.stat().st_size for p in files),
                      "content_identity_sha256_at_9122":entry["content_identity_sha256"],
                      "content_identity_sha256_now":actual_identity,
                      "content_identity_matches_9122":actual_identity==entry["content_identity_sha256"],
                      "preexisted_before_9122_mode_load":entry["preexisted_before_mode_load"],
                      "effective_compilation_mode":run["compilation_mode"],"effective_cudagraph_mode":run["cudagraph_mode"],
                      "effective_backend":run["backend"],"enforce_eager":run["enforce_eager"],
                      "compiled_model":run["compiled_model"],"compiled_submodules":entry["compiled_submodules"],
                      "suffix_counts":suffixes,"landmarks":landmarks})
    extra_roots=[]
    for path in (Path.home()/".cache/torch/inductor",Path.home()/".cache/torch/torchinductor",
                 Path.home()/".cache/vllm/torch_compile_cache"):
        extra_roots.append({"path":str(path),"status":"PRESENT" if path.is_dir() else "ABSENT"})
    result={"authority_mode_canary_commit":"9122fac5c50dbf19706636fc03978a356ffd800f",
            "observer_failure_commit":"c48331a9ea5a3f381741aad4bae91dfb0eefc2c2",
            "read_only":True,"gpu_used":False,"roots":roots,"other_cache_roots":extra_roots}
    write_json("COMPILE_CACHE_AUTHORITY.json",result)
    with (PACK/"ARTIFACT_FILE_INDEX.tsv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["point","mode","cache_path","relative_path","size_bytes","sha256","suffix"],delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(index)
    print(json.dumps({"status":"PASS","roots":len(roots),"files":len(index),"identity_matches":[(x["point"],x["mode"],x["content_identity_matches_9122"]) for x in roots]}))

if __name__=="__main__":main()
