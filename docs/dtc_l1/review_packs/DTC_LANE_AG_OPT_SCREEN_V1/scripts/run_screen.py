#!/usr/bin/env python3
"""One AG coordinator, fixed ordered reservations, one Popen per qualified UUID.

Not an executor until a full immutable registration has been pushed and fetched
back and PUBLICATION_READBACK.json has been written outside Git. Never resumes.
"""
from common import *
from strict_screen import require,input_identity,collect
from audit_site import snapshot,proc
from review_authority import review
from resource_policy import RuntimePolicy,admission_checks
import fcntl
import signal
import shutil
import time
import threading

def start_oom_watchdog(pid,pidfd,start_events,destination,event_path=Path('/sys/fs/cgroup/memory.events')):
 """Independent light poll stays active during identity hashes/full /proc audit.

 Only a direct, unreaped Popen child pidfd is accepted by the caller. This
 thread cannot launch anything and never signals by a name/group/session.
 """
 stopped=threading.Event();state=dict(reason=None,signal_sent=False)
 def work():
  with destination.open('x') as log:
   while not stopped.is_set():
    try:
     events=dict((k,int(v)) for k,v in (l.split() for l in event_path.read_text().splitlines()))
     reason='NEW_CGROUP_OOM_OR_OOM_KILL_LIGHT_WATCHDOG' if any(events[k]>start_events[k] for k in ['oom','oom_kill']) else None
    except Exception as exc:
     events=None;reason='OOM_WATCHDOG_READ_FAILURE:'+repr(exc)
    log.write(json.dumps(dict(utc=now(),monotonic_ns=time.monotonic_ns(),events=events,reason=reason))+'\n');log.flush()
    if reason:
     state['reason']=reason
     if not state['signal_sent']:
      try:signal.pidfd_send_signal(pidfd,signal.SIGTERM)
      except ProcessLookupError:pass
      state['signal_sent']=True
      log.write(json.dumps(dict(utc=now(),decision='STOP',signal='SIGTERM',api='pidfd_send_signal',own_direct_child=pid))+'\n');log.flush()
     return
    stopped.wait(.25)
 thread=threading.Thread(target=work,name='AG_owned_child_OOM_guard',daemon=False)
 thread.start();return stopped,thread,state

def publication_check():
 receipt=json.loads((RAW/'PUBLICATION_READBACK.json').read_text())
 commit=receipt['commit']
 require(receipt['fetched_commit']==commit,'published_fetch_back_commit')
 require(git(FW,'rev-parse','refs/ag-publication/preregistered')==commit,'local_fetch_back_ref')
 require(git(FW,'merge-base','--is-ancestor',commit,'HEAD')=='','published_registration_ancestor')
 manifest_path=PACK/'EXECUTABLE_PREREGISTRATION.json'
 require(sha(manifest_path)==receipt['manifest_sha256'],'immutable_registration_manifest')
 manifest=json.loads(manifest_path.read_text())
 require(manifest['status']=='EXECUTABLE_PREREGISTERED_NOT_YET_STARTED','full_registration_status')
 for path,digest in manifest['files'].items():
  require(sha(PACK/path)==digest,'registered_file_changed:'+path)
  require(hashlib.sha256(blob(FW,commit,str((PACK/path).relative_to(FW)))).hexdigest()==digest,'published_file_changed:'+path)
 require(git(CORE,'rev-parse','HEAD')==manifest['combined_core_commit'],'fixed_combined_Core')
 require(not git(CORE,'status','--porcelain'),'combined_Core_not_clean')
 for item in manifest['runtime_files']:
  require(sha(item['path'])==item['sha256'],'runtime_or_loader_changed:'+item['path'])
 require(not (RAW/'MATRIX_TERMINAL.json').exists(),'terminal_matrix_NO_AUTOMATIC_RESTART')
 return dict(commit=commit,manifest_sha256=sha(manifest_path)),manifest

def budget(specs):
 reservations={s['attempt_uuid'] for s in specs};starts=[]
 for p in (RAW/'attempts').glob('*/RUN_START.json'):
  r=json.loads(p.read_text());require(r['attempt_uuid'] in reservations,'foreign_UUID_in_AG_raw')
  starts.append(r['attempt_uuid'])
 require(len(starts)==len(set(starts)) and len(starts)<=8,'actual_start_budget_or_duplicate')
 return starts

def admission(run_label,owner):
 dest=RAW/'admissions'/run_label;dest.mkdir(parents=True,exist_ok=False)
 a=snapshot();write(dest/'FIRST.json',a)
 time.sleep(10.1)
 b=snapshot();write(dest/'SECOND.json',b)
 checks=admission_checks(a,b);authority=review(b,owner)
 decision=dict(utc=now(),resource_checks=checks,authority=authority,
     host_global_delta={k:b[k]-a[k] for k in ['pswpin','pswpout']},
     global_swap_decision='WARN_NOT_PROCESS_ATTRIBUTION' if any(b[k]>a[k] for k in ['pswpin','pswpout']) else 'NO_GLOBAL_INCREMENT',
     source='FRESH_BEFORE_EACH_ATTEMPT_ALL_PROJECTS_ALL_FDINFO_FLOCKS')
 write(dest/'DECISION.json',decision)
 require(all(checks.values()),'PRELAUNCH_RESOURCE_STOP:'+str(dest))
 require(all(authority['checks'].values()),'PRELAUNCH_AUTHORITY_STOP:'+str(dest))
 return dict(path=str(dest),sha256=sha(dest/'DECISION.json')),b

def mapped_files(text):
 return sorted({l.split(None,5)[5] for l in text.splitlines() if len(l.split(None,5))==6 and l.split(None,5)[5].startswith('/')})

def final_pre_popen_snapshot(owner,prior,destination):
 # The two >=10s samples already passed. Recheck current minimum admission
 # lines and authority after publication/config hashing, without inventing a
 # second time gap or launching into a newly degraded resource state.
 current=snapshot();checks=admission_checks(prior,current)
 fresh={k:v for k,v in checks.items() if k.startswith('second_') or k=='no_new_cgroup_oom'}
 authority=review(current,owner)
 write(destination,dict(utc=now(),snapshot=current,resource_checks=fresh,authority=authority),exclusive=True)
 require(all(fresh.values()),'FINAL_PRE_POPEN_RESOURCE_STOP')
 require(all(authority['checks'].values()),'FINAL_PRE_POPEN_AUTHORITY_STOP')
 return current

def attest_child(pid,spec,manifest,start_events=None):
 p=None;maps=''
 for _ in range(200):
  if start_events is not None:
   events=dict((k,int(v)) for k,v in (l.split() for l in Path('/sys/fs/cgroup/memory.events').read_text().splitlines()))
   require(not any(events[k]>start_events[k] for k in ['oom','oom_kill']),'NEW_CGROUP_OOM_OR_OOM_KILL_DURING_LOADER_ATTESTATION')
  p=proc(pid)
  try:maps=Path('/proc',str(pid),'maps').read_text()
  except OSError:pass
  if p and spec['runtime_library_path'] in maps:break
  time.sleep(.01)
 require(p is not None,'own_child_identity_missing')
 actual=[dict(path=x,sha256=sha(x)) for x in mapped_files(maps)]
 expected={str(Path(x['path']).resolve()):x['sha256'] for x in manifest['runtime_files']}
 bad=[x for x in actual if expected.get(str(Path(x['path']).resolve()))!=x['sha256']]
 identity=(str(Path(p['exe']).resolve())==str(Path(spec['runtime_path']).resolve()) and
     sha('/proc/'+str(pid)+'/exe')==spec['runtime_sha256'] and spec['runtime_library_path'] in maps and
     any(str(Path(x['path']).resolve())==str(Path(manifest['loader']['path']).resolve()) for x in actual) and not bad)
 return p,maps,actual,dict(status='PASS_EXACT_ACTUAL_ELF_LOADER_ALL_MAPPED_LIBRARIES' if identity else 'STOP_LOADED_IDENTITY',
     identity_pass=identity,unregistered_or_changed_mappings=bad)

def usage_record(usage):
 return {k:getattr(usage,k) for k in ['ru_utime','ru_stime','ru_maxrss','ru_minflt','ru_majflt','ru_inblock','ru_oublock','ru_nvcsw','ru_nivcsw']}

def run_one(spec,specs,owner,publication,manifest):
 label=spec['point'];uid=spec['attempt_uuid']
 require(uid not in budget(specs),'UUID_previously_started_NO_RETRY')
 publication_check();identity=input_identity(spec)
 adm,start=admission(label,owner)
 publication_check();require(uid not in budget(specs),'late_UUID_conflict')
 run=RAW/'attempts'/(label+'_'+uid);run.mkdir(parents=True,exist_ok=False)
 copies=[]
 for i,c in enumerate(spec['configs']):
  require(sha(c['path'])==c['sha256'],'prelaunch_config_mutation')
  dest=run/f'config-{i}.config';shutil.copy2(c['path'],dest);dest.chmod(0o444)
  copies.append(dict(path=str(dest),sha256=sha(dest)))
 args=[spec['runtime_path'],'-trace',spec['trace_list']]
 for c in copies:args.extend(['-config',c['path']])
 write(run/'SPEC.json',spec,exclusive=True)
 for name in ['run_screen.py','strict_screen.py','resource_policy.py']:
  shutil.copyfile(PACK/'scripts'/name,run/('immutable_'+name))
 start=final_pre_popen_snapshot(owner,start,run/'FINAL_PRE_POPEN.json')
 # This receipt is the conservative actual-start accounting boundary. Even a
 # failed Popen consumes the reservation; no post-failure replacement exists.
 write(run/'RUN_START.json',dict(utc=now(),attempt_uuid=uid,point=label,
     publication=publication,authority=owner,admission=adm,input_identity=identity,
     argv=args,config_copies=copies,environment=spec['runtime_environment'],
     single_Popen=True,retries=0,timeout_seconds=7200),exclusive=True)
 started=time.monotonic();forced=None;rc=None;usage=None;child=None;pidfd=None;pidrecord=None;identity_pass=False
 watchdog=None
 write(run/'RESOURCE_START.json',start,exclusive=True)
 policy=RuntimePolicy(start);previous_faults=0;next_full=started;last_progress=started
 interrupted=[]
 def interrupted_handler(signum,frame):interrupted.append(signum)
 old_handlers={s:signal.signal(s,interrupted_handler) for s in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]}
 try:
  with (run/'simulator.stdout').open('xb') as out,(run/'simulator.stderr').open('xb') as err,(run/'RESOURCE_MONITOR.jsonl').open('x') as monitor:
   child=subprocess.Popen(args,cwd=run,env=spec['runtime_environment'],stdout=out,stderr=err,close_fds=True)
   pidfd=os.pidfd_open(child.pid)
   write(run/'POPEN_CHILD.json',dict(utc=now(),pid=child.pid,initial_proc=proc(child.pid),
       actual_exec_Popen_returned=True,scientific_UUID=uid),exclusive=True)
   watchdog=start_oom_watchdog(child.pid,pidfd,start['cgroup']['events'],run/'OOM_LIGHT_POLL.jsonl')
   pidrecord,maps,files,attest=attest_child(child.pid,spec,manifest,start['cgroup']['events'])
   identity_pass=attest['identity_pass']
   owner['child_pid']=child.pid;owner['child_start_ticks']=pidrecord['start_ticks']
   write(run/'PID.json',pidrecord,exclusive=True);(run/'PROCESS_MAPS.txt').write_text(maps)
   write(run/'LOADED_FILES_SHA256.json',files,exclusive=True);write(run/'ACTUAL_IDENTITY.json',attest,exclusive=True)
   if not identity_pass:forced='ACTUAL_PROCESS_LOADER_OR_LIBRARY_IDENTITY_STOP'
   while True:
    if watchdog[2]['reason'] and forced is None:forced=watchdog[2]['reason']
    if not watchdog[1].is_alive() and not watchdog[2]['reason'] and forced is None:
     forced='OOM_WATCHDOG_STOPPED_UNEXPECTEDLY'
    got,status,rusage=os.wait4(child.pid,os.WNOHANG)
    if got:
     rc=os.waitstatus_to_exitcode(status);child.returncode=rc;usage=usage_record(rusage);break
    instant=time.monotonic()
    events=dict((k,int(v)) for k,v in (l.split() for l in Path('/sys/fs/cgroup/memory.events').read_text().splitlines()))
    if any(events[k]>start['cgroup']['events'][k] for k in ['oom','oom_kill']) and forced is None:
     forced='NEW_CGROUP_OOM_OR_OOM_KILL_LIGHT_POLL'
     monitor.write(json.dumps(dict(utc=now(),monotonic_ns=time.monotonic_ns(),decision='STOP',reason=forced,events=events))+'\n');monitor.flush()
    if interrupted and forced is None:forced='COORDINATOR_SIGNAL_'+str(interrupted[0])
    if instant-started>=7200 and forced is None:forced='TIMEOUT_7200_SECONDS'
    if instant>=next_full:
     current=snapshot();own=proc(child.pid)
     fault=own['majflt'] if own else previous_faults
     decision=policy.observe(current,fault,previous_faults);previous_faults=fault
     authority=review(current,owner)
     if not all(authority['checks'].values()) and forced is None:forced='CURRENT_AUTHORITY_OR_FLOCK_NOT_CLOSED'
     if decision['decision']=='STOP' and forced is None:forced=';'.join(decision['stop_reasons'])
     monitor.write(json.dumps(dict(snapshot=current,own=own,resource_decision=decision,authority=authority,forced_reason=forced))+'\n');monitor.flush()
     next_full=time.monotonic()+decision['next_full_sample_seconds']
     if instant-last_progress>=60 or decision['decision']!='CONTINUE' or forced:
      print(json.dumps(dict(point=label,elapsed_seconds=round(instant-started),pid=child.pid,
          resource=decision['decision'],reasons=decision['warnings']+decision['stop_reasons'],forced=forced)),flush=True)
      last_progress=instant
    if forced and not watchdog[2]['signal_sent'] and not (run/'OWN_STOP_SIGNAL.json').exists():
     current=proc(child.pid)
     require(current and current['start_ticks']==pidrecord['start_ticks'],'own_child_PID_startticks_before_signal')
     write(run/'OWN_STOP_SIGNAL.json',dict(utc=now(),reason=forced,pid=child.pid,start_ticks=pidrecord['start_ticks'],
         signal='SIGTERM',api='pidfd_send_signal',foreign_signals=0),exclusive=True)
     signal.pidfd_send_signal(pidfd,signal.SIGTERM)
     watchdog[2]['signal_sent']=True
    time.sleep(.5)
 except BaseException as exc:
  forced=forced or (watchdog[2]['reason'] if watchdog else None) or 'RUNNER_EXCEPTION:'+repr(exc)
  if child is not None and child.returncode is None:
   # pidfd refers only to our direct Popen child. No name/group/foreign signal.
   got,status,rusage=os.wait4(child.pid,os.WNOHANG)
   if not got:
    if pidfd is None:pidfd=os.pidfd_open(child.pid)
    try:signal.pidfd_send_signal(pidfd,signal.SIGTERM)
    except ProcessLookupError:pass  # Exit raced with our owned-child cleanup.
    _,status,rusage=os.wait4(child.pid,0)
   rc=os.waitstatus_to_exitcode(status);child.returncode=rc;usage=usage_record(rusage)
 finally:
  if watchdog is not None:
   watchdog[0].set();watchdog[1].join()
   forced=forced or watchdog[2]['reason']
  if pidfd is not None:os.close(pidfd)
  for s,h in old_handlers.items():signal.signal(s,h)
  owner.pop('child_pid',None);owner.pop('child_start_ticks',None)
 write(run/'RUN_TERMINAL.json',dict(utc=now(),returncode=rc,forced_reason=forced,identity_pass=identity_pass,
     host_wall_seconds_noncomparative=time.monotonic()-started,resource_usage=usage,PID=pidrecord),exclusive=True)
 write(run/'RESOURCE_FINAL.json',snapshot(),exclusive=True)
 result=collect(run,spec)
 table(run/'FILES_SHA256.tsv',[dict(path=str(p.relative_to(run)),sha256=sha(p),bytes=p.stat().st_size)
     for p in sorted(run.rglob('*')) if p.is_file() and p.name!='FILES_SHA256.tsv'])
 return result

def main():
 # No --resume, retry, selective arm or altered timeout interface exists.
 publication,manifest=publication_check()
 specs=[json.loads((PACK/p).read_text()) for p in manifest['ordered_specs']]
 require([s['point'] for s in specs]==['BASE_GEMM','BASE_Gaussian','AC_GEMM','AC_Gaussian','AD_GEMM','AD_Gaussian','AE_GEMM','AE_Gaussian'],'fixed_order')
 require(not budget(specs),'PREEXISTING_AG_START_NO_AUTOMATIC_RESTART')
 with (RAW/'AG_execution.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  owner=proc(os.getpid());owner['lock']=str(RAW/'AG_execution.lock');owner['max_new_sim_concurrency']=1
  write(RAW/'AUTHORITY_ACTIVE.json',dict(utc=now(),owner=owner),exclusive=True)
  results=[];failure=None
  try:
   for spec in specs:
    if spec['qualification']=='HOLD_UNQUALIFIED':
     result=dict(point=spec['point'],attempt_uuid=spec['attempt_uuid'],status='HOLD_UNQUALIFIED',reason=spec['qualification_reason'],actual_start=False)
     results.append(result);write(RAW/'HOLDS'/ (spec['point']+'.json'),result,exclusive=True);continue
    if spec['arm']!='BASE':require(len([r for r in results if r.get('arm')=='BASE' and r.get('performance_accepted')])==2,'BOTH_COMMON_BASES_STRICT_AND_CALIBRATION_REQUIRED')
    result=run_one(spec,specs,owner,publication,manifest);results.append(result)
    print('TERMINAL',spec['point'],result['status'],result.get('cycles'),flush=True)
    require(result['performance_accepted'],'STOP_AFTER_FAILED_ATTEMPT_STRICT_OR_BASE_CALIBRATION:'+spec['point'])
  except BaseException as exc:
   failure=repr(exc);print('MATRIX_STOP',failure,flush=True)
  finally:
   write(RAW/'MATRIX_TERMINAL.json',dict(utc=now(),status='STOP' if failure else 'ALL_FIXED_SLOTS_TERMINAL',
       reason=failure,actual_starts=len(budget(specs)),results=results,no_automatic_dispatch_remaining=True),exclusive=True)
   write(RAW/'AUTHORITY_TERMINAL.json',dict(utc=now(),owner=owner,own_child_reaped=True,
       lock_release='ON_FILE_CONTEXT_RETURN',foreign_signals=0),exclusive=True)

if __name__=='__main__':main()
