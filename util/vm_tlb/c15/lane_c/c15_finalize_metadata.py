#!/usr/bin/env python3
"""Refresh Lane-C closeout metadata after a committed, read-only B audit."""
from __future__ import annotations
import csv, hashlib, json, os, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/"docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_c"
REPORT=ROOT/"docs/vm_tlb/codex_handoff/c15/lane_c/LATEST_REPORT.md"
PLANNING="9a755b14b01c5a77a6fc98c2547616e1c490e806"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def rows(p):
    with p.open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))

def tsv(p,fields,data):
    with tempfile.NamedTemporaryFile("w",newline="",dir=p.parent,prefix=f".{p.name}.",suffix=".tmp",delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(data);tmp=Path(f.name)
    os.replace(tmp,p)

def text(p,value):
    with tempfile.NamedTemporaryFile("w",dir=p.parent,prefix=f".{p.name}.",suffix=".tmp",delete=False) as f:f.write(value);tmp=Path(f.name)
    os.replace(tmp,p)

def main():
    note="B manifest 8963919d hash-verified; it is offline/header-only with no NATIVE_NEW metrics, so dynamic cross-model validation remains pending"
    status=rows(OUT/"STAGE_STATUS.tsv"); fields=list(status[0])
    for r in status:r["note"]=note
    tsv(OUT/"STAGE_STATUS.tsv",fields,status)
    ledger=rows(OUT/"COST_LEDGER.tsv"); lf=list(ledger[0])
    for r in ledger:
        if r["work_id"]=="C15-C-VALIDATE":
            r["bytes_written"]="NA";r["measured_or_estimated"]="MEASURED_RAW_BYTES_AND_WALL; OUTPUT_BYTES_UNALLOCATED_NOT_ZERO"
    tsv(OUT/"COST_LEDGER.tsv",lf,ledger)
    text(OUT/"FINAL_REPORT.md","""# C15 Lane C final report

Status: `C15_C_SAMPLING_VALIDATION_CAPABILITY_LIMITED_READY_FOR_REVIEW`. The 22-arm C12 zero-sampling conservation control passed using hash-verified historical raw logs; corrected C13 admitted only the ten EQ-gated mode=0 identities. No simulator replay, trace capture, GPU task, Core change, or protected-source write occurred.

The released primary is a phase/opaque-order cheap selector with seed 15001 and virtual budgets 8/12/24/48. It intentionally has explicit UNKNOWN operator/implementation/shape/dtype/KV/TP buckets. The historical operator/layer/page scan is an oracle only, never the primary selector. Historical C12/C13 outcomes are retrospective calibration/cross-config tests, not blind tests.

Scientific boundary: the cheap selector is `SAMPLER_NOT_QUALIFIED` for mechanism or causal conclusions; deterministic estimates have no fabricated confidence interval, and small or unresolved effects are `INCONCLUSIVE`. Existing compact scans support exact 64KiB page-set fingerprints, but not bytes, read/write/atomic, line-set, MRC, private-L1, or global-order claims. C14 cold micro comparisons remain confounded by explicit state/context non-equivalence.

Lane B commit `8963919d608d05713e2caa22965d8895c728bc92` was consumed read-only after manifest validation: all 21 payload hashes matched, but its declared state is `NO_NEW_NATIVE_GPU_RUN` and its catalog is header-only. No dynamic metric was imported; dynamic cross-model validation therefore remains pending a future committed native manifest.
""")
    text(REPORT,"""# C15 Lane C handoff

`planning_sha`/initial HEAD: `9a755b14b01c5a77a6fc98c2547616e1c490e806`.

C15 Lane C is capability-limited ready for review. The zero-sampling C12 control passed; the frozen cheap primary sampler is not qualified for mechanism claims. B's committed offline/header-only checkpoint was hash-verified but supplied no native dynamic metric, so no cross-model claim is made. See the Lane-C review pack README and FINAL_REPORT for receipts, costs, failure boundaries, and three future-only requests.
""")
    files=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="PUBLISH_MANIFEST.json": files.append({"path":p.name,"sha256":sha(p),"size_bytes":p.stat().st_size})
    head=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    manifest={"schema_version":"C15_LANE_C_PUBLISH_V1","planning_sha":PLANNING,"lane":"C","run_id":"C15_C_FROZEN_HISTORY_V1","producer_source_sha":head,"evidence_tier":"RETROSPECTIVE_CALIBRATION","metric_scope":"C12/C13 historical only; B manifest audit contains no NATIVE_NEW metric","capture_state":"NO_NEW_CAPTURE","status":"CAPABILITY_LIMITED_READY_FOR_REVIEW","evidence_note":note,"new_simulator_replay":0,"files":files,"dynamic_cross_model":"PENDING_COMMITTED_NATIVE_B_MANIFEST"}
    text(OUT/"PUBLISH_MANIFEST.json",json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(f"PASS C15 metadata refresh: {len(files)} files")
if __name__=="__main__":main()
