"""Finite read-only tar+zstd sender. Frozen V3 roots only; no source writes."""
import fcntl, gzip, hashlib, json, os, pathlib, stat, subprocess, sys, threading, time

ROOTS = {
 '463600cb':'/workspace/worktrees/gpu-l2-v3-signoff-463600cb/build/postcheck',
 '46bf3a69':'/workspace/worktrees/gpu-l2-v3-signoff-46bf3a69/build/postcheck',
}
TAG=sys.argv[1]; root=pathlib.Path(ROOTS[TAG]); rate=30*1024**2
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
os.nice(19);subprocess.run(['ionice','-c','3','-p',str(os.getpid())],check=True)
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
lock=os.open(B/'.TLS_V10_SOURCE_SENDER.lock',os.O_RDONLY|os.O_NOFOLLOW)
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
raw=sys.stdin.buffer.read(32*1024**2);rows=[json.loads(x) for x in gzip.decompress(raw).splitlines()]
expected={'463600cb':'06ce69e2aa1fc5ee24c9bd61c9bf6b30b475758ef9e7483b9f92e7e8d4245f3e',
          '46bf3a69':'19ff2122104d2b0ccd929e857870638f08614a0fbc7a1963765ba905dc8c3402'}
assert hashlib.sha256(raw).hexdigest()==expected[TAG]

def guard():
    share=os.statvfs(B);assert share.f_bavail*share.f_frsize>=40*1024**3
    mem=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
    assert mem>=64*1024**3
    p=pathlib.Path('/sys/fs/cgroup/memory.max');limit=p.read_text().strip()
    assert limit=='max' or int(limit)-int(p.with_name('memory.current').read_text())>=512*1024**2
    pressure=float(pathlib.Path('/proc/pressure/io').read_text().splitlines()[0].split()[1].split('=')[1])
    return pressure

def frozen():
    for r in rows:
        assert r[0]=='.' or not pathlib.PurePosixPath(r[0]).is_absolute() and '..' not in pathlib.PurePosixPath(r[0]).parts
        p=root/r[0];s=p.lstat();kind='directory' if stat.S_ISDIR(s.st_mode) else 'regular' if stat.S_ISREG(s.st_mode) else 'OTHER'
        got=[kind,s.st_dev,s.st_ino,s.st_nlink,s.st_mode,s.st_uid,s.st_gid,s.st_size,s.st_blocks,s.st_mtime_ns,s.st_ctime_ns,None]
        assert got==r[1:], 'BA frozen identity drift: '+r[0]

def readers():
    hits=[];gaps=[];mine={os.getpid(),os.getppid()};prefix=str(root)
    for proc in pathlib.Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) in mine:continue
        try:
            args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            if prefix in args:hits.append({'pid':int(proc.name),'kind':'argv'})
            for n in ['cwd','exe']:
                try:
                    target=os.readlink(proc/n)
                    if target==prefix or target.startswith(prefix+'/'):hits.append({'pid':int(proc.name),'kind':n})
                except FileNotFoundError:pass
            for fd in (proc/'fd').iterdir():
                try:
                    target=os.readlink(fd)
                    if target==prefix or target.startswith(prefix+'/'):hits.append({'pid':int(proc.name),'kind':'fd'})
                except FileNotFoundError:pass
            if prefix in (proc/'maps').read_text(errors='replace'):hits.append({'pid':int(proc.name),'kind':'maps'})
        except (FileNotFoundError,ProcessLookupError):pass
        except PermissionError:gaps.append(int(proc.name))
    assert not hits and not gaps, 'active source readers or scan gaps: '+str((hits,gaps))
    return {'active_exact_root_readers':hits,'permission_gaps':gaps}

assert guard()<=10, 'existing IO guard10 not met before stream'
activity=readers();frozen();assert guard()<=10
tar=subprocess.Popen(['tar','--format=pax','--numeric-owner','--acls','--xattrs','--selinux',
                      '--sort=name','--one-file-system','-C',str(root.parent),'-cf','-','--','postcheck'],
                     stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=sys.stderr.buffer)
zstd=subprocess.Popen(['zstd','-T1','-3','--check','-c'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=sys.stderr.buffer)
tar_hash=hashlib.sha256();compressed_hash=hashlib.sha256();state={'tar_bytes':0,'errors':[]}

def pump():
    start=time.monotonic();last=0;held_since=None
    try:
        while True:
            if time.monotonic()-last>=2:
                pressure=guard();last=time.monotonic()
                while pressure>10:
                    if held_since is None:held_since=time.monotonic()
                    assert time.monotonic()-held_since<=30, 'IO guard10 held >30s; preserve partial'
                    time.sleep(5);pressure=guard()
                held_since=None
            data=tar.stdout.read(1024**2)
            if not data:break
            state['tar_bytes']+=len(data);tar_hash.update(data)
            time.sleep(max(0,state['tar_bytes']/rate-(time.monotonic()-start)))
            zstd.stdin.write(data)
    except BaseException as e:
        state['errors'].append(repr(e));tar.terminate()
    finally:
        zstd.stdin.close();tar.stdout.close()

thread=threading.Thread(target=pump);thread.start();count=0;start=time.monotonic()
try:
    while True:
        data=zstd.stdout.read(1024**2)
        if not data:break
        count+=len(data);compressed_hash.update(data)
        time.sleep(max(0,count/rate-(time.monotonic()-start)))
        sys.stdout.buffer.write(data);sys.stdout.buffer.flush()
    thread.join();trc=tar.wait();zrc=zstd.wait()
    assert not state['errors'] and trc==zrc==0, str((state['errors'],trc,zrc))
    frozen();guard()
    receipt=dict(schema='COLD_STREAM_SOURCE_COMPLETE_V1',status='SOURCE_READONLY_STREAM_COMPLETE',tag=TAG,
                 root=str(root),BA_manifest_gzip_sha256=expected[TAG],frozen_metadata_entries=len(rows),
                 frozen_metadata_before_after_exact=True,compressed_bytes=count,
                 archive_sha256=compressed_hash.hexdigest(),tar_stream_bytes=state['tar_bytes'],
                 tar_stream_sha256=tar_hash.hexdigest(),source_files_modified_deleted=0,
                 source_overlay_payload_temporary_bytes=0,source_originals='SOURCE_KEEP',activity=activity)
    print('COLD_SOURCE_DONE '+json.dumps(receipt),file=sys.stderr,flush=True)
finally:
    for child in [tar,zstd]:
        if child.poll() is None:child.terminate();child.wait()
    os.close(lock)
