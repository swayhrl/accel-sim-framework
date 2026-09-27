#!/usr/bin/env python3
import csv,json,statistics
from pathlib import Path

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
with (ROOT/'SNAPSHOT_PRODUCTION_TIMING.tsv').open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
arms=['P0','P1_D512','P2_D512','P1_D2048','P2_D2048']
groups={a:[float(r['total_gpu_ms']) for r in rows if r['arm']==a] for a in arms}
assert all(len(v)==7 for v in groups.values())

def stats(values):
    m=statistics.median(values)
    deviations=[abs(x-m) for x in values]
    return {'median_ms':m,'min_ms':min(values),'max_ms':max(values),
            'mad_ms':statistics.median(deviations),
            'max_relative_deviation':max(deviations)/m,
            'mad_relative':statistics.median(deviations)/m,
            'formal_values_ms':values}

summary={a:stats(groups[a]) for a in arms}
base=summary['P0']
for arm in arms[1:]:
    current=summary[arm]
    fraction=(current['median_ms']-base['median_ms'])/base['median_ms']
    noise=max(base['max_relative_deviation'],current['max_relative_deviation'])
    current.update({'overhead_fraction_vs_p0':fraction,
                    'larger_conservative_jitter_fraction':noise,
                    'effect_over_jitter_ratio':fraction/noise if noise else None,
                    'stable_material_cost':fraction>=0.05 and fraction>3*noise})
summary['P0']['overhead_fraction_vs_p0']=0.0
(ROOT/'PRODUCTION_ANALYSIS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps({a:{k:summary[a].get(k) for k in ['median_ms','overhead_fraction_vs_p0','larger_conservative_jitter_fraction','effect_over_jitter_ratio','stable_material_cost']} for a in arms},indent=2))
