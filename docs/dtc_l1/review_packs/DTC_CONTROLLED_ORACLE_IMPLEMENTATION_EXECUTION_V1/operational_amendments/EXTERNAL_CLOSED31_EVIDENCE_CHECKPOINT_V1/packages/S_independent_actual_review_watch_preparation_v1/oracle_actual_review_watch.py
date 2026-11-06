"""Independent CPU-only actual-closure reviewer. Default is inert preparation.

Only the frozen original reviewer may write its original narrow qualification
receipts. No models, scientific registration, dispatch or budget writes exist.
"""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,subprocess,time,types

BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1');ROOT=BASE/'initial8'
REQUEST='DTC_ORACLE_INITIAL8_20261106_V1'
PLAN_SHA='6bb3876db0fe5dc7ef4544e7a0a03f822a53da73129daed9bce5bc9d822c53b0'
MATRIX_SHA='658fc5f35827d3c516b8d3eba06501b33e0d55dc1d546a4ae832ef9819e7b81a'
RUNNER_SHA='12608931a0c7b904722360b751f2aa10a15219e1d5a5eafd8076969638c5341d'
REVIEWER_SHA='2446f7db384b4df2977decface1fb49fe42af1939b3cbb091112f6cb1809edc7'
RESOURCE_SHA='3f20a6bb18d401825a84eb5445c00d0771c449fa5766ddd434d9f284b7ff4b7f'
ENGINE_SHA='5f978c77586f3be030ca0295adb6eec09d8152254df1f88f85becb45588850d9'
PASS='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE'
JOB_LOCK=BASE/'control/ORACLE_INDEPENDENT_ACTUAL_REVIEW_JOB.lock'
WORKER_LOCK=BASE/'control/ORACLE_INDEPENDENT_ACTUAL_REVIEW_WATCH.lock'

class Hold(RuntimeError):pass
def need(x,why):
 if not x:raise Hold(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def pin(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def load(p,name):
 p=Path(p);m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def write(path,value,exclusive=False):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
 if exclusive:
  with path.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 else:
  tmp=path.with_name('.'+path.name+'.'+str(os.getpid())+'.writing');tmp.write_bytes(b);os.replace(tmp,path)

def closed_result(root,row):
 """Only stable naturally accepted exact result identity; never rank by speed."""
 path=Path(root)/'analysis'/(row['cohort']+'.RESULT.json')
 if not path.exists():return None
 a=path.stat();data=path.read_bytes();b=path.stat()
 if (a.st_size,a.st_mtime_ns)!=(b.st_size,b.st_mtime_ns)or not data.endswith(b'\n'):return None
 try:value=json.loads(data)
 except (ValueError,UnicodeDecodeError):return None
 if value.get('state')!=PASS:return None
 need(value.get('cohort')==row['cohort']and value.get('input_digest')==row['input_digest']
      and value.get('plan_id')==row['plan_id']and value.get('oracle_mode')==row['mode'],'RESULT_FROZEN_ROW_IDENTITY')
 need(value.get('proof',{}).get('performance_accepted')is True,'RESULT_STRICT_ACCEPTANCE')
 return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),uuid=value['uuid'])

def complete_json(path):
 path=Path(path)
 if not path.exists():return False
 a=path.stat();data=path.read_bytes();b=path.stat()
 if (a.st_size,a.st_mtime_ns)!=(b.st_size,b.st_mtime_ns)or not data.endswith(b'\n'):return False
 try:json.loads(data);return True
 except (ValueError,UnicodeDecodeError):return False

def select_ready(plan,points,results,existing_cohorts,existing_modes):
 """Pure fixed-set readiness; HOLD/negative/missing rows do not become accepted."""
 need(len(points)==32 and len({x['cohort']for x in points})==32,'FIXED32_ROWS_REQUIRED')
 need(len({x['input_digest']for x in points})==8,'FIXED8_INPUTS_REQUIRED')
 jobs=[];qual=plan['initial_qualifiers']
 for mode,c in qual.items():
  if c not in existing_cohorts and results.get(c)is not None:jobs.append(dict(kind='cohort',subject=c))
 for mode in plan['qualified_modes']:
  if mode in existing_modes:continue
  members=[p for p in points if p['mode']in['OFF_MATCHED',mode]]
  need(len(members)==16 and len({x['input_digest']for x in members})==8,'EXACT_MODE_AND_SHARED_OFF8')
  if not all(results.get(p['cohort'])is not None for p in members):continue
  if not {qual['OFF_MATCHED'],qual[mode]}<=set(existing_cohorts):continue
  jobs.append(dict(kind='mode',subject=mode))
 return jobs

def validate_release(path,expected_sha):
 need(sha(path)==expected_sha,'EXACT_MAIN_RELEASE_PIN')
 release=rd(path)
 need(release['schema']=='DTC_ORACLE_CPU_ACTUAL_REVIEW_WATCH_RELEASE_V1'
      and release['status']=='APPROVED_CPU_REVIEW_ONLY'
      and release['worker_source_sha256']==sha(__file__)
      and release['request']==REQUEST and release['new_scientific_starts']==0,
      'CPU_REVIEW_ONLY_MAIN_RELEASE_REQUIRED')
 review=rd(pin(release['independent_review']))
 need(review['status']=='PASS'and review['scope']=='INDEPENDENT_CPU_ONLY_ACTUAL_REVIEW_WATCH'
      and review['subject_source_sha256']==sha(__file__),'EXACT_INDEPENDENT_REVIEW_REQUIRED')
 need(sha(ROOT/'control/EXECUTION_PLAN.json')==PLAN_SHA
      and sha(ROOT/'control/MATRIX.fixed.json')==MATRIX_SHA,'FROZEN_PLAN_MATRIX_REQUIRED')
 for name,h in [('oracle_actual_review_runner.py',RUNNER_SHA),('oracle_actual_qualification_reviewer.py',REVIEWER_SHA),
                ('oracle_resources.py',RESOURCE_SHA),('oracle_native.py',ENGINE_SHA)]:
  need(sha(ROOT/'tools'/name)==h,'EXACT_FROZEN_REVIEW_CHAIN_REQUIRED:'+name)
 return release

def run(release_path,release_sha,interval=15):
 """Actual entry is dormant until Main release; CPU tests never call it."""
 release=validate_release(release_path,release_sha)
 evidence=Path(release['engineering_evidence_root']);evidence.mkdir(parents=True,exist_ok=False)
 plan=rd(ROOT/'control/EXECUTION_PLAN.json');points=rd(ROOT/'control/MATRIX.fixed.json')['points']
 engine=load(ROOT/'tools/oracle_native.py','INDEPENDENT_REVIEW_READ_ENGINE')
 resources=load(ROOT/'tools/oracle_resources.py','INDEPENDENT_REVIEW_PURE_GATES')
 cooldown={};completed={};worker_state=dict(schema='DTC_CPU_ONLY_ACTUAL_REVIEW_WATCH_STATE_V1',pid=os.getpid(),
     models_started=0,scientific_registrations=0,budget_writes=0,source_sha256=sha(__file__))
 with WORKER_LOCK.open('a+b')as held:
  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
  while True:
   validate_release(release_path,release_sha)
   q=engine.registered()[2];need(q['request']==REQUEST and q['budget']==32,'EXACT_ORIGINAL32')
   results={p['cohort']:closed_result(ROOT,p)for p in points}
   existing={};modes={}
   for c in plan['initial_qualifiers'].values():
    p=ROOT/'control/actual_qualification_reviews'/(c+'.json')
    if complete_json(p):existing[c]=resources._qualifier_review(plan,c,q) # validate and reuse; never rerun/overwrite
   for mode in plan['qualified_modes']:
    p=Path(plan['mode_gate2_reviews'][mode])
    if complete_json(p):modes[mode]=resources.verify_mode_extension_receipt(plan,mode)
   worker_state.update(valid_cohort_reviews=existing,valid_mode_reviews=modes,
                       accepted_closed_results=sum(v is not None for v in results.values()),
                       updated_unix_seconds=time.time(),executing=None)
   write(evidence/'STATE.json',worker_state)
   if len(modes)==len(plan['qualified_modes']):
    write(evidence/'COMPLETE.fixed.json',dict(worker_state,status='ALL_FIXED_MODE_GATE2_REVIEWED_NO_NEW_SCIENCE'),True);return
   if (evidence/'STOP_NEW_REVIEWS.json').exists():
    write(evidence/'STOPPED.fixed.json',dict(worker_state,status='CPU_REVIEW_ADMISSION_STOPPED_NO_CHILD_KILLED'),True);return
   jobs=select_ready(plan,points,results,existing,modes)
   jobs=[j for j in jobs if time.monotonic()>=cooldown.get((j['kind'],j['subject']),0)]
   if not jobs:time.sleep(interval);continue
   job=jobs[0];tail=['--mode',job['subject']]if job['kind']=='mode'else[job['subject']]
   command=['/usr/bin/python3','-B',str(ROOT/'tools/oracle_actual_review_runner.py'),str(ROOT),*tail]
   with JOB_LOCK.open('a+b')as joblock:
    try:fcntl.flock(joblock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:time.sleep(interval);continue
    # Recheck canonical target after lock, to coexist with the real B pool's
    # identically locked CPU review queue. No two writers run the same review.
    target=Path(plan['mode_gate2_reviews'][job['subject']])if job['kind']=='mode'else ROOT/'control/actual_qualification_reviews'/(job['subject']+'.json')
    if target.exists():continue
    seq=str(time.time_ns());begin=dict(job=job,argv=command,source_sha256=sha(__file__),
         runner_sha256=RUNNER_SHA,reviewer_sha256=REVIEWER_SHA,review_results_are_not_models=True)
    write(evidence/(seq+'.BEGIN.json'),begin,True)
    # Child shares this exact OFD. A dead watch parent cannot release the job
    # lock while its real verifier is still reading/writing its narrow receipt.
    child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,pass_fds=(joblock.fileno(),))
    while child.poll()is None:
     worker_state.update(executing=dict(job=job,CPU_child_pid=child.pid),updated_unix_seconds=time.time())
     write(evidence/'STATE.json',worker_state);time.sleep(1)
    stdout,stderr=child.communicate()
    write(evidence/(seq+'.END.json'),dict(begin,returncode=child.returncode,stdout=stdout,stderr=stderr,
          no_model_or_child_signals=True),True)
    cooldown[(job['kind'],job['subject'])]=time.monotonic()+60
    # The frozen runner emits its own HOLD evidence on verifier rejection.
    # We never promote, fabricate or overwrite that result.

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--release');parser.add_argument('--release-sha');parser.add_argument('--interval',type=int,default=15)
 a=parser.parse_args()
 if not a.run:print(json.dumps(dict(status='PREPARATION_ONLY',scientific_starts=0)));return
 need(a.release and a.release_sha and 5<=a.interval<=300,'MAIN_RELEASE_AND_VALID_INTERVAL_REQUIRED')
 run(a.release,a.release_sha,a.interval)
if __name__=='__main__':main()
