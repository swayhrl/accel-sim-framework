#!/usr/bin/env python3
"""Synthetic exact artifact feedback tests, never production161."""
import pathlib,json,hashlib,copy
D=pathlib.Path(__file__).resolve().parent
prefix=(D/'test_auto161_metadata_adapter_v2.py').read_text().split('tests=[]',1)[0]
prefix=prefix.replace("T=D/'synthetic_fixtures_v2'","T=D/'artifact_fixtures_v2'")
ns={'__file__':str(D/'test_auto161_metadata_adapter_v2.py'),'__name__':'artifact_fixture_factory'};exec(compile(prefix,'synthetic_artifact_factory','exec'),ns)
a=ns['a'];T=ns['T'];ref=ns['ref'];row,_,_,_=ns['fixture']('ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED',True)
source=T/'synthetic_CPU_producer.py';source.write_text('# synthetic producer source fixture only\n')
sh=hashlib.sha256(source.read_bytes()).hexdigest()
registry={'schema':'AUTO161_ALLOWLIST_V1','artifact_producers':{'SYNTHETIC_CPU_ONLY':{'profile':'SYNTHETIC_CPU_ONLY_V1','source_path':str(source),'source_sha256':sh,'allowed_gates':['EXACT_SYNTHETIC_CPU_GATE'],'allowed_next_stages':['WAIT_ISA_ADAPTER']}}}
base={'schema':'AUTO161_ARTIFACT_V1','producer_id':'SYNTHETIC_CPU_ONLY','profile':'SYNTHETIC_CPU_ONLY_V1','producer_source_sha256':sh,'status':'PASS','qualification_granted':False,'gpu_executed':False,'historical_queue_mutated':False,'next_stage':'WAIT_ISA_ADAPTER','provided_gates':['EXACT_SYNTHETIC_CPU_GATE'],'evidence':[ref({'synthetic_CPU_test':'PASS'})],'requires':[],'target_queue_ids':[row['queue_id']],'family_keys':['research_dependency_only'],'row_bindings':{row['queue_id']:a.digest(row)}}
def consume(doc):
 ctx={'allowlist_ref':ref(registry,'registry'),'dependency_artifacts':[ref(doc,'artifact')]}
 rr=a.Reader();return a.consume_approved_CPU_artifacts(ctx,row,rr),rr
tests=[]
out,rr=consume(copy.deepcopy(base));assert len(out['closed_CPU_candidate_gates'])==1 and not out['dynamic_missing_proofs_removed']
tests.append({'case':'exact_approved_artifact_raw_source_evidence_reopened_CPU_gate_feedback','status':'PASS','read_files':len(rr.refs)})
doc=copy.deepcopy(base);doc['target_queue_ids']=[];doc['row_bindings']={};out,_=consume(doc);assert not out['closed_CPU_candidate_gates']and out['research_dependencies']
tests.append({'case':'family_only_no_exact_gate','status':'PASS'})
doc=copy.deepcopy(base);doc['status']='HOLD';out,_=consume(doc);assert not out['closed_CPU_candidate_gates']
tests.append({'case':'HOLD_artifact_no_closed_gate','status':'PASS'})
doc=copy.deepcopy(base);doc['requires']=['a'*64];out,_=consume(doc);assert not out['closed_CPU_candidate_gates']and out['requires_missing']==['a'*64]
tests.append({'case':'missing_dependency_no_gate','status':'PASS'})
for name,mutate in [
 ('wrong_row_binding',lambda d:d['row_bindings'].update({row['queue_id']:'0'*64})),
 ('unknown_producer',lambda d:d.update(producer_id='UNKNOWN')),
 ('wrong_profile',lambda d:d.update(profile='UNKNOWN')),
 ('wrong_source_sha',lambda d:d.update(producer_source_sha256='0'*64)),
 ('qualification_overclaim',lambda d:d.update(qualification_granted=True)),
 ('missing_qualification_flag',lambda d:d.pop('qualification_granted')),
 ('GPU_overclaim',lambda d:d.update(gpu_executed=True)),
 ('unknown_gate',lambda d:d.update(provided_gates=['UNREGISTERED_GATE'])),
 ('wrong_evidence_hash',lambda d:d['evidence'][0].update(sha256='0'*64)),
 ('unknown_nextstage',lambda d:d.update(next_stage='FINISHED_TRACE')),
 ('wrong_schema',lambda d:d.update(schema='AUTO161_ARTIFACT_V2'))]:
 doc=copy.deepcopy(base);mutate(doc)
 try:consume(doc)
 except (ValueError,KeyError)as e:tests.append({'case':name,'status':'REJECTED','reason':str(e)})
 else:raise AssertionError('negative accepted '+name)
result={'schema':'AUTO161_ARTIFACT_FEEDBACK_SYNTHETIC_FIXTURES_V2','status':'PASS','test_count':len(tests),'tests':tests,'adapter_source_sha256':hashlib.sha256((D/'auto161_metadata_adapter_v2.py').read_bytes()).hexdigest(),'formal161_or_GPU_or_simulation':False}
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','tests':len(tests),'formal161_or_GPU_or_simulation':False}))
