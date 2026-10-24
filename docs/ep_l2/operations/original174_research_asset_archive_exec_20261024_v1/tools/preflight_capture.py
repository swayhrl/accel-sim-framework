from exec_local import *
SERVER=r'''
import os,json,time,pathlib,subprocess,stat
P=pathlib.Path;GIB=1024**3;MIB=1024**2
def meta(p):
 try:
  s=P(p).lstat();return dict(path=str(p),dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink')
 except OSError as e:return dict(path=str(p),error=str(e))
reg=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');r=json.loads(reg.read_bytes());native=sum(int(v.get('reserved_write_bytes',0)) for v in r['registered_future_requests'].values());host=os.uname().nodename;ns=os.readlink('/proc/self/ns/mnt')
o=dict(unix=time.time(),host=host,namespace=ns,registry_current_requests={},filesystems={},current_research_processes=[],pressure={},foreign_reservations_native_bytes=native,source_registry=None,old_archive_locks=[],new_goal_receiver_or_sender_started=False)
for k,v in r['registered_future_requests'].items():o['registry_current_requests'][k]={q:v.get(q) for q in ['state','reserved_write_bytes','budget','remaining','owner','registration_sha256','authorization_path','authorization_sha256','request_path','spec_path','output','controller','execution_entry']};o['registry_current_requests'][k]['consumed_count']=len(v['consumed']) if isinstance(v.get('consumed'),dict) else v.get('consumed')
for p in ['/workspace','/root/data','/root/share','/root/share/mnt164']:
 s=os.statvfs(p);o['filesystems'][p]=dict(stat=meta(p),available_bytes=s.f_bavail*s.f_frsize,total_bytes=s.f_blocks*s.f_frsize,mount=subprocess.check_output(['findmnt','-J','-T',p],text=True))
for k in ['io','cpu','memory']:o['pressure'][k]=P('/proc/pressure/'+k).read_text()
o['memory']=dict(MemAvailable_bytes=int(next(z.split()[1] for z in P('/proc/meminfo').read_text().splitlines() if z.startswith('MemAvailable:')))*1024,cgroup_current=int(P('/sys/fs/cgroup/memory.current').read_text()),cgroup_max=P('/sys/fs/cgroup/memory.max').read_text().strip())
if host=='huangrulin-174':
 p=P('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');v=json.loads(p.read_bytes());study=v['mechanism_study_20261019_v1'];leases={k:x for k,x in v['resource_leases'].items() if x.get('status')!='RELEASED'};o['source_registry']=dict(policy=study['workspace_disk_policy'],actual_starts=study['actual_starts'],T0=study['t0_unix'],leases=leases);source_extra=sum(max(x.get('disk_growth_bytes',0),x.get('result_growth_bytes',0)) for x in leases.values())
else:source_extra=0
o['registered_Source_extra_reserved_bytes']=source_extra;o['required_SSD_bytes']=7*GIB+GIB+64*MIB+native+source_extra;o['SSD_deficit_bytes']=max(0,o['required_SSD_bytes']-o['filesystems']['/root/data']['available_bytes'])
for p in P('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cwd=os.readlink(p/'cwd');comm=(p/'comm').read_text().strip();s=(p/'stat').read_text().rsplit(')',1)[1].split()
  if any(t in cwd for t in ['dtc','ep_l2','accel-sim','c16']):o['current_research_processes'].append(dict(pid=int(p.name),start_ticks=int(s[19]),cwd=cwd,comm=comm,state=s[0],cpu_ticks=int(s[11])+int(s[12])))
 except (OSError,ValueError,IndexError):pass
locks=P('/proc/locks').read_text().splitlines()
for name in ['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock']:
 p=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')/name
 if not p.exists():continue
 s=p.stat()
 for line in locks:
  fields=line.split()
  if len(fields)>5:
   parts=fields[5].split(':')
   if len(parts)==3 and (int(parts[0],16),int(parts[1],16),int(parts[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):o['old_archive_locks'].append(dict(path=str(p),kernel_entry=line))
target='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_trace_closure_followup_v1'
if host=='huangrulin-sshfs-174':o['new_target_root_stat']=meta(target)
print(json.dumps(o))
'''
def capture(label):
 for alias,end in [('hrl','SOURCE'),('hrl-174-new','TARGET')]:
  x=remote(alias,SERVER,60);save('resource/'+label+'_'+end+'.json',x);print(label,end,'free',x['filesystems']['/root/data']['available_bytes'],'required',x['required_SSD_bytes'],'deficit',x['SSD_deficit_bytes'],flush=True)
if __name__=='__main__':capture(sys.argv[1] if len(sys.argv)>1 else 'CHECK1')
