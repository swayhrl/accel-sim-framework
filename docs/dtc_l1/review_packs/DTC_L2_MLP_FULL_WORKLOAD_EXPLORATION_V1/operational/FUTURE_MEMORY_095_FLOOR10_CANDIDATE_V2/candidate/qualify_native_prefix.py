"""Actual frozen native loop through PID and runtime(False), no model Popen.
Isolated fixture + in-memory authority/lease/proc identities and synthetic headroom.
This is engineering prefix evidence, never a scientific accepted simulation.
"""
import pathlib,json,copy,types,subprocess,io,os,sys,hashlib,importlib.util,tempfile
P=pathlib.Path;IO=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/B/shared_json_outer_v1');D=P(__file__).parent;B=IO.parent/'padding_only_overlay_v1';padding_mode=len(sys.argv)<2 or sys.argv[1]=='padding';REAL=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
core=load('prefix_padding_core',B/'padding_overlay.py');front=load('prefix_padding_front',B/'padding_frontend.py');realnative=load('prefix_reference_native',REAL/'tools/l2_native.py');reg,epoch,q0,plan=realnative.registered();q=copy.deepcopy(q0);c=min((c for c in q['admitted_specs']if c not in q['consumed']),key=lambda c:realnative.canonical(c)['estimated_peak_model_RAM_bytes']);fixture=P(tempfile.mkdtemp(prefix='CPU_NATIVEPREFIX_',dir=D));checks=[]
def ck(n,v):assert v,n;checks.append(n)
for sub in['control/specs','control/qualification_ledger','control/dispatch_bindings','DTC/run/results','DTC/control']:(fixture/sub).mkdir(parents=True,exist_ok=True)
for name in['SCIENCE_AUTHORIZATION.json','BUILD_PROFILE.json','SCOPE.json','EXECUTION_PLAN.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','RESOURCE_POLICY.json','HISTORICAL_RSS.json']:(fixture/'control'/name).symlink_to(REAL/'control'/name)
for name in['tools','common-lib','DTC/env','DTC/bin']:
 p=fixture/name
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(REAL/name,target_is_directory=True)
for name in[c+'_SPEC.json','specs/'+c+'.json']:(fixture/'control'/name).symlink_to(REAL/'control'/name)
s=realnative.canonical(c);realdb=REAL/'control/dispatch_bindings'/(c+'.json');db=core.read(realdb)if realdb.exists()else dict(cohort=c,canonical_spec_sha256=core.sha(REAL/'control/specs'/(c+'.json')),host_cpu=min(os.sched_getaffinity(0)),resolved_spec_sha256=core.jsonsha(dict(s,host_cpu=min(os.sched_getaffinity(0)))));(fixture/'control/dispatch_bindings'/(c+'.json')).write_bytes(core.canonical(db));resolved=dict(s,host_cpu=db['host_cpu']);(fixture/'control/POOL_DISPATCH_RESERVATIONS.json').write_bytes(core.canonical(dict(claims={c:dict(host_cpu=db['host_cpu'],result_cap_bytes=s['limits']['max_result_directory_bytes'])})))
roles=dict(source='padding_overlay.py',frontend='padding_frontend.py',extra_strict='padding_extra_strict.py',owner='padding_owner.py',history_validator='history_evidence_validator.py');qualified={role:core.sha(B/name)for role,name in roles.items()};policy_path=B/'POLICY.json';CP=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/padding_only_admission_v1/A_ONLY_ELIGIBILITY_CERTIFICATE_V1.json');qa=fixture/'CPU_SYNTHETIC_QA.json';pub=fixture/'CPU_SYNTHETIC_READBACK.json';summary=dict(qualified_sources=qualified,policy_sha256=core.sha(policy_path),certificate_sha256=core.sha(CP));qa.write_bytes(core.canonical(dict(summary,status='PASS',CPU_fixture_only=True,native_prefix_qualified=True,owner_instance_qualified=True,additional_strict_qualified=True)));pub.write_bytes(core.canonical(dict(summary,verified=True,CPU_fixture_only=True)));cfg=dict(status='ACTIVE_FUTURE_ONLY',request=core.REQ,overlay_id=core.read(policy_path)['overlay_id'],allowed_cohorts=[c],policy_path=str(policy_path),certificate_path=str(CP),QA_path=str(qa),readback_path=str(pub),policy_sha256=core.sha(policy_path),certificate_sha256=core.sha(CP),QA_sha256=core.sha(qa),readback_sha256=core.sha(pub))
for role,name in roles.items():cfg[role+'_path']=str(B/name);cfg[role+'_sha256']=core.sha(B/name)
record={k:cfg[k]for k in core.CONFIG_EQUAL_KEYS};record['status']='ACTIVE';q['additional_operational_overlays']={cfg['overlay_id']:record};fake=copy.deepcopy(reg);fake['registered_future_requests'][core.REQ]=q
engine=load('prefix_isolated_private_engine',REAL/'tools/l2_native.py');engine.R=fixture;engine.registered=lambda:(fake,epoch,q,plan);engine.assert_parent_lease=lambda:dict(pid=os.getpid(),start_ticks=0,CPU_fixture_only=True);engine.update_authority=lambda fn:fn(fake);frozen_res=load('prefix_frozen_resources',REAL/'tools/l2_resources.py')
def base_resource(spec,fresh=False):
 value=frozen_res.resources(spec,fresh)
 if fresh:
  budget=int(192*core.G*.88);value.update(host_MemAvailable_bytes=200*core.G,cgroup_effective_headroom_bytes=200*core.G,physical_RAM_pass=value['total_projected_additional_RAM_bytes']<=budget);value['admission_decision']=dict(value['admission_decision'],admission_RAM_budget_bytes=budget,effective_usable_bytes=192*core.G,pass_admission=value['physical_RAM_pass'])
 return value
engine.resources=base_resource
outer=load('new_io_outer',IO/'io_frontend.py');helper=load('new_io_helper',IO/'shared_json_io.py');io_roles=dict(source='shared_json_io.py',frontend='io_frontend.py',extra_strict='io_extra_strict.py',owner='io_owner.py');ioq={k:core.sha(IO/n)for k,n in io_roles.items()};pins={str(p):core.sha(p)for p in helper.ALLOWED};ioqa=fixture/'IO_CPU_QA.json';ioback=fixture/'IO_CPU_BACK.json';ioval=dict(qualified_sources=ioq,expected_pins=pins);ioqa.write_bytes(core.canonical(dict(ioval,status='PASS',native_prefix_qualified=True,additional_strict_qualified=True,CPU_fixture_only=True)));ioback.write_bytes(core.canonical(dict(ioval,verified=True,CPU_fixture_only=True)));iocfg=dict(status='ACTIVE_FUTURE_ONLY',request=core.REQ,overlay_id=outer.ID,expected_pins=pins,QA_path=str(ioqa),QA_sha256=core.sha(ioqa),readback_path=str(ioback),readback_sha256=core.sha(ioback))
for role,name in io_roles.items():iocfg[role+'_path']=str(IO/name);iocfg[role+'_sha256']=core.sha(IO/name)
iorecord={k:iocfg[k]for k in['request','overlay_id','expected_pins',*[k+'_sha256'for k in list(io_roles)+['QA','readback']]]};iorecord['status']='ACTIVE';q['additional_operational_overlays'][outer.ID]=iorecord

memory=load('new_future_memory_library',D/'future_memory.py');memory_roles=dict(library='future_memory.py',frontend='memory_frontend.py',owner='memory_owner.py',extra_strict='memory_extra_strict.py',joint_padding='joint_padding_strict.py',joint_io='joint_io_strict.py');memory_qualified={k:core.sha(D/n)for k,n in memory_roles.items()};ioactive=fixture/'IO_ACTIVE_FIXTURE.json';ioactive.write_bytes(core.canonical(iocfg));mpins={x['path']:x['sha256']for x in plan['source_pins']};mpins[str(REAL/'control/RESOURCE_POLICY.json')]=core.sha(REAL/'control/RESOURCE_POLICY.json');mpins[str(REAL/'control/operational_amendments/padding_only_v1/padding_extra_strict.py')]=core.sha(B/'padding_extra_strict.py');mpins.update(pins);memoryqa=fixture/'MEMORY_CPU_QA_SYNTHETIC.json';memoryback=fixture/'MEMORY_CPU_BACK_SYNTHETIC.json';memoryval=dict(qualified_sources=memory_qualified,expected_pins=mpins);memoryqa.write_bytes(core.canonical(dict(memoryval,status='PASS',native_prefix_qualified=True,joint_strict_qualified=True,CPU_fixture_only=True)));memoryback.write_bytes(core.canonical(dict(memoryval,verified=True,CPU_fixture_only=True)));mcfg=dict(status='ACTIVE_FUTURE_ONLY',request=memory.REQ,overlay_id=memory.ID,scope_mode='FINITE_CANARY',memory_utilization_fraction=.95,host_floor_bytes=10*core.G,cgroup_floor_bytes=10*core.G,expected_pins=mpins,io_active_path=str(ioactive),io_active_sha256=core.sha(ioactive),allowed_cohorts=[c],QA_path=str(memoryqa),QA_sha256=core.sha(memoryqa),readback_path=str(memoryback),readback_sha256=core.sha(memoryback))
for role,name in memory_roles.items():mcfg[role+'_path']=str(D/name);mcfg[role+'_sha256']=core.sha(D/name)
q['additional_operational_overlays'][memory.ID]=dict(memory.record(mcfg),status='ACTIVE')
outer.R=fixture;pcfgpath=fixture/'control/operational_amendments/padding_only_v1/ACTIVE_FRONTEND.json';pcfgpath.parent.mkdir(parents=True);pcfgpath.write_bytes(core.canonical(cfg));native,overlay=outer.private_engine(iocfg,padding_mode,native_module=engine);native=memory.install_future_native(native,mcfg,padding_mode)
def prepared(cohort):
 v=native.resources(resolved,True);return dict(status='CPU_FIXTURE_REAL_ARITHMETIC_SYNTHETIC_HEADROOM',operational_resource_profile=native.binding(),additional_padding_admission_proof=v.get('additional_padding_admission_proof'))
native.prepare=prepared;n=native.engine();n.ROOT=fixture;n.read_current_authority=lambda:(fake,epoch);n.authority_consistent=lambda:True;n.identity=lambda:dict(native_device=2128,mnt_namespace='mnt:[4026535153]',CPU_fixture_only=True);n.assert_batch_lease=native.assert_parent_lease
class ReachedRuntimeAfterPID(BaseException):pass
state=dict(pid_written=False,model_Popen_calls=0,runtime_false_seen=False)
original_resources=n.resources
oldexclusive=n.exclusive
def exclusive(path,obj):
 value=oldexclusive(path,obj)
 if P(path).name=='NATIVE_SIMULATOR_PID_AND_MAPS.json':state['pid_written']=True
 return value
n.exclusive=exclusive
class FakeProcPath:
 def __init__(self,path):self.path=path
 def __truediv__(self,x):return FakeProcPath(self.path+'/'+str(x))
 def exists(self):return self.path.endswith('/children')
 def read_text(self):return '99999991'if self.path.endswith('/children')else''
n._observer_race_children=lambda path:['99999991']
n.P=lambda path:FakeProcPath(str(path))if str(path)=='/proc'else P(path)
n.child_info=lambda pid:dict(pid=pid,start_ticks=1,mnt_namespace='mnt:[4026535153]',pid_namespace='CPU_ONLY',maps=resolved['native_simulator_argv'][0],cmdline='CPU_FIXTURE_SYNTHETIC_NOT_A_MODEL',host_cpu_affinity_actual=[resolved['host_cpu']],actual_process_limits_text='CPU fixture',CPU_fixture_only=True)
class DummyGuard:
 def __init__(self,*args):pass
 def drain(self):return dict(records=[],terminal=None)
 def quick_stop(self):return None
sys.modules['sweep_guard_cap1m']=types.SimpleNamespace(NativeDTCGuard=DummyGuard)
class FakePopen:
 def __init__(self,argv,**kw):state['model_Popen_calls']+=1;self.pid=99999990;self.poll_calls=0;self.stdout=io.BytesIO(b'CPU_ONLY_NO_SIMULATOR_EXECUTED\n');state['out']=str(kw['cwd']);ck('model_argv_has_no_optin_flag','--padding-only-admission-v1'not in argv);ck('unchanged_model_argv_suffix',argv[-len(resolved['native_simulator_argv']):]==resolved['native_simulator_argv'])
 def poll(self):
  self.poll_calls+=1;return None if self.poll_calls==1 else 0
 def wait(self,*args,**kwargs):return 0
n.subprocess=types.SimpleNamespace(Popen=FakePopen,PIPE=subprocess.PIPE,STDOUT=subprocess.STDOUT,TimeoutExpired=subprocess.TimeoutExpired)
def resources(spec,fresh_source=False):
 value=original_resources(spec,fresh_source)
 if not fresh_source and state['pid_written']:
  state['runtime_false_seen']=True;ck('runtime_false_does_not_replace_fresh_evidence',overlay is None or overlay.last_proof['fresh_source']is True);raise ReachedRuntimeAfterPID()
 return value
n.resources=resources
# No real process group may ever receive a test signal.
n.os=types.SimpleNamespace(**{k:getattr(os,k)for k in dir(os)if not k.startswith('__')});n.os.killpg=lambda *_:(_ for _ in()).throw(AssertionError('CPU fixture must never signal'))
try:n.run_native(c)
except ReachedRuntimeAfterPID:pass
else:raise AssertionError('actual native runtime boundary not reached')
out=P(state['out']);intent=core.read(fixture/'control/qualification_ledger'/(c+'.INTENT.json'));launch=core.read(out/'NATIVE_LAUNCH.json');pid=core.read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');documents=[intent,launch,pid];ck('actual_native_prefix_PID_and_runtime_reached',state['pid_written']and state['runtime_false_seen']);ck('three_identical_IO_bindings',all(v['additional_shared_json_io_binding']==intent['additional_shared_json_io_binding']for v in documents));ck('old_base_bindings_all_preserved',all(v['l2_mlp_execution_binding']==native.binding()for v in documents));ck('atomic_leaf_used_by_real_native',n._original_exclusive.__name__=='atomic_exclusive');ck('no_scientific_DONE_or_result_created',not(fixture/'control/qualification_ledger'/(c+'.DONE.json')).exists())

oldproof=dict(performance_accepted=True,CPU_fixture_base_mock=True);extra=load('prefix_memory_extra',D/'memory_extra_strict.py');extra.R=fixture;proof=extra.terminal(c,oldproof);ck('newmemory_IO_originalperformance_closed',proof['additional_future_memory_admission_strict']['status']=='PASS_FUTURE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE');ck('memory_three_bindings_exact',all(x['additional_future_memory_admission_binding']==intent['additional_future_memory_admission_binding']for x in documents));ck('memory_snapshot_exactSHA',intent['additional_future_memory_admission_binding']['snapshot_sha256']==core.sha(out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json'));ck('no_oldB5_PASS_claimed',proof['additional_future_memory_admission_strict']['old_B5_strict_PASS_claimed']is False)
try:extra.terminal(c,dict(performance_accepted=False))
except AssertionError:checks.append('false_original_performance_never_promoted')
else:raise AssertionError('false original strict accepted')
snapshot=core.read(out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json');runtime_base=base_resource(resolved,False);runtime_wrapper=memory.wrap_resources(lambda *a:runtime_base);ck('freshFalse exactoldobject_return',runtime_wrapper(resolved,False)is runtime_base);mp=snapshot['fresh_preflights'][0]
for label,mutate in [('growth_reduction',lambda p:p.update(growth_unchanged_bytes=p['growth_unchanged_bytes']-1)),('cachecredit_fabrication',lambda p:p.update(no_new_clean_cache_credit=False)),('sample_host_mismatch',lambda p:p['sample'].update(host_MemAvailable_bytes=p['sample']['host_MemAvailable_bytes']+1)),('pressure_erasure',lambda p:p.update(pressure_reasons=['CPU_FIXTURE_PRESSURE'])),('own_bound_bypass',lambda p:p.update(disk_and_own_bound_pass=False)),('budget_increase',lambda p:p['effective_decision'].update(admission_RAM_budget_bytes=p['effective_decision']['admission_RAM_budget_bytes']+1)),('canonical_cost_reduction',lambda p:p.update(canonical_candidate_and_claim_costs_unchanged=False))]:
 bad=copy.deepcopy(mp);mutate(bad)
 try:memory.verify_memory_proof(bad)
 except(RuntimeError,AssertionError):checks.append('memoryreject_'+label)
 else:raise AssertionError(label+' accepted')
saved=copy.deepcopy(pid);badpid=copy.deepcopy(pid);badpid['additional_future_memory_admission_binding']['snapshot_sha256']='0'*64;(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').write_bytes(core.canonical(badpid))
try:extra.terminal(c,oldproof)
except AssertionError:checks.append('mismatched_newmemory_PIDbinding_rejected')
else:raise AssertionError('mismatched newmemorybinding accepted')
(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').write_bytes(core.canonical(saved))
if padding_mode:
 joint=load('cpu_joint_memory_padding',D/'joint_padding_strict.py');joint.R=fixture;joint._MEMORY_VERIFY=memory.verify_memory_proof;legacy=load('cpu_old_padding_strict',B/'padding_extra_strict.py');legacy.R=fixture;ev=core.read(out/'PADDING_ADMISSION_EVIDENCE.json');overlaymod=load('cpu_joint_overlay',out/'PADDING_OVERLAY_SOURCE.py');ob=overlaymod.PaddingOverlay(fixture,out/'PADDING_POLICY.json',out/'PADDING_CERTIFICATES.json',ev['binding']['policy_sha256'],ev['binding']['certificate_sha256'],lambda:{},lambda *_:None)
 for old in ev['fresh_preflights']:ck('oldproof_legacy_replay_equivalent',legacy.replay_proof(old,ob,c)==joint.replay_proof(old,ob,c))
 original=ev['fresh_preflights'][0];T=original['effective_total_additional_RAM_bytes'];H=int((T/.95+10*core.G+T/.88+8*core.G)/2);oldbudget=int((H-8*core.G)*.88);newbudget=int((H-10*core.G)*.95);ck('synthetic_newbudget_only_window_exists',oldbudget<T<=newbudget);changed=copy.deepcopy(original);changed['base_resource_sample'].update(host_MemAvailable_bytes=H,cgroup_effective_headroom_bytes=H);changed['base_decision']['admission_RAM_budget_bytes']=oldbudget;changed['effective_decision']['admission_RAM_budget_bytes']=oldbudget;changed['base_decision']['pass_admission']=changed['base_total_additional_RAM_bytes']<=oldbudget;changed['effective_decision']['pass_admission']=False;matching=next(x for x in snapshot['fresh_preflights']if x['legacy_padding_proof_sha256']==memory.objsha(original));base=copy.deepcopy(matching['base_resource_snapshot']);base.update(host_MemAvailable_bytes=H,cgroup_effective_headroom_bytes=H,additional_padding_admission_proof=changed,admission_decision=copy.deepcopy(changed['effective_decision']),total_projected_additional_RAM_bytes=T,physical_RAM_pass=False);newmp=memory.project(base)['additional_future_memory_admission_proof'];newmp['legacy_padding_proof_sha256']=memory.objsha(changed);joint.replay_proof(changed,ob,c,newmp);checks.append('newjoint_strict_accepts_explicit095only_window_preservingallcosts')
 try:legacy.replay_proof(changed,ob,c)
 except AssertionError:checks.append('oldstrict_correctly_HOLD_same095only_window_not_claimedPASS')
 else:raise AssertionError('old strict wrongly accepted newwindow')
 for key in ['candidate_full_original','all_foreign_and_claims_unchanged','no_physical_headroom_credit']:
  bad=copy.deepcopy(changed);bad[key]=False
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_'+key)
  else:raise AssertionError(key+' bypassed')
 for key in ['total_discount_bytes','snapshot_total_discount_cap_bytes','total_topup_bytes','effective_total_additional_RAM_bytes']:
  bad=copy.deepcopy(changed);bad[key]+=1
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_'+key)
  else:raise AssertionError(key+' bypassed')
 if changed['claim_candidate_topups']:
  bad=copy.deepcopy(changed);bad['claim_candidate_topups'][0]['canonical_prediction']+=1
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_canonical_fullprediction')
  else:raise AssertionError('canonical cost bypassed')
 if changed['discount_rows']:
  bad=copy.deepcopy(changed);bad['discount_rows'][0]['uuid']='WRONG_GENERATION'
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_discount_generation')
  else:raise AssertionError('discount generation bypassed')
report=dict(status='PASS',mode='padding'if padding_mode else'noflag',checks=checks,passed=len(checks),actual_model_starts=0,model_Popen_was_mock=True,fixture=str(fixture),synthetic_authority_lease_headroom_proc_and_baseproof_only_in_CPU_fixture=True,production_mutations=0,qualified_sources=memory_qualified,expected_pins=mpins,model_signal_calls=0,original_IO_and_optional_padding_math_checks_retained=True);(D/('NATIVE_PREFIX_'+report['mode'].upper()+'.json')).write_bytes(core.canonical(report));print(json.dumps(dict(status='PASS',mode=report['mode'],checks=len(checks),path=str(D/('NATIVE_PREFIX_'+report['mode'].upper()+'.json')))))
