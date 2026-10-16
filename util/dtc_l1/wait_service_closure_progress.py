#!/usr/bin/env python3
"""Bounded read-only observation of existing jobs; never launch, retry or stop them."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observe(root, processes):
    live, missing, reused = {}, [], []
    for pid, previous in processes.items():
        try:
            stat = (Path('/proc')/pid/'stat').read_text().rsplit(')', 1)[1].split()
        except FileNotFoundError:
            missing.append(pid)
            continue
        if int(stat[19]) != previous['start_ticks']:
            reused.append(pid)
            continue
        ticks = int(stat[11]) + int(stat[12])
        assert ticks >= previous['cpu_ticks']
        live[pid] = dict(state=stat[0], start_ticks=int(stat[19]), cpu_ticks=ticks)
    mem = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    return dict(utc=datetime.now(timezone.utc).isoformat(), actual_live_simulators=live,
                missing_processes=missing, reused_pids=reused,
                mem_available_kib=int(mem['MemAvailable'].split()[0]),
                disk_free_bytes=shutil.disk_usage(root).free)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True)
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--checkpoint', required=True)
    ap.add_argument('--seconds', type=int, default=300, choices=range(1, 601), metavar='1..600')
    a = ap.parse_args()
    root, baseline, checkpoint = Path(a.root), Path(a.baseline), Path(a.checkpoint)
    source_sha = digest(Path(__file__))
    baseline_sha = digest(baseline)
    state = checkpoint/'REGISTERED_R2_STATE.tsv'
    state_sha = digest(state)
    base = json.loads(baseline.read_text())
    processes = base.get('processes', base.get('actual_live_simulators'))
    assert processes, 'No previously observed live jobs: inspect terminal state.'
    known = {r['attempt_uuid']+'.json' for r in csv.DictReader(state.open(), delimiter='\t')
             if r['status'] == 'PASS_CHECKED_SCOPE'}
    started, last = time.monotonic(), 0
    observations, terminal_reviews = [], {}
    event = 'WAITING'
    while time.monotonic()-started < a.seconds:
        sample = observe(root, processes)
        for file in (root/'r2-attempts/strict_reviews_v2').glob('*.json'):
            if file.name in known:
                continue
            try:
                review = json.loads(file.read_text())
            except json.JSONDecodeError:
                # The existing watcher creates its immutable receipt before
                # writing it. An incomplete read is not a failed simulation.
                continue
            terminal_reviews[file.name] = review
        if terminal_reviews or sample['missing_processes'] or sample['reused_pids']:
            event = 'NEW_TERMINAL_OR_HANDLE_CHANGE_REQUIRES_REVIEW'
        elif any(v['state'] == 'Z' for v in sample['actual_live_simulators'].values()):
            event = 'EXITING_HANDLE_REQUIRES_TERMINAL_REVIEW'
        if time.monotonic()-last >= 45 or event != 'WAITING':
            observations.append(sample)
            print(json.dumps({k: v for k, v in sample.items() if k != 'actual_live_simulators'} |
                             dict(event=event, live_count=len(sample['actual_live_simulators']),
                                  new_strict_receipts=sorted(terminal_reviews))), flush=True)
            last = time.monotonic()
        if event != 'WAITING':
            break
        time.sleep(min(2, max(0, a.seconds-(time.monotonic()-started))))
    else:
        event = 'VERIFIED_WAIT_INTERVAL_COMPLETE'
    assert digest(baseline) == baseline_sha and digest(state) == state_sha
    assert digest(Path(__file__)) == source_sha
    receipt = dict(event=event, source_sha256=source_sha,
                   wait_elapsed_host_seconds=time.monotonic()-started,
                   baseline=str(baseline.resolve()), baseline_sha256=baseline_sha,
                   checkpoint=str(checkpoint.resolve()), checkpoint_state_sha256=state_sha,
                   observations=observations, new_terminal_reviews=terminal_reviews,
                   no_launcher=True, no_restart=True, no_timeout_applied_to_simulators=True)
    out = root/'verified-waits'
    out.mkdir(exist_ok=True)
    target = out/('bounded_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'.json')
    with target.open('x') as f:
        json.dump(receipt, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(event=event, receipt=str(target))), flush=True)


if __name__ == '__main__':
    main()
