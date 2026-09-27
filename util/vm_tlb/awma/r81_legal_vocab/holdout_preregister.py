#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1')
source=WT/'util/vm_tlb/awma/r81_legal_vocab'
fixture=json.loads((source/'fixture.json').read_text())
prereg=json.loads((ROOT/'PREREGISTRATION.json').read_text())
assert len(fixture['cohorts']['H0_HETEROGENEOUS_HOLDOUT'])==4
assert prereg['cohort_holdout']=='H0_HETEROGENEOUS_HOLDOUT'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data={'stage':'AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1',
 'holdout_authority':'H0_HETEROGENEOUS_HOLDOUT',
 'fixture_sha256':sha(source/'fixture.json'),
 'preregistration_sha256':sha(ROOT/'PREREGISTRATION.json'),
 'input_runtime_bindings_sha256':sha(ROOT/'INPUT_RUNTIME_BINDINGS.json'),
 'heads_source_sha256':sha(source/'heads.py'),
 'reference_source_sha256':sha(source/'reference.py'),
 'full_generation_source_sha256':sha(source/'full_generation.py'),
 'trigger':'A3 local sparse-mask head-region response in discovery; complete-generation effect not established',
 'arms':['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT'],
 'semantic_gate':'exact selected token/full generated sequence versus fixed dense reference',
 'formal_warmups':2,'formal_repetitions':7,
 'control_strata':[{'name':'UNION_LT_1_PERCENT','rule':'union_count/model_vocab<0.01'},
                   {'name':'UNION_GT_50_PERCENT','rule':'union_count/model_vocab>0.5'},
                   {'name':'ALL_STEPS','rule':'retain all timesteps'}],
 'control_purpose':'separate local sparse structural response from broad free-text steps without selecting new requests',
 'holdout_model_outcomes_seen_before_freeze':False,
 'kernel_or_prompt_tuning_after_holdout':False}
(ROOT/'HOLDOUT_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps({'holdout':data['holdout_authority'],'arms':data['arms'],
                  'holdout_preregistration_sha256':sha(ROOT/'HOLDOUT_PREREGISTRATION.json')},sort_keys=True))
