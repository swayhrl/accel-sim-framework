"""Bounded queue mode of campaign_r0; all admission and acceptance use existing tools."""
import json
import fcntl
import os
from pathlib import Path
import socket
import signal
import subprocess
import sys
import time

from acceptance import authorize_launch, current_manifest, load_current_authority
from registry import ACTIVE, PARALLEL, Registry, admit_result_output, attempt_count, local_resources, process_identity, run_key, write_json
from run import digest

REPO = Path(__file__).resolve().parents[3]
H = REPO / 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'
TOOLS = REPO / 'util/ep_l2/ft_lane5'
OUT = Path('/workspace/ep_l2_potential20261017_lane5_results')
PACKS = REPO / 'docs/ep_l2/review_packs'
HANDOFF_FILES = [H / n for n in ['APPLICATION_ACCEPTANCE.json', 'PARALLEL_CONTINUE_RECEIPT.json',
                               'PARALLEL_CAMPAIGN_LEDGER.json', 'RECEIPT.json', 'STATUS.md']]


def read_registry(registry):
    # Registry.snapshot historically rewrites updated_at; this polling read does not.
    with (registry.root / 'REGISTRY.lock').open('r') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        return json.loads((registry.root / 'RUN_REGISTRY.json').read_text())


def validate_budget(queue, campaign):
    if queue['experiment_id'] != PARALLEL or queue['deadline_unix'] != campaign['deadline_unix'] or queue['maximum_starts'] != campaign['maximum_starts'] or queue['t0_unix'] != campaign['t0_unix']:
        raise ValueError('Queue cannot alter frozen campaign budget/deadline')


def disposition(spec, registry, accepted):
    """Existing keys are observed, never reset, retried, or launched again."""
    key = run_key(spec['identity'])
    row = registry['runs'].get(key)
    if row and row['identity'] != spec['identity']:
        raise ValueError('Canonical identity mismatch')
    if key in accepted:
        if not row or row['status'] != 'COMPLETE_VALID':
            raise ValueError('Accepted key lacks valid canonical terminal')
        return 'ACCEPTED'
    return row['status'] if row else 'UNSTARTED'


def command(args, log):
    with log.open('xb') as stream:
        result = subprocess.run(args, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError('Existing tool failed; preserve evidence: ' + str(log))


def python(tool, *args):
    return [sys.executable, '-B', str(TOOLS / tool), *map(str, args)]


def publish(unit, specs, tag, deadline, controller):
    single = unit['kind'] == 'single'
    spec = specs[0]
    workload = spec['identity']['workload']
    regime = spec['regime']
    stem = ('FT20261017_LANE5_PARALLEL_' + regime + '_' + workload.upper()
            + ('_' + spec['producer_profile'] if single else ''))
    point = PACKS / (stem + ('_POINT_r1' if single else '_PAIR_r1'))
    acceptance = PACKS / (stem + '_ACCEPTANCE_r1')
    previous = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    if single:
        review = python('review_local_endpoint.py', '--spec', unit['specs'][0]['path'], '--pack', point)
    else:
        review = python('review_r0_1_pair.py', '--workload', workload, '--regime', regime,
                        '--spec-b', unit['specs'][0]['path'], '--spec-u', unit['specs'][1]['path'],
                        '--stage', OUT / 'reviewed_pairs', '--pack', point, '--deadline-unix', deadline)
    command(review, OUT / (tag + '_review.log'))
    command(python('publish_r0_1_acceptance.py', '--pair-pack', point, '--acceptance-pack', acceptance),
            OUT / (tag + '_stage.log'))
    main_receipt=json.loads((H/'RECEIPT.json').read_text())
    main_receipt['foreground_campaign_controller']=controller
    write_json(H/'RECEIPT.json',main_receipt)
    # Never commit an unrelated edit made while this foreground campaign runs.
    allowed = {str(p.relative_to(REPO)) for p in HANDOFF_FILES}
    changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=REPO, text=True).splitlines()
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=REPO, text=True).splitlines()
    if staged or any(p not in allowed for p in changed):
        raise ValueError('Unrelated worktree/index changes; no automatic commit')
    subprocess.run(['git', 'add', *map(str, HANDOFF_FILES)], cwd=REPO, check=True)
    subprocess.run(['git', 'add', '-f', str(point), str(acceptance)], cwd=REPO, check=True)
    subprocess.run(['git', 'diff', '--cached', '--check', '--', '*.py', '*.json', '*.md', '*SHA256SUMS'], cwd=REPO, check=True)
    command(['git', '-c', 'gc.auto=0', 'commit', '-m', 'Lane5 independently accept ' + unit['id']], OUT / (tag + '_commit.log'))
    env = os.environ.copy()
    env['GIT_SSH_COMMAND'] = 'ssh -p 443 -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes'
    with (OUT / (tag + '_push.log')).open('xb') as log:
        subprocess.run(['git', '-c', 'gc.auto=0', '-c', 'pack.threads=1', 'push',
                        'git@ssh.github.com:swayhrl/accel-sim-framework.git',
                        'HEAD:refs/heads/hrl/ep-l2-ft20261016-lane5-v1'], cwd=REPO, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    verify = python('verify_r0_1_delivery.py', '--since-publication', previous, '--workload', workload)
    verify += ['--single-pack', str(point), '--single-acceptance-pack', str(acceptance)] if single else ['--regime', regime]
    command(verify, OUT / (tag + '_remote_readback.log'))
    command(python('parallel_checkpoint.py', '--out', OUT / (tag + '_checkpoint.json')),
            OUT / (tag + '_checkpoint.log'))
    print(json.dumps({'event': 'CURRENT_ACCEPTED_REMOTE_VERIFIED', 'unit': unit['id'],
                      'point': str(point), 'sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()}), flush=True)


def main(queue_path):
    def stop_driver(signum, frame):
        raise KeyboardInterrupt('Campaign controller stopped; existing simulator runners remain untouched')
    signal.signal(signal.SIGTERM, stop_driver)
    queue_path = Path(queue_path).resolve()
    queue_sha = digest(queue_path)
    queue = json.loads(queue_path.read_text())
    registry = Registry()
    snapshot = read_registry(registry)
    campaign = snapshot['campaigns'][PARALLEL]
    validate_budget(queue, campaign)
    prepared = []
    for unit in queue['units']:
        if unit['kind'] not in ('single', 'pair'):
            raise ValueError('Unsupported unit kind')
        specs = []
        for item in unit['specs']:
            path = Path(item['path']).resolve()
            if not path.is_relative_to(H) or digest(path) != item['sha256']:
                raise ValueError('Prepared spec changed/outside original worktree')
            spec = json.loads(path.read_text())
            if spec['experiment_id'] != PARALLEL or spec.get('retry_checkpoint'):
                raise ValueError('No other campaign or implicit retry')
            specs.append(spec)
        if len(specs) != (1 if unit['kind'] == 'single' else 2):
            raise ValueError('Invalid explicit endpoint/pair unit')
        prepared.append((unit, specs))
    receipt = OUT / (queue['revision'] + '_PROGRESS.json')
    start = OUT / (queue['revision'] + '_START.json')
    with start.open('x') as f:
        json.dump({'process': process_identity(os.getpid()), 'queue': str(queue_path),
                   'queue_sha256': queue_sha, 'deadline_unix': campaign['deadline_unix'],
                   'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
                   'scope': 'One foreground campaign runner; adopts existing keys, no lease while waiting'}, f, indent=2)
    controller=json.loads(start.read_text())
    children = {}
    denied = set()
    fingerprint = None
    status = 'RUNNING'
    error = None
    try:
        while True:
            if digest(queue_path) != queue_sha:
                raise ValueError('Queue changed while running; current simulations remain untouched')
            snapshot = read_registry(registry)
            expected_policy = {'max_simulators':4,'max_cpu_units':8,'max_reserved_memory_bytes':32*2**30,
                               'max_result_bytes':12*2**30,'min_disk_free_bytes':48*2**30,
                               'min_available_memory_bytes':64*2**30,'default_run_output_limit_bytes':2*2**30}
            if any(snapshot['hosts'][socket.gethostname()][k] != v for k,v in expected_policy.items()):
                raise ValueError('Central policy changed outside frozen authorization')
            state = load_current_authority()
            manifest = current_manifest(state)
            accepted = {r['run_key'] for r in manifest['rows'] if r['scientific_acceptance'] == 'CURRENT_ACCEPTED'}
            for key, (child, log) in list(children.items()):
                if child.poll() is not None:
                    log.close()
                    del children[key]
                    snapshot = read_registry(registry)
                    if child.returncode and key not in snapshot['runs']:
                        denied.add(key)  # A raced preclaim refusal consumes no start; no busy retry.
                    elif snapshot['runs'][key]['status'] != 'COMPLETE_VALID':
                        raise RuntimeError('Preserved non-valid terminal requires scoped engineering/science review: ' + key)
            current = (tuple(sorted((k, v['status']) for k, v in snapshot['runs'].items())),
                       tuple(sorted((k, v['status']) for k, v in snapshot['resource_leases'].items())))
            if current != fingerprint:
                denied.clear()
                fingerprint = current
            active = [v for v in snapshot['runs'].values() if v['status'] in ACTIVE]
            starts = sum(attempt_count(v) for v in snapshot['runs'].values() if v.get('experiment_id') == PARALLEL)
            write_json(receipt, {'status': status, 'at_unix': time.time(), 'runner': process_identity(os.getpid()),
                                'queue_sha256': queue_sha, 'starts': starts, 'maximum_starts': campaign['maximum_starts'],
                                'deadline_unix': campaign['deadline_unix'], 'current_V2': state['binding'],
                                'active_runs': active, 'child_runner_pids': [p.pid for p, _ in children.values()],
                                'denied_without_start': sorted(denied)})
            if time.time() >= campaign['deadline_unix']:
                status = 'DEADLINE_NO_NEW_ACTION_EXISTING_RUNNERS_LEFT_NATURAL'
                break
            # Independently accept each completed point or complete pair before further launches.
            published = False
            for unit, specs in prepared:
                dispositions = [disposition(s, snapshot, accepted) for s in specs]
                if all(d == 'ACCEPTED' for d in dispositions):
                    continue
                if any(d not in ('ACCEPTED', 'UNSTARTED', 'COMPLETE_VALID', *ACTIVE) for d in dispositions):
                    raise RuntimeError('Historical failed key requires explicit audited recovery; never automatic retry: ' + unit['id'])
                if all(d == 'COMPLETE_VALID' for d in dispositions):
                    if specs[0]['regime']=='P2':
                        from review_r0_1_pair import p2_h0_candidates
                        if any(len(p2_h0_candidates(manifest['rows'],spec,mode))!=1 for spec,mode in zip(specs,['B16_BANKED','U_WB16'])):
                            continue  # Complete P2 is retained until its same-source one-port anchors are accepted.
                    for item in unit['specs']:
                        if digest(item['path']) != item['sha256']:
                            raise ValueError('Frozen execution spec changed')
                    publish(unit, specs, queue['revision'] + '_' + unit['id'], campaign['deadline_unix'],controller)
                    published = True
                    break
            if published:
                continue
            if all(all(disposition(s, snapshot, accepted) == 'ACCEPTED' for s in specs) for _, specs in prepared):
                status = 'SELECTED_READY_MATRIX_CURRENT_ACCEPTED'
                break
            launched = False
            if starts < campaign['maximum_starts'] and not any(k not in snapshot['runs'] for k in children):
                for unit, specs in prepared:
                    for item, spec in zip(unit['specs'], specs):
                        key = run_key(spec['identity'])
                        if disposition(spec, snapshot, accepted) != 'UNSTARTED' or key in denied or key in children:
                            continue
                        if digest(item['path']) != item['sha256']:
                            raise ValueError('Prepared execution spec changed')
                        authorize_launch(spec['identity'], digest(spec['qualified_release']), state)
                        try:
                            registry.admission(snapshot, socket.gethostname(), 1, spec['memory_reservation_bytes'], False, 'simulation', local_resources())
                            admit_result_output(snapshot, socket.gethostname(), spec['identity'], OUT / key)
                        except ValueError as exc:
                            denied.add(key)
                            print(json.dumps({'event': 'PREFLIGHT_NO_LEASE_NO_START', 'cell': spec['cell_id'], 'reason': str(exc)}), flush=True)
                            continue
                        log = (OUT / (queue['revision'] + '_' + spec['cell_id'] + '_CONTROLLER.log')).open('xb')
                        child = subprocess.Popen(python('run.py', '--spec', item['path']), cwd=REPO,
                                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                        children[key] = child, log
                        print(json.dumps({'event': 'ORIGINAL_RUNNER_INVOKED', 'cell': spec['cell_id'], 'runner_pid': child.pid}), flush=True)
                        launched = True
                        break
                    if launched:
                        break
            if not launched and not active and not children and not any(v['status'] in ACTIVE for v in snapshot['resource_leases'].values()):
                status = 'START_CAP_BOUNDARY' if starts >= campaign['maximum_starts'] else 'NO_CURRENT_SAFE_ENVELOPE_FOR_REMAINING_READY_CELLS'
                break
            time.sleep(5)
    except (Exception, KeyboardInterrupt) as exc:
        status = 'STOP_NEW_ACTIONS_SCOPED_OPERATOR_REVIEW_REQUIRED'
        error = repr(exc)
    finally:
        # Never kill, reclaim or modify an existing runner/lease on driver exit.
        final = read_registry(registry)
        write_json(receipt, {'status': status, 'error': error, 'at_unix': time.time(),
                            'runner': process_identity(os.getpid()), 'queue': str(queue_path), 'queue_sha256': queue_sha,
                            'deadline_unix': campaign['deadline_unix'],
                            'active_runs': [v for v in final['runs'].values() if v['status'] in ACTIVE],
                            'resume': 'Audit exact queue and progress, real PID/lease/current V2. Preserve all attempts. No implicit retry or reset.'})
        print(json.dumps({'event': 'FOREGROUND_CAMPAIGN_STOPPED', 'status': status, 'error': error}), flush=True)
    return 0 if error is None else 1
