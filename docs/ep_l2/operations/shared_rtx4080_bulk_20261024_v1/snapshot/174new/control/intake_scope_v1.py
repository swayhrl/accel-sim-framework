#!/usr/bin/env python3
"""Content identities and explicit queue dispositions; no GPU execution."""
import pathlib,json,hashlib,re,time,collections
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control'
S=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def key(t):return hashlib.sha256(json.dumps([t.get('binary_sha256'),t.get('argv',[])[1:]],sort_keys=True).encode()).hexdigest()
sources=[];rows={};known_jobs={}
for p in (C/'capture_jobs').glob('*.json'):
 j=read(p)
 if 'task' in j:known_jobs[key(j['task'])]=j
def add(t,observation,state=None):
 k=key(t);o=rows.setdefault(k,{'content_id':k,'suite':t.get('suite'),'source_version':t.get('version',t.get('source_version')),'source_head':t.get('source_head'),'program':t.get('program'),'variant':t.get('variant'),'argv':t.get('argv'),'binary_sha256':t.get('binary_sha256'),'input_identity':t.get('input_files',t.get('input_identity')),'source_identity':t.get('source_files',t.get('sources',t.get('source'))),'observations':[],'native_evidence':[],'status':'NATIVE_NOT_YET_ACCEPTED','consumer_qualification':'NOT_GRANTED'})
 o['observations'].append(observation)
 if state:o['native_evidence'].append(state)
 if k in known_jobs:o.update(status='QUEUED',capture_job_id=known_jobs[k]['id'])
 return o
for name in ['RODINIA_EXACT_INPUT_QUEUE_V2.json','PARBOIL_EXACT_INPUT_QUEUE_V2.json','PARBOIL_SGEMM_HOST_RETURN_REPAIR_QUEUE_V1.json']:
 p=C/name;sources.append({'path':str(p),'sha256':sha(p),'count':len(read(p))})
 for t in read(p):add(t,{'manifest':str(p),'task_id':t.get('task_id')})
for p in [R/'native_control/NATIVE_BATCH_rodinia51_v1.json',C/'NATIVE_BATCH_parboil25_v2.json']:
 for n in read(p):
  t=n['task'];o=add(t,{'native_batch':str(p)}, {'receipt':str(pathlib.Path(n['output'])/'NATIVE_RECEIPT.json'),'exit':n.get('exit'),'status':n.get('status')})
  if n.get('exit',n.get('exit_code')) not in [0,None]:o['status']='NATIVE_FAILURE_RETAINED'
pending=read(C/'PENDING_SPECIAL_INPUT_QUEUE_V1.json')
for x in pending:
 o=add(x['task'],{'pending_queue':str(C/'PENDING_SPECIAL_INPUT_QUEUE_V1.json')});o.update(status='SPECIAL',special_reason=x['status'])
states=read(S/'manifests/ALL_NATIVE_ASSET_STATES_V1.json');candidates=read(S/'manifests/ALL_CAPTURE_CANDIDATES_PROFILE_PENDING_V1.json')
new=[];special=[];duplicates=0
prepared=read(C/'WORKER_V3_PREPARED.json')
late=C/'NATIVE_BATCH_parboil_late3_v1.json'
if late.exists():
 for n in read(late):
  t=n['task'];o=add(t,{'native_batch':str(late)}, {'receipt':str(pathlib.Path(n['output'])/'NATIVE_RECEIPT.json'),'exit':n.get('exit'),'status':n['status']})
  if key(t) in known_jobs:continue
  if n.get('exit')!=0:o['status']='NATIVE_FAILURE_RETAINED';continue
  ident='ORD_LATE_'+t['program']+'_'+key(t)[:12]+'_A001'
  j={'id':ident,'asset_id':ident,'task':t,'native_receipt':n,'numerical_policy':'CAPTURE_REFERENCE_CHECK_REQUIRED','allowed_capture_exits':[0]}
  p=C/'capture_jobs'/('LATE_'+ident+'.json')
  if not p.exists():p.write_text(json.dumps(j,indent=2)+'\n')
  q={'id':ident,'type':'CAPTURE_ORDINARY','job_path':str(p),'worker_script':prepared['path'],'worker_sha256':prepared['sha256'],'status':'PENDING','priority':10}
  new.append(q);known_jobs[key(t)]=j;o.update(status='QUEUED',capture_job_id=ident)
for t in candidates:
 state=t['native_state'];o=add(t,{'candidate_manifest':str(S/'manifests/ALL_CAPTURE_CANDIDATES_PROFILE_PENDING_V1.json'),'task_id':t.get('task_id')},state)
 if key(t) in known_jobs:duplicates+=1;continue
 flags=state.get('profile_flags',[])
 text=''
 for f in t.get('source_files',[]):
  p=pathlib.Path(f['path'])
  if p.suffix in ['.cu','.cpp','.c','.h']:text+=p.read_text(errors='replace')
 seeded=bool(re.search(r'srand\s*\(\s*(?:\([^)]*\)\s*)?time\s*\(',text))
 if flags or seeded or t.get('workload_kind') in ['RUNTIME_JIT_LOADED_CUBIN_IDENTITY_PENDING']:
  reason=flags+(['ACTUAL_TIME_SEEDED_INPUT_BYTES_NOT_FROZEN'] if seeded else [])
  o.update(status='SPECIAL',special_reason=reason)
  special.append({'content_id':key(t),'task':t,'status':'PENDING_SPECIALIST_EXTENSION','reason':reason});continue
 ident='ORD_EXT_'+re.sub('[^a-zA-Z0-9_.-]+','_',t['program'])+'_'+key(t)[:12]+'_A001'
 native=read(pathlib.Path(state['native_receipt']));assert sha(pathlib.Path(state['native_receipt']))==state['native_receipt_sha256']
 job={'id':ident,'asset_id':ident,'task':t,'native_receipt':native,'native_state':state,'numerical_policy':'NUMERICAL_UNVERIFIED_NATIVE_EVIDENCE_AVAILABLE','allowed_capture_exits':[0],'input_byte_identity_qualification':'FILES_FULL_SHA_AND_SOURCE_RULE;NO_UNRECORDED_SEED_ASSUMPTION'}
 p=C/'capture_jobs'/('EXT_'+ident+'.json')
 if not p.exists():p.write_text(json.dumps(job,indent=2)+'\n')
 else:assert read(p)==job
 q={'id':ident,'type':'CAPTURE_ORDINARY','job_path':str(p),'worker_script':prepared['path'],'worker_sha256':prepared['sha256'],'status':'PENDING','priority':20}
 new.append(q);known_jobs[key(t)]=job;o.update(status='QUEUED',capture_job_id=ident)
# Preserve every native attempt, including unavailable/API/negative, independently of content candidates.
attempts=[]
for state in states:
 d=state['capture_disposition'];status={'NO_SASS_EXPECTED_API_ONLY':'EXPLICIT_NO_KERNEL','NO_CUDA_WORK_CPU_CONFIGURATION':'EXPLICIT_NO_KERNEL','SINGLE_GPU_PLATFORM_UNAVAILABLE':'HARDWARE_UNAVAILABLE','CURRENT_HEADLESS_GL_CONTEXT_ADAPTER_REQUIRED':'SPECIAL','EXPECTED_DEVICE_ASSERT_DIAGNOSTIC_ONLY':'SPECIAL','FAILED_EXECUTION_DIAGNOSTIC_CAPTURE_ONLY':'NATIVE_FAILURE_RETAINED','NOT_EXECUTED_RETAINED':'NATIVE_NOT_EXECUTED'}.get(d,'CONTENT_CANDIDATE')
 attempts.append(dict(state,scope_status=status,content_id=key(state)))
new=[]
for p in sorted(list((C/'capture_jobs').glob('EXT_*.json'))+list((C/'capture_jobs').glob('LATE_*.json'))):
 j=read(p);new.append({'id':j['id'],'type':'CAPTURE_ORDINARY','job_path':str(p),'worker_script':prepared['path'],'worker_sha256':prepared['sha256'],'status':'PENDING','priority':10 if p.name.startswith('LATE_') else 20})
sources.extend({'path':str(p),'sha256':sha(p),'count':len(read(p))} for p in [S/'manifests/ALL_NATIVE_ASSET_STATES_V1.json',S/'manifests/ALL_CAPTURE_CANDIDATES_PROFILE_PENDING_V1.json',S/'manifests/SDK429_82_PROGRAM_VERSION_ROUTE_MATRIX_V1.json',S/'manifests/CUDA_SAMPLES_V118_FULL_DENOMINATOR_V1.json'])
report={'schema':'RTX4080_UNIFIED_SCOPE_STATUS_V1','utc_unix':time.time(),'scope':'Each exact binary+full argv identity; version/input/source observations retained; historical alias equivalence does not certify historical numerical identity','source_manifests':sources,'source_denominators':{'rodinia_3_1_families':23,'rodinia_2_0_ft_families':11,'rodinia_exact_invocations':51,'parboil_programs':11,'parboil_official_datasets':25,'polybench_programs':15,'cuda_official_sdk429_programs':82,'cuda_modern_v118_programs':73,'cuda_modern_official_invocations':103,'candidate_native_content':176,'all_cuda_poly_native_attempts':231},'contents':list(rows.values()),'native_attempts':attempts,'sdk429_program_routes':read(S/'manifests/SDK429_82_PROGRAM_VERSION_ROUTE_MATRIX_V1.json'),'cuda_v118_program_denominator':read(S/'manifests/CUDA_SAMPLES_V118_FULL_DENOMINATOR_V1.json'),'ordinary_new_queue_count':len(new),'existing_capture_content_duplicates':duplicates,'special_new_count':len(special),'capture_state_overlay_required':True}
for name,o in [('UNIFIED_SCOPE_STATUS.json',report),('ADDITIONAL_ORDINARY_CAPTURE_QUEUE_V1.json',new),('ADDITIONAL_SPECIAL_CAPTURE_QUEUE_V1.json',special)]:
 (C/name).write_text(json.dumps(o,indent=2)+'\n')
print(json.dumps({'content_rows':len(rows),'ordinary_new':len(new),'special_new':len(special),'duplicates':duplicates,'status_counts':dict(collections.Counter(x['status'] for x in rows.values()))}))
