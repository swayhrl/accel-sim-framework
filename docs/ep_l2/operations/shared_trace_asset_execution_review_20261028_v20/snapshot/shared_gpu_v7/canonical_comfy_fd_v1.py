"""Independent canonical Comfy flock FD; no state/token/API mutation, no LOCK_UN."""
import os,pathlib,stat,fcntl,json,hashlib,time,subprocess,urllib.request
ENV='ROOT_CANONICAL_COMFY_SHARED_FD_V1'
CANON='/home/huangrulin/workspace/image-lab/cache/gpu-validation.lock'
MAINT='/home/huangrulin/workspace/image-lab/cache/service-maintenance.json'
SOURCE='/home/huangrulin/workspace/image-lab/scripts/resource_coordination.py'
SOURCE_SHA='3639e0f2997c3474e551ed9cc537c097bb4fcfbf9b27ff6e97ddcb5a7a531ae8'
def need(v,m):
 if not v:raise RuntimeError(m)
def owner(pid):
 q=pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
 try:boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 except OSError as e:raise RuntimeError('SHARED_BOOT_METADATA_UNREADABLE_HOLD')from e
 return [int(pid),q[19],boot]
def regular(p):
 p=pathlib.Path(p)
 for a in[p,*p.parents]:need(not a.is_symlink(),'SHARED_CANONICAL_NO_SYMLINK')
 s=p.stat();need(stat.S_ISREG(s.st_mode),'SHARED_CANONICAL_REGULAR');return s
def proof(fd,guard_pid,process=None):
 base=pathlib.Path('/proc/self')if process is None else pathlib.Path('/proc',str(process))
 s=os.fstat(fd)if process is None else os.stat(base/'fd'/str(fd));text=(base/'fdinfo'/str(fd)).read_text()
 rows=[r.split()[2:]for r in text.splitlines()if r.startswith('lock:')]
 need(len(rows)==1 and rows[0][:4]==['FLOCK','ADVISORY','WRITE',str(guard_pid)],'SHARED_FD_REAL_FLOCK_OWNER')
 key=rows[0][4].split(':');need(len(key)==3 and [int(key[0],16),int(key[1],16),int(key[2])]==[os.major(s.st_dev),os.minor(s.st_dev),s.st_ino],'SHARED_FD_DEVICE_INODE')
 return dict(fd=fd,dev=s.st_dev,inode=s.st_ino,owner_pid=guard_pid)
def maintenance_requested(path):
 p=pathlib.Path(path)
 if not p.exists():return False
 regular(p)
 with p.open('rb')as f:
  a=os.fstat(f.fileno());need(a.st_size<=65536,'BOUNDED_MAINTENANCE_STATUS');raw=f.read(65537);z=os.fstat(f.fileno())
 need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns)and len(raw)==a.st_size,'MAINTENANCE_SAMEFD')
 # Only status is used; do not persist/print/reuse lease_id or advisory tokens.
 return json.loads(raw).get('status')in ['REQUESTED','ACTIVE']
def queue_counts(url):
 need(url=='http://127.0.0.1:8188/queue','EXACT_EXISTING_COMFY_QUEUE_ENDPOINT')
 op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 with op.open(urllib.request.Request(url,method='GET'),timeout=3)as f:
  need(f.status==200,'COMFY_QUEUE_HTTP_STATUS');b=f.read(2*2**20+1)
 need(len(b)<=2*2**20,'COMFY_QUEUE_BOUNDED_RESPONSE');q=json.loads(b)
 need(type(q.get('queue_running'))is list and type(q.get('queue_pending'))is list,'EXISTING_COMFY_QUEUE_SCHEMA')
 return dict(running=len(q['queue_running']),pending=len(q['queue_pending']),unix=time.time(),response_sha256=hashlib.sha256(b).hexdigest(),response_bytes=len(b))
def small_json(p):
 regular(p)
 with pathlib.Path(p).open('rb')as f:
  a=os.fstat(f.fileno());need(a.st_size<=2*2**20,'BOUNDED_SC_CONTROL_METADATA');b=f.read(2*2**20+1);z=os.fstat(f.fileno())
 need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and len(b)==a.st_size,'SC_CONTROL_SAMEFD')
 return json.loads(b),hashlib.sha256(b).hexdigest()
def sc_positive_closed(a):
 r=a['SC_positive_closure'];root=pathlib.Path(r['remote_run_root'])
 try:
  scope,scope_sha=small_json(root/'ROOT_SCOPE.raw.json')
  need(scope_sha==r['scope_sha256']and scope['code_manifest_sha256']==r['code_manifest_sha256']and scope['run_id']==r['run_id'],'EXACT_ROOT_SC_SCOPE_CODE_RUN')
  need(scope['schema']==r['scope_schema']and scope['status']=='ROOT_APPROVED_CPU_ONLY'and scope['remote_boot_id']==a['remote_boot_id'],'SC_SCOPE_ROLE_BOOT')
  need(root==pathlib.Path(scope['remote_runtime_root'])/'runs'/scope['run_id'],'EXACT_SC_RUN_ROOT')
  release,rh=small_json(root/'NATIVE_RELEASED.json')
  if release.get('status')!='REMOTE_OWNED_CLOSED_ACKED_ASSET_LOCKS_RELEASED'or release.get('remote_returncode')!=0:return False
  z,zh=small_json(root/'REMOTE_CLOSED_PROPOSAL.json')
  if z.get('status')!='ALL_REMAINING_SELECTED_CLOSED'or z.get('error')is not None:return False
  need(z['owned_descendants']==[]and set(z['closed_refs'])==set(scope['selected']),'SC_POSITIVE_ALL_SELECTED_CLOSED')
  obs,oh=small_json(root/'REMOTE_CLOSURE_OBSERVATION.json');ack,ah=small_json(root/'NATIVE_CLEANUP_ACK.json');used,uh=small_json(root/'REMOTE_ACK_CONSUMED.json');start,sh=small_json(root/'REMOTE_START.json');keeper,kh=small_json(root/'NATIVE_KEEPER.json')
  need(all(v['scope_sha256']==scope_sha for v in [release,z,obs,ack,used,start]),'SC_ALL_CONTROL_SCOPE')
  need(obs['schema']=='SC_REMOTE_POST61_CLOSURE_OBSERVATION_V1','SC_OBSERVATION_SCHEMA')
  need(obs['proposal_sha256']==zh and obs['owned_closed']is True and obs['service_members']==[start['owner'][0]],'SC_INDEPENDENT_OBSERVATION')
  need(ack['proposal_sha256']==zh and ack['observation_sha256']==oh and used['ACK_sha256']==ah,'SC_RAW_ACK_CHAIN')
  need(z['owner']==obs['owner']==used['owner']==start['owner']and release['owner']==keeper['owner'],'SC_EXACT_OWNERS')
  try:live=owner(start['owner'][0])
  except(FileNotFoundError,ProcessLookupError):live=None
  if live is not None:
   need(live[1]==start['owner'][1],'SC_CLOSED_PID_REUSED_HOLD');return False
  cg=pathlib.Path(start['cgroup']);need(cg.is_relative_to(pathlib.Path('/sys/fs/cgroup'))and str(cg).endswith('/sc-post59-'+r['run_id']+'.service'),'SC_EXACT_CLOSED_CGROUP')
  if cg.exists():
   ev=dict(l.split()for l in(cg/'cgroup.events').read_text().splitlines());need(ev.get('populated')in ['0','1'],'SC_CGROUP_STATE')
   if ev['populated']=='1':return False
  return True
 except FileNotFoundError:return False

class Guard:
 def __init__(self,spec,bindings):
  self.spec=spec;self.bindings=bindings;self.fd=None;self.held=False;self.guard=owner(os.getpid())
 def try_acquire(self):
  self.queue_before=queue_counts(self.spec['queue_url'])
  if self.queue_before['running']or self.queue_before['pending']:return False
  p=pathlib.Path(self.spec['path']);s=regular(p)
  need((s.st_dev,s.st_ino,s.st_uid)==(self.spec['dev'],self.spec['inode'],self.spec['uid']),'SHARED_CANONICAL_PATH_IDENTITY')
  fd=os.open(p,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:
   z=os.fstat(fd);need((z.st_dev,z.st_ino)==(s.st_dev,s.st_ino),'SHARED_OPEN_SAME_FILE')
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:os.close(fd);return False
   if maintenance_requested(self.spec['maintenance_path']):os.close(fd);return False
   self.queue_after=queue_counts(self.spec['queue_url'])
   if self.queue_after['running']or self.queue_after['pending']:os.close(fd);return False
   actual=proof(fd,self.guard[0]);q=p.stat();need((q.st_dev,q.st_ino)==(actual['dev'],actual['inode']),'SHARED_POSTLOCK_NAMESPACE')
   self.fd=fd;self.held=True
   self.descriptor=dict(schema='ROOT_CANONICAL_COMFY_OFD_V1',guard=self.guard,bindings=self.bindings,path=str(p),fd=fd,dev=actual['dev'],inode=actual['inode'])
   return True
  except BaseException:
   try:os.close(fd)
   except OSError:pass
   raise
 def environment(self):
  need(self.held,'SHARED_LEASE_NOT_HELD');return {ENV:json.dumps(self.descriptor,separators=(',',':'))}
 def close_after_closed(self,children):
  need(not children(),'SHARED_RELEASE_REQUIRES_OWNED_CLOSED')
  if self.fd is not None:
   r=proof(self.fd,self.guard[0]);need((r['dev'],r['inode'])==(self.descriptor['dev'],self.descriptor['inode']),'SHARED_CLOSE_SAME_OFD')
   os.close(self.fd);self.fd=None
  self.held=False
def production_guard(a,bindings):
 spec=a['canonical_comfy_lock']
 need(spec['path']==CANON and spec['maintenance_path']==MAINT and spec['source_path']==SOURCE and spec['source_sha256']==SOURCE_SHA,'EXACT_EXISTING_COMFY_PROTOCOL')
 regular(SOURCE)
 need(hashlib.sha256(pathlib.Path(SOURCE).read_bytes()).hexdigest()==SOURCE_SHA,'EXISTING_COMFY_PROTOCOL_CHANGED')
 return Guard(spec,bindings)
def adopt(desc,bindings):
 need(desc['schema']=='ROOT_CANONICAL_COMFY_OFD_V1'and desc['path']==CANON and desc['bindings']==bindings,'SHARED_INHERITED_SCOPE')
 need(desc['guard']==owner(desc['guard'][0])and os.getppid()==desc['guard'][0],'SHARED_DIRECT_GUARD_PARENT')
 r=proof(desc['fd'],desc['guard'][0]);s=regular(desc['path'])
 need((r['dev'],r['inode'])==(desc['dev'],desc['inode'])==(s.st_dev,s.st_ino),'SHARED_INHERITED_REAL_FD')
 return Inherited(desc)
class Inherited:
 def __init__(self,desc):self.descriptor=desc;self.fd=desc['fd']
 def install_child_inheritance(self):
  # Original GuardLeases' two-FD wrapper remains intact; compose a third FD.
  os.set_inheritable(self.fd,True);old=subprocess.Popen;fd=self.fd
  class SharedPopen(old):
   def __init__(self,*args,**kwargs):
    kwargs['pass_fds']=tuple(sorted(set(kwargs.get('pass_fds',()))|{fd}));kwargs['close_fds']=True
    super().__init__(*args,**kwargs)
  subprocess.Popen=SharedPopen
def verify_remote(desc,bindings,expected_guard):
 need(desc['bindings']==bindings and desc['guard'][:2]==list(expected_guard[:2]),'SHARED_OBSERVATION_OWNER_SCOPE')
 need(desc['guard']==owner(desc['guard'][0]),'SHARED_OBSERVATION_LIVE_OWNER')
 r=proof(desc['fd'],desc['guard'][0],desc['guard'][0]);s=regular(CANON)
 need((r['dev'],r['inode'])==(s.st_dev,s.st_ino)==(desc['dev'],desc['inode']),'SHARED_OBSERVED_CANONICAL_FD')
 return True
def blocker_active(a):
 if time.time()<a['Root_GPU_not_before_unix']:return True
 if not sc_positive_closed(a):return True
 p=a.get('SC_CPU_ONLY_blocker')
 if p is None:return False
 need(p['boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'SC_CPU_ONLY_BOOT')
 try:q=owner(p['pid'])
 except(FileNotFoundError,ProcessLookupError):q=None
 if q is not None:need(q[1]==p['start_ticks'],'SC_CPU_ONLY_PID_IDENTITY_CHANGED');return True
 cg=pathlib.Path(p['cgroup'])
 need(cg.is_relative_to(pathlib.Path('/sys/fs/cgroup'))and '..'not in cg.parts,'SC_CPU_ONLY_EXACT_CGROUP')
 if cg.exists():
  ev=dict(l.split()for l in(cg/'cgroup.events').read_text().splitlines());need(ev.get('populated')in ['0','1'],'SC_CPU_ONLY_CGROUP_STATE')
  return ev['populated']=='1'
 return False
