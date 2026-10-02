#!/usr/bin/env python3
"""Durable 164 raw publish with per-file SHA and copy-back verification."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

DURABLE_PARENT=Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_dq2_native_recovery_109_v1")
COPYBACK_PARENT=Path("/data/c16/dq2_native_recovery_v1/copyback_verify")

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def verify(root):
    entries=[]
    for line in (root/"RAW_SHA256SUMS").read_text().splitlines():
        digest,name=line.split("  ",1)
        p=root/name
        entries.append({"relative_path":name,"sha256":digest,"actual_sha256":sha(p),"size_bytes":p.stat().st_size})
    actual={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name!="RAW_SHA256SUMS"}
    passed=actual=={x["relative_path"] for x in entries} and all(x["sha256"]==x["actual_sha256"] for x in entries)
    return {"status":"PASS" if passed else "FAIL","manifest_sha256":sha(root/"RAW_SHA256SUMS"),"file_count":len(entries),"files":entries}

def publish(raw,pack):
    run_id=raw.name
    if not re.fullmatch(r"[0-9]{8}T[0-9]{6}Z",run_id):raise ValueError("invalid RUN_ID")
    payload=sorted(p for p in raw.rglob("*") if p.is_file() and p.name!="RAW_SHA256SUMS")
    (raw/"RAW_SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(raw)}\n" for p in payload))
    local=verify(raw)
    if local["status"]!="PASS":raise RuntimeError("LOCAL_RAW_SHA_FAILURE")
    remote=DURABLE_PARENT/run_id
    subprocess.run(["ssh","hrl174new","mkdir","-p",str(remote)],check=True)
    subprocess.run(["scp","-r",str(raw)+"/.",f"hrl174new:{remote}/"],check=True)
    helper=Path(__file__).with_name("verify_raw.py")
    subprocess.run(["scp",str(helper),"hrl174new:/tmp/c16_dq2_verify_raw.py"],check=True)
    remote_receipt=json.loads(subprocess.check_output(["ssh","hrl174new","python3","/tmp/c16_dq2_verify_raw.py",str(remote)],text=True))
    if remote_receipt["status"]!="PASS" or remote_receipt["manifest_sha256"]!=local["manifest_sha256"]:raise RuntimeError("REMOTE_RAW_SHA_FAILURE")
    COPYBACK_PARENT.mkdir(parents=True,exist_ok=True)
    subprocess.run(["scp","-r",f"hrl174new:{remote}",str(COPYBACK_PARENT)],check=True)
    copyback=COPYBACK_PARENT/run_id
    copied=verify(copyback)
    if copied["status"]!="PASS" or copied["manifest_sha256"]!=local["manifest_sha256"]:raise RuntimeError("COPYBACK_RAW_SHA_FAILURE")
    receipt={"status":"PASS_DURABLE_PUBLISH_AND_COPYBACK","local_raw":str(raw),"durable_host":"hrl174new",
             "durable_path":str(remote),"copyback_path":str(copyback),"local_verify":local,
             "remote_verify":remote_receipt,"copyback_verify":copied}
    pack.mkdir(parents=True,exist_ok=True)
    (pack/"PUBLISH_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    index=[]
    for item in local["files"]:
        name=item["relative_path"]
        index.append({"local_path":str(raw/name),"durable_path":str(remote/name),
                      "copyback_path":str(copyback/name),"size_bytes":item["size_bytes"],"sha256":item["sha256"]})
    (pack/"RAW_INDEX.json").write_text(json.dumps(index,indent=2,sort_keys=True)+"\n")
    return receipt
