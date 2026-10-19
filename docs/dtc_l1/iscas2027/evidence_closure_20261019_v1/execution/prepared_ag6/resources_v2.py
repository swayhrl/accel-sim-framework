"""Source preparation only: original R2 plus explicit V2 domain/disk checks.

No fork, signal, lock or retry. The caller supplies the untouched all-project
snapshot from the same current-authority callback. Old R2 runtime persistence
intervals stay intact; V2 adds both PSI domains, host OOM and the 10 GiB floor.
"""
import hashlib
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
FROZEN = HERE / 'frozen_ag4_resource_policy.py.txt'
FROZEN_SHA256 = 'a023f3d3d716088d5f2f596de60b15ac64332b1dc1a3e7a9875bbca53f077bb0'
GIB = 1024 ** 3


def require(value, message):
    if not value:
        raise ValueError(message)


def _policy():
    data = FROZEN.read_bytes()
    require(hashlib.sha256(data).hexdigest() == FROZEN_SHA256,
            'FROZEN_R2_SOURCE_CHANGED')
    scope = {'__builtins__': __builtins__}
    exec(compile(data, str(FROZEN), 'exec'), scope)
    return scope


def parsed_pressure(raw):
    return {line.split()[0]: dict(x.split('=') for x in line.split()[1:])
            for line in raw.splitlines()}


def enrich(snapshot, output):
    """Keep all visible projects; add only otherwise absent resource fields."""
    import os
    import shutil
    result = dict(snapshot)
    result['host_oom_kill'] = next(int(line.split()[1])
        for line in Path('/proc/vmstat').read_text().splitlines()
        if line.startswith('oom_kill '))
    result['output_filesystem_device'] = os.stat(output).st_dev
    result['disk_free_bytes'] = shutil.disk_usage(output).free
    result['cgroup_pressure_parsed'] = {kind: parsed_pressure(
        snapshot['cgroup'][kind + '.pressure']) for kind in ('memory', 'io')}
    return result


def checks(sample):
    old = _policy()
    values = {
        'original174': sample['host'] == 'huangrulin-174' and sample['uid'] == 0,
        'host_memory_headroom_ge32GiB': sample['host_MemAvailable_bytes'] >= 32 * GIB,
        'cgroup_memory_headroom_ge32GiB': old['headroom'](sample) >= 32 * GIB,
        'actual_output_filesystem_ge10GiB': sample['disk_free_bytes'] >= 10 * GIB,
    }
    for domain, pressure in [('host', sample['pressure']),
                             ('cgroup', sample['cgroup_pressure_parsed'])]:
        for kind, limit in [('memory', 1), ('io', 25)]:
            values[domain + '_' + kind + '_full_avg10'] = (
                float(pressure[kind]['full']['avg10']) <= limit)
    return values


def paired(first, second):
    values = {'first_' + k: v for k, v in checks(first).items()}
    values.update({'second_' + k: v for k, v in checks(second).items()})
    values['gap_ge10s'] = second['monotonic_ns'] - first['monotonic_ns'] >= 10 * 10**9
    values['same_output_filesystem'] = (first['output_filesystem_device'] ==
                                        second['output_filesystem_device'])
    values['no_new_host_OOM'] = first['host_oom_kill'] == second['host_oom_kill']
    values['no_new_cgroup_OOM'] = all(first['cgroup']['events'][key] ==
        second['cgroup']['events'][key] for key in ('oom', 'oom_kill'))
    return values


class Runtime:
    def __init__(self, baseline, output):
        policy = _policy()['RuntimePolicy']
        self.output = Path(output)
        self.first = baseline
        self.host = policy(baseline)
        self.cgroup = policy(self._project(baseline))

    @staticmethod
    def _project(sample):
        return dict(sample, pressure=sample['cgroup_pressure_parsed'])

    def quick_stop(self):
        """Call only while an own guard is active; returns a reason, never signals."""
        import shutil
        if shutil.disk_usage(self.output).free < 10 * GIB:
            return 'V2_ACTUAL_OUTPUT_FILESYSTEM_BELOW_10GiB'
        events = dict(line.split() for line in
                      Path('/sys/fs/cgroup/memory.events').read_text().splitlines())
        if any(int(events[k]) != self.first['cgroup']['events'][k]
               for k in ('oom', 'oom_kill')):
            return 'NEW_CGROUP_OOM_OR_OOM_KILL'
        host_oom = next(int(line.split()[1]) for line in
            Path('/proc/vmstat').read_text().splitlines() if line.startswith('oom_kill '))
        if host_oom != self.first['host_oom_kill']:
            return 'NEW_HOST_OOM_KILL'
        return None

    def observe(self, sample, own_faults, previous_faults):
        host = self.host.observe(sample, own_faults, previous_faults)
        cgroup = self.cgroup.observe(self._project(sample), own_faults, previous_faults)
        reasons = [domain + ':' + reason for domain, decision in
            [('host', host), ('cgroup', cgroup)] for reason in decision['stop_reasons']]
        if sample['disk_free_bytes'] < 10 * GIB:
            reasons.append('V2_ACTUAL_OUTPUT_FILESYSTEM_BELOW_10GiB')
        if sample['output_filesystem_device'] != self.first['output_filesystem_device']:
            reasons.append('V2_OUTPUT_FILESYSTEM_CHANGED')
        if sample['host_oom_kill'] != self.first['host_oom_kill']:
            reasons.append('NEW_HOST_OOM_KILL')
        return dict(decision='STOP' if reasons else 'WARN' if
                    any(x['decision'] == 'WARN' for x in [host, cgroup]) else 'CONTINUE',
                    stop_reasons=reasons, domains={'host': host, 'cgroup': cgroup},
                    next_full_sample_seconds=min(host['next_full_sample_seconds'],
                                                 cgroup['next_full_sample_seconds']))
