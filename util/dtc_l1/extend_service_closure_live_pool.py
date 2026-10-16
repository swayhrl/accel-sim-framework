#!/usr/bin/env python3
"""One bounded admission into the existing plan; never restart a live supervisor."""
import argparse
import csv
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from collect_service_closure_attempts import collect, sha


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True)
    ap.add_argument('--root', required=True)
    ap.add_argument('--historical-ledger', required=True)
    ap.add_argument('--expected-hold-sha', required=True)
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--own-cap', type=int, choices=(16, 24), default=16)
    ap.add_argument('--labels', nargs='+', required=True)
    a = ap.parse_args()
    root, out = Path(a.root).resolve(), Path(a.output_dir).resolve()
    guard = (root/'CRITICAL_LAUNCH.lock').open('a')
    fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert 1 <= len(a.labels) <= 8 and len(set(a.labels)) == len(a.labels)
    plan = list(csv.DictReader(Path(a.plan).open(), delimiter='\t'))
    by_label = {r['label']: r for r in plan}
    chosen = [by_label[label] for label in a.labels]
    assert all(r['workload'] != 'Hotspot1' and r['phase'] in {'COHORT', 'CONTROL'} for r in chosen)
    for r in chosen:
        assert sha(Path(r['spec_path'])) == r['spec_sha256']
    peak = {}
    for r in csv.DictReader(Path(a.historical_ledger).open(), delimiter='\t'):
        peak[r['workload']] = max(peak.get(r['workload'], 0), int(r['max_rss_kb']))
    # Twice the observed old-model peak, with a 4GiB minimum, is a host-memory
    # reservation, not an assertion of source/timing equivalence.
    reservations = {r['label']: max(4*1024**3, 2*peak[r['workload']]*1024) for r in chosen}
    hold = root/'HOLD_LAUNCHES'
    assert sha(hold) == a.expected_hold_sha
    original = hold.read_bytes()
    status = json.loads((root/'SCOPED_DISPATCH_STATUS.json').read_text())
    assert status['plan_sha256'] == sha(Path(a.plan)) and not status['failed']
    os.kill(status['coordinator_pid'], 0)

    def inspect():
        starts = [(p, json.loads(p.read_text())) for p in root.glob('*/RUN_START.json')]
        current = [(p, s) for p, s in starts if s['spec']['label'] in by_label]
        terminals = [collect(p.parent) for p, s in current if (p.parent/'RUN_TERMINAL.json').exists()]
        assert all(r['status'] == 'PASS_CHECKED_SCOPE' for r in terminals), 'Strict terminal failure: preserve admission hold.'
        qualified = {by_label[r['label']]['arm'] for r in terminals
                     if by_label[r['label']]['phase'] == 'PILOT' and by_label[r['label']]['workload'] != 'Hotspot1'}
        for row in chosen:
            if row['phase'] == 'CONTROL':
                assert row['arm'] in {'IO128', 'WAIT128'}
                assert {'IO', 'OO'}.issubset(qualified)
            else:
                assert row['arm'] in qualified
        held = set(json.loads((root/'ROW_ADMISSION_HOLDS.json').read_text())['held_labels'])
        assert not held.intersection(a.labels)
        live = [s['spec']['label'] for p, s in current if not (p.parent/'RUN_TERMINAL.json').exists()]
        return starts, terminals, qualified, live

    starts, terminals, qualified, live = inspect()
    assert not set(a.labels).intersection(s['spec']['label'] for p, s in starts)
    assert len(live) + len(chosen) <= a.own_cap
    mem = dict(s.split(':', 1) for s in Path('/proc/meminfo').read_text().splitlines())
    available = int(mem['MemAvailable'].split()[0])*1024
    assert available >= sum(reservations.values()) + 8*1024**3
    assert shutil.disk_usage(root).free >= a.own_cap*512*1024**2
    out.mkdir(parents=True, exist_ok=False)
    (out/'ORIGINAL_HOLD_LAUNCHES').write_bytes(original)
    receipt = dict(utc=datetime.now(timezone.utc).isoformat(), source_sha256=sha(Path(__file__)),
        plan_sha256=sha(Path(a.plan)), historical_ledger_sha256=sha(Path(a.historical_ledger)),
        labels=a.labels, spec_sha256={r['label']: r['spec_sha256'] for r in chosen},
        existing_live=live, qualified_non_hotspot_pilot_arms=sorted(qualified),
        terminal_reviews=terminals, observed_historical_peak_kib=peak,
        incremental_reservations_bytes=reservations, mem_available_bytes=available,
        disk_available_bytes=shutil.disk_usage(root).free, own_simulator_cap=a.own_cap,
        reason='Measured memory characterization permits bounded expansion; exact preregistered critical rows, no scientific identity or service change.',
        original_coordinator_pid=status['coordinator_pid'], original_hold_sha256=a.expected_hold_sha)
    save(out/'PREREGISTERED_ADMISSION.json', receipt)
    # The original supervisor sees a hold; scoped supervisor accepts only the
    # original hash. This temporary token disables both while this caller admits.
    replacement = root/'EXTENSION_HOLD.tmp'
    save(replacement, dict(reason='BOUNDED_LIVE_POOL_EXTENSION_EXCLUSIVE_ADMISSION', receipt=str(out), pid=os.getpid()))
    assert sha(hold) == a.expected_hold_sha
    replacement.replace(hold)
    temporary_sha = sha(hold)
    time.sleep(12)
    assert (root/'SCOPED_DISPATCH_STATUS.json').stat().st_mtime >= hold.stat().st_mtime
    launched = []
    runner = Path(__file__).with_name('service_closure_attempt.py')
    for row in chosen:
        starts, _, _, live = inspect()
        assert row['label'] not in {s['spec']['label'] for p, s in starts}
        assert len(live) < a.own_cap and sha(hold) == temporary_sha
        assert sha(Path(row['spec_path'])) == row['spec_sha256']
        stream = (root/'launcher_logs'/(row['label']+'.log')).open('x')
        proc = subprocess.Popen(['python3', str(runner), '--spec', row['spec_path'], '--root', str(root)],
                                stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        stream.close()
        while True:
            starts, _, _, _ = inspect()
            if any(s['spec']['label'] == row['label'] for p, s in starts):
                break
            assert proc.poll() is None, 'Preflight failed: keep admission hold and raw evidence.'
            time.sleep(1)
        launched.append(dict(label=row['label'], runner_pid=proc.pid))
        print(json.dumps(launched[-1]), flush=True)
    _, _, _, live = inspect()
    assert len(live) <= a.own_cap and sha(hold) == temporary_sha
    save(out/'STARTED.json', dict(utc=datetime.now(timezone.utc).isoformat(), launched=launched, live=live,
         strict_review='ALL_CURRENT_TERMINALS_RECHECKED', original_processes='PRESERVED'))
    replacement.write_bytes(original)
    assert sha(replacement) == a.expected_hold_sha
    replacement.replace(hold)
    save(out/'SCOPED_AUTHORITY_RESTORED.json', dict(hold_sha256=sha(hold),
         coordinator_pid=status['coordinator_pid'], new_supervisor=False,
         note='Existing cap8 coordinator observes added attempts and refills only below its cap; no simulator restarted.'))


if __name__ == '__main__':
    main()
