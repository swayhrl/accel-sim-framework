#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
numeric=json.loads((ROOT/'R101_NUMERICAL_CANARY_RECEIPT_DISCOVERY.json').read_text())
assert numeric['same_map_pair_pass']
data={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'purpose':'remove repeat-call Python launch overhead for the same frozen finite maps',
 'same_input_tile_payload_sha256':{str(t):json.loads((ROOT/'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())['tiles'][str(t)]['payload_sha256'] for t in [128,256,512]},
 'arms':['F128_GRAPH','K128_GRAPH','L256_GRAPH','L512_GRAPH'],
 'F128_K128_same_map':True,'ns_steps':5,'coefficients':[3.4445,-4.7750,2.0315],
 'capture_after_author_jit_and_autotune_warmup':True,
 'fixed_input_pointer_and_control_path':True,
 'liveness_canary':'temporarily perturb one tile element, replay, require changed output; restore input and require original output within author tolerance before timing',
 'formal':{'canary':1,'warmups':2,'repetitions':7,'paired_interleaved_F128_K128':True},
 'numerical_rtol':0.01,'numerical_atol':0.01,
 'eager_timing_authority_sha256':sha(ROOT/'OPERATOR_TIMING.tsv'),
 'no_new_tile_or_algorithm':True,
 'frozen_before_graph_timing':True}
(ROOT/'GRAPH_CONTROL_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps({'arms':data['arms'],'sha256':sha(ROOT/'GRAPH_CONTROL_PREREGISTRATION.json')}))
