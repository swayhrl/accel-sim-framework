#!/usr/bin/env python3
"""CPU analyzer for the eventual locked producer outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path

from contracts import POINTS  # keeps this module CPU-only


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--raw",type=Path,required=True); parser.add_argument("--out",type=Path,required=True); args=parser.parse_args()
    qualification=json.loads((args.raw/"qualification.json").read_text())
    launch=json.loads((args.raw/"launch_audit.json").read_text())
    timing=json.loads((args.raw/"timing_samples.json").read_text())["samples"]
    if qualification["status"]!="PASS" or launch["status"]!="PASS": raise RuntimeError("producer qualification failed")
    summary=[]
    for track in ("DENSE","W4"):
        for point in [row["point"] for row in POINTS]:
            if track=="DENSE":
                values=[row["ms"] for row in timing if row["track"]==track and row["point"]==point]
                if len(values)!=50: raise RuntimeError(f"dense sample count: {point}")
                summary.append({"track":track,"point":point,"cell":"WARM_ONLY","n":50,"min_ms":min(values),"median_ms":statistics.median(values),"max_ms":max(values),"mean_ms":statistics.mean(values),"cv":statistics.pstdev(values)/statistics.mean(values)})
            else:
                cells={}
                for cell in ("A_W","B_W","A_E","B_E"):
                    values=[row["ms"] for row in timing if row["track"]==track and row["point"]==point and row["cell"]==cell]
                    if len(values)!=50: raise RuntimeError(f"W4 sample count: {point}/{cell}")
                    cells[cell]=statistics.median(values)
                    summary.append({"track":track,"point":point,"cell":cell,"n":50,"min_ms":min(values),"median_ms":cells[cell],"max_ms":max(values),"mean_ms":statistics.mean(values),"cv":statistics.pstdev(values)/statistics.mean(values)})
                summary.append({"track":"W4_DERIVED","point":point,"cell":"GAINS","gain_W":1-cells["B_W"]/cells["A_W"],"gain_E":1-cells["B_E"]/cells["A_E"],"state_interaction":(1-cells["B_W"]/cells["A_W"])-(1-cells["B_E"]/cells["A_E"])})
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"TIMING_SUMMARY.json").write_text(json.dumps({"status":"PASS","rows":summary},indent=2,sort_keys=True)+"\n")
    index=[]
    for path in sorted(args.raw.iterdir()):
        if path.is_file(): index.append({"artifact":path.name,"bytes":path.stat().st_size,"sha256":sha(path)})
    (args.out/"RAW_INDEX.json").write_text(json.dumps(index,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS_ANALYSIS","summary_rows":len(summary),"raw_files":len(index)}))


if __name__=="__main__": main()
