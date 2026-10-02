#!/usr/bin/env python3
"""Read-only 164-side raw manifest verifier; standard library only."""
import json
import hashlib
import sys
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def verify(root):
    entries=[]
    for line in (root/"RAW_SHA256SUMS").read_text().splitlines():
        digest,name=line.split("  ",1);p=root/name
        entries.append({"relative_path":name,"sha256":digest,"actual_sha256":sha(p),"size_bytes":p.stat().st_size})
    actual={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name!="RAW_SHA256SUMS"}
    passed=actual=={x["relative_path"] for x in entries} and all(x["sha256"]==x["actual_sha256"] for x in entries)
    return {"status":"PASS" if passed else "FAIL","manifest_sha256":sha(root/"RAW_SHA256SUMS"),"file_count":len(entries),"files":entries}

if __name__=="__main__":
    result=verify(Path(sys.argv[1]))
    print(json.dumps(result,sort_keys=True))
    if result["status"]!="PASS":raise SystemExit(2)
