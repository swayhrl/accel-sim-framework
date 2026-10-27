"""Run on174-new. Isolated fixtures and interception only; NEVER production writes.

Monitor identities use an explicitly synthetic CPU helper; not a real guard service.
"""
import copy,datetime,hashlib,importlib.util,json,os,pathlib,subprocess,sys,tempfile,time,uuid,threading,io,types
P=pathlib.Path;HERE=P(__file__).resolve().parent
PROD=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');checks=[]
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def check(v,label):assert v,label;checks.append(label)
def rejected(fn,fragment,label):
 try:fn()
 except (RuntimeError,AssertionError)as exc:check(fragment in str(exc),label)
 else:raise AssertionError('Expected rejection '+label)
g=load('qualified_guard_candidate',HERE/'guarded_native.py')
e=load('guard_qualification_base',PROD/'tools/l2_native.py');other=load('guard_unmodified_private_comparison',PROD/'tools/l2_native.py')
before={str(p):sha(p)for p in [PROD/'tools/l2_native.py',PROD/'tools/l2_resources.py',PROD/'tools/l2_frontend.py',PROD/'tools/l2_strict.py',PROD/'control/EXECUTION_PLAN.json',PROD/'control/BUILD_PROFILE.json']}
prodreg,prodep=e.authority();q=copy.deepcopy(prodreg['registered_future_requests'][e.REQ]);q['consumed']={};q['remaining']=q['budget'];q['state']='ARMED'
fixture=P(tempfile.mkdtemp(prefix='dtc_l2_guard_CPU_A_',dir='/root/data'))
for n in ['control/qualification_ledger','control/dispatch_bindings','DTC/run/results']:(fixture/n).mkdir(parents=True,exist_ok=True)
for p in(PROD/'control').iterdir():
 if p.name in ['POOL_DISPATCH_RESERVATIONS.json','qualification_ledger','dispatch_bindings','draft_preimages']:continue
 (fixture/'control'/p.name).symlink_to(p,target_is_directory=p.is_dir())
for n in ['tools','common-lib','DTC/env','DTC/bin']:(fixture/n).parent.mkdir(parents=True,exist_ok=True);(fixture/n).symlink_to(PROD/n,target_is_directory=True)
s=read(PROD/'control/specs'/(g.PILOT+'.json'))
for item in s['runtime_files']:
 dst=fixture/item['target']
 if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);dst.symlink_to(PROD/item['target'])
check(len(s['expected_options'])>=250,'all scientific option fields available: '+str(len(s['expected_options'])))
for c in g.PILOT_CANDIDATES:
 sp=read(PROD/'control/specs'/(c+'.json'));resolved=dict(sp,host_cpu=min(os.sched_getaffinity(0)))
 put(fixture/'control/dispatch_bindings'/(c+'.json'),dict(cohort=c,canonical_spec_sha256=sha(PROD/'control/specs'/(c+'.json')),host_cpu=resolved['host_cpu'],resolved_spec_sha256=e.jsonsha(resolved)))
e.R=fixture;reg={'registered_future_requests':{e.REQ:q}};plan=read(PROD/'control/EXECUTION_PLAN.json')
e.registered=lambda:(reg,dict(epoch=2,state='NATIVE_SCIENCE_ACTIVE',holder=os.uname().nodename),q,plan)
lease=dict(pid=os.getpid(),start_ticks=g.proc_start(os.getpid()),controller_sha256=plan['parent_controller_sha256'])
e.assert_parent_lease=lambda:lease;e.update_authority=lambda fn:fn(reg)
binding_before=e.binding();old_resource_fn=e.resources;other_resource_fn=other.resources
qualified_stub=fixture/'fixture_qualification.json';put(qualified_stub,dict(status='PASS',actual_model_starts=0,full_native_prefix_intercepted=True,actual_compiled_INTENT_LAUNCH_PID_triple_qualified=True,additional_strict_cpu_qualified=True,no_overlay_original_strict_qualified=True,actual_B_guard_empty_resolver_native_prepare_qualified=True,fixture_only=True))
record={'request':e.REQ,'status':'APPROVED_CPU_NATIVE_PREFIX_QUALIFIED','allowed_cohorts':g.PILOT_CANDIDATES,'changes_scientific_identity':False,'original_engine_sha256':sha(e.__file__),'original_binding_sha256':g.jsonsha(binding_before),'heartbeat_path':str(fixture/'heartbeat.json')}
for key,n in [('overlay_source','guarded_native.py'),('policy','POLICY.json'),('additional_strict_source','additional_strict.py')]:record[key]=dict(path=str(HERE/n),sha256=sha(HERE/n))
B_SOURCE=HERE.parent.parent/'B/memory_guard_v1/memory_guard.py'
check(sha(B_SOURCE)=='d65ca467f0fd9570cc265a43ee7776159a3c3014dea6c9e7660123ea7b11b016','exact frozen B guard source SHA')
record['monitor_source']=dict(path=str(B_SOURCE),sha256=sha(B_SOURCE))
stub=read(qualified_stub);stub.update(source_sha256={'guarded_native.py':sha(HERE/'guarded_native.py'),'additional_strict.py':sha(HERE/'additional_strict.py')},policy_sha256=sha(HERE/'POLICY.json'),B_guard_source_sha256=record['monitor_source']['sha256']);put(qualified_stub,stub)
record['cpu_native_prefix_qualification']=dict(path=str(qualified_stub),sha256=sha(qualified_stub));q['resource_admission_overlays']={g.OVERLAY_ID:record}
pubstub=fixture/'PUBLICATION_CPU_FIXTURE.json';put(pubstub,dict(status='READBACK_VERIFIED',commit='f'*40,fixture_only=True,source_sha256={k:record[k]['sha256']for k in ['overlay_source','policy','monitor_source','additional_strict_source','cpu_native_prefix_qualification']}));record['publication_readback']=dict(path=str(pubstub),sha256=sha(pubstub))
record['guard_token']='SYNTHETIC_CPU_ONLY_GUARD_TOKEN';record['pause_journal_path']=str(fixture/'PAUSE_JOURNAL.jsonl');P(record['pause_journal_path']).write_bytes(b'')
policy=read(HERE/'POLICY.json');boot=P('/proc/sys/kernel/random/boot_id').read_text().strip()
saved_publication=pubstub.read_bytes();badpub=read(pubstub);badpub['status']='PENDING';put(pubstub,badpub);record['publication_readback']['sha256']=sha(pubstub)
rejected(lambda:g.approval(e,g.PILOT),'PUBLICATION','unpublished source cannot authorize native prefix')
pubstub.write_bytes(saved_publication);record['publication_readback']['sha256']=sha(pubstub)
e.R=PROD
rejected(lambda:g.approval(e,g.PILOT),'FIXTURE_IS_NOT_PRODUCTION','CPU fixture approval cannot be replayed against production root')
e.R=fixture
def select(c,**extra):
 token=dict(request=e.REQ,cohort=c,epoch=2,boot_id=boot,nonce=uuid.uuid4().hex,issued_monotonic=time.monotonic()-1,expires_monotonic=time.monotonic()+90,owner_pid=lease['pid'],owner_start_ticks=lease['start_ticks'],canonical_spec_sha256=sha(PROD/'control/specs'/(c+'.json')),dispatch_binding_sha256=sha(fixture/'control/dispatch_bindings'/(c+'.json')));token.update(extra)
 path=fixture/'tokens'/(token['nonce']+'.json');put(path,token)
 active=dict(overlay_id=g.OVERLAY_ID,cohort=c,nonce=token['nonce'],path=str(path),sha256=sha(path));q['active_resource_admission_token']=active;q.setdefault('resource_admission_token_history',{})[token['nonce']]={k:active[k]for k in ['path','sha256','cohort']};return token
select(g.PILOT)
rejected(lambda:g.approval(e,'E2-OLD-AG8R1'),'PILOT_ONLY','old request rejected')
token=select(g.PILOT,epoch=1);rejected(lambda:g.selected_token(e,g.PILOT,record,policy,{'epoch':2},q),'EPOCH','token wrong epoch rejected')
token=select(g.PILOT,issued_monotonic=time.monotonic()-100,expires_monotonic=time.monotonic()-1);rejected(lambda:g.selected_token(e,g.PILOT,record,policy,{'epoch':2},q),'EXPIRED','expired token rejected')
token=select(g.PILOT,owner_start_ticks=1);rejected(lambda:g.selected_token(e,g.PILOT,record,policy,{'epoch':2},q),'OWNER','wrong owner generation token rejected')
select(g.PILOT);rejected(lambda:g.selected_token(e,g.PILOT_CANDIDATES[1],record,policy,{'epoch':2},q),'NOT_SELECTED','fallback cannot self-select')
helper=subprocess.Popen([sys.executable,'-c','import time; time.sleep(300)',str((HERE/'guard_monitor.py').resolve())])
guard_stop=threading.Event();guard_thread=threading.Thread(target=guard_stop.wait,name='CPU_ONLY_GUARD_IDENTITY');guard_thread.start()
def beat(**override):
 h=dict(schema='L2MLP_GUARD_HEARTBEAT_V1',request=e.REQ,overlay_id=g.OVERLAY_ID,epoch=2,boot_id=boot,registry_overlay_record_sha256=g.jsonsha(record),policy_sha256=record['policy']['sha256'],monitor_source_sha256=record['monitor_source']['sha256'],monotonic=time.monotonic(),monitor_pid=lease['pid'],monitor_start_ticks=lease['start_ticks'],owner_pid=lease['pid'],owner_start_ticks=lease['start_ticks'],guard_tid=guard_thread.native_id,guard_start_ticks=g.thread_state(lease['pid'],guard_thread.native_id)[1],guard_token=record['guard_token'],active_admission_token_sha256=q['active_resource_admission_token']['sha256'],pause_journal_path=record['pause_journal_path'],pause_journal_prefix_bytes=0,pause_journal_sha256=hashlib.sha256(b'').hexdigest(),paused_handles=[],handle_state_sha256=g.jsonsha([]),shadow_mode=False,signals_enabled=True,healthy=True,fault=None,fresh_admission_allowed=True,warmup_complete=True,pause_new_admission=False,pause_reasons=[],own_live_generations={})
 h['aggressive_admission_armed']=True;h.update(override);put(record['heartbeat_path'],h);return h
try:
 hb=lambda:g.heartbeat(record,policy,{'epoch':2},q,owner_lease=lease)
 beat();check(hb()[2]<=2,'fresh live-generation heartbeat accepted')
 beat(monotonic=time.monotonic()-3);rejected(hb,'STALE','stale heartbeat HOLD')
 beat(pause_new_admission=True,pause_reasons=['HOST_BELOW_10G']);rejected(hb,'PRESSURE','10G pressure heartbeat HOLD')
 beat(monitor_start_ticks=1);rejected(hb,'GENERATION','monitor PID generation mismatch HOLD')
 beat(warmup_complete=False);rejected(hb,'WARMUP','monitor warmup HOLD')
 beat(shadow_mode=True);rejected(hb,'SHADOW','shadow guard cannot authorize aggressive native admission')
 beat(signals_enabled=False);rejected(hb,'SIGNALS_DISABLED','signals-disabled guard HOLD')
 beat(aggressive_admission_armed=False);rejected(hb,'FAILSAFE_NOT_ARMED','unarmed aggressive-admission failsafe HOLD')
 missing=beat();missing.pop('aggressive_admission_armed');put(record['heartbeat_path'],missing);rejected(hb,'FAILSAFE_NOT_ARMED','missing aggressive-admission failsafe flag HOLD')
 beat(guard_tid=999999999);rejected(hb,'THREAD_NOT_ALIVE','dead native guard thread HOLD even with fresh heartbeat')
 beat(pause_journal_sha256='0'*64);rejected(hb,'JOURNAL','pause journal hash mismatch HOLD')
 beat(active_admission_token_sha256='0'*64);rejected(hb,'TOKEN','heartbeat must bind exact active pilot token')
 select(g.PILOT);beat()
 # Artificial resource data solely within the isolated CPU fixture.
 candidate=s['estimated_peak_model_RAM_bytes'];foreign=20*g.G;live_old=200*g.G
 q['consumed']['CPU_ONLY_LIVE_FIXTURE']=dict(uuid='CPU_ONLY_UUID')
 base=dict(schema='L2_MLP_DYNAMIC_WORKINGSET_RESOURCE_V1',source_module_sha256=sha(PROD/'tools/l2_resources.py'),physical_RAM_pass=False,physical_disk_pass=True,host_MemAvailable_bytes=160*g.G,cgroup_effective_headroom_bytes=160*g.G,native_free_bytes=1000*g.G,required_free_bytes=5*g.G,total_projected_additional_RAM_bytes=foreign+live_old+candidate,admission_decision={'pressure_reasons':[]},own_ram_forecasts=[dict(cohort='CPU_ONLY_LIVE_FIXTURE',kind='LIVE_MODEL',RSS_bytes=g.G,additional_reserved_bytes=live_old),dict(cohort=g.PILOT,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=candidate)])
 h=beat(own_live_generations={'CPU_ONLY_LIVE_FIXTURE':dict(uuid='CPU_ONLY_UUID',pid=helper.pid,start_ticks=g.proc_start(helper.pid),RSS_bytes=g.G,growth_reserve_bytes=g.G)})
 decision=g.decision(base,h,policy,g.PILOT,q);check(decision['pass_admission'],'base-future peak HOLD can guarded-admit with full candidate reservation')
 math_gate=load('guard_pure_historical_math_cpu',HERE/'additional_strict.py');check(math_gate.verify_reservation_math(base,h,decision,policy,g.PILOT,q,candidate),'changed live reservation historical arithmetic closes without proc liveness')
 check(decision['guarded_total_additional_RAM_bytes']==foreign+g.G+candidate,'foreign full, current candidate full, only observed live growth discounted')
 check(decision['unchanged_rows'][0]['guarded_reserved_bytes']==candidate,'81GiB Lava forecast remains full')
 low=dict(base,host_MemAvailable_bytes=9*g.G);check(not g.decision(low,h,policy,g.PILOT,q)['pass_admission'],'below10GiB real headroom HOLD')
 unknown=copy.deepcopy(base);unknown['own_ram_forecasts'][0]['kind']='SPENT_UNRESOLVED_GENERATION';check(not g.decision(unknown,h,policy,g.PILOT,q)['pass_admission'],'unresolved generation reserves full forecast')
 q['consumed'].pop('CPU_ONLY_LIVE_FIXTURE')
 def fixture_resources(spec,fresh_source=False):
  row=copy.deepcopy(base);row['own_ram_forecasts']=row['own_ram_forecasts'][1:];row['total_projected_additional_RAM_bytes']=candidate;row['physical_RAM_pass']=True
  return row
 e.resources=fixture_resources;cpu=min(os.sched_getaffinity(0));put(fixture/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={g.PILOT:dict(host_cpu=cpu)}));select(g.PILOT);beat()
 saved_spec=copy.deepcopy(e.spec_for(g.PILOT));installed=g.install(e,g.PILOT)
 check(e.binding()==binding_before,'exact original e.binding unchanged')
 check(other.resources is other_resource_fn,'separate unoverlaid module untouched')
 check(e.spec_for(g.PILOT)==saved_spec,'all scientific options/spec/forecast/RSS/AS unchanged after overlay install')
 check(installed['additional_binding']['base_forecast_fields_are_not_the_effective_admission_gate'],'truthful distinct effective provider binding')
 prepared=e.prepare(g.PILOT);check(prepared['scientific_starts']==0,'real frozen native prepare no-start pass')
 check(prepared['operational_resource_profile']==binding_before,'prepare preserves old operational binding exactly')
 check(prepared['resources']['resource_overlay_binding']==installed['additional_binding'],'prepare additional binding present')
 n=e.engine();real_popen=subprocess.Popen;intercept=[]
 class NoExec(BaseException):pass
 def blocked(argv,**kw):
  if any('accel-sim.out'in str(a)for a in argv)and'cwd'in kw:intercept.append(dict(argv=argv,cwd=str(kw['cwd'])));raise NoExec()
  return real_popen(argv,**kw)
 subprocess.Popen=blocked
 try:
  try:n.run_native(g.PILOT);raise AssertionError('Popen not intercepted')
  except NoExec:pass
 finally:subprocess.Popen=real_popen
 ip=fixture/'control/qualification_ledger'/(g.PILOT+'.INTENT.json');intent=read(ip)
 check(len(intercept)==1,'real unchanged native launch prefix intercepted once before executable')
 check(intercept[0]['argv'][-len(saved_spec['native_simulator_argv']):]==saved_spec['native_simulator_argv'],'exact canonical native simulator argv retained')
 check(intent['l2_mlp_execution_binding']==binding_before,'INTENT exact original binding preserved')
 check(intent['resource_overlay_binding']==installed['additional_binding'],'INTENT truthful separate overlay binding present')
 check(q['consumed'][g.PILOT]['intent_sha256']==sha(ip),'only fixture authority charged exact augmented intent')
 check(e.spec_for(g.PILOT)==saved_spec,'all270 scientific options/spec remain identical through pre-fork')
 # Completed-overlay gate fixtures are entirely synthetic and explicitly not
 # scientific results. The unchanged full terminal validator is tested below.
 extra=load('guard_additional_strict_cpu',HERE/'additional_strict.py');out=P(intent['output'])
 augmented={k:intent[k]for k in ['l2_mlp_execution_binding','resource_overlay_binding','resource_overlay_admission_evidence']}
 put(out/'NATIVE_LAUNCH.json',augmented);put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',augmented)
 (out/'DISPATCH_BINDING.json').write_bytes((fixture/'control/dispatch_bindings'/(g.PILOT+'.json')).read_bytes())
 check(extra.verify(g.PILOT,e)['status']=='PASS_ADDITIONAL_GUARDED_ADMISSION_BINDING','independent additional strict synthetic overlay fixture passes')
 bad=copy.deepcopy(augmented);bad['resource_overlay_binding']['policy_sha256']='0'*64;put(out/'NATIVE_LAUNCH.json',bad)
 rejected(lambda:extra.verify(g.PILOT,e),'','independent additional strict rejects extra binding tamper')
 put(out/'NATIVE_LAUNCH.json',augmented)
 for label,mutate in [('total_zero',lambda v:v['decision'].__setitem__('guarded_total_additional_RAM_bytes',0)),('missing_row',lambda v:v['decision']['unchanged_rows'].clear()),('inflated_ceiling',lambda v:v['decision'].__setitem__('RAM_available_after_10G_floors_bytes',v['decision']['RAM_available_after_10G_floors_bytes']+1))]:
  bad=copy.deepcopy(augmented);mutate(bad['resource_overlay_admission_evidence']);put(out/'NATIVE_LAUNCH.json',bad);rejected(lambda:extra.verify(g.PILOT,e),'','additional strict rejects reservation math '+label)
 put(out/'NATIVE_LAUNCH.json',augmented)
 bad=copy.deepcopy(augmented);bad['resource_overlay_admission_evidence']['decision']['unchanged_rows'][0]['guarded_reserved_bytes']=0;put(out/'NATIVE_LAUNCH.json',bad)
 rejected(lambda:extra.verify(g.PILOT,e),'','independent additional strict rejects lowered candidate reservation')
 put(out/'NATIVE_LAUNCH.json',augmented)
 # Original terminal validator exercised against a real already accepted result,
 # then read-only virtual top-level additions. No original result file is edited.
 st=load('guard_original_strict_readonly',PROD/'tools/l2_strict.py')
 chosen='E2-DTCL2MLP-16f4c42373e4961e-DH-E384-V1';original_terminal=st.terminal(chosen);original_read=st.read
 def with_extra(p):
  v=original_read(p)
  if P(p).name.endswith('.INTENT.json')or P(p).name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:return dict(v,resource_overlay_binding={'CPU_READONLY_COMPATIBILITY_FIXTURE':True},resource_overlay_admission_evidence={'CPU_FIXTURE_ONLY':True})
  return v
 st.read=with_extra;augmented_terminal=st.terminal(chosen)
 check(augmented_terminal==original_terminal,'full original terminal strict accepts identical natural population with additive top fields')
 # A second, unconsumed isolated fixture point drives the actual transformed
 # run_native through LAUNCH/PID writes with a CPU fake launcher and fake BA
 # telemetry. This is NOT a scientific completion or real simulator execution.
 c2=g.PILOT_CANDIDATES[1];select(c2);beat();e2=load('guard_cpu_full_mock_launcher',PROD/'tools/l2_native.py');e2.R=fixture
 e2.registered=e.registered;e2.assert_parent_lease=e.assert_parent_lease;e2.update_authority=e.update_authority
 sp2=e2.spec_for(c2);est2=sp2['estimated_peak_model_RAM_bytes']
 def resources2(spec,fresh_source=False):
  row=copy.deepcopy(base);row['physical_RAM_pass']=True;row['total_projected_additional_RAM_bytes']=est2;row['own_ram_forecasts']=[dict(cohort=c2,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=est2)];return row
 e2.resources=resources2;put(fixture/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={c2:dict(host_cpu=cpu)}));ins2=g.install(e2,c2);n2=e2.engine()
 check(n2.run_native.__globals__ is n2.__dict__,'observer exec shares exact native module dictionary, not a copied namespace')
 check(n2.run_native.__globals__['exclusive']is n2.exclusive,'transformed native launcher resolves final overlay exclusive chain')
 class FakeLauncher:
  def __init__(self):self.pid=helper.pid;self.stdout=io.BytesIO(b'CPU_ONLY_FAKE_LAUNCHER_NOT_A_SCIENTIFIC_MODEL\n');self.polls=0
  def poll(self):self.polls+=1;return None if self.polls==1 else 0
  def wait(self,timeout=None):return 0
 class FakeBA:
  def __init__(self,*a,**kw):pass
  def drain(self):return {'records':[],'terminal':'NATURAL'}
  def quick_stop(self):return None
  def sample(self,*a):return {'decision':{'decision':'CONTINUE'}}
 fakeguard=types.ModuleType('sweep_guard_cap1m');fakeguard.NativeDTCGuard=FakeBA
 fakecache=types.ModuleType('sweep_read_cache')
 class Adviser:
  def process(self,*args):pass
 fakecache.Adviser=Adviser;prior_modules={k:sys.modules.get(k)for k in ['sweep_guard_cap1m','sweep_read_cache']};sys.modules['sweep_guard_cap1m']=fakeguard;sys.modules['sweep_read_cache']=fakecache
 model_info=dict(pid=helper.pid,start_ticks=g.proc_start(helper.pid),mnt_namespace=sp2['execution_mnt_namespace'],maps=sp2['native_simulator_argv'][0],host_cpu_affinity_actual=[cpu],actual_process_limits_text='CPU_ONLY_FAKE_MAPS_FOR_LAUNCHER_CHAIN_TEST')
 n2.child_info=lambda pid:dict(model_info);n2._observer_race_children=lambda path:[str(helper.pid)]
 def fake_popen(argv,**kw):
  if any('accel-sim.out'in str(a)for a in argv)and'cwd'in kw:return FakeLauncher()
  return real_popen(argv,**kw)
 subprocess.Popen=fake_popen
 try:mock_receipt=n2.finish_cell(c2)
 finally:
  subprocess.Popen=real_popen
  for k,v in prior_modules.items():
   if v is None:sys.modules.pop(k,None)
   else:sys.modules[k]=v
 ip2=fixture/'control/qualification_ledger'/(c2+'.INTENT.json');out2=P(read(ip2)['output']);triple=[read(ip2),read(out2/'NATIVE_LAUNCH.json'),read(out2/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]
 check(all(v['resource_overlay_binding']==ins2['additional_binding']for v in triple),'real transformed native chain writes identical extra binding into INTENT/LAUNCH/PID')
 check(all(v['l2_mlp_execution_binding']==binding_before for v in triple),'INTENT/LAUNCH/PID preserve identical old full binding in real compiled path')
 check(all(v['observer_exit_race_binding']==triple[0]['observer_exit_race_binding']for v in triple),'INTENT/LAUNCH/PID retain original observer binding')
 check(mock_receipt['native_simulator_observed']and mock_receipt['stop_reason']is None,'synthetic launcher drives unchanged observer and natural-closure path only inside fixture')
 check(extra.verify(c2,e2)['status']=='PASS_ADDITIONAL_GUARDED_ADMISSION_BINDING','additional strict validates actually written triple fixture')
 # Actual frozen B guard, real dedicated native thread, empty resolver: no
 # simulator ownership or signals. Its real heartbeat feeds the A native gate.
 bm=load('actual_B_guard_CPU_integration',B_SOURCE)
 check(bm.jsonsha(dict(bm.DEFAULT_POLICY,**policy))==sha(HERE/'POLICY.json'),'A full canonical policy exactly equals B merged policy hash')
 class EmptyResolver:
  root=B_SOURCE.parent/'CPU_ISOLATED_REGISTRY'
  def targets(self):return []
 journal_dir=fixture/'actual_B_guard_CPU';guard=bm.MemoryGuard(EmptyResolver(),journal_dir,signals_enabled=True,policy=policy)
 record['guard_token']=guard.token;record['pause_journal_path']=str(journal_dir/'PAUSE_JOURNAL.jsonl');record['heartbeat_path']=str(journal_dir/'HEARTBEAT.json')
 c3=g.PILOT_CANDIDATES[2];select(c3)
 guard.execution_binding.update(overlay_id=g.OVERLAY_ID,registry_overlay_record_sha256=g.jsonsha(record),active_admission_token_sha256=q['active_resource_admission_token']['sha256'],aggressive_admission_armed=True)
 actual_stop=threading.Event();actual_thread=threading.Thread(target=guard.run,args=(actual_stop,),name='ACTUAL_B_GUARD_CPU_EMPTY_RESOLVER');actual_thread.start()
 try:
  deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   try:
    actual_h=g.heartbeat(record,policy,{'epoch':2},q,owner_lease=lease)[0];break
   except (OSError,RuntimeError,ValueError):time.sleep(.1)
  else:raise AssertionError('Actual B heartbeat cannot satisfy A gate: '+str(read(record['heartbeat_path'])))
  check(actual_h['guard_tid']==actual_thread.native_id,'actual B live native thread heartbeat consumed by A guard')
  check(actual_h['signals_enabled']is True and actual_h['shadow_mode']is False and not guard.handles,'actual signal-enabled empty resolver uses no model handles and sends no signals')
  e3=load('A_actual_B_prepare_CPU',PROD/'tools/l2_native.py');e3.R=fixture;e3.registered=e.registered;e3.assert_parent_lease=e.assert_parent_lease;e3.update_authority=e.update_authority
  est3=e3.spec_for(c3)['estimated_peak_model_RAM_bytes']
  def resources3(spec,fresh_source=False):
   row=copy.deepcopy(base);row['physical_RAM_pass']=True;row['total_projected_additional_RAM_bytes']=est3;row['own_ram_forecasts']=[dict(cohort=c3,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=est3)];return row
  e3.resources=resources3;put(fixture/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={c3:dict(host_cpu=cpu)}));g.install(e3,c3)
  check(e3.prepare(c3)['scientific_starts']==0,'real A native prepare accepts actual B heartbeat without model execution')
 finally:actual_stop.set();actual_thread.join(timeout=10)
 # Frontend no-overlay path delegates exact argument list without guard installation.
 frontend=load('guard_frontend_cpu',HERE/'guarded_frontend.py');calls=[]
 class FakeFrontend:
  def main(self,a):calls.append(a);return {'EXACT_UNMODIFIED_DELEGATION':a}
 frontend.load=lambda n,p:FakeFrontend()
 args=['result','archive','E2-DTCL2MLP-EXAMPLE']
 check(frontend.main(args)=={'EXACT_UNMODIFIED_DELEGATION':args}and calls==[args],'no-overlay archive delegates unchanged original frontend')
 args=['experiment','prepare',g.PILOT,'--project','DTC_L1']
 check(frontend.main(args)=={'EXACT_UNMODIFIED_DELEGATION':args},'no-overlay prepare delegates unchanged original frontend')
 for p,hsh in before.items():check(sha(p)==hsh,'original frozen bytes unchanged '+p)
 result=dict(status='PASS',actual_model_starts=0,full_native_prefix_intercepted=True,actual_compiled_INTENT_LAUNCH_PID_triple_qualified=True,additional_strict_cpu_qualified=True,no_overlay_original_strict_qualified=True,actual_B_guard_empty_resolver_native_prepare_qualified=True,production_registration_or_entry_mutation=False,checks=len(checks),check_labels=checks,CPU_fixture_root=str(fixture),scientific_option_count=len(s['expected_options']),Popen_interceptions=intercept,original_strict_real_result_readonly=chosen,limitations=['Actual B guard integration uses an empty resolver in an isolated CPU process; no production simulator handles or signals are acquired.','No production-parent insertion or IO-pressure soak has run; coordinator must validate/observe the real parent signal-enabled guard before activation.','Synthetic launcher/PID/telemetry and overlay gate fixtures are NOT completed scientific models; original natural-completion strict compatibility uses a separate real previously accepted result in read-only mode.','Fixture metadata approval/qualification stub is isolated only; not a production scientific or operational authorization.'],source_sha256={p.name:sha(p)for p in HERE.glob('*.py')},policy_sha256=sha(HERE/'POLICY.json'),B_guard_source_sha256=sha(B_SOURCE),original_frozen_source_sha256=before,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 put(HERE/'CPU_QUALIFICATION.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['check_labels','Popen_interceptions','source_sha256','original_frozen_source_sha256']}))
finally:
 guard_stop.set();guard_thread.join(timeout=10)
 helper.terminate();helper.wait(timeout=10)
