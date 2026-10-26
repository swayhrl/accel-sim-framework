"""Shared real two-stage gate. CPU fixture uses private dirs; no GPU or scheduling."""
import pathlib,os,time,json,fcntl,hashlib
def ident():
 t=pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()
 return {'pid':os.getpid(),'start_ticks':t[19],'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':t[0]}
def save(p,x):
 with p.open('x') as f:json.dump(x,f);f.flush();os.fsync(f.fileno())
def acquire_and_wait(run,control,token,deadline):
 lease=(control/'RTX4080_DISPATCHER.lock').open('r+');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
 me=ident();st=os.fstat(lease.fileno());ready=dict(me,token=token,dispatcher_lease_owned=True,lease_dev=st.st_dev,lease_inode=st.st_ino)
 save(run/'RESUME_READY_WAIT_STOP_RETIRE.json',ready)
 until=time.monotonic()+min(60,max(0,deadline-time.time()-120));gate=run/'RESUME_RUN_GATE.json'
 while not gate.exists():
  assert time.monotonic()<until,'RUN_GATE absent; cannot schedule'
  time.sleep(.05)
 g=json.loads(gate.read_text());assert all(g[k]==me[k] for k in ('pid','start_ticks','boot_id')) and g['token']==token and g['deadline_unix']==deadline,'RUN_GATE identity'
 assert not (control/'STOP_AFTER_CURRENT').exists(),'STOP not retired'
 return me,lease
def lease_owned_by(pid,path):
 st=path.stat();target=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}'
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  p=line.split()
  if len(p)>5 and p[1:4]==['FLOCK','ADVISORY','WRITE'] and p[4]==str(pid) and p[5].lower()==target.lower():return True
 return False
