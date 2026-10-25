#!/usr/bin/env python3
"""Explicit exact restoration; never overwrites an existing local file."""
import os,json,hashlib,pathlib,sys,time,fcntl
P=pathlib.Path
sys.path.insert(0,'/root/data/research_asset_verified_offload_20261024_v1/tools')
import server_resources as resources
lease=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock','rb')
fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
M=json.loads((P(__file__).parent/'QUALIFIED.json').read_bytes())
for x in M['files']:
 p=P(x['source']); a=P(x['archive']['path']); expected=x['sha256']
 assert p.is_relative_to('/root') and '/src/gpgpu-sim/build/' in str(p) and p.suffix in ('.o','.a')
 if p.exists():
  assert p.is_file() and not p.is_symlink()
  with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected,'existing file differs: '+str(p)
  continue
 assert p.parent.is_dir() and p.parent.resolve()==p.parent,'restore parents changed'
 gate=resources.admission('TARGET',allowed_lock_pids=(os.getpid(),))
 s=os.statvfs('/root/data');assert s.f_bavail*s.f_frsize>=gate['SSD_required_bytes']+x['identity']['size'],'restore requires original admission plus complete-file temporary capacity'
 tmp=p.with_name(p.name+'.T2_exact_restore.writing');h=hashlib.sha256()
 with a.open('rb') as src,tmp.open('xb') as out:
  while True:
   t=time.monotonic();b=src.read(1024**2)
   if not b:break
   h.update(b);out.write(b);time.sleep(max(0,len(b)/(15*1024**2)-(time.monotonic()-t)))
  out.flush();os.fsync(out.fileno())
 assert h.hexdigest()==expected and tmp.stat().st_size==x['identity']['size']
 with tmp.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
 i=x['identity'];os.chown(tmp,i['uid'],i['gid']);os.chmod(tmp,i['mode']&0o7777)
 os.utime(tmp,ns=(i['mtime_ns'],i['mtime_ns']))
 os.link(tmp,p);tmp.unlink()
print('Exact compiler copies restored; ctime is historical provenance only.')
