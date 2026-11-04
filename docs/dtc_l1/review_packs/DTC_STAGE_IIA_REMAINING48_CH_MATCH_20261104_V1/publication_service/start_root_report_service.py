from pathlib import Path
import json,hashlib,subprocess,fcntl,os,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
D=A/'publication_service_v1';src=D/'report_only_publisher.py'
def rd(p):return json.loads(p.read_bytes())
def put(p,v):
 t=p.with_suffix('.writing');t.write_text(json.dumps(v,indent=2)+'\n');os.replace(t,p)
def proc_identity(pid):
 stat=Path('/proc/'+str(pid)+'/stat').read_text().rsplit(')',1)[1].split()
 return dict(start_ticks=int(stat[19]),state=stat[0])
with(D/'ROOT_SERVICE_START.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 contract=rd(D/'SERVICE_CONTRACT.json');checks=rd(D/'CPU_CHECKS.json');s=hashlib.sha256(src.read_bytes()).hexdigest()
 assert contract['source_sha256']==s==checks['source_sha256']and checks['passed']>=16
 old=D/'ROOT_SERVICE_START_RECEIPT.json'
 if old.exists():
  prior=rd(old)
  try:
   identity=proc_identity(prior['pid']);live=identity['start_ticks']==prior['start_ticks']and identity['state']not in ['Z','X']
  except FileNotFoundError:live=False
  if live:print(json.dumps({'already_live':True,**prior}));raise SystemExit(0)
  raise RuntimeError('Prior publication process is no longer live; preserve evidence and review, do not silently restart')
 out=(D/'publisher.log').open('ab',buffering=0)
 child=subprocess.Popen(['python3','-B',str(src)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True,cwd=str(D),env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 v=dict(pid=child.pid,start_ticks=proc_identity(child.pid)['start_ticks'],source_sha256=s,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='ROOT_REPORT_ONLY_GIT_PUBLISHER_NOT_MODEL_DISPATCHER',interval_seconds=1800,scientific_starts=0,native_writes=0)
 put(old,v);print(json.dumps(v))
