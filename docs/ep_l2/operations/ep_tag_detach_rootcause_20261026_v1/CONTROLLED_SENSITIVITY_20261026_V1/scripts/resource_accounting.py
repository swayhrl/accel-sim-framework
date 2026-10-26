"""Read-only local admission snapshot; never locks or mutates shared authority.

Disk counts remaining result growth plus one future native restore, not the DTC
pool ceiling. Existing file bytes are already represented in statvfs. RAM uses
the current DTC V4 working-set reservation, preserving legacy hard-cap entries.
A PASS is a sampled prerequisite, not registration, budget, or a held lease.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os

G = 1024 ** 3
M = 1024 ** 2
N = Path('/root/data/ep_l2_dtc_l1_native_v2')
T = Path('/root/data/dtc_main_v100_sweep_20261025_v1')
F = Path('/root/data/dtc_failure_repair_20261025_v1')
REGISTRY = N / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH = N / 'control/CURRENT_SCIENCE_EPOCH.json'
CLAIMS = T / 'control/POOL_DISPATCH_RESERVATIONS.json'
V4 = T / 'control/HOST_EXECUTION_PLAN_V4.json'
ORIGINAL = 'DTC_AE_V100_FULL_SWEEP_20261025_V1'
TERMINAL = {'COMPLETE', 'CLOSED', 'CANCELLED', 'STOPPED', 'SEALED'}


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read(path, guards):
    path = Path(path)
    raw = path.read_bytes()
    guards[str(path)] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def _size(root):
    """Bounded metadata-only walk, with no symlink traversal or remote mount."""
    root = Path(root)
    if not root.exists():
        return 0
    if root.is_symlink() or root.stat().st_dev != T.stat().st_dev:
        raise ValueError('result root must be local and not a symlink: ' + str(root))
    total = 0
    count = 0
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in list(dirs):
            p = Path(parent) / name
            if p.is_symlink() or p.stat().st_dev != root.stat().st_dev:
                raise ValueError('unexpected result directory alias: ' + str(p))
        for name in files:
            p = Path(parent) / name
            count += 1
            if count > 32768:
                raise ValueError('bounded result metadata walk exceeded 32768 files')
            try:
                if not p.is_symlink():
                    total += p.stat().st_size
            except FileNotFoundError:
                pass  # concurrent archive/removal; no negative reservation credit
    return total


def _rss(out, guards):
    p = Path(out) / 'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    if not p.exists():
        return 0, False
    b = _read(p, guards)
    proc = Path('/proc') / str(b['pid'])
    try:
        stat = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
        if int(stat[19]) != b['start_ticks'] or stat[0] in {'Z', 'X'}:
            return 0, False
        rss = int(next(x.split()[1] for x in (proc / 'status').read_text().splitlines()
                       if x.startswith('VmRSS:'))) * 1024
        return rss, True
    except (FileNotFoundError, ProcessLookupError, StopIteration):
        return 0, False


def _repair_ram(requests, guards):
    """Actual repair hard caps minus RSS; no invented working-set qualification."""
    roots = {
        'DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1': F / 'validation',
        'DTC_AE_LAVAMEM_REPAIR_20261026_V2': F / 'validation_lava_memory_v2',
        'DTC_AE_LATE_FAILURE_REPAIR_20261026_V1': F / 'validation_late_failure_v1',
    }
    entries = []
    for request, proot in roots.items():
        peer = requests.get(request)
        if peer is None:
            continue
        consumed = peer['consumed']
        claims = _read(proot / 'control/POOL_DISPATCH_RESERVATIONS.json', guards)['claims']
        if not isinstance(consumed, dict) or not isinstance(claims, dict):
            raise ValueError('unknown repair consumed/claim schema: ' + request)
        # Retained historical claims for completed rows create no future RAM.
        targets = {c for c, row in consumed.items() if not row.get('execution_receipt')}
        targets.update(set(claims) - set(consumed))
        for case in sorted(targets):
            if peer.get('state') in TERMINAL:
                raise ValueError('closed repair has unresolved active/pending claim: ' + case)
            sp = proot / 'control/specs' / (case + '.json')
            spec = _read(sp, guards)
            expected = peer['admitted_specs'][case]
            if guards[str(sp)] != expected:
                raise ValueError('repair admitted spec drift: ' + case)
            hard = spec['limits']['max_process_tree_rss_bytes']
            if type(hard) is not int or hard <= 0:
                raise ValueError('unknown repair hard RAM cap: ' + case)
            if case in claims and claims[case].get('RAM_cap_bytes') != hard:
                raise ValueError('repair claim/spec RAM hard-cap mismatch: ' + case)
            row = consumed.get(case)
            rss, live = _rss(proot / 'DTC/run/results' / row['uuid'], guards) if row else (0, False)
            additional = max(0, hard-rss)
            entries.append({'request': request, 'case': case,
                            'claimed_before_INTENT': row is None,
                            'observed_model_RSS_bytes': rss, 'model_live': live,
                            'RAM_hard_cap_bytes': hard,
                            'registered_estimate_bytes_information_only': peer.get('estimated_peak_model_RAM_bytes'),
                            'RAM_additional_bytes': additional,
                            'RAM_basis': 'unqualified working-set: reserve exact hard-cap remainder'})
    return sum(e['RAM_additional_bytes'] for e in entries), entries


def snapshot(job_root, own_case, own_reservation_bytes, memory_cap_bytes, runtime=False):
    """Return a JSON-compatible admission sample without acquiring any lock.

    own_reservation_bytes is the entire additional EP write/restore/staging/
    engineering envelope. Caller must not separately add existing bytes in df.
    Any torn authority/claims/pin snapshot returns decision RESAMPLE, never
    an abort recommendation. runtime=True checks only actual disk/RAM headroom;
    peer future claims are re-admitted by their owner, not by this runtime guard.
    """
    own_reservation_bytes = int(own_reservation_bytes)
    memory_cap_bytes = int(memory_cap_bytes)
    if own_reservation_bytes < 0 or memory_cap_bytes < 0:
        raise ValueError('reservations must be nonnegative')
    root = Path(job_root)
    anchor = root if root.exists() else root.parent
    if not anchor.exists():
        anchor = Path('/root/data')
    guards = {}
    errors = []
    vbefore = os.statvfs(anchor)
    result = {'schema': 'EP_MEMORY_PATH_READONLY_RESOURCE_SNAPSHOT_V1',
              'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'job_root': str(root), 'own_case': str(own_case),
              'locks_acquired': 0, 'authority_writes': 0, 'runtime': bool(runtime),
              'own_reservation_bytes': own_reservation_bytes,
              'memory_cap_bytes': memory_cap_bytes}
    entries = []
    peers = []
    dtc_disk = G  # existing producer's bounded controller/archive metadata envelope
    dtc_ram = 0
    repair_ram = 0
    repair_entries = []
    try:
        reg = _read(REGISTRY, guards)
        epoch = _read(EPOCH, guards)
        claims = _read(CLAIMS, guards)['claims']
        profile = _read(V4, guards)
        legacy = set(profile['legacy_V1_cells'])
        if profile.get('profile_id') != 'HOST_ACTUAL4G40_V4':
            errors.append('unknown DTC host working-set reservation profile')
        adapter = T / 'tools/sweep_host_execution_v4.py'
        guards[str(adapter)] = _digest(adapter)
        if guards[str(adapter)] != profile.get('adapter_sha256'):
            errors.append('DTC V4 adapter SHA drift')
        if epoch['native_registry_sha256'] != guards[str(REGISTRY)]:
            errors.append('registry SHA does not match current epoch')
        if (epoch.get('epoch') != 2 or epoch.get('state') != 'NATIVE_SCIENCE_ACTIVE'
                or epoch.get('holder') != os.uname().nodename):
            errors.append('current epoch is not active epoch2')
        q = reg['registered_future_requests'][ORIGINAL]
        consumed = {} if runtime else q['consumed']
        if runtime:
            claims = {}  # runtime does not re-admit future peer work
        for case, row in consumed.items():
            # Archived/native-restored bytes are already in df; no future write.
            if (T / 'control' / (case + '_ARCHIVE_RECEIPT.json')).exists():
                continue
            out = T / 'DTC/run/results' / row['uuid']
            used = _size(out)
            done = bool(row.get('execution_receipt'))
            entry = {'case': case, 'uuid': row['uuid'], 'existing_result_bytes': used,
                     'execution_receipt_present': done, 'output': str(out)}
            if done:
                reserve = used + 16*M  # remaining one restore, not a second result
                entry['RAM_additional_bytes'] = 0
            else:
                sp = T / 'control' / (case + '_SPEC.json')
                spec = _read(sp, guards)
                expected = q.get('admitted_specs', {}).get(case)
                if expected and guards[str(sp)] != expected:
                    errors.append('DTC admitted spec drift: ' + case)
                cap = int(spec['limits']['max_result_directory_bytes'])
                op = T / 'control' / ('OPERATIONAL_OUTPUT_CAP_' + case + '.json')
                if op.exists():
                    cap = min(cap, int(_read(op, guards)['effective_result_cap_bytes']))
                reserve = max(0, cap-used) + cap
                rss, live = _rss(out, guards)
                hard = int(spec['limits']['max_process_tree_rss_bytes'])
                envelope = hard if case in legacy else min(hard, max(4*G, rss))
                additional = max(0, envelope-rss)
                dtc_ram += additional
                entry.update(result_cap_bytes=cap, observed_model_RSS_bytes=rss,
                             model_live=live, RAM_hard_cap_bytes=hard,
                             RAM_working_set_envelope_bytes=envelope,
                             RAM_additional_bytes=additional,
                             legacy_hard_cap_reservation=case in legacy)
            dtc_disk += reserve
            entry['remaining_write_and_restore_bytes'] = reserve
            entries.append(entry)
        for case, claim in claims.items():
            if case in consumed:
                continue
            cap = int(claim['result_cap_bytes'])
            hard = int(claim['RAM_cap_bytes'])
            additional = min(hard, 4*G)
            dtc_disk += 2*cap
            dtc_ram += additional
            entries.append({'case': case, 'claimed_before_INTENT': True,
                            'result_cap_bytes': cap,
                            'remaining_write_and_restore_bytes': 2*cap,
                            'RAM_additional_bytes': additional})
        for key, peer in ([] if runtime else reg['registered_future_requests'].items()):
            if key == ORIGINAL or not isinstance(peer, dict):
                continue
            if (peer.get('state') in TERMINAL or
                    peer.get('reserved_write_bytes') == 0):
                continue
            if key == str(own_case) or peer.get('job_root') == str(root):
                continue
            extra = peer.get('reserved_write_bytes')
            if type(extra) is not int or extra < 0:
                errors.append('unknown active peer write reservation: ' + key)
                continue
            # LAVA repair remains conservatively charged at its registered1.5GiB.
            peers.append({'request': key, 'state': peer.get('state'),
                          'remaining_write_bytes_conservative': extra})
        if not runtime:
            repair_ram, repair_entries = _repair_ram(reg['registered_future_requests'], guards)
        result['DTC_pool_ceiling_bytes_information_only'] = q['reserved_write_bytes']
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(type(error).__name__ + ': ' + str(error))
    mem = int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines()
                   if x.startswith('MemAvailable:'))) * 1024
    cur = int(Path('/sys/fs/cgroup/memory.current').read_text())
    maximum = Path('/sys/fs/cgroup/memory.max').read_text().strip()
    ms = dict((a, int(b)) for a, b in (x.split() for x in
              Path('/sys/fs/cgroup/memory.stat').read_text().splitlines()))
    clean = max(0, ms.get('file',0)-ms.get('shmem',0)-ms.get('file_mapped',0)
                -ms.get('file_dirty',0)-ms.get('file_writeback',0))
    credit = max(0, min(ms.get('inactive_file',0),clean)-8*G)
    effective = None if maximum == 'max' else int(maximum)-cur+credit
    after = {}
    for path in guards:
        try:
            after[path] = _digest(path)
        except OSError:
            after[path] = None
    consistent = guards == after and not errors
    va = os.statvfs(anchor)
    free = min(vbefore.f_bavail*vbefore.f_frsize, va.f_bavail*va.f_frsize)
    peer_write = sum(x['remaining_write_bytes_conservative'] for x in peers)
    required = 8*G + own_reservation_bytes + (0 if runtime else dtc_disk + peer_write)
    ram_extra = 0 if runtime else dtc_ram + repair_ram + memory_cap_bytes
    disk_pass = consistent and free > required and va.f_favail >= 100000
    ram_pass = (consistent and mem >= 64*G+ram_extra and
                (effective is None or effective >= 48*G+ram_extra))
    result.update(consistent_snapshot=consistent, guard_SHA256_before=guards,
                  guard_SHA256_after=after, errors=errors, free_bytes=free,
                  required_bytes=required, local_floor_bytes=7*G,
                  unknown_incremental_margin_bytes=G,
                  DTC_metadata_envelope_bytes=G,
                  DTC_remaining_write_and_restore_bytes=dtc_disk,
                  DTC_additional_RAM_bytes=dtc_ram, DTC_entries=entries,
                  repair_additional_RAM_bytes=repair_ram, repair_RAM_entries=repair_entries,
                  known_peer_breakdown=peers, peer_incremental_write_bytes=peer_write,
                  host_MemAvailable_bytes=mem, cgroup_memory_current_bytes=cur,
                  cgroup_memory_max=maximum, clean_inactive_file_credit_bytes=credit,
                  cgroup_effective_headroom_bytes=effective,
                  required_host_available_RAM_bytes=64*G+ram_extra,
                  required_cgroup_effective_headroom_bytes=48*G+ram_extra,
                  RAM_pass=ram_pass, disk_pass=disk_pass,
                  admission_pass=(None if runtime else ram_pass and disk_pass),
                  runtime_pass=(ram_pass and disk_pass if runtime and consistent else None),
                  resample_required=not consistent,
                  abort_recommended=bool(runtime and consistent and not (ram_pass and disk_pass)),
                  decision=('RESAMPLE' if not consistent else 'PASS' if ram_pass and disk_pass else 'HOLD'),
                  RAM_basis=('runtime actual headroom; own RSS/cap checked separately by caller' if runtime else 'admission projected own+active/claimed peer RAM'),
                  reservation_held=False,
                  storage_basis='existing bytes already in df; current active/claimed growth plus one native restore; DTC35GiB is only a ceiling')
    return result