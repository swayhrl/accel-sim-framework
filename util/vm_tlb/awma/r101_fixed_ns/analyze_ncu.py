#!/usr/bin/env python3
from __future__ import annotations
import csv,json,math
from collections import defaultdict
from pathlib import Path

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
TARGETS=['K128','L512']
METRICS=['dram__bytes_read.sum','dram__bytes_write.sum','lts__t_bytes.sum',
         'sm__cycles_active.sum','sm__warps_active.avg.pct_of_peak_sustained_active',
         'launch__registers_per_thread','launch__shared_mem_per_block']

def number(value):
    if value is None or value in ('','N/A','nan'):return None
    try:return float(value.replace(',',''))
    except ValueError:return None

def family(name):
    s=name.lower()
    if 'xxt_kernel' in s:return 'AUTHOR_XXT'
    if 'ba_plus_caa_kernel' in s:return 'AUTHOR_BA_PLUS_CAA'
    if 'bmm_add_kernel' in s:return 'AUTHOR_FUSED_BMM_ADD'
    if 'norm' in s:return 'NORMALIZATION'
    return 'OTHER'

rows=[];summary={}
for target in TARGETS:
    path=ROOT/'raw/ncu'/target/f'{target}.raw.csv'
    with path.open(newline='') as f:
        reader=csv.DictReader(f)
        raw=list(reader)
    if not raw:raise ValueError(f'empty NCU CSV {target}')
    units={k:raw[0].get(k,'') for k in METRICS}
    kernels=[]
    for r in raw:
        if r['ID']=='':continue
        name=r['Kernel Name']
        item={'target':target,'source_family':family(name),'exact_kernel_name':name,
              'grid':r['Grid Size'],'block':r['Block Size']}
        for metric in METRICS:item[metric]=number(r.get(metric))
        kernels.append(item);rows.append(item)
    counts={f:sum(r['source_family']==f for r in kernels) for f in
      ['AUTHOR_XXT','AUTHOR_BA_PLUS_CAA','AUTHOR_FUSED_BMM_ADD','NORMALIZATION','OTHER']}
    if any(counts[f]!=5 for f in ['AUTHOR_XXT','AUTHOR_BA_PLUS_CAA','AUTHOR_FUSED_BMM_ADD']):
        raise ValueError(f'wrong NCU source family count {target}: {counts}')
    receipt=json.loads((ROOT/'raw/ncu'/target/'PROFILE_TARGET_RECEIPT.json').read_text())
    if not receipt['same_numerical_output_with_author_tolerance']:
        raise ValueError(f'NCU output not qualified {target}')
    totals={}
    for metric in METRICS[:4]:
        vals=[r[metric] for r in kernels]
        totals[metric]=sum(v for v in vals if v is not None)
    ns_only={}
    for metric in METRICS[:4]:
        vals=[r[metric] for r in kernels if r['source_family'].startswith('AUTHOR_')]
        ns_only[metric]=sum(v for v in vals if v is not None)
    summary[target]={'kernel_count':len(kernels),'family_counts':counts,
      'raw_metric_units':units,'all_kernel_metric_sums_in_reported_units':totals,
      'three_NS_family_metric_sums_in_reported_units':ns_only,
      'cache_control':'none','clock_control':'none','pipeline_boost':'dynamic',
      'ncu_time_is_not_primary':True,
      'source_input_same_as_numerical_canary':True}

with (ROOT/'NCU_DIAGNOSTIC.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
(ROOT/'NCU_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
