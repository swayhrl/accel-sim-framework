"""Main3 pure locked transaction delta. Never calls apply or actual owner."""
import pathlib as P,json,hashlib,copy,ast,tempfile,importlib.util,fcntl,traceback,datetime
A=P.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=A/'agents/A/broad_Main3_qualification_v1';D.mkdir(exist_ok=True)
SRC=A/'coordinator/BROAD_SHARED_CPU_MAIN3_SOURCE_V1/main_install.py'
def sha(p):return hashlib.sha256(P.Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(P.Path(p).read_bytes())
def put(p,v):p=P.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
source_sha=sha(SRC);s=importlib.util.spec_from_file_location('Main3_private_pure',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
root=P.Path(tempfile.mkdtemp(prefix='PRIVATE_MAIN3_',dir=D));actualq=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];scope=read(A/'coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json')
REQ=actualq['request'];checks=[]
def fixture(tag):
 r=root/tag;r.mkdir();q=copy.deepcopy(actualq);reg={'registered_future_requests':{REQ:q},'unrelated_authority':{'preserve':'EXACT'}}
 for row in scope['rows']:
  c=row['cohort']
  for rel in ['control/specs/'+c+'.json','control/'+c+'_SPEC.json']:
   p=r/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/rel).read_bytes())
 put(r/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 before=dict(budget=q['budget'],remaining=q['remaining'],consumed=copy.deepcopy(q['consumed']),operational_records=copy.deepcopy(q['additional_operational_overlays']))
 canonical=m.check_unused(r,q,scope);records={k:dict(schema=k,status='ACTIVE',private_qualification_only=True)for k in [m.RESOURCE_ID,m.OBSERVER_ID]}
 return r,q,reg,before,canonical,records
def check(name,fn):
 try:details=fn();checks.append(dict(name=name,status='PASS',details=details))
 except BaseException as e:checks.append(dict(name=name,status='FAIL',error=repr(e),traceback=traceback.format_exc()))
def locked_call(r,q,reg,before,canonical,records):
 path=r/'PRIVATE_REGISTRY_UPDATE.lock';path.touch();blocked=False
 with path.open('r+')as a:
  fcntl.flock(a,fcntl.LOCK_EX)
  try:
   with path.open('r')as b:
    try:fcntl.flock(b,fcntl.LOCK_SH|fcntl.LOCK_NB)
    except BlockingIOError:blocked=True
    else:raise AssertionError('SECOND_FD_SHARED_LOCK_NOT_BLOCKED')
   # Trap any accidental lookup of engine/authority, without taking a lock.
   m.engine=m.registered=m.authority=lambda *a:(_ for _ in ()).throw(AssertionError('ENGINE_AUTHORITY_REENTRY'))
   m.append_records_locked(reg,REQ,records,r,scope,canonical,before)
  finally:fcntl.flock(a,fcntl.LOCK_UN)
 assert blocked
def positive():
 r,q,reg,before,canonical,records=fixture('positive');old=copy.deepcopy(reg);locked_call(r,q,reg,before,canonical,records)
 expected=copy.deepcopy(old);expected['registered_future_requests'][REQ]['additional_operational_overlays'].update(copy.deepcopy(records));assert reg==expected
 assert q['budget']==360 and q['remaining']==26 and len(q['consumed'])==334
 assert all(q['additional_operational_overlays'][k]==v for k,v in before['operational_records'].items())
 return dict(real_independent_FD_EX=True,second_SH_NB_blocked=True,new_operational_records=2,new_grants=0,old_UUIDs_preserved=334,old_full_records_preserved=True)
check('real_EX_pure_exact_two_rows_zero_grants_old334_UUIDs',positive)
def negative_cases():
 done=[]
 for name in ['science','IR_authorization','IR_canonical_lineage','canonical_refresh_after_prepare','disk_claim','caller_claim','INTENT','consumption','record_conflict','new_ID_already_registered','benign_old_receipt']:
  r,q,reg,before,canonical,records=fixture('negative_'+name);c=scope['rows'][0]['cohort'];p=r/'control/specs'/(c+'.json');a=r/'control'/(c+'_SPEC.json');spec=read(p)
  if name=='science':spec['core_commit']='FORGED';put(p,spec);a.write_bytes(p.read_bytes());q['admitted_specs'][c]=sha(p)
  if name=='IR_authorization':next(x for x in q['authorized_incident_recovery_trials']if x['cohort']==c)['original_uuid']='FORGED'
  if name=='IR_canonical_lineage':spec['incident_recovery_trial_lineage']['original_uuid']='FORGED';put(p,spec);a.write_bytes(p.read_bytes());q['admitted_specs'][c]=sha(p);canonical[c]=sha(p)
  if name=='canonical_refresh_after_prepare':spec['estimated_peak_model_RAM_bytes']+=123;put(p,spec);a.write_bytes(p.read_bytes());q['admitted_specs'][c]=sha(p)
  if name=='disk_claim':put(r/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{c:{'private':True}}})
  if name=='INTENT':put(r/'control/qualification_ledger'/(c+'.INTENT.json'),{'uuid':'PRIVATE_NOT_ACTUAL'})
  if name=='consumption':q['consumed'][c]={'uuid':'CONCURRENT_PRIVATE_BIRTH'};q['remaining']-=1
  if name=='record_conflict':q['additional_operational_overlays'][next(iter(before['operational_records']))]['CONCURRENT']='PRESERVE'
  if name=='new_ID_already_registered':q['additional_operational_overlays'][m.RESOURCE_ID]={'PREEXISTING':'DO_NOT_OVERWRITE'};before['operational_records']=copy.deepcopy(q['additional_operational_overlays'])
  if name=='benign_old_receipt':q['consumed'][next(iter(q['consumed']))]['new_benign_receipt']='PRESERVE_COMPLETE_CURRENT_ROW'
  current=copy.deepcopy(reg)
  try:
   if name=='caller_claim':m.check_unused(r,q,scope,{c:{'private':True}})
   else:locked_call(r,q,reg,before,canonical,records)
  except AssertionError:pass
  else:raise AssertionError('NEGATIVE_NOT_REJECTED '+name)
  assert reg==current,'MUTATION_BEFORE_REJECTION '+name;done.append(name)
 return dict(rejected_before_mutation=done,benign_receipt_policy='CONSERVATIVE_HOLD_PRESERVE_NEW_RECEIPT_NOT_CONTINUE_CAS')
check('science_IR_lineage_canonical_claim_INTENT_consumption_CAS_receipt_reject',negative_cases)
def safe_refresh():
 r,q,reg,before,canonical,records=fixture('legal_refresh_pre_prepare');c=scope['rows'][0]['cohort'];p=r/'control/specs'/(c+'.json');s=read(p);s['estimated_peak_model_RAM_bytes']+=9999;s['limits']['max_process_tree_rss_bytes']+=9999;put(p,s);(r/'control'/(c+'_SPEC.json')).write_bytes(p.read_bytes());q['admitted_specs'][c]=sha(p)
 canonical=m.check_unused(r,q,scope);locked_call(r,q,reg,before,canonical,records);return dict(legal_RSS_limit_refresh_not_locked_to_provenance_full_SHA=True,science_projection_unchanged=True)
check('legitimate_operational_refresh_before_prepare_keeps_science',safe_refresh)
tree=ast.parse(SRC.read_text());pure={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['check_unused','append_records_locked']}
for fn in pure.values():
 for node in ast.walk(fn):
  if isinstance(node,ast.Call):assert not(isinstance(node.func,ast.Attribute)and node.func.attr in ['canonical','registered','authority','assert_parent_lease','validate'])
result=dict(schema='BROAD_MAIN3_PURE_LOCKED_TRANSACTION_CPU_QUALIFICATION_V1',status='PASS'if all(x['status']=='PASS'for x in checks)else'FAIL',source_path=str(SRC),source_sha256=source_sha,driver_path=__file__,driver_sha256=sha(__file__),fixture_root=str(root),checks=checks,pure_function_AST_sha256={name:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()for name,node in pure.items()},coverage='Actual two pure functions and private independent EX; no apply/actual owner/module installation tested',actual_owner_executed=False,models_started=0,production_mutations=0,new_grants=0,signals=0)
assert sha(SRC)==source_sha,'SOURCE_CHANGED_DURING_QUALIFICATION';put(D/'CPU_QUALIFICATION.json',result);print(json.dumps(dict(status=result['status'],source_sha256=source_sha,QA_sha256=sha(D/'CPU_QUALIFICATION.json'),checks=[(x['name'],x['status'],x.get('error'))for x in checks]),indent=2))
