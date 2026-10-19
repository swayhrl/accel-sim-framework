'''Finalize the existing P9 transaction and prove all141 files from genuine164.
Uses unchanged qualified V9 and full-index tools; never a Source release tool.
'''
import json,sys,pathlib,subprocess
import tls_target as t
M=t.get('SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json')
reserved=t.get('TLS_V10_P9_PUBLIC_TARGET_ROOT_RESERVED.json');plan=t.get('TLS_V10_P9_PUBLIC_INACTIVE_BATCHING_PROPOSAL_AFTER_B0001.json')
t.require_tls_restore_location('TLS_V10_P9_PUBLIC_B0033')
closed=[]
for num in range(1,34):
 wid='TLS_V10_P9_PUBLIC_B%04d'%num;p=t.BASE/(wid+'_BRIDGE_CLEANUP_COPY16.json')
 if p.exists():
  c=json.loads(p.read_bytes());assert c['txid']==reserved['txid'] and c['source_originals']=='SOURCE_KEEP'
  if num==1:assert c['schema']=='TLS_V10_B0001_EXACT_BRIDGE_CLEANUP_DONE_V1' and c['archive_and_native_proof_reopened_SHA_match'] is True
  else:assert c['archive_and_native_every_range_reverified'] is True
  closed.append(wid)
summary=dict(original_file_count=len(M['files']),original_directory_count=len(M['directories']),original_bytes=sum(x['size'] for x in M['files']),closed_windows=len(closed),required_windows=33,canonical_approval_commit='9f1a21a909e437f1e34233b22595d0f7359f3dd3',unchanged_core_SHA=t.sha(t.BASE/'tools'/'v9_transaction.py'),unchanged_full_index_SHA=t.sha(t.BASE/'tools'/'tls_v10_full_restore_index.py'),source_files_deleted=0)
assert len(M['files'])==141 and len(M['directories'])==4 and summary['original_bytes']==2897196811
if '--execute-after-all33-closed' not in sys.argv:
 print(json.dumps(dict(summary,plan_only=True,remote_payload_IO=False),indent=2));raise SystemExit(0)
assert len(closed)==33,'Not all original33 windows closed; no remote payload action'
# Read Source registry only, never alter the campaign/leases or execute its sender.
source_probe=r'''
import os,pathlib,json,hashlib,datetime
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
p=pathlib.Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');s=p.stat();assert s.st_size<8*1024**2;b=p.read_bytes();assert p.stat().st_mtime_ns==s.st_mtime_ns
r=json.loads(b);a=[dict(id=k,**v) for k,v in r['resource_leases'].items() if v.get('status') not in ['RELEASED','CANCELLED','EXPIRED','CLOSED']]
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registry_sha256=hashlib.sha256(b).hexdigest(),active_leases=a)))
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','hrl','timeout 20s python3 -B -'],input=source_probe.encode(),capture_output=True,check=True,timeout=30)
source=json.loads(p.stdout);assert not source['active_leases'],'SOURCE_ACTIVE_LEASE_HOLD_BEFORE_FULL_RESTORE'
code=r'''
import sys,os,pathlib,json,hashlib,datetime,fcntl,subprocess,stat,time
sys.dont_write_bytecode=True
N=pathlib.Path('/root/tls-v10-native-restore-20261018-target01');TOOLS=N/'test_tools/full_index_f80c8559dcefec69'
assert hashlib.sha256((TOOLS/'v9_transaction.py').read_bytes()).hexdigest()=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
assert hashlib.sha256((TOOLS/'tls_v10_full_restore_index.py').read_bytes()).hexdigest()=='f80c8559dcefec69bbf5def495522deb7db1f2e9a1a0660b548ac15aa28564a2'
sys.path.insert(0,str(TOOLS));import v9_transaction as v9;import tls_v10_full_restore_index as full
M=__MANIFEST__;txid=__TXID__;B=pathlib.Path(__BRIDGE__);base=pathlib.Path(M['destination_path_on_174new']);approval='9f1a21a909e437f1e34233b22595d0f7359f3dd3'
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]';v9.mount_identity(base);assert v9.validate_manifest(M)==txid
native_mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(N),'-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
assert (native_mount['target'],native_mount['source'],native_mount['fstype'])==(str(N),'tls-v10-target-native-proof','tmpfs')
lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not [p for p in B.glob('*/files') if any(q.is_file() for q in p.rglob('*'))]
reserve=1073741824;memfloor=64*1024**3;sharefloor=40*1024**3
progress=N/'P9_FULL_RECOVERY_PROGRESS.json';started=time.monotonic();phase='PREFLIGHT';observed=0;last_check=0

def check():
 global last_check
 sv=os.statvfs(B);ns=os.statvfs(N);mem=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cm=pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip();cc=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
 assert sv.f_bavail*sv.f_frsize>=sharefloor and mem>=memfloor and ns.f_bavail*ns.f_frsize>=reserve
 assert cm=='max' or int(cm)-cc>=64*1024**2
 m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(base),'-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
 assert (m['target'],m['source'],m['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs')
 row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,throttled_IO_bytes=observed,elapsed_seconds=time.monotonic()-started,Share_free=sv.f_bavail*sv.f_frsize,native_free=ns.f_bavail*ns.f_frsize,MemAvailable=mem,cgroup_current=cc)
 tmp=progress.with_suffix('.writing');tmp.write_bytes(v9.canonical(row));os.replace(tmp,progress);last_check=time.monotonic();return row
original_throttle=v9.Throttle.__call__
def guarded_throttle(self,size):
 global observed
 original_throttle(self,size);observed+=size
 if time.monotonic()-last_check>5:check()
v9.Throttle.__call__=guarded_throttle
before=check();payload=sum(r['size'] for r in M['files']);assert before['native_free']>=payload+reserve and before['MemAvailable']-payload-reserve>=memfloor
T=v9.Transaction(base,M)
# Validate exact current durable range coverage before making any assembled file.
records=[json.loads(p.read_bytes()) for p in (T.work/'chunks').glob('*.json')]
if not (T.final/'COMMIT.json').exists():
 assert len(records)==156
 for row in M['files']:
  parts=sorted((x for x in records if x['relative_path']==row['relative_path']),key=lambda x:x['offset']);offset=0
  for x in parts:assert x['txid']==txid and x['offset']==offset and x['size']>0;offset+=x['size']
  assert offset==row['size']
T.transition('ARCHIVE_STAGED',dict(range_count=156,original_file_count=141,logical_bytes=2897196811,all33windows_closed=True,source_originals='SOURCE_KEEP'))
phase='ASSEMBLE_AND_COMMIT_GENUINE164_FULL_ARCHIVE';check();archive=T.finalize();tree=archive/'tree'
T.transition('ARCHIVE_VERIFIED',dict(original_file_count=141,logical_bytes=2897196811,manifest_sha256=v9.digest(v9.canonical(M)),commit_sha256=v9.digest((archive/'COMMIT.json').read_bytes()),full_file_SHA_verified=True,genuine164=True))
parent=N/'full_groups'/txid;native=parent/'tree';v9.no_symlinks(parent);parent_was_present=os.path.lexists(parent)
if not parent_was_present:parent.parent.mkdir(mode=0o700,exist_ok=True);parent.mkdir(mode=0o700)
reservation=dict(schema='TLS_V10_FULL_NATIVE_RESTORE_RESERVATION_V1',txid=txid,manifest_sha256=v9.digest(v9.canonical(M)),native_tree=str(native),destination_absent_before_restore=True,source_originals='SOURCE_KEEP')
rp=parent/'RESTORE_RESERVATION.json'
if not rp.exists():assert not parent_was_present and not os.path.lexists(native),'Unowned existing full restore parent: HOLD';v9.exclusive_json(rp,reservation)
else:assert rp.read_bytes()==v9.canonical(reservation)
phase='FULL141_RESTORE_FROM_GENUINE164_TO_NATIVE_ABSENT';check()
if not os.path.lexists(native):native_receipt=v9.native_restore(tree,M,native)
else:native_receipt=dict(status='EXISTING_OWNED_NATIVE_TREE_REQUIRES_FULL_INDEPENDENT_REAUDIT_NO_OVERWRITE')
phase='INDEPENDENT_FULL141_SHA_SIZE_NUMERIC_METADATA_AND4DIR_AUDIT';check();index=full.audit_full_restore(M,txid,tree,native)
assert index['file_count']==141 and index['directory_count']==4 and index['original_logical_bytes']==2897196811 and index['full_file_SHA_and_numeric_metadata_verified']
v9.exclusive_json(parent/'ALL_FILES_RESTORE_INDEX.json',index)
v9.exclusive_json(base/'TLS_V10_P9_PUBLIC_FULL141_ARCHIVE_NATIVE_RESTORE_INDEX.json',index)
certificate_path=base/'TLS_V10_P9_PUBLIC_ALL141_ARCHIVE_AND_NATIVE_RESTORE_PASS.json'
certificate=dict(schema='TLS_V10_P9_PUBLIC_ALL141_ARCHIVE_AND_NATIVE_RESTORE_PASS_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical_approval_commit=approval,txid=txid,selector_sha256=M['selector_sha256'],status='P9_ALL141_TRUE164_NATIVE_RESTORE_PASS',native_restore_execution_host='huangrulin-sshfs-174',native_mount=native_mount,native_proof_is_volatile=True,durable_archive_is_genuine164=True,restoration_read_source='GENUINE164_COMMITTED_FULL_TREE_NOT_BRIDGE_OR_OLD174',fresh_ABSENT_restore_reservation=reservation,index=index,native_core_restore=native_receipt,source_originals='SOURCE_KEEP',target_source_unlink_authority=False,source_current_readers_SHA_identity_resource_and_release_journal_independently_required=True,source_actual_reclaimed_bytes=0)
if certificate_path.exists():
 old=json.loads(certificate_path.read_bytes());assert old['index']==index and old['txid']==txid and old['canonical_approval_commit']==approval;certificate=old
else:v9.exclusive_json(certificate_path,certificate)
assert v9.digest(certificate_path.read_bytes())==v9.digest(v9.canonical(certificate))
T.transition('RESTORE_VERIFIED',dict(file_count=141,directory_count=4,native_tree=str(native),full_content_and_numeric_metadata=True,certificate_sha256=v9.digest(certificate_path.read_bytes()),canonical_approval_commit=approval,source_originals='SOURCE_KEEP'))
phase='COMPLETE_ALL141_FULL_CONTENT_METADATA4_AND_DURABLE164_CERTIFICATE';after=check()
print(json.dumps(dict(certificate=certificate,certificate_sha256=v9.digest(certificate_path.read_bytes()),certificate_path=str(certificate_path),before=before,after=after,source_files_deleted=0)))
'''
for key,value in [('__MANIFEST__',M),('__TXID__',reserved['txid']),('__BRIDGE__',t.BRIDGE)]:code=code.replace(key,repr(value))
r=t.remote(code,'TLS_V10_P9_PUBLIC_FULL141_FINALIZATION_AND_RESTORE_RESULT_V1',1800)
canonical=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+chr(10)).encode()
(t.BASE/'TLS_V10_P9_PUBLIC_ALL141_ARCHIVE_AND_NATIVE_RESTORE_PASS.json').write_bytes(canonical(r['certificate']))
assert t.sha(t.BASE/'TLS_V10_P9_PUBLIC_ALL141_ARCHIVE_AND_NATIVE_RESTORE_PASS.json')==r['certificate_sha256']
(t.BASE/'TLS_V10_P9_PUBLIC_FULL141_ARCHIVE_NATIVE_RESTORE_INDEX.json').write_bytes(canonical(r['certificate']['index']))
print('FULL141_CERT_SHA',t.sha(t.BASE/'TLS_V10_P9_PUBLIC_ALL141_ARCHIVE_AND_NATIVE_RESTORE_PASS.json'))
