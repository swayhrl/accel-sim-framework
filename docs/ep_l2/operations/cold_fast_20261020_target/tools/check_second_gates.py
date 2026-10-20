"""Lightweight existing second-V3 admission snapshot. No payload or tree scan."""
import concurrent.futures,json,pathlib,subprocess,sys,datetime
D=pathlib.Path(__file__).resolve().parent
CODE=r'''
import pathlib,os,json,subprocess,fcntl,datetime
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
ns=os.readlink('/proc/self/ns/mnt');host='Source' if ns=='mnt:[4026534768]' else 'Target' if ns=='mnt:[4026535153]' else 'WRONG'
lines=pathlib.Path('/proc/pressure/io').read_text().splitlines()
io={s.split()[0]:float(s.split()[1].split('=')[1]) for s in lines}
mem=int(next(s.split()[1] for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
limit=pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip();current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
v=os.statvfs(B);r=dict(role=host,namespace=ns,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),host_IO_avg10=io,MemAvailable_bytes=mem,Share_available_bytes=v.f_bavail*v.f_frsize,cgroup_headroom_bytes=None if limit=='max' else int(limit)-current,identity_pass=host!='WRONG')
if host=='Source':
 p=pathlib.Path('/workspace/worktrees/gpu-l2-v3-signoff-46bf3a69/build/postcheck')
 if p.exists():
  s=p.lstat();r['source_root_identity']=[s.st_dev,s.st_ino,s.st_nlink];r['identity_pass']=r['source_root_identity']==[156,33145222,3]
 else:r['identity_pass']=False
else:
 r['mount']=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164','-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
 m=r['mount'];r['identity_pass']=r['identity_pass'] and (m['target'],m['source'],m['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs') and pathlib.Path('/root/share/mnt164').stat().st_dev==39
 r['locks']={}
 for name in ['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock']:
  with (B/name).open('rb') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);r['locks'][name]='IDLE';fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:r['locks'][name]='BUSY'
 # Immediate known staging children only; never recurse a source tree/NAS.
 r['active_bridge_windows']=[p.parent.name for p in B.glob('*/files') if any(p.iterdir())]
 root=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/cold_projects/20261020/V3_46BF3A69_POSTCHECK_7fad6fe01e554816')
 r['destination_exists']=root.exists()
 r['destination_entries']=[p.name for p in root.iterdir()] if root.exists() else []
 s=os.statvfs('/root/share/mnt164');r['NAS_available_bytes']=s.f_bavail*s.f_frsize
print(json.dumps(r))
'''
def probe(host):
 p=subprocess.run(['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',host,'timeout 25s python3 -B -'],input=CODE.encode(),capture_output=True,timeout=40)
 if p.returncode:raise RuntimeError(host+': '+p.stderr.decode(errors='replace')[-800:])
 return json.loads(p.stdout)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 source,target=list(pool.map(probe,['hrl','hrl-174-new']))
reasons=[]
for item in [source,target]:
 prefix=item['role']
 if not item['identity_pass']:reasons.append(prefix+'_IDENTITY_HOLD')
 if max(item['host_IO_avg10'].values())>=80:reasons.append(prefix+'_EXTREME_HOST_IO_AT_LEAST80')
 if item['MemAvailable_bytes']<64*1024**3:reasons.append(prefix+'_RAM_BELOW64GiB')
 if item['Share_available_bytes']<40*1024**3:reasons.append(prefix+'_SHARE_BELOW40GiB')
 if item['cgroup_headroom_bytes'] is not None and item['cgroup_headroom_bytes']<512*1024**2:reasons.append(prefix+'_CGROUP_HEADROOM')
if any(v!='IDLE' for v in target['locks'].values()):reasons.append('EXISTING_FLOW_BUSY_DO_NOT_DUPLICATE')
if target['active_bridge_windows']:reasons.append('EXISTING_BRIDGE_WINDOW_KEEP')
if target['NAS_available_bytes']<1024**3:reasons.append('NAS_FREE_HOLD')
result=dict(schema='LANE_T_SECOND_LIGHTWEIGHT_ORIGINAL_GATES_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='ALL_ORIGINAL_LIGHTWEIGHT_GATES_PASS' if not reasons else 'RESOURCE_HOLD',reasons=reasons,source=source,target=target,no_payload_read=True,no_full_tree_scan=True,no_model_or_ledger_changes=True,former_host_IO10_removed_by_user=True,extreme_host_IO_circuit_breaker=80)
raw=(json.dumps(result,indent=2)+'\n').encode();(D/'LATEST_SECOND_LIGHTWEIGHT_GATE.json').write_bytes(raw)
with (D/'SECOND_LIGHTWEIGHT_GATE_HISTORY.jsonl').open('ab') as f:f.write((json.dumps(result)+'\n').encode())
print(json.dumps({'utc':result['utc'],'status':result['status'],'Source_host_IO':source['host_IO_avg10'],'Target_host_IO':target['host_IO_avg10'],'reasons':reasons,'existing_destination':target['destination_entries']}),flush=True)
