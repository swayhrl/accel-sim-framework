"""Actual completed IO canary plus three read-only negative-chain replays."""
import copy,hashlib,json,pathlib
from unittest.mock import patch
import io_chain_audit as m
P=pathlib.Path;HERE=P(__file__).resolve().parent
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
c='E2-DTCL2MLP-2b93f70cd0666c51-DH-F256-V1';result=m.read(R/'analysis'/(c+'.RESULT.json'))
v=m.audit(R,c,result);assert v['status']=='PASS_READONLY_IO_AND_ORIGINAL_STRICT_CHAIN';checks=['actual_closed_IO_canary_binding_chain_AND_padding_verified_readonly']
oldread=m.read
def changed(p):
 value=oldread(p)
 if P(p).name=='NATIVE_LAUNCH.json':value['additional_shared_json_io_binding']['snapshot_sha256']='WRONG'
 return value
with patch.object(m,'read',side_effect=changed):
 try:m.audit(R,c,result)
 except AssertionError:pass
 else:raise AssertionError('mismatched IO binding accepted')
checks.append('launch_intent_PID_binding_mismatch_rejected')
bad=copy.deepcopy(result);bad['proof']['additional_shared_json_io_strict']['sidecar_sha256']='WRONG'
try:m.audit(R,c,bad)
except AssertionError:pass
else:raise AssertionError('sidecar SHA mismatch accepted')
checks.append('extra_IO_strict_sidecar_SHA_mismatch_rejected')
bad=copy.deepcopy(result);bad['proof'].pop('additional_padding_admission_strict',None)
try:m.audit(R,c,bad)
except KeyError:pass
else:raise AssertionError('padding AND missing accepted')
checks.append('padding_AND_required_cannot_be_omitted')
out=dict(status='PASS',checks=checks,count=len(checks),source_sha256=hashlib.sha256((HERE/'io_chain_audit.py').read_bytes()).hexdigest(),
 actual_canary_cohort=c,actual_RESULT_sha256=hashlib.sha256((R/'analysis'/(c+'.RESULT.json')).read_bytes()).hexdigest(),production_changes=0,model_starts=0,signals=0)
(HERE/'IO_AUDIT_CPU_AND_ACTUAL_QUALIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
