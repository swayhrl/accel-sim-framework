"""Read-only plan for three exact, terminal, owned RTX Native cache trees."""
import hashlib, importlib.util, json, os, pathlib, shutil, time

C = pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
N = C.parent
B = pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ID = 'ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2'
SOURCES = [
    (N/(ID+'_post_native_epoch3/EPOCH3_NATIVE8_098'), 'stage_retained_native_rtx_post_epoch3_tail2_20261025_v1'),
    (N/'post_parallel_v3_real_A1', 'stage_retained_native_rtx_post48_qualification_20261025_v1'),
    (N/'c8_two_vector_native_cold_v1', 'stage_retained_native_rtx_two_vector_cold_20261025_v1'),
]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
terminal = C/(ID+'_POST_EPOCH3_SUPERVISOR_TERMINAL.json')
term = json.loads(terminal.read_text())
assert term['status']=='FAILED_RETAINED' and not term['unresolved_exact_own_processes']
assert term['controller_returncode']==-15
spec = importlib.util.spec_from_file_location('auth', C/'read_native_foreign_reserve_v1.py')
auth = importlib.util.module_from_spec(spec); spec.loader.exec_module(auth)
authority = auth.snapshot()
rate = 15*2**20
rows = []
for root, ident in SOURCES:
    assert root.is_dir() and not root.is_symlink() and N in root.resolve().parents
    assert root.stat().st_dev==2128
    members=[]; directories=[]; inodes={}; start=time.monotonic(); done=0
    for current, dirs, files in os.walk(root, followlinks=False):
        parent=pathlib.Path(current)
        for name in dirs+files: assert not (parent/name).is_symlink()
        ds=parent.stat()
        directories.append({'path':parent.relative_to(root).as_posix(),'mode':ds.st_mode,'mtime_ns':ds.st_mtime_ns})
        for name in sorted(files):
            p=parent/name; before=p.stat(); assert p.is_file() and before.st_dev==2128
            h=hashlib.sha256()
            with p.open('rb') as inp:
                for data in iter(lambda:inp.read(2**20),b''):
                    h.update(data);done+=len(data)
                    time.sleep(max(0,done/rate-(time.monotonic()-start)))
            after=p.stat()
            fields=['st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns','st_mode','st_nlink']
            assert all(getattr(before,k)==getattr(after,k)for k in fields)
            r={'path':p.relative_to(root).as_posix(),'bytes':before.st_size,'sha256':h.hexdigest(),
               'allocated_bytes':before.st_blocks*512,'dev':before.st_dev,'ino':before.st_ino,
               'nlink':before.st_nlink,'mtime_ns':before.st_mtime_ns,'ctime_ns':before.st_ctime_ns,
               'mode':before.st_mode,'uid':before.st_uid,'gid':before.st_gid}
            members.append(r);inodes.setdefault((r['dev'],r['ino']),[]).append(r)
    releasable=sum(v[0]['allocated_bytes']for v in inodes.values()if v[0]['nlink']==len(v))
    external_links=[{'dev':k[0],'ino':k[1],'nlink':v[0]['nlink'],'observed_in_tree':len(v)}for k,v in inodes.items()if v[0]['nlink']!=len(v)]
    rows.append({'source':str(root),'target_object':str(B/'objects'/ident),'target_tree':str(B/'objects'/ident/'tree'),
                 'kind':'ENGINEERING_RETAINED_NATIVE_TREE_NOT_FORMAL_WORKLOAD',
                 'files':members,'directories':directories,'logical_bytes':sum(x['bytes']for x in members),
                 'file_count':len(members),'conservative_file_data_releasable_bytes':releasable,
                 'external_hardlink_sets':external_links,'source_payload_written':False,
                 'planned_original_path_after_verified_switch':'cold symlink to target_tree',
                 'planned_receiver_steps':['RTX SOURCE then TARGET NB lease','copy to new ABSENT NAS inflight/tree, 1MiB buffer/15MiBps single stream','all target files fsync close reopen fullSHA; exact directory/file set','source fullSHA/stat recheck, MANIFEST+COMMIT-last','rename source to owned local retired name; install original-path cold symlink; fsync parent','follow original path and verify all member SHA through cold reference','only then remove exact original owned Native files; retain cleanup receipt and original failures in cold tree'],
                 'no_original_science_raw_deleted':True})
reserved=authority['sum_all_records_reserved_write_bytes']
result={'status':'PLAN_ONLY_NOT_EXECUTED_PARENT_REVIEW_REQUIRED','sources':rows,
        'sum_logical_bytes':sum(x['logical_bytes']for x in rows),
        'sum_conservative_file_data_releasable_bytes':sum(x['conservative_file_data_releasable_bytes']for x in rows),
        'source_terminal_receipt':str(terminal),'source_terminal_receipt_sha256':sha(terminal),
        'current_authority':authority,'current_free_bytes':shutil.disk_usage(N).free,
        'dynamic_minimum_floor_formula':'5GiB + sum ALL registered reserved_write_bytes + 1GiB headroom + 64MiB controls',
        'dynamic_minimum_floor_bytes':5*2**30+reserved+2**30+64*2**20,
        'copy_buffer_bytes':2**20,'additional_Native_payload_bytes':0,
        'NAS_write_rate_bytes_sec':rate,'maximum_lease_scope':'one tree, release before next',
        'new_manifest_control_bytes_expected_less_than':2**20,
        'NAS_target_not_yet_created':True,'no_deletions_or_symlink_changes_done':True,
        'no_GPU_109_SIM_or_registry_writes':True,'native_source_rate_limited_bytes_sec':rate,
        'notes':'Original GPU100 raw and full46e validation remain unchanged on NAS.98 closed groups remain in flight.Never resume into a cold symlink; future CPU attempt must use a fresh Native work namespace.',
        'unix':time.time()}
out=C/'NATIVE_RTX_TERMINAL_COLD_OFFLOAD_PLAN_V1.json';assert not out.exists()
with out.open('x')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'path':str(out),'sha256':sha(out),'files':sum(x['file_count']for x in rows),
                  'logical_bytes':result['sum_logical_bytes'],'releasable_bytes':result['sum_conservative_file_data_releasable_bytes'],
                  'floor':result['dynamic_minimum_floor_bytes'],'free':result['current_free_bytes']}))
