#!/usr/bin/env python3
"""Read-only postmortem. No Popen, simulator, signal or execution-guard edits."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import *
from audit_site import proc
from strict_screen import input_identity

def main():
 run=RAW/'attempts/BASE_GEMM_5de274d3-f296-4ee8-a577-17cc661e718e'
 manifest=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
 binding=json.loads((PACK/'RUNTIME_BINDINGS.json').read_text())
 observed=json.loads((run/'LOADED_FILES_SHA256.json').read_text())
 expected={str(Path(r['path']).resolve()):r['sha256'] for r in manifest['runtime_files']}
 rows=[]
 for item in observed:
  path=Path(item['path']);digest=expected.get(str(path.resolve()))
  with path.open('rb') as f:magic=f.read(4)
  rows.append(dict(path=str(path),observed_sha256=item['sha256'],preregistered_sha256=digest or 'UNREGISTERED_AT_LAUNCH',
      classification_current_file='ELF' if magic==b'\x7fELF' else 'NON_ELF_DATA',
      observed_equals_preregistered=digest==item['sha256'],current_sha256=sha(path)))
 mismatches=[r for r in rows if not r['observed_equals_preregistered']]
 assert len(mismatches)==1 and mismatches[0]['path']=='/etc/ld.so.cache'
 assert mismatches[0]['classification_current_file']=='NON_ELF_DATA'
 assert all(r['observed_equals_preregistered'] for r in rows if r['classification_current_file']=='ELF')
 assert all(sha(PACK/n)==h for n,h in manifest['files'].items())
 assert all(sha(r['path'])==r['sha256'] for r in manifest['runtime_files'])
 assert git(CORE,'rev-parse','HEAD')==binding['combined_core_commit'] and not git(CORE,'status','--porcelain')
 for workload in ['GEMM','Gaussian']:
  s=json.loads((PACK/f'specs/BASE_{workload}.json').read_text());input_identity(s)
 terminal=json.loads((run/'RUN_TERMINAL.json').read_text())
 initial=json.loads((run/'RESOURCE_START.json').read_text())
 final=json.loads((run/'RESOURCE_FINAL.json').read_text())
 matrix=json.loads((RAW/'MATRIX_TERMINAL.json').read_text())
 assert matrix['actual_starts']==1 and terminal['returncode']==-15 and not terminal['identity_pass']
 assert proc(3739908) is None and proc(3740731) is None
 table(PACK/'OBSERVED_MAPPING_IDENTITY.tsv',rows)
 write(PACK/'STOP_EVIDENCE.json',dict(status='STOP_RUNTIME_MAPPING_MANIFEST_GAP_NO_RETRY_NO_PERFORMANCE_RESULT',
     utc=now(),attempt_uuid='5de274d3-f296-4ee8-a577-17cc661e718e',point='BASE_GEMM',
     actual_starts=1,actual_start_cap=8,full_strict_passes=0,
     observed_completed_kernel_headers=(run/'simulator.stdout').read_text().count('kernel_name = '),
     accepted_cycles='UNAVAILABLE',BASE_calibration='NOT_REACHED',all_arm_ratios='UNAVAILABLE',
     identity_failure=mismatches,all_observed_ELF_SHA_match=True,overall_identity_pass=False,
     responsible_component='AG runtime freeze/first-map classification mismatch; loader cache was not preregistered',
     no_posthoc_whitelist=True,no_rerun=True,no_replacement=True,no_subsequent_dispatch=True,
     source_or_private_runtime_changed_after_launch=False,all197_operative_files_unchanged=True,
     all_frozen_runtime_files_unchanged=True,all_original_members_stat_stable_and_lists_SHA_match=True,
     own_coordinator_PID=3739908,own_coordinator_start_ticks=905150778,
     own_sim_PID=3740731,own_sim_start_ticks=905152384,both_own_instances_absent=True,
     signal=json.loads((run/'OWN_STOP_SIGNAL.json').read_text()),
     returncode=-15,resource_usage=terminal['resource_usage'],
     resource_final_decision=final['decision'],
     host_global_swap_deltas={k:final['snapshot'][k]-initial[k] for k in ['pswpin','pswpout']},
     cgroup_OOM_delta={k:final['snapshot']['cgroup']['events'][k]-initial['cgroup']['events'][k] for k in ['oom','oom_kill']},
     cgroup_swap_growth_bytes=int(final['snapshot']['cgroup']['memory.swap.current'])-int(initial['cgroup']['memory.swap.current']),
     stdout_bytes=(run/'simulator.stdout').stat().st_size,stdout_sha256=sha(run/'simulator.stdout'),
     stderr_bytes=(run/'simulator.stderr').stat().st_size,stderr_sha256=sha(run/'simulator.stderr'),
     raw=str(run),raw_index_sha256=sha(run/'FILES_SHA256.tsv'),
     cache_transience='LOADER_ROLE_EXPLANATION_NOT_AN_OBSERVED_UNMAP_IN_THIS_STOPPED_ATTEMPT',
     retrospective_identity_acceptance=False))
 print('STOP evidence verified: 1 start, 0 full strict; all observed ELF SHAs match, only unregistered non-ELF loader cache; frozen files intact.')

if __name__=='__main__':main()
