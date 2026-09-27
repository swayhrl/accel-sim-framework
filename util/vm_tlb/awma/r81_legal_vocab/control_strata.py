#!/usr/bin/env python3
import csv,json,statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
COHORTS=['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT']
ARMS=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT']
work=list(csv.DictReader((ROOT/'MASK_WORK_SUMMARY.tsv').open(),delimiter='\t'))
work_by={(r['cohort'],int(r['step'])):r for r in work}
rules={
  'UNION_LT_1_PERCENT':lambda x:float(x['union_fraction_of_model_vocab'])<0.01,
  'UNION_GT_50_PERCENT':lambda x:float(x['union_fraction_of_model_vocab'])>0.5,
  'ALL_STEPS':lambda x:True,
}
raw=[];summary=[]
for cohort in COHORTS:
    timing=list(csv.DictReader((ROOT/'raw/head_replay'/cohort/'TIMING_STEPS.tsv').open(),delimiter='\t'))
    for label,rule in rules.items():
        selected={step for (c,step),x in work_by.items() if c==cohort and rule(x)}
        for arm in ARMS:
            for rep in range(7):
                total=sum(float(r['elapsed_head_region_ms']) for r in timing
                          if r['arm']==arm and int(r['rep'])==rep and int(r['step']) in selected)
                raw.append({'cohort':cohort,'stratum':label,'arm':arm,'rep':rep,
                            'step_count':len(selected),'head_region_sum_ms':total})
        base=statistics.median(r['head_region_sum_ms'] for r in raw
                               if r['cohort']==cohort and r['stratum']==label and r['arm']=='A0_DENSE_VENDOR')
        for arm in ARMS:
            vals=[r['head_region_sum_ms'] for r in raw if r['cohort']==cohort and r['stratum']==label and r['arm']==arm]
            med=statistics.median(vals)
            summary.append({'cohort':cohort,'stratum':label,'arm':arm,'step_count':len(selected),
                'median_stratum_head_region_sum_ms':med,'a0_median_ms':base,
                'fraction_vs_a0':(med/base-1) if base else None,
                'measured_values_ms':json.dumps(vals,separators=(',',':')),
                'scope':'offline workset stratification of existing formal runs; not a new GPU configuration'})
for name,rows in [('CONTROL_STRATIFICATION_RUNS.tsv',raw),('CONTROL_STRATIFICATION_SUMMARY.tsv',summary)]:
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
print(json.dumps([r for r in summary if r['arm']=='A3_RAGGED_DIRECT'],indent=2))
