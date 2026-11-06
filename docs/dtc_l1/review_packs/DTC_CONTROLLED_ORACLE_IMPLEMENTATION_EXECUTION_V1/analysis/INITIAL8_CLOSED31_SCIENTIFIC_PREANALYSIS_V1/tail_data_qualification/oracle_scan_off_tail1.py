"""Independent existing-UUID tail closeout; inert until separate Main release.

No simulation, registration, owner/tracer action, daemon or model retry exists.
The fixed31 driver/auth is never edited or reused.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,time,types
BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1');ROOT=BASE/'initial8'
COHORT='E2-DTCORACLE-I8-6df3a84b612086e8-DH-OFF_MATCHED-V1'
UUID='b1e1d2b8-4359-46d2-af61-65844b889b70'
INPUT='6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39'
SPEC_SHA='b846c5a67397b5e954a7e1082bf09b7d3ba8781ca686928fbbb42bfbfd4d30ec'
REQUEST='DTC_ORACLE_INITIAL8_20261106_V1'
S17_SHA='d0d344e4dc50e299d5f72fb361ce5856f4c2960ea4132c5424f43c80cc13b507'
RETIREMENT_SHA='3ceb9a96c0dd4b40272f70d0211962f132c62dc7aa7213bdf50b1b040d2b10f6'
PASS='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE'
NEG='FAIL_CONTROLLED_ORACLE_DH_ARCHIVED_NO_RETRY'
GOV=BASE/'control/OWNER_RECOVERY_AND_CLOSEOUT.lock'
class Hold(RuntimeError):pass
def need(x,why):
 if not x:raise Hold(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def pin(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def load(p,name):
 p=Path(p);m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def start(pid):return int(Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19])
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as h:h.write((json.dumps(v,sort_keys=True,indent=2)+'\n').encode());h.flush();os.fsync(h.fileno())

def predecessor_terminal_projection(final,snapshot,current_result_hashes):
 need(final['state']=='ALL_FIXED31_CLOSED_VERIFIED_PASS_COMPLETE_NO_SCIENCE_RELEASE'
      and final['caller_pid']==450154 and final['errors']==[],'WAIT_EXTERNAL31_NATURAL_COMPLETE')
 rows=snapshot['rows'];completed=final['completed']
 need(len(rows)==len(completed)==31 and len({x['cohort']for x in completed})==31,'EXACT_PREDECESSOR31')
 by={x['cohort']:x for x in rows}
 need(set(by)=={x['cohort']for x in completed}and COHORT not in by,'TAIL_NOT_PREVIOUSLY_ADMITTED')
 for v in completed:
  old=by[v['cohort']]
  need(v['uuid']==old['uuid']and v['original_state']==PASS
       and current_result_hashes[v['cohort']]==v['result_sha256'],'ALL_PREDECESSOR_RESULTS_IMMUTABLE')
  if old['existing_result_sha256']is not None:
   need(v['result_sha256']==old['existing_result_sha256']and v['preserved_existing_result']is True,
        'ORIGINAL8_MUST_REMAIN_EXACT')
 return dict(previous31_results_preserved=True,previous8_preserved=True,previous31_complete=True)

def predecessor_process_exited(fields,expected_start):
 if fields is None:return True
 if int(fields[19])!=expected_start:return True # original process gone; never signal/reap PID reuse
 need(fields[0]=='Z'and int(fields[49])==0,'WAIT_EXTERNAL31_EXIT_NO_CONCURRENT_CLOSER')
 return True

def predecessor_finished(config,auth):
 need(auth['predecessor31_natural_exit_confirmed']is True,'MAIN_MUST_CONFIRM_ACTUAL_PREDECESSOR_EXIT')
 need(auth['external31_FINAL']==config['external31_FINAL']and auth['external31_snapshot']==config['external31_snapshot'],
      'PREDECESSOR_FINAL_SOURCE_BINDING')
 final=rd(pin(config['external31_FINAL']));snapshot=rd(pin(config['external31_snapshot']))
 process=config['external31_process'];need(process==dict(pid=450154,start_ticks=1073442087),'EXACT_PREDECESSOR_PROCESS')
 p=Path('/proc',str(process['pid']))
 fields=(p/'stat').read_text().rsplit(')',1)[1].split()if p.exists()else None
 predecessor_process_exited(fields,process['start_ticks'])
 hashes={x['cohort']:sha(ROOT/'analysis'/(x['cohort']+'.RESULT.json'))for x in snapshot['rows']}
 return predecessor_terminal_projection(final,snapshot,hashes)

def closed_tail(engine):
 """Honest closed positive OR original negative; absence means WAIT, not zero."""
 q=engine.registered()[2];need(q['request']==REQUEST and q['budget']==32 and q['remaining']==0,'ORIGINAL_REQUEST_ONLY')
 row=q['consumed'][COHORT];need(row['uuid']==UUID,'ORIGINAL_TAIL_UUID_ONLY')
 spec=engine.spec_for(COHORT)
 need(spec['input_digest']==INPUT and spec['program']=='scan'and spec['oracle_mode']=='OFF_MATCHED','FROZEN_SCAN_OFF_FULL_INPUT')
 need(sha(ROOT/'control/specs'/(COHORT+'.json'))==SPEC_SHA,'FROZEN_TAIL_SPEC')
 ledger=ROOT/'control/qualification_ledger';ip=ledger/(COHORT+'.INTENT.json');dp=ip.with_name(COHORT+'.DONE.json')
 need(dp.exists()and row.get('execution_receipt')is not None,'WAIT_REAL_TAIL_DONE_NO_INTERVENTION')
 i,d=rd(ip),rd(dp);out=ROOT/'DTC/run/results'/UUID
 need(sha(ip)==row['intent_sha256']and i['uuid']==d['uuid']==UUID and Path(i['output'])==out,
      'ORIGINAL_TAIL_INTENT_IDENTITY')
 need(d==row['execution_receipt']==rd(out/'NATIVE_EXIT.json')and d['cohort']==i['cohort']==COHORT,
      'REAL_TAIL_DONE_EXIT_RECEIPT')
 need(d['new_attempt_consumed']==1 and d['automatic_retry']is False
      and type(d['launcher_wait_returncode'])is int and type(d['native_simulator_observed'])is bool,
      'ORIGINAL_TAIL_ONCE_ONLY_LIFECYCLE')
 need(sha(out/'raw.log.gz')==d['raw_sha256'],'TAIL_ORIGINAL_RAW_PIN')
 pidpath=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if pidpath.exists():
  need(d['native_simulator_observed']is True,'PID_MAPS_OBSERVATION_MUST_MATCH_ORIGINAL_DONE')
  pid=rd(pidpath)
  try:live=start(pid['pid'])==pid['start_ticks']
  except FileNotFoundError:live=False
  need(not live,'WAIT_TAIL_MODEL_STILL_LIVE')
 else:
  need(d['native_simulator_observed']is False,'OBSERVED_MODEL_REQUIRES_ACTUAL_PID_MAPS')
  launch=rd(out/'NATIVE_LAUNCH.json')
  need(not Path('/proc',str(launch['launcher_pid'])).exists(),'WAIT_UNOBSERVED_LAUNCHER_CLOSURE')
 negative=bool(d['stop_reason']or d['launcher_wait_returncode']or not d['native_simulator_observed'])
 return dict(uuid=UUID,cohort=COHORT,input_digest=INPUT,negative=negative,
             intent_sha256=sha(ip),DONE_sha256=sha(dp),raw_sha256=d['raw_sha256'],output=str(out))

def verify_closeout_admission(context,config):
 need(context['execution_mode']=='EXTERNAL_POSTPROCESS_ONLY'and context['request']==REQUEST
      and context['caller_pid']==os.getpid()and context['caller_start_ticks']==start(os.getpid()),'REAL_EXTERNAL_TAIL_CALLER')
 need(config['retirement_basis']['sha256']==RETIREMENT_SHA,'ONLY_REVIEWED_KERNEL_RETIREMENT_GATE')
 basis=load(pin(config['retirement_basis']),'TAIL_PINNED_RETIREMENT_BASIS')
 basis.verify_governance_fd(context,GOV)
 auth=rd(pin(config['authorization']))
 need(auth['status']=='AUTHORIZED_CLOSED_ONLY'and auth['scope']=='EXTERNAL_SCAN_OFF_TAIL1_ONLY'
      and auth['runner_sha256']==S17_SHA and auth['tail_source_sha256']==sha(__file__)
      and auth['authorized_closed_cohorts']==[COHORT]and auth['uuid']==UUID and auth['input_digest']==INPUT,
      'SEPARATE_MAIN_TAIL1_RELEASE_NOT_FIXED31_AUTH_REUSE')
 need(auth['no_owner_or_tracer_advancement_until_tail_driver_exits']is True
      and auth['new_scientific_starts']==auth['new_scientific_requests']==0
      and auth['not_a_B_or_scientific_owner_release']is True,'ZERO_SCIENCE_AND_CONTROL_EXCLUSION')
 for key in ['retirement_basis','kernel_boundary_proof','future_image_manifest','raw_exec_request','inflight_raw_journal','global_ONCE']:
  need(auth[key]==config[key],'TAIL_RELEASE_ACTUAL_RETIREMENT_BINDING:'+key)
 review=rd(pin(config['independent_review']))
 need(review['status']=='PASS'and review['scope']=='EXTERNAL_SCAN_OFF_TAIL1_CLOSED_ONLY'
      and review['subject_tail_source_sha256']==sha(__file__)and review['S17_source_sha256']==S17_SHA,
      'EXACT_INDEPENDENT_TAIL_SOURCE_REVIEW')
 pred=predecessor_finished(config,auth);actual=basis.inspect_retirement_basis(config)
 now=time.monotonic_ns()
 return dict(status='PASS',request=REQUEST,governance_lock=str(GOV),caller_pid=os.getpid(),caller_start_ticks=start(os.getpid()),
      execution_mode='EXTERNAL_POSTPROCESS_ONLY',original_closer_threads_excluded=True,owner_recovery_excluded=True,
      new_scientific_starts_permitted=False,independent_quiescence_or_retirement_review='PASS',
      observed_monotonic_ns=now,valid_until_monotonic_ns=now+30*10**9,previous31=pred,kernel_retirement_basis=actual,
      actual_target_or_tracer_actions=0,scientific_requests_registered=0)

def finish_one(session,base_component):
 """Positive uses S17 unchanged; negative uses its original honest consumer."""
 session._assert_thread();session._admission()
 engine=session.consumer.load('TAIL_READONLY_SCIENCE_ENGINE','oracle_native.py')
 q=copy.deepcopy(engine.registered()[2]);original=closed_tail(engine)
 if not original['negative']:return session.finish(COHORT)
 path=ROOT/'analysis'/(COHORT+'.RESULT.json');old=sha(path)if path.exists()else None
 outbox=session.consumer.load('TAIL_ORIGINAL_OUTBOX_VERIFY','oracle_outbox.py')
 done=rd(Path(original['output'])/'NATIVE_EXIT.json')
 optional=[Path(original['output'])/'L2_STRICT.json',ROOT/'DTC/control'/('SCIENCE_QUALIFICATION_'+COHORT+'.json')]
 optional_before={str(p):sha(p)if p.exists()else None for p in optional}
 try:
  value=session.consumer.finish_evidence(COHORT) # original negative branch; never fabricate performance strict
  expected=dict(status='CONTROLLED_ORACLE_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=done['stop_reason'],
      returncode=done['launcher_wait_returncode'],native_simulator_observed=done['native_simulator_observed'],
      failure_classification=outbox.classification(done),accepted_cycles=None,raw_sha256=done['raw_sha256'],
      raw_uncompressed_sha256=done['raw_uncompressed_sha256'],performance_accepted=False)
  need(value['uuid']==UUID and value['cohort']==COHORT and value['state']==NEG
       and value['cycles']is None and value['proof']==expected,'EXACT_ORIGINAL_NEGATIVE_PROOF_NEVER_PERFORMANCE_PASS')
  archived=outbox.verify(COHORT)
  need(archived==value['archive']and archived['registered_outbox_binding']['negative_performance_accepted']is False
       and archived['registered_outbox_binding']['failure_classification']==expected['failure_classification'],
       'REAL_NEGATIVE_TRUE164_NATIVE_RESTORE_AND_LIFECYCLE_PROOF')
  need(rd(path)==value and(old is None or sha(path)==old),'EXISTING_NEGATIVE_RESULT_NOT_OVERWRITTEN')
  return value
 finally:
  base_component.verify_request_monotonic(q,engine.registered()[2],ROOT)
  need(closed_tail(engine)==original,'ORIGINAL_TAIL_NEGATIVE_SOURCE_UNCHANGED')
  need({str(p):sha(p)if p.exists()else None for p in optional}==optional_before,
       'NEGATIVE_OPTIONAL_STRICT_QUAL_MISSING_MUST_STAY_MISSING_OR_IDENTICAL')

def run(config_path,config_sha):
 need(sha(config_path)==config_sha,'SOURCE_BOUND_MAIN_CONFIG')
 config=rd(config_path);need(config.get('actual_execution_authorized')is True,'DEFAULT_UNARMED')
 auth=rd(pin(config['authorization']));need(auth['tail_source_sha256']==sha(__file__),'MAIN_TAIL_SOURCE_RELEASE')
 need(config['S17_component']['sha256']==S17_SHA,'FROZEN_S17_COMPONENT')
 component=load(pin(config['S17_component']),'TAIL_S17_UNCHANGED_COMPONENT')
 # Read-only readiness before entering the single-pass namespace. Missing DONE
 # does not consume a metadata pass or cause a model operation/retry.
 engine=component._load_consumer(config).load('TAIL_READONLY_READY_ENGINE','oracle_native.py')
 closed_tail(engine);predecessor_finished(config,auth)
 out=BASE/'control/external_scan_off_tail1_pass'/config['authorization']['sha256'];out.mkdir(parents=True,exist_ok=False)
 status=dict(schema='EXTERNAL_SCAN_OFF_TAIL1_STATUS_V1',caller_pid=os.getpid(),source_sha256=sha(__file__),
      cohort=COHORT,uuid=UUID,input_digest=INPUT,Main_authorization=config['authorization'],
      new_scientific_starts=0,new_scientific_requests=0,model_retries=0,owner_or_tracer_actions=0)
 write(out/'BEGIN.fixed.json',status)
 try:
  with component.CloseoutSession(config)as session:
   value=finish_one(session,component)
   need(value['state']in[PASS,NEG],'HONEST_ACCEPTED_OR_NEGATIVE_TERMINAL_ONLY')
   status.update(state=value['state'],cycles=value['cycles'],result_path=str(ROOT/'analysis'/(COHORT+'.RESULT.json')),
                 result_sha256=sha(ROOT/'analysis'/(COHORT+'.RESULT.json')),performance_accepted=value['state']==PASS)
  write(out/'FINAL.fixed.json',status);return status
 except BaseException as error:
  status.update(state='TAIL1_ENGINEERING_HOLD_PRESERVE_NO_AUTOMATIC_RETRY',error=repr(error));write(out/'FINAL.fixed.json',status);raise

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--config');p.add_argument('--config-sha');a=p.parse_args()
 if not a.run:print(json.dumps(dict(status='CPU_PREPARATION_ONLY_TAIL1_NOT_RUN')));return
 need(a.config and a.config_sha,'EXACT_MAIN_CONFIG_REQUIRED');run(a.config,a.config_sha)
if __name__=='__main__':main()
