"""Guard-owned flock OFDs. Never LOCK_UN; unknown closure retains the guard."""
import os,pathlib,stat,fcntl,json,hashlib,subprocess,time,re
from activity_proof_v3 import process_identity,same_identity,need
ENV='SCOPED_LEASE_DESCRIPTOR_V6'
PRODUCTION_PATHS=('/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','/data/c16/locks/c16_gpu_campaign.lock')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def fd_lock(fd,pid,process=None,expected_mode='WRITE'):
 need(expected_mode in ['READ','WRITE'],'exact expected flock mode')
 base=pathlib.Path('/proc/self')if process is None else pathlib.Path('/proc',str(process))
 st=os.fstat(fd)if process is None else os.stat(base/'fd'/str(fd));text=(base/'fdinfo'/str(fd)).read_text()
 locks=[line.split()[2:]for line in text.splitlines()if line.startswith('lock:')]
 want=['FLOCK','ADVISORY',expected_mode,str(pid)]
 need(len(locks)==1 and locks[0][:4]==want,'FD must carry the guard-owned FLOCK OFD')
 dev=locks[0][4].split(':');need(len(dev)==3,'lock device/inode grammar')
 need(int(dev[0],16)==os.major(st.st_dev)and int(dev[1],16)==os.minor(st.st_dev)and int(dev[2])==st.st_ino,'lock FD device/inode mismatch')
 return dict(dev=st.st_dev,inode=st.st_ino,mode=st.st_mode,fdinfo=text,owner_pid=pid,lock_mode=expected_mode)
def path_identity(path):
 p=pathlib.Path(path);need(p.is_absolute()and '..'not in p.parts,'absolute exact lease path')
 for ancestor in [p,*p.parents]:need(not ancestor.is_symlink(),'lease symlink forbidden')
 st=p.stat();need(stat.S_ISREG(st.st_mode),'lease regular file required')
 return st

LOCAL_IO=PRODUCTION_PATHS[0]
CPU_SLOTS=tuple('/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_NAS_SHARED_CPU_POST_ROLE_'+str(i)+'.lock'for i in range(2))
CONTRACT_SCHEMA='ROOT_EXACT_NAS_GPU1_CPU2_LOCALIO_SHARED_V1'
G=2**30
def hash64(x):return type(x)is str and re.fullmatch('[0-9a-f]{64}',x)is not None
def read_contract(ref):
 p=pathlib.Path(ref['path']);need(p.is_absolute()and '..'not in p.parts,'absolute pinned contract path');need(type(ref.get('bytes'))is int and 0<ref['bytes']<=2**20 and hash64(ref.get('sha256')),'bounded pinned Root coactivity contract')
 for q in [p,*p.parents]:need(not q.is_symlink(),'contract symlink')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and a.st_size==ref['bytes'],'contract regular bounded file')
  raw=b''
  while len(raw)<=ref['bytes']:
   b=os.read(fd,min(65536,ref['bytes']+1-len(raw)))
   if not b:break
   raw+=b
  z=os.fstat(fd);key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  need(key(a)==key(z)and len(raw)==ref['bytes']and hashlib.sha256(raw).hexdigest()==ref['sha256'],'contract raw bytes SHA and stable same FD')
 finally:os.close(fd)
 return json.loads(raw)
def policy_modes(paths,bindings,shared_policy):
 paths=tuple(map(str,paths))
 if shared_policy is None:return ['WRITE']*len(paths)
 sp=shared_policy
 need(type(sp)is dict and bindings.get('io_coactivity')==sp and hash64(bindings.get('Root_sha256')),'explicit Root scope/coactivity binding')
 need(all(hash64(sp.get(k))for k in ['source_manifest_sha256','input_identity_sha256','code_manifest_sha256','data_sha256']),'source/input/execution pins')
 need(bindings.get('job_id')==sp.get('job_id')and type(sp['job_id'])is str,'exact descriptor job')
 need(type(sp.get('runtime_root'))is str and pathlib.Path(sp['runtime_root']).is_absolute(),'exact runtime')
 c=read_contract(sp['contract_ref'])
 need(c['schema']==CONTRACT_SCHEMA and c['status']=='ROOT_APPROVED_EXACT_NAS_PIPELINE'and c['NAS_only']is True,'Root approved NAS-only exact pipeline')
 need(c['max_GPU_roles']==1 and c['max_CPU_roles']==2 and c['physical_headroom_bytes']==32*G,'bounded GPU1 CPU2 physical reservation')
 roles=c['roles'];gpu=roles['GPU_CAPTURE'];slots=roles['CPU_POST']['slots']
 need(len(slots)==2 and [s['slot_index']for s in slots]==[0,1],'exact two CPU role slots')
 need(gpu['own_hard_bytes']==8*G and all(s['own_hard_bytes']==2*G for s in slots),'GPU8 CPU2+2 hard limits')
 allcfg=[gpu,*slots]
 for cfg in allcfg:
  need(hash64(cfg['source_manifest_sha256'])and type(cfg['job_bindings'])is dict,'contract source-only/job pins')
  need(cfg.get('state')in['ACTIVE','INACTIVE']and bool(cfg['job_bindings'])==(cfg['state']=='ACTIVE'),'role active or empty inactive exact inputs')
  need(type(cfg['runtime_roots_by_job'])is dict and set(cfg['runtime_roots_by_job'])==set(cfg['job_bindings']),'exact runtime roots by job')
  need(type(cfg['cpu_ids'])is list and cfg['cpu_ids']and len(set(cfg['cpu_ids']))==len(cfg['cpu_ids'])and all(type(v)is int and v>=0 for v in cfg['cpu_ids']),'exact CPU sets')
  need(all(hash64(v['input_identity_sha256'])for v in cfg['job_bindings'].values()),'contract independent exact input pins')
  need('execution_code_manifest_sha256'not in cfg and 'data_sha256'not in cfg and 'Root_scope_sha256'not in cfg,'no coactivity/execution hash cycle')
 need(slots[0]['cpu_ids']==[2]and slots[1]['cpu_ids']==[3],'CPU slots fixed separate single cores')
 need(all(not(set(a['cpu_ids'])&set(b['cpu_ids']))for i,a in enumerate(allcfg)for b in allcfg[i+1:]),'GPU/CPU CPUsets disjoint')
 need(all(not(set(a['job_bindings'])&set(b['job_bindings']))for i,a in enumerate(allcfg)for b in allcfg[i+1:]),'all GPU/CPU exact inputs pairwise disjoint')
 role=sp['role'];need(role in ['GPU_CAPTURE','CPU_POST'],'exact coactivity role')
 if role=='GPU_CAPTURE':
  need('slot_index'not in sp,'GPU has no CPU slot');cfg=gpu
  need(paths==PRODUCTION_PATHS,'GPU original canonical IO plus campaign paths')
  modes=['READ','WRITE']
 else:
  ix=sp['slot_index'];need(type(ix)is int and ix in [0,1],'CPU slot index')
  cfg=slots[ix];r=cfg['role_slot_ref']
  need(r['path']==CPU_SLOTS[ix]and paths==(CPU_SLOTS[ix],LOCAL_IO),'CPU chosen role EX then canonical IO SH')
  st=path_identity(r['path'])
  need((st.st_dev,st.st_ino,st.st_uid)==(r['dev'],r['inode'],r['uid'])and st.st_nlink==1,'Root pinned role slot exact namespace')
  modes=['WRITE','READ']
 need(cfg['state']=='ACTIVE'and sp['job_id']in cfg['runtime_roots_by_job'],'inactive role may not acquire')
 roots=cfg['runtime_roots_by_job'][sp['job_id']]
 need(set(roots)=={'native_runtime_root','remote_runtime_root'}and sp['runtime_root']in roots.values(),'exact role per-job runtime root')
 need(sp['source_manifest_sha256']==cfg['source_manifest_sha256']and sp['own_hard_bytes']==cfg['own_hard_bytes']and sp['cpu_ids']==cfg['cpu_ids'],'source/role/resource binding')
 need(sp['job_id']in cfg['job_bindings']and sp['input_identity_sha256']==cfg['job_bindings'][sp['job_id']]['input_identity_sha256'],'exact role input identity')
 need(all(p==LOCAL_IO or m=='WRITE'for p,m in zip(paths,modes)),'only canonical LOCAL_IO shared')
 return modes

class GuardLeases:
 def __init__(self,paths,bindings,shared_policy=None):
  self.paths=tuple(map(str,paths));self.modes=policy_modes(self.paths,bindings,shared_policy);self.fds=[];self.guard=process_identity(os.getpid());need(self.guard is not None,'guard identity')
  try:
   rows=[]
   for p,mode in zip(self.paths,self.modes):
    before=path_identity(p);fd=os.open(p,os.O_RDWR|os.O_CLOEXEC|os.O_NOFOLLOW);self.fds.append(fd);st=os.fstat(fd)
    need((st.st_dev,st.st_ino)==(before.st_dev,before.st_ino),'lease changed during open')
    fcntl.flock(fd,(fcntl.LOCK_SH if mode=='READ'else fcntl.LOCK_EX)|fcntl.LOCK_NB)
    r=fd_lock(fd,self.guard['pid'],expected_mode=mode);after=path_identity(p);need((r['dev'],r['inode'])==(after.st_dev,after.st_ino),'lease namespace drift')
    rows.append(dict(path=p,fd=fd,dev=r['dev'],inode=r['inode'],owner_pid=self.guard['pid'],lock_mode=mode))
   self.descriptor=dict(schema='GUARD_OWNED_SHARED_OFD_LEASES_V6',guard=self.guard,bindings=bindings,shared_policy=shared_policy,files=rows)
  except BaseException:
   for fd in self.fds:os.close(fd)
   self.fds=[];raise
 def environment(self):return {ENV:json.dumps(self.descriptor,separators=(',',':'))}
 def close_after_closed(self,owned):
  need(not owned(),'owned descendants not closed: retain guard/OFDs')
  need(same_identity(process_identity(os.getpid()),self.guard),'guard identity changed before close')
  for fd,mode in zip(self.fds,self.modes):fd_lock(fd,self.guard['pid'],expected_mode=mode)
  for fd in self.fds:os.close(fd)
  self.fds=[]
 def hold_unknown(self,receipt_path,error,owned):
  try:
   data=dict(schema='OWNED_CLOSURE_UNKNOWN_LEASE_HOLD_V6',status='HOLD_UNKNOWN_NOT_SUCCESS',guard=self.guard,leases=self.descriptor,error=repr(error),owned=owned(),unix=time.time())
   with pathlib.Path(receipt_path).open('x')as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
  finally:
   # No new spawn, no automatic unlock or success. Root must reconcile exact identities.
   while True:time.sleep(60)
def descriptor_hash():return digest(json.loads(os.environ[ENV]))
def adopt_worker(parent,bindings,paths=PRODUCTION_PATHS,shared_policy=None):
 desc=json.loads(os.environ.pop(ENV));need(desc['schema']=='GUARD_OWNED_SHARED_OFD_LEASES_V6','lease schema')
 need(same_identity(desc['guard'],parent)and same_identity(process_identity(os.getppid()),parent)and os.getppid()==parent['pid'],'lease guard identity/parent')
 need(desc['bindings']==bindings,'lease exact Root/job/worker/guard binding')
 need([r['path']for r in desc['files']]==list(paths),'fixed lease path set')
 need(desc.get('shared_policy')==shared_policy,'explicit descriptor policy')
 modes=policy_modes(paths,bindings,shared_policy)
 fds=[]
 for r,mode in zip(desc['files'],modes):
  need(r['lock_mode']==mode,'descriptor exact lock mode')
  fd=r['fd'];need(type(fd)is int and fd>=3 and fd not in fds,'distinct inherited FDs')
  st=path_identity(r['path']);actual=fd_lock(fd,parent['pid'],expected_mode=mode)
  need((actual['dev'],actual['inode'])==(r['dev'],r['inode'])==(st.st_dev,st.st_ino),'inherited lease FD/namespace')
  need(os.readlink('/proc/self/fd/'+str(fd))==r['path'],'inherited FD exact path')
  need((fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE)==os.O_RDWR,'lease access mode')
  fds.append(fd)
 return WorkerLeases(tuple(fds),desc)
class WorkerLeases:
 def __init__(self,fds,descriptor):self.fds=fds;self.descriptor=descriptor
 def install_child_inheritance(self):
  # All direct Python subprocess children inherit the same locked OFDs.
  old=subprocess.Popen;fds=self.fds
  class LeasePopen(old):
   def __init__(self,*args,**kwargs):
    kwargs['pass_fds']=tuple(sorted(set(kwargs.get('pass_fds',()))|set(fds)));kwargs['close_fds']=True
    super().__init__(*args,**kwargs)
  subprocess.Popen=LeasePopen
 def verify_capture(self,pid,proof):
  need(same_identity(process_identity(pid),proof)and proof['parent_pid']==os.getpid(),'capture identity/direct worker parent before FD proof')
  for r in self.descriptor['files']:
   info=fd_lock(r['fd'],self.descriptor['guard']['pid'],pid,expected_mode=r['lock_mode'])
   need((info['dev'],info['inode'])==(r['dev'],r['inode']),'capture lease object drift')
  need(same_identity(process_identity(pid),proof),'capture changed during FD proof')
 def close_copies(self):
  for fd in self.fds:os.close(fd)
  self.fds=()
