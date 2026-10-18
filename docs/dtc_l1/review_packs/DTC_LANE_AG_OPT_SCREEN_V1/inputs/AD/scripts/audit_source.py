"""Read only Core diff/critical functions; write AD review receipts only."""
import argparse, hashlib, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--core',required=True,type=Path);p.add_argument('--pack',required=True,type=Path);a=p.parse_args()
base='e32afdcf44be3374ff36d22568ed01a075459b6f'
def git(*args):return subprocess.check_output(['git',*args],cwd=a.core)
head=git('rev-parse','HEAD').decode().strip()
def sha(s):return hashlib.sha256(s).hexdigest()
allowed=['CMakeLists.txt','src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','tests/dtc_l1_ad_off_trace.cc','tests/dtc_l1_progressive_ldst_test.cc','tests/dtc_l1_progressive_wakeup_test.cc']
changed=git('diff','--name-only',base,head).decode().splitlines();assert sorted(changed)==sorted(allowed)
def body(s,sig):
    start=s.index(sig);pos=s.index('{',start);depth=0
    for end in range(pos,len(s)):
        if s[end]=='{':depth+=1
        if s[end]=='}':
            depth-=1
            if depth==0:return s[start:end+1]
    raise AssertionError(sig)
protected={
'src/gpgpu-sim/shader.cc':[
 'bool ldst_unit::dtc_l1_oo_consume_response(',
 'bool ldst_unit::dtc_l1_oo_memory_cycle(',
 'void ldst_unit::dtc_l1_oo_issue_lower_requests(',
 'bool ldst_unit::dtc_l1_oo_select_ready(',
 'bool ldst_unit::dtc_l1_oo_writeback_ready(',
 'void ldst_unit::dtc_l1_oo_complete_instruction(',
 'bool ldst_unit::dtc_l1_m4_observe_admit(',
 'void ldst_unit::dtc_l1_m4_observe_complete(',
 'void ldst_unit::invalidate(', 'void ldst_unit::flush('],
'src/gpgpu-sim/dtc-l1-common.h':[
 '  lookup_invalidation_result invalidate_lookup(',
 '  bool retire_one_ready(', '  bool retire_ready_uid(']}
checks=[]
for path,functions in protected.items():
    left=git('show',base+':'+path).decode();right=(a.core/path).read_text()
    if path.endswith('common.h'):
        left=left[left.index('class oo_frontend {'):left.index('// Sector-aware continuation')]
        right=right[right.index('class oo_frontend {'):right.index('// Sector-aware continuation')]
    for sig in functions:
        l=body(left,sig);r=body(right,sig);assert l==r,(path,sig)
        checks.append(dict(path=path,function=sig,sha256=sha(l.encode()),status='BYTE_IDENTICAL'))
(a.pack/'SOURCE_ALLOWLIST.json').write_text(json.dumps(dict(base=base,head=head,status='PASS_STATIC_ALLOWLIST_AND_PROTECTED_BODIES',allowed=allowed,changed=changed,protected=checks),indent=2)+'\n')
(a.pack/'SOURCE_DIFF.patch').write_bytes(git('diff','--binary',base,head))
rows=['scope\tpath\tsha256']
for path in allowed: rows.append('AD_CORE\t'+path+'\t'+sha((a.core/path).read_bytes()))
rows.append('FIXED_X2\tsrc/gpgpu-sim/dtc-l1-common.h\t'+sha(git('show',base+':src/gpgpu-sim/dtc-l1-common.h')))
(a.pack/'SOURCE_SHA256.tsv').write_text('\n'.join(rows)+'\n')
print(json.dumps(dict(status='PASS',files=len(changed),protected_bodies=len(checks),head=head)))
