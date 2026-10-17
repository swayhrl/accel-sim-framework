"""One finite serial authority: original DWT2D strict PASS before original BICG."""
import argparse
import fcntl
import signal
import time
from common import *
from wrapper_scope_v2 import resource_snapshot
from strict_collect import strict


def safety(snapshot, policy, baseline=None):
    limits=policy['admission']
    headroom=(snapshot['cgroup_memory_max']-snapshot['cgroup_memory_current']) if snapshot['cgroup_memory_max'] else snapshot['mem_available']
    checks=dict(host=snapshot['host']=='huangrulin-174',
        host_memory=snapshot['mem_available']>=limits['host_MemAvailable_min_gib']*1024**3,
        cgroup_headroom=headroom>=limits['cgroup_headroom_min_gib']*1024**3,
        disk=snapshot['disk_free']>=limits['disk_free_min_gib']*1024**3,
        memory_pressure=float(snapshot['pressure']['memory']['full']['avg10'])<=limits['memory_pressure_avg10_max'],
        io_pressure=float(snapshot['pressure']['io']['full']['avg10'])<=limits['io_pressure_avg10_max'],
        old_authorities_absent=not any(p['owners'] for p in snapshot['old_locks']))
    foreign=[]
    for p in snapshot['processes']:
        if p['pid']==os.getpid():continue
        if p['argv'] and p['argv'][0].startswith(str(ROOT/'attempts/binaries')+'/'):continue
        foreign.append(p)
    checks['no_unknown_or_foreign_dtc_authority']=not foreign
    prior=Path('/workspace/dtc-tag-pilot-174-v1')
    locks=Path('/proc/locks').read_text().splitlines()
    prior_owners=[]
    for name in ['AUTHORITY.lock','BACKGROUND_MONITOR.lock']:
        inode=(prior/name).stat().st_ino
        prior_owners += [line for line in locks if line.split()[5].split(':')[-1]==str(inode)]
    for name in ['AUTHORITY_ACTIVE_V2.json','BACKGROUND_MONITOR_ACTIVE_V1.json']:
        a=json.loads((prior/name).read_text());p=proc(a['pid'])
        if p and p['state']!='Z' and p['start_ticks']==a['start_ticks']:prior_owners.append(name)
    checks['completed_lane_t_remains_terminal']=not prior_owners
    if baseline:
        checks['no_new_swap_in_probe']=all(snapshot[k]==baseline[k] for k in ['pswpin','pswpout'])
        checks['no_new_oom_in_probe']=all(snapshot['cgroup_events'].get(k)==baseline['cgroup_events'].get(k) for k in ['oom','oom_kill'])
    return checks


def probe(policy):
    first=resource_snapshot();time.sleep(policy['admission']['probe_interval_seconds'])
    second=resource_snapshot();checks=safety(second,policy,first)
    return dict(utc=now(),first=first,second=second,checks=checks,
                status='PASS' if all(checks.values()) else 'WAIT_OR_STOP',max_parallel=1)


def verify():
    receipt=json.loads((ROOT/'PRE_REG_FETCH_BACK.json').read_text())
    assert receipt['status']=='PASS_FETCH_BACK_BEFORE_ANY_NEW_HOLDOUT_PERFORMANCE'
    assert receipt['plan_sha256']==sha(PACK/'PRE_REGISTRATION.tsv')
    for row in csv.DictReader((PACK/'PREREG_FILES_SHA256.tsv').open(),delimiter='\t'):
        p=PACK/row['path'];assert sha(p)==row['sha256']
        blob=subprocess.check_output(['git','-C',str(FW),'show',receipt['commit']+':'+str(p.relative_to(FW))])
        assert hashlib.sha256(blob).hexdigest()==row['sha256']
    source_check()
    return receipt


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    policy=json.loads((PACK/'POLICY.json').read_text())
    plan=list(csv.DictReader((PACK/'PRE_REGISTRATION.tsv').open(),delimiter='\t'))
    assert len(plan)==2 and [r['workload'] for r in plan]==['DWT2D','BICG']
    if not args.execute:
        result=probe(policy);write(ROOT/('RESOURCE_PREFLIGHT_'+str(time.time_ns())+'.json'),result)
        print(json.dumps(result),flush=True);return
    prereg=verify()
    lock=(ROOT/'AUTHORITY.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (ROOT/'AUTHORITY_ACTIVE.json').exists(), 'Inspect existing lineage; never create a second authority'
    assert not list((ROOT/'attempts').glob('*/RUN_START.json'))
    owner=proc(os.getpid())
    write(ROOT/'AUTHORITY_ACTIVE.json',dict(pid=os.getpid(),start_ticks=owner['start_ticks'],utc=now(),
        max_new_attempts=2,max_parallel=1,old_locks='READ_ONLY_NEVER_ACQUIRED',foreground=True))
    active=None;launched=[];finished={};halted=None;last_sample=0;strikes=0
    (ROOT/'attempts').mkdir(exist_ok=True);(ROOT/'launcher_logs').mkdir(exist_ok=True)
    def publish():
        value=dict(utc=now(),authority_pid=os.getpid(),launched=list(launched),
            active=[active[0]['label']] if active else [],terminal=dict(finished),halted=halted,
            not_launched=[p['label'] for p in plan if p['label'] not in launched])
        tmp=ROOT/'STATUS.tmp';tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(ROOT/'STATUS.json')
        return value
    try:
        while True:
            if active and active[1].poll() is not None:
                row,process,stream=active;stream.close();spec=json.loads(Path(row['spec_path']).read_text())
                run=ROOT/'attempts'/(row['label']+'_'+row['attempt_uuid'])
                try:
                    assert (run/'RUN_TERMINAL.json').exists(),'Runner exited without terminal'
                    result=strict(run,spec);write(ROOT/(row['attempt_uuid']+'.strict.json'),result)
                    finished[row['label']]=result['status']
                except Exception as exc:
                    finished[row['label']]='FAIL_PRESERVED_COLLECTOR_OR_RUNNER'
                    write(ROOT/(row['attempt_uuid']+'.strict_failure.json'),dict(utc=now(),error=repr(exc)))
                print('TERMINAL',row['label'],finished[row['label']],flush=True)
                if finished[row['label']]!='PASS_STRICT_HOLDOUT_SCOPE':halted='STRICT_OR_RUNNER_FAILURE_NO_RETRY'
                active=None
            if time.monotonic()-last_sample>=60:
                last_sample=time.monotonic();sample=resource_snapshot()
                with (ROOT/'RESOURCE_SAMPLES.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
                safe=safety(sample,policy)
                if not all(safe[k] for k in ['old_authorities_absent','no_unknown_or_foreign_dtc_authority','completed_lane_t_remains_terminal']):
                    halted='SCIENTIFIC_AUTHORITY_CONFLICT_STOP_FURTHER_LAUNCH'
                headroom=sample['cgroup_memory_max']-sample['cgroup_memory_current'] if sample['cgroup_memory_max'] else sample['mem_available']
                emergency=(headroom<policy['resource_stop']['cgroup_headroom_min_gib']*1024**3 or
                    sample['disk_free']<policy['resource_stop']['disk_free_min_gib']*1024**3 or
                    float(sample['pressure']['memory']['full']['avg10'])>policy['resource_stop']['memory_pressure_avg10_max'])
                strikes=strikes+1 if emergency else 0
                if strikes>=policy['resource_stop']['consecutive_samples']:
                    halted='RESOURCE_SAFETY_STOP_OWN_PROCESS_GROUP_ONLY'
                    if active:
                        row=active[0];pidfile=ROOT/'attempts'/(row['label']+'_'+row['attempt_uuid'])/'PID.json'
                        if pidfile.exists():
                            pid=json.loads(pidfile.read_text());current=proc(pid['process_pid'])
                            if current and current['start_ticks']==pid['process_start_ticks'] and str(ROOT) in ' '.join(current['argv']):
                                os.killpg(pid['process_pid'],signal.SIGTERM)
            if not active and not halted and len(launched)<2:
                row=plan[len(launched)]
                assert row['workload']=='DWT2D' or finished.get(plan[0]['label'])=='PASS_STRICT_HOLDOUT_SCOPE'
                admission=probe(policy)
                write(ROOT/('ADMISSION_PROBE_'+str(time.time_ns())+'.json'),admission)
                if all(admission['checks'].values()):
                    verify();assert sha(row['spec_path'])==row['spec_sha256']
                    assert not list((ROOT/'attempts').glob(row['label']+'_*'))
                    assert len(list((ROOT/'attempts').glob('*/RUN_START.json')))<2
                    if not (ROOT/'EXECUTION_GATE.json').exists():
                        write(ROOT/'EXECUTION_GATE.json',dict(status='PASS_FOR_PREREGISTERED_TWO_HOLDOUT_ONLY',
                            utc=now(),plan_sha256=sha(PACK/'PRE_REGISTRATION.tsv'),prereg_commit=prereg['commit'],
                            resource=admission,authority_pid=os.getpid(),authority_start_ticks=owner['start_ticks']))
                    stream=(ROOT/'launcher_logs'/(row['label']+'.log')).open('x')
                    process=subprocess.Popen(['python3','-B',str(PACK/'scripts/attempt.py'),'--spec',row['spec_path'],
                        '--root',str(ROOT/'attempts')],stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
                    active=(row,process,stream);launched.append(row['label'])
                    print('LAUNCHED',row['label'],'runner_pid='+str(process.pid),flush=True)
            status=publish()
            if not active and (len(finished)==2 or halted):break
            time.sleep(10)
        write(ROOT/'AUTHORITY_TERMINAL.json',dict(utc=now(),status='NATURAL_FOREGROUND_AUTHORITY_END',final=status,
            actual_new_starts=len(list((ROOT/'attempts').glob('*/RUN_START.json'))),max_parallel=1,
            no_new_candidates=True,no_t2=True))
    finally:lock.close()


if __name__=='__main__':main()
