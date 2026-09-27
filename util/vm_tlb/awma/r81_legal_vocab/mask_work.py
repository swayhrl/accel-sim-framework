#!/usr/bin/env python3
import csv,json,statistics
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
rows=[]
for cohort in ['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT']:
    ledger=json.loads((ROOT/'raw/reference'/cohort/'STEP_LEDGER.json').read_text())
    for s in ledger:
        active=len(s['active_request_ids'])
        union=s['legal_union_count'];total=s['legal_sum_count']
        rows.append({'cohort':cohort,'step':s['step'],'active_requests':active,
          'legal_counts':json.dumps(s['legal_counts'],separators=(',',':')),
          'union_count':union,'sum_legal_counts':total,
          'shared_union_logical_rows':active*union,'ragged_logical_rows':total,
          'union_to_ragged_logical_ratio':active*union/total if total else None,
          'union_fraction_of_model_vocab':union/151936,
          'singleton_active_requests':s['singleton_request_count'],
          'dense_head_invoked_rows':len(s['head_invoked_rows']),
          'grammar_fill_ms_diagnostic':s['grammar_fill_ms_diagnostic'],
          'dense_head_region_ms_diagnostic':s['dense_head_region_ms_diagnostic'],
          'mask_sha256':s['mask_sha256'],'hidden_sha256':s['hidden_sha256']})
with (ROOT/'MASK_WORK_SUMMARY.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
summary={}
for cohort in ['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT']:
    subset=[r for r in rows if r['cohort']==cohort]
    summary[cohort]={'steps':len(subset),
      'union_count_min':min(r['union_count'] for r in subset),
      'union_count_median':statistics.median(r['union_count'] for r in subset),
      'union_count_max':max(r['union_count'] for r in subset),
      'union_fraction_median':statistics.median(r['union_fraction_of_model_vocab'] for r in subset),
      'logical_union_to_ragged_ratio_median':statistics.median(r['union_to_ragged_logical_ratio'] for r in subset),
      'logical_union_to_ragged_ratio_max':max(r['union_to_ragged_logical_ratio'] for r in subset),
      'steps_with_singleton_active':sum(r['singleton_active_requests']>0 for r in subset),
      'steps_with_union_over_half_vocab':sum(r['union_fraction_of_model_vocab']>0.5 for r in subset),
      'steps_with_union_under_1k':sum(r['union_count']<1000 for r in subset),
      'all_steps_retained':True,
      'logical_rows_not_DDR_bytes_or_speedup_bound':True}
(ROOT/'MASK_WORK_AGGREGATE.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
