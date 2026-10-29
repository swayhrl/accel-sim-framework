"""Main's bounded30-minute review publisher. No simulator or authority writes."""
import argparse
import collections
import csv
import datetime
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import uuid

J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0, str(J/'tools'))
from ep_perf_common import GOAL, M, G, REG, EPOCH, authority, exact, need, put, read, ref, sha

REPO = J/'review'
DOC = Path('docs/ep_l2/operations/ep_full_workload_performance_20261027_v1')
REMOTE = 'git@github.com:swayhrl/accel-sim-framework.git'
BRANCH = 'hrl/ep-l2-full-workload-performance-20261027-v1'
ANALYSIS = J/'agent_b/results_analysis_20261028_v1'
CTRL = J/'control/periodic_results_publication_v1'
INTERVAL = 1800
ALLOWED_ANALYSIS = {'RESULTS_ANALYSIS_CURRENT.md', 'RESULTS_ANALYSIS_CURRENT.json', 'RESULTS_ANALYSIS_CURRENT.csv'}
REPORTER_REF = None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def git(*args, data=None):
    env = dict(os.environ, GIT_SSH_COMMAND='ssh -oBatchMode=yes -oConnectTimeout=15 -oServerAliveInterval=10 -oServerAliveCountMax=2',
               GIT_TERMINAL_PROMPT='0')
    a = subprocess.run(['git', '-C', str(REPO), *args], input=data,
                       capture_output=True, timeout=90, env=env)
    need(a.returncode == 0, 'git '+args[0]+': '+a.stderr.decode(errors='replace')[-2000:])
    return a.stdout.decode().strip()


def csv_rows(data):
    return list(csv.DictReader(io.StringIO(data.decode())))


def refresh_report():
    """Existing pure aggregation only; this never imports a scientific actor."""
    from ep_perf_common import module
    need(REPORTER_REF is not None, 'reporter pin not initialized')
    module(REPORTER_REF, 'MainPeriodicReadOnlyAggregation').report()


def capture():
    live = J/'analysis/live'
    last = None
    for unused in range(4):
        status_bytes = (live/'CURRENT_STATUS.json').read_bytes()
        files = {name: (live/name).read_bytes() for name in ['RUN_STATUS.csv', 'MATCHED_PERFORMANCE.csv']}
        if status_bytes != (live/'CURRENT_STATUS.json').read_bytes():
            last = 'reporter transition'
            continue
        status = json.loads(status_bytes)
        runs = csv_rows(files['RUN_STATUS.csv'])
        pairs = csv_rows(files['MATCHED_PERFORMANCE.csv'])
        counts = dict(collections.Counter(r['state'] for r in runs))
        if (len(runs) != status['admitted_exact_points'] or counts != status['terminal_counts'] or
                len(pairs) != status['all_accepted_profile_pairs']):
            last = 'cross-file population transition'
            continue
        need((datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(status['utc'].replace('Z','+00:00'))).total_seconds() < 300,
             'live reporter older than five minutes; do not publish stale current claims')
        registry, unused_epoch = authority()
        q = registry['registered_future_requests'][GOAL]
        actual_counts = dict(collections.Counter(q['consumed'].get(r['cohort'], {}).get('state', 'NOT_STARTED') for r in runs))
        if set(q['admitted_specs']) != {r['cohort'] for r in runs} or actual_counts != counts:
            last = 'scientific state advanced; wait for next reporter snapshot'
            refresh_report()
            continue
        need(q['budget'] == len(q['admitted_specs']) and q['remaining'] == q['budget']-len(q['consumed']), 'budget arithmetic')
        accepted = {r['cohort'] for r in runs if r['state'] == 'CLOSED_ACCEPTED'}
        need(all(p['S_cohort'] in accepted and p['F_cohort'] in accepted for p in pairs), 'pair without accepted endpoints')
        endpoints = []
        for case in sorted(accepted):
            row = q['consumed'][case]
            pointref = row['accepted_point_ref']
            need(Path(pointref['path']).resolve().is_relative_to((J/'cases'/case/'run').resolve()), 'accepted-point scope')
            point = exact(pointref)
            ar = row['archive_receipt_ref']
            need(Path(ar['path']).resolve().is_relative_to((J/'cases'/case/'control').resolve()), 'archive receipt scope')
            archive = exact(ar)
            need(archive['status'] == 'TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and
                 len(archive['native_restores']) == 2 and archive['source_keep'] is True, 'actual archive closure')
            endpoints.append(dict(cohort=case, state='CLOSED_ACCEPTED', accepted_point_ref=pointref,
                                  archive_receipt_ref=ar, archive_ref=archive['archive_ref'],
                                  source_identity=point['source_identity'], spec_ref=point['spec_ref'],
                                  cycles=point['cycles'], instructions=point['instructions'], CTA=point['CTA'],
                                  kernel_count=point['kernel_count'], hardware_drained=point['hardware_drained']))
        files['CURRENT_STATUS.json'] = status_bytes
        files['ACCEPTED_RESULT_REFS_CURRENT.json'] = (json.dumps(dict(goal=GOAL, utc=now(),
            status='INTERIM_ACCEPTED_ENDPOINT_REFERENCE_INDEX_NOT_COMPLETE_COMMON_SET',
            rows=endpoints, accepted_count=len(endpoints), raw_or_Trace_copied=False), sort_keys=True, indent=2)+'\n').encode()
        return files, status, q
    raise RuntimeError(last)


def analysis_snapshot():
    path = ANALYSIS/'CURRENT.json'
    if not path.exists():
        return {}, dict(status='AGENT_B_FIRST_ANALYSIS_PENDING')
    raw = path.read_bytes()
    x = json.loads(raw)
    need(x['schema'] == 'EP_AGENT_B_ACCEPTED_RESULTS_ANALYSIS_SNAPSHOT_V1' and x['goal'] == GOAL, 'analysis pointer schema/goal')
    outputs = {}
    for r in x['files']:
        name = r['publish_name']
        p = Path(r['path'])
        need(name in ALLOWED_ANALYSIS and name not in outputs and p.resolve().is_relative_to(ANALYSIS.resolve()), 'analysis allowlist/scope')
        b = p.read_bytes()
        need(len(b) <= 4*M and hashlib.sha256(b).hexdigest() == r['sha256'], 'closed analysis bytes/SHA')
        outputs['results_analysis/'+name] = b
    need(path.read_bytes() == raw and sum(map(len, outputs.values())) <= 8*M, 'analysis publication transition/bound')
    return outputs, dict(status='BYTE_VERIFIED_AGENT_ANALYSIS', analysis_utc=x['utc'], manifest_ref=ref(path),
                         analysis_is_asof_own_inputs_not_automatically_latest_model_completion=True)


def live_models():
    rows = []
    for case, x in read(J/'control/DISPATCH_CLAIMS.json')['claims'].items():
        if x['state'] != 'RUNNING':
            continue
        row = dict(cohort=case, pid=x['model_pid'], start_ticks=x['model_start_ticks'], actual_generation_live=False)
        try:
            stat = (Path('/proc')/str(row['pid'])/'stat').read_text().rsplit(')',1)[1].split()
            row['actual_generation_live'] = int(stat[19]) == row['start_ticks'] and stat[0] not in ['Z','X']
        except (FileNotFoundError, ProcessLookupError):
            row['status'] = 'DEPARTED_PENDING_RECONCILIATION'
        rows.append(row)
    return rows


def publication():
    uid = str(uuid.uuid4())
    attempt = CTRL/'attempts'/uid
    attempt.mkdir(parents=True, exist_ok=False)
    staging = False
    before = None
    staged_paths = []
    try:
        available = int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines()
                             if x.startswith('MemAvailable:')))*1024
        need(available >= 512*M, 'finite control-plane512MiB actual RAM envelope; no new model')
        need(git('branch', '--show-current') == BRANCH, 'wrong review branch')
        need(not git('diff', '--cached', '--name-only'), 'another index owner is staging; do not overwrite')
        status = read(J/'analysis/live/CURRENT_STATUS.json')
        age = (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(status['utc'].replace('Z','+00:00'))).total_seconds()
        if age > 120:
            refresh_report()
        files, status, q = capture()
        analysis_files, analysis = analysis_snapshot()
        files.update(analysis_files)
        fs = os.statvfs(J)
        need(fs.f_bavail*fs.f_frsize > G+q['reserved_write_bytes']+32*M, 'registered remaining writes plus32MiB bounded Git delta and1GiB emergency')
        for source in ['control/STAGE_MAIN35_SYRK_LAVAMD_F2_V1.json', 'control/W_ONLY_EXACT3_MAIN_EXECUTION_V1.json']:
            p = J/source
            if p.exists():
                files[p.name] = p.read_bytes()
        snapshot = dict(schema='EP_MAIN_PERIODIC_RESULTS_PUBLICATION_V1', goal=GOAL, utc=now(),
                        live_snapshot_utc=status['utc'], publication_interval_seconds=INTERVAL,
                        registered=status['admitted_exact_points'], consumed=status['consumed_starts'],
                        accepted=status['fully_closed_accepted'], terminal_counts=status['terminal_counts'],
                        remaining=status['fresh_registered_remaining'], analysis=analysis,
                        complete_common_set_GM=None, scientific_scope='TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST',
                        numeric_output='UNKNOWN', original_capture_completeness='UNKNOWN',
                        large_assets='GENUINE164_NO_BULK_GIT_COPY', source_keep=True,
                        simulator_starts=0, scientific_authority_writes=0, writer='Main sole periodic publisher')
        snapshot['model_generations'] = live_models()
        snapshot['verified_live_models'] = sum(x['actual_generation_live'] for x in snapshot['model_generations'])
        files['PERIODIC_PUBLICATION_CURRENT.json'] = (json.dumps(snapshot, sort_keys=True, indent=2)+'\n').encode()
        need(sum(map(len, files.values())) <= 16*M, 'bounded review-only publication')
        before = git('rev-parse', 'HEAD')
        remote = git('ls-remote', REMOTE, 'refs/heads/'+BRANCH).split()
        need(len(remote) == 2, 'remote branch identity missing')
        if remote[0] != before:
            need(git('merge-base', remote[0], before) == remote[0], 'remote diverged; no force/merge')
            git('push', REMOTE, 'HEAD:refs/heads/'+BRANCH)
            need(git('ls-remote', REMOTE, 'refs/heads/'+BRANCH).split()[0] == before, 'pending head readback')
        for name, b in files.items():
            rel = (DOC/name).as_posix()
            oid = git('hash-object', '-w', '--stdin', data=b.replace(b'\r\n', b'\n'))
            git('update-index', '--add', '--cacheinfo', '100644,'+oid+','+rel)
            staging = True
            staged_paths.append(rel)
            target = REPO/rel
            # Reporter owns these three volatile worktree files. Their captured
            # blobs above are coherent; never race its working-file writes.
            if name not in ['CURRENT_STATUS.json', 'RUN_STATUS.csv', 'MATCHED_PERFORMANCE.csv']:
                target.parent.mkdir(parents=True, exist_ok=True)
                temp = target.with_name('.'+target.name+'.publisher')
                temp.write_bytes(b.replace(b'\r\n', b'\n'))
                temp.replace(target)
        git('diff', '--cached', '--check')
        git('commit', '-m', 'Publish EP-L2 accepted results and analysis '+snapshot['utc'][:16]+' UTC')
        staging = False
        head = git('rev-parse', 'HEAD')
        git('push', REMOTE, 'HEAD:refs/heads/'+BRANCH)
        actual = git('ls-remote', REMOTE, 'refs/heads/'+BRANCH).split()[0]
        need(actual == head, 'actual remote HEAD readback mismatch')
        receipt = dict(status='COMMITTED_PUSHED_AND_REMOTE_HEAD_READBACK_PASS', utc=now(),
                       previous_HEAD=before, HEAD=head, remote=REMOTE, branch=BRANCH,
                       accepted=snapshot['accepted'], analysis=analysis,
                       files={k:dict(bytes=len(v), sha256=hashlib.sha256(v).hexdigest()) for k,v in files.items()},
                       raw_or_Trace_copied=False, scientific_starts=0, registry_writes=0)
        put(attempt/'RECEIPT.json', receipt, True)
        put(CTRL/'LATEST.json', receipt)
        return receipt
    except Exception as error:
        # Only release this writer's own index entries if no commit was made.
        # All source data/working files and pending local commits are preserved.
        if staging and before is not None:
            try:
                names = set(git('diff', '--cached', '--name-only').splitlines())
                if git('rev-parse', 'HEAD') == before and names <= set(staged_paths):
                    git('restore', '--staged', '--', *staged_paths)
            except Exception:
                pass
        hold = dict(status='PUBLICATION_HOLD_SCIENCE_UNCHANGED', utc=now(), error=str(error), traceback=traceback.format_exc())
        put(attempt/'HOLD.json', hold, True)
        put(CTRL/'LATEST_HOLD.json', hold)
        return hold


def main():
    global REPORTER_REF
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=int, default=24, choices=range(1,25))
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256*M, 256*M))
    resource.setrlimit(resource.RLIMIT_CORE, (0,0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16*M,16*M))
    os.nice(15)
    os.sched_setaffinity(0, {max(os.sched_getaffinity(0))})
    CTRL.mkdir(parents=True, exist_ok=True)
    lock = (CTRL/'SINGLE_MAIN_PUBLISHER.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    pid = os.getpid()
    ticks = int((Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
    deadline = time.monotonic()+args.hours*3600
    REPORTER_REF = ref(J/'tools/ep_perf_live_report_v1.py')
    next_at = time.monotonic()
    lease = dict(schema='EP_MAIN_PERIODIC_RESULTS_PUBLISHER_LEASE_V1', pid=pid, start_ticks=ticks,
                 source_ref=ref(__file__), interval_seconds=INTERVAL, finite_hours=args.hours,
                 read_only_reporter_ref=REPORTER_REF,
                 created_utc=now(), science_starts=0, authority_writes=0, no_new_scientific_lane=True)
    put(CTRL/'LEASE.json', lease)
    last_request = None
    while time.monotonic() < deadline and not (CTRL/'STOP').exists():
        request = CTRL/'PUBLISH_NOW.json'
        token = request.read_bytes() if request.exists() else None
        due = time.monotonic() >= next_at
        if due or token != last_request:
            result = publication()
            print(json.dumps(result), flush=True)
            last_request = token
            if due:
                next_at += INTERVAL
            put(CTRL/'NEXT.json', dict(next_regular_utc=(datetime.datetime.now(datetime.timezone.utc)+
                datetime.timedelta(seconds=max(0,next_at-time.monotonic()))).isoformat(), last_status=result['status'], lease=lease))
        time.sleep(min(5, max(.1, deadline-time.monotonic())))
    put(CTRL/'TERMINAL.json', dict(status='FINITE_LEASE_ENDED_OR_MAIN_STOPPED', utc=now(), lease=lease))


if __name__ == '__main__':
    main()
