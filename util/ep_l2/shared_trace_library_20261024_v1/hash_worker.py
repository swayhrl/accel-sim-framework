"""Read-only source hashes under existing sender lease; emits resumable metadata."""
import os,sys,json,time,hashlib,fcntl,stat
req=json.load(sys.stdin)
assert os.uname().nodename==req['hostname']
if req['host']=='174':
 lock=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock','rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:os.nice(19)
except OSError:pass
rate=30*1024**2;start=time.monotonic();total=0;last=start
def identity(s):return {'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink,'type':'file' if stat.S_ISREG(s.st_mode) else 'other'}
for row in req['files']:
 before=identity(os.stat(row['path']));assert before==row['identity'],('SOURCE_CHANGED',row['path'])
 fd=os.open(row['path'],os.O_RDONLY|getattr(os,'O_NOATIME',0));h=hashlib.sha256();count=0
 with os.fdopen(fd,'rb') as f:
  while True:
   b=f.read(1024**2)
   if not b:break
   h.update(b);count+=len(b);total+=len(b)
   time.sleep(max(0,total/rate-(time.monotonic()-start)))
   if time.monotonic()-last>=10:
    print(json.dumps({'event':'HASH_PROGRESS','key':row['key'],'file_bytes':count,'session_bytes':total,'elapsed':time.monotonic()-start}),flush=True);last=time.monotonic()
  assert identity(os.fstat(f.fileno()))==before
 assert identity(os.stat(row['path']))==before and count==before['size']
 print(json.dumps({'event':'FILE_SHA','key':row['key'],'path':row['path'],'sha256':h.hexdigest(),'identity':before,'bytes':count,'source_before_after_unchanged':True}),flush=True)
print(json.dumps({'event':'HASH_DONE','session_bytes':total,'elapsed':time.monotonic()-start,'source_writes':0}),flush=True)
