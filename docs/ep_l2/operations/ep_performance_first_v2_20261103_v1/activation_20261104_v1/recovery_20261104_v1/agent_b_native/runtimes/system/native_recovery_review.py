# Read-only exact reviewed Native amendment check. No actor imports/writes.
from pathlib import Path
import json,hashlib,re
REVIEW_REF={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/agent_b_native/APPROVED_NATIVE_INSERT_REVIEW.json', 'sha256': '09eb485f3aacde4d0894aa4df9529217e543a43a518cab09b3ffdd931c018cd1'}
EXPECTED_CURRENT='2f5b5905b59d20f1e0028b57a1fd0fc098f0026833cf25e0303710e4c7c82ce2'
EXPECTED_OLD='46c69a74154e0690afd82324a348da236baf90189d9a7e474b4b14eb01ab4f0e'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def exact(r):
 b=Path(r['path']).read_bytes();need(sha(b)==r['sha256'],'review evidence drift');return b
def validate_bytes(current,review):
 need(sha(current)==EXPECTED_CURRENT,'unreviewed global Native hash')
 old=exact(review['old_ref']);new=exact(review['current_ref']);insert=exact(review['exact_insert_ref'])
 need(sha(old)==EXPECTED_OLD and current==new,'review snapshot mismatch')
 n=review['insert_after_exact_prefix_bytes'];need(current==old[:n]+insert+old[n:],'not exact insert-only historical bytes')
 need(insert==exact(review['DTC_route_block_ref']),'not exact authorized DTC route block')
 auth=json.loads(exact(review['DTC_authorization_ref']));need(auth['explicit_user_approval']is True and len(auth['budgets'])==16 and set(auth['budgets'].values())=={1},'DTC exact16 authorization')
 routed={x.decode()for x in re.findall(rb'(?:experiment|result):(E2-DTC2A16-[A-Za-z0-9-]+)',insert)};need(routed==set(auth['budgets'])==set(review['DTC_exact16_cohorts']),'route cohort scope changed')
 return dict(status='EXACT_REVIEWED_AUTHORIZED_DTC16_INSERT_ONLY_PASS',current_sha256=EXPECTED_CURRENT,old_sha256=EXPECTED_OLD,future_changes_allowed=False)
def validate_current():
 review=json.loads(exact(REVIEW_REF));return validate_bytes(Path(review['actual_global_path']).read_bytes(),review)
