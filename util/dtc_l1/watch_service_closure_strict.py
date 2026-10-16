#!/usr/bin/env python3
"""Independent strict terminal review of the existing plan; never launches jobs."""
import argparse
import csv
import fcntl
import json
from pathlib import Path
import time
from collect_service_closure_attempts import collect, sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',required=True)
    ap.add_argument('--root',required=True)
    a=ap.parse_args()
    root=Path(a.root)
    lock=(root/'STRICT_REVIEW.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    with Path(a.plan).open() as f:
        labels={r['label'] for r in csv.DictReader(f,delimiter='\t')}
    output=root/'strict_reviews_v2';output.mkdir(exist_ok=True)
    seen=set()
    while True:
        for terminal in root.glob('*/RUN_TERMINAL.json'):
            if str(terminal) in seen:
                continue
            start=json.loads((terminal.parent/'RUN_START.json').read_text())
            if start['spec']['label'] not in labels:
                continue
            row=collect(terminal.parent)
            target=output/(row['attempt_uuid']+'.json')
            receipt=dict(collector_sha256=sha(Path(__file__).with_name('collect_service_closure_attempts.py')),
                plan_sha256=sha(Path(a.plan)),terminal_review=row)
            if target.exists():
                assert json.loads(target.read_text())==receipt
            else:
                with target.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
            if row['status']!='PASS_CHECKED_SCOPE':
                hold=root/'HOLD_LAUNCHES'
                if not hold.exists():
                    with hold.open('x') as f:
                        json.dump(dict(reason='STRICT_TERMINAL_FAILURE_REVIEW_REQUIRED',review=str(target)),f,indent=2)
                raise SystemExit('STRICT_FAILURE_PRESERVED '+str(target))
            seen.add(str(terminal))
            print(json.dumps(dict(label=row['label'],attempt_uuid=row['attempt_uuid'],status=row['status'])),flush=True)
        if len(seen)==len(labels):
            return
        time.sleep(10)


if __name__=='__main__':
    main()
