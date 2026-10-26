import pathlib,json,types,sys,copy,itertools,hashlib,time,os
P=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/auto161_pipeline_20261026_v1');R=P/'root/proof_progress_v3'
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]));os.nice(15)
sys.path.insert(0,str(P/'audit/proof_progress_v3'))
from audit_common_v1 import Reader,AuditError
from audit_progress_v3 import verify_progress
a=types.ModuleType('adapter');ap=P/'adapters/auto161_metadata_adapter_v3.py';exec(compile(ap.read_text(),str(ap),'exec'),a.__dict__)
scope=json.loads((P.parent/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json').read_text())['rows'];index=json.loads((P/'adapters/FROZEN_AUTHORITY_INDEX_V2.json').read_text())
base=json.loads((R/'BASELINE_ACCEPTED_RESULTS_V1.json').read_text());bb={x['queue_id']:x for x in base['rows']}
reg=R/'FIXTURE_ALLOWLIST_NOT_PRODUCTION.json'
def ref(p):
 b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
inp=json.loads((P/'family_input_prepare_v1/ROOT_ENTRY_V1.json').read_text())
refs=json.loads((P/'orchestrator/inbox/INDEX.json').read_text())['artifacts']+[ref(p)for p in sorted((P/'family_static_reopen_v1/validation_run_v1/artifacts').glob('*.json'))if json.loads(p.read_text())['status']=='PASS']+inp['artifacts']
cases=[];sample=None
for i,row in enumerate(scope):
 rr=a.Reader();projection=rr.refobj(index['rows'][i]['projection_ref']);job=rr.obj(projection['identity_row']['job_evidence']['snapshot'],row['job_sha256'])
 related=[r for r in refs if row['queue_id']in json.loads(pathlib.Path(r['path']).read_text())['target_queue_ids']]
 ctx={'allowlist_ref':ref(reg),'dependency_artifacts':related,'missing_dependency_sha256':[]}
 feedback=a.consume_approved_CPU_artifacts(ctx,row,rr);out=a.resolve_CPU_proofs(row,a.evaluate(row,projection,job,index,rr),feedback)
 vr=Reader([P.parent]);expected=verify_progress(vr,ctx,row,out);assert expected==out['next_stage']
 cases.append('real161_independent:'+row['queue_id'])
 if sample is None and row['profile_families_nonexclusive']and out['cpu_resolved_proofs']:sample=(row,ctx,out)
 if bb[row['queue_id']]['accepted_state']=='WAIT_SOURCE_RUNTIME_ADAPTER'and row['next_step']=='READONLY_EXISTING_WORKLOAD_AVAILABILITY_ROUTE_REVIEW_NO_HISTORICAL_ALIAS':
  for perm in itertools.permutations(related):
   c=copy.deepcopy(ctx);c['dependency_artifacts']=list(perm);assert verify_progress(Reader([P.parent]),c,row,out)=='WAIT_SOURCE_RUNTIME_ADAPTER'
  cases.append('C8_all_artifact_order_permutations:'+row['queue_id'])
row,ctx,out=sample
bad=[]
x=copy.deepcopy(out);x['original_missing_proofs'][0]['required_evidence']=['forged'];bad.append(('original_missing_false',x))
x=copy.deepcopy(out);x['missing_proofs']=[p for p in x['missing_proofs']if not p['proof_id'].startswith('ISA_')];bad.append(('ISA_proof_removed_by_CPU',x))
x=copy.deepcopy(out);x['cpu_resolved_proofs'][0]['artifact_sha256']='0'*64;bad.append(('fake_closing_artifact',x))
x=copy.deepcopy(out);x['cpu_resolved_proofs'].append({'proof_id':'ACTUAL_APPLICATION_INPUT_LIFETIME_SNAPSHOT','CPU_only':True});bad.append(('input_promoted_from_PREPARED',x))
x=copy.deepcopy(out);x['dependency_requests']=[];bad.append(('lost_next_requests',x))
x=copy.deepcopy(out);x['missing_proofs']=[];bad.append(('CPU_completed_application',x))
for name,b in bad:
 try:verify_progress(Reader([P.parent]),ctx,row,b)
 except (AuditError,ValueError,KeyError):cases.append('rejected:'+name)
 else:raise AssertionError(name)
# Pure supervisor artifact routing reproduction, original LWW vs V3 hint-ignoring.
sys.path.insert(0,str(P/'orchestrator'))
old=types.ModuleType('old_engine');old.__file__=str(P/'orchestrator/orchestrator.py');exec(compile((P/'orchestrator/orchestrator.py').read_text(),old.__file__,'exec'),old.__dict__)
new=types.ModuleType('new_engine');new.__file__=str(R/'orchestrator_v3_candidate.py');exec(compile(pathlib.Path(new.__file__).read_text(),new.__file__,'exec'),new.__dict__)
F=R/'routing_fixture';(F/'inbox').mkdir(parents=True)
one=next(x for x in scope if x['queue_id']=='SDK42_VECTOR_4000000_ADA7_A001')
actual=[r for r in refs if one['queue_id']in json.loads(pathlib.Path(r['path']).read_text())['target_queue_ids']]
registry=json.loads(reg.read_text());old.c.D=F;new.c.D=F
old_states=set()
for order in itertools.permutations(actual):
 (F/'inbox/INDEX.json').write_text(json.dumps({'schema':'AUTO161_ARTIFACT_INDEX_V1','artifacts':list(order)}))
 registry['metadata_adapter']['id']='auto161_metadata_identity_static_v2';old_states.add(old.artifacts(one,registry)[2])
 registry['metadata_adapter']['id']='auto161_metadata_identity_static_v3';assert new.artifacts(one,registry)[2]is None
assert 'WAIT_EXISTING_AVAILABILITY_REVIEW'in old_states and 'WAIT_SOURCE_RUNTIME_ADAPTER'in old_states
cases.append('real_old_LWW_regression_reproduced_and_new_hint_suppressed')
result={'status':'ROOT_V3_INDEPENDENT_PROOF_AND_ROUTING_REGRESSIONS_PASS','checks':len(cases),'real_rows':161,'negative_rejections':len(bad),'all_C8_artifact_permutations':True,'old_LWW_regression_proven':True,'current_production_code_changed':False,'cases':cases,'created_unix':time.time()}
(R/'ROOT_INDEPENDENT_V3_REGRESSION_RESULT_V1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
