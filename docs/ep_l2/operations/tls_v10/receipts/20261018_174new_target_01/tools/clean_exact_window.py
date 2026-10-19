"""One exact acknowledged bridge cleanup; no Source original operation.

Arguments: window_id Source ACK commit cache-prefix-of-copied-ACK.
"""
import sys
import tls_target as t

wid,commit,prefix=sys.argv[1:]
assert wid.startswith('TLS_V10_P9_PUBLIC_B') and len(commit)==40

# Explicit user amendment; both sides must adopt the same immutable Git commit.
t.require_tls_restore_location(wid)

name=prefix+wid+'_SOURCE_KEEP_ACK.json'
A=t.get(name);D=t.get(wid+'_DEST_VERIFIED.json');R=t.get(wid+'_RESTORE_VERIFIED.json');W=t.get(wid+'_TARGET_SOLE_WINDOW_REQUEST_COPY16.json')
assert A['schema']=='TLS_V10_P9_EXACT_RANGE_SOURCE_KEEP_ACK_V1'
assert A['status']=='SOURCE_KEEP_ACK_TARGET_MAY_CLEAN_EXACT_VERIFIED_BRIDGE_RANGES'
assert A['source_originals']=='SOURCE_KEEP' and A['source_science_files_unlinked']==A['source_science_df_gain_bytes']==0
assert A['source_frozen_files_metadata_rechecked']==141
for key in ['window_id','txid','selector_sha256','canonical_manifest_sha256','source_ready_git_commit','source_ready_sha256','range_count','raw_bytes']:assert A[key]==D[key]
assert A['target_dest_receipt_sha256']==t.sha(t.BASE/(wid+'_DEST_VERIFIED.json'))
assert A['target_native_restore_receipt_sha256']==t.sha(t.BASE/(wid+'_RESTORE_VERIFIED.json'))
assert A['target_receiving_receipt_sha256']==t.sha(t.BASE/(wid+'_TARGET_RECEIVING_RECEIPT_COPY16.json'))
for suffix in ['DEST_VERIFIED.json','RESTORE_VERIFIED.json','TARGET_RECEIVING_RECEIPT_COPY16.json']:
 p=t.BASE/(wid+'_'+suffix)
 assert t.git('show',A['target_dest_restore_git_commit']+':'+p.relative_to(t.REPO).as_posix())==p.read_bytes()
t.git('merge-base','--is-ancestor',A['target_dest_restore_git_commit'],'origin/'+t.BRANCH)
# Preserve original signed raw bytes; normalize only the in-memory permission vector.
permissions=A['bridge_payload_exact_cleanup_permission'];assert len(permissions)==len(D['entries'])==len(R['entries'])
flat=[]
for permission,d,r in zip(permissions,D['entries'],R['entries']):
 assert permission['owner']=='174-new TARGET ONLY AFTER_GITHUB_SOURCE_ACK_READBACK'
 assert permission['path']==d['bridge_path'] and permission['identity']==d['bridge_identity'] and permission['sha256']==d['chunk_sha256']
 flat.append(dict(permission['identity'],path=permission['path'],sha256=permission['sha256'],owner=permission['owner']))
A=dict(A,bridge_payload_exact_cleanup_permissions=flat)
code=(t.META/'clean_exact_remote_template.py').read_text(encoding='utf-8')
for token,value in [('__ACK__',A),('__DEST__',D),('__RESTORE__',R),('__WINDOW__',W),('__PIN__',t.sha(t.BASE/name)),('__COMMIT__',commit)]:code=code.replace(token,repr(value))
t.remote(code,wid+'_BRIDGE_CLEANUP_COPY16',180)
