"""Pure binder into independent SYSTEM850 runtime. Main alone installs/registers."""
from pathlib import Path
import copy,json,hashlib
R=Path(__file__).resolve().parent/'runtime'
GOAL='EP_L2_SYSTEM_850MHZ_PARAMETER_FAMILY_V2_20261104_V1'
def ref(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def bind(config_draft,bindings):
 scope=json.loads((R/'FAMILY_SCOPE.json').read_text());r=next(x for x in scope['points']if x['id']==config_draft['cohort'])
 assert config_draft['expected_effective_options']==json.loads(Path(r['option_preview_ref']['path']).read_text()),'draft options changed'
 base=json.loads(Path(r['old_REF850_spec_ref']['path']).read_text());s=copy.deepcopy(base)
 s.update(schema='EP_FULL_PERF_EXACT_SPEC_V1',goal='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1',science_request_id=GOAL,cohort=r['id'],profile='PFV2_SYSTEM850_'+r['family'],mode=r['mode'],M=False,T=False,geometry=r['geometry'],expected_effective_options=config_draft['expected_effective_options'],system_family_point_id=r['id'],system_family_proposal_ref=scope['proposal_ref'],absolute_REF850_spec_ref=r['old_REF850_spec_ref'],REF850_usage='ABSOLUTE_REFERENCE_ONLY_NOT_SAME_BACKGROUND_S',status='MAIN_BOUND_EXACT_ONE_START_SPEC_NOT_AUTHORITY_BY_ITSELF',application_budget=1,automatic_retry=False,refund=False,source_keep=True,host_cpu=None,approved_launches=1,old_application_acceptance_inherited=False,ro_qualification_ref=None)
 peers=[p for p in scope['points']if p['input_identity_sha256']==r['input_identity_sha256']and p['family']==r['family']and p['mode']!=r['mode']];assert len(peers)==1
 s['same_background_peer_cohort']=peers[0]['id'];overlay=R/'configs'/s['cohort']/'final_system850.config'
 assert overlay.read_bytes()==Path(r['final_overlay_ref']['path']).read_bytes()
 s['ordered_configs']=base['ordered_configs']+[ref(overlay)];s['system_final_overlay_ref']=ref(overlay)
 for field,name in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('archive_module_ref','ep_perf_archive.py'),('postprocess_module_ref','ep_perf_postprocess.py')]:s[field]=ref(R/name)
 for field in ['host_qualification_ref','mode_cpu_qualification_ref','source_qualification_ref','eligibility_ref','resource_module_ref','resource_policy_ref','absolute_REF850_S_anchor_qualification_ref','absolute_REF850_EP_anchor_qualification_ref','native_boot_id','native_mount_namespace']:
  assert field in bindings,field;s[field]=bindings[field]
 s['Main_scientific_launch_authorization']=bindings['authorization_ref']
 if 'native_entry_ref'in bindings:s['native_entry_ref']=bindings['native_entry_ref']
 s.pop('matched_S_anchor_qualification_ref',None)
 s['pinned_files']={p:h for p,h in base['pinned_files'].items()if '/env/lib/'in p or '/common-lib/'in p}
 for field in ['helpers_ref','output_module_ref','compact_module_ref','resource_module_ref','resource_policy_ref']:
  x=s[field];s['pinned_files'][x['path']]=x['sha256']
 for p in R.rglob('*'):
  if p.is_file()and p.suffix!='.pyc':s['pinned_files'][str(p)]=ref(p)['sha256']
 assert s['source_identity']==base['source_identity']and s['expected_effective_options']==config_draft['expected_effective_options']
 return s
