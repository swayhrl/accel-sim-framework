"""Original bounded E scheduler: approved resource-only formal concurrency.

No second controller, background resource watcher or executor-count contract.
Legacy scheduling keeps its original finite target when no exact amendment.
"""
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import json
from pathlib import Path
import socket
import sys
import time

from coordinator import (Coordinator,CAMPAIGN,AUTHORITY,require,digest,run_key,write_json,tooling_binding,
 resource_gate,local_resources,output_usage,FIELD,OUTPUT,FULL_GROWTH,GIB)
from runner import execute,accept_pair
import capacity_policy
import limits_policy
import concurrency_policy
import durable_exit
import detach_diagnostic_policy as detach_policy


def roll_pairs(coord,requests):
    snapshot=coord.snapshot();by_key={r['run_key']:aid for aid,r in snapshot['accepted_results'].items()}
    pairs=[]
    for p in requests:
        if p['pair_id'] in snapshot['accepted_pairs']:continue
        if p['left_run_key'] in by_key and p['right_run_key'] in by_key:
            pairs.append(accept_pair(coord,by_key[p['left_run_key']],by_key[p['right_run_key']],p['pair_id'],p.get('mechanism','UNSPECIFIED')))
    return pairs


def submitted_reservation_view(data,running):
    """Pure forecast only: cover submitted hashing work not yet in registry.

    Real RESERVED/RUNNING rows already count. Completed futures need no virtual
    reserve and must be processed before any further dispatch. No shadow record
    is persisted, granted a lease or charged as an application start.
    """
    view=copy.deepcopy(data);virtual=[]
    for future,spec in running.items():
        if future.done():continue
        key=run_key(spec['identity']);actual=view['runs'].get(key)
        if actual and actual['status'] in ('RESERVED','RUNNING'):continue
        vkey='READONLY_SUBMITTED_FORECAST_'+key
        view['runs'][vkey]=dict(run_key=vkey,status='RESERVED',host=socket.gethostname(),
          experiment_id=CAMPAIGN,owner='E_READONLY_FORECAST_NOT_LEASE',cpu_units=1,
          memory_bytes=spec.get('memory_bytes',8*GIB),disk_growth_bytes=spec.get('maximum_result_bytes',FULL_GROWTH),
          monitor_reserve_bytes=2*GIB,result_directory=str(OUTPUT/vkey),
          scan=spec['identity']['workload']=='scan',process=None)
        virtual.append(key)
    return view,virtual


def forecast(coord,spec,running):
    """Read-only resource forecast; original transactional admission is final."""
    data=json.loads((coord.registry.root/'RUN_REGISTRY.json').read_text())
    view,virtual=submitted_reservation_view(data,running)
    resources=local_resources();usage=output_usage()
    result=dict(at_unix=time.time(),run_key=run_key(spec['identity']),
      virtual_submitted_run_keys=virtual,read_only=True,resources=resources,output_usage=usage)
    try:
        resource_gate(view,'simulation',1,spec.get('memory_bytes',8*GIB),
                      spec.get('maximum_result_bytes',FULL_GROWTH),resources,usage,
                      spec['identity']['workload']=='scan',
                      **({'authority_data':data,'read_only_forecast':True} if detach_policy.successor.has(data[FIELD]) else {}))
        result.update(fits=True,reason='Original resource gate fits including submitted-not-reserved work')
    except ValueError as error:
        result.update(fits=False,reason=str(error))
    return result


def deferred_prelaunch_resource(coord,spec,error,running):
    """Only an unreserved, uncharged exact resource-gate race may be deferred.

    A science/identity error is not converted into a resource wait. An attempt
    already recorded (even cancelled-before-start) retains original retry rules.
    """
    snapshot=coord.snapshot();key=run_key(spec['identity'])
    if any(a['run_key']==key for a in snapshot['attempts']):return None
    observation=forecast(coord,spec,running)
    if not observation['fits'] and observation['reason']==str(error):return observation
    return None


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
        require(limits['start_deadline_unix'] is None or
                queue['input_and_profile_freeze_unix']<limits['start_deadline_unix'],'late condition freeze')
        pending=[];snapshot=coord.snapshot()
        detach_policy.queue_guard(snapshot,queue,digest)
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
        resource_only=concurrency_policy.resource_only(snapshot,'simulation')
        if resource_only:
            # This is finite queue storage capacity, NOT a formal simulator cap.
            target=max(1,len(pending));report['concurrency_mode']='RESOURCE_ONLY'
            report['finite_pending_executor_capacity']=len(pending)
            report['resource_waits']=[];report['resource_admissions']=[]
        else:
            target=snapshot.get('target_simulators',2);require(1<=target<=3,'invalid E simultaneous target')
            report['concurrency_mode']='LEGACY_FINITE_TARGET'
        before=snapshot['actual_starts'];blocked=False;resource_stop=False
        with ThreadPoolExecutor(max_workers=target) as pool:
            running={}
            while pending or running:
                if durable_exit.STOP.is_set():
                    blocked=True
                    if not resource_only:pending.clear()
                if resource_only and queue_path.read_bytes()!=raw:
                    blocked=True;report['queue_change_note']='Queue changed: admitted work drains; no new admissions until explicit revision intake.'
                while pending and len(running)<target and not blocked and limits_policy.deadline_open(limits['start_deadline_unix']):
                    # Process actual terminal outcomes before spending released
                    # resources, so a capacity FAILED blocks further admissions.
                    if resource_only and any(f.done() for f in running):break
                    spec=pending[0]
                    if 'qualification:'+spec['qualification_id'] in coord.snapshot().get('scientific_holds',{}):
                        pending.pop(0);report['held_run_keys'].append(run_key(spec['identity']))
                        report['outcomes'].append({'run_key':run_key(spec['identity']),'status':'NOT_RUN_SCIENTIFIC_REVIEW_HOLD'})
                        continue
                    if resource_only:
                        admission=forecast(coord,spec,running)
                        if not admission['fits']:
                            admission['action']='WAIT_OWN_FUTURE_COMPLETION' if running else 'LEGAL_STOP_NO_OWN_FUTURE'
                            report['resource_waits'].append(admission)
                            resource_stop=not bool(running)
                            break
                        if any(f.done() for f in running):break
                        report['resource_admissions'].append(admission)
                    pending.pop(0)
                    running[pool.submit(execute,spec,coord)]=spec
                if not running:break
                # No periodic external-state polling: completion of existing
                # real work is the only resource-reforecast event in this loop.
                done,_=wait(running,return_when=FIRST_COMPLETED)
                for future in done:
                    spec=running.pop(future)
                    try:
                        result=future.result();outcome={k:result[k] for k in ('attempt_id','run_key','status','detail')}
                        if result['status']=='COMPLETE_VALID':
                            write_json(coord.handoff/'events'/('E_ACCEPTED_POINT_'+result['attempt_id']+'.json'),result)
                            report['pairs']+=roll_pairs(coord,queue.get('pairs',[]))
                        elif result['status'] in ('RESOURCE_LIMIT','INCOMPLETE'):blocked=True
                        elif result['status']=='FAILED' and capacity_policy.is_capacity_spec(spec):blocked=True
                    except Exception as error:
                        deferral=deferred_prelaunch_resource(coord,spec,error,running) if resource_only else None
                        if deferral is not None:
                            pending.insert(0,spec);deferral['action']='UNRESERVED_UNCHARGED_RESOURCE_RACE_DEFERRED'
                            report['resource_waits'].append(deferral)
                            outcome={'run_key':run_key(spec['identity']),'status':'NOT_LAUNCHED_RESOURCE_DEFERRED',
                                     'detail':str(error),'actual_start_charged':False}
                        else:
                            outcome={'run_key':run_key(spec['identity']),'status':'NOT_LAUNCHED_OR_NEEDS_RECONCILIATION',
                                     'detail':str(error)};blocked=True
                    report['outcomes'].append(outcome)
                if queue_path.read_bytes()!=raw:
                    blocked=True;report['queue_change_note']='Queue changed: admitted work drained, further admissions stopped; intake new revision explicitly.'
        after=coord.snapshot();report['applications_started_by_this_step']=after['actual_starts']-before
        report.update(status='BLOCKED_EVENT_REQUIRED' if blocked else ('RESOURCE_ADMISSION_STOP_NO_OWN_FUTURE' if resource_stop else ('SCOPED_HOLDS_PENDING' if report['held_run_keys'] else 'READY_QUEUE_DRAINED_OR_START_CUTOFF')),
           ledger_actual_starts=after['actual_starts'],ledger_remaining_start_capacity=after['remaining_start_capacity'],
           queue_remaining_count=len(pending),pending_run_keys=[run_key(spec['identity']) for spec in pending],
           queue_sha256=digest(queue_path),background_process=False)
        write_json(coord.handoff/'CONTROLLER_STEP.json',report)
        return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--once',action='store_true',required=True)
    p.add_argument('--queue',type=Path);args=p.parse_args();coord=Coordinator()
    print(json.dumps(step(coord,args.queue or coord.handoff/'inbox/READY_QUEUE.json'),indent=2))

if __name__=='__main__':main()
