from closure_local import *
from closure_resources import UTIL,checkpoint
req=load(B/'evidence/C16_CANONICAL_SOURCE_MODELS_CURRENT_IDENTITY_AND_IMMUTABLE_RECEIPTS.json')
proof=rows(B/'references/SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv') if False else list(csv.DictReader((B/'references/SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
for alias,endpoint in [('hrl','SOURCE_PROTECTED_CANONICAL'),('hrl-174-new','TRUE164_AUTHORITY')]:
 ps=[r['path'] for r in req] if alias=='hrl' else [r['authority_alias_174new'] for r in proof]
 code=UTIL+'\npaths='+repr(ps)+'\nprint(json.dumps(dict(utc=time.time(),files=[meta(p) for p in paths],model_content_bytes_read=0)))'
 save('evidence/C16_'+endpoint+'_CURRENT_METADATA_NO_MODEL_READ.json',remote(alias,code,60))
# Existing frozen status/continuation references, without touching transaction locks/payloads.
ref='09a6b4e4d329dfde43d8cf3cc1c6bd2f3e2d2b03';p='docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/LANE_T_S_E2_EXACT_RESUME_STATUS_RECEIPT_20261020.json'
b=git('show',ref+':'+p);save('evidence/TLS_P9_LATEST_FROZEN_TRANSACTION_STATUS_NO_RESUME.json',dict(commit=ref,path=p,sha256=hashlib.sha256(b).hexdigest(),status=json.loads(b),new_resumed_transactions=0))
planned=load(B/'references/ONE_SHOT_TRUE164_RECOVERY_INDEX.json')
save('evidence/TLS_OTHER_GROUPS_EXISTING_INDEX_SCOPE_NOT_ARCHIVE_PROMOTION.json',planned)
checkpoint('P3_MODELS_AND_TLS_METADATA_END')
