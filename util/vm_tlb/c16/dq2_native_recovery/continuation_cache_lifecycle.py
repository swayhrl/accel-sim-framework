#!/usr/bin/env python3
"""Read-only two-stage cache-path identity helpers for MP03_B continuation."""
import hashlib
import json
import pickletools
from pathlib import Path

EXPECTED_AOT=Path("/home/huangrulin/.cache/vllm/torch_compile_cache/torch_aot_compile/e3e9e809f85090188765b47bd34adcf7546a9bd28e1927888155ece5008170cc")
EXPECTED_FINAL=Path("/home/huangrulin/.cache/vllm/torch_compile_cache/c97581f1bb/rank_0_0/backbone")
PINNED_QWEN2_SHA="eb2f0eeb13c57a28bbc06bc64afff18cd8865f89fbe9ff2a3cf3a896f037cfe9"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def tree_identity(root):
    root=Path(root)
    files=sorted((p for p in root.rglob("*") if p.is_file()),key=lambda p:str(p.relative_to(root))) if root.is_dir() else []
    triples=[(str(p.relative_to(root)),p.stat().st_size,sha(p)) for p in files]
    identity=hashlib.sha256(json.dumps(triples,separators=(",", ":")).encode()).hexdigest() if root.is_dir() else None
    return {"path":str(root),"exists":root.is_dir(),"content_identity_sha256":identity,
            "file_count":len(files),"total_bytes":sum(x[1] for x in triples),
            "files":[{"relative_path":name,"size_bytes":size,"sha256":digest} for name,size,digest in triples]}

def aot_source_binding(root):
    model=Path(root)/"rank_0_0/model"
    if not model.is_file():return {"status":"ABSENT_MODEL_ARTIFACT","model_path":str(model)}
    data=model.read_bytes();matches=[];qwen_model_marker=False
    for op,arg,pos in pickletools.genops(data):
        if isinstance(arg,(str,bytes)):
            payload=arg.encode() if isinstance(arg,str) else arg
            digest=hashlib.sha256(payload).hexdigest()
            if digest==PINNED_QWEN2_SHA:matches.append(pos)
            if payload==b"Qwen2Model.forward":qwen_model_marker=True
    return {"status":"PASS" if matches and qwen_model_marker else "SOURCE_BINDING_UNRESOLVED",
            "model_path":str(model),"model_sha256":hashlib.sha256(data).hexdigest(),
            "embedded_pinned_qwen2_source_sha256":PINNED_QWEN2_SHA if matches else None,
            "embedded_source_pickle_positions":matches,"qwen2model_forward_marker":qwen_model_marker,
            "parser":"pickletools.genops only; no pickle.load or torch/vLLM import"}

def pre_warmup_gate(actual_path,expected_content_sha):
    actual=Path(actual_path)
    root=tree_identity(actual)
    binding=aot_source_binding(actual)
    passed=actual==EXPECTED_AOT and str(actual).startswith(str(EXPECTED_AOT.parent)+"/") and root["content_identity_sha256"]==expected_content_sha and binding["status"]=="PASS"
    return {"status":"PASS" if passed else "PRE_WARMUP_AOT_IDENTITY_FAIL",
            "actual_path":str(actual),"expected_path":str(EXPECTED_AOT),
            "actual_content_sha256":root["content_identity_sha256"],"expected_content_sha256":expected_content_sha,
            "file_count":root["file_count"],"source_binding":binding}

def after_warmup_gate(actual_path,expected_final_sha):
    actual=Path(actual_path)
    root=tree_identity(EXPECTED_FINAL)
    passed=actual==EXPECTED_FINAL and root["content_identity_sha256"]==expected_final_sha
    return {"status":"PASS" if passed else "AFTER_WARMUP_FINAL_IDENTITY_FAIL",
            "actual_path":str(actual),"expected_path":str(EXPECTED_FINAL),
            "accepted_final_content_sha256":root["content_identity_sha256"],
            "expected_final_content_sha256":expected_final_sha,"accepted_final_file_count":root["file_count"]}

if __name__=="__main__":
    aot=tree_identity(EXPECTED_AOT);binding=aot_source_binding(EXPECTED_AOT)
    print(json.dumps({"aot_sha256":aot["content_identity_sha256"],"file_count":aot["file_count"],
                      "source_binding":binding["status"],"model_sha256":binding.get("model_sha256")}))
