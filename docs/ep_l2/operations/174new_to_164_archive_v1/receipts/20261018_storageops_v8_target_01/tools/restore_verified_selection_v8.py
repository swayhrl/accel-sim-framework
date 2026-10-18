"""Dry-run by default. Recover exact SHA-pinned files into one new target path."""
import argparse,hashlib,json,os,stat,time,fcntl
from pathlib import Path,PurePosixPath
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02')
V8=A/'increments/20261018_fast_v8';B=Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
LIMIT=512*1024**2;RATE=30*1024**2
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def rel(s):
 p=PurePosixPath(s);need(s and not p.is_absolute() and all(x not in ['', '.', '..'] for x in s.split('/')) and '\\' not in s,'unsafe relative path');return Path(*p.parts)
def digest(p):
 h=hashlib.sha256();t=time.monotonic();n=0
 with p.open('rb') as f:
  for data in iter(lambda:f.read(4*1024**2),b''):
   h.update(data);n+=len(data);delay=n/RATE-(time.monotonic()-t)
   if delay>0:time.sleep(delay)
 return h.hexdigest()
def attr(p,row):
 os.chown(p,row['uid'],row['gid'],follow_symlinks=False);os.chmod(p,row['mode'],follow_symlinks=False);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']),follow_symlinks=False)
def run(plan_path,expected,destination,execute=False,native=False):
 raw=Path(plan_path).read_bytes();need(hashlib.sha256(raw).hexdigest()==expected,'plan SHA mismatch');p=json.loads(raw);files=p['files'];dirs=p.get('directories',[]);need(files and sum(max(f['size_bytes'],f.get('allocated_bytes',f['size_bytes'])) for f in files)<=LIMIT,'selection exceeds512MiB')
 dest=Path(destination);need(dest.is_absolute() and not os.path.lexists(dest) and dest.parent.resolve()==dest.parent and dest.parent.is_dir(),'new absent destination with existing nonsymlink parent required');need(dest.is_relative_to(V8/'recovery_drills') or dest.is_relative_to(B/'v8_native_recovery'),'destination outside authorized recovery area')
 for f in files:
  rel(f['relative_path']);src=Path(f['archive_path']);need(src.is_relative_to(A) and src.resolve()==src and src.is_file() and not src.is_symlink(),'unsafe source archive path');need(src.stat().st_size==f['size_bytes'],'source archive size changed')
 for d in dirs:
  if d['relative_path']:rel(d['relative_path'])
 result=dict(status='DRY_RUN_PASS',plan_sha256=expected,files=len(files),bytes=sum(f['size_bytes'] for f in files),directories=len(dirs),destination=str(dest),writes=0,native_numeric_metadata_verified=False,source_original_modified=0)
 if not execute:return result
 if native:need(os.geteuid()==0 and dest.parent.stat().st_dev==2431,'native numeric proof requires root and verified native shared device')
 free=os.statvfs(B);need(free.f_bavail*free.f_frsize>=40*1024**3+(result['bytes']+1024**2 if dest.is_relative_to(B) else 0),'Share floor or recovery capacity')
 lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW)
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);dest.mkdir(mode=0o700)
  for d in sorted(dirs,key=lambda x:len(Path(x['relative_path']).parts)):
   if d['relative_path']:(dest/rel(d['relative_path'])).mkdir(parents=True,exist_ok=True,mode=0o700)
  for f in files:
   src=Path(f['archive_path']);before=src.stat();need(digest(src)==f['sha256'],'archive SHA changed');q=dest/rel(f['relative_path']);q.parent.mkdir(parents=True,exist_ok=True);fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);t=time.monotonic();n=0
   with src.open('rb') as inp,os.fdopen(fd,'wb') as out:
    for data in iter(lambda:inp.read(4*1024**2),b''):
     out.write(data);n+=len(data);delay=n/RATE-(time.monotonic()-t)
     if delay>0:time.sleep(delay)
    out.flush();os.fsync(out.fileno())
   need(digest(q)==f['sha256'],'closed reopened restore SHA mismatch');after=src.stat();need((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'archive changed during recovery')
   if native:
    attr(q,f);s=q.stat();need((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(f['uid'],f['gid'],f['mode'],f['mtime_ns']),'native file attributes mismatch')
  if native:
   for d in sorted(dirs,key=lambda x:len(Path(x['relative_path']).parts),reverse=True):attr(dest/rel(d['relative_path']) if d['relative_path'] else dest,d)
   for d in dirs:
    s=(dest/rel(d['relative_path']) if d['relative_path'] else dest).stat();need((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(d['uid'],d['gid'],d['mode'],d['mtime_ns']),'native directory attributes mismatch')
  result.update(status='RESTORE_PASS',writes=result['bytes'],native_numeric_metadata_verified=native,ctime_restored=False);return result
 finally:os.close(lock)
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--plan',required=True);a.add_argument('--expected-plan-sha256',required=True);a.add_argument('--destination',required=True);a.add_argument('--execute',action='store_true');a.add_argument('--native-metadata',action='store_true');v=a.parse_args();print(json.dumps(run(v.plan,v.expected_plan_sha256,v.destination,v.execute,v.native_metadata),indent=2))
if __name__=='__main__':main()
