"""Finite epoch2 entry for the explicitly authorized isolated Ada semantic candidate."""
import copy,fcntl,hashlib,json,os,pathlib,resource,signal,subprocess,sys,time,uuid
sys.path.insert(0,"/root/data/ada_native_extensions_stage4_20261024_v1")
from native_maps_observer_v1 import MapsObserver,stat as pid_stat
P=pathlib.Path; B=P('/root/data/ep_l2_main_ada_warpsync_maps_compat_20261024_v1'); N=P('/root/data/ep_l2_dtc_l1_native_v2')
C='EP_ADA_TRACE_COMPAT_WARPSYNC65_MAPS_V8_20261024_V1';GIB=2**30
sys.path.insert(0,'/root/data/ep_l2_main_vector_r5_20261023_v1');import vector_runtime as base
def read(p):return json.loads(P(p).read_text())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):
 with P(p).open('x')as f:json.dump(x,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def need(x,m):
 if not x:raise RuntimeError(m)
def spec():
 s=read(B/'control/FROZEN_SPEC.json');need(s['request']==C and s['maximum_application_attempts']==1 and list(s['cases'])==['warpsync65_maps_v8_v1'],'wrong exact spec')
 for p,h in s['pinned_files'].items():need(sha(p)==h,'pin drift '+p)
 return s
def guard():
 host=base.identity();reg=read(base.REG);epoch=read(base.EPOCH);need(sha(base.REG)==epoch['native_registry_sha256'],'epoch CAS drift')
 need(epoch['epoch']==2 and epoch['holder']==os.uname().nodename,'wrong epoch')
 reserve=sum(v.get('reserved_write_bytes',0)for k,v in reg['registered_future_requests'].items()if k!=C)
 v=os.statvfs(B);free=v.f_frsize*v.f_bavail;need(free>=5*GIB+GIB+reserve+128*2**20,'native disk reserve')
 mem=int(next(x.split()[1]for x in P('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
 current=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip();limits=spec()['limits']
 need(mem>=limits['minimum_host_available_memory_bytes'] and (maximum=='max'or int(maximum)-current>=limits['memory_cap_bytes']+512*2**20),'physical RAM/cgroup reserve')
 return dict(identity=host,free_bytes=free,foreign_reserved_write_bytes=reserve,baseline_floor_bytes=5*GIB,headroom_bytes=GIB,own_output_cap_bytes=limits['output_cap_bytes'],host_available_memory_bytes=mem,cgroup_current=current,cgroup_max=maximum)
def argv(case):
 s=spec();c=s['cases'][case];return [s['loader'],'--inhibit-cache','--library-path',s['library_path'],s['binary'],'-trace',c['trace_entry'],'-config',c['config']]
def qualify():
 s=spec();g=guard();need(not(B/'control/NATIVE_HELP_INTENT_R2.json').exists(),'help already consumed')
 args=[s['loader'],'--inhibit-cache','--library-path',s['library_path'],s['binary'],'-h'];put(B/'control/NATIVE_HELP_INTENT_R2.json',dict(argv=args,full_application=False))
 cp=subprocess.run(args,cwd=B,env={'PATH':'/usr/bin:/bin','LANG':'C'},capture_output=True,timeout=20)
 text=cp.stdout+cp.stderr;(B/'control/ELF_HELP_R2.log').write_bytes(text)
 need(cp.returncode in(0,1)and b'gpu_tot_sim_insn'not in text and (b'option'in text.lower()or b'usage'in text.lower())and b'error while loading shared libraries'not in text,'positive help qualification')
 q=dict(status='PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED',spec_sha256=sha(B/'control/FROZEN_SPEC.json'),resources=g,help_returncode=cp.returncode,help_sha256=sha(B/'control/ELF_HELP_R2.log'))
 put(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json',q);return q
def registry(reg,e,op):
 oldB,oldC=base.B,base.C;base.B=B;base.C=C
 try:base.registry_change(reg,e,op)
 finally:base.B=oldB;base.C=oldC
def campaign(reg,s):
 members=s['campaign']['request_ids'];return sum(reg['registered_future_requests'].get(k,{}).get('consumed',0)for k in members)
def register():
 lock=base.lock();s=spec();guard();q=read(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json')
 approval=read(B/'control/PARENT_APPROVED_FOR_REGISTRATION.json');need(approval['spec_sha256']==sha(B/'control/FROZEN_SPEC.json') and approval['request']==C and approval['approved_for_registration'] is True,'parent review missing/stale')
 need(q['spec_sha256']==sha(B/'control/FROZEN_SPEC.json'),'qualification stale');reg=read(base.REG);e=read(base.EPOCH)
 need(C not in reg['registered_future_requests'],'already registered');need(campaign(reg,s)<s['campaign']['application_attempt_ceiling'],'campaign exhausted')
 reg['registered_future_requests'][C]=dict(project='EP_L2',owner='EP-MAIN',state='AUTHORIZED_UNUSED',budget=1,consumed=0,reserved_write_bytes=s['limits']['output_cap_bytes'],automatic_retry=False,spec_path=str(B/'control/FROZEN_SPEC.json'),spec_sha256=sha(B/'control/FROZEN_SPEC.json'),authorization_path=str(B/'control/USER_AUTHORIZATION.json'),authorization_sha256=sha(B/'control/USER_AUTHORIZATION.json'),native_qualification_sha256=sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json'),case_consumption={})
 reg['new_scientific_budget_remaining']+=1;registry(reg,e,'REGISTER');return dict(status='FINITE_ADA_COMPAT_REGISTERED',request=C,budget=1,defined_cases=list(s['cases']))
def run(case):
 lock=base.lock();s=spec();g=guard();need(case in s['cases'],'undefined case');reg=read(base.REG);e=read(base.EPOCH);row=reg['registered_future_requests'][C]
 need(row['spec_sha256']==sha(B/'control/FROZEN_SPEC.json')and row['authorization_sha256']==sha(B/'control/USER_AUTHORIZATION.json')and row['native_qualification_sha256']==sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json'),'registered spec/auth/qualification drift');need(row['state']=='AUTHORIZED_UNUSED'and row['budget']==1 and row['consumed']==0 and case not in row['case_consumption']and reg['new_scientific_budget_remaining']>0,'no unused exact attempt')
 need(campaign(reg,s)<s['campaign']['application_attempt_ceiling'],'campaign exhausted')
 uid=uuid.uuid4().hex;out=B/'run'/uid;out.mkdir();args=argv(case)
 intent=dict(request=C,case=case,uuid=uid,argv=args,spec_sha256=sha(B/'control/FROZEN_SPEC.json'),consumed_before_fork=True,automatic_retry=False,output=str(out))
 put(B/'control'/(case+'.INTENT.json'),intent);row['consumed']+=1;row['state']='RUNNING';row['case_consumption'][case]=intent;reg['new_scientific_budget_remaining']-=1;registry(reg,e,'CONSUME_'+case)
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','ADA6_SEMANTIC_DIAG':'1','OMP_NUM_THREADS':'1','ADA_NATIVE_MAP_CHECKPOINTS':'1'}
 def limits():
  os.setsid();os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(s['limits']['memory_cap_bytes'],s['limits']['memory_cap_bytes']))
 start=time.monotonic();p=None;reason=None;peak=0;observed=None;last=-5;peakrss=0;observer=None;checkpoints=[];maps_proof=None
 try:
  with(out/'raw.log').open('xb')as log:
   p=subprocess.Popen(args,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits)
   observer=MapsObserver(p.pid,s['pinned_files'],out/'MAP_OBSERVATIONS')
   while p.poll()is None:
    try:
     state=pid_stat(p.pid)
     if state['state'] in ('T','t'):
      text=(out/'raw.log').read_text(errors='replace')
      label='FIRST_ISSUE' if not checkpoints else 'TERMINAL'
      need(len(checkpoints)<2 and 'ADA_NATIVE_MAP_CHECKPOINT '+label in text,'unknown/reordered host stop')
      observer.sample(label)
      need(any(x['primary'] and s['binary'] in x['paths'] for x in observer.checkpoints if x['label']==label),'primary executable absent at checkpoint')
      checkpoints.append(label)
      if observed is None:
       observed=base.info(p.pid);put(out/'NATIVE_PROCESS.json',observed)
      os.kill(p.pid,signal.SIGCONT)
     else:observer.sample()
    except FileNotFoundError:pass
    size=sum(x.stat().st_size for x in out.rglob('*')if x.is_file());peak=max(peak,size)
    if size>s['limits']['output_cap_bytes']:reason='OUTPUT_CAP'
    if time.monotonic()-start>s['limits']['wall_seconds']:reason='TIME_CAP'
    if time.monotonic()-start-last>=s['limits']['resource_poll_seconds']:
     last=time.monotonic()-start;g=guard();rss=int(next(x.split()[1]for x in(P('/proc')/str(p.pid)/'status').read_text().splitlines()if x.startswith('VmRSS:')))*1024;peakrss=max(peakrss,rss)
     with(out/'RESOURCE_SAMPLES.jsonl').open('a')as samples:samples.write(json.dumps(dict(elapsed=last,rss_bytes=rss,resources=g))+'\n')
     if rss>s['limits']['memory_cap_bytes']:reason='RSS_CAP'
    if(B/'control/ABORT').exists():reason='EXPLICIT_ABORT'
    if reason:os.killpg(p.pid,signal.SIGTERM);break
    time.sleep(s['limits']['maps_sample_seconds'])
   try:rc=p.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
   if rc==0 and reason is None:maps_proof=observer.require_terminal()
 except BaseException as error:
  reason=type(error).__name__+':'+str(error);rc=None
 finally:
  if p is not None and p.poll()is None:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
 result=dict(request=C,case=case,uuid=uid,exit_code=rc,stop_reason=reason,elapsed=time.monotonic()-start,peak_result_bytes=peak,peak_rss_bytes=peakrss,native_observed=observed is not None,maps_observation_proof=maps_proof,host_observation_stop_profile=True,raw_sha256=sha(out/'raw.log'),output=str(out),application_attempt_consumed=1,automatic_retry=False,scientific_qualification='PENDING_INDEPENDENT_SEMANTIC_JOIN',hardware_performance_qualification=False)
 put(out/'EXIT.json',result);put(B/'control'/(case+'.DONE.json'),result)
 reg=read(base.REG);e=read(base.EPOCH);reg['registered_future_requests'][C]['state']='COMPAT_PARTIAL_COMPLETE';reg['registered_future_requests'][C]['case_consumption'][case]['exit_receipt']=str(out/'EXIT.json');registry(reg,e,'CLOSE_'+case)
 return result
if __name__=='__main__':
 try:
  op=sys.argv[1]
  result=qualify()if op=='qualify'else register()if op=='register'else run(sys.argv[2])if op=='run-native'else dict(spec=spec(),resources=guard())
  print(json.dumps(result,indent=2))
 except Exception as error:print(json.dumps(dict(status='HOLD',reason=str(error),automatic_retry=False)),file=sys.stderr);sys.exit(2)
