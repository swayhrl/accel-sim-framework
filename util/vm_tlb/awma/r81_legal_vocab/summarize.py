#!/usr/bin/env python3
from __future__ import annotations
import csv,json,statistics
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
COHORTS=['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT']
ARMS=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT']

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

sem=[];timing=[];stats=[]
validity=list(csv.DictReader((ROOT/'GRAMMAR_VALIDITY.tsv').open(),delimiter='\t'))
assert len(validity)==12 and all(r['schema_valid']=='True' for r in validity)
for cohort in COHORTS:
    ref=json.loads((ROOT/'raw/reference'/cohort/'REQUEST_RESULTS.json').read_text())
    head=json.loads((ROOT/'raw/head_replay'/cohort/'CANARY_RESULTS.json').read_text())
    full=json.loads((ROOT/'raw/full_generation'/cohort/'CANARY_RESULTS.json').read_text())
    assert all(head['status'][a]=='QUALIFIED' and full[a]['semantic_exact'] for a in ARMS)
    expected_ids=[r['generated_token_ids'] for r in ref]
    expected_stops=[r['stop_reason'] for r in ref]
    for arm in ARMS:
        assert full[arm]['generated_token_ids']==expected_ids
        assert full[arm]['stop_reasons']==expected_stops
        sem.append({'cohort':cohort,'arm':arm,'reference_steps':len(json.loads((ROOT/'raw/reference'/cohort/'STEP_LEDGER.json').read_text())),
          'head_replay_exact_all_steps':True,'full_generation_token_ids_exact':True,
          'stop_status_exact':True,'generated_counts':json.dumps(full[arm]['generated_counts'],separators=(',',':')),
          'stop_reasons':json.dumps(expected_stops,separators=(',',':')),
          'all_json_schema_valid':True,'truncated_requests':0})
    for scope,source,col in [('HEAD_REGION',ROOT/'raw/head_replay'/cohort/'TIMING_REPETITIONS.tsv','total_head_region_ms'),
                             ('FULL_GENERATION',ROOT/'raw/full_generation'/cohort/'TIMING_RESULTS.tsv','wall_ms')]:
        with source.open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
        assert len(rows)==28
        for row in rows:
            timing.append({'cohort':cohort,'scope':scope,'arm':row['arm'],'rep':int(row['rep']),
              'elapsed_ms':float(row[col]),
              'valid_token_count':row.get('valid_token_count',''),
              'semantic_exact':True,
              'run_status':'FORMAL',
              'primary_timing':scope=='FULL_GENERATION',
              'source_relative_to_root':str(source.relative_to(ROOT))})
        for arm in ARMS:
            vals=[float(r[col]) for r in rows if r['arm']==arm]
            median=statistics.median(vals)
            stats.append({'cohort':cohort,'scope':scope,'arm':arm,'formal_n':len(vals),
              'median_ms':median,'min_ms':min(vals),'max_ms':max(vals),
              'max_relative_deviation':max(abs(x-median) for x in vals)/median,
              'values_ms':json.dumps(vals,separators=(',',':'))})
write_tsv(ROOT/'SEMANTIC_RESULTS.tsv',sem)
write_tsv(ROOT/'TIMING_RESULTS.tsv',timing)
write_tsv(ROOT/'TIMING_SUMMARY.tsv',stats)
binding=json.loads((ROOT/'INPUT_RUNTIME_BINDINGS.json').read_text())
compile_rows=[{'schema_sha256':x['schema_sha256'],'compiler_ms':x['compiler_ms'],
               'compiled_json_sha256':x['compiled_json_sha256'],
               'compiled_bytes':x['compiled_bytes']} for x in binding['compiled_grammar_receipts']]
write_tsv(ROOT/'GRAMMAR_COMPILE_COST.tsv',compile_rows)

agg=json.loads((ROOT/'MASK_WORK_AGGREGATE.json').read_text())
control=list(csv.DictReader((ROOT/'CONTROL_STRATIFICATION_SUMMARY.tsv').open(),delimiter='\t'))
def ctrl(cohort,stratum,arm):
    return next(float(r['fraction_vs_a0']) for r in control if r['cohort']==cohort and r['stratum']==stratum and r['arm']==arm)
def timing_stat(cohort,scope,arm):
    return next(r for r in stats if r['cohort']==cohort and r['scope']==scope and r['arm']==arm)
effects={}
for cohort in COHORTS:
    base=timing_stat(cohort,'FULL_GENERATION','A0_DENSE_VENDOR')
    candidate=timing_stat(cohort,'FULL_GENERATION','A3_RAGGED_DIRECT')
    delta=candidate['median_ms']/base['median_ms']-1
    noise=max(base['max_relative_deviation'],candidate['max_relative_deviation'])
    effects[cohort]={'a0_ms':base['median_ms'],'a3_ms':candidate['median_ms'],
      'a3_fraction_vs_a0':delta,'larger_max_relative_deviation':noise,
      'a3_reliable_complete_improvement':delta<=-0.05 and abs(delta)>3*noise,
      'sparse_stratum_a3_fraction_vs_a0':ctrl(cohort,'UNION_LT_1_PERCENT','A3_RAGGED_DIRECT'),
      'broad_stratum_a3_fraction_vs_a0':ctrl(cohort,'UNION_GT_50_PERCENT','A3_RAGGED_DIRECT'),
      'union_median_fraction_of_vocab':agg[cohort]['union_fraction_median'],
      'broad_union_steps':agg[cohort]['steps_with_union_over_half_vocab'],
      'total_steps':agg[cohort]['steps']}
assert not any(v['a3_reliable_complete_improvement'] for v in effects.values())
decision={'stage':'AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1',
 'final_state':'R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM',
 'scope':'109 RTX4080 SM89, Qwen2.5-0.5B BF16, authored B4 JSON-schema fixture, 128 max new tokens',
 'strongest_known_capability_baseline':'A0_DENSE_VENDOR on both discovery cohorts and holdout',
 'all_12_requests_schema_valid':True,'all_arms_exact_generated_ids_and_stop':True,
 'A3_local_sparse_response_persists_holdout':all(v['sparse_stratum_a3_fraction_vs_a0']<0 for v in effects.values()),
 'A3_complete_generation_reliable_improvement':False,
 'effects':effects,
 'explanations':['most free-text states have union around 96.8% of model vocabulary',
   'direct ragged avoids sparse structural row work but pays broad-state direct-index weight traffic and metadata',
   'indexed union gathers nearly all head rows on broad states',
   'FlashSampling-style A1 is a bounded greedy adaptation, not the original optimized implementation'],
 'next_scope':'software-only support-aware dispatch worth a separate bounded review; no architecture admission',
 'ncu_profiles':0,'ncu_reason':'no registered mechanism question remaining after NSYS, exact support and complete-generation controls',
 'r82_touched':False,'accel_sim_run':False,'full_nvbit_trace':False}
(ROOT/'DECISION_RECEIPT.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n')
print(json.dumps({'final_state':decision['final_state'],'effects':effects},indent=2))
