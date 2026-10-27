"""Real SIGSTOP/CONT only on isolated small dummy allocators; never simulations."""
import os,sys,time,json,pathlib,subprocess,importlib.util,hashlib,threading,uuid,copy
P=pathlib.Path;B=P(__file__).parent;s=importlib.util.spec_from_file_location('candidate_memory_guard',B/'memory_guard.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);G=m.G;checks=[]
def ck(name,v):assert v,name;checks.append(name)
def sample(g):return dict(monotonic=time.monotonic(),headroom_bytes=g*G)
def wait_state(pid,st):
 end=time.monotonic()+3
 while time.monotonic()<end:
  if m.proc(pid)['state']in st:return
  time.sleep(.01)
 raise AssertionError('process state timeout')
p=m.DEFAULT_POLICY;a=dict(cohort='growth',program='a',growth_rate=3*G,remaining_growth_bytes=10*G,hard_remaining_growth_bytes=12*G,rss_bytes=G,paused=False);b=dict(cohort='finishing',program='b',growth_rate=0,remaining_growth_bytes=1024,hard_remaining_growth_bytes=1024,rss_bytes=G,eta_seconds=3,paused=False)
d=m.decide([a,b],18*G,now=10);ck('soft_pauses_growth_keeps_finishable',d['pause']==['growth']and'finishing'not in d['pause']);ck('STOP_not_credited_as_RSS_release',d['no_RSS_release_assumed'])
d=m.decide([a,b],8*G,now=10);ck('external_burst_hard_pressure_pauses_all_growth',set(d['pause'])=={'growth','finishing'}and not d['fresh_admission_allowed'])
pa=dict(a,paused=True,paused_since=1);ck('hysteresis_no_premature_multi_resume',not m.decide([pa,dict(b,paused=False)],25*G,now=10)['resume'])
ck('resume_one_over30',m.decide([pa],35*G,now=10)['resume']==['growth'])
ck('all_paused_safe_single_escape_below30',m.decide([pa],25*G,now=10)['resume']==['growth'])
ck('all_paused_no_unsafe_escape_under10',m.decide([pa],8*G,now=10)['reason']=='EXTERNAL_PRESSURE_NO_SAFE_PROGRESS')
ck('huge_remaining_growth_not_blindly_resumed',not m.decide([dict(pa,hard_remaining_growth_bytes=100*G)],35*G,now=10)['resume'])
ck('resume_rate_limited',not m.decide([pa],35*G,last_resume_at=9,now=10)['resume'])
ck('fresh_admission_stale_heartbeat_closed',not m.admission_allowed(dict(monotonic=1,healthy=True,fresh_admission_allowed=True),10))
ck('fresh_admission_fault_closed',not m.admission_allowed(dict(monotonic=10,healthy=True,fresh_admission_allowed=True,fault='bad'),10))
ck('fresh_admission_healthy_open',m.admission_allowed(dict(monotonic=10,healthy=True,fresh_admission_allowed=True,fault=None),10))
c=dict(a,cohort='user_priority',program='priority',growth_rate=G)
d=m.decide([a,c,b],18*G,dict(user_program_priority={'priority':10000},pause_priority_mode='user_first'),now=10);ck('configurable_pause_priority_visible',d['pause'][0]=='user_priority')
d=m.decide([a,c,b],18*G,dict(user_program_priority={'priority':10000}),now=10);ck('growth_rate_remains_first_by_default',d['pause'][0]=='growth')
heavy_finish=[dict(b,cohort='f'+str(i),hard_remaining_growth_bytes=4*G)for i in range(3)];d=m.decide(heavy_finish,18*G,now=10);ck('finishable_group_growth_bound_not_oversold',len(d['pause'])>=2)
# Exactly56MiB allocator payload total; no actual simulation target is used.
script=B/'CPU_DUMMY_ALLOCATOR.py';script.write_text('import sys,time,select\\na=bytearray(int(sys.argv[1])*1024**2)\\nfor i in range(0,len(a),4096):a[i]=1\\nprint("READY",flush=True)\\nx=0\\nwhile True:\\n for i in range(10000):x+=i\\n if select.select([sys.stdin],[],[],0)[0]:\\n  if sys.stdin.readline().strip()=="quit":break\\n'.replace('\\n','\n'))
children=[];guard=None;shadow=None
try:
 root=B/'CPU_ISOLATED_REGISTRY';c='E2-DTCL2MLP-CPU-GUARD-DH-P0-V1';uid=str(uuid.uuid4());out=root/'DTC/run/results'/uid
 for path in [root/'control/specs',root/'control/qualification_ledger',root/'control/dispatch_bindings',root/'DTC/env/lib',root/'common-lib',out]:path.mkdir(parents=True,exist_ok=True)
 loader=root/'common-lib/ld-linux-x86-64.so.2'
 if not loader.exists():loader.symlink_to('/lib64/ld-linux-x86-64.so.2')
 cfg=root/'DTC/env/dummy.config';cfg.write_text('CPU fixture only')
 native=[sys.executable,'-B',str(script),'48','DTC_GUARD_CPU_DUMMY_ALLOCATOR','-config',str(cfg)];argv=[str(loader),'--inhibit-cache','--library-path',str(root/'DTC/env/lib'),*native];cpu=min(os.sched_getaffinity(0))
 def pin():os.sched_setaffinity(0,{cpu})
 production_runtime=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');trace_argv=[str(production_runtime/'common-lib/ld-linux-x86-64.so.2'),'--library-path',str(production_runtime/'tools/lib')+':'+str(production_runtime/'common-lib'),str(production_runtime/'tools/bin/strace'),'-f','-e','trace=none','-o',str(B/'CPU_DUMMY_STRACE.log'),'--',*argv]
 own=subprocess.Popen(trace_argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,preexec_fn=pin);foreign=subprocess.Popen([sys.executable,'-B',str(script),'8','FOREIGN_DUMMY_NEVER_SIGNAL'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);children=[own,foreign];assert own.stdout.readline().strip()=='READY'and foreign.stdout.readline().strip()=='READY';model_pid=int((P('/proc')/str(own.pid)/'task'/str(own.pid)/'children').read_text().split()[0]);real=m.proc(model_pid);ck('real_dummy_under_actual_native_strace',model_pid!=own.pid);foreign_start=m.proc(foreign.pid)
 ns={k:os.readlink(P('/proc')/str(model_pid)/'ns'/k)for k in ['pid','mnt']};plan=root/'control/EXECUTION_PLAN.json';plan.write_text(json.dumps({'CPU_fixture_only':True}));plan_sha=m.filesha(plan);spec=dict(request=m.REQ,cohort=c,program='dummy',project='DTC',host_cpu=None,native_simulator_argv=native,configs=[dict(path=str(cfg))],execution_mnt_namespace=ns['mnt'],estimated_peak_model_RAM_bytes=64*1024**2,limits={'max_process_tree_rss_bytes':96*1024**2});sp=root/'control/specs'/(c+'.json');sp.write_text(json.dumps(spec));canonical=m.filesha(sp);bp=root/'control/dispatch_bindings'/(c+'.json');bp.write_text(json.dumps(dict(cohort=c,canonical_spec_sha256=canonical,host_cpu=cpu,resolved_spec_sha256=m.jsonsha(dict(spec,host_cpu=cpu)))));binding_sha=m.filesha(bp);execution=dict(request=m.REQ,plan_sha256=plan_sha)
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=dict(cohort=c,uuid=uid,output=str(out),spec_sha256=canonical,dispatch_binding_sha256=binding_sha,l2_mlp_execution_binding=execution);ip.write_text(json.dumps(intent));pidproof=dict(pid=model_pid,start_ticks=real['start_ticks'],cmdline=' '.join(argv)+' ',dispatch_binding_sha256=binding_sha,l2_mlp_execution_binding=execution,host_cpu_affinity_actual=[cpu],mnt_namespace=ns['mnt'],pid_namespace=ns['pid'],exe=os.readlink(P('/proc')/str(model_pid)/'exe'));pidpath=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';pidpath.write_text(json.dumps(pidproof));launch=dict(scientific_qualification_uuid=uid,dispatch_binding_sha256=binding_sha,l2_mlp_execution_binding=execution,argv=['fixture-strace','--',*argv],host=dict(mnt_namespace=ns['mnt'],pid_namespace=ns['pid']));lp=out/'NATIVE_LAUNCH.json';lp.write_text(json.dumps(launch));q=dict(request=m.REQ,execution_plan_sha256=plan_sha,consumed={c:{'uuid':uid,'intent_sha256':m.filesha(ip)}},admitted_specs={c:canonical});resolver=m.NativeRegistryResolver(root,lambda:copy.deepcopy(q),'DTC_GUARD_CPU_DUMMY_ALLOCATOR');meta=resolver.targets()[0]
 # Deliberately corrupt proof chains; every case must reject before any signal.
 for name,path,bad,good in [
 ('wrong_launch_UUID_rejected',lp,dict(launch,scientific_qualification_uuid=str(uuid.uuid4())),launch),
 ('wrong_dispatch_binding_rejected',pidpath,dict(pidproof,dispatch_binding_sha256='0'*64),pidproof),
 ('wrong_namespace_rejected',pidpath,dict(pidproof,mnt_namespace='mnt:[wrong]'),pidproof),
 ('foreign_PID_file_mixup_rejected',pidpath,dict(pidproof,pid=foreign.pid,start_ticks=foreign_start['start_ticks']),pidproof)]:
  path.write_text(json.dumps(bad))
  try:resolver.targets()
  except AssertionError:checks.append(name)
  else:raise AssertionError(name+' accepted')
  path.write_text(json.dumps(good))
 saved=q['consumed'][c]['intent_sha256'];q['consumed'][c]['intent_sha256']='0'*64
 try:resolver.targets()
 except AssertionError:checks.append('registry_INTENT_SHA_mismatch_rejected')
 else:raise AssertionError('wrong INTENT hash accepted')
 q['consumed'][c]['intent_sha256']=saved
 rejected_root=B/'CPU_NOT_AUTHORIZED_TO_SIGNAL';(rejected_root/'control').mkdir(parents=True,exist_ok=True);(rejected_root/'control/EXECUTION_PLAN.json').write_text('{}');badresolver=m.NativeRegistryResolver(rejected_root,lambda:q,'DTC_GUARD_CPU_DUMMY_ALLOCATOR')
 try:m.MemoryGuard(badresolver,B/'CPU_REJECTED_GUARD',True)
 except AssertionError:checks.append('signals_enable_requires_existing_owner_or_explicit_CPU_fixture')
 else:raise AssertionError('unauthorized signal guard constructed')
 ck('only_registered_newREQ_dummy_discovered',len(resolver.targets())==1 and meta['pid']==model_pid and meta['pid']!=foreign.pid)
 try:m.OwnedPidfd(dict(meta,start_ticks=real['start_ticks']+1),True)
 except AssertionError:checks.append('PID_generation_mismatch_rejected')
 else:raise AssertionError('wrong PID generation accepted')
 oldq=dict(q,request='OLD_DTC_REQUEST')
 try:m.NativeRegistryResolver(root,lambda:oldq,'DTC_GUARD_CPU_DUMMY_ALLOCATOR').targets()
 except AssertionError:checks.append('old_request_rejected_before_signal')
 else:raise AssertionError('old request accepted')
 shadow=m.MemoryGuard(resolver,B/'CPU_SHADOW',False);before=m.proc(model_pid);heartbeat=shadow.step(sample(8));ck('heartbeat_policy_and_paused_state_hashes',heartbeat['policy_sha256']==m.jsonsha(shadow.policy)and heartbeat['handle_state_sha256']==m.jsonsha(heartbeat['paused_handles']));ck('adaptive_reaction_envelope_recorded',heartbeat['reaction_envelope']['ten_GiB_not_guaranteed_against_unbounded_burst']);time.sleep(.15);ck('shadow_never_signals',m.proc(model_pid)['state']not in['T','t']and not shadow.handles[c].paused);shadow.close_after_safe_recovery()
 guard=m.MemoryGuard(resolver,B/'CPU_REAL_DUMMY_SIGNALS',True);guard.collect();pre=m.proc(model_pid);foreign_pre=m.proc(foreign.pid);
 end=time.monotonic()+3
 while not guard.handles[c].paused and time.monotonic()<end:
  guard.collect()
  if not guard.handles[c].externally_stopped:guard.pause(c)
  time.sleep(.01)
 assert guard.handles[c].paused;wait_state(model_pid,['T','t']);stopped=m.proc(model_pid);time.sleep(.3);after=m.proc(model_pid)
 ck('real_dummy_STOP_stops_CPU',after['cpu_ticks']==stopped['cpu_ticks']);ck('STOP_keeps_RSS',after['rss_bytes']>=pre['rss_bytes']*.95);ck('foreign_dummy_CPU_continues',m.proc(foreign.pid)['cpu_ticks']>foreign_pre['cpu_ticks']);ck('pidfd_pause_handle_retained',guard.handles[c].paused and guard.handles[c].alive())
 def fail():raise RuntimeError('injected guard failure with low headroom')
 guard.step=fail;guard.run(threading.Event());ck('exception_low_headroom_does_not_CONT',m.proc(model_pid)['state']in['T','t']and guard.handles[c].paused);hb=m.read(guard.directory/'HEARTBEAT.json');ck('exception_blocks_fresh_admission',not m.admission_allowed(hb,time.monotonic()));successor=m.adopt_retained_guard(guard.token);ck('successor_retains_same_pidfd_object',successor is guard and successor.handles[c].fd==guard.handles[c].fd)
 ck('low_headroom_recovery_refused',not successor.recover_one(sample(8))and m.proc(model_pid)['state']in['T','t']);ck('safe_recovery_one_succeeds',successor.recover_one(sample(64)));wait_state(model_pid,['R','S']);t=m.proc(model_pid)['cpu_ticks'];time.sleep(.3);ck('real_dummy_CONT_resumes_CPU',m.proc(model_pid)['cpu_ticks']>t)
 # A guard failure before any pause must halt an armed owned allocator too.
 guard.execution_binding['aggressive_admission_armed']=False;before_unarmed=m.proc(model_pid)['cpu_ticks'];guard.run(threading.Event());time.sleep(.15);ck('unarmed_fault_does_not_STOP_running_allocator',not guard.handles[c].paused and m.proc(model_pid)['cpu_ticks']>before_unarmed)
 guard.execution_binding['aggressive_admission_armed']=True;foreign_before=m.proc(foreign.pid)['cpu_ticks'];guard.resolver.registry_loader=lambda:(_ for _ in()).throw(RuntimeError('registry intentionally unavailable'));guard.run(threading.Event());wait_state(model_pid,['T','t']);ck('armed_fault_freezes_cached_owned_allocator',guard.handles[c].paused and guard.fault_freeze_summary['signals']==1);time.sleep(.15);ck('armed_fault_foreign_keeps_running',m.proc(foreign.pid)['cpu_ticks']>foreign_before);ck('failsafe_does_not_reload_broken_registry',guard.fault_freeze_summary['registry_reloaded']is False);ck('armed_fault_never_blind_CONT',guard.fault_freeze_summary['blind_CONT_sent']is False and guard.handles[c].paused)
 # Restore read-only identity provider only for qualified successor recovery.
 guard.resolver.registry_loader=lambda:copy.deepcopy(q);time.sleep(2.1);ck('armed_fault_safe_successor_can_resume',guard.recover_one(sample(64)));wait_state(model_pid,['R','S'])
 # A prior external stop must not acquire automatic CONT ownership. Keep a
 # fault containment watcher alive until explicit same-owner handoff/stop.
 handle=guard.handles[c];handle.send(__import__('signal').SIGSTOP);wait_state(model_pid,['T','t']);handle.paused=False;handle.externally_stopped=True;stopper=threading.Event();watch=threading.Thread(target=guard.run,args=(stopper,),name='CPU_FAULT_CONTAINMENT');watch.start();time.sleep(.75);ck('persistent_external_stop_keeps_fault_watcher_alive',watch.is_alive()and m.proc(model_pid)['state']in['T','t']);ck('persistent_external_stop_does_not_claim_CONT_ownership',not handle.paused);stopper.set();watch.join(3);ck('fault_watcher_explicit_handoff_closes',not watch.is_alive());handle.send(__import__('signal').SIGCONT);handle.externally_stopped=False;wait_state(model_pid,['R','S'])
 journal=[json.loads(x)for x in(guard.directory/'PAUSE_JOURNAL.jsonl').read_text().splitlines()];actions=[x for x in journal if x.get('cohort')==c and x.get('guard_token')==guard.token];ck('all_preempts_source_epoch_UUID_generation_traced',all(x['epoch']==2 and x['request']==m.REQ and x['uuid']==uid and x['start_ticks']==real['start_ticks']and x['source_sha256']==guard.source_sha256 for x in actions))
 own.stdin.write('quit\n');own.stdin.flush();own.wait(5);ck('pidfd_observes_original_generation_exit',not guard.handles[c].alive());closed=guard.fault_freeze_cached();ck('failsafe_natural_exit_race_is_closed_not_error',closed['signals']==0 and not closed['identity_or_signal_refused']and c in closed['naturally_closed'])
 try:guard.handles[c].send(__import__('signal').SIGSTOP)
 except AssertionError:checks.append('dead_pidfd_cannot_hit_reused_numeric_PID')
 else:raise AssertionError('dead pidfd signal unexpectedly accepted')
 guard.close_after_safe_recovery();ck('closed_handle_cleanup_only_after_safe_resume',not guard.handles)
finally:
 # Test-only tiny dummy cleanup. Never a production emergency-CONT policy.
 if guard:
  for h in guard.handles.values():
   if h.paused and h.alive():h.send(__import__('signal').SIGCONT);h.paused=False
 for child in children:
  if child.poll()is None:child.stdin.write('quit\n');child.stdin.flush();child.wait(5)
result=dict(status='PASS',checks=checks,passed=len(checks),python_version=sys.version,allocated_dummy_payload_MiB_total=56,real_simulator_signals=0,production_installation=False,production_parent_attached=False,source_sha256=hashlib.sha256((B/'memory_guard.py').read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),SIGSTOP_retains_RSS=True,production_fault_policy='retain_parent_object_pidfds_and_journal; fresh_admission_HOLD; safe_single_recovery_only')
(B/'CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
