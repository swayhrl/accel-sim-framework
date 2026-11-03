"""Bounded private CPU controls. No registry/native/model/Git writes."""
import pathlib,importlib.util,json,copy,hashlib,tempfile,types,os
D=pathlib.Path(__file__).parent
p=D/'finite_stencil_successor.py';sp=importlib.util.spec_from_file_location('candidate_successor',p);x=importlib.util.module_from_spec(sp);sp.loader.exec_module(x)
rp=D/'stage2_resources_stencil.py';sp=importlib.util.spec_from_file_location('candidate_resources',rp);r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
results=[]
def run(name,fn,negative=False):
 try:
  fn()
  if negative:raise AssertionError('negative control unexpectedly passed')
 except (RuntimeError,ValueError,KeyError)as e:
  if not negative:raise
 results.append(dict(test=name,status='PASS',expected_rejection=negative))
run('handoff_waits_missing_finish',lambda:x.need(x.handoff_status({},None,False)=='WAIT_PRIOR_FINISHED','handoff'))
run('handoff_holds_nonterminal_prior',lambda:x.need(x.handoff_status({},dict(all_eight_terminal=False),False)=='HOLD_PRIOR_SCOPE_NOT_TERMINAL','handoff'))
run('handoff_waits_live_prior_generation',lambda:x.need(x.handoff_status({},dict(all_eight_terminal=True),True)=='WAIT_PRIOR_PID_GENERATION_GONE','handoff'))
run('handoff_allterminal_dead_generation_ready',lambda:x.need(x.handoff_status({},dict(all_eight_terminal=True),False)=='READY','handoff'))
run('dead_generation_does_not_signal',lambda:x.need(not x.same_live(dict(pid=999999999,start_ticks=1)),'generation'))
run('actual_own_generation_live',lambda:x.need(x.same_live(x.pid_identity(os.getpid())),'generation'))
source=dict(core_source_commit='78f4b59e865b136eede74df74c44c210f5b4ca04',binary_sha256='78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a')
objects={}
for c,mode in [('EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY','W_ONLY'),('EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO','WV_ZERO_RO')]:objects[c]=dict(cohort=c,mode=mode,science_request_id=x.REQUEST,source_identity=source,input_identity_sha256='bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146')
objects['authorization']=dict(approved_by='EP-MAIN')
original_exact=x.exact;original_sha=x.sha
x.exact=lambda rr:copy.deepcopy(objects[rr['id']]);x.sha=lambda p:'same'
points=[dict(cohort=c,group='stencil',science_request_id=x.REQUEST,spec_ref=dict(path=str(x.H/'stencil/cases'/c/'control/FROZEN_SPEC.json'),sha256='same',id=c))for c in ['EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY','EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO']]
m=dict(schema='EP_MAIN_STENCIL_EXACT_EXECUTION_MANIFEST_V1',status='MAIN_AUTHORIZED_EXACT_TWO_STENCIL_NATIVE_STARTS',root=str(x.H),max_concurrent_models=2,new_model_start_ceiling=2,automatic_retry=False,points=points,authorization_ref=dict(id='authorization'),native_entry_ref=dict(path='private',sha256='same'),publication=dict(repo=str(x.BASE_REPO),relative_directory='docs/test/execution_stencil_wv_20261103_v1'))
run('exact_two_modes_manifest_pass',lambda:x.validate_manifest(m))
for name,key,val in [('ceiling3_reject','new_model_start_ceiling',3),('concurrency3_reject','max_concurrent_models',3),('retry_true_reject','automatic_retry',True)]:
 bad=copy.deepcopy(m);bad[key]=val;run(name,lambda bad=bad:x.validate_manifest(bad),True)
bad=copy.deepcopy(m);bad['points'][0]['science_request_id']='foreign';run('foreign_request_reject',lambda:x.validate_manifest(bad),True)
bad=copy.deepcopy(m);bad['publication']['relative_directory']='../../foreign';run('publication_escape_reject',lambda:x.validate_manifest(bad),True)
objects['EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO']['mode']='F';run('unapproved_F_mode_reject',lambda:x.validate_manifest(m),True);objects['EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO']['mode']='WV_ZERO_RO'
objects['EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO']['input_identity_sha256']='other';run('input_mismatch_reject',lambda:x.validate_manifest(m),True);objects['EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO']['input_identity_sha256']='bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146'
run('zero_prestarted_no_receipt_pass',lambda:x.need(x.adoption_check(m,{},dict())is None,'zero adopt'))
run('prestarted_without_Main_review_reject',lambda:x.adoption_check(m,{},dict(EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY=dict(state='RUNNING'))),True)
run('two_prestarted_reject',lambda:x.adoption_check(m,{},dict(EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY={},EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO={})),True)
v=dict(schema='EP_MAIN_STENCIL_PRESTARTED_NATIVE_ADOPTION_V1',status='MAIN_REVIEWED_SINGLE_CONSUMED_NATIVE_FRONTEND_FOR_SUCCESSOR_ADOPTION',approved_by='EP-MAIN',cohort='EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY',science_request_id=x.REQUEST,spec_ref=points[0]['spec_ref'],native_run_admission_receipt_ref=dict(id='authorization'),automatic_retry=False,never_reconsume=True,native_frontend_generation=dict(pid=100,start_ticks=1000),model_generation=dict(pid=101,start_ticks=1001));objects['adoption']=v;a=dict(prestarted_adoption_ref=dict(id='adoption'))
run('one_prestarted_exact_receipt_pass',lambda:x.adoption_check(m,a,dict(EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY=dict(state='RUNNING'))))
objects['adoption']['never_reconsume']=False;run('adoption_reconsume_reject',lambda:x.adoption_check(m,a,dict(EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY=dict(state='RUNNING'))),True);objects['adoption']['never_reconsume']=True
x.exact=original_exact;x.sha=original_sha
run('three_peer_scopes_mapped',lambda:x.need(len(r.SCOPES)==3 and x.REQUEST in r.SCOPES,'scope count'))
run('one_GiB_only_emergency_floor',lambda:x.need(r.DEFAULT_POLICY['native_safety_floor_bytes']==1<<30,'floor'))
# Empty test scope is pure read-only; no active foreign commitments erased.
fake=types.SimpleNamespace(process=lambda *a:dict(live=False,RSS_bytes=0,PSS_bytes=0),owner_growth=lambda q,e,h,rss:max(0,e-rss))
with tempfile.TemporaryDirectory(prefix='cpu_scope_',dir=D)as td:
 f=r.fresh_scope('test',dict(consumed={},admitted_specs={},reserved_write_bytes=0),pathlib.Path(td),fake)
 run('empty_scope_no_future_doublecharge',lambda:x.need(f['ram']==[]and f['writes']==[]and not f['errors'],'empty'))
 q=dict(consumed={'unexpected':dict(state='RUNNING')},admitted_specs={},reserved_write_bytes=0)
 f=r.fresh_scope('test',q,pathlib.Path(td),fake)
 run('unresolved_consumed_without_claim_reject',lambda:x.need(bool(f['errors']),'unresolved claim not caught'))
receipt=dict(schema='EP_MAIN_STENCIL_SUCCESSOR_PRIVATE_CPU_CONTROLS_V1',status='PASS',tests=results,count=len(results),actual_science_starts=0,registry_writes=0,native_entry_writes=0,Git_writes=0,production_models_affected=False,code_ref=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),resource_candidate_ref=dict(path=str(rp),sha256=hashlib.sha256(rp.read_bytes()).hexdigest()))
(D/'CPU_CONTROLS_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status='PASS',count=len(results),science_starts=0)))
