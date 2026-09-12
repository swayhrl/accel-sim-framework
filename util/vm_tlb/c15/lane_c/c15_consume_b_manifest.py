#!/usr/bin/env python3
"""Hash-verify Lane B's committed publish checkpoint without consuming live data."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/"docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_c"
REV="8963919d608d05713e2caa22965d8895c728bc92"
BASE="docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_b"

def blob(path):
    return subprocess.check_output(["git","-C",str(ROOT),"show",f"{REV}:{path}"])

def main():
    began=time.time()
    manifest_bytes=blob(f"{BASE}/PUBLISH_MANIFEST.json"); manifest=json.loads(manifest_bytes)
    checked=[]; bytes_read=len(manifest_bytes)
    for item in manifest["files"]:
        content=blob(f"{BASE}/{item['path']}"); bytes_read+=len(content); actual=hashlib.sha256(content).hexdigest()
        if actual!=item["sha256"]: raise SystemExit(f"hash mismatch: {item['path']}")
        checked.append(item["path"])
    eligible=(manifest.get("capture_state")!="NO_NEW_NATIVE_GPU_RUN")
    rows=[{"consumer_lane":"C","producer_lane":"B","producer_commit":REV,"manifest_path":f"{BASE}/PUBLISH_MANIFEST.json","manifest_sha256":hashlib.sha256(manifest_bytes).hexdigest(),"verified_file_count":len(checked),"capture_state":manifest.get("capture_state","NA"),"consumption":"NO_DYNAMIC_METRICS_CONSUMED","reason":"B published offline/header-only checkpoint; no NATIVE_NEW result exists","dynamic_cross_model_status":"PENDING" if not eligible else "REQUIRES_SEPARATE_ADMISSION"}]
    fields=list(rows[0]); path=OUT/"CONSUMED_INPUTS.tsv"
    with tempfile.NamedTemporaryFile("w",newline="",dir=path.parent,prefix=".CONSUMED_INPUTS.",suffix=".tmp",delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(rows); tmp=Path(f.name)
    os.replace(tmp,path)
    ledger=OUT/"COST_LEDGER.tsv"
    with ledger.open(newline="") as f: cost=list(csv.DictReader(f,delimiter="\t")); cost_fields=f.seek(0)  # keep source schema below
    fields=["work_id","parent_work_id","lane","stage_id","attempt","operation","start_utc","end_utc","wall_s","cpu_core_s","gpu_active_s","peak_rss_B","peak_vram_B","bytes_read","bytes_downloaded","bytes_written","warmup_s","retry_s","measured_or_estimated","result_status"]
    cost=[row for row in cost if row["work_id"]!="C15-C-CONSUME-B"]
    cost.append({"work_id":"C15-C-CONSUME-B","parent_work_id":"NA","lane":"C","stage_id":"C15-4.7","attempt":1,"operation":"read-only B committed manifest and payload hash verification","start_utc":"NA","end_utc":"NA","wall_s":f"{time.time()-began:.12g}","cpu_core_s":"NA","gpu_active_s":0,"peak_rss_B":"NA","peak_vram_B":0,"bytes_read":bytes_read,"bytes_downloaded":0,"bytes_written":path.stat().st_size,"warmup_s":0,"retry_s":0,"measured_or_estimated":"MEASURED_MANIFEST_BLOB_BYTES_AND_WALL","result_status":"CAPABILITY_LIMITED_NO_NATIVE_DYNAMIC_IMPORT"})
    with tempfile.NamedTemporaryFile("w",newline="",dir=ledger.parent,prefix=".COST_LEDGER.",suffix=".tmp",delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(cost); tmp=Path(f.name)
    os.replace(tmp,ledger)
    print(f"PASS B manifest hash verification: {len(checked)} files; dynamic import withheld")

if __name__=="__main__": main()
