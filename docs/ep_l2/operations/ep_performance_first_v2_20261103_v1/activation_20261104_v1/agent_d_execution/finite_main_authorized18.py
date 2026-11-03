#!/usr/bin/env python3
"""Unified Main exact18 candidate. Passive import/default prepare; no registration.
One dispatcher, two native families; distinct accept-serialization and child restore locks.
"""
import argparse,contextlib,csv,datetime,fcntl,hashlib,importlib.util,json,os,pathlib,subprocess,sys,time,uuid,shutil
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');V=J/'research/performance_first_v2_20261103_v1';ACT=V/'activation_20261104_v1';DEFAULT_CONTROL=ACT/'control'
BASE=J/'execution_v2_20261103_v1/tools/finite_main_executor.py';BASE_SHA='5db1fe2dfe2abdb17df10f187725e347600fa35793aa32a09c8b25f3801324ef'
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=BASE_SHA:raise RuntimeError('frozen passive generic helper drift')
sp=importlib.util.spec_from_file_location('frozen_finite_main_definitions_only',BASE);base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
need,read,put,ref,exact,sha,now,lock,authority,pid_identity,same_live=map(lambda n:getattr(base,n),['need','read','put','ref','exact','sha','now','lock','authority','pid_identity','same_live'])
REQUESTS={'system':'EP_L2_SYSTEM_850MHZ_PARAMETER_FAMILY_V2_20261104_V1','highclock':'EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'};BUDGETS={'system':12,'highclock':6};ROOTS={'system':J/'execution_system850_v2_20261104_v1/system','highclock':J/'execution_cc_cam_highclock_20261104_v1/highclock'}
SOURCE_CORE={'system':'78f4b59e865b136eede74df74c44c210f5b4ca04','highclock':'862376f62ab19f9a677abe31c6a422028b44fcd0'}
ADMISSION=J/'execution_performance_first_20261103_v1/control/ADMISSION.lock';RESTORE=ADMISSION.with_name('ARCHIVE_SHARED_WINDOW.lock');GITLOCK=ADMISSION.with_name('MAIN_GIT_PUBLICATION.lock');OWNERSHIP=J/'execution_v2_20261103_v1/control/GLOBAL_MAIN_SUCCESSOR_OWNERSHIP.lock'
SYSTEM={f'EP_PERF_PFV2_SYSTEM850_{w}_{m}_{f}_V1'for w in ['FWT','GEMM']for m in ['S','WV_ZERO_RO']for f in ['G64W16','FRFCFS256','G64W16_FRFCFS256']};HIGH={f'EP_PERF_CC_CAM_VECTOR4M_{m}_{f}_V1'for m in ['S','F']for f in [850,1275,1700]};TERMINAL=base.TERMINAL;M=1<<20

def nas_capacity_gate(spec,mount=None,stat=None):
 # Fresh real free bytes, not an arbitrary reserve and not duplicated local pool.
 path='/root/share/mnt164'
 if mount is None:mount=json.loads(subprocess.check_output(['findmnt','-J','-T',path],text=True))['filesystems'][0]
 need(mount.get('source')=='admin-wcx@10.208.130.164:/home/shared'and mount.get('fstype')=='fuse.sshfs','NAS_QUALIFICATION_HOLD: genuine164 mount/source required')
 if stat is None:stat=os.statvfs(path)
 free=stat.f_bavail*stat.f_frsize;required=spec['limits']['result_bytes']+2*M
 need(not(stat.f_flag&getattr(os,'ST_RDONLY',1)),'NAS_QUALIFICATION_HOLD: read-only164')
 need(free>=required,'RESOURCE_ADMISSION_HOLD: true164 free bytes '+str(free)+' less than actual point archive increment '+str(required))
 return dict(status='TRUE164_FRESH_MOUNT_AND_INCREMENTAL_FREE_PASS',utc=now(),source=mount['source'],fstype=mount['fstype'],free_bytes=free,point_result_limit_bytes=spec['limits']['result_bytes'],archive_increment_plus_metadata_bytes=required,arbitrary_extra_GiB_reservation=False)

def same_ref(a,b):return isinstance(a,dict)and isinstance(b,dict)and a.get('path')==b.get('path')and a.get('sha256')==b.get('sha256')
def source_input(p):return p['source_identity'],p['input_identity_sha256']
def system_meta(c):
 w='FWT'if'_FWT_'in c else'GEMM';f='G64W16_FRFCFS256'if'_G64W16_FRFCFS256_'in c else('G64W16'if'_G64W16_'in c else'FRFCFS256');return w,f

def validate_manifest(m):
 need(m['schema']=='EP_MAIN_V2_AUTHORIZED18_EXECUTION_MANIFEST_V1','exact18 manifest schema');need(P(m['control_root'])==DEFAULT_CONTROL,'central control root')
 need(m['max_concurrent_models']==2 and m['new_model_start_ceiling']==18 and m['automatic_retry']is False and m['refund']is False,'cap2/exact18/no retry/refund')
 need(set(m['groups'])==set(REQUESTS),'two exact native groups');need(len(m['points'])==18 and {p['cohort']for p in m['points']}==SYSTEM|HIGH,'exact18 names/no duplicate')
 need(P(m['global_admission_lock'])==ADMISSION and P(m['runtime_global_restore_lock'])==RESTORE,'same actual runtime global locks');need(P(m['accept_serial_lock'])!=RESTORE and P(m['accept_serial_lock'])!=ADMISSION,'no parent-child same-lock deadlock')
 for g,qid in REQUESTS.items():
  z=m['groups'][g];need(z['request_id']==qid and z['budget']==BUDGETS[g]and P(z['data_root'])==ROOTS[g],'exact data/scope/budget')
  need(P(z['native_entry_ref']['path'])==ROOTS[g].parent/'bin/native'and sha(z['native_entry_ref']['path'])==z['native_entry_ref']['sha256'],'qualified per-family native entry');exact(z['authorization_ref'])
  need((P(z['runtime_root'])/'ep_perf_frontend.py').is_file(),'qualified runtime root')
 for p in m['points']:
  c=p['cohort'];g=p['group'];need(g in REQUESTS and c in(SYSTEM if g=='system'else HIGH),'cohort/group');need(P(p['spec_ref']['path'])==ROOTS[g]/'cases'/c/'control/FROZEN_SPEC.json','exact frozen case path')
  s=exact(p['spec_ref']);need(s['cohort']==c and s['science_request_id']==REQUESTS[g]and s['source_identity']['core_source_commit']==SOURCE_CORE[g],'Source/cohort/scope')
  need(len(s['expected_effective_options'])==282,'actual282 contract');need(s['mode']in(['S','WV_ZERO_RO']if g=='system'else['S','F']),'approved modes')
  if'priority'in p:need(type(p['priority'])is int,'priority integer')
 for r in m.get('runtime_pin_refs',[]):need(sha(r['path'])==r['sha256'],'runtime module binding drift')
 need(sha(m['shared_native_ref']['path'])==m['shared_native_ref']['sha256'],'shared native changed')
 p=m['publication'];need(P(p['repo'])==V/'review'and p['branch']=='hrl/ep-l2-performance-first-v2-20261103-v1','one Main review repo/branch');rel=P(p['relative_directory']);need(not rel.is_absolute()and'..'not in rel.parts and str(rel).startswith('docs/ep_l2/operations/ep_performance_first_v2_20261103_v1/activation_20261104_v1/'),'owned publication subtree')
 return True

def system_combo_gate(reference,g,f):
 need(all(type(x)is int and x>0 for x in [reference,g,f]),'cycles positive ints')
 return ((100*(reference-g)>=reference and 100*(reference-f)>=reference)or(100*(reference-g)>=3*reference and f<=reference)or(100*(reference-f)>=3*reference and g<=reference))
def high1700_gate(s850,f850,s1275,f1275):
 need(all(type(x)is int and x>0 for x in [s850,f850,s1275,f1275]),'newSource cycles positive ints');return max(s850/s1275,f850/f1275)>=1.03

def evaluate_policy(points,rows,views,specs,system_refs,technical_holds=()):
 out={};held=set(technical_holds)
 def done(c):return rows.get(c,{}).get('state')in TERMINAL and views.get(c,{}).get('archived')
 def accepted(c):return rows.get(c,{}).get('state')=='CLOSED_ACCEPTED'and views.get(c,{}).get('accepted')and done(c)
 def bad(c):return rows.get(c,{}).get('state')=='CLOSED_UNACCEPTED'
 fwt_single=[c for c in SYSTEM if system_meta(c)[0]=='FWT'and system_meta(c)[1]!='G64W16_FRFCFS256'];fwt_settled=all(done(c)for c in fwt_single)
 high850={f'EP_PERF_CC_CAM_VECTOR4M_{m}_850_V1'for m in ['S','F']};high1275={c.replace('_850_','_1275_')for c in high850}
 for p in points:
  c=p['cohort'];g=p['group'];status='WAIT';reason='PRECURSOR_NOT_COMPLETE'
  if c in held:status,reason='HOLD','MAIN_EXPLICIT_TECHNICAL_QUALIFICATION_HOLD'
  elif g=='system':
   w,f=system_meta(c)
   if f!='G64W16_FRFCFS256':
    if w=='FWT'or fwt_settled:status,reason='RELEASE','INITIAL_SINGLE_FAMILY; FWT_TERMINAL_ARCHIVED_BEFORE_GEMM'
   else:
    prec=[x for x in SYSTEM if system_meta(x)[0]==w and system_meta(x)[1]!='G64W16_FRFCFS256']
    if any(bad(x)for x in prec):status,reason='HOLD','SAME_INPUT_COMBO_PRECURSOR_FAILED'
    elif all(accepted(x)for x in prec):
     gs=next(x for x in prec if specs[x]['mode']=='WV_ZERO_RO'and system_meta(x)[1]=='G64W16');fs=next(x for x in prec if specs[x]['mode']=='WV_ZERO_RO'and system_meta(x)[1]=='FRFCFS256');r=system_refs[w]['cycles'];ok=system_combo_gate(r,views[gs]['cycles'],views[fs]['cycles']);status,reason=('RELEASE','ABSOLUTE_EP_COMBO_CRITERION')if ok else('PRUNE','EP_ABSOLUTE_CRITERION_FALSE; S_RATIO_NOT_USED')
  else:
   freq=int(c.rsplit('_',2)[1])
   if freq==850:status,reason='RELEASE','NEW_SOURCE_850_FRESH_REFERENCE'
   elif any(bad(x)for x in high850):status,reason='HOLD','NEW_SOURCE_850_PRECURSOR_FAILED'
   elif all(accepted(x)for x in high850):
    if freq==1275:status,reason='RELEASE','NEW850_BOTH_ACCEPTED_AND_ARCHIVED'
    elif any(bad(x)for x in high1275):status,reason='HOLD','NEW_SOURCE_1275_PRECURSOR_FAILED'
    elif all(accepted(x)for x in high1275):
     c1=lambda m,f:f'EP_PERF_CC_CAM_VECTOR4M_{m}_{f}_V1';ok=high1700_gate(views[c1('S',850)]['cycles'],views[c1('F',850)]['cycles'],views[c1('S',1275)]['cycles'],views[c1('F',1275)]['cycles']);status,reason=('RELEASE','AT_LEAST_ONE_NEW_SOURCE_ABSOLUTE_SPEEDUP_RATIO_GE1.03')if ok else('PRUNE','NO_NEW_SOURCE_ARM_3PCT_ABSOLUTE_SPEEDUP')
  out[c]=dict(status=status,reason=reason,group=g)
 return out

class Executor(base.Executor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_manifest(self.m);self.C=P(self.m['control_root']);self.states={};self.running={};self.pending_accept=[];self.started=time.monotonic();self.lastpublish=0;self.lastresource={};self.fatal=[];self.session=str(uuid.uuid4());self.points=self.m['points'];self.bypoint={p['cohort']:p for p in self.points};self.specs={p['cohort']:exact(p['spec_ref'])for p in self.points};self.phase_cache={};self.failures={}
 def rows(self):
  reg=authority();out={}
  for g,qid in REQUESTS.items():
   q=reg['registered_future_requests'].get(qid)
   if q is not None:out.update(q['consumed'])
  return reg,out
 def group_call(self,g,source,args=()):
  root=self.m['groups'][g]['runtime_root'];code='import sys,json;sys.path.insert(0,'+repr(root)+');'+source
  return subprocess.run([sys.executable,'-B','-c',code,*map(str,args)],text=True,capture_output=True,timeout=180)
 def native(self,op,c,**kw):
  g=self.bypoint[c]['group'];r=self.m['groups'][g]['native_entry_ref'];need(sha(r['path'])==r['sha256'],'family native entry drift');need(sha(self.m['shared_native_ref']['path'])==self.m['shared_native_ref']['sha256'],'shared native byte drift');return subprocess.Popen([r['path'],'experiment',op,c,'--project','EP_L2'],**kw)
 def claim(self,p,cpu):
  c=p['cohort'];s=self.specs[c];root=P(self.m['groups'][p['group']]['data_root']);path=root/'control/DISPATCH_CLAIMS.json';q=read(path);need(c not in q['claims'],'existing claim requires reviewed recovery')
  q['claims'][c]=dict(state='CLAIMED',cohort=c,spec_sha256=p['spec_ref']['sha256'],host_cpu=cpu,estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],remaining_write_bytes=s['limits']['result_bytes']+2*M,utc=now(),controller_pid=os.getpid(),controller_start_ticks=pid_identity(os.getpid())['start_ticks']);put(path,q);put(root/'control/dispatch_bindings'/(c+'.json'),dict(cohort=c,spec_sha256=p['spec_ref']['sha256'],host_cpu=cpu,controller_session=self.session));r=self.group_call(p['group'],'from ep_perf_common_v2 import *;publish_own_write_carrier(read(ROOT/"control/DISPATCH_CLAIMS.json")["claims"])');need(r.returncode==0,'publish current scope write carrier failed '+r.stderr[-1000:])
 def release_unconsumed_claim(self,p):
  _,rows=self.rows();c=p['cohort'];need(c not in rows,'consumed claims cannot be refunded');root=P(self.m['groups'][p['group']]['data_root']);v=read(root/'control/DISPATCH_CLAIMS.json');v['claims'].pop(c,None);put(root/'control/DISPATCH_CLAIMS.json',v);r=self.group_call(p['group'],'from ep_perf_common_v2 import *;publish_own_write_carrier(read(ROOT/"control/DISPATCH_CLAIMS.json")["claims"])');need(r.returncode==0,'unconsumed carrier reconciliation failed')
 def closed_view(self,c,row):
  if row.get('state')not in TERMINAL:return dict(archived=False,accepted=False)
  ar=exact(row['archive_receipt_ref']);rr=ar.get('native_restores',[]);need(ar.get('status')=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and ar['cohort']==c and ar['source_keep']is True and len(rr)==2 and all(x['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'for x in rr),'complete archive two restores required');need(ar['archive_ref']['path'].startswith('/root/share/mnt164/'),'true164')
  v=dict(archived=True,accepted=False,archive_receipt_ref=row['archive_receipt_ref'])
  if row['state']=='CLOSED_ACCEPTED':
   pt=exact(row['accepted_point_ref']);s=self.specs[c];need(pt['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED'and pt['hardware_drained']is True and pt['cohort']==c and pt['source_identity']==s['source_identity']and pt['input_identity_sha256']==s['input_identity_sha256']and pt['mode']==s['mode']and same_ref(pt['spec_ref'],self.bypoint[c]['spec_ref']),'accepted Source/input/spec/mode/drain');need(pt['uuid']==row['uuid']==ar['uuid'],'accepted archive UUID');v.update(pt,archived=True,accepted=True,accepted_point_ref=row['accepted_point_ref'],archive_receipt_ref=row['archive_receipt_ref'])
  return v
 def system_refs(self):
  refs={}
  for w in ['FWT','GEMM']:
   c=next(c for c,p in self.bypoint.items()if p['group']=='system'and system_meta(c)[0]==w);s=self.specs[c];q=exact(s['absolute_REF850_EP_anchor_qualification_ref']);pt=exact(q['point_ref']);need(q['approved_by']=='EP-MAIN'and q['currently_accepted_population']is True and q['current_closed_state']=='CLOSED_ACCEPTED'and pt['source_identity']==s['source_identity']and pt['input_identity_sha256']==s['input_identity_sha256']and pt['mode']=='WV_ZERO_RO','Main exact accepted ownEP850 reference');refs[w]=dict(pt,review_ref=s['absolute_REF850_EP_anchor_qualification_ref'],point_ref=q['point_ref'])
  return refs
 def priorities(self,p):
  c=p['cohort'];g=p['group'];priority=p.get('priority')
  if priority is None:
   if g=='highclock':priority={850:10,1275:25,1700:50}[int(c.rsplit('_',2)[1])]
   else:w,f=system_meta(c);priority=(10 if w=='FWT'else 35)if f!='G64W16_FRFCFS256'else(45 if w=='FWT'else 55)
  # Alternate ready families at samepriority; accepted/active status is elsewhere.
  return priority,g,c
 def technical_holds(self):
  p=self.C/'MAIN_TECHNICAL_QUALIFICATION_HOLDS.json'
  if not p.exists():return set()
  q=read(p);need(q['approved_by']=='EP-MAIN'and same_ref(q['manifest_ref'],ref(self.manifest_path)),'explicit Main technical withdrawal');held=set(q['held_cohorts']);need(held.issubset(self.bypoint),'hold unknowncohort');return held

 def immutable(self,path,value):
  path=P(path)
  if path.exists():need(read(path)==value,'immutable stage receipt drift '+str(path));return ref(path)
  return put(path,value)
 def decisions(self,reg,rows):
  views={};out={};refs={};errors={}
  for g in REQUESTS:
   try:
    for p in self.points:
     if p['group']==g:views[p['cohort']]=self.closed_view(p['cohort'],rows.get(p['cohort'],{}))
    if g=='system':refs=self.system_refs()
    out.update(evaluate_policy([p for p in self.points if p['group']==g],rows,views,self.specs,refs,self.technical_holds()))
   except Exception as e:
    errors[g]=repr(e)
    for p in self.points:
     if p['group']==g:out[p['cohort']]=dict(status='HOLD',group=g,reason='LOCAL_FAMILY_EVIDENCE_OR_QUALIFICATION_HOLD',detail=repr(e))
  return out,views,refs,errors
 def emit_stage_receipts(self,decisions,views,refs,rows,only_group=None):
  # All stage artifacts are Main control metadata. Runtime remains the final
  # checker and atomically consumes only after a fresh resource admission.
  with lock(ADMISSION):
   for w in ['FWT','GEMM']:
    if only_group not in [None,'system']:continue
    combo=[p for p in self.points if p['group']=='system'and system_meta(p['cohort'])==(w,'G64W16_FRFCFS256')]
    if not all(decisions[p['cohort']]['status']=='RELEASE'for p in combo):continue
    gs=next(c for c in SYSTEM if system_meta(c)==(w,'G64W16')and self.specs[c]['mode']=='WV_ZERO_RO');fs=next(c for c in SYSTEM if system_meta(c)==(w,'FRFCFS256')and self.specs[c]['mode']=='WV_ZERO_RO');s=self.specs[gs];root=P(self.m['groups']['system']['data_root']);r=refs[w]
    review=dict(schema='EP_MAIN_SYSTEM850_ABSOLUTE_EP_COMBINATION_GATE_REVIEW_V1',status='MAIN_REVIEWED_SYSTEM850_ABSOLUTE_EP_GATE_PASS',approved_by='EP-MAIN',request_id=REQUESTS['system'],input_identity_sha256=s['input_identity_sha256'],source_identity=s['source_identity'],reference_EP_point_ref=r['point_ref'],G64W16_EP_point_ref=rows[gs]['accepted_point_ref'],FRFCFS256_EP_point_ref=rows[fs]['accepted_point_ref'],reference_EP_cycles=r['cycles'],geometry_EP_cycles=views[gs]['cycles'],scheduler_EP_cycles=views[fs]['cycles'],criterion='EACH>=1PCT_EP_CYCLE_REDUCTION_OR_ONE>=3PCT_OTHER_NONNEGATIVE; SAMEINPUT4SINGLE_ARMS_CLOSED_ACCEPTED_ARCHIVED',S_ratio_not_used=True,controller_manifest_ref=ref(self.manifest_path))
    rr=self.immutable(root/'control/combination_reviews'/(w+'.json'),review)
    for p in combo:self.immutable(root/'control/conditional_release'/(p['cohort']+'.json'),dict(status='MAIN_RELEASED_APPROVED_CONDITIONAL_CELL',cohort=p['cohort'],request_id=REQUESTS['system'],spec_sha256=p['spec_ref']['sha256'],criterion_review_ref=rr))
   if only_group=='system':return
   hc=lambda m,f:f'EP_PERF_CC_CAM_VECTOR4M_{m}_{f}_V1';root=P(self.m['groups']['highclock']['data_root']);baseco=[hc(m,850)for m in ['S','F']]
   if all(views.get(c,{}).get('accepted')for c in baseco):
    s=self.specs[baseco[0]];review=dict(schema='EP_MAIN_CC_CAM_NEW_SOURCE_850_PAIR_ACCEPTANCE_REVIEW_V1',status='MAIN_REVIEWED_NEW_SOURCE_850_PAIR_ACCEPTED_ARCHIVED',approved_by='EP-MAIN',source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],accepted_point_refs={m:rows[hc(m,850)]['accepted_point_ref']for m in ['S','F']},archive_receipt_refs={m:rows[hc(m,850)]['archive_receipt_ref']for m in ['S','F']},controller_manifest_ref=ref(self.manifest_path));rr=self.immutable(root/'control/NEW_SOURCE_850_PAIR_MAIN_REVIEW.json',review);self.immutable(root/'control/NEW_SOURCE_850_PAIR_MAIN_REVIEW_REF.json',rr)
   target=[self.bypoint[hc(m,1700)]for m in ['S','F']]
   if all(decisions[p['cohort']]['status']=='RELEASE'for p in target):
    cpu=exact(self.m['cpu1700_ref']);s=self.specs[hc('S',1700)];need(cpu['status']=='PASS'and cpu['new_source_core']==s['source_identity']['core_source_commit']and any(z.get('mhz')==1700 and z.get('PASS')is True for z in cpu['rows'])and all(z.get('PASS')is True for z in cpu['rows']if z.get('mhz')==1700),'actual CPU1700 finalSource proof')
    ratios={m:views[hc(m,850)]['cycles']/views[hc(m,1275)]['cycles']for m in ['S','F']};need(max(ratios.values())>=1.03,'exact3pct absolute speedup ratio')
    review=dict(status='MAIN_REVIEWED_CC_CAM_1700_EXTENSION_CRITERION_PASS',approved_by='EP-MAIN',source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],accepted_1275_point_refs={m:rows[hc(m,1275)]['accepted_point_ref']for m in ['S','F']},archive_1275_receipt_refs={m:rows[hc(m,1275)]['archive_receipt_ref']for m in ['S','F']},cpu1700_ref=self.m['cpu1700_ref'],absolute_speedup_ratios=ratios,threshold=1.03,S_only_trigger_not_EP_success=True,controller_manifest_ref=ref(self.manifest_path));rr=self.immutable(root/'control/EXTENSION1700_MAIN_REVIEW.json',review)
    for p in target:self.immutable(root/'control/conditional_release'/(p['cohort']+'.json'),dict(status='MAIN_RELEASED_APPROVED_CONDITIONAL_CELL',cohort=p['cohort'],request_id=REQUESTS['highclock'],spec_sha256=p['spec_ref']['sha256'],family_stage='CONDITIONAL1700',criterion_review_ref=rr))
 def start(self,p):
  c=p['cohort'];g=p['group']
  if time.monotonic()<self.lastresource.get(c,0)+60:return False
  self.lastresource[c]=time.monotonic();cpu=self.available_cpu()
  if cpu is None:return False
  with lock(ADMISSION):
   reg,rows=self.rows();need(c not in rows,'consumed model is never forked again');need(c not in self.technical_holds(),'Main technicalhold')
   count=sum(v.get('state')in ['CONSUMED_BEFORE_FORK','RUNNING']for qid,q in reg['registered_future_requests'].items()if qid.startswith('EP_')and isinstance(q.get('consumed'),dict)for v in q['consumed'].values())
   if count>=2 or len(self.running)>=2:self.states[c]=dict(status='RESOURCE_HOLD_GLOBAL_EP_CAP2',utc=now());return False
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
 def poll(self):
  for c,v in list(self.running.items()):
   rc=v['process'].poll()
   if rc is None:continue
   _,rows=self.rows();p=self.bypoint[c]
   if c in rows:
    if not rows[c].get('done_ref'):self.states[c]=dict(status='LOCAL_CONSUMED_WRAPPER_EXIT_WITHOUT_DONE_HOLD',reason='preserve live-generation/resource claim; no retry',returncode=rc,terminal_hold=True);continue
    exact(rows[c]['done_ref']);v['log'].close();self.running.pop(c);self.pending_accept.append(c);self.states[c]=dict(status='NATIVE_TERMINAL_PENDING_ACCEPT',returncode=rc,utc=now())
   else:
    v['log'].close();self.running.pop(c);self.release_unconsumed_claim(p);msg=P(v['log_path']).read_text(errors='replace')[-6000:];resource='RESOURCE_ADMISSION_HOLD:'in msg;self.states[c]=dict(status='PRECONSUME_RESOURCE_HOLD'if resource else'PRECONSUME_TECHNICAL_HOLD',terminal_hold=not resource,reason=msg,utc=now())
   self.event('NATIVE_FRONTEND_EXIT',cohort=c,returncode=rc,consumed=c in rows)
 def archive_only_safe(self,c,row):
  need(row['state']=='PARSE_HOLD'and row.get('done_ref'),'only sealed consumed PARSE_HOLD may archive-only close');exact(row['done_ref']);g=self.bypoint[c]['group'];claims=read(P(self.m['groups'][g]['data_root'])/'control/DISPATCH_CLAIMS.json')['claims'];cl=claims.get(c,{})
  if cl.get('model_pid'):need(not same_live(dict(pid=cl['model_pid'],start_ticks=cl['model_start_ticks'])),'model generation stilllive')
  if cl.get('launcher_pid'):
   try:q=pid_identity(cl['launcher_pid']);need(q['state']in ['Z','X'],'tracedlauncher stilllive')
   except OSError:pass
  return True
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0)
  # Different outer mutex! The child itself takes the actual common RESTORE
  # lock and nests ADMISSION only when releasing its resource claim.
  with lock(self.m['accept_serial_lock']):
   path=self.C/'native_logs'/(c+'.accept.log')
   with path.open('xb')as f:p=self.native('accept',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL);rc=p.wait()
   _,rows=self.rows();row=rows[c]
   if row['state']=='PARSE_HOLD':
    marker=self.C/'ARCHIVE_ONLY_CLOSURES'/(c+'.json')
    if not marker.exists():
     self.archive_only_safe(c,row);put(marker,dict(status='ARCHIVE_ONLY_CLOSURE_NO_MODEL_RETRY_NO_REPARSE',cohort=c,done_ref=row['done_ref'],original_validation_hold_ref=row.get('validation_hold_ref'),only_one_extra_native_accept=True,scientific_start_count=0));self.event('ARCHIVE_ONLY_CLOSURE_NO_MODEL_RETRY_NO_REPARSE',cohort=c)
     with(self.C/'native_logs'/(c+'.archive_only.log')).open('xb')as f:p=self.native('accept',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL);rc=p.wait()
     _,rows=self.rows();row=rows[c]
   self.states[c]=dict(status=row['state'],accept_returncode=rc,utc=now())
   if row['state']not in TERMINAL:self.states[c].update(terminal_hold=True,reason='bounded acceptance/archive reviewHOLD; no model retry')
   self.event('ACCEPT_ARCHIVE_TWO_RESTORES_FINISHED',cohort=c,state=row['state'],returncode=rc)

 def check_activation(self):
  a=read(self.C/'MAIN_EXECUTION_AUTHORIZATION.json');need(a['schema']=='EP_MAIN_V2_AUTHORIZED18_EXECUTOR_ACTIVATION_V1'and a['status']=='MAIN_REVIEWED_REGISTERED_EXACT18_FINITE_EXECUTION_AUTHORIZED'and a['approved_by']=='EP-MAIN','Main activation required');need(same_ref(a['executor_ref'],ref(__file__))and same_ref(a['manifest_ref'],ref(self.manifest_path))and a['no_retry']is True and a['no_refund']is True,'exact Maincode/manifest')
  reg,rows=self.rows();need(not rows,'fresh existing scopes required; recovery needs explicit Main handoff')
  for g,qid in REQUESTS.items():
   rr=exact(a['registration_receipt_refs'][g]);need(rr['foreign_rows_preserved']is True,'fresh registration preservedforeign');q=reg['registered_future_requests'][qid];need(q['budget']==BUDGETS[g]and q['remaining']==BUDGETS[g]and q['consumed']=={},'fresh separate authorized budgets')
   needed={p['cohort']:p['spec_ref']['sha256']for p in self.points if p['group']==g};need(q['admitted_specs']==needed,'exact admitted specs')
   need(not read(P(self.m['groups'][g]['data_root'])/'control/DISPATCH_CLAIMS.json')['claims'],'no stale scopeclaims')
  ended=exact(a['old_X_finished_ref']);need(ended['status']=='SAME_OWNER_AUTHORIZED_REMAINDER_TERMINAL_OR_HOLD','old scope naturalfinish proof')
  old=read(J/'execution_performance_first_20261103_v1/control/OPERATIONAL_SUCCESSOR_STARTED.json');need(not same_live(old['process']),'old controller live')
 def metrics(self,p,point,row):
  path=self.C/'MECHANISM_METRICS'/(p['cohort']+'.json')
  if path.exists():return ref(path)
  b=exact(point['validation_ref']);return put(path,dict(schema='EP_MAIN_ACCEPTED_SMALL_MECHANISM_SUMMARY_V1',cohort=p['cohort'],group=p['group'],validation_ref=point['validation_ref'],mechanism_metrics=b.get('model',{}).get('mechanism_metrics','UNKNOWN'),raw_or_Trace_scan=False,blocked_exposures_are_not_exclusive_GPUcycles=True))
 def summary(self,decisions=None):
  reg,rows=self.rows();out=[]
  for p in self.points:
   c=p['cohort'];s=self.specs[c];r=rows.get(c,{});v=dict(cohort=c,group=p['group'],mode=s['mode'],source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],spec_ref=p['spec_ref'],state=r.get('state',self.states.get(c,{}).get('status','NOT_STARTED')),consumed=c in rows,controller_state=self.states.get(c),family_decision=(decisions or{}).get(c))
   for k in ['done_ref','accepted_point_ref','archive_receipt_ref','validation_ref']:v[k]=r.get(k)
   if r.get('accepted_point_ref')and r.get('state')=='CLOSED_ACCEPTED':
    pt=exact(r['accepted_point_ref']);v.update({k:pt[k]for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']})
    try:v['mechanism_metrics_ref']=self.metrics(p,pt,r)
    except Exception as e:v['small_metrics_status']=dict(status='UNKNOWN',reason=repr(e))
   if r.get('done_ref'):
    d=exact(r['done_ref']);v.update({k:d.get(k)for k in ['elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason']})
   out.append(v)
  pairs=[]
  for p in self.points:
   s=self.specs[p['cohort']]
   if s['mode']=='S'or rows.get(p['cohort'],{}).get('state')!='CLOSED_ACCEPTED':continue
   if p['group']=='system':w,f=system_meta(p['cohort']);peer=f'EP_PERF_PFV2_SYSTEM850_{w}_S_{f}_V1'
   else:peer=p['cohort'].replace('_F_','_S_')
   if rows.get(peer,{}).get('state')=='CLOSED_ACCEPTED':
    a=exact(rows[peer]['accepted_point_ref']);b=exact(rows[p['cohort']]['accepted_point_ref']);need(source_input(a)==source_input(b),'no crossSource/input performance pair');pairs.append(dict(S=peer,EP=p['cohort'],same_background_S_over_EP=a['cycles']/b['cycles'],EP_cycle_reduction=1-b['cycles']/a['cycles']))
  result=dict(schema='EP_MAIN_V2_AUTHORIZED18_FINITE_RESULTS_V1',utc=now(),session=self.session,points=out,same_background_pairs=pairs,budgets={g:{k:reg['registered_future_requests'][q].get(k)for k in ['budget','remaining','state']}for g,q in REQUESTS.items()},active_native_frontends=len(self.running),max_global_EP_models=2,cap18_is_only_current_approved_scope=True,new_model_start_ceiling=18,no_consumed_retry=True,no_refund=True,Source_keep=True,raw_polling=False,combined_GM=False,family_failures=self.failures)
  put(self.C/'RESULTS_CURRENT.json',result)
  with(self.C/'RESULTS_CURRENT.csv').open('w',newline='')as f:
   cols=['cohort','group','mode','state','consumed','cycles','instructions','CTA','kernel_count','hardware_drained','elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason'];w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(out)
  return result
 def publish(self,final=False):
  p=self.m['publication'];repo=P(p['repo']);rel=p['relative_directory'];dst=repo/rel
  with lock(GITLOCK):
   need(subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip()==p['branch'],'Main publication branch');need(not subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).strip(),'foreignstaged work');dst.mkdir(parents=True,exist_ok=True)
   for name in ['RESULTS_CURRENT.json','RESULTS_CURRENT.csv','EXECUTOR_STARTED.json']:
    if(self.C/name).exists():shutil.copy2(self.C/name,dst/name)
   for sub in ['MECHANISM_METRICS','ARCHIVE_ONLY_CLOSURES']:
    (dst/sub).mkdir(exist_ok=True)
    for src in(self.C/sub).glob('*.json'):need(src.stat().st_size<=16*M,'smallsummary bound');shutil.copy2(src,dst/sub/src.name)
   put(dst/'EXECUTION_SCOPE.json',dict(manifest_ref=ref(self.manifest_path),executor_ref=ref(__file__),approved18=18,budgets=BUDGETS,final=final,utc=now(),single_Main_writer=True))
   subprocess.run(['git','-C',str(repo),'add','--sparse','--',rel],check=True);subprocess.run(['git','-C',str(repo),'add','--sparse','-f','--',str(P(rel)/'RESULTS_CURRENT.csv')],check=True);changed=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();need(all(x.startswith(rel+'/')for x in changed),'publication escape')
   if changed:subprocess.run(['git','-C',str(repo),'commit','-m','EP V2 authorized18 '+('finite closeout'if final else'accepted execution progress')],check=True)
   subprocess.run(['git','-C',str(repo),'push','origin',p['branch']],check=True);head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','origin','refs/heads/'+p['branch']],text=True).split()[0];need(head==remote,'remote readback');put(self.C/'REMOTE_PUBLICATION_RECEIPT.json',dict(utc=now(),HEAD=head,remote_HEAD=remote,final=final));self.lastpublish=time.monotonic()
 def run(self):
  self.check_activation()
  with lock(self.C/'SINGLE_MAIN_AUTHORIZED18_EXECUTOR.lock',True),lock(OWNERSHIP,True):
   need(not(self.C/'EXECUTOR_STARTED.json').exists(),'no automatic resume/re-fork');put(self.C/'EXECUTOR_STARTED.json',dict(schema='EP_MAIN_V2_AUTHORIZED18_EXECUTOR_START_V1',utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),no_consumed_retry=True));self.event('SINGLE_MAIN_EXECUTOR_STARTED')
   self.summary()
   try:self.publish()
   except Exception as e:self.event('INITIAL_PUBLICATION_HOLD',reason=repr(e))
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
    while len(self.running)<2 and any(ready.values()):
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
   _,rows=self.rows();remote=read(self.C/'REMOTE_PUBLICATION_RECEIPT.json')if(self.C/'REMOTE_PUBLICATION_RECEIPT.json').exists()else{};put(self.C/'EXECUTOR_FINISHED.json',dict(utc=now(),session=self.session,status='AUTHORIZED18_TERMINAL_OR_LOCAL_REVIEW_HOLD',consumed=len(rows),accepted=sum(r['state']=='CLOSED_ACCEPTED'for r in rows.values()),unaccepted=sum(r['state']=='CLOSED_UNACCEPTED'for r in rows.values()),unconsumed_cohorts=[p['cohort']for p in self.points if p['cohort']not in rows],all_consumed_terminal=all(r['state']in TERMINAL for r in rows.values()),final_remote_readback_pass=remote.get('final')is True and remote.get('HEAD')==remote.get('remote_HEAD'),no_retry=True,no_refund=True))

def main(argv=None):
 ap=argparse.ArgumentParser(description='Unified18 Main candidate; default passive prepare');ap.add_argument('--manifest',required=True);g=ap.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');a=ap.parse_args(argv)
 if a.run:Executor(a.manifest).run()
 else:m=read(a.manifest);validate_manifest(m);print(json.dumps(dict(status='PASS_PASSIVE_EXACT18_MANIFEST_NO_LAUNCH',points=18,model_starts=0,registry_writes=0,dispatcher_started=False)))
if __name__=='__main__':main()
