import pathlib,json,hashlib,types,copy,itertools,time,os,resource
P=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/auto161_pipeline_20261026_v1');R=P/'root/proof_progress_v3'
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]));os.nice(15);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
source=P/'adapters/auto161_metadata_adapter_v3.py';a=types.ModuleType('candidate');exec(compile(source.read_text(),str(source),'exec'),a.__dict__)
registry=json.loads((P/'orchestrator/ALLOWLIST.json').read_text())
static=json.loads((P/'family_static_reopen_v1/PRODUCER_REGISTRATION_CANDIDATE_V1.json').read_text());registry['artifact_producers'][static['producer_id']]=static['entry']
inp=json.loads((P/'family_input_prepare_v1/ROOT_ENTRY_V1.json').read_text())
registry['artifact_producers'][inp['producer_id']]={'profile':inp['profile'],'source_path':inp['producer_source_path'],'source_sha256':inp['producer_source_sha256'],'allowed_gates':['ACTUAL_INPUT_CAPTURE_REQUEST_SPEC_CPU_PREPARED_V1'],'allowed_next_stages':list(a.ROUTES.values())}
reg=R/'FIXTURE_ALLOWLIST_NOT_PRODUCTION.json';reg.write_text(json.dumps(registry,indent=2)+'\n')
def ref(p):
 b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
index=json.loads((P/'orchestrator/inbox/INDEX.json').read_text())['artifacts']
static_refs=[]
for p in sorted(pathlib.Path(static['candidate_artifact_directory']).glob('*.json')):
 if json.loads(p.read_text())['status']=='PASS':static_refs.append(ref(p))
assert len(static_refs)==69
allrefs=index+static_refs+inp['artifacts']
baseline=json.loads((R/'BASELINE_ACCEPTED_RESULTS_V1.json').read_text());oldby={x['queue_id']:x for x in baseline['rows']}
scope=json.loads((P.parent/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json').read_text());authority=json.loads((P/'adapters/FROZEN_AUTHORITY_INDEX_V2.json').read_text())
results=[];maxrefs=0;cases=[];removed=0;over=[]
for i,row in enumerate(scope['rows']):
 reader=a.Reader();item=authority['rows'][i];projection=reader.refobj(item['projection_ref']);job=reader.obj(projection['identity_row']['job_evidence']['snapshot'],row['job_sha256'])
 relevant=[r for r in allrefs if row['queue_id'] in json.loads(pathlib.Path(r['path']).read_text())['target_queue_ids']]
 feedback=a.consume_approved_CPU_artifacts({'allowlist_ref':ref(reg),'dependency_artifacts':relevant},row,reader)
 evaluated=a.evaluate(row,projection,job,authority,reader)
 original=copy.deepcopy(evaluated)
 assert evaluated['missing_proofs']==json.loads(pathlib.Path(oldby[row['queue_id']]['baseline_result_ref']['path']).read_text())['missing_proofs']
 result=a.resolve_CPU_proofs(row,evaluated,feedback)
 # Real inputs/source are re-opened; expected limits also reserve context/source/scope/index refs.
 nr=len(reader.refs)+4;maxrefs=max(maxrefs,nr)
 if nr>64:over.append({'queue_id':row['queue_id'],'predicted_input_refs':nr})
 for order in [list(reversed(feedback['closed_CPU_candidate_gates'])),sorted(feedback['closed_CPU_candidate_gates'],key=lambda x:x['artifact_sha256'])]:
  f=copy.deepcopy(feedback);f['closed_CPU_candidate_gates']=order;x=a.resolve_CPU_proofs(row,copy.deepcopy(original),f)
  assert x['missing_proofs']==result['missing_proofs'] and x['next_stage']==result['next_stage'] and x['cpu_resolved_proofs']==result['cpu_resolved_proofs']
 cases.append('order_independent:'+row['queue_id'])
 orig={x['proof_id']for x in original['missing_proofs']};now={x['proof_id']for x in result['missing_proofs']}
 assert orig-now <= {'EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF','ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION'}
 assert all(x['proof_id'] in now for x in original['missing_proofs'] if x['proof_id'].startswith(('ISA_','ACTUAL_APPLICATION_INPUT','GAUSSIAN16','EXACT_MAPPING_REPAIR')))
 if oldby[row['queue_id']]['accepted_state']=='WAIT_SOURCE_RUNTIME_ADAPTER':assert result['next_stage']=='WAIT_SOURCE_RUNTIME_ADAPTER'
 removed+=len(result['cpu_resolved_proofs'])
 results.append({'queue_id':row['queue_id'],'removed_CPU_proofs':[x['proof_id']for x in result['cpu_resolved_proofs']],'missing_count':len(result['missing_proofs']),'next_stage':result['next_stage'],'read_refs_with_reserve':nr})
sample=scope['rows'][0];r=results[0]
report={'status':'ROOT_REAL161_V3_CPU_PROOF_RESOLUTION_REPLAY_PASS','real_rows':161,'registered_fixture_static_PASS_artifacts':69,'CPU_proofs_resolved':removed,'order_independence_real_row_cases':len(cases),'max_predicted_refs':maxrefs,'predicted_core_limit_violations':over,'results':results,'source_sha256':ref(source)['sha256'],'production_registered':False,'GPU_executions':0,'trace_qualification':False,'created_unix':time.time()}
(R/'ROOT_REAL161_PROGRESS_REPLAY_V1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'}))
