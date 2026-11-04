#!/usr/bin/env python3
"""Idle same-owner cap10 candidate. No live mutation or automatic activation."""
import argparse,copy,hashlib,sys,pathlib,subprocess,time,uuid
P=pathlib.Path;V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1');PREV=V/'recovery_20261104_v1/agent_d_successor/finite_same_owner_successor_v2.py'
if hashlib.sha256(PREV.read_bytes()).hexdigest()!='36baa9f0f63320c7b8063c3d70df9b2e0f49e2c68fafd26b93887280f920945a':raise RuntimeError('frozen recovery predecessor drift')
sys.path.insert(0,str(PREV.parent));import finite_same_owner_successor_v2 as R
from finite_same_owner_successor_v2 import *
CONTROL=V/'activation_20261104_v1/recovery_20261104_v1/concurrency10_20261104_v1/control'
def validate_manifest10(m):
 need(m['schema']=='EP_MAIN_V2_CAP10_SAME_OWNER_EXECUTION_MANIFEST_V1'and P(m['control_root'])==CONTROL,'cap10 unique control/schema');need(m['max_concurrent_models']==10,'authorized max10')
 prior=exact(m['predecessor_manifest_ref']);need(prior['schema']=='EP_MAIN_V2_SAME_OWNER_RECOVERY_EXECUTION_MANIFEST_V1','exact previous same-owner manifest')
 amendment=exact(m['concurrency_amendment_authorization_ref']);need(P(m['concurrency_amendment_authorization_ref']['path'])==CONTROL/'USER_CONCURRENCY10_AUTHORIZATION.json','exact amendment path')
 need(amendment['authority']=='EXPLICIT_CURRENT_CHAT_USER_CONCURRENCY_AMENDMENT'and amendment['approved_global_EP_model_cap']==10 and amendment['previous_global_EP_cap']==2 and amendment['total_new_scientific_start_ceiling']==18 and amendment['additional_scientific_budget']==0 and amendment['Source_ELF_input_effective282_observer_and_stage_conditions_unchanged']is True,'explicit user only-concurrency amendment')
 for g in REQUESTS:need(same_ref(m['groups'][g]['authorization_ref'],prior['groups'][g]['authorization_ref']),'original family user authorization bytes preserved')
 preserved=m['preserved_consumed_spec_refs'];need(set(preserved)<=(SYSTEM|HIGH),'known preserved consumed population');pp={p['cohort']:p for p in prior['points']}
 for p in m['points']:
  if p['cohort']in preserved:need(same_ref(p['spec_ref'],preserved[p['cohort']])and same_ref(p['spec_ref'],pp[p['cohort']]['spec_ref']),'consumed checkpoint spec never changes')
 index=exact(m['resource_only_migration_index_ref']);need(index['schema']=='EP_MAIN_CAP10_RESOURCE_ONLY_DYNAMIC_SPEC_MIGRATION_V1'and set(index['allowed_changed_fields'])=={'resource_module_ref','resource_policy_ref','pinned_files'}and index['global_EP_model_limit']==10 and index['science_budget_changed']is False and index['runtime_or_native_changed']is False,'Main exact resource-only migration index')
 revised={row['cohort']:row for row in index['rows']};need(set(revised)|set(preserved)==SYSTEM|HIGH and not(set(revised)&set(preserved)),'all18 split consumed/resource-only revisions')
 for p in m['points']:
  if p['cohort']in revised:
   row=revised[p['cohort']];need(same_ref(row['original_spec_ref'],pp[p['cohort']]['spec_ref'])and row['successor_spec_ref']['sha256']==p['spec_ref']['sha256']and set(row['changed_fields'])<={'resource_module_ref','resource_policy_ref','pinned_files'},'exact previous/candidate resource-only SHA chain')
 adjusted=copy.deepcopy(m);adjusted['schema']='EP_MAIN_V2_SAME_OWNER_RECOVERY_EXECUTION_MANIFEST_V1';adjusted['control_root']=str(R.RECOVERY_CONTROL);adjusted['max_concurrent_models']=2;R.validate_recovery_manifest(adjusted);return True

def concurrency_capacity(active,local,cap):
 need(type(cap)is int and 1<=cap<=10,'finite authorized concurrency1..10');need(type(active)is int and active>=0 and type(local)is int and local>=0,'actual counts');return active<cap and local<cap

class Executor10(R.Successor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_manifest10(self.m);self.C=P(self.m['control_root']);self.states={};self.running={};self.pending_accept=[];self.started=time.monotonic();self.lastpublish=0;self.lastresource={};self.fatal=[];self.session=str(uuid.uuid4());self.points=self.m['points'];self.bypoint={p['cohort']:p for p in self.points};self.specs={p['cohort']:exact(p['spec_ref'])for p in self.points};self.phase_cache={};self.failures={};self.initial_consumed=sorted(self.m['preserved_consumed_spec_refs'])
 def effective_cap(self):
  p=self.C/'MAIN_MODEL_CONCURRENCY_POLICY.json'
  if not p.exists():return 10
  q=read(p);need(q['approved_by']=='EP-MAIN'and same_ref(q['manifest_ref'],ref(self.manifest_path)),'Main exact concurrency policy');v=q['max_concurrent_models'];need(type(v)is int and 1<=v<=10,'no cap beyond10');return v
 def check_activation(self):
  a=read(self.C/'MAIN_CAP10_IDLE_HANDOFF_AUTHORIZATION.json');need(a['schema']=='EP_MAIN_V2_CAP10_IDLE_HANDOFF_ACTIVATION_V1'and a['status']=='MAIN_REVIEWED_IDLE_OWNER_CAP10_HANDOFF_AUTHORIZED'and a['approved_by']=='EP-MAIN','Main explicit idle handoff')
  need(same_ref(a['executor_ref'],ref(__file__))and same_ref(a['manifest_ref'],ref(self.manifest_path))and a['no_retry']is True and a['no_refund']is True,'exact code/manifest/no refund')
  need(same_ref(a['concurrency_amendment_authorization_ref'],self.m['concurrency_amendment_authorization_ref']),'activation must bind explicit user cap10 amendment');exact(a['concurrency_amendment_authorization_ref'])
  old=exact(a['predecessor_started_ref']);need(same_ref(old['manifest_ref'],self.m['predecessor_manifest_ref'])and not same_live(old['process']),'previous generation live/wrong manifest')
  snap=exact(a['consumed_snapshot_ref']);requests=snap.get('requests',snap);reg,rows=self.rows();need(set(rows)==set(self.m['preserved_consumed_spec_refs']),'consumed population exact')
  for g,qid in REQUESTS.items():
   q=reg['registered_future_requests'][qid];sq=requests[qid]if qid in requests else requests[g]
   need(q['budget']==sq['budget']==BUDGETS[g]and q['remaining']==sq['remaining']==BUDGETS[g]-len(q['consumed']),'original budget no refund');need(q['consumed']==sq['consumed'],'exact terminal snapshot')
   need(q['admitted_specs']=={p['cohort']:p['spec_ref']['sha256']for p in self.points if p['group']==g},'exact resource-only successor specs')
   cl=read(P(self.m['groups'][g]['data_root'])/'control/DISPATCH_CLAIMS.json');need(cl==exact(a['claims_snapshot_refs'][g])and not cl['claims'],'idle claims0 required')
   for c,row in q['consumed'].items():need(row['state']in TERMINAL and self.closed_view(c,row)['archived'],'all consumed terminal/archive required')
  need(sha(self.m['shared_native_ref']['path'])==self.m['shared_native_ref']['sha256'],'exact globalNative')
 def close_handoff_done(self):
  _,rows=self.rows();need(all(rows[c]['state']in TERMINAL for c in self.initial_consumed),'idle handoff cannot accept pending')
 def native(self,op,c,**kwargs):
  need(c not in self.m['preserved_consumed_spec_refs'],'consumed cannot fork/accept again');return E.Executor.native(self,op,c,**kwargs)
 def _verify_inherited_stage(self,path,value):
  path=P(path);g='highclock'if path.is_relative_to(P(self.m['groups']['highclock']['data_root']))else'system'
  if g=='highclock':
   freq=1700 if path.name=='EXTENSION1700_MAIN_REVIEW.json'or(path.parent.name=='conditional_release'and'_1700_'in path.name)else 1275
   case=next(p['cohort']for p in self.points if p['group']==g and self.specs[p['cohort']]['mode']=='S'and p['cohort'].endswith('_'+str(freq)+'_V1'))
   code='from ep_perf_native_wv_modes_draft import *;s=read(spec_path(sys.argv[1]));r,_=authority();q=r["registered_future_requests"][GOAL];print(enforce_stage_gates(s,q,r))'
  else:
   w='FWT'if path.stem=='FWT'or'_FWT_'in path.name else'GEMM';case=next(p['cohort']for p in self.points if p['group']==g and system_meta(p['cohort'])==(w,'G64W16_FRFCFS256')and self.specs[p['cohort']]['mode']=='WV_ZERO_RO')
   code='from ep_perf_common_v2 import *;import mode_contract;s=read(ROOT/"cases"/sys.argv[1]/"control/FROZEN_SPEC.json");r,_=authority();print(mode_contract.validate_combo_release(s,r,ROOT/"control/conditional_release"/(sys.argv[1]+".json"),data_root=ROOT))'
  r=self.group_call(g,code,[case]);need(r.returncode==0,'actual inherited stage gate rejected '+r.stderr[-2000:]);self.event('INHERITED_STAGE_VERIFIED_NO_REWRITE',path=str(path),group=g,cohort=case)
 def immutable(self,path,value):
  path=P(path)
  if path.exists()and read(path)!=value:
   old=read(path);need('controller_manifest_ref'in old and'controller_manifest_ref'in value,'only controller provenance may differ')
   need({k:v for k,v in old.items()if k!='controller_manifest_ref'}=={k:v for k,v in value.items()if k!='controller_manifest_ref'},'scientific stage content changed')
   need(path.name in ['NEW_SOURCE_850_PAIR_MAIN_REVIEW.json','EXTENSION1700_MAIN_REVIEW.json']or path.parent.name=='combination_reviews','known stage review only');self._verify_inherited_stage(path,old);return ref(path)
  return E.Executor.immutable(self,path,value)
 def summary(self,decisions=None):
  r=E.Executor.summary(self,decisions);r.update(max_global_EP_models=self.effective_cap(),authorized_max_global_EP_models=10,same_owner_idle_handoff=True,prior_consumed_never_reforked=self.initial_consumed,maximum_remaining_new_starts=18-len(self.initial_consumed),new_budget_or_refund=False);put(self.C/'RESULTS_CURRENT.json',r);return r
 def publish(self,final=False):
  oldfile=E.__file__;E.__file__=__file__
  try:return E.Executor.publish(self,final)
  finally:E.__file__=oldfile
 def start(self,p):
  c=p['cohort'];g=p['group']
  if time.monotonic()<self.lastresource.get(c,0)+60:return False
  self.lastresource[c]=time.monotonic();cpu=self.available_cpu()
  if cpu is None:return False
  with lock(ADMISSION):
   reg,rows=self.rows();need(c not in rows,'consumed model is never forked again');need(c not in self.technical_holds(),'Main technicalhold')
   count=sum(v.get('state')in ['CONSUMED_BEFORE_FORK','RUNNING']for qid,q in reg['registered_future_requests'].items()if qid.startswith('EP_')and isinstance(q.get('consumed'),dict)for v in q['consumed'].values())
   cap=self.effective_cap()
   if not concurrency_capacity(count,len(self.running),cap):self.states[c]=dict(status='RESOURCE_HOLD_GLOBAL_EP_CAP10',utc=now());return False
   try:nas=nas_capacity_gate(self.specs[c])
   except Exception as e:
    resource='RESOURCE_ADMISSION_HOLD:'in str(e);self.states[c]=dict(status='RESOURCE_ADMISSION_HOLD'if resource else'NAS_QUALIFICATION_HOLD',terminal_hold=not resource,reason=repr(e),utc=now());self.event('FRESH_TRUE164_ADMISSION_HOLD',cohort=c,resource_only=resource);return False
   put(self.C/'NAS_ADMISSION'/(c+'.'+str(uuid.uuid4())+'.json'),dict(**nas,cohort=c,spec_ref=p['spec_ref']))
   self.claim(p,cpu)
   r=self.group_call(g,'from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);resource_gate(s,dispatch_binding(sys.argv[1]))',[c])
   if r.returncode:
    self.release_unconsumed_claim(p);message=(r.stdout+r.stderr)[-6000:];resource='RESOURCE_ADMISSION_HOLD:'in message;self.states[c]=dict(status='RESOURCE_ADMISSION_HOLD'if resource else'PRECONSUME_LOCAL_QUALIFICATION_HOLD',terminal_hold=not resource,reason=message,utc=now());self.event('ADMISSION_HOLD',cohort=c,group=g,resource_only=resource);return False
   path=self.C/'native_logs'/(c+'.'+str(uuid.uuid4())+'.run.log');path.parent.mkdir(exist_ok=True);f=path.open('xb')
   try:process=self.native('run-native',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   except BaseException:f.close();self.release_unconsumed_claim(p);raise
   self.running[c]=dict(process=process,log=f,cpu=cpu,launcher=pid_identity(process.pid),log_path=str(path),started_monotonic=time.monotonic());self.states[c]=dict(status='NATIVE_IN_PROGRESS',cpu=cpu,native_frontend_pid=process.pid,utc=now());self.event('NATIVE_RUN_STARTED',cohort=c,group=g,pid=process.pid);return True
 def run(self):
  self.check_activation()
  with lock(self.C/'SINGLE_MAIN_AUTHORIZED18_EXECUTOR.lock',True),lock(OWNERSHIP,True):
   need(not(self.C/'EXECUTOR_STARTED.json').exists(),'no automatic resume/re-fork');put(self.C/'EXECUTOR_STARTED.json',dict(schema='EP_MAIN_V2_AUTHORIZED18_EXECUTOR_START_V1',utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),no_consumed_retry=True));self.event('SINGLE_MAIN_EXECUTOR_STARTED')
   self.summary()
   try:self.publish()
   except Exception as e:self.event('INITIAL_PUBLICATION_HOLD',reason=repr(e))
   self.close_handoff_done()
   nextgroup='highclock'
   while True:
    try:self.poll()
    except Exception as e:self.event('LOCAL_POLL_HOLD_NO_MODEL_KILL',reason=repr(e))
    try:self.accept_one()
    except Exception as e:
     _,heldrows=self.rows()
     for hc,hr in heldrows.items():
      if hr.get('state')not in TERMINAL and hc not in self.running and hc not in self.pending_accept:self.states[hc]=dict(status='LOCAL_ACCEPTANCE_REVIEW_HOLD',terminal_hold=True,reason=repr(e),utc=now())
     self.event('LOCAL_ACCEPTANCE_HOLD_NO_MODEL_RETRY',reason=repr(e))
    reg,rows=self.rows();decisions,views,refs,errors=self.decisions(reg,rows);self.failures=errors
    for g in REQUESTS:
     try:self.emit_stage_receipts(decisions,views,refs,rows,only_group=g)
     except Exception as e:
      self.failures[g]=repr(e)
      for p in self.points:
       if p['group']==g and p['cohort']not in rows:decisions[p['cohort']]=dict(status='HOLD',group=g,reason='LOCAL_STAGE_RECEIPT_HOLD',detail=repr(e))
    ready={g:[]for g in REQUESTS}
    for p in sorted(self.points,key=self.priorities):
     c=p['cohort'];d=decisions[c]
     if c in rows or c in self.running:continue
     if d['status']in ['HOLD','PRUNE']:self.states[c]=dict(status='PRUNED_NOT_CONSUMED'if d['status']=='PRUNE'else'LOCAL_FAMILY_HOLD_NOT_CONSUMED',terminal_hold=True,reason=d['reason'],utc=now());continue
     if d['status']=='RELEASE'and not self.states.get(c,{}).get('terminal_hold'):ready[p['group']].append(p)
    while len(self.running)<self.effective_cap() and any(ready.values()):
     g=nextgroup if ready[nextgroup]else next(g for g in REQUESTS if ready[g]);p=ready[g].pop(0);nextgroup='system'if g=='highclock'else'highclock'
     try:self.start(p)
     except Exception as e:self.states[p['cohort']]=dict(status='LOCAL_PRELAUNCH_QUALIFICATION_HOLD',terminal_hold=True,reason=repr(e),utc=now());self.event('LOCAL_PRELAUNCH_QUALIFICATION_HOLD',cohort=p['cohort'],reason=repr(e))
    self.summary(decisions)
    if time.monotonic()-self.lastpublish>=1800:
     try:self.publish()
     except Exception as e:self.event('PERIODIC_PUBLICATION_HOLD',reason=repr(e))
    _,rows=self.rows();settled=all(rows.get(p['cohort'],{}).get('state')in TERMINAL or self.states.get(p['cohort'],{}).get('terminal_hold')for p in self.points)
    if settled and not self.running and not self.pending_accept:break
    if time.monotonic()-self.started>self.m.get('admission_wait_and_execution_wall_seconds',7*86400)and not self.running:break
    time.sleep(10)
   self.summary(decisions)
   try:self.archive_summary()
   except Exception as e:self.event('SUMMARY_ARCHIVE_HOLD',reason=repr(e))
   try:self.publish(final=True)
   except Exception as e:self.event('FINAL_PUBLICATION_HOLD',reason=repr(e))
   _,rows=self.rows();remote=read(self.C/'REMOTE_PUBLICATION_RECEIPT.json')if(self.C/'REMOTE_PUBLICATION_RECEIPT.json').exists()else{};put(self.C/'EXECUTOR_FINISHED.json',dict(utc=now(),session=self.session,status='CAP10_SAME_OWNER_TERMINAL_OR_LOCAL_REVIEW_HOLD',consumed=len(rows),accepted=sum(r['state']=='CLOSED_ACCEPTED'for r in rows.values()),unaccepted=sum(r['state']=='CLOSED_UNACCEPTED'for r in rows.values()),unconsumed_cohorts=[p['cohort']for p in self.points if p['cohort']not in rows],all_consumed_terminal=all(r['state']in TERMINAL for r in rows.values()),final_remote_readback_pass=remote.get('final')is True and remote.get('HEAD')==remote.get('remote_HEAD'),no_retry=True,no_refund=True))

def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);g=ap.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');a=ap.parse_args(argv)
 if a.run:Executor10(a.manifest).run()
 else:validate_manifest10(read(a.manifest));print('PASS_PASSIVE_CAP10_SAME_OWNER_NO_START')
if __name__=='__main__':main()
