"""One finite EP dispatcher. It cannot manufacture budgets or retry a consumed model."""
import os, pathlib, subprocess, sys, time
from ep_perf_common import *


def live_model_cpus():
    busy = set()
    for entry in P('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            argv = (entry/'cmdline').read_bytes().replace(b'\0',b' ')
            if b'accel-sim.out' in argv and b'/root/data/' in argv:
                busy.update(os.sched_getaffinity(int(entry.name)))
        except (OSError, ProcessLookupError):
            pass
    return busy


def state():
    return authority()[0]['registered_future_requests'][GOAL]


def claim(case, cpu, s):
    with locked(ROOT/'control/ADMISSION.lock'):
        q = state()
        need(case not in q['consumed'], 'already consumed; no retry')
        path = ROOT/'control/DISPATCH_CLAIMS.json'
        value = read(path)
        need(case not in value['claims'] and cpu not in {v['host_cpu'] for v in value['claims'].values() if v['state'] in ['CLAIMED','RUNNING']}, 'own claim/CPU conflict')
        need(cpu not in live_model_cpus(), 'CPU became occupied')
        binding_path = ROOT/'control/dispatch_bindings'/(case+'.json')
        if binding_path.exists():
            prior = read(binding_path)
            put(ROOT/'control/dispatch_binding_history'/case/(sha(binding_path)+'.json'), prior)
        binding = dict(cohort=case, spec_sha256=q['admitted_specs'][case], host_cpu=cpu,
                       selected_utc=now(), resolution='host-only dynamic CPU; scientific spec immutable')
        put(binding_path, binding)
        value['claims'][case] = dict(cohort=case, spec_sha256=q['admitted_specs'][case], host_cpu=cpu,
                                    estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],
                                    hard_RSS_bytes=s['limits']['RSS_bytes'], state='CLAIMED',
                                    remaining_write_bytes=s['limits']['result_bytes']+2*M, utc=now())
        put(path,value)
        # Published peer write guarantee: unmaterialized model output plus a single shared restore window.
        publish_own_write_carrier(value['claims'])
        return binding


def release_unused(case):
    with locked(ROOT/'control/ADMISSION.lock'):
        need(case not in state()['consumed'], 'consumed claim cannot be released as unused')
        path = ROOT/'control/DISPATCH_CLAIMS.json'
        value = read(path)
        value['claims'].pop(case,None)
        put(path,value)
        publish_own_write_carrier(value['claims'])


def status(workers, target, phase):
    q = state()
    counts = {}
    for row in q['consumed'].values():
        counts[row['state']] = counts.get(row['state'],0)+1
    value = dict(goal=GOAL, utc=now(), phase=phase, admitted=len(q['admitted_specs']),
                 consumed=len(q['consumed']), remaining=q['remaining'], terminal_counts=counts,
                 worker_pids={c:p.pid for c,p in workers.items()}, worker_target=target,
                 automatic_model_retry=False, source_keep=True)
    put(ROOT/'control/CURRENT_PROGRESS.json',value)
    return value


def main(stage_path):
    stage = read(stage_path)
    need(stage['goal'] == GOAL and stage['status'] == 'MAIN_REVIEWED_EXACT_FINITE_STAGE','finite reviewed stage')
    scope = [read(item['path'])['cohort'] for item in stage['specs']]
    specs = {c:read(ROOT/'cases'/c/'control/FROZEN_SPEC.json') for c in scope}
    for c in scope:
        need(c in state()['admitted_specs'],'not registered')
    target = 4
    workers = {}
    attempted_zero_start = {}
    began = time.monotonic()
    last_status = -60
    last_ramp = began
    with locked(ROOT/'control/UNIFIED_DISPATCHER.lock',True):
        while True:
            q = state()
            # Main may append another exact finite registered stage while this single dispatcher runs.
            for case in q['admitted_specs']:
                if case not in specs:
                    specs[case]=read(ROOT/'cases'/case/'control/FROZEN_SPEC.json')
                    scope.append(case)
            for case,p in list(workers.items()):
                if p.poll() is not None:
                    workers.pop(case)
                    if case not in state()['consumed']:
                        release_unused(case)
                        attempted_zero_start[case] = time.monotonic()
                        put(ROOT/'control/dispatch_events'/(str(uuid.uuid4())+'.json'),
                            dict(cohort=case,status='PRECONSUME_HOLD_ZERO_STARTS',returncode=p.returncode,utc=now()))
            pending = [c for c in scope if c not in q['consumed'] and c not in workers]
            pending.sort(key=lambda c:specs[c].get('estimated_wall_seconds',0),reverse=True)
            snapshots={}
            for case in pending:
                if len(workers) >= target:
                    break
                if time.monotonic() - attempted_zero_start.get(case,-1000) < 30:
                    continue
                s = specs[case]
                resources = module(s['resource_module_ref'],'ep_perf_dispatch_resources')
                resource_key=s['resource_module_ref']['sha256']
                snapshot=snapshots.get(resource_key)
                if snapshot is None or time.monotonic()-snapshot['monotonic']>2.5:
                    snapshot=resources.snapshot()
                    snapshots[resource_key]=snapshot
                claims = read(ROOT/'control/DISPATCH_CLAIMS.json')['claims']
                own_ram = sum(max(0,v['estimated_peak_RAM_bytes']-v.get('observed_RSS_bytes',0)) for v in claims.values() if v['state'] in ['CLAIMED','RUNNING'])
                own_writes = sum(v['remaining_write_bytes'] for v in claims.values())
                policy = exact(s['resource_policy_ref'])
                shared_window=max([specs[c]['limits']['result_bytes'] for c in claims if c in specs]+[s['limits']['result_bytes']])
                decision = resources.admit(snapshot,own_ram+s['estimated_peak_RAM_bytes'],own_writes+s['limits']['result_bytes']+shared_window+4*M,policy=policy)
                if not decision['pass_admission']:
                    put(ROOT/'control/LATEST_RESOURCE_HOLD.json',dict(utc=now(),cohort=case,decision=decision))
                    continue
                busy = live_model_cpus() | {v['host_cpu'] for v in claims.values() if v['state'] in ['CLAIMED','RUNNING']}
                # Any extra foreign claim CPU exclusions supplied by passive resource inventory are respected.
                busy.update(snapshot.get('reserved_cpu_ids',[]))
                candidates = sorted(set(os.sched_getaffinity(0))-busy)
                if not candidates:
                    continue
                cpu = candidates[0]
                claim(case,cpu,s)
                logroot = ROOT/'control/worker_logs'
                try:
                    logroot.mkdir(exist_ok=True)
                    with (logroot/(case+'.stdout')).open('ab') as out, (logroot/(case+'.stderr')).open('ab') as err:
                        workers[case] = subprocess.Popen([str(NATIVE/'bin/native'),'experiment','run-native',case,'--project','EP_L2'],
                                                        stdout=out,stderr=err,start_new_session=True)
                except Exception as exc:
                    if case not in state()['consumed']:
                        release_unused(case)
                        attempted_zero_start[case]=time.monotonic()
                    put(ROOT/'control/dispatch_events'/(str(uuid.uuid4())+'.json'),
                        dict(cohort=case,status='WORKER_CREATION_ENGINEERING_HOLD',
                             scientific_consumed=case in state()['consumed'],reason=repr(exc),utc=now()))
            if time.monotonic()-last_status >= 15:
                status(workers,target,'FINITE_REFERENCE_STAGE_RUNNING')
                last_status=time.monotonic()
            q = state()
            if all(c in q['consumed'] and q['consumed'][c].get('done_ref') for c in scope) and not workers:
                return status(workers,target,'ALL_STAGE_STARTS_TERMINAL_POSTPROCESS_PENDING')
            # Ramp requires measured nonpressure and enough qualified pending work, never an inherited cap2.
            if time.monotonic()-last_ramp > 180 and workers and len(pending)>target:
                s=next(iter(specs.values()))
                resources=module(s['resource_module_ref'],'ep_perf_ramp_resources')
                sample=resources.snapshot()
                if not resources.pressure(sample).get('pause_new_admission',True):
                    target=min(len(scope),target*2)
                last_ramp=time.monotonic()
            time.sleep(5)


if __name__ == '__main__':
    need(len(sys.argv)==2,'exact registered finite stage JSON required')
    print(json.dumps(main(sys.argv[1])))
