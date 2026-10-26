#!/usr/bin/env python3
"""Real schema/data joins only: never run() or evaluate() over the production161."""
import pathlib,json,hashlib,importlib.util,copy,collections
D=pathlib.Path(__file__).resolve().parent
N=D.parents[1]
sp=importlib.util.spec_from_file_location('adapter_v2',D/'auto161_metadata_adapter_v2.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
S=N/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json'
B=N/'auto161_pipeline_20261026_v1/root/CURRENT_BINARY_ATTESTATION_V1.json'
# D.parents[1] is N because D=N/auto161_pipeline.../adapters.
def raw(p,h=None):
 b=p.read_bytes();v=hashlib.sha256(b).hexdigest()
 if h is not None:assert v==h,(str(p),v,h)
 return json.loads(b),{'path':str(p),'sha256':v,'bytes':len(b)}
scope,sref=raw(S,a.SCOPE_SHA);att,bref=raw(B,'6eea0372813e8d102a042601cfc7bedcf3f269effc5ebdc63c5af7bc4c99ad78')
idx,iref=raw(D/'FROZEN_AUTHORITY_INDEX_V2.json',a.INDEX_SHA)
assert len(scope['rows'])==161 and len(att['rows'])==118
all_qids={r['queue_id']for r in scope['rows']}
assert {x for br in att['rows']for x in br['source_ids']}==all_qids
joined=[]
for i,row in enumerate(scope['rows']):
 fr=idx['rows'][i];assert fr['queue_id']==row['queue_id']and fr['frozen_row_sha256']==a.digest(row)
 projection,pref=raw(pathlib.Path(fr['projection_ref']['path']),fr['projection_ref']['sha256'])
 job,jref=raw(pathlib.Path(projection['identity_row']['job_evidence']['snapshot']),row['job_sha256'])
 checks=a.bind_core(row,projection,job);assert all(x['passed']for x in checks)
 br=a.validate_current_binary_attestation(att,row,a.SCOPE_SHA)
 joined.append({'queue_id':row['queue_id'],'row_index':i,'frozen_row_sha256':a.digest(row),'binary_path':br['path'],'binary_sha256':br['actual_sha256'],'status':br['status'],'exact_source_id_membership':row['queue_id']in br['source_ids'],'job_preimage_sha256':jref['sha256'],'projection_sha256':pref['sha256'],'core_checks_passed':len(checks)})
negative=[]
for case,mut in [('wrong_real_status',lambda x:x['rows'][0].update(status='MATCH')),('wrong_real_source_id',lambda x:x['rows'][0].update(source_ids=['WRONG_QID'])),('wrong_real_schema',lambda x:x.update(schema='UNSUPPORTED'))]:
 bad=copy.deepcopy(att);mut(bad)
 try:a.validate_current_binary_attestation(bad,scope['rows'][0],a.SCOPE_SHA)
 except ValueError as e:negative.append({'case':case,'status':'REJECTED','reason':str(e)})
 else:raise AssertionError('real protocol negative accepted '+case)
out={'schema':'AUTO161_REAL_BINARY_ATTESTATION_JOIN_REGRESSION_V2','status':'PASS','source':{'adapter_source_sha256':hashlib.sha256((D/'auto161_metadata_adapter_v2.py').read_bytes()).hexdigest(),'scope':sref,'attestation':bref,'index':iref},'unique_binary_pairs':len({(r['binary_path'],r['binary_sha256'])for r in joined}),'exact_rows_joined':len(joined),'all_118_cover_all161':len(joined)==161,'rows':joined,'negative_cases':negative,'tests':4,'production_worker_run':False,'evaluate_or_run_called':False,'current_binary_or_trace_payload_read':False,'GPU_or_simulation':False,'historical_QUEUE_mutated':False}
p=D/'REAL_BINARY_JOIN_REGRESSION_V2.json'
with p.open('x')as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','rows_joined':len(joined),'binary_pairs':out['unique_binary_pairs'],'real_protocol_negatives':len(negative),'production_worker_run':False,'report_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
