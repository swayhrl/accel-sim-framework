#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
root=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
current_path=root/'PRODUCTION_CANARY_RECEIPT.json'
attempt_path=root/'raw/production_attempt0_input_constructed_after_start/PRODUCTION_CANARY_RECEIPT.json'
restore_path=root/'R54_P2_CHECKPOINT_AUTHORITY.json'
current=json.loads(current_path.read_text())['canaries']['P2_D512']['slot_hashes'][-1]
attempt=json.loads(attempt_path.read_text())['canaries']['P2_D512']['slot_hashes'][-1]
restore=json.loads(restore_path.read_text())['checkpoint_hashes']
assert current==attempt==restore
receipt={'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2',
 'corrected_production_canary_sha256':hashlib.sha256(current_path.read_bytes()).hexdigest(),
 'attempt0_production_canary_sha256':hashlib.sha256(attempt_path.read_bytes()).hexdigest(),
 'restore_checkpoint_authority_sha256':hashlib.sha256(restore_path.read_bytes()).hexdigest(),
 'token_4096_P2_D512_checkpoint_hashes_exact_match':True,
 'gdn_layer_count':len(current),'fields_per_layer':['conv','recurrent'],
 'interpretation':'input preallocation timing repair did not alter the P2 checkpoint payload used for restore'}
(root/'CHECKPOINT_AUTHORITY_REQUAL_JOIN.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2,sort_keys=True))
