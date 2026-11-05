"""Exact single-Source 283-option template. Unregistered sources/profiles fail closed; no launch authority."""
from pathlib import Path
import json,hashlib,re,os

def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def exact(r):
 need(isinstance(r,dict) and isinstance(r.get('path'),str) and re.fullmatch('[0-9a-f]{64}',r.get('sha256','')),'invalid immutable reference')
 need(sha(r['path'])==r['sha256'],'immutable reference drift '+r['path']);return read(r['path'])
def validate_spec_contract(s,contract_ref,closure_ref,require_bound_cpu=False,check_current_domain=False,check_current_dependencies=False,extra_dependencies_ref=None):
 contract=exact(contract_ref);closure=exact(closure_ref)
 need(contract.get('schema')=='EP_V5_ONE_SOURCE283_CONSUMER_CONTRACT_V1' and contract.get('review_status')=='MAIN_REVIEWED_EXACT_SOURCE283' and contract.get('scope')=='EXACT_ONE_SOURCE283_ONLY' and contract.get('option_count')==283,'Source283 template not qualified')
 need(contract.get('Source5')==closure['Source5']==s.get('source_identity'),'exact new Source5 contract required')
 profile=s.get('source_feature_profile')
 need(type(profile)is str and profile in contract.get('expected_283_maps_by_profile',{}),'unreviewed Source283 feature profile')
 expected=exact(contract['expected_283_maps_by_profile'][profile])
 need(type(expected)is dict and len(expected)==283 and s.get('expected_effective_options')==expected,'Source283 complete map mismatch')
 feature=contract.get('declared_feature_options')
 need(type(feature)is list and len(feature)>0 and all(type(x)is str and x in expected for x in feature),'explicit feature whitelist required')
 base=exact(contract['same_mode_feature_off_283_map_by_profile'][profile])
 need(len(base)==283 and {k:v for k,v in expected.items()if k not in feature}=={k:v for k,v in base.items()if k not in feature},'undeclared Source283 feature-on background change')
 q=exact(contract['production_CPU_review_ref'])
 need(q.get('approved_by')=='EP-MAIN' and q.get('Source5')==s['source_identity'] and profile in q.get('closed_profiles',[]) and q.get('application_model_started')is False,'exact production CPU review absent')
 receipt=exact(q['actual_constructor_receipt_ref'])
 need(profile in q.get('actual_constructed_283_map_refs',{}) and exact(q['actual_constructed_283_map_refs'][profile])==expected,'actual constructed283 profile map mismatch')
 need(q.get('actual_constructor_source_key')in['Source5','source_identity'] and receipt.get(q['actual_constructor_source_key'])==s['source_identity'],'actual constructor Source5 mismatch')
 need(q.get('actual_constructor_receipt_schema')==receipt.get('schema') and q.get('review_boundary')=='EXACT_SOURCE283_CONSTRUCTOR_AND_FEATURE_CONTRACT_ONLY','actual constructor review binding')
 required=contract['required_keys'];need(len(required)==43 and len(set(required))==43,'43-field consumer contract required')
 missing=sorted(set(required)-set(s));need(not missing,'missing required runtime fields: '+','.join(missing))
 for k in ['binary_path','cohort','goal','mode','schema','static_library_path','trace_entry']:
  need(isinstance(s[k],str) and bool(s[k]),'invalid string field '+k)
 for k in ['T','M','automatic_retry','source_keep']:
  need(type(s[k])is bool,'invalid boolean field '+k)
 need(s['automatic_retry']is False and s['source_keep']is True,'source KEEP/no retry contract')
 for k in ['application_budget','approved_launches','estimated_peak_RAM_bytes']:
  need(type(s[k])is int and s[k]>0,'invalid positive integer '+k)
 need(s['application_budget']==s['approved_launches']==1,'one-start proposal contract')
 need(isinstance(s['same_background_peer_cohort'],str) and s['same_background_peer_cohort']!=s['cohort'],'invalid peer cohort')
 need(isinstance(s['native_boot_id'],str) and re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}',s['native_boot_id']) is not None,'invalid native_boot_id')
 need(isinstance(s['native_mount_namespace'],str) and re.fullmatch(r'mnt:\[[0-9]+\]',s['native_mount_namespace']) is not None,'invalid native_mount_namespace')
 if check_current_domain:
  need(s['native_boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'native boot changed before consume')
  need(s['native_mount_namespace']==os.readlink('/proc/self/ns/mnt'),'native mount namespace changed before consume')
 if require_bound_cpu:need(type(s['host_cpu'])is int and s['host_cpu'] in os.sched_getaffinity(0),'dispatch CPU binding missing/unavailable')
 else:need(s['host_cpu']is None or type(s['host_cpu'])is int and s['host_cpu']>=0,'invalid dispatch CPU type')
 need(isinstance(s['limits'],dict),'invalid limits')
 for k in ['AS_bytes','RSS_bytes','wall_seconds','result_bytes']:need(type(s['limits'].get(k))is int and s['limits'][k]>0,'missing/invalid runtime hard limit '+k)
 need(s['limits']['AS_bytes']>=s['limits']['RSS_bytes'],'AS below RSS')
 need(isinstance(s['source_identity'],dict),'invalid Source5')
 for k in ['binary_sha256','archive_sha256','core_source_commit','framework_source_commit','vendor_pybind11_commit']:
  need(isinstance(s['source_identity'].get(k),str) and re.fullmatch('[0-9a-f]{'+str(64 if k.endswith('sha256')else 40)+'}',s['source_identity'][k]),'invalid Source5 '+k)
 need(s['source_identity']==closure['Source5'],'runtime closure belongs to different Source5')
 need(isinstance(s['pinned_files'],dict),'invalid pinned_files')
 for p,h in s['pinned_files'].items():need(isinstance(p,str)and p.startswith('/')and isinstance(h,str)and re.fullmatch('[0-9a-f]{64}',h),'invalid path/SHA pin')
 native=closure['pinned_files'];missing_pins={p:h for p,h in native.items()if s['pinned_files'].get(p)!=h}
 need(not missing_pins,'missing/mismatched native runtime dependency pins: '+','.join(sorted(missing_pins)))
 refs=['Main_scientific_launch_authorization','eligibility_ref','helpers_ref','host_common_ref','host_engine_ref','host_qualification_ref','input_binding_ref','mode_contract_ref','native_entry_ref','native_route_guard_ref','output_module_ref','resource_module_ref','resource_policy_ref','source_qualification_ref','validation_module_ref']
 for k in refs:
  r=s[k];need(isinstance(r,dict)and isinstance(r.get('path'),str)and r['path'].startswith('/')and isinstance(r.get('sha256'),str)and re.fullmatch('[0-9a-f]{64}',r['sha256']),'invalid reference field '+k)
 need(s['ro_qualification_ref']is None or isinstance(s['ro_qualification_ref'],dict),'invalid RO reference')
 need((s['T']or s['M'])or s['ro_qualification_ref']is None,'RO-disabled mode inherited certificate')
 for k in ['core','framework']:need(isinstance(s['source_worktrees'],dict)and isinstance(s['source_worktrees'].get(k),str)and s['source_worktrees'][k].startswith('/'),'invalid source_worktrees '+k)
 need(isinstance(s['observer_env'],dict)and all(isinstance(k,str)and isinstance(v,str)for k,v in s['observer_env'].items()),'invalid observer environment')
 need(isinstance(s['expected_effective_options'],dict)and len(s['expected_effective_options'])==283 and all(isinstance(k,str)and k.startswith('-')and isinstance(v,str)and (bool(v.strip())or k in contract.get('allowed_empty_options',[]))for k,v in s['expected_effective_options'].items()),'full283 Source-specific option schema')
 need(s['expected_effective_options'].get('-trace')==s['trace_entry'],'input/config identity')
 need(isinstance(s['input_identity_sha256'],str)and re.fullmatch('[0-9a-f]{64}',s['input_identity_sha256']),'invalid input identity')
 need(isinstance(s['ordered_configs'],list)and len(s['ordered_configs'])>0,'invalid ordered configs')
 for r in s['ordered_configs']:need(isinstance(r,dict)and isinstance(r.get('path'),str)and r['path'].startswith('/')and isinstance(r.get('sha256'),str)and re.fullmatch('[0-9a-f]{64}',r['sha256']),'invalid ordered config ref')
 need(isinstance(s['all_unique_kernel_members'],list)and len(s['all_unique_kernel_members'])>0,'invalid full input members')
 for m in s['all_unique_kernel_members']:need(isinstance(m.get('path'),str)and isinstance(m.get('member'),str)and type(m.get('size'))is int and m['size']>0 and isinstance(m.get('sha256'),str)and re.fullmatch('[0-9a-f]{64}',m['sha256']),'invalid member schema')
 extra=[]
 if extra_dependencies_ref:
  e=exact(extra_dependencies_ref);need(e['Source5']==s['source_identity'],'extra dependencies different Source5');extra=e['dependencies']
  for d in extra:
   need(s['pinned_files'].get(d['path'])==d['sha256'],'extra Host dependency pin missing '+d['path'])
   if check_current_dependencies:need(str(Path(d['path']).resolve())==d['resolved_path'] and sha(d['path'])==d['sha256'],'extra Host dependency identity drift '+d['path'])
 if check_current_dependencies:
  for p,h in native.items():need(sha(p)==h,'current native dependency drift '+p)
 return dict(status='FULL_43_FIELD_PRECONSUME_SCHEMA_AND_SOURCE_CLOSURE_PASS',option_count=283,source_feature_profile=profile,required_key_count=len(required),native_dependency_pins=len(native),extra_Host_dependencies=len(extra),launch_permission=False)
