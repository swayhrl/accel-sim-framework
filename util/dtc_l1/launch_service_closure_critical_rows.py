#!/usr/bin/env python3
"""Start two already-gated slow rows without restarting the live coordinator."""
import argparse
import csv
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import shutil
import subprocess
import time
from collect_service_closure_attempts import collect, sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',required=True)
    ap.add_argument('--root',required=True)
    a=ap.parse_args()
    root=Path(a.root)
    guard=(root/'CRITICAL_LAUNCH.lock').open('a')
    fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    with Path(a.plan).open() as f: plan=list(csv.DictReader(f,delimiter='\t'))
    labels=['R2_V2_COHORT_IO_GESUMMV','R2_V2_COHORT_OO_GESUMMV']
    chosen=[next(r for r in plan if r['label']==label) for label in labels]
    assert all(r['heavy']=='True' for r in chosen)
    specs={r['label']:json.loads(Path(r['spec_path']).read_text()) for r in plan}
    for r in chosen:assert sha(Path(r['spec_path']))==r['spec_sha256']
    existing=[(p,json.loads(p.read_text())) for p in root.glob('*/RUN_START.json')]
    assert not set(labels).intersection(s['spec']['label'] for _,s in existing)
    completed=[collect(p.parent) for p,s in existing if s['spec']['label'] in specs and (p.parent/'RUN_TERMINAL.json').exists()]
    assert all(r['status']=='PASS_CHECKED_SCOPE' for r in completed)
    qualified={specs[r['label']]['arm'] for r in completed if specs[r['label']]['phase']=='PILOT'}
    assert {'IO','OO'}.issubset(qualified)
    live=[s for p,s in existing if not (p.parent/'RUN_TERMINAL.json').exists()]
    assert len(live)+2<=8
    assert not any(specs[s['spec']['label']]['workload'] in ['GESUMMV','GEMM','MRI-Q'] for s in live)
    mem=dict(line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())
    assert int(mem['MemAvailable'].split()[0])*1024>=2*8*1024**3
    assert shutil.disk_usage(root).free>=8*512*1024**2
    receipt=dict(utc=datetime.now(timezone.utc).isoformat(),plan_sha256=sha(Path(a.plan)),
        labels=labels,qualified_arms=sorted(qualified),source_sha256=sha(Path(__file__)),
        live_before=[s['spec']['label'] for s in live],mem_available_kib=int(mem['MemAvailable'].split()[0]),
        disk_available_bytes=shutil.disk_usage(root).free,temporary_own_worker_cap=8,heavy_cap=2,
        reason='Start preregistered slow critical rows after same-arm strict pilot gates; no row/parameter/input change or coordinator restart.')
    hold=root/'HOLD_LAUNCHES'
    with hold.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    hold_hash=sha(hold)
    with (root/'CRITICAL_LAUNCH_V1.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    procs=[]
    for r in chosen:
        stream=(root/'launcher_logs'/(r['label']+'.log')).open('x')
        procs.append(subprocess.Popen(['python3',str(Path(__file__).with_name('service_closure_attempt.py')),
            '--spec',r['spec_path'],'--root',str(root)],stdout=stream,stderr=subprocess.STDOUT,start_new_session=True))
        stream.close()
    while True:
        starts=[json.loads(p.read_text()) for p in root.glob('*/RUN_START.json')]
        if set(labels).issubset(s['spec']['label'] for s in starts):break
        assert all(p.poll() is None for p in procs),'Preflight failure: retain launch hold and inspect original logs.'
        time.sleep(1)
    # An independent strict watcher may have encountered a failure during preflight.
    for p in root.glob('*/RUN_START.json'):
        s=json.loads(p.read_text())
        if s['spec']['label'] in specs and (p.parent/'RUN_TERMINAL.json').exists():
            assert collect(p.parent)['status']=='PASS_CHECKED_SCOPE'
    assert sha(hold)==hold_hash
    shutil.copy2(hold,root/'CRITICAL_LAUNCH_HOLD_RELEASED_V1.json')
    hold.unlink()
    print(json.dumps(dict(status='STARTED_REGISTERED_CRITICAL_ROWS',runner_pids=[p.pid for p in procs],labels=labels)),flush=True)


if __name__=='__main__':
    main()
