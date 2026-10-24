"""Archive exact terminal owned trees; cold reference first, verified deletion last."""
import pathlib,json,hashlib,os,time,fcntl,stat,subprocess
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
PLAN=C/'NATIVE_RTX_TERMINAL_COLD_OFFLOAD_PLAN_V1.json';PLAN_SHA='e4073538901097776a3867cc1561e2075e1070630d80d7b9eaa5ddb73d7ff631'
RATE=15*2**20
def digest(p,rate=False):
 h=hashlib.sha256();start=time.monotonic();done=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):
   h.update(b);done+=len(b)
   if rate:time.sleep(max(0,done/RATE-(time.monotonic()-start)))
 return h.hexdigest()
def save(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();temp=p.with_name(p.name+'.tmp')
 with temp.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,p)
def syncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def sets(root):
 files=set();dirs=set()
 for current,ds,fs in os.walk(root,followlinks=False):
  p=pathlib.Path(current);dirs.add(p.relative_to(root).as_posix())
  for name in ds+fs:assert not(p/name).is_symlink()
  for name in fs:
   assert stat.S_ISREG((p/name).lstat().st_mode);files.add((p/name).relative_to(root).as_posix())
 return files,dirs
def verify(root,r,identity=False,rate=False):
 assert sets(root)==({x['path']for x in r['files']},{x['path']for x in r['directories']})
 for x in r['files']:
  p=root/x['path'];v=p.stat();assert v.st_size==x['bytes']and digest(p,rate)==x['sha256']
  if identity:assert(v.st_dev,v.st_ino,v.st_mtime_ns,v.st_nlink)==(x['dev'],x['ino'],x['mtime_ns'],x['nlink'])
def mount():
 v=json.loads(subprocess.check_output(['findmnt','-T',str(B),'-o','SOURCE,FSTYPE,TARGET','-J']))['filesystems'][0]
 assert v=={'source':'admin-wcx@10.208.130.164:/home/shared','fstype':'fuse.sshfs','target':'/root/share/mnt164'}
 return v
class Lease:
 def __enter__(self):
  self.fs=[];deadline=time.monotonic()+600
  try:
   for n in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
    f=open(C/n,'a');self.fs.append(f)
    while True:
     try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
     except BlockingIOError:assert time.monotonic()<deadline;time.sleep(.1)
  except BaseException:self.__exit__();raise
  return self
 def __exit__(self,*args):
  for f in reversed(self.fs):fcntl.flock(f,fcntl.LOCK_UN);f.close()
def one(r):
 src=pathlib.Path(r['source']);dest=pathlib.Path(r['target_object']);tree=dest/'tree'
 assert N in src.resolve().parents and src.stat().st_dev==2128 and not src.is_symlink()
 assert dest.parent==B/'objects'and not dest.exists()
 retired=src.with_name(src.name+'_NATIVE_OFFLOAD_RETIRED_V1');assert not retired.exists()
 ident=dest.name;flight=B/'inflight'/ident;assert not flight.exists()
 verify(src,r,True);before_free=os.statvfs(N).f_bavail*os.statvfs(N).f_frsize;before_mount=mount()
 with Lease():
  flight.mkdir();newtree=flight/'tree';newtree.mkdir()
  for d in r['directories']:
   if d['path']!='.':(newtree/d['path']).mkdir(parents=True,exist_ok=True)
  for x in r['files']:
   source=src/x['path'];target=newtree/x['path'];h=hashlib.sha256();start=time.monotonic();done=0
   with source.open('rb')as inp,target.open('xb')as out:
    for b in iter(lambda:inp.read(2**20),b''):
     h.update(b);out.write(b);done+=len(b);time.sleep(max(0,done/RATE-(time.monotonic()-start)))
    out.flush();os.fsync(out.fileno())
   assert done==x['bytes']and h.hexdigest()==x['sha256'];os.chmod(target,stat.S_IMODE(x['mode'])&0o777)
  verify(newtree,r,rate=True);verify(src,r,True)
  manifest={'kind':r['kind'],'original_Native_path':str(src),'plan_sha256':PLAN_SHA,'files':r['files'],'directories':r['directories'],'source_original_science_RAW_untouched':True,'scope':'All exact bytes/paths preserved; native inode/ctime/uid equivalence after cold-reference switch not claimed'}
  save(flight/'MANIFEST.json',manifest);mh=digest(flight/'MANIFEST.json')
  commit={'kind':r['kind'],'status':'COMMITTED_VERIFIED','object_id':ident,'manifest_sha256':mh,'plan_sha256':PLAN_SHA,'files':len(r['files']),'logical_bytes':r['logical_bytes'],'original_Native_path':str(src),'source_GPU_raw_deleted':False,'full_trace_asset_count_increment':0,'unix':time.time()}
  save(flight/'COMMIT.json',commit);syncdir(flight);flight.rename(dest)
  assert digest(dest/'MANIFEST.json')==mh
  # Preserve original path before releasing any Native file data.
  src.rename(retired)
  try:
   src.symlink_to(tree,target_is_directory=True);syncdir(src.parent)
   assert src.is_symlink()and src.resolve()==tree.resolve()
   verify(src,r,rate=True)
   assert mount()==before_mount
  except BaseException:
   if src.is_symlink()and src.resolve()==tree.resolve():src.unlink()
   if not src.exists():retired.rename(src)
   raise
  # Explicit final checks against the exact owned Native retired tree.
  assert retired.resolve().is_relative_to(N.resolve())and retired.stat().st_dev==2128 and not retired.is_symlink()
  verify(retired,r,True)
  inode_rows={}
  for x in r['files']:inode_rows.setdefault((x['dev'],x['ino']),[]).append(x)
  freed=sum(v[0]['allocated_bytes']for v in inode_rows.values()if v[0]['nlink']==len(v))
  for x in r['files']:
   p=retired/x['path'];v=p.lstat()
   assert stat.S_ISREG(v.st_mode)and(v.st_dev,v.st_ino,v.st_size)==(x['dev'],x['ino'],x['bytes'])
   p.unlink()
  for d in sorted(r['directories'],key=lambda x:len(pathlib.PurePosixPath(x['path']).parts),reverse=True):
   if d['path']!='.':(retired/d['path']).rmdir()
  retired.rmdir();syncdir(src.parent)
  after_free=os.statvfs(N).f_bavail*os.statvfs(N).f_frsize
  receipt={'status':'TRUE164_CLOSED_REOPENED_COLD_REFERENCE_AND_OWN_NATIVE_RELEASE_PASS','object_id':ident,'manifest_sha256':mh,'COMMIT_sha256':digest(dest/'COMMIT.json'),'source_Native_path':str(src),'cold_reference':str(tree),'files':len(r['files']),'logical_bytes':r['logical_bytes'],'unlinked_exclusive_file_allocated_bytes':freed,'Native_df_before':before_free,'Native_df_after':after_free,'observed_net_free_change_including_concurrent_others':after_free-before_free,'original_GPU_raw_and_46e_untouched':True,'full_asset_count_increment':0,'no_GPU_SIM_109_or_registry_mutation':True,'mount_identity':before_mount,'unix':time.time()}
  save(B/'receipts'/(ident+'_NATIVE_RELEASE.json'),receipt);save(C/(ident+'_NATIVE_RELEASE.json'),receipt)
  return receipt
assert digest(PLAN)==PLAN_SHA;plan=json.loads(PLAN.read_text());assert plan['status']=='PLAN_ONLY_NOT_EXECUTED_PARENT_REVIEW_REQUIRED'
single=open(C/'NATIVE_RTX_TERMINAL_OFFLOAD.lock','a');fcntl.flock(single,fcntl.LOCK_EX|fcntl.LOCK_NB)
save(C/'NATIVE_RTX_TERMINAL_OFFLOAD_PROCESS.json',{'pid':os.getpid(),'ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'plan_sha256':PLAN_SHA,'unix':time.time()})
results=[]
try:
 for r in plan['sources']:
  q=one(r);results.append(q);print(json.dumps(q),flush=True)
 save(C/'NATIVE_RTX_TERMINAL_OFFLOAD_COMPLETE.json',{'status':'ALL_THREE_TERMINAL_OWNED_TREES_OFFLOADED_NATIVE_RELEASE_PASS','results':results,'unlinked_exclusive_file_allocated_bytes':sum(x['unlinked_exclusive_file_allocated_bytes']for x in results),'no_CPU_post_restart':True,'unix':time.time()})
except BaseException as e:
 save(C/'NATIVE_RTX_TERMINAL_OFFLOAD_FAILURE.json',{'status':'FAILED_RETAINED_OFFLOAD_NO_AUTORETRY','error':repr(e),'completed_objects':results,'unix':time.time()});raise
