"""Main-only passive exact spec rebinding. No budget/entry/model writes."""
import pathlib,json,hashlib,copy
P=pathlib.Path
ROOT=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_stencil_wv_20261103_v1/stencil')
MODULES=ROOT.parent/'runtime'
def ref(p):
 p=P(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def bind(original,bindings):
 s=copy.deepcopy(original)
 assert s['cohort'] in ('EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY','EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO')
 assert s['mode']=={'EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY':'W_ONLY','EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO':'WV_ZERO_RO'}[s['cohort']] and s['T'] is False and s['M'] is False
 assert len(s['expected_effective_options'])==282
 s['schema']='EP_FULL_PERF_EXACT_SPEC_V1';s['status']='MAIN_FROZEN_EXACT_ONE_START_SPEC'
 s['science_request_id']='EP_L2_WV_STENCIL_DECOMPOSITION_20261103_V1'
 for field,name in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('archive_module_ref','ep_perf_archive.py'),('postprocess_module_ref','ep_perf_postprocess.py')]:s[field]=ref(MODULES/name)
 # Exact Main reviews and current resource adapter are supplied explicitly.
 for field in ['host_qualification_ref','source_qualification_ref','eligibility_ref','resource_module_ref','resource_policy_ref']:
  assert field in bindings;s[field]=bindings[field]
 s['Main_scientific_launch_authorization']=bindings['authorization_ref']
 if 'native_entry_ref' in bindings:s['native_entry_ref']=bindings['native_entry_ref']
 s['host_cpu']=None
 s['approved_launches']=1
 # Native domain values must be read and frozen by Main at activation.
 for k in ['native_boot_id','native_mount_namespace']:s[k]=bindings[k]
 for p in MODULES.rglob('*'):
  if p.is_file():s['pinned_files'][str(p)]=ref(p)['sha256']
 assert s['expected_effective_options']==original['expected_effective_options']
 return s
