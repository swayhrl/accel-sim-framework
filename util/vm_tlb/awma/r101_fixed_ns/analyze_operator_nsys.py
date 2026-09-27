#!/usr/bin/env python3
import csv,json,sqlite3
from collections import Counter
from pathlib import Path
ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
con=sqlite3.connect(ROOT/'raw/nsys/operator_path.sqlite')
arms=['F128','K128','L256','L512']
rows=[];summary={}

def family(name):
    lower=name.lower()
    if 'ns5_smem_kernel' in lower:return 'AUTHOR_FUSED_NS5'
    if 'xxt_kernel' in lower:return 'AUTHOR_XXT'
    if 'ba_plus_caa_kernel' in lower:return 'AUTHOR_BA_PLUS_CAA'
    if 'bmm_add_kernel' in lower:return 'AUTHOR_FUSED_BMM_ADD'
    return 'OTHER'

for mode in ('EAGER','GRAPH'):
    for arm in arms:
        label=f'R101_OPERATOR_{mode}_{arm}' if mode=='EAGER' else f'R101_OPERATOR_{mode}_{arm}_GRAPH'
        ranges=con.execute('select start,end from NVTX_EVENTS where text=? and end is not null',(label,)).fetchall()
        if len(ranges)!=1:raise ValueError(f'need one range {label}, got {len(ranges)}')
        start,end=ranges[0]
        result=con.execute('''select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,
                            count(*),sum(k.end-k.start)
                            from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName
                            where k.start>=? and k.end<=?
                            group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ
                            order by sum(k.end-k.start) desc''',(start,end)).fetchall()
        counts=Counter()
        for name,gx,gy,gz,bx,by,bz,count,total in result:
            fam=family(name)
            counts[fam]+=count
            rows.append({'mode':mode,'arm':arm,'family':fam,'exact_demangled_name':name,
              'grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}',
              'launches':count,'gpu_duration_sum_ms_noncritical':total/1e6})
        expect_fused=arm=='F128'
        if expect_fused:
            qualified=counts['AUTHOR_FUSED_NS5']>=1 and all(counts[x]==0 for x in ['AUTHOR_XXT','AUTHOR_BA_PLUS_CAA','AUTHOR_FUSED_BMM_ADD'])
        else:
            qualified=all(counts[x]>=5 for x in ['AUTHOR_XXT','AUTHOR_BA_PLUS_CAA','AUTHOR_FUSED_BMM_ADD']) and counts['AUTHOR_FUSED_NS5']==0
        summary[f'{mode}_{arm}']={'nvtx_label':label,'nvtx_wall_ms_profiler_only':(end-start)/1e6,
          'kernel_launches':sum(counts.values()),'family_counts':dict(counts),
          'intended_source_path_qualified':qualified,
          'timing_source':'separate formal CUDA event data, not NSYS replay/profile time'}
        if not qualified:
            print(json.dumps({'mode':mode,'arm':arm,'counts':dict(counts),
                'names':[r[0] for r in result]},indent=2))
            raise ValueError(f'path identity failed {mode}/{arm}: {dict(counts)}')

with (ROOT/'R101_OPERATOR_KERNEL_STRATA.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
(ROOT/'R101_OPERATOR_PATH_QUALIFICATION.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v['family_counts'] for k,v in summary.items()},indent=2))
