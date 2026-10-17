#!/usr/bin/env python3
"""CPU metadata/proof consumer. Never opens trace bodies or launches tools.

Only immutable git blobs, /proc, the four exact lists, and member stat metadata
are read. This program deliberately has no body-scan/resume/launch switch.
"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/workspace/repos/accel-sim-framework')
CORE_REPO = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
A = 'f5c37d6edcce832a72cb0830021bffa78df6cc13'
T = 'f520a445436b57c0a0f2494fb858a1636f04d2bc'
U = '16e56912cfd02f2311a1603a29415dee829fd495'
FRAMEWORK = '18a68dcccd795f1b6cda75504e9450d00c9cee02'
CORE = '6fba0136f8465b59fe5858a950fa39efb265f654'
AP = 'docs/dtc_l1/iscas2027/service_closure_174_v1'
TP = 'docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1'
UP = 'docs/dtc_l1/review_packs/DTC_T1C_HOLDOUT_V1'
TARGETS = {'Gaussian': (T, TP, 510, 283685120),
           'GEMM': (T, TP, 1, 739246080),
           'DWT2D': (U, UP, 10, 148684429),
           'BICG': (U, UP, 2, 145666048)}
NA = 'UNAVAILABLE'
provenance = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(name, value):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def table(name, rows, columns=None):
    rows = list(rows)
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns or list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def blob(commit, path, dest=None, repo=REPO):
    data = subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:{path}'])
    provenance.append(dict(repo=str(repo), commit=commit, path=path, sha256=sha(data), bytes=len(data)))
    if dest:
        p = ROOT / dest
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return data


def rows(data):
    return list(csv.DictReader(io.StringIO(data.decode()), delimiter='\t'))


def resource_probe():
    pressure = {}
    for kind in ('io', 'memory', 'cpu'):
        pressure[kind] = Path(f'/proc/pressure/{kind}').read_text()
    processes = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            comm = (p / 'comm').read_text().strip()
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        if comm == 'accel-sim.out' or ('/workspace/dtc-t1c-holdout-174-v1/' in cmd and int(p.name) != os.getpid()):
            processes.append(dict(pid=int(p.name), comm=comm,
                                  u_path_in_cmd='/workspace/dtc-t1c-holdout-174-v1/' in cmd))
    full10 = float(pressure['io'].split('full avg10=')[1].split()[0])
    disk = shutil.disk_usage(ROOT)
    # A conservative W read-side guard; this is not a change to T/U admission.
    reasons = []
    if full10 >= 5:
        reasons.append('IO_FULL_AVG10_GE_5_PERCENT')
    if disk.used / (disk.used + disk.free) >= .98:
        reasons.append('FILESYSTEM_USED_GE_98_PERCENT')
    if any(p['u_path_in_cmd'] for p in processes):
        reasons.append('U_PATH_PROCESS_OBSERVED')
    return dict(utc=datetime.now(timezone.utc).isoformat(), host=socket.gethostname(),
                uid=os.getuid(), pressure=pressure, filesystem=dict(total=disk.total,
                used=disk.used, free=disk.free), matching_processes=processes,
                w_scan_guard_reasons=reasons, body_scan_started=False,
                body_scan_decision='DEFERRED_SAFE_STOP' if reasons else 'NOT_IMPLEMENTED_IN_METADATA_CONSUMER',
                unrelated_processes_preserved=True)


def build():
    preflight = resource_probe()
    assert preflight['host'] == 'huangrulin-174', 'Wrong host: do not substitute inputs'
    dump('RESOURCE_PREFLIGHT.json', preflight)
    source = json.loads(blob(T, TP + '/SOURCE_IDENTITY.json', 'inputs/T_SOURCE_IDENTITY.json'))
    blob(U, UP + '/SOURCE_INPUT_IDENTITY.json', 'inputs/U_SOURCE_INPUT_IDENTITY.json')
    blob(U, UP + '/AUTHORITY_TERMINAL.json', 'inputs/U_AUTHORITY_TERMINAL.json')
    source_checks = []
    for r in source['files']:
        observed = sha(Path(r['path']).read_bytes())
        assert observed == r['sha256'], ('Frozen source/proof changed', r['path'])
        source_checks.append(dict(path=r['path'], expected_sha256=r['sha256'],
                                  observed_sha256=observed, status='PASS', repo_commit=r['repo_commit']))
    table('SOURCE_IDENTITY_CHECKS.tsv', source_checks)
    raw_body = blob(A, AP + '/review_pack/trace_body_v1/KERNEL_BODY_AUDIT.tsv')
    body = [r for r in rows(raw_body) if r['workload'].lower() in {w.lower() for w in TARGETS}]
    table('inputs/KERNEL_BODY_AUDIT.tsv', body)
    for name in ('MEMORY_WIDTHS.tsv', 'OPCODE_FORMS.tsv', 'WORKLOAD_SUMMARY.tsv'):
        rr = rows(blob(A, AP + '/review_pack/trace_body_v1/' + name))
        rr = [r for r in rr if r['workload'].lower() in {w.lower() for w in TARGETS}]
        table('inputs/' + name, rr)
    blob(A, AP + '/review_pack/trace_body_v1/ORACLE_RECEIPT.json', 'inputs/ORACLE_RECEIPT.json')
    blob(A, AP + '/HOTSPOT_SHARED_FORMAT_REVIEW_V1.md', 'inputs/HOTSPOT_BOUNDARY.md')
    blob(T, TP + '/SCIENTIFIC_SCOPE.md', 'inputs/T_SCIENTIFIC_SCOPE.md')
    scope, order, commands, counts, reuse, risks, checks = [], [], [], [], [], [], []
    opcodes = rows((ROOT / 'inputs/OPCODE_FORMS.tsv').read_bytes())
    for workload, (commit, prefix, expected_members, expected_inst) in TARGETS.items():
        spec = json.loads(blob(commit, prefix + f'/inputs/{workload}_OO128_SPEC.json'))
        accepted_list = blob(commit, prefix + f'/inputs/{workload}_kernelslist.g', f'inputs/{workload}_kernelslist.g')
        current_list = Path(spec['trace_list']).read_bytes()
        assert current_list == accepted_list
        assert sha(current_list) == spec['trace_list_sha256']
        members = spec['members']
        assert len(members) == expected_members
        ordered_names = [s.strip() for s in accepted_list.decode().splitlines() if s.strip().startswith('kernel-')]
        assert ordered_names == [Path(m['path']).name for m in members]
        br = sorted([r for r in body if r['workload'].lower() == workload.lower()], key=lambda r:int(r['ordinal']))
        assert len(br) == expected_members
        assert sum(int(r['active_thread_instructions']) for r in br) == expected_inst == spec['expected_instructions']
        scope.append(dict(workload=workload, kind='original_list', ordinal=0, path=spec['trace_list'],
                          sha256=sha(current_list), bytes=len(current_list), provenance_commit=commit,
                          current_verification='READ_ONLY_SHA256_MATCH'))
        totals = {}
        for m, b in zip(members, br):
            assert m['path'] == b['path'] and m['sha256'] == b['sha256']
            st = Path(m['path']).stat()  # No trace body open or rehash.
            assert st.st_size == m['bytes']
            scope.append(dict(workload=workload, kind='trace_member', ordinal=b['ordinal'], path=m['path'],
                              sha256=m['sha256'], bytes=st.st_size, provenance_commit=commit,
                              current_verification='STAT_SIZE_ONLY_SHA_REUSED_ACCEPTED_PROOF'))
            order.append(dict(workload=workload, **{k:b[k] for k in ('ordinal','kernel','binary_version','trace_version',
                'complete_ctas','complete_warps','warp_instruction_records','active_thread_instructions',
                'sparse_mask_base_stride_records','unaligned_lane_memory_addresses','coverage')},
                stream_id=NA, source_invalidate_event='NOT_A_TRACE_COMMAND;SEE_SOURCE_DEFINED_INVALIDATE.tsv',
                ordering='LIST_ORDINAL_ONLY_NOT_EXECUTION_HAPPENS_BEFORE'))
            paths = json.loads(b['memory_paths'])
            for cls, n in paths.items():
                totals[cls] = totals.get(cls, 0) + n
                counts.append(dict(workload=workload, ordinal=b['ordinal'], kernel=b['kernel'], pc=NA,
                    access_class=cls, count=n, unit='DYNAMIC_WARP_INSTRUCTION_RECORDS', evidence='ACCEPTED_CPU_BODY_PROOF',
                    active_lane_count=NA, byte_mask=NA, sector_mask=NA))
            reuse.append(dict(workload=workload, segment=f"kernel-{b['ordinal']}", kernel=b['kernel'],
                prior_kernel_candidates='1..'+str(int(b['ordinal'])-1) if int(b['ordinal'])>1 else 'NONE',
                prior_read_current_read_lines=NA, previous_kernel_write_current_read_lines=NA,
                reusable_distinct_lines=NA, line_bytes=128, byte_conflicts=NA, status='DEFERRED_NO_ADDRESS_SCAN'))
            risks.append(dict(workload=workload, ordinal=b['ordinal'], kernel=b['kernel'], read_pc=NA, write_pc=NA,
                cacheable_read_warp_records=paths.get('CACHEABLE_GLOBAL_LOAD',0), store_warp_records=paths.get('ORDINARY_STORE',0),
                same_line_read_write_candidates=NA, byte_overlap_candidates=NA,
                same_warp_write_then_read=NA, cross_warp_order='UNKNOWN',
                actual_old_mapping_exposure=NA, status='RISK_SCREEN_ONLY_NO_PC_OR_ADDRESS_PROOF'))
        wo = [r for r in opcodes if r['workload'].lower() == workload.lower()]
        # Zero only when the complete opcode inventory rules these paths out.
        for cls, prefixes in [('ATOMIC',('ATOM','RED')),('BYPASS_GLOBAL_LOAD',('LDGSTS',)),
                              ('FENCE',('MEMBAR','FENCE'))]:
            found = [r for r in wo if r['opcode'].startswith(prefixes)]
            assert not found, ('Requires explicit classification', found)
            if cls == 'BYPASS_GLOBAL_LOAD':
                assert all(r['opcode']=='LDG.E.SYS' for r in wo if r['opcode'].startswith('LDG'))
            totals[cls] = 0
        for cls,n in totals.items():
            counts.append(dict(workload=workload, ordinal='ALL', kernel='ALL', pc=NA, access_class=cls,
                count=n, unit='DYNAMIC_WARP_INSTRUCTION_RECORDS', evidence='ACCEPTED_BODY_PLUS_COMPLETE_OPCODE_INVENTORY',
                active_lane_count=NA, byte_mask=NA, sector_mask=NA))
        ordinal=0
        for command_position, line in enumerate(accepted_list.decode().splitlines(),1):
            if not line.strip():
                continue
            if line.startswith('kernel-'):
                ordinal+=1
                kind='KERNEL_LIST_ENTRY'
                address=byte_count=NA
            elif line.startswith('MemcpyHtoD,'):
                kind='MEMCPY_HTOD'; _, address, byte_count = line.split(',')
            else:
                kind='UNCLASSIFIED_COMMAND'; address=byte_count=NA
            assert kind != 'UNCLASSIFIED_COMMAND', line
            commands.append(dict(workload=workload, list_position=command_position, kind=kind,
                kernel_ordinal=ordinal if kind=='KERNEL_LIST_ENTRY' else NA,
                command=line, address=address, bytes=byte_count,
                timing='LIST_ORDER_ONLY', source_invalidate='UNAVAILABLE_DYNAMIC_INVOCATION'))
        checks.append(dict(workload=workload, members=expected_members, active_thread_instructions=expected_inst,
                           list_and_order='PASS', accepted_member_sha_vs_body_proof='PASS',
                           current_members='STAT_ONLY_NO_REHASH', body_scanned_this_lane=False,
                           source_sparse_mask_records=sum(int(b['sparse_mask_base_stride_records']) for b in br)))
    table('TRACE_SCOPE_SHA256.tsv', scope)
    table('KERNEL_ORDER_AND_COVERAGE.tsv', order)
    table('COMMAND_SEQUENCE.tsv', commands)
    table('ACCESS_CLASS_COUNTS.tsv', counts)
    table('CROSS_KERNEL_ALIAS_AND_REUSE.tsv', reuse)
    table('WRITE_READ_RISK.tsv', risks)
    table('INPUT_CHECKS.tsv', checks)
    # Bind each source excerpt to the immutable implementation being reviewed.
    excerpts = [
      (CORE_REPO,CORE,'src/gpgpu-sim/shader.cc',[(2622,2656),(3899,3930),(4007,4015)]),
      (CORE_REPO,CORE,'src/gpgpu-sim/gpu-sim.cc',[(1748,1756),(2518,2528)]),
      (CORE_REPO,CORE,'src/gpgpu-sim/dtc-l1-common.h',[(560,586),(690,718)]),
      (REPO,FRAMEWORK,'gpu-simulator/trace-parser/trace_parser.cc',[(100,120),(152,184),(282,328),(390,437)]),
      (REPO,FRAMEWORK,'gpu-simulator/trace-driven/trace_driven.cc',[(384,434)]),
      (REPO,FRAMEWORK,'gpu-simulator/accel-sim.cc',[(48,70),(92,119)]),
    ]
    for i,(repo,commit,path,spans) in enumerate(excerpts,1):
        data=blob(commit,path,repo=repo)
        lines=data.decode().splitlines()
        out=[f'{repo} {commit}:{path} SHA256={sha(data)}']
        for first,last in spans:
            out += [f'{n}: {lines[n-1]}'.rstrip() for n in range(first,last+1)]
        (ROOT/f'inputs/SOURCE_EXCERPT_{i}.txt').write_text('\n'.join(out)+'\n')
    for path,dest in [('configs/dtc_l1/fast64/FAST64_OO.config','inputs/FROZEN_FAST64_OO.config'),
       (AP+'/config/FINITE_PRIMARY_COMMON.config','inputs/FROZEN_FINITE_PRIMARY_COMMON.config')]:
        blob(A,path,dest)
    blob(FRAMEWORK, 'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config', 'inputs/FROZEN_trace.config')
    table('PROVENANCE_SHA256.tsv', provenance)
    dump('CPU_READONLY_CHECKS.json', dict(status='PASS_METADATA_AND_ACCEPTED_PROOF_ONLY',
        frozen=dict(A=A,T=T,U=U,framework=FRAMEWORK,core=CORE), new_simulation_attempts=0,
        trace_body_opens=0, trace_member_bytes_rehashed=0, prior_raw_reads=0, prior_raw_writes=0,
        decoder_changes=0, u_snapshot='IMMUTABLE_GIT_COMMIT_ONLY_NO_U_RAW',
        full_access_semantics_complete=False, scan_status='DEFERRED_SAFE_STOP',
        deferred=['PCs','128B line intersections','byte/sector masks','distinct lines','same-warp ordering']))


if __name__ == '__main__':
    build()
    print('PASS: metadata/proof pack built; no trace bodies opened, no simulation attempts')
