import pathlib as P, json, hashlib, copy, importlib.util, tempfile, types, threading, fcntl, os, traceback, datetime
A=P.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
SRC=A/'agents/B/cpu_shared_stage2_main_handoff_v1/main_handoff.py'
SHA='06aee02a8a6476c4ea071063b5aa9cfb989ca7ec149b86093d7e62a904dd2118'
OUT=A/'agents/A/cpu_shared_stage2_main_handoff_qualification_v1'
OUT.mkdir(exist_ok=True,parents=True)
def sha(p):return hashlib.sha256(P.Path(p).read_bytes()).hexdigest()
assert sha(SRC)==SHA
spec=importlib.util.spec_from_file_location('private_stage2_qualification',SRC);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BASE=P.Path(tempfile.mkdtemp(prefix='PRIVATE_MAIN2_',dir=OUT))
S=types.SimpleNamespace
results=[]
def put(p,o):p=P.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,sort_keys=True,indent=2)+'\n')
def check(name,fn):
 try:details=fn();results.append(dict(name=name,status='PASS',details=details))
 except BaseException as e:results.append(dict(name=name,status='FAIL',error=repr(e),traceback=traceback.format_exc()))
def fixture(tag,fail=None):
 root=BASE/tag;root.mkdir();m.R=root
 for d in ['control/specs','control/qualification_ledger']: (root/d).mkdir(parents=True,exist_ok=True)
 put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 put(root/'control/MATRIX_CURRENT.json',{'fixture':True});put(root/'control/SCOPE.json',{'fixture':True})
 q=dict(budget=360,remaining=29,admitted_specs={},consumed={m.FIRST:{'uuid':'2d24a1be-db7b-4100-9752-42b16ea46035','execution_receipt':{'fixture':True}}},sealed=[],additional_operational_overlays={})
 for i in range(330):q['consumed']['OLD_'+str(i)]={'uuid':'old-uuid-'+str(i)}
 for c in m.FOUR:
  x=dict(cohort=c,host_cpu=None,scientific_role='ENGINEERING_OBSERVATION_CANARY',fixture_science='UNCHANGED')
  p=root/'control/specs'/(c+'.json');put(p,x);(root/'control'/(c+'_SPEC.json')).write_bytes(p.read_bytes());q['admitted_specs'][c]=sha(p)
 for k in [m.RESOURCE_ID,m.OBSERVATION_ID]:q['additional_operational_overlays'][k]={'schema':k,'generation':'OLD','status':'ACTIVE','provenance_extra':{'preserve':True}}
 reg={'registered_future_requests':{'PRIVATE_REQUEST':q},'other_authority':{'preserve':True}}
 trace=[];inside=[False];engine=S(REQ='PRIVATE_REQUEST')
 def registered():
  assert not inside[0],'AUTHORITY_REENTRY_IN_EX';return (None,None,copy.deepcopy(q))
 engine.registered=registered;engine.assert_parent_lease=lambda:trace.append('LEASE_STANDIN')
 lock=root/'PRIVATE_REGISTRY_UPDATE.lock';lock.touch()
 def update(fn):
  # Simulates a benign actual receipt committed since the caller snapshot.
  q['consumed']['OLD_0']['concurrent_receipt']='PRESERVE_THIS_NEW_RECEIPT'
  with lock.open('r+')as ex:
   fcntl.flock(ex,fcntl.LOCK_EX);inside[0]=True
   try:
    with lock.open('r')as sh:
     try:fcntl.flock(sh,fcntl.LOCK_SH|fcntl.LOCK_NB)
     except BlockingIOError:trace.append('INDEPENDENT_FD_SH_CORRECTLY_BLOCKED')
     else:raise AssertionError('REAL_EX_NOT_EXCLUSIVE')
    fn(reg);trace.append('CAS')
   finally:inside[0]=False;fcntl.flock(ex,fcntl.LOCK_UN)
 engine.update_authority=update
 orig_worker=lambda c:('ORIGINAL_WORKER',c)
 orig_choose=lambda pending,*a,**kw:('ORIGINAL_CHOOSE',[s['cohort']for s in pending],a,kw)
 orig_safe=lambda *a:('ORIGINAL_SAFE',a)
 callbacks=tuple((lambda *a,i=i:i)for i in range(4))
 consumer=S(safe_finish=object(),**dict(zip(['load','finish_evidence','put','archive_closed'],callbacks)))
 frame=S(f_locals=dict(res=None,consumer=consumer,pool=object(),claims={},running={},post=object(),registry=object()),f_globals={})
 aging=S(lock=threading.RLock());res=S(DTC_LARGE_JOB_AGING_INSTALLED=aging);frame.f_locals['res']=res
 memory={'aging':aging,'context':{'cfg':{'OLD_CPU2_CONTEXT':'UNCHANGED'}}}
 main=S(DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1=memory)
 owner_marker='PRIVATE_B_DISPATCH'
 def readiness(pending,*a,**kw):return orig_choose([s for s in pending if s['cohort']not in m.FOUR],*a,**kw)
 oldfence=lambda c:('OLD_FENCE',c)
 oldwrap=lambda c:('OLD_B_WRAPPER',c)
 oldchoose=lambda *a,**kw:('OLD_B_CHOOSE',a,kw)
 frame.f_globals['worker']=oldwrap;res.choose_dispatch=oldchoose
 setattr(main,owner_marker,dict(wrapper=oldwrap,chooser=oldchoose,previous_choose=readiness))
 old=dict(frame=frame,engine=engine,memory=memory,aging=aging,phase='ARMED_ACKED',readiness_choose=readiness,fence=oldfence,originals=dict(worker=orig_worker,choose=orig_choose,safe_finish=orig_safe,callbacks=callbacks))
 def maybe(stage):
  if fail==stage:raise SystemExit('PRIVATE_INJECTED_'+stage)
 def restoreB(main):
  assert res.choose_dispatch is oldchoose and consumer.safe_finish is not orig_safe
  trace.append('B1_RESTORE');frame.f_globals['worker']=oldfence;res.choose_dispatch=readiness;delattr(main,owner_marker);maybe('B1');return {'fixture':'B1'}
 def restoreE(lease,main):
  assert res.choose_dispatch is readiness and frame.f_globals['worker']is oldfence
  trace.append('E1_RESTORE_MASK_PRESERVED');consumer.safe_finish=orig_safe;maybe('E1');return {'fixture':'E1'}
 old['modules']={'producer':S(restore_owner_dispatch=restoreB),'consumer':S(restore_in_owner=restoreE)}
 setattr(main,m.OLD_MARKER,old)
 def record_rc(cfg):return {'schema':m.RESOURCE_ID,'generation':'NEW','config_sha':m.digest(cfg)}
 def record_oc(cfg):return {'schema':m.OBSERVATION_ID,'generation':'NEW','config_sha':m.digest(cfg)}
 lib=S(ID=m.RESOURCE_ID,record=record_rc,validate=lambda cfg,q:None)
 def installE(frame,*a,**kw):
  assert frame.f_globals['worker'](m.FOUR[1])['state']=='ZERO_START_DEFERRED'
  assert res.choose_dispatch([{'cohort':c}for c in m.FOUR]+[{'cohort':'PRIMARY'}])[1]==['PRIMARY']
  trace.append('E2_INSTALL_CLOSED');consumer.safe_finish='NEW_MANDATORY_CONSUMER';maybe('E2');return {'fixture':'E2'}
 def installB(frame,*a,armed,**kw):
  assert armed is False and consumer.safe_finish=='NEW_MANDATORY_CONSUMER'
  trace.append('B2_INSTALL_UNARMED');previous=frame.f_globals['worker'];previouschoose=res.choose_dispatch
  frame.f_globals['worker']=lambda c:previous(c)
  res.choose_dispatch=lambda p,*a,**k:previouschoose(p,*a,**k)
  maybe('B2');return {'armed':False,'fixture':True}
 def arm(main):trace.append('ARM');maybe('ARM');return {'armed':True,'fixture':True}
 producer=S(ID=m.OBSERVATION_ID,OWNER_MARKER=owner_marker,record=record_oc,validate=lambda cfg,q:None,verify_engineering_spec=lambda *a:None,install_owner_dispatch=installB,arm_owner_dispatch=arm)
 bridge=S(install_on_frame=installE,consumer_check=lambda *a:True)
 modulefiles={}
 for name in ['library','producer','consumer','other_role']:
  p=root/(name+'_STANDIN.py');p.write_text('# Explicit private controlflow stand-in, not actual B/E execution\n');modulefiles[name]=str(p)
 oldcfg={'source_paths':{'old_library':str(root/'oldsource.py')},'qualified_sources':{}}
 (root/'oldsource.py').write_text('# private oldsource\n');oldcfg['qualified_sources']['old_library']=sha(root/'oldsource.py')
 put(root/'old_resource.json',oldcfg);put(root/'old_observation.json',oldcfg)
 put(root/'old_Main1.json',dict(resource_configuration_path=str(root/'old_resource.json'),observation_configuration_path=str(root/'old_observation.json')));old['config_path']=str(root/'old_Main1.json')
 rcfg=dict(allowed_cohorts=list(m.FOUR),max_shared_running=1,qualification_stage='AFTER_NATURAL_SHARED_CANARY',qualification_only=False,source_paths={'library':modulefiles['library']},qualified_sources={'library':sha(modulefiles['library'])})
 put(root/'resource.json',rcfg)
 ocfg=dict(modes={c:'BPF_REQUIRED'if'-OBSBPF-'in c else'DEFAULT_CONTROL'for c in m.FOUR},future_primary_policy='NONE',qualification_only=False,resource_configuration_sha256=sha(root/'resource.json'),source_paths={k:modulefiles[k]for k in ['producer','consumer']},qualified_sources={k:sha(modulefiles[k])for k in ['producer','consumer']})
 put(root/'observation.json',ocfg);put(root/'CPU2_ACTIVE.json',{'OLD_CPU2':'UNCHANGED'})
 main1=A/'coordinator/CPU_SHARED_MAIN_INSTALL_CANDIDATE_V1/main_install.py'
 assert sha(main1)==m.MAIN1_SHA
 paths=[str(SRC),str(main1)]+[modulefiles[k]for k in ['library','producer','consumer']]
 cfg=dict(schema='MAIN_CPU_SHARED_STAGE2_HANDOFF_CONFIG_V1',root=str(root),installer_path=str(SRC),installer_sha256=SHA,Main1_source_path=str(main1),Main1_source_sha256=m.MAIN1_SHA,source_pins={p:sha(p)for p in paths},modules={k:modulefiles[k]for k in ['library','producer','consumer']},resource_configuration_path=str(root/'resource.json'),observation_configuration_path=str(root/'observation.json'),expected_frame_object_ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']},directory=str(root/'artifacts'),old_memory_active_path=str(root/'CPU2_ACTIVE.json'),matrix_sha256=sha(root/'control/MATRIX_CURRENT.json'),scope_sha256=sha(root/'control/SCOPE.json'),old_memory_active_sha256=sha(root/'CPU2_ACTIVE.json'),exclusion_contract_path='PRIVATE_STANDIN',exclusion_contract_sha256='PRIVATE_STANDIN',owner={'qualification_only_standin':True})
 put(root/'config.json',cfg)
 modules={'library':lib,'producer':producer,'consumer':bridge}
 def loader(n,p):
  if n=='main_stage2_exact_Main1_owner_discovery':return S(actual_owner=lambda cfg:(main,frame,engine))
  return modules[n.removeprefix('main_stage2_')]
 m.load=loader
 return S(root=root,q=q,reg=reg,trace=trace,engine=engine,frame=frame,res=res,main=main,old=old,cfg=cfg,consumer=consumer,record=copy.deepcopy(q['additional_operational_overlays']),run=lambda:m.apply(root/'config.json'))

def full_success():
 f=fixture('success');before=copy.deepcopy(f.q);r=f.run();assert r['status']=='ARMED_SAME_OWNER_NOT_SIMULATION_ACCEPTANCE',r
 seq=[x for x in f.trace if x!='LEASE_STANDIN'];assert seq==['B1_RESTORE','E1_RESTORE_MASK_PRESERVED','INDEPENDENT_FD_SH_CORRECTLY_BLOCKED','CAS','E2_INSTALL_CLOSED','B2_INSTALL_UNARMED','ARM'],seq
 assert r['scope']==list(m.FOUR[1:])and r['already_consumed_preserved'][m.FIRST]==before['consumed'][m.FIRST]['uuid']
 expected=copy.deepcopy(before);expected['additional_operational_overlays']=f.q['additional_operational_overlays'];expected['consumed']['OLD_0']['concurrent_receipt']='PRESERVE_THIS_NEW_RECEIPT';assert f.q==expected
 for k,row in f.q['additional_operational_overlays'].items():assert row['provenance_extra']=={'preserve':True}and row['operational_generation_history']
 assert json.loads((f.root/'artifacts/OLD_OPERATIONAL_RECORDS.json').read_text())==f.record
 return dict(sequence=seq,source='actual_apply_controlflow',external_modules='EXPLICIT_STANDINS',C0_not_resubmitted=True,independent_FD_EX=True,budget_UUIDs_preserved=True,concurrent_receipt_preserved=True)
check('actual_apply_order_exact_CAS_preimages_and_no_reentry',full_success)

def cas_negatives():
 kinds=['row_conflict','alias_drift','prepared_canonical_drift','UUID_drift','scope_spent','persistent_claim']
 for k in kinds:
  f=fixture('negative_'+k);q=f.q;scope=m.fresh_scope(q);canon={c:q['admitted_specs'][c]for c in scope};old=copy.deepcopy(f.record);uu={c:r['uuid']for c,r in q['consumed'].items()};new={key:{'new':True}for key in old}
  if k=='row_conflict':q['additional_operational_overlays'][m.RESOURCE_ID]['changed']=True
  if k=='alias_drift':(f.root/'control'/(scope[0]+'_SPEC.json')).write_text('{}')
  if k=='prepared_canonical_drift':canon[scope[0]]='0'*64
  if k=='UUID_drift':q['consumed'][m.FIRST]['uuid']='changed'
  if k=='scope_spent':q['consumed'][scope[0]]={'uuid':'newborn'};q['remaining']-=1
  if k=='persistent_claim':put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{scope[0]:{'fixture':True}}})
  before=copy.deepcopy(f.reg)
  try:m.replace_records_locked(f.reg,f.engine.REQ,old,new,f.root,scope,canon,360,uu)
  except AssertionError:pass
  else:raise AssertionError('NEGATIVE_ACCEPTED '+k)
  assert f.reg==before
 return dict(rejected_before_mutation=kinds)
check('CAS_conflicts_alias_currentcanonical_UUID_scope_claim',cas_negatives)

def phases():
 out=[]
 for phase in ['B1','E1','E2','B2','ARM']:
  f=fixture('failure_'+phase,phase);r=f.run();assert r['status']=='STAGE2_HANDOFF_HOLD_PRESERVE'and r['ever_exposed']
  state=getattr(f.main,m.MARKER)
  assert f.frame.f_globals['worker'](m.FIRST)['state']=='SPENT_ENGINEERING_PRESERVE'
  unused=f.frame.f_globals['worker'](m.FOUR[1]);assert unused['state']=='ZERO_START_DEFERRED'and unused['model_starts']==0
  f.engine.registered=lambda:(_ for _ in ()).throw(SystemExit('PRIVATE_UNKNOWN'))
  unknown=f.frame.f_globals['worker'](m.FOUR[1]);assert unknown['state']=='ENGINEERING_PRESERVE'and'model_starts'not in unknown
  expected_worker=('OLD_FENCE','PRIMARY')if phase in ['B1','E1']else('ORIGINAL_WORKER','PRIMARY')
  assert f.frame.f_globals['worker']('PRIMARY')==expected_worker
  if phase in ['E2','B2','ARM']:assert f.consumer.safe_finish=='NEW_MANDATORY_CONSUMER'
  assert f.res.choose_dispatch([{'cohort':c}for c in m.FOUR]+[{'cohort':'PRIMARY'}],7,flag=8)[1]==['PRIMARY']
  assert f.q['budget']==360 and len(f.q['consumed'])==331
  out.append(dict(phase=phase,typed_unused_spent_unknown=True,mandatory_consumer_retained=True,no_worker_invoked_by_apply=True))
 return out
check('exposed_BaseException_failure_containment_five_boundaries',phases)

def guards():
 out=[]
 for kind in ['module_source_join','old_generation_source_drift','initial_source_pin_drift']:
  f=fixture('guard_'+kind)
  if kind=='module_source_join':f.cfg['modules']['library']=str(f.root/'other_role_STANDIN.py');put(f.root/'config.json',f.cfg)
  if kind=='old_generation_source_drift':(f.root/'oldsource.py').write_text('# DRIFT\n')
  if kind=='initial_source_pin_drift':f.cfg['source_pins'][str(SRC)]='0'*64;put(f.root/'config.json',f.cfg)
  before=copy.deepcopy(f.reg)
  try:r=f.run();assert r['status']=='STAGE2_HANDOFF_HOLD_PRESERVE'and not r['ever_exposed']
  except AssertionError:
   assert kind=='initial_source_pin_drift'
  assert f.reg==before and 'B1_RESTORE'not in f.trace
  out.append(kind)
 return dict(final_06aee_preload_guard_cases=out,mutation_or_route_exposure=False)
check('new_06aee_source_join_and_old_generation_drift_guards',guards)

assert sha(SRC)==SHA
receipt=dict(schema='CPU_SHARED_STAGE2_MAIN_HANDOFF_PRIVATE_COMPONENT_QUALIFICATION_V1',status='PASS'if all(r['status']=='PASS'for r in results)else'FAIL',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_path=str(SRC),source_sha256=SHA,driver_path=__file__,driver_sha256=sha(__file__),fixture_path=str(BASE),cases=results,coverage=dict(actual_main_handoff_source_functions=True,actual_apply_controlflow=True,independent_FD_EX=True,owner_lease_B_E_library_validators='EXPLICIT_PRIVATE_STANDINS_NOT_ACTUAL_MAIN_OR_B_E_QUALIFICATION',actual_models_started=0,production_authority_mutations=0,signals=0,new_grants=0,old_suite_rerun=False),limitations=['No actual owner/lease/install or scientific simulation','Private module contracts test source-join logic, not final production configuration readiness','B/E own prefix/consumer qualifications remain separate required evidence'])
put(OUT/'CPU_QUALIFICATION.json',receipt)
put(OUT/'MANIFEST.json',dict(source_path=str(SRC),source_sha256=SHA,qualification_path=str(OUT/'CPU_QUALIFICATION.json'),qualification_sha256=sha(OUT/'CPU_QUALIFICATION.json'),driver_path=__file__,driver_sha256=sha(__file__),production_actions=0))
print(json.dumps(dict(status=receipt['status'],qualification_path=str(OUT/'CPU_QUALIFICATION.json'),qualification_sha256=sha(OUT/'CPU_QUALIFICATION.json'),manifest_sha256=sha(OUT/'MANIFEST.json'),cases=[(r['name'],r['status'],r.get('error'))for r in results]),indent=2))
