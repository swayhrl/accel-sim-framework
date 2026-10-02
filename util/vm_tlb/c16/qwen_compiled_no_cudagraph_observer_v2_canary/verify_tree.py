#!/usr/bin/env python3
"""Read-only per-file raw SHA verifier for node 109 or the 164 durable host."""
import hashlib
import json
import sys
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def verify(root):
    entries=[]
    for line in (root/"RAW_SHA256SUMS").read_text().splitlines():
        digest,name=line.split("  ",1)
        path=root/name
        entries.append({"relative_path":name,"expected_sha256":digest,"actual_sha256":sha(path),"size_bytes":path.stat().st_size})
    expected_names={x["relative_path"] for x in entries}
    actual_names={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name!="RAW_SHA256SUMS"}
    passed=expected_names==actual_names and all(x["expected_sha256"]==x["actual_sha256"] for x in entries)
    return {"status":"PASS" if passed else "FAIL","root":str(root),"file_count":len(entries),
            "manifest_sha256":sha(root/"RAW_SHA256SUMS"),"files":entries}

if __name__=="__main__":
    result=verify(Path(sys.argv[1]))
    print(json.dumps(result,sort_keys=True))
    if result["status"]!="PASS":raise SystemExit(2)
