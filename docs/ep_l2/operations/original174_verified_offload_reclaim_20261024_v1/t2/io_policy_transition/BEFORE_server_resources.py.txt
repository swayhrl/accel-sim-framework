"""Scoped COPY_ONLY admission. Never edits scientific policies/controllers."""
import os,json,time,pathlib,subprocess,stat,re
P=pathlib.Path;MIB=1024**2;GIB=1024**3
TASK=P('/root/data/research_asset_verified_offload_20261024_v1');NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2');NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets')
def need(v,m):
 if not v:raise RuntimeError(m)
def js(p):return json.loads(P(p).read_bytes())
def ident(p):
 s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
def pressure(kind='io'):
 return {line.split()[0]:{t.split('=')[0]:float(t.split('=')[1]) for t in line.split()[1:]} for line in P('/proc/pressure/'+kind).read_text().splitlines()}
def old_lock_holders():
 names=['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock'];root=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');out=[]
 for name in names:
  p=root/name
  if not p.exists():continue
  st=p.stat()
  for line in P('/proc/locks').read_text().splitlines():
   fields=line.split()
   if len(fields)<=5 or fields[1]=='->':continue
   z=fields[5].split(':')
   if len(z)==3 and (int(z[0],16),int(z[1],16),int(z[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):out.append(dict(path=str(p),kernel_lock=line,pid=int(fields[4])))
 return out

def current_science():
 out=[]
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   cwd=os.readlink(proc/'cwd');comm=(proc/'comm').read_text().strip();raw=(proc/'stat').read_text().rsplit(')',1)[1].split()
   if any(t in cwd for t in ['ep_l2','dtc','accel-sim','c16']):out.append(dict(pid=int(proc.name),start_ticks=int(raw[19]),comm=comm,cwd=cwd,state=raw[0],cpu_ticks=int(raw[11])+int(raw[12])))
  except (OSError,ValueError,IndexError):pass
 return out
def source_reserved():
 p=P('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');r=js(p);study=r['mechanism_study_20261019_v1'];policy=study['workspace_disk_policy']
 need(policy['disk_floor_bytes']==5*GIB and policy['monitor_reserve_bytes']==2*GIB,'SOURCE_POLICY_IDENTITY_HOLD_DO_NOT_REWRITE')
 leases={k:v for k,v in r['resource_leases'].items() if v.get('status')!='RELEASED'}
 need(all('disk_growth_bytes' in v or 'result_growth_bytes' in v for v in leases.values()),'UNKNOWN_SOURCE_ACTIVE_WRITE_RESERVATION')
 reserved=sum(max(v.get('disk_growth_bytes',0),v.get('result_growth_bytes',0)) for v in leases.values())
 live=[]
 for name in ['AG_execution.lock','AG_execution_io_warning.lock']:
  p=P('/workspace/dtc-ag8r1-finite-resume-174-v1')/name
  if not p.exists():continue
  v=js(p);proc=P('/proc')/str(v['pid'])
  try:
   if int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])==int(v['start_ticks']):live.append(v)
  except OSError:pass
 need(not live,'SOURCE_LIVE_DTC_OWNER_RESERVATION_JOIN_HOLD')
 return dict(registered_reserved_bytes=reserved,leases=leases,science_starts=study['actual_starts'],T0=study['t0_unix'],floor_bytes=5*GIB,monitor_reserve_bytes=2*GIB,unclosed_DTC_locks=live)
def admission(role,remote_peak=0,include_activity=True,allowed_lock_pids=(),metadata_only=False):
 host=os.uname().nodename;ns=os.readlink('/proc/self/ns/mnt');need((host,ns) in [('huangrulin-174','mnt:[4026534768]'),('huangrulin-sshfs-174','mnt:[4026535153]')],'ENDPOINT_IDENTITY_HOLD')
 reg=js(NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');native_reserved=sum(int(v.get('reserved_write_bytes',0)) for v in reg.get('registered_future_requests',{}).values())
 src=source_reserved() if role=='SOURCE' else None
 source_reserved_bytes=src['registered_reserved_bytes'] if src else 0
 disk=os.statvfs('/root/data');free=disk.f_bavail*disk.f_frsize;required=7*GIB+native_reserved+source_reserved_bytes+GIB+64*MIB
 # Read-only metadata identity/SHA-reuse preparation is not data-copy
 # admission. Report the unchanged copy threshold and its actual PASS/HOLD;
 # no Source payload write or full-body read is permitted by that caller.
 copy_space_pass=free>=required and disk.f_favail>=100000
 if not metadata_only:need(copy_space_pass,'RESOURCE_HOLD_SSD_ALL_DECLARED_RESERVATIONS')
 mem=int(next(l.split()[1] for l in P('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;cur=int(P('/sys/fs/cgroup/memory.current').read_text());mx=P('/sys/fs/cgroup/memory.max').read_text().strip()
 need(mem>=64*GIB and (mx=='max' or int(mx)-cur>=GIB),'RESOURCE_HOLD_RAM_OR_CGROUP')
 locks=old_lock_holders();foreign_locks=[x for x in locks if x['pid'] not in (os.getpid(),*allowed_lock_pids)]
 if not metadata_only:need(not foreign_locks,'OTHER_EXISTING_ARCHIVE_LOCK_HELD_NO_TAKEOVER')
 io=pressure();need(io.get('some',{}).get('avg60',0)<25 and io.get('full',{}).get('avg60',0)<20,'RESOURCE_HOLD_SUSTAINED_SEVERE_HOST_IO')
 active=[]
 if role=='TARGET':
  for request_id,req in reg.get('registered_future_requests',{}).items():
   if req.get('state')!='RUNNING':continue
   consumed=req.get('consumed')
   # Other science owners use an integer counter plus case_consumption.
   # An unfamiliar RUNNING schema is a common resource HOLD, never an idle
   # science claim or a parser crash followed by 106 repeated asset attempts.
   need(isinstance(consumed,dict),'RESOURCE_HOLD_ACTIVE_SCIENCE_UNSUPPORTED_PROGRESS_SCHEMA '+request_id)
   for cohort,item in consumed.items():
    if not isinstance(item,dict) or item.get('execution_receipt'):continue
    ip=item.get('intent')
    need(ip and ip.startswith(str(NATIVE/'control')+'/'),'CURRENT_SCIENCE_INTENT_IDENTITY_HOLD')
    intent=js(ip);output=intent.get('output');need(output and output.startswith('/root/data/'),'CURRENT_SCIENCE_OUTPUT_IDENTITY_HOLD')
    proof=P(output)/'NATIVE_SIMULATOR_PID_AND_MAPS.json';need(proof.exists(),'CURRENT_SCIENCE_PREFORK_TRANSITION_HOLD')
    v=js(proof);proc=P('/proc')/str(v['pid'])
    try:tick=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
    except OSError:continue
    if tick==int(v['start_ticks']):active.append(dict(request_id=request_id,cohort=cohort,pid=v['pid'],start_ticks=tick))
 if active:need(io.get('some',{}).get('avg10',0)<=5 and io.get('full',{}).get('avg10',0)<=1,'RESOURCE_HOLD_ACTUAL_ACTIVE_AEFAIR_IO')
 nas=None
 if role=='TARGET':
  m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0];need(m.get('source')=='admin-wcx@10.208.130.164:/home/shared' and m.get('fstype')=='fuse.sshfs','NOT_TRUE164_TARGET_HOLD')
  f=os.statvfs(NAS.parent);avail=f.f_bavail*f.f_frsize;need(avail>=remote_peak+GIB,'RESOURCE_HOLD_TRUE164_PEAK_CAPACITY');nas=dict(mount=m,available_bytes=avail,reserved_peak_bytes=remote_peak)
 share=os.statvfs('/root/share');sfree=share.f_bavail*share.f_frsize
 return dict(unix=time.time(),host=host,mount_namespace=ns,role=role,SSD_available_bytes=free,SSD_required_bytes=required,copy_SSD_admission_pass=copy_space_pass,metadata_only=metadata_only,native_registered_reserved_bytes=native_reserved,source_registry=src,outside_registered_project_headroom_bytes=GIB,own_controls_reserve_bytes=64*MIB,MemAvailable_bytes=mem,cgroup_memory_current=cur,cgroup_memory_max=mx,IO=io,CPU_pressure=pressure('cpu'),active_AEFAIR=active,science_processes=current_science() if include_activity else [],old_archive_locks_observed=locks,Share_available_bytes=sfree,Share_global40GiB_policy_changed=False,route_exception='TASK_QUALIFIED_ZERO_SHARE_PAYLOAD_STAGING_ONLY',Share_payload_write_budget_bytes=0,true164=nas)
def selected_readers_writers(files,dirs):
 selected={(x['dev'],x['inode']) for x in files+dirs};readers=[];writers=[]
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:fds=list((proc/'fd').iterdir())
  except OSError:continue
  for fd in fds:
   try:
    s=fd.stat()
    if (s.st_dev,s.st_ino) not in selected:continue
    flags=int(next(z.split()[1] for z in (proc/'fdinfo'/fd.name).read_text().splitlines() if z.startswith('flags:')),8)
    if int(proc.name)==os.getpid():continue
    ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]);row=dict(pid=int(proc.name),start_ticks=ticks,fd=fd.name,mode=flags&os.O_ACCMODE)
    (writers if row['mode'] in [os.O_WRONLY,os.O_RDWR] else readers).append(row)
   except FileNotFoundError:pass
 need(not writers,'ACTIVE_SELECTED_SOURCE_WRITER_HOLD')
 need(not readers,'ACTIVE_SELECTED_UNCLOSED_SOURCE_READER_HOLD')
 return dict(current_selected_readers=readers,current_selected_writers=writers,planned_readers='Original Source remains KEEP; no reader path/controller changed; archived bytes preserve exact current owner input and order')
