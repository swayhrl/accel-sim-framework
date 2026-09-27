#!/usr/bin/env python3
import csv
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
DB = ROOT / 'raw/fastpath/r54_v1r1_fastpath.sqlite'
OUT = ROOT / 'receipts/R54_V1R1_KERNEL_STRATA.tsv'
con = sqlite3.connect(DB)

ranges = list(con.execute("""
select start,end,text from NVTX_EVENTS
where text like 'R54_V1R1_%' and end is not null
order by start
"""))

rows = []
for start, end, text in ranges:
    q = """
    select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,
           count(*),sum(k.end-k.start),min(k.end-k.start),max(k.end-k.start)
    from CUPTI_ACTIVITY_KIND_KERNEL k
    join StringIds s on s.id=k.demangledName
    where k.start>=? and k.end<=?
    group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ
    order by sum(k.end-k.start) desc
    """
    for name,gx,gy,gz,bx,by,bz,count,total,min_ns,max_ns in con.execute(q,(start,end)):
        lname=name.lower()
        target = any(x in lname for x in [
            'causal_conv1d', 'causal_conv1d_update', 'gated_delta', 'wy_fast',
            'chunk_local_cumsum', 'chunk_gated', 'fused_recurrent',
            'recompute_w_u_fwd', 'chunk_o_fwd', 'chunk_bwd', 'fwd_prepare_wy_repr',
        ])
        origin = 'HUB_TARGET_SIGNATURE' if target else 'OTHER'
        rows.append({
            'nvtx_range':text,
            'arm':'HUB' if '_HUB=' in text else 'FALLBACK',
            'phase':'PREFILL' if 'PREFILL' in text else 'DECODE',
            'kernel':name,
            'grid':f'{gx},{gy},{gz}',
            'block':f'{bx},{by},{bz}',
            'launches':count,
            'total_gpu_ns':total,
            'min_gpu_ns':min_ns,
            'max_gpu_ns':max_ns,
            'classification':origin,
        })

with OUT.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader(); w.writerows(rows)

summary={}
for arm in ['FALLBACK','HUB']:
    subset=[r for r in rows if r['arm']==arm]
    target=[r for r in subset if r['classification']=='HUB_TARGET_SIGNATURE']
    summary[arm]={
        'ranges':len({r['nvtx_range'] for r in subset}),
        'kernel_launches':sum(r['launches'] for r in subset),
        'target_signature_strata':len(target),
        'target_signature_launches':sum(r['launches'] for r in target),
        'target_kernel_names':sorted({r['kernel'] for r in target}),
    }
(ROOT/'receipts/R54_V1R1_NSYS_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
