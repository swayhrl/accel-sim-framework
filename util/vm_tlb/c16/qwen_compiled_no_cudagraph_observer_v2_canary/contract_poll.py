#!/usr/bin/env python3
"""CPU-only Lane6 branch poll, at 300-second intervals for at most 180 minutes."""
import csv
import json
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_PREP_109_V1"
REF="refs/heads/hrl/c16-qwen-compiled-no-cudagraph-observer-v2-contract-174new-v1"
INTERVAL=300.0

def stamp():return datetime.now(timezone.utc).isoformat()

def check():
    output=subprocess.check_output(["git","-C",str(ROOT),"ls-remote","--heads","origin",REF],text=True).strip()
    if not output:return None
    sha,ref=output.split("\t")
    if ref!=REF:raise RuntimeError("unexpected remote ref")
    subprocess.run(["git","-C",str(ROOT),"fetch","origin",REF],check=True)
    actual=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","FETCH_HEAD"],text=True).strip()
    if actual!=sha:raise RuntimeError("fetch-back commit mismatch")
    return sha

def main():
    deadline=float(sys.argv[1])
    PACK.mkdir(parents=True,exist_ok=True)
    log=PACK/"CONTRACT_POLL.tsv"
    if not log.exists():log.write_text("checked_utc\tstatus\tremote_commit\n")
    next_check=time.monotonic()
    while time.time()<deadline:
        if time.monotonic()<next_check:
            time.sleep(min(next_check-time.monotonic(),5))
            continue
        try:
            sha=check()
            status="FOUND" if sha else "ABSENT"
        except Exception as e:
            sha=""
            status=f"FETCH_ERROR:{type(e).__name__}:{e}"
        with log.open("a",newline="") as f:
            writer=csv.writer(f,delimiter="\t",lineterminator="\n")
            writer.writerow([stamp(),status,sha or ""])
        if sha:
            (PACK/"CONTRACT_AVAILABLE.json").write_text(json.dumps({"status":"FOUND","commit":sha,"ref":REF,"checked_utc":stamp()},indent=2,sort_keys=True)+"\n")
            return
        next_check+=INTERVAL
    (PACK/"CONTRACT_POLL_TIMEOUT.json").write_text(json.dumps({"status":"TIMEOUT_180_MINUTES","ref":REF,"checked_utc":stamp()},indent=2,sort_keys=True)+"\n")

if __name__=="__main__":main()
