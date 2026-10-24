"""Read-only source hashes under existing sender lease; emits resumable metadata."""
import os,sys,json,time,hashlib,fcntl,stat,subprocess
req=json.load(sys.stdin)
assert os.uname().nodename==req['hostname']
if req['host']=='174':
 lock=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock','rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:os.nice(19)
except OSError:pass
rate=30*1024**2;start=time.monotonic();total=0;last=start;rate_checked=0;current_rate=rate
if os.path.isfile('/usr/bin/ionice'):subprocess.run(['/usr/bin/ionice','-c','3','-p',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def adaptive_rate():
 global rate_checked,current_rate
 now=time.monotonic()
 if now-rate_checked>=5:
  try:
   line=next(x for x in open('/proc/pressure/io') if x.startswith('full '));full=float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
  except (OSError,StopIteration,ValueError):full=100
  current_rate=min(rate,(30 if full<5 else 10 if full<10 else 4 if full<20 else 1)*1024**2);rate_checked=now
 return current_rate
def identity(s):return {'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink,'type':'file' if stat.S_ISREG(s.st_mode) else 'other'}
for row in req['files']:
 before=identity(os.stat(row['path']));assert before==row['identity'],('SOURCE_CHANGED',row['path'])
 fd=os.open(row['path'],os.O_RDONLY|getattr(os,'O_NOATIME',0));h=hashlib.sha256();count=0
 with os.fdopen(fd,'rb') as f:
  while True:
   tick=time.monotonic();b=f.read(1024**2)
   if not b:break
   h.update(b);count+=len(b);total+=len(b)
   time.sleep(max(0,len(b)/adaptive_rate()-(time.monotonic()-tick)))
   if time.monotonic()-last>=10:
    print(json.dumps({'event':'HASH_PROGRESS','key':row['key'],'file_bytes':count,'session_bytes':total,'elapsed':time.monotonic()-start,'adaptive_rate_bytes_sec':current_rate,'io_policy':'USER_AUTHORIZED_PROGRESS_WITH_ADAPTIVE_THROTTLE'}),flush=True);last=time.monotonic()
  assert identity(os.fstat(f.fileno()))==before
 assert identity(os.stat(row['path']))==before and count==before['size']
 print(json.dumps({'event':'FILE_SHA','key':row['key'],'path':row['path'],'sha256':h.hexdigest(),'identity':before,'bytes':count,'source_before_after_unchanged':True}),flush=True)
print(json.dumps({'event':'HASH_DONE','session_bytes':total,'elapsed':time.monotonic()-start,'source_writes':0}),flush=True)
