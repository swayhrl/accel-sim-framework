#!/usr/bin/env python3
"""Main-only finite exact8 candidate. Import/default never activates or starts science.
Reuses pinned predecessor claim/poll/closed-view mechanics. No Git publisher."""
import argparse,fcntl,hashlib,importlib.util,json,os,pathlib,subprocess,sys,time,uuid
P=pathlib.Path
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1')
V=J/'research/performance_first_v5_20261105_v1'
CONTROL=V/'activation_20261105_v1/control'
PREV=J/'research/performance_first_v2_20261103_v1/activation_20261104_v1/agent_d_execution/finite_main_authorized18.py'
PREV_SHA='414826aa29620a4daf2cc73a230786bee072d58ac8c2217d7e0f9c834e9d7f33'
if hashlib.sha256(PREV.read_bytes()).hexdigest()!=PREV_SHA:raise ValueError('pinned predecessor mechanics drift')
sp=importlib.util.spec_from_file_location('pfv5_pinned_finite_main_mechanics',PREV)
E=importlib.util.module_from_spec(sp);sp.loader.exec_module(E)
need,read,put,ref,exact,sha,now,lock,authority,pid_identity,same_live=map(lambda n:getattr(E,n),['need','read','put','ref','exact','sha','now','lock','authority','pid_identity','same_live'])
ADMISSION,RESTORE,OWNERSHIP=E.ADMISSION,E.RESTORE,E.OWNERSHIP
TERMINAL=E.TERMINAL
REQUESTS={'A':'EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1','B':'EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1','D':'EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1'}
BUDGETS={'A':3,'B':2,'D':3}
ROOTS={'A':V/'track_a_wv/host_private_candidate_v1/main_materialized/37e5a2db776190ee3f74/execution','B':V/'track_b_fullf/host_private_candidate_v1/execution','D':V/'track_d_workloads/three_mm/execution'}
# Only this imported module object's scope changes; predecessor source is untouched.
E.REQUESTS=REQUESTS;E.BUDGETS=BUDGETS;E.ROOTS=ROOTS
def same_ref(a,b):return E.same_ref(a,b)
def load_module(r,name):
 need(sha(r['path'])==r['sha256'],'immutable module drift '+r['path'])
 z=importlib.util.spec_from_file_location(name,r['path']);m=importlib.util.module_from_spec(z);z.loader.exec_module(m);return m
def sealed_command(fd,argv):
 head=os.pread(fd,64,0);p='/proc/self/fd/'+str(fd)
 if head.startswith(b'#!/bin/sh\n'):return ['/bin/sh',p,*argv]
 if head.startswith(b'#!/usr/bin/env python3\n')or head.startswith(b'#!/usr/bin/python3\n'):return ['/usr/bin/python3','-B',p,*argv]
 raise ValueError('unqualified sealed entry interpreter')
def validate_manifest(m):
 need(m['schema']=='EP_MAIN_PFV5_AUTHORIZED8_EXECUTION_MANIFEST_V1'and P(m['control_root'])==CONTROL,'exact V5 manifest control/schema')
 need(m['new_model_start_ceiling']==8 and m['authorized_max_concurrent_models']==10 and m['automatic_retry']is False and m['refund']is False,'exact8 cap10 no retry/refund')
 need(same_ref(m['user_authorization_ref'],ref(CONTROL/'USER_AUTHORIZATION.json')),'exact parent authorization')
 auth=exact(m['user_authorization_ref'])
 need(auth['explicit_user_approval']is True and auth['approved_total_launches']==8 and auth['global_EP_model_cap']==10 and auth['old_budgets_reusable']is False and auth['automatic_retry']is False and auth['refund']is False,'fresh parent exact8 approval')
 need(auth['all_eight_independently_released']is True and auth['baseline_completion_is_launch_gate']is False and auth['WV_REF_completion_is_launch_gate']is False and auth['cross_family_completion_gates']is False,'no application-completion predecessor')
 fam={r['name']:r for r in auth['families']}
 need(set(fam)==set(REQUESTS)==set(m['groups']),'exact three groups A/B/D')
 pts=m['points'];need(len(pts)==len({p['cohort']for p in pts})==8,'exact unique eight')
 expected_modes={'A':{'S','WV_ZERO_RO'},'B':{'F_BASELINE','F_PRESSURE_EPOCH'},'D':{'S','WV_ZERO_RO'}}
 for g,request in REQUESTS.items():
  z=m['groups'][g];f=fam[g]
  need(z['request_id']==f['request']==request and z['budget']==f['approved_launches']==BUDGETS[g]and P(z['data_root'])==ROOTS[g],'exact request/root/budget')
  need(z['route_file']==('NATIVE_ENTRY_ROUTE_V3.json'if g=='B'else'NATIVE_ENTRY_ROUTE_V4.json'),'exact group route carrier')
  need({p['cohort']for p in pts if p['group']==g}==set(f['allowed_cohorts']),'exact approved cohorts')
  need(same_ref(z['native_entry_ref'],ref(z['native_entry_ref']['path'])),'entry pin')
  for p in pts:
   if p['group']!=g:continue
   s=exact(p['spec_ref']);need(P(p['spec_ref']['path'])==ROOTS[g]/'cases'/p['cohort']/'control/FROZEN_SPEC.json','exact installed Spec path')
   need(s['cohort']==p['cohort']and s['science_request_id']==request and s['source_identity']==f['Source5'],'exact Source/request/cohort')
   need(len(s['expected_effective_options'])==(282 if g=='D' else 283)and s['expected_effective_options']['-trace']==s['trace_entry'],'source-specific full282/283 input map')
   need(s['source_keep']is True and s['automatic_retry']is False and s['application_budget']==s['approved_launches']==1,'one start no retry KEEP')
   need(p['host_limits']==s['limits']and p['estimated_peak_RAM_bytes']==s['estimated_peak_RAM_bytes'],'exact Host limits')
   need(all(type(s['limits'][k])is int and s['limits'][k]>0 for k in['AS_bytes','RSS_bytes','wall_seconds','result_bytes']),'typed hard limits')
   need(s['limits']['AS_bytes']>=s['limits']['RSS_bytes']and type(s['estimated_peak_RAM_bytes'])is int and 0<s['estimated_peak_RAM_bytes']<=s['limits']['RSS_bytes'],'Host bounds')
   family_auth=exact(s['Main_scientific_launch_authorization'])
   need(family_auth['hard_wall_seconds']==s['limits']['wall_seconds'],'exact current Main-authorized hard wall; no old ceiling')
   need(same_ref(s['native_entry_ref'],z['native_entry_ref']),'group/Spec entry')
   need(s['mode']in expected_modes[g],'exact approved mode')
   need(s['expected_effective_options']['-dram_latency']=='100'and s['expected_effective_options']['-gpgpu_clock_domains']==('1132.0:1132.0:1132.0:1700.0'if g=='B'else'1132.0:1132.0:1132.0:850.0'),'exact clocks/latency')
  need({exact(p['spec_ref'])['mode']for p in pts if p['group']==g}==expected_modes[g],'exact mode population')
 need(P(m['global_admission_lock'])==ADMISSION and P(m['runtime_global_restore_lock'])==RESTORE,'shared Main admission/restore locks')
 need(P(m['accept_serial_lock'])not in[ADMISSION,RESTORE],'separate outer accept lock')
 return True
def stage_decisions(points,rows,views,technical=()):
 held=set(technical);out={}
 for p in points:
  c=p['cohort']
  if c in rows:out[c]=dict(status='CONSUMED',reason='NEVER_RETRY_OR_REFUND')
  elif c in held:out[c]=dict(status='HOLD',reason='EXACT_POINT_TECHNICAL_HOLD_ONLY')
  else:out[c]=dict(status='RELEASE',reason='INDEPENDENT_EXACT_USER_AUTHORIZED_POINT_NO_PREDECESSOR')
 return out
def concurrency_capacity(active,local):
 need(type(active)is int and active>=0 and type(local)is int and local>=0,'actual process counts')
 return active<10 and local<10
class Executor(E.Executor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_manifest(self.m)
  self.C=CONTROL;self.states={};self.running={};self.pending_accept=[];self.accepting=None;self.started=time.monotonic()
  self.lastresource={};self.session=str(uuid.uuid4());self.points=[]
  for p in self.m['points']:
   p=dict(p);p['mode']=exact(p['spec_ref'])['mode'];self.points.append(p)
  self.bypoint={p['cohort']:p for p in self.points};self.specs={p['cohort']:exact(p['spec_ref'])for p in self.points};self.failures={}
 def event(self,event,**data):
  put(self.C/'EXECUTOR_EVENTS'/(str(time.time_ns())+'.'+str(uuid.uuid4())+'.json'),dict(utc=now(),session=self.session,event=event,**data))
 def effective_cap(self):return 10
 def native(self,op,c,**kwargs):
  need(c in self.bypoint and op in['prepare','inspect','run-native','accept'],'exact scoped Native operation')
  p=self.bypoint[c];g=p['group'];s=self.specs[c];z=self.m['groups'][g]
  guard=load_module(s['native_route_guard_ref'],'pfv5_dispatcher_exact_route_guard')
  fd,proof=guard.sealed_entry(ROOTS[g]/'control'/z['route_file'])
  try:
   need(same_ref(proof['entry_ref'],z['native_entry_ref'])and c in proof['exact_cohorts'],'wrong installed group entry')
   put(self.C/'ROUTE_INVOCATIONS'/(c+'.'+op+'.'+str(uuid.uuid4())+'.json'),dict(**proof,cohort=c,operation=op,science_consumption_here=False))
   return subprocess.Popen(sealed_command(fd,['experiment',op,c,'--project','EP_L2']),pass_fds=(fd,),**kwargs)
  finally:os.close(fd)
 def closed_view(self,c,row):
  v=super().closed_view(c,row)
  if v.get('archived'):
   ar=exact(row['archive_receipt_ref']);rr=ar['native_restores'];h=ar['archive_ref']['sha256']
   need(len({r.get('target')for r in rr})==2 and all(r.get('archive_sha256')==h for r in rr),'two distinct native restores of same full archive')
   v['two_restores_complete']=True
  return v
 def decisions(self,reg,rows):
  views={};errors={}
  for p in self.points:
   c=p['cohort']
   try:views[c]=self.closed_view(c,rows.get(c,{}))
   except Exception as exc:errors[c]=repr(exc)
  held=set(self.technical_holds())|{c for c,s in self.states.items()if s.get('terminal_hold')}
  out=stage_decisions(self.points,rows,views,held)
  return out,views,errors
 def available_cpu(self,p):
  # Per-point Spec resource module decides actual CPU occupancy, including foreign commitments.
  source='from ep_perf_common_v2 import *;s=read(ROOT/"cases"/sys.argv[1]/"control/FROZEN_SPEC.json");r=module(s["resource_module_ref"],"pfv5_controller_resource_snapshot");print(json.dumps(r.snapshot()))'
  cp=self.group_call(p['group'],source,[p['cohort']])
  need(cp.returncode==0,'resource snapshot HOLD '+cp.stderr[-2000:])
  s=json.loads(cp.stdout);need(s.get('current_request')==REQUESTS[p['group']],'cross-request resource snapshot')
  need('occupied_model_or_claim_cpus'in s,'missing actual occupied CPU population')
  need(not s.get('foreign_metadata_errors'),'RESOURCE_ADMISSION_HOLD:foreign metadata '+repr(s.get('foreign_metadata_errors')))
  occupied=set(s['occupied_model_or_claim_cpus'])|{r['cpu']for r in self.running.values()}
  allowed=set(os.sched_getaffinity(0));candidates=self.m.get('host_cpu_candidates',sorted(allowed))
  return next((c for c in candidates if type(c)is int and c in allowed and c not in occupied),None),s
 def claim(self,p,cpu):
  # The pinned predecessor writes claims only after new full schema/current CPU validation.
  code='from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);s=dict(s,host_cpu=int(sys.argv[2]));print(json.dumps(validate_spec_contract(s,require_bound_cpu=True)))'
  cp=self.group_call(p['group'],code,[p['cohort'],cpu]);need(cp.returncode==0,'PRECLAIM_SCHEMA_OR_SCOPE_HOLD:'+cp.stderr[-3000:])
  super().claim(p,cpu)
 def priorities(self,p):return ({'B':10,'A':20,'D':30}[p['group']],p['cohort'])
 def start(self,p):
  c=p['cohort'];g=p['group']
  if time.monotonic()<self.lastresource.get(c,0)+10:return False
  self.lastresource[c]=time.monotonic()
  with lock(ADMISSION):
   reg,rows=self.rows();need(c not in rows,'consumed point never refork')
   decisions,views,errors=self.decisions(reg,rows)
   if decisions[c]['status']!='RELEASE':return False
   active=sum(r.get('state')in['CONSUMED_BEFORE_FORK','RUNNING']for qid,q in reg['registered_future_requests'].items()if qid.startswith('EP_')and isinstance(q.get('consumed'),dict)for r in q['consumed'].values())
   if not concurrency_capacity(active,len(self.running)):return False
   try:cpu,snapshot=self.available_cpu(p)
   except Exception as exc:
    self.states[c]=dict(status='RESOURCE_SNAPSHOT_HOLD',reason=str(exc),terminal_hold=False,utc=now());return False
   if cpu is None:return False
   nas=E.nas_capacity_gate(self.specs[c]);put(self.C/'NAS_ADMISSION'/(c+'.'+str(uuid.uuid4())+'.json'),dict(**nas,cohort=c,spec_ref=p['spec_ref']))
   self.claim(p,cpu)
   cp=self.group_call(g,'from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);resource_gate(s,dispatch_binding(sys.argv[1]))',[c])
   if cp.returncode:
    self.release_unconsumed_claim(p);message=(cp.stdout+cp.stderr)[-6000:];resource='RESOURCE_ADMISSION_HOLD:'in message or 'V4_REQUEST_NOT_REGISTERED'in message
    self.states[c]=dict(status='RESOURCE_ADMISSION_HOLD'if resource else'PRECONSUME_LOCAL_QUALIFICATION_HOLD',terminal_hold=not resource,reason=message,utc=now());return False
   path=self.C/'native_logs'/(c+'.'+str(uuid.uuid4())+'.run.log');path.parent.mkdir(parents=True,exist_ok=True);f=path.open('xb')
   try:proc=self.native('run-native',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   except BaseException:f.close();self.release_unconsumed_claim(p);raise
   self.running[c]=dict(process=proc,log=f,cpu=cpu,launcher=pid_identity(proc.pid),log_path=str(path),started_monotonic=time.monotonic())
   self.states[c]=dict(status='NATIVE_IN_PROGRESS',cpu=cpu,native_frontend_pid=proc.pid,utc=now());self.event('SINGLE_MAIN_NATIVE_STARTED',cohort=c,pid=proc.pid);return True
 def accept_one(self):
  # Start at most one archive/accept asynchronously; never wait for it in the scheduler.
  if self.accepting or not self.pending_accept:return
  path=P(self.m['accept_serial_lock']);path.parent.mkdir(parents=True,exist_ok=True);handle=path.open('a+b')
  try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:handle.close();return
  c=self.pending_accept.pop(0);logpath=self.C/'native_logs'/(c+'.'+str(uuid.uuid4())+'.accept.log');f=logpath.open('xb')
  try:proc=self.native('accept',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
  except Exception as exc:
   f.close();fcntl.flock(handle,fcntl.LOCK_UN);handle.close();self.states[c]=dict(status='ACCEPT_ARCHIVE_START_HOLD',terminal_hold=True,reason=repr(exc),utc=now());return
  self.accepting=dict(cohort=c,process=proc,log=f,lock=handle,log_path=str(logpath));self.event('ASYNC_ACCEPT_ARCHIVE_STARTED',cohort=c,pid=proc.pid)
 def poll_accept(self):
  if not self.accepting:return
  a=self.accepting;rc=a['process'].poll()
  if rc is None:return
  c=a['cohort'];a['log'].close();fcntl.flock(a['lock'],fcntl.LOCK_UN);a['lock'].close();self.accepting=None
  _,rows=self.rows();row=rows.get(c,{})
  state=row.get('state','CONSUMED_ACCEPT_REVIEW_HOLD')
  self.states[c]=dict(status=state,accept_returncode=rc,terminal_hold=state not in TERMINAL,utc=now())
  if state in TERMINAL:
   try:self.closed_view(c,row)
   except Exception as exc:self.states[c].update(terminal_hold=True,reason='ARCHIVE_CLOSURE_REVIEW_HOLD:'+repr(exc))
  self.event('ASYNC_ACCEPT_ARCHIVE_FINISHED',cohort=c,state=state,returncode=rc,no_model_retry=True)
 def check_activation(self):
  a=read(self.C/'MAIN_EXECUTOR_ACTIVATION.json')
  need(a['status']=='MAIN_REVIEWED_PFV5_EXACT8_ACTIVATION'and a['approved_by']=='EP-MAIN','explicit Main exact8 activation')
  need(same_ref(a['manifest_ref'],ref(self.manifest_path))and same_ref(a['executor_ref'],ref(__file__)),'exact manifest/controller pins')
  need(a['no_retry']is True and a['no_refund']is True,'no retry/refund')
  for old in a.get('prior_executor_started_refs',[]):need(not same_live(exact(old)['process']),'previous Main dispatcher live')
  reg,rows=self.rows();need(not rows,'fresh exact8 cannot resume/refork consumed points')
  for g,qid in REQUESTS.items():
   q=reg['registered_future_requests'][qid]
   need(q['budget']==q['remaining']==BUDGETS[g]and not q['consumed'],'fresh independent per-group budgets3/2/3')
   need(q['admitted_specs']=={p['cohort']:p['spec_ref']['sha256']for p in self.points if p['group']==g},'exact registered Specs')
   need(same_ref(q['native_entry_ref'],self.m['groups'][g]['native_entry_ref']),'registered sole Native entry')
   need(not read(ROOTS[g]/'control/DISPATCH_CLAIMS.json')['claims'],'fresh group claims not empty')
   s=next(self.specs[p['cohort']]for p in self.points if p['group']==g)
   load_module(s['native_route_guard_ref'],'pfv5_activation_guard').validate_current(ROOTS[g]/'control'/self.m['groups'][g]['route_file'])
 def summary(self,decisions=None):
  reg,rows=self.rows();out=[]
  for p in self.points:
   c=p['cohort'];r=rows.get(c,{});s=self.specs[c];v=dict(cohort=c,group=p['group'],mode=s['mode'],spec_ref=p['spec_ref'],state=r.get('state',self.states.get(c,{}).get('status','NOT_STARTED')),consumed=c in rows,controller_state=self.states.get(c),family_decision=(decisions or{}).get(c))
   for k in ['done_ref','accepted_point_ref','archive_receipt_ref','validation_ref']:v[k]=r.get(k)
   out.append(v)
  result=dict(schema='EP_MAIN_PFV5_FINITE_EXACT8_RESULTS_V1',utc=now(),session=self.session,points=out,budgets={g:{k:reg['registered_future_requests'][q].get(k)for k in['budget','remaining','state']}for g,q in REQUESTS.items()},active_native_frontends=len(self.running),async_archive_cohort=self.accepting['cohort']if self.accepting else None,new_model_start_ceiling=8,max_global_EP_models=10,not_global_project_experiment_limit=True,no_consumed_retry=True,no_refund=True,Source_keep=True,raw_polling=False,automatic_git_publication=False)
  put(self.C/'RESULTS_CURRENT.json',result);return result
 def warn_soft_references(self):
  for c,v in self.running.items():
   s=self.specs[c];soft=s.get('soft_wall_reference_seconds')
   if isinstance(soft,dict):soft=soft.get(s['mode'])
   if type(soft)is int and soft>0 and not v.get('soft_reference_warned')and time.monotonic()-v['started_monotonic']>soft:
    self.event('SOFT_REFERENCE_EXCEEDED_ADVISORY_ONLY',cohort=c,elapsed_seconds=time.monotonic()-v['started_monotonic'],soft_reference_seconds=soft,hard_wall_seconds=s['limits']['wall_seconds'],signals_sent=0,admission_or_completion_gate_added=False)
    v['soft_reference_warned']=True
 def run(self):
  self.check_activation()
  with lock(self.C/'SINGLE_MAIN_PFV5_EXECUTOR.lock',True),lock(OWNERSHIP,True):
   need(not(self.C/'EXECUTOR_STARTED.json').exists(),'no automatic controller rerun/resume')
   put(self.C/'EXECUTOR_STARTED.json',dict(schema='EP_MAIN_PFV5_EXACT8_EXECUTOR_STARTED_V1',utc=now(),session=self.session,process=pid_identity(os.getpid()),executor_ref=ref(__file__),manifest_ref=ref(self.manifest_path),no_consumed_retry=True))
   while True:
    try:self.poll()
    except Exception as exc:self.event('LOCAL_POLL_HOLD_NO_KILL',reason=repr(exc))
    try:self.poll_accept()
    except Exception as exc:self.event('LOCAL_ACCEPT_POLL_HOLD_NO_KILL',reason=repr(exc))
    self.warn_soft_references()
    reg,rows=self.rows();decisions,views,errors=self.decisions(reg,rows)
    # Dispatch all ready short/independent points before starting an archive worker.
    for p in sorted(self.points,key=self.priorities):
     c=p['cohort']
     if c in rows or c in self.running or self.states.get(c,{}).get('terminal_hold'):continue
     if decisions[c]['status']=='HOLD':
      self.states[c]=dict(status='LOCAL_EXACT_HOLD_NOT_CONSUMED',terminal_hold=True,reason=decisions[c]['reason'],utc=now());continue
     if decisions[c]['status']!='RELEASE':continue
     if len(self.running)>=10:break
     try:self.start(p)
     except Exception as exc:self.states[c]=dict(status='LOCAL_PRELAUNCH_REVIEW_HOLD',terminal_hold=True,reason=repr(exc),utc=now());self.event('LOCAL_PRELAUNCH_HOLD',cohort=c,reason=repr(exc))
    self.accept_one();self.summary(decisions)
    _,rows=self.rows();settled=all(rows.get(p['cohort'],{}).get('state')in TERMINAL or self.states.get(p['cohort'],{}).get('terminal_hold')for p in self.points)
    if settled and not self.running and not self.pending_accept and not self.accepting:break
    if time.monotonic()-self.started>self.m.get('admission_wait_and_execution_wall_seconds',7*86400)and not self.running and not self.accepting:break
    time.sleep(5)
   result=self.summary(decisions)
   put(self.C/'EXECUTOR_FINISHED.json',dict(schema='EP_MAIN_PFV5_EXACT8_EXECUTOR_FINISHED_V1',utc=now(),session=self.session,status='FINITE_TERMINAL_OR_MAIN_REVIEW_HOLD',manifest_ref=ref(self.manifest_path),consumed=sum(p['consumed']for p in result['points']),no_retry=True,no_refund=True,automatic_git_publication=False))
def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);g=ap.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');a=ap.parse_args(argv)
 if a.run:Executor(a.manifest).run()
 else:validate_manifest(read(a.manifest));print('PASS_PASSIVE_V5_EXACT8_NO_START')
if __name__=='__main__':main()

