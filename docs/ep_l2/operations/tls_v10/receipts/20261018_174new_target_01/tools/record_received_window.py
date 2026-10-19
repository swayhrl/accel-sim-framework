"""Create deterministic-shape batch handoff/accounting from actual receipts only."""
import sys
import tls_target as t

wid=sys.argv[1]
D=t.get(wid+'_DEST_VERIFIED.json');R=t.get(wid+'_RESTORE_VERIFIED.json')
assert D['status']=='DEST_VERIFIED' and R['status']=='RESTORE_VERIFIED'
assert D['source_ready_sha256']==R['source_ready_sha256']
accepted={}
for p in t.BASE.glob('TLS_V10_P9_PUBLIC_B????_DEST_VERIFIED.json'):
    d=t.get(p.name)
    restored=t.get(p.name.replace('_DEST_VERIFIED.json','_RESTORE_VERIFIED.json'))
    assert restored['status']=='RESTORE_VERIFIED' and restored['txid']==d['txid']
    assert restored['source_ready_sha256']==d['source_ready_sha256']
    if 'entries' in d:
        values=[(e['relative_path'],e['offset'],e['length'],e['chunk_sha256']) for e in d['entries']]
        assert values==[(e['relative_path'],e['offset'],e['length'],e['chunk_sha256']) for e in restored['entries']]
        assert all(e['native_chunk_proof']['receipt']['native_metadata_verified'] for e in restored['entries'])
    else:
        values=[(d['relative_path'],d['offset'],d['length'],d['source_sha256'])]
        assert restored['native_chunk_proof']['receipt']['chunk_sha256']==d['source_sha256']
        assert restored['native_chunk_proof']['receipt']['native_metadata_verified'] is True
    for rel,off,size,sha in values:
        key=(rel,off)
        if key in accepted:assert accepted[key]==(size,sha),'Conflicting actual accepted range'
        accepted[key]=(size,sha)
total=sum(size for size,sha in accepted.values())
out=dict(schema='TLS_V10_TARGET_GROUPED_RECEIVING_RECEIPT_COPY16_V1',utc=t.now(),
    status=wid.rsplit('_',1)[-1]+'_DEST_AND_NATIVE_RANGE_RESTORE_VERIFIED_AWAIT_SOURCE_KEEP_ACK',
    **{k:D[k] for k in ['window_id','txid','selector_sha256','canonical_manifest_sha256','source_ready_git_commit','source_ready_sha256','target_window_git_commit','target_window_sha256']},
    source_originals='SOURCE_KEEP',source_files_deleted_by_target=0,
    dest_receipt=wid+'_DEST_VERIFIED.json',dest_receipt_sha256=t.sha(t.BASE/(wid+'_DEST_VERIFIED.json')),
    restore_receipt=wid+'_RESTORE_VERIFIED.json',restore_receipt_sha256=t.sha(t.BASE/(wid+'_RESTORE_VERIFIED.json')),
    range_count=D['range_count'],raw_bytes=D['raw_bytes'],
    total_real_accepted_ranges=len(accepted),total_real_native_range_proofs=len(accepted),
    total_effective_unique_original_payload_bytes=total,
    nonempty_originals_with_complete_verified_range_coverage=D['nonempty_originals_with_complete_verified_range_coverage'],
    full_group_certificate_created=False,full_group_all141_native_tree_restored=False,
    source_scientific_release_bytes=0,bridge_payloads_retained=True,
    exact_Source_KEEP_ACK_required='Both exact vector receipt SHA/Git commit, Source READY/window/txid/selector/manifest, all current Source/bridge identities+range SHA; original141 KEEP; Target-only exact bridge cleanup permission.',
    goal_mode='ACTIVE',goal_complete=False)
t.save(wid+'_TARGET_RECEIVING_RECEIPT_COPY16.json',out)
print('Actual unique accepted ranges/bytes',len(accepted),total)
