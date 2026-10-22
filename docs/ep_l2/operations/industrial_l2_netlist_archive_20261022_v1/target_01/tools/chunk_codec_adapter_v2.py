
"""Bounded independent gzip chunks on V9 primitives; no sender/receiver daemon.
Only exact new9file manifest, SOURCE_KEEP. Native164 proof never uses SSHFS.
"""
import gzip,hashlib,json,os,stat,subprocess,sys,zlib,time
from pathlib import Path,PurePosixPath
import v9_transaction as v
RAW_CAP=128*1024**2
NATIVE_PREFIX='/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261022_industrial_l2_r8p_9json_v1/'
CODEC=dict(name='gzip',level=1,mtime=0,filename='',python=sys.version.split()[0],zlib=zlib.ZLIB_VERSION)
PREFIXES=['postcheck/V3_R8P_PROXY_CRITICAL_PATH_DISCOVERY/pre_3f/','postcheck/V3_R8P_PROXY_CRITICAL_PATH_DISCOVERY/post_0d/','postcheck/V3_R8P2_TOP_CRITICAL_PATH_OPTIMIZATION/baseline_structural/']
def scope(manifest,fixture=False):
 tx=v.validate_manifest(manifest)
 v.require(manifest['source_root']=='/workspace/repos/gpu-l2-cache-verilog/build','wrong source root')
 v.require(len(manifest['files'])==9,'not exact nine')
 v.require(all(r['relative_path'].endswith('.json') and any(r['relative_path'].startswith(p) for p in PREFIXES) for r in manifest['files']),'unapproved file scope')
 v.require(sum(r['relative_path'].startswith(PREFIXES[2]) for r in manifest['files'])==3,'R8P2 count')
 v.require(manifest['source_originals_action']=='SOURCE_KEEP_NO_RELEASE_AUTHORITY','source action')
 if not fixture:v.require(manifest['genuine164_destination_root'].startswith(NATIVE_PREFIX),'destination scope')
 if 'original_source_binding' in manifest:
  b=manifest['original_source_binding'];src_raw=json.dumps(b,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
  v.require(v.digest(src_raw)==manifest['source_transaction_id'],'industrial source txid mismatch')
  v.require(b['canonical_root']==manifest['source_root'] and b['source_commit']==manifest['source_frozen_commit'] and b['native164_destination']==manifest['genuine164_destination_root'] and b['exact_frozen_selector_sha256']==manifest['source_selector_sha256'],'industrial source binding mismatch')
  tx=manifest['source_transaction_id']
 return tx
class StrictThrottle:
 def __init__(self):self.next=time.monotonic()
 def __call__(self,n):
  now=time.monotonic();self.next=max(self.next,now)+n/v.RATE;time.sleep(max(0,self.next-now))
class Archive:
 def __init__(self,root,manifest,fixture=False,native_existing=False):
  self.root=v.no_symlinks(root);self.manifest=manifest;self.fixture=fixture;self.read_only=native_existing;self.txid=scope(manifest,fixture)
  if fixture:v.fixture_root(self.root)
  elif native_existing:
   self.native164_guard(self.root)
   v.require(str(self.root)==manifest['genuine164_destination_root'],'wrong native archive root')
  else:
   v.mount_identity(self.root if self.root.exists() else self.root.parent);v.require(str(self.root)==manifest['destination_path_on_174new'],'wrong target alias')
  if native_existing:v.require((self.root/'COMMIT.json').exists(),'native restore requires committed archive')
  if not self.root.exists():self.root.mkdir(mode=0o700)
  else:v.require((self.root/'RESERVATION.json').exists(),'existing unowned root')
  self.codec=CODEC if not native_existing else json.loads((self.root/'RESERVATION.json').read_bytes())['codec']
  reservation=dict(txid=self.txid,manifest_sha256=v.digest(v.canonical(manifest)),codec=self.codec)
  if native_existing:
   v.require((self.root/'RESERVATION.json').read_bytes()==v.canonical(reservation),'native reservation changed')
   v.require((self.root/'SOURCE_MANIFEST.json').read_bytes()==v.canonical(manifest),'native manifest changed')
  else:
   v.exclusive_json(self.root/'RESERVATION.json',reservation);v.exclusive_json(self.root/'SOURCE_MANIFEST.json',manifest);(self.root/'chunks').mkdir(exist_ok=True)
  self.rows={r['relative_path']:r for r in manifest['files']};self.throttle=StrictThrottle()
 def key(self,name,offset):return v.digest(name.encode())+'.%016d'%offset
 def iter_chunk(self,p,raw_sha,size,compressed_sha=None):
  try:
   if compressed_sha:v.require(v.hash_file(p,throttle=self.throttle)==compressed_sha,'compressed SHA mismatch')
   h=hashlib.sha256();n=0
   with gzip.open(v.no_symlinks(p),'rb') as f:
    while True:
     b=f.read(min(1024**2,size-n+1))
     if not b:break
     n+=len(b);v.require(n<=size,'decompression length exceeds pinned raw');h.update(b);self.throttle(len(b));yield b
   v.require(n==size and h.hexdigest()==raw_sha,'raw SHA/size mismatch')
  except (gzip.BadGzipFile,EOFError,zlib.error) as e:raise v.Hold('compressed stream corrupt: '+str(e))
 def put(self,name,offset,bridge,raw_sha,txid,crash=None):
  v.require(not self.read_only,'native archive read-only');v.require(txid==self.txid,'wrong txid');v.require(not (self.root/'COMMIT.json').exists(),'committed archive is immutable')
  v.relpath(name);v.require(name in self.rows,'unfrozen path');p=v.no_symlinks(bridge);s=p.stat();n=s.st_size
  v.require(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<n<=RAW_CAP and s.st_blocks*512<=v.CAP,'bridge cap/type')
  v.require(0<=offset and offset+n<=self.rows[name]['size'],'range')
  v.require(v.hash_file(p,throttle=self.throttle)==raw_sha,'source/bridge raw SHA')
  key=self.key(name,offset);dst=self.root/'chunks'/(key+'.gz');partial=self.root/'chunks'/(key+'.gz.partial');record=self.root/'chunks'/(key+'.json')
  base=dict(txid=txid,relative_path=name,offset=offset,raw_size=n,raw_sha256=raw_sha,codec=self.codec,chunk_file=dst.name)
  if record.exists():
   r=json.loads(record.read_bytes());v.require(all(r[k]==x for k,x in base.items()),'immutable chunk binding differs')
   for b in self.iter_chunk(dst,raw_sha,n,r['compressed_sha256']):pass
   return dict(r,reused=True)
  if not dst.exists():
   if not partial.exists():
    with p.open('rb') as inp,partial.open('xb') as out:
     before=v.identity(os.fstat(inp.fileno()));v.require(before==v.identity(s),'source open identity')
     with gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=1,mtime=0) as gz:
      for b in iter(lambda:inp.read(1024**2),b''):gz.write(b);self.throttle(len(b))
     out.flush();os.fsync(out.fileno());v.require(v.identity(os.fstat(inp.fileno()))==before==v.identity(p.stat()),'bridge changed')
    if crash=='partial':raise v.Hold('injected complete partial before finalize')
   for b in self.iter_chunk(partial,raw_sha,n):pass
   v.rename_noreplace(partial,dst)
   if crash=='final_before_record':raise v.Hold('injected final before receipt')
  for b in self.iter_chunk(dst,raw_sha,n):pass
  r=dict(base,compressed_size=dst.stat().st_size,compressed_sha256=v.hash_file(dst,throttle=self.throttle))
  v.exclusive_json(record,r)
  if crash=='record':raise v.Hold('injected after receipt')
  return dict(r,reused=False)
 def records(self,name):
  rs=[json.loads(p.read_bytes()) for p in (self.root/'chunks').glob('*.json')]
  return sorted((r for r in rs if r['relative_path']==name),key=lambda r:r['offset'])
 def iter_file(self,name):
  offset=0;h=hashlib.sha256()
  for r in self.records(name):
   v.require(r['txid']==self.txid and r['offset']==offset and r['codec']==self.codec,'gap/overlap/txid/codec')
   v.require(r['chunk_file']==self.key(name,r['offset'])+'.gz','unexpected chunk path')
   for b in self.iter_chunk(self.root/'chunks'/r['chunk_file'],r['raw_sha256'],r['raw_size'],r['compressed_sha256']):h.update(b);offset+=len(b);yield b
  row=self.rows[name];v.require(offset==row['size'] and h.hexdigest()==row['sha256'],'whole original SHA/size mismatch or missing chunk')
 def seal(self):
  verified=[]
  for name in self.rows:
   for b in self.iter_file(name):pass
   verified.append(dict(relative_path=name,size=self.rows[name]['size'],sha256=self.rows[name]['sha256']))
  seal=dict(txid=self.txid,manifest_sha256=v.digest(v.canonical(self.manifest)),files=verified,codec=self.codec,source_action='SOURCE_KEEP_NO_RELEASE_AUTHORITY')
  if self.read_only:v.require((self.root/'COMMIT.json').read_bytes()==v.canonical(seal),'native COMMIT differs')
  else:v.exclusive_json(self.root/'COMMIT.json',seal)
  return seal
 def native_restore(self,destination,fixture=False):
  self.seal();dst=v.no_symlinks(destination);v.require(not os.path.lexists(dst),'restore path exists')
  if fixture:v.fixture_root(dst)
  else:
   v.require(not self.fixture,'fixture cannot mint native164 proof')
   v.require(str(dst).startswith(NATIVE_PREFIX),'restore outside approved164 root')
   self.native164_guard(dst.parent)
  dirs=self.manifest['directories'];need=sum(r['size'] for r in self.rows.values())+256*1024**2;sv=os.statvfs(dst.parent);v.require(sv.f_bavail*sv.f_frsize>=need,'restore capacity')
  v.require(os.geteuid()==0 or all(r['uid']==os.geteuid() and r['gid']==os.getegid() for r in [*self.rows.values(),*dirs]),'native numeric ownership permission')
  dst.mkdir(mode=0o700)
  for d in sorted(dirs,key=lambda r:len(PurePosixPath(r['relative_path']).parts)):(dst/v.relpath(d['relative_path'],root_ok=True)).mkdir(exist_ok=True)
  files=[]
  for name,row in self.rows.items():
   p=dst/name
   with p.open('xb') as out:
    for b in self.iter_file(name):out.write(b)
    out.flush();os.fsync(out.fileno())
   self.apply_verify(p,row);v.require(v.hash_file(p,throttle=self.throttle)==row['sha256'],'independent restored whole SHA')
   files.append(dict(relative_path=name,sha256=row['sha256'],native_identity=v.identity(p.stat())))
  for d in sorted(dirs,key=lambda r:len(PurePosixPath(r['relative_path']).parts),reverse=True):self.apply_verify(dst/v.relpath(d['relative_path'],root_ok=True),d)
  return dict(status='SYNTHETIC_NATIVE_FIXTURE_PASS' if fixture else 'NATIVE164_RESTORE_VERIFIED',txid=self.txid,files=files,directories=len(dirs),ctime='PROVENANCE_ONLY',fixture_only=fixture)
 @staticmethod
 def native164_guard(path):
  ips=subprocess.check_output(['hostname','-I'],text=True).split();v.require('10.208.130.164' in ips,'not independently executed on164')
  fs=subprocess.check_output(['findmnt','-n','-o','FSTYPE','-T',str(path)],text=True).strip();v.require(not any(x in fs for x in ['fuse','sshfs','tmpfs','overlay','ramfs']),'not native164 persistent filesystem')
 @staticmethod
 def apply_verify(p,row):
  os.chown(p,row['uid'],row['gid']);os.chmod(p,row['mode']);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']));s=p.stat()
  v.require((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(row['uid'],row['gid'],row['mode'],row['mtime_ns']),'native metadata mismatch')
