#!/usr/bin/env python3
"""Finite Main successor candidate; import is passive. Exact Main activation mandatory.
Waits old controller natural finish and PID generation gone; may adopt one Main
prestarted native frontend, never consume/retry it. No old controller writes.
"""
import argparse,importlib.util,hashlib,json,pathlib,sys,os,time,uuid,subprocess,csv,shutil
P=pathlib.Path
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1'); OLD=J/'execution_v2_20261103_v1'; H=J/'execution_stencil_wv_20261103_v1'
PRIOR_CODE=OLD/'tools/finite_main_executor.py'; PRIOR_SHA='5db1fe2dfe2abdb17df10f187725e347600fa35793aa32a09c8b25f3801324ef'
if hashlib.sha256(PRIOR_CODE.read_bytes()).hexdigest()!=PRIOR_SHA:raise RuntimeError('prior immutable executor drift')
sp=importlib.util.spec_from_file_location('prior_finite_main_pure_definitions',PRIOR_CODE);base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
need,read,put,ref,exact,sha,now,lock,authority,pid_identity,same_live=map(lambda n:getattr(base,n),['need','read','put','ref','exact','sha','now','lock','authority','pid_identity','same_live'])
REQUEST='EP_L2_WV_STENCIL_DECOMPOSITION_20261103_V1';M=1<<20;TERMINAL=base.TERMINAL
BASE_REPO=P('/root/data/ep_l2_full_workload_performance_20261027_v1/receipts/lane_o_v1r2_20261029/review')
def validate_manifest(m):
 need(m['schema']=='EP_MAIN_STENCIL_EXACT_EXECUTION_MANIFEST_V1','exact Main manifest schema')
 need(m['status']=='MAIN_AUTHORIZED_EXACT_TWO_STENCIL_NATIVE_STARTS','exact Main status')
 need(P(m['root'])==H and m['max_concurrent_models']==2 and m['new_model_start_ceiling']==2 and m['automatic_retry'] is False,'fixed root/start/concurrency/no-retry')
 ps=m['points'];need(len(ps)==2 and set(p['cohort']for p in ps)=={'EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY','EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO'},'exact authorized Stencil cohorts2')
 ss=[]
 for p in ps:
  need(p['group']=='stencil' and p['science_request_id']==REQUEST,'only Stencil scope')
  need(P(p['spec_ref']['path'])==H/'stencil/cases'/p['cohort']/'control/FROZEN_SPEC.json','exact frozen spec path')
  s=exact(p['spec_ref']);need(s['cohort']==p['cohort'] and s['science_request_id']==REQUEST,'registered spec scope');ss.append(s)
 need(set(s['mode']for s in ss)=={'W_ONLY','WV_ZERO_RO'},'exact W_ONLY/WV modes')
 need(ss[0]['source_identity']==ss[1]['source_identity'] and ss[0]['input_identity_sha256']==ss[1]['input_identity_sha256'],'matched source/input')
 need(ss[0]['input_identity_sha256']=='bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146','exact Stencil accepted input identity')
 need(ss[0]['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04' and ss[0]['source_identity']['binary_sha256']=='78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a','exact unchanged Source78 ELF')
 exact(m['authorization_ref']);need(sha(m['native_entry_ref']['path'])==m['native_entry_ref']['sha256'],'qualified scoped native drift')
 rel=P(m['publication']['relative_directory']);need(not rel.is_absolute() and '..'not in rel.parts and str(rel).endswith('/execution_stencil_wv_20261103_v1'),'bounded publication directory')
 need(P(m['publication']['repo'])==BASE_REPO,'sole Main review repo')
 if m.get('prior_NI_finalizer_ref'):need(sha(m['prior_NI_finalizer_ref']['path'])==m['prior_NI_finalizer_ref']['sha256'],'Main passive prior NI finalizer drift')
 return True

def handoff_status(started,finished,live):
 if finished is None:return 'WAIT_PRIOR_FINISHED'
 if not finished.get('all_eight_terminal'):return 'HOLD_PRIOR_SCOPE_NOT_TERMINAL'
 if live:return 'WAIT_PRIOR_PID_GENERATION_GONE'
 return 'READY'

def adoption_check(m,a,rows):
 consumed=set(rows);need(len(consumed)<=1,'only0or1 Main prestarted point')
 pr=a.get('prestarted_adoption_ref')
 if not consumed:need(pr is None,'unexpected prestarted receipt with no consumed point');return None
 need(pr is not None,'prestarted receipt required');v=exact(pr)
 need(v['schema']=='EP_MAIN_STENCIL_PRESTARTED_NATIVE_ADOPTION_V1' and v['status']=='MAIN_REVIEWED_SINGLE_CONSUMED_NATIVE_FRONTEND_FOR_SUCCESSOR_ADOPTION' and v['approved_by']=='EP-MAIN','Main prestarted review')
 c=next(iter(consumed));need(v['cohort']==c and v['science_request_id']==REQUEST,'adopt exact consumed point')
 p=next(p for p in m['points']if p['cohort']==c);need(v['spec_ref']==p['spec_ref'],'adopt exact spec')
 exact(v['native_run_admission_receipt_ref']);need(v['automatic_retry'] is False and v['never_reconsume'] is True,'adopt no retry/reconsume')
 need(v['model_generation']['pid']>0 and v['model_generation']['start_ticks']>0,'adopted claimed model generation')
 need(v['native_frontend_generation']['start_ticks']>0 and v['native_frontend_generation']['pid']>0,'native frontend generation')
 return v

class Executor(base.Executor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_manifest(self.m);self.E=H;self.C=H/'control';self.states={};self.running={};self.pending_accept=[];self.started=time.monotonic();self.lastpublish=0;self.lastresource={};self.fatal=[];self.phase_written=False;self.points=sorted(self.m['points'],key=lambda p:exact(p['spec_ref'])['mode']);self.bypoint={p['cohort']:p for p in self.points};self.session=str(uuid.uuid4());self.activation=None
 def rows(self):
  r=authority();return r,dict(r['registered_future_requests'][REQUEST]['consumed'])
 def group_call(self,g,source,args=()):
  need(g=='stencil','single scope runtime');code='import sys,json;sys.path.insert(0,'+repr(str(H/'runtime'))+');'+source
  return subprocess.run([sys.executable,'-B','-c',code,*map(str,args)],text=True,capture_output=True,timeout=120)
 def check_activation(self):
  a=read(self.C/'MAIN_EXECUTION_AUTHORIZATION.json');need(a['schema']=='EP_MAIN_STENCIL_SUCCESSOR_ACTIVATION_V1' and a['status']=='MAIN_REVIEWED_REGISTERED_EXACT_TWO_FINITE_EXECUTION_AUTHORIZED' and a['approved_by']=='EP-MAIN','Main activation required')
  need(a['manifest_ref']==ref(self.manifest_path) and a['executor_ref']==ref(__file__) and a['automatic_retry'] is False,'exact activation code/manifest/no retry')
  r=exact(a['registration_receipt_ref']);need(r['foreign_rows_preserved'] is True,'registration foreign preservation');reg,rows=self.rows();q=reg['registered_future_requests'][REQUEST]
  need(q['budget']==2 and q['remaining']==2-len(rows),'fresh exact2 budget accounting')
  for p in self.points:need(q['admitted_specs'][p['cohort']]==p['spec_ref']['sha256'],'registered exact spec')
  self.adoption=adoption_check(self.m,a,rows);self.activation=a
 def wait_handoff(self):
  original=read(OLD/'control/EXECUTOR_STARTED.json');need(original['code_ref']['sha256']==PRIOR_SHA,'prior frozen code identity')
  while True:
   fp=OLD/'control/EXECUTOR_FINISHED.json';finished=read(fp)if fp.exists()else None;state=handoff_status(original,finished,same_live(original['process']))
   put(self.C/'HANDOFF_WAIT_CURRENT.json',dict(utc=now(),status=state,prior_started_ref=ref(OLD/'control/EXECUTOR_STARTED.json'),prior_finished_ref=ref(fp)if fp.exists()else None,passive_only=True,no_Git_postprocess_or_science_dispatch=True))
   if state=='READY':break
   if time.monotonic()-self.started>self.m.get('handoff_wait_wall_seconds',86400):raise RuntimeError('bounded prior handoff wait expired; no process killed')
   time.sleep(10)
  reg=authority()
  for qid in ['EP_L2_WV_DECOMPOSITION_V2','EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1']:
   q=reg['registered_future_requests'][qid];need(q['remaining']==0 and all(r['state']in TERMINAL for r in q['consumed'].values()),'prior scope not terminal')
   root=OLD/('wv'if 'WV_DECOMPOSITION'in qid else't3');claims=read(root/'control/DISPATCH_CLAIMS.json')['claims'];need(not claims,'prior remaining resource claims require Main review')
  # Separate Main-pinned offline comparator repairs prior wrapper NameError;
  # model, source, raw, criteria and original HOLD history remain unchanged.
  if self.m.get('prior_NI_finalizer_ref'):
   rr=self.m['prior_NI_finalizer_ref'];need(sha(rr['path'])==rr['sha256'],'prior NI finalizer drift');r=subprocess.run([sys.executable,'-B',rr['path']],text=True,capture_output=True,timeout=180);need(r.returncode==0,'prior passive NI finalizer review: '+r.stderr[-2000:]);put(self.C/'PRIOR_NI_FINALIZER_RECEIPT.json',dict(utc=now(),code_ref=rr,returncode=r.returncode,stdout=r.stdout[-10000:],scientific_launches=0))
  put(self.C/'SOLE_MAIN_SUCCESSOR_HANDOFF.json',dict(utc=now(),status='PRIOR_FINISHED_PID_GONE_TERMINAL_NO_CLAIMS_SUCCESSOR_OWNS_MAIN_DISPATCH',prior_finished_ref=ref(fp),successor_process=pid_identity(os.getpid()),prestarted_adoption_ref=self.activation.get('prestarted_adoption_ref'),same_global_scientific_owner='EP-MAIN',new_dispatcher_lane=False))
 def adopt(self):
  if self.adoption is None:return
  v=self.adoption;c=v['cohort'];_,rows=self.rows();row=rows[c]
  if row['state']in TERMINAL:self.states[c]={'status':row['state'],'adopted_terminal':True,'utc':now()};return
  claims=read(H/'stencil/control/DISPATCH_CLAIMS.json')['claims'];need(c in claims,'adopted claim missing');cl=claims[c]
  need(cl['spec_sha256']==self.bypoint[c]['spec_ref']['sha256'],'adopted claim spec drift')
  need(cl['model_pid']==v['model_generation']['pid'] and cl['model_start_ticks']==v['model_generation']['start_ticks'],'adopted claimed model generation drift')
  gen=v['native_frontend_generation']
  if same_live(gen):self.running[c]=dict(adopted=True,launcher=gen,cpu=cl['host_cpu'],log_path=v.get('native_log_path'),started_monotonic=time.monotonic());self.states[c]={'status':'ADOPTED_EXISTING_NATIVE_FRONTEND','native_frontend_generation':gen,'utc':now()}
  else:
   need(row.get('done_ref')is not None,'adopted native PID gone without sealed DONE; HOLD no restart');exact(row['done_ref']);self.pending_accept.append(c);self.states[c]={'status':'ADOPTED_DONE_PENDING_ACCEPT','utc':now()}
  self.event('MAIN_PRESTARTED_ADOPTED_NEVER_RECONSUMED',cohort=c,frontend_live=same_live(gen))
 def start(self,p):
  c=p['cohort'];g=p['group']
  if time.monotonic()<self.lastresource.get(c,0)+60:return False
  self.lastresource[c]=time.monotonic();cpu=self.available_cpu()
  if cpu is None:return False
  with lock(OLD/'control/GLOBAL_STAGEII_ADMISSION.lock'):
   reg,rows=self.rows();need(c not in rows,'consumed point never relaunched');others=0
   for qid,q in reg['registered_future_requests'].items():
    if qid==REQUEST or not qid.startswith('EP_'):continue
    cr=q.get('consumed',{});cr=cr.values()if isinstance(cr,dict)else[];others+=sum(r.get('state')in['CONSUMED_BEFORE_FORK','RUNNING']for r in cr)
   if others+len(self.running)>=2:self.states[c]={'status':'ADMISSION_HOLD_GLOBAL_EP_CAP2','utc':now()};return False
   self.claim(p,cpu);r=self.group_call(g,'from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);resource_gate(s,dispatch_binding(sys.argv[1]))',[c])
   if r.returncode:
    self.release_unconsumed_claim(p);msg=(r.stderr+r.stdout)[-8000:];resource='RESOURCE_ADMISSION_HOLD:'in msg;self.states[c]={'status':'RESOURCE_ADMISSION_HOLD'if resource else'PRELAUNCH_QUALIFICATION_HOLD','reason':msg,'terminal_hold':not resource,'utc':now()};self.event('ADMISSION_HOLD',cohort=c,resource_only=resource,reason=msg);return False
   path=self.C/'native_logs'/(c+'.'+str(uuid.uuid4())+'.run.log');path.parent.mkdir(exist_ok=True);f=path.open('xb');proc=self.native('run-native',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   self.running[c]={'process':proc,'log':f,'cpu':cpu,'launcher':pid_identity(proc.pid),'log_path':str(path),'started_monotonic':time.monotonic()};self.states[c]={'status':'NATIVE_IN_PROGRESS','native_frontend_pid':proc.pid,'cpu':cpu,'utc':now()};self.event('NATIVE_RUN_STARTED',cohort=c,pid=proc.pid,cpu=cpu);return True
 def poll(self):
  for c,v in list(self.running.items()):
   if not v.get('adopted'):
    rc=v['process'].poll()
    if rc is None:continue
    v['log'].close()
   else:
    if same_live(v['launcher']):continue
    rc='ADOPTED_EXTERNAL_PARENT_DONE'
   _,rows=self.rows();p=self.bypoint[c]
   if c in rows:
    need(rows[c].get('done_ref')is not None,'native wrapper gone without sealed DONE; no retry');exact(rows[c]['done_ref']);self.running.pop(c);self.pending_accept.append(c);self.states[c]={'status':'NATIVE_TERMINAL_PENDING_ACCEPT','returncode':rc,'utc':now()}
   else:
    self.running.pop(c);self.release_unconsumed_claim(p);text=P(v['log_path']).read_text(errors='replace')[-8000:];resource='RESOURCE_ADMISSION_HOLD:'in text;self.states[c]={'status':'PRECONSUME_RESOURCE_HOLD'if resource else'PRECONSUME_TECHNICAL_HOLD','terminal_hold':not resource,'reason':text,'utc':now()}
   self.event('NATIVE_FRONTEND_EXIT',cohort=c,returncode=rc,consumed=c in rows)
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0)
  with lock(OLD/'control/GLOBAL_ACCEPT_AND_RESTORE_WINDOW.lock'):
   path=self.C/'native_logs'/(c+'.accept.log')
   with path.open('xb')as f:p=self.native('accept',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL);rc=p.wait()
   _,rows=self.rows();row=rows[c];self.states[c]={'status':row['state'],'accept_returncode':rc,'utc':now()}
   if row['state']not in TERMINAL:self.states[c].update(terminal_hold=True,reason='Main acceptance/archive review, no automatic retry')
   self.event('ACCEPT_AND_ARCHIVE_EXIT',cohort=c,returncode=rc,state=row['state'])
 def summary(self):
  reg,rows=self.rows();out=[];contrasts=[]
  for p in self.points:
   c=p['cohort'];s=exact(p['spec_ref']);r=rows.get(c,{});v=dict(cohort=c,group='stencil',mode=s['mode'],source_identity=s['source_identity'],spec_ref=p['spec_ref'],state=r.get('state',self.states.get(c,{}).get('status','NOT_STARTED')),consumed=c in rows,controller_state=self.states.get(c),input_identity_sha256=s['input_identity_sha256'])
   for k in ['accepted_point_ref','archive_receipt_ref','done_ref','validation_ref']:v[k]=r.get(k)
   if r.get('accepted_point_ref'):
    pt=exact(r['accepted_point_ref']);v.update({k:pt[k]for k in['cycles','instructions','CTA','kernel_count','hardware_drained']})
    try:v['mechanism_metrics_ref']=self.metrics(p,pt,r)
    except Exception as exc:v['mechanism_metrics_analysis']={'status':'UNKNOWN','reason':repr(exc),'scientific_run_affected':False}
   if r.get('done_ref'):
    d=exact(r['done_ref']);v.update({k:d.get(k)for k in['elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason']})
   out.append(v)
  accepted={v['mode']:v for v in out if v['state']=='CLOSED_ACCEPTED'}
  if set(accepted)=={'W_ONLY','WV_ZERO_RO'}:
   w,v=accepted['W_ONLY'],accepted['WV_ZERO_RO'];contrasts.append(dict(contrast='W_ONLY_to_WV',baseline=w['cohort'],treatment=v['cohort'],speedup=w['cycles']/v['cycles'],cycle_reduction_fraction=1-v['cycles']/w['cycles'],same_Source78=True))
  for p in self.points:
   v=next(v for v in out if v['cohort']==p['cohort'])
   if v['state']!='CLOSED_ACCEPTED':continue
   s=exact(p['spec_ref']);refs=dict(p.get('matched_reference_points',{}))
   # Only explicit Main-qualified Source78 exact-input references. F context
   # remains labeled complete mechanism context, never independent T benefit.
   if 'matched_S_anchor_qualification_ref'in s:
    q=exact(s['matched_S_anchor_qualification_ref']);need(q['approved_by']=='EP-MAIN'and q['currently_accepted_population']is True,'Main exactS review');refs.setdefault('S',q['point_ref'])
   for name,rr in refs.items():
    old=exact(rr);need(old['source_identity']==v['source_identity']and old['input_identity_sha256']==v['input_identity_sha256'],'matched reference lineage');contrasts.append(dict(contrast=name+'_to_'+v['mode'],baseline=old['cohort'],treatment=v['cohort'],speedup=old['cycles']/v['cycles'],cycle_reduction_fraction=1-v['cycles']/old['cycles'],Main_exact_reference_ref=rr,attribution='complete_F_context_not_T_independent'if name=='F'else'matched_mode_comparison'))
  result=dict(schema='EP_MAIN_STENCIL_FINITE_RESULTS_V1',utc=now(),session=self.session,points=out,contrasts=contrasts,budget={k:reg['registered_future_requests'][REQUEST].get(k)for k in['budget','remaining','state']},active_native_frontends=len(self.running),maximum_concurrency=2,automatic_retry=False,Source_keep=True,combined_GM=False,fatal=self.fatal,numeric_application_output='UNKNOWN')
  put(self.C/'RESULTS_CURRENT.json',result)
  with(self.C/'RESULTS_CURRENT.csv').open('w',newline='')as f:
   cols=['cohort','group','mode','state','consumed','cycles','instructions','CTA','kernel_count','hardware_drained','elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason'];w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(out)
  return result
 def publish(self,final=False):
  p=self.m['publication'];repo=P(p['repo']);rel=p['relative_directory'];dst=repo/rel;dst.mkdir(parents=True,exist_ok=True)
  with lock(OLD/'control/MAIN_GIT_PUBLICATION.lock'):
   need(subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip()==p['branch'],'Main branch drift');need(not subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).strip(),'foreign staged work')
   for name in['RESULTS_CURRENT.json','RESULTS_CURRENT.csv']:shutil.copy2(self.C/name,dst/name)
   put(dst/'EXECUTION_SCOPE.json',dict(manifest_ref=ref(self.manifest_path),authorization_ref=self.m['authorization_ref'],maxstarts=2,automatic_retry=False,final=final,utc=now(),prior_handoff_ref=ref(self.C/'SOLE_MAIN_SUCCESSOR_HANDOFF.json')))
   (dst/'MECHANISM_METRICS').mkdir(exist_ok=True)
   for src in(self.C/'MECHANISM_METRICS').glob('*.json'):need(src.stat().st_size<=16*M,'bounded summary size');shutil.copy2(src,dst/'MECHANISM_METRICS'/src.name)
   (dst/'README.md').write_text('# Stencil W/V decomposition\n\nExact Source78 W-only/WV two fresh starts. No retries or additional workloads. Full raw, exact SHA and two independent restores on genuine164. S is exact Main-qualified reference; F is complete mechanism context only. Negative and zero results retained.\n')
   subprocess.run(['git','-C',str(repo),'add','--sparse','--',rel],check=True)
   # Existing repository ignore patterns may cover CSV; force only bounded file.
   subprocess.run(['git','-C',str(repo),'add','--sparse','-f','--',str(P(rel)/'RESULTS_CURRENT.csv')],check=True)
   changed=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();need(all(x.startswith(rel+'/')for x in changed),'publication paths escape scope')
   if changed:subprocess.run(['git','-C',str(repo),'commit','-m','EP Main Stencil W/V '+('final results'if final else'accepted execution progress')],check=True)
   subprocess.run(['git','-C',str(repo),'push','origin',p['branch']],check=True);head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','origin','refs/heads/'+p['branch']],text=True).split()[0];need(head==remote,'remote HEAD mismatch');put(self.C/'REMOTE_PUBLICATION_RECEIPT.json',dict(utc=now(),HEAD=head,remote_HEAD=remote,final=final,exact_directory=rel));self.lastpublish=time.monotonic();self.event('REMOTE_PUBLISHED',HEAD=head,final=final)
 def run(self):
  self.check_activation();self.C.mkdir(parents=True,exist_ok=True)
  with lock(self.C/'FINITE_MAIN_EXECUTOR.lock',True):
   need(not(self.C/'EXECUTOR_STARTED.json').exists(),'already started, no automatic resume');put(self.C/'EXECUTOR_WAITING_STARTED.json',dict(utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),passive_until_handoff=True));self.wait_handoff()
   with lock(OLD/'control/GLOBAL_MAIN_SUCCESSOR_OWNERSHIP.lock',True):
    need(not(self.C/'EXECUTOR_STARTED.json').exists(),'successor already started');put(self.C/'EXECUTOR_STARTED.json',dict(utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),automatic_resume=False));self.adopt();self.event('SUCCESSOR_MAIN_CONTROLLER_STARTED')
    while True:
     try:self.poll();self.accept_one();_,rows=self.rows()
     except Exception as exc:self.event('OPERATIONAL_REVIEW_HOLD_WITHOUT_MODEL_KILL',reason=repr(exc));time.sleep(10);continue
     for p in self.points:
      if len(self.running)>=2:break
      c=p['cohort']
      if c in rows or c in self.running or self.states.get(c,{}).get('terminal_hold'):continue
      try:self.start(p)
      except Exception as exc:self.states[c]={'status':'PRELAUNCH_ENGINEERING_REVIEW_HOLD','terminal_hold':True,'reason':repr(exc),'utc':now()};self.event('PRELAUNCH_ENGINEERING_REVIEW_HOLD',cohort=c,reason=repr(exc))
     self.summary()
     if time.monotonic()-self.lastpublish>=1800:
      try:self.publish()
      except Exception as exc:self.event('PUBLICATION_HOLD',reason=repr(exc))
     settled=all(rows.get(p['cohort'],{}).get('state')in TERMINAL or self.states.get(p['cohort'],{}).get('terminal_hold')for p in self.points)
     if settled and not self.running and not self.pending_accept:break
     if time.monotonic()-self.started>self.m.get('admission_wait_and_execution_wall_seconds',7*86400):
      self.event('FINITE_WALL_HOLD');need(not self.running,'wall reached with live model; never auto kill');break
     time.sleep(10)
    self.summary()
    try:self.archive_summary()
    except Exception as exc:self.event('SUMMARY_ARCHIVE_HOLD',reason=repr(exc))
    try:self.publish(final=True)
    except Exception as exc:self.event('FINAL_PUBLICATION_HOLD',reason=repr(exc))
    _,rows=self.rows();remote=read(self.C/'REMOTE_PUBLICATION_RECEIPT.json')if(self.C/'REMOTE_PUBLICATION_RECEIPT.json').exists()else{};pub=remote.get('final')is True and remote.get('HEAD')==remote.get('remote_HEAD');accepted=all(rows.get(p['cohort'],{}).get('state')=='CLOSED_ACCEPTED'for p in self.points)
    put(self.C/'EXECUTOR_FINISHED.json',dict(utc=now(),session=self.session,status='TWO_STENCIL_ACCEPTED_AND_REMOTE_FINAL_PASS'if accepted and pub else'FINITE_SCOPE_TERMINAL_OR_REVIEW_HOLD',both_accepted=accepted,all_terminal=all(rows.get(p['cohort'],{}).get('state')in TERMINAL for p in self.points),final_remote_HEAD_verified=pub,automatic_retry=False,science_starts_reconciled_by_authority=True))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--manifest',required=True);x=a.parse_args()
 try:Executor(x.manifest).run()
 except BaseException as exc:print(json.dumps(dict(status='MAIN_SUCCESSOR_REVIEW_HOLD',reason=repr(exc),automatic_retry=False)),file=sys.stderr);raise
