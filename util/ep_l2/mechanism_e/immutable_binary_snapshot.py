"""Exact r5 future-two physical sharing only; default disabled. No launch authority.
Cooperative producer freeze protects against ordinary accidental writes; no
security claim against malicious privileged writers. Canonical/result caps stay384.
"""
import copy,errno,fcntl,hashlib,json,os,socket,stat
from contextlib import contextmanager
from pathlib import Path
AUTHORITY_REF={'path': '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1/engineering/remaining_two_lossless_storage_r1/ACTUAL_BINARY_FREEZE_AUTHORITY.json', 'sha256': 'c5d4414c4916b2c63feed71be6cb761e345020314019afb2f68b39431f28d47b'}  # Root only after true mode555/aliases/no-writers freeze receipt.
CAP=384*2**20;SIZE=87878744;SHA='e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33';SCI='TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1';CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1';FIELD='mechanism_study_20261019_v1';ACTIVE={'RESERVED','RUNNING','START_INTENT_UNRECONCILED'}
IDS={'V8_TAGPRESSURE_vectorAdd_4M_F','V8_TAGPRESSURE_convolutionSeparable_F'};OUTPUT=Path('/workspace/ep_l2_ms20261019_e_results')
def need(x,m):
 if not x:raise ValueError(m)
def enabled(spec):return AUTHORITY_REF is not None and spec.get('scientific_scope')==SCI and spec.get('condition_id')in IDS
def _sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as s:
  for b in iter(lambda:s.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def authority():
 need(AUTHORITY_REF is not None,'sharing disabled');p=Path(AUTHORITY_REF['path']);need(p.stat().st_size<=2**20 and _sha(p)==AUTHORITY_REF['sha256'],'sharing authority bytes changed');a=json.loads(p.read_text());need(a['schema']=='E2_R5_IMMUTABLE_BINARY_SHARING_ENGINEERING_V1'and a['status']=='ROOT_SOURCE_FREEZE_AND_KNOWN_ALIASES_VERIFIED','root sourcefreeze receipt required');need(a['conditions']==sorted(IDS)and a['binary_sha256']==SHA and a['binary_size']==SIZE and a['logical_endpoint_cap']==CAP and a['private_inode_not_scientifically_required']is True,'exact frozen sharing contract');need(a['no_privileged_malicious_writer_security_claim']is True,'scope of producer freeze explicit');return a

def fd_writable(flags):return (int(flags,8)&os.O_ACCMODE)!=os.O_RDONLY
def map_writable_shared(line,dev,ino):
 f=line.split(None,5)
 if len(f)<5:return False
 major,minor=(int(x,16)for x in f[3].split(':'));return int(f[4])==ino and os.makedev(major,minor)==dev and len(f[1])==4 and f[1][1]=='w'and f[1][3]=='s'
def writer_scan(dev,ino):
 """Finite /proc read only. ENOENT exited/fd-race benign, permissions unknown fatal."""
 pids=[p for p in Path('/proc').iterdir()if p.name.isdigit()];need(len(pids)<=4096,'bounded process reader exceeded');nf=0
 for p in pids:
  try:
   for f in (p/'fd').iterdir():
    nf+=1;need(nf<=262144,'bounded FD reader exceeded')
    try:
     s=f.stat()
     if(s.st_dev,s.st_ino)==(dev,ino):
      info=(p/'fdinfo'/f.name).read_text();flags=next(x.split(':',1)[1].strip()for x in info.splitlines()if x.startswith('flags:'));need(not fd_writable(flags),'canonical writable FD')
    except(FileNotFoundError,ProcessLookupError):continue
   maps=p/'maps';body=maps.read_bytes();need(len(body)<=4*2**20,'bounded map reader exceeded');need(not any(map_writable_shared(x,dev,ino)for x in body.decode().splitlines()),'canonical shared-writable mapping')
  except(FileNotFoundError,ProcessLookupError):continue
 return {'status':'NO_WRITABLE_FD_OR_SHARED_WRITABLE_MAP','pids':len(pids),'fds':nf}

def check_alias_count(paths,nlink):need(len(paths)==nlink,'unknown canonical hardlink alias')

def known_aliases(data,canonical,dev,ino):
 paths={str(canonical)}
 for a in data[FIELD]['attempts'][55:]:
  if a['identity']['binary_sha256']!=SHA:continue
  p=Path(a['result_directory'])/'accel-sim.out';need(p.parent.parent.resolve()==OUTPUT,'owned sharing alias path')
  if p.exists():
   s=p.lstat();need(not stat.S_ISLNK(s.st_mode),'binary alias symlink')
   if(s.st_dev,s.st_ino)==(dev,ino):paths.add(str(p))
 return paths

def pin(spec,data,*,dest=None,scan=True):
 a=authority();need(spec['condition_id']in IDS and spec['identity']['binary_sha256']==SHA,'newtwo actual source only');p=Path(a['canonical_path']);need(spec.get('binary',str(p))==str(p),'canonical source path changed');s=p.lstat();need(stat.S_ISREG(s.st_mode)and stat.S_IMODE(s.st_mode)==0o555,'immutable regular executable555 required');need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(a['dev'],a['ino'],SIZE,a['mtime_ns']),'canonical frozen inode/stat changed');check_alias_count(known_aliases(data,p,s.st_dev,s.st_ino),s.st_nlink)
 for l in data['resource_leases'].values():
  if l.get('status')in ACTIVE and l.get('experiment_id')==CAMPAIGN and 'BUILD'in str(l.get('kind','')).upper():raise ValueError('source build lease conflicts with binary freeze')
 if dest is not None:
  d=Path(dest).lstat();need(stat.S_ISREG(d.st_mode)and(d.st_dev,d.st_ino,d.st_size)==(s.st_dev,s.st_ino,SIZE),'real shared executable not canonical inode')
 if scan:writer_scan(s.st_dev,s.st_ino)
 return dict(canonical_path=str(p),dev=s.st_dev,ino=s.st_ino,size=SIZE,sha256=SHA,mtime_ns=s.st_mtime_ns,mode=0o555,known_nlink=s.st_nlink,logical_endpoint_cap=CAP,physical_future_cap=CAP-SIZE)

def stage_plan(spec,data,*,prestart=False,cwd=None):
 if not enabled(spec):return None
 dest=Path(cwd)/'accel-sim.out'if prestart else None;proof=pin(spec,data,dest=dest)
 if not prestart:need(Path(OUTPUT).stat().st_dev==proof['dev'],'EXDEV sharing not eligible')
 return {'proof':proof,'growth':CAP-SIZE,'usage':None,'metadata_credit':0 if prestart else SIZE,'mandatory_full_batch_generation_preflight':True}

def link_verified(source,target,expected):
 """Filesystem primitive; no copy fallback. Used after source/registry proof."""
 source=Path(source);target=Path(target);s=source.lstat();need(stat.S_ISREG(s.st_mode)and stat.S_IMODE(s.st_mode)==0o555,'frozen executable555 required');need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(expected['dev'],expected['ino'],expected['size'],expected['mtime_ns']),'prelink source changed');need(target.parent.stat().st_dev==s.st_dev and not target.exists(),'new same-filesystem snapshot only');os.link(source,target,follow_symlinks=False);d=target.lstat();after=source.lstat();need((d.st_dev,d.st_ino,d.st_size)==(s.st_dev,s.st_ino,s.st_size)and(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns),'actual hardlink source replaced');return {'source':str(source),'snapshot':str(target),'dev':d.st_dev,'ino':d.st_ino,'size':d.st_size,'mode':0o555,'copy_fallback':False}

def snapshot(coord,spec,attempt,directory,write_json):
 with coord.locked()as(data,item):
  actual=next(a for a in item['attempts']if a['attempt_id']==attempt['attempt_id']);need(actual['state']=='RESERVED'and actual['result_directory']==str(directory),'exact held snapshot only');proof=pin(spec,data);receipt=link_verified(proof['canonical_path'],Path(directory)/'accel-sim.out',proof);pin(spec,data,dest=Path(directory)/'accel-sim.out');receipt.update(scientific_identity_unchanged=True,physical_growth_credit=SIZE,logical_endpoint_cap=CAP,logical_generation_credit=0);write_json(Path(directory)/'BINARY_STORAGE_SNAPSHOT.json',receipt);return receipt

@contextmanager
def readonly_original_lock(coord):
 """Same permanent lock, no Registry.locked updated_at rewrite or second authority."""
 lock=coord.registry.root/'REGISTRY.lock';need(lock.is_file(),'original lock absent')
 with lock.open('r')as f:
  fcntl.flock(f,fcntl.LOCK_EX);data=json.loads((coord.registry.root/'RUN_REGISTRY.json').read_text());need(data['authority_host']==socket.gethostname(),'original dispatcher host only');yield data
