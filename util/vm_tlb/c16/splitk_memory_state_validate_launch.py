#!/usr/bin/env python3
"""Validate the pre-timing nsys launch audit against the accepted split8/split1 contract."""
import argparse
import json
import sqlite3
from pathlib import Path

EXPECTED = {
    ("up_proj","A"): [("GEMM",18944,(32,2,1)),("REDUCTION",9472,(32,4,1))],
    ("up_proj","B"): [("GEMM",2368,(32,2,1))],
    ("down_proj","A"): [("GEMM",3584,(32,2,1)),("REDUCTION",1792,(32,4,1))],
    ("down_proj","B"): [("GEMM",448,(32,2,1))],
}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--sqlite',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    db=sqlite3.connect(a.sqlite)
    ranges=list(db.execute("select start,end,coalesce(text,(select value from StringIds where id=textId)) from NVTX_EVENTS where coalesce(text,(select value from StringIds where id=textId)) like 'C16_SPLITK_STATE_AUDIT_%' order by start"))
    kernels=list(db.execute("select k.start,k.end,s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,k.registersPerThread,k.staticSharedMemory,k.dynamicSharedMemory from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName order by k.start"))
    rows=[]
    for start,end,label in ranges:
        body=label.removeprefix('C16_SPLITK_STATE_AUDIT_'); operator,arm=body.rsplit('_',1)
        selected=[k for k in kernels if k[0]>=start and k[1]<=end]
        expected=EXPECTED[(operator,arm)]
        if len(selected)!=len(expected): raise RuntimeError(f'LAUNCH_COUNT_FAIL {operator} {arm} {len(selected)}/{len(expected)}')
        for order,(k,e) in enumerate(zip(selected,expected)):
            kind='GEMM' if 'gemm_forward' in k[2] else 'REDUCTION' if 'reduce_kernel' in k[2] else 'OTHER'
            passed=kind==e[0] and k[3]==e[1] and (k[6],k[7],k[8])==e[2]
            row={"operator":operator,"arm":arm,"order":order,"kernel_kind":kind,"kernel_name":k[2],"grid":[k[3],k[4],k[5]],"block":[k[6],k[7],k[8]],"registers_per_thread":k[9],"static_shared_bytes":k[10],"dynamic_shared_bytes":k[11],"pass":passed}
            rows.append(row)
            if not passed: raise RuntimeError(f'LAUNCH_CONTRACT_FAIL {row}')
    if len(ranges)!=4 or len(rows)!=6: raise RuntimeError(f'LAUNCH_AUDIT_INCOMPLETE ranges={len(ranges)} rows={len(rows)}')
    a.output.write_text(json.dumps({"status":"PASS","ranges":len(ranges),"rows":rows},indent=2,sort_keys=True)+'\n')
    print(json.dumps({"status":"PASS_LAUNCH_AUDIT","ranges":len(ranges),"kernel_rows":len(rows)}))


if __name__=='__main__': main()
