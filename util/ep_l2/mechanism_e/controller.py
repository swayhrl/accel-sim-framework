"""One bounded event-driven E scheduler; no permanent empty resource watcher.

Run --once for readiness intake. Only a complete E-owned READY_QUEUE.json can
request real launches. No queue/no qualified release means no disk resurvey,
lease, simulator, or background child. Default 2 simultaneous applications.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import json
from pathlib import Path
import sys
import time

from coordinator import Coordinator,CAMPAIGN,AUTHORITY,START_DEADLINE,require,digest,run_key,write_json,tooling_binding
from runner import execute,accept_pair
import durable_exit
import capacity_policy


def roll_pairs(coord,requests):
    snapshot=coord.snapshot();by_key={r['run_key']:aid for aid,r in snapshot['accepted_results'].items()}
    pairs=[]
    for p in requests:
        if p['pair_id'] in snapshot['accepted_pairs']:continue
        if p['left_run_key'] in by_key and p['right_run_key'] in by_key:
            pairs.append(accept_pair(coord,by_key[p['left_run_key']],by_key[p['right_run_key']],p['pair_id'],p.get('mechanism','UNSPECIFIED')))
    return pairs


def step(coord,queue_path):
    tooling_binding();queue_path=Path(queue_path)
    with coord.unique_controller(),durable_exit.controller_signals():
        report={'campaign_id':CAMPAIGN,'authority_commit':AUTHORITY,'at_unix':time.time(),
                'applications_started_by_this_step':0,'outcomes':[],'pairs':[],'held_run_keys':[]}
        if not queue_path.exists():
            report.update(status='WAITING_EXACT_A_RELEASE_AND_D_INPUTS',background_process=False)
            write_json(coord.handoff/'CONTROLLER_STEP.json',report);return report
        raw=queue_path.read_bytes();queue=json.loads(raw)
        require(queue['campaign_id']==CAMPAIGN and queue['prepared_by']=='E','wrong dispatch authority')
        require(queue['authority_commit']==AUTHORITY,'wrong frozen contract')
        limits=capacity_policy.effective_limits(coord.snapshot())
        require(queue['input_and_profile_freeze_unix']<limits['start_deadline_unix'],'late condition freeze')
        pending=[];snapshot=coord.snapshot()
        for entry in queue['specs']:
            path=Path(entry['path']);require(digest(path)==entry['sha256'],'queued spec changed')
            spec=json.loads(path.read_text());key=run_key(spec['identity'])
            existing=[a for a in snapshot['attempts'] if a['run_key']==key]
            if existing and not spec.get('retry_previous_attempt'):continue
            if existing and existing[-1]['state'] in ('RESERVED','START_INTENT_UNRECONCILED','RUNNING','COMPLETE_VALID'):continue
            if 'qualification:'+spec['qualification_id'] in snapshot.get('scientific_holds',{}):
                report['held_run_keys'].append(key);continue
            pending.append(spec)
        report['pairs']+=roll_pairs(coord,queue.get('pairs',[]))
        target=snapshot.get('target_simulators',2);require(1<=target<=3,'invalid E simultaneous target')
        before=snapshot['actual_starts'];blocked=False
        with ThreadPoolExecutor(max_workers=target) as pool:
            running={}
            while pending or running:
                if durable_exit.STOP.is_set():blocked=True;pending.clear()
                while pending and len(running)<target and not blocked and time.time()<limits['start_deadline_unix']:
                    spec=pending.pop(0)
                    if 'qualification:'+spec['qualification_id'] in coord.snapshot().get('scientific_holds',{}):
                        report['held_run_keys'].append(run_key(spec['identity']))
                        report['outcomes'].append({'run_key':run_key(spec['identity']),'status':'NOT_RUN_SCIENTIFIC_REVIEW_HOLD'})
                        continue
                    running[pool.submit(execute,spec,coord)]=spec
                if not running:break
                done,_=wait(running,return_when=FIRST_COMPLETED)
                for future in done:
                    spec=running.pop(future)
                    try:
                        result=future.result();outcome={k:result[k] for k in ('attempt_id','run_key','status','detail')}
                        if result['status']=='COMPLETE_VALID':
                            write_json(coord.handoff/'events'/('E_ACCEPTED_POINT_'+result['attempt_id']+'.json'),result)
                            report['pairs']+=roll_pairs(coord,queue.get('pairs',[]))
                        elif result['status'] in ('RESOURCE_LIMIT','INCOMPLETE'):blocked=True
                    except Exception as error:
                        # No repeated admission retries in this controller step.
                        outcome={'run_key':run_key(spec['identity']),'status':'NOT_LAUNCHED_OR_NEEDS_RECONCILIATION',
                                 'detail':str(error)};blocked=True
                    report['outcomes'].append(outcome)
                if queue_path.read_bytes()!=raw:
                    blocked=True;report['queue_change_note']='Queue changed: admitted work drained, further admissions stopped; intake new revision explicitly.'
        after=coord.snapshot();report['applications_started_by_this_step']=after['actual_starts']-before
        report.update(status='BLOCKED_EVENT_REQUIRED' if blocked else ('SCOPED_HOLDS_PENDING' if report['held_run_keys'] else 'READY_QUEUE_DRAINED_OR_START_CUTOFF'),
           ledger_actual_starts=after['actual_starts'],ledger_remaining_start_capacity=after['remaining_start_capacity'],
           queue_remaining_count=len(pending),queue_sha256=digest(queue_path),background_process=False)
        write_json(coord.handoff/'CONTROLLER_STEP.json',report)
        return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--once',action='store_true',required=True)
    p.add_argument('--queue',type=Path);args=p.parse_args();coord=Coordinator()
    print(json.dumps(step(coord,args.queue or coord.handoff/'inbox/READY_QUEUE.json'),indent=2))

if __name__=='__main__':main()
