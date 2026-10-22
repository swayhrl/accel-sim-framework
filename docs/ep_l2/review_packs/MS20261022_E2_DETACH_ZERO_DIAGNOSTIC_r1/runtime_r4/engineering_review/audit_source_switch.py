#!/usr/bin/env python3
"""Bounded read-only metadata guard; not a runtime resource admission."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'runtime'))
from detach_scope_core import old_seal,ACTIVE
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
d=json.loads(REG.read_text());i=d['mechanism_study_20261019_v1'];campaign='EPL2_MECHANISM_STUDY_20261019_V1'
scientific=[dict(v, registry_run_key=k) for k,v in d['runs'].items() if v.get('experiment_id')==campaign and v.get('status') in ACTIVE]
helpers=[dict(v, registry_lease_id=k) for k,v in d['resource_leases'].items() if v.get('experiment_id')==campaign and v.get('status') in ACTIVE]
# All active helpers using this campaign API are source-switch blockers until
# completion or explicit evidence that they never imported it. Role is not proof.
r=dict(status='QUIESCENT_METADATA_ONLY' if i['controller']['state']=='STOPPED' and i['actual_starts']==50 and not scientific and not helpers else 'SOURCE_SWITCH_NOT_READY',controller=i['controller'],actual_starts=i['actual_starts'],scientific_blockers=scientific,helper_dependency_review=helpers,old50seal=old_seal(i),registry_sha256=hashlib.sha256(REG.read_bytes()).hexdigest(),locks_acquired=False,resources_admitted=False,notes=['No independent C/A engineering lease is classified as scientific-scope violation.','For source activation, an old imported E API helper must retire even if role A/C; unknown dependence blocks activation.','Unrelated-project leases retain original resource accounting; never alter them.','Root must use original CONTROLLER.lock and central API transactional recheck.'])
(HERE/'SOURCE_SWITCH_READONLY.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':r['status'],'scientific_blockers':len(scientific),'same_campaign_helpers':len(helpers)}))
