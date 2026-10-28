import pathlib,os,resource,time,signal
G=2**30
EVENT_PREVIOUS={}
def need(v,m):
 if not v:raise RuntimeError(m)
def ticks(pid):
 try:return pathlib.Path('/proc/%s/stat'%pid).read_text().rsplit(')',1)[1].split()[19]
 except FileNotFoundError:return None
def cgpath():
 rel=pathlib.Path('/proc/self/cgroup').read_text().strip().split('::',1)[1]
 return pathlib.Path('/sys/fs/cgroup')/rel.lstrip('/')
def physical_gate(available,current,peer):
 need(peer==28*G,'ROOT_PEER_RESERVE_EXACT')
 return available>=max(0,2*G-current)+peer+16*G
def service():
 cg=cgpath();need(int((cg/'memory.max').read_text())==2*G and int((cg/'memory.swap.max').read_text())==0,'ACTUAL_HARD2_SWAP0')
 need(set(os.sched_getaffinity(0))<=set(range(8)),'CPU0_TO7_ONLY')
 quota,period=(cg/'cpu.max').read_text().split();need(quota!='max'and int(quota)/int(period)<=2,'ACTUAL_CPUQUOTA_MAX2')
 return cg
EVENT_PREVIOUS={}
def integer_or_max(text):
 text=text.strip();return None if text=='max'else int(text)
def pressure(text):
 rows={}
 for line in text.splitlines():
  f=line.split();rows[f[0]]=float(dict(x.split('=')for x in f[1:])['avg10'])
 return rows
def node_verdict(node,required,is_service=False):
 cap=node['memory_max'];high=node['memory_high'];limits=[x for x in[cap,high]if x is not None]
 head=None if not limits else min(limits)-node['memory_current']
 failures=[]
 if not is_service and head is not None and head<required:failures.append('ANCESTOR_ACTUAL_HEADROOM')
 if is_service and cap!=2*G:failures.append('OWN_HARD2_CHANGED')
 if is_service and high is not None and high<2*G:failures.append('OWN_HIGH_BELOW_HARD2')
 if node['pressure']['full']>5 or node['pressure']['some']>20:failures.append('MEMORY_PRESSURE')
 if any((node['events_delta']or{}).get(k,0)!=0 for k in['oom','oom_kill','oom_group_kill']):failures.append('NEW_OOM_OR_KILL_EVENT')
 return dict(node,effective_headroom=head,required_additional=None if is_service else required,limit_touch_events_telemetry_only={k:(node['events_delta']or{}).get(k,0)for k in ['high','max']},failures=failures,PASS=not failures)
def fresh(cg,peer):
 mem={k:int(v.split()[0])*1024 for k,v in(line.split(':',1)for line in pathlib.Path('/proc/meminfo').read_text().splitlines())}
 current=int((cg/'memory.current').read_text());required=max(0,2*G-current)+peer+16*G
 root=pathlib.Path('/sys/fs/cgroup');nodes=[];p=cg
 while True:
  need(p==root or p.is_relative_to(root),'CGROUP_VISIBLE_ROOT')
  st=p.stat()
  if p==root and not(p/'memory.max').exists():
   mounts=[l for l in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()if l.split(' - ',1)[0].split()[4]==str(root)]
   need(len(mounts)==1 and mounts[0].split(' - ',1)[1].split()[0]=='cgroup2'and mounts[0].split(' - ',1)[0].split()[3]=='/'and 'memory'in(p/'cgroup.controllers').read_text().split(),'ACTUAL_UNNAMESPACED_KERNEL_CGROUP2_ROOT')
   need(not(p/'memory.high').exists()and not(p/'memory.current').exists()and not(p/'memory.events').exists(),'ROOT_LIMIT_INTERFACE_SHAPE')
   node=dict(path=str(p),dev=st.st_dev,inode=st.st_ino,memory_current=None,memory_max=None,memory_high=None,pressure=pressure((p/'memory.pressure').read_text()),events=None,events_delta=None,kernel_root_has_no_memory_limit_or_current_event_interface=True,host_MemAvailable_checked_separately=True)
   nodes.append(node_verdict(node,required,False));break
  events={k:int(v)for k,v in(line.split()for line in(p/'memory.events').read_text().splitlines())}
  previous=EVENT_PREVIOUS.get(str(p));identity=(st.st_dev,st.st_ino)
  if previous is not None:need(previous[0]==identity and all(v>=previous[1].get(k,0)for k,v in events.items()),'CGROUP_NODE_REPLACED_OR_COUNTER_RESET')
  delta={k:0 if previous is None else v-previous[1].get(k,0)for k,v in events.items()};EVENT_PREVIOUS[str(p)]=(identity,events)
  if p==cg:need(events.get('oom_kill',0)==0 and events.get('oom_group_kill',0)==0,'OWN_SERVICE_OOM')
  node=dict(path=str(p),dev=st.st_dev,inode=st.st_ino,memory_current=int((p/'memory.current').read_text()),memory_max=integer_or_max((p/'memory.max').read_text()),memory_high=integer_or_max((p/'memory.high').read_text()),pressure=pressure((p/'memory.pressure').read_text()),events=events,events_delta=delta)
  nodes.append(node_verdict(node,required,p==cg))
  if p==root:break
  p=p.parent
 return dict(available_bytes=mem['MemAvailable'],own_current_bytes=current,own_hard_bytes=2*G,EP_reserved_bytes=peer,physical_headroom_bytes=16*G,required_remaining_plus_peer_floor=required,PASS=physical_gate(mem['MemAvailable'],current,peer)and all(n['PASS']for n in nodes),cgroup_nodes=nodes,remote_future_foreign_cap_authority_complete=False)
def ownsignal(p,t,sig,cg):
 need(ticks(p.pid)==t,'OWN_WORKER_TICKS')
 group=pathlib.Path('/proc/%d/cgroup'%p.pid).read_text().strip().split('::',1)[1]
 need(pathlib.Path('/sys/fs/cgroup')/group.lstrip('/')==cg,'EXACT_OWN_HARD_CGROUP')
 fd=os.pidfd_open(p.pid)
 try:
  need(ticks(p.pid)==t,'OWN_WORKER_RECHECK');signal.pidfd_send_signal(fd,sig)
 finally:os.close(fd)
