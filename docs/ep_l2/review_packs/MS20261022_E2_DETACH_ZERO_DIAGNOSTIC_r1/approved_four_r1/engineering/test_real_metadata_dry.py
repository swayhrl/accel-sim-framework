"""Actual root-sealed candidate metadata, isolated deep-copy transitions only.

No original Coordinator API, file write outside /tmp, real app/process, raw/trace
read or binary hash. Registry/Q/spec files are only read as bounded metadata.
"""
import copy,json,sys
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');sys.path[:0]=[str(HERE),str(E/'util/ep_l2/mechanism_e')]
import detach_successor as n
import detach_diagnostic_policy as dp
P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_four_r1'
d=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text());item=d['mechanism_study_20261019_v1'];old51=copy.deepcopy(item['attempts']);ref=n.file_ref(P/'FINAL_MANIFEST.json');s=n.Scope(ref);m=s.manifest();events=[]
with patch.object(n,'_SCOPE',s):
 assert s.adopt(item,d,[],dp.authority().active)
 events.append('DEEP_COPY_ADOPT_EXACT_APPROVED_FOUR')
 for cid in n.CONDITIONS:
  c=m['conditions'][cid];spec=n.read(c['spec_ref']);q=n.read(c['qualification']);s.check_spec(spec)
  qid=c['qualification']['sha256'];item['qualifications'][qid]=dict(path=c['qualification']['path'],sha256=qid,qualification=q)
  s.bind(item,spec,dp.authority().active);s.active(item,dp.authority().active)
  n.prepare_validator(item['qualifications'][qid],spec,None)
  assert n.qualification(q,None)
  events.append('DEEP_COPY_EXACT_Q_BIND_'+cid)
 assert item['attempts']==old51 and item['actual_starts']==51
 assert s.crosscheck(d,item,dp.authority().active,dp._legacy_crosscheck_data)
report=dict(status='PASS_ACTUAL_METADATA_DEEP_COPY_ADOPT_BIND_AND_REAL_SHARED_ADAPTER_CHECKS',manifest_ref=ref,steps=events,real_new_registrations=0,real_new_starts=0,source_CLIENT_registry_controller_changed=False,root_scientific_qualification_claim='Existing root Q read only; this control validates metadata interface compatibility, not new application completion',actual_original51_untouched=True)
(HERE/'REAL_METADATA_DRY_CONTROL.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'steps':len(events)}))
