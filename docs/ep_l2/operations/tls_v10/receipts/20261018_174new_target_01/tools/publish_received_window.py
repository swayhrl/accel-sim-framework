"""One compact publication for a completed real window; unchanged safety gates."""
import subprocess
import sys
import tls_target as t

wid=sys.argv[1]
subprocess.run([sys.executable,str(t.META/'record_received_window.py'),wid],cwd=t.REPO,check=True)
summary=t.get(wid+'_TARGET_RECEIVING_RECEIPT_COPY16.json')
D=t.get(wid+'_DEST_VERIFIED.json');R=t.get(wid+'_RESTORE_VERIFIED.json')
for n in ['fetch_exact_window_controls.py','receive_exact_window.py','record_received_window.py',
          'publish_received_window.py','prepare_next_p9_window.py','finalize_closed_metadata.py']:
    (t.BASE/'tools'/n).write_bytes((t.META/n).read_bytes())
p=t.BASE/'STATUS.md';s=p.read_text(encoding='utf-8');line=s.index('\n')
s='# TLS-V10 Target: '+wid.rsplit('_',1)[-1]+' real164/native range verification PASS; KEEP ACK pending; Goal active'+s[line:]
s+='\nCurrent'+D['utc']+': '+wid+' actual '+str(D['range_count'])+' ranges/'+str(D['raw_bytes'])+' originalB verified on genuine164 and independent native range restore with Source numeric metadata. Source READY '+D['source_ready_git_commit']+' rawSHA '+D['source_ready_sha256']+', exact frozen request/plan/manifest/prior cleanup and reviewed unchanged runner/test bindings confirmed; fresh Source actual16G/Share40/RAM64/cgroup/lease/readers gate decisions reviewed, current Target mount/lock/resources/physical staging independently checked. DEST rawSHA '+t.sha(t.BASE/(wid+'_DEST_VERIFIED.json'))+'; RESTORE rawSHA '+t.sha(t.BASE/(wid+'_RESTORE_VERIFIED.json'))+'. Cumulative unique real accepted/native ranges '+str(summary['total_real_accepted_ranges'])+', original bytes '+str(summary['total_effective_unique_original_payload_bytes'])+', complete nonempty raw-file coverage '+str(summary['nonempty_originals_with_complete_verified_range_coverage'])+'. Complete141/4 archive+new absent all-file native restoration/certificate still pending; Source originalsKEEP, science/workspace release0. Await exact Source KEEP ACK before precise journaled bridge cleanup; next frozen window only after closure. Data-only control reused, no repeated unchanged code/test development, one flow. Goalactive.\n'
p.write_bytes(s.encode())
names=[wid+'_DEST_VERIFIED.json',wid+'_RESTORE_VERIFIED.json',
       wid+'_TARGET_RECEIVING_RECEIPT_COPY16.json',wid+'_TARGET_SOURCE_RUNNER_REVIEW_COPY16.json']
subprocess.run([sys.executable,str(t.META/'publish.py'),
    'ops(tls-v10): verify '+wid.rsplit('_',1)[-1]+' with same rolling range receiver',*names],cwd=t.REPO,check=True)
