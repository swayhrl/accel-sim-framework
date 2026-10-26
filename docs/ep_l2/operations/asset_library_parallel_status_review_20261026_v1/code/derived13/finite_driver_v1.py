#!/usr/bin/env python3
"""Finite two-slot preparation only; no GPU, simulator, public catalog writes."""
import pathlib,json,hashlib,os,sys,time,fcntl,subprocess,signal,resource
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.tmp')
 with t.open('w') as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def ticks(pid):
 try:return pathlib.Path('/proc/%d/stat'%pid).read_text().split(') ',1)[1].split()[19]
 except FileNotFoundError:return None
def stop(p,t):
 if ticks(p.pid)==t:
  fd=os.pidfd_open(p.pid)
  try:
   if ticks(p.pid)==t:signal.pidfd_send_signal(fd,signal.SIGTERM)
  finally:os.close(fd)
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:
   if ticks(p.pid)==t:
    fd=os.pidfd_open(p.pid)
    try:
     if ticks(p.pid)==t:signal.pidfd_send_signal(fd,signal.SIGKILL)
    finally:os.close(fd)
   p.wait(timeout=10)
def main():
 resource.setrlimit(resource.RLIMIT_AS,(256*2**20,1536*2**20))
 gp=pathlib.Path(sys.argv[1]).resolve();g=json.loads(gp.read_text());assert g['status']=='APPROVED_FINITE_DERIVED_CATCHUP_PREPARE_V1'
 assert g['concurrency'] in [1,2] and g['run_root'].startswith(str(R)+'/run_')
 for x in g['code']:
  p=R/x['path'];assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes']
 assert sha(R/'SCOPE.json')==g['scope_sha256'];scope=json.loads((R/'SCOPE.json').read_text());assert len(scope['rows'])==13
 run=pathlib.Path(g['run_root']);run.mkdir(exist_ok=False);(run/'work').mkdir();active={};rows=[];deadline=time.monotonic()+30*3600
 lease=(R/'DERIVED_PREPARE_CONTROLLER.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
 pending=list(range(len(scope['rows'])));halt=False
 def term(a,b):raise KeyboardInterrupt('controller signal')
 signal.signal(signal.SIGTERM,term);signal.signal(signal.SIGHUP,term)
 save(run/'PROCESS_START.json',{'pid':os.getpid(),'start_ticks':ticks(os.getpid()),'scope_sha256':g['scope_sha256'],'grant_sha256':sha(gp),'source_KEEP':True,'release_bytes':0})
 try:
  while pending or active:
   assert time.monotonic()<deadline,'batch deadline'
   while pending and not halt and len(active)<g['concurrency']:
    i=pending.pop(0);log=(run/('%02d.stdout.log'%i)).open('xb')
    p=subprocess.Popen([sys.executable,'-B',str(R/'derive_worker_v1.py'),str(gp),str(i)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    active[i]=(p,ticks(p.pid),log,time.monotonic())
   for i,(p,t,log,started) in list(active.items()):
    if p.poll() is None:
     if time.monotonic()-started>6*3600:stop(p,t)
     else:continue
    rc=p.wait();log.close();rows.append({'index':i,'parent_asset_id':scope['rows'][i]['parent_asset_id'],'exit':rc,'status':'PREPARED_VALIDATED_NOT_PUBLISHED' if rc==0 else 'FAILED_RETAINED'});del active[i]
    if rc!=0:halt=True;pending=[]
   save(run/'STATE.json',{'status':'RUNNING' if active else ('FAILED_RETAINED' if halt else 'DRAINED'),'rows':rows,'active':[{'index':i,'pid':v[0].pid,'start_ticks':v[1]} for i,v in active.items()],'pending':pending})
   if active:time.sleep(2)
  save(run/'TERMINAL.json',{'status':'PREPARE_COMPLETE' if not halt and len(rows)==13 else 'FAILED_RETAINED','rows':rows,'source_KEEP':True,'release_bytes':0,'published':0})
  return 1 if halt else 0
 except BaseException as e:
  save(run/'EXCEPTION.json',{'status':'FAILED_RETAINED','exception':type(e).__name__,'reason':str(e),'rows':rows,'source_KEEP':True,'release_bytes':0})
  raise
 finally:
  for p,t,log,started in active.values():stop(p,t);log.close()
  fcntl.flock(lease,fcntl.LOCK_UN);lease.close()
if __name__=='__main__':sys.exit(main())
