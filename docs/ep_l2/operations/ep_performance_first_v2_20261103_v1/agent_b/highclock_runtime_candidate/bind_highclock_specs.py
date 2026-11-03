"""Pure exact newSource six-cell binder. No authority/native/process writes."""
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent/'runtime'
REQUEST='EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'
def ref(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def bind(draft,bindings):
 s=copy.deepcopy(draft);scope=json.loads((R/'FAMILY_SCOPE.json').read_text());r=next(r for r in scope['points']if r['cohort']==s['cohort']);assert s['source_identity']==r['source5']
 s.update(schema='EP_FULL_PERF_EXACT_SPEC_V1',goal='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1',science_request_id=REQUEST,application_budget=1,automatic_retry=False,refund=False,source_keep=True,old_application_acceptance_inherited=False,host_cpu=None,approved_launches=1)
 for field,name in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('archive_module_ref','ep_perf_archive.py'),('postprocess_module_ref','ep_perf_postprocess.py')]:s[field]=ref(R/name)
 for field in ['source_qualification_ref','mode_cpu_qualification_ref','host_qualification_ref','eligibility_ref','resource_module_ref','resource_policy_ref','native_boot_id','native_mount_namespace']:assert field in bindings,field;s[field]=bindings[field]
 s['ro_qualification_ref']=bindings['ro_qualification_ref']if s['mode']=='F'else None
 s['Main_scientific_launch_authorization']=bindings['authorization_ref']
 if 'native_entry_ref'in bindings:s['native_entry_ref']=bindings['native_entry_ref']
 for field in ['matched_S_anchor_qualification_ref','absolute_REF850_S_anchor_qualification_ref','absolute_REF850_spec_ref']:s.pop(field,None)
 for p in R.rglob('*'):
  if p.is_file():s['pinned_files'][str(p)]=ref(p)['sha256']
 assert s['expected_effective_options']==draft['expected_effective_options']and s['ordered_configs']==draft['ordered_configs']
 return s
