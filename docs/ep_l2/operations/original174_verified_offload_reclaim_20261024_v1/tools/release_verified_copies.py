"""Exact user-authorized retirement. No recursive removal or scientific writes."""
import os,sys,json,stat,hashlib,time,pathlib,fcntl,subprocess,shlex
P=pathlib.Path
TASK=P('/root/data/research_asset_verified_offload_20261024_v1')
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1')
KEYS=['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','nlink']

def need(ok,msg):
    if not ok: raise RuntimeError(msg)

def ident(p):
    s=P(p).lstat()
    need(stat.S_ISREG(s.st_mode),'NOT_EXACT_REGULAR_FILE '+str(p))
    return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,allocated=s.st_blocks*512)

def free():
    s=os.statvfs('/root/data');return s.f_bavail*s.f_frsize

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()

def journal(path,x,sync=True):
    path=P(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('ab') as f:
        f.write(canon(x));f.flush()
        if sync:os.fsync(f.fileno())

def check_rows(rows):
    ids=set()
    for index,x in enumerate(rows):
        p=x['path'];need(p and p.startswith(('/root/data/full_result_offload_20261023_v1/','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/')),'UNAUTHORIZED_SELECTOR')
        need(os.path.realpath(p)==p,'SYMLINK_ANCESTOR_OR_ALIAS')
        now=ident(p);need(all(now[k]==x['identity'][k] for k in KEYS),'SOURCE_IDENTITY_CHANGED '+p)
        need(now['nlink']==1,'NONUNIQUE_LINK_HOLD');ids.add((now['dev'],now['inode']))
    uses=[]
    for proc in P('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
        try:
            for fd in (proc/'fd').iterdir():
                try:
                    s=fd.stat()
                    if (s.st_dev,s.st_ino) in ids:uses.append(dict(pid=int(proc.name),fd=fd.name))
                except (FileNotFoundError,ProcessLookupError):pass
            for line in (proc/'maps').read_text().splitlines():
                z=line.split(None,5)
                if len(z)>=5 and z[4]!='0':
                    a,b=z[3].split(':');key=(os.makedev(int(a,16),int(b,16)),int(z[4]))
                    if key in ids:uses.append(dict(pid=int(proc.name),memory_mapped_inode=int(z[4])))
        except (FileNotFoundError,ProcessLookupError):pass
        except PermissionError:raise RuntimeError('READER_MAP_OR_FD_VISIBILITY_HOLD '+proc.name)
    need(not uses,'ACTIVE_READER_WRITER_OR_MMAP '+json.dumps(uses))
    return dict(files=len(rows),open_or_mapped_readers=[],actual_current_identity_matches=True)

def retire(rows,role):
    pre=check_rows(rows);before=free();log=TASK/'release'/('SOURCE.jsonl' if role=='SOURCE' else 'TARGET.jsonl')
    done={}
    if log.exists():
        for line in log.read_text().splitlines():
            x=json.loads(line)
            if x.get('event')=='DONE':done[x['path']]=x
    results=[]
    for x in rows:
        p=P(x['path']);before_one=free()
        # All exact files must be present on the initial invocation; a restart
        # requires explicit reconciliation of this durable DONE list, never a
        # new broad selector or silent treatment of unrelated absence.
        now=ident(p);need(all(now[k]==x['identity'][k] for k in KEYS),'IDENTITY_CHANGED_BEFORE_UNLINK')
        event=dict(event='INTENT',role=role,unix=time.time(),path=str(p),identity=now,expected_sha256=x['sha256'],recovery=x['recovery'],authorization_commit=REQUEST['authorization_commit'])
        journal(log,event,sync=role=='SOURCE')
        # Narrow unlink only. Directory trees, links, originals of the T test
        # copies, Git objects and all unlisted scientific assets stay intact.
        p.unlink()
        event=dict(event='DONE',role=role,unix=time.time(),path=str(p),expected_allocated_bytes=now['allocated'],df_before_bytes=before_one,df_after_bytes=free(),still_exists=os.path.lexists(p),expected_sha256=x['sha256'],recovery=x['recovery'])
        need(not event['still_exists'],'UNLINK_NOT_COMPLETE');journal(log,event,sync=role=='SOURCE' or index%256==255 or index==len(rows)-1)
        results.append(event)
    return dict(role=role,preflight=pre,files_unlinked=len(results),expected_allocated_regular_bytes=sum(x['identity']['allocated'] for x in rows),df_before_bytes=before,df_after_bytes=free(),results=results)

def source_main():
    global REQUEST
    REQUEST=json.loads(sys.stdin.buffer.readline())
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'WRONG_SOURCE_NAMESPACE')
    rows=REQUEST['source_rows'];need(len(rows)==4,'EXACT_FOUR_SOURCE_FILES_ONLY')
    need(all('/polybench-bicg/NO_ARGS/traces/kernel-' in x['path'] or '/polybench-atax/NO_ARGS/traces/kernel-' in x['path'] for x in rows),'WRONG_SOURCE_SUBSET')
    print(json.dumps(retire(rows,'SOURCE')),flush=True)

def main():
    global REQUEST
    REQUEST=json.loads(P(sys.argv[1]).read_bytes())
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-sshfs-174','mnt:[4026535153]'),'WRONG_TARGET_NAMESPACE')
    m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0]
    need(m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs','NOT_GENUINE164')
    mem=int(next(z.split()[1] for z in P('/proc/meminfo').read_text().splitlines() if z.startswith('MemAvailable:')))*1024
    need(mem>=64*1024**3,'RAM_HOLD')
    lock=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    need(not (TASK/'release'/'COMPLETE.json').exists(),'ALREADY_RELEASED_USE_PERSISTED_RECEIPT')
    for c in REQUEST['archive_control_checks']:
        need(hashlib.sha256(P(c['path']).read_bytes()).hexdigest()==c['sha256'],'ARCHIVE_PROOF_CHANGED '+c['path'])
    for x in REQUEST['remote_trace_objects']:
        now=ident(x['path']);need(all(now[k]==x['identity'][k] for k in ['dev','inode','size','mtime_ns']),'VERIFIED_ARCHIVE_OBJECT_CHANGED')
    check_rows(REQUEST['native_rows'])
    NAS.mkdir(exist_ok=True);(NAS/'control').mkdir(exist_ok=True)
    # Persist both scopes before any destructive operation, including Source
    # rows whose archive is readable only from the genuine Target mount.
    with (NAS/'control'/'AUTHORIZED_EXACT_RELEASE_REQUEST.json').open('xb') as f:f.write(canon(REQUEST));f.flush();os.fsync(f.fileno())
    need(json.loads((NAS/'control'/'AUTHORIZED_EXACT_RELEASE_REQUEST.json').read_bytes())==REQUEST,'PERSISTENT_AUTH_REOPEN_MISMATCH')
    journal(NAS/'control'/'TARGET_RELEASE_INTENT_DONE.jsonl',dict(event='INTENT',exact_file_plan='AUTHORIZED_EXACT_RELEASE_REQUEST.json',files=len(REQUEST['native_rows']),unix=time.time()))
    before=free();target=retire(REQUEST['native_rows'],'TARGET')
    journal(NAS/'control'/'TARGET_RELEASE_INTENT_DONE.jsonl',dict(event='DONE',files=target['files_unlinked'],df_before_bytes=target['df_before_bytes'],df_after_bytes=target['df_after_bytes'],unix=time.time()))
    need(target['df_after_bytes']>target['df_before_bytes'],'NO_POSITIVE_NATIVE_SSD_RECLAIM_HOLD')
    source=P(__file__).read_text();boot='import sys,json;exec(compile(json.loads(sys.stdin.buffer.readline()),"exact_authorized_retirement.py","exec"),{"__name__":"source_release"})'
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174']
    child=subprocess.run(ssh+['python3 -B -c '+shlex.quote(boot)],input=(json.dumps(source+'\nsource_main()\n')+'\n').encode()+canon(REQUEST),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    need(child.returncode==0,'SOURCE_RETIREMENT_HOLD '+child.stderr.decode(errors='replace')[-2000:]);src=json.loads(child.stdout)
    result=dict(status='EXACT_VERIFIED_DUPLICATE_RETIREMENT_DONE',unix=time.time(),df_before_bytes=before,df_after_bytes=free(),actual_observed_shared_SSD_free_increase_bytes=free()-before,target=target,source=src,archive_preserved=True,all_other_source_files='KEEP',new_scientific_starts=0)
    for path in [TASK/'release'/'COMPLETE.json',NAS/'control'/'EXACT_RELEASE_DONE.json']:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:f.write(canon(result));f.flush();os.fsync(f.fileno())
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
