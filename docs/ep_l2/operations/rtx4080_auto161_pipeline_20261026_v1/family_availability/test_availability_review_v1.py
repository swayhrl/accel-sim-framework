#!/usr/bin/env python3
"""Pure-comparator and exact metadata negative fixtures; no trace/input payload reads."""
import pathlib,json,copy,importlib.util,hashlib,time
D=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('availability_review',D/'availability_review_adapter_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
config=m.load_config();mod=m.comparator(config);cases=[];positives=[]
for item in config['rows']:
 row=item['scope_row'];job=json.loads(m.read_ref(item['job_snapshot_ref']));right=json.loads(m.read_ref(item['existing_route']['side_ref']));left={'task':job['task'],'old_hold_status':row['historical_queue_status']}
 result=m.validate_route(mod,left,right,item['existing_route']['asset_id'],row)
 positives.append({'queue_id':row['queue_id'],'availability_route':result['availability_route'],'actual_profile':result['actual_capture_profile']['right']['profile']['actual_producer_sha256'],'historical_profile_equal':result['actual_capture_profile']['equal'],'historical_input_equal':result['observed_input_bytes']['equal_observed_supported_scope_only']})
 if item is not config['rows'][0]:continue
 def add(name,l,r,asset=None,scope_row=None):cases.append((name,l,r,asset or item['existing_route']['asset_id'],scope_row or row))
 bad=copy.deepcopy(right);bad['commit']['manifest_sha256']='0'*64;add('COMMIT_manifest_wrong',left,bad)
 bad=copy.deepcopy(right);bad['manifest_raw_utf8']+=' ';add('raw_manifest_byte_drift',left,bad)
 bad=copy.deepcopy(right);bad['asset']['producer_sha256']='55'*32;add('legacy55_cannot_replace_actualC8_producer',left,bad)
 bad=copy.deepcopy(right);bad['execution']['tool_sha256']='0'*64;add('producer_triple_mismatch',left,bad)
 bad=copy.deepcopy(right);bad['capsule']['status']='UNQUALIFIED';add('capsule_not_closed',left,bad)
 bad=copy.deepcopy(right);bad['pair']['scope']='COMPLETE_CUDA_DEVICE_READBACK';add('input_scope_widening_denied',left,bad)
 bad=copy.deepcopy(right);bad['pair']['comparison']='INPUT_DIFF';add('INPUT_DIFF_not_relabelled_MATCH',left,bad)
 bad=copy.deepcopy(right);bad['pair']['observer_ordered_sha256']='1'*64;add('observer_trace_hash_mismatch',left,bad)
 bad=copy.deepcopy(right);bad['execution']['exit_code']=1;add('capture_nonzero',left,bad)
 bad=copy.deepcopy(right);bad['asset']['full_application']['sampling']='SAMPLED';add('sampled_not_full',left,bad)
 bad=copy.deepcopy(right);bad['task']['argv']=['DIFFERENT'];add('wrong_actual_argv',left,bad)
 bad=copy.deepcopy(left);bad['task']['binary_sha256']='2'*64;add('wrong_legacy_binary',bad,right)
 add('historical_actual_proof_is_not_invented',right,right)
 add('wrong_selected_asset',left,right,'DIFFERENT_ASSET')
 bad=copy.deepcopy(row);bad['binary_sha256']='3'*64;add('wrong_exact_row_binary',left,right,scope_row=bad)
 bad=copy.deepcopy(right);bad.pop('capsule');add('missing_capsule',left,bad)
 bad=copy.deepcopy(right);bad['metadata_raw_utf8']['ASSET.json']='{}';add('metadata_parsed_raw_mismatch',left,bad)
rejected=[]
for name,left,right,asset,row in cases:
 try:m.validate_route(mod,left,right,asset,row)
 except (ValueError,KeyError,TypeError):rejected.append(name)
 else:raise AssertionError('accepted forbidden availability case '+name)
# Every emitted artifact must remain CPU-only, row-exact, and unregistered.
runs=sorted((D/'runs').glob('run_*'));assert runs
run=runs[-1];catalog=json.loads((run/'CURRENT_ROUTING_CANDIDATE.json').read_text());assert len(catalog['rows'])==3
for ref in catalog['artifact_refs']:
 a=json.loads(m.read_ref(ref));assert a['schema']=='AUTO161_ARTIFACT_V1'and a['producer_id']==m.PRODUCER and a['profile']==m.PROFILE
 assert a['producer_source_sha256']==m.file_ref(D/'availability_review_adapter_v1.py')['sha256']
 assert len(a['target_queue_ids'])==1 and len(a['row_bindings'])==1 and a['next_stage']=='WAIT_SOURCE_RUNTIME_ADAPTER'
 for k in ['qualification_granted','gpu_executed','simulation_executed','historical_queue_mutated','consumer_qualified','native_qualified','timing_qualified','science_qualified','trace_qualified','historical_input_equivalence','historical_profile_equivalence']:assert a[k]is False,k
 for e in a['evidence']:m.read_ref(e)
 assert 'EXISTING_C8_AVAILABILITY_METADATA_REVIEW_CLOSED_V1'in a['provided_gates']
result={'status':'PASS','actual_pure_comparator_positive_cases':positives,'negative_cases_rejected':len(rejected),'negative_names':rejected,'emitted_artifact_schema_exact_bindings_and_negative_qualifications':True,'trace_or_input_payload_body_reads':0,'public_registration_or_overlay_applied':False,'run':str(run),'source_ref':m.file_ref(D/'availability_review_adapter_v1.py')}
p=D/'TEST_RESULTS.json';p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','positive':3,'negative':len(rejected),'test_ref':m.file_ref(p)}))
