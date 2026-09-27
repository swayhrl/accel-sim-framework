#!/usr/bin/env python3
import csv,json,sqlite3
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
cohort='C1_HETEROGENEOUS_DISCOVERY'
arms=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT']
summary=[];strata=[]
for arm in arms:
    db=ROOT/'raw/nsys'/cohort/arm/f'{arm}.sqlite'
    con=sqlite3.connect(db)
    nvtx=con.execute('select start,end from NVTX_EVENTS where text=? and end is not null',
      (f'R81_FULL_GENERATION_C1_{arm}',)).fetchone()
    if nvtx is None:raise ValueError(f'missing NVTX {arm}')
    start,end=nvtx
    kernels=con.execute('''select s.value,count(*),sum(k.end-k.start) from CUPTI_ACTIVITY_KIND_KERNEL k
      join StringIds s on s.id=k.demangledName
      where k.start>=? and k.end<=?
      group by s.value order by sum(k.end-k.start) desc''',(start,end)).fetchall()
    copy_ops={id_:label for id_,label in con.execute('select id,label from ENUM_CUDA_MEMCPY_OPER')}
    copies=con.execute('''select copyKind,count(*),sum(bytes),sum(end-start)
      from CUPTI_ACTIVITY_KIND_MEMCPY where start>=? and end<=? group by copyKind''',(start,end)).fetchall()
    by_kind={copy_ops[k]:{'count':n,'bytes':b,'gpu_ms':dur/1e6} for k,n,b,dur in copies}
    target_signatures={
      'A0_DENSE_VENDOR':['gemm','gemv'],
      'A1_DENSE_FUSED':['dense_fused_tiles'],
      'A2_INDEXED_UNION':['indexSelect','index_select','gemm','gemv'],
      'A3_RAGGED_DIRECT':['ragged_direct_groups']}
    names=[name for name,_,_ in kernels]
    target_present=any(any(s.lower() in name.lower() for s in target_signatures[arm]) for name in names)
    summary.append({'cohort':cohort,'arm':arm,'nvtx_wall_ms_profiler_only':(end-start)/1e6,
       'kernel_launches':sum(n for _,n,_ in kernels),
       'kernel_gpu_duration_sum_ms_noncritical':sum(d for _,_,d in kernels)/1e6,
       'distinct_kernel_names':len(kernels),
       'target_signature_present':target_present,
       'copy_kinds_json':json.dumps(by_kind,separators=(',',':')),
       'profile_receipt_semantic_exact':json.loads((ROOT/'raw/nsys'/cohort/arm/'PROFILE_CANARY_RECEIPT.json').read_text())['semantic_exact'],
       'primary_timing_source':'formal TIMING_RESULTS.tsv; profiler canary not used as latency'})
    for name,count,duration in kernels[:30]:
        strata.append({'cohort':cohort,'arm':arm,'kernel_name':name,'launches':count,
          'gpu_duration_sum_ms_noncritical':duration/1e6})
for name,rows in [('NSYS_CANARY_SUMMARY.tsv',summary),('NSYS_TOP_KERNEL_STRATA.tsv',strata)]:
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
print(json.dumps(summary,indent=2))
if not all(r['target_signature_present'] and r['profile_receipt_semantic_exact'] for r in summary):
    raise SystemExit(2)
