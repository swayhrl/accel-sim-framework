#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
path=json.loads((ROOT/'R101_OPERATOR_PATH_QUALIFICATION.json').read_text())
assert all(x['intended_source_path_qualified'] for x in path.values())
micro=json.loads((ROOT/'R101_GRADIENT_MICROSTATE_RECEIPT_DISCOVERY.json').read_text())
assert micro['status']=='MICROSTATE_COMPLETE'
data={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'scope':'fixed selected three real layer0 Qwen projection parameters only, not a full-model training step',
 'frozen_gradient_microstate_sha256':sha(ROOT/'R101_GRADIENT_MICROSTATE_RECEIPT_DISCOVERY.json'),
 'frozen_gradient_payload_sha256':micro['payload_sha256'],
 'source_commit':'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
 'source_path_qualification_sha256':sha(ROOT/'R101_OPERATOR_PATH_QUALIFICATION.json'),
 'tile_edges':[256,512],
 'author_optimizer':'HiMuon single GPU non-DTensor cross-layer bucket path',
 'author_settings':{'lr':0.02,'momentum':0.95,'nesterov':True,
  'weight_decay':0.1,'ns_steps':5,'cuda_graph':True,'cuda_graph_warmup':3,
  'b_hw':None,'lr_adjust':'tile'},
 'plan_buffer_reuse_required':True,
 'graph_scope':'author optimizer step graph captures momentum/tile/NS/untile; WD/LR outside graph',
 'first_frozen_state_canary':'compare one eager first step to graph replay after restoring initial params/zero momentum; author rtol=atol=1e-2',
 'formal_replay_reset':'outside timing restore original parameter values and zero existing momentum buffers; preserve all grad/state pointers and shapes',
 'formal':{'canary':1,'warmups':2,'repetitions':7,'paired_interleaved_L256_L512':True},
 'primary':'complete selected optimizer replay CUDA event ms',
 'secondary':'host elapsed, NSYS graph node kernel counts/durations, peak allocation',
 'ncu_materiality_decision_after_formal':True,
 'no_gradient_or_algorithm_or_tile_change':True,
 'frozen_before_optimizer_timing':True}
(ROOT/'OPTIMIZER_REPLAY_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps({'tile_edges':data['tile_edges'],'preregistration_sha256':sha(ROOT/'OPTIMIZER_REPLAY_PREREGISTRATION.json')}))
