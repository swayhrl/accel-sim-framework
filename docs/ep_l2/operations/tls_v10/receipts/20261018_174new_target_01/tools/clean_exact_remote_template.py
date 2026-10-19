
import os,sys,pathlib,json,stat,fcntl,datetime
sys.dont_write_bytecode=True
sys.path.insert(0,'/root/tls-v10-native-restore-20261018-target01/test_tools/grouped_7155b810af658331')
import v9_transaction as v9
A=__ACK__;D=__DEST__;R=__RESTORE__;W=__WINDOW__;pin=__PIN__;commit=__COMMIT__
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
root=v9.no_symlinks(W['bridge_root']);assert root==B/(W['window_id']+'_574747b05622')/'files'
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ackfile=B/(W['window_id']+'_SOURCE_KEEP_ACK.json');assert v9.digest(ackfile.read_bytes())==pin
pub=json.loads((B/(W['window_id']+'_SOURCE_KEEP_ACK_PUBLICATION.json')).read_bytes())
assert pub['source_git_commit']==commit and pub['source_keep_ack_sha256']==pin and pub['range_count']==len(D['entries'])
assert pub.get('target_dest_restore_git_commit',A['target_dest_restore_git_commit'])==A['target_dest_restore_git_commit']
assert set(root.iterdir())=={pathlib.Path(e['bridge_path']) for e in D['entries']}
assert set(root.parent.iterdir())=={root}
throttle=v9.Throttle();native=[];total=0
for permission,d,r in zip(A['bridge_payload_exact_cleanup_permissions'],D['entries'],R['entries']):
 p=v9.no_symlinks(d['bridge_path']);assert p.parent==root
 assert v9.identity(p.lstat())==d['bridge_identity']
 assert v9.hash_file(p,expected=d['bridge_identity'],throttle=throttle)==d['chunk_sha256']==permission['sha256']
 chunk=v9.no_symlinks(d['archived_chunk_path']);v9.mount_identity(chunk)
 assert v9.hash_file(chunk,throttle=throttle)==d['chunk_sha256']
 proof=v9.no_symlinks(r['native_restore_receipt_path']);assert v9.digest(proof.read_bytes())==r['native_restore_receipt_sha256']
 info=r['native_chunk_proof']['receipt'];np=v9.no_symlinks(info['native_payload']);s=np.lstat()
 assert v9.hash_file(np,throttle=throttle)==d['chunk_sha256']
 assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==tuple(info['numeric_metadata'][k] for k in ['uid','gid','mode','mtime_ns'])
 total+=p.lstat().st_blocks*512
before=os.statvfs(B);before_free=before.f_bavail*before.f_frsize;assert before_free>=40*1024**3
journal=B/(W['window_id']+'_BRIDGE_CLEANUP_JOURNAL_COPY16.jsonl')
assert not journal.exists(),'Existing exact bridge journal: HOLD for bounded reconciliation, never blind repeat'
v9.journal_append(journal,dict(event='BEGIN',window_id=W['window_id'],txid=W['txid'],source_ACK_git_commit=commit,source_ACK_sha256=pin,exact_files=len(D['entries']),source_original_unlink=False))
parent=root.lstat();fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
removed=[]
try:
 assert (os.fstat(fd).st_dev,os.fstat(fd).st_ino)==(parent.st_dev,parent.st_ino)
 for d in D['entries']:
  p=pathlib.Path(d['bridge_path']);expected=d['bridge_identity']
  assert v9.digest(ackfile.read_bytes())==pin
  assert v9.identity(os.stat(p.name,dir_fd=fd,follow_symlinks=False))==expected
  v9.journal_append(journal,dict(event='INTENT',window_id=W['window_id'],txid=W['txid'],path=str(p),identity=expected,sha256=d['chunk_sha256'],source_ACK_sha256=pin,parent_identity=dict(dev=parent.st_dev,inode=parent.st_ino)))
  assert v9.identity(os.stat(p.name,dir_fd=fd,follow_symlinks=False))==expected
  os.unlink(p.name,dir_fd=fd);os.fsync(fd)
  assert not os.path.lexists(p)
  v9.journal_append(journal,dict(event='DONE',window_id=W['window_id'],txid=W['txid'],path=str(p)))
  removed.append(str(p))
finally:os.close(fd)
root.rmdir();root.parent.rmdir();v9.fsync_dir(B)
v9.journal_append(journal,dict(event='COMPLETE',window_id=W['window_id'],txid=W['txid'],removed_files=len(removed),source_files_deleted=0))
after=os.statvfs(B)
result=dict(schema='TLS_V10_GROUPED_EXACT_BRIDGE_CLEANUP_DONE_COPY16_V1',status=W['window_id'].rsplit('_',1)[-1]+'_CLOSED_EXACT_ACKNOWLEDGED_BRIDGE_PAYLOADS_CLEANED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),window_id=W['window_id'],txid=W['txid'],selector_sha256=W['selector_sha256'],source_ACK_git_commit=commit,source_ACK_sha256=pin,source_ACK_Git_bridge_raw_match=True,target_proof_git_commit=A['target_dest_restore_git_commit'],target_dest_receipt_sha256=A['target_dest_receipt_sha256'],target_restore_receipt_sha256=A['target_native_restore_receipt_sha256'],removed_bridge_files=removed,removed_count=len(removed),removed_bridge_payload_allocated_bytes=total,exact_empty_staging_directories_removed=[str(root),str(root.parent)],archive_and_native_every_range_reverified=True,fsynced_INTENT_before_each_unlink_and_DONE_after=True,journal_path=str(journal),journal_sha256=v9.digest(journal.read_bytes()),Share_available_before_bytes=before_free,Share_available_after_bytes=after.f_bavail*after.f_frsize,Share_measured_endpoint_delta_bytes=after.f_bavail*after.f_frsize-before_free,source_originals='SOURCE_KEEP',source_files_deleted_by_target=0,science_source_workspace_release_bytes=0,next_window_requires_new_exact_request_and_fresh_source_gate=True,new_source_payload_requested_or_staged=False)
v9.exclusive_json(B/(W['window_id']+'_BRIDGE_CLEANUP_DONE_COPY16.json'),result);v9.fsync_dir(B)
os.close(lock)
print(json.dumps(result))
