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
p=t.BASE/'STATUS.md'
status=('TLS-V10 Target: '+wid+' real164/native range verification PASS; exact KEEP ACK pending\n\n'
 'Canonical user-approved execution location: Framework9f1a21a909e437f1e34233b22595d0f7359f3dd3, jointly adopted with Source. '
 'Native proofs run on qualified174-new private tmpfs, volatile validation only; durable archive is genuine164. '
 'Old native164-only and historical build HOLD receipts are historical, not current admission.\n\n'
 'Current window: '+str(D['range_count'])+' ranges/'+str(D['raw_bytes'])+'B. Source READY '+D['source_ready_git_commit']+
 ' rawSHA '+D['source_ready_sha256']+'. Fresh Source scoped16G/Share40/RAM64/cgroup/readers/identity gates and frozen request/plan/manifest binding verified. '
 'Current Target mount, exclusive receiver, Share/RAM/headroom and physical bridge cap verified. DEST SHA '+t.sha(t.BASE/(wid+'_DEST_VERIFIED.json'))+
 '; native range RESTORE SHA '+t.sha(t.BASE/(wid+'_RESTORE_VERIFIED.json'))+'.\n\n'
 'Cumulative original verified range bytes '+str(summary['total_effective_unique_original_payload_bytes'])+
 ', ranges '+str(summary['total_real_accepted_ranges'])+', nonempty originals fully range-covered '+str(summary['nonempty_originals_with_complete_verified_range_coverage'])+'. '
 'This is range-only proof. Full141-file committed archive, complete independent native whole-file restoration and4 directory metadata certificate remain pending. '
 'No Source originals deleted by Target; actual TLS Source workspace release0.\n\n'
 'Next: independent Source exact KEEP ACK with matching Git AND bridge publication; only then exact fsynced bridge cleanup and next frozen window. '
 'No data retransfer, new transaction, second stream or user approval per batch. P9 source-only exact141 release remains conditional on full original recovery and all original Source gates/journals; other24 SOURCE_KEEP. '
 'C16 approvals/IO10/supply/source retention unchanged; no model IO during TLS.\n')
p.write_bytes(status.encode())

names=[wid+'_DEST_VERIFIED.json',wid+'_RESTORE_VERIFIED.json',
       wid+'_TARGET_RECEIVING_RECEIPT_COPY16.json',wid+'_TARGET_SOURCE_RUNNER_REVIEW_COPY16.json']
subprocess.run([sys.executable,str(t.META/'publish.py'),
    'ops(tls-v10): verify '+wid.rsplit('_',1)[-1]+' with same rolling range receiver',*names],cwd=t.REPO,check=True)
