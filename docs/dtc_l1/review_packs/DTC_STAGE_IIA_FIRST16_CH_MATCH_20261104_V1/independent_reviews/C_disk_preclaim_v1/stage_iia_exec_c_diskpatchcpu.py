from pathlib import Path
import json,hashlib,importlib.util,copy,ast
R=Path('/root/data/dtc_stage_iia_first16_20261104_v1');P=R/'control/operational_amendments/disk_preclaim_v1/owner_disk_preclaim.py';A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');O=A/'agents/C_disk_preclaim_v1';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('C_private_disk_preclaim_fixture',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);rows=[]
basepending=[{'cohort':'LEGAL16_A','request':'DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1'}];choice={'cohort':'LEGAL16_A','host_cpu':32};sample={'FIXTURE':True};claims={};good={'physical_RAM_pass':True,'physical_disk_pass':True,'admission_disk_pass':True}
def test(name,decision=None,admission=None,expect='PASS',pending=None,resource_raises=False):
 p=copy.deepcopy(basepending if pending is None else pending);cl=copy.deepcopy(claims);before=copy.deepcopy((p,cl));calls=[]
 def resource(s,fresh):
  calls.append((s,fresh))
  if resource_raises:raise RuntimeError('FIXTURE_READONLY_HOLD')
  return copy.deepcopy(good if admission is None else admission)
 original=lambda *a,**k:choice if decision is None else decision
 if expect=='NO_CHOICE':original=lambda *a,**k:None
 try:
  result=m.gated_choose(original,resource,p,sample,cl,policy={'fixture':True});ok=(result is choice if expect=='PASS'else result is None if expect in ['HOLD','NO_CHOICE']else False);err=None
 except (AssertionError,RuntimeError)as e:ok=expect=='REJECT';err=repr(e)
 ok=ok and before==(p,cl) and (len(calls)==0 if expect in ['NO_CHOICE']else True)
 rows.append({'case':name,'PASS':ok,'resource_calls':len(calls),'fresh_true':all(f for s,f in calls),'claims_and_pending_unchanged':before==(p,cl),'error':err})
test('AcceptedChoiceReturnedExactObject')
test('NoMemoryChoiceDoesNotCallResource',expect='NO_CHOICE')
for key in good:
 a=dict(good);a[key]=False;test('False_'+key+'DoesNotCreateClaim',admission=a,expect='HOLD')
for key in good:
 a=dict(good);a.pop(key);test('Missing_'+key+'RejectsAdmission',admission=a,expect='HOLD')
a=dict(good);a['physical_disk_pass']=1;test('IntegerOneIsNotTrue',admission=a,expect='HOLD')
test('UnknownChosenCandidateRejected',decision={'cohort':'NOT_REGISTERED'},expect='REJECT')
test('DuplicateCandidateRejected',pending=basepending*2,expect='REJECT')
test('ResourceReadErrorNoClaim',resource_raises=True,expect='REJECT')
plan=json.loads((R/'control/EXECUTION_PLAN.json').read_text());pinsok=all(sha(x['path'])==x['sha256'] for x in plan['source_pins']);text=P.read_text();checks=[{'check':'Source exact reviewed patch','PASS':sha(P)=='a4c5aaf17ad92adb2ae8141fb864b73377ce8db2ded64056e7b4b75fd9f99d38'},{'check':'All62 frozen scientific sources remain unchanged','PASS':pinsok},{'check':'New scheduler Main/PID/start/RLock/source and finite budget guards','PASS':all(x in text for x in ['os.getpid()==1498278','977758783',"state['phase']=='ACKED'",'with held:',"q['budget']==16",'plan[\'source_pins\']',"P(original.__code__.co_filename)==R/'tools/stage2_resources.py'",'res.choose_dispatch=wrapper'])},{'check':'Only introduces resource check before future claims','PASS':all(x['PASS']for x in rows)}];o={'schema':'DTC_STAGE_IIA_C_DISK_PRECLAIM_READONLY_REVIEW_V1','decision':'PASS_ROOT_SINGLE_SOURCE_BOUND_CALLBACK'if all(x['PASS']for x in checks)else'HOLD','source_path':str(P),'source_sha256':sha(P),'all_checks_PASS':all(x['PASS']for x in checks),'checks':checks,'CPU_cases':rows,'execution_plan_sha256':sha(R/'control/EXECUTION_PLAN.json'),'models_started_by_review':0,'authority_or_owner_changes_by_review':0,'scope':'Pure gated_choose cases use fake decisions/resource values. apply() not invoked. Existing models, source62, specs, engine, guard and16 grants unchanged.','operational_preconditions':['Root creates a fresh callback directory; APPLIED.json absent and writeable before single callback.','If receipt writing fails after marker/callable install, inspect installed marker and reconcile forward; never blindly repeat.','Keep APPLIED receipt/source SHA and original callable in owner marker.','This restricts future admission only; it does not convert runtime witnesses into accepted performance or add starts.']};(O/'DISK_PRECLAIM_REVIEW.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'decision':o['decision'],'CPU_cases':len(rows),'all_PASS':o['all_checks_PASS'],'failed':[x for x in rows if not x['PASS']],'review_sha256':sha(O/'DISK_PRECLAIM_REVIEW.json')},indent=2))
