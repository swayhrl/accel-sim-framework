#!/usr/bin/env python3
import csv,json,sqlite3
from collections import Counter
from pathlib import Path
ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
rows=[];summary={}
for edge in (256,512):
    db=ROOT/'raw/nsys'/f'optimizer_L{edge}'/f'optimizer_L{edge}.sqlite'
    con=sqlite3.connect(db)
    label=f'R101_SELECTED_OPTIMIZER_L{edge}_GRAPH'
    ranges=con.execute('select start,end from NVTX_EVENTS where text=? and end is not null',(label,)).fetchall()
    if len(ranges)!=1:raise ValueError(f'missing optimizer range L{edge}')
    start,end=ranges[0]
    kernels=con.execute('''select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,
          count(*),sum(k.end-k.start) from CUPTI_ACTIVITY_KIND_KERNEL k
          join StringIds s on s.id=k.demangledName where k.start>=? and k.end<=?
          group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ
          order by sum(k.end-k.start) desc''',(start,end)).fetchall()
    counts=Counter();times=Counter()
    for name,gx,gy,gz,bx,by,bz,n,t in kernels:
        lower=name.lower()
        family='XXT' if 'xxt_kernel' in lower else 'BA_PLUS_CAA' if 'ba_plus_caa_kernel' in lower else 'FUSED_BMM_ADD' if 'bmm_add_kernel' in lower else 'OTHER'
        counts[family]+=n;times[family]+=t
        rows.append({'edge':edge,'family':family,'exact_demangled_name':name,
                     'grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}',
                     'launches':n,'gpu_duration_sum_ms_noncritical':t/1e6})
    if not all(counts[f]>=5 for f in ['XXT','BA_PLUS_CAA','FUSED_BMM_ADD']):
        raise ValueError(f'missing NS family L{edge}: {dict(counts)}')
    ns_ns=sum(times[f] for f in ['XXT','BA_PLUS_CAA','FUSED_BMM_ADD'])
    total_ns=sum(times.values())
    summary[str(edge)]={'nvtx_label':label,'nvtx_wall_ms_profiler_only':(end-start)/1e6,
      'total_kernel_launches':sum(counts.values()),'ns_three_kernel_launches':sum(counts[f] for f in ['XXT','BA_PLUS_CAA','FUSED_BMM_ADD']),
      'family_counts':dict(counts),'ns_family_gpu_duration_sum_ms_noncritical':ns_ns/1e6,
      'all_kernel_duration_sum_ms_noncritical':total_ns/1e6,
      'ns_fraction_of_sum_kernel_duration':ns_ns/total_ns if total_ns else None,
      'intended_author_path_qualified':True,
      'profile_time_is_not_primary':True}
with (ROOT/'R101_OPTIMIZER_KERNEL_STRATA.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
(ROOT/'R101_OPTIMIZER_NSYS_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2))
