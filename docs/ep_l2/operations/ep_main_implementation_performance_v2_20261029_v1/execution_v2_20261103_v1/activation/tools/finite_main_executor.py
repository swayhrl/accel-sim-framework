#!/usr/bin/env python3
"""Finite Main executor candidate. No operation occurs on import. Main activation required."""
import argparse,contextlib,csv,datetime,fcntl,hashlib,json,os,pathlib,subprocess,sys,time,uuid
P=pathlib.Path
REG=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH=REG.parents[1]/'CURRENT_SCIENCE_EPOCH.json'
REQUESTS={'wv':'EP_L2_WV_DECOMPOSITION_V2','t3':'EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1'}
ARMS=['A_F_MINUS_T','B_LEGACY_F','C_CORRECTED_F']
T_OFF=['EP_PERF_T3_CONV16X8_'+a+'_OFF_V1' for a in ARMS]
T_ON=[c.replace('_OFF_','_ON_') for c in T_OFF]
TERMINAL={'CLOSED_ACCEPTED','CLOSED_UNACCEPTED'}
M=1024**2

def need(x,msg):
 if not x: raise RuntimeError(msg)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def ref(p):return {'path':str(p),'sha256':sha(p)}
def exact(r):
 need(sha(r['path'])==r['sha256'],'Immutable reference drift: '+r['path']);return read(r['path'])
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name('.'+p.name+'.'+str(uuid.uuid4()))
 with q.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(q,p);return ref(p)
@contextlib.contextmanager
def lock(p,nonblock=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a+b') as f:
  fcntl.flock(f,fcntl.LOCK_EX|(fcntl.LOCK_NB if nonblock else 0));yield

def authority():
 for _ in range(5):
  s=sha(REG);r=read(REG);e=read(EPOCH)
  if s==sha(REG)==e['native_registry_sha256']:return r
  time.sleep(.1)
 raise RuntimeError('Authority snapshot changed; no launch')
def pid_identity(pid):
 parts=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'start_ticks':int(parts[19]),'state':parts[0]}
def same_live(p):
 try:r=pid_identity(p['pid']);return r['start_ticks']==p['start_ticks'] and r['state'] not in ['Z','X']
 except (OSError,ValueError):return False

def validate_manifest(m):
 need(m['schema']=='EP_MAIN_STAGEII_EXACT_EXECUTION_MANIFEST_V1','Main exact manifest schema')
 need(m['status'] in ['MAIN_AUTHORIZED_EXACT_EIGHT_FINITE_NATIVE_STARTS','USER_AUTHORIZED_READY_FOR_FRESH_REGISTRATION_NOT_STARTED'],'Main activation status')
 need(m['max_concurrent_models']==2,'exact concurrency cap2')
 need(m['new_model_start_ceiling']==8,'exact2+6 ceiling')
 need(m['automatic_retry'] is False,'no consumed science retry')
 points=m['points'];need(len(points)==8,'exact8 points')
 names=[p['cohort'] for p in points];need(len(set(names))==8,'duplicate cohort')
 wp=[p for p in points if p['group']=='wv'];tp=[p for p in points if p['group']=='t3']
 need(len(wp)==2 and len(tp)==6 and set(p['cohort'] for p in tp)==set(T_OFF+T_ON),'exactW2/T6')
 ws=[exact(p['spec_ref']) for p in wp]
 need(all(s['mode']=='W_ONLY' for s in ws),'only W_ONLY initial2')
 need(set(p['cohort'] for p in wp)=={'EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','EP_PERF_V2_PROPOSED_FASTWALSHTRANSFORM_FC3A9062_W_ONLY'},'onlyGEMM/FWT')
 for p in points:
  need(p['group'] in REQUESTS and p['science_request_id']==REQUESTS[p['group']],'group request scope')
  s=exact(p['spec_ref']);need(s['cohort']==p['cohort'],'cohort/spec mismatch')
  need(P(p['spec_ref']['path'])==P(m['root'])/p['group']/'cases'/p['cohort']/'control/FROZEN_SPEC.json','frozen exact group spec path')
 need(sha(m['native_entry_ref']['path'])==m['native_entry_ref']['sha256'],'qualified scoped native changed')
 exact(m['authorization_ref']);exact(m['NI_criteria_ref'])
 repo=P(m['publication']['repo']);rel=P(m['publication']['relative_directory'])
 need(not rel.is_absolute() and '..' not in rel.parts and str(rel).endswith('/execution_v2_20261103_v1'),'publication exactowned relative path')
 need(str(repo)=='/root/data/ep_l2_full_workload_performance_20261027_v1/receipts/lane_o_v1r2_20261029/review','onlyMainreviewrepo')
 return True

def runnable(points,rows,states):
 primary_done=all(rows.get(c,{}).get('state')=='CLOSED_ACCEPTED' and rows[c].get('archive_receipt_ref') for c in T_OFF)
 primary_bad=any(rows.get(c,{}).get('state')=='CLOSED_UNACCEPTED' or states.get(c,{}).get('terminal_hold') for c in T_OFF)
 out=[]
 for p in points:
  c=p['cohort']
  if c in rows or states.get(c,{}).get('terminal_hold'):continue
  if c in T_ON and not primary_done:continue
  out.append(p)
 return out,primary_done,primary_bad

class Executor:
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_manifest(self.m)
  self.E=P(self.m['root']);self.C=self.E/'control';self.states={};self.running={};self.pending_accept=[]
  self.started=time.monotonic();self.lastpublish=0;self.lastresource={};self.fatal=[];self.phase_written=False
  self.points=sorted(self.m['points'],key=lambda p:(0 if p['cohort'] in T_OFF else (1 if p['group']=='wv' else 2),0 if 'GEMM' in p['cohort'] else 1,p['cohort']));self.bypoint={p['cohort']:p for p in self.points}
  self.session=str(uuid.uuid4())
 def rows(self):
  reg=authority();out={}
  for g,q in REQUESTS.items():out.update(reg['registered_future_requests'][q]['consumed'])
  return reg,out
 def event(self,kind,**v):
  with (self.C/'EXECUTOR_EVENTS.jsonl').open('a') as f:f.write(json.dumps(dict(utc=now(),event=kind,session=self.session,**v),sort_keys=True)+'\n');f.flush()
 def native(self,op,c,**kw):
  n=self.m['native_entry_ref'];need(sha(n['path'])==n['sha256'],'scoped native entry drift')
  shared=self.m['shared_native_ref'];need(sha(shared['path'])==shared['sha256'],'shared foreign native bytes drift; no rewrite permitted')
  return subprocess.Popen([n['path'],'experiment',op,c,'--project','EP_L2'],**kw)
 def group_call(self,g,source,args=()):
  # Separate interpreter prevents two groups sharing same-named module globals.
  mod=str(self.E/('runtime_w' if g=='wv' else 'runtime_t'))
  code='import sys;sys.path.insert(0,'+repr(mod)+');'+source
  return subprocess.run([sys.executable,'-B','-c',code,*map(str,args)],text=True,capture_output=True,timeout=120)
 def claim(self,p,cpu):
  c=p['cohort'];g=p['group'];s=exact(p['spec_ref']);root=self.E/g
  row=dict(state='CLAIMED',cohort=c,spec_sha256=p['spec_ref']['sha256'],host_cpu=cpu,
   estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],remaining_write_bytes=s['limits']['result_bytes']+2*M,
   utc=now(),controller_pid=os.getpid(),controller_start_ticks=pid_identity(os.getpid())['start_ticks'])
  with lock(root/'control/ADMISSION.lock'):
   claims=read(root/'control/DISPATCH_CLAIMS.json');need(c not in claims['claims'],'preexisting claim requires Main review')
   claims['claims'][c]=row;put(root/'control/DISPATCH_CLAIMS.json',claims)
   put(root/'control/dispatch_bindings'/(c+'.json'),dict(cohort=c,spec_sha256=p['spec_ref']['sha256'],host_cpu=cpu,controller_session=self.session))
   r=self.group_call(g,'from ep_perf_common_v2 import *;publish_own_write_carrier(read(ROOT/"control/DISPATCH_CLAIMS.json")["claims"])')
   need(r.returncode==0,'claim carrier publication failed '+r.stderr[-1000:])
 def release_unconsumed_claim(self,p):
  _,rows=self.rows();need(p['cohort'] not in rows,'consumed claim cannot be released as unspent')
  root=self.E/p['group']
  with lock(root/'control/ADMISSION.lock'):
   q=read(root/'control/DISPATCH_CLAIMS.json');q['claims'].pop(p['cohort'],None);put(root/'control/DISPATCH_CLAIMS.json',q)
   r=self.group_call(p['group'],'from ep_perf_common_v2 import *;publish_own_write_carrier(read(ROOT/"control/DISPATCH_CLAIMS.json")["claims"])')
   need(r.returncode==0,'unspent claim publication failed '+r.stderr[-1000:])
 def available_cpu(self):
  used={r['cpu'] for r in self.running.values()}
  for d in P('/proc').iterdir():
   if not d.name.isdigit():continue
   try:
    cmd=(d/'cmdline').read_bytes()
    if b'accel-sim.out' not in cmd:continue
    affinity=os.sched_getaffinity(int(d.name))
    if len(affinity)<=8:used.update(affinity)
   except (OSError,ValueError):pass
  allowed=set(os.sched_getaffinity(0));candidates=self.m.get('host_cpu_candidates',sorted(allowed))
  return next((c for c in candidates if c in allowed and c not in used),None)
 def start(self,p):
  c=p['cohort'];g=p['group']
  if time.monotonic()<self.lastresource.get(c,0)+60:return False
  self.lastresource[c]=time.monotonic();cpu=self.available_cpu()
  if cpu is None:return False
  with lock(self.C/'GLOBAL_STAGEII_ADMISSION.lock'):
   reg,rows=self.rows();need(c not in rows,'consumed point never relaunched')
   need(len(self.running)<2,'max2 own models')
   others=0
   for qid,q in reg['registered_future_requests'].items():
    if qid in REQUESTS.values() or not qid.startswith('EP_'):continue
    cr=q.get('consumed',{});cr=cr.values() if isinstance(cr,dict) else []
    others+=sum(r.get('state') in ['CONSUMED_BEFORE_FORK','RUNNING'] for r in cr)
   if others+len(self.running)>=2:
    self.states[c]={'status':'ADMISSION_HOLD_FOREIGN_EP_CONCURRENCY','utc':now()};return False
   self.claim(p,cpu)
   # Real module gates fresh RAM/native-space/peer commitments; current group's own pending estimate is counted once.
   r=self.group_call(g,'from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);resource_gate(s,dispatch_binding(sys.argv[1]))',[c])
   if r.returncode:
    self.release_unconsumed_claim(p)
    msg=(r.stderr+r.stdout)[-8000:];resource='RESOURCE_ADMISSION_HOLD:' in msg
    self.states[c]={'status':'RESOURCE_ADMISSION_HOLD' if resource else 'PRELAUNCH_QUALIFICATION_HOLD','reason':msg,'utc':now(),'terminal_hold':not resource}
    self.event('ADMISSION_HOLD',cohort=c,resource_only=resource,reason=msg);return False
   log=self.C/'native_logs'/(c+'.'+str(uuid.uuid4())+'.run.log');log.parent.mkdir(exist_ok=True)
   f=log.open('xb');proc=self.native('run-native',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   self.running[c]={'process':proc,'log':f,'cpu':cpu,'launcher':pid_identity(proc.pid),'log_path':str(log),'started_monotonic':time.monotonic()}
   self.states[c]={'status':'NATIVE_IN_PROGRESS','cpu':cpu,'native_frontend_pid':proc.pid,'utc':now()}
   self.event('NATIVE_RUN_STARTED',cohort=c,pid=proc.pid,cpu=cpu,science_consumption='consult authority intent, never inferred from process start')
   return True
 def poll(self):
  for c,v in list(self.running.items()):
   rc=v['process'].poll()
   if rc is None:continue
   _,rows=self.rows()
   v['log'].close();self.running.pop(c);p=self.bypoint[c]
   if c in rows:
    self.pending_accept.append(c);self.states[c]={'status':'NATIVE_TERMINAL_PENDING_ACCEPT','returncode':rc,'utc':now()}
   else:
    self.release_unconsumed_claim(p)
    text=P(v['log_path']).read_text(errors='replace')[-8000:]
    resource='RESOURCE_ADMISSION_HOLD:' in text
    self.states[c]={'status':'PRECONSUME_RESOURCE_HOLD' if resource else 'PRECONSUME_TECHNICAL_HOLD','terminal_hold':not resource,'reason':text,'utc':now()}
   self.event('NATIVE_FRONTEND_EXIT',cohort=c,returncode=rc,consumed=c in rows)
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0)
  # One Main global window serializes both group archive/restore pipelines.
  with lock(self.C/'GLOBAL_ACCEPT_AND_RESTORE_WINDOW.lock'):
   log=self.C/'native_logs'/(c+'.accept.log')
   with log.open('xb') as f:
    p=self.native('accept',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL);rc=p.wait()
   _,rows=self.rows();row=rows[c]
   self.states[c]={'status':row['state'],'accept_returncode':rc,'utc':now()}
   if row['state'] not in TERMINAL:
    self.states[c].update(terminal_hold=True,reason='Acceptance/archive requires Main review; no automatic retry')
   self.event('ACCEPT_AND_ARCHIVE_EXIT',cohort=c,returncode=rc,state=row['state'])
 def phase(self,rows):
  if self.phase_written:return
  if not all(rows.get(c,{}).get('state')=='CLOSED_ACCEPTED' for c in T_OFF):return
  criteria=exact(self.m['NI_criteria_ref']);need(criteria['same_arm_only'] is True,'Main samearm NI contract')
  source=exact(self.bypoint[T_OFF[0]]['spec_ref'])['source_identity'];points={}
  for c in T_OFF:
   row=rows[c];pt=exact(row['accepted_point_ref']);ar=exact(row['archive_receipt_ref'])
   need(pt['source_identity']==source,'primary source consistency')
   need(ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and len(ar['native_restores'])==2,'primary archive and two restores')
   points[c]=row['accepted_point_ref']
  review=dict(schema='EP_MAIN_T3_DIAGNOSTIC_PHASE_REVIEW_V1',status='MAIN_REVIEWED_PRIMARY_ACCEPTED_AND_NI_CRITERIA_APPROVED',approved_by='EP-MAIN',
   science_request_id=REQUESTS['t3'],source_identity=source,application_NI_already_proven=False,primary_accepted_points=points,NI_criteria_ref=self.m['NI_criteria_ref'],
   authorization_ref=self.m['authorization_ref'],controller_manifest_ref=ref(self.manifest_path),utc=now(),no_positive_performance_or_detach_requirement=True)
  pr=put(self.C/'T3_DIAGNOSTIC_PHASE_MAIN_REVIEW.json',review)
  put(self.E/'t3/control/T3_DIAGNOSTIC_PHASE_MAIN_REVIEW_REF.json',pr);self.phase_written=True;self.event('CONDITIONAL_ON_PHASE_CRITERIA_REVIEW',ref=pr)
 def ni(self,rows):
  for off,on in zip(T_OFF,T_ON):
   path=self.C/'NI_RESULTS'/(off+'.json')
   if path.exists() or not all(rows.get(c,{}).get('state')=='CLOSED_ACCEPTED' for c in [off,on]):continue
   try:
    r=self.group_call('t3','import t3_application_ni;print(json.dumps(t3_application_ni.compare(sys.argv[1],sys.argv[2])))',[off,on])
    v=json.loads(r.stdout) if r.returncode==0 else {'status':'NI_ANALYSIS_HOLD','reason':(r.stderr+r.stdout)[-8000:]}
   except Exception as exc:v={'status':'NI_ANALYSIS_HOLD','reason':repr(exc)}
   put(path,v);self.event('SAME_ARM_NI_ANALYSIS',off=off,on=on,status=v['status'])
 def metrics(self,p,point,row):
  path=self.C/'MECHANISM_METRICS'/(p['cohort']+'.json')
  if path.exists():return ref(path)
  bundle=exact(point['validation_ref']);model=bundle.get('model',{});metrics=model.get('mechanism_metrics','UNKNOWN')
  v=dict(schema='EP_MAIN_ACCEPTED_MECHANISM_METRICS_V1',cohort=p['cohort'],validation_ref=point['validation_ref'],mechanism_metrics=metrics,
   T3_counter_audit=bundle.get('T3_counter_audit','NOT_APPLICABLE'),strict_demand_unique_NEW='NOT_INSTRUMENTED',later_UID_completion_chain='NOT_MEASURED',
   counter_population_note='B0 counters retain their own populations; blocked observations over slices are not exclusive critical-path GPU cycles')
  if p['group']=='t3':
   import gzip
   done=exact(row['done_ref']);raw=done.get('raw_compressed_ref');p1={};diag=None;tp=None
   if raw:
    need(sha(raw['path'])==raw['sha256'],'accepted raw ref drift for bounded summary')
    with gzip.open(raw['path'],'rt') as f:
     for line in f:
      if line.startswith('gpu_tot_sim_cycle = '):p1={}
      elif line.startswith('EPL2P1V2|SET_ELIGIBILITY_QUERY|'):
       r=dict(x.split('=',1)for x in line.strip().split('|')[2:]);p1[r['slice']]=r
      elif line.startswith('EPL2TAGPRESSUREV1|'):
       r=json.loads(line.split('|',1)[1])
       if r.get('record')=='GLOBAL':tp=r
      elif line.startswith('EPL2DETACH_DIAG_V1|'):
       r=json.loads(line.split('|',1)[1])
       if r.get('record')=='GLOBAL':diag=r
   v.update(P1_final_records_by_slice=p1 or 'UNKNOWN',TP_final_GLOBAL=tp or 'OFF_NOT_MEASURED',DETACH_DIAG_final_GLOBAL=diag or 'OFF_NOT_MEASURED',raw_analysis='one bounded streaming pass after acceptance; no Trace scanned')
  return put(path,v)
 def summary(self):
  reg,rows=self.rows();out=[]
  for p in self.points:
   c=p['cohort'];s=exact(p['spec_ref']);r=rows.get(c,{});v=dict(cohort=c,group=p['group'],mode=s['mode'],observer_profile=s.get('observer_profile'),
    source_identity=s['source_identity'],spec_ref=p['spec_ref'],state=r.get('state',self.states.get(c,{}).get('status','NOT_STARTED')),consumed=c in rows,
    controller_state=self.states.get(c),input_identity_sha256=s['input_identity_sha256'])
   for k in ['accepted_point_ref','archive_receipt_ref','done_ref','validation_ref']:v[k]=r.get(k)
   if r.get('accepted_point_ref'):
    pt=exact(r['accepted_point_ref']);v.update({k:pt[k] for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']})
    try:v['mechanism_metrics_ref']=self.metrics(p,pt,r)
    except Exception as exc:v['mechanism_metrics_analysis']={'status':'UNKNOWN','reason':repr(exc),'scientific_run_affected':False}
   if r.get('done_ref'):
    done=exact(r['done_ref']);v.update({k:done.get(k) for k in ['elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason']})
   out.append(v)
  contrasts=[];idx={x['cohort']:x for x in out}
  for a,b,label in [(T_OFF[0],T_OFF[1],'Legacy_T_independent'),(T_OFF[1],T_OFF[2],'P1_correction'),(T_OFF[0],T_OFF[2],'Corrected_T_total')]:
   aa,bb=idx[a],idx[b]
   if all(x.get('state')=='CLOSED_ACCEPTED' for x in [aa,bb]):
    need(aa['source_identity']==bb['source_identity'] and aa['input_identity_sha256']==bb['input_identity_sha256'],'T causal identity')
    contrasts.append(dict(contrast=label,baseline=a,treatment=b,speedup=aa['cycles']/bb['cycles'],cycle_reduction_fraction=1-bb['cycles']/aa['cycles'],same_new_Source=True))
  # W reference paths are Main-verified accepted_point refs explicitly bound in finalmanifest, never historical perf pasted.
  for p in self.points:
   if p['group']!='wv' or idx[p['cohort']]['state']!='CLOSED_ACCEPTED':continue
   try:
    w=idx[p['cohort']]
    references=dict(p.get('matched_reference_points',{}))
    spec=exact(p['spec_ref'])
    for key,name in [('matched_S_anchor_qualification_ref','S'),('reused_WV_Main_qualification_ref','WV')]:
     if key in spec and name not in references:
      review=exact(spec[key]);need(review['approved_by']=='EP-MAIN' and review['currently_accepted_population'] is True,'Main reference reuse review');references[name]=review['point_ref']
    for name,proof in references.items():
     old=exact(proof);need(old['source_identity']==w['source_identity'] and old['input_identity_sha256']==w['input_identity_sha256'],'W matched reference lineage')
     contrasts.append(dict(contrast=name+'_to_W_ONLY',baseline=old['cohort'],treatment=p['cohort'],speedup=old['cycles']/w['cycles'],cycle_reduction_fraction=1-w['cycles']/old['cycles'],Main_exact_reference_ref=proof))
   except Exception as exc:
    contrasts.append(dict(contrast='W_REFERENCE_ANALYSIS',treatment=p['cohort'],status='UNKNOWN',reason=repr(exc),scientific_run_affected=False))
  result=dict(schema='EP_MAIN_STAGEII_FINITE_RESULTS_V1',utc=now(),session=self.session,points=out,contrasts=contrasts,
   budgets={g:{k:reg['registered_future_requests'][q].get(k) for k in ['budget','remaining','state']} for g,q in REQUESTS.items()},
   active_native_frontends=len(self.running),maximum_concurrency=2,automatic_retry=False,Source_keep=True,combined_GM=False,fatal=self.fatal,
   strict_demand_NEW='NOT_INSTRUMENTED',later_UID_completion_chain='NOT_MEASURED',numeric_application_output='UNKNOWN',
   host_overhead='descriptive OFF/ON single-pair timing, separate from simulated GPU cycles')
  put(self.C/'RESULTS_CURRENT.json',result)
  with (self.C/'RESULTS_CURRENT.csv').open('w',newline='') as f:
   cols=['cohort','group','mode','observer_profile','state','consumed','cycles','instructions','CTA','kernel_count','hardware_drained','elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason'];w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(out)
  return result
 def publish(self,final=False):
  publication=self.m['publication'];repo=P(publication['repo']);rel=publication['relative_directory'];dst=repo/rel;dst.mkdir(parents=True,exist_ok=True)
  with lock(self.C/'MAIN_GIT_PUBLICATION.lock'):
   branch=subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip();need(branch==publication['branch'],'Main publication branch drift')
   need(not subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).strip(),'foreign staged Git work; Main review required')
   import shutil
   for name in ['RESULTS_CURRENT.json','RESULTS_CURRENT.csv']:
    shutil.copy2(self.C/name,dst/name)
   put(dst/'EXECUTION_SCOPE.json',dict(manifest_ref=ref(self.manifest_path),native_entry_ref=self.m['native_entry_ref'],authorization_ref=self.m['authorization_ref'],maxstarts=8,automatic_retry=False,utc=now(),final=final))
   for sub in ['NI_RESULTS','MECHANISM_METRICS']:
    nd=dst/sub;nd.mkdir(exist_ok=True)
    for src in (self.C/sub).glob('*.json'):
     need(src.stat().st_size<=16*M,'derived publication unexpectedly large');shutil.copy2(src,nd/src.name)
   (dst/'README.md').write_text('# EP Main Stage II finite execution\n\nW Source78 W-only2; newSource Conv16x8 primary3 plus conditional same-arm diagnostic3. No extra workloads, no consumed retry/refund. Full raw and independent restore receipts reside on genuine164; links and hashes appear in RESULTS_CURRENT. Host wall time is separate from GPU cycles. Missing metrics remain UNKNOWN.\n')
   subprocess.run(['git','-C',str(repo),'add','--sparse','--',rel],check=True)
   changed=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();need(all(x==rel or x.startswith(rel+'/') for x in changed),'staged path escapes publication scope')
   if changed:subprocess.run(['git','-C',str(repo),'commit','-m','EP Main Stage II '+('final finite results' if final else 'accepted execution progress')],check=True)
   subprocess.run(['git','-C',str(repo),'push','origin',publication['branch']],check=True)
   head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','origin','refs/heads/'+publication['branch']],text=True).split()[0]
   need(head==remote,'remote HEAD readback mismatch');put(self.C/'REMOTE_PUBLICATION_RECEIPT.json',dict(utc=now(),HEAD=head,remote_HEAD=remote,exact_directory=rel,final=final))
   self.event('REMOTE_PUBLISHED',HEAD=head,final=final);self.lastpublish=time.monotonic()
 def archive_summary(self):
  # Small derived files only; no Trace or old asset recopies. Commit-last genuine164 copy with reopened SHA verification.
  import shutil
  mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
  need(mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs','summary archive genuine164')
  target=P(self.m['summary_archive_root'])/self.session;need(str(target).startswith('/root/share/mnt164/huangrulin/'),'summary archive approved164 prefix')
  target.mkdir(parents=True,exist_ok=False);members=[]
  files=[self.C/'RESULTS_CURRENT.json',self.C/'RESULTS_CURRENT.csv',self.manifest_path]
  files+=sorted((self.C/'NI_RESULTS').glob('*.json'))+sorted((self.C/'MECHANISM_METRICS').glob('*.json'))
  for src in files:
   relative=src.relative_to(self.C) if src.is_relative_to(self.C) else P('manifest')/src.name
   dst=target/relative;dst.parent.mkdir(parents=True,exist_ok=True);need(not dst.exists(),'summary member collision');need(src.stat().st_size<=16*M,'summary unexpectedly large');shutil.copy2(src,dst);need(sha(src)==sha(dst),'summary reopened SHA');members.append(dict(name=str(relative),source_ref=ref(src),archive_ref=ref(dst)))
  receipt=dict(schema='EP_MAIN_SMALL_SUMMARY_TRUE164_RECEIPT_V1',utc=now(),status='REOPENED_SHA_PASS',Source_keep=True,members=members)
  put(target/'COMMIT.json',receipt);put(self.C/'SUMMARY_ARCHIVE_RECEIPT.json',dict(**receipt,target=str(target)))
 def check_activation(self):
  a=read(self.C/'MAIN_EXECUTION_AUTHORIZATION.json')
  need(a['schema']=='EP_MAIN_STAGEII_EXECUTOR_ACTIVATION_V1' and a['status']=='MAIN_REVIEWED_REGISTERED_EXACT_FINITE_EXECUTION_AUTHORIZED' and a['approved_by']=='EP-MAIN','Main executor activation required')
  need(a['manifest_ref']==ref(self.manifest_path) and a['executor_ref']==ref(__file__) and a['automatic_retry'] is False,'activation exact manifest/code/no-retry')
  receipt=exact(a['registration_receipt_ref']);need(receipt.get('foreign_rows_preserved') is True,'registration preservation receipt')
  reg,_=self.rows()
  for g,qid in REQUESTS.items():
   q=reg['registered_future_requests'][qid];need(q['budget']=={'wv':2,'t3':6}[g] and q['remaining']==q['budget'] and q['consumed']=={},'fresh exact unconsumed budget')
   for p in self.points:
    if p['group']==g:need(q['admitted_specs'][p['cohort']]==p['spec_ref']['sha256'],'registered exact spec SHA')
 def run(self):
  self.check_activation()
  self.C.mkdir(parents=True,exist_ok=True)
  with lock(self.C/'FINITE_MAIN_EXECUTOR.lock',True):
   need(not (self.C/'EXECUTOR_STARTED.json').exists(),'finite executor already started; Main review required, no automatic resume')
   _,rows=self.rows();need(not rows,'new fresh scopes only; consumed startup requires Main explicit operational review')
   put(self.C/'EXECUTOR_STARTED.json',dict(schema='EP_MAIN_FINITE_EXECUTOR_START_V1',utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),automatic_resume=False))
   self.event('CONTROLLER_STARTED')
   while True:
    try:self.poll();self.accept_one();_,rows=self.rows()
    except Exception as exc:
     self.event('OPERATIONAL_REVIEW_HOLD_WITHOUT_MODEL_KILL',reason=repr(exc));time.sleep(10);continue
    try:self.phase(rows)
    except Exception as exc:
     for c in T_ON:
      if c not in rows:self.states[c]={'status':'CONDITIONAL_PHASE_REVIEW_HOLD','terminal_hold':True,'reason':repr(exc),'utc':now()}
     self.event('CONDITIONAL_PHASE_REVIEW_HOLD',reason=repr(exc))
    try:self.ni(rows)
    except Exception as exc:self.event('OPTIONAL_NI_ANALYSIS_HOLD',reason=repr(exc))
    eligible,ready,bad=runnable(self.points,rows,self.states)
    if bad:
     for c in T_ON:
      if c not in rows:self.states[c]={'status':'CONDITIONAL_ON_HOLD_PRIMARY_NOT_ACCEPTED','terminal_hold':True,'utc':now()}
     eligible=[p for p in eligible if p['cohort'] not in T_ON]
    for p in eligible:
     if len(self.running)>=2:break
     if p['cohort'] not in self.running:
      try:self.start(p)
      except Exception as exc:
       self.states[p['cohort']]={'status':'PRELAUNCH_ENGINEERING_REVIEW_HOLD','terminal_hold':True,'reason':repr(exc),'utc':now()};self.event('PRELAUNCH_ENGINEERING_REVIEW_HOLD',cohort=p['cohort'],reason=repr(exc))
    try:result=self.summary()
    except Exception as exc:
     self.event('RESULT_SUMMARY_REVIEW_HOLD_WITHOUT_MODEL_KILL',reason=repr(exc))
     if self.running:time.sleep(10);continue
     raise
    if time.monotonic()-self.lastpublish>=1800:
     try:self.publish()
     except Exception as exc:self.event('PUBLICATION_HOLD',reason=repr(exc))
    settled=all(p['cohort'] in rows and rows[p['cohort']]['state'] in TERMINAL or self.states.get(p['cohort'],{}).get('terminal_hold') for p in self.points)
    if settled and not self.running and not self.pending_accept:break
    if time.monotonic()-self.started>self.m.get('admission_wait_and_execution_wall_seconds',7*86400):
     self.event('FINITE_WALL_HOLD');need(not self.running,'controller wall reached with live native frontend; never auto kill healthy model')
     break
    time.sleep(10)
   self.summary()
   try:self.archive_summary()
   except Exception as exc:self.event('SUMMARY_ARCHIVE_HOLD',reason=repr(exc))
   try:self.publish(final=True)
   except Exception as exc:self.event('FINAL_PUBLICATION_HOLD',reason=repr(exc))
   _,rows=self.rows()
   allterminal=all(rows.get(p['cohort'],{}).get('state') in TERMINAL for p in self.points)
   allaccepted=all(rows.get(p['cohort'],{}).get('state')=='CLOSED_ACCEPTED' for p in self.points)
   nis=[read(f) for f in (self.C/'NI_RESULTS').glob('*.json')]
   nipass=len(nis)==3 and all(v.get('status')=='PASS_ACCEPTED_SAME_ARM_COMPACT_SEMANTICS' for v in nis)
   remote=read(self.C/'REMOTE_PUBLICATION_RECEIPT.json') if (self.C/'REMOTE_PUBLICATION_RECEIPT.json').exists() else {}
   pubpass=remote.get('final') is True and remote.get('HEAD')==remote.get('remote_HEAD')
   put(self.C/'EXECUTOR_FINISHED.json',dict(utc=now(),session=self.session,status='ALL_EIGHT_ACCEPTED_NI_AND_REMOTE_FINAL_PASS' if allaccepted and nipass and pubpass else 'FINITE_SCOPE_TERMINAL_OR_REVIEW_HOLD',all_eight_terminal=allterminal,all_eight_accepted=allaccepted,three_same_arm_NI_pass=nipass,final_remote_HEAD_verified=pubpass,summary_archive_verified=(self.C/'SUMMARY_ARCHIVE_RECEIPT.json').exists(),automatic_retry=False,science_starts_reconciled_by_authority=True))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);a=ap.parse_args()
 try:Executor(a.manifest).run()
 except BaseException as exc:
  print(json.dumps(dict(status='MAIN_EXECUTOR_REVIEW_HOLD',reason=repr(exc),automatic_retry=False)),file=sys.stderr);raise
