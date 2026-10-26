"""R5 explicit resource scopes; R4 generic Resources is unchanged and not subclassed.
Only typed read-only accounting or a single preallocated, owned readback slot.
"""
from pathlib import Path
import os,stat,json,hashlib,time,subprocess,threading,fcntl,contextlib,importlib.util,re,math
MIB=2**20;GIB=2**30;BASE='e2b1a814a201f7f5dd95c55c61a94f04069690dd18ecfabd89c9f88dc7ae19c7'
def need(x,msg):
 if not x:raise RuntimeError('R5_HOLD_'+msg)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def ident(st):return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_mode,st.st_uid,st.st_gid)
def no_links(path):
 p=Path(path).absolute();need('..'not in p.parts,'PATH_PARENT_TRAVERSAL')
 for q in [p,*p.parents]:
  if os.path.lexists(q):need(not q.is_symlink(),'PATH_SYMLINK')
 return p
DEADLINE_ENV='SM70_R5_STAGE_DEADLINE_MONOTONIC'
def inherited_deadline():
 value=os.environ.get(DEADLINE_ENV)
 if value is None:return float('inf')
 try:d=float(value)
 except ValueError:raise RuntimeError('R5_HOLD_INVALID_ABSOLUTE_STAGE_DEADLINE')
 need(math.isfinite(d)and d>0,'INVALID_ABSOLUTE_STAGE_DEADLINE');return d
def deadline_boundary():
 need(time.monotonic()<inherited_deadline(),'FINITE_STAGE_DEADLINE')
def raw(path,limit=128*MIB,deadline_enforced=True):
 if deadline_enforced:deadline_boundary()
 p=no_links(path);before=p.lstat();need(stat.S_ISREG(before.st_mode)and before.st_size<=limit,'METADATA_TYPE_OR_LIMIT')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb',buffering=0)as f:
  need(ident(os.fstat(f.fileno()))==ident(before),'METADATA_OPEN_IDENTITY');parts=[];count=0
  while True:
   if deadline_enforced:deadline_boundary()
   part=f.read(min(MIB,limit-count+1))
   if deadline_enforced:deadline_boundary()
   if not part:break
   count+=len(part);need(count<=limit,'METADATA_GROWTH_OR_FD_CHANGE');parts.append(part)
  b=b''.join(parts)
  if deadline_enforced:deadline_boundary()
  need(len(b)<=limit and ident(os.fstat(f.fileno()))==ident(before),'METADATA_GROWTH_OR_FD_CHANGE')
 need(ident(p.lstat())==ident(before),'METADATA_PATH_CHANGE')
 if deadline_enforced:deadline_boundary()
 return b
def load_ref(ref):
 b=raw(ref['path']);need(sha(b)==ref['sha256']and len(b)==ref['bytes'],'REF_BYTES_SHA');return json.loads(b)
def immutable_json(path,value,deadline_enforced=True):
 if not deadline_enforced:need(value.get('schema')=='R5_OWNED_PARTIAL_PRESERVED_V1'or value.get('preallocation_failure_preserved')is True or value.get('owned_partial_preserved')is True,'ONLY_FAILURE_EVIDENCE_CAN_BYPASS_DEADLINE')
 elif deadline_enforced:deadline_boundary()
 p=no_links(path);p.parent.mkdir(parents=True,exist_ok=True);b=canon(value)
 if p.exists():need(raw(p,deadline_enforced=deadline_enforced)==b,'IMMUTABLE_RECEIPT_COLLISION')
 else:
  fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'wb')as f:need(f.write(b)==len(b),'RECEIPT_SHORT_WRITE');f.flush();os.fsync(f.fileno())
 need(raw(p,deadline_enforced=deadline_enforced)==b,'CLOSED_RECEIPT_BYTES')
 return dict(path=str(p),sha256=sha(b),bytes=len(b))
def pid_identity(pid):
 try:
  a=(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
  return None if a[0]in['Z','X','x']else dict(pid=pid,start_ticks=int(a[19]))
 except (FileNotFoundError,ProcessLookupError):return None
def base_module():
 p=Path(__file__).with_name('resources.py');manifest=json.loads(raw(p.with_name('CODE_MANIFEST.json')))
 need(sha(raw(p))==manifest['files']['resources.py']['sha256'],'FROZEN_R4_RESOURCES_PIN')
 s=importlib.util.spec_from_file_location('R5_frozen_R4_resources',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class Scope:
 """No generic materialize/window method. Root authority is exact scope+code+policy."""
 def __init__(self,profile,policy_ref,approval_ref,code_id,kind,deadline=None):
  need(deadline is None or(math.isfinite(float(deadline))and float(deadline)>0),'INVALID_ABSOLUTE_STAGE_DEADLINE')
  self.deadline=min(inherited_deadline(),float('inf')if deadline is None else float(deadline));self.check_deadline()
  self.profile=dict(profile);self.testing=profile['execution_scope']=='QUALIFICATION'
  need(profile['execution_scope']in['PRODUCTION','QUALIFICATION'],'PROFILE_SCOPE')
  self.policy=load_ref(policy_ref);self.approval=load_ref(approval_ref);self.policy_ref=policy_ref;self.approval_ref=approval_ref
  q=self.policy;a=self.approval;self.kind=kind;self.code_id=code_id
  need(q['schema']=='SM70_EXPLICIT_RESOURCE_POLICY_R5'and q['kind']==kind and q['base_code_version_id']==BASE,'UNKNOWN_POLICY')
  need(kind in ['READ_ONLY_ZERO_NATIVE','EXACT_SINGLE_SLOT_READBACK','EXACT_SMALL_BUNDLE32'],'UNKNOWN_KIND')
  need(re.fullmatch('[A-Za-z0-9_-]{1,64}',q['scope_epoch'])and q['code_version_id']==code_id,'SCOPE_EPOCH_CODE')
  need(q['provider_sha256']==sha(raw(Path(__file__)))and q['native_floor_bytes']==5*GIB and q['own_native_cap_bytes']==256*MIB,'POLICY_PROVIDER_OR_CAP')
  need(q['native_window_cap_bytes']==64*MIB and q['slot_count']==1 and q['control_margin_bytes']==16*MIB,'POLICY_WINDOW_MARGIN')
  need(a['status']=='ROOT_APPROVED_R5_EXACT_RESOURCE_SCOPE'and a['policy_sha256']==policy_ref['sha256']and a['code_version_id']==code_id and a['scope_epoch']==q['scope_epoch']and a['kind']==kind,'ROOT_SCOPE_APPROVAL')
  need(a['scientific_starts_authorized']is False and a['generic_materialize_authorized']is False,'ROOT_AUTH_SCOPE')
  self.work=no_links(profile['native_work_root']);need(str(self.work)==q['native_work_root'],'OWN_WORK_ROOT')
  self.evidence=no_links(q['nas_evidence_root']);need(self.evidence.is_dir(),'PREPARED_NAS_EVIDENCE_ROOT')
  if not self.testing:
   need(self.evidence.resolve().is_relative_to(Path(profile['nas_mount_root']).resolve()),'EVIDENCE_NOT_NAS')
   expected=self.work/'authority'/('R5_'+q['scope_epoch']+'.json');need(Path(approval_ref['path'])==expected,'ROOT_AUTHORITY_PATH')
   st=expected.lstat();need(st.st_uid==0 and st.st_mode&0o022==0,'ROOT_AUTHORITY_PERMISSIONS')
   manifest=json.loads(raw(Path(__file__).with_name('CODE_MANIFEST.json')))
   need(manifest['code_version_id']==code_id==Path(__file__).parent.name,'NEW_CODE_ID_REQUIRED')
  self.base=base_module();self.platform=self.base.Resources(profile)
  self.bindings=load_ref(q['binding_set_ref']);need(self.bindings['schema']=='SM70_EXACT_BOUND_RESOURCE_BINDINGS_R5','BINDING_SET_SCHEMA')
  need(self.bindings['scope_epoch']==q['scope_epoch']and self.bindings['catalog_pins']==q['catalog_pins'],'BINDING_SET_EPOCH')
  self.bindings=self.bindings['bindings']
  if kind=='EXACT_SMALL_BUNDLE32':
   need(q.get('small_bundle_cap_bytes')==32*MIB and q.get('small_receipt_cap_bytes')==MIB and 1<=len(q.get('small_materializations',[]))<=3,'SMALL_EXACT_POLICY_CAP')
   rows=q['small_materializations'];need(len({x['destination']for x in rows})==len(rows),'SMALL_DESTINATIONS_UNIQUE')
   for row in rows:
    dest=Path(row['destination']);need(dest.is_absolute()and '..'not in dest.parts and dest.is_relative_to(self.work/'small_materializations_r5'/q['scope_epoch'])and Path(row['cwd']).is_absolute(),'SMALL_OWNED_PATH_SCOPE')
  self.last_full=0;self.latest=None;self.samples=[];self.counters=dict(read=0,write=0)
  self.started=time.monotonic();self.lock=threading.RLock();self.active_slot=None;self.operation_lock=None
  self.authority_identity=(ident(Path(policy_ref['path']).lstat()),ident(Path(approval_ref['path']).lstat()))
 def check_deadline(self):
  need(time.monotonic()<min(self.deadline,inherited_deadline()),'FINITE_STAGE_DEADLINE')
 def _authority(self):
  self.check_deadline()
  need(self.authority_identity==(ident(Path(self.policy_ref['path']).lstat()),ident(Path(self.approval_ref['path']).lstat())),'AUTHORITY_EPOCH_CHANGED')
 def observe(self,force=False):
  with self.lock:
   self._authority();q=self.profile
   if not force and self.latest and time.monotonic()-self.last_full<1:return self.latest
   if self.testing:
    s=json.loads(raw(q['qualification_resource_state']));need(s['host_ok']and s['mount_ok']and s['foreign_ok'],'QUALIFIED_OBSERVATION_HEALTH')
    registry=s['registry'];free=s['free_bytes'];inodes=s['free_inodes'];ram=s['mem_available'];cg=s['cgroup_available'];rate=s['rate'];active=s.get('active_foreign',[])
    need(s.get('registry_epoch_before','same')==s.get('registry_epoch_after','same'),'FOREIGN_EPOCH_RACE')
   else:
    need(os.uname().nodename==q['expected_host']and os.readlink('/proc/self/ns/mnt')==q['expected_mount_namespace']and Path('/root/data').stat().st_dev==q['native_device'],'TARGET_IDENTITY')
    fs=json.loads(subprocess.check_output(['/usr/bin/findmnt','-J','-T',q['nas_mount_root']],text=True))['filesystems'][0]
    need(fs['source']==q['nas_endpoint']and fs['fstype']=='fuse.sshfs','TRUE164')
    before=raw(q['native_registry']);registry,reserved_original,active=self.platform._platform();after=raw(q['native_registry'])
    need(before==after and json.loads(before)==registry,'FOREIGN_EPOCH_RACE')
    st=os.statvfs('/root/data');free=st.f_bavail*st.f_frsize;inodes=st.f_favail
    ram=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
    current=int(Path('/sys/fs/cgroup/memory.current').read_text());maximum=Path('/sys/fs/cgroup/memory.max').read_text().strip();cg=2**63 if maximum=='max'else int(maximum)-current
    rate=self.base.adaptive_io_rate(q['maximum_io_bytes_sec'])
   records=registry.get('registered_future_requests',{});need(isinstance(records,dict),'FOREIGN_REQUESTS_TYPE')
   for record in records.values():need(type(record.get('reserved_write_bytes',0))is int and record.get('reserved_write_bytes',0)>=0,'FOREIGN_RESERVED_INVALID')
   reserved=sum(x.get('reserved_write_bytes',0)for x in records.values())
   need(ram>=64*GIB and cg>=GIB and inodes>=100000,'RAM_OR_INODES')
   own=self.base.allocated_tree(self.work)
   value=dict(observed_unix=time.time(),free=free,free_inodes=inodes,host_MemAvailable_bytes=ram,cgroup_available=cg,rate=rate,own_allocated_bytes=own,registered_foreign_reserved_bytes=reserved,all_foreign_requests=records,foreign_registry_sha256=sha(canon(registry)),active_foreign=active,foreign_future_ceilings_committed_by_this_scope=False,source_keep=True)
   self.latest=value;self.last_full=time.monotonic();self.samples.append(value);self.samples=self.samples[-128:]
   immutable_json(self.evidence/('resource_'+str(time.time_ns())+'.json'),value)
   self.check_deadline();return value
 def check_block(self,pending_native=0):
  self._authority();no_links(self.work);need(type(pending_native)is int and pending_native>=0,'PENDING_WRITE_BOUND')
  v=self.observe(False)
  if self.testing:s=json.loads(raw(self.profile['qualification_resource_state']));free=s['free_bytes'];own=s.get('own_allocated_override',self.base.allocated_tree(self.work))
  else:
   s=os.statvfs('/root/data');free=s.f_bavail*s.f_frsize;own=self.base.allocated_tree(self.work)
  need(free>=5*GIB+pending_native,'ACTUAL_FLOOR_AND_PENDING_NATIVE')
  need(own+pending_native<=256*MIB,'OWN_NATIVE256MIB')
  self.check_deadline();return dict(v,free=free,own_allocated_bytes=own,required_free=5*GIB+pending_native,scope_kind=self.kind)
 def account(self,n,direction):
  self.check_deadline();need(direction in self.counters and type(n)is int and n>=0,'IO_COUNTER')
  self.counters[direction]+=n;v=self.check_block(0 if self.kind=='READ_ONLY_ZERO_NATIVE'else 16*MIB);rate=v['rate'];need(rate>0,'IO_RATE')
  delay=sum(self.counters.values())/rate-(time.monotonic()-self.started)
  if delay>0:time.sleep(min(delay,max(0,min(self.deadline,inherited_deadline())-time.monotonic())))
  self.check_deadline()
 def check(self,force=False):
  # Public readonly accounting is explicit. This object cannot authorize materialization.
  need(self.kind=='READ_ONLY_ZERO_NATIVE','GENERIC_RESOURCE_API_FORBIDDEN')
  if force:self.observe(True)
  return self.check_block(0)
 def binding(self,binding,context):
  need(self.kind=='EXACT_SINGLE_SLOT_READBACK','READONLY_CANNOT_OPEN_SLOT')
  h=context['sha256'];need(h in self.bindings and self.bindings[h]==dict(binding_id=binding['binding_id'],size=binding['size'],context=context),'EXACT_BINDING_SCOPE')
  need(self.policy['allowed_operation']=='SM70_EXACT_BOUND_RESTORE_WINDOW_ONLY','OPERATION_KIND')
 @contextlib.contextmanager
 def operation(self):
  need(self.kind in['EXACT_SINGLE_SLOT_READBACK','EXACT_SMALL_BUNDLE32']and self.operation_lock is None,'SINGLE_OPERATION')
  self.check_block(16*MIB);self.work.mkdir(parents=True,exist_ok=True)
  f=self.work/'.R5_SINGLE_SLOT.lock';no_links(f);fd=os.open(f,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
  try:
   st=os.fstat(fd);need(stat.S_ISREG(st.st_mode)and(self.testing or(st.st_uid==os.geteuid()and st.st_mode&0o022==0)),'LOCK_OWNER_PERMISSIONS')
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);self.operation_lock=fd
   # Respect the old R4 operation boundary as well; never interrupt another owner.
   old=os.open(self.work/'.NATIVE_BOUND_OPERATION.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
   try:
    st=os.fstat(old);need(stat.S_ISREG(st.st_mode)and(self.testing or(st.st_uid==os.geteuid()and st.st_mode&0o022==0)),'OLD_OPERATION_LOCK_PERMISSIONS')
    fcntl.flock(old,fcntl.LOCK_EX|fcntl.LOCK_NB)
    yield self
   finally:fcntl.flock(old,fcntl.LOCK_UN);os.close(old)
  finally:
   try:
    if self.active_slot is not None:self.active_slot.preserve('operation ended before exact owned cleanup')
   finally:
    self.operation_lock=None;fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 def slot(self,binding,context,offset,length):
  self.binding(binding,context);need(self.operation_lock is not None and self.active_slot is None,'ONE_CONCURRENT_SLOT')
  need(type(offset)is int and type(length)is int and 0<length<=64*MIB and 0<=offset<context['size']and offset+length<=context['size'],'SLOT_LENGTH_OFFSET')
  return Slot(self,context,offset,length)

class Slot:
 def __init__(self,scope,context,offset,length):
  self.scope=scope;self.context=context;self.offset=offset;self.length=length;self.position=0;self.fd=None;self.closed=None
  scope.check_block(length+16*MIB)
  root=scope.work/'bounded_readback_r5'/scope.policy['scope_epoch'];no_links(root)
  marker=scope.evidence/'EPOCH_NATIVE_ROOT.json'
  if root.exists():
   need(marker.is_file(),'EXISTING_EPOCH_ROOT_WITHOUT_OWNERSHIP')
   saved=load_ref(dict(path=str(marker),sha256=sha(raw(marker)),bytes=marker.stat().st_size))
   st=root.lstat();need(saved==dict(scope_epoch=scope.policy['scope_epoch'],policy_sha256=scope.policy_ref['sha256'],path=str(root),identity=[st.st_dev,st.st_ino,st.st_mode,st.st_uid]),'EPOCH_ROOT_IDENTITY')
  else:
   root.mkdir(mode=0o700,parents=True,exist_ok=False);st=root.lstat()
   immutable_json(marker,dict(scope_epoch=scope.policy['scope_epoch'],policy_sha256=scope.policy_ref['sha256'],path=str(root),identity=[st.st_dev,st.st_ino,st.st_mode,st.st_uid]))
  need(stat.S_ISDIR(st.st_mode)and(scope.testing or(st.st_uid==os.geteuid()and st.st_mode&0o022==0)),'EPOCH_DIRECTORY_PERMISSIONS')
  self.root=root;self.root_identity=(st.st_dev,st.st_ino,st.st_mode,st.st_uid)
  self.path=root/(context['sha256']+'_'+str(offset)+'.slot')
  need(not os.path.lexists(self.path),'EXISTING_SLOT_REQUIRES_EXACT_RECOVERY')
  self.tag=context['sha256']+'_'+str(offset)+'_'+str(time.time_ns())
  self.owner=dict(schema='R5_OWNED_NATIVE_SLOT_V1',scope_epoch=scope.policy['scope_epoch'],policy_sha256=scope.policy_ref['sha256'],code_version_id=scope.code_id,context=context,offset=offset,capacity=length,path=str(self.path),owner=pid_identity(os.getpid()),preexisting_path=False,source_KEEP=True)
  immutable_json(scope.evidence/(self.tag+'.INTENT.json'),self.owner)
  fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_RDWR|os.O_NOFOLLOW,0o600);self.fd=fd
  try:
   if scope.testing:
    os.ftruncate(fd,length);preallocation='QUALIFICATION_LOGICAL_ONLY_NOT_NATIVE_PHYSICAL_PROOF'
   else:
    fs=json.loads(subprocess.check_output(['/usr/bin/findmnt','-J','-T',str(root)],text=True))['filesystems'][0]
    need(fs['fstype']=='ext4'and os.fstat(fd).st_dev==scope.profile['native_device'],'EXT4_NATIVE_SLOT_REQUIRED')
    os.posix_fallocate(fd,0,length);need(os.fstat(fd).st_blocks*512>=length,'PHYSICAL_PREALLOCATION_REQUIRED');preallocation='POSIX_FALLOCATE_CLOSED_NATIVE_EXT4'
   os.fsync(fd);self.created=ident(os.fstat(fd));need(self.created[2]==length,'PREALLOCATED_CAPACITY')
   self.owner.update(created_identity=list(self.created),preallocation=preallocation)
   immutable_json(scope.evidence/(self.tag+'.CREATED.json'),self.owner)
   scope.active_slot=self;scope.check_block(16*MIB)
  except BaseException:
   failure=dict(self.owner,allocation_failed_identity=list(ident(os.fstat(fd))),preallocation_failure_preserved=True)
   immutable_json(scope.evidence/(self.tag+'.ALLOCATION_FAILED.json'),failure,deadline_enforced=False)
   os.close(fd);self.fd=None
   # Retain file plus exact created FD identity on uncertain allocation failure.
   raise
 def write(self,data):
  need(self.fd is not None and self.closed is None and 0<len(data)<=MIB and self.position+len(data)<=self.length,'SLOT_BOUNDED_WRITE')
  self.scope.check_block(16*MIB);no_links(self.path);st=self.root.lstat();need((st.st_dev,st.st_ino,st.st_mode,st.st_uid)==self.root_identity,'SLOT_ROOT_CHANGED');now=os.fstat(self.fd);path=self.path.lstat()
  need(now.st_nlink==path.st_nlink==1,'SLOT_HARDLINK')
  need((now.st_dev,now.st_ino)==self.created[:2]==(path.st_dev,path.st_ino)and now.st_size==self.length and path.st_size==self.length,'SLOT_FD_PATH_OR_SIZE')
  n=os.pwrite(self.fd,data,self.position);need(n==len(data),'SLOT_SHORT_WRITE');self.position+=n;self.scope.account(n,'write')
 def finish(self,expected_sha,readback_consume=None):
  need(self.fd is not None and self.position==self.length,'SLOT_INCOMPLETE')
  no_links(self.path);need(os.fstat(self.fd).st_nlink==1,'SLOT_HARDLINK');os.fsync(self.fd);closed=ident(os.fstat(self.fd));os.close(self.fd);self.fd=None
  need(ident(self.path.lstat())==closed,'CLOSED_SLOT_PATH')
  fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256();count=0
  with os.fdopen(fd,'rb',buffering=0)as f:
   need(ident(os.fstat(f.fileno()))==closed,'REOPEN_SLOT_IDENTITY')
   while True:
    self.scope.check_block(16*MIB);part=f.read(MIB)
    if not part:break
    count+=len(part);h.update(part);self.scope.account(len(part),'read')
    if readback_consume:readback_consume(part)
   need(ident(os.fstat(f.fileno()))==closed,'REOPEN_SLOT_FD_CHANGED')
  need(ident(self.path.lstat())==closed and count==self.length and h.hexdigest()==expected_sha,'CLOSED_SLOT_WHOLE_SHA')
  self.closed=closed
  proof=dict(schema='R5_SLOT_CLOSED_NATIVE_REOPEN_V1',owner=self.owner,bytes=count,source_sha256=expected_sha,closed_sha256=h.hexdigest(),native_closed_identity=list(closed),Native_write_and_closed_reopen_FD_path_stable=True,qualification_only=self.scope.testing,source_KEEP=True)
  self.proof_ref=immutable_json(self.scope.evidence/(self.tag+'.CLOSED.json'),proof);return proof
 def cleanup(self):
  no_links(self.path);need(self.fd is None and self.closed is not None and ident(self.path.lstat())==self.closed and self.path.lstat().st_nlink==1,'EXACT_CLOSED_CLEANUP_IDENTITY')
  proof=load_ref(self.proof_ref);need(proof['owner']==self.owner and proof['native_closed_identity']==list(self.closed),'DURABLE_PROOF_BEFORE_CLEANUP')
  self.scope.check_block(16*MIB);self.path.unlink();self.scope.active_slot=None
  return immutable_json(self.scope.evidence/(self.tag+'.CLEANUP.json'),dict(schema='R5_EXACT_OWNED_SLOT_CLEANUP_V1',closed_proof_ref=self.proof_ref,released_bytes=self.length,source_payload_released_bytes=0,path_absent=not os.path.lexists(self.path)))
 def preserve(self,reason):
  if self.fd is not None:os.fsync(self.fd);os.close(self.fd);self.fd=None
  record=dict(schema='R5_OWNED_PARTIAL_PRESERVED_V1',owner=self.owner,last_position=self.position,current_identity=list(ident(self.path.lstat())),reason=str(reason),source_KEEP=True)
  immutable_json(self.scope.evidence/(self.tag+'.PRESERVED.json'),record,deadline_enforced=False);self.scope.active_slot=None

def recover_owned_partial(scope,preserved_ref,recovery_ref):
 """Future explicit Root recovery only; never discovers or deletes caches."""
 need(scope.kind=='EXACT_SINGLE_SLOT_READBACK'and scope.operation_lock is not None and scope.active_slot is None,'RECOVERY_OPERATION_LEASE')
 record=load_ref(preserved_ref);approval=load_ref(recovery_ref);owner=record['owner']
 need(record['schema']=='R5_OWNED_PARTIAL_PRESERVED_V1'and owner['schema']=='R5_OWNED_NATIVE_SLOT_V1','RECOVERY_SCHEMA')
 need(approval['status']=='ROOT_APPROVED_R5_OWNED_PARTIAL_CLEANUP'and approval['preserved_sha256']==preserved_ref['sha256']and approval['scope_epoch']==scope.policy['scope_epoch'],'RECOVERY_ROOT_EXACT_GRANT')
 need(approval['no_recent_use_or_reuse']is True and approval['source_payload_deletion_authorized']is False,'RECOVERY_REUSE_OR_SOURCE')
 if not scope.testing:
  p=scope.work/'authority'/('R5_CLEANUP_'+scope.policy['scope_epoch']+'.json');need(Path(recovery_ref['path'])==p,'RECOVERY_AUTHORITY_PATH')
  st=p.lstat();need(st.st_uid==0 and st.st_mode&0o022==0,'RECOVERY_AUTHORITY_PERMISSIONS')
 need(owner['scope_epoch']==scope.policy['scope_epoch']and owner['policy_sha256']==scope.policy_ref['sha256']and owner['code_version_id']==scope.code_id and owner['preexisting_path']is False,'RECOVERY_OWNER_SCOPE')
 # A currently reused PID also HOLDs; this limited recovery does not infer quiescence.
 need(pid_identity(owner['owner']['pid'])is None,'RECOVERY_OWNER_PID_STILL_EXISTS')
 ctx=owner['context'];need(ctx['sha256']in scope.bindings and scope.bindings[ctx['sha256']]['context']==ctx,'RECOVERY_BINDING')
 expected=scope.work/'bounded_readback_r5'/scope.policy['scope_epoch']/(ctx['sha256']+'_'+str(owner['offset'])+'.slot')
 p=no_links(owner['path']);need(p==expected,'RECOVERY_PATH_SCOPE')
 now=ident(p.lstat());need(list(now)==record['current_identity']and stat.S_ISREG(now[5])and now[2]==owner['capacity']and 0<now[2]<=64*MIB and p.lstat().st_nlink==1,'RECOVERY_CURRENT_IDENTITY')
 created=owner['created_identity'];need(now[:3]==tuple(created[:3]),'RECOVERY_CREATED_INODE')
 scope.check_block(16*MIB);need(ident(p.lstat())==now,'RECOVERY_PREUNLINK_IDENTITY');p.unlink()
 return immutable_json(scope.evidence/('RECOVERY_'+preserved_ref['sha256']+'.json'),dict(schema='R5_EXACT_PARTIAL_CLEANUP_V1',preserved_ref=preserved_ref,recovery_ref=recovery_ref,path=str(p),released_bytes=now[2],source_payload_released_bytes=0))
