#!/usr/bin/env python3
import hashlib,json
from pathlib import Path

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
fixture=ROOT/'FULL_R54_FIXTURE_RECEIPT.json'
schema=ROOT/'R54_EXACT_STATE_SCHEMA.tsv'
gate=ROOT/'R54_SEMANTIC_GATE_RECEIPT.json'
g=json.loads(gate.read_text())
assert g['status']=='SEMANTIC_GATES_PASS'
data={
 'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2',
 'backend':'V1R1_HUB_GENERIC_FOUR_FUNCTIONS_V1R2_GREEDY_QUALIFIED',
 'model_revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb',
 'model_weight_sha256':'04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696',
 'transformers_commit':'96331a9f93b72697f160a958d2883d4b49a56739',
 'torch':'2.14.0+cu130','kernels':'0.17.0',
 'mamba_revision':'20b2508ad12ae40260291539bf45183000451850',
 'fla_revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639',
 'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),
 'schema_sha256':hashlib.sha256(schema.read_bytes()).hexdigest(),
 'semantic_gate_sha256':hashlib.sha256(gate.read_bytes()).hexdigest(),
 'prefix':'PREFIX_DISCOVERY_4096','chunk_tokens':512,
 'densities':[512,2048],
 'production_arms':['P0','P1_D512','P2_D512','P1_D2048','P2_D2048'],
 'production_per_arm':{'canary':1,'warmup':2,'formal_repetitions':7},
 'primary_interval':'first prefix chunk GPU submission to both model completion and all required snapshots ready',
 'P0':'chunked512 no snapshot, comparable GDN hooks',
 'P1':'preallocated synchronous D2D exact GDN state snapshot at boundary',
 'P2':'dedicated snapshot stream, per-GDN-layer ready/done events, source reuse wait before next update',
 'recurrent_state_bytes_per_boundary':19759104,
 'full_attention_kv':'ordinary resident prefix cache, excluded from recurrent checkpoint',
 'materiality':{'minimum_overhead_fraction':0.05,'minimum_effect_over_jitter':3},
 'restore_arms':['R0','R1A','R1B','L1A','L1B','F1A','F1B'],
 'restore_per_arm':{'canary':1,'warmup':2,'formal_repetitions':7},
 'restore_denominator':'measured avoided prefix4096 recompute',
 'amortization_reuse_counts':[1,2,4],
 'holdout_trigger':'qualified stable >=5% production P2 or restore residual',
 'holdout_prefix':'PREFIX_HOLDOUT_2048',
 'holdout_density_selection':'larger qualified P2 production residual; tie D512',
 'ncu_max_profiles_if_holdout_pass':2,
 'parameter_scan':False,
 'frozen_before_formal_timing':True,
}
(ROOT/'R54_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps({'production_arms':data['production_arms'],'fixture_sha256':data['fixture_sha256']},indent=2))
