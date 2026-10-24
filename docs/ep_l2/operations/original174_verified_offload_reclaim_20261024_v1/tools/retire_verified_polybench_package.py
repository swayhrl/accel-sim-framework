"""Exact optional cold-package retirement after current whole NAS SHA PASS.

Uses the user's same-procedure continuation authorization. One fixed file;
no trace directory deletion, no package upload, no scientific state mutation.
"""
import os,sys,json,time,pathlib,stat,hashlib,fcntl,subprocess,shlex
P=pathlib.Path
TASK=P('/root/data/research_asset_verified_offload_20261024_v1')
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1')
SOURCE='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz'
DEST='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz'
SHA='9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca'
EXPECTED=dict(dev=156,inode=33890200,size=17943970556,mtime_ns=1786486434897892302,ctime_ns=1786486434897892302,uid=0,gid=0,mode=0o644,nlink=1)

def need(v,m):
    if not v:raise RuntimeError(m)

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()

def ident(p):
    s=P(p).lstat();need(stat.S_ISREG(s.st_mode),'PACKAGE_NOT_REGULAR')
    return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,allocated=s.st_blocks*512)

def free():
    s=os.statvfs('/root/data');return s.f_bavail*s.f_frsize

def durable(path,x):
    path=P(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        need(path.read_bytes()==canon(x),'EXISTING_EXACT_RECLAIM_RECEIPT_COLLISION');return
    with path.open('xb') as f:f.write(canon(x));f.flush();os.fsync(f.fileno())
    need(path.read_bytes()==canon(x),'CLOSED_REOPEN_RECLAIM_METADATA_MISMATCH')

def source_once(request):
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'SOURCE_IDENTITY_HOLD')
    lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if not os.path.lexists(SOURCE):
        done=TASK/'release/POLYBENCH_PACKAGE_SOURCE_DONE.json';need(done.exists(),'SOURCE_PACKAGE_MISSING_WITHOUT_OWN_DONE')
        out=json.loads(done.read_bytes());need(out['path']==SOURCE and out['archive_sha256']==SHA and not out['source_exists'],'EXISTING_PACKAGE_DONE_IDENTITY_MISMATCH');print(json.dumps(out),flush=True);return
    current=ident(SOURCE);need(all(current[k]==v for k,v in EXPECTED.items()),'SOURCE_PACKAGE_CHANGED_SINCE_TRUSTED_WHOLE_SHA')
    need(os.path.realpath(SOURCE)==SOURCE,'SOURCE_PACKAGE_ALIAS_HOLD');key=(current['dev'],current['inode']);uses=[]
    for proc in P('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
        try:
            for fd in (proc/'fd').iterdir():
                try:
                    s=fd.stat()
                    if (s.st_dev,s.st_ino)==key:uses.append(dict(pid=int(proc.name),fd=fd.name))
                except (FileNotFoundError,ProcessLookupError):pass
            for line in (proc/'maps').read_text().splitlines():
                z=line.split(None,5)
                if len(z)<5 or z[4]=='0':continue
                a,b=z[3].split(':')
                if (os.makedev(int(a,16),int(b,16)),int(z[4]))==key:uses.append(dict(pid=int(proc.name),memory_mapped=True))
        except (FileNotFoundError,ProcessLookupError):pass
        except PermissionError:raise RuntimeError('PACKAGE_READER_VISIBILITY_HOLD')
    need(not uses,'PACKAGE_ACTIVE_READER_OR_WRITER_HOLD')
    r=json.loads(P('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_bytes());leases={k:v for k,v in r['resource_leases'].items() if v.get('status')!='RELEASED'}
    need(not leases,'SOURCE_PLANNED_ACTIVE_SCIENTIFIC_LEASE_REQUIRES_DISPOSITION')
    scope=json.loads(__import__('gzip').decompress((TASK/'control/FROZEN_SCOPES.json.gz').read_bytes()))
    need(not any(x['path']==SOURCE for a in scope['scopes'] for x in a['files']),'PACKAGE_NEEDED_BY_CURRENT_FROZEN_COPY_QUEUE')
    intent=dict(event='INTENT',unix=time.time(),path=SOURCE,identity=current,sha256=SHA,archive_current_full_SHA=request['current_true164_full_SHA'],known_current_reader_handles=[],known_Source_scientific_resource_leases=leases,planned_readers_disposition='Cold compressed backup only; no current frozen-copy member or live Source scientific lease. User designates genuine164 as retained backup authority; future Source-local extraction must restore this exact package first.',restore_numeric_metadata=EXPECTED,source_full_SHA_reused_from_unchanged_identity=True,authorization='20261024 explicit same verified local-copy retirement approval')
    durable(TASK/'release/POLYBENCH_PACKAGE_SOURCE_INTENT.json',intent)
    # The full exact target-side intent is durable on genuine164 already.
    before=free();need(all(ident(SOURCE)[k]==v for k,v in EXPECTED.items()),'SOURCE_CHANGED_IMMEDIATELY_BEFORE_UNLINK');os.unlink(SOURCE);after=free()
    result=dict(event='DONE',unix=time.time(),path=SOURCE,source_exists=os.path.lexists(SOURCE),logical_bytes=EXPECTED['size'],source_allocated_before_bytes=current['allocated'],df_before_bytes=before,df_after_bytes=after,actual_observed_SSD_increase_bytes=after-before,archive_sha256=SHA,all_other_Source_files='KEEP',scientific_starts_or_stops=0)
    durable(TASK/'release/POLYBENCH_PACKAGE_SOURCE_DONE.json',result);need(not result['source_exists'],'PACKAGE_UNLINK_NOT_COMPLETE');print(json.dumps(result),flush=True)

def main():
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-sshfs-174','mnt:[4026535153]'),'TARGET_IDENTITY_HOLD')
    lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    proof=json.loads((TASK/'control/EXISTING_POLYBENCH_CURRENT_FULL_SHA.json').read_bytes());need(proof['status']=='EXISTING_GENUINE164_WHOLE_PACKAGE_CURRENT_FULL_SHA_PASS' and proof['sha256']==SHA and proof['bytes_hashed']==EXPECTED['size'],'FRESH_FULL_ARCHIVE_SHA_REQUIRED')
    now=ident(DEST);need(all(now[k]==v for k,v in proof['identity'].items()),'ARCHIVE_CHANGED_AFTER_CURRENT_WHOLE_SHA')
    m=json.loads(subprocess.check_output(['findmnt','-J','-T',DEST],text=True))['filesystems'][0];need(m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs','NOT_GENUINE164')
    metadata_root=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/infrastructure/project_manifests')
    for leaf,expected in {'POLYBENCH_STAGE_DIRECTORY_METADATA_V2.jsonl':'d0f8ea5d069e370a045f9834cb21799d8fffa341c62285a39b00bec33ddbb3e9','POLYBENCH_STAGE_RESTORE_MAP_R10_V1.json':'4d172393f335ca4f471b540ae0d61049d553abbffb90ddc25ba4c04110452652','POLYBENCH_STAGE_FILE_METADATA_V2.jsonl':'50c22e05d5550a5f3a8d80e45baf9b13e34beadfa01f5d6a333e914894753a80'}.items():
        need(hashlib.sha256((metadata_root/leaf).read_bytes()).hexdigest()==expected,'R13_RECOVERY_METADATA_CHANGED '+leaf)
    request=dict(event='INTENT',Source_exact_path=SOURCE,Source_expected_identity=EXPECTED,current_true164_full_SHA=proof,retained_archive=DEST,retained_original_Metadata='R13 POLYBENCH_STAGE_* metadata and Source R10 source full SHA receipt',recovery='Read exact persistent tgz from genuine164; full byte SHA9feffb...; original Source numeric metadata in this intent. Qualified future ABSENT restoration only; Source same-name MD127 shadow forbidden.',authorization='USER_AUTHORIZATION.md and exact-review plan_B plus subsequent same-procedure approval',scope='ONLY_SOURCE_COMPRESSED_PACKAGE_NOT_EXPANDED_TRACES_OR_ANY_MODEL')
    durable(NAS/'control/POLYBENCH_PACKAGE_RELEASE_INTENT.json',request)
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174']
    code=P(__file__).read_text()+'\nsource_once(json.loads(sys.stdin.buffer.readline()))\n';boot='import sys,json;exec(compile(json.loads(sys.stdin.buffer.readline()),"one_verified_cold_package.py","exec"),{"__name__":"source_package_retirement"})'
    child=subprocess.run(ssh+['python3 -B -c '+shlex.quote(boot)],input=(json.dumps(code)+'\n').encode()+canon(request),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    need(child.returncode==0,'SOURCE_PACKAGE_RETIREMENT_HOLD '+child.stderr.decode(errors='replace')[-2000:]);result=json.loads(child.stdout)
    durable(NAS/'control/POLYBENCH_PACKAGE_RELEASE_DONE.json',result);durable(TASK/'release/POLYBENCH_PACKAGE_COMPLETE.json',result)
    need(result['actual_observed_SSD_increase_bytes']>0,'NO_PHYSICAL_PACKAGE_RECLAIM_HOLD');print(json.dumps(result),flush=True)

if __name__=='__main__':main()
