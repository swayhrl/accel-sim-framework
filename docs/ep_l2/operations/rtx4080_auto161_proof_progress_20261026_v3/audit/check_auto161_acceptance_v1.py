#!/usr/bin/env python3
"""Finite read-only exact161 acceptance. Never schedules, executes, signals or mutates pipeline."""
import argparse,collections,hashlib,json,pathlib,sys,time
from audit_common_v1 import Reader,AuditError,need,canonical,no_qualification,interval_checks
from audit_attempt_v1 import audit_attempt,admission_for,STAGE
from check_dependency_artifacts_v1 import permitted_next
from check_production_preservation_v1 import preservation,N,ROOT,ROOT_ACCEPTANCE_SHA
from check_binary_attestation_v1 import check_binary_attestation
SCOPE=N/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json'
SCOPE_SHA='b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a'
PIPELINE=N/'auto161_pipeline_20261026_v1/orchestrator'
def pinned(reader,path,digest,code):
 raw=reader.bytes(path);need(hashlib.sha256(raw).hexdigest()==digest,code,path);return reader.obj(path)
def event_chain(reader,pipeline):
 files=sorted((pipeline/'events').glob('*.json'));need(len(files)<=4096,'EVENT_AUDIT_LIMIT')
 previous=None;events=[]
 for i,p in enumerate(files):
  need(p.name==f'{i:012d}.json','EVENT_SEQUENCE_FILENAME_GAP',p)
  obj=reader.obj(p);need(obj.get('schema')=='AUTO161_EVENT_V1' and obj.get('sequence')==i and obj.get('prev_sha256')==previous,'EVENT_CHAIN_BROKEN',p)
  previous=hashlib.sha256(reader.bytes(p)).hexdigest();events.append(obj)
 return events
def audit(pipeline,run,approval_sha,fixture=None):
 pipeline=pathlib.Path(pipeline);run=pathlib.Path(run)
 if fixture:
  need(fixture.get('fixture') is True,'FIXTURE_CONFIG_REQUIRED')
  roots=[pathlib.Path(fixture['root'])];scope_path=pathlib.Path(fixture['scope_path']);scope_sha=fixture['scope_sha256'];accept_path=pathlib.Path(fixture['root_acceptance_path']);accept_sha=fixture['root_acceptance_sha256']
 else:
  roots=[N,pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control'),pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates')]
  scope_path=SCOPE;scope_sha=SCOPE_SHA;accept_path=ROOT/'ROOT_SCOPE_AND_ACCEPTANCE_V1.json';accept_sha=ROOT_ACCEPTANCE_SHA
 reader=Reader(roots)
 need(run.parent==pipeline/'runs','WRONG_RUN_DIRECTORY')
 approval_path=run/'ROOT_APPROVAL_FROZEN.json' if (run/'ROOT_APPROVAL_FROZEN.json').exists() else pipeline/'ROOT_APPROVAL.json'
 approval=pinned(reader,approval_path,approval_sha,'ROOT_APPROVAL_BYTES_CHANGED')
 need(approval.get('schema')=='AUTO161_ROOT_APPROVAL_V1' and approval.get('status')=='APPROVED_PRIVATE_CPU_ONLY_EXACT161','ROOT_APPROVAL_MISSING')
 need(approval.get('scope_sha256')==scope_sha and approval.get('root_acceptance_sha256')==accept_sha,'ROOT_APPROVAL_SCOPE_CHANGED')
 need(approval.get('max_workers')==2 and approval.get('max_attempts_per_fingerprint')==3,'APPROVAL_RESOURCE_POLICY_CHANGED')
 for name in ['core.py','worker.py','orchestrator.py','ALLOWLIST.json','FROZEN_ADMISSIONS.json']:
  artifact=run/'PINS_FROZEN'/name if (run/'PINS_FROZEN'/name).exists() else (run/'ALLOWLIST_FROZEN.json' if name=='ALLOWLIST.json' and (run/'ALLOWLIST_FROZEN.json').exists() else pipeline/name)
  need(hashlib.sha256(reader.bytes(artifact)).hexdigest()==approval['pins'][name],'APPROVED_CODE_OR_CONFIGURATION_CHANGED',name)
 accept=pinned(reader,accept_path,accept_sha,'ROOT_ACCEPTANCE_PIN_CHANGED')
 scope=pinned(reader,scope_path,scope_sha,'FROZEN_EXACT161_SCOPE_CHANGED');rows=scope['rows']
 need(len(rows)==161 and len({x['queue_id'] for x in rows})==161,'FROZEN_SCOPE_NOT_UNIQUE161')
 ids=[x['queue_id'] for x in rows]
 need(accept.get('frozen_ids')==ids and accept.get('frozen_todo_sha256')==scope_sha,'ROOT_EXACT161_SCOPE_JOIN_CHANGED')
 admissions=reader.obj(pipeline/'FROZEN_ADMISSIONS.json')
 need(admissions.get('schema')=='AUTO161_FROZEN_ADMISSIONS_V1' and admissions.get('count')==161,'ADMISSION_MANIFEST_COUNT_CHANGED')
 expected=[admission_for(row,i,scope_sha) for i,row in enumerate(rows)]
 need(admissions.get('rows')==expected,'DUPLICATE_OR_MODIFIED_ADMISSION')
 need(pathlib.Path(admissions['scope_ref']['path'])==scope_path and admissions['scope_ref']['sha256']==scope_sha,'ADMISSION_SCOPE_REF_CHANGED');reader.ref(admissions['scope_ref'])
 bysha={x['admission_sha256']:(x,rows[x['row_index']]) for x in expected}
 registry_path=run/'ALLOWLIST_FROZEN.json' if (run/'ALLOWLIST_FROZEN.json').exists() else pipeline/'ALLOWLIST.json'
 need(hashlib.sha256(reader.bytes(registry_path)).hexdigest()==approval['pins']['ALLOWLIST.json'],'RUN_ALLOWLIST_FROZEN_PIN_CHANGED')
 registry=reader.obj(registry_path);allow=registry['metadata_adapter']
 need(allow.get('profile')=='AUTO161_READONLY_CPU_METADATA_V1' and isinstance(allow.get('id'),str),'UNKNOWN_METADATA_ADAPTER_PROFILE')
 need(hashlib.sha256(reader.bytes(allow['path'])).hexdigest()==allow['sha256'],'APPROVED_ADAPTER_SOURCE_CHANGED')
 run_obj=reader.obj(run/'RUN_IDENTITY.json')
 need(run_obj.get('schema')=='AUTO161_RUN_IDENTITY_V1' and run_obj.get('run_id')==run.name,'RUN_IDENTITY_MISMATCH')
 need(run_obj.get('pins')==approval['pins'],'RUN_USED_DIFFERENT_SOURCE_PINS')
 need(pathlib.Path(run_obj['approval_ref']['path']) in (approval_path,run/'ROOT_APPROVAL_SNAPSHOT.json') and run_obj['approval_ref']['sha256']==approval_sha,'RUN_APPROVAL_NOT_ROOT_PINNED');reader.ref(run_obj['approval_ref'])
 if 'allowlist_ref' in run_obj:need(pathlib.Path(run_obj['allowlist_ref']['path'])==registry_path and run_obj['allowlist_ref']['sha256']==approval['pins']['ALLOWLIST.json'],'RUN_ALLOWLIST_REF_MISMATCH');reader.ref(run_obj['allowlist_ref'])
 need(0<run_obj['started_monotonic_ns']<run_obj['deadline_monotonic_ns'] and run_obj['deadline_monotonic_ns']-run_obj['started_monotonic_ns']<=3600*10**9,'RUN_DEADLINE_SCOPE_CHANGED')
 events=event_chain(reader,pipeline)
 event_ack_keys=set()
 for logged in events:
  if 'queue_id' in logged:need(logged['queue_id'] in ids,'EVENT_OUTSIDE_EXACT161')
  if logged.get('kind')=='ACK_REOPEN_VERIFIED':
   key=(logged.get('queue_id'),logged.get('attempt_id'));need(key not in event_ack_keys,'DUPLICATE_ACK_EVENT');event_ack_keys.add(key)
   event_ack=reader.refobj(logged['ack_ref']);need(event_ack.get('queue_id')==key[0] and event_ack.get('attempt_id')==key[1],'EVENT_ACK_IDENTITY_MISMATCH')
 need(any(x.get('kind')=='FINITE_ROUND_START' and x.get('run_id')==run.name for x in events),'REAL_RUN_START_EVENT_MISSING')
 errors=[];attempt_results=[];intervals=[];accepted=collections.defaultdict(list);fingerprints=collections.defaultdict(list);identities=set();nonces=set()
 attempt_dirs=sorted({p.parent for p in (pipeline/'runs').glob('*/rows/*/attempts/*/INTENT.json')})
 need(len(attempt_dirs)<=1024,'FINITE_ATTEMPT_AUDIT_LIMIT')
 for directory in attempt_dirs:
  try:
   admission_sha=directory.parent.parent.name;need(admission_sha in bysha,'UNREGISTERED_ATTEMPT_ADMISSION',directory)
   ad,row=bysha[admission_sha]
   ctx=reader.obj(directory/'CONTEXT.json');need(ctx['attempt_id']==directory.name,'WRONG_ATTEMPT_ID_PATH')
   ancestor=directory.parents[3];need(ancestor.parent==pipeline/'runs','WRONG_ATTEMPT_RUN_PATH')
   own_run=reader.obj(ancestor/'RUN_IDENTITY.json')
   if 'approval_ref' in ctx:need(ctx['approval_ref']==own_run['approval_ref'],'CONTEXT_APPROVAL_NOT_RUN_FROZEN');reader.ref(ctx['approval_ref'])
   if 'allowlist_ref' in ctx:need(ctx['allowlist_ref']==own_run.get('allowlist_ref'),'CONTEXT_ALLOWLIST_NOT_RUN_FROZEN');reader.ref(ctx['allowlist_ref'])
   trusted={approval_sha,*approval.get('accepted_prior_approval_sha256',[])}
   need(own_run['approval_ref']['sha256'] in trusted,'HISTORICAL_RUN_APPROVAL_NOT_ROOT_TRUSTED')
   prior=reader.refobj(own_run['approval_ref']);need(prior.get('schema')=='AUTO161_ROOT_APPROVAL_V1' and prior.get('status')=='APPROVED_PRIVATE_CPU_ONLY_EXACT161' and prior.get('scope_sha256')==scope_sha and prior.get('root_acceptance_sha256')==accept_sha and prior.get('max_workers')==2 and prior.get('max_attempts_per_fingerprint')==3,'HISTORICAL_APPROVAL_POLICY_MISMATCH')
   need(own_run.get('pins')==prior['pins'],'HISTORICAL_RUN_SOURCE_PINS_MISMATCH')
   prior_reg=reader.refobj(own_run['allowlist_ref']) if 'allowlist_ref' in own_run else registry
   if 'allowlist_ref' in own_run:need(own_run['allowlist_ref']['sha256']==prior['pins']['ALLOWLIST.json'],'HISTORICAL_ALLOWLIST_PIN_MISMATCH')
   for name in ['core.py','worker.py','orchestrator.py','FROZEN_ADMISSIONS.json']:
    source=ancestor/'PINS_FROZEN'/name if (ancestor/'PINS_FROZEN'/name).exists() else pipeline/name
    need(hashlib.sha256(reader.bytes(source)).hexdigest()==prior['pins'][name],'HISTORICAL_SOURCE_BYTES_UNAVAILABLE_OR_CHANGED',name)
   overrides=permitted_next(reader,ctx,row,prior_reg)
   out=audit_attempt(reader,directory,ad,row,prior_reg['metadata_adapter'],prior['pins']['worker.py'],own_run['orchestrator'],permitted_next_stages=overrides,require_authority_projection=not bool(fixture))
   out['directory']=str(directory);attempt_results.append(out)
   fingerprints[(ad['queue_id'],ctx['input_fingerprint'])].append(out)
   if 'interval' in out:intervals.append(out['interval'])
   if out['execution_covered']:
    ack_ref={'path':out['ack_path'],'bytes':len(reader.bytes(out['ack_path'])),'sha256':hashlib.sha256(reader.bytes(out['ack_path'])).hexdigest()}
    need(sum(x.get('kind')=='ACK_REOPEN_VERIFIED' and x.get('attempt_id')==out['attempt_id'] and x.get('queue_id')==ad['queue_id'] and x.get('ack_ref')==ack_ref for x in events)==1,'ACK_EVENT_MISSING_DUPLICATE_OR_FORGED')
    nonce=out['nonce'];need(nonce not in nonces,'DUPLICATE_EXECUTION_NONCE',nonce);nonces.add(nonce)
    identity=tuple(out['worker_identity']);need(identity not in identities,'REUSED_EXECUTION_PROCESS_IDENTITY',identity);identities.add(identity)
    accepted[ad['queue_id']].append(out)
  except (AuditError,KeyError,ValueError,OSError,TypeError) as exc:
   errors.append({'path':str(directory),'code':getattr(exc,'code','SCHEMA_OR_IO_ERROR'),'detail':str(exc)})
 for key,attempts in fingerprints.items():
  if len(attempts)>3:errors.append({'code':'RETRY_BOUND_GT3','detail':str(key)})
  if sum(x['execution_covered'] for x in attempts)>1:errors.append({'code':'DUPLICATE_EFFECTIVE_ACK','detail':str(key)})
  if sum(x['status']=='RUNNING' for x in attempts)>1:errors.append({'code':'DUPLICATE_LIVE_ATTEMPT','detail':str(key)})
 peak=0
 try:peak=interval_checks(intervals)
 except AuditError as exc:errors.append({'code':exc.code,'detail':exc.detail})
 row_results=[];covered=0
 for ad,row in zip(expected,rows):
  state_path=pipeline/'rows'/ad['admission_sha256']/'STATE.json'
  try:
   if not state_path.exists():
    row_results.append({'queue_id':row['queue_id'],'status':'AWAIT_FIRST_REAL_CPU_EXECUTION','execution_covered':False});continue
   state=reader.obj(state_path);need(state.get('schema')=='AUTO161_ROW_STATE_V1' and state.get('queue_id')==row['queue_id'] and state.get('admission_sha256')==ad['admission_sha256'],'ROW_STATE_IDENTITY_CHANGED')
   need(state.get('exact_trace_qualified') is False,'STATE_MISREPORTS_TRACE_QUALIFICATION');no_qualification(state)
   matches=[x for x in accepted[row['queue_id']] if x['attempt_id']==state.get('attempt_id') and x['input_fingerprint']==state.get('input_fingerprint')]
   if not matches:
    need('latest_ack_ref' not in state,'STATE_POINTS_TO_UNVERIFIED_ACK')
    row_results.append({'queue_id':row['queue_id'],'status':state['status'],'execution_covered':False});continue
   need(len(matches)==1,'DUPLICATE_LATEST_EFFECTIVE_ACK');proof=matches[0]
   need(state['status']==proof['next_stage'],'STATE_UNAPPROVED_ADVANCEMENT')
   need(pathlib.Path(state['latest_ack_ref']['path'])==pathlib.Path(proof['ack_path']),'STATE_WRONG_ACK_PATH');reader.ref(state['latest_ack_ref'])
   samefp=fingerprints[(row['queue_id'],state['input_fingerprint'])]
   need(state.get('attempt_count')==len(samefp),'STATE_ATTEMPT_COUNT_MISMATCH')
   need(state.get('stage_execution_complete') is True,'STATE_EXECUTION_CLAIM_MISSING')
   covered+=1;row_results.append({'queue_id':row['queue_id'],'status':state['status'],'execution_covered':True,'stage_result':proof['status'],'attempt_id':proof['attempt_id'],'missing_proof_count':proof['missing_proof_count']})
  except (AuditError,KeyError,ValueError,OSError,TypeError) as exc:
   errors.append({'queue_id':row['queue_id'],'code':getattr(exc,'code','SCHEMA_OR_IO_ERROR'),'detail':str(exc)})
 states=sorted((pipeline/'rows').glob('*/STATE.json'))
 need(all(p.parent.name in bysha for p in states),'UNREGISTERED_EXTRA_ROW_STATE')
 history=None;binary=None
 if not fixture:
  history=preservation(reader,set(ids))
  binary=check_binary_attestation(reader,ROOT/'CURRENT_BINARY_ATTESTATION_V1.json',rows)
 status_counts=dict(collections.Counter(x['status'] for x in row_results))
 if covered==161 and any(x['status'] in ('AWAIT_EXECUTION','AWAIT_ACK_AFTER_EXECUTION','RUNNING') for x in attempt_results):errors.append({'code':'UNACKNOWLEDGED_INCOMPLETE_HISTORY','detail':'A later success cannot hide an unclosed or live attempt; require ACK or explicit non-executed recovery closure.'})
 # All waits remain blockers; covered metadata never counts as a qualified trace.
 report={'schema':'AUTO161_INDEPENDENT_ACCEPTANCE_V1','status':'ACCEPTED_REAL_CPU_EXECUTION_COVERAGE_NOT_TRACE_QUALIFICATION' if covered==161 and not errors else 'REJECTED_OR_INCOMPLETE','production_acceptance':not bool(fixture),'run_id':run.name,'scope_sha256':scope_sha,'registered_unique_ids':161,'real_CPU_execution_covered_ids':covered,'uncovered_ids':161-covered,'attempt_status_counts':dict(collections.Counter(x['status'] for x in attempt_results)),'row_status_counts':status_counts,'await_or_blocked_rows':sum(x.get('status','').startswith(('WAIT_','AWAIT_')) for x in row_results),'await_root_GPU_rows':sum(x.get('status','').startswith('WAIT_ROOT_GPU') for x in row_results),'await_research_or_dependency_rows':sum(x.get('status','').startswith('WAIT_') and not x.get('status','').startswith('WAIT_ROOT_GPU') for x in row_results),'await_first_execution_rows':sum(x.get('status','')=='AWAIT_FIRST_REAL_CPU_EXECUTION' for x in row_results),'running_rows':sum(x.get('status','').startswith('RUNNING') for x in row_results),'failed_or_retry_attention_rows':sum(x.get('status','').startswith(('FAILED','RETRY_','LIVE_')) for x in row_results),'processed_stage_receipts':sum(x['execution_covered'] for x in attempt_results),'CPU_attempts_with_verified_closed_EXEC':sum(x.get('real_cpu_execution',False) for x in attempt_results),'metadata_executed_rows':len({x['queue_id'] for x in attempt_results if x.get('real_cpu_execution')}),'independently_verified_gate_success_rows':covered,'trace_qualified':0,'consumer_qualified':0,'scientifically_qualified':0,'peak_verified_CPU_processes':peak,'read_bytes':reader.total,'errors':errors,'rows':row_results,'preservation':history,'binary_attestation':binary,'summary_stdout_not_used_as_evidence':True,'checker_never_executes_or_signals_workers':True,'completed_unix':time.time()}
 return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pipeline-dir',default=str(PIPELINE));ap.add_argument('--run-dir',required=True);ap.add_argument('--approval-sha',required=True);ap.add_argument('--fixture-config');ap.add_argument('--output',required=True);args=ap.parse_args()
 fixture=json.loads(pathlib.Path(args.fixture_config).read_text()) if args.fixture_config else None
 out=pathlib.Path(args.output);allowed=pathlib.Path(fixture['root']) if fixture else N/'auto161_pipeline_20261026_v1/audit'
 need(out.is_absolute() and (out.parent==allowed or allowed in out.parents) and not out.is_symlink(),'OUTPUT_OUTSIDE_PRIVATE_AUDIT_DIRECTORY')
 try:report=audit(args.pipeline_dir,args.run_dir,args.approval_sha,fixture)
 except (AuditError,KeyError,ValueError,OSError,TypeError) as exc:
  report={'schema':'AUTO161_INDEPENDENT_ACCEPTANCE_V1','status':'REJECTED','real_CPU_execution_covered_ids':0,'trace_qualified':0,'production_acceptance':not bool(fixture),'errors':[{'code':getattr(exc,'code','SCHEMA_OR_IO_ERROR'),'detail':str(exc)}]}
 with out.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('rows',)}))
 return 0 if report['status']=='ACCEPTED_REAL_CPU_EXECUTION_COVERAGE_NOT_TRACE_QUALIFICATION' else 2
if __name__=='__main__':sys.exit(main())
