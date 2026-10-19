"""Fetch compact immutable Source controls; no Source filesystem operations."""
import json
import subprocess
import sys
import tls_target as t

wid,commit=sys.argv[1:]
assert wid.startswith('TLS_V10_P9_PUBLIC_B') and len(commit)==40
P='docs/ep_l2/operations/tls_v10_174_to_164_source/'
names=[wid+'_EXACT_SOURCE_WINDOW_BINDING.json',wid+'_SOURCE_GATE_PASS_COPY16.json',
       wid+'_SOURCE_READY_COPY16.json','TLS_V10_P9_EXACT_WINDOW_PROTOCOL_ADOPTION_COPY16.json',
       'tls_v10_p9_exact_window_runner.py','test_tls_v10_p9_exact_window_runner.py']
bare='D:/repo/storage-ops-174new-164-exec-v1/.git/source-evidence.git'
result=subprocess.run(['git','--git-dir='+bare,'cat-file','--batch'],
    input=''.join(commit+':'+P+n+'\n' for n in names).encode(),capture_output=True,check=True).stdout
folder='source_'+commit[:7];D=t.META/folder;D.mkdir(exist_ok=True)
pos=0
for n in names:
    end=result.index(b'\n',pos);header=result[pos:end].split()
    assert len(header)==3 and header[1]==b'blob',n
    size=int(header[2]);raw=result[end+1:end+1+size];pos=end+size+2
    (D/n).write_bytes(raw)
    # Immutable control bytes are committed once; unchanged code is identified
    # by its reviewed SHA and Source commit, rather than copied every window.
    if n.endswith('.json'):(t.BASE/('SOURCE_'+commit[:7]+'_'+n)).write_bytes(raw)
assert pos==len(result)
R=json.loads((D/(wid+'_SOURCE_READY_COPY16.json')).read_bytes())
print(json.dumps(dict(window_id=wid,source_ready_commit=commit,cache=folder,
    READY_sha256=t.sha(D/(wid+'_SOURCE_READY_COPY16.json')),range_count=R['range_count'],
    raw_bytes=R['raw_bytes'],runner_sha256=t.sha(D/'tls_v10_p9_exact_window_runner.py'))))

if 'post_stage_recovery_code_sha256' in R and R['post_stage_recovery_code_sha256']=='408e83ac9d468b80e47364dbc115cf85ab62b0bce9504bcfcbb1b103e2b30ebb':
 for n in ['tls_v10_one_shot_stage_recovery.py','test_tls_v10_one_shot_stage_recovery.py','TLS_V10_FOLLOWUP_PRESERVED_STAGE_RECOVERY_QUALIFICATION_20261020.json']:
  raw=subprocess.check_output(['git','--git-dir='+bare,'show',commit+':'+P+n]);(D/n).write_bytes(raw)
 assert t.sha(D/'tls_v10_one_shot_stage_recovery.py')==R['post_stage_recovery_code_sha256']
