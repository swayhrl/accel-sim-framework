"""Independent official R0.1 directed replay; no compiler or automatic certificate."""
import argparse
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import time

from registry import Registry, local_resources, process_identity, write_json
from run import GATES, digest, process_tree_rss, terminate_owned

REPO = Path(__file__).resolve().parents[3]
PLAN = REPO / 'docs/ep_l2/review_packs/FT20261017_LANE5_ENGINEERING_PILOT_REVIEW_r1/INDEPENDENT_GATE_PLAN_r7.json'
BUILD = Path('/workspace/build/ep-l2-ft20261016-lane1-r0-1')
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-r0-1')
FRAMEWORK = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r0-1')
PREFILL = ('PREFILL_FULL_ADDRESS_SECTOR_REPEAT_EPOCH_NATIVE_HIT PASS',
           'PREFILL_CLEAN_VICTIM_REAL_MISS_FILL_QUIESCENT_OWNER_REUSE PASS',
           'PREFILL_DIRTY_VICTIM_REFUSAL_UNMODIFIED_REAL_WB_SET_DONE_RETRY PASS',
           'PREFILL_FRONTEND_PENDING_AND_RESPONSE_BACKPRESSURE_GUARD PASS',
           'FT_HOST_PREFILL_PRODUCTION_SUITE PASS')
DIRECTED = ('FT WAD128 pre-mutation refusal and drain PASS',
            'FT sector identity, merge, fill and response-backpressure pins PASS',
            'FT production same-bank pool-full, nonmutating refusal, WB progress PASS',
            'FT independent store/WB/lower/fill/merged-response version reference PASS',
            'FT production directed suite PASS')


def require(ok, reason):
    if not ok: raise ValueError(reason)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, timeout=20,
                                   env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))


def check_directed_log(case, text):
    name = case['case']
    if name.startswith('host_prefill_'):
        require(all(marker in text for marker in PREFILL), 'Missing host prefill lifecycle/reference marker')
    elif name == 'ft_directed':
        require(all(marker in text for marker in DIRECTED), 'Missing directed reference/request/lifecycle marker')
        for mode in (1, 2):
            for cap in (8, 16):
                require(f'FT production capacity/version/drain mode={mode} C={cap} PASS' in text, 'Missing capacity case')
    else:
        mode, cap = map(int, case['argv'][2:4])
        matches = re.findall(r'FT real partition lower-full/WBUF/WAD/set_done mode=(\d+) C=(\d+) peak=(\d+) PASS', text)
        require(len(matches) == 1 and tuple(map(int, matches[0][:2])) == (mode, cap), 'Partition identity/closure missing')
        peak = int(matches[0][2]); require(0 < peak <= 128 and (mode != 1 or peak <= cap), 'Finite WBUF/WAD bound')
        if 'clock' in name:
            rows = re.findall(r'CLOCK_AUDIT\|offset=(\d+)\|violations=(\d+)\|max_grants_per_physical_bank_cycle=(\d+)', text)
            expected = case['required_clock']['offset']
            require(len(rows) == 1 and int(rows[0][0]) == expected and int(rows[0][1]) == 0 and int(rows[0][2]) <= 1,
                    'Physical bank clock counterexample or missing exact audit')
            require('CLOCK_VIOLATION|' not in text, 'Physical bank violation')
    return {'status': 'PASS', 'scope': 'Exact production-driven directed assertions/markers; no automatic eleven-gate certificate'}


def audit_producer(path, publication, published_path):
    raw = Path(path).read_bytes(); p = json.loads(raw)
    require(git(REPO, 'show', publication + ':' + published_path) == raw, 'Producer receipt is not exact published Git bytes')
    require(p.get('owner') == 'lane1' and p.get('release') == 'R0.1' and
            p.get('status') == 'PRODUCER_TESTS_PASS_NOT_INDEPENDENTLY_QUALIFIED', 'No official completed R0.1 producer')
    require(p.get('compiler_started') is True and p.get('independent_qualification') is False,
            'Producer/independent provenance missing')
    require(p.get('engineering_classification') not in ('ENGINEERING_ONLY', 'ENGINEERING_PILOT') and
            p.get('classification') not in ('ENGINEERING_ONLY', 'ENGINEERING_PILOT'), 'Engineering binary is ineligible')
    require(Path(p['build']).resolve() == BUILD and Path(p['binary']).resolve() == BUILD / 'accel-sim.out', 'Foreign/engineering build root')
    require(digest(p['binary']) == p['binary_sha256'], 'Official binary hash mismatch')
    plan = json.loads(PLAN.read_text())
    for root, key in [(CORE, 'core_source_commit'), (FRAMEWORK, 'framework_source_commit')]:
        require(git(root, 'rev-parse', 'HEAD').decode().strip() == p[key], 'Producing source moved')
        require(not git(root, 'status', '--porcelain', '--untracked-files=no'), 'Dirty producing tracked source')
    require(p['core_source_commit'] == plan['static_target_core'] and p['framework_source_commit'] == plan['static_target_framework'],
            'Source changed: perform affected-gate rebind before replay, never inherit qualification')
    vendor = FRAMEWORK / 'gpu-simulator/extern/pybind11'
    require(git(vendor, 'rev-parse', 'HEAD').decode().strip() == p['pybind11']['commit'] == 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b', 'Vendor mismatch')
    require(not git(vendor, 'status', '--porcelain', '--untracked-files=no'), 'Dirty vendor')
    require(bool(p['assertion_flags_sha256']), 'Missing assertion flags')
    for name, h in p['assertion_flags_sha256'].items():
        require(digest(name) == h and '-DNDEBUG' not in Path(name).read_text(), 'Changed flags or disabled assertions')
    for name, h in p['input_sha256'].items(): require(digest(name) == h, 'Changed producer input: ' + name)
    commands = [[str(BUILD / ('gpgpu-sim/' + case['target'])),
                 *[str(CORE / arg) if arg.endswith('.config') else arg for arg in case['argv']]]
                for case in plan['planned_production_executions']]
    require(len(p['tests']) == 21 and [r['command'] for r in p['tests']] == commands, 'Actual21 producer command matrix incomplete or different')
    for case, row in zip(plan['planned_production_executions'], p['tests']):
        require(row['exit_code'] == 0 and digest(row['log']) == row['log_sha256'] and row.get('process'), 'Missing real producer execution/log')
        require(digest(row['command'][0]) == p['test_executables'][row['command'][0]], 'Test executable not pinned')
        check_directed_log(case, Path(row['log']).read_text())
    for name in ('configure', 'build'):
        rows = [r for r in p['commands'] if Path(r['log']).name == name + '.log']
        require(len(rows) == 1 and rows[0]['exit_code'] == 0 and digest(rows[0]['log']) == rows[0]['log_sha256'], 'Missing exact compiler log')
    return p, plan, commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer-report', required=True, type=Path)
    parser.add_argument('--producer-publication', required=True)
    parser.add_argument('--published-report-path', required=True)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--deadline-unix', required=True, type=float)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    require(time.time() < args.deadline_unix, 'CONTINUE deadline passed')
    producer, plan, commands = audit_producer(args.producer_report, args.producer_publication, args.published_report_path)
    args.out.mkdir(parents=True, exist_ok=False)
    report = {'status': 'EXACT_OFFICIAL_PRODUCER_AUDITED_NOT_EXECUTED', 'producer_publication': args.producer_publication,
              'producer_report_sha256': digest(args.producer_report), 'source_identity': {k: producer[k] for k in ('core_source_commit', 'framework_source_commit', 'binary_sha256', 'pybind11')},
              'tests': [], 'gates': {g: 'PENDING_INDEPENDENT_REVIEW' for g in sorted(GATES)},
              'scientific_qualification': False, 'automatic_certificate_or_launch_authority': False}
    lease = None; process = None
    try:
        if not args.execute: return
        require(local_resources()['disk_free_bytes'] >= 48 * 1024**3, 'Unchanged48GiB floor')
        s = os.statvfs('/root/share'); require(s.f_bavail * s.f_frsize >= 40 * 1024**3, 'Share40GiB protection')
        registry = Registry();lease = registry.build_lease('lane5', cpu=1, memory=4 * 1024**3)
        report['lease_id'] = lease;report['status'] = 'INDEPENDENT_DIRECTED_RUNNING'
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        environment = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        for case, command in zip(plan['planned_production_executions'], commands):
            require(time.time() < args.deadline_unix, 'CONTINUE deadline reached')
            live = local_resources(); share = os.statvfs('/root/share')
            require(live['disk_free_bytes'] >= 48 * 1024**3 and live['available_memory_bytes'] >= 64 * 1024**3 and
                    share.f_bavail * share.f_frsize >= 40 * 1024**3, 'Pre-dispatch resource floor')
            log = args.out / (case['case'] + '.log'); row = {'case': case['case'], 'command': command, 'log': str(log), 'binary_sha256': digest(command[0])}
            report['tests'].append(row);write_json(args.out / 'INDEPENDENT_R0_1_DIRECTED.json', report)
            with log.open('x') as stream:
                process = subprocess.Popen(command, cwd=args.out, env=environment, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                row['process'] = process_identity(process.pid); started = time.monotonic()
                while process.poll() is None:
                    live = local_resources(); share = os.statvfs('/root/share')
                    require(time.time() < args.deadline_unix and time.monotonic() - started < 180, 'Owned test deadline')
                    require(live['disk_free_bytes'] >= 48 * 1024**3 and live['available_memory_bytes'] >= 64 * 1024**3 and
                            share.f_bavail * share.f_frsize >= 40 * 1024**3, 'Resource floor; stop own test only')
                    require(process_tree_rss(process.pid) <= 4 * 1024**3 and log.stat().st_size <= 128 * 1024**2, 'Owned test cap')
                    time.sleep(0.2)
            row.update(exit_code=process.returncode, log_sha256=digest(log));require(process.returncode == 0, 'Independent test failed')
            row['independent_validation'] = check_directed_log(case, log.read_text())
            row['producer_stdout_equal'] = row['log_sha256'] == producer['tests'][len(report['tests']) - 1]['log_sha256']
            print(case['case'], 'PASS', flush=True);process = None
        audit_producer(args.producer_report, args.producer_publication, args.published_report_path)
        report['status'] = 'INDEPENDENT21_PASS_REVIEW_ELEVEN_GATES_BEFORE_ANY_APPLICATION'
        report['unresolved_before_certificate'] = ['Affected OFF production equivalence and mode-legality qualification per unchanged r7 plan',
                                                 'Independent sector/request/lifecycle evidence review, exact V2 launch authorization and complete input hashing']
    except BaseException as error:
        report['status'] = 'INDEPENDENT_FAILED_FROZEN_EVIDENCE_NO_APPLICATION';report['error'] = repr(error)
        raise
    finally:
        if process is not None:
            terminate_owned(process)
            row['exit_code'] = process.returncode
            if log.exists(): row['log_sha256'] = digest(log)
        if lease is not None: registry.release_build(lease, 'lane5')
        write_json(args.out / 'INDEPENDENT_R0_1_DIRECTED.json', report)


if __name__ == '__main__':
    main()
