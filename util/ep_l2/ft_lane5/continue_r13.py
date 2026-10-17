"""One bounded Lane5 dependency observation, never a build/simulation/watch daemon."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time

from registry import ACTIVE, DEFAULT_ROOT, local_resources, process_identity, write_json

REPO = Path(__file__).resolve().parents[3]
LANE1 = 'hrl/ep-l2-ft20261016-lane1-v1'
TARGET = 'hrl/ops-174new-164-archive-exec-v1'
SOURCE = 'hrl/ops-174-source-audit-exec-v1'
SOURCE_ROOT = 'docs/ep_l2/operations/174new_to_164_archive_v1/source_receipts/20261016_storageops_02'
LANE1_ROOT = 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1'
TARGET_ROOT = 'docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261016_storageops_06'


def command(args):
    return subprocess.check_output(args, cwd=REPO, timeout=45, stderr=subprocess.PIPE)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_raw(commit, path):
    return command(['gh', 'api', '--header', 'Accept: application/vnd.github.raw+json',
                    '/repos/swayhrl/gpu-l2-cache-verilog/contents/' + path + '?ref=' + commit])


def live():
    with (DEFAULT_ROOT / 'REGISTRY.lock').open('r') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        registry = json.loads((DEFAULT_ROOT / 'RUN_REGISTRY.json').read_text())
        client = json.loads((DEFAULT_ROOT / 'CLIENT_CONTRACT.json').read_text())
    waiter = json.loads((DEFAULT_ROOT / 'LANE1_GATEWAITER_STATUS.json').read_text())
    pid = waiter.get('pid', {}).get('pid')
    try:
        actual = process_identity(pid) if pid else None
    except (FileNotFoundError, ProcessLookupError):
        actual = None
    fs = {}
    for path in ('/workspace', '/root/share'):
        s = os.statvfs(path)
        fs[path] = {'available_bytes': s.f_bavail * s.f_frsize,
                    'device': os.stat(path).st_dev, 'fsid': s.f_fsid}
    # A raw formal driver receipt can announce a build in progress; it does not
    # replace a published official release or the independent scientific gates.
    raw_producer = None
    if waiter.get('output'):
        path = Path(waiter['output']) / 'formal_build_attempt_r1/BUILD_AND_TEST_RECEIPT.json'
        if path.is_file():
            raw = path.read_bytes()
            raw_producer = {'path': str(path), 'sha256': sha(raw), 'report': json.loads(raw)}
    return {'host': socket.gethostname(), 'mount_namespace': os.readlink('/proc/self/ns/mnt'),
            'resources': local_resources(), 'filesystems': fs,
            'active_runs': {k: v for k, v in registry['runs'].items() if v['status'] in ACTIVE},
            'active_resource_leases': {k: v for k, v in registry['resource_leases'].items() if v['status'] in ACTIVE},
            'host_policy': registry['hosts'][registry['authority_host']],
            'waiter': waiter, 'waiter_actual_identity': actual,
            'waiter_identity_matches': actual is not None and all(actual[k] == waiter['pid'].get(k, waiter.get(k)) for k in ('pid', 'start_ticks', 'boot_id')),
            'current_scientific_authority': client['scientific_acceptance'],
            'raw_formal_producer': raw_producer}


def observe(contract, out):
    spec = json.loads(Path(contract).read_text())
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    with (out / 'OBSERVATION.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous = sorted(out.glob('EVENT_*.json'))
        now = time.time()
        if previous and now < json.loads(previous[-1].read_text())['checked_at_unix'] + 600:
            raise ValueError('Next dependency observation is not due; minimum600s, no busy polling')
        event = {'checked_at_unix': now, 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                 'deadline_utc': spec['deadline_utc'], 'additional_background_worker': False,
                 'authorization_or_lease_claim': False, 'errors': [], 'live': live()}
        if now >= spec['deadline_unix']:
            event['status'] = 'CONTINUE_WINDOW_EXPIRED_NO_NEW_DEPENDENCY_EXECUTION'
        else:
            event['status'] = 'OBSERVED_DEPENDENCIES_PENDING'
            try:
                command(['git', '-c', 'gc.auto=0', '-c', 'url.https://github.com/.insteadOf=git@github.com:',
                         '-c', 'credential.helper=!gh auth git-credential', 'fetch', '--no-tags', 'origin',
                         'refs/heads/' + LANE1 + ':refs/remotes/origin/' + LANE1,
                         'refs/heads/' + TARGET + ':refs/remotes/origin/' + TARGET])
                for label, ref, root in [('lane1', LANE1, LANE1_ROOT), ('target_ops', TARGET, TARGET_ROOT)]:
                    commit = command(['git', 'rev-parse', 'refs/remotes/origin/' + ref]).decode().strip()
                    directory = out / (label + '_' + commit); directory.mkdir(exist_ok=True)
                    event[label] = {'commit': commit, 'evidence_directory': str(directory), 'files': {}}
                    for name in ('STATUS.md', 'RECEIPT.json'):
                        path = directory / name
                        if not path.exists(): path.write_bytes(command(['git', 'show', commit + ':' + root + '/' + name]))
                        event[label]['files'][name] = sha(path.read_bytes())
                    if label == 'lane1':
                        receipt = json.loads((directory / 'RECEIPT.json').read_text())
                        event['official_release_candidate'] = {'binary_sha256': receipt.get('binary_sha256'),
                            'runtime_ready': receipt.get('runtime_ready'), 'status': receipt['status'],
                            'source': 'Published receipt candidate only; independently audit formal provenance,21 real tests and11 gates before launch'}
            except (subprocess.SubprocessError, OSError, ValueError) as error:
                event['errors'].append({'kind': 'FRAMEWORK_FETCH_OR_EVIDENCE_UNAVAILABLE', 'error': str(error)})
            try:
                head = json.loads(command(['gh', 'api', '/repos/swayhrl/gpu-l2-cache-verilog/git/ref/heads/' + SOURCE]))['object']['sha']
                directory = out / ('source_ops_' + head); directory.mkdir(exist_ok=True)
                listing = directory / 'DIRECTORY.json'
                if not listing.exists(): listing.write_bytes(command(['gh', 'api', '/repos/swayhrl/gpu-l2-cache-verilog/contents/' + SOURCE_ROOT + '?ref=' + head]))
                names = [item['name'] for item in json.loads(listing.read_text())]
                selected = [name for name in names if name == 'STATUS.md' or name == 'SOURCE_RELEASE_RECEIPT.json' or
                            (name.startswith('POLYBENCH') and any(term in name for term in ('R13', 'RELEASE')))]
                files = {}
                for name in selected:
                    path = directory / name
                    if not path.exists(): path.write_bytes(source_raw(head, SOURCE_ROOT + '/' + name))
                    files[name] = sha(path.read_bytes())
                event['source_ops'] = {'commit': head, 'evidence_directory': str(directory), 'files': files,
                                       'literal_SOURCE_RELEASE_RECEIPT_present': 'SOURCE_RELEASE_RECEIPT.json' in names,
                                       'interpretation': 'Archive/copy bytes never count as root df reclaim; inspect exact per-stage release receipt and independently measured live space'}
            except (subprocess.SubprocessError, OSError, ValueError, KeyError) as error:
                event['errors'].append({'kind': 'SOURCE_FETCH_OR_EVIDENCE_UNAVAILABLE', 'error': str(error)})
        path = out / f'EVENT_{len(previous):03d}.json'
        if path.exists(): raise ValueError('Never overwrite event evidence')
        write_json(path, event)
        print(json.dumps({'event': str(path), 'status': event['status'], 'errors': event['errors'],
                          'official_release_candidate': event.get('official_release_candidate'),
                          'next_check_not_before_unix': now + 600}, indent=2))
        return event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    observe(args.contract, args.out)


if __name__ == '__main__':
    main()
