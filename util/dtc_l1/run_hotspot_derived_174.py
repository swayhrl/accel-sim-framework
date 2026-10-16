#!/usr/bin/env python3
"""One immutable runner plus immediate strict review; no retries or scheduling."""
import json
from pathlib import Path
import sys
import service_closure_attempt
from collect_hotspot_derived_174 import review


def main():
    # Delegate launch/locking/content-addressed binary freezing unchanged.
    args=sys.argv[1:]; specpath=Path(args[args.index('--spec')+1]); root=Path(args[args.index('--root')+1])
    spec=json.loads(specpath.read_text()); error=None
    try:
        service_closure_attempt.main()
    except BaseException as exc:
        error=exc
    candidates=[p.parent for p in root.glob('*/RUN_START.json')
                if json.loads(p.read_text())['spec']==spec]
    if len(candidates)==1 and (candidates[0]/'RUN_TERMINAL.json').exists():
        result=review(candidates[0]); target=candidates[0]/'DERIVED_STRICT_VALIDATION_V1.json'
        with target.open('x') as f: json.dump(result,f,indent=2); f.write('\n')
        print(json.dumps(result),flush=True)
        if result['terminal_review']['status']!='PASS_CHECKED_SCOPE':
            raise SystemExit('STRICT_FAILURE_PRESERVED '+str(target))
    if error is not None: raise error


if __name__=='__main__': main()
