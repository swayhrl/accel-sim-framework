"""Finite, resumable shared-asset Goal stages; never launches a scientific job."""
from pathlib import Path
import json,os,sys,time,subprocess,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
def status(stage,**kw):
 d={'stage':stage,'utc_unix':time.time(),**kw};tmp=R/'control/GOAL_STATE.writing';tmp.write_text(json.dumps(d)+'\n');os.replace(tmp,R/'control/GOAL_STATE.json');print(json.dumps(d),flush=True)
def run(script,args=[],marker=None):
 if marker and (R/'control'/marker).exists():return
 status(script)
 with (R/'logs'/('stage_'+script+'.log')).open('a') as f:
  cp=subprocess.run(['python3','-B',str(R/'tools'/script)]+args,stdout=f,stderr=subprocess.STDOUT)
 if cp.returncode:status('ATTENTION',script=script,returncode=cp.returncode,log=str(R/'logs'/('stage_'+script+'.log')));raise RuntimeError(script+' held')
status('WAIT_SOURCE_FULL_SHA')
deadline=time.monotonic()+24*3600
while not (R/'control/174_HASH_COMPLETE.json').exists():
 if time.monotonic()>deadline:raise RuntimeError('finite source SHA wait deadline')
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
