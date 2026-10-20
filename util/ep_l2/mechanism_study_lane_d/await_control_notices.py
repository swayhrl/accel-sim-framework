"""Bounded notification adapter for the two already-running E controls.

Only E's CURRENT_ACCEPTED declaration triggers the existing D projection CLI.
Own D lock/state/output only; no simulator, trace, E ledger/lease or git writes.
The calling Codex turn handles scientific interpretation and publication.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import sync_intake as intake

TARGETS=['V2_CONTROL_convolutionSeparable_F_VS_F_MINUS_R_MAIN61',
         'V2_CONTROL_convolutionSeparable_S_VS_S_COPY_FREE_MAIN61']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--state',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=7200)
    a=p.parse_args()
    if not 1<=a.seconds<=7200:raise ValueError('bounded observer maximum two hours')
    a.state.parent.mkdir(parents=True,exist_ok=True)
    with a.state.with_suffix('.lock').open('w') as owner:
        fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB)
        identity=dict(pid=os.getpid(),start_ticks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),
          boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
        deadline=time.monotonic()+a.seconds
        previous=json.loads((a.baseline/'CURRENT_E_PAIR_REFERENCES.json').read_text())
        observed={k:previous.get(k) for k in TARGETS};caches=[a.baseline];events=[]
        def record(state):
            a.state.write_text(json.dumps(dict(state=state,process=identity,deadline_utc=deadline_utc,
              observed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),interval_seconds=60,
              targets=TARGETS,events=events,Goal_restarted=False,E_mutations=0,application_starts=0),indent=2)+'\n')
        deadline_utc=dt.datetime.fromtimestamp(time.time()+a.seconds,dt.timezone.utc).isoformat()
        record('ACTIVE_BOUNDED_NOTICE_WAIT')
        print(json.dumps(dict(event='D_NOTICE_WAIT_STARTED',process=identity,deadline_utc=deadline_utc)),flush=True)
        while time.monotonic()<deadline:
            with (intake.SHARED/'REGISTRY.lock').open() as lock:
                fcntl.flock(lock,fcntl.LOCK_SH)
                ledger=json.loads((intake.SHARED/'RUN_REGISTRY.json').read_text())[intake.FIELD]
            current={k:ledger.get('accepted_pairs',{}).get(k) for k in TARGETS}
            changed=[k for k in TARGETS if current[k]!=observed[k]]
            if changed:
                # This is a notice check, not acceptance. The existing intake
                # independently refuses stale/mismatched/withdrawn endpoints.
                out=a.out/('accepted_event_'+str(time.time_ns()))
                cmd=[sys.executable,str(Path(__file__).with_name('control_incremental.py')),
                  '--plan',str(a.plan),'--out',str(out),'--render']
                for cache in caches:cmd+=['--cache',str(cache)]
                run=subprocess.run(cmd,capture_output=True,text=True)
                event=dict(changed=changed,output=str(out),returncode=run.returncode,
                  at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),stdout=run.stdout,stderr=run.stderr)
                events.append(event);record('EVENT_PROJECTED' if run.returncode==0 else 'D_PROJECTION_ENGINEERING_HOLD')
                print(json.dumps(event),flush=True)
                if run.returncode:sys.exit(run.returncode)
                caches.insert(0,out);observed=current
            if all(v and v.get('status')=='CURRENT_ACCEPTED' for v in current.values()):
                record('BOTH_E_TARGETS_CURRENT_ACCEPTED_PROJECTION_FINISHED');return
            time.sleep(min(60,max(0,deadline-time.monotonic())))
        record('BOUNDED_WAIT_EXPIRED_NO_EXECUTION_PERMISSION_INFERRED')
        print(json.dumps(dict(event='D_NOTICE_WAIT_EXPIRED',accepted_targets=[k for k,v in observed.items() if v and v.get('status')=='CURRENT_ACCEPTED'])),flush=True)

if __name__=='__main__':main()
