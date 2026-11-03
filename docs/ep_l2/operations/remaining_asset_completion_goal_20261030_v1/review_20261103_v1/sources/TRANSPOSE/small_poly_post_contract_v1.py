"""Exact two-role CPU6/7 NAS-only contract and inherited role lease; no GPU locks."""
from pathlib import Path
import os,json,stat,hashlib,fcntl,time
NB=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ST=Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2')
G=2**30
def need(v,m):
 if not v:raise RuntimeError(m)
def localpath(p):
 p=Path(p);need(p.is_absolute()and '..'not in p.parts,'ABSOLUTE_NAS_PATH')
 for b in [NB,ST]:
  if p.is_relative_to(b):return (NB if Path(__file__).is_relative_to(NB)else ST)/p.relative_to(b)
 raise RuntimeError('ONLY_EXACT_TWO_NAS_ALIASES')
def pinned(r):
 p=localpath(r['path']);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<a.st_size==r['bytes']<=4*2**20,'EXACT_BOUNDED_META')
  raw=b''
  while len(raw)<=r['bytes']:
   x=os.read(fd,min(65536,r['bytes']+1-len(raw)))
   if not x:break
   raw+=x
  z=os.fstat(fd);key=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
  need(key(a)==key(z)and len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'SAMEFD_RAW_META_SHA')
 finally:os.close(fd)
 return json.loads(raw)
def check(a,mf,data):
 c=pinned(a['Root_two_role_contract_ref'])
 need(c['schema']=='ROOT_SDK429_REPEAT2_EXACT_CPU6_CPU7_HARD2_TWO_ROLE_CONTRACT_V1'and c['status']=='ROOT_APPROVED_EXACT_SDK429_REPEAT2_CPU_POST_TWO_ROLES','ROOT_EXACT_TWO_ROLE_CONTRACT')
 need(c['own_total_hard_bytes']==4*G and c['existing_MC_hard_reserved_bytes']==4*G and c['foreign_peer_reserved_bytes']==28*G and c['physical_floor_bytes']==16*G and c['total_full_remaining_required_bytes']==52*G,'EXPLICIT52G_NOT_FUTURE_QUOTA')
 need(set(c['roles'])=={'cpu6','cpu7'},'EXACT_TWO_CPU_ROLES')
 expected={'cpu6':{'SDK429_ALIGNEDTYPES_ORIGINAL50MB_TYPES12_REPEAT2_V1'},'cpu7':{'SDK429_TRANSPOSE_ORIGINAL1024_OUTER2_INNER2_ALL8_V1'}}
 alljobs=set()
 for role,cpu in [('cpu6',6),('cpu7',7)]:
  r=c['roles'][role];need(r['cpu_ids']==[cpu]and r['hard_bytes']==2*G and r['max_cpu_percent']==100,'ROLE_FIXED_CPU_HARD2')
  need(set(r['jobs'])==expected[role] and not(alljobs&set(r['jobs'])),'DISJOINT_EXACT_ROLE_QIDS');alljobs.update(r['jobs'])
  slot=r['role_slot_ref'];need(slot['path']=='/data/c16/rtx4080_suite_fill_20261024_v1/control/SDK429_REPEAT2_NAS_CPU_POST_ROLE_'+str(cpu)+'.lock','FIXED_ROLE_EX_LOCK')
  need(all(type(slot[k])is int and slot[k]>=0 for k in ['dev','inode','uid']),'REAL_ROOT_SLOT_IDENTITY')
 io=c['IO_domain_policy'];need(io['schema']=='ROOT_SDK429_REPEAT2_EXACT_NAS_ONLY_CPU_POST_IO_EXCEPTION_V1'and io['status']=='ROOT_APPROVED_EXACT_NAS_ONLY_CPU_POST_EXCEPTION','ROOT_NAS_ONLY_IO_ADMISSION')
 need(io['canonical_LOCAL_IO_acquired']is False and io['GPU_lock_acquired']is False and io['local_payload_or_sort_tmp_allowed']is False and io['whole_system_zero_local_IO_claimed']is False,'NO_LOCAL_PAYLOAD_NO_GPU_LOCK')
 q=data['qids'][0];role=a['cpu_role'];need(role in c['roles'],'ROLE_KEY')
 r=c['roles'][role];need(a['cpu_ids']==r['cpu_ids']and a['own_hard_bytes']==r['hard_bytes']==2*G,'SCOPE_ROLE_CPU_HARD2')
 j=r['jobs'][q];row=data['rows'][0];root=Path(__file__).parent
 need(localpath(j['native_runtime_root'])==localpath(j['remote_runtime_root'])==root and a['remote_runtime_root']==str(ST/root.relative_to(NB)if root.is_relative_to(NB)else root),'EXACT_JOB_RUNTIME_BOTH_HOSTS')
 need(j['code_manifest_sha256']==a['code_manifest_sha256']and j['input_data_sha256']==mf['files']['EXACT_REPEAT_ONLY_POST_DATA_V1.json']['sha256'],'SCOPE_CONTRACT_CODE_DATA_PIN')
 need(j['binary_sha256']==row['binary_sha256']and j['argv']==row['argv'],'EXACT_JOB_BINARY_ARGV')
 need(io['per_job_paths'][q]==dict(source_root=row['source_root'],runtime_output_root=j['remote_runtime_root'],grouped_and_scratch_root=j['remote_runtime_root']+'/runs',sort_tmp_policy='EXPLICIT_-T_<work>/sort-XXXXXXXX',native_body_IO_allowed=False),'EXACT_NAS_SOURCE_SCRATCH_SORT_DOMAIN')
 need(a['cpu_role_slot_expected']==r['role_slot_ref'],'SCOPE_CONTRACT_SLOT_PIN')
 return c,r
def slot_identity(r):
 p=Path(r['path']);need(not p.is_symlink(),'NO_ROLE_SYMLINK')
 z=p.stat();need(stat.S_ISREG(z.st_mode)and z.st_size==0 and stat.S_IMODE(z.st_mode)==0o600,'ROLE_REGULAR0600_EMPTY')
 need((z.st_dev,z.st_ino,z.st_uid)==(r['dev'],r['inode'],r['uid'])and z.st_uid==os.getuid(),'ROOT_PINNED_ROLE_IDENTITY')
 return z
def acquire(r):
 slot_identity(r);fd=os.open(r['path'],os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  z=os.fstat(fd);need((z.st_dev,z.st_ino,z.st_uid)==(r['dev'],r['inode'],r['uid']),'SAMEFD_ROLE_IDENTITY');fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);os.set_inheritable(fd,True);return fd
 except BaseException:os.close(fd);raise
def inherited(fd,guard,r,process=None):
 base=Path('/proc',str(os.getpid()if process is None else process))
 z=(base/'fd'/str(fd)).stat();need((z.st_dev,z.st_ino,z.st_uid)==(r['dev'],r['inode'],r['uid']),'CHILD_ROLE_INHERITED_INODE')
 lines=[l for l in(base/'fdinfo'/str(fd)).read_text().splitlines()if l.startswith('lock:')]
 need(len(lines)==1 and lines[0].split()[2:6]==['FLOCK','ADVISORY','WRITE',str(guard)],'CHILD_ACTUAL_ROLE_EX_FLOCK')
 need(os.readlink(base/'fd'/str(fd))==r['path'],'CHILD_FIXED_ROLE_PATH')
 return dict(fd=fd,dev=z.st_dev,inode=z.st_ino,fdinfo_lock_lines=lines)
