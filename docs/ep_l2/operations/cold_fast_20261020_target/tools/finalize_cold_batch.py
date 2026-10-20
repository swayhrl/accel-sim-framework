"""Publish one cross-verified cold archive; never delete old174 data."""
import base64,hashlib,json,pathlib,sys
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import tls_target as t
tag=sys.argv[1];proof=json.loads((D/(tag+'_CROSS_VERIFIED.json')).read_bytes());C=proof['config']
verify=r'''#!/usr/bin/env python3
import gzip,hashlib,json,os,pathlib,stat,sys
here=pathlib.Path(__file__).resolve().parent;root=pathlib.Path(sys.argv[1]);count=0
with gzip.open(here/'MEMBER_SHA256_AND_METADATA.jsonl.gz','rt') as rows:
 for line in rows:
  r=json.loads(line);p=root/r['relative_path'];s=p.lstat()
  assert not p.is_symlink()
  assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(r['uid'],r['gid'],r['mode'],r['mtime_ns']),str(p)
  if r['type']=='regular':
   assert stat.S_ISREG(s.st_mode) and s.st_size==r['size'];h=hashlib.sha256()
   with p.open('rb') as f:
    while b:=f.read(1024**2):h.update(b)
   assert h.hexdigest()==r['sha256'],str(p)
  else:assert stat.S_ISDIR(s.st_mode)
  count+=1
print('ALL_RESTORED_CONTENT_AND_NUMERIC_METADATA_MATCH',count)
'''
restore='''#!/usr/bin/env bash
set -euo pipefail
[[ $# == 1 ]] || { echo "usage: $0 ABSENT_NATIVE_RESTORE_PARENT" >&2; exit 2; }
here=$(cd -- "$(dirname -- "$0")" && pwd)
dest=$1
[[ ! -e "$dest" && ! -L "$dest" ]] || { echo "restore destination must be ABSENT" >&2; exit 3; }
[[ $(id -u) == 0 ]] || { echo "root is required to restore original numeric UID/GID" >&2; exit 4; }
(cd -- "$here" && sha256sum -c ARCHIVE_SHA256SUMS)
mkdir -- "$dest"
zstd -dc -- "$here/postcheck.tar.zst" | tar -xpf - --numeric-owner --same-owner --acls --xattrs --selinux --delay-directory-restore -C "$dest"
python3 "$here/VERIFY_RESTORE.py" "$dest/postcheck"
'''
pathmap=dict(source_root=C['source_root'],archive_root_on_174new=C['target_root'],
             archive_root_native164=C['target_root'].replace('/root/share/mnt164','/home/shared',1),
             archive='postcheck.tar.zst',archive_top_level='postcheck',
             future_restore_path='ABSENT_NATIVE_RESTORE_PARENT/postcheck',
             Source_manifest='SOURCE_MANIFEST.jsonl.gz',content_manifest='MEMBER_SHA256_AND_METADATA.jsonl.gz',
             numeric_metadata='PAX tar plus full frozen Source sidecar; restore as root, original uid/gid/mode/mtime_ns',
             dev_inode_ctime='Source provenance, not recreated identities')
readme=('Run RESTORE.sh with one ABSENT destination on a capacity-qualified native filesystem. It verifies archive hashes, restores postcheck/ including empty directories and original numeric owners/modes/PAX nanosecond mtimes, then checks every restored file SHA and all numeric metadata.\n'
        'Requires bash, GNU tar, zstd, Python3 and root for numeric UID/GID. No RTL/signoff execution or simulator installation.\n'
        'Source original root: '+C['source_root']+'\nPersistent genuine164 root: '+pathmap['archive_root_native164']+'\n'
        'Scientific status is preserved in SOURCE_BINDING.json. This receipt never upgrades incomplete/signoff or timeout outcomes.\n'
        'Target has no Source deletion authority. BA/Source must separately check current readers/identity and approved exact release, journal actions and report measured df.\n')
files={'PATH_MAP.json':(json.dumps(pathmap,indent=2)+'\n').encode(),'RESTORE.sh':restore.encode(),
       'VERIFY_RESTORE.py':verify.encode(),'RECOVERY_POINTER.md':readme.encode(),
       'SOURCE_STREAM_COMPLETE.json':(json.dumps(proof['source'],indent=2)+'\n').encode()}
code=r'''
import pathlib,os,json,hashlib,fcntl,base64,sys,datetime,time,subprocess
proof=__PROOF__;C=proof['config'];base=pathlib.Path(C['target_root']);B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
sys.path.insert(0,'/root/tls-v10-native-restore-20261018-target01/test_tools/grouped_7155b810af658331');import v9_transaction as v9
assert hashlib.sha256(pathlib.Path(v9.__file__).read_bytes()).hexdigest()=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
v9.mount_identity(base);assert base.stat().st_dev==39
locks=[]
for n in ['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock']:
 f=os.open(B/n,os.O_RDONLY|os.O_NOFOLLOW);locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert proof['source_and_target_archive_and_decoded_tar_SHA_equal'] and proof['source']['frozen_metadata_before_after_exact']
p=base/'postcheck.tar.zst.partial';target=proof['target']
assert json.loads((base/'VERIFIED_PARTIAL.json').read_bytes())==target
throttle=v9.Throttle(8*1024**2);assert v9.hash_file(p,throttle=throttle)==proof['source']['archive_sha256']==target['archive_sha256']
assert p.stat().st_size==target['archive_bytes']
for src,dst in [('postcheck.tar.zst.partial','postcheck.tar.zst'),('MEMBER_SHA256_AND_METADATA.jsonl.gz.partial','MEMBER_SHA256_AND_METADATA.jsonl.gz')]:
 a=base/src;b=base/dst;assert not b.exists();v9.rename_noreplace(a,b)
for name,raw64 in __FILES__.items():
 raw=base64.b64decode(raw64);p=base/name;assert not p.exists()
 with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256(raw).hexdigest()
done=dict(schema='COLD_PROJECT_DURABLE164_DEST_VERIFIED_V1',status='DEST_VERIFIED_COLD_ARCHIVE_COMPLETE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          source_handoff_git_commit=proof['source_handoff_commit'],source_root=C['source_root'],target_root=str(base),
          native164_root=str(base).replace('/root/share/mnt164','/home/shared',1),
          archive_sha256=target['archive_sha256'],archive_bytes=target['archive_bytes'],tar_stream_sha256=target['tar_stream_sha256'],
          source_and_target_whole_compressed_and_decoded_tar_SHA_match=True,zstd_decode_and_frame_checksums_pass=True,
          all_frozen_files_empty_directories_and_numeric_metadata_verified=True,
          regular_files=target['regular_files'],directories_including_root=target['directories_including_root'],logical_bytes=target['logical_bytes'],
          BA_frozen_metadata_gzip_sha256=C['manifest_sha256'],member_content_and_metadata_manifest_sha256=target['member_manifest_sha256'],
          representative_native_restores=target['samples'],whole_tree_extraction_performed=False,
          source_originals='SOURCE_KEEP_PENDING_BA_EXACT_RELEASE_REVIEW',source_files_deleted_by_target=0,source_actual_df_reclaimed_bytes=0,
          persistent_copy_is_genuine164=True,bridge_payload_bytes=0,source_overlay_payload_scratch_bytes=0,
          independent_from_TLS_P9_and_E2=True,restore_command='bash RESTORE.sh /chosen/ABSENT_NATIVE_RESTORE_PARENT')
v9.exclusive_json(base/'DONE.json',done)
names=['postcheck.tar.zst','SOURCE_MANIFEST.jsonl.gz','SOURCE_BINDING.json','MEMBER_SHA256_AND_METADATA.jsonl.gz','VERIFIED_PARTIAL.json',*__FILES__.keys(),'DONE.json']
checks=[]
for name in names:checks.append(v9.hash_file(base/name,throttle=throttle)+'  '+name+'\n')
p=base/'ARCHIVE_SHA256SUMS'
with p.open('xb') as f:f.write(''.join(checks).encode());f.flush();os.fsync(f.fileno())
v9.fsync_dir(base)
result=dict(done=done,DONE_sha256=hashlib.sha256((base/'DONE.json').read_bytes()).hexdigest(),
            archive_checksums_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            PATH_MAP_sha256=hashlib.sha256((base/'PATH_MAP.json').read_bytes()).hexdigest(),
            RESTORE_sha256=hashlib.sha256((base/'RESTORE.sh').read_bytes()).hexdigest())
for f in locks:os.close(f)
print(json.dumps(result))
'''
for k,v in [('__PROOF__',proof),('__FILES__',{n:base64.b64encode(raw).decode() for n,raw in files.items()})]:code=code.replace(k,repr(v))
r=t.remote(code,'COLD_'+tag+'_DEST_VERIFIED_AND_RECOVERY_POINTER',timeout=300,save_receipt=False)
(D/(tag+'_DONE_RECEIPT.json')).write_bytes((json.dumps(r,indent=2)+'\n').encode())
for n,raw in files.items():(D/(tag+'_'+n)).write_bytes(raw)
print('DURABLE_DONE '+tag+' '+r['DONE_sha256'],flush=True)
