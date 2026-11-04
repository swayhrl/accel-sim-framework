"""Actual measure->choose source-flow regression; private files only."""
import pathlib,json,copy,datetime,tempfile,ast,difflib,sys
sys.dont_write_bytecode=True
import derived35_consumer as new
D=pathlib.Path(__file__).parent;V1=D.parent/'derived35_analysis_consumer_v1'
OLD_SHA='c9f2b998185860d7a8ebf0e475ffdf3254bd5a1e47e3b90f91524327f00cf83e'
old=new.load('frozen_c9_counterexample',V1/'derived35_consumer.py',OLD_SHA)
qa=V1/'CPU_QUALIFICATION_FROZEN.json';assert new.sha(qa)=='7fe65c3b3f00ac018db2ccfcb714727e6125752975c930e4dd03b6a5bdcf2cc2'
A_REVIEW=new.A/'agents/A/derived35_consumer_independent_review_v1/REVIEW.json';assert new.sha(A_REVIEW)=='d43bba17fc77bb7743e6596139d8f9a45981cccdc2edc74de8650ea9ca33a829'
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('CPU isolated, no models/processes/signals')
sys.addaudithook(audit)
checks=[]
def check(name,fn):fn();checks.append(dict(name=name,status='PASS'))
def eq(a,b):assert a==b,(a,b)
def function_asts(module):return {n.name:ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(pathlib.Path(module.__file__).read_text()))if isinstance(n,ast.FunctionDef)}
changed=[name for name,body in function_asts(new).items()if function_asts(old).get(name)!=body]
check('only measure and choose changed; original30 other algorithms source-identical',lambda:eq(set(changed),{'measure','choose_reference'}))
base=new.ReadonlyConsumer();oldbase=old.ReadonlyConsumer();c='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';link=base.links[c];target=copy.deepcopy(base.spec(c))
frozen=new.read(V1/'DRY_20261028T234226933840Z/EVIDENCE.json');alternate=next(r['alternate']for r in frozen['rows']if r['original_cohort']==c)
assert alternate['valid']is True and alternate['RESULT_sha256']==new.sha(alternate['RESULT_path'])
root=pathlib.Path(tempfile.mkdtemp(prefix='CPU_BRANCH_ONLY_',dir=D));(root/'analysis').mkdir();rp=root/'analysis'/(c+'.RESULT.json')
records=[]
def branch(module,prototype,kind):
 x=object.__new__(module.ReadonlyConsumer);x.__dict__=dict(prototype.__dict__);x.specs=copy.deepcopy(prototype.specs);x.pins=dict(prototype.pins);x.cache={}
 s=copy.deepcopy(target)
 if kind in ['BADROLE_PASS','BADROLE_REUSE','BADROLE_NEGATIVE']:s['scientific_role']='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'
 if kind=='WRONG_ROI_PASS':s['expected']['CTA']+=1
 x.specs[c]=s
 state={'BADROLE_PASS':new.PASS,'BADROLE_REUSE':new.REUSE,'BADROLE_NEGATIVE':'FAIL_L2MLP_ARCHIVED_NO_RETRY','WRONG_ROI_PASS':new.PASS,'UNKNOWN':'UNKNOWN_RESULT_STATE'}
 if kind=='UNREADABLE':rp.write_text('{truncated')
 elif kind=='ABSENT':
  if rp.exists():rp.unlink()
 else:rp.write_text(json.dumps(dict(state=state[kind],cohort=c,cycles=1,uuid='CPU_ONLY')))
 previous=module.R;module.R=root
 try:
  measured=x.measure(c,target,'ORIGINAL_PRIMARY_SLOT');decision=module.choose_reference(measured,copy.deepcopy(alternate),link)
 finally:module.R=previous
 record=dict(module_source_sha256=new.sha(module.__file__),kind=kind,measure=measured,selected=decision['selected']['cohort']if decision['selected']else None,reason=decision['reason'],private_root=str(root));records.append(record);return record
counter=branch(old,oldbase,'BADROLE_PASS')
check('frozen c9 reproduces actual accepted-marker+badrole unintended R2 substitution',lambda:eq(counter['selected'],link['alternate_cohort']))
for kind in ['BADROLE_PASS','BADROLE_REUSE','WRONG_ROI_PASS','UNREADABLE','UNKNOWN','BADROLE_NEGATIVE']:
 r=branch(new,base,kind)
 check('V2 actual measure->choose HOLD '+kind,lambda r=r:eq(r['selected'],None))
absent=branch(new,base,'ABSENT')
check('valid identity absent typed-censored original still permits exact ratified R2',lambda:eq(absent['selected'],link['alternate_cohort']))
check('V2 records apparent accepted before bad role failure',lambda:eq((records[1]['measure']['apparent_accepted'],records[1]['measure']['identity_verified']),(True,False)))
check('unreadable and unknown preserve uncertainty instead of inferring negative',lambda:eq([r['measure']['acceptance_uncertain']for r in records if r['kind']in ['UNREADABLE','UNKNOWN']],[True,True]))
report=dict(schema='DTC_DERIVED35_CONSUMER_CPU_QUALIFICATION_V2',status='PASS',consumer_sha256=new.sha(new.__file__),contract_sha256=new.CONTRACT_SHA,qualification_only=True,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,count=len(checks),base_qualification=dict(path=str(qa),sha256=new.sha(qa),count=30,scope='Unchanged code/math and actual normal-path qualification inherited by exact source delta; V2 changes only measure failure ordering and substitution HOLD'),independent_defect_review=dict(path=str(A_REVIEW),sha256=new.sha(A_REVIEW)),records=records,old_code_preserved=True,formal_GM_generated=False,models_started=0,new_grants=0,production_changes=0)
with(D/'CPU_QUALIFICATION.json').open('x')as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
diff=''.join(difflib.unified_diff(pathlib.Path(old.__file__).read_text().splitlines(True),pathlib.Path(new.__file__).read_text().splitlines(True),fromfile='frozen-c9',tofile='consumer-v2'))
with(D/'EXACT_DIFF_FROM_C9.patch').open('x')as f:f.write(diff)
print(json.dumps(dict(source_sha256=new.sha(new.__file__),QA_sha256=new.sha(D/'CPU_QUALIFICATION.json'),count=len(checks),old_counterexample=counter['selected'],status='PASS')))
