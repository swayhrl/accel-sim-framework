"""Historical initial scaffold. Final package must use main_install_materialize.py."""
from pathlib import Path
import json,hashlib,os,shutil,difflib,subprocess
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');V=P/'research/performance_first_v3_20261104_v1/activation_20261104_v1';I=V/'agent_b_incident_20261104_v1';H=V/'agent_b_formal/runtime';O=P/'research/performance_first_v4_20261104_v1/track_b';R=O/'private_runtime';R.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def put(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
# Copy immutable private runtime modules, never production paths.
shutil.copytree(H,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy(I/'candidate/RUNTIME_STATIC_KEY_CONTRACT.json',R/'RUNTIME_STATIC_KEY_CONTRACT.json')
shutil.copy(I/'candidate/SOURCE862_NATIVE_RUNTIME_CLOSURE.json',R/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json')
extra=[]
for p,role in [('/bin/sh','trace child shell'),('/usr/bin/cat','trace child regular-file reader'),('/lib64/ld-linux-x86-64.so.2','kernel PT_INTERP for shell/cat'),('/lib/x86_64-linux-gnu/libc.so.6','DT_NEEDED libc.so.6 for shell/cat')]:
 extra.append(dict(path=p,resolved_path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size,role=role,historical_accepted_identity='UNKNOWN_NO_HISTORICAL_PIN',current_identity_only=True))
put(R/'TRACE_CHILD_HOST_DEPENDENCIES.json',dict(schema='EP_V4_CURRENT_TRACE_CHILD_DEPENDENCIES_V1',Source5=read(R/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json')['Source5'],separate_from_original_22=True,dependencies=extra,static_needed={p:subprocess.check_output(['readelf','-d',p],text=True) for p in ['/bin/sh','/usr/bin/cat']},scope='Current identities; no claim these caused prior failures'))
(R/'runtime_monitor_schema.py').write_text(r'''"""Source-parametric, read-only full consumer contract; never grants launch authority."""
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
 need(isinstance(s['expected_effective_options'],dict)and len(s['expected_effective_options'])==282 and all(isinstance(k,str)and isinstance(v,str)for k,v in s['expected_effective_options'].items()),'full282 option schema')
 need(s['expected_effective_options'].get('-trace')==s['trace_entry'],'input/config identity')
 need(isinstance(s['input_identity_sha256'],str)and re.fullmatch('[0-9a-f]{64}',s['input_identity_sha256']),'invalid input identity')
 need(isinstance(s['ordered_configs'],list)and len(s['ordered_configs'])>0,'invalid ordered configs')
 for r in s['ordered_configs']:need(isinstance(r,dict)and isinstance(r.get('path'),str)and isinstance(r.get('sha256'),str)and re.fullmatch('[0-9a-f]{64}',r['sha256']),'invalid ordered config ref')
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
 return dict(status='FULL_43_FIELD_PRECONSUME_SCHEMA_AND_SOURCE_CLOSURE_PASS',required_key_count=len(required),native_dependency_pins=len(native),extra_Host_dependencies=len(extra),launch_permission=False)
''')
# Fresh exact scope. Preserve all monitor/eventloop implementation.
old='EP_PERF_PFV3_VECTOR4M_';new='EP_PERF_PFV4_VECTOR4M_';goal='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104'
engine=(H/'ep_perf_native_wv_modes_draft.py').read_text().replace(old,new)
imports='from ep_perf_common_v2 import *\n'
wrapper='''from runtime_monitor_schema import validate_spec_contract as _validate_spec_contract
_SCHEMA_ROOT=P(__file__).resolve().parent
_SCHEMA_REFS='''+repr({k:ref(R/n)for k,n in [('contract_ref','RUNTIME_STATIC_KEY_CONTRACT.json'),('closure_ref','SOURCE862_NATIVE_RUNTIME_CLOSURE.json'),('extra_dependencies_ref','TRACE_CHILD_HOST_DEPENDENCIES.json')]})+'''
def validate_spec_contract(s,require_bound_cpu=False,check_current_domain=True):
    need(sha(_SCHEMA_ROOT/'runtime_monitor_schema.py')=='''+repr(sha(R/'runtime_monitor_schema.py'))+''','schema implementation drift')
    return _validate_spec_contract(s,**_SCHEMA_REFS,require_bound_cpu=require_bound_cpu,check_current_domain=check_current_domain,check_current_dependencies=True)
'''
engine=engine.replace(imports,imports+wrapper+'\n',1)
engine=engine.replace('    return s\n\n\ndef accepted_cell','    validate_spec_contract(s,check_current_domain=True)\n    return s\n\n\ndef accepted_cell',1)
engine=engine.replace("    s = dict(s, host_cpu=binding['host_cpu'])\n","    s = dict(s, host_cpu=binding['host_cpu'])\n    validate_spec_contract(s,require_bound_cpu=True,check_current_domain=True)\n",1)
engine=engine.replace("EP_MAIN_PFV3_SCOPED_USER_AUTHORIZATION_V1","EP_MAIN_PFV4_SCOPED_USER_AUTHORIZATION_V1")
engine=engine.replace("    return dict(status='EXACT_APPROVED_VECTOR1700_TWO_MODE_SCOPE_NO_OLD_BUDGET_REUSE')","    if s['mode']=='WV_ZERO_RO':\n        accepted_cell('EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1',s,q)\n    return dict(status='EXACT_APPROVED_VECTOR1700_TWO_MODE_SCOPE_NO_OLD_BUDGET_REUSE')")
(R/'ep_perf_native_wv_modes_draft.py').write_text(engine)
common=(H/'ep_perf_common_v2.py').read_text().replace(str(P/'execution_vector1700_decomposition_v3_20261104_v1/vector1700'),str(O/'private_execution/vector1700')).replace('EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104',goal)
(R/'ep_perf_common_v2.py').write_text(common)
mc=(H/'mode_contract.py').read_text().replace(old,new)
(R/'mode_contract.py').write_text(mc)
engine=engine.replace("MODE_CONTRACT_SHA='9e43b1f218124e5b4a83f385482b7bef15754f0ef12539ac4f452a326b2d52d0'","MODE_CONTRACT_SHA="+repr(sha(R/'mode_contract.py')))
(R/'ep_perf_native_wv_modes_draft.py').write_text(engine)
# Import-free CLI sole entry only invokes guarded original engine methods; no default start.
(R/'native_entry_v4.py').write_text('''"""Private fresh V4 sole entry. Requires Main native route/auth installation before use."""
import argparse,os
from ep_perf_native_wv_modes_draft import prepare,run_native
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','run']);ap.add_argument('cohort');a=ap.parse_args()
 if os.environ.get('EP_FULL_PERF_NATIVE_ENTRY')!='1':raise RuntimeError('native sole entry required')
 print((prepare if a.action=='prepare'else run_native)(a.cohort))
''')
changes=[]
for n in ['ep_perf_native_wv_modes_draft.py','ep_perf_common_v2.py','mode_contract.py']:
 changes.append(''.join(difflib.unified_diff((H/n).read_text().splitlines(True),(R/n).read_text().splitlines(True),fromfile=str(H/n),tofile=str(R/n))))
(O/'PRIVATE_RUNTIME_EXACT_DIFF.patch').write_text('\n'.join(changes))
put(O/'PRIOR_EVIDENCE_REUSE.json',dict(prior_124_tests_rerun=False,known_incident_rediagnosed=False,refs=[ref(I/'FULL_MONITOR_CONTRACT_CPU_RESULTS.json'),ref(I/'actual_process_fixture_v2/ACTUAL_PROCESS_HOST_INTEGRATION_RECEIPT.json'),ref(I/'closure_addendum_v1/DELIVERY_MANIFEST.json'),ref(I/'DELIVERY_MANIFEST.json')]))
print(json.dumps(dict(output=str(O),engine=ref(R/'ep_perf_native_wv_modes_draft.py'),schema=ref(R/'runtime_monitor_schema.py'),extra_dependencies=extra)))
