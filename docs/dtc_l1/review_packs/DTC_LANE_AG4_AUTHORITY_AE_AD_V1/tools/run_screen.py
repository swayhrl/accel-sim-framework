"""AG4 five reservations, sequential, fail-stop. Only --dispatch can run sims.
CPU-only tests import pure gates / the exact guarded_process engine instead.
"""
from common import *
from strict_screen import require,input_identity,collect
from resource_policy import RuntimePolicy,admission_checks
from audit_site import snapshot,proc
from review_authority import review
from guarded_process import run_guarded
from mapping_roles import validate_manifest,verify_file
import fcntl,signal,time,shutil,argparse,uuid

ORDER=['BASE_Gaussian','AE_GEMM','AE_Gaussian','AD_GEMM','AD_Gaussian']

def validate_records(records,specs):
 reservations={s['attempt_uuid'] for s in specs}
 require(len(specs)==len(reservations)==5,'FIVE_UNIQUE_UUID_RESERVATIONS')
 require([s['point'] for s in specs]==ORDER,'FIXED_FIVE_POINT_ORDER')
 require(all(uuid.UUID(v).version==4 for v in reservations),'STANDARD_UUID4_REQUIRED')
 starts=[r['attempt_uuid'] for r in records]
 require(len(starts)==len(set(starts)) and len(starts)<=5,'BUDGET_CAP_OR_DUPLICATE_START')
 require(set(starts)<=reservations,'FOREIGN_UUID_IN_AG4_RAW')
 require(starts==[s['attempt_uuid'] for s in specs[:len(starts)]],'START_PREFIX_ORDER')
 return starts

def budget(specs):
 paths=sorted((RAW/'attempts').glob('*/RUN_START.json'))
 rows=sorted([json.loads(p.read_text()) for p in paths],key=lambda r:r['order'])
 return validate_records(rows,specs)

def check_files(manifest):
 for name,digest in manifest['files'].items():require(sha(PACK/name)==digest,'IMMUTABLE_REGISTRATION_FILE_CHANGED:'+name)
 for m in json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text()).values():validate_manifest(m)

def publication_check():
 require(not git(FW,'status','--porcelain'),'FRAMEWORK_WORKTREE_NOT_CLEAN')
 receipt=json.loads((RAW/'PREREG_PUBLICATION_READBACK.json').read_text());head=receipt['head']
 require(receipt['fetched_head']==head==git(FW,'rev-parse','refs/ag4-publication/preregistered'),'PUSH_FETCH_BACK_REQUIRED')
 require(git(FW,'merge-base','--is-ancestor',head,'HEAD')=='','REGISTERED_HEAD_ANCESTRY')
 path=PACK/'EXECUTABLE_PREREGISTRATION.json';require(sha(path)==receipt['manifest_sha256'],'REGISTERED_MANIFEST_SHA')
 manifest=json.loads(path.read_text());require(manifest['status']=='EXECUTABLE_PREREGISTERED_NOT_YET_STARTED','EXECUTABLE_REGISTRATION_REQUIRED')
 check_files(manifest)
 for name,digest in manifest['files'].items():require(hashlib.sha256(blob(FW,head,str((PACK/name).relative_to(FW)))).hexdigest()==digest,'PUBLISHED_BLOB_CHANGED:'+name)
 require(git(CORE,'rev-parse','HEAD')==manifest['core_commit'] and not git(CORE,'status','--porcelain'),'CORE_IDENTITY_NOT_CLOSED')
 require(git(CORE,'rev-parse','refs/ag4-source/core-final')==manifest['core_commit'],'CORE_PUBLICATION_REQUIRED')
 return manifest,head

def admission(label,owner):
 dest=RAW/'admissions'/label;dest.mkdir(parents=True,exist_ok=False)
 a=snapshot();write(dest/'FIRST.json',a);time.sleep(10.1);b=snapshot();write(dest/'SECOND.json',b)
 checks=admission_checks(a,b);authority=review(b,owner)
 write(dest/'DECISION.json',dict(resource_checks=checks,authority=authority,no_resource_retry=True))
 require(all(checks.values()),'PRELAUNCH_RESOURCE_STOP:'+label)
 require(all(authority['checks'].values()),'PRELAUNCH_AUTHORITY_STOP:'+label)
 return b

def require_BASE_gate(spec,specs):
 reuse=json.loads((PACK/'AG3_GEMM_BASE_REUSE_QUALIFICATION.json').read_text())
 require(reuse['status']=='PASS_REUSE_AG3_GEMM_BASE_FOR_AG4_DISCOVERY','IMPORTED_GEMM_BASE_REUSE_NOT_QUALIFIED')
 if spec['arm']=='BASE':return
 base=specs[0]
 path=RAW/'attempts'/(base['point']+'_'+base['attempt_uuid'])/'STRICT.json'
 require(path.is_file(),'NEW_FULL_GAUSSIAN_BASE_STRICT_RECEIPT_REQUIRED')
 row=json.loads(path.read_text())
 require(row.get('performance_accepted') is True and row.get('calibration',{}).get('status')=='PASS_FULL_INPUT_CYCLES_AND_ALL_FROZEN_COMMON_METRICS','BASE_STRICT_CALIBRATION_NOT_CLOSED')

def run_one(spec,specs,owner):
 publication_check();require_BASE_gate(spec,specs);require(spec['attempt_uuid'] not in budget(specs),'NO_UUID_RESTART')
 identity=input_identity(spec);start=admission(spec['point'],owner);publication_check()
 run=RAW/'attempts'/(spec['point']+'_'+spec['attempt_uuid']);run.mkdir(parents=True,exist_ok=False)
 args=[spec['runtime_path'],'-trace',spec['trace_list']];copies=[]
 for i,entry in enumerate(spec['configs']):
  require(sha(entry['path'])==entry['sha256'],'CONFIG_CHANGED')
  dest=run/f'config-{i}.config';shutil.copyfile(entry['path'],dest);dest.chmod(0o444)
  copies.append(dict(path=str(dest),sha256=sha(dest)));args.extend(['-config',str(dest)])
 # Final sample after publication hashing: minimum admission and authority only,
 # retaining the independently observed >=10s pair and its exact policy.
 fresh=snapshot();checks=admission_checks(start,fresh);authority=review(fresh,owner)
 require(all(v for k,v in checks.items() if k.startswith('second_') or k=='no_new_cgroup_oom'),'FINAL_PRE_FORK_RESOURCE_STOP')
 require(all(authority['checks'].values()),'FINAL_PRE_FORK_AUTHORITY_STOP')
 write(run/'FINAL_PRE_FORK.json',dict(snapshot=fresh,authority=authority,resource_checks=checks))
 policy=RuntimePolicy(fresh);next_full=[0.];last_fault=[0];last_progress=[0.];interrupted=[]
 old={s:signal.signal(s,lambda signum,frame:interrupted.append(signum)) for s in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]}
 def observe(pid,full_hint,ownership):
  if interrupted:return 'COORDINATOR_SIGNAL_'+str(interrupted[0])
  cg={k:int(v) for k,v in (l.split() for l in Path('/sys/fs/cgroup/memory.events').read_text().splitlines())}
  if any(cg[k]>fresh['cgroup']['events'][k] for k in ['oom','oom_kill']):return 'NEW_CGROUP_OOM_OR_OOM_KILL'
  if time.monotonic()<next_full[0]:return None
  current=snapshot();own=proc(pid)
  if own:owner['child_pid']=pid;owner['child_start_ticks']=own['start_ticks']
  fault=own['majflt'] if own else last_fault[0];decision=policy.observe(current,fault,last_fault[0]);last_fault[0]=fault
  auth=review(current,owner,ownership);next_full[0]=time.monotonic()+decision['next_full_sample_seconds']
  with (run/'RESOURCE_MONITOR.jsonl').open('a') as log:log.write(json.dumps(dict(snapshot=current,own=own,decision=decision,authority=auth))+'\n')
  if time.monotonic()-last_progress[0]>=60 or decision['decision']!='CONTINUE':
   print(json.dumps(dict(point=spec['point'],pid=pid,resource=decision['decision'],sampled_RSS_bytes=own['rss_bytes'] if own else None,io_full=current['pressure']['io']['full']['avg10'],elapsed_seconds=int((current['monotonic_ns']-fresh['monotonic_ns'])/1e9))),flush=True);last_progress[0]=time.monotonic()
  if decision['decision']=='STOP':return ';'.join(decision['stop_reasons'])
  if not all(auth['checks'].values()):return 'RUNTIME_AUTHORITY_NOT_CLOSED'
  return None
 engine=None
 try:
  # This exclusive conservative reservation boundary precedes the only real
  # fork/exec. It consumes a slot even if the fork/loader later fails.
  write(run/'RUN_START.json',dict(utc=now(),order=spec['order'],attempt_uuid=spec['attempt_uuid'],point=spec['point'],argv=args,input_identity=identity,config_copies=copies,source_core=spec['core_commit'],timeout_seconds=7200,retries=0,real_start_API='owned fork/exec via guarded_process; never a canary'),exclusive=True)
  def capability(target,argv,env):
   publication_check();require(budget(specs)[-1]==spec['attempt_uuid'],'CURRENT_EXCLUSIVE_START_RECEIPT')
   require(target==spec['runtime_path'] and argv==args and env==spec['runtime_environment'],'EXACT_REGISTERED_REAL_RUN_IDENTITY')
   require(not (run/'ENGINE/FORK_CHILD.json').exists(),'NO_SECOND_REAL_CHILD')
  manifests=json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text())
  engine=run_guarded(args,spec['runtime_environment'],manifests,run/'ENGINE','SIMULATION',7200,capability,observe)
  final=snapshot();decision=policy.observe(final,last_fault[0],last_fault[0]);final_auth=review(final,owner);write(run/'RESOURCE_FINAL.json',dict(snapshot=final,decision=decision,authority=final_auth))
  require(final_auth['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY','FINAL_AUTHORITY_NOT_CLOSED')
  write(run/'RUN_TERMINAL.json',dict(returncode=engine['returncode'],forced_reason=engine['forced_reason'] or ('FINAL_RESOURCE_STOP' if decision['decision']=='STOP' else None),identity_pass=engine['identity_pass'],engine=engine),exclusive=True)
  os.link(run/'ENGINE/stdout',run/'simulator.stdout');os.link(run/'ENGINE/stderr',run/'simulator.stderr')
  result=collect(run,spec)
  table(run/'FILES_SHA256.tsv',[dict(path=str(q.relative_to(run)),sha256=sha(q),bytes=q.stat().st_size) for q in sorted(run.rglob('*')) if q.is_file()])
  return result
 except BaseException as exc:
  write(run/'WRAPPER_EXCEPTION.json',dict(utc=now(),reason=repr(exc),engine=engine,no_retry=True),exclusive=True)
  if not (run/'RUN_TERMINAL.json').exists():write(run/'RUN_TERMINAL.json',dict(returncode=None,forced_reason=repr(exc),identity_pass=False,engine=engine),exclusive=True)
  if not (run/'STRICT.json').exists():write(run/'STRICT.json',dict(status='HOLD_STRICT_FAILED',performance_accepted=False,cycles='UNAVAILABLE',failure=repr(exc)),exclusive=True)
  raise
 finally:
  owner.pop('child_pid',None);owner.pop('child_start_ticks',None)
  for sig,handler in old.items():signal.signal(sig,handler)

def main(dispatch=False):
 require(dispatch,'EXPLICIT_DISPATCH_REQUIRED')
 require(not (RAW/'COHORT_TERMINAL.json').exists(),'TERMINAL_COHORT_NO_RESTART')
 manifest,head=publication_check();specs=[json.loads((PACK/n).read_text()) for n in manifest['ordered_specs']]
 require(not budget(specs),'ANY_PRIOR_START_NO_RESUME')
 results=[];failure=None
 with (RAW/'AG_execution.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);owner=proc(os.getpid());owner['lock']=str(RAW/'AG_execution.lock')
  write(RAW/'AUTHORITY_ACTIVE.json',dict(owner=owner,publication=head,max_concurrency=1),exclusive=True)
  try:
   for spec in specs:
    require_BASE_gate(spec,specs)
    result=run_one(spec,specs,owner);results.append(result);print('TERMINAL',spec['point'],result['status'],result.get('cycles'),flush=True)
    require(result['performance_accepted'],'STRICT_IDENTITY_RESOURCE_OR_CALIBRATION_STOP:'+spec['point'])
  except BaseException as exc:failure=repr(exc);print('COHORT_STOP',failure,flush=True)
  finally:
   write(RAW/'COHORT_TERMINAL.json',dict(utc=now(),status='STOP' if failure else 'COMPLETE_FIVE_POINT_DISCOVERY_WITH_IMPORTED_GEMM_CONTROL',reason=failure,reserved_starts=len(budget(specs)),actual_fork_children=len(list((RAW/'attempts').glob('*/ENGINE/FORK_CHILD.json'))),results=results,no_automatic_dispatch=True),exclusive=True)
 write(RAW/'AUTHORITY_RELEASE.json',dict(utc=now(),own_lock_closed=True,owner=owner,no_automatic_dispatch=True,foreign_signals=0),exclusive=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dispatch',action='store_true');a=p.parse_args();main(a.dispatch)
