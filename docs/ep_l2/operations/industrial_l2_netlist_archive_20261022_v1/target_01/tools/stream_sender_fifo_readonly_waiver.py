
"""One bounded readonly Source stream. No source temp/copy/unlink."""
import pathlib,json,os,sys,hashlib,fcntl,time,importlib.util
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');T=B/'INDUSTRIAL_L2_9JSON_20261022_TARGET';P=json.loads((T/'TRANSFER_PLAN_STREAM_V2.json').read_bytes());S=B/'INDUSTRIAL_L2_9JSON_20261022_SOURCE'
raw=(S/'SOURCE_FROZEN_MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==P['source_manifest_sha256'];M=json.loads(raw);assert M['transaction_id']==P['transaction_id']
target_raw=(T/'TARGET_ARCHIVE_READY_STREAM_V2.json').read_bytes();assert hashlib.sha256(target_raw).hexdigest()==P['target_ready_sha256'];assert json.loads(target_raw)['transaction_id']==M['transaction_id']
mod=pathlib.Path('/workspace/worktrees/gpu-l2-netlist-copyonly-source-20261022/docs/ep_l2/operations/industrial_l2_netlist_archive_20261022_source/freeze_source.py');assert hashlib.sha256(mod.read_bytes()).hexdigest()==P['source_freeze_tool_sha256'];spec=importlib.util.spec_from_file_location('owner_freeze',mod);owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)

# Only this direct-user-approved readonly nine-file transaction waives workspace numeric floor.
import datetime
amraw=(T/'USER_WORKSPACE_READONLY_THRESHOLD_AMENDMENT.json').read_bytes();assert hashlib.sha256(amraw).hexdigest()=='2f4406e46ce799863762db56a57338a43c750f3df86902a32368edaaebcc6821';am=json.loads(amraw);assert am['transaction_id']==M['transaction_id'] and am['source_manifest_sha256']==P['source_manifest_sha256'] and am['workspace_numeric_floor_bytes'] is None
assert am['source_disposition']=='SOURCE_KEEP' and not am['source_delete_move_rewrite_or_large_temp_authorized']
def scoped_readonly_resources():
 assert os.readlink('/proc/self/ns/mnt')==M['transaction_binding']['source_fs_id']['namespace']
 w=os.statvfs('/workspace');sh=os.statvfs('/root/share');mem=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 assert os.stat('/workspace').st_dev==M['transaction_binding']['source_fs_id']['dev'] and w.f_fsid==M['transaction_binding']['source_fs_id']['fsid']
 assert sh.f_bavail*sh.f_frsize>=40*1024**3 and mem>=64*1024**3
 return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),namespace=os.readlink('/proc/self/ns/mnt'),workspace_f_bavail_bytes=w.f_bavail*w.f_frsize,workspace_numeric_floor='EXPLICIT_USER_WAIVED_FOR_THIS_READONLY_TX_ONLY',Share_available_bytes=sh.f_bavail*sh.f_frsize,MemAvailable_bytes=mem,amendment_sha256='2f4406e46ce799863762db56a57338a43c750f3df86902a32368edaaebcc6821',source_payload_staging_bytes=0)
owner.resources=scoped_readonly_resources

lock=(B/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);os.nice(19)
owner.resources();owner.activity(M['files'])
def event(j):print(json.dumps(j),file=sys.stderr,flush=True)
def control(name,j):
 data=(json.dumps(j,indent=2)+'\n').encode();p=S/name
 if p.exists():assert p.read_bytes()==data
 else:
  with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
fresh=owner.resources()
control('SOURCE_EXECUTION_COPY_READY_'+str(os.getpid())+'.json',dict(status='COPY_READY',transaction_id=M['transaction_id'],source_manifest_sha256=P['source_manifest_sha256'],target_ready_sha256=P['target_ready_sha256'],fresh_activity_verified=True,fresh_resources=fresh,source_action='SOURCE_KEEP',issued_by='readonly sender executing in original174 namespace before first byte'))
event(dict(event='SOURCE_EXECUTION_COPY_READY',txid=M['transaction_id'],fresh_resources=fresh,source_action='SOURCE_KEEP'))
skip=set(json.loads((T/'SKIP_VERIFIED_CHUNKS_AFTER_16G_HOLD.json').read_bytes())['keys']);total=0
for r in M['files']:
 p=pathlib.Path(r['absolute_path']);assert owner.parent_identity(p)==r['parents'];assert owner.fingerprint(p.lstat())==r['identity'];h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb',buffering=0) as f:
  assert owner.fingerprint(os.fstat(f.fileno()))==r['identity']
  for c in r['chunks']:
   if r['file_id']+':'+str(c['offset']) in skip:
    f.seek(c['offset']+c['length']);continue
   owner.resources();ch=hashlib.sha256();left=c['length'];n=0;start=time.monotonic()
   while left:
    b=f.read(min(1024**2,left));assert b;sys.stdout.buffer.write(b);sys.stdout.buffer.flush();h.update(b);ch.update(b);left-=len(b);n+=len(b);total+=len(b);time.sleep(max(0,n/(30*1024**2)-(time.monotonic()-start)))
   assert ch.hexdigest()==c['raw_sha256'];assert owner.fingerprint(os.fstat(f.fileno()))==r['identity'];owner.resources()
  assert not f.read(1) and owner.fingerprint(p.lstat())==r['identity']
  if not any(r['file_id']+':'+str(c['offset']) in skip for c in r['chunks']):assert h.hexdigest()==r['sha256']
 event(dict(event='SOURCE_FILE_SENT_KEEP',file_id=r['file_id'],source_expected_whole_sha256=r['sha256'],bytes_sent_this_phase=total))
for r in M['files']:assert owner.fingerprint(pathlib.Path(r['absolute_path']).lstat())==r['identity']
control('SOURCE_STREAM_COMPLETE_KEEP_SHARED_FIFO.json',dict(status='SOURCE_STREAM_COMPLETE_SOURCE_KEEP',transaction_id=M['transaction_id'],source_manifest_sha256=P['source_manifest_sha256'],files=9,bytes_sent=total,all_frozen_source_identities_intact=True,source_released_bytes=0))
event(dict(event='SOURCE_STREAM_COMPLETE_KEEP',bytes_sent=total))
