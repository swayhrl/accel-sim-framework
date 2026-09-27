#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
root=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
prod=json.loads((root/'PRODUCTION_ANALYSIS.json').read_text())
assert prod['P2_D512']['stable_material_cost'] is True
assert prod['P2_D512']['overhead_fraction_vs_p0']>prod['P2_D2048']['overhead_fraction_vs_p0']
fixture=json.loads((root/'FULL_R54_FIXTURE_RECEIPT.json').read_text())
data={'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2',
 'trigger':'P2_D512_DISCOVERY_STABLE_MATERIAL_COST',
 'selected_density':'D512','selection_rule':'larger qualified P2 production residual; tie D512',
 'discovery_p2_d512_overhead_fraction':prod['P2_D512']['overhead_fraction_vs_p0'],
 'discovery_p2_d2048_overhead_fraction':prod['P2_D2048']['overhead_fraction_vs_p0'],
 'prefix':'PREFIX_HOLDOUT_2048','prefix_token_sha256':fixture['parts']['PREFIX_HOLDOUT_2048']['token_ids_sha256'],
 'suffix':'HOLDOUT_SUFFIX_256','suffix_token_sha256':fixture['parts']['HOLDOUT_SUFFIX_256']['token_ids_sha256'],
 'arms':['P0','P2_D512','R1_HOLDOUT','L1_HOLDOUT','F1_HOLDOUT'],
 'canary_per_arm':1,'warmups_per_arm':2,'formal_repetitions_per_arm':7,
 'semantic_gate':'same Hub backend; snapshot content exact; exact greedy/top8/top2/16-token continuation',
 'materiality':{'minimum_overhead_fraction':0.05,'effect_over_conservative_jitter':3},
 'tuning_on_holdout':False,'frozen_before_holdout_run':True}
(root/'HOLDOUT_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps(data,indent=2))
