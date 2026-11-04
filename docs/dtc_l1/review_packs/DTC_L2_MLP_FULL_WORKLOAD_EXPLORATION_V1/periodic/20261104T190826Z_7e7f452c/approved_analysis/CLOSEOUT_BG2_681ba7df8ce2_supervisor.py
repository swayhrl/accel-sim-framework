from pathlib import Path
import argparse,json,hashlib,os,sys,time,subprocess,fcntl,datetime
P=Path
p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();cfg=P(a.config);c=json.loads(cfg.read_bytes());base=cfg.parent

def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(n,v):
 t=base/(n+'.tmp');t.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');os.replace(t,base/n)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(__file__)==c['supervisor_sha256']
with(base/'supervisor.lock').open('a+b')as lk:
 fcntl.flock(lk,fcntl.LOCK_EX|fcntl.LOCK_NB)
 s=P('/proc/self/stat').read_text().rsplit(')',1)[1].split();own=dict(pid=os.getpid(),start_ticks=int(s[19]),source_sha256=sha(__file__),configuration_sha256=sha(cfg),not_a_model_controller=True,not_a_git_publisher=True);put('SUPERVISOR_PID.json',own)
 attempt=0
 while not(base/'STOP').exists():
  for key in ['daemon','analysis_configuration']:
   assert sha(c[key]['path'])==c[key]['sha256'],'SOURCE_CHANGED_HOLD '+key
  out=P(c['output_root']);st=out/'STATE.json'
  if st.exists() and json.loads(st.read_bytes()).get('status')=='ALL_REGISTERED_AND_HISTORICAL_COMPLETE_REMOTE_VERIFIED':
   put('SUPERVISOR_STATE.json',dict(UTC=stamp(),status='FINAL_REMOTE_VERIFIED',attempt=attempt,**own));break
  attempt+=1
  with(base/'analysis.stdout.log').open('ab',buffering=0)as log:
   child=subprocess.Popen([sys.executable,'-B',c['daemon']['path'],'--config',c['analysis_configuration']['path']],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   childstat=P('/proc',str(child.pid),'stat').read_text().rsplit(')',1)[1].split();put('SUPERVISOR_STATE.json',dict(UTC=stamp(),status='ANALYSIS_RUNNING',attempt=attempt,child_pid=child.pid,child_start_ticks=int(childstat[19]),**own));rc=child.wait()
  put('SUPERVISOR_STATE.json',dict(UTC=stamp(),status='CHILD_EXITED',attempt=attempt,returncode=rc,**own))
  if rc==0:
   put('SUPERVISOR_STATE.json',dict(UTC=stamp(),status='CHILD_COMPLETED_REMOTE_VERIFIED',attempt=attempt,returncode=rc,**own));break
  # Child owns its single-process flock. Restart after crash; no simulator signals or dispatcher changes.
  time.sleep(60)
