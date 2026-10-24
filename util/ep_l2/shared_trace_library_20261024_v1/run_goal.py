"""Finite, resumable shared-asset Goal stages; never launches a scientific job."""
from pathlib import Path
import json,os,sys,time,subprocess,hashlib,fcntl
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
lease=(R/'control/SUPERVISOR.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
os.nice(19)
ticks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
(R/'control/SUPERVISOR_PID.json').write_text(json.dumps({'pid':os.getpid(),'start_ticks':ticks,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'finite_goal_only':True})+'\n')
def status(stage,**kw):
 d={'stage':stage,'utc_unix':time.time(),**kw};tmp=R/'control/GOAL_STATE.writing';tmp.write_text(json.dumps(d)+'\n');os.replace(tmp,R/'control/GOAL_STATE.json');print(json.dumps(d),flush=True)
def run(script,args=[],marker=None):
 if marker and (R/'control'/marker).exists():return
 while True:
  status(script)
  path=R/'logs'/('stage_'+script+'.log')
  offset=path.stat().st_size if path.exists() else 0
  with path.open('a') as f:
   cp=subprocess.run(['python3','-B',str(R/'tools'/script)]+args,stdout=f,stderr=subprocess.STDOUT)
  if not cp.returncode:return
  with path.open() as f:f.seek(offset);tail=f.read()[-32768:]
  if ('RESOURCE_HOLD_' in tail or 'BlockingIOError: [Errno 11]' in tail) and time.monotonic()<deadline:
   status('WAIT_RESOURCE',script=script,returncode=cp.returncode,log=str(path),retry_seconds=60)
   time.sleep(60);continue
  status('ATTENTION',script=script,returncode=cp.returncode,log=str(path));raise RuntimeError(script+' held')
status('WAIT_SOURCE_FULL_SHA')
deadline=time.monotonic()+24*3600
while not (R/'control/174_HASH_COMPLETE.json').exists():
 if time.monotonic()>deadline:raise RuntimeError('finite source SHA wait deadline')
 # A disconnected client may end only the owned source-hash driver. Resume its
 # already flushed SHA ledger after freshness expires; never start a second
 # driver while an exact existing Goal driver is alive.
 active=[]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:argv=(proc/'cmdline').read_bytes().split(b'\0')
  except OSError:continue
  if len(argv)>3 and argv[2]==str(R/'tools/hash_driver.py').encode() and argv[3]==b'174':active.append(int(proc.name))
 progress=R/'control/174_HASH_PROGRESS.json'
 if not active and (not progress.exists() or time.time()-progress.stat().st_mtime>90):run('hash_driver.py',['174'],marker='174_HASH_COMPLETE.json')
 time.sleep(10)
run('prepare_native_hash.py',marker='174-new_HASH_COMPLETE.json')
run('hash_driver.py',['174-new'],marker='174-new_HASH_COMPLETE.json')
run('qualify_native.py',marker='NATIVE_BACKEND_QUALIFICATION.json')
run('build_expanded_plan.py',marker='EXPANDED_FROZEN_BUDGET.json')
run('adopt_prior.py',marker='PRIOR_ADOPTION_COMPLETE.json')
(R/'control/PRIOR_ADOPTION_COMPLETE.json').write_text('{"status":"PASS"}\n')
run('transfer_batches.py',['EXPANDED_BATCHES.json'],marker='EXPANDED_BATCHES_TRANSFER_COMPLETE.json')
run('archive_driver.py',marker='ARCHIVE_COMPLETE.json')
run('build_archive_plan.py',marker='ARCHIVE_FROZEN_BUDGET.json')
run('transfer_batches.py',['ARCHIVE_BATCHES.json'],marker='ARCHIVE_BATCHES_TRANSFER_COMPLETE.json')
run('publish_library.py',marker='LIBRARY_PUBLICATION.json')
run('cross_project_validate.py',marker='CROSS_PROJECT_VALIDATION.json')
run('restore_all_windows.py',marker='BOUNDED_NATIVE_RESTORE_COMPLETE.json')
run('finish_report.py',marker='FINAL_VALIDATION.json')
status('DATA_ACCESS_AND_REPORT_VERIFIED_GIT_PUBLICATION_PENDING')
