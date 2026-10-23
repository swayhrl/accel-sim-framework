"""Finite V9-style COPY_ONLY bundle adapter; no scientific launcher/delete API.

Owner inputs are normalized and pinned by the Windows trusted coordinator.
Existing9 sidecars are immutable164 references, not uploaded again. A raw PAX
tar carries other members, split into <=128MiB records in the original single
receiver window. No Source archive or Share payload is ever written.
"""
import base64,datetime,fcntl,hashlib,io,json,os,posixpath,stat,struct,subprocess,sys,tarfile,time,zlib
from pathlib import Path,PurePosixPath
sys.dont_write_bytecode=True
MIB=1024**2;GIB=1024**3;CHUNK=128*MIB;RATE=30*MIB
BRIDGE=Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
NATIVE=Path('/root/data/full_result_offload_20261023_v1')
NAS=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_full_result_offload_v1')
ROOTS={'EP_L2_E057':'/workspace/ep_l2_ms20261019_e_results/E057_b4a7e175','DTC_L1_AD_GEMM':'/workspace/dtc-ag8r1-finite-resume-174-v1/attempts/AD_GEMM_940981e5-61c4-4772-83a3-50593fd1ba3a'}
PILOT=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_result_offload_real_sidecars_v1')
PILOT_REUSE={'EP_L2_E057':('96202aab2446a3f6440108c045f524f9797a500c61446eeb7a52598c6ef37845','7c429e019de4f1f1699abc61ca544542a3552ed8567923be15f02d1cb5936505','E057_b4a7e175',{'NATIVE_EXIT.json','config-0.config','config-1.config','config-2.config','config-3.config'}),'DTC_L1_AD_GEMM':('24b5cab04e21b55c269d15fce39746c03c4730159b24a2f5fd657ae687964a9c','db87833e52fd98c738a68e85591da3c70e2cb506f2c6fd7ffd495fe4bd27077d','',{'RUN_START.json','RUN_TERMINAL.json','ACTUAL_PRODUCER_BINDING.json','STRICT.json'})}
V9SHA='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
def require(ok,why):
 if not ok:raise RuntimeError(why)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(s):return dict(dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,allocated=s.st_blocks*512,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def safe(root,rel):
 p=PurePosixPath(rel);require(not p.is_absolute() and '..' not in p.parts and '\\' not in rel and '\0' not in rel,'unsafe relative path')
 require(rel=='.' or str(p)==rel,'noncanonical path')
 out=Path(root)/rel
 for parent in out.parents:
  require(not parent.is_symlink(),'symlink ancestor '+str(parent))
 return out
def file_sha(p):
 require(not p.is_symlink(),'hash symlink refused');h=hashlib.sha256()
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0)),'rb') as f:
  s=ident(os.fstat(f.fileno()))
  for b in iter(lambda:f.read(MIB),b''):h.update(b)
  require(ident(os.fstat(f.fileno()))==s==ident(p.lstat()),'file changed while hashing')
 return h.hexdigest()
def validate(m):
 slug=m['project'];require(slug in ROOTS and m['source_root']==ROOTS[slug],'source scope')
 require(m['source_disposition']=='SOURCE_KEEP' and m['full_owner_ready_verified'] is True,'independent owner READY missing')
 require(m['genuine164_destination_root']==str(NAS/slug).replace('/root/share/mnt164','/home/shared',1),'NAS scope')
 require(len(m['entries'])<=200000,'bounded selector')
 seen=set();dirs=set()
 for r in m['entries']:
  p=r['path'];safe('/scope',p);require(p not in seen,'duplicate selector');seen.add(p)
  require(r['type'] in ['file','directory','symlink'],'unsupported member')
  if r['type']=='directory':dirs.add(p)
  if r['type']=='file':
   require(r['size']>=0 and len(r['sha256'])==64,'file digest missing')
   require(r['nlink']==1 or m['hardlink_policy']=='COPY_BYTES_EXTERNAL_ALIAS_PROVENANCE','unapproved hardlink semantics')
  if r['type']=='symlink':
   t=r['target'];resolved=posixpath.normpath(posixpath.join(posixpath.dirname(p),t))
   require(not t.startswith('/') and resolved!='..' and not resolved.startswith('../') and '\0' not in t,'escaping symbolic reference')
 require('.' in dirs,'root directory record')
 for r in m['entries']:
  if r['path']!='.':require(str(PurePosixPath(r['path']).parent) in dirs,'missing parent directory')
  if r['type']=='symlink':require(posixpath.normpath(posixpath.join(posixpath.dirname(r['path']),r['target'])) in seen,'unclosed symbolic reference')
 oldtx,oldsha,prefix,names=PILOT_REUSE[slug];require(set(m['reused_objects'])==names,'all9 existing sidecars must be reused')
 for name,ref in m['reused_objects'].items():require(ref['path_on_target']==str(PILOT/slug/oldtx/'tree'/prefix/name) and ref['pilot_receipt_sha256']==oldsha,'unqualified existing164 reference')
 selector=digest(canon(m['entries']));require(selector==m['selector_sha256'],'selector changed')
 txkeys={k:m[k] for k in ['source_filesystem_identity','source_root','selector_sha256','source_frozen_commit','genuine164_destination_root']}
 require(digest(canon(txkeys))==m['txid'],'transaction identity changed')
 return slug
def source_check(m,check_writers=True):
 fs=m['source_filesystem_identity'];require(os.uname().nodename==fs['host'] and os.readlink('/proc/self/ns/mnt')==fs['mount_namespace'] and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==fs['boot_id'],'Source host identity')
 actual={};stack=[Path(m['source_root'])]
 while stack:
  p=stack.pop();s=p.lstat();rel=p.relative_to(m['source_root']).as_posix();actual[rel]=ident(s)
  require(len(actual)<=200000,'bounded inventory')
  if stat.S_ISDIR(s.st_mode):stack.extend(p.iterdir())
 require(set(actual)=={r['path'] for r in m['entries']},'Source full tree member drift')
 for r in m['entries']:
  require(actual[r['path']]=={k:r[k] for k in actual[r['path']]},'Source stat drift '+r['path'])
  p=safe(m['source_root'],r['path'])
  if r['type']=='symlink':require(p.is_symlink() and os.readlink(p)==r['target'],'Source link drift')
  elif r['type']=='file':require(stat.S_ISREG(p.lstat().st_mode),'Source regular-file type drift')
  else:require(stat.S_ISDIR(p.lstat().st_mode),'Source directory type drift')
 selected={(r['dev'],r['inode']) for r in m['entries']};writers=[]
 if check_writers:
  for proc in Path('/proc').iterdir():
   if not proc.name.isdigit():continue
   try:fds=list((proc/'fd').iterdir())
   except FileNotFoundError:continue
   for fd in fds:
    try:
     s=fd.stat()
     if (s.st_dev,s.st_ino) not in selected:continue
     flags=int(next(l.split()[1] for l in (proc/'fdinfo'/fd.name).read_text().splitlines() if l.startswith('flags:')),8)
     if (flags&os.O_ACCMODE) in (os.O_WRONLY,os.O_RDWR):writers.append({'pid':int(proc.name),'fd':fd.name})
    except FileNotFoundError:continue
 require(not writers,'Source selected writer active')
 return {'utc':utc(),'full_member_count':len(actual),'active_selected_writers':writers,'source_disposition':'SOURCE_KEEP'}
def source_resources():
 require(os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]','Source resource identity mismatch')
 p=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');v=json.loads(p.read_bytes());leases={k:x for k,x in v['resource_leases'].items() if x.get('status')!='RELEASED'}
 require(all('disk_growth_bytes' in x or 'result_growth_bytes' in x for x in leases.values()),'active lease lacks exact disk reservation')
 reserved=sum(max(x.get('disk_growth_bytes',0),x.get('result_growth_bytes',0)) for x in leases.values())
 policy=v['mechanism_study_20261019_v1']['workspace_disk_policy'];c=v['mechanism_study_20261019_v1']
 require(policy['disk_floor_bytes']==5*GIB and policy['monitor_reserve_bytes']==2*GIB,'science disk policy changed; readmission required')
 live=[]
 for name in ['AG_execution.lock','AG_execution_io_warning.lock']:
  p=Path('/workspace/dtc-ag8r1-finite-resume-174-v1')/name
  if p.exists():
   d=json.loads(p.read_bytes());proc=Path('/proc')/str(d['pid'])
   if proc.exists():
    try:
     ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
     if ticks==d['start_ticks']:live.append(d)
    except FileNotFoundError:pass
 # Unclosed DTC controller resources are not inferred from a stale lock file.
 require(not live,'DTC live resource reservation requires explicit current remaining-write join')
 mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;mx=Path('/sys/fs/cgroup/memory.max').read_text().strip();cur=int(Path('/sys/fs/cgroup/memory.current').read_text());require(mem>=64*GIB and (mx=='max' or int(mx)-cur>=512*MIB),'Source RAM/cgroup floor')
 return {'utc':utc(),'registry_sha256':digest(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_bytes()),'active_leases':leases,'outstanding_write_reservation_bytes':reserved,'DTC_live_owner_locks':live,'science_actual_starts':c['actual_starts'],'science_t0_unix':c['t0_unix'],'science_controller':c.get('controller'),'disk_floor':5*GIB,'monitor_reserve':2*GIB,'MemAvailable':mem,'cgroup_memory_current':cur,'cgroup_memory_max':mx,'IO_pressure':Path('/proc/pressure/io').read_text()}
class FrameWriter:
 def __init__(self,skip):self.buf=bytearray();self.skip=skip;self.pos=0;self.h=hashlib.sha256();self.sent=0;self.started=time.monotonic();self.next_send=time.monotonic()
 def write(self,b):
  self.h.update(b);n=len(b);self.pos+=n
  if self.skip:
   k=min(self.skip,n);b=b[k:];self.skip-=k
  self.buf.extend(b)
  while len(self.buf)>=CHUNK:self.emit(CHUNK)
  return n
 def emit(self,n):
  b=bytes(self.buf[:n]);del self.buf[:n];self.sent+=n
  sys.stdout.buffer.write(struct.pack('!Q',n)+hashlib.sha256(b).digest());sys.stdout.buffer.flush()
  for start in range(0,n,MIB):
   part=memoryview(b)[start:start+MIB];self.next_send=max(time.monotonic(),self.next_send)+len(part)/RATE;delay=self.next_send-time.monotonic()
   if delay>0:time.sleep(delay)
   sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
 def finish(self,proof):
  require(self.skip==0,'resume offset beyond deterministic archive')
  if self.buf:self.emit(len(self.buf))
  proof.update(archive_bytes=self.pos,archive_sha256=self.h.hexdigest(),new_stream_bytes=self.sent)
  b=canon(proof);sys.stdout.buffer.write(struct.pack('!Q',0)+struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.count=0
 def read(self,n):
  b=self.f.read(n);self.h.update(b);self.count+=len(b);return b
def export(m,skip):
 os.nice(19)
 validate(m);lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 before=source_check(m);res=source_resources();w=FrameWriter(skip);checked=[]
 with tarfile.open(mode='w|',fileobj=w,format=tarfile.PAX_FORMAT) as tar:
  for r in m['entries']:
   if r['path'] in m['reused_objects']:continue
   p=safe(m['source_root'],r['path']);info=tarfile.TarInfo(r['path']);info.uid=r['uid'];info.gid=r['gid'];info.mode=r['mode'];info.mtime=r['mtime_ns']//10**9;info.uname='';info.gname='';info.pax_headers={'mtime':str(r['mtime_ns']//10**9)+'.'+str(r['mtime_ns']%10**9).zfill(9)}
   if r['type']=='directory':info.type=tarfile.DIRTYPE;tar.addfile(info)
   elif r['type']=='symlink':info.type=tarfile.SYMTYPE;info.linkname=r['target'];tar.addfile(info)
   else:
    info.size=r['size'];fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
    with os.fdopen(fd,'rb',buffering=0) as f:
     old=ident(os.fstat(f.fileno()));require(old=={k:r[k] for k in old},'Source pre-read drift')
     h=HashReader(f);tar.addfile(info,h);require(h.count==r['size'] and h.h.hexdigest()==r['sha256'],'Source original full SHA mismatch '+r['path'])
     require(ident(os.fstat(f.fileno()))==old==ident(p.lstat()),'Source changed during archive')
     checked.append({'path':r['path'],'sha256':h.h.hexdigest(),'size':h.count})
 for r in m['entries']:
  if r['path'] in m['reused_objects']:require(file_sha(safe(m['source_root'],r['path']))==r['sha256'],'Source reused file SHA drift')
 after=source_check(m);w.finish({'status':'SOURCE_READONLY_FULL_CONTENT_VERIFIED','txid':m['txid'],'before':before,'after':after,'resources':res,'whole_file_checks':checked,'reused_source_paths':list(m['reused_objects']),'source_disposition':'SOURCE_KEEP','source_released_bytes':0});lock.close()
def read_exact(f,n):
 b=bytearray()
 while len(b)<n:
  v=f.read(n-len(b));require(v,'unexpected stream EOF');b.extend(v)
 return bytes(b)
class PartsReader(io.RawIOBase):
 def __init__(self,paths):self.paths=iter(paths);self.f=None
 def readable(self):return True
 def read(self,n=-1):
  require(n>=0,'unbounded archive read refused');out=bytearray()
  while len(out)<n:
   if self.f is None:
    try:self.f=next(self.paths).open('rb')
    except StopIteration:break
   b=self.f.read(n-len(out))
   if b:out.extend(b)
   else:self.f.close();self.f=None
  return bytes(out)
def native_meta(p,r):
 os.chown(p,r['uid'],r['gid'],follow_symlinks=False)
 if r['type']!='symlink':os.chmod(p,r['mode'])
 os.utime(p,ns=(r['mtime_ns'],r['mtime_ns']),follow_symlinks=False)
def check_native(root,m,hash_bytes=True):
 rows=[];actual=set();stack=[root]
 while stack:
  p=stack.pop();r=p.relative_to(root).as_posix();actual.add(r)
  if p.is_dir() and not p.is_symlink():stack.extend(p.iterdir())
 require(actual=={r['path'] for r in m['entries']},'native restore inventory mismatch')
 for r in m['entries']:
  p=safe(root,r['path']);s=p.lstat();a=ident(s)
  for k in ['uid','gid','mode','mtime_ns']:require(a[k]==r[k],'native '+k+' mismatch '+r['path'])
  if r['type']=='file':
   require(stat.S_ISREG(s.st_mode) and s.st_size==r['size'],'native file type/size')
   if hash_bytes:require(file_sha(p)==r['sha256'],'native full SHA mismatch '+r['path'])
  elif r['type']=='directory':require(stat.S_ISDIR(s.st_mode),'native directory type')
  else:require(stat.S_ISLNK(s.st_mode) and os.readlink(p)==r['target'],'native link semantics')
  rows.append({'path':r['path'],'type':r['type'],'sha256':r.get('sha256'),'identity':a,'target':r.get('target')})
 return rows
def restore(bundle,m,dst,v,gate=None):
 require(subprocess.check_output(['findmnt','-n','-T',str(dst.parent),'-o','FSTYPE'],text=True).strip()=='ext4','restore requires qualified native ext4')
 require(not os.path.lexists(dst),'ABSENT native destination required')
 dst.mkdir(mode=0o700);entries={r['path']:r for r in m['entries']};seen=set()
 for r in sorted(m['entries'],key=lambda r:len(PurePosixPath(r['path']).parts)):
  if r['type']=='directory':safe(dst,r['path']).mkdir(mode=0o700,exist_ok=True)
 parts=[bundle/'chunks'/c['name'] for c in json.loads((bundle/'ARCHIVE_INDEX.json').read_bytes())['chunks']]
 last_gate=time.monotonic()
 with tarfile.open(fileobj=PartsReader(parts),mode='r|') as tar:
  for member in tar:
   if gate is not None and time.monotonic()-last_gate>=10:gate();last_gate=time.monotonic()
   name=member.name.rstrip('/') or '.';require(name in entries and name not in seen and name not in m['reused_objects'],'unexpected/duplicate tar member');seen.add(name);r=entries[name];p=safe(dst,name)
   require((member.uid,member.gid,member.mode)==(r['uid'],r['gid'],r['mode']),'archive numeric metadata mismatch')
   sec,_,frac=member.pax_headers.get('mtime',str(member.mtime)).partition('.');require(int(sec)*10**9+int((frac+'0'*9)[:9])==r['mtime_ns'],'archive timestamp mismatch')
   if r['type']=='directory':require(member.isdir(),'archive directory type')
   elif r['type']=='symlink':require(member.issym() and member.linkname==r['target'],'archive link type/target');os.symlink(r['target'],p)
   else:
    require(member.isfile() and member.size==r['size'],'archive file type/size');h=hashlib.sha256();count=0
    with tar.extractfile(member) as src,p.open('xb') as f:
     for b in iter(lambda:src.read(MIB),b''):f.write(b);h.update(b);count+=len(b)
     f.flush();os.fsync(f.fileno())
    require(h.hexdigest()==r['sha256'] and count==r['size'],'restored whole-file SHA mismatch '+name)
   if r['type']!='directory':native_meta(p,r)
 require(seen==set(entries)-set(m['reused_objects']),'tar full selector incomplete')
 for name,ref in m['reused_objects'].items():
  r=entries[name];src=Path(ref['path_on_target']);require(file_sha(src)==r['sha256'],'existing164 reference changed');p=safe(dst,name)
  with src.open('rb') as a,p.open('xb') as b:
   for data in iter(lambda:a.read(MIB),b''):b.write(data)
   b.flush();os.fsync(b.fileno())
  require(file_sha(p)==r['sha256'],'reused content recovery mismatch');native_meta(p,r)
 for r in sorted(m['entries'],key=lambda r:len(PurePosixPath(r['path']).parts),reverse=True):
  if r['type']=='directory':native_meta(safe(dst,r['path']),r)
 return check_native(dst,m)
def new_json(v,p,x):v.exclusive_json(p,x)
def import_v9(b):
 import types
 require(digest(b)==V9SHA,'pinned V9 changed');v=types.ModuleType('frozen_v9');exec(compile(b,'frozen_v9.py','exec'),v.__dict__);return v
def verify_archive(bundle,m):
 require((bundle/'SOURCE_MANIFEST.json').read_bytes()==canon(m),'persisted manifest drift')
 index=json.loads((bundle/'ARCHIVE_INDEX.json').read_bytes());seal=json.loads((bundle/'COMMIT.json').read_bytes())
 require(seal=={'txid':m['txid'],'manifest_sha256':digest(canon(m)),'archive_index_sha256':digest(canon(index)),'policy':'EXCLUSIVE_CREATE_COMMIT_MARKER_LAST'},'COMMIT identity changed')
 h=hashlib.sha256();offset=0
 for r in index['chunks']:
  require(r['txid']==m['txid'] and r['offset']==offset and 0<r['size']<=CHUNK and r['name']==str(offset).zfill(20)+'.part','chunk identity/coverage')
  p=safe(bundle/'chunks',r['name']);require(p.lstat().st_size==r['size'],'chunk length drift');ch=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(MIB),b''):h.update(b);ch.update(b)
  require(ch.hexdigest()==r['sha256'],'durable chunk SHA mismatch');offset+=r['size']
 require(offset==index['archive_bytes'] and h.hexdigest()==index['archive_sha256'],'full archive SHA/coverage mismatch')
 return index
def source_rpc(tool,expression):
 require(expression=='source_resources()','only the read-only resource RPC is available')
 bootstrap="import sys,json,zlib,struct; n=struct.unpack('!Q',sys.stdin.buffer.read(8))[0]; d=json.loads(zlib.decompress(sys.stdin.buffer.read(n))); env={'__name__':'injected'}; exec(compile(d['tool'],'full_result_bundle.py','exec'),env); print(json.dumps(env['source_resources']()))"
 cmd=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-o','ConnectTimeout=10','-p','2233','root@10.208.130.174','python3 -B -c '+__import__('shlex').quote(bootstrap)]
 data=zlib.compress(canon({'tool':tool,'expression':expression}));p=subprocess.run(cmd,input=struct.pack('!Q',len(data))+data,capture_output=True,timeout=45);require(p.returncode==0,'Source resource probe HOLD '+p.stderr.decode(errors='replace')[-2000:]);return json.loads(p.stdout)
def target(config,tool):
 os.nice(19)
 m=config['manifest'];slug=validate(m);v=import_v9(base64.b64decode(config['v9_base64']));start=time.monotonic();nas=NAS/slug/m['txid'];native=NATIVE/slug/m['txid'];peak={'native_allocated':0,'NAS_SSHFS_reported_allocated':0};require(digest(base64.b64decode(config['owner_raw_base64']))==m['owner_ready_sha256'],'raw owner READY binding changed')
 require(os.uname().nodename=='huangrulin-sshfs-174','Target host mismatch')
 def allocated(root):
  total=0;seen=set()
  if not root.exists():return 0
  for p in [root,*root.rglob('*')]:
   s=p.lstat();key=(s.st_dev,s.st_ino)
   if key not in seen:total+=s.st_blocks*512;seen.add(key)
  return total
 def gate():
  require(subprocess.check_output(['findmnt','-n','-T',str(NAS.parent),'-o','TARGET,SOURCE,FSTYPE'],text=True).split()==['/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs'],'true164 mount changed')
  require(Path('/root/data').stat().st_dev==2128 and subprocess.check_output(['findmnt','-n','-T','/root/data','-o','FSTYPE'],text=True).strip()=='ext4','native device changed')
  free=lambda p:(lambda a:a.f_bavail*a.f_frsize)(os.statvfs(p));mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
  a=allocated(native);n=allocated(nas);peak['native_allocated']=max(peak['native_allocated'],a);peak['NAS_SSHFS_reported_allocated']=max(peak['NAS_SSHFS_reported_allocated'],n)
  remain=max(0,config['native_reservation_bytes']-a);require(free('/root/data')-remain-config['concurrent_write_reservation_bytes']>=7*GIB,'SSD remaining-all-reservations below scoped7GiB')
  require(mem>=64*GIB,'host RAM floor');mx=Path('/sys/fs/cgroup/memory.max').read_text().strip();cur=int(Path('/sys/fs/cgroup/memory.current').read_text());require(mx=='max' or int(mx)-cur>=512*MIB,'Target cgroup headroom')
  require(n<=config['NAS_reservation_bytes'] and free(NAS.parent)>=config['NAS_reservation_bytes']-n,'NAS full-size reservation')
  return {'utc':utc(),'SSD_available_bytes':free('/root/data'),'Share_available_bytes':free('/root/share'),'Share_new_bytes':0,'true164_available_bytes':free(NAS.parent),'MemAvailable_bytes':mem,'native_allocated':a,'NAS_SSHFS_reported_allocated':n,'remaining_own_native_reservation':remain,'concurrent_write_reservation_bytes':config['concurrent_write_reservation_bytes']}
 resources=source_rpc(tool,'source_resources()');require(resources['outstanding_write_reservation_bytes']<=config['concurrent_write_reservation_bytes'],'fresh science concurrent reservations exceed budget')
 first=gate();lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 oldtx,oldsha,oldprefix,names=PILOT_REUSE[slug];require(digest((PILOT/slug/'RECEIPT.json').read_bytes())==oldsha,'original pilot receipt changed')
 for name,ref in m['reused_objects'].items():require(file_sha(Path(ref['path_on_target']))==next(r['sha256'] for r in m['entries'] if r['path']==name),'pinned9 existing archive bytes no longer match')
 reservation={'txid':m['txid'],'manifest_sha256':digest(canon(m)),'owner_ready_sha256':m['owner_ready_sha256'],'native_reservation_bytes':config['native_reservation_bytes'],'NAS_reservation_bytes':config['NAS_reservation_bytes'],'tool_sha256':digest(tool.encode()),'zero_new_Share_write':True}
 for root in [nas,native]:
  if root.exists():require((root/'RESERVATION.json').read_bytes()==canon(reservation),'unowned/existing destination conflict')
  else:root.mkdir(parents=True,mode=0o700)
  new_json(v,root/'RESERVATION.json',reservation);new_json(v,root/'SOURCE_MANIFEST.json',m)
  for n,b in [('OWNER_COPY_READY.json',base64.b64decode(config['owner_raw_base64'])),('full_result_bundle.py',tool.encode()),('v9_transaction.py',base64.b64decode(config['v9_base64']))]:
   p=root/n
   if p.exists():require(p.read_bytes()==b,'immutable control changed '+n)
   else:
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 chunks=nas/'chunks';chunks.mkdir(exist_ok=True);records=[];offset=0
 for p in sorted(chunks.glob('*.json')):
  r=json.loads(p.read_bytes());require(r['offset']==offset and r['txid']==m['txid'] and file_sha(chunks/r['name'])==r['sha256'],'resume record gap/identity/SHA');records.append(r);offset+=r['size']
 if not (nas/'COMMIT.json').exists():
  bootstrap="import sys,json,zlib,struct; n=struct.unpack('!Q',sys.stdin.buffer.read(8))[0]; d=json.loads(zlib.decompress(sys.stdin.buffer.read(n))); env={'__name__':'injected'}; exec(compile(d['tool'],'full_result_bundle.py','exec'),env); env['export'](d['manifest'],d['skip'])"
  cmd=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-o','ConnectTimeout=10','-p','2233','root@10.208.130.174','python3 -B -c '+__import__('shlex').quote(bootstrap)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE);b=zlib.compress(canon({'tool':tool,'manifest':m,'skip':offset}));p.stdin.write(struct.pack('!Q',len(b))+b);p.stdin.close();newbytes=0
  try:
   while True:
    n=struct.unpack('!Q',read_exact(p.stdout,8))[0]
    if n==0:
     n=struct.unpack('!Q',read_exact(p.stdout,8))[0];require(n<=32*MIB,'Source proof bound');proof=json.loads(read_exact(p.stdout,n));break
    require(0<n<=CHUNK,'raw chunk too large');expected=read_exact(p.stdout,32).hex();data=read_exact(p.stdout,n);require(digest(data)==expected,'wire chunk SHA');resources=source_rpc(tool,'source_resources()');require(resources['outstanding_write_reservation_bytes']<=config['concurrent_write_reservation_bytes'],'science reservations changed during data window');gate()
    name=str(offset).zfill(20)+'.part';final=chunks/name;writing=chunks/(name+'.writing')
    if writing.exists():
     require(writing.stat().st_size==n and file_sha(writing)==expected,'incomplete orphan retained HOLD');v.rename_noreplace(writing,final)
    elif not final.exists():
     with writing.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
     require(file_sha(writing)==expected,'close-reopen chunk SHA');v.rename_noreplace(writing,final)
    require(final.stat().st_size==n and file_sha(final)==expected,'committed chunk drift');r={'name':name,'offset':offset,'size':n,'sha256':expected,'txid':m['txid']};new_json(v,chunks/(name+'.json'),r);records.append(r);offset+=n;newbytes+=n;del data
    print(json.dumps({'event':'CHUNK_DEST_VERIFIED','project':slug,'offset':offset,'new_transferred_bytes':newbytes,'resources':gate()}),flush=True)
   require(p.wait(timeout=30)==0,'Source exporter failed');require(proof['txid']==m['txid'] and proof['archive_bytes']==offset,'Source terminal binding');require(proof['resources']['outstanding_write_reservation_bytes']<=config['concurrent_write_reservation_bytes'],'Source start reservations exceed allocation')
   h=hashlib.sha256()
   for r in records:
    with (chunks/r['name']).open('rb') as f:
     for b in iter(lambda:f.read(MIB),b''):h.update(b)
   require(h.hexdigest()==proof['archive_sha256'],'independent full archive SHA mismatch')
   index={'txid':m['txid'],'archive_bytes':offset,'archive_sha256':h.hexdigest(),'format':'uncompressed PAX tar excluding pinned9 referenced files','chunks':records,'effective_new_transferred_bytes':newbytes}
   new_json(v,nas/'SOURCE_FULL_SHA_PROOF.json',proof);new_json(v,nas/'ARCHIVE_INDEX.json',index);new_json(v,nas/'COMMIT.json',{'txid':m['txid'],'manifest_sha256':digest(canon(m)),'archive_index_sha256':digest(canon(index)),'policy':'EXCLUSIVE_CREATE_COMMIT_MARKER_LAST'})
  except BaseException:
   if p.poll() is None:p.terminate();p.wait(timeout=15)
   raise
 else:index=verify_archive(nas,m);newbytes=0
 if (nas/'RECEIPT.json').exists():
  receipt=json.loads((nas/'RECEIPT.json').read_bytes());check_native(Path(receipt['native_restore_root']),m);print(json.dumps({'event':'COMPLETED_REUSED','new_transferred_bytes':0,'receipt':receipt}),flush=True);return
 resources=source_rpc(tool,'source_resources()');require(resources['outstanding_write_reservation_bytes']<=config['concurrent_write_reservation_bytes'],'science reservations changed before restore');gate();dst=native/'restored'
 if dst.exists():raise RuntimeError('unfinished native restore retained HOLD; use recovery command with a separately admitted ABSENT directory')
 def restore_gate():
  resources=source_rpc(tool,'source_resources()');require(resources['outstanding_write_reservation_bytes']<=config['concurrent_write_reservation_bytes'],'new science reservation during restore');return gate()
 new_json(v,native/'RESTORE_INTENT.json',{'txid':m['txid'],'destination':str(dst),'was_ABSENT':True,'utc':utc()});rows=restore(nas,m,dst,v,restore_gate);last=gate()
 restoreproof={'status':'RESTORE_VERIFIED_NATIVE_TARGET','txid':m['txid'],'utc':utc(),'files':[r for r in rows if r['type']=='file'],'directories':[r for r in rows if r['type']=='directory'],'symlinks':[r for r in rows if r['type']=='symlink'],'archive_read_only_source':str(nas).replace('/root/share/mnt164','/home/shared',1),'native_root':str(dst),'original_bytes_and_all_numeric_metadata':True,'hardlink_policy':m['hardlink_policy'],'native164_restore_claimed':False}
 new_json(v,nas/'NATIVE_TARGET_RESTORE_PROOF.json',restoreproof)
 pathmap=[{'source':m['source_root']+'/'+r['path'],'bundle_manifest_path':r['path'],'true164_bundle':str(nas).replace('/root/share/mnt164','/home/shared',1),'native_restore':str(dst/r['path']),'sha256':r.get('sha256'),'type':r['type'],'reference':m['reused_objects'].get(r['path'])} for r in m['entries']];new_json(v,nas/'PATH_MAP.json',pathmap)
 pointer={'txid':m['txid'],'true164_bundle':str(nas).replace('/root/share/mnt164','/home/shared',1),'mount_path_on_174new':str(nas),'source_root':m['source_root'],'manifest':'SOURCE_MANIFEST.json','raw_archive_index':'ARCHIVE_INDEX.json','existing164_references':m['reused_objects'],'restore_command':'python3 -B '+str(nas/'full_result_bundle.py')+' --restore '+str(nas)+' --destination /root/data/full_result_offload_20261023_v1/recovery_NEW_ABSENT_'+slug,'restore_scope':'native Target ext4, not native164; new ABSENT directory; complete SHA and numeric metadata; fresh resource admission required'}
 new_json(v,nas/'RECOVERY_POINTER.json',pointer)
 script='#!/bin/sh\nset -eu\n: "${1:?Pass an authorized NEW ABSENT native Target destination}"\nHERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec python3 -B "$HERE/full_result_bundle.py" --restore "$HERE" --destination "$1"\n'
 p=nas/'RESTORE.sh'
 if p.exists():require(p.read_bytes()==script.encode(),'immutable RESTORE changed')
 else:
  with p.open('xb') as f:f.write(script.encode());f.flush();os.fsync(f.fileno())
 receipt={'schema':'FULL_ACCEPTED_RESULT_COPY_ONLY_RECEIPT_V1','status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','project':slug,'txid':m['txid'],'utc':utc(),'manifest_sha256':digest(canon(m)),'owner_ready_sha256':m['owner_ready_sha256'],'archive_index_sha256':digest(canon(index)),'restore_proof_sha256':digest(canon(restoreproof)),'regular_files':sum(r['type']=='file' for r in m['entries']),'directories':sum(r['type']=='directory' for r in m['entries']),'symlinks':sum(r['type']=='symlink' for r in m['entries']),'original_regular_bytes':sum(r['size'] for r in m['entries'] if r['type']=='file'),'archive_bytes':index['archive_bytes'],'effective_new_transferred_bytes':newbytes,'reused_existing164_files':len(m['reused_objects']),'reused_existing164_bytes':sum(next(r['size'] for r in m['entries'] if r['path']==n) for n in m['reused_objects']),'true164_bundle':str(nas).replace('/root/share/mnt164','/home/shared',1),'native_restore_root':str(dst),'elapsed_seconds':time.monotonic()-start,'resources_before':first,'resources_after':last,'observed_allocated_peaks':peak,'source_disposition':'SOURCE_KEEP','source_released_bytes':0,'new_Share_bytes':0,'scientific_acceptance':'OWNER_ONLY_UNCHANGED','owner_postcopy_confirmation':'PENDING_INDEPENDENT_OWNER'}
 new_json(v,nas/'RECEIPT.json',receipt);new_json(v,native/'RECEIPT.json',receipt);print(json.dumps({'event':'DONE','receipt':receipt,'target_receipt_sha256':digest(canon(receipt))}),flush=True);lock.close()
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--restore',type=Path);p.add_argument('--destination',type=Path);a=p.parse_args()
 require(a.restore is not None and a.destination is not None,'finite --restore BUNDLE --destination ABSENT required')
 require(subprocess.check_output(['findmnt','-n','-T',str(NAS.parent),'-o','TARGET,SOURCE,FSTYPE'],text=True).split()==['/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs'],'recovery true164 mount identity');m=json.loads((a.restore/'SOURCE_MANIFEST.json').read_bytes());validate(m);v=import_v9((a.restore/'v9_transaction.py').read_bytes());require(a.restore.resolve().is_relative_to(NAS),'restore input outside authorized true164 roots');require(a.destination.resolve().is_relative_to(NATIVE),'native recovery output outside task scratch');verify_archive(a.restore,m)
 raw=sum(r['size'] for r in m['entries'] if r['type']=='file');free=(lambda s:s.f_bavail*s.f_frsize)(os.statvfs('/root/data'));require(free-raw-64*MIB>=7*GIB,'recovery native capacity floor');resources=source_rpc((a.restore/'full_result_bundle.py').read_text(),'source_resources()');require(free-raw-64*MIB-resources['outstanding_write_reservation_bytes']>=7*GIB,'recovery concurrent reservations')
 lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);a.destination.parent.mkdir(parents=True,exist_ok=True);restore(a.restore,m,a.destination,v);print('RESTORE_VERIFIED_NATIVE_TARGET')
if __name__=='__main__':main()
