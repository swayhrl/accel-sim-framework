"""Read-only existing NAS package audit; no new data copy or Source mutation.

Independent NAS I/O path, serialized against actual Target receivers. The other
task's SSD-only Source hash lease is preserved. No model or raw file is read.
"""
import os,json,time,hashlib,pathlib,subprocess,fcntl
P=pathlib.Path
TASK=P('/root/data/research_asset_verified_offload_20261024_v1')
FILE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz')
EXPECTED='9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca'

def need(x,msg):
    if not x:raise RuntimeError(msg)

def identity(s):return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)

def save(name,x):
    p=TASK/'control'/name;t=p.with_name(p.name+'.own-writing')
    with t.open('w') as f:json.dump(x,f);f.flush();os.fsync(f.fileno())
    os.replace(t,p)

def gate():
    need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','READ_AUDIT_IDENTITY_HOLD')
    m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(FILE)],text=True))['filesystems'][0]
    need(m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs','READ_AUDIT_NOT_GENUINE164')
    mem=int(next(z.split()[1] for z in P('/proc/meminfo').read_text().splitlines() if z.startswith('MemAvailable:')))*1024
    need(mem>=64*1024**3,'READ_AUDIT_RAM_HOLD')
    current=int(P('/sys/fs/cgroup/memory.current').read_text());limit=P('/sys/fs/cgroup/memory.max').read_text().strip()
    need(limit=='max' or int(limit)-current>=1024**3,'READ_AUDIT_CGROUP_RAM_HOLD')
    io={z.split()[0]:{a.split('=')[0]:float(a.split('=')[1]) for a in z.split()[1:]} for z in P('/proc/pressure/io').read_text().splitlines()}
    reg=json.loads(P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())
    active=[k for k,v in reg.get('registered_future_requests',{}).items() if v.get('state')=='RUNNING']
    if active:need(io['some']['avg10']<=5 and io['full']['avg10']<=1,'READ_AUDIT_ACTIVE_SCIENCE_IO_HOLD')
    need(io['some']['avg60']<25 and io['full']['avg60']<20,'READ_AUDIT_SUSTAINED_SEVERE_IO_HOLD')
    return dict(unix=time.time(),io=io,active_science_requests=active,MemAvailable_bytes=mem,Source_sender_lease_taken=False,Source_payload_writes=0,local_payload_writes=0,operation='READ_ONLY_EXISTING_ARCHIVE_AUDIT_NOT_COPY_ADMISSION')

def main():
    lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    before=gate();original=identity(FILE.stat());need(original['size']==17943970556,'EXISTING_PACKAGE_SIZE_CHANGED')
    h=hashlib.sha256();count=0;start=time.monotonic();last=0;samples=[]
    with FILE.open('rb') as f:
        while True:
            b=f.read(1024**2)
            if not b:break
            h.update(b);count+=len(b)
            time.sleep(max(0,count/(15*1024**2)-(time.monotonic()-start)))
            if time.monotonic()-last>=10:
                sample=gate();samples.append(sample);last=time.monotonic()
                save('EXISTING_POLYBENCH_HASH_PROGRESS.json',dict(phase='READ_ONLY_EXISTING_TRUE164_FULL_SHA',pid=os.getpid(),unix=time.time(),bytes_hashed=count,total_bytes=original['size'],elapsed_seconds=time.monotonic()-start,resource=sample))
        need(identity(os.fstat(f.fileno()))==original,'ARCHIVE_CHANGED_DURING_CURRENT_FULL_HASH')
    need(identity(FILE.stat())==original and h.hexdigest()==EXPECTED,'CURRENT_FULL_ARCHIVE_SHA_MISMATCH')
    with FILE.open('rb') as f:need(identity(os.fstat(f.fileno()))==original,'CLOSED_REOPEN_IDENTITY_CHANGED')
    out=dict(status='EXISTING_GENUINE164_WHOLE_PACKAGE_CURRENT_FULL_SHA_PASS',path=str(FILE),identity=original,sha256=h.hexdigest(),bytes_hashed=count,elapsed_seconds=time.monotonic()-start,resource_before=before,resource_after=gate(),Source_deleted_bytes=0,Source_retirement='NOT_PERFORMED; current/planned reader and exact authorization admission still required',native_full_restore_claimed=False)
    save('EXISTING_POLYBENCH_CURRENT_FULL_SHA.json',out);print(json.dumps(out),flush=True)

if __name__=='__main__':main()
