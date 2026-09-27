#!/usr/bin/env python3
import csv,json,statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
ARMS=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT']
result={}
for cohort in ['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY']:
    work={int(r['step']):r for r in csv.DictReader((ROOT/'MASK_WORK_SUMMARY.tsv').open(),delimiter='\t') if r['cohort']==cohort}
    timing=list(csv.DictReader((ROOT/'raw/head_replay'/cohort/'TIMING_STEPS.tsv').open(),delimiter='\t'))
    full=json.loads((ROOT/'raw/full_generation'/cohort/'TIMING_SUMMARY.json').read_text())
    regions={'UNION_LT_1_PERCENT':lambda w:float(w['union_fraction_of_model_vocab'])<0.01,
             'UNION_1_TO_50_PERCENT':lambda w:0.01<=float(w['union_fraction_of_model_vocab'])<=0.5,
             'UNION_GT_50_PERCENT':lambda w:float(w['union_fraction_of_model_vocab'])>0.5,
             'UNION_RAGGED_RATIO_GE_2':lambda w:float(w['union_to_ragged_logical_ratio'])>=2,
             'ALL_STEPS':lambda w:True}
    strata={}
    for label,predicate in regions.items():
        steps={step for step,w in work.items() if predicate(w)}
        strata[label]={'step_count':len(steps),
          'head_region_step_ms_median':{arm:statistics.median(float(r['elapsed_head_region_ms']) for r in timing if r['arm']==arm and int(r['step']) in steps)
            if steps else None for arm in ARMS}}
    a0=full['A0_DENSE_VENDOR']['wall_ms']
    paired={arm:[full[arm]['wall_ms'][i]-a0[i] for i in range(7)] for arm in ARMS[1:]}
    result[cohort]={'strata':strata,
      'full_generation_median_ms':{arm:full[arm]['median_wall_ms'] for arm in ARMS},
      'full_generation_paired_delta_vs_A0_ms':paired,
      'full_generation_paired_delta_median_ms':{arm:statistics.median(v) for arm,v in paired.items()},
      'fastest_known_capability_baseline':min(ARMS[:3],key=lambda arm:full[arm]['median_wall_ms']),
      'reference_request_count':4,
      'all_timesteps_retained':True}
(ROOT/'DISCOVERY_ANALYSIS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
