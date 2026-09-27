#!/usr/bin/env python3
import csv,json,sqlite3
from pathlib import Path

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
rows=[]
for arm in ['P0','P1_D512','P2_D512','P1_D2048','P2_D2048']:
    db=ROOT/'raw'/'production_profile'/arm/f'{arm}.sqlite'
    con=sqlite3.connect(db)
    nvtx=con.execute("select start,end from NVTX_EVENTS where text=? and end is not null",(f'R54_PRODUCTION_PROFILE_{arm}',)).fetchone()
    if not nvtx:raise ValueError(f'Missing profile NVTX {arm}')
    start,end=nvtx
    kinds={i:(name,label) for i,name,label in con.execute('select id,name,label from ENUM_CUDA_MEMCPY_OPER')}
    for kind,count,bytes_,duration in con.execute('''
      select copyKind,count(*),sum(bytes),sum(end-start)
      from CUPTI_ACTIVITY_KIND_MEMCPY
      where start>=? and end<=?
      group by copyKind order by copyKind''',(start,end)):
        rows.append({'arm':arm,'copy_kind_id':kind,'copy_kind':kinds[kind][1],
           'count':count,'bytes':bytes_,'total_gpu_ms':duration/1e6,
           'nvtx_scope':'includes timed prefill plus post-timing 16-token diagnostic'})
with (ROOT/'NSYS_MEMCPY_STRATA.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
print(json.dumps(rows,indent=2))
