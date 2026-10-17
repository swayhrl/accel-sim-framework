"""CPU-only reservation and evidence capture. Contains no simulator launch path.

Missing scientific evidence is UNAVAILABLE, never an implicit PASS. This program
does not acquire any old lock or alter any other lane's files/processes.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import subprocess
import uuid
from datetime import datetime, timezone

PACK = Path(__file__).resolve().parents[1]
FW = PACK.parents[3]
ROOT = Path('/workspace/dtc-lane-aa-gaussian-174-v1')
PILOT = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-tag-pilot-174-v1/docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1')
U = Path('/workspace/dtc-t1c-holdout-174-v1')
CORE = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
BASE_CORE = '6fba0136f8465b59fe5858a950fa39efb265f654'
BASE_BINARY = Path('/workspace/dtc-service-closure-174-v1/build-r1-a1/accel-sim.out')


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def write(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def table(p, rows):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def proc(pid):
    p = Path('/proc') / str(pid)
    try:
        stat = p.joinpath('stat').read_text().rsplit(')', 1)[1].split()
        return dict(pid=int(pid), state=stat[0], start_ticks=int(stat[19]),
                    rss_bytes=int(stat[21])*os.sysconf('SC_PAGE_SIZE'),
                    argv=[v.decode(errors='replace') for v in p.joinpath('cmdline').read_bytes().split(b'\0') if v])
    except (FileNotFoundError, ProcessLookupError):
        return None


def snap():
    cg = Path('/sys/fs/cgroup')
    raw = {k: cg.joinpath(k).read_text().strip() for k in
           ['memory.current', 'memory.max', 'memory.swap.current', 'memory.swap.max',
            'memory.events', 'memory.pressure', 'io.pressure', 'io.stat', 'cpu.pressure']}
    ps = [r for p in Path('/proc').glob('[0-9]*') if (r := proc(p.name))]
    vm = dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
    return dict(utc=datetime.now(timezone.utc).isoformat(), host=socket.gethostname(),
                boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                cgroup=raw, meminfo=Path('/proc/meminfo').read_text(),
                pressure={k:Path('/proc/pressure', k).read_text() for k in ['memory','io','cpu']},
                disk_free_bytes=shutil.disk_usage(ROOT).free,
                pswpin=int(vm['pswpin']), pswpout=int(vm['pswpout']),
                all_project_rss_bytes=sum(p['rss_bytes'] for p in ps),
                processes=ps, proc_locks=Path('/proc/locks').read_text())


def read_options(paths):
    result = {}
    for p in paths:
        key = None
        for token in shlex.split(Path(p).read_text(), comments=True):
            if re.match(r'^-[A-Za-z_]', token):
                key = token
                result[key] = []
            else:
                assert key is not None
                result[key].extend(token.split())
    return result


def main():
    assert socket.gethostname() == 'huangrulin-174'
    assert git(FW, 'branch', '--show-current') == 'hrl/iscas2027-dtc-lane-aa-flush-factorial-174-v1'
    assert not (PACK/'PRE_REGISTRATION.tsv').exists(), 'Never overwrite a reserved UUID/plan'
    ROOT.mkdir(exist_ok=True)
    write(ROOT/'CPU_START_RESOURCES.json', snap())
    base_sha = git(FW, 'rev-parse', 'HEAD')
    identities = dict(observed_framework_base=base_sha, accepted_original_core=BASE_CORE,
                      accepted_original_binary_sha256=sha(BASE_BINARY),
                      new_core='UNAVAILABLE', new_binary_sha256='UNAVAILABLE',
                      new_build_framework_sha='UNAVAILABLE',
                      status='CPU_PREPARATION_ONLY_NOT_FULL_EXECUTION_PREREGISTRATION')
    assert identities['accepted_original_binary_sha256'] == 'fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b'
    assert git(CORE,'rev-parse','HEAD') == BASE_CORE
    write(PACK/'SOURCE_IDENTITY.json', identities)

    # Observe U without acquiring/releasing/rewriting its authority locks.
    ufiles = ['AUTHORITY_ACTIVE.json', 'AUTHORITY_TERMINAL.json',
              'TERMINAL_ARCHIVE_ACTIVE.json', 'TERMINAL_ARCHIVE_TERMINAL.json']
    udata = {}
    for name in ufiles:
        f = U/name
        if f.exists():
            udata[name] = json.loads(f.read_text())
            (PACK/'inputs').mkdir(exist_ok=True)
            (PACK/'inputs'/('U_'+name)).write_bytes(f.read_bytes())
    refs = []
    active = udata['AUTHORITY_ACTIVE.json']
    refs.append(dict(role='U_coordinator', pid=active['pid'], start_ticks=active['start_ticks']))
    for f in sorted((U/'attempts').glob('*/PID.json')):
        data = json.loads(f.read_text())
        for kind in ['runner', 'process']:
            refs.append(dict(role=f.parent.name+'/'+kind, pid=data[kind+'_pid'], start_ticks=data[kind+'_start_ticks']))
        for name in ['PID.json','RUN_TERMINAL.json']:
            src=f.parent/name
            if src.exists():
                (PACK/'inputs'/(f.parent.name+'_'+name)).write_bytes(src.read_bytes())
    arc=udata.get('TERMINAL_ARCHIVE_ACTIVE.json',{})
    if 'pid' in arc and 'start_ticks' in arc:
        refs.append(dict(role='U_terminal_archiver',pid=arc['pid'],start_ticks=arc['start_ticks']))
    for r in refs:
        r['observed_proc'] = proc(r['pid'])
        r['same_incarnation_present'] = r['observed_proc'] is not None and r['observed_proc']['start_ticks']==r['start_ticks']
    lock_lines=Path('/proc/locks').read_text().splitlines()
    locks=[]
    oldroots=[U,Path('/workspace/dtc-service-closure-174-v1/r2-attempts')]
    for oldroot in oldroots:
        for f in sorted(oldroot.glob('*.lock')):
            st=f.stat()
            owners=[]
            for line in lock_lines:
                columns=line.split()
                if len(columns)>6:
                    dev=columns[5].split(':')
                    if len(dev)==3 and (int(dev[0],16),int(dev[1],16),int(dev[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):
                        owners.append(line)
            locks.append(dict(path=str(f),inode=st.st_ino,device=st.st_dev,owners=owners))
    uproof=dict(observed_utc=datetime.now(timezone.utc).isoformat(), process_identities=refs,
                lock_observations=locks, terminal_authority=udata.get('AUTHORITY_TERMINAL.json'),
                terminal_archive=udata.get('TERMINAL_ARCHIVE_TERMINAL.json'),
                all_recorded_incarnations_absent=all(not r['same_incarnation_present'] for r in refs),
                all_observed_old_locks_released=all(not l['owners'] for l in locks),
                locks_acquired_by_AA=False, any_U_restart_by_AA=False,
                note='Archive failure is preserved; it is not a scientific PASS or authority grant.')
    write(PACK/'U_TERMINATION_PROOF.json',uproof)

    # Both original controls, not extra performance attempts.
    oldspec=json.loads((PILOT/'inputs/Gaussian_OO128_SPEC.json').read_text())
    tc_run=Path('/workspace/dtc-tag-pilot-174-v1/attempts/DTC_TAG_PILOT_V1_T1_C_Gaussian_63f15c5a-a731-4c07-a3ce-c65312142a50')
    tc_spec=json.loads((tc_run/'SPEC.json').read_text())
    old_run=next(Path('/workspace/dtc-service-closure-174-v1/r2-attempts').glob('*_41e02b7d-474d-4bf1-9f2b-b515aa326179'))
    controls=[]
    for name,run,cycles,uid in [('32x4',old_run,3798174,'41e02b7d-474d-4bf1-9f2b-b515aa326179'),
                                ('64x8',tc_run,3278356,'63f15c5a-a731-4c07-a3ce-c65312142a50')]:
        out=run/'simulator.stdout'
        text=out.read_text()
        echo={}
        for line in text.splitlines():
            if re.match(r'^-[A-Za-z_]',line):
                parts=line.split('#',1)[0].split(None,1)
                if len(parts)==2: echo[parts[0]]=parts[1].strip().split()
        found=re.findall(r'^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$',text,re.M)
        assert int(found[-1])==cycles
        table(PACK/'inputs'/f'ORIGINAL_{name}_OPTION_ECHO.tsv',
              [dict(option=k,value=json.dumps(v)) for k,v in sorted(echo.items())])
        control=dict(tag=name,uuid=uid,cycles=cycles,stdout_sha256=sha(out),
                     terminal_sha256=sha(run/'RUN_TERMINAL.json'),run_dir=str(run),
                     role='CALIBRATION_REFERENCE_ONLY_NOT_A_NEW_K0')
        controls.append(control)
    write(PACK/'ACCEPTED_ORIGINAL_REFERENCES.json',controls)

    ordered=json.loads((PILOT/'ORDERED_KERNELS.json').read_text())['Gaussian']
    assert len(ordered)==len(oldspec['members'])==510
    assert sum(r['active_instructions'] for r in ordered)==283685120
    listing=Path(oldspec['trace_list'])
    assert sha(listing)==oldspec['trace_list_sha256']
    (PACK/'inputs/Gaussian_kernelslist.g').write_bytes(listing.read_bytes())
    lines=[s.strip() for s in listing.read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')]
    assert [s for s in lines if s.startswith('kernel-')]==[Path(m['path']).name for m in oldspec['members']]
    assert all(s.startswith(('kernel-','MemcpyHtoD,')) for s in lines)
    members=[]
    for m,r in zip(oldspec['members'],ordered):
        assert Path(m['path']).stat().st_size==m['bytes']
        actual=sha(m['path'])
        assert actual==m['sha256']==r['member_sha256']
        assert m['path']==r['member_path']
        members.append(dict(ordinal=r['ordinal'],path=m['path'],sha256=actual,bytes=m['bytes']))
    table(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv',members)
    write(PACK/'ORDERED_KERNELS.json',ordered)
    with (PILOT/'inputs/KERNEL_BODY_AUDIT.tsv').open() as f:
        body=[r for r in csv.DictReader(f,delimiter='\t') if r['workload'].lower()=='gaussian']
    table(PACK/'inputs/GAUSSIAN_KERNEL_BODY_AUDIT.tsv',body)
    write(PACK/'INPUT_PREFLIGHT.json',dict(status='PASS_REHASHED_ORIGINAL_FULL_INPUT',
          list_path=str(listing),list_sha256=sha(listing),members_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),
          ordered_sha256=sha(PACK/'ORDERED_KERNELS.json'),kernel_count=510,
          active_thread_instructions=283685120,complete_ctas=sum(r['complete_ctas'] for r in ordered),
          full_list_commands=len(lines),
          active_instruction_proof='REUSED_ACCEPTED_CPU_BODY_AUDIT_BOUND_TO_REHASHED_510_MEMBERS',
          independent_new_trace_decode=False,new_simulator_launches=0))

    # Preserve exact existing config order. Only logical sets/ways overlays vary.
    config=[]
    for entry in tc_spec['configs'][:3]:
        source=Path(entry['path'])
        assert sha(source)==entry['sha256']
        dest=PACK/'config'/source.name
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(source.read_bytes())
        config.append(dest)
    plans=[]
    deltas=[]
    matrix=[]
    for priority,(name,k,sets,ways) in enumerate([('K0_32x4',0,32,4),('K0_64x8',0,64,8),('K1_32x4',1,32,4),('K1_64x8',1,64,8)]):
        uid=str(uuid.uuid4())
        overlay=PACK/'config'/f'TAG_{sets}x{ways}.config'
        if not overlay.exists():
            overlay.write_text(f'-gpgpu_dtc_l1_logical_sets {sets}\n-gpgpu_dtc_l1_logical_ways {ways}\n')
        paths=config+[overlay]
        opts=read_options(paths)
        expected=dict(tc_spec['expected_effective_options'])
        expected['-gpgpu_dtc_l1_logical_sets']=[str(sets)]
        expected['-gpgpu_dtc_l1_logical_ways']=[str(ways)]
        assert opts==expected
        spec=dict(label=name,attempt_uuid=uid,priority=priority,K=k,sets=sets,ways=ways,
             status='RESERVED_UNBOUND_DO_NOT_EXECUTE',new_core_sha='UNAVAILABLE',
             new_binary_sha256='UNAVAILABLE',new_framework_build_sha='UNAVAILABLE',
             framework_preparation_base_sha=base_sha,K_option_name='UNAVAILABLE_PENDING_LANE_X',
             K_semantics='OFF' if k==0 else 'ON_SOURCE_DEFINED_INVALIDATE_ONLY',
             configs=[dict(path=str(p),sha256=sha(p)) for p in paths],
             expected_common_and_tag_effective_options=opts,
             trace_list=str(listing),trace_list_sha256=sha(listing),
             members_manifest_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),
             ordered_kernel_manifest_sha256=sha(PACK/'ORDERED_KERNELS.json'),
             expected_kernel_count=510,expected_active_thread_instructions=283685120,
             expected_complete_ctas=sum(r['complete_ctas'] for r in ordered),
             expected_cores=64,expected_active_pib=128,expected_physical_lines=640,
             expected_ordinary_kib=16,expected_shared_kib=96,
             wall_timeout_seconds=7200,actual_start_limit=1,
             wrapper_recovery='SAME_UUID_SAME_DEADLINE_NO_SECOND_SIMULATOR_START',
             historical_K0_calibration_cycles=3798174 if sets==32 else 3278356,
             event_count_contract='UNAVAILABLE_PENDING_LANE_V_X_Y',
             lower_return_sector_numeric_proof='UNAVAILABLE',numeric_load_value_proof='UNAVAILABLE',
             requires_full_committed_pushed_fetched_preregistration=True,
             dependencies=['U_TERMINAL_AND_LOCKS','V','W','X_CORE_PUSH_FETCH','Y_PASS','Z','EVENT_REACHABILITY','NEW_K0_IDENTITY_OPTIONS_BEHAVIOR'])
        write(PACK/'specs'/f'{name}.json',spec)
        plans.append(dict(point=name,uuid=uid,K=k,sets=sets,ways=ways,priority=priority,
                     spec_sha256=sha(PACK/'specs'/f'{name}.json'),timeout_seconds=7200,
                     status='RESERVED_UNBOUND_NOT_LAUNCHABLE',new_core_sha='UNAVAILABLE',new_binary_sha256='UNAVAILABLE'))
        matrix.append(dict(point=name,uuid=uid,K=k,sets=sets,ways=ways,actual_starts=0,
                           status='NOT_STARTED_SCIENTIFIC_GATE_UNBOUND',natural_exit='UNAVAILABLE',
                           cycles='UNAVAILABLE',active_instructions='UNAVAILABLE',strict='NOT_RUN'))
        for option in sorted(opts):
            deltas.append(dict(point=name,option=option,value=json.dumps(opts[option]),
                          role='TAG_FACTOR' if option in ['-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'] else 'FROZEN_COMMON'))
        deltas.append(dict(point=name,option='UNBOUND_LANE_X_K_OPTION',value=k,role='K_FACTOR_CONCEPT_ONLY_NOT_A_VALID_CLI_OPTION'))
        write(ROOT/'receipts'/uid/'STRICT.json',dict(uuid=uid,point=name,status='NOT_RUN',actual_starts=0,
                   reason='Scientific and binary gates unbound; no raw simulator output exists',
                   event_count='UNAVAILABLE',invalidated_mapping_count='UNAVAILABLE',
                   references_legal_after_invalidation='UNAVAILABLE'))
        table(ROOT/'receipts'/uid/'RAW_SHA256.tsv',[dict(path='UNAVAILABLE_NO_RUN',sha256='UNAVAILABLE',status='NOT_CREATED')])
    table(PACK/'PRE_REGISTRATION.tsv',plans)
    table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    table(PACK/'FULL_MATRIX.tsv',matrix)
    write(PACK/'PRE_REGISTRATION_STATUS.json',dict(status='RESERVATION_ONLY_NOT_SCIENTIFIC_ADMISSION',
          reserved_uuids=4,full_attempt_ceiling=4,actual_starts=0,canary_starts=0,
          new_source_binary_event_contracts_bound=False,launchable=False,
          note='Four specs reserve design and UUIDs. Missing source, binary and event contracts must not be represented as completed preregistration.'))
    write(ROOT/'CPU_END_RESOURCES.json',snap())
    print('CPU reservation complete; four UUIDs, zero simulator starts; not launchable.')


if __name__=='__main__':
    main()
