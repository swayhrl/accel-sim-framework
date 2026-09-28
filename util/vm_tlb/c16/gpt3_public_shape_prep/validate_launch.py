#!/usr/bin/env python3
"""Validate frozen W4 launches and inventory synthetic Dense launches from NSYS SQLite."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from contracts import canonical_tables


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--sqlite",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    expected={(row["point"],row["arm"]):row for row in canonical_tables()[1]}
    db=sqlite3.connect(args.sqlite)
    ranges=list(db.execute("select start,end,coalesce(text,(select value from StringIds where id=textId)) from NVTX_EVENTS where coalesce(text,(select value from StringIds where id=textId)) like 'C16_GPT3_LAUNCH_AUDIT_%' order by start"))
    kernels=list(db.execute("select k.start,k.end,s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,k.registersPerThread,k.staticSharedMemory,k.dynamicSharedMemory from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName order by k.start"))
    rows=[]; seen=set()
    for start,end,label in ranges:
        selected=[k for k in kernels if k[0]>=start and k[1]<=end]
        body=label.removeprefix("C16_GPT3_LAUNCH_AUDIT_")
        if body.startswith("DENSE_"):
            point=body.removeprefix("DENSE_"); seen.add(("DENSE",point))
            if not selected: raise RuntimeError(f"dense launch missing: {point}")
            for order,k in enumerate(selected):
                rows.append({"track":"DENSE","point":point,"arm":"NA","order":order,"kernel_kind":"VENDOR_DENSE","kernel_name":k[2],"grid":[k[3],k[4],k[5]],"block":[k[6],k[7],k[8]],"registers_per_thread":k[9],"static_shared_bytes":k[10],"dynamic_shared_bytes":k[11],"pass":True})
            continue
        point,arm=body.removeprefix("W4_").rsplit("_",1); seen.add(("W4",point,arm)); contract=expected[(point,arm)]
        expected_kernels=[("GEMM",contract["gemm_grid"],(32,2,1))]
        if arm=="A": expected_kernels.append(("REDUCTION",contract["reduction_grid"],(32,4,1)))
        if len(selected)!=len(expected_kernels): raise RuntimeError(f"W4 launch count mismatch: {point}/{arm}")
        for order,(k,want) in enumerate(zip(selected,expected_kernels)):
            kind="GEMM" if "gemm_forward" in k[2] else "REDUCTION" if "reduce_kernel" in k[2] else "OTHER"
            passed=kind==want[0] and k[3]==want[1] and (k[6],k[7],k[8])==want[2]
            row={"track":"W4","point":point,"arm":arm,"order":order,"kernel_kind":kind,"kernel_name":k[2],"grid":[k[3],k[4],k[5]],"block":[k[6],k[7],k[8]],"registers_per_thread":k[9],"static_shared_bytes":k[10],"dynamic_shared_bytes":k[11],"scratch_shape":contract["scratch_shape"],"scratch_bytes":contract["scratch_bytes"],"reduction_expected":contract["reduction_expected"],"pass":passed}
            rows.append(row)
            if not passed: raise RuntimeError(f"W4 launch contract failed: {row}")
    if len([x for x in seen if x[0]=="DENSE"])!=4 or len([x for x in seen if x[0]=="W4"])!=8:
        raise RuntimeError(f"launch range coverage incomplete: {seen}")
    args.output.write_text(json.dumps({"status":"PASS","range_count":len(ranges),"rows":rows},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS_LAUNCH_AUDIT","ranges":len(ranges),"kernels":len(rows)}))


if __name__=="__main__": main()
