#!/usr/bin/env python3
"""Read-only 9122-bound compile-cache content check before/after DQ2 GPU work."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
AUTH=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1/COMPILE_CACHE_IDENTITY.json"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def check(phase):
    expected=json.loads(AUTH.read_text())
    rows=[]
    for item in expected:
        root=Path(item["path"])
        files=sorted((p for p in root.rglob("*") if p.is_file()),key=lambda p:str(p.relative_to(root))) if root.is_dir() else []
        triples=[(str(p.relative_to(root)),p.stat().st_size,sha(p)) for p in files]
        identity=hashlib.sha256(json.dumps(triples,separators=(",", ":")).encode()).hexdigest() if root.is_dir() else None
        rows.append({"point":item["point"],"mode":item["mode"],"path":str(root),
                     "status":"PASS" if identity==item["content_identity_sha256"] else "CONTENT_DRIFT",
                     "expected_sha256":item["content_identity_sha256"],"actual_sha256":identity,
                     "expected_file_count":item["file_count"],"actual_file_count":len(files),
                     "expected_total_bytes":item["total_bytes"],"actual_total_bytes":sum(x[1] for x in triples),
                     "files":[{"relative_path":name,"size_bytes":size,"sha256":digest} for name,size,digest in triples]})
    return {"phase":phase,"status":"PASS" if all(x["status"]=="PASS" for x in rows) else "CONTENT_DRIFT",
            "authority_commit":"9122fac5c50dbf19706636fc03978a356ffd800f","read_only":True,"rows":rows}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--phase",choices=("BEFORE","AFTER"),required=True);p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();result=check(args.phase)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"phase":args.phase,"status":result["status"],"roots":len(result["rows"])}))
    if result["status"]!="PASS":raise SystemExit(2)
