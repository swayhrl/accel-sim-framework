#!/usr/bin/env python3
import csv,json,math,statistics
from pathlib import Path

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
prod=json.loads((ROOT/'PRODUCTION_ANALYSIS.json').read_text())
rest=json.loads((ROOT/'RESTORE_ANALYSIS.json').read_text())
hold=json.loads((ROOT/'HOLDOUT_ANALYSIS.json').read_text())
with (ROOT/'SNAPSHOT_PRODUCTION_TIMING.tsv').open(newline='') as f:prod_rows=list(csv.DictReader(f,delimiter='\t'))
with (ROOT/'HOLDOUT_RESULTS.tsv').open(newline='') as f:hold_rows=list(csv.DictReader(f,delimiter='\t'))

def med(rows,arm,col):
    return statistics.median(float(r[col]) for r in rows if r['arm']==arm)

recurrent_bytes=19759104
amort=[]
for density in (512,2048):
    p0=prod['P0']['median_ms'];p2=prod[f'P2_D{density}']['median_ms']
    for suffix in ('A','B'):
        live=rest[f'L1{suffix}']['median_ms']
        restore_suffix=rest[f'R1{suffix}']['median_ms']
        full=rest[f'F1{suffix}']['median_ms']
        avoided_prefix=full-live
        incremental_restore=restore_suffix-live
        for n in (1,2,4):
            nocache=n*full
            reuse=p0+(p2-p0)+n*restore_suffix
            amort.append({'density':density,'suffix':suffix,'reuse_count_N':n,
              'measured_P0_prefix_ms':p0,'measured_P2_prefix_and_checkpoint_ms':p2,
              'measured_production_increment_ms':p2-p0,
              'measured_live_suffix_ms':live,
              'measured_restore_plus_suffix_ms':restore_suffix,
              'measured_full_recompute_plus_suffix_ms':full,
              'measured_avoided_prefix_recompute_ms':avoided_prefix,
              'measured_incremental_restore_ms':incremental_restore,
              'derived_no_cache_total_ms':nocache,'derived_reuse_total_ms':reuse,
              'derived_reuse_saving_ms':nocache-reuse,
              'derived_reuse_saving_fraction':(nocache-reuse)/nocache,
              'derived_integer_break_even_N':math.floor(p2/(full-restore_suffix))+1 if full>restore_suffix else 'NEVER',
              'recurrent_checkpoint_bytes_per_boundary':recurrent_bytes,
              'total_recurrent_checkpoint_storage_bytes':recurrent_bytes*(4096//density),
              'attention_KV':'already resident separately; excluded from each recurrent checkpoint'})
with (ROOT/'AMORTIZATION_RESULTS.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(amort[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(amort)

restore_result={}
for suffix in ('A','B'):
    incr=rest[f'R1{suffix}']['median_ms']-rest[f'L1{suffix}']['median_ms']
    avoided=rest[f'F1{suffix}']['median_ms']-rest[f'L1{suffix}']['median_ms']
    baseline_jitter=rest[f'L1{suffix}']['max_relative_jitter']
    restore_jitter=rest[f'R1{suffix}']['max_relative_jitter']
    relative_effect=incr/avoided
    restore_result[suffix]={'incremental_restore_ms':incr,'avoided_prefix_recompute_ms':avoided,
      'restore_fraction_of_avoided_prefix':relative_effect,
      'larger_relative_jitter_fraction':max(baseline_jitter,restore_jitter),
      'material_restore':relative_effect>=0.05 and relative_effect>3*max(baseline_jitter,restore_jitter)}

holdout_components={
 'P2_D512_host_snapshot_schedule_ms':med(hold_rows,'P2_D512','host_snapshot_schedule_ms'),
 'P2_D512_copy_gpu_ms_sum':med(hold_rows,'P2_D512','copy_gpu_ms_sum'),
 'P2_D512_source_reuse_waits':med(hold_rows,'P2_D512','source_reuse_waits'),
 'P2_D512_overhead_ms':hold['P2_D512']['median_ms']-hold['P0']['median_ms'],
 'restore_increment_ms':hold['R1_HOLDOUT']['median_ms']-hold['L1_HOLDOUT']['median_ms'],
 'avoided_prefix_ms':hold['F1_HOLDOUT']['median_ms']-hold['L1_HOLDOUT']['median_ms'],
}
holdout_components['restore_fraction_of_avoided_prefix']=holdout_components['restore_increment_ms']/holdout_components['avoided_prefix_ms']
decision={'discovery_production':{a:{k:prod[a].get(k) for k in ['median_ms','overhead_fraction_vs_p0','effect_over_jitter_ratio','stable_material_cost']}
    for a in ['P0','P1_D512','P2_D512','P1_D2048','P2_D2048']},
 'restore':restore_result,
 'holdout':{'production_p0_ms':hold['P0']['median_ms'],
            'production_p2_d512_ms':hold['P2_D512']['median_ms'],
            'p2_overhead_fraction':hold['P2_D512']['overhead_fraction_vs_p0'],
            'p2_effect_over_jitter':hold['P2_D512']['effect_over_jitter_ratio'],
            'p2_stable_material_cost':hold['P2_D512']['stable_material_cost'],
            **holdout_components},
 'amortization':'derived from measured components, not service hit distribution'}
(ROOT/'R54_COMPONENT_ANALYSIS.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n')
print(json.dumps(decision,indent=2,sort_keys=True))
