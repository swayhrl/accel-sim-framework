"""Stream to genuine164 partial; fully inspect tar without a full extraction.

Only a later Source/Target cross-check may publish the final archive filename.
"""
import decimal,fcntl,gzip,hashlib,json,os,pathlib,stat,subprocess,sys,tarfile,time

config=json.loads(sys.argv[1]);base=pathlib.Path(config['target_root']);B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
N=pathlib.Path('/root/tls-v10-native-restore-20261018-target01');rate=30*1024**2
limited_existing=(config.get('validation_only') is True and
                  config.get('bounded_existing_small_V3_validation') is True)
if limited_existing:
    assert config['source_root'] in [
        '/workspace/worktrees/gpu-l2-v3-signoff-463600cb/build/postcheck',
        '/workspace/worktrees/gpu-l2-v3-signoff-46bf3a69/build/postcheck']
    assert 0<config['expected_archive_bytes']<=256*1024**2
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
assert str(base).startswith('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/cold_projects/20261020/')
def real164():
    m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(base),'-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
    assert (m['target'],m['source'],m['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs') and base.stat().st_dev==39
    return m
def digest(p):
    h=hashlib.sha256();start=time.monotonic();total=0
    with p.open('rb') as f:
        while data:=f.read(1024**2):
            h.update(data);total+=len(data);time.sleep(max(0,total/(8*1024**2 if limited_existing else rate)-(time.monotonic()-start)))
    return h.hexdigest()
def guard():
    s=os.statvfs(B);assert s.f_bavail*s.f_frsize>=40*1024**3
    mem=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
    assert mem>=64*1024**3
    c=pathlib.Path('/sys/fs/cgroup/memory.max');limit=c.read_text().strip()
    assert limit=='max' or int(limit)-int(c.with_name('memory.current').read_text())>=512*1024**2
    held=time.monotonic()
    pressure_file=pathlib.Path('/sys/fs/cgroup/io.pressure' if limited_existing else '/proc/pressure/io')
    while float(pressure_file.read_text().splitlines()[0].split()[1].split('=')[1])>10:
        assert time.monotonic()-held<=30,'existing IO guard10 HOLD >30s; preserve verified input'
        time.sleep(5)
    assert os.statvfs(base).f_bavail*os.statvfs(base).f_frsize>=1024**3

lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
mount=real164();guard();os.nice(19);subprocess.run(['ionice','-c','3','-p',str(os.getpid())],check=True)
manifest=base/'SOURCE_MANIFEST.jsonl.gz';assert digest(manifest)==config['manifest_sha256']
rows={r[0]:r for r in (json.loads(l) for l in gzip.decompress(manifest.read_bytes()).splitlines())}
assert len(rows)==config['entries']
archive=base/'postcheck.tar.zst.partial';assert not (base/'postcheck.tar.zst').exists(),'final exists: reconcile without receiving'
if config.get('validation_only'):
    assert archive.is_file() and not archive.is_symlink()
    count=archive.stat().st_size;closed_sha=digest(archive)
    assert closed_sha==config['expected_archive_sha256'] and count==config['expected_archive_bytes']
else:
    assert not archive.exists(),'owned partial exists: reconcile, never overwrite'
    print('COLD_TARGET_READY '+json.dumps({'base':str(base),'mount':mount}),file=sys.stderr,flush=True)
    h=hashlib.sha256();count=0;last=time.monotonic();start=last
    with archive.open('xb') as out:
        while data:=sys.stdin.buffer.read(1024**2):
            if time.monotonic()-last>5:guard();real164();last=time.monotonic()
            out.write(data);h.update(data);count+=len(data)
            time.sleep(max(0,count/rate-(time.monotonic()-start)))
        out.flush();os.fsync(out.fileno())
    closed_sha=digest(archive);assert closed_sha==h.hexdigest()
guard()
zstd=pathlib.Path(config['zstd']);assert zstd.is_file()
decoder=subprocess.Popen([str(zstd),'-dc','--',str(archive)],stdout=subprocess.PIPE,stderr=sys.stderr.buffer)
class TarReader:
    def __init__(self,stream):self.stream=stream;self.hash=hashlib.sha256();self.count=0;self.started=time.monotonic();self.last=0
    def read(self,n=-1):
        if time.monotonic()-self.last>5:guard();self.last=time.monotonic()
        data=self.stream.read(n);self.hash.update(data);self.count+=len(data)
        time.sleep(max(0,self.count/rate-(time.monotonic()-self.started)))
        return data
reader=TarReader(decoder.stdout);seen=set();files=dirs=logical=0
sample_names=config['sample_paths'];samples=[]
sample_root=N/'cold_restore_samples'/config.get('sample_run_tag',config['tag']);sample_root.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
assert not os.path.lexists(sample_root),'sample root must be ABSENT'
sample_root.mkdir(mode=0o700)
member_path=base/'MEMBER_SHA256_AND_METADATA.jsonl.gz.partial'
assert not member_path.exists()
with member_path.open('xb',buffering=1024**2) as rawout:
    with gzip.GzipFile(fileobj=rawout,mode='wb',mtime=0) as member_out:
        with tarfile.open(fileobj=reader,mode='r|') as tf:
            for item in tf:
                name=item.name.rstrip('/')
                assert name=='postcheck' or name.startswith('postcheck/')
                rel='.' if name=='postcheck' else name[len('postcheck/'):]
                assert rel=='.' or not pathlib.PurePosixPath(rel).is_absolute() and '..' not in pathlib.PurePosixPath(rel).parts
                assert rel in rows and rel not in seen,'unexpected/duplicate member '+rel
                seen.add(rel);r=rows[rel]
                kind='directory' if item.isdir() else 'regular' if item.isfile() else 'OTHER'
                assert kind==r[1] and kind in ['regular','directory']
                assert item.mode==stat.S_IMODE(r[5]) and item.uid==r[6] and item.gid==r[7]
                ns=int(decimal.Decimal(item.pax_headers.get('mtime',str(item.mtime)))*1000000000)
                assert ns==r[10], 'mtime_ns mismatch '+rel
                sha=None
                if kind=='regular':
                    assert item.size==r[8];f=tf.extractfile(item);fh=hashlib.sha256();n=0
                    want_sample=rel in sample_names
                    if want_sample:
                        assert r[8]<=65536
                        p=sample_root/rel;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True);dest=p.open('xb')
                    while chunk:=f.read(1024**2):
                        fh.update(chunk);n+=len(chunk)
                        if want_sample:dest.write(chunk)
                    assert n==r[8];sha=fh.hexdigest();files+=1;logical+=n
                    if want_sample:
                        dest.flush();os.fsync(dest.fileno());dest.close();os.chown(p,r[6],r[7]);os.chmod(p,stat.S_IMODE(r[5]));os.utime(p,ns=(r[10],r[10]));s=p.stat()
                        assert digest(p)==sha and (s.st_size,s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(r[8],r[6],r[7],stat.S_IMODE(r[5]),r[10])
                        samples.append(dict(relative_path=rel,native_path=str(p),size=n,sha256=sha,numeric_metadata_verified=True))
                else:dirs+=1
                line=dict(relative_path=rel,type=kind,size=r[8] if kind=='regular' else 0,uid=r[6],gid=r[7],mode=stat.S_IMODE(r[5]),mtime_ns=r[10],sha256=sha)
                member_out.write((json.dumps(line,separators=(',',':'))+'\n').encode())
                tf.members.clear()
        while reader.read(1024**2):pass
    rawout.flush();os.fsync(rawout.fileno())
assert decoder.wait()==0,'zstd frame/checksum validation failed'
assert seen==set(rows) and files==config['files'] and dirs==config['directories'] and logical==config['logical_bytes']
assert {s['relative_path'] for s in samples}==set(sample_names)
result=dict(schema='COLD_TARGET_VERIFIED_PARTIAL_V1',status='VERIFIED_PARTIAL_PENDING_SOURCE_COMPLETION_CROSSCHECK',tag=config['tag'],
            source_root=config['source_root'],target_root=str(base),genuine164_mount=mount,archive_partial=str(archive),
            archive_sha256=closed_sha,archive_bytes=count,tar_stream_sha256=reader.hash.hexdigest(),tar_stream_bytes=reader.count,
            all_BA_frozen_members_and_numeric_metadata_match=True,regular_files=files,directories_including_root=dirs,logical_bytes=logical,
            source_metadata_manifest_sha256=config['manifest_sha256'],member_manifest_sha256=digest(member_path),
            samples=samples,sample_native_filesystem='qualified174-new tmpfs; volatile verification only',
            verification_IO_mode='EXISTING_SMALL_V3_ARCHIVE_MAX256MiB_NATIVE_CGROUP_IO10_8MiB_HASH_1MiB_BUFFER' if limited_existing else 'ORIGINAL_HOST_IO10',
            observed_host_IO_at_completion=pathlib.Path('/proc/pressure/io').read_text(),
            observed_target_cgroup_IO_at_completion=pathlib.Path('/sys/fs/cgroup/io.pressure').read_text(),
            persistent_archive_is_genuine164=True,source_originals='SOURCE_KEEP',source_files_deleted=0,source_released_bytes=0)
p=base/'VERIFIED_PARTIAL.json';assert not p.exists()
with p.open('xb') as f:f.write((json.dumps(result,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
os.close(lock);print(json.dumps(result),flush=True)
