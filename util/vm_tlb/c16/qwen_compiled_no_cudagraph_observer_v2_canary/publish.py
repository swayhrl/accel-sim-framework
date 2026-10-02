#!/usr/bin/env python3
"""Publish bounded raw payload to 164 and verify every file plus copy-back."""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

from verify_tree import sha, verify

DURABLE_PARENT=Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_qwen_compiled_no_cudagraph_observer_v2_canary_109_v1")
COPYBACK_PARENT=Path("/data/c16/qwen_compiled_no_cudagraph_observer_v2_canary_v1/copyback_verify")

def publish(raw,pack):
    run_id=raw.name
    if not re.fullmatch(r"[0-9]{8}T[0-9]{6}Z",run_id):
        raise ValueError("unexpected raw run ID")
    files=sorted(p for p in raw.rglob("*") if p.is_file() and p.name!="RAW_SHA256SUMS")
    (raw/"RAW_SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(raw)}\n" for p in files))
    local=verify(raw)
    if local["status"]!="PASS":raise RuntimeError("LOCAL_RAW_SHA_FAILURE")
    remote=DURABLE_PARENT/run_id
    subprocess.run(["ssh","hrl174new","mkdir","-p",str(remote)],check=True)
    subprocess.run(["scp","-r",str(raw)+"/.",f"hrl174new:{remote}/"],check=True)
    helper=Path(__file__).with_name("verify_tree.py")
    subprocess.run(["scp",str(helper),"hrl174new:/tmp/c16_qwen_obs_v2_verify_tree.py"],check=True)
    remote_result=json.loads(subprocess.check_output(["ssh","hrl174new","python3","/tmp/c16_qwen_obs_v2_verify_tree.py",str(remote)],text=True))
    if remote_result["status"]!="PASS" or remote_result["manifest_sha256"]!=local["manifest_sha256"]:
        raise RuntimeError("REMOTE_RAW_SHA_FAILURE")
    COPYBACK_PARENT.mkdir(parents=True,exist_ok=True)
    subprocess.run(["scp","-r",f"hrl174new:{remote}",str(COPYBACK_PARENT)],check=True)
    copyback=COPYBACK_PARENT/run_id
    copy_result=verify(copyback)
    if copy_result["status"]!="PASS" or copy_result["manifest_sha256"]!=local["manifest_sha256"]:
        raise RuntimeError("COPYBACK_RAW_SHA_FAILURE")
    pack.mkdir(parents=True,exist_ok=True)
    receipt={"status":"PASS_DURABLE_PUBLISH_AND_COPYBACK","raw_local":str(raw),"durable_host":"hrl174new",
             "durable_path":str(remote),"copyback_path":str(copyback),"manifest_sha256":local["manifest_sha256"],
             "file_count":local["file_count"],"remote_verify":remote_result,"copyback_verify":copy_result}
    (pack/"PUBLISH_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    with (pack/"RAW_INDEX.tsv").open("w",newline="") as f:
        writer=csv.writer(f,delimiter="\t",lineterminator="\n")
        writer.writerow(["local_path","durable_path","copyback_path","size_bytes","sha256"])
        for row in local["files"]:
            name=row["relative_path"]
            writer.writerow([str(raw/name),str(remote/name),str(copyback/name),row["size_bytes"],row["expected_sha256"]])
    return receipt

if __name__=="__main__":
    result=publish(Path(sys.argv[1]),Path(sys.argv[2]))
    print(json.dumps({"status":result["status"],"file_count":result["file_count"]}))
