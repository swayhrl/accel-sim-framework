#!/usr/bin/env python3
"""Resume a frozen R2 plan with row-local gates and a single coordinator lock."""
import argparse
import csv
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from collect_service_closure_attempts import collect, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True)
    ap.add_argument('--root', required=True)
    ap.add_argument('--workers', type=int, default=6)
    args = ap.parse_args()
    assert 1 <= args.workers <= 6
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    lock = (root / 'DISPATCH.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    with Path(args.plan).open() as f:
        plan = list(csv.DictReader(f, delimiter='\t'))
    for row in plan:
        assert sha(Path(row['spec_path'])) == row['spec_sha256']
    runner = Path(__file__).with_name('service_closure_attempt.py')
    active = {}
    launcher_failures = {}
    terminal_cache = {}
    logs = root / 'launcher_logs'
    logs.mkdir(exist_ok=True)
    previous_summary = None
    while True:
        for label, (proc, stream) in list(active.items()):
            if proc.poll() is not None:
                if proc.returncode:
                    launcher_failures[label] = proc.returncode
                stream.close()
                del active[label]
        # Reading terminal receipts never modifies an old attempt or receipt.
        attempts = {}
        for start in root.glob('*/RUN_START.json'):
            data = json.loads(start.read_text())
            label = data['spec']['label']
            if label in {r['label'] for r in plan}:
                terminal = start.parent/'RUN_TERMINAL.json'
                if terminal.exists():
                    signature = tuple((p.stat().st_mtime_ns,p.stat().st_size) for p in
                                      [terminal,start.parent/'simulator.stdout',start.parent/'simulator.stderr'])
                    cached = terminal_cache.get(str(start.parent))
                    if cached is None or cached[0] != signature:
                        cached = (signature,collect(start.parent))
                        terminal_cache[str(start.parent)] = cached
                    attempts[label] = cached[1]
                else:
                    attempts[label] = dict(status='RUNNING',run_dir=str(start.parent))
        passed = {label for label, r in attempts.items() if r['status']=='PASS_CHECKED_SCOPE'}
        failed = {label for label, r in attempts.items() if r['status']=='FAIL_PRESERVED'} | set(launcher_failures)
        qualified = {r['arm'] for r in plan if r['phase']=='PILOT' and r['label'] in passed}
        heavy_active = sum(r['heavy']=='True' and (r['label'] in active or attempts.get(r['label'],{}).get('status')=='RUNNING') for r in plan)
        external = 0
        for p in Path('/proc').glob('[0-9]*/cmdline'):
            try:
                argv = p.read_bytes().split(b'\0')
                exe = argv[0].decode(errors='replace')
                if '/workspace/dtc-service-closure-174-v1/' in exe and '/binaries/' in exe and exe.endswith('/accel-sim.out') and str(root) not in exe:
                    external += 1
            except (OSError, IndexError):
                pass
        resumed_running = sum(r.get('status')=='RUNNING' for label,r in attempts.items() if label not in active)
        available = min(args.workers-len(active)-resumed_running, 8-external-len(active)-resumed_running)
        if not failed and not (root/'HOLD_LAUNCHES').exists():
            for row in sorted(plan, key=lambda r:(int(r['priority']),r['label'])):
                label = row['label']
                if available <= 0:
                    break
                if label in attempts or label in active:
                    continue
                if row['phase']=='COHORT' and row['arm'] not in qualified:
                    continue
                if row['phase']=='CONTROL' and not {'IO','OO'}.issubset(qualified):
                    continue
                heavy = row['heavy']=='True'
                if heavy and heavy_active>=2:
                    continue
                mem = dict(s.split(':',1) for s in Path('/proc/meminfo').read_text().splitlines())
                free_mem = int(mem['MemAvailable'].split()[0])*1024
                if free_mem < (8 if heavy else 4)*1024**3:
                    continue
                if shutil.disk_usage(root).free < (len(active)+external+1)*512*1024**2:
                    continue
                assert sha(Path(row['spec_path'])) == row['spec_sha256']
                stream = (logs/(label+'.log')).open('x')
                proc = subprocess.Popen(['python3', str(runner), '--spec',row['spec_path'],'--root',str(root)],stdout=stream,stderr=subprocess.STDOUT)
                active[label]=(proc,stream)
                available-=1
                heavy_active+=int(heavy)
                print('LAUNCHED',label,'pid='+str(proc.pid),flush=True)
        summary = dict(coordinator_pid=os.getpid(), plan_sha256=sha(Path(args.plan)),
                       passed=len(passed), failed=sorted(failed), active=sorted(active),
                       resumed_running=resumed_running, external_simulators=external,
                       qualified_pilot_arms=sorted(qualified), planned=len(plan),
                       modern_dtc='NOT_IN_THIS_PLAN_CAPACITY_REVIEW_PENDING')
        temp = root/'DISPATCH_STATUS.tmp'
        temp.write_text(json.dumps(summary,indent=2)+'\n')
        temp.replace(root/'DISPATCH_STATUS.json')
        if summary != previous_summary:
            print(json.dumps(summary),flush=True)
            previous_summary=summary
        if len(passed)==len(plan):
            return
        if not active and not resumed_running:
            if failed:
                raise SystemExit('PRESERVED_FAILURE_HOLD: diagnose before authorizing a replacement identity')
            if not any(r['label'] not in attempts for r in plan):
                return
        time.sleep(10)


if __name__=='__main__':
    main()
