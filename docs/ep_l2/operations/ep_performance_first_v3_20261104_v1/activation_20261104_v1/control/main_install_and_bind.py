from pathlib import Path
import json,hashlib,copy,datetime,os,uuid,fcntl,subprocess
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');V=J/'research/performance_first_v3_20261104_v1';A=V/'activation_20261104_v1';C=A/'control';N=Path('/root/data/ep_l2_dtc_l1_native_v2');REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def exact(r):assert sha(r['path'])==r['sha256'],r['path'];return read(r['path'])
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();t=p.with_name('.'+p.name+'.'+str(uuid.uuid4()))
 with t.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 os.replace(t,p);fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
 return ref(p)
def remaining(r):
 if 'remaining'in r:return r['remaining']
 q=r.get('consumed',0);return max(0,r.get('budget',0)-(q if type(q)is int else len(q)))
m=read(C/'EXACT_EXECUTION_MANIFEST.json');auth=exact(m['user_authorization_ref']);assert auth['explicit_user_approval']and auth['global_EP_model_cap']==10
nativeq=read(A/'agent_d_execution/FORMAL_NATIVE_CPU_HOST_QUALIFICATION.json');assert nativeq['status']=='PASS'
resourceq=read(A/'agent_c_resources/CPU_RESOURCE_QUALIFICATION.json');assert resourceq['status']=='PASS'and set(resourceq['qualified_global_EP_caps'])=={2,10}
entry=N/'bin/native';candidate=A/'agent_d_execution/GLOBAL_NATIVE_EXACT10_CANDIDATE.sh';pre=A/'agent_d_execution/GLOBAL_NATIVE_PREIMAGE_530.sh';header=b'#!/bin/sh\nset -eu\n';old=pre.read_bytes();new=candidate.read_bytes();assert old.startswith(header)and new.startswith(header)
assert new.endswith(old[len(header):]) and len(new)>len(old);added=new[len(header):len(new)-len(old)+len(header)]
assert b'EP_PERF_PFV3_'in added and b'E2-DTC'in old and b'E2-DTC'not in added
assert sha(candidate)=='a7a9a1d77dc8fb3680cd57c925b2e4f56fdc46cbfe94861c67ed377a5cd370fa'
subprocess.run(['/bin/sh','-n',str(candidate)],check=True)
# Active foreign entry compatibility: none of its source pins contains shared bin/native.
plan=read('/root/data/dtc_stage_iia_remaining48_20261104_v1/control/EXECUTION_PLAN.json');assert all(Path(r['path'])!=entry for r in plan['source_pins'])
foreign_proof=dict(status='READ_ONLY_DTC48_ENTRY_COMPATIBILITY_REVIEW_PASS',utc=now(),plan_ref=ref('/root/data/dtc_stage_iia_remaining48_20261104_v1/control/EXECUTION_PLAN.json'),foreign_shared_native_hash_pin=False,experiment_wrapper_ref=ref(N/'bin/experiment'),existing_global_suffix_bytes_preserved=True,foreign_source_or_process_changes=False)
put(C/'FOREIGN_ENTRY_COMPATIBILITY_REVIEW.json',foreign_proof)
route_receipts={}
for group,g in m['groups'].items():
 root=Path(g['data_root']);runtime=Path(g['runtime_root']);slist=[exact(p['spec_ref'])for p in m['points']if p['group']==group]
 assert len(slist)==g['budget'] and all(s['source_identity']==next(f['Source5']for f in auth['families']if f['name']==group)for s in slist)
 paths={}
 def add(p):
  p=Path(p)
  assert p.is_file()and not p.is_symlink(),str(p)
  assert p.stat().st_size<16*1024*1024,str(p)
  paths[str(p)]=ref(p)
 for p in runtime.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts and p.suffix in ['.py','.json']:add(p)
 for s in slist:
  for key,value in s.items():
   if key.endswith('_ref')and isinstance(value,dict)and'path'in value and (key.endswith('_module_ref')or key in ['host_engine_ref','host_common_ref','helpers_ref','validation_module_ref','postprocess_module_ref','mode_contract_ref','native_route_guard_ref','resource_policy_ref','mode_cpu_qualification_ref','host_qualification_ref','eligibility_ref','source_qualification_ref']):
    assert sha(value['path'])==value['sha256'];add(value['path'])
  host=exact(s['host_qualification_ref'])
  for r in host['modules']:assert sha(r['path'])==r['sha256'];add(r['path'])
 for p in [A/'native/native_v3.py',A/'agent_d_execution/native_route_guard_v3.py',A/'agent_d_execution/safe_native_core_v3.py',A/'agent_c_resources/resources_v3.py']:
  add(p)
 r=dict(schema='EP_MAIN_PFV3_MAIN_INSTALLED_SCOPED_NATIVE_ROUTE_V1',status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',approved_by='EP-MAIN',scientific_scope_activated=True,goal=g['request_id'],entry_ref=g['native_entry_ref'],frontend_ref=ref(runtime/'ep_perf_frontend.py'),guard_module_ref=ref(A/'agent_d_execution/native_route_guard_v3.py'),exact_cohorts=sorted(s['cohort']for s in slist),global_shared_native_ref=dict(path=str(entry),sha256=sha(candidate)),shared_route_contract_ref=ref(A/'agent_d_execution/SHARED_ROUTE_CONTRACT_V3.json'),owned_runtime_pins=list(paths.values()),Main_user_authorization_ref=m['user_authorization_ref'],formal_Native_CPU_Host_qualification_ref=ref(A/'agent_d_execution/FORMAL_NATIVE_CPU_HOST_QUALIFICATION.json'),resource_qualification_ref=ref(A/'agent_c_resources/CPU_RESOURCE_QUALIFICATION.json'),application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN',Source_KEEP=True)
 path=root/'control/NATIVE_ENTRY_ROUTE_V3.json';assert not path.exists();route_receipts[group]=put(path,r)
 claims=root/'control/DISPATCH_CLAIMS.json'
 if not claims.exists():put(claims,dict(claims={}))
 assert read(claims)==dict(claims={})
with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b')as lock,(N/'control/science_authority/NATIVE_ROUTE_UPDATE.lock').open('a+b')as route_lock:
 fcntl.flock(lock,fcntl.LOCK_EX);fcntl.flock(route_lock,fcntl.LOCK_EX)
 r=read(REG);e=read(EPOCH);assert sha(REG)==e['native_registry_sha256'];before=copy.deepcopy(r);old_epoch=copy.deepcopy(e)
 for p in [REG,EPOCH]:
  archive=N/'control/science_authority/request_history'/(p.stem+'.'+sha(p)+'.json')
  if not archive.exists():archive.write_bytes(p.read_bytes())
 assert entry.read_bytes()==old,'Native changed: HOLD CAS, do not overwrite foreign update'
 # Atomically install only the qualified additive exact10 route. No old line is changed.
 tmp=entry.with_name('.native.V3.'+str(uuid.uuid4()))
 with tmp.open('xb')as h:h.write(new);h.flush();os.fsync(h.fileno())
 tmp.chmod(entry.stat().st_mode&0o777);assert entry.read_bytes()==old,'Native changed before CAS';os.replace(tmp,entry)
 fd=os.open(entry.parent,os.O_RDONLY);os.fsync(fd);os.close(fd);assert entry.read_bytes()==new
 for group,g in m['groups'].items():
  q=r['registered_future_requests'][g['request_id']];assert not q['consumed']and q['budget']==q['remaining']==g['budget']and not q['admitted_specs']
  q['admitted_specs']={p['cohort']:p['spec_ref']['sha256']for p in m['points']if p['group']==group};q['native_entry_ref']=g['native_entry_ref'];q['native_qualification_ref']=route_receipts[group];q['Main_manifest_ref']=ref(C/'EXACT_EXECUTION_MANIFEST.json');q['state']='ARMED';q['global_model_concurrency_qualified']=10
  rt=Path(g['runtime_root']);engine=rt/'ep_perf_native_wv_modes_draft.py';q['runtime_versions'][sha(engine)]=dict(common_ref=ref(rt/'ep_perf_common_v2.py'),engine_ref=ref(engine));q['Main_activated_utc']=now()
 for key,value in before['registered_future_requests'].items():
  if key not in [g['request_id']for g in m['groups'].values()]:assert r['registered_future_requests'][key]==value,'foreign/old row mutation'
 assert {k:x for k,x in r.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}=={k:x for k,x in before.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}
 r['new_scientific_budget_remaining']=sum(remaining(q)for q in r['registered_future_requests'].values());put(REG,r)
 e['native_registry_sha256']=sha(REG);e['new_budget_remaining']=r['new_scientific_budget_remaining'];e['request_revision']=dict(request_id=[g['request_id']for g in m['groups'].values()],operation='MAIN_V3_INSTALL_QUALIFIED_ADDITIVE_NATIVE_AND_BIND_EXACT8_PLUS2_SPECS',utc=now());put(EPOCH,e)
 receipt=dict(schema='EP_MAIN_V3_FORMAL_NATIVE_AND_SPEC_INSTALLATION_V1',utc=now(),status='NATIVE_AND_EXACT10_SPECS_REGISTERED_ARMED_NOT_CONSUMED',global_before=ref(pre),global_after=ref(entry),route_refs=route_receipts,manifest_ref=ref(C/'EXACT_EXECUTION_MANIFEST.json'),registry_ref=ref(REG),epoch_ref=ref(EPOCH),foreign_old_rows_preserved=True,old_budgets_preserved=True,scientific_starts=0,source_and_ELF_unchanged=True,qualified_global_EP_cap=10)
 put(C/'MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json',receipt)
print(json.dumps(receipt,indent=2))
