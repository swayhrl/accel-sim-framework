#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
R1=Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
prefix_path=ROOT/'R54_V1R2_PREFIX_RECEIPT.json'
prefix=json.loads(prefix_path.read_text())
backend=json.loads((R1/'R54_V1R1_ENVIRONMENT_RECEIPT.json').read_text())
assert backend['torch']=='2.14.0+cu130'
assert backend['kernels']=='0.17.0'
assert backend['transformers_source_commit']=='96331a9f93b72697f160a958d2883d4b49a56739'
data={
 'stage':'AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2',
 'contract':'R54_GREEDY_BACKEND_EQUIVALENCE_V1',
 'contract_frozen_before_gpu':True,
 'prefix_receipt_sha256':hashlib.sha256(prefix_path.read_bytes()).hexdigest(),
 'prefixes_in_fixed_order':['S0','PREFIX_HOLDOUT_2048','PREFIX_DISCOVERY_4096'],
 'arms':['F_USE_KERNELS_FALSE','H_USE_KERNELS_TRUE'],
 'clean_process_per_arm':True,
 'maximum_generated_tokens':64,
 'temperature':0,
 'natural_eos':prefix['eos_token_id'],
 'primary_gate':['exact_generated_token_ids','same_eos_stop_position','same_continuation_length',
                 'valid_cache_seq_length_progression','finite_logits'],
 'diagnostic_only':['top2_order','top8_order_and_set','selected_and_second_logit',
                    'logit_margin','max_abs_logit_difference'],
 'absolute_error_threshold':None,
 'backend_environment_receipt_sha256':hashlib.sha256((R1/'R54_V1R1_ENVIRONMENT_RECEIPT.json').read_bytes()).hexdigest(),
 'backend_toolchain':{'torch':backend['torch'],'torch_cuda':backend['torch_cuda'],
                      'transformers_commit':backend['transformers_source_commit'],
                      'kernels':backend['kernels'],
                      'mamba_revision':'20b2508ad12ae40260291539bf45183000451850',
                      'fla_revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639'},
 'on_fail':'R54_V1R2_GREEDY_BACKEND_NOT_QUALIFIED',
 'on_pass':'R54_V1R2_GREEDY_BACKEND_QUALIFIED_THEN_RESUME_R54_CONTRACT',
}
(ROOT/'R54_V1R2_PREREGISTRATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:data[k] for k in ['prefixes_in_fixed_order','primary_gate','backend_toolchain']},indent=2))
