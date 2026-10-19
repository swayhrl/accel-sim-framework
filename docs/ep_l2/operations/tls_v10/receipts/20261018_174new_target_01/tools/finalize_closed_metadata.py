"""Commit-ready audit for an ALREADY completed exact bridge cleanup.

Metadata only. Never reruns cleanup, stages payload or edits Source files.
"""
import hashlib
import json
import sys
import tls_target as t

wid=sys.argv[1]
closed=t.get(wid+'_BRIDGE_CLEANUP_COPY16.json')
assert closed['window_id']==wid and closed['removed_count']>0
assert closed['source_files_deleted_by_target']==closed['science_source_workspace_release_bytes']==0
assert closed['source_originals']=='SOURCE_KEEP'
path=t.BRIDGE+'/'+wid+'_BRIDGE_CLEANUP_JOURNAL_COPY16.jsonl'
assert path==closed['journal_path']
code="""import pathlib,json,hashlib
p=pathlib.Path(__PATH__);raw=p.read_bytes()
print(json.dumps(dict(records=[json.loads(l) for l in raw.splitlines()],sha256=hashlib.sha256(raw).hexdigest())))
""".replace('__PATH__',repr(path))
item=t.remote(code,wid+'_JOURNAL_READBACK',save_receipt=False)
raw=b''.join((json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode() for r in item['records'])
assert hashlib.sha256(raw).hexdigest()==item['sha256']==closed['journal_sha256']
assert all(r['window_id']==wid and r['txid']==closed['txid'] for r in item['records'])
assert item['records'][0]['event']=='BEGIN' and item['records'][-1]['event']=='COMPLETE'
assert sum(r['event']=='INTENT' for r in item['records'])==sum(r['event']=='DONE' for r in item['records'])==closed['removed_count']
(t.BASE/(wid+'_BRIDGE_CLEANUP_JOURNAL_COPY16.jsonl')).write_bytes(raw)
for n in ['receive_exact_window.py','clean_exact_window.py','clean_exact_remote_template.py',
          'record_received_window.py','prepare_next_p9_window.py','finalize_closed_metadata.py']:
    (t.BASE/'tools'/n).write_bytes((t.META/n).read_bytes())
accepted=t.get(wid+'_TARGET_RECEIVING_RECEIPT_COPY16.json')
status=t.BASE/'STATUS.md';s=status.read_text(encoding='utf-8')
first=s.index('\n');s='# TLS-V10 Target: '+wid.rsplit('_',1)[-1]+' closed; next frozen window pending; Goal active'+s[first:]
s+='\nCurrent'+closed['utc']+': '+wid+' CLOSED; Source KEEP ACK '+closed['source_ACK_git_commit']+' rawSHA '+closed['source_ACK_sha256']+' matches exact Target proof '+closed['target_proof_git_commit']+' and all permission rows. Target independently rechecked every bridge/archive/native SHA and numeric proof; fsynced BEGIN/INTENT-before-each-unlink/DONE/COMPLETE; only exact acknowledged bridge files and empty staging directories removed. Committed journal rawSHA '+closed['journal_sha256']+'. Current real accepted/native ranges '+str(accepted['total_real_accepted_ranges'])+', unique original bytes '+str(accepted['total_effective_unique_original_payload_bytes'])+', complete nonempty raw-file coverage '+str(accepted['nonempty_originals_with_complete_verified_range_coverage'])+'. Full141/4 archive/native tree/certificate still incomplete. Source science/workspace release0, all141 originalsKEEP. Prior pending-ACK notes are historical. Next request prepared data-only from same frozen plan and published in same push as actual cleanup parent commit; no extra stream or safety-gate change. Goalactive.\n'
status.write_bytes(s.encode())
print('Commit-ready exact cleanup audit',wid,'files',closed['removed_count'])
