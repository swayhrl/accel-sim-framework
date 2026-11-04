from pathlib import Path
import hashlib,importlib.util,json,os,sys,shutil,subprocess,datetime
sys.dont_write_bytecode=True
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');A=P/'research/performance_first_v4_20261104_v1/track_a';O=Path(__file__).resolve().parent;OLD=A/'private_main_integration';B=P/'research/performance_first_v4_20261104_v1/track_b/private_runtime'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text())
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
helper=Path(sys.argv[1]);helper_sha=sys.argv[2];assert sha(helper)==helper_sha
oldindex=read(OLD/'PRIVATE_GRAPH_INDEX.json');closure=read(OLD/'SOURCE78_NATIVE_CLOSURE.json');extra=read(OLD/'SOURCE78_HELPER_DEPENDENCIES.json');graphs=[];snapshot_receipts=[]
for old in oldindex['graphs']:
 lane=old['lane'];R=O/lane;H=R/'runtime';E=R/'execution';OH=Path(old['runtime']);OE=Path(old['execution'])
 def remap(x):
  if isinstance(x,str):return x.replace(str(OH),str(H)).replace(str(OE),str(E))
  if isinstance(x,list):return [remap(v)for v in x]
  if isinstance(x,dict):return {remap(k):remap(v)for k,v in x.items()}
  return x
 shutil.copytree(OH,H,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(OE,E,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
 # Rebind source paths only; monitor functions, dispatcher control and pure geometry/parser code remain unchanged.
 scope=remap(read(OH/'FAMILY_SCOPE.json'));write(H/'FAMILY_SCOPE.json',scope)
 oldmode=sha(OH/'mode_contract.py');oldterminal=sha(OH/'mode_aware_terminal.py')
 t=(H/'mode_contract.py').read_text().replace(sha(OH/'FAMILY_SCOPE.json'),sha(H/'FAMILY_SCOPE.json'));(H/'mode_contract.py').write_text(t)
 t=(H/'mode_aware_terminal.py').read_text().replace(oldmode,sha(H/'mode_contract.py'));(H/'mode_aware_terminal.py').write_text(t)
 for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','native_request2']:
  t=(H/n).read_text().replace(str(OH),str(H)).replace(str(OE),str(E))
  if n=='ep_perf_native_wv_modes_draft.py':t=t.replace(oldmode,sha(H/'mode_contract.py')).replace(oldterminal,sha(H/'mode_aware_terminal.py'))
  (H/n).write_text(t)
 (H/'native_request2').chmod(0o755)
 wrapper=H/'resources_request2.py'
 wrapper.write_text('''# Exact Source78 request2 resource wiring; Main-owned additive helper, read-only API.
import pathlib,hashlib,importlib.util
PATH=pathlib.Path('''+repr(str(helper))+''');SHA='''+repr(helper_sha)+''';REQUEST='''+repr(old['request_id'])+'''
def shared():
    if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('Main V4 resource dependency drift')
    sp=importlib.util.spec_from_file_location('Main_v4_exact_resources',PATH);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
    if s.get('current_request')!=REQUEST:raise ValueError('cross-family resource snapshot')
    return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
''')
 # Remap private control documents and refresh all runtime path/pin carriers.
 for n in ['EXACT_REQUEST.json','MODE_CPU_EVIDENCE_REBIND.json','SOURCE_CPU_EVIDENCE_REBIND.json']:
  write(E/'control'/n,remap(read(OE/'control'/n)))
 auth=remap(read(OE/'control/USER_AUTHORIZATION.json'));auth['request_ref']=ref(E/'control/EXACT_REQUEST.json');write(E/'control/USER_AUTHORIZATION.json',auth)
 modules=[ref(p)for p in sorted(H.rglob('*'))if p.is_file()and '__pycache__'not in str(p)]+[ref(B/'runtime_monitor_schema_v4_strict.py'),ref(B/'RUNTIME_FULL_43_CONTRACT_V4.json'),ref(helper)]
 hq=remap(read(OE/'control/HOST_DELTA_QUALIFICATION_CANDIDATE.json'));hq['modules']=modules;hq['prior_private_hostq_ref']=old['hostq_ref'];hq['resource_wiring_revision']='MAIN_ADDITIVE_V4_NEW_SCOPE_AND_EXACT_NEW_CONSUMPTION_ROOT'
 hq['prior_qualification_limit']='Old full43/monitor/parser qualification did not cover resource snapshot unknown V3 scope defect; defect reproduced explicitly in follow-up.'
 write(E/'control/HOST_DELTA_QUALIFICATION_CANDIDATE.json',hq)
 candidates=[]
 for oldref in old['candidate_specs']:
  s=remap(read(oldref['path']));s['prior_frozen_private_spec_ref']=oldref;s['final_consumer_execution_ROOT']=str(E)
  for field,name in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('native_entry_ref','native_request2'),('native_route_guard_ref','native_route_guard_v3.py'),('resource_module_ref','resources_request2.py'),('postprocess_module_ref','ep_perf_postprocess.py'),('archive_module_ref','ep_perf_archive.py')]:s[field]=ref(H/name)
  for field,name in [('Main_scientific_launch_authorization','USER_AUTHORIZATION.json'),('host_qualification_ref','HOST_DELTA_QUALIFICATION_CANDIDATE.json'),('source_qualification_ref','SOURCE_CPU_EVIDENCE_REBIND.json'),('mode_cpu_qualification_ref','MODE_CPU_EVIDENCE_REBIND.json')]:s[field]=ref(E/'control'/name)
  s['native_boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip();s['native_mount_namespace']=os.readlink('/proc/self/ns/mnt')
  s['pinned_files']=closure['pinned_files'].copy()
  for d in extra['dependencies']:s['pinned_files'][d['path']]=d['sha256']
  for d in modules:s['pinned_files'][d['path']]=d['sha256']
  s['pinned_files'][str(E/'control/HOST_DELTA_QUALIFICATION_CANDIDATE.json')]=sha(E/'control/HOST_DELTA_QUALIFICATION_CANDIDATE.json')
  path=E/'cases'/s['cohort']/'control/FROZEN_SPEC.json';write(path,s);candidates.append(ref(path))
 route=remap(read(OE/'control/NATIVE_ENTRY_ROUTE_V4.json'));route.update(entry_ref=ref(H/'native_request2'),guard_module_ref=ref(H/'native_route_guard_v3.py'),frontend_ref=ref(H/'ep_perf_frontend.py'),owned_runtime_pins=modules);write(E/'control/NATIVE_ENTRY_ROUTE_V4.json',route)
 g=dict(lane=lane,request_id=old['request_id'],root=str(R),runtime=str(H),execution=str(E),candidate_specs=candidates,entry_ref=ref(H/'native_request2'),hostq_ref=ref(E/'control/HOST_DELTA_QUALIFICATION_CANDIDATE.json'),resource_wrapper_ref=ref(wrapper),Main_helper_ref=ref(helper),prior_frozen_graph=old,requested_starts=2,actual_approved_registered_consumed_starts=0,installed=False)
 # Real readonly snapshot now consumes exactly the wrapper and ROOT selected by the new Specs.
 sp=importlib.util.spec_from_file_location('resource_delta_'+lane,wrapper);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);snap=m.snapshot()
 assert snap['current_request']==g['request_id']and snap['resource_admission_is_not_science_permission']is True
 p=R/'ACTUAL_READONLY_RESOURCE_SNAPSHOT.json';write(p,dict(status='REAL_SNAPSHOT_RETURNED_NO_UNKNOWN_SCOPE',resource_wrapper_ref=ref(wrapper),Main_helper_ref=ref(helper),final_consumer_execution_ROOT=str(E),snapshot=snap,admission_executed=False,science_permission=False))
 g['actual_snapshot_ref']=ref(p);graphs.append(g)
write(O/'FINAL_CONSUMER_GRAPH_INDEX.json',dict(schema='EP_PFV4_SOURCE78_FINAL_RESOURCE_AND_CONSUMER_ROOT_GRAPH_V2',status='FINAL_SELECTED_PRIVATE_GRAPHS_NO_SCIENCE_AUTHORITY',graphs=graphs,A1_priority=True,A3_optional_separate=True,A2_unchanged_conditional=True,prior60_and111_files_unchanged=True))
# Separate interpreter per graph prevents old common module cache from masking ROOT mismatches.
results=[]
for g in graphs:
 for item in g['candidate_specs']:
  s=read(item['path']);case=s['cohort']
  code="import sys,json;sys.dont_write_bytecode=True;sys.path.insert(0,"+repr(g['runtime'])+");import ep_perf_native_wv_modes_draft as e;s=e.engineering_spec_for("+repr(case)+");assert str(e.ROOT)=="+repr(g['execution'])+";assert e.spec_path(s['cohort']).as_posix()=="+repr(item['path'])+";print(json.dumps(e.validate_spec_contract(s)))"
  cp=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True);assert cp.returncode==0,(case,cp.stdout,cp.stderr)
  cmd=[g['entry_ref']['path'],'experiment','prepare',case,'--project','EP_L2'];q=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  assert q.returncode==2 and 'MISSING_FRESH_EXACT_REQUEST2_SCIENTIFIC_AUTHORIZATION'in q.stderr,(case,q.stdout,q.stderr)
  results.append(dict(cohort=case,final_Spec_ref=item,actual_consumer_ROOT=g['execution'],full43_currentdomain_Source78_native22_helper_dependencies_schema=json.loads(cp.stdout),real_private_Native_prepare_argv=cmd,prepare_exitcode=q.returncode,prepare_receipt=json.loads(q.stderr),model_starts=0))
write(O/'FOUR_FINAL_SPEC_SCHEMA_AND_NATIVE_HOLDS.json',dict(status='PASS',rows=results,old32_negative_or_eventloop_or_geometry_tests_rerun=0,shared_or_registry_or_model_changes=0))
# Preserve both older complete deliveries byte-for-byte.
oldcheck=read(O/'OLD_RESOURCE_DEFECT_AND_FROZEN_PREIMAGE.json')
for x in oldcheck['frozen_manifests']:
 assert sha(x['manifest_path'])==x['sha256']and all(sha(r['path'])==r['sha256']for r in read(x['manifest_path'])['files'])
write(O/'FROZEN60_111_POSTCHECK.json',dict(status='PASS',manifests=oldcheck['frozen_manifests'],all_original_file_bytes_unchanged=True))
(O/'README.md').write_text('''# Final Source78 resource and consumer ROOT follow-up
Earlier A1/A3 wrappers really failed snapshot with unknown V3 scope. The earlier qualification was limited to schema/monitor/parser; this actual resource-wiring defect is disclosed in OLD_RESOURCE_DEFECT_AND_FROZEN_PREIMAGE.json.

These final selected A1/A3 graphs each clone the prior runtime+execution into this directory. common ROOT, native entry path, guard reference, mode scope/preview, parser pin, HostQ, owned pins and all four conditional exact Spec chains are rebound to the new execution ROOT. The actual new Specs consume the pinned Main V4 resource adapter. Real read-only snapshot calls for both requests succeeded; four full43/currentdomain/dependency/source/input/mode schema paths passed and real private Native prepare commands held specifically for absent fresh request2 scientific authorization. New candidate sidecars are not being mistaken for old hardbound Specs.

No old32-negative suite, actual eventloop, Source/geometry tests or application NI was rerun. Original60/111 frozen file bytes and old execution candidates remain unchanged. Shared route, registry, budget and models were not changed. Snapshot success establishes resource wiring, not scientific permission or a guarantee of current resource admission.

Main must use FINAL_CONSUMER_GRAPH_INDEX.json as the selected runtime/execution root, preserve candidate snapshots when materializing fresh approval Spec revisions, and install/register only the separately approved exact request2. A1 is priority; A3 remains independently optional; A2 retains its real WV eligibility gap. Dynamic admission still preserves foreign commitments and cap10 through Main's unchanged resource math.
''')
write(O/'MAIN_FINAL_INSTALL_SUPPLEMENT.json',dict(schema='EP_PFV4_MAIN_FINAL_SOURCE78_RESOURCE_CONSUMER_INSTALL_SUPPLEMENT_V2',status='ENGINEERING_WIRING_AND_CONSUMPTION_ROOT_CLOSED_NO_SCIENCE_AUTHORITY',graphs=graphs,selection_supersedes='Prior private_main_integration graph selection for A1/A3 only; its immutable evidence remains retained.',Main_remaining_steps=['Review this exact supplement and pin the final graph paths in FINAL_CONSUMER_GRAPH_INDEX.json.','Obtain fresh independently scoped A1 or optional A3 two-point scientific authorization; materialize new exact Spec revision in this selected execution ROOT while preserving candidate snapshots.','Install only Main-approved additive exact Native route and register exact request2 budget+SpecSHA+owned graph; no old approval reuse.','Refresh CPU/native domain and actual dynamic resource admission before claim/consume/fork.'],remaining_resource_engineering_HOLD=False,resource_snapshot_is_not_science_authority=True,prior60_111_unchanged=True,real_approved_registered_consumed_starts=0))
# Every private owned reference must now match the final selected graph, without reading any Trace body.
errors=[];count=0
for p in O.rglob('*.json'):
 if p.name=='RESOURCE_FOLLOWUP_MANIFEST.json':continue
 def walk(d):
  global count
  if isinstance(d,dict):
   if isinstance(d.get('path'),str)and isinstance(d.get('sha256'),str)and d['path'].startswith(str(O)+'/'):
    count+=1
    if not Path(d['path']).is_file()or sha(d['path'])!=d['sha256']:errors.append(dict(referrer=str(p),target=d['path']))
   for v in d.values():walk(v)
  elif isinstance(d,list):
   for v in d:walk(v)
 walk(read(p))
assert not errors,errors
write(O/'FINAL_RESOURCE_GRAPH_REFERENCE_AUDIT.json',dict(status='PASS',owned_references_checked=count,drift=errors))
files=[dict(member=str(p.relative_to(O)),**ref(p),bytes=p.stat().st_size)for p in sorted(O.rglob('*'))if p.is_file()and '__pycache__'not in str(p)and p.name!='RESOURCE_FOLLOWUP_MANIFEST.json']
write(O/'RESOURCE_FOLLOWUP_MANIFEST.json',dict(schema='EP_PFV4_A1_A3_FINAL_RESOURCE_AND_CONSUMER_ROOT_DELIVERY_V2',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='REAL_SNAPSHOT_AND_FOUR_ACTUAL_CONSUMER_SCHEMA_PASS_FRESH_SCIENCE_HOLD_ONLY',Main_helper_ref=ref(helper),entry_ref=ref(O/'FINAL_CONSUMER_GRAPH_INDEX.json'),files=files,models_budget_registry_shared_changes=0,prior60_111_files_unchanged=True))
print(json.dumps(dict(status='PASS',manifest_ref=ref(O/'RESOURCE_FOLLOWUP_MANIFEST.json'),graphs=len(graphs),actual_readonly_snapshots=2,actual_new_consumer_schema_and_science_HOLDs=len(results),files=len(files),old60_111_unchanged=True)))

