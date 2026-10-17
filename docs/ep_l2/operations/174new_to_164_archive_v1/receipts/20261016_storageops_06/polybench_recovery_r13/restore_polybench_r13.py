"""Selective, no-overwrite PolyBench recovery. Writes only into a new destination."""
import argparse,csv,gzip,hashlib,io,json,os,stat,tarfile,time
from pathlib import Path,PurePosixPath
RATE=30*1024**2
STAGES=['polybench.correlation.closeout.stage','polybench.covariance.closeout.stage']
FROZEN={'POLYBENCH_STAGE_HASHES.tsv':'bca6dfc2b43f4715ce0c6e55d4faa8ae11f3f4c7be7b96279e5671489004f274','POLYBENCH_STAGE_FILE_METADATA_V2.jsonl':'50c22e05d5550a5f3a8d80e45baf9b13e34beadfa01f5d6a333e914894753a80','POLYBENCH_STAGE_DIRECTORY_METADATA_V2.jsonl':'d0f8ea5d069e370a045f9834cb21799d8fffa341c62285a39b00bec33ddbb3e9','POLYBENCH_STAGE_RESTORE_MAP_R10_V1.json':'4d172393f335ca4f471b540ae0d61049d553abbffb90ddc25ba4c04110452652'}
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024**2),b''):h.update(chunk)
 return h.hexdigest()
def rel(value):
 p=PurePosixPath(value);require(not p.is_absolute() and '..' not in p.parts and p.parts and p.parts[0] in STAGES,'unsafe mapped destination');return Path(*p.parts)
def metadata(path,uid,gid,mode,mtime):
 require(not path.is_symlink(),'symlink metadata target');os.chown(path,int(uid),int(gid),follow_symlinks=False);os.chmod(path,int(mode,8),follow_symlinks=False);os.utime(path,ns=(int(mtime),int(mtime)),follow_symlinks=False)
class Reader:
 def __init__(self,f,limit):self.f=f;self.count=0;self.start=time.monotonic();self.limit=limit
 def read(self,n=-1):
  raw=self.f.read(min(4*1024**2,n) if n>=0 else 4*1024**2);self.count+=len(raw);require(not self.limit or self.count<=self.limit,'small recovery compressed-read bound exceeded');delay=self.count/RATE-(time.monotonic()-self.start)
  if delay>0:time.sleep(delay)
  return raw
def recover(bundle,archive,destination,stage='both',small=False,native=False,reserve=0):
 bundle=Path(bundle);m=json.loads((bundle/'POLYBENCH_RECOVERY_MAP_R13.json').read_bytes())
 for n,want in FROZEN.items():require(digest(bundle/n)==want,'frozen sidecar mismatch: '+n)
 old=json.loads((bundle/'POLYBENCH_STAGE_RESTORE_MAP_R10_V1.json').read_bytes());stripped=[{k:v for k,v in f.items() if k!='packaged_marker_relative_path'} for f in m['file_mapping']];require(stripped==old['file_mapping'] and m['directory_metadata']==old['directory_metadata'],'mapping changed from frozen evidence')
 rows=list(csv.DictReader(io.StringIO((bundle/'POLYBENCH_STAGE_HASHES.tsv').read_text()),delimiter='\t'));known={r['relative_path_under_decoupled_l2_extract']:r for r in rows};require(len(known)==len(m['file_mapping'])==13 and len(m['directory_metadata'])==14,'wrong production scope')
 for f in m['file_mapping']:
  r=known[str(rel(f['relative_path']))];require(int(r['logical_bytes'])==f['size_bytes'] and r['sha256']==f['sha256'],'frozen file content mapping mismatch')
 stages=STAGES if stage=='both' else [STAGES[0 if stage=='correlation' else 1]];files=[f for f in m['file_mapping'] if rel(f['relative_path']).parts[0] in stages]
 if small:files=[f for f in files if f['size_bytes']==0 or f.get('tar_member')=='polybench/11.0/polybench-correlation/NO_ARGS/traces/stats.csv']
 require(files and any(f['size_bytes'] for f in files),'empty content selection');dest=Path(destination);require(dest.is_absolute() and not os.path.lexists(dest) and dest.parent.is_dir() and dest.parent.resolve()==dest.parent,'destination must be new, absolute, and have an existing nonsymlink parent')
 for root in STAGES:require(not dest.is_relative_to(Path(m['original_extract_root'])/root),'refuse in-place scientific-source recovery')
 if native:require(hasattr(os,'geteuid') and os.geteuid()==0,'numeric native metadata requires root')
 available=os.statvfs(dest.parent);need=sum(f['size_bytes'] for f in files)+reserve+1024**2;require(available.f_bavail*available.f_frsize>=need,'insufficient recovery capacity/reserve');archive=Path(archive);require(archive.resolve()==archive and archive.is_file() and not archive.is_symlink() and archive.stat().st_size==m['primary_archive_bytes'],'wrong archive locator/size')
 before=archive.stat();dest.mkdir(mode=0o700);dirs=[d for d in m['directory_metadata'] if rel(d['relative_path_under_decoupled_l2_extract']).parts[0] in stages]
 for d in sorted(dirs,key=lambda d:len(rel(d['relative_path_under_decoupled_l2_extract']).parts)):(dest/rel(d['relative_path_under_decoupled_l2_extract'])).mkdir(mode=0o700,parents=True,exist_ok=True)
 expected={f['tar_member']:f for f in files if f['size_bytes']};seen={};written=0;write_start=time.monotonic()
 with archive.open('rb') as raw:
  reader=Reader(raw,8*1024**3 if small else 0)
  with gzip.GzipFile(fileobj=reader,mode='rb') as gz:
   with tarfile.open(fileobj=gz,mode='r|') as tar:
    for member in tar:
     name=member.name.removeprefix('./')
     if name not in expected:continue
     require(name not in seen and member.isfile(),'duplicate or nonregular selected member');f=expected[name];require(member.size==f['size_bytes'],'member size mismatch');target=dest/rel(f['relative_path']);h=hashlib.sha256();count=segment=0;fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
     with tar.extractfile(member) as content:
      while True:
       chunk=content.read(min(4*1024**2,512*1024**2-segment))
       if not chunk:break
       view=memoryview(chunk)
       while view:n=os.write(fd,view);view=view[n:]
       h.update(chunk);count+=len(chunk);segment+=len(chunk);written+=len(chunk);delay=written/RATE-(time.monotonic()-write_start)
       if delay>0:time.sleep(delay)
       if segment==512*1024**2:
        os.fsync(fd);os.close(fd);fd=os.open(target,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW);segment=0
     os.fsync(fd);os.close(fd);require(count==f['size_bytes'] and h.hexdigest()==f['sha256'] and digest(target)==f['sha256'],'restored file SHA256 mismatch');seen[name]=dict(size_bytes=count,sha256=h.hexdigest())
     if small and len(seen)==len(expected):break
   if not small:
    while gz.read(4*1024**2):pass
 require(set(seen)==set(expected),'missing selected tar member');markers=[]
 for f in files:
  if f['size_bytes']:continue
  marker=bundle/f['packaged_marker_relative_path'];require(marker.is_file() and marker.stat().st_size==0 and digest(marker)==f['sha256'],'missing packaged marker');target=dest/rel(f['relative_path']);fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd);require(digest(target)==f['sha256'],'restored marker mismatch');markers.append(f['relative_path'])
 if native:
  for f in files:metadata(dest/rel(f['relative_path']),f['original_uid'],f['original_gid'],f['original_mode_octal'],f['original_mtime_ns'])
  for d in sorted(dirs,key=lambda d:len(rel(d['relative_path_under_decoupled_l2_extract']).parts),reverse=True):metadata(dest/rel(d['relative_path_under_decoupled_l2_extract']),d['uid'],d['gid'],d['mode_octal'],d['mtime_ns'])
  for f in files:
   s=(dest/rel(f['relative_path'])).stat();require((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(f['original_uid'],f['original_gid'],int(f['original_mode_octal'],8),f['original_mtime_ns']),'native file attributes mismatch')
  for d in dirs:
   s=(dest/rel(d['relative_path_under_decoupled_l2_extract'])).stat();require((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(d['uid'],d['gid'],int(d['mode_octal'],8),d['mtime_ns']),'native directory attributes mismatch')
 after=archive.stat();require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'archive changed during recovery')
 return dict(status='RECOVERY_PASS',destination=str(dest),small_test=small,files_verified=len(files),nonempty_files_verified=len(seen),empty_markers_verified=len(markers),directories_created=len(dirs),restored_bytes=written,compressed_bytes_read=reader.count,native_numeric_file_and_directory_metadata_verified=native,ctime_restored=False,full_66gb_native_restore_performed=not small and stage=='both',source_files_modified_or_deleted=0,stage=stage)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',default=str(Path(__file__).resolve().parent));p.add_argument('--archive',required=True);p.add_argument('--destination',required=True);p.add_argument('--stage',choices=['correlation','covariance','both'],default='both');p.add_argument('--small-test',action='store_true');p.add_argument('--apply-native-metadata',action='store_true');p.add_argument('--min-free-after-bytes',type=int,default=0);a=p.parse_args();print(json.dumps(recover(a.bundle,a.archive,a.destination,a.stage,a.small_test,a.apply_native_metadata,a.min_free_after_bytes),indent=2))
if __name__=='__main__':main()
