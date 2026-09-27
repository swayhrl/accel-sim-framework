#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
input_receipt=json.loads((ROOT/'R101_INPUT_RECEIPT.json').read_text())
graph=json.loads((ROOT/'GRAPH_CONTROL_ANALYSIS.json').read_text())
assert graph['same_map_graph']['material_response']
opt=json.loads((ROOT/'OPTIMIZER_REPLAY_ANALYSIS.json').read_text())
ncu=json.loads((ROOT/'NCU_SUMMARY.json').read_text())
assert ncu['L512']['family_counts']['AUTHOR_XXT']==5
data={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'holdout':'TRAIN_HOLDOUT_256','token_ids_json_sha256':input_receipt['parts']['TRAIN_HOLDOUT_256']['token_ids_json_sha256'],
 'token_payload_sha256':input_receipt['parts']['TRAIN_HOLDOUT_256']['file_sha256'],
 'independence':'pre-frozen disjoint token IDs [256:512] of accepted raw R53 prompt stream',
 'parameter_names':['model.layers.12.self_attn.q_proj.weight',
                    'model.layers.12.mlp.up_proj.weight',
                    'model.layers.12.mlp.down_proj.weight'],
 'gradient_contract':'one BF16 next-token cross-entropy and backward, no parameter update; author zero-momentum Nesterov first step',
 'tile_edges':[128,512],
 'S128_arms':['F128','K128','F128_GRAPH','K128_GRAPH'],
 'L512_arm':'author compiled three-kernel plus selected-parameter HiMuon graph optimizer replay',
 'coefficients':[3.4445,-4.7750,2.0315],'steps':5,
 'numerical_rtol':0.01,'numerical_atol':0.01,
 'formal':{'canary':1,'warmups':2,'repetitions':7,'paired_interleaved_F128_K128':True},
 'required_direction':['F128 faster than K128 on same S128 input','L512 material inside selected graph optimizer replay'],
 'discovery_graph_analysis_sha256':sha(ROOT/'GRAPH_CONTROL_ANALYSIS.json'),
 'discovery_optimizer_replay_sha256':sha(ROOT/'OPTIMIZER_REPLAY_ANALYSIS.json'),
 'discovery_ncu_summary_sha256':sha(ROOT/'NCU_SUMMARY.json'),
 'holdout_outcomes_seen_before_freeze':False,'no_tuning_on_holdout':True}
(ROOT/'HOLDOUT_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps({'tile_edges':data['tile_edges'],'sha256':sha(ROOT/'HOLDOUT_PREREGISTRATION.json')}))
