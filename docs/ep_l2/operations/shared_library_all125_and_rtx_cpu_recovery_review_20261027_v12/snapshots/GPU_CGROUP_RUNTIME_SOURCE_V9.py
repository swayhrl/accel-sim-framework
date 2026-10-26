"""Typed actual Linux cgroup-v2 memory chain, separate from foreign reservation authority."""
import pathlib,os,stat,json,time,hashlib,math,re
MiB=1024**2;GiB=1024**3;FLOOR=256*MiB;SERVICE_CAP=20*GiB
def need(x,m):
 if not x:raise RuntimeError(m)
def integer(text,unlimited=False):
 t=text.strip()
 if unlimited and t=='max':return None
 need(re.fullmatch(r'[0-9]{1,24}',t)is not None,'nonnegative integer/max cgroup value')
 return int(t)
def events(text):
 d={}
 for line in text.splitlines():
  p=line.split();need(len(p)==2 and p[0]not in d and re.fullmatch('[a-z_]+',p[0]),'typed unique event row');d[p[0]]=integer(p[1])
 need({'high','max','oom','oom_kill'}<=set(d),'missing event counters');return d
def pressure(text):
 d={}
 for line in text.splitlines():
  p=line.split();need(p[0]in ('some','full')and p[0]not in d,'typed PSI rows')
  q={}
  for item in p[1:]:
   k,v=item.split('=',1);need(k not in q and k in ('avg10','avg60','avg300','total'),'typed unique PSI field')
   q[k]=integer(v)if k=='total'else float(v)
   need(k=='total'or math.isfinite(q[k])and 0<=q[k]<=100,'finite PSI percentage')
  need(set(q)=={'avg10','avg60','avg300','total'},'complete PSI row');d[p[0]]=q
 need(set(d)=={'some','full'},'complete PSI some/full');return d
def bounded(path,limit=16384):
 p=pathlib.Path(path);fd=os.open(p,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode),'kernel metadata regular file')
  raw=os.read(fd,limit+1);b=os.fstat(fd);q=p.stat()
  need(len(raw)<=limit and(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)==(q.st_dev,q.st_ino),'bounded stable kernel FD/path identity')
  return raw.decode(),dict(dev=a.st_dev,inode=a.st_ino,sha256=hashlib.sha256(raw).hexdigest())
 finally:os.close(fd)
def host():
 p=pathlib.Path('/proc/self');s=(p/'stat').read_text();f=s.rsplit(')',1)[1].split()
 return dict(pid=os.getpid(),start_ticks=f[19],boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),namespaces={n:os.readlink(p/'ns'/n)for n in ('pid','mnt','user','cgroup')})
def unescape(s):
 return re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),s)
def location():
 cg,cr=bounded('/proc/self/cgroup');rows=[x.split(':',2)for x in cg.splitlines()];rows=[x for x in rows if len(x)==3 and x[0]=='0'and x[1]==''];need(len(rows)==1,'one unified cgroup-v2 membership')
 member=pathlib.PurePosixPath(rows[0][2]);need(member.is_absolute()and '..'not in member.parts,'absolute normalized membership')
 text,mr=bounded('/proc/self/mountinfo',262144);mounts=[]
 for line in text.splitlines():
  left,right=line.split(' - ',1);a=left.split();b=right.split()
  if b[0]=='cgroup2':
   root=pathlib.PurePosixPath(unescape(a[3]));mount=pathlib.Path(unescape(a[4]))
   if member.is_relative_to(root):mounts.append((root,mount))
 need(len(mounts)==1,'unambiguous cgroup2 hierarchy mount')
 root,mount=mounts[0];current=mount/member.relative_to(root);need(current.is_relative_to(mount),'exact hierarchy mapping')
 for q in [current,*current.parents]:
  if q.is_relative_to(mount):need(not q.is_symlink(),'no cgroup directory alias')
 return current,mount,dict(membership=str(member),mount_root=str(root),mountpoint=str(mount),cgroup_ref=cr,mountinfo_ref=mr,visible_namespace_boundary=True)
def node(p,root_allowed=False):
 out={'path':str(p),'file_refs':{},'kind':'CGROUP_MEMORY_CONTROLLER_NODE'}
 absent=[]
 for name in ['memory.max','memory.current','memory.high','memory.swap.max','memory.swap.current','memory.oom.group','cpu.max','memory.events']:
  if not(p/name).exists():absent.append(name)
 if absent:
  need(root_allowed and len(absent)==8,'non-root or partial missing controller memory proof')
  controllers,ref=bounded(p/'cgroup.controllers');need('memory'in controllers.split(),'actual root controller memory availability')
  out.update(kind='KERNEL_HIERARCHY_ROOT_NO_LIMIT_FILES',absent_files=absent,controllers=controllers.split());out['file_refs']['cgroup.controllers']=ref
  for name in absent:out[name]=None
 for name in ['memory.max','memory.current','memory.high','memory.swap.max','memory.swap.current','memory.oom.group','cpu.max','memory.events','memory.pressure','cgroup.procs']:
  if name in absent:continue
  text,ref=bounded(p/name);out['file_refs'][name]=ref
  if name in ('memory.max','memory.high','memory.swap.max'):out[name]=integer(text,True)
  elif name in ('memory.current','memory.swap.current','memory.oom.group'):out[name]=integer(text)
  elif name=='memory.events':out[name]=events(text)
  elif name=='memory.pressure':out[name]=pressure(text)
  elif name=='cgroup.procs':out[name]=[integer(x)for x in text.split()]
  else:
   t=text.split();need(len(t)==2,'typed cpu.max');out[name]=[integer(t[0],True),integer(t[1])]
 return out
def collect():
 before=host();current,mount,loc=location();paths=[];p=current
 while True:
  paths.append(p)
  if p==mount:break
  need(len(paths)<32,'bounded cgroup ancestor depth');p=p.parent
 start=time.time();a=[node(p,p==mount)for p in paths];time.sleep(.03);b=[node(p,p==mount)for p in paths]
 after=host();again,again_mount,again_loc=location()
 need(before==after and again==current and again_mount==mount and again_loc['membership']==loc['membership'],'membership/boot/ns/PID stable throughout snapshot')
 need(time.time()-start<=5,'bounded cgroup snapshot duration')
 for x,y in zip(a,b):
  for f in ('memory.max','memory.high','memory.swap.max','memory.oom.group','cpu.max'):need(x[f]==y[f],'cgroup limits changed during snapshot')
  for f in x['file_refs']:need((x['file_refs'][f]['dev'],x['file_refs'][f]['inode'])==(y['file_refs'][f]['dev'],y['file_refs'][f]['inode']),'cgroup file identity changed')
 return dict(schema='ACTUAL_CGROUP2_MEMORY_CHAIN_V9',origin='KERNEL_SELF_FIXED_PATHS',host=before,location=loc,before=a,after=b,started_unix=start,ended_unix=time.time(),MemAvailable_bytes=int(next(x.split()[1]for x in pathlib.Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024,module_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
def evaluate(s,foreign_RAM_bytes,own_RAM_bytes,role='native174',run_id=None,owned_pids=None):
 need(type(foreign_RAM_bytes)is int and foreign_RAM_bytes>=0 and type(own_RAM_bytes)is int and own_RAM_bytes>=0,'explicit full foreign and own RAM budgets')
 need(role in ('native174','gpu109_service','CPU_READONLY_OBSERVATION'),'closed runtime role')
 need(s['schema']=='ACTUAL_CGROUP2_MEMORY_CHAIN_V9'and s['origin']=='KERNEL_SELF_FIXED_PATHS','typed kernel snapshot')
 a=s['before'];b=s['after'];need(a and len(a)==len(b),'complete two-pass chain')
 need(a[-1]['path']==s['location']['mountpoint'],'visible hierarchy root included')
 for i,(x,y)in enumerate(zip(a,b)):
  need(x['path']==y['path']and x['kind']==y['kind'],'same node chain/kind')
  if i:need(str(pathlib.Path(a[i-1]['path']).parent)==x['path'],'no missing/reordered ancestor')
 rows=[];failures=[];required=foreign_RAM_bytes+own_RAM_bytes+FLOOR
 for i,(x,y)in enumerate(zip(a,b)):
  root_without_limits=x['kind']=='KERNEL_HIERARCHY_ROOT_NO_LIMIT_FILES'
  if root_without_limits:need(i==len(a)-1 and y['kind']==x['kind']and x['absent_files']==y['absent_files']and 'memory'in y['controllers'],'typed actual hierarchy-root absence')
  limit=y['memory.max'];high=y['memory.high'];current=None if root_without_limits else max(x['memory.current'],y['memory.current'])
  caps=[v for v in (limit,high)if v is not None];effective=min(caps)if caps else None;headroom=None if effective is None else max(0,effective-current)
  for f in ('memory.max','memory.high','memory.swap.max','memory.oom.group','cpu.max'):need(x[f]==y[f],'limit drift in evaluated pair')
  delta={}if root_without_limits else{k:y['memory.events'].get(k,0)-x['memory.events'].get(k,0)for k in set(x['memory.events'])|set(y['memory.events'])}
  if any(delta.get(k,0)!=0 for k in ('high','max','oom','oom_kill','oom_group_kill')):failures.append(dict(path=x['path'],reason='memory pressure/OOM event delta',delta=delta))
  psi=max(x['memory.pressure']['full']['avg10'],y['memory.pressure']['full']['avg10']);some=max(x['memory.pressure']['some']['avg10'],y['memory.pressure']['some']['avg10'])
  if psi>5 or some>20:failures.append(dict(path=x['path'],reason='actual memory PSI pressure',full_avg10=psi,some_avg10=some))
  need_at_node=FLOOR if role=='gpu109_service'and i==0 else required
  if headroom is not None and headroom<need_at_node:failures.append(dict(path=x['path'],reason='cgroup actual effective headroom below full reservation + own + floor',headroom=headroom,required=need_at_node))
  rows.append(dict(kind=y['kind'],path=x['path'],memory_max=limit,memory_high=high,current_conservative=current,effective_headroom=headroom,required_additional=need_at_node,full_foreign_RAM_bytes=foreign_RAM_bytes,own_RAM_bytes=own_RAM_bytes,pressure_full_avg10=psi,pressure_some_avg10=some,events_delta=delta))
 if s['MemAvailable_bytes']<required:failures.append(dict(reason='host physical MemAvailable below full foreign + own + floor',available=s['MemAvailable_bytes'],required=required))
 if role=='gpu109_service':
  leaf=b[0];need(run_id is not None and leaf['path'].endswith('/trace-bridge-v9-'+run_id+'.service'),'exact own Root-scoped service cgroup')
  if leaf['memory.max']!=SERVICE_CAP or leaf['memory.swap.max']!=0 or leaf['memory.oom.group']!=1:failures.append(dict(reason='actual service hard20GiB/swap0/OOMgroup'))
  q,p=leaf['cpu.max']if leaf['cpu.max']is not None else(None,1)
  if q is None or q>8*p:failures.append(dict(reason='actual service CPU upper bound'))
  need(owned_pids is not None,'actual owned service membership required')
  if not(set(a[0]['cgroup.procs'])|set(leaf['cgroup.procs']))<=set(owned_pids):failures.append(dict(reason='foreign/unknown PID inside own service cgroup'))
 return dict(schema='TYPED_CGROUP2_RUNTIME_MEMORY_GATE_V9',status='PASS'if not failures else'HOLD',role=role,foreign_RAM_bytes=foreign_RAM_bytes,own_RAM_bytes=own_RAM_bytes,control_floor_bytes=FLOOR,host_MemAvailable=s['MemAvailable_bytes'],rows=rows,failures=failures,namespace_boundary=s['location'],foreign_authority_not_inferred_from_kernel=True,production_qualification=False)
def runtime_gate(foreign_RAM_bytes,own_RAM_bytes,role,run_id=None,owned_pids=None):
 snap=collect();verdict=evaluate(snap,foreign_RAM_bytes,own_RAM_bytes,role,run_id,owned_pids)
 need(verdict['status']=='PASS','actual cgroup runtime memory HOLD: '+json.dumps(verdict['failures'],sort_keys=True))
 return snap,verdict
if __name__=='__main__':print(json.dumps(collect()))
