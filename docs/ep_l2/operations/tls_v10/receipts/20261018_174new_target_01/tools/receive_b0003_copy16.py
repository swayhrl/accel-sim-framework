import datetime
import json
import tls_target as t

D=t.META/'source_3d49d60'
ready_name='TLS_V10_P9_PUBLIC_B0003_SOURCE_READY_COPY16.json'
gate_name='TLS_V10_P9_PUBLIC_B0003_SOURCE_GATE_PASS_COPY16.json'
adopt_name='TLS_V10_P9_PUBLIC_B0003_SOURCE_PROTOCOL_ADOPTION_COPY16.json'
R=json.loads((D/ready_name).read_bytes());G=json.loads((D/gate_name).read_bytes());A=json.loads((D/adopt_name).read_bytes())
W=t.get('TLS_V10_P9_PUBLIC_B0003_TARGET_SOLE_WINDOW_REQUEST_COPY16.json')
M=t.get('SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json')
reserved=t.get('TLS_V10_P9_PUBLIC_TARGET_ROOT_RESERVED.json')
assert R['schema']=='TLS_V10_OLD174_GROUPED_RAW_READY_V1' and R['status']=='READY_SOURCE_KEEP'
for k in ['window_id','txid','selector_sha256','canonical_manifest_sha256','group','source_frozen_commit','source_root']:
    assert R[k]==W[k],k
assert R['source_namespace']=='mnt:[4026534768]' and R['source_dev']==156
assert R['source_repo']=='swayhrl/gpu-l2-cache-verilog' and R['source_branch']==W['source_branch']
assert R['source_originals']=='SOURCE_KEEP' and R['source_files_unlinked']==0
assert R['target_window_git_commit']=='04fce1cc8f0f54a058941fb108b786ca874401b3'
assert R['target_window_sha256']==t.sha(t.BASE/'TLS_V10_P9_PUBLIC_B0003_TARGET_SOLE_WINDOW_REQUEST_COPY16.json')
assert R['target_root_native164']==M['genuine164_destination_root']
assert R['prior_cleanup_sha256']==W['prior_window_cleanup_sha256']
assert R['source_gate_sha256']==t.sha(D/gate_name)
assert R['source_protocol_adoption_sha256']==t.sha(D/adopt_name)
assert R['source_test_receipt_sha256']==t.sha(t.META/'source_3d49d60/TLS_V10_P9_PUBLIC_B0003_SOURCE_FIXTURE_QUALIFICATION.json')
assert R['qualified_source_sender_code_sha256']==t.sha(t.META/'source_559a014/tls_v10_p9_grouped_source_range.py')
assert R['qualified_source_controller_code_sha256']==t.sha(D/'tls_v10_p9_b0003_stage.py')==A['source_controller_code_sha256']
assert A['source_preflight_code_sha256']==t.sha(D/'tls_v10_p9_b0003_preflight.py')
assert A['target_grouped_protocol_sha256']==t.sha(t.BASE/'TLS_V10_GROUPED_RAW_WINDOW_PROTOCOL_AFTER_B0001.md')
assert A['target_receiver_adapter_sha256']==t.sha(t.BASE/'tools/tls_v10_grouped_ranges.py')
assert G['source_controller_sha256']==R['qualified_source_controller_code_sha256']
assert G['source_authority_sha256']=='745fb24b603627b63bc43a1cb130a9e61038d23adee618e2850e3d80755c7bf1'
assert G['source_user_approval_sha256']=='789528e6dd4e7b51c3a437e14f8a9b3df1045bfa5e1eefc71974b3324ce9b61d'
assert R['policy_id']=='TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019'
assert R['range_count']==len(R['entries'])==W['range_count']==1
assert R['raw_bytes']==sum(e['length'] for e in R['entries'])==W['raw_bytes']==134217728
rows={r['relative_path']:r for r in M['files']}
ID=('dev','inode','nlink','size','allocated','uid','gid','mode','mtime_ns','ctime_ns')
for e,w in zip(R['entries'],W['ranges']):
    for k in ['relative_path','offset','length','bridge_path']:assert e[k]==w[k]
    row=rows[e['relative_path']]
    assert e['source_identity']==w['source_identity']=={k:row[k] for k in ID}
    assert e['source_full_sha256']==w['original_sha256']==row['sha256']
    assert e['offset']==0 and e['length']==134217728 and e['length']<row['size']
    assert e['chunk_sha256']==R['gate_before_stage']['current_range_sha256']
assert G['decision']['decision']=='POLICY_ELIGIBLE_NOT_READY' and not G['decision']['reasons']
pre=R['gate_before_stage'];post=R['gate_after_stage'];b=pre['input']
for gate in [pre,post]:
    assert gate['decision']['decision']=='POLICY_ELIGIBLE_NOT_READY' and not gate['decision']['reasons']
    assert gate['decision']['effective_workspace_floor_bytes']==16*1024**3
assert b['workspace_available_bytes']-b['planned_overlay_write_bytes']>=16*1024**3
assert 0<=b['planned_overlay_write_bytes']<=32*1024**2
assert b['share_available_bytes']-b['planned_bridge_staged_bytes']>=40*1024**3
assert b['memory_available_bytes']-b['planned_memory_bytes']>=64*1024**3
assert b['cgroup_headroom_bytes']>=b['planned_memory_bytes']
assert post['workspace_available_bytes']-b['planned_overlay_write_bytes']>=16*1024**3
assert post['share_available_bytes']>=40*1024**3
assert not pre['physical_source_refs'] and not pre['proc_unreadable'] and not pre['lane_physical_pids'] and not pre['other_transfer_pids']
assert not post['source_process_refs'] and not post['unreadable_proc_pids'] and not post['lane_physical_pids'] and not post['other_transfer_pids']
assert pre['lane_current_registry']['active_runs']==pre['lane_current_registry']['active_leases']==0
assert post['lane_current_registry']['active_runs']==post['lane_current_registry']['active_leases']==0
assert pre['all141_frozen_metadata_exact'] and pre['active_script_chain_clear'] and post['scheduled_readers_clear']
for key in ['copy_lease_authorized','physical_scan_complete','candidate_root_idle','scheduled_readers_clear','first_source_identity_ok','first_source_sha_refreshed','sole_source_sender','sole_target_receiver','target_request_present_and_exact','lane_runs_clear','lane_leases_clear']:assert b[key] is True,key
assert 0<=b['snapshot_age_seconds']<=30
delta=(datetime.datetime.fromisoformat(R['at_utc'])-datetime.datetime.fromisoformat(pre['at_utc'])).total_seconds();assert 0<=delta<=30
assert R['entries'][0]['chunk_sha256']==pre['current_range_sha256']==post['source_range_sha256_after_stage']
assert post['all141_source_metadata_exact'] is True

review=dict(schema='TLS_V10_B0003_TARGET_PRODUCTION_SOURCE_REVIEW_V1',utc=t.now(),status='EXACT_SOURCE_GATE_ADOPTION_AND_READY_VERIFIED_FOR_B0003_ONLY',source_commit='e5200732e55f17e248983231067f4aabc41a1742',source_ready_sha256=t.sha(D/ready_name),source_gate_sha256=t.sha(D/gate_name),source_adoption_sha256=t.sha(D/adopt_name),source_production_preflight_stage_and7_fixture_methods_fully_read=True,source7_fixture_methods_and24_negative_gate_cases_reviewed=True,paired_synthetic_source_to_target_roundtrip_verified=True,source_fresh_before_stage_utc=pre['at_utc'],source_fresh_after_stage_utc=post['at_utc'],fresh_stage_interval_seconds=delta,source_projected_workspace_bytes=pre['decision']['projected_workspace_available_bytes'],source_ranges=1,source_raw_bytes=134217728,science_source_files_deleted=0,source_keep=True,no_global16_or_other_release_permission=True,goal_mode='ACTIVE')
t.save('TLS_V10_B0003_TARGET_PRODUCTION_SOURCE_REVIEW_COPY16.json',review)
code=r'''
import pathlib,json,os,sys,hashlib,fcntl,subprocess,datetime,stat
sys.dont_write_bytecode=True;os.nice(19)
subprocess.run(['ionice','-c','3','-p',str(os.getpid())],capture_output=True,check=True)
R=__READY__;W=__WINDOW__;M=__MANIFEST__;reserved=__RESERVED__;ready_sha=__PIN__;source_commit='e5200732e55f17e248983231067f4aabc41a1742'
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');base=pathlib.Path(M['destination_path_on_174new'])
tools=pathlib.Path('/root/tls-v10-native-restore-20261018-target01/test_tools/grouped_7155b810af658331')
pins=__PINS__
for n,h in pins.items():assert hashlib.sha256((tools/n).read_bytes()).hexdigest()==h
sys.path.insert(0,str(tools));import v9_transaction as v9;import tls_v10_grouped_ranges as grouped
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]';v9.mount_identity(base)
lock=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
raw=(B/'TLS_V10_P9_PUBLIC_B0003_SOURCE_READY_COPY16.json').read_bytes();assert v9.digest(raw)==ready_sha
pub=json.loads((B/'TLS_V10_P9_PUBLIC_B0003_SOURCE_READY_PUBLICATION_COPY16.json').read_bytes());assert pub['source_git_commit']==source_commit and pub['source_ready_sha256']==ready_sha
assert pub['txid']==W['txid'] and pub['source_originals']=='SOURCE_KEEP'
assert v9.digest((B/'TLS_V10_P9_PUBLIC_B0003_TARGET_SOLE_WINDOW_REQUEST_COPY16.json').read_bytes())==R['target_window_sha256']
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
T.transition('DISCOVERED',dict(group='P9_PUBLIC',source_root=M['source_root']))
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
common=dict(utc=now,window_id=W['window_id'],group='P9_PUBLIC',txid=T.txid,selector_sha256=M['selector_sha256'],canonical_manifest_sha256=W['canonical_manifest_sha256'],target_window_git_commit=R['target_window_git_commit'],target_window_sha256=R['target_window_sha256'],source_ready_git_commit=source_commit,source_ready_sha256=ready_sha,source_gate_sha256=R['source_gate_sha256'],source_protocol_adoption_sha256=R['source_protocol_adoption_sha256'],source_originals='SOURCE_KEEP',source_files_deleted_by_target=0,science_source_release_bytes=0,proof_scope='COLLECTION_OF_CHUNK_RANGES',full_group_archived=False,full_group_native_restored=False,range_count=len(dest_rows),raw_bytes=R['raw_bytes'],await_source_signed_SOURCE_KEEP_ACK=True)
dest=dict(schema='TLS_V10_TARGET_GROUPED_DEST_VERIFIED_COPY16_V1',status='DEST_VERIFIED',**common,entries=dest_rows,genuine164_mount_verified=True,native164_base=M['genuine164_destination_root'],actual_all_bridge_payload_directory_and_TLS_control_allocated_bytes=allocated,Share_available_bytes=share,MemAvailable_bytes=mem,cgroup_headroom_bytes=cg,one_receiver_lock=True,reused_chunks=sum(e['reused_existing_archive_chunk'] for e in dest_rows),nonempty_originals_with_complete_verified_range_coverage=covered,total_accepted_ranges_in_transaction=len(records))
restore=dict(schema='TLS_V10_TARGET_GROUPED_RESTORE_VERIFIED_COPY16_V1',status='RESTORE_VERIFIED',**common,entries=native_rows,independent_actual_native_restore=True,numeric_metadata_verified_every_range=True,native_full_group_file_restore_count=0)
os.close(lock)
print(json.dumps(dict(schema='TLS_V10_B0003_EXISTING_GROUPED_RECEIVER_RESULT_V1',dest=dest,restore=restore,accepted_vector=accepted,source_originals='SOURCE_KEEP',new_flow=False)))
'''
pins={n:t.sha(t.BASE/'tools'/n) for n in ['v9_transaction.py','tls_v10_native_chunk_proof.py','tls_v10_grouped_ranges.py']}
for token,val in [('__READY__',R),('__WINDOW__',W),('__MANIFEST__',M),('__RESERVED__',reserved),('__PIN__',t.sha(D/ready_name)),('__PINS__',pins)]:code=code.replace(token,repr(val))
result=t.remote(code,'TLS_V10_P9_PUBLIC_B0003_RECEIVER_RESULT_COPY16',180)
t.save('TLS_V10_P9_PUBLIC_B0003_DEST_VERIFIED.json',result['dest'])
t.save('TLS_V10_P9_PUBLIC_B0003_RESTORE_VERIFIED.json',result['restore'])
print('B0003_DEST_SHA',t.sha(t.BASE/'TLS_V10_P9_PUBLIC_B0003_DEST_VERIFIED.json'))
print('B0003_RESTORE_SHA',t.sha(t.BASE/'TLS_V10_P9_PUBLIC_B0003_RESTORE_VERIFIED.json'))
