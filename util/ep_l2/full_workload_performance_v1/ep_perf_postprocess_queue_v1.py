"""Single finite operational postprocessor; never starts scientific models."""
import json, os, subprocess, sys, time
from ep_perf_common import *


def main():
    attempted=set()
    with locked(ROOT/'control/UNIFIED_POSTPROCESSOR.lock',True):
        while True:
            registry,unused=authority()
            q=registry['registered_future_requests'][GOAL]
            for case,row in q['consumed'].items():
                if not row.get('done_ref') or row['state'] in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED','PARSE_HOLD'] or case in attempted:
                    continue
                s=read(ROOT/'cases'/case/'control/FROZEN_SPEC.json')
                item=s['postprocess_module_ref']
                need(sha(item['path'])==item['sha256'],'postprocess module changed')
                output=ROOT/'control/postprocess_logs'
                output.mkdir(exist_ok=True)
                began=time.monotonic()
                with (output/(case+'.stdout')).open('ab') as out,(output/(case+'.stderr')).open('ab') as err:
                    result=subprocess.run(['/usr/bin/python3','-B',item['path'],case],cwd='/root/workspace',
                                          stdout=out,stderr=err,timeout=1800)
                attempted.add(case)
                put(ROOT/'control/postprocess_events'/(str(uuid.uuid4())+'.json'),dict(goal=GOAL,
                     cohort=case,returncode=result.returncode,seconds=time.monotonic()-began,
                     no_new_model_started=True,utc=now(),module_ref=item),True)
            registry,unused=authority()
            q=registry['registered_future_requests'][GOAL]
            if q['remaining']==0 and len(q['consumed'])==len(q['admitted_specs']) and all(
                row['state'] in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED','PARSE_HOLD'] or
                (case in attempted and row.get('done_ref')) for case,row in q['consumed'].items()):
                return dict(status='ALL_REGISTERED_MODELS_TERMINAL_POSTPROCESS_ATTEMPTS_COMPLETE',
                            parse_holds_require_offline_review=True,source_keep=True)
            time.sleep(10)


if __name__=='__main__':
    print(json.dumps(main()))
