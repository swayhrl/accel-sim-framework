
import pathlib,json,os,sys,hashlib,fcntl,subprocess,datetime,stat
sys.dont_write_bytecode=True;os.nice(19)
subprocess.run(['ionice','-c','3','-p',str(os.getpid())],capture_output=True,check=True)
R=__READY__;W=__WINDOW__;M=__MANIFEST__;reserved=__RESERVED__;ready_sha=__PIN__;source_commit=__SOURCE_COMMIT__
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');base=pathlib.Path(M['destination_path_on_174new'])
tools=pathlib.Path('/root/tls-v10-native-restore-20261018-target01/test_tools/grouped_7155b810af658331')
pins=__PINS__
for n,h in pins.items():assert hashlib.sha256((tools/n).read_bytes()).hexdigest()==h
sys.path.insert(0,str(tools));import v9_transaction as v9;import tls_v10_grouped_ranges as grouped
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]';v9.mount_identity(base)
lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
raw=(B/__READY_FILENAME__).read_bytes();assert v9.digest(raw)==ready_sha
pub=json.loads((B/__PUBLICATION_FILENAME__).read_bytes());assert pub['source_git_commit']==source_commit and pub['source_ready_sha256']==ready_sha
assert pub['txid']==W['txid'] and pub['source_originals']=='SOURCE_KEEP'
assert v9.digest((B/__WINDOW_FILENAME__).read_bytes())==R['target_window_sha256']
assert v9.digest((base/'TARGET_TX_RESERVATION.json').read_bytes())==reserved['reservation_sha256']
assert v9.digest(v9.canonical(M))==W['canonical_manifest_sha256']
root=v9.no_symlinks(W['bridge_root']);assert root.is_dir() and root.stat().st_dev==2431
expected={pathlib.Path(e['bridge_path']) for e in R['entries']}
assert set(root.iterdir())==expected
active=[];allocated=0
for files in B.glob('*/files'):
 v9.no_symlinks(files);payload=[]
 for parent,dirs,names in os.walk(files,followlinks=False):
  for n in dirs+names:
   p=v9.no_symlinks(pathlib.Path(parent)/n);s=p.lstat();allocated+=s.st_blocks*512
   if not stat.S_ISDIR(s.st_mode):
    assert stat.S_ISREG(s.st_mode) and s.st_nlink==1;payload.append(p)
 if payload:active.append((files,set(payload)))
assert active==[(root,expected)]
allocated+=(root.lstat().st_blocks+root.parent.lstat().st_blocks)*512
allocated+=sum(p.lstat().st_blocks*512 for p in B.glob('TLS_V10*.json') if p.is_file() and not p.is_symlink())
assert allocated<=256*1024**2
assert sum(p.lstat().st_blocks*512 for p in expected)==R['bridge_payload_allocated_bytes']
sv=os.statvfs(B);share=sv.f_bavail*sv.f_frsize;assert share>=40*1024**3
mem=int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
cg=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())-int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
assert mem-R['raw_bytes']>=64*1024**3 and cg>=R['raw_bytes']
N=pathlib.Path('/root/tls-v10-native-restore-20261018-target01');nsv=os.statvfs(N);assert nsv.f_bavail*nsv.f_frsize>=R['raw_bytes']
T=v9.Transaction(base,M)
T.transition('DISCOVERED',dict(group=W['group'],source_root=M['source_root']))
T.transition('SOURCE_FROZEN',dict(source_manifest_sha256=reserved['canonical_manifest_sha256'],source_inventory_commit=reserved['source_frozen_commit'],source_binding_commit=reserved['source_binding_commit']))
T.transition('COPY_READY',dict(selector_sha256=M['selector_sha256'],source_originals='SOURCE_KEEP',admission_policy_id=R['policy_id']))
accepted=grouped.accept_group(T,W,R['entries'],native_parent=N/'chunk_proofs')
dest_rows=[];native_rows=[]
for e,src in zip(accepted['entries'],R['entries']):
 want=e['range'];native=e['native_proof']['receipt'];path=pathlib.Path(native['native_payload']).parent/'RESTORE_RECEIPT.json'
 dest_rows.append(dict(relative_path=want['relative_path'],offset=want['offset'],length=want['length'],original_size=want['original_size'],source_full_sha256=want['original_sha256'],source_identity=src['source_identity'],chunk_sha256=src['chunk_sha256'],bridge_path=e['bridge_path'],bridge_identity=e['bridge_identity'],archived_chunk_path=e['archive_chunk'],archived_close_reopen_sha256=src['chunk_sha256'],reused_existing_archive_chunk=e['reused_archive_chunk']))
 native_rows.append(dict(relative_path=want['relative_path'],offset=want['offset'],length=want['length'],chunk_sha256=src['chunk_sha256'],native_chunk_proof=e['native_proof'],native_restore_receipt_path=str(path),native_restore_receipt_sha256=v9.digest(path.read_bytes())))
records=[json.loads(p.read_bytes()) for p in (T.work/'chunks').glob('*.json')]
covered=0
for row in M['files']:
 if row['size']==0:continue
 rs=sorted((r for r in records if r['relative_path']==row['relative_path']),key=lambda r:r['offset']);off=0;ok=True
 for r in rs:
  if r['offset']!=off:ok=False;break
  off+=r['size']
 if ok and off==row['size']:covered+=1
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
common=dict(utc=now,window_id=W['window_id'],group=W['group'],txid=T.txid,selector_sha256=M['selector_sha256'],canonical_manifest_sha256=W['canonical_manifest_sha256'],target_window_git_commit=R['target_window_git_commit'],target_window_sha256=R['target_window_sha256'],source_ready_git_commit=source_commit,source_ready_sha256=ready_sha,source_gate_sha256=R['source_gate_sha256'],source_protocol_adoption_sha256=R['source_protocol_adoption_sha256'],source_originals='SOURCE_KEEP',source_files_deleted_by_target=0,science_source_release_bytes=0,proof_scope='COLLECTION_OF_CHUNK_RANGES',full_group_archived=False,full_group_native_restored=False,range_count=len(dest_rows),raw_bytes=R['raw_bytes'],await_source_signed_SOURCE_KEEP_ACK=True)
dest=dict(schema='TLS_V10_TARGET_GROUPED_DEST_VERIFIED_COPY16_V1',status='DEST_VERIFIED',**common,entries=dest_rows,genuine164_mount_verified=True,native164_base=M['genuine164_destination_root'],actual_all_bridge_payload_directory_and_TLS_control_allocated_bytes=allocated,Share_available_bytes=share,MemAvailable_bytes=mem,cgroup_headroom_bytes=cg,one_receiver_lock=True,reused_chunks=sum(e['reused_existing_archive_chunk'] for e in dest_rows),nonempty_originals_with_complete_verified_range_coverage=covered,total_accepted_ranges_in_transaction=len(records))
restore=dict(schema='TLS_V10_TARGET_GROUPED_RESTORE_VERIFIED_COPY16_V1',status='RESTORE_VERIFIED',**common,entries=native_rows,independent_actual_native_restore=True,numeric_metadata_verified_every_range=True,native_full_group_file_restore_count=0)
os.close(lock)
print(json.dumps(dict(schema='TLS_V10_EXISTING_GROUPED_RECEIVER_RESULT_V1',dest=dest,restore=restore,accepted_vector=accepted,source_originals='SOURCE_KEEP',new_flow=False)))
