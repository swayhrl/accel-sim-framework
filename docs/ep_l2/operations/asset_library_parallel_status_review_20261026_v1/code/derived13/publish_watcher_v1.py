#!/usr/bin/env python3
"""Finite watcher for exact13 prepared outputs. No source/target writer lock."""
import pathlib,json,hashlib,subprocess,time,os,sys,signal,resource,fcntl
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.tmp')
 with t.open('w')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def main():
 gp=pathlib.Path(sys.argv[1]).resolve();g=json.loads(gp.read_text());assert g['status']=='APPROVED_FINITE_DERIVED_CATCHUP_PUBLISH_V1'
 for x in g['code']:
  p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 assert sha(R/'SCOPE.json')==g['scope_sha256'];scope=json.loads((R/'SCOPE.json').read_text());assert len(scope['rows'])==13
 run=pathlib.Path(g['run_root']);assert str(run).startswith(str(R)+'/run_')
 end=time.monotonic()+30*3600
 while not run.exists():
  assert time.monotonic()<end;time.sleep(2)
 lock=(R/'DERIVED_PUBLISH_WATCHER.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 resource.setrlimit(resource.RLIMIT_AS,(256*2**20,1536*2**20));rows=[];done=set();child=None;child_ticks=None
 def term(a,b):raise KeyboardInterrupt('watcher signal')
 signal.signal(signal.SIGTERM,term);signal.signal(signal.SIGHUP,term)
 pidticks=pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19];save(run/'PUBLISH_WATCHER_START.json',{'pid':os.getpid(),'start_ticks':pidticks,'scope_sha256':g['scope_sha256'],'grant_sha256':sha(gp)})
 try:
  while len(done)<13:
   assert time.monotonic()<end,'watcher deadline'
   for i,row in enumerate(scope['rows']):
    if i in done:continue
    prepared=run/'work'/row['parent_asset_id']/'PREPARED.json'
    if not prepared.exists():continue
    with (run/('%02d.publish.log'%i)).open('xb')as f:
     child=subprocess.Popen([sys.executable,'-B',str(R/'publish_one_derived_nas_v1.py'),str(gp),str(prepared.parent/'derived')],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
     child_ticks=pathlib.Path('/proc/%d/stat'%child.pid).read_text().split(') ',1)[1].split()[19]
     rc=child.wait(timeout=8*3600);child=None
    assert rc==0,'publisher nonzero; no retry'
    rows.append({'index':i,'asset_id':row['derived_asset_id'],'status':'COMMITTED_VERIFIED','returncode':rc});done.add(i);save(run/'PUBLISH_STATE.json',{'status':'RUNNING','rows':rows})
   if (run/'EXCEPTION.json').exists():raise RuntimeError('prepare exception retained')
   terminal=run/'TERMINAL.json'
   if terminal.exists() and json.loads(terminal.read_text())['status']!='PREPARE_COMPLETE':raise RuntimeError('prepare failure retained')
   if len(done)<13:time.sleep(2)
  save(run/'PUBLISH_TERMINAL.json',{'status':'ALL13_DERIVED_COMMITTED_VERIFIED','rows':rows,'source_KEEP':True,'release_bytes':0,'scientific_qualification_granted':False})
 except BaseException as e:
  save(run/'PUBLISH_EXCEPTION.json',{'status':'FAILED_RETAINED','exception':type(e).__name__,'reason':str(e),'rows':rows});raise
 finally:
  if child is not None and child.poll() is None:
   fd=os.pidfd_open(child.pid)
   try:
    actual=pathlib.Path('/proc/%d/stat'%child.pid).read_text().split(') ',1)[1].split()[19]
    if actual==child_ticks:signal.pidfd_send_signal(fd,signal.SIGTERM)
    try:child.wait(timeout=10)
    except subprocess.TimeoutExpired:
     if pathlib.Path('/proc/%d/stat'%child.pid).read_text().split(') ',1)[1].split()[19]==child_ticks:signal.pidfd_send_signal(fd,signal.SIGKILL)
     child.wait(timeout=10)
   finally:os.close(fd)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
