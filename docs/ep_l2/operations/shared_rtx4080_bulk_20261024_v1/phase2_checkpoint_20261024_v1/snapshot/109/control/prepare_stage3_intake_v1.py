#!/usr/bin/env python3
import pathlib,json,hashlib,re,sys
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control';sys.path.insert(0,str(C));from scientific_identity_v2a import key,identity,physical
S=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/manifests/STAGE3_INCREMENTAL_NATIVE_CANDIDATES_V1.json');data=json.loads(S.read_text());rows=[];queue=[];worker=json.loads((C/'WORKER_V7_PREPARED.json').read_text());existing={key(json.loads(p.read_text())['task']) for p in (C/'capture_jobs').glob('*.json')}
for original in data['candidates']:
 task=dict(original);task.setdefault('variant','SOURCE_DECLARED_DEFAULT_NO_VARIANT_FIELD')
 state=task['native_state'];receipt=pathlib.Path(state['native_receipt']);native=json.loads(receipt.read_text());flags=list(task.get('profile_flags',[]));kind=task.get('workload_kind','');status='SPECIAL'
 if 'API_ONLY' in kind:status='EXPLICIT_NO_KERNEL'
 elif 'INTENTIONAL_DEVICE_ASSERT' in kind:flags+=['EXPECTED_DEVICE_ASSERT_DIAGNOSTIC_NOT_ORDINARY_TERMINAL_EXIT']
 else:
  text='\n'.join(pathlib.Path(f['path']).read_text(errors='replace') for f in task.get('source_files',[]) if pathlib.Path(f['path']).suffix in ['.cu','.h','.cpp','.c'])
  if re.search(r'cudaMallocManaged|cudaMemPrefetchAsync|cudaMemAdvise',text):flags+=['UNIFIED_MANAGED_MEMORY_INPUT_AND_SYSTEM_MODEL_PENDING']
  if re.search(r'#\s*pragma\s+omp\s+parallel|pthread_create|std::thread',text):flags+=['MULTITHREADED_HOST_LAUNCH_ORDER_REVIEW_REQUIRED']
  if re.search(r'\brand\s*\(|\bsrand\s*\(|\brandom\s*\(',text):flags+=['GENERATED_INPUT_ACTUAL_BYTE_SNAPSHOT_PENDING']
  informational={'EXACT_OFFICIAL_QA_OR_FULL_DEFAULT_INPUT','LEGACY_SDK_SOURCE_SEPARATE_IDENTITY','ORIGINAL_SOURCE_KERNEL_UNCHANGED','EXPLICIT_HOST_API_OR_LIFECYCLE_VARIANT_KERNEL_BODY_UNCHANGED','HOST_API_MIGRATION_DISTINCT_VARIANT','SOURCE_CONFIRMED_HEADLESS_NO_GL_CALLS','NO_GL_CONTEXT_IN_OFFICIAL_QATEST_BRANCH','EXPLICIT_FIXED_SEED_12345'}
  if not set(flags)-informational:status='STATIC_PREFLIGHT_PENDING'
 ident='ORD_STAGE3_'+re.sub('[^A-Za-z0-9_.-]','_',task['program'])+'_'+key(task)[:12]+'_A001'
 row={'content_id':key(task),'legacy_physical_content_id':physical(task),'scientific_identity':identity(task),'suite':task['suite'],'source_version':task['version'],'source_head':task.get('source_head'),'program':task['program'],'variant':task['variant'],'argv':task['argv'],'binary_sha256':task['binary_sha256'],'input_identity':task.get('input_files'),'status':status,'special_reason':flags,'observations':[{'source_candidate_manifest':str(S),'sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'task_id':task['task_id']}],'native_evidence':[dict(state,receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest())],'consumer_qualification':'NOT_GRANTED','source_scope_extension':True}
 if status=='STATIC_PREFLIGHT_PENDING' and key(task) not in existing:
  job={'id':ident,'asset_id':ident,'task':task,'native_receipt':native,'native_state':state,'numerical_policy':'NUMERICAL_UNVERIFIED_NATIVE_EVIDENCE_AVAILABLE','allowed_capture_exits':[0],'input_byte_identity_qualification':'PENDING_ACTUAL_BYTES_OR_SPECIFIC_SOURCE_RULE'};p=C/'capture_jobs'/(ident+'.json')
  assert not p.exists();p.write_text(json.dumps(job,indent=2)+'\n');row['capture_job_id']=ident
  queue.append({'id':ident,'type':'CAPTURE_ORDINARY','job_path':str(p),'worker_script':worker['path'],'worker_sha256':worker['sha256'],'status':'PENDING_SPECIALIST_EXTENSION','result':{'reason':'STATIC_PREFLIGHT_PENDING_NOT_YET_ADMITTED'},'priority':80})
 rows.append(row)
(C/'STAGE3_V1_SCOPE_DELTA.json').write_text(json.dumps({'schema':'CUDA205_INCREMENTAL_SCOPE_DELTA_V1','contents':rows,'source_candidate_count':len(rows),'source_native_attempt_count':data['attempts_audited'],'source_manifest_sha256':hashlib.sha256(S.read_bytes()).hexdigest()},indent=2)+'\n')
(C/'STAGE3_V1_CAPTURE_QUEUE_DELTA.json').write_text(json.dumps(queue,indent=2)+'\n')
mapping=[]
for q in queue:
 j=json.loads(pathlib.Path(q['job_path']).read_text());mapping.append({'id':j['id'],'asset_id':j['asset_id'],'content_id':key(j['task']),'job_path':q['job_path'],'task':j['task']})
(C/'STAGE3_V1_CAPTURE_MAP_DELTA.json').write_text(json.dumps(mapping,indent=2)+'\n')
print('new95 scope',len(rows),'ordinary awaits static',len(queue))
