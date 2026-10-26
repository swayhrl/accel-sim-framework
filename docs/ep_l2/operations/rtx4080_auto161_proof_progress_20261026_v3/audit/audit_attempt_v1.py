#!/usr/bin/env python3
"""Independent exact-stage evidence checks. Does not import orchestrator validation."""
import hashlib,pathlib,time
from audit_common_v1 import AuditError,need,canonical,process_key,no_qualification,proc_identity
from check_frozen_identity_inputs_v1 import verify_identity_inputs
STAGE='METADATA_IDENTITY_STATIC'
PROFILE='AUTO161_READONLY_CPU_METADATA_V1'
WAITS={'WAIT_EXISTING_AVAILABILITY_REVIEW','WAIT_ISA_ADAPTER','WAIT_ACTUAL_INPUT_ADAPTER','WAIT_MAPPING_ADAPTER','WAIT_SOURCE_RUNTIME_ADAPTER','WAIT_ROOT_GPU_EXACT','WAIT_ROOT_GPU_VARIANT','WAIT_ROOT_GPU_SDK_ARMED'}
ROUTES={'READONLY_EXISTING_WORKLOAD_AVAILABILITY_ROUTE_REVIEW_NO_HISTORICAL_ALIAS':'WAIT_EXISTING_AVAILABILITY_REVIEW','ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED':'WAIT_ISA_ADAPTER','ACTUAL_INPUT_LIFETIME_SNAPSHOT_PREPARATION_REQUIRED':'WAIT_ACTUAL_INPUT_ADAPTER','MAPPING_PROOF_HOLD':'WAIT_MAPPING_ADAPTER','SDK42_DEFAULT50000_MICROWINDOW_ARMED_NOT_EXECUTED':'WAIT_ROOT_GPU_SDK_ARMED','EXACT_RUNTIME_OR_STATIC_EVIDENCE_REVIEW_REQUIRED':'WAIT_SOURCE_RUNTIME_ADAPTER','SOURCE_INPUT_ORACLE_AND_GPU_ADMISSION_REVIEW_REQUIRED':'WAIT_SOURCE_RUNTIME_ADAPTER','ROOT_GPU_PILOT_REQUIRED_EXACT_SOURCE_BINARY':'WAIT_ROOT_GPU_EXACT','SEPARATE_REPAIRED_VARIANT_GPU_REQUIRED_NO_V3_SUPERSESSION':'WAIT_ROOT_GPU_VARIANT'}
def admission_for(row,index,scope_sha):
 value={'schema':'AUTO161_ADMISSION_V1','queue_id':row['queue_id'],'row_index':index,'scope_sha256':scope_sha,'frozen_row_sha256':canonical(row)}
 return dict(value,admission_sha256=canonical(value))
def exact_ref(reader,ref,path):
 need(pathlib.Path(ref['path'])==pathlib.Path(path),'CROSS_ATTEMPT_OR_WRONG_EVIDENCE_PATH',ref)
 return reader.refobj(ref)
def same(field,*objects):
 need(all(field in o for o in objects),'MISSING_BINDING_FIELD',field)
 need(all(o[field]==objects[0][field] for o in objects[1:]),'BINDING_MISMATCH',field)
def audit_attempt(reader,directory,admission,row,allow,runner_sha,parent_identity=None,live_probe=proc_identity,permitted_next_stages=None,require_authority_projection=True):
 directory=pathlib.Path(directory)
 intent=reader.obj(directory/'INTENT.json');ctx=exact_ref(reader,intent['context_ref'],directory/'CONTEXT.json')
 expected={'queue_id':admission['queue_id'],'row_index':admission['row_index'],'scope_sha256':admission['scope_sha256'],'frozen_row_sha256':admission['frozen_row_sha256'],'stage':STAGE}
 for key,value in expected.items():need(ctx.get(key)==value,'CONTEXT_ROW_STAGE_SCOPE_MISMATCH',key)
 need(ctx.get('admission_sha256')==admission['admission_sha256'],'CONTEXT_ADMISSION_MISMATCH')
 need(ctx.get('attempt_directory')==str(directory),'WRONG_ATTEMPT_DIRECTORY')
 need(ctx.get('adapter_profile')==allow['profile']==PROFILE,'WRONG_PROFILE')
 need(ctx.get('adapter_path')==allow['path'],'UNKNOWN_ADAPTER_PATH')
 need(ctx.get('adapter_source_sha256')==allow['sha256'],'UNKNOWN_ADAPTER_SHA')
 need(hashlib.sha256(reader.bytes(allow['path'])).hexdigest()==allow['sha256'],'ADAPTER_SOURCE_CHANGED')
 need(intent.get('adapter_id')==allow['id'],'UNKNOWN_ADAPTER_ID')
 need(intent.get('runner_source_sha256')==runner_sha,'UNKNOWN_RUNNER_SHA')
 for key in ['attempt_id','queue_id','stage','input_fingerprint','slot_id','adapter_source_sha256']:
  same(key,intent,ctx)
 # The fixed stage execution context binds a fresh nonce; logs cannot substitute for a result.
 nonce=ctx.get('nonce');need(isinstance(nonce,str) and len(nonce)>=16,'MISSING_ATTEMPT_NONCE')
 need(intent.get('nonce',intent.get('start_nonce'))==nonce,'INTENT_NONCE_MISMATCH')
 need(isinstance(ctx['input_fingerprint'],str) and len(ctx['input_fingerprint'])==64,'INVALID_INPUT_FINGERPRINT')
 fp=canonical({'admission':admission['admission_sha256'],'stage':STAGE,'adapter_sha256':allow['sha256'],'artifacts':ctx.get('dependency_artifacts',[]),'missing_dependencies':ctx.get('missing_dependency_sha256',[])})
 need(ctx['input_fingerprint']==fp,'INPUT_FINGERPRINT_CHANGED')
 ordinal=ctx['attempt_id'].rsplit('_',1)[-1]
 need(ordinal in ('1','2','3') and ctx['attempt_id']==admission['admission_sha256'][:12]+'_'+fp[:12]+'_'+ordinal,'ATTEMPT_ID_OR_RETRY_BOUND_CHANGED')
 need(ctx['slot_id'] in (0,1),'CPU_SLOT_OUTSIDE_TWO')
 no_qualification(intent);no_qualification(ctx)
 start_path=directory/'PROCESS_START.json';exec_path=directory/'EXECUTION.json';ack_path=directory/'ACK.json'
 if not start_path.exists():
  need(not exec_path.exists() and not ack_path.exists(),'ACK_OR_EXEC_WITHOUT_PROCESS_START')
  if (directory/'RECOVERY_CLOSED.json').exists():
   closed=reader.obj(directory/'RECOVERY_CLOSED.json')
   need(closed.get('schema')=='AUTO161_RECOVERY_CLOSURE_V1' and closed.get('attempt_id')==ctx['attempt_id'] and closed.get('worker_live') is False and closed.get('stage_execution_complete') is False and closed.get('reason')=='DEAD_INCOMPLETE_ATTEMPT_NOT_STAGE_EXECUTED','WRONG_NO_START_RECOVERY_CLOSURE')
   exact_ref(reader,closed['context_ref'],directory/'CONTEXT.json')
   need(closed.get('process_start_ref') is None and closed.get('closed_monotonic_ns',0)>0,'FABRICATED_PROCESS_START_IN_RECOVERY')
   launch=directory/'LAUNCH.json'
   if launch.exists():
    proof=exact_ref(reader,closed['launch_ref'],launch)['worker'];need(process_key(proof)==process_key(closed['worker_proof']),'RECOVERY_LAUNCH_PID_MISMATCH')
    live=live_probe(proof['pid']);need(live is None or process_key(live)!=process_key(proof) or live.get('state') in ('Z','X'),'LIVE_LAUNCH_CANNOT_BE_RECOVERED')
   else:need(closed.get('launch_ref') is None and closed.get('worker_proof') is None,'FABRICATED_RECOVERY_WORKER')
   need((directory/'FAILURE.json').exists(),'RECOVERY_FAILURE_RECEIPT_MISSING');reader.obj(directory/'FAILURE.json')
   return {'status':'RECOVERY_CLOSED_NOT_EXECUTED','queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':False}
  return {'status':'AWAIT_EXECUTION','queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':False}
 start=reader.obj(start_path)
 same('attempt_id',start,ctx);same('nonce',start,ctx);same('slot_id',start,ctx)
 need(start.get('schema')=='AUTO161_PROCESS_START_V1','WRONG_PROCESS_START_SCHEMA')
 need(start.get('adapter_source_sha256')==allow['sha256'] and start.get('runner_source_sha256')==runner_sha,'START_TOOL_PIN_MISMATCH')
 exact_ref(reader,start['context_ref'],directory/'CONTEXT.json')
 worker=process_key(start['worker']);parent=process_key(start['parent'])
 need(worker[0]==parent[0] and worker!=parent,'INVALID_PROCESS_PARENT')
 if parent_identity is not None:need(parent==process_key(parent_identity),'WRONG_ORCHESTRATOR_PARENT_IDENTITY')
 need(start['worker'].get('parent_pid',parent[1])==parent[1],'WRONG_WORKER_PARENT_PID')
 if not exec_path.exists():
  need(not ack_path.exists(),'ACK_WITHOUT_EXECUTION')
  closure_path=directory/'RECOVERY_CLOSED.json'
  if closure_path.exists():
   closure=reader.obj(closure_path)
   need(closure.get('schema')=='AUTO161_RECOVERY_CLOSURE_V1' and closure.get('attempt_id')==ctx['attempt_id'],'WRONG_RECOVERY_CLOSURE')
   need(closure.get('worker_live') is False and closure.get('stage_execution_complete') is False and closure.get('reason')=='DEAD_INCOMPLETE_ATTEMPT_NOT_STAGE_EXECUTED','CRASH_CLOSURE_MISREPORTS_EXECUTION')
   exact_ref(reader,closure['context_ref'],directory/'CONTEXT.json')
   exact_ref(reader,closure['process_start_ref'],start_path)
   need(process_key(closure['worker_proof'])==worker,'RECOVERY_CLOSURE_REUSED_PID')
   live=live_probe(worker[1]);need(live is None or process_key(live)!=worker or live.get('state') in ('Z','X'),'LIVE_WORKER_CANNOT_HAVE_RECOVERY_CLOSURE')
   need(closure['closed_monotonic_ns']>start['started_monotonic_ns'],'INVALID_RECOVERY_CLOSE_INTERVAL')
   need((directory/'FAILURE.json').exists(),'RECOVERY_FAILURE_RECEIPT_MISSING');reader.obj(directory/'FAILURE.json')
   return {'status':'RECOVERY_CLOSED_NOT_EXECUTED','queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':False,'interval':{'queue_id':admission['queue_id'],'slot':ctx['slot_id'],'start':start['started_monotonic_ns'],'end':closure['closed_monotonic_ns']}}
  live=live_probe(worker[1])
  if live is not None:
   need(process_key(live)==worker and live.get('state') not in ('Z','X'),'REUSED_OR_DEAD_PID_CANNOT_BE_LIVE')
   return {'status':'RUNNING','queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':False,'interval':{'queue_id':admission['queue_id'],'slot':ctx['slot_id'],'start':start['started_monotonic_ns'],'end':time.monotonic_ns()}}
  raise AuditError('FAILED_OR_STALE_INTENT_NO_ACK',ctx['attempt_id'])
 exe=reader.obj(exec_path)
 need(exe.get('schema')=='AUTO161_EXECUTION_V1','WRONG_EXEC_SCHEMA')
 for key in ['attempt_id','nonce','slot_id','started_monotonic_ns','adapter_source_sha256','runner_source_sha256']:
  same(key,start,exe)
 need(process_key(exe['worker'])==worker and process_key(exe['parent'])==parent,'EXECUTION_PID_REUSE_OR_PARENT_MISMATCH')
 need(type(exe.get('returncode')) is int,'MISSING_REAL_EXIT_CODE')
 for key in ['cpu_user_seconds','cpu_system_seconds','max_rss_kib']:
  need(isinstance(exe.get(key),(float,int)) and exe[key]>=0,'INVALID_CPU_USAGE',key)
 need(exe['ended_monotonic_ns']>exe['started_monotonic_ns']>0,'INVALID_EXECUTION_INTERVAL')
 need(exe['ended_unix']>=exe['started_unix']>0,'INVALID_WALL_INTERVAL')
 no_qualification(start);no_qualification(exe)
 interval={'queue_id':admission['queue_id'],'slot':ctx['slot_id'],'start':exe['started_monotonic_ns'],'end':exe['ended_monotonic_ns']}
 if not ack_path.exists():
  if exe['returncode']!=0 and (directory/'FAILURE.json').exists():
   failure=reader.obj(directory/'FAILURE.json');need(isinstance(failure.get('error'),str) and failure.get('unix',0)>0,'INVALID_FAILURE_RECEIPT')
   return {'status':'FAILED_RETAINED_UNACKED','queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':False,'real_cpu_execution':True,'verified_gate_success':False,'returncode':exe['returncode'],'interval':interval}
  return {'status':'AWAIT_ACK_AFTER_EXECUTION','queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':False,'real_cpu_execution':True,'verified_gate_success':False,'returncode':exe['returncode'],'interval':interval}
 ack=reader.obj(ack_path);need(ack.get('schema')=='AUTO161_ACK_V1','WRONG_ACK_SCHEMA')
 no_qualification(ack)
 need(ack.get('qualification_granted') is False and ack.get('exact_trace_qualified') is False,'ACK_QUALIFICATION_FLAGS_MISSING')
 for key in ['attempt_id','queue_id','stage','input_fingerprint']:
  same(key,intent,ctx,ack)
 need(ack.get('admission_sha256')==admission['admission_sha256'],'ACK_ADMISSION_MISMATCH')
 for key in ['slot_id','started_monotonic_ns','ended_monotonic_ns']:same(key,ack,exe)
 need(process_key(ack['worker'])==worker and process_key(ack['parent'])==parent,'ACK_PID_REUSE_OR_PARENT_MISMATCH')
 exact_ref(reader,ack['intent_ref'],directory/'INTENT.json')
 exact_ref(reader,ack['context_ref'],directory/'CONTEXT.json')
 exact_ref(reader,ack['process_start_ref'],directory/'PROCESS_START.json')
 exact_ref(reader,ack['execution_ref'],directory/'EXECUTION.json')
 result=exact_ref(reader,exe['result_ref'],directory/'RESULT.json')
 need(ack['result_ref']==exe['result_ref'],'ACK_RESULT_REF_MISMATCH')
 reader.ref(ack['stdout_ref']);reader.ref(ack['stderr_ref'])
 need(pathlib.Path(ack['stdout_ref']['path']).parent==directory and pathlib.Path(ack['stderr_ref']['path']).parent==directory,'WRONG_LOG_PATH')
 need(exe['returncode']==0 and exe.get('error') is None,'FAILED_EXECUTION_CANNOT_HAVE_ACCEPTED_ACK')
 need(result.get('schema')=='AUTO161_ADAPTER_RESULT_V1','WRONG_RESULT_SCHEMA')
 for key,value in expected.items():need(result.get(key)==value,'RESULT_ROW_STAGE_SCOPE_MISMATCH',key)
 same('attempt_id',result,ctx);same('nonce',result,ctx)
 need(result.get('adapter_profile')==allow['profile'],'WRONG_RESULT_PROFILE')
 need(result.get('adapter_id')==allow['id'] and result.get('profile')==allow['profile'],'WRONG_RESULT_ADAPTER_OR_PROFILE')
 need(result.get('status') in ('PASS','HOLD'),'FAILED_OR_UNKNOWN_STAGE_CANNOT_HAVE_ACCEPTED_ACK')
 need(result.get('stage_execution_complete') is True,'LISTING_OR_DISPATCH_NOT_EXECUTED')
 need(result.get('next_stage') in WAITS,'INVALID_NEXT_STAGE')
 if allow['id']=='auto161_metadata_identity_static_v3':
  from audit_progress_v3 import verify_progress
  expected_progress=verify_progress(reader,ctx,row,result)
  need(result.get('next_stage')==expected_progress and ack.get('next_stage')==expected_progress,'V3_EXACT_PROVED_ROUTE_MISMATCH')
 else:
  need(result.get('next_stage')==ROUTES[row['next_step']],'NEXT_STAGE_ROUTE_MISMATCH')
 need(ack.get('accepted_result_status')==result['status'],'ACK_RESULT_STATUS_MISMATCH')
 need(ack.get('next_stage') in ({result['next_stage']} if permitted_next_stages is None else permitted_next_stages),'ACK_UNAPPROVED_NEXT_STAGE')
 for key in ['qualification_granted','historical_queue_mutated','gpu_executed','simulation_executed']:
  need(result.get(key) is False,'RESULT_PERMISSION_FLAGS_MISSING_OR_TRUE',key)
 no_qualification(result)
 checks=result.get('checks');need(isinstance(checks,list) and len(checks)>=3,'MISSING_EXECUTED_CHECKS')
 for check in checks:need(isinstance(check,dict) and isinstance(check.get('name'),str) and type(check.get('passed')) is bool,'MALFORMED_EXECUTED_CHECK')
 need(all(x['passed'] for x in checks),'FAILED_CHECK_CANNOT_HIDE_BEHIND_HOLD_OR_PASS')
 refs=result.get('inputs',[])+result.get('evidence',[]);need(2<=len(refs)<=64,'MISSING_REAL_EVIDENCE')
 for ref in refs:reader.ref(ref)
 verify_identity_inputs(reader,result,row,admission,allow,require_authority_projection)
 need(intent['context_ref'] in refs,'RESULT_DID_NOT_REOPEN_CONTEXT')
 need(any(x['path']==ctx['scope_path'] and x['sha256']==admission['scope_sha256'] for x in refs),'RESULT_SCOPE_EVIDENCE_MISSING')
 need(isinstance(result.get('missing_proofs'),list) and isinstance(result.get('family_keys'),list),'MISSING_TYPED_RESEARCH_REQUIREMENTS')
 need(bool(result.get('missing_proofs')),'NO_EXPLICIT_BLOCKER_DESPITE_WAIT_STATE')
 evidence=result.get('execution_evidence',{})
 need(evidence.get('pid')==worker[1],'ADAPTER_RESULT_PID_REUSE_OR_FAKE_EXECUTION')
 need(start['started_unix']<=evidence.get('started_unix',0)<=evidence.get('ended_unix',0)<=exe['ended_unix'],'ADAPTER_EXECUTION_TIME_OUTSIDE_SUPERVISOR')
 need(0<=evidence.get('cpu_seconds',-1)<=exe['cpu_user_seconds']+exe['cpu_system_seconds']+.05,'ADAPTER_CPU_EVIDENCE_INCONSISTENT')
 inputs=result.get('inputs',[])
 need(evidence.get('actual_distinct_file_reads')==len(inputs)>=2 and evidence.get('actual_metadata_bytes_read')==sum(x['bytes'] for x in inputs)>0,'ADAPTER_METADATA_READ_ACCOUNTING_FALSE')
 need(isinstance(evidence.get('operations'),list) and len(evidence['operations'])>=3,'ADAPTER_OPERATIONS_EVIDENCE_MISSING')
 need(result.get('historical_actual_input_equality_granted') is False and result.get('actual_GPU_producer_profile_inferred_from_legacy55') is False,'LEGACY_PROFILE_OR_ACTUAL_INPUT_OVERCLAIM')
 for proof in result['missing_proofs']:
  need(isinstance(proof,dict) and isinstance(proof.get('proof_id'),str) and bool(proof.get('required_evidence')) and proof.get('satisfied') is False,'UNTYPED_OR_FAKE_MISSING_PROOF')
  binding=proof.get('binding',{})
  need(binding.get('queue_id')==row['queue_id'] and binding.get('job_sha256',row['job_sha256'])==row['job_sha256'] and binding.get('binary_sha256')==row['binary_sha256'] and binding.get('declared_identity_sha256',row['declared_identity_sha256'])==row['declared_identity_sha256'] and binding.get('argv_sha256')==canonical(row['argv']),'DEPENDENCY_WRONG_ROW_IDENTITY')
  need(isinstance(proof.get('next_adapter_id'),str) and proof.get('next_adapter_ABI')=='AUTO161_ARTIFACT_V1','MISSING_RETRY_OR_READMISSION_ADAPTER_ABI')
 return {'status':'PROCESSED_STAGE_'+result['status'],'queue_id':admission['queue_id'],'attempt_id':ctx['attempt_id'],'execution_covered':True,'real_cpu_execution':True,'verified_gate_success':True,'next_stage':ack['next_stage'],'result_ref':exe['result_ref'],'ack_path':str(ack_path),'interval':interval,'worker_identity':worker,'nonce':nonce,'input_fingerprint':ctx['input_fingerprint'],'missing_proof_count':len(result['missing_proofs']),'trace_qualified':False}
