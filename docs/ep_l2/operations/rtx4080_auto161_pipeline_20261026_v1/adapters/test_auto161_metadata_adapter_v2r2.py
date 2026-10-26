#!/usr/bin/env python3
"""Synthetic adapter logic/IO fixtures only. Never runs the production161 CLI."""
import pathlib,json,hashlib,importlib.util,copy,time
D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('adapter',D/'auto161_metadata_adapter_v2.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
T=D/'synthetic_fixtures_v2r2';T.mkdir(exist_ok=False)
counter=0
def ref(obj,name='data'):
 global counter
 counter+=1;p=T/('%03d_%s.json'%(counter,name));p.write_text(json.dumps(obj,indent=2)+'\n');b=p.read_bytes()
 return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def task():return {'suite':'SYNTHETIC','version':'v1','program':'synthetic','variant':'test-only','binary_sha256':'a'*64,'argv':['/synthetic/application'],'source_files':[{'path':'/synthetic/app.cu','sha256':'d'*64}],'cwd':'/synthetic','input_identity':'synthetic deterministic fixture only'}
def coherent_side(t):
 prod='b'*64;h='c'*64;ordered='e'*64;inputh='f'*64
 cap={'status':'OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_CLOSED_SHA_QUALIFIED','ordered_input_identity_sha256':ordered,'binary_sha256':t['binary_sha256'],'tool_sha256':prod,'lifecycle':{'process_end_observed':True},'application_exit_code':0,'copies':{'1':{'restorable_relative_path':'input.bin','sha256':inputh,'bytes':4,'boundary':'SYNC_API_SUCCESS_SOURCE_BYTES_FROZEN','api':'cudaMemcpy'}} ,'total_bytes':4}
 pair={'scope':'OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_ONLY','comparison':'MATCH','observer_ordered_sha256':ordered,'trace_ordered_sha256':ordered,'source_initialization_oracle':'SYNTHETIC_ONLY'}
 flags={'INSTR_BEGIN':'0','INSTR_END':'4294967295','C16_EXACT_ROOT_FUNCTION_ONLY':'0','C16_USE_NVBIT_STATIC_INDEX':'0','ENABLE_SPINLOCK_FAST_FORWARD':'0','TERMINATE_UPON_LIMIT':'0'}
 asset={'producer_sha256':prod,'binary_sha256':t['binary_sha256'],'full_application':{'sampling':'NONE','all_warps_terminate':True},'contract_sha256':h,'validator_sha256':h,'map_manifest_sha256':h,'map_maker_sha256':h,'postprocessor_sha256':h}
 ex={'tool_sha256':prod,'binary_sha256':t['binary_sha256'],'tracer_control_flags':flags,'explicit_capture_environment':{'DYNAMIC_KERNEL_RANGE':''},'exit_code':0}
 out={'task':t,'asset':asset,'execution':ex,'capsule':cap,'pair':pair,'metadata_raw_utf8':{}}
 files=[{'path':'tools/producer.so','sha256':prod,'bytes':1},{'path':'input.bin','sha256':inputh,'bytes':4}]
 for n,k in [('TASK.json','task'),('ASSET.json','asset'),('EXECUTION.json','execution'),('INPUT_CAPSULE_QUALIFICATION_V4R2.json','capsule'),('INPUT_SNAPSHOT_PAIR_IDENTITY.json','pair')]:
  raw=json.dumps(out[k]);out['metadata_raw_utf8'][n]=raw;files.append({'path':n,'sha256':hashlib.sha256(raw.encode()).hexdigest(),'bytes':len(raw.encode())})
 out['manifest']={'files':files};out['manifest_raw_utf8']=json.dumps(out['manifest']);out['commit']={'status':'COMMITTED_VERIFIED','manifest_sha256':hashlib.sha256(out['manifest_raw_utf8'].encode()).hexdigest()}
 return out
def fixture(route,family=False):
 t=task();qid='SYNTHETIC_'+str(counter);ji=ref({'task':t},'job');identity={'binary_sha256':t['binary_sha256'],'argv':t['argv'],'source_files':t['source_files']}
 ih=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 families=['CALL_REL_RET_REL']if family else[]
 gap={'CALL_REL_RET_REL':{'gap':'synthetic exact CALL/RET lane target/return/loaded proof missing'}}if family else{}
 row={'queue_id':qid,'historical_queue_status':'PENDING_SPECIALIST_EXTENSION','job_sha256':ji['sha256'],'declared_identity_sha256':ih,'binary_sha256':t['binary_sha256'],'argv':t['argv'],'program':'synthetic','profile_families_nonexclusive':families,'profile_family_gaps':gap,'next_step':route}
 ir={'queue_id':qid,'original_queue_row':{'id':qid,'status':row['historical_queue_status']},'job_evidence':dict(ji,snapshot=ji['path']),'scientific_identity':identity,'scientific_identity_sha256':ih}
 pr={'queue_id':qid,'job_evidence':dict(ji,snapshot=ji['path']),'binary_sha256':t['binary_sha256'],'argv':t['argv'],'profile_families':families}
 projection={'scope_row':copy.deepcopy(row),'identity_row':ir,'profile_row':pr,'mapper_row':None}
 ba={'schema':'EXACT161_CURRENT_BINARY_READONLY_ATTESTATION_V1','closed':True,'no_GPU':True,'scope_sha256':a.SCOPE_SHA,'rows':[{'path':t['argv'][0],'expected_sha256':t['binary_sha256'],'actual_sha256':t['binary_sha256'],'bytes':123,'status':'MATCH_CLOSED_CURRENT_BINARY','source_ids':[qid]}]}
 ga={'binary_sha256':'0'*64,'exact_argv':['/different/exact','-s','16'],'dynamic_required':['synthetic dynamic proof missing']}
 index={'root_binary_attestation':ref(ba,'attest'),'root_receipts':{'comparator':ref({'status':'PASS_FOR_READONLY_GOAL_AUDIT_ONLY'}),'mapper':ref({'status':'ROOT_STATIC_REVIEW_AND_INDEPENDENT_12_CPU_CASES_PASS_GPU_NOT_ADMITTED'}),'window':ref({'status':'ROOT_REVIEWED_ADMITTED_EXACT_SDK42_DEFAULT50000_BOUNDARY_WINDOW_ONCE'})},'gaussian':{'manifest':ref({'fixture':'manifest'}),'commit':ref({'fixture':'commit'}),'spec':ref(ga),'small_closed_evidence':[],'expected_binary':ga['binary_sha256'],'expected_argv':ga['exact_argv'],'profile':'GAUSSIAN16_DIRECT_RETPAIR_V1_CANDIDATE'},'comparator_source':json.loads((D/'FROZEN_AUTHORITY_INDEX_V2.json').read_text())['comparator_source'],'mapper_codes':[]}
 if route.startswith('READONLY_EXISTING'):
  side=coherent_side(t);projection['existing_route']={'asset_id':'SYNTHETIC_UNPUBLISHED','side_ref':ref(side,'side'),'member_refs':{}}
 if route.startswith('SDK42'):
  row['window_job_id']='C8_SDK42_VECTOR_DEFAULT50000_SPECIALIST_A001'
  index['sdk_arm']=ref({'status':'ARMED_WAITING_CURRENT_WHOLE_JOB','controller':{'pid':1,'start_ticks':'SYNTHETIC'},'run_directory':'SYNTHETIC_NOT_REAL'})
 if route.startswith('ROOT_GPU_PILOT')or route.startswith('SEPARATE_REPAIRED'):
  candidate={'id':'SYNTHETIC_A002','legacy_id':qid,'binary_sha256':t['binary_sha256'],'job_sha256':'1'*64,'variant_class':'EXPLICIT_REPAIRED_SOURCE_BINARY_VARIANT_V4'if route.startswith('SEPARATE')else'ORIGINAL_SOURCE_BINARY_IDENTITY_NEW_CAPTURE_ATTEMPT','input_policy':'DETERMINISTIC_SOURCE_INPUT_POLICY_ONLY;ACTUAL_INPUT_BYTE_SNAPSHOT_NOT_GRANTED'}
  row['new_candidate']={'job_sha256':candidate['job_sha256']};projection['prepared_mapper_candidate']=candidate
  projection['prepared_mapper_proof']=ref({'binary_sha256':t['binary_sha256'],'images':1,'ordinal_rows':[{'full_dump_exact':True}]})
  index['mapper_scope']=ref({'rows':[candidate]})
 if route.startswith('ACTUAL_INPUT'):row['input_preparation']={'origin':'SYNTHETIC_HOST_RNG','snapshot_scope':'OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_ONLY'}
 projection['scope_row']=copy.deepcopy(row)
 return row,projection,{'task':t},index
tests=[]
def runpositive(name,route,family=False):
 row,p,j,idx=fixture(route,family);rr=a.Reader();out=a.evaluate(row,p,j,idx,rr)
 assert out['missing_proofs']and out['next_stage']==a.ROUTES[route]
 assert all(x['binding']['queue_id']==row['queue_id']and x['required_evidence']and x['next_adapter_id']for x in out['missing_proofs'])
 assert all(x['passed']for x in out['checks'])
 tests.append({'case':name,'status':'PASS','next_stage':out['next_stage'],'missing_proofs':len(out['missing_proofs']),'actual_metadata_reads':len(rr.refs)})
for route in a.ROUTES:runpositive('route_'+route,route,route.startswith('ISA_'))
def negative(name,mutate):
 row,p,j,idx=fixture('ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED',True);mutate(row,p,j,idx)
 try:a.evaluate(row,p,j,idx,a.Reader())
 except (ValueError,KeyError,AssertionError)as e:tests.append({'case':name,'status':'REJECTED','reason':str(e)});return
 raise AssertionError('negative accepted:'+name)
negative('binary_mismatch',lambda r,p,j,i:j['task'].update(binary_sha256='0'*64))
negative('argv_mismatch',lambda r,p,j,i:j['task'].update(argv=['/different']))
negative('unknown_route',lambda r,p,j,i:r.update(next_step='UNKNOWN'))
negative('unknown_family',lambda r,p,j,i:(r.update(profile_families_nonexclusive=['UNKNOWN']),p['profile_row'].update(profile_families=['UNKNOWN'])))
negative('identity_digest_drift',lambda r,p,j,i:p['identity_row'].update(scientific_identity_sha256='0'*64))
negative('profile_preimage_drift',lambda r,p,j,i:p['profile_row']['job_evidence'].update(sha256='0'*64))
negative('scope_row_drift',lambda r,p,j,i:p['scope_row'].update(binary_sha256='0'*64))
negative('binary_attestation_mismatch',lambda r,p,j,i:i.update(root_binary_attestation=ref({'closed':True,'no_GPU':True,'scope_sha256':a.SCOPE_SHA,'rows':[]})))
negative('family_gap_empty',lambda r,p,j,i:r['profile_family_gaps'].update(CALL_REL_RET_REL={}))

def wrong_attestation(index,field,value):
 b=a.Reader().refobj(index['root_binary_attestation'])
 if field=='schema':b['schema']=value
 else:b['rows'][0][field]=value
 index['root_binary_attestation']=ref(b,'wrong_attestation')
negative('real_schema_required',lambda r,p,j,i:wrong_attestation(i,'schema','UNSUPPORTED_SCHEMA'))
negative('real_status_no_MATCH_alias',lambda r,p,j,i:wrong_attestation(i,'status','MATCH'))
negative('exact_source_id_membership_required',lambda r,p,j,i:wrong_attestation(i,'source_ids',['DIFFERENT_QUEUE_ID']))

# Real IO boundary tests use only our private synthetic metadata files.
r=ref({'synthetic':True},'hash')
try:a.Reader().read(r['path'],'0'*64)
except ValueError:tests.append({'case':'raw_file_SHA_mismatch','status':'REJECTED'})
else:raise AssertionError('badSHA accepted')
try:a.Reader().read('/etc/passwd')
except ValueError:tests.append({'case':'outside_NAS_read','status':'REJECTED'})
else:raise AssertionError('outsideNAS accepted')
so=T/'fake.so';so.write_bytes(b'not executed')
try:a.Reader().read(so)
except ValueError:tests.append({'case':'executable_body_read_forbidden','status':'REJECTED'})
else:raise AssertionError('executablebody read accepted')
result={'schema':'AUTO161_ADAPTER_SYNTHETIC_FIXTURES_V1','status':'PASS','tests':tests,'test_count':len(tests),'formal161_run':False,'GPU_or_simulation':False,'source_deletions':0,'historical_QUEUE_mutations':0}
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'tests':len(tests),'formal161_run':False}))
