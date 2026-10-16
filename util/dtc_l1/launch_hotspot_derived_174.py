#!/usr/bin/env python3
"""One bounded submission through the existing174 authority; no daemon/retry."""
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

HOLD_SHA='070fe0146a778e5d12e960dafeaf17985273a8f4fc65936569b31c15b341300e'
PLAN_SHA='281b2d22ace3bbf105711473516f075fc11c495a1d6c214d9f4a3e42414892e1'


def save(p,value):
    with p.open('x') as f: json.dump(value,f,indent=2);f.write('\n')


def simulators():
    found=[]
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            cmd=p.read_bytes().split(b'\0'); exe=cmd[0].decode()
            if exe.startswith('/workspace/dtc-service-closure-174-v1/') and exe.endswith('/accel-sim.out'):
                fields=(p.parent/'stat').read_text().rsplit(')',1)[1].split()
                found.append(dict(pid=int(p.parent.name),start_ticks=fields[19],cpu_ticks=int(fields[11])+int(fields[12]),exe=exe))
        except (OSError,UnicodeError,IndexError): pass
    return found


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--registration',required=True);ap.add_argument('--output-dir',required=True)
    a=ap.parse_args(); registered=Path(a.registration).resolve(); authority=Path('/workspace/dtc-service-closure-174-v1/r2-attempts')
    guard=(authority/'CRITICAL_LAUNCH.lock').open('a');fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    status=json.loads((authority/'SCOPED_DISPATCH_STATUS.json').read_text());pid=status['coordinator_pid']
    inode=(authority/'SCOPED_DISPATCH.lock').stat().st_ino
    assert any(' FLOCK ' in line and f' WRITE {pid} ' in line and f':{inode} 0 EOF' in line for line in Path('/proc/locks').read_text().splitlines()),'Existing authority lock required'
    assert status['plan_sha256']==PLAN_SHA and not status['failed'];os.kill(pid,0)
    old_hold=authority/'HOLD_LAUNCHES'; assert sha(old_hold)==HOLD_SHA; original=old_hold.read_bytes()
    contract=json.loads((registered/'PAIRING_CONTRACT.json').read_text());plan=registered/'REGISTERED_DERIVED_ROWS.tsv'
    assert sha(plan)==contract['plan_sha256']
    rows=list(csv.DictReader(plan.open(),delimiter='\t'))
    assert {r['arm'] for r in rows}=={'B16-N','IO256','OO128','TRAD96','TC80-N'} and len(rows)==5
    root=registered/'attempts'; assert not list(root.glob('*/RUN_START.json')),'Reuse existing attempts; no duplicate launch'
    for row in rows:
        assert sha(Path(row['spec_path']))==row['spec_sha256']
        spec=json.loads(Path(row['spec_path']).read_text()); gate=json.loads(Path(spec['admission_receipt']).read_text())
        assert sha(Path(spec['admission_receipt']))==spec['admission_receipt_sha256'] and gate['status']=='DERIVED_INPUT_ADMITTED_FOR_SOURCE_PROFILE_SCOPE'
        assert spec['input_bundle_sha256']==gate['bundle_sha256'] and all(gate['checks'].values())
    for name,digest in contract['execution_sources'].items(): assert sha(registered/'execution_sources'/name)==digest
    # Retain and revalidate existing terminals, including scientific-pending rows.
    original_plan=Path(__file__).resolve().parents[2]/'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r2/REGISTERED_ROWS_V2.tsv'
    assert sha(original_plan)==PLAN_SHA
    current_labels={r['label'] for r in csv.DictReader(original_plan.open(),delimiter='\t')}
    terminal_rows=[collect(p.parent) for p in authority.glob('*/RUN_START.json')
                   if json.loads(p.read_text())['spec']['label'] in current_labels and (p.parent/'RUN_TERMINAL.json').exists()]
    assert all(r['status']=='PASS_CHECKED_SCOPE' for r in terminal_rows)
    live=simulators(); assert len(live)+5<=24
    mem=dict(line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())
    available=int(mem['MemAvailable'].split()[0])*1024
    assert available>=28*1024**3 # 4GiB per new Hotspot arm plus8GiB host headroom
    assert shutil.disk_usage(root).free>=24*512*1024**2
    out=Path(a.output_dir).resolve();out.mkdir(exist_ok=False)
    proof=dict(utc=datetime.now(timezone.utc).isoformat(),coordinator_pid=pid,coordinator_lock_inode=inode,
        original_plan_sha256=PLAN_SHA,original_hold_sha256=HOLD_SHA,derived_plan_sha256=sha(plan),
        live_before=live,original_terminal_strict_pass=len(terminal_rows),mem_available_bytes=available,
        incremental_reservation_bytes=20*1024**3,host_headroom_bytes=8*1024**3,disk_available_bytes=shutil.disk_usage(root).free,
        own_cap=24,new_rows=[r['label'] for r in rows],new_persistent_launcher=False,source_sha256=sha(Path(__file__)))
    save(out/'PREREGISTERED_SUBMISSION.json',proof);(out/'ORIGINAL_HOLD_LAUNCHES').write_bytes(original)
    temp=authority/'DERIVED_ADMISSION_HOLD.tmp';save(temp,dict(reason='SOLE174_BOUNDED_DERIVED_ADMISSION',pid=os.getpid(),receipt=str(out)))
    assert sha(old_hold)==HOLD_SHA;temp.replace(old_hold);temporary_sha=sha(old_hold)
    time.sleep(12)
    assert (authority/'SCOPED_DISPATCH_STATUS.json').stat().st_mtime>=old_hold.stat().st_mtime
    logs=root/'launcher_logs';logs.mkdir(exist_ok=True);launched=[]
    for row in rows:
        assert sha(old_hold)==temporary_sha and len(simulators())<24
        assert not any(json.loads(p.read_text())['spec']['label']==row['label'] for p in root.glob('*/RUN_START.json'))
        with (logs/(row['label']+'.log')).open('x') as f:
            proc=subprocess.Popen(['python3',str(registered/'execution_sources/run_hotspot_derived_174.py'),'--spec',row['spec_path'],'--root',str(root)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        while not any(json.loads(p.read_text())['spec']['label']==row['label'] for p in root.glob('*/RUN_START.json')):
            assert proc.poll() is None,'Runner preflight failed; preserve evidence and authority hold'
            time.sleep(1)
        launched.append(dict(label=row['label'],runner_pid=proc.pid));print(json.dumps(launched[-1]),flush=True)
    # Immutable start identities prove single submission, not a completion claim.
    starts=[json.loads(p.read_text()) for p in root.glob('*/RUN_START.json')]
    assert len(starts)==5 and {s['spec']['label'] for s in starts}=={r['label'] for r in rows}
    for before in live:
        p=Path('/proc')/str(before['pid'])/'stat'
        if p.exists():assert p.read_text().rsplit(')',1)[1].split()[19]==before['start_ticks']
        # A natural terminal while submitting is legal; never stop/restart it.
    save(out/'STARTED.json',dict(utc=datetime.now(timezone.utc).isoformat(),launched=launched,starts=starts,live_after=simulators(),signals_or_restarts=False))
    assert sha(old_hold)==temporary_sha;temp.write_bytes(original);assert sha(temp)==HOLD_SHA;temp.replace(old_hold)
    save(out/'AUTHORITY_RESTORED.json',dict(coordinator_pid=pid,hold_sha256=sha(old_hold),new_persistent_launcher=False,
        immediate_strict_validation='Each immutable per-attempt wrapper calls strict collector after natural terminal; no new scheduler.'))


if __name__=='__main__':main()
