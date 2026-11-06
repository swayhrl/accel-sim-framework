"""Controlled Oracle helpers. Import is inert; no model, registration, or signals.

Only Main may integrate these pure projections in the sole owner's bounded
registry mutation. This module deliberately contains no scientific launcher.
"""
import copy, hashlib, json, os, pathlib, re, time

MODES = {'OFF_MATCHED': 0, 'M_DATAREAD': 1, 'L2_DATAREAD': 2, 'L1_DATAREADY': 3}
G = 1024 ** 3

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def append_request_projection(registry, candidate, matrix_rows, qualified_modes, stage):
    """No file/authority access: call only with mutator's passed EX snapshot."""
    require(stage in ['INITIAL_FIXED8', 'CONDITIONAL_CORE32_EXTENSION'], 'BAD_STAGE')
    qualified_modes = set(qualified_modes)
    require(qualified_modes and qualified_modes <= set(MODES) - {'OFF_MATCHED'}, 'NO_QUALIFIED_ORACLE')
    expected_n = 8 if stage == 'INITIAL_FIXED8' else 24
    rows = [r for r in matrix_rows if bool(r['initial_fixed8']) == (expected_n == 8)
            and r['mode'] in qualified_modes | {'OFF_MATCHED'}]
    require(len(rows) == expected_n * (1 + len(qualified_modes)), 'CONDITIONAL_MATRIX_SIZE')
    require(len({(r['input_digest'], r['mode']) for r in rows}) == len(rows), 'DUPLICATE_MATRIX_IDENTITY')
    require(len({r['input_digest'] for r in rows}) == expected_n, 'INPUT_POPULATION_SIZE')
    require(all(r['design'] == 'DH' for r in rows), 'CH_BUDGET_ZERO')
    require(candidate['request'] not in registry['registered_future_requests'], 'REQUEST_ALREADY_EXISTS')
    require(candidate['budget'] == candidate['remaining'] == len(rows), 'EXACT_NEW_BUDGET')
    require(candidate['consumed'] == {} and candidate['model_automatic_retries'] == 0, 'NO_REUSE_RETRY')
    require(candidate['authority_commit'] == '18b1ee9d339902e555fc2e04ef51c84f77dfe1b1', 'AUTHORITY_MISMATCH')
    require(set(candidate['admitted_plan_ids']) == {r['plan_id'] for r in rows}, 'EXACT_STATIC_ROWS_REQUIRED')
    require(len(candidate['admitted_specs']) == len(rows), 'ADMITTED_SPEC_COUNT')
    result = copy.deepcopy(registry)
    result['registered_future_requests'][candidate['request']] = copy.deepcopy(candidate)
    require({k: v for k, v in result.items() if k != 'registered_future_requests'} ==
            {k: v for k, v in registry.items() if k != 'registered_future_requests'}, 'FOREIGN_HISTORY_CHANGE')
    require(all(result['registered_future_requests'][k] == v for k, v in registry['registered_future_requests'].items()),
            'FOREIGN_REQUEST_CHANGED')
    return result

def append_exact_route(before, block, cohorts):
    require(before.startswith(b'#!/bin/sh\nset -eu\n'), 'NATIVE_ROUTE_ANCHOR')
    require(block and block not in before, 'ROUTE_REAPPLY_FORBIDDEN')
    require(cohorts and len(set(cohorts)) == len(cohorts), 'BAD_EXACT_COHORTS')
    # Exact cohort alternatives, never a broad E2-* route swallowing other lanes.
    require(all(c.encode() in block for c in cohorts), 'MISSING_EXACT_ROUTE_COHORT')
    require(b'E2-*' not in block and b'E2-DTCORACLE-*' not in block, 'BROAD_ROUTE_FORBIDDEN')
    anchor = b'#!/bin/sh\nset -eu\n'
    after = anchor + block + before[len(anchor):]
    require(after.replace(block, b'', 1) == before, 'PRIOR_ROUTE_BYTES_CHANGED')
    return after

def append_lease_projection(lease, request, owner_pid, owner_start, controller_sha):
    require(lease['pid'] == owner_pid and lease['start_ticks'] == owner_start, 'OWNER_GENERATION')
    require(lease['controller_sha256'] == controller_sha, 'OWNER_SOURCE')
    require(request not in lease.get('additional_requests', []), 'LEASE_REAPPLY')
    result = copy.deepcopy(lease)
    result.setdefault('additional_requests', []).append(request)
    require({k: v for k, v in result.items() if k != 'additional_requests'} ==
            {k: v for k, v in lease.items() if k != 'additional_requests'}, 'PRIMARY_LEASE_CHANGED')
    return result

def owner_identity(pid=1498278, start_ticks=977758783):
    """Fresh /proc-only evidence; open FD is never interpreted as a held lock."""
    root = pathlib.Path('/proc') / str(pid)
    stat = (root / 'stat').read_text().rsplit(')', 1)[1].split()
    require(int(stat[19]) == start_ticks and stat[0] not in ['Z', 'X'], 'OWNER_NOT_LIVE')
    held = []
    for fd, suffix in [(3, '/root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock'),
                       (4, '/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock')]:
        p = root / 'fd' / str(fd)
        info = (root / 'fdinfo' / str(fd)).read_text()
        require(os.readlink(p) == suffix and re.search(r'lock:.*FLOCK\s+ADVISORY\s+WRITE\s+' + str(pid) + r'\s', info),
                'OWNER_ACTUAL_FLOCK_MISSING')
        held.append(dict(fd=fd, path=suffix, inode=p.stat().st_ino, fdinfo=info))
    return dict(pid=pid, start_ticks=start_ticks, held=held, affinity=sorted(os.sched_getaffinity(pid)))

def verify_option_echo(text, expected, historical270, mode):
    require(mode in MODES and len(historical270) == 270, 'FROZEN_270_REQUIRED')
    require(len(expected) == 271 and set(expected) == set(historical270) | {'-gpgpu_dtc_oracle_mode'}, 'EXACT_271_REQUIRED')
    require(all(expected[k] == v for k, v in historical270.items()), 'NONORACLE_OPTION_CHANGED')
    require(expected['-gpgpu_dtc_oracle_mode'] == [str(MODES[mode])], 'MODE_ENUM_MISMATCH')
    require(expected['-gpgpu_perfect_mem'] == ['0'] and expected['-l2_ideal'] == ['0'], 'INVALID_STOCK_ORACLE')
    values = {}
    for line in text.splitlines():
        m = re.match(r'^\s*(-\S+)\s+(.*?)\s*$', line)
        if m and m.group(1) in expected:
            new = m.group(2).split('#', 1)[0].split()
            require(m.group(1) not in values or values[m.group(1)] == new,
                    'CONFLICTING_OPTION_ECHO:' + m.group(1))
            values[m.group(1)] = new
    require(set(values) == set(expected), 'MISSING_OPTION_ECHO')
    require(values == expected, 'CORRUPT_OPTION_ECHO')
    return dict(expected_count=271, verified_count=271, mode=mode)

def oracle_counter_terminal(text, mode, require_exposure=False):
    """Latest cumulative block per physical unit, not sum of repeated snapshots.

    Counters supplement (never replace) original population, authenticated ROI,
    ref/PIB/physical/credit/Store/Atomic/Fence and actual native checks. Missing
    counters are an error. Final print placement must be independently frozen.
    """
    require(mode in MODES, 'UNKNOWN_MODE')
    mrows, l2rows = {}, {}
    for line in text.splitlines():
        if line.startswith('DTC_ORACLE_M_V1 '):
            d = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', line)}
            needed = {'mode','cluster','parents_enqueued','required_sectors','sectors_enqueued','parents_transferred',
                      'sectors_received','parents_closed','pending_parents','peak_parents','fifo_stalls','normal_grants'}
            require(set(d) == needed, 'M_COUNTER_SCHEMA')
            require(d['mode'] == MODES[mode], 'M_COUNTER_MODE')
            mrows[d['cluster']] = d
        if line.startswith('dtc_oracle_l2 '):
            d = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', line)}
            require(set(d) == {'sub_partition','eligible_seen','virtual_hit_served','returned','outstanding'}, 'L2_COUNTER_SCHEMA')
            l2rows[d['sub_partition']] = d
    require(set(mrows) == set(range(64)), 'M_ALL_64_CLUSTERS_REQUIRED')
    require(set(l2rows) == set(range(40)), 'L2_ALL_40_SUBPARTITIONS_REQUIRED')
    for d in mrows.values():
        require(d['parents_enqueued'] == d['parents_transferred'] == d['parents_closed'], 'M_PARENT_CONSERVATION')
        require(d['required_sectors'] == d['sectors_enqueued'] == d['sectors_received'], 'M_SECTOR_CONSERVATION')
        require(d['pending_parents'] == 0, 'M_TERMINAL_DRAIN')
        if mode != 'M_DATAREAD':
            require(all(d[k] == 0 for k in set(d) - {'mode','cluster'}), 'M_ACTIVE_IN_OTHER_MODE')
    for d in l2rows.values():
        require(d['eligible_seen'] == d['virtual_hit_served'] == d['returned'] and d['outstanding'] == 0,
                'L2_SERVICE_CONSERVATION_OR_DRAIN')
        if mode != 'L2_DATAREAD':
            require(all(d[k] == 0 for k in set(d) - {'sub_partition'}), 'L2_ACTIVE_IN_OTHER_MODE')
    l1 = {}
    for name in ['eligible_admitted','events_enqueued','events_delivered','events_pending']:
        vals = re.findall(r'^DTC_ORACLE_L1_' + name + r'\s*=\s*(\d+)\s*$', text, re.M)
        require(vals, 'MISSING_L1_COUNTER:' + name)
        l1[name] = int(vals[-1])
    require(l1['events_enqueued'] == l1['events_delivered'] and l1['events_pending'] == 0, 'L1_EVENT_DRAIN')
    if mode != 'L1_DATAREADY':
        require(all(v == 0 for v in l1.values()), 'L1_ACTIVE_IN_OTHER_MODE')
    exposure = {'OFF_MATCHED': 0, 'M_DATAREAD': sum(d['parents_enqueued'] for d in mrows.values()),
                'L2_DATAREAD': sum(d['virtual_hit_served'] for d in l2rows.values()),
                'L1_DATAREADY': l1['events_enqueued']}[mode]
    if require_exposure:
        require(mode != 'OFF_MATCHED' and exposure > 0, 'NO_EXPOSURE')
    return dict(mode=mode, exposure=exposure, M_units=64, L2_units=40, L1=l1,
                final_counter_placement_requires_source_review=True)

def local_safety_sample(native_path):
    """No registry, peer, SSH, FUSE, recursive tree or subprocess calls."""
    mem = {k: int(v.split()[0]) * 1024 for k, v in (line.split(':', 1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines())}
    cg = pathlib.Path('/sys/fs/cgroup')
    def val(name):
        s = (cg / name).read_text().strip()
        return None if s == 'max' else int(s)
    fs = os.statvfs(native_path)
    maximum, current = val('memory.max'), val('memory.current')
    return dict(monotonic_ns=time.monotonic_ns(), host_mem_available_bytes=mem['MemAvailable'],
                cgroup_memory_max_bytes=maximum, cgroup_memory_current_bytes=current,
                cgroup_headroom_bytes=None if maximum is None else max(0, maximum-current),
                native_free_bytes=fs.f_bavail * fs.f_frsize, native_free_inodes=fs.f_favail,
                memory_psi=pathlib.Path('/proc/pressure/memory').read_text(),
                io_psi=pathlib.Path('/proc/pressure/io').read_text(),
                memory_events=(cg / 'memory.events').read_text(),
                swap_free_bytes=mem['SwapFree'], cgroup_swap_current_bytes=val('memory.swap.current'))

def admit_resource(sample, predicted_rss, queued_reserved_rss=0, write_reservation=0,
                   restore_reservation=0, peer_reservation=0, fraction=.88):
    require(.85 <= fraction <= .90 and predicted_rss > 0, 'RESOURCE_ESTIMATE')
    available = min(sample['host_mem_available_bytes'], sample['cgroup_headroom_bytes']
                    if sample['cgroup_headroom_bytes'] is not None else sample['host_mem_available_bytes'])
    reasons = []
    if predicted_rss + queued_reserved_rss > fraction * max(0, available-8*G):
        reasons.append('DYNAMIC_MEMORY_ADMISSION_HOLD')
    some = re.search(r'some avg10=([\d.]+)', sample['memory_psi'])
    full = re.search(r'full avg10=([\d.]+)', sample['memory_psi'])
    if not some or not full or float(some.group(1)) > 2 or float(full.group(1)) > .5:
        reasons.append('MEMORY_PRESSURE_ADMISSION_HOLD')
    required = 5*G + 256*1024**2 + write_reservation + restore_reservation + peer_reservation
    if sample['native_free_bytes'] < required:
        reasons.append('NATIVE_ACTUAL_RESERVATION_HOLD')
    if sample['native_free_inodes'] < 100000:
        reasons.append('NATIVE_INODES_HOLD')
    return dict(admit=not reasons, reasons=reasons, memory_fraction=fraction,
                available_bytes=available, required_native_bytes=required,
                healthy_models_terminated=False, missing_peer_or_archive_checks_still_required=True)
