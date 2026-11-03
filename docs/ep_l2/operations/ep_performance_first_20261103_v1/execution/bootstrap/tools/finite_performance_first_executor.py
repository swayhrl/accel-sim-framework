#!/usr/bin/env python3
"""Sole Main finite24 executor candidate. Import and default --prepare are passive.
Only explicit --run plus exact Main activation may dispatch native entries.
No registration, route installation, retry/refund or direct model invocation.
"""
import argparse,importlib.util,hashlib,json,pathlib,sys,os,time,uuid,subprocess,csv,shutil
P=pathlib.Path
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');X=J/'execution_performance_first_20261103_v1';C=X/'control'
BASE=J/'execution_v2_20261103_v1/tools/finite_main_executor.py';BASE_SHA='5db1fe2dfe2abdb17df10f187725e347600fa35793aa32a09c8b25f3801324ef'
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=BASE_SHA:raise RuntimeError('immutable previous generic executor drift')
sp=importlib.util.spec_from_file_location('previous_finite_executor_definitions_only',BASE);base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
need,read,put,ref,exact,sha,now,lock,authority,pid_identity,same_live=map(lambda n:getattr(base,n),['need','read','put','ref','exact','sha','now','lock','authority','pid_identity','same_live'])
sp=importlib.util.spec_from_file_location('performance_first_stage_policy',P(__file__).with_name('performance_first_stage_policy.py'));policy=importlib.util.module_from_spec(sp);sp.loader.exec_module(policy)
REQUESTS={'retention':'EP_L2_PF_RETENTION_CLASS_FWT_GEMM_20261103_V1','service':'EP_L2_PF_DRAM_SERVICE_FWT_GEMM_VECTOR4M_20261103_V1'}
BUDGETS={'retention':8,'service':16};TERMINAL=base.TERMINAL;M=1<<20
APPROVED_IDS=set(['PF_RET_'+w+'_'+v+'_'+o for w in ['fastWalshTransform','GEMM']for v in ['CLEAN_ONLY','DIRTY_ONLY']for o in ['ON','OFF']]+['PF_DRAM_'+w+'_'+m+'_'+str(f)for w in ['FWT','GEMM']for m in ['S','WV_ZERO_RO']for f in [1020,1275,1700]]+['PF_DRAM_VECTOR4M_'+m+'_'+str(f)for m in ['S','F']for f in [1275,1700]])
def cohort_for(cellid):return 'EP_PERF_PF_'+cellid.removeprefix('PF_')+'_V1'
def validate_manifest(m,load_specs=True):
 need(m['schema']=='EP_PERFORMANCE_FIRST_EXACT_EXECUTION_MANIFEST_V1','performance manifest schema')
 need(m['root']==str(X)and m['max_concurrent_models']==2 and m['new_model_start_ceiling']==24 and m['automatic_retry']is False,'fixed root/24 scope/cap2/no retry')
 idx=exact(m['approved_cells_ref']);need(idx['groups']==REQUESTS and {z['proposal_cell_id']for z in idx['cells']}==APPROVED_IDS and len(idx['cells'])==24,'exact approved24 cells')
 need(m['authorization_ref']==idx['authorization_ref'],'authorization matches approved index');exact(m['authorization_ref'])
 ps=m['points'];need(len(ps)==24 and {z['proposal_cell_id']for z in ps}==APPROVED_IDS,'exact finite24 point manifest')
 im={z['proposal_cell_id']:z for z in idx['cells']}
 for p in ps:
  i=im[p['proposal_cell_id']];need(p['cohort']==cohort_for(p['proposal_cell_id'])==i['cohort'],'exact cohort mapping')
  need(p['group']==i['group']and p['science_request_id']==REQUESTS[p['group']],'exact family scope')
  if p.get('spec_ref')and load_specs:validate_spec(p,exact(p['spec_ref']),i)
  elif not p.get('spec_ref'):need(p.get('qualification_status')in ['HOLD','NOT_QUALIFIED'],'null spec only explicit engineering HOLD')
 need(sum(bool(i['initial'])for i in idx['cells'])==10,'initial10 accounting')
 for k in ['native_entry_ref','shared_native_ref']:need(sha(m[k]['path'])==m[k]['sha256'],'current native bytes drift')
 need(P(m['native_entry_ref']['path'])==X/'bin/native','new scoped native only')
 rel=P(m['publication']['relative_directory']);need(str(rel)=='docs/ep_l2/operations/ep_performance_first_20261103_v1/execution','bounded publication path')
 need(P(m['publication']['repo'])==J/'research/performance_first_20261103_v1/review','sole Main new review repo')
 return idx

def validate_spec(p,s,i,amendment=None):
 need(P(p['spec_ref']['path'])==X/p['group']/'cases'/p['cohort']/'control/FROZEN_SPEC.json','exact group spec path')
 a=i['point'];need(s['cohort']==p['cohort']and s['science_request_id']==REQUESTS[p['group']],'exact frozen cohort/request')
 for k,sk in [('source5','source_identity'),('input_identity_sha256','input_identity_sha256'),('geometry','geometry'),('observer_env','observer_env'),('mode','mode')]:need(s[sk]==a[k],'frozen approved '+sk)
 original=exact(a['option_candidate_ref']);opts=original.get('expected_effective_options',original.get('effective_options',original))
 need(isinstance(opts,dict)and len(opts)==282,'approved option candidate full282')
 if amendment is not None:
  need(p['group']=='retention'and a['observer_variant']=='OFF','only retention OFF observer amendment')
  am=exact(amendment);need(am['approved_by']=='EP-MAIN'and am['cohort']==p['cohort'],'Main exact observer amendment')
  exact(am['user_authorization_ref']);new=am['expected_effective_options'];changed={k for k in opts if opts[k]!=new.get(k)}
  need(set(new)==set(opts)and changed.issubset({'-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats'})and new['-gpgpu_ep_l2_ms_observer']=='0','amendment observer-only approved scope')
  need(new['-gpgpu_ep_l2_b0_stats']in ['0','1']and new['-gpgpu_ep_l2_m0a_stats']in ['0','1'],'observer values');opts=new
 need(s['expected_effective_options']==opts,'all282 approved options exact')
 need(s['expected_CTA']==a['expected_CTA']and s['expected_instructions']==a['expected_instructions']and s['source_keep']is True,'completion/KEEP contract')
 return True

def safe_prepare(manifest):
 m=read(manifest);idx=validate_manifest(m)
 return dict(status='PASS_PASSIVE_MANIFEST_CHECK_NOT_LAUNCH_AUTHORIZATION',manifest_ref=ref(manifest),approved_cells=24,initial10=10,qualified_specs=sum(p.get('spec_ref')is not None for p in m['points']),engineering_HOLD=sum(p.get('spec_ref')is None for p in m['points']),new_model_starts=0,registry_writes=0,native_writes=0,processes_started=0)

class Executor(base.Executor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);self.index=validate_manifest(self.m);self.cells={z['cohort']:z for z in self.index['cells']};self.E=X;self.C=C
  self.points=sorted(self.m['points'],key=lambda z:(0 if self.cells[z['cohort']]['initial']else 1,z.get('priority',100),z['cohort']));self.bypoint={p['cohort']:p for p in self.points}
  self.states={};self.running={};self.pending_accept=[];self.started=time.monotonic();self.lastpublish=0;self.lastresource={};self.fatal=[];self.session=str(uuid.uuid4());self.lastpolicy=None;self.ni_qualified=False;self.view_cache={}
 def rows(self):
  reg=authority();out={}
  for q in REQUESTS.values():
   if q in reg['registered_future_requests']:out.update(reg['registered_future_requests'][q]['consumed'])
  return reg,out
 def group_call(self,g,source,args=()):
  need(g in REQUESTS,'known group');code='import sys,json;sys.path.insert(0,'+repr(str(X/('runtime_'+g)))+');'+source
  return subprocess.run([sys.executable,'-B','-c',code,*map(str,args)],text=True,capture_output=True,timeout=180)
 def refresh_qualifications(self,rows):
  qpath=C/'MAIN_POINT_QUALIFICATIONS.json'
  if not qpath.exists():return
  q=read(qpath);need(q['approved_by']=='EP-MAIN'and q['manifest_ref']==ref(self.manifest_path),'Main exact dynamic qualifications')
  for c,v in q['points'].items():
   need(c in self.bypoint,'unknown qualification point');p=self.bypoint[c]
   if v.get('status')!='MAIN_QUALIFIED_FOR_NATIVE':continue
   n=dict(p,spec_ref=v['spec_ref'],qualification_status='MAIN_QUALIFIED_FOR_NATIVE');validate_spec(n,exact(n['spec_ref']),self.cells[c],v.get('observer_amendment_ref'));exact(v['qualification_receipt_ref'])
   if c in rows:need(rows[c].get('spec_sha256')==n['spec_ref']['sha256']or rows[c].get('spec_ref')==n['spec_ref'],'consumed frozen spec cannot mutate')
   p.update(n)
 def check_activation(self):
  a=read(C/'MAIN_EXECUTION_AUTHORIZATION.json');need(a['schema']=='EP_PERFORMANCE_FIRST_EXECUTOR_ACTIVATION_V1'and a['status']=='MAIN_REVIEWED_REGISTERED_FINITE_EXECUTION_AUTHORIZED'and a['approved_by']=='EP-MAIN','Main executor activation required')
  need(a['manifest_ref']==ref(self.manifest_path)and a['executor_ref']==ref(__file__)and a['stage_policy_ref']==ref(P(__file__).with_name('performance_first_stage_policy.py'))and a['automatic_retry']is False,'exact activation code/manifest/policy')
  rr=exact(a['registration_receipt_ref']);need(rr['foreign_rows_preserved']is True,'foreign registry preservation')
  ended=exact(self.m['prior_finished_ref']);need(ended['status']=='TWO_STENCIL_ACCEPTED_AND_REMOTE_FINAL_PASS'and ended['all_terminal'],'prior Main finite scope not naturally closed')
  old=exact(self.m['prior_started_ref']);need(not same_live(old['process']),'prior Main controller still live')
  reg,rows=self.rows();need(not rows,'fresh scopes only; no automatic consumed resume')
  for g,qid in REQUESTS.items():
   qualified=[p for p in self.points if p['group']==g and p.get('spec_ref')]
   q=reg['registered_future_requests'].get(qid)
   if q is None:need(not qualified,'qualified group must be registered');continue
   need(q['budget']==BUDGETS[g]and q['remaining']==BUDGETS[g]and q['consumed']=={},'fresh separate family budget')
   for p in qualified:need(q['admitted_specs'][p['cohort']]==p['spec_ref']['sha256'],'registered exact qualified spec')
  return True

 def accepted_view(self,row):
  if row.get('state')=='CLOSED_UNACCEPTED':return dict(failed=True,accepted_and_archived=False)
  if row.get('state')!='CLOSED_ACCEPTED':return dict(accepted_and_archived=False)
  pt=exact(row['accepted_point_ref']);ar=exact(row['archive_receipt_ref']);cachekey=(row['accepted_point_ref']['sha256'],row['archive_receipt_ref']['sha256'])
  if cachekey in self.view_cache:return dict(self.view_cache[cachekey])
  need(ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and len(ar['native_restores'])==2,'two native restores required')
  need(str(ar['archive_ref']['path']).startswith('/root/share/mnt164/huangrulin/'),'genuine164 archive prefix')
  v=dict(pt,accepted_and_archived=True,accepted_point_ref=row['accepted_point_ref'],archive_receipt_ref=row['archive_receipt_ref'],victim_read_responses=None)
  try:
   b=exact(pt['validation_ref']);need(b.get('source_identity')==pt['source_identity'],'accepted mechanism bundle Source drift');victim=b['model']['mechanism_metrics']['full_mechanism_records']['victim']
   if set(victim)==set(map(str,range(64)))and all(type(z.get('read_responses'))is int and z['read_responses']>=0 for z in victim.values()):v['victim_read_responses']=sum(z['read_responses']for z in victim.values())
  except (KeyError,TypeError):pass
  self.view_cache[cachekey]=dict(v);return v
 def reference_view(self,r):
  need('accepted_point_ref'in r and'archive_receipt_ref'in r and'Main_reuse_review_ref'in r,'Main exact reference/reuse packet required')
  review=exact(r['Main_reuse_review_ref']);need(review['approved_by']=='EP-MAIN'and review['point_ref']==r['accepted_point_ref'],'Main reuse approval exact accepted reference')
  return self.accepted_view(dict(state='CLOSED_ACCEPTED',accepted_point_ref=r['accepted_point_ref'],archive_receipt_ref=r['archive_receipt_ref']))
 def service_history(self,rows):
  h={}
  for w,frequencies in self.m.get('reference_points',{}).items():
   for f,pair in frequencies.items():
    s=self.reference_view(pair['S']);e=self.reference_view(pair['EP']);need(s['source_identity']==e['source_identity']and s['input_identity_sha256']==e['input_identity_sha256'],'reference same Source/input')
    h[(w,int(f))]=dict(accepted_and_archived=True,S_cycles=s['cycles'],EP_cycles=e['cycles'])
  for w in ['FWT','GEMM','VECTOR4M']:
   for f in [1020,1275,1700]:
    group=[p for p in self.points if p['group']=='service'and self.cells[p['cohort']]['point']['id'].startswith('PF_DRAM_'+w+'_')and self.cells[p['cohort']]['point']['DRAM_MHz']==f]
    if not group:continue
    vs=[self.accepted_view(rows.get(p['cohort'],{}))for p in group]
    if any(v.get('failed')for v in vs):h[(w,f)]=dict(failed=True,accepted_and_archived=False)
    elif len(vs)==2 and all(v.get('accepted_and_archived')for v in vs):
     ss=next(v for v in vs if v['mode']=='S');ee=next(v for v in vs if v['mode']!='S');need(ss['source_identity']==ee['source_identity']and ss['input_identity_sha256']==ee['input_identity_sha256'],'service pair same Source/input')
     h[(w,f)]=dict(accepted_and_archived=True,S_cycles=ss['cycles'],EP_cycles=ee['cycles'])
  return h
 def validate_ms_ni(self,n,on,off,rows):
  need(n.get('schema')=='EP_MAIN_PF_RETENTION_MS_APPLICATION_NI_V1'and n.get('status')=='PASS_MS_ONLY_APPLICATION_NI','exact MS-only NI receipt schema/status')
  a=self.cells[on]['point'];need(n['mode']==a['mode']and n['input_identity_sha256']==a['input_identity_sha256'],'NI exact mode/input')
  need(n.get('source_identity',n.get('source'))==a['source5'],'NI exact Source5')
  need(n['primary_point_ref']==rows[on]['accepted_point_ref']and n['off_point_ref']==rows[off]['accepted_point_ref'],'NI exact accepted primary/OFF refs')
  fields=n['equal_fields'];names=set(fields)
  need(len(names)==7 and 'FT_TVD_resource_closure'in names,'all seven frozen equal fields including FT/TVD closure')
  if isinstance(fields,dict):need(all(v is True for v in fields.values()),'NI unequal field cannot PASS')
  return True
 def ni(self,rows):
  qf=C/'NI_COMPARATOR_QUALIFICATION.json'
  if not qf.exists():return
  q=read(qf)
  if q.get('status')!='MAIN_QUALIFIED_SAME_MODE_APPLICATION_COMPARATOR':return
  need(q['approved_by']=='EP-MAIN'and q['manifest_ref']==ref(self.manifest_path),'Main NI comparator review')
  need(sha(q['module_ref']['path'])==q['module_ref']['sha256'],'NI comparator drift')
  module=q.get('module_name','application_ni');need(module.isidentifier(),'bounded NI module name')
  for w in ['fastWalshTransform','GEMM']:
   for v in ['CLEAN_ONLY','DIRTY_ONLY']:
    on=cohort_for('PF_RET_'+w+'_'+v+'_ON');off=cohort_for('PF_RET_'+w+'_'+v+'_OFF');path=C/'NI_RESULTS'/(on+'.json')
    if not all(rows.get(c,{}).get('state')=='CLOSED_ACCEPTED'for c in [on,off]):continue
    if path.exists():
     prev=read(path)
     if prev.get('comparator_ref')==q['module_ref']:continue
    call='import importlib;v=importlib.import_module('+repr(module)+').compare(sys.argv[1],sys.argv[2]);print(json.dumps(v))'
    r=self.group_call('retention',call,[off,on]);value=json.loads(r.stdout)if r.returncode==0 else dict(status='NI_HOLD',reason=(r.stdout+r.stderr)[-4000:])
    if value.get('status')=='PASS_MS_ONLY_APPLICATION_NI':
     try:self.validate_ms_ni(value,on,off,rows)
     except Exception as exc:value=dict(status='NI_HOLD',reported_status='PASS_MS_ONLY_APPLICATION_NI',reason=repr(exc))
    value.update(comparator_ref=q['module_ref'],qualification_ref=ref(qf),same_mode_pair=[off,on]);put(path,value);self.event('SAME_MODE_NI_ANALYSIS',on=on,off=off,status=value.get('status'))
 def stage_decisions(self,rows):
  history=self.service_history(rows);decisions={}
  for group in REQUESTS:
   groups={}
   for p in self.points:
    if p['group']==group:groups.setdefault(self.cells[p['cohort']]['point']['stage'],[]).append(p)
   ordered=sorted(groups,key=lambda s:0 if s in ['FIRST_FWT','FIRST6']else(1 if '1275'in s else 2))
   for stage in ordered:
    ps=groups[stage]
    if group=='service':
     a=self.cells[ps[0]['cohort']]['point'];w=a['id'].split('_')[2];freq=a['DRAM_MHz'];d=policy.evaluate_service(stage,w,freq,history)
     if stage!='FIRST6'and freq==1700:
      previous=decisions.get('service:CONDITIONAL_'+w+'_1275')
      if previous and previous['status']=='PRUNE':d=policy.decision('PRUNE','PREVIOUS_FREQUENCY_PAIR_PRUNED')
    else:
     vv=[]
     for p in self.points:
      a=self.cells[p['cohort']]['point']
      if p['group']=='retention'and a['stage']=='FIRST_FWT':vv.append(dict(self.accepted_view(rows.get(p['cohort'],{})),observer_variant=a['observer_variant'],mode=a['mode']))
     ns=[]
     for kind in ['CLEAN_ONLY','DIRTY_ONLY']:
      n=C/'NI_RESULTS'/(cohort_for('PF_RET_fastWalshTransform_'+kind+'_ON')+'.json')
      raw=read(n).get('status')if n.exists()else'NI_HOLD';ns.append('PASS'if raw in self.m.get('NI_pass_statuses',['PASS_MS_ONLY_APPLICATION_NI'])else'NI_HOLD')
     rr=self.m.get('retention_WV_reference');baseline=self.reference_view(rr)if rr else None;d=policy.evaluate_retention(stage,vv,baseline,ns)
    d.update(group=group,stage=stage,cohorts=sorted(p['cohort']for p in ps));decisions[group+':'+stage]=d
  released=[]
  for d in decisions.values():
   if d['status']!='RELEASE':continue
   if d['stage'] not in ['FIRST6'] and not all(self.bypoint[c].get('spec_ref')for c in d['cohorts']):d.update(status='WAIT',reason='WHOLE_STAGE_QUALIFICATION_PENDING');continue
   if d['stage']=='FIRST6':
    for w in ['FWT','GEMM','VECTOR4M']:
     pair=[c for c in d['cohorts']if self.cells[c]['point']['id'].startswith('PF_DRAM_'+w+'_')]
     if len(pair)==2 and all(self.bypoint[c].get('spec_ref')for c in pair):released.extend(pair)
   else:released.extend(d['cohorts'])
  # Native conditional cells receive the exact per-case contract already used by
  # service runtime. Immutable criterion review and both case bindings are
  # created under the same admission lock as consume; no model/registry writes.
  with lock(C/'ADMISSION.lock'):
   for d in decisions.values():
    if d['group']!='service'or d['stage']=='FIRST6'or d['status']!='RELEASE':continue
    need(len(d['cohorts'])==2 and all(c in released for c in d['cohorts']),'atomic conditional S/EP qualification')
    first=self.cells[d['cohorts'][0]]['point'];rp=C/'CONDITION_REVIEWS'/(d['stage']+'.json')
    if not rp.exists():
     proof={c:{k:r[k]for k in ['accepted_point_ref','archive_receipt_ref']if k in r}for c,r in rows.items()if r.get('state')=='CLOSED_ACCEPTED'}
     put(rp,dict(status='MAIN_REVIEWED_APPROVED_FAMILY_EXTENSION_CRITERION_PASS',approved_by='EP-MAIN',request_id=REQUESTS['service'],input_identity_sha256=first['input_identity_sha256'],family_stage=d['stage'],controller_manifest_ref=ref(self.manifest_path),stage_policy_ref=ref(P(__file__).with_name('performance_first_stage_policy.py')),authorization_ref=self.m['authorization_ref'],decision=d,accepted_evidence_refs=proof,reference_points=self.m.get('reference_points',{}),utc=now()))
    review=read(rp);need(review['status']=='MAIN_REVIEWED_APPROVED_FAMILY_EXTENSION_CRITERION_PASS'and review['family_stage']==d['stage']and review['request_id']==REQUESTS['service'],'existing criterion review drift')
    for c in d['cohorts']:
     p=self.bypoint[c];target=X/'service/control/conditional_release'/(c+'.json');value=dict(status='MAIN_RELEASED_APPROVED_CONDITIONAL_CELL',cohort=c,spec_sha256=p['spec_ref']['sha256'],request_id=REQUESTS['service'],family_stage=d['stage'],criterion_review_ref=ref(rp))
     if target.exists():need(read(target)==value,'immutable conditional cell binding drift')
     else:put(target,value)
  rd=decisions.get('retention:CONDITIONAL_GEMM')
  if rd and rd['status']=='RELEASE':
   with lock(C/'ADMISSION.lock'):
    ni_refs=[ref(C/'NI_RESULTS'/(cohort_for('PF_RET_fastWalshTransform_'+kind+'_ON')+'.json'))for kind in ['CLEAN_ONLY','DIRTY_ONLY']]
    views=[]
    for nr in ni_refs:
     n=exact(nr);need(n['schema']=='EP_MAIN_PF_RETENTION_MS_APPLICATION_NI_V1'and n['status']=='PASS_MS_ONLY_APPLICATION_NI','strict frozen MS-only NI receipt')
     need(n['input_identity_sha256']=='fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e','same exact FWT NI input')
     views.append(n)
    need({n['mode']for n in views}=={'WV_CLEAN_ONLY','WV_DIRTY_ONLY'},'both actual modes NI')
    baseline=self.reference_view(self.m['retention_WV_reference']);partial_refs=[];predicates=[];cycle_pass=False;victim_pass=False
    oldcycles=baseline['cycles'];oldreads=baseline.get('victim_read_responses');need(type(oldcycles)is int and oldcycles>0 and type(oldreads)is int and oldreads>=0,'retention criterion exact baseline cycle/Victim populations')
    source=baseline['source_identity']
    for kind in ['CLEAN_ONLY','DIRTY_ONLY']:
     co=cohort_for('PF_RET_fastWalshTransform_'+kind+'_ON');pv=self.accepted_view(rows[co]);need(pv.get('accepted_and_archived')and pv['source_identity']==source,'retention exact current partial Source')
     newcycles=pv['cycles'];newreads=pv.get('victim_read_responses');need(type(newcycles)is int and newcycles>0 and type(newreads)is int and newreads>=0,'retention criterion exact partial cycle/Victim populations')
     cp=newcycles*200<=oldcycles*199;vp=oldreads>0 and abs(newreads-oldreads)*10>=oldreads;cycle_pass|=cp;victim_pass|=vp;partial_refs.append(rows[co]['accepted_point_ref'])
     predicates.append(dict(cohort=co,mode=pv['mode'],partial_point_ref=rows[co]['accepted_point_ref'],old_WV_cycles=oldcycles,partial_cycles=newcycles,cycle_reduction_numerator=oldcycles-newcycles,cycle_reduction_denominator=oldcycles,cycle_reduction_fraction=(oldcycles-newcycles)/oldcycles,cycle_threshold='.005',cycle_predicate=cp,old_WV_Victim_read_responses=oldreads,partial_Victim_read_responses=newreads,Victim_absolute_change_numerator=abs(newreads-oldreads),Victim_change_denominator=oldreads,Victim_absolute_relative_change=abs(newreads-oldreads)/oldreads if oldreads>0 else None,Victim_threshold='.10',Victim_predicate=vp,population='SUM_EXACT64SLICE_FINAL_ACCEPTED_FULL_MECHANISM_VICTIM_READ_RESPONSES'))
    need(cycle_pass or victim_pass,'retention exact integer predicate not satisfied')
    criterion=dict(schema='EP_MAIN_PF_RETENTION_PERFORMANCE_CRITERION_V1',status='MAIN_REVIEWED_RETENTION_PERFORMANCE_CRITERION_PASS',approved_by='EP-MAIN',request_id=REQUESTS['retention'],criterion_satisfied=True,source_identity=source,input_identity_sha256='fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e',old_WV_point_ref=self.m['retention_WV_reference']['accepted_point_ref'],partial_point_refs=partial_refs,actual_predicates=predicates,cycle_predicate_any=cycle_pass,Victim_predicate_any=victim_pass,decision=rd,ni_comparison_refs=ni_refs,WV_reference=self.m['retention_WV_reference'],authorization_ref=self.m['authorization_ref'],controller_manifest_ref=ref(self.manifest_path))
    cr=C/'CONDITION_REVIEWS/RETENTION_GEMM.json'
    if not cr.exists():put(cr,criterion)
    else:need(read(cr)==criterion,'immutable retention criterion review drift')
    amendment=self.index.get('NI_amendment_authorization_ref');need(amendment is not None,'exact approved NI011 amendment required');exact(amendment)
    value=dict(schema='EP_MAIN_PF_RETENTION_GEMM_STAGE_RELEASE_V1',status='RELEASED_AFTER_FWT_TWO_MODE_MS_NI_PASS',approved_by='EP-MAIN',science_request_id=REQUESTS['retention'],ni_contract_amendment_authorization_ref=amendment,ni_comparison_refs=ni_refs,criterion_review_ref=ref(cr),sourcecriterion_review_ref=ref(cr),actual_criterion_review_ref=ref(cr),controller_manifest_ref=ref(self.manifest_path),authorization_ref=self.m['authorization_ref'])
    target=C/'STAGE_RELEASE_RETENTION_GEMM.json'
    if target.exists():need(read(target)==value,'immutable GEMM stage release drift')
    else:put(target,value)
  payload=dict(schema='EP_PERFORMANCE_FIRST_STAGE_RELEASES_V1',utc=now(),approved_by='EP-MAIN',manifest_ref=ref(self.manifest_path),authorization_ref=self.m['authorization_ref'],stage_policy_ref=ref(P(__file__).with_name('performance_first_stage_policy.py')),decisions=decisions,released_cohorts=sorted(released),NI_never_pruned_for_negative_performance=True)
  old=read(C/'STAGE_RELEASES.json')if(C/'STAGE_RELEASES.json').exists()else{}
  comparable=lambda z:{k:v for k,v in z.items()if k!='utc'}
  if comparable(old)!=comparable(payload):put(C/'STAGE_RELEASES.json',payload);self.event('FINITE_STAGE_DECISIONS_UPDATED',decisions={k:v['status']for k,v in decisions.items()})
  return payload
 def start(self,p):
  c=p['cohort'];g=p['group']
  if time.monotonic()<self.lastresource.get(c,0)+60:return False
  self.lastresource[c]=time.monotonic();cpu=self.available_cpu()
  if cpu is None:return False
  with lock(C/'ADMISSION.lock'):
   reg,rows=self.rows();need(c not in rows,'consumed point never relaunched');q=reg['registered_future_requests'].get(REQUESTS[g]);need(q is not None and q['admitted_specs'].get(c)==p['spec_ref']['sha256'],'current native registration required')
   others=0
   for qid,z in reg['registered_future_requests'].items():
    if qid in REQUESTS.values()or not qid.startswith('EP_'):continue
    cr=z.get('consumed',{});others+=sum(v.get('state')in ['CONSUMED_BEFORE_FORK','RUNNING']for v in cr.values())if isinstance(cr,dict)else 0
   if others+len(self.running)>=2:self.states[c]=dict(status='RESOURCE_HOLD_EP_GLOBAL_CAP2',utc=now());return False
   releases=read(C/'STAGE_RELEASES.json');need(c in releases['released_cohorts'],'conditional stage not released')
   self.claim(p,cpu);r=self.group_call(g,'from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);resource_gate(s,dispatch_binding(sys.argv[1]))',[c])
   if r.returncode:
    self.release_unconsumed_claim(p);msg=(r.stdout+r.stderr)[-8000:];resource='RESOURCE_ADMISSION_HOLD:'in msg;self.states[c]=dict(status='RESOURCE_ADMISSION_HOLD'if resource else'PRELAUNCH_QUALIFICATION_HOLD',terminal_hold=not resource,reason=msg,utc=now());self.event('ADMISSION_HOLD',cohort=c,resource_only=resource);return False
   path=C/'native_logs'/(c+'.'+str(uuid.uuid4())+'.run.log');path.parent.mkdir(exist_ok=True);f=path.open('xb')
   try:proc=self.native('run-native',c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   except BaseException:f.close();self.release_unconsumed_claim(p);raise
   self.running[c]=dict(process=proc,log=f,cpu=cpu,launcher=pid_identity(proc.pid),log_path=str(path),started_monotonic=time.monotonic());self.states[c]=dict(status='NATIVE_IN_PROGRESS',native_frontend_pid=proc.pid,cpu=cpu,utc=now());self.event('NATIVE_RUN_STARTED',cohort=c,pid=proc.pid,cpu=cpu);return True
 def poll(self):
  for c,v in list(self.running.items()):
   rc=v['process'].poll()
   if rc is None:continue
   _,rows=self.rows();p=self.bypoint[c]
   if c in rows:
    need(rows[c].get('done_ref')is not None,'consumed frontend gone without sealed DONE; no retry/model kill');exact(rows[c]['done_ref']);v['log'].close();self.running.pop(c);self.pending_accept.append(c);self.states[c]=dict(status='NATIVE_TERMINAL_PENDING_ACCEPT',returncode=rc,utc=now())
   else:
    v['log'].close();self.running.pop(c);self.release_unconsumed_claim(p);msg=P(v['log_path']).read_text(errors='replace')[-8000:];resource='RESOURCE_ADMISSION_HOLD:'in msg;self.states[c]=dict(status='PRECONSUME_RESOURCE_HOLD'if resource else'PRECONSUME_TECHNICAL_HOLD',terminal_hold=not resource,reason=msg,utc=now())
   self.event('NATIVE_FRONTEND_EXIT',cohort=c,returncode=rc,consumed=c in rows)
 def accept_one(self):
  with lock(J/'execution_v2_20261103_v1/control/GLOBAL_ACCEPT_AND_RESTORE_WINDOW.lock'):return super().accept_one()

 def summary(self):
  reg,rows=self.rows();out=[]
  for p in self.points:
   c=p['cohort'];cell=self.cells[c]['point'];row=rows.get(c,{});v=dict(cohort=c,group=p['group'],proposal_cell_id=p['proposal_cell_id'],mode=cell['mode'],purpose=cell['purpose'],stage=cell['stage'],observer_variant=cell.get('observer_variant','ON'),state=row.get('state',self.states.get(c,{}).get('status','NOT_STARTED')),consumed=c in rows,spec_ref=p.get('spec_ref'),input_identity_sha256=cell['input_identity_sha256'],source_identity=cell['source5'],controller_state=self.states.get(c))
   for k in ['accepted_point_ref','archive_receipt_ref','done_ref','validation_ref']:v[k]=row.get(k)
   if row.get('accepted_point_ref'):
    pt=exact(row['accepted_point_ref']);v.update({k:pt[k]for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']})
    try:v['mechanism_metrics_ref']=self.metrics(p,pt,row)
    except Exception as e:v['mechanism_metrics_analysis']=dict(status='UNKNOWN',reason=repr(e),scientific_run_affected=False)
   if row.get('done_ref'):
    d=exact(row['done_ref']);v.update({k:d.get(k)for k in ['elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason']})
   out.append(v)
  result=dict(schema='EP_PERFORMANCE_FIRST_FINITE_RESULTS_V1',utc=now(),session=self.session,points=out,budgets={g:{k:reg['registered_future_requests'].get(q,{}).get(k)for k in ['budget','remaining','state']}for g,q in REQUESTS.items()},active_native_frontends=len(self.running),maximum_concurrency=2,new_model_start_ceiling=24,automatic_retry=False,Source_keep=True,combined_GM=False,numeric_output='UNKNOWN',stage_releases_ref=ref(C/'STAGE_RELEASES.json')if(C/'STAGE_RELEASES.json').exists()else None,retention_NI='MODE_SPECIFIC_NOT_INHERITED',formal_point_qualification='SEPARATE_FROM_ACCEPTANCE')
  put(C/'RESULTS_CURRENT.json',result)
  with(C/'RESULTS_CURRENT.csv').open('w',newline='')as f:
   cols=['cohort','group','mode','purpose','stage','observer_variant','state','consumed','cycles','instructions','CTA','kernel_count','hardware_drained','elapsed_seconds','peak_process_tree_RSS_bytes','peak_hot_bytes','stop_reason'];w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(out)
  return result
 def publish(self,final=False):
  p=self.m['publication'];repo=P(p['repo']);rel=p['relative_directory'];dst=repo/rel
  with lock(C/'MAIN_GIT_PUBLICATION.lock'):
   need(subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip()==p['branch'],'sole Main branch drift');need(not subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).strip(),'foreign staged Git work')
   dst.mkdir(parents=True,exist_ok=True)
   for name in ['RESULTS_CURRENT.json','RESULTS_CURRENT.csv','STAGE_RELEASES.json']:
    if(C/name).exists():shutil.copy2(C/name,dst/name)
   for sub in ['NI_RESULTS','MECHANISM_METRICS']:
    (dst/sub).mkdir(exist_ok=True)
    for f in(C/sub).glob('*.json'):need(f.stat().st_size<=16*M,'small summary bound');shutil.copy2(f,dst/sub/f.name)
   put(dst/'EXECUTION_SCOPE.json',dict(manifest_ref=ref(self.manifest_path),authorization_ref=self.m['authorization_ref'],maxstarts=24,first10=10,conditional14=14,no_global_research_cap=True,final=final,utc=now()))
   subprocess.run(['git','-C',str(repo),'add','--sparse','--',rel],check=True);subprocess.run(['git','-C',str(repo),'add','--sparse','-f','--',str(P(rel)/'RESULTS_CURRENT.csv')],check=True)
   changed=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();need(all(x.startswith(rel+'/')for x in changed),'publication path escape')
   if changed:subprocess.run(['git','-C',str(repo),'commit','-m','EP performance-first '+('finite result closure'if final else'accepted performance progress')],check=True)
   subprocess.run(['git','-C',str(repo),'push','origin',p['branch']],check=True);head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','origin','refs/heads/'+p['branch']],text=True).split()[0];need(head==remote,'remote readback mismatch');put(C/'REMOTE_PUBLICATION_RECEIPT.json',dict(utc=now(),HEAD=head,remote_HEAD=remote,final=final));self.lastpublish=time.monotonic()
 def run(self):
  self.check_activation()
  with lock(C/'FINITE_MAIN_EXECUTOR.lock',True),lock(J/'execution_v2_20261103_v1/control/GLOBAL_MAIN_SUCCESSOR_OWNERSHIP.lock',True):
   need(not(C/'EXECUTOR_STARTED.json').exists(),'no automatic controller resume');put(C/'EXECUTOR_STARTED.json',dict(utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),automatic_resume=False));self.event('SOLE_MAIN_CONTROLLER_STARTED')
   while True:
    try:
     self.poll();self.accept_one();reg,rows=self.rows();self.refresh_qualifications(rows);self.ni(rows);release=self.stage_decisions(rows)
    except Exception as e:self.event('OPERATIONAL_REVIEW_HOLD_NO_MODEL_KILL',reason=repr(e));time.sleep(10);continue
    for p in self.points:
     c=p['cohort'];d=release['decisions'][p['group']+':'+self.cells[c]['point']['stage']]
     if c in rows or c in self.running:continue
     if not p.get('spec_ref'):self.states[c]=dict(status='QUALIFICATION_HOLD_NOT_CONSUMED',utc=now());continue
     if d['status']=='PRUNE':self.states[c]=dict(status='PRUNED_NOT_CONSUMED',terminal_hold=True,reason=d['reason'],utc=now());continue
     if d['status']=='HOLD':self.states[c]=dict(status='CONDITIONAL_SCIENTIFIC_REVIEW_HOLD',terminal_hold=d['reason']in ['PREVIOUS_PAIR_FAILED_NO_RETRY_OR_REFUND','FWT_PRIMARY_OR_NI_EXECUTION_FAILED'],reason=d['reason'],utc=now());continue
     if d['status']!='RELEASE' or self.states.get(c,{}).get('terminal_hold'):continue
     if len(self.running)>=2:break
     try:self.start(p)
     except Exception as e:self.states[c]=dict(status='PRELAUNCH_QUALIFICATION_HOLD_NOT_RETRIED',terminal_hold=True,reason=repr(e),utc=now());self.event('PRELAUNCH_QUALIFICATION_HOLD',cohort=c,reason=repr(e))
    try:self.summary()
    except Exception as e:self.event('SMALL_SUMMARY_HOLD_NO_MODEL_KILL',reason=repr(e))
    if time.monotonic()-self.lastpublish>=1800:
     try:self.publish()
     except Exception as e:self.event('PUBLICATION_HOLD',reason=repr(e))
    settled=all(rows.get(p['cohort'],{}).get('state')in TERMINAL or self.states.get(p['cohort'],{}).get('terminal_hold')for p in self.points)
    if settled and not self.running and not self.pending_accept:break
    if time.monotonic()-self.started>self.m.get('admission_wait_and_execution_wall_seconds',7*86400):
     self.event('FINITE_WALL_REVIEW_HOLD_NEVER_KILL_LIVE_MODEL')
     if not self.running:break
    time.sleep(10)
   self.summary()
   try:self.archive_summary()
   except Exception as e:self.event('SUMMARY_ARCHIVE_HOLD',reason=repr(e))
   try:self.publish(final=True)
   except Exception as e:self.event('FINAL_PUBLICATION_HOLD',reason=repr(e))
   _,rows=self.rows();put(C/'EXECUTOR_FINISHED.json',dict(utc=now(),session=self.session,status='FINITE_APPROVED_SCOPE_TERMINAL_OR_REVIEW_HOLD',all24_consumed=len(rows)==24,accepted=sum(r.get('state')=='CLOSED_ACCEPTED'for r in rows.values()),unaccepted=sum(r.get('state')=='CLOSED_UNACCEPTED'for r in rows.values()),pruned_or_HOLD=[c for c,s in self.states.items()if c not in rows and s.get('terminal_hold')],all_consumed_terminal=all(r['state']in TERMINAL for r in rows.values()),automatic_retry=False,refund=False))

def main(argv=None):
 ap=argparse.ArgumentParser(description='Default passive prepare; no scheduler started without --run and Main activation');ap.add_argument('--manifest',required=True);z=ap.add_mutually_exclusive_group();z.add_argument('--prepare',action='store_true');z.add_argument('--run',action='store_true');args=ap.parse_args(argv)
 if args.run:Executor(args.manifest).run()
 else:print(json.dumps(safe_prepare(args.manifest),sort_keys=True))
if __name__=='__main__':
 try:main()
 except BaseException as e:print(json.dumps(dict(status='PASSIVE_OR_MAIN_REVIEW_HOLD',reason=repr(e),automatic_retry=False)),file=sys.stderr);raise
