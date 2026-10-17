"""One finite foreground Lane T authority; no daemon, resubmission, or old queue writes."""
import argparse
import fcntl
import signal
import time
from common import *
from strict_collect import strict


def verify_preregistration():
    receipt=json.loads((ROOT/'PRE_REG_FETCH_BACK.json').read_text())
    assert receipt['status']=='PASS_FETCH_BACK_BEFORE_ANY_NEW_PERFORMANCE'
    assert receipt['plan_sha256']==sha(PACK/'PRE_REGISTRATION.tsv')
    with (PACK/'PREREG_FILES_SHA256.tsv').open() as f:
        for row in csv.DictReader(f,delimiter='\t'):
            path=PACK/row['path']
            assert sha(path)==row['sha256'],path
            committed=subprocess.check_output(['git','-C',str(FW),'show',
                receipt['commit']+':'+str(path.relative_to(FW))])
            assert hashlib.sha256(committed).hexdigest()==row['sha256']
    source_check()
    m=json.loads((ROOT/'M_CONSUMPTION.json').read_text())
    assert m['status']=='PASS_INPUT_AND_HYPOTHESIS_GATE'
    assert m['verified_remote_head']==git(FW,'rev-parse','origin/'+M_BRANCH)
    for file in m['files']:
        data=subprocess.check_output(['git','-C',str(FW),'show',m['verified_remote_head']+':'+file['path']])
        assert hashlib.sha256(data).hexdigest()==file['sha256']
    return receipt,m


def safety(snapshot, policy, baseline=None, admission=True):
    limits=policy['admission']
    headroom=(snapshot['cgroup_memory_max']-snapshot['cgroup_memory_current']) if snapshot['cgroup_memory_max'] else snapshot['mem_available']
    checks=dict(host=snapshot['host']=='huangrulin-174',
                mem_available=snapshot['mem_available']>=limits['host_MemAvailable_min_gib']*1024**3,
                cgroup_headroom=headroom>=limits['cgroup_headroom_min_gib']*1024**3,
                disk=snapshot['disk_free']>=limits['disk_free_min_gib']*1024**3,
                memory_pressure=float(snapshot['pressure']['memory']['full']['avg10'])<=limits['memory_pressure_avg10_max'],
                io_pressure=float(snapshot['pressure']['io']['full']['avg10'])<=limits['io_pressure_avg10_max'],
                old_authorities_absent=not any(x['owners'] for x in snapshot['old_locks']))
    foreign=[]
    for item in snapshot['processes']:
        if item['pid']==os.getpid():continue
        argv=item['argv']
        if argv and argv[0].endswith('accel-sim.out') and str(ROOT/'attempts/binaries') in argv[0]:continue
        foreign.append(item)
    checks['no_foreign_simulator_or_authority']=not foreign
    if baseline:
        checks['no_new_swap']=(snapshot['pswpin']==baseline['pswpin'] and snapshot['pswpout']==baseline['pswpout'])
        checks['no_new_oom']=(snapshot['cgroup_events'].get('oom_kill')==baseline['cgroup_events'].get('oom_kill'))
    return checks


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--execute',action='store_true')
    args=ap.parse_args()
    policy=json.loads((PACK/'POLICY.json').read_text())
    with (PACK/'PRE_REGISTRATION.tsv').open() as f:plan=list(csv.DictReader(f,delimiter='\t'))
    assert len(plan)==7
    specs={r['label']:json.loads(Path(r['spec_path']).read_text()) for r in plan}
    for row in plan:assert sha(row['spec_path'])==row['spec_sha256']
    first=resource_snapshot()
    time.sleep(policy['admission']['probe_interval_seconds'])
    second=resource_snapshot()
    checks=safety(second,policy,first)
    resource=dict(utc=now(),first=first,second=second,checks=checks,
                  status='PASS' if all(checks.values()) else 'HOLD',max_parallel=2)
    if not args.execute:
        target=ROOT/('RESOURCE_PREFLIGHT_'+str(time.time_ns())+'.json')
        write(target,resource)
        print(str(target),resource['status'],flush=True)
        return
    prereg,m=verify_preregistration()
    assert all(checks.values()),json.dumps(resource)
    lock=(ROOT/'AUTHORITY.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (ROOT/'AUTHORITY_ACTIVE.json').exists(),'Prior authority evidence exists: inspect; do not resume automatically'
    owner=proc(os.getpid())
    write(ROOT/'AUTHORITY_ACTIVE.json',dict(pid=os.getpid(),start_ticks=owner['start_ticks'],
          utc=now(),plan_sha256=sha(PACK/'PRE_REGISTRATION.tsv'),foreground=True,
          max_attempts=7,max_parallel=2,old_locks='READ_ONLY_NEVER_ACQUIRED'))
    write(ROOT/'EXECUTION_GATE.json',dict(status='PASS_FOR_PREREGISTERED_SEVEN_ONLY',utc=now(),
          plan_sha256=sha(PACK/'PRE_REGISTRATION.tsv'),prereg_commit=prereg['commit'],
          lane_m_commit=m['verified_remote_head'],lane_m_receipt_sha256=sha(ROOT/'M_CONSUMPTION.json'),
          authority_pid=os.getpid(),authority_start_ticks=owner['start_ticks'],resource=resource))
    root=ROOT/'attempts'
    root.mkdir(exist_ok=True)
    logs=ROOT/'launcher_logs'
    logs.mkdir(exist_ok=True)
    active={}
    finished={}
    launched=set()
    halted=None
    last_sample=0
    pressure_strikes=0
    try:
        while True:
            for label,(process,stream,row) in list(active.items()):
                if process.poll() is None:continue
                stream.close()
                spec=specs[label]
                run=root/(label+'_'+spec['attempt_uuid'])
                if (run/'RUN_TERMINAL.json').exists():
                    try:
                        result=strict(run,spec)
                        write(ROOT/(spec['attempt_uuid']+'.strict.json'),result)
                        finished[label]=result['status']
                    except Exception as exc:
                        write(ROOT/(spec['attempt_uuid']+'.strict_failure.json'),dict(utc=now(),error=repr(exc),status='FAIL_PRESERVED'))
                        finished[label]='FAIL_PRESERVED_COLLECTOR_EXCEPTION'
                else:
                    finished[label]='FAIL_PRESERVED_RUNNER_NO_TERMINAL'
                if not finished[label].startswith('PASS_'):
                    halted='STRICT_OR_RUNNER_FAILURE_HOLD_NO_RETRY'
                print('TERMINAL',label,finished[label],flush=True)
                del active[label]
            if time.monotonic()-last_sample>=60:
                last_sample=time.monotonic()
                sample=resource_snapshot()
                with (ROOT/'RESOURCE_SAMPLES.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
                live=safety(sample,policy)
                if not live['old_authorities_absent'] or not live['no_foreign_simulator_or_authority']:
                    halted='AUTHORITY_CONFLICT_HOLD_NO_FURTHER_LAUNCH'
                headroom=sample['cgroup_memory_max']-sample['cgroup_memory_current'] if sample['cgroup_memory_max'] else sample['mem_available']
                emergency=(headroom<policy['resource_stop']['cgroup_headroom_min_gib']*1024**3 or
                           sample['disk_free']<policy['resource_stop']['disk_free_min_gib']*1024**3 or
                           float(sample['pressure']['memory']['full']['avg10'])>policy['resource_stop']['memory_pressure_avg10_max'])
                pressure_strikes=pressure_strikes+1 if emergency else 0
                if pressure_strikes>=policy['resource_stop']['consecutive_samples']:
                    halted='RESOURCE_SAFETY_STOP_OWN_ATTEMPTS_ONLY'
                    for label in active:
                        spec=specs[label]
                        path=root/(label+'_'+spec['attempt_uuid'])/'PID.json'
                        if path.exists():
                            pid=json.loads(path.read_text())['process_pid']
                            # /usr/bin/time process is a session leader created
                            # by our runner; its whole group contains only this attempt.
                            current=proc(pid)
                            if current and str(root) in ' '.join(current['argv']):
                                os.killpg(pid,signal.SIGTERM)
            while not halted and len(active)<policy['max_parallel']:
                row=next((r for r in plan if r['label'] not in launched),None)
                if row is None:break
                live=resource_snapshot()
                admission=safety(live,policy)
                if not all(admission.values()):break
                label=row['label']
                assert not list(root.glob(label+'_*')),'Attempt already present; no resubmission'
                assert sha(row['spec_path'])==row['spec_sha256']
                stream=(logs/(label+'.log')).open('x')
                process=subprocess.Popen(['python3',str(PACK/'scripts/attempt.py'),
                    '--spec',row['spec_path'],'--root',str(root)],stdout=stream,stderr=subprocess.STDOUT,
                    start_new_session=True)
                active[label]=(process,stream,row)
                launched.add(label)
                print('LAUNCHED',label,'runner_pid='+str(process.pid),flush=True)
            status=dict(utc=now(),authority_pid=os.getpid(),launched=sorted(launched),
                        active=sorted(active),terminal=finished,halted=halted,
                        not_launched=[r['label'] for r in plan if r['label'] not in launched])
            temp=ROOT/'STATUS.tmp'
            temp.write_text(json.dumps(status,indent=2)+'\n')
            temp.replace(ROOT/'STATUS.json')
            if not active and (len(launched)==7 or halted):break
            time.sleep(10)
        write(ROOT/'AUTHORITY_TERMINAL.json',dict(utc=now(),status='NATURAL_FOREGROUND_AUTHORITY_END',
              final=status,holdout_launched=False,t2_launched=False))
    finally:
        lock.close()


if __name__=='__main__':
    main()
