#!/usr/bin/env python3
"""Immutable review checkpoint from raw receipts; no runs, retries or averages."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
from collect_service_closure_attempts import collect, sha


def table(path,rows):
    with path.open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--task-root',required=True)
    ap.add_argument('--evidence-root',required=True)
    ap.add_argument('--output-dir',required=True)
    a=ap.parse_args()
    root=Path(a.task_root);evidence=Path(a.evidence_root);out=Path(a.output_dir)
    out.mkdir(parents=True,exist_ok=False)
    plan=list(csv.DictReader((evidence/'review_pack/r2/REGISTERED_ROWS_V2.tsv').open(),delimiter='\t'))
    labels={r['label'] for r in plan}
    attempts=[];raw_hashes=[];reviewed={}
    for name in ['r1-attempts','r2-attempts','modern-baseline-attempts','spmv-admission-attempts']:
        for p in sorted((root/name).glob('*/RUN_START.json')):
            row=collect(p.parent)
            row['current_registered_r2']=row['label'] in labels
            row['performance_disposition']=('CURRENT_REGISTERED_R2' if row['label'] in labels else
                'MODERN_BASELINE_ONLY' if row['label'].startswith('B0_') else
                'QUALIFICATION_OR_SUPERSEDED_NOT_CURRENT_R2_PERFORMANCE')
            attempts.append(row)
            if row['current_registered_r2']:
                reviewed[row['label']]=row
            for f in [p,p.parent/'SPEC.json',p.parent/'PID.json',p.parent/'RUN_TERMINAL.json',
                      p.parent/'VALIDATION.json',p.parent/'TERMINAL_RECOVERY_V1.json']:
                if f.exists():
                    raw_hashes.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f)))
            # Running logs are mutable and deliberately receive no sealed hash.
            if row['status']!='RUNNING':
                for f in [p.parent/'simulator.stdout',p.parent/'simulator.stderr',p.parent/'resource.time']:
                    raw_hashes.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f)))
    table(out/'ALL_ATTEMPTS.tsv',attempts)
    table(out/'RAW_RECEIPT_HASHES.tsv',raw_hashes)
    states=[]
    for p in plan:
        r=reviewed.get(p['label'],{})
        states.append(dict(label=p['label'],workload=p['workload'],arm=p['arm'],phase=p['phase'],
            spec_sha256=p['spec_sha256'],status=r.get('status','REGISTERED_NOT_LAUNCHED'),
            attempt_uuid=r.get('attempt_uuid',''),cycles=r.get('cycles',''),instructions=r.get('instructions',''),
            core=r.get('core',''),binary_sha256=r.get('binary_sha256',''),
            stdout_sha256=r.get('stdout_sha256',''),terminal_sha256=r.get('terminal_sha256',''),
            raw_dir=r.get('run_dir',''),scientific_checks=r.get('scientific_checks','NOT_EXECUTED'),
            service_metrics=r.get('service_metrics','UNAVAILABLE')))
    table(out/'REGISTERED_R2_STATE.tsv',states)
    baselines=list(csv.DictReader((evidence/'review_pack/r2/CANONICAL_BASELINE_REUSE.tsv').open(),delimiter='\t'))
    pairs=[]
    for r in states:
        if r['status']!='PASS_CHECKED_SCOPE':
            continue
        matching = list(baselines)
        if r['arm'] in ['IO','OO','IO128']:
            matching += [dict(workload=b['workload'],variant='TRAD96-P256-M512',
                             instructions=b['instructions'],attempt_uuid=b['attempt_uuid'],
                             core=b['core'],binary_sha256=b['binary_sha256'],cycles=b['cycles'])
                         for b in states if b['workload']==r['workload'] and
                         b['arm']=='TRAD96' and b['status']=='PASS_CHECKED_SCOPE']
        for b in matching:
            if b['workload']==r['workload']:
                assert b['instructions']==r['instructions']
                pairs.append(dict(workload=r['workload'],arm=r['arm'],comparison_baseline=b['variant'],
                    new_attempt_uuid=r['attempt_uuid'],new_core=r['core'],new_binary_sha256=r['binary_sha256'],
                    new_cycles=r['cycles'],baseline_attempt_uuid=b['attempt_uuid'],baseline_core=b['core'],
                    baseline_binary_sha256=b['binary_sha256'],baseline_cycles=b['cycles'],
                    baseline_cycles_over_new_cycles=float(b['cycles'])/float(r['cycles']),
                    scope='ONE_COMPLETE_FROZEN_WORKLOAD_NOT_GM12_OR_NATIVE_DTC_SPEEDUP'))
    if pairs:table(out/'COMPLETED_ROW_PAIRS.tsv',pairs)
    for file in [root/'producer109-890fb0be/CONSUMER_ARCHIVE_VERIFICATION_V2.json',
                 root/'producer109-890fb0be/AUDIT_A1_FAILURE_PRESERVED.json',
                 root/'r2-attempts/DISPATCH_STATUS.json']:
        shutil.copy2(file,out/file.name)
    summary=dict(snapshot_utc=datetime.now(timezone.utc).isoformat(),
        plan_sha256=sha(evidence/'review_pack/r2/REGISTERED_ROWS_V2.tsv'),
        registered_rows=len(states),
        r2_states={s:sum(r['status']==s for r in states) for s in sorted({r['status'] for r in states})},
        native_cases_reused=15,native_reruns=0,
        modern_dtc='HOLD_CAPACITY_AND_PORT_ORGANIZATION_REVIEW',
        spmv_simulator='NOT_ADMITTED_SM89_DISPATCH',layernorm_simulator='NOT_ADMITTED_SM86_SKIPPED_CALL',
        main_goal='ACTIVE_REGISTERED_ROWS_ROLLING_NOT_COMPLETE',averages='NONE')
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    subprocess.run([sys.executable,str(Path(__file__).with_name('collect_service_closure_modern.py')),
                    '--root',str(root/'modern-baseline-attempts'),
                    '--output',str(out/'MODERN_BASELINE_ONLY.tsv')],check=True)
    # Hash derived outputs last; this manifest intentionally excludes itself.
    table(out/'FILES_SHA256.tsv',[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir()) if p.is_file()])
    print(json.dumps(summary))


if __name__=='__main__':
    main()
