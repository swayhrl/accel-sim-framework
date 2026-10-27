"""Opt-in, shadow-default guard candidate. Importing never starts or signals anything.
SIGSTOP retains RSS. Only a matched registered new-request model can own a handle.
No kill/restart/refund; no change to cgroups, swap, frozen science or controllers.
"""
import os,signal,time,json,pathlib,hashlib,uuid,threading,select,sys
def jsonsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def filesha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
P=pathlib.Path;G=1024**3;REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
DEFAULT_POLICY=dict(soft_pause_bytes=20*G,hard_floor_bytes=10*G,resume_bytes=30*G,heartbeat_max_age_seconds=3.,period_seconds=.25,resume_interval_seconds=2.,burst_margin_bytes=2*G,finishable_seconds=15.,finishable_growth_bytes=128*1024**2,finishable_rate_bytes_per_second=1024**2,user_program_priority={},priority_weight_bytes_per_second=1024**2,pause_priority_mode='growth_first',reaction_growth_floor_bytes_per_second=8*1024**3,reaction_error_bytes=1024**3,actuation_budget_seconds=.25)
def read(p):return json.loads(P(p).read_bytes())
def proc(pid):
 p=P('/proc')/str(pid);a=(p/'stat').read_text().rsplit(')',1)[1].split();return dict(start_ticks=int(a[19]),state=a[0],rss_bytes=int(a[21])*os.sysconf('SC_PAGE_SIZE'),cpu_ticks=int(a[11])+int(a[12]))
def headroom_sample():
 mem=int(next(x.split()[1]for x in P('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024;c=P('/sys/fs/cgroup');mx=(c/'memory.max').read_text().strip();cur=int((c/'memory.current').read_text());st={a:int(b)for a,b in(x.split()for x in(c/'memory.stat').read_text().splitlines())};clean=max(0,st.get('file',0)-sum(st.get(x,0)for x in ['shmem','file_mapped','file_dirty','file_writeback']));credit=max(0,min(st.get('inactive_file',0),clean)-2*G);raw=None if mx=='max'else max(0,int(mx)-cur);effective=None if raw is None else raw+credit
 return dict(monotonic=time.monotonic(),host_available_bytes=mem,cgroup_raw_headroom_bytes=raw,cgroup_conservative_credit_bytes=credit,cgroup_effective_headroom_bytes=effective,headroom_bytes=min(mem,raw)if raw is not None else mem)
def admission_allowed(heartbeat,now,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));return bool(heartbeat and 0<=now-heartbeat.get('monotonic',-1e30)<=p['heartbeat_max_age_seconds']and heartbeat.get('healthy')and heartbeat.get('fresh_admission_allowed')and not heartbeat.get('fault'))
def is_finishable(job,p):
 return job.get('eta_seconds')is not None and job['eta_seconds']<=p['finishable_seconds']and job.get('remaining_growth_bytes',2**63)<=p['finishable_growth_bytes']and job.get('growth_rate',float('inf'))<=p['finishable_rate_bytes_per_second']
def decide(jobs,headroom,policy=None,last_resume_at=-1e30,now=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));now=time.monotonic()if now is None else now;assert 0<p['hard_floor_bytes']<p['soft_pause_bytes']<p['resume_bytes'];active=[x for x in jobs if not x.get('paused')and not x.get('externally_stopped')];paused=[x for x in jobs if x.get('paused')];prior=p['user_program_priority'];pause=[];resume=[];reason='HYSTERESIS_HOLD'
 def risk(x):
  values=(x.get('growth_rate',0),x.get('remaining_growth_bytes',0),prior.get(x.get('program'),0),x.get('rss_bytes',0))
  return(prior.get(x.get('program'),0),)+values if p['pause_priority_mode']=='user_first'else values
 if headroom<p['soft_pause_bytes']:
  reason='HARD_PRESSURE'if headroom<=p['hard_floor_bytes']else'SOFT_PRESSURE'
  # One demonstrably affordable escape can finish and free its actual RSS.
  safe=[x for x in active if x.get('hard_remaining_growth_bytes',2**63)+p['burst_margin_bytes']<=max(0,headroom-p['hard_floor_bytes'])]
  escape=min(safe,key=lambda x:(not is_finishable(x,p),x.get('eta_seconds')if x.get('eta_seconds')is not None else float('inf'),x.get('hard_remaining_growth_bytes',2**63)))if safe else None
  preserved_bound=escape.get('hard_remaining_growth_bytes',0)if escape is not None else 0
  for x in sorted(active,key=risk,reverse=True):
   if escape is not None and x['cohort']==escape['cohort']:continue
   if headroom>p['hard_floor_bytes']and is_finishable(x,p)and preserved_bound+x.get('hard_remaining_growth_bytes',2**63)+p['burst_margin_bytes']<=headroom-p['hard_floor_bytes']:
    preserved_bound+=x['hard_remaining_growth_bytes'];continue
   pause.append(x['cohort'])
  if not active and paused:
   affordable=[x for x in paused if x.get('hard_remaining_growth_bytes',2**63)+p['burst_margin_bytes']<=max(0,headroom-p['hard_floor_bytes'])]
   if affordable and now-last_resume_at>=p['resume_interval_seconds']:resume=[min(affordable,key=lambda x:(not is_finishable(x,p),x.get('hard_remaining_growth_bytes',2**63),x.get('paused_since',now)))['cohort']];reason='SAFE_SINGLE_ESCAPE'
   elif not affordable:reason='EXTERNAL_PRESSURE_NO_SAFE_PROGRESS'
 elif headroom>=p['resume_bytes']and paused and now-last_resume_at>=p['resume_interval_seconds']:
  affordable=[x for x in paused if x.get('hard_remaining_growth_bytes',2**63)+p['burst_margin_bytes']<=max(0,headroom-p['hard_floor_bytes'])]
  resume=[min(affordable,key=lambda x:(not is_finishable(x,p),x.get('remaining_growth_bytes',2**63),x.get('paused_since',now)))['cohort']]if affordable else[];reason='HYSTERESIS_RESUME_ONE'if affordable else'RESUME_GROWTH_BOUND_NOT_FIT'
 if not active and paused and not resume and now-last_resume_at>=p['resume_interval_seconds']:
  safe=[x for x in paused if x.get('hard_remaining_growth_bytes',2**63)+p['burst_margin_bytes']<=max(0,headroom-p['hard_floor_bytes'])]
  if safe:resume=[min(safe,key=lambda x:(not is_finishable(x,p),x.get('hard_remaining_growth_bytes',2**63),x.get('paused_since',now)))['cohort']];reason='SAFE_SINGLE_ESCAPE'
  else:reason='EXTERNAL_PRESSURE_NO_SAFE_PROGRESS'
 return dict(pause=pause,resume=resume,reason=reason,fresh_admission_allowed=headroom>=p['soft_pause_bytes']and not paused and not pause,headroom_bytes=headroom,no_RSS_release_assumed=True)

class NativeRegistryResolver:
 def __init__(self,root,registry_loader,command_marker='/root/data/dtc_failure_repair_20261025_v1/framework-build/accel-sim.out',finishable_estimator=None):
  self.root=P(root);self.registry_loader=registry_loader;self.command_marker=command_marker;self.finishable_estimator=finishable_estimator
 def targets(self):
  q=self.registry_loader();assert q['request']==REQ;targets=[];plan_path=self.root/'control/EXECUTION_PLAN.json';plan_sha=filesha(plan_path);assert q['execution_plan_sha256']==plan_sha
  for c,row in q['consumed'].items():
   if row.get('execution_receipt'):continue
   try:
    uid=str(uuid.UUID(row['uuid']));out=self.root/'DTC/run/results'/uid;ip=self.root/'control/qualification_ledger'/(c+'.INTENT.json');assert filesha(ip)==row['intent_sha256'];i=read(ip);assert i['cohort']==c and i['uuid']==uid and P(i['output'])==out
    sp=self.root/'control/specs'/(c+'.json');raw=sp.read_bytes();canonical_sha=hashlib.sha256(raw).hexdigest();assert canonical_sha==q['admitted_specs'][c];spec=json.loads(raw);assert spec['request']==REQ and spec['cohort']==c
    bp=self.root/'control/dispatch_bindings'/(c+'.json');binding=read(bp);bsha=filesha(bp);assert binding['cohort']==c and binding['canonical_spec_sha256']==canonical_sha and i['spec_sha256']==canonical_sha and type(binding['host_cpu'])is int;resolved=dict(spec,host_cpu=binding['host_cpu']);assert binding['resolved_spec_sha256']==jsonsha(resolved)
    d=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=read(out/'NATIVE_LAUNCH.json');assert launch['scientific_qualification_uuid']==uid
    for proof in [i,d,launch]:
     assert proof['dispatch_binding_sha256']==bsha;execution=proof['l2_mlp_execution_binding'];assert execution['request']==REQ and execution['plan_sha256']==plan_sha
    assert type(d['pid'])is int and type(d['start_ticks'])is int;actual=proc(d['pid']);assert actual['start_ticks']==d['start_ticks'];pp=P('/proc')/str(d['pid']);argv=[x.decode()for x in(pp/'cmdline').read_bytes().split(b'\0')if x];cmd=' '.join(argv)+' ';assert cmd==d['cmdline']and self.command_marker in cmd
    loader=str(self.root/'common-lib/ld-linux-x86-64.so.2');expected=[loader,'--inhibit-cache','--library-path',str(self.root/spec['project']/'env/lib'),*resolved['native_simulator_argv']];assert argv==expected and launch['argv'][launch['argv'].index('--')+1:]==expected
    configs=[expected[k+1]for k,v in enumerate(expected[:-1])if v=='-config'];assert configs==[x['path']for x in spec['configs']]and configs and all(P(x).is_relative_to(self.root/'DTC/env')for x in configs)
    assert sorted(os.sched_getaffinity(d['pid']))==d['host_cpu_affinity_actual']==[binding['host_cpu']]
    namespaces={k:os.readlink(pp/'ns'/k)for k in ['mnt','pid']};assert namespaces['mnt']==d['mnt_namespace']==spec['execution_mnt_namespace']==launch['host']['mnt_namespace'];assert namespaces['pid']==d['pid_namespace']==launch['host']['pid_namespace'];assert os.readlink(pp/'exe')==d['exe']
    targets.append(dict(cohort=c,uuid=uid,pid=d['pid'],start_ticks=d['start_ticks'],program=spec.get('program'),forecast_bytes=spec['estimated_peak_model_RAM_bytes'],hard_cap_bytes=spec['limits']['max_process_tree_rss_bytes'],command_marker=self.command_marker,expected_cmdline=cmd,expected_affinity=[binding['host_cpu']],expected_namespaces=namespaces,dispatch_binding_sha256=bsha,intent_sha256=row['intent_sha256'],plan_sha256=plan_sha,eta_seconds=None))
   except(FileNotFoundError,ProcessLookupError):continue
  if self.finishable_estimator:
   for meta in targets:
    estimate=self.finishable_estimator(dict(meta))
    if estimate is not None and estimate.get('confidence')=='RECENT_PROGRESS_ESTIMATE'and 0<=time.monotonic()-estimate.get('monotonic',-1e30)<=3 and estimate.get('eta_seconds',-1)>=0:meta['eta_seconds']=estimate['eta_seconds'];meta['eta_provenance']=estimate.get('source')
  return targets

class OwnedPidfd:
 def __init__(self,meta,signals_enabled=False):
  self.meta=dict(meta);self.signals_enabled=signals_enabled;self.paused=False;self.paused_since=None;before=proc(meta['pid']);assert before['start_ticks']==meta['start_ticks'];self.fd=os.pidfd_open(meta['pid'],0)
  try:
   after=proc(meta['pid']);assert after['start_ticks']==meta['start_ticks'];cmd=(P('/proc')/str(meta['pid'])/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace');assert meta['command_marker']in cmd and cmd==meta['expected_cmdline'];assert sorted(os.sched_getaffinity(meta['pid']))==meta['expected_affinity'];assert all(os.readlink(P('/proc')/str(meta['pid'])/'ns'/k)==v for k,v in meta['expected_namespaces'].items());self.externally_stopped=after['state']in['T','t']
  except BaseException:os.close(self.fd);raise
 def alive(self):
  poll=select.poll();poll.register(self.fd,select.POLLIN);return not poll.poll(0)
 def send(self,sig):
  assert self.signals_enabled and sig in[signal.SIGSTOP,signal.SIGCONT];assert self.alive();assert proc(self.meta['pid'])['start_ticks']==self.meta['start_ticks'];pp=P('/proc')/str(self.meta['pid']);assert(pp/'cmdline').read_bytes().replace(b'\0',b' ').decode()==self.meta['expected_cmdline'];assert sorted(os.sched_getaffinity(self.meta['pid']))==self.meta['expected_affinity'];assert all(os.readlink(pp/'ns'/k)==v for k,v in self.meta['expected_namespaces'].items());signal.pidfd_send_signal(self.fd,sig,None,0)
 def close(self):os.close(self.fd)

class MemoryGuard:
 def __init__(self,resolver,journal_dir,signals_enabled=False,policy=None,execution_binding=None):
  if signals_enabled:
   plan=read(resolver.root/'control/EXECUTION_PLAN.json')
   if resolver.root==P('/root/data/dtc_l2_mlp_exploration_20261027_v1'):assert os.getpid()==plan['parent_pid']and proc(os.getpid())['start_ticks']==plan['parent_start_ticks'],'Only the existing registered owner may enable production signals'
   else:assert plan.get('CPU_fixture_only')is True and resolver.root.is_relative_to(P(__file__).parent),'Nonproduction signals restricted to explicit local CPU fixture'
  self.execution_binding=dict(execution_binding or {});self.last_jobs={};self.fault_freeze_events=[];self.fault_freeze_summary=None;self.journal_degraded_errors=[];self.sample_count=0;self.last_step_seconds=.25;self.previous_headroom=None
  self.resolver=resolver;self.directory=P(journal_dir);self.directory.mkdir(parents=True,exist_ok=True);(self.directory/'PAUSE_JOURNAL.jsonl').touch(exist_ok=True);self.signals_enabled=signals_enabled;self.policy=dict(DEFAULT_POLICY,**(policy or {}));self.token=uuid.uuid4().hex;self.handles={};self.previous={};self.last_resume=-1e30;self.fault=None;self.lock=threading.RLock();self.owner_pid=os.getpid();self.source_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest();self.epoch=2;self.boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip();main=sys.modules['__main__'];objects=getattr(main,'DTC_L2_MLP_MEMORY_GUARD_OBJECTS_V1',{});objects[self.token]=self;setattr(main,'DTC_L2_MLP_MEMORY_GUARD_OBJECTS_V1',objects)
 def journal(self,event,**kw):
  if kw.get('cohort')in self.handles:
   meta=self.handles[kw['cohort']].meta;kw=dict(dict(uuid=meta['uuid'],pid=meta['pid'],start_ticks=meta['start_ticks']),**kw)
  with(self.directory/'PAUSE_JOURNAL.jsonl').open('a')as h:h.write(json.dumps(dict(event=event,monotonic=time.monotonic(),guard_token=self.token,owner_pid=self.owner_pid,request=REQ,epoch=self.epoch,boot_id=self.boot_id,source_sha256=self.source_sha256,**kw))+'\n');h.flush();os.fsync(h.fileno())
 def heartbeat(self,decision,healthy=True):
  now=time.monotonic();tid=threading.get_native_id();ownstat=proc(os.getpid());tidstat=proc(tid);paused=[dict(cohort=c,uuid=h.meta['uuid'],pid=h.meta['pid'],start_ticks=h.meta['start_ticks'],pidfd=h.fd,paused_since=h.paused_since)for c,h in self.handles.items()if h.paused];journal=self.directory/'PAUSE_JOURNAL.jsonl';raw=journal.read_bytes()if journal.exists()else b'';states=[dict(cohort=c,uuid=h.meta['uuid'],pid=h.meta['pid'],start_ticks=h.meta['start_ticks'],rss_bytes=self.last_jobs.get(c,{}).get('rss_bytes'),growth_rate=self.last_jobs.get(c,{}).get('growth_rate'),state='PAUSED_BY_GUARD'if h.paused else'EXTERNALLY_STOPPED'if h.externally_stopped else'RUNNING_OR_WAITING')for c,h in self.handles.items()]
  data=dict(self.execution_binding);data.update(decision);data.update(schema='L2MLP_GUARD_HEARTBEAT_V1',monotonic=now,guard_token=self.token,owner_pid=self.owner_pid,owner_start_ticks=ownstat['start_ticks'],monitor_pid=self.owner_pid,monitor_start_ticks=ownstat['start_ticks'],guard_tid=tid,guard_start_ticks=tidstat['start_ticks'],signals_enabled=self.signals_enabled,shadow_mode=not self.signals_enabled,healthy=healthy,fault=self.fault,request=REQ,epoch=self.epoch,boot_id=self.boot_id,source_sha256=self.source_sha256,monitor_source_sha256=self.source_sha256,policy_sha256=jsonsha(self.policy),warmup_complete=self.sample_count>=3,aggressive_admission_armed=self.execution_binding.get('aggressive_admission_armed')is True,fault_freeze_summary=self.fault_freeze_summary,journal_degraded_errors=self.journal_degraded_errors,live_generation_states=states,own_live_generations=states,paused_handles=paused,handle_state_sha256=jsonsha(paused),pause_journal_path=str(journal),pause_journal_prefix_bytes=len(raw),pause_journal_sha256=hashlib.sha256(raw).hexdigest(),pause_new_admission=not decision.get('fresh_admission_allowed',False))
  tmp=self.directory/'.HEARTBEAT.writing';tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(self.directory/'HEARTBEAT.json');return data
 def pause(self,c):
  h=self.handles[c];assert not h.externally_stopped
  if h.paused:return
  if proc(h.meta['pid'])['state']in['T','t']:
   h.externally_stopped=True;self.journal('SKIP_UNKNOWN_OR_TRACER_STOP',cohort=c);return
  self.journal('PAUSE_INTENT',cohort=c,pid=h.meta['pid'],start_ticks=h.meta['start_ticks'],rss_kept=True)
  if self.signals_enabled:
   h.send(signal.SIGSTOP);h.paused=True;h.paused_since=time.monotonic()
  self.journal('PAUSE_CONFIRMED'if self.signals_enabled else'SHADOW_PAUSE',cohort=c,pid=h.meta['pid'],start_ticks=h.meta['start_ticks'],pidfd=h.fd)
 def resume(self,c):
  h=self.handles[c];assert h.paused and not h.externally_stopped
  self.journal('RESUME_INTENT',cohort=c,pid=h.meta['pid'],start_ticks=h.meta['start_ticks'])
  if h.alive():h.send(signal.SIGCONT)
  h.paused=False;h.paused_since=None;self.last_resume=time.monotonic();self.journal('RESUME_CONFIRMED',cohort=c,pid=h.meta['pid'],start_ticks=h.meta['start_ticks'])
 def collect(self):
  targets=self.resolver.targets();seen=set();now=time.monotonic();jobs=[]
  for meta in targets:
   c=meta['cohort'];seen.add(c)
   if c not in self.handles:self.handles[c]=OwnedPidfd(meta,self.signals_enabled)
   h=self.handles[c];assert h.meta['pid']==meta['pid']and h.meta['start_ticks']==meta['start_ticks']
   if not h.alive():continue
   actual=proc(meta['pid']);old=self.previous.get(c)
   if not h.paused:
    if actual['state']not in['T','t']or(old and actual['cpu_ticks']>old.get('cpu_ticks',0)):h.externally_stopped=False
    elif actual['state']in['T','t']:h.externally_stopped=True
   rate=max(0,(actual['rss_bytes']-old['rss_bytes'])/(now-old['monotonic']))if old and now>old['monotonic']else 0;self.previous[c]=dict(rss_bytes=actual['rss_bytes'],monotonic=now,cpu_ticks=actual['cpu_ticks']);jobs.append(dict(meta,**actual,growth_rate=rate,remaining_growth_bytes=max(0,meta['forecast_bytes']-actual['rss_bytes']),hard_remaining_growth_bytes=max(0,meta['hard_cap_bytes']-actual['rss_bytes']),paused=h.paused,paused_since=h.paused_since,externally_stopped=h.externally_stopped))
  for c,h in list(self.handles.items()):
   if c not in seen or not h.alive():
    if h.paused and h.alive():
     self.fault='PAUSED_GENERATION_NOT_IN_CURRENT_AUTHORITY';continue
    h.close();del self.handles[c]
  self.last_jobs={x['cohort']:x for x in jobs};return jobs
 def step(self,sample=None):
  with self.lock:
   begun=time.monotonic();assert os.getpid()==self.owner_pid;jobs=self.collect();sample=headroom_sample()if sample is None else sample;now=time.monotonic();age=max(0,now-sample.get('monotonic',now));rate=sum(x['growth_rate']for x in jobs if not x['paused']);fall=0
   if self.previous_headroom:
    dt=now-self.previous_headroom[0]
    if dt>0:fall=max(0,(self.previous_headroom[1]-sample['headroom_bytes'])/dt)
   self.previous_headroom=(now,sample['headroom_bytes']);rate=max(rate,fall,self.policy['reaction_growth_floor_bytes_per_second']);latency=self.last_step_seconds+self.policy['period_seconds']+age+self.policy['actuation_budget_seconds'];needed=self.policy['hard_floor_bytes']+rate*latency+self.policy['burst_margin_bytes']+self.policy['reaction_error_bytes'];operating=dict(self.policy,soft_pause_bytes=max(self.policy['soft_pause_bytes'],needed),resume_bytes=max(self.policy['resume_bytes'],needed+10*G));d=decide(jobs,sample['headroom_bytes'],operating,self.last_resume,now);d['headroom_sample']=sample;d['reaction_envelope']=dict(aggregate_rate_bytes_per_second=rate,latency_seconds=latency,required_margin_bytes=needed,soft_pause_bytes=operating['soft_pause_bytes'],resume_bytes=operating['resume_bytes'],burst_bound_not_proven=True,ten_GiB_not_guaranteed_against_unbounded_burst=True)
   if self.fault:d['fresh_admission_allowed']=False;d['pause']=[];d['resume']=[];d['reason']='GUARD_FAULT_RETAINED_OWNERSHIP'
   for c in d['pause']:self.pause(c)
   for c in d['resume']:
    if self.signals_enabled:self.resume(c)
    else:self.journal('SHADOW_RESUME',cohort=c)
   if any(x.get('externally_stopped')for x in jobs):d['fresh_admission_allowed']=False;d['external_stop_detected']=True
   self.sample_count+=1;self.last_step_seconds=time.monotonic()-begun;d['actual_step_seconds']=self.last_step_seconds;return self.heartbeat(d)
 def recover_one(self,sample=None):
  """Explicit successor-owner recovery: one affordable owned handle, never all."""
  sample=headroom_sample()if sample is None else sample;jobs=self.collect();paused=[x for x in jobs if x['paused']];p=self.policy;available=max(0,sample['headroom_bytes']-p['hard_floor_bytes']-p['burst_margin_bytes']);fits=[x for x in paused if x['hard_remaining_growth_bytes']<=available]
  if sample['headroom_bytes']<p['resume_bytes']or not fits:return False
  if time.monotonic()-self.last_resume<p['resume_interval_seconds']:return False
  c=min(fits,key=lambda x:(not is_finishable(x,p),x['hard_remaining_growth_bytes'],x['paused_since']))['cohort'];self.journal('SAFE_RECOVERY_ONE',cohort=c);self.resume(c);return True
 def fault_freeze_cached(self,recheck_seconds=.5):
  """Freeze only cached, strongly bound active handles; never reload authority."""
  if not(self.signals_enabled and self.execution_binding.get('aggressive_admission_armed')is True):return dict(armed=False,signals=0,reason='UNARMED_OR_SHADOW_NO_FAULT_SIGNALS')
  with self.lock:
   pending={c for c,h in self.handles.items()if not h.paused};closed=[];stopped=[];refused=[];deadline=time.monotonic()+recheck_seconds
   def record(event,c,**extra):
    h=self.handles[c];v=dict(event=event,cohort=c,uuid=h.meta['uuid'],pid=h.meta['pid'],start_ticks=h.meta['start_ticks'],request=REQ,epoch=self.epoch,source_sha256=self.source_sha256,guard_token=self.token,monotonic=time.monotonic(),**extra);self.fault_freeze_events.append(v)
    try:self.journal(event,cohort=c,**extra)
    except BaseException as error:self.journal_degraded_errors.append(repr(error))
   while pending:
    for c in list(pending):
     h=self.handles[c]
     try:
      if not h.alive():closed.append(c);pending.remove(c);record('FAULT_GENERATION_ALREADY_CLOSED',c);continue
      actual=proc(h.meta['pid']);assert actual['start_ticks']==h.meta['start_ticks']
      if actual['state']in['T','t']:continue
      h.externally_stopped=False;record('FAULT_FREEZE_INTENT',c,rss_kept=True)
      # send() revalidates cached exact cmd/namespace/affinity/PID generation.
      h.send(signal.SIGSTOP);h.paused=True;h.paused_since=time.monotonic();stopped.append(c);pending.remove(c);record('FAULT_FREEZE_CONFIRMED',c,pidfd=h.fd)
     except(FileNotFoundError,ProcessLookupError):
      closed.append(c);pending.discard(c);record('FAULT_NATURAL_EXIT_RACE_NO_SIGNAL',c)
     except BaseException as error:
      if not h.alive():closed.append(c);pending.discard(c);record('FAULT_NATURAL_EXIT_RACE_NO_SIGNAL',c)
      else:refused.append(dict(cohort=c,error=repr(error)));pending.discard(c);record('FAULT_IDENTITY_OR_SIGNAL_REFUSED',c,error=repr(error))
    if not pending or time.monotonic()>=deadline:break
    time.sleep(.01)
   for c in pending:
    self.handles[c].externally_stopped=True;record('FAULT_PERSISTENT_EXTERNAL_OR_TRACE_STOP_NO_OWNERSHIP',c)
   summary=dict(armed=True,signals=len(stopped),paused_by_failsafe=stopped,naturally_closed=closed,persistent_external_or_trace_stops=sorted(pending),identity_or_signal_refused=refused,registry_reloaded=False,blind_CONT_sent=False,all_cached_generations_stopped_or_closed_or_external=not refused,containment_watch_required=bool(pending or refused))
   self.fault_freeze_summary=summary;return summary
 def run(self,stop_event):
  try:
   while not stop_event.is_set():self.step();stop_event.wait(self.policy['period_seconds'])
  except BaseException as error:
   self.fault=repr(error)
   try:self.journal('GUARD_FAULT_RETAIN_HANDLES',error=self.fault)
   except BaseException as failure:self.journal_degraded_errors.append(repr(failure))
   # Publish unhealthy/HOLD before any cached-handle emergency STOP actions.
   try:self.heartbeat(dict(fresh_admission_allowed=False,reason='GUARD_FAULT_FAILSAFE_PENDING'),healthy=False)
   except BaseException:pass
   containment=self.fault_freeze_cached()
   while containment.get('containment_watch_required')and not stop_event.is_set():
    try:self.heartbeat(dict(fresh_admission_allowed=False,reason='FAULT_CONTAINMENT_CACHED_WATCH'),healthy=False)
    except BaseException:pass
    stop_event.wait(.1)
    if not stop_event.is_set():containment=self.fault_freeze_cached(.1)
  finally:
   # Never blind-CONT under memory pressure. Normal stop also freezes cached
   # active generations when an aggressive pilot has armed this guard.
   if self.execution_binding.get('aggressive_admission_armed')is True and self.fault_freeze_summary is None:
    try:self.heartbeat(dict(fresh_admission_allowed=False,reason='GUARD_STOP_FAILSAFE_PENDING'),healthy=False)
    except BaseException:pass
    self.fault_freeze_cached()
   try:self.heartbeat(dict(fresh_admission_allowed=False,reason='GUARD_STOPPED_OR_FAULT_OWNERSHIP_RETAINED'),healthy=False)
   except BaseException:pass
 def close_after_safe_recovery(self):
  assert not any(h.paused for h in self.handles.values()),'Recover safely before closing pause handles'
  for h in self.handles.values():h.close()
  self.handles.clear()

def adopt_retained_guard(token):
 guard=getattr(sys.modules['__main__'],'DTC_L2_MLP_MEMORY_GUARD_OBJECTS_V1')[token];assert guard.owner_pid==os.getpid();assert guard.source_sha256==hashlib.sha256(P(__file__).read_bytes()).hexdigest();return guard
