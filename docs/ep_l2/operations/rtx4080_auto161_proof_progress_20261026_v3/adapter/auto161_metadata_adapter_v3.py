#!/usr/bin/env python3
"""Finite readonly CPU metadata adapter. Never launches GPU, subprocesses or simulations."""
import argparse,hashlib,json,os,pathlib,time,types
ADAPTER_ID='auto161_metadata_identity_static_v3'
PROFILE='AUTO161_READONLY_CPU_METADATA_V1'
SCOPE_SHA='b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a'
INDEX_SHA='16b323304b0d1af9cd77d1f1ae8298f2f96a93f6183617e9cbd6cb93ed19e4cc'
N=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1')
ROUTES={
 'READONLY_EXISTING_WORKLOAD_AVAILABILITY_ROUTE_REVIEW_NO_HISTORICAL_ALIAS':'WAIT_EXISTING_AVAILABILITY_REVIEW',
 'ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED':'WAIT_ISA_ADAPTER',
 'ACTUAL_INPUT_LIFETIME_SNAPSHOT_PREPARATION_REQUIRED':'WAIT_ACTUAL_INPUT_ADAPTER',
 'MAPPING_PROOF_HOLD':'WAIT_MAPPING_ADAPTER',
 'SDK42_DEFAULT50000_MICROWINDOW_ARMED_NOT_EXECUTED':'WAIT_ROOT_GPU_SDK_ARMED',
 'EXACT_RUNTIME_OR_STATIC_EVIDENCE_REVIEW_REQUIRED':'WAIT_SOURCE_RUNTIME_ADAPTER',
 'SOURCE_INPUT_ORACLE_AND_GPU_ADMISSION_REVIEW_REQUIRED':'WAIT_SOURCE_RUNTIME_ADAPTER',
 'ROOT_GPU_PILOT_REQUIRED_EXACT_SOURCE_BINARY':'WAIT_ROOT_GPU_EXACT',
 'SEPARATE_REPAIRED_VARIANT_GPU_REQUIRED_NO_V3_SUPERSESSION':'WAIT_ROOT_GPU_VARIANT'}
FAMILIES={'BRANCH_INDIRECT','CALL_ABS_INDIRECT','CALL_REL_RET_REL','OTHER_UNCLASSIFIED','TEX_FILTERED_ARRAY_2D','TLD_NONB_SCR','WARPSYNC','WARPSYNC_EXCLUSIVE'}
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def byte_sha(b):return hashlib.sha256(b).hexdigest()
class Reader:
 def __init__(self,allowed_root=N):self.root=pathlib.Path(allowed_root).resolve();self.refs=[];self.cache={};self.bytes=0
 def read(self,path,expected=None,max_bytes=2*2**20):
  p=pathlib.Path(path).resolve()
  if not p.is_relative_to(self.root):raise ValueError('READ_OUTSIDE_APPROVED_NAS_ROOT')
  if p.suffix.lower() not in {'.json','.py','.md','.c','.cc','.h','.patch','.txt','.log','.stdout','.stderr'}:raise ValueError('PAYLOAD_OR_EXECUTABLE_BODY_READ_FORBIDDEN')
  if str(p)in self.cache:b=self.cache[str(p)]
  else:
   size=p.stat().st_size
   if size>max_bytes or self.bytes+size>8*2**20:raise ValueError('SMALL_METADATA_READ_BOUND')
   b=p.read_bytes();self.bytes+=len(b);self.cache[str(p)]=b
   self.refs.append({'path':str(p),'sha256':byte_sha(b),'bytes':len(b)})
  if expected is not None and byte_sha(b)!=expected:raise ValueError('INPUT_SHA_MISMATCH')
  return b
 def obj(self,path,expected=None):return json.loads(self.read(path,expected))
 def refobj(self,ref):
  b=self.read(ref['path'],ref['sha256'])
  if len(b)!=ref['bytes']:raise ValueError('INPUT_LENGTH_MISMATCH')
  return json.loads(b)
def bind_core(row,projection,job):
 ir=projection['identity_row'];pr=projection['profile_row'];mr=projection.get('mapper_row');t=job['task'];qid=row['queue_id']
 checks=[]
 def check(name,ok,detail):
  checks.append({'name':name,'passed':bool(ok),'detail':detail})
  if not ok:raise ValueError('BINDING_FAILED:'+name)
 check('authority_exact_row',projection['scope_row']==row,'Exact frozen authority row equality, not label-only routing')
 check('identity_profile_queue_binding',ir['queue_id']==pr['queue_id']==qid,'Separate immutable identity and profile ledger rows')
 check('legacy_status_preserved',ir['original_queue_row']['status']==row['historical_queue_status'],'No historical queue write')
 check('job_preimage_binding',ir['job_evidence']['sha256']==pr['job_evidence']['sha256']==row['job_sha256'],'Job raw-byte SHA is independently reopened')
 check('binary_argv_match',t['binary_sha256']==row['binary_sha256']==ir['scientific_identity']['binary_sha256']==pr['binary_sha256'] and t['argv']==row['argv']==ir['scientific_identity']['argv']==pr['argv'],'Declared fields checked; actual binary bytes are a distinct Root attestation gate')
 legacy=hashlib.sha256(json.dumps(ir['scientific_identity'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 check('declared_identity_digest',legacy==ir['scientific_identity_sha256']==row['declared_identity_sha256'],'Legacy declared identity is not actual producer/profile/input equality')
 check('profile_family_identity',pr['profile_families']==row['profile_families_nonexclusive'],'Per-row family binding, not promotion from binary name')
 check('known_family_set',set(row['profile_families_nonexclusive'])<=FAMILIES,'Unknown family rejects')
 if mr:check('mapper_exact_identity',mr['id']==qid and mr['binary_sha256']==row['binary_sha256'],'Fresh mapper metadata joins exact binary SHA')
 check('route_known',row['next_step']in ROUTES,'Closed next-adapter ABI allowlist')
 return checks

BINARY_ATTESTATION_SCHEMA='EXACT161_CURRENT_BINARY_READONLY_ATTESTATION_V1'
BINARY_ATTESTATION_STATUS='MATCH_CLOSED_CURRENT_BINARY'
def validate_current_binary_attestation(ba,row,expected_scope_sha=SCOPE_SHA):
 if ba.get('schema')!=BINARY_ATTESTATION_SCHEMA:raise ValueError('BINARY_ATTESTATION_SCHEMA_REJECT')
 if ba.get('closed')is not True or ba.get('no_GPU')is not True or ba.get('scope_sha256')!=expected_scope_sha:raise ValueError('BINARY_ATTESTATION_NOT_EXACT_CLOSED_SCOPE')
 matches=[x for x in ba.get('rows',[])if x.get('path')==row['argv'][0]and x.get('expected_sha256')==row['binary_sha256']]
 if len(matches)!=1:raise ValueError('BINARY_ATTESTATION_EXACT_PATH_SHA_NOT_UNIQUE')
 r=matches[0]
 if r.get('status')!=BINARY_ATTESTATION_STATUS or r.get('actual_sha256')!=row['binary_sha256']:raise ValueError('BINARY_ATTESTATION_STATUS_OR_ACTUAL_SHA_REJECT')
 if not isinstance(r.get('source_ids'),list)or row['queue_id']not in r['source_ids']:raise ValueError('BINARY_ATTESTATION_SOURCE_ID_REJECT')
 return r

def evaluate(row,projection,job,index,reader):
 checks=bind_core(row,projection,job);qid=row['queue_id'];next_stage=ROUTES[row['next_step']]
 binding={'queue_id':qid,'job_sha256':row['job_sha256'],'binary_sha256':row['binary_sha256'],'argv_sha256':digest(row['argv']),'declared_identity_sha256':row['declared_identity_sha256']}
 missing=[];families=[];requests=[];facts={}
 def need(proof_id,evidence,adapter,extra=None):
  x={'proof_id':proof_id,'binding':dict(binding),'required_evidence':evidence,'next_adapter_id':adapter,'next_adapter_ABI':'AUTO161_ARTIFACT_V1','satisfied':False}
  if extra:x.update(extra)
  missing.append(x)
 def checked(name,ok,detail):
  checks.append({'name':name,'passed':bool(ok),'detail':detail})
  if not ok:raise ValueError('EVIDENCE_FAILED:'+name)
 # Existing actual current-binary hash proof is distinct from declared-job hashes.
 ba=reader.refobj(index['root_binary_attestation'])
 br=validate_current_binary_attestation(ba,row,SCOPE_SHA)
 checked('Root_binary_attestation_closed_schema',ba['schema']==BINARY_ATTESTATION_SCHEMA,'Exact real receipt schema; no status aliases accepted')
 checked('actual_binary_attestation_exact_path_sha_source_id',br['status']==BINARY_ATTESTATION_STATUS and qid in br['source_ids'],'Exact path+expectedSHA+queue source ID; no fresh binary-body read by this worker')
 facts['actual_binary']={'status':'MATCH_IN_CLOSED_ROOT_ATTESTATION','bytes':br['bytes'],'actual_sha256':br['actual_sha256'],'actual_executable_bytes_read_this_worker':False}
 # A closed static summary reuses a single fresh metadata rehash from preparation time.
 ssref=projection.get('static_summary_ref')
 if ssref:
  ss=reader.refobj(ssref);checked('closed_static_summary_binary',ss['summary_binary_sha256']==row['binary_sha256'],'Exact binary-scoped summary')
  m=projection.get('mapper_row')or{}
  if ss.get('source_manifest_ref'):
   checked('prior_static_manifest_SHA_chain',ss['source_manifest_ref']['sha256']==m.get('manifest_sha256')and ss.get('manifest_binary_bound')and ss.get('instruction_count',0)>0,'Underlying static manifest read+SHA once at shared freeze; this row reads its closed summary only')
   facts['static_metadata']={'mode':'SHARED_CLOSED_SMALL_METADATA_REUSE','manifest_sha256':ss['source_manifest_ref']['sha256'],'instructions':ss['instruction_count'],'image_count':len(ss['cubins']),'fresh_full_static_manifest_read_this_worker':False,'trace_body_read':False}
  else:
   need('COMPLETE_STATIC_MAP_METADATA_OR_ERROR_REPAIR',['closed manifest/map binary SHA','all listed cubins and full nonNOP PC/owner closure','exact failure resolution without synthesized register rows'],'auto161_mapping_cpu_prepare_v1')
  facts['mapping_error']=ss.get('error');facts['unsupported_opcodes']=ss.get('unsupported_opcodes')
 else:
  need('EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF',['existing mapper manifest raw SHA and binary binding','independent full image/owner/PC closure or retained exact error'],'auto161_mapping_cpu_prepare_v1')
 # Instruction families remain exact application dependencies.
 for family in row['profile_families_nonexclusive']:
  key=family+':'+row['binary_sha256']+':'+digest(row['argv']);families.append(key)
  gap=row['profile_family_gaps'].get(family)
  checked('family_gap_'+family,isinstance(gap,dict)and bool(gap.get('gap')),'Explicit family qualification gap required for this row')
  need('ISA_'+family,['exact binary/argv/source+all-loaded module/owner scope','whole launch/CTA/warp/EOF closure',gap['gap'],'new producer and independent consumer CPU/dynamic evidence; no old-profile application promotion'],'auto161_isa_family_cpu_prepare_v1',{'family_key':key,'current_gap':gap['gap']})
 if row['profile_families_nonexclusive']:
  ga=index['gaussian'];reader.refobj(ga['manifest']);reader.refobj(ga['commit']);g=reader.refobj(ga['spec'])
  for fr in ga['small_closed_evidence']:reader.read(fr['path'],fr['sha256'])
  exact=(row['binary_sha256']==ga['expected_binary']and row['argv']==ga['expected_argv'])
  facts['Gaussian_REL_RET_CPU_candidate']={'applicable_to_this_exact_binary_argv':exact,'profile':ga['profile'],'phase':'CPU_CANDIDATE_ONLY_DYNAMIC_REQUIRED','scope_not_promoted_to_family':True,'SO_body_rehashed_this_worker':False,'dynamic_proof_present':False}
  checked('Gaussian_candidate_scope_not_widened',g['binary_sha256']==ga['expected_binary']and g['exact_argv']==ga['expected_argv'],'General family dependency only unless exact Gaussian-s16 binding')
  if exact:need('GAUSSIAN16_EXACT_DYNAMIC_CONTROL_PROOF',g['dynamic_required'],'auto161_gaussian16_dynamic_request_v1',{'root_GPU_window_required':True})
 # Reexecute the Root-reviewed pure comparator for exactly three frozen C8 metadata routes.
 if projection.get('existing_route'):
  r=projection['existing_route'];accept=reader.refobj(index['root_receipts']['comparator'])
  checked('comparator_Root_readonly_acceptance',accept['status']=='PASS_FOR_READONLY_GOAL_AUDIT_ONLY','Read-only routes only; no historical/input/producer equivalence')
  code=reader.read(index['comparator_source']['path'],index['comparator_source']['sha256']);mod=types.ModuleType('closed_comparator');exec(compile(code,index['comparator_source']['path'],'exec'),mod.__dict__)
  right=reader.refobj(r['side_ref'])
  for fr in r['member_refs'].values():reader.read(fr['path'],fr['sha256'])
  result=mod.compare({'task':job['task'],'old_hold_status':row['historical_queue_status']},right)
  checked('pure_comparator_existing_route',result['availability_route']=='WORKLOAD_AVAILABILITY_ROUTE_ONLY_NO_HISTORICAL_EQUIVALENCE'and not result['historical_equivalence']and not result['observed_input_bytes']['equal_observed_supported_scope_only'],'Actual metadata closure recomputed; trace/input payload not read')
  facts['existing_route']={'asset_id':r['asset_id'],'availability_route':result['availability_route'],'declared_workload_equal':result['declared_workload_identity']['equal'],'actual_capture_profile_equal':result['actual_capture_profile']['equal'],'historical_input_equal':False}
  need('ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION',['explicit availability-only selection','historical input/profile equivalence must remain ungranted'],'auto161_availability_route_review_v1')
 # Current SDK controller is reused as an entry; no second controller is constructed.
 if next_stage=='WAIT_ROOT_GPU_SDK_ARMED':
  arm=reader.refobj(index['sdk_arm']);acc=reader.refobj(index['root_receipts']['window'])
  checked('SDK_existing_Root_armed_entry',arm['status']=='ARMED_WAITING_CURRENT_WHOLE_JOB'and acc['status']=='ROOT_REVIEWED_ADMITTED_EXACT_SDK42_DEFAULT50000_BOUNDARY_WINDOW_ONCE','Frozen armed receipt; not a claim of present PID state or new GPU completion')
  checked('SDK_declared_default50k_binding',row.get('window_job_id')=='C8_SDK42_VECTOR_DEFAULT50000_SPECIALIST_A001'and len(row['argv'])==1,'Declared exact binary+argv only; old actual input equality false')
  facts['existing_SDK_entry']={'controller':arm['controller'],'run_directory':arm['run_directory'],'new_controller_started':False,'receipt_only_not_live_PID_observation':True}
  need('SDK_EXISTING_WINDOW_TERMINAL_CLOSED',['existing controller exact ACK and terminal','observed supported HtoD bytes/lifetime and producer closure','independent cleanup then original exact33 resume ACK'],'auto161_existing_sdk_window_refresh_v1')
 # Original-source candidates and explicit repaired variant remain separate.
 if projection.get('prepared_mapper_candidate'):
  cand=projection['prepared_mapper_candidate'];acc=reader.refobj(index['root_receipts']['mapper']);ms=reader.refobj(index['mapper_scope'])
  checked('Root_static_acceptance_no_GPU',acc['status']=='ROOT_STATIC_REVIEW_AND_INDEPENDENT_12_CPU_CASES_PASS_GPU_NOT_ADMITTED','12 independent CPU cases; no GPU grant inherited')
  for fr in index['mapper_codes']:reader.read(fr['path'],fr['sha256'])
  proof=reader.refobj(projection['prepared_mapper_proof'])
  checked('prepared_exact_new_job_binding',cand in ms['rows']and cand['binary_sha256']==row['binary_sha256']and cand['legacy_id']==qid and cand['job_sha256']==row['new_candidate']['job_sha256'],'New A002 distinct from immutable old row')
  checked('prepared_static_image_metadata',proof['binary_sha256']==row['binary_sha256']and proof['images']==len(proof['ordinal_rows'])and all(x['full_dump_exact']for x in proof['ordinal_rows']),'Per-binary ordinal static proof metadata; no new liveness run')
  facts['prepared_mapper_candidate']={'id':cand['id'],'variant_class':cand['variant_class'],'input_policy':cand['input_policy'],'qualification':'STATIC_CPU_PREPARATION_ONLY'}
  need('ROOT_EXACT_NEW_GPU_GRANT_AND_FULL_CAPTURE',['Root exact new job/worker/proof grant and natural safe boundary','actual loaded/JIT and exact whole application full-record closure','numerical QA and immutable sender/receiver COMMIT'],'auto161_exact_gpu_request_prepare_v1',{'root_GPU_window_required':True,'separate_variant':next_stage=='WAIT_ROOT_GPU_VARIANT'})
 ip=row.get('input_preparation')
 if ip:
  need('ACTUAL_APPLICATION_INPUT_LIFETIME_SNAPSHOT',['exact source/binary/argv and library identities','all supported source copy bytes length/SHA/order/API success/lifetime','explicit launch bank0/Memset/D2D/symbol/managed/mapped/external coverage',ip.get('snapshot_scope','scope must be declared'),'source-aware whole application numerical oracle; seed is not actual byte equality'],'auto161_actual_input_cpu_prepare_v1',{'origin':ip.get('origin'),'size_bound':ip.get('size_bound'),'snapshot_scope':ip.get('snapshot_scope')})
 if next_stage=='WAIT_MAPPING_ADAPTER':
  error=(projection.get('mapper_row')or{}).get('error')or'Existing mapping proof incomplete'
  need('EXACT_MAPPING_REPAIR_WITH_NEGATIVE_REGRESSION',['error:'+error,'exact binary+all-image extraction proof','no missing nonNOP PLR, owner ambiguity or false static PASS'],'auto161_mapping_cpu_prepare_v1')
 if next_stage=='WAIT_SOURCE_RUNTIME_ADAPTER':
  program=row['program'];detail='full source/input initialization and runtime loaded/oracle proof'
  if program=='GESUMMV':detail='B allocated and kernel-read without init(A,x) covering B; preserve original failed identity'
  elif program=='FDTD-2D':detail='original v3 wrong ex stride/ghost boundaries; corrected v4 is a distinct source/binary identity'
  elif program in {'3DCONV','ATAX','BICG','2MM'}:detail='uninitialized output buffers copied HtoD require complete source read-before-write dominance or actual byte proof'
  elif program=='asyncAPI':detail='source stream/event/completion ordering and actual async input lifetime profile'
  need('SOURCE_RUNTIME_ORACLE_EXACT_PROOF',[detail,'source SHA-bound path/branch and complete input read set','exact numerical oracle and observed all-launch coverage'],'auto161_source_runtime_cpu_prepare_v1')
 # Explicit requests make subsequent work executable by ABI, not a status-only placeholder.
 for x in missing:
  requests.append({'adapter_id':x['next_adapter_id'],'ABI':x['next_adapter_ABI'],'target_queue_ids':[qid],'family_keys':[x['family_key']]if x.get('family_key')else [],'requires_proof_id':x['proof_id'],'input_binding':x['binding'],'provided_gates_must_remain_CPU_only':True,'next_stage':next_stage})
 if not missing:need('ROOT_RESEARCH_REVIEW_STILL_REQUIRED',['Root decision on exact metadata audit; no inferred historical or runtime qualification'],'auto161_source_runtime_cpu_prepare_v1')
 return {'checks':checks,'facts':facts,'missing_proofs':missing,'family_keys':families,'dependency_requests':requests,'next_stage':next_stage}
def consume_approved_CPU_artifacts(ctx,row,reader):
 refs=ctx.get('dependency_artifacts',[])
 if not refs:return {'closed_CPU_candidate_gates':[],'research_dependencies':[],'requires_missing':[],'checked_artifact_count':0}
 registry=reader.refobj(ctx['allowlist_ref'])
 if registry.get('schema')!='AUTO161_ALLOWLIST_V1':raise ValueError('ARTIFACT_ALLOWLIST_SCHEMA')
 all_sha={x['sha256']for x in refs};closed=[];research=[];requires_missing=[]
 for ref in refs:
  doc=reader.refobj(ref)
  if doc.get('schema')!='AUTO161_ARTIFACT_V1':raise ValueError('ARTIFACT_SCHEMA_REJECT')
  producer=registry.get('artifact_producers',{}).get(doc.get('producer_id'))
  if not isinstance(producer,dict)or doc.get('profile')!=producer.get('profile'):raise ValueError('ARTIFACT_PRODUCER_PROFILE_REJECT')
  if doc.get('producer_source_sha256')!=producer.get('source_sha256'):raise ValueError('ARTIFACT_PRODUCER_CODE_PIN_REJECT')
  reader.read(producer['source_path'],producer['source_sha256'])
  if doc.get('status')not in {'PASS','HOLD'}:raise ValueError('ARTIFACT_STATUS_REJECT')
  for flag in ['qualification_granted','gpu_executed','historical_queue_mutated']:
   if doc.get(flag)is not False:raise ValueError('ARTIFACT_FORBIDDEN_OR_MISSING_FLAG:'+flag)
  for flag in ['simulation_executed','consumer_qualified','science_qualified','trace_qualified']:
   if doc.get(flag,False)is not False:raise ValueError('ARTIFACT_FORBIDDEN_FLAG:'+flag)
  gates=doc.get('provided_gates')
  if not isinstance(gates,list)or not set(gates)<=set(producer.get('allowed_gates',[])):raise ValueError('ARTIFACT_GATE_NOT_ALLOWLISTED')
  if doc.get('next_stage')not in producer.get('allowed_next_stages',[])or doc['next_stage']not in set(ROUTES.values()):raise ValueError('ARTIFACT_NEXT_STAGE_NOT_ALLOWLISTED')
  ev=doc.get('evidence')
  if not isinstance(ev,list)or not ev:raise ValueError('ARTIFACT_REAL_EVIDENCE_REFS_REQUIRED')
  for x in ev:
   data=reader.read(x['path'],x['sha256'])
   if len(data)!=x['bytes']:raise ValueError('ARTIFACT_EVIDENCE_LENGTH')
  requires=doc.get('requires',[])
  if not isinstance(requires,list)or any(not isinstance(h,str)or len(h)!=64 or any(c not in '0123456789abcdef'for c in h)for h in requires):raise ValueError('ARTIFACT_REQUIRES_SHA_FORMAT')
  unresolved=sorted(set(requires)-all_sha);requires_missing.extend(unresolved)
  targets=doc.get('target_queue_ids',[]);bindings=doc.get('row_bindings',{})
  if not isinstance(targets,list)or not isinstance(bindings,dict):raise ValueError('ARTIFACT_TARGET_BINDING_FORMAT')
  qid=row['queue_id'];exact=qid in targets and bindings.get(qid)==digest(row)
  if qid in targets and not exact:raise ValueError('ARTIFACT_EXACT_ROW_BINDING_REJECT')
  record={'artifact_sha256':ref['sha256'],'producer_id':doc['producer_id'],'profile':doc['profile'],'provided_gates':gates,'status':doc['status'],'exact_row_bound':exact,'requires_missing':unresolved,'next_stage':doc['next_stage'],'application_or_dynamic_qualification':False}
  if exact and not unresolved and doc['status']=='PASS':
   for gate in gates:closed.append(dict(record,gate=gate))
  else:research.append(record)
 return {'closed_CPU_candidate_gates':closed,'research_dependencies':research,'requires_missing':sorted(set(requires_missing)),'checked_artifact_count':len(refs),'dynamic_missing_proofs_removed':False}


# Only these reviewed CPU gates may discharge typed metadata requirements.
# Dynamic/ISA/input/runtime proofs are never matched by a generic gate name.
CPU_PROOF_RULES={
 ('AUTO161_EXISTING_STATIC_REOPEN_CPU_V1','AUTO161_EXISTING_STATIC_METADATA_REOPEN_CPU_V1','EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF'):'EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF',
 ('AUTO161_C8_AVAILABILITY_REVIEW_ADAPTER_V1','AUTO161_EXISTING_C8_AVAILABILITY_REVIEW_V1','EXISTING_C8_AVAILABILITY_METADATA_REVIEW_CLOSED_V1'):'ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION'}
def resolve_CPU_proofs(row,result,feedback):
 original=json.loads(json.dumps(result['missing_proofs']))
 byproof={}
 for gate in feedback['closed_CPU_candidate_gates']:
  rule=(gate['producer_id'],gate['profile'],gate['gate'])
  proof=CPU_PROOF_RULES.get(rule)
  if proof:
   byproof.setdefault(proof,[]).append(gate)
 removed=[];remaining=[]
 for proof in original:
  candidates=byproof.get(proof['proof_id'],[])
  if candidates:
   # Sorting makes duplicate equivalent evidence independent of INDEX order.
   gate=sorted(candidates,key=lambda x:x['artifact_sha256'])[0]
   removed.append({'proof_id':proof['proof_id'],'artifact_sha256':gate['artifact_sha256'],'producer_id':gate['producer_id'],'profile':gate['profile'],'CPU_only':True})
  else:remaining.append(proof)
 next_stage=ROUTES[row['next_step']]
 if next_stage=='WAIT_EXISTING_AVAILABILITY_REVIEW' and 'ROOT_AVAILABLE_WORKLOAD_ROUTE_DECISION' in {x['proof_id']for x in removed}:
  next_stage='WAIT_SOURCE_RUNTIME_ADAPTER'
  if not any(x['proof_id']=='SOURCE_RUNTIME_ORACLE_EXACT_PROOF'for x in remaining):
   remaining.append({'proof_id':'SOURCE_RUNTIME_ORACLE_EXACT_PROOF','binding':{'queue_id':row['queue_id'],'job_sha256':row['job_sha256'],'binary_sha256':row['binary_sha256'],'argv_sha256':digest(row['argv']),'declared_identity_sha256':row['declared_identity_sha256']},'required_evidence':['Selected actual C8 producer/profile and observed supported HtoD scope remain distinct from old input/profile','Exact source initialization, all-loaded runtime/input read set and numerical oracle','Independent consumer/native compatibility; no full CUDA state from host-source capsules'],'next_adapter_id':'auto161_source_runtime_cpu_prepare_v1','next_adapter_ABI':'AUTO161_ARTIFACT_V1','satisfied':False})
 if not remaining:raise ValueError('CPU_PROOF_RESOLUTION_CANNOT_GRANT_TRACE_OR_UNQUALIFIED_COMPLETION')
 requests=[]
 for x in remaining:
  requests.append({'adapter_id':x['next_adapter_id'],'ABI':x['next_adapter_ABI'],'target_queue_ids':[row['queue_id']],'family_keys':[x['family_key']]if x.get('family_key')else [],'requires_proof_id':x['proof_id'],'input_binding':x['binding'],'provided_gates_must_remain_CPU_only':True,'next_stage':next_stage})
 result['original_missing_proofs']=original
 result['cpu_resolved_proofs']=removed
 result['missing_proofs']=remaining
 result['dependency_requests']=requests
 result['next_stage']=next_stage
 result['facts']['proof_progress_policy']={'schema':'AUTO161_EXACT_CPU_PROOF_PROGRESS_V3','CPU_only_removed_proof_ids':sorted(x['proof_id']for x in removed),'artifact_next_stage_hints_are_routing_authority':False,'remaining_dynamic_ISA_input_runtime_proofs_preserved':True,'ordering_independent':True}
 return result

def run(args):
 start=time.time();cpu=time.process_time();reader=Reader()
 ctx=reader.obj(args.context_json)
 output=pathlib.Path(args.output).resolve();attempt=pathlib.Path(ctx['attempt_directory']).resolve()
 if output!=pathlib.Path(ctx['output_path']).resolve()or output.parent!=attempt or output.name!='RESULT.json':raise ValueError('OUTPUT_CONTEXT_BINDING')
 if not attempt.is_relative_to(N.resolve()):raise ValueError('ATTEMPT_OUTSIDE_NAS')
 scope_raw=reader.read(args.scope_json,SCOPE_SHA);scope=json.loads(scope_raw)
 if len(scope['rows'])!=161 or not 0<=args.row_index<161:raise ValueError('EXACT_SCOPE_SIZE_OR_INDEX')
 row=scope['rows'][args.row_index]
 if ctx['schema']!='AUTO161_CONTEXT_V1' or ctx['queue_id']!=row['queue_id'] or ctx['row_index']!=args.row_index or ctx['stage']!='METADATA_IDENTITY_STATIC':raise ValueError('CONTEXT_ROW_STAGE_BINDING')
 if ctx['scope_sha256']!=SCOPE_SHA or ctx['frozen_row_sha256']!=digest(row):raise ValueError('CONTEXT_SCOPE_OR_ROW_SHA')
 if ctx['adapter_id']!=ADAPTER_ID or ctx['adapter_profile']!=PROFILE:raise ValueError('UNKNOWN_ADAPTER_OR_PROFILE')
 source=reader.read(pathlib.Path(__file__),ctx['adapter_source_sha256'])
 idx=reader.obj(pathlib.Path(__file__).with_name('FROZEN_AUTHORITY_INDEX_V2.json'),INDEX_SHA)
 item=idx['rows'][args.row_index]
 if item['queue_id']!=row['queue_id']or item['frozen_row_sha256']!=digest(row):raise ValueError('FROZEN_PROJECTION_INDEX_BINDING')
 projection=reader.refobj(item['projection_ref'])
 jr=projection['identity_row']['job_evidence'];job=reader.obj(jr['snapshot'],row['job_sha256'])
 artifact_feedback=consume_approved_CPU_artifacts(ctx,row,reader)
 result=evaluate(row,projection,job,idx,reader)
 result=resolve_CPU_proofs(row,result,artifact_feedback)
 result['facts']['CPU_artifact_feedback']=artifact_feedback
 result['facts']['closed_CPU_candidate_gates']=artifact_feedback['closed_CPU_candidate_gates']
 result['checks'].append({'name':'context_dependency_artifacts_reopened_and_exact_CPU_scoped','passed':True,'detail':'All supplied approved refs/source/evidence SHA rechecked; family-only dependencies never grant exact application gates'})
 if artifact_feedback['requires_missing']:
  result['missing_proofs'].append({'proof_id':'CPU_ARTIFACT_DEPENDENCY_CLOSURE','binding':{'queue_id':row['queue_id'],'binary_sha256':row['binary_sha256'],'argv_sha256':digest(row['argv'])},'required_evidence':artifact_feedback['requires_missing'],'next_adapter_id':'auto161_artifact_dependency_refresh_v1','next_adapter_ABI':'AUTO161_ARTIFACT_V1','satisfied':False})
 out={'schema':'AUTO161_ADAPTER_RESULT_V1','adapter_id':ADAPTER_ID,'adapter_profile':PROFILE,'profile':PROFILE,'attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'queue_id':row['queue_id'],'row_index':args.row_index,'scope_sha256':SCOPE_SHA,'frozen_row_sha256':digest(row),'stage':'METADATA_IDENTITY_STATIC','status':'HOLD'if result['missing_proofs']else'PASS','stage_execution_complete':True,'checks':result['checks'],'inputs':reader.refs,'evidence':[],'original_missing_proofs':result['original_missing_proofs'],'cpu_resolved_proofs':result['cpu_resolved_proofs'],'missing_proofs':result['missing_proofs'],'family_keys':result['family_keys'],'dependency_requests':result['dependency_requests'],'next_stage':result['next_stage'],'facts':result['facts'],'qualification_granted':False,'historical_queue_mutated':False,'gpu_executed':False,'simulation_executed':False,'trace_body_read':False,'input_payload_body_read':False,'historical_actual_input_equality_granted':False,'actual_GPU_producer_profile_inferred_from_legacy55':False,'execution_evidence':{'pid':os.getpid(),'started_unix':start,'ended_unix':time.time(),'cpu_seconds':time.process_time()-cpu,'actual_distinct_file_reads':len(reader.refs),'actual_metadata_bytes_read':reader.bytes,'operations':['raw_sha256_and_exact_row_bind','Root_binary_attestation_lookup','profile_missing_proof_derivation','closed_static_or_error_validation','specific_next_adapter_dependency_construction']},'shared_evidence_policy':'Existing closed evidence reused explicitly; no claim of per-row new payload/executable/static-body hash'}
 with output.open('x')as f:json.dump(out,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--scope-json',required=True);p.add_argument('--row-index',required=True,type=int);p.add_argument('--output',required=True);p.add_argument('--context-json',required=True);args=p.parse_args()
 result=run(args)
 # No context nonce or scientific data is emitted to stdout.
 print(json.dumps({'schema':result['schema'],'queue_id':result['queue_id'],'stage':result['stage'],'status':result['status'],'qualification_granted':False}))
if __name__=='__main__':main()
