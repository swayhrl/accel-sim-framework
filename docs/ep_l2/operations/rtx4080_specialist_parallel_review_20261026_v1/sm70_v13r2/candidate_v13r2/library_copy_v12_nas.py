"""Finite COPY_ONLY ordered trace receiver; never a scientific launcher.

Adapts the qualified native V2 length-framed input protocol to exact multi-member
manifests. Uses the original sender/receiver locks and pinned V9 publication
primitives. Data buffers are bounded; no source modification or Share staging.
"""
import pathlib,os,sys,json,hashlib,struct,time,fcntl,subprocess,shlex,importlib.util,stat,threading
from concurrent.futures import ThreadPoolExecutor
from collections import deque
P=pathlib.Path;MIB=1024**2;GIB=1024**3;CHUNK=128*MIB;RATE=64*MIB
TASK=P('/root/data/shared_sm70_trace_library_20261024_v1')
NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2')
NAS=P('/root/share/mnt164/huangrulin/traces')
BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
BASELINE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_full_result_offload_v1/EP_L2_E057/aadbbab26f921819e7e24f3bb2187d1955eccd79381a38d475e7eed4e0f36e7d')
V9_SHA='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
sys.dont_write_bytecode=True
SELF_BYTES=P(__file__).read_bytes() if '__file__' in globals() else b''
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def safe(root,name):
 p=P(name);need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,'unsafe relative member');dest=P(root)/p
 for parent in [dest.parent,*dest.parent.parents]:
  if parent==P(root).parent:break
  need(not parent.is_symlink(),'symlink member ancestor')
 return dest
def identity(p):
 s=P(p).lstat();return {'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':s.st_mode&0o7777,'nlink':s.st_nlink,'type':'file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special'}
def same_source(a,b):return all(a[k]==b[k] for k in ['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','type'])
def emit(x):print(json.dumps(x),flush=True)
def v9():
 raw=(BASELINE/'v9_transaction.py').read_bytes();need(digest(raw)==V9_SHA,'qualified V9 primitive changed');s=importlib.util.spec_from_file_location('trace_copy_pinned_v9',BASELINE/'v9_transaction.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def publish_bytes(path,b,v):
 path=P(path)
 if path.exists():need(path.read_bytes()==b,'immutable object collision '+str(path));return
 temp=path.with_name(path.name+'.writing')
 if temp.exists():need(temp.read_bytes()==b,'owned metadata partial collision')
 else:
  with temp.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 v.rename_noreplace(temp,path);need(path.read_bytes()==b,'closed-reopen metadata mismatch')
def hash_file(p,rate=64*MIB,gate=None):
 h=hashlib.sha256();start=time.monotonic();count=0
 with P(p).open('rb') as f:
  while True:
   b=f.read(MIB)
   if not b:break
   h.update(b);count+=len(b)
   if rate:adaptive_io_pace(len(b),rate)
   if gate:gate()
 return h.hexdigest()


_io_pressure_cached=(0,100)
_block_observation=None
_block_health={'known':False}
def block_health():
 global _block_observation,_block_health
 now=time.monotonic()
 if _block_observation and now-_block_observation[0]<5:return _block_health
 try:
  row=next(line.split() for line in P('/proc/diskstats').read_text().splitlines() if line.split()[2]=='sdf')
  values=list(map(int,row[3:]));previous=_block_observation;_block_observation=(now,values)
  if previous:
   elapsed=now-previous[0];old=previous[1];ops=values[0]-old[0]+values[4]-old[4]
   busy=max(0,values[9]-old[9])/elapsed/10
   await_ms=max(0,values[3]-old[3]+values[7]-old[7])/max(1,ops)
   _block_health={'known':True,'device':'sdf','busy_percent':busy,'await_ms':await_ms,'inflight':values[8]}
 except (OSError,StopIteration,ValueError,IndexError):_block_health={'known':False}
 return _block_health
def adaptive_io_rate(maximum,full=None):
 global _io_pressure_cached
 if full is None:
  now=time.monotonic()
  if now-_io_pressure_cached[0]>=5:
   try:
    line=next(x for x in P('/proc/pressure/io').read_text().splitlines() if x.startswith('full '));full=float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
   except (OSError,StopIteration,ValueError):full=100
   _io_pressure_cached=(now,full)
  full=_io_pressure_cached[1]
 health=block_health()
 if health.get('known') and health['busy_percent']<10 and health['await_ms']<25 and health['inflight']<4 and full<5 and _nas_health.get('known') and _nas_health.get('healthy') and time.monotonic()-_nas_health.get('observed_monotonic',0)<30:
  return min(maximum,64*MIB)
 return min(maximum,(30 if full<5 else 10 if full<10 else 4 if full<20 else 1)*MIB)
def adaptive_io_pace(count,maximum):time.sleep(count/adaptive_io_rate(maximum))

"""Resource-progress adapter only; no Source/protocol/partial/manifest changes."""
def _progress_process_identity(proof):
 pid=proof['pid'];ticks=proof['start_ticks']
 need(type(pid)is int and type(ticks)is int and pid>0 and ticks>0,'RESOURCE_HOLD_ACTIVE_PID_PROOF_INVALID')
 try:row=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
 except (FileNotFoundError,ProcessLookupError):return None
 if int(row[19])!=ticks or row[0]in ['Z','X','x']:return None
 return {'pid':pid,'start_ticks':ticks}
class _ProgressTail:
 def __init__(self):self.pending=bytearray();self.records=deque(maxlen=32);self.record_count=0;self.decoded_bytes=0
 def add_record(self,line):
  if not line.strip():return
  try:row=json.loads(line)
  except (ValueError,UnicodeDecodeError)as e:raise RuntimeError('RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_JSON')from e
  need(isinstance(row,dict),'RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_JSON_TYPE');self.records.append(row);self.record_count+=1
 def feed(self,data):
  self.decoded_bytes+=len(data);need(self.decoded_bytes<=64*MIB,'RESOURCE_HOLD_ACTIVE_PROGRESS_DECODED64M_LIMIT')
  self.pending.extend(data)
  while True:
   at=self.pending.find(b'\n')
   if at<0:break
   need(at<=256*1024,'RESOURCE_HOLD_ACTIVE_PROGRESS_RECORD256K_LIMIT');line=bytes(self.pending[:at]);del self.pending[:at+1];self.add_record(line)
  need(len(self.pending)<=256*1024,'RESOURCE_HOLD_ACTIVE_PROGRESS_RECORD256K_LIMIT')
 def finish(self,allow_live_partial):
  if self.pending.strip():
   try:row=json.loads(self.pending)
   except (ValueError,UnicodeDecodeError):
    need(allow_live_partial and bool(self.records)and bytes(self.pending).lstrip().startswith(b'{'),'RESOURCE_HOLD_ACTIVE_PROGRESS_TRUNCATED_JSON')
   else:
    need(isinstance(row,dict),'RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_JSON_TYPE');self.records.append(row);self.record_count+=1;self.pending.clear()
  need(bool(self.records),'RESOURCE_HOLD_ACTIVE_PROGRESS_UNREADABLE')
  return self.records[-1]
def _progress_snapshot(out):
 """Bounded metadata read; a live final gzip member need not have its trailer yet."""
 import zlib
 out=P(out);plain=out/'progress.jsonl';compressed=False
 if plain.exists():path=plain
 else:path=out/'progress.jsonl.gz';compressed=True
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW);tail=_ProgressTail();raw_bytes=0;frames=0;decoder=None;last_eof=False;member_prefix=b''
 with os.fdopen(fd,'rb',buffering=0)as stream:
  before=os.fstat(stream.fileno());need(stat.S_ISREG(before.st_mode),'RESOURCE_HOLD_ACTIVE_PROGRESS_FILE_TYPE')
  if not compressed:
   start=max(0,before.st_size-4096);stream.seek(start);raw=stream.read(before.st_size-start);raw_bytes=len(raw)
   if start:raw=raw.split(b'\n',1)[1]if b'\n'in raw else b''
   tail.feed(raw);last=tail.finish(True)
  else:
   need(before.st_size<=16*MIB,'RESOURCE_HOLD_ACTIVE_PROGRESS_COMPRESSED16M_LIMIT');left=before.st_size
   while left:
    raw=stream.read(min(64*1024,left));need(bool(raw),'RESOURCE_HOLD_ACTIVE_PROGRESS_TRUNCATED_FILE');left-=len(raw);raw_bytes+=len(raw);data=raw
    while data:
     if decoder is None:decoder=zlib.decompressobj(31);member_prefix=b''
     if len(member_prefix)<2:
      member_prefix+=data[:2-len(member_prefix)]
      need(b'\x1f\x8b'.startswith(member_prefix),'RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_GZIP_HEADER')
     previous=len(data)
     try:decoded=decoder.decompress(data,min(64*1024,64*MIB-tail.decoded_bytes+1))
     except zlib.error as e:raise RuntimeError('RESOURCE_HOLD_ACTIVE_PROGRESS_BAD_GZIP')from e
     tail.feed(decoded)
     if decoder.eof:
      frames+=1;data=decoder.unused_data;decoder=None;last_eof=not data
     else:
      data=decoder.unconsumed_tail;last_eof=False
      need(bool(decoded)or len(data)<previous,'RESOURCE_HOLD_ACTIVE_PROGRESS_DECODER_NO_PROGRESS')
   last=tail.finish(decoder is not None)
  after=os.fstat(stream.fileno());path_after=path.lstat()
  need(stat.S_ISREG(path_after.st_mode)and before.st_dev==after.st_dev==path_after.st_dev and before.st_ino==after.st_ino==path_after.st_ino,'RESOURCE_HOLD_ACTIVE_PROGRESS_PATH_FD_CHANGED')
  need(after.st_size>=before.st_size and path_after.st_size>=before.st_size,'RESOURCE_HOLD_ACTIVE_PROGRESS_FILE_TRUNCATED')
  if compressed:need(after.st_size<=16*MIB and path_after.st_size<=16*MIB,'RESOURCE_HOLD_ACTIVE_PROGRESS_COMPRESSED16M_LIMIT')
 meta={'path':str(path),'format':'gzip_stream'if compressed else'plain_tail','compressed_bytes_read':raw_bytes if compressed else 0,'plain_bytes_read':raw_bytes if not compressed else 0,'decoded_bytes':tail.decoded_bytes,'complete_records_seen':tail.record_count,'retained_records':len(tail.records),'gzip_completed_members':frames if compressed else None,'gzip_last_member_eof':last_eof if compressed else None,'live_unfinalized_gzip_CRC_not_claimed':compressed and decoder is not None,'pending_bytes_not_adopted_as_complete':len(tail.pending),'limits':{'compressed_bytes':16*MIB,'decoded_bytes':64*MIB,'retained_records':32,'single_record_bytes':256*1024}}
 return last,meta
def _current_foreign_progress(out,proof):
 """Exact proof identity on both sides; concurrent exit/Z is not an active health failure."""
 before=_progress_process_identity(proof)
 if before is None:return None
 try:
  last,meta=_progress_snapshot(out)
  has_identity='pid'in last or 'start_ticks'in last
  if meta['format']=='gzip_stream'or has_identity:
   need(type(last.get('pid'))is int and type(last.get('start_ticks'))is int and last['pid']==proof['pid']and last['start_ticks']==proof['start_ticks'],'RESOURCE_HOLD_ACTIVE_PROGRESS_PID_TICKS_MISMATCH')
   meta['record_identity']='MATCHED_EXACT_PROOF_PID_START_TICKS'
  else:meta['record_identity']='LEGACY_PLAIN_SCHEMA_WITHOUT_PID_FIELDS_LIVE_PROOF_PRE_POST'
  age=(time.monotonic_ns()-last['mono_ns'])/1e9
  need(age<=30,'RESOURCE_HOLD_ACTIVE_AEFAIR_PROGRESS_FRESHNESS')
  completed=last['completed'];phase=last['phase']
 except (RuntimeError,OSError,ValueError,KeyError,TypeError)as e:
  if _progress_process_identity(proof)is None:return None
  if isinstance(e,RuntimeError)and str(e).startswith('RESOURCE_HOLD_'):raise
  raise RuntimeError('RESOURCE_HOLD_ACTIVE_PROGRESS_UNREADABLE: '+repr(e))from e
 if _progress_process_identity(proof)!=before:return None
 return {'pid':proof['pid'],'start_ticks':proof['start_ticks'],'completed':completed,'phase':phase,'progress_age_seconds':age,'progress_reader':meta}

CODE=P(__file__).resolve().parent
EXACT_MANIFEST=P('/root/data/shared_sm70_trace_library_20261024_v1/manifests/2dcf6422136b02adcc6d.json')
EXACT_MANIFEST_SHA='4f2e611e7b1a2e599005fc2160122eaf0f975c66a45757b0a1f7730713d630ba'
SOURCE_PROOF=P('/root/share/mnt164/huangrulin/traces/receipts/sm70_source_inode_rebind_qualification_20261026_v1/RESULT.json')
SOURCE_PROOF_SHA='5ff68b61806c79a0a6393cf289e4db88aac212f7dfb1a64acca98863c655ccf1'
APPROVED_STATUS='PASS_ROOT_APPROVED_SM70_NAS_ONLY_FUSE_STABLE_FIELDS_V13R2'
_nas_health={'known':False}
def observe_nas_health():
 global _nas_health
 start=time.monotonic()
 try:
  st=os.statvfs(NAS);elapsed=time.monotonic()-start
  _nas_health={'known':True,'observed_monotonic':time.monotonic(),'metadata_latency_s':elapsed,'free_bytes':st.f_bavail*st.f_frsize,'healthy':elapsed<=1.0 and st.f_bavail*st.f_frsize>=64*GIB}
 except OSError as exc:_nas_health={'known':False,'error':repr(exc)}
 return dict(_nas_health)
def root_approval():
 a=read(CODE/'ROOT_APPROVAL.json')
 need(a['status']==APPROVED_STATUS and a['engine_sha256']==digest(SELF_BYTES) and a['manifest_sha256']==EXACT_MANIFEST_SHA and a['source_proof_sha256']==SOURCE_PROOF_SHA,'Root NAS-only/alias approval missing or changed')
 return a

EXACT_ARCHIVE_ALIAS_PATH='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz'
EXACT_ARCHIVE_ALIAS_SHA='9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca'
def fuse_alias_metadata_equal(expected,current):
 # Conservative: every recorded identity field except FUSE inode is exact.
 if not isinstance(expected,dict) or not isinstance(current,dict):return False
 if expected.get('type')!='file' or current.get('type')!='file':return False
 if type(expected.get('inode'))is not int or type(current.get('inode'))is not int or min(expected['inode'],current['inode'])<=0:return False
 return set(expected)==set(current) and all(expected[k]==current[k] for k in expected if k!='inode')
def _genuine164_archive_mount(path):
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(path)],text=True))['filesystems'][0]
 need(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','archive alias not genuine164 FUSE mount')
 return True
def _approved_archive_same_source(expected,current,manifest,testing=False):
 context=manifest.get('_qualified_fuse_alias_context')
 if testing or not context:return same_source(expected,current)
 need(manifest['archive_path']==EXACT_ARCHIVE_ALIAS_PATH and manifest['archive_sha256']==EXACT_ARCHIVE_ALIAS_SHA,'archive FUSE alias exact path or Source SHA changed')
 need(context=={'archive_path':EXACT_ARCHIVE_ALIAS_PATH,'archive_sha256':EXACT_ARCHIVE_ALIAS_SHA,'source_proof_sha256':SOURCE_PROOF_SHA,'manifest_sha256':EXACT_MANIFEST_SHA},'unbound archive FUSE alias context')
 _genuine164_archive_mount(manifest['archive_path'])
 return fuse_alias_metadata_equal(expected,current)
class _SenderStderrCapture:
 def __init__(self,pipe,limit=65536):
  self.pipe=pipe;self.limit=limit;self.tail=bytearray();self.total=0;self.error=None;self.mutex=threading.Lock();self.finished=threading.Event()
  self.thread=threading.Thread(target=self._drain,name='bounded_source_stderr',daemon=True);self.thread.start()
 def _drain(self):
  try:
   while True:
    data=os.read(self.pipe.fileno(),8192)
    if not data:break
    with self.mutex:
     self.total+=len(data);self.tail.extend(data)
     if len(self.tail)>self.limit:del self.tail[:-self.limit]
  except (OSError,ValueError) as exc:
   with self.mutex:self.error=repr(exc)
  finally:self.finished.set()
 def snapshot(self,wait_seconds=.2):
  self.finished.wait(timeout=wait_seconds)
  with self.mutex:return {'sender_stderr_utf8':bytes(self.tail).decode(errors='replace'),'sender_stderr_captured_bytes':len(self.tail),'sender_stderr_total_bytes':self.total,'sender_stderr_limit_bytes':self.limit,'sender_stderr_may_be_truncated':self.total>self.limit,'sender_stderr_read_error':self.error,'sender_stderr_drainer_finished':self.finished.is_set(),'sender_stderr_capture_policy':'CONTINUOUS_DRAIN_RETAIN_LAST64KiB'}
def start_sender_stderr_capture(child):
 need(not hasattr(child,'_bounded_stderr_capture'),'sender stderr collector already attached')
 child._bounded_stderr_capture=_SenderStderrCapture(child.stderr)
 return child
def sender_stderr_snapshot(child,wait_seconds=.2):
 capture=getattr(child,'_bounded_stderr_capture',None)
 if capture is None:return {'sender_stderr_read_error':'MISSING_CONTINUOUS_COLLECTOR','sender_stderr_drainer_finished':False}
 return capture.snapshot(wait_seconds)
def sender_eof_diagnostic(child,wait_seconds=2.0):
 try:rc=child.wait(timeout=wait_seconds)
 except subprocess.TimeoutExpired:rc=None
 return {'sender_returncode':rc,**sender_stderr_snapshot(child),'sender_diagnostic_no_restart':True}


def qualified_archive_request(request,testing=False):
 if testing:return request
 a=root_approval();need(a.get('source_alias_approved')is True,'Source alias requires explicit Root approval')
 need(digest(EXACT_MANIFEST.read_bytes())==EXACT_MANIFEST_SHA,'frozen historical manifest changed')
 original=read(EXACT_MANIFEST);need(request['manifest']==original,'alias scope differs from exact manifest')
 raw=SOURCE_PROOF.read_bytes();need(digest(raw)==SOURCE_PROOF_SHA,'Source fullSHA proof changed');proof=json.loads(raw)
 need(proof['status']=='PASS_FROZEN_ARCHIVE_WHOLE_SHA_EQUAL_NEW_INODE' and proof['manifest_sha256']==EXACT_MANIFEST_SHA and proof['manifest_not_modified']is True and proof['Source_KEEP']is True and proof['release_bytes']==0,'Source proof status/scope')
 need(proof['archive_sha256']==original['archive_sha256'] and proof['bytes_read']==original['archive_identity']['size'] and proof['frozen_archive_identity']==original['archive_identity'],'Source fullSHA not equal frozen inventory')
 old=proof['frozen_archive_identity'];new=proof['observed_archive_identity']
 need({k for k in old if old[k]!=new[k]}=={'inode'},'alias must differ only in historical FUSE inode')
 current=identity(original['archive_path']);_genuine164_archive_mount(original['archive_path'])
 need(fuse_alias_metadata_equal(new,current),'qualified Source alias stable metadata changed')
 alias=json.loads(json.dumps(request));alias['manifest']['archive_identity']=current
 alias['manifest']['_qualified_fuse_alias_context']={'archive_path':original['archive_path'],'archive_sha256':original['archive_sha256'],'source_proof_sha256':SOURCE_PROOF_SHA,'manifest_sha256':EXACT_MANIFEST_SHA}
 observe_nas_health();install_nas_write_boundary(a);return alias
def native_control_bytes():
 # Runtime logs/artifacts must live on genuine164; no new Native payload path exists.
 if CODE.is_relative_to(NAS):return 0
 need(CODE.is_relative_to(P('/root/data/sm70_nas_only_alias_resume_review_20261026_v1')),'unrecognized code location')
 return sum(p.lstat().st_blocks*512 for p in CODE.rglob('*') if p.is_file() and not p.is_symlink())
def nas_native_budget(free,reservations,controls):
 need(type(controls)is int and 0<=controls<=64*MIB,'RESOURCE_HOLD_OWN_NATIVE_CONTROL64M_CAP')
 required=5*GIB+64*MIB
 need(free>=required,'RESOURCE_HOLD_PHYSICAL_NATIVE5GiB_PLUS_CONTROL64M')
 need(all(type(x)is int and x>=0 for x in reservations),'RESOURCE_HOLD_REGISTERED_RESERVATION_SCHEMA')
 return {'required_SSD_bytes':required,'own_Native_payload_write_bytes':0,'own_Native_control_cap_bytes':64*MIB,'own_Native_control_current_bytes':controls,'registered_foreign_write_reservations_bytes':sum(reservations),'foreign_reservations_exceed_free_report_only':sum(reservations)>free,'foreign_reservations_modified_or_excluded':False,'NAS_only_runtime':True}

_boundary_installed=False
def install_nas_write_boundary(approval):
 global _boundary_installed
 if _boundary_installed:return
 roots=[P(approval['runtime_root']).resolve(),P(read(EXACT_MANIFEST)['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1)).resolve()]
 locks={str((TASK/'control/SUPERVISOR.lock').resolve()),str((TASK/'control/TRANSFER_DRIVER.lock').resolve()),str((BRIDGE/'.SHARED_SM70_LIBRARY_SOURCE.lock').resolve()),str((BRIDGE/'.SHARED_SM70_LIBRARY_TARGET.lock').resolve())}
 def allowed(path,lock_open=False):
  if isinstance(path,int):return True
  q=P(os.fsdecode(path)).absolute().resolve()
  if lock_open and str(q)in locks:
   need(q.is_file() and not q.is_symlink(),'existing exact lease file required');return True
  return any(q==r or q.is_relative_to(r) for r in roots)
 def audit(event,args):
  if event=='open':
   path,mode,flags=args
   writing=(isinstance(mode,str)and any(c in mode for c in 'wax+'))or(bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
   if writing:
    devnull=False
    if not isinstance(path,int) and str(P(os.fsdecode(path)).absolute())=='/dev/null':
     try:
      node=P('/dev/null').lstat();devnull=not stat.S_ISLNK(node.st_mode) and stat.S_ISCHR(node.st_mode) and os.major(node.st_rdev)==1 and os.minor(node.st_rdev)==3
     except OSError:devnull=False
    need(devnull or allowed(path,lock_open=not bool(flags&os.O_TRUNC)),'NATIVE_WRITE_BOUNDARY_DENIED '+str(path))
  elif event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.chown','os.utime'):
   need(allowed(args[0]),'NATIVE_MUTATION_BOUNDARY_DENIED '+str(args[0]))
  elif event in ('os.rename','os.link','os.symlink'):
   need(allowed(args[0])and allowed(args[1]),'NATIVE_MOVE_BOUNDARY_DENIED')
 sys.addaudithook(audit);_boundary_installed=True

class Resources:
 def __init__(self,testing=False):self.last=0;self.last_value=None;self.testing=testing;self.samples=[];self.mutex=threading.RLock()
 def __call__(self,force=False):
  with self.mutex:return self._checked(force)
 def _checked(self,force=False):
  if not force and self.last_value and time.monotonic()-self.last<10:return self.last_value
  need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]' and NATIVE.stat().st_dev==2128,'Target identity changed')
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0];need(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','not genuine164')
  registry=read(NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reserved=sum(x.get('reserved_write_bytes',0) for x in registry.get('registered_future_requests',{}).values());disk=os.statvfs(NATIVE);free=disk.f_bavail*disk.f_frsize;required=5*GIB+reserved+GIB+64*MIB
  need(free>=required and disk.f_favail>=100000,'RESOURCE_HOLD_SHARED_SSD_ALL_PROJECT_RESERVATIONS')
  mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;cur=int(P('/sys/fs/cgroup/memory.current').read_text());maxval=P('/sys/fs/cgroup/memory.max').read_text().strip();need(mem>=64*GIB and (maxval=='max' or int(maxval)-cur>=GIB),'RESOURCE_HOLD_HOST_OR_CGROUP_RAM')
  pressure={line.split()[0]:{a.split('=')[0]:float(a.split('=')[1]) for a in line.split()[1:]} for line in P('/proc/pressure/io').read_text().splitlines()};active=[]
  ae=P('/root/data/dtc_main_20261023_v1/ae_fair_v1/control/qualification_ledger')
  pending_intents=set(ae.glob('*.INTENT.json'))
  for registered in registry.get('registered_future_requests',{}).values():
   consumed=registered.get('consumed',{})
   if not isinstance(consumed,dict):continue
   for record in consumed.values():
    if isinstance(record,dict) and not record.get('execution_receipt') and record.get('intent'):pending_intents.add(P(record['intent']))
  for f in sorted(pending_intents):
   if f.with_name(f.name.replace('.INTENT.','.DONE.')).exists():continue
   try:i=read(f)
   except FileNotFoundError as e:raise RuntimeError('RESOURCE_HOLD_FOREIGN_INTENT_UNREADABLE: '+str(f))from e
   out=P(i['output']);proof=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   try:p=read(proof)
   except FileNotFoundError:continue
   observed=_current_foreign_progress(out,p)
   if observed is None:continue
   active.append({'cohort':i['cohort'],**observed})
  # This COPY_ONLY task uses a conservative low-pressure window while science
  # is active; it never alters the scientific controller's IO warning policy.
  # User authorizes adaptive low-priority progress rather than a blanket IO HOLD.
  io_rate=adaptive_io_rate(30*MIB,pressure.get('full',{}).get('avg10',100))
  value={'observed_unix':time.time(),'SSD_free_bytes':free,'required_SSD_bytes':required,'registered_foreign_write_reservations_bytes':reserved,'unregistered_other_project_headroom_bytes':GIB,'task_controls_reserve_bytes':64*MIB,'host_MemAvailable_bytes':mem,'cgroup_current':cur,'host_IO_pressure':pressure,'adaptive_IO_max_read_bytes_sec':io_rate,'IO_policy':'V7_BLOCK_HEALTH_DISTINGUISHES_NAS_SELF_WAIT','physical_block_health':dict(_block_health),'active_AEFAIR':active,'Share_new_bytes':0,'all_policy_gates_pass':True};self.last=time.monotonic();self.last_value=value;self.samples.append(value);return value

def source_send(request,testing=False):
 manifest=request['manifest'];skip=request['skip']
 if manifest.get('source_backend')=='archive':return source_archive_send(request,testing)
 if testing:need(P(manifest['source_root']).is_relative_to(TASK/'synthetic'),'test source outside own synthetic namespace')
 else:need((os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]') or (manifest.get('source_backend')=='native' and os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'),'wrong frozen source namespace')
 lock=((TASK/'synthetic/.SOURCE_TEST.lock') if testing else (BRIDGE/'.SHARED_SM70_LIBRARY_SOURCE.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:os.nice(19)
 except OSError:pass
 def frame(obj):b=canon(obj);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
 for row in manifest['members']:
  path=safe(manifest['source_root'],row['relative_path']);before=identity(path);need(same_source(before,row),'Source exact frozen identity changed '+str(path));need(row['type']=='file','nonregular producer member');h=hashlib.sha256();offset=0;need(skip[row['relative_path']]<=row['size'],'invalid resume range')
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb',buffering=0) as f:
   while True:
    b=f.read(CHUNK)
    if not b:break
    h.update(b)
    if offset>=skip[row['relative_path']]:
     frame({'event':'CHUNK','path':row['relative_path'],'offset':offset,'size':len(b),'sha256':digest(b)})
     for i in range(0,len(b),MIB):part=memoryview(b)[i:i+MIB];adaptive_io_pace(len(part),RATE);sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
    offset+=len(b)
  need(same_source(before,identity(path)) and offset==row['size'],'Source changed during readonly stream');need(h.hexdigest()==row['sha256'],'Source full SHA differs from frozen evidence '+str(path));frame({'event':'FILE_END','path':row['relative_path'],'size':offset,'sha256':h.hexdigest(),'source_before_after_identity_unchanged':True,'source_disposition':'SOURCE_KEEP'})
 frame({'event':'SOURCE_DONE','Source_simulator_starts':0,'source_disposition':'SOURCE_KEEP'})

def spawn_sender(manifest,skip,testing=False):
 request={'manifest':manifest,'skip':skip}
 if testing or manifest.get('source_backend')=='native' or manifest.get('source_host')=='174-new':
  p=subprocess.Popen(['/usr/bin/python3','-B',str(P(__file__)),('source-native' if manifest.get('source_backend')=='native' or manifest.get('source_host')=='174-new' else 'source-synthetic')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);start_sender_stderr_capture(p);p.stdin.write(canon(request));p.stdin.close();return p
 source=SELF_BYTES.decode();boot='import sys,json;code=sys.stdin.buffer.readline();exec(compile(json.loads(code),"frozen_readonly_trace_export.py","exec"),{"__name__":"trace_source"})';payload=source+'\nsource_send(json.loads(sys.stdin.buffer.readline()))\n'
 ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174'];p=subprocess.Popen(ssh+['python3 -B -c '+shlex.quote(boot)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);start_sender_stderr_capture(p);p.stdin.write((json.dumps(payload)+'\n').encode()+canon(request));p.stdin.close();return p

def migrate(manifest,testing=False,inject_after_ranges=None):
 need(manifest['freeze_status'].startswith('FROZEN'),'source scope held');g=Resources(testing);before=g(True);bundle=P(manifest['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));need(bundle.is_relative_to(NAS),'wrong new NAS scope');need(not manifest.get('reuse'),'reuse must not enter new payload path')
 available=os.statvfs(NAS.parent).f_bavail*os.statvfs(NAS.parent).f_frsize;need(available>=3*manifest['source_data_bytes']+64*MIB,'RESOURCE_HOLD_NAS_CAPACITY')
 lock=(BRIDGE/('.SHARED_SM70_V8_QUAL_TARGET.lock' if testing else '.SHARED_SM70_LIBRARY_TARGET.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);v=v9();bundle.mkdir(parents=True,exist_ok=True);publish_bytes(bundle/'SOURCE_MANIFEST.json',canon(manifest),v);(bundle/'chunks').mkdir(exist_ok=True);(bundle/'tree').mkdir(exist_ok=True)
 if (bundle/'COMMIT.json').exists():return verify_committed(bundle,g,rehash=False)
 if not testing:qualified_archive_request({'manifest':manifest,'skip':{}}) # Early bounded metadata admission, before the mandatory full retained-range SHA pass.
 skip={};ranges={};newbytes=0;resumed=0
 for row in manifest['members']:
  name=row['relative_path'];key=digest(name.encode());folder=bundle/'chunks'/key;folder.mkdir(exist_ok=True);chunks=[];offset=0
  for orphan in folder.glob('*.part'):
   if orphan.with_name(orphan.name+'.json').exists():continue
   header=orphan.with_name(orphan.name+'.frame');need(header.exists(),'unbound orphan range retained HOLD');c=read(header);need(orphan.stat().st_size==c['size'] and hash_file(orphan,gate=g)==c['sha256'],'orphan range SHA mismatch');publish_bytes(orphan.with_name(orphan.name+'.json'),canon(c),v)
  for p in sorted(folder.glob('*.json')):
   c=read(p);need(c['offset']==offset and 0<c['size']<=CHUNK,'resume coverage gap');data=folder/c['name'];need(data.stat().st_size==c['size'] and hash_file(data,gate=g)==c['sha256'],'resume chunk damaged');chunks.append(c);offset+=c['size'];resumed+=c['size']
  need(offset<=row['size'],'resume beyond source EOF');skip[name]=offset;ranges[name]=chunks
 p=spawn_sender(manifest,skip,testing);ends=[];count_ranges=0
 # Exactly one frame receiver and one source sender retain the original leases.
 # Two workers only verify distinct closed chunks; at most three chunks can be
 # pending. They never receive source frames, assemble trees, or publish COMMIT.
 pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='closed_chunk_SHA')
 pending=deque();next_offsets=dict(skip);peak_pending=0
 def verify_closed(partial,dest,folder,leaf,c):
  need(hash_file(partial,gate=g)==c['sha256'],'closed chunk full SHA mismatch')
  v.rename_noreplace(partial,dest)
  need(hash_file(dest,gate=g)==c['sha256'],'published range reopen SHA')
  publish_bytes(folder/(leaf+'.json'),canon(c),v)
  return c
 def drain_one():
  nonlocal newbytes,count_ranges
  name,future=pending.popleft();c=future.result()
  ranges[name].append(c);newbytes+=c['size'];count_ranges+=1
  emit({'event':'RANGE_VERIFIED','asset':manifest['primary_asset_id'],'file':name,'verified_end':c['offset']+c['size'],'new_payload_bytes':newbytes})
  if inject_after_ranges is not None and count_ranges>=inject_after_ranges:raise RuntimeError('INJECTED_BOUNDED_OWN_RANGE_CRASH')
 def exact(n):
  out=bytearray()
  while len(out)<n:
   b=p.stdout.read(n-len(out))
   if not b:raise RuntimeError('Source EOF before complete verification '+json.dumps(sender_eof_diagnostic(p),sort_keys=True))
   out.extend(b)
  return bytes(out)
 try:
  while True:
   length=struct.unpack('!Q',exact(8))[0];need(length<=1024**2,'header bound');event=json.loads(exact(length));g()
   if event['event']=='SOURCE_DONE':break
   if event['event']=='FILE_END':ends.append(event);continue
   need(event['event']=='CHUNK' and event['path'] in ranges,'unknown frame');name=event['path'];need(event['offset']==next_offsets[name] and 0<event['size']<=CHUNK,'range offset/size changed');folder=bundle/'chunks'/digest(name.encode());leaf=str(event['offset']).zfill(20)+'.part';dest=folder/leaf;partial=folder/(leaf+'.writing');h=hashlib.sha256();left=event['size']
   if partial.exists():
    # Owned uncommitted partial may only be removed if its prefix matches this
    # exact incoming immutable range. No scientific/source path is involved.
    previous=partial.read_bytes();need(len(previous)<=left,'partial larger than range')
   else:previous=b''
   c={'name':leaf,'offset':event['offset'],'size':event['size'],'sha256':event['sha256']};publish_bytes(folder/(leaf+'.frame'),canon(c),v)
   with partial.open('ab' if previous else 'xb') as f:
    pos=0
    while left:
     b=exact(min(MIB,left));h.update(b)
     overlap=min(len(b),max(0,len(previous)-pos))
     if overlap:need(b[:overlap]==previous[pos:pos+overlap],'owned partial prefix collision')
     if overlap<len(b):f.write(b[overlap:])
     pos+=len(b);left-=len(b);g()
    f.flush();os.fsync(f.fileno())
   need(h.hexdigest()==event['sha256'],'received chunk full SHA mismatch')
   next_offsets[name]+=event['size']
   pending.append((name,pool.submit(verify_closed,partial,dest,folder,leaf,c)))
   peak_pending=max(peak_pending,len(pending))
   if len(pending)>=3:drain_one()
  while pending:drain_one()
  rc=p.wait(timeout=30);need(rc==0,'Source readonly export failed: '+json.dumps(sender_stderr_snapshot(p),sort_keys=True))
 finally:
  if p.poll() is None:p.terminate();p.wait(timeout=10)
  p.stdout.close();p.stderr.close()
  pool.shutdown(wait=True)
 need([x['path'] for x in ends]==[x['relative_path'] for x in manifest['members']],'incomplete/unordered source EOF proof')
 for row,end in zip(manifest['members'],ends):
  need((end['sha256'],end['size'])==(row['sha256'],row['size']),'source member proof mismatch');dest=safe(bundle/'tree',row['relative_path']);dest.parent.mkdir(exist_ok=True,parents=True);partial=dest.with_name(dest.name+'.writing')
  if dest.exists():need(dest.stat().st_size==row['size'] and hash_file(dest,gate=g)==row['sha256'],'existing tree file collision');continue
  if partial.exists():need(partial.stat().st_size==row['size'] and hash_file(partial,gate=g)==row['sha256'],'owned tree partial needs range recovery; retained')
  else:
   offset=0;h=hashlib.sha256();start=time.monotonic();done=0
   with partial.open('xb') as f:
    for c in ranges[row['relative_path']]:
     need(c['offset']==offset,'assembly gap');chunk=bundle/'chunks'/digest(row['relative_path'].encode())/c['name']
     with chunk.open('rb') as src:
      while True:
       b=src.read(MIB)
       if not b:break
       f.write(b);h.update(b);done+=len(b);adaptive_io_pace(len(b),RATE);g()
     offset+=c['size']
    f.flush();os.fsync(f.fileno())
   need(offset==row['size'] and h.hexdigest()==row['sha256'],'materialized whole content mismatch')
  need(hash_file(partial,gate=g)==row['sha256'],'closed-reopened materialized whole SHA');v.rename_noreplace(partial,dest);dest.chmod(0o444)
 treeproof=verify_tree(bundle/'tree',manifest,g,rehash=False);publish_bytes(bundle/'SOURCE_CURRENT_EOF_SHA_PROOFS.json',canon(ends),v);publish_bytes(bundle/'RANGE_INDEX.json',canon(ranges),v);publish_bytes(bundle/'TREE_VERIFICATION.json',canon(treeproof),v)
 result={'status':'TRUE164_DIRECT_READ_READY','asset_id':manifest['primary_asset_id'],'object_id':manifest['object_id'],'bundle':str(bundle),'true164_bundle':manifest['new_true164_bundle'],'true164_tree':manifest['new_true164_bundle']+'/tree','mount_tree':str(bundle/'tree'),'manifest_sha256':digest(canon(manifest)),'original_bytes':manifest['source_data_bytes'],'members':len(manifest['members']),'kernels':len(manifest['ordered_kernel_members']),'new_payload_bytes':newbytes,'reused_verified_range_bytes':resumed,'bounded_verification_pipeline':{'workers':2,'pending_chunk_limit':3,'observed_peak_pending':peak_pending,'source_and_target_writer_leases':1,'closed_and_published_chunk_full_SHA_preserved':True},'Source_full_SHA_matches':True,'true164_closed_reopen_whole_SHA_matches':True,'RESTORE_VERIFIED_NATIVE_TARGET':'NOT_PERFORMED_BY_TRANSFER; independent bounded check is separate','before':before,'after':g(True),'resource_samples':g.samples,'source_disposition':'SOURCE_KEEP','Source_simulator_starts':0,'Share_new_bytes':0}
 publish_bytes(bundle/'RECEIPT.json',canon({k:x for k,x in result.items() if k not in ['before','after','resource_samples','new_payload_bytes','reused_verified_range_bytes']}),v)
 publish_bytes(bundle/'trace_copy.py',SELF_BYTES,v);publish_bytes(bundle/'RESTORE.sh',b'#!/bin/sh\nset -eu\n: "${1:?Pass a NEW ABSENT task-native recovery directory}"\nHERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec /usr/bin/python3 -B "$HERE/trace_copy.py" restore "$HERE" "$1"\n',v)
 commit={'schema':'IMMUTABLE_MULTI_MEMBER_TRACE_INPUT_COMMIT_V1','object_id':manifest['object_id'],'manifest_sha256':digest(canon(manifest)),'range_index_sha256':digest(canon(ranges)),'tree_verification_sha256':digest(canon(treeproof)),'Source_disposition':'SOURCE_KEEP','scientific_acceptance_granted':False};publish_bytes(bundle/'COMMIT.json',canon(commit),v)
 return result

def verify_tree(tree,manifest,gate,rehash=False):
 tree=P(tree);need(tree.is_dir() and not tree.is_symlink(),'missing physical true164 tree');rows=[]
 expected=set(x['relative_path'] for x in manifest['members']);actual={x.relative_to(tree).as_posix() for x in tree.rglob('*') if x.is_file()};need(actual==expected,'complete tree membership mismatch')
 for row in manifest['members']:
  p=safe(tree,row['relative_path']);need(p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'],'tree file type/size');gate()
  if rehash:need(hash_file(p,gate=gate)==row['sha256'],'current whole tree SHA mismatch')
  with p.open('rb') as f:
   first=f.read(min(1024,p.stat().st_size));f.seek(max(0,p.stat().st_size-64));tail=f.read(64)
  with p.open('rb') as f:need(f.read(len(first))==first,'reopen mismatch')
  if manifest.get('payload_kind')=='CAS_FILES_V1':
   if row.get('header_prefix_hex'):need(first[:128].hex()==row['header_prefix_hex'],'CAS prefix differs from frozen source')
  elif row['relative_path']==manifest['entry_name']:need(p.read_bytes().hex()==manifest['commandlist_bytes_hex'],'commandlist bytes/order drift')
  else:need(first[:128].hex()==row['header_prefix_hex'],'kernel header differs from source')
  rows.append({'relative_path':row['relative_path'],'size':row['size'],'sha256':row['sha256'],'actual_tree_identity':identity(p),'open_seek_reopen':True,'header_matches_source':True,'last_read_bytes':len(tail),'full_hash_recomputed_in_this_call':rehash})
 return rows

def verify_committed(bundle,gate=None,rehash=False):
 gate=gate or Resources();m=read(P(bundle)/'SOURCE_MANIFEST.json');c=read(P(bundle)/'COMMIT.json');need(c['manifest_sha256']==digest(canon(m)) and c['object_id']==m['object_id'],'committed selector changed');proof=verify_tree(P(bundle)/'tree',m,gate,rehash=rehash);r=read(P(bundle)/'RECEIPT.json');need(r['object_id']==m['object_id'],'committed receipt mismatch');return dict(r,new_payload_bytes=0,reused_verified_range_bytes=m['source_data_bytes'],completed_transaction_reused=True,current_tree_validation=proof)

def restore_native(tree,manifest,destination,gate=None):
 gate=gate or Resources();gate(True);dest=P(destination);need(dest.is_absolute() and dest.is_relative_to(TASK/'recovery') and '..' not in dest.parts,'restore outside dedicated native namespace');need(not os.path.lexists(dest),'ABSENT restore destination required');need(manifest['source_data_bytes']<=240*MIB,'NOT_PERFORMED_NATIVE_RESTORE_EXCEEDS_BOUNDED240MIB_WINDOW')
 allocated=sum(p.lstat().st_blocks*512 for p in TASK.rglob('*') if not p.is_symlink());need(allocated+manifest['source_data_bytes']<=256*MIB,'RESOURCE_HOLD_NATIVE_TASK256MIB_SCRATCH_CAP');dest.parent.mkdir(parents=True,exist_ok=True);dest.mkdir(mode=0o700);rows=[]
 for row in manifest['members']:
  src=safe(tree,row['relative_path']);p=safe(dest,row['relative_path']);p.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();start=time.monotonic();count=0
  with src.open('rb') as f,p.open('xb') as out:
   while True:
    b=f.read(MIB)
    if not b:break
    out.write(b);h.update(b);count+=len(b);time.sleep(max(0,count/(30*MIB)-(time.monotonic()-start)));gate()
   out.flush();os.fsync(out.fileno())
  need(count==row['size'] and h.hexdigest()==row['sha256'],'restored original bytes mismatch');os.chown(p,row['uid'],row['gid']);p.chmod(row['mode']);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']));a=identity(p);need(all(a[k]==row[k] for k in ['size','uid','gid','mode','mtime_ns']) and hash_file(p,rate=0)==row['sha256'],'closed restored SHA/numeric metadata mismatch');rows.append({'relative_path':row['relative_path'],'sha256':row['sha256'],'identity':a})
 d=manifest['source_root_identity'];os.chown(dest,d['uid'],d['gid']);dest.chmod(d['mode']);os.utime(dest,ns=(d['mtime_ns'],d['mtime_ns']));need(all(identity(dest)[k]==d[k] for k in ['uid','gid','mode','mtime_ns']),'root directory restored metadata mismatch')
 return {'status':'RESTORE_VERIFIED_NATIVE_TARGET','destination':str(dest),'scope':'Dedicated174-new native ext4, not native164','regular_files':len(rows),'rows':rows,'root_directory_original_numeric_metadata':manifest.get('payload_kind')!='CAS_FILES_V1','root_directory_manifest_numeric_metadata':True,'original_bytes':manifest['source_data_bytes'],'Source_mutations':0}



def archive_member_end_event(path,size,sha256,manifest):
 event={'event':'FILE_END','path':path,'size':size,'sha256':sha256,'source_before_after_identity_unchanged':True,'source_disposition':'SOURCE_KEEP'}
 if manifest.get('_qualified_fuse_alias_context'):
  event.update({'source_before_after_identity_unchanged':None,'stable_fields_excluding_FUSE_inode':True,'policy':'EXACT_ROOT_FUSE_ALIAS_PLUS_ARCHIVE_AND_MEMBER_SHA','whole_archive_proof':'PENDING_UNTIL_SOURCE_DONE'})
 return event

def source_archive_send(request,testing=False):
 import tarfile,gzip,threading
 m=request['manifest'];archive=P(m['archive_path']);skip=request['skip']
 if testing:need(archive.is_relative_to(TASK/'synthetic'),'archive test outside owned source')
 else:need((os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]') or (m.get('source_host')=='174-new' and os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'),'archive source identity')
 need(_approved_archive_same_source(m['archive_identity'],identity(archive),m,testing),'archive stable identity changed before stream')
 lock=((TASK/'synthetic/.SOURCE_TEST.lock') if testing else (BRIDGE/'.SHARED_SM70_LIBRARY_SOURCE.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:os.nice(19)
 except OSError:pass
 def frame(o):b=canon(o);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
 wanted={r['archive_member']:r for r in m['members']};found=[];decoder=None;feeder=None;gz=None;errors=[];started=time.monotonic();physical=[0];archive_hash=hashlib.sha256()
 fd=os.open(archive,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0));raw=os.fdopen(fd,'rb')
 class RateReader:
  def read(self,n=-1):
   b=raw.read(n);archive_hash.update(b);physical[0]+=len(b);adaptive_io_pace(len(b),30*MIB);return b
 reader=RateReader()
 if str(archive).endswith('.zst'):
  decoder=subprocess.Popen([('/usr/bin/zstd' if P('/usr/bin/zstd').is_file() else str(TASK/'tools/zstd')),'-dc'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def feed():
   try:
    while True:
     b=reader.read(MIB)
     if not b:break
     decoder.stdin.write(b)
    decoder.stdin.close()
   except Exception as x:errors.append(str(x))
  feeder=threading.Thread(target=feed);feeder.start();decoded_stream=decoder.stdout
 else:gz=gzip.GzipFile(fileobj=reader,mode='rb');decoded_stream=gz
 class StrictTarInfo(tarfile.TarInfo):
  @classmethod
  def fromtarfile(cls,archive):
   try:return super().fromtarfile(archive)
   except (tarfile.EmptyHeaderError,tarfile.EOFHeaderError):raise
   except tarfile.HeaderError as exc:raise tarfile.ReadError('strict archive header '+str(exc)) from exc
 tf=tarfile.open(fileobj=decoded_stream,mode='r|',ignore_zeros=True,tarinfo=StrictTarInfo,errorlevel=2)
 try:
  for ti in tf:
   name=ti.name
   if name not in wanted or name in found:continue
   row=wanted[name];need(ti.isfile() and ti.size==row['size'],'archive member type/size drift');f=tf.extractfile(ti);h=hashlib.sha256();offset=0
   while True:
    b=f.read(CHUNK)
    if not b:break
    h.update(b)
    if offset>=skip[row['relative_path']]:
     frame({'event':'CHUNK','path':row['relative_path'],'offset':offset,'size':len(b),'sha256':digest(b)})
     for i in range(0,len(b),MIB):part=memoryview(b)[i:i+MIB];adaptive_io_pace(len(part),RATE);sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
    offset+=len(b)
   need(offset==row['size'] and h.hexdigest()==row['sha256'],'archive member full SHA drift');found.append(name)
   frame(archive_member_end_event(row['relative_path'],offset,h.hexdigest(),m))
  need(found==[r['archive_member'] for r in m['members']],'archive member order or EOF mismatch')
  need(_approved_archive_same_source(m['archive_identity'],identity(archive),m,testing),'archive stable identity changed during stream')
 finally:
  tf.close()
  if decoder:
   while decoder.stdout.read(MIB):pass
   feeder.join();need(not errors,'zstd input stream error');need(decoder.wait()==0,'zstd decoder failed')
  else:
   while gz.read(MIB):pass
   gz.close()
   while reader.read(MIB):pass
  raw.close()
 need(physical[0]==m['archive_identity']['size'],'archive physical EOF incomplete')
 if m.get('archive_sha256'):need(archive_hash.hexdigest()==m['archive_sha256'],'archive whole SHA differs from inventory')
 need(_approved_archive_same_source(m['archive_identity'],identity(archive),m,testing),'archive stable identity changed before final source close')
 frame({'event':'SOURCE_DONE','Source_simulator_starts':0,'source_disposition':'SOURCE_KEEP'})

StrictResourcesV10=Resources
class NASOnlyResources(StrictResourcesV10):
 def _checked(self,force=False):
   if not force and self.last_value and time.monotonic()-self.last<10:return self.last_value
   need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]' and NATIVE.stat().st_dev==2128,'Target identity changed')
   fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0];need(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','not genuine164')
   registry=read(NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reservations=[x.get('reserved_write_bytes',0) for x in registry.get('registered_future_requests',{}).values()];disk=os.statvfs(NATIVE);free=disk.f_bavail*disk.f_frsize;budget=nas_native_budget(free,reservations,native_control_bytes());reserved=budget['registered_foreign_write_reservations_bytes'];required=budget['required_SSD_bytes'];observe_nas_health()
   need(free>=required and disk.f_favail>=100000,'RESOURCE_HOLD_SHARED_SSD_ALL_PROJECT_RESERVATIONS')
   mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;cur=int(P('/sys/fs/cgroup/memory.current').read_text());maxval=P('/sys/fs/cgroup/memory.max').read_text().strip();need(mem>=64*GIB and (maxval=='max' or int(maxval)-cur>=GIB),'RESOURCE_HOLD_HOST_OR_CGROUP_RAM')
   pressure={line.split()[0]:{a.split('=')[0]:float(a.split('=')[1]) for a in line.split()[1:]} for line in P('/proc/pressure/io').read_text().splitlines()};active=[]
   ae=P('/root/data/dtc_main_20261023_v1/ae_fair_v1/control/qualification_ledger')
   pending_intents=set(ae.glob('*.INTENT.json'))
   for registered in registry.get('registered_future_requests',{}).values():
    consumed=registered.get('consumed',{})
    if not isinstance(consumed,dict):continue
    for record in consumed.values():
     if isinstance(record,dict) and not record.get('execution_receipt') and record.get('intent'):pending_intents.add(P(record['intent']))
   for f in sorted(pending_intents):
    if f.with_name(f.name.replace('.INTENT.','.DONE.')).exists():continue
    try:i=read(f)
    except FileNotFoundError as e:raise RuntimeError('RESOURCE_HOLD_FOREIGN_INTENT_UNREADABLE: '+str(f))from e
    out=P(i['output']);proof=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    try:p=read(proof)
    except FileNotFoundError:continue
    observed=_current_foreign_progress(out,p)
    if observed is None:continue
    active.append({'cohort':i['cohort'],**observed})
   # This COPY_ONLY task uses a conservative low-pressure window while science
   # is active; it never alters the scientific controller's IO warning policy.
   # User authorizes adaptive low-priority progress rather than a blanket IO HOLD.
   io_rate=adaptive_io_rate(30*MIB,pressure.get('full',{}).get('avg10',100))
   value={'observed_unix':time.time(),'SSD_free_bytes':free,'required_SSD_bytes':required,'registered_foreign_write_reservations_bytes':reserved,'unregistered_other_project_headroom_bytes':0,'NAS_only_Native_budget':budget,'task_controls_reserve_bytes':64*MIB,'host_MemAvailable_bytes':mem,'cgroup_current':cur,'host_IO_pressure':pressure,'adaptive_IO_max_read_bytes_sec':io_rate,'IO_policy':'V7_BLOCK_HEALTH_DISTINGUISHES_NAS_SELF_WAIT','physical_block_health':dict(_block_health),'active_AEFAIR':active,'Share_new_bytes':0,'all_policy_gates_pass':True};self.last=time.monotonic();self.last_value=value;self.samples.append(value);return value
def enable_nas_only():
 global Resources
 Resources=NASOnlyResources

source_archive_send_frozen_v10=source_archive_send
def source_archive_send(request,testing=False):
 return source_archive_send_frozen_v10(qualified_archive_request(request,testing),testing)

if __name__=='__main__':
 try:
  if sys.argv[1:] in [['source-synthetic']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=True)
  elif sys.argv[1:] in [['source-native']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=False)
  elif sys.argv[1]=='migrate-exact-approved':
    root_approval();need(P(sys.argv[2])==EXACT_MANIFEST,'exact manifest only');qualified_archive_request({'manifest':read(EXACT_MANIFEST),'skip':{}});enable_nas_only();emit(migrate(read(EXACT_MANIFEST)))
  elif sys.argv[1]=='verify':emit(verify_committed(P(sys.argv[2]),rehash='--full' in sys.argv[3:]))
  elif sys.argv[1]=='restore':
   bundle=P(sys.argv[2]);m=read(bundle/'SOURCE_MANIFEST.json');verify_committed(bundle);emit(restore_native(bundle/'tree',m,P(sys.argv[3])))
  else:raise RuntimeError('finite trace-copy operation required')
 except (RuntimeError,OSError,ValueError,KeyError) as error:print(json.dumps({'status':'HOLD_EXACT_ASSET_NO_SCIENTIFIC_ACTION','reason':str(error)}),file=sys.stderr);sys.exit(2)
