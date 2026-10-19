"""Metadata-only next frozen window; never stage Source or create NAS roots.

Arguments: next window number, actual local cleanup commit, Source ACK commit.
Caller pushes cleanup parent and this request together using the usual publisher.
"""
import copy
import json
import sys
import tls_target as t

number=int(sys.argv[1]);cleanup_commit=sys.argv[2];ack_commit=sys.argv[3]
assert 5<=number<=33 and len(cleanup_commit)==len(ack_commit)==40
wid='TLS_V10_P9_PUBLIC_B%04d'%number;prev='TLS_V10_P9_PUBLIC_B%04d'%(number-1)
W=copy.deepcopy(t.get('TLS_V10_P9_PUBLIC_B0004_TARGET_SOLE_WINDOW_REQUEST_COPY16.json'))
M=t.get('SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json')
plan=t.get('TLS_V10_P9_PUBLIC_INACTIVE_BATCHING_PROPOSAL_AFTER_B0001.json')
assert number-1<len(plan['batches'])
batch=plan['batches'][number-1];rows={r['relative_path']:r for r in M['files']}
cleanup_name=prev+'_BRIDGE_CLEANUP_COPY16.json';cleanup=t.get(cleanup_name)
assert cleanup['window_id']==prev and cleanup['txid']==W['txid']
assert cleanup['source_originals']=='SOURCE_KEEP' and cleanup['source_files_deleted_by_target']==0
assert cleanup['archive_and_native_every_range_reverified'] is True
assert cleanup['source_ACK_git_commit']==ack_commit
relative=t.BASE.relative_to(t.REPO).as_posix()+'/'+cleanup_name
assert t.git('show',cleanup_commit+':'+relative)==(t.BASE/cleanup_name).read_bytes()
root=t.BRIDGE+'/'+wid+'_'+W['txid'][:12]+'/files';ranges=[]
for i,e in enumerate(batch['entries']):
    row=rows[e['relative_path']]
    ranges.append(dict(e,source_path=M['source_root']+'/'+e['relative_path'],
                       source_identity={k:row[k] for k in ('dev','inode','nlink','size','allocated','uid','gid','mode','mtime_ns','ctime_ns')},
                       bridge_path=root+'/range-%04d.bin'%i))
W.update(utc=t.now(),window_id=wid,prior_window=prev,prior_window_cleanup_commit=cleanup_commit,
         prior_window_cleanup_name=cleanup_name,prior_window_cleanup_sha256=t.sha(t.BASE/cleanup_name),
         prior_source_keep_ACK_commit=ack_commit,plan_batch_index=number-1,bridge_root=root,ranges=ranges,
         range_count=len(ranges),raw_bytes=sum(e['length'] for e in ranges),
         expected_target_dest_receipt=wid+'_DEST_VERIFIED.json',
         expected_target_native_receipt=wid+'_RESTORE_VERIFIED.json',expected_source_ACK=wid+'_SOURCE_KEEP_ACK.json')
W.pop('batch4_offset_note',None)
W['source_must_before_stage'][0]='Verify exact current request Git/raw SHA and actual previous cleanup literal commit/file/raw SHA. Both local commits arrive in ONE push; no self-reference/schema change.'
W['source_must_before_stage'][1]='Reuse the already-qualified data-driven P9 exact-window runner/test SHA. Exact data-only bindings must equal the frozen plan index/vector; no per-window cloned script or unchanged test-suite rerun. Changed code still needs bounded review/tests.'
W['receiver_adapter']['production_source_sender_qualification']='Existing qualified exact-window runner with THIS frozen data-only binding and fresh Source actual16/40/64 resources/readers/lease/identity/SHA PASS plus signed READY. No automatic data admission.'
t.save(wid+'_TARGET_SOLE_WINDOW_REQUEST_COPY16.json',W)
code=r'''
import os,pathlib,json,datetime,fcntl
B=pathlib.Path(__BRIDGE__);future=pathlib.Path(__ROOT__);wid=__WID__;prev=__PREV__
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
assert not os.path.lexists(future.parent)
assert not (B/(prev+'_574747b05622')).exists()
assert not [p for p in B.glob('*/files') if any(q.is_file() for q in p.rglob('*'))]
fd=os.open(B/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
s=os.statvfs(B);share=s.f_bavail*s.f_frsize;assert share-128*1024**2>=40*1024**3
mem=int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
assert mem-128*1024**2>=64*1024**3
os.close(fd)
result=dict(schema='TLS_V10_NEXT_GROUPED_WINDOW_TARGET_METADATA_PREFLIGHT_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),window_id=wid,bridge_payloads_absent=True,receiver_idle=True,next_stage_not_created_by_target=True,Share_available_bytes=share,MemAvailable_bytes=mem,source_admission_not_inferred=True)
result['prior_B%04d_closed'%(__NUMBER__-1)]=True
print(json.dumps(result))
'''
for token,value in [('__BRIDGE__',t.BRIDGE),('__ROOT__',root),('__WID__',wid),('__PREV__',prev),('__NUMBER__',number)]:code=code.replace(token,repr(value))
t.remote(code,wid+'_TARGET_METADATA_PREFLIGHT_COPY16')
print(json.dumps(dict(window_id=wid,ranges=W['range_count'],raw_bytes=W['raw_bytes'],request_sha256=t.sha(t.BASE/(wid+'_TARGET_SOLE_WINDOW_REQUEST_COPY16.json')))))
