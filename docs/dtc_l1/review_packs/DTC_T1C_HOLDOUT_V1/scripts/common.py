"""Shared evidence helpers for the seven-point, default-off pilot wrapper."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
from datetime import datetime, timezone

PACK = Path(__file__).resolve().parents[1]
FW = PACK.parents[3]
MAIN = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-service-closure-174-v1')
CORE = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
ROOT = Path('/workspace/dtc-t1c-holdout-174-v1')
CORE_SHA = '6fba0136f8465b59fe5858a950fa39efb265f654'
BUILD_FW = '18a68dcccd795f1b6cda75504e9450d00c9cee02'
AUTH_HEAD = 'f520a445436b57c0a0f2494fb858a1636f04d2bc'
A_HEAD = 'f5c37d6edcce832a72cb0830021bffa78df6cc13'
BINARY_SHA = 'fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b'
RUNTIME = Path('/workspace/dtc-service-closure-174-v1/build-r1-a1/accel-sim.out')
M_BRANCH = 'hrl/iscas2027-dtc-mechanism-consumer-174-v1'
M_PATH = 'docs/dtc_l1/review_packs/DTC_MECHANISM_CPU_CONSUMER_V1'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, data):
    if Path(path).exists():
        assert json.loads(Path(path).read_text()) == data, 'Immutable evidence conflict: '+str(path)
        return
    with Path(path).open('x') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def table(path, rows):
    assert rows
    with Path(path).open('x') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode().strip()


def options(paths):
    result = {}
    for path in paths:
        key = None
        for token in shlex.split(Path(path).read_text(), comments=True):
            if re.match(r'^-[A-Za-z_]', token):
                key = token
                result[key] = []
            else:
                assert key is not None
                # Compare printed option values with equivalent whitespace,
                # including the frozen quoted multiline DRAM timing string.
                result[key].extend(token.split())
    return result


def echo_options(text):
    # Frozen option_parser print format: one option/value and trailing # comment.
    result = {}
    for line in text.splitlines():
        if re.match(r'^-[A-Za-z_]', line):
            parts = line.split('#', 1)[0].split(None, 1)
            if len(parts) == 2:
                result[parts[0]] = parts[1].strip().split()
    return result


def old_collector():
    path = PACK/'inputs/collect_service_closure_attempts.py'
    spec = importlib.util.spec_from_file_location('frozen_collect', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def proc(pid):
    try:
        p = Path('/proc')/str(pid)
        stat = p.joinpath('stat').read_text()
        rest = stat[stat.rfind(')')+2:].split()
        return dict(pid=int(pid), state=rest[0], start_ticks=int(rest[19]),
                    argv=[s.decode(errors='replace') for s in p.joinpath('cmdline').read_bytes().split(b'\0') if s],
                    rss_kib=int(rest[21])*os.sysconf('SC_PAGE_SIZE')//1024)
    except (FileNotFoundError, ProcessLookupError):
        return None


def resource_snapshot():
    cg = Path('/sys/fs/cgroup')
    read = lambda name: cg.joinpath(name).read_text().strip()
    mem = {k: int(v.split()[0])*1024 for k,v in
           (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
    pressure = {}
    for kind in ('memory', 'io'):
        pressure[kind] = {line.split()[0]: dict(x.split('=') for x in line.split()[1:])
                          for line in Path('/proc/pressure',kind).read_text().splitlines()}
    locks_text = Path('/proc/locks').read_text().splitlines()
    old_locks = []
    for path in sorted((MAIN.parent.parent/'dtc-service-closure-174-v1/r2-attempts').glob('*.lock')):
        # MAIN.parent.parent is /workspace; read only, never acquire these locks.
        inode = path.stat().st_ino
        owners = [line for line in locks_text if line.split()[5].split(':')[-1] == str(inode)]
        old_locks.append(dict(path=str(path), inode=inode, owners=owners))
    processes = []
    for path in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv = [a.decode(errors='replace') for a in path.read_bytes().split(b'\0') if a]
            if not argv:
                continue
            if argv[0].endswith('accel-sim.out') or any(Path(arg).name in
                    ['service_closure_dispatch.py','watch_service_closure_strict.py','run_pilot.py','run_pilot_v2.py','run_holdout.py'] for arg in argv):
                item = proc(path.parent.name)
                if item and item['state'] != 'Z':
                    processes.append(item)
        except (OSError, IndexError):
            pass
    usage = __import__('shutil').disk_usage(ROOT)
    vmstat = dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
    limit = read('memory.max')
    return dict(utc=now(), host=__import__('socket').gethostname(),
                mem_available=mem['MemAvailable'], cgroup_memory_current=int(read('memory.current')),
                cgroup_memory_max=int(limit) if limit!='max' else None,
                cgroup_swap_current=int(read('memory.swap.current')),
                cgroup_events=dict(line.split() for line in read('memory.events').splitlines()),
                pressure=pressure, pswpin=int(vmstat['pswpin']), pswpout=int(vmstat['pswpout']),
                disk_free=usage.free, old_locks=old_locks, processes=processes)


def source_check():
    assert git(CORE,'rev-parse','HEAD') == CORE_SHA
    assert git(MAIN,'rev-parse','HEAD') == A_HEAD
    assert sha(RUNTIME) == BINARY_SHA
    for prior,expected in [(Path('/workspace/worktrees/accel-sim-iscas2027-dtc-tag-pilot-174-v1'),AUTH_HEAD),(Path('/workspace/worktrees/accel-sim-iscas2027-dtc-mechanism-consumer-174-v1'),'d723784a8b897566b63113f95972f7a8d12a01ce')]:
        assert git(prior,'rev-parse','HEAD') == expected
        assert not git(prior,'status','--porcelain')
    for library in json.loads((PACK/'DYNAMIC_LIBRARY_IDENTITIES.json').read_text())['libraries']:
        assert sha(library['path']) == library['sha256']
    identity = json.loads((PACK/'SOURCE_IDENTITY.json').read_text())
    for item in identity['files']:
        assert sha(item['path']) == item['sha256'], item['path']
    return identity
