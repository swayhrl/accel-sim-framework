#!/usr/bin/env python3
"""Pin published inputs and independent eight UUID reservations; no launch."""
from common import *
import uuid


def main():
    provenance=[]
    selected=['LATEST_REPORT.md','STOP_RECORD.json','RESOURCE_CONTRACT.json','FROZEN_SOURCE_BINDINGS.json',
        'NORMAL_TERMINAL_EXPORT_GATE.json','METRIC_DICTIONARY.tsv','ORDERED_KERNELS.json',
        'inputs/X2/BUILD_TRACE_CPU_ONLY.cmake','inputs/X2/7_CTEST.json',
        'inputs/X2/NORMAL_EXPORT_CONTRACT.md','inputs/X2/CPU_NORMAL_ENTRYPOINT_TESTS.json',
        'inputs/X2/scripts/run_cpu_normal_entrypoint_tests.py','inputs/X2/scripts/parse_normal_export.py',
        'inputs/CPU_EXPORT_FIXTURE_BASE.config',
        'scripts/normal_export_fixture.cc','scripts/abi_stats_dump.inc','scripts/test_full_strict_cpu.py',
        'scripts/strict_matrix.py','scripts/common.py','scripts/run_matrix.py','scripts/supplement_export_gate.py',
        'config/FAST64_OO.config','config/FINITE_PRIMARY_COMMON.config','config/trace.config','config/K0_64x8.config',
        'continuations/USER_RECHECK_20261018T030133Z/FINAL_AUTHORITY_RELEASE.json',
        'continuations/USER_RECHECK_20261018T030133Z/AUTHORITY_TERMINAL.json',
        'continuations/USER_RECHECK_20261018T030133Z/STOP_RECORD.json',
        'continuations/USER_RECHECK_20261018T030133Z/EXECUTION_RESOURCES.tsv',
        'continuations/USER_RECHECK_20261018T030133Z/scripts/run_matrix.py']
    for name in selected:
        provenance.append(copy_blob(FW_REPO,AA5,AA5_PACK+'/'+name,'inputs/AA5/'+name))
    for name in ['LATEST_REPORT.md','AUTHORITY_DECISION.md']:
        provenance.append(copy_blob(FW_REPO,AB,AB_PACK+'/'+name,'inputs/AB/'+name))
    for name in ['SOURCE_IDENTITY.json','inputs/GEMM_OO128_SPEC.json','inputs/Gaussian_OO128_SPEC.json',
                 'inputs/GEMM_kernelslist.g','inputs/Gaussian_kernelslist.g','inputs/KERNEL_BODY_AUDIT.tsv']:
        provenance.append(copy_blob(FW_REPO,T,T_PACK+'/'+name,'inputs/T/'+name))
    table(PACK/'UPSTREAM_SOURCE_SHA256.tsv',provenance)
    path=PACK/'UUID_RESERVATIONS.json'
    if not path.exists():
        labels=[(a,w) for a in ['BASE','AC','AD','AE'] for w in ['GEMM','Gaussian']]
        write(path,dict(cohort='DISCOVERY_OPT',registration_status='RESERVED_CPU_PREPARATION_NOT_EXECUTABLE',
            actual_start_budget=8,max_new_sim_concurrency=1,actual_starts=0,
            rows=[dict(order=i,arm=a,workload=w,uuid=str(uuid.uuid4()),
                       status='CPU_QUALIFICATION_PENDING' if a!='BASE' else 'BASE_CPU_AND_CALIBRATION_PENDING')
                  for i,(a,w) in enumerate(labels)],
            replacements=False,reruns=False,AF_in_screen=False),exclusive=True)
    reservations=json.loads(path.read_text())
    assert len(reservations['rows'])==len({r['uuid'] for r in reservations['rows']})==8
    assert not ({r['uuid'] for r in reservations['rows']} & {
        'd0a29a82-c171-46e4-b077-d7ccfd2c4b7a','aba7a8eb-e82c-4a18-b410-5d568f819f27',
        'dd65b440-dc75-4632-9f7b-3e8a1062d5a1','a9d64a6f-4fb5-4e3d-883c-ae75f1ac5f89'})
    write(PACK/'BASE_SOURCE_BINDINGS.json',dict(core_base=X2,framework_build_base=FRAMEWORK_BUILD,
        AA5_published=AA5,AA5_actual_starts=1,AA5_full_strict_passes=0,
        AA5_prefix_not_calibration=True,core_worktree=str(CORE),framework_worktree=str(FW),
        raw_root=str(RAW),build_root=str(BUILD),
        expected_full_BASE_cycles=dict(GEMM=1071405,Gaussian=3278356),
        phase='CPU_PREPARATION_NO_EXECUTABLE_PERFORMANCE_REGISTRATION',new_simulation_attempts=0))
    print(json.dumps(dict(status='PINNED_INPUT_METADATA_AND_8_UUID_RESERVATIONS',files=len(provenance),actual_starts=0)))


if __name__=='__main__':
    main()
