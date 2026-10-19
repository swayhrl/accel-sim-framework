import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import tls_target as t

SRC = t.META / 'source_c0ee7b1'
READY_COMMIT = 'e6199c059b52d8ad08eed90c6f0438e42250b431'
GATE_COMMIT = 'c2c40c6b0538d2f71bd81783bfa729ac54c8f174'
PRE = 'docs/ep_l2/operations/tls_v10_174_to_164_source/'
BARE = 'D:/repo/storage-ops-174new-164-exec-v1/.git/source-evidence.git'
ready_name = 'TLS_V10_P9_PUBLIC_B0001_SOURCE_READY_COPY16.json'
gate_name = 'TLS_V10_COPY_ONLY_16G_GATE_PASS_B0001.json'
test_name = 'TLS_V10_COPY_ONLY_16G_POLICY_TEST_RECEIPT.json'


def load(name):
    return json.loads((SRC / name).read_bytes())


ready = load(ready_name)
gate = load(gate_name)
tests = load(test_name)
manifest = t.get('SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json')
request = t.get('TLS_V10_P9_PUBLIC_TARGET_SOLE_WINDOW_READY.json')
reserved = t.get('TLS_V10_P9_PUBLIC_TARGET_ROOT_RESERVED.json')
for commit, name in [(READY_COMMIT, ready_name), (GATE_COMMIT, gate_name)]:
    raw = subprocess.check_output(['git', '--git-dir=' + BARE, 'show', commit + ':' + PRE + name])
    assert raw == (SRC / name).read_bytes()
assert tests['passed'] == 45 and tests['failed'] == 0
assert len(tests['synthetic_cases']) == 45
assert all(c['pass'] is True and c['expected'] == c['observed'] for c in tests['synthetic_cases'])
assert tests['gate_code_sha256'] == t.sha(SRC / 'tls_v10_copy_only16g_gate.py')
assert tests['test_code_sha256'] == t.sha(SRC / 'test_tls_v10_copy_only16g_gate.py')
assert tests['original_default_floor_bytes_unchanged'] == 48 * 1024**3
assert tests['authority_sha256'] == '745fb24b603627b63bc43a1cb130a9e61038d23adee618e2850e3d80755c7bf1'
assert tests['user_approval_sha256'] == '789528e6dd4e7b51c3a437e14f8a9b3df1045bfa5e1eefc71974b3324ce9b61d'
assert ready['schema'] == 'TLS_V10_P9_PUBLIC_B0001_OLD174_SOURCE_READY_COPY16_V1'
assert ready['status'] == 'READY_SOURCE_KEEP'
assert ready['source_originals'] == 'SOURCE_KEEP' and ready['source_unlink_count'] == 0
for field in ['window_id', 'txid', 'group', 'selector_sha256', 'canonical_manifest_sha256', 'source_root']:
    assert ready[field] == request[field]
assert ready['target_request_sha256'] == t.sha(t.BASE / 'TLS_V10_P9_PUBLIC_TARGET_SOLE_WINDOW_READY.json')
assert ready['target_root_native164'] == manifest['genuine164_destination_root']
assert ready['source_gate_git_commit'] == GATE_COMMIT
assert ready['source_gate_sha256'] == t.sha(SRC / gate_name)
assert gate['status'] == 'COPY_ONLY_16G_GATE_PASS_NOT_READY'
assert gate['test_receipt_sha256'] == t.sha(SRC / test_name)
for field in ['relative_path', 'offset', 'length']:
    assert ready[field] == request['range'][field]
assert ready['source_full_sha256'] == request['range']['original_full_sha256']
assert ready['bridge_payload_path'] == request['range']['bridge_payload_path']
original = request['source_original_entry']
for field in ['dev', 'inode', 'nlink', 'mtime_ns', 'ctime_ns', 'sha256']:
    assert ready['source_file_identity'][field] == original[field]
assert ready['source_file_identity']['size'] == original['size_bytes']
assert ready['source_file_identity']['path'] == original['source_path']

stage = ready['source_gate_fresh_at_stage']
inp = stage['input']
assert stage['policy_id'] == ready['policy_id'] == tests['policy_id'] == 'TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019'
assert stage['authority_sha256'] == tests['authority_sha256']
assert stage['user_approval_sha256'] == tests['user_approval_sha256']
assert stage['test_receipt_sha256'] == t.sha(SRC / test_name)
assert stage['decision']['decision'] == 'POLICY_ELIGIBLE_NOT_READY' and not stage['decision']['reasons']
assert stage['decision']['effective_workspace_floor_bytes'] == 16 * 1024**3
assert inp['workspace_available_bytes'] - inp['planned_overlay_write_bytes'] >= 16 * 1024**3
assert 0 <= inp['planned_overlay_write_bytes'] <= 32 * 1024**2
assert inp['share_available_bytes'] >= 40 * 1024**3
assert inp['memory_available_bytes'] - inp['planned_memory_bytes'] >= 64 * 1024**3
assert inp['cgroup_headroom_bytes'] >= inp['planned_memory_bytes']
assert inp['source_namespace'] == 'mnt:[4026534768]' and inp['source_dev'] == 156 and inp['bridge_dev'] == 2431
assert inp['source_repo'] == 'swayhrl/gpu-l2-cache-verilog' and inp['source_branch'] == request['source_branch']
assert inp['source_root'] == manifest['source_root'] and inp['manifest_sha256'] == request['canonical_manifest_sha256']
assert inp['target_root_native164'] == manifest['genuine164_destination_root']
assert inp['txid'] == request['txid'] and inp['selector_sha256'] == manifest['selector_sha256']
for field in ['copy_lease_authorized', 'physical_scan_complete', 'candidate_root_idle', 'scheduled_readers_clear',
              'first_source_identity_ok', 'first_source_sha_refreshed', 'target_request_present_and_exact',
              'lane_runs_clear', 'lane_leases_clear', 'sole_source_sender', 'sole_target_receiver']:
    assert inp[field] is True, field
assert stage['lane_current_active_runs'] == stage['lane_current_active_leases'] == 0
assert not stage['candidate_root_process_refs'] and not stage['proc_unreadable'] and not stage['lane_physical_pids'] and not stage['other_transfer_pids']
assert stage['lane_closure_commit'] == '94fd48b69b37adb692e6152301b317f5f2e6a1e9'
assert stage['active_script_chain_separate_from_P9_PUBLIC'] is True
assert 0 <= inp['snapshot_age_seconds'] <= 30
assert 0 <= (datetime.datetime.fromisoformat(ready['at_utc']) - datetime.datetime.fromisoformat(stage['at_utc'])).total_seconds() <= 30
assert ready['post_stage_workspace_f_bavail_bytes'] - inp['planned_overlay_write_bytes'] >= 16 * 1024**3
assert ready['post_stage_share_f_bavail_bytes'] >= 40 * 1024**3
assert stage['first_source'] == ready['source_file_identity']
assert inp['planned_rate_bytes_per_second'] <= 30 * 1024**2

review = dict(schema='TLS_V10_COPY16_TARGET_SOURCE_POLICY_AND_READY_REVIEW_V1', utc=t.now(),
              source_read_commit='c0ee7b169c5f11d7b5c8b63d7ed0731d8238ba16', ready_commit=READY_COMMIT,
              ready_sha256=t.sha(SRC / ready_name), gate_commit=GATE_COMMIT, gate_sha256=t.sha(SRC / gate_name),
              copy_policy_code_sha256=tests['gate_code_sha256'], source_copy_synthetic_cases=45,
              full_source_copy_code_test_preflight_stage_read=True, target_did_not_run_source_policy_or_stage=True,
              source_fresh_at_stage_snapshot=stage['at_utc'], fresh_at_stage_delta_seconds=2.428728,
              workspace_available_before_stage=inp['workspace_available_bytes'],
              workspace_projected_after_control=stage['decision']['projected_workspace_available_bytes'],
              lane_registry_historical_not_used_as_fresh_lease=True,
              independent_final_closure_plus_current_physical_lease_scan_present=True,
              source_copy_gate_is_B0001_only_not_automatic_other_windows=True,
              source_originals='SOURCE_KEEP', target_has_source_unlink_authority=False,
              production_receive_permitted_for_exact_existing_B0001_only=True)
t.save('TLS_V10_COPY16_TARGET_SOURCE_POLICY_AND_READY_REVIEW.json', review)

code = r'''
import os,sys,pathlib,json,hashlib,subprocess,fcntl,datetime,stat
sys.dont_write_bytecode=True;os.nice(19)
subprocess.run(['ionice','-c','3','-p',str(os.getpid())],check=True,capture_output=True)
ready=__READY__;request=__REQUEST__;manifest=__MANIFEST__;reserved=__RESERVED__;source_commit=__COMMIT__;ready_sha=__SHA__
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
base=pathlib.Path(reserved['archive_root_on_174new'])
tools='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/tools/v9_6fd13ab5a9df_td90381f1cfcf'
proof_tools='/root/tls-v10-native-restore-20261018-target01/test_tools/53e7fba995c41118_d940e46b65c85eac'
assert hashlib.sha256((pathlib.Path(tools)/'v9_transaction.py').read_bytes()).hexdigest()=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
assert hashlib.sha256((pathlib.Path(proof_tools)/'tls_v10_native_chunk_proof.py').read_bytes()).hexdigest()=='53e7fba995c41118f0f2d240a1ca6e1210814eaf5fa798d96804c12b59fdc530'
sys.path.insert(0,tools);sys.path.insert(0,proof_tools)
import v9_transaction as v9
import tls_v10_native_chunk_proof as proof
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
mount=v9.mount_identity(base)
lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW)
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert v9.digest((B/'TLS_V10_P9_PUBLIC_B0001_SOURCE_READY_COPY16.json').read_bytes())==ready_sha
pub=json.loads((B/'TLS_V10_P9_PUBLIC_B0001_SOURCE_READY_COPY16_PUBLICATION.json').read_bytes())
assert pub['source_git_commit']==source_commit and pub['source_ready_sha256']==ready_sha
assert pub['source_repo']=='swayhrl/gpu-l2-cache-verilog' and pub['source_branch']==request['source_branch']
assert pub['txid']==ready['txid'] and pub['source_originals']=='SOURCE_KEEP'
for parent in [B,base]:
 assert v9.digest(v9.no_symlinks(parent/'TLS_V10_P9_PUBLIC_TARGET_SOLE_WINDOW_READY.json').read_bytes())==ready['target_request_sha256']
assert v9.digest((base/'TARGET_TX_RESERVATION.json').read_bytes())==reserved['reservation_sha256']
assert v9.digest(v9.canonical(manifest))==ready['canonical_manifest_sha256']
p=v9.no_symlinks(ready['bridge_payload_path']);assert p==B/'TLS_V10_P9_PUBLIC_B0001_574747b05622/files/payload.bin'
s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
actual=v9.identity(s)
for k in ['dev','inode','nlink','size','allocated']:assert actual[k]==ready['bridge_payload_identity'][k]
assert actual['size']==144 and actual['dev']==2431
payload_roots=[];staging_bytes=0
for files in B.glob('*/files'):
 v9.no_symlinks(files)
 staged=[]
 for parent,dirs,names in os.walk(files,followlinks=False):
  for n in dirs+names:
   q=v9.no_symlinks(pathlib.Path(parent)/n);qs=q.lstat();staging_bytes+=qs.st_blocks*512
   if not stat.S_ISDIR(qs.st_mode):
    assert stat.S_ISREG(qs.st_mode) and qs.st_nlink==1
    staged.append(q)
 if staged:payload_roots.append((files,staged))
assert payload_roots==[(p.parent,[p])],str(payload_roots)
staging_bytes+=(p.parent.lstat().st_blocks+p.parent.parent.lstat().st_blocks)*512
control_cost=sum(q.lstat().st_blocks*512 for q in B.glob('TLS_V10*.json') if q.is_file() and not q.is_symlink())
staging_and_controls=staging_bytes+control_cost
assert staging_and_controls<=256*1024**2
share=os.statvfs(B);assert share.f_bavail*share.f_frsize>=40*1024**3
mem=int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
assert mem-144>=64*1024**3
cg=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())-int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());assert cg>=144
transfer=v9.Transaction(base,manifest);assert transfer.txid==ready['txid']
transfer.transition('DISCOVERED',dict(group='P9_PUBLIC',source_root=manifest['source_root']))
transfer.transition('SOURCE_FROZEN',dict(source_manifest_sha256=reserved['canonical_manifest_sha256'],source_inventory_commit=reserved['source_frozen_commit'],source_binding_commit=reserved['source_binding_commit']))
transfer.transition('COPY_READY',dict(selector_sha256=manifest['selector_sha256'],source_originals='SOURCE_KEEP',admission_policy_id=ready['policy_id']))
key=v9.digest(ready['relative_path'].encode())+'.%016d'%ready['offset']
chunk=transfer.work/'chunks'/key;reused=chunk.exists()
assert v9.hash_file(p,expected=actual,throttle=transfer.throttle)==ready['source_full_sha256']
accepted=transfer.accept_chunk(ready['relative_path'],ready['offset'],p,ready['source_full_sha256'],txid=transfer.txid)
archive_identity=v9.identity(chunk.lstat())
assert v9.hash_file(chunk,expected=archive_identity,throttle=transfer.throttle)==ready['source_full_sha256']
native_dest=pathlib.Path(request['target_expected_native_chunk_proof'])
native=proof.prove_chunk(manifest,transfer.txid,ready['relative_path'],0,144,ready['source_full_sha256'],chunk,native_dest)
assert v9.identity(p.lstat())==actual
at=datetime.datetime.now(datetime.timezone.utc).isoformat()
dest=dict(schema='TLS_V10_TARGET_CHUNK_DEST_VERIFIED_COPY16_V1',status='DEST_VERIFIED',utc=at,
 window_id=ready['window_id'],group='P9_PUBLIC',txid=transfer.txid,selector_sha256=manifest['selector_sha256'],
 canonical_manifest_sha256=ready['canonical_manifest_sha256'],source_ready_git_commit=source_commit,
 source_ready_sha256=ready_sha,target_request_sha256=ready['target_request_sha256'],source_gate_git_commit=ready['source_gate_git_commit'],
 source_gate_sha256=ready['source_gate_sha256'],source_gate_fresh_at_stage_utc=ready['source_gate_fresh_at_stage']['at_utc'],
 policy_id=ready['policy_id'],relative_path=ready['relative_path'],offset=0,length=144,
 source_sha256=ready['source_full_sha256'],bridge_payload_path=str(p),bridge_identity=actual,
 archived_chunk_path=str(chunk),archived_chunk_identity=archive_identity,archived_close_reopen_sha256=ready['source_full_sha256'],
 genuine164_mount_verified=True,native164_base=manifest['genuine164_destination_root'],reused_existing_archive_chunk=reused,
 actual_bridge_payload_allocated_bytes=actual['allocated'],all_current_bridge_payload_and_TLS_control_allocated_bytes=staging_and_controls,
 Share_available_bytes=share.f_bavail*share.f_frsize,MemAvailable_bytes=mem,cgroup_headroom_bytes=cg,
 proof_scope='CHUNK_RANGE_ONLY',full_group_archive_verified=False,full_group_native_restored=False,
 source_originals='SOURCE_KEEP',source_science_release_bytes=0,source_files_deleted_by_target=0,
 exact_bridge_cleanup_authorized=False,await_source_signed_SOURCE_KEEP_ACK=True)
rest=dict(schema='TLS_V10_TARGET_CHUNK_RESTORE_VERIFIED_COPY16_V1',status='RESTORE_VERIFIED',utc=at,
 window_id=ready['window_id'],group='P9_PUBLIC',txid=transfer.txid,selector_sha256=manifest['selector_sha256'],
 canonical_manifest_sha256=ready['canonical_manifest_sha256'],source_ready_git_commit=source_commit,source_ready_sha256=ready_sha,
 target_request_sha256=ready['target_request_sha256'],relative_path=ready['relative_path'],offset=0,length=144,
 original_full_file_sha256=ready['source_full_sha256'],native_chunk_proof=native,
 native_restore_receipt_path=str(native_dest/'RESTORE_RECEIPT.json'),native_restore_receipt_sha256=v9.digest((native_dest/'RESTORE_RECEIPT.json').read_bytes()),
 independent_actual_native_restore=True,proof_scope='CHUNK_RANGE_ONLY',full_group_native_restored=False,
 source_originals='SOURCE_KEEP',target_has_source_unlink_authority=False,
 source_files_deleted_by_target=0,await_source_signed_SOURCE_KEEP_ACK=True)
os.close(lock)
print(json.dumps(dict(schema='TLS_V10_B0001_EXISTING_RECEIVER_RESULT_COPY16_V1',dest=dest,restore=rest,unchanged_transaction=True,new_flow=False)))
'''
for token,value in [('__READY__',ready),('__REQUEST__',request),('__MANIFEST__',manifest),('__RESERVED__',reserved),('__COMMIT__',READY_COMMIT),('__SHA__',t.sha(SRC/ready_name))]:
    code=code.replace(token,repr(value))
result=t.remote(code,'TLS_V10_P9_PUBLIC_B0001_RECEIVER_RESULT_COPY16',90)
t.save('TLS_V10_P9_PUBLIC_B0001_DEST_VERIFIED.json',result['dest'])
t.save('TLS_V10_P9_PUBLIC_B0001_RESTORE_VERIFIED.json',result['restore'])
print('DEST_SHA256',t.sha(t.BASE/'TLS_V10_P9_PUBLIC_B0001_DEST_VERIFIED.json'))
print('RESTORE_SHA256',t.sha(t.BASE/'TLS_V10_P9_PUBLIC_B0001_RESTORE_VERIFIED.json'))
