#!/usr/bin/env python3
"""Read-only all-project /proc, cgroup and fdinfo FLOCK audit. No lock/signal APIs."""
from common import *
from resource_policy import admission_checks
import re
import shutil
import socket
import time
import argparse

PAGE=os.sysconf('SC_PAGE_SIZE')
AA5_PIDS={3507265:904463811,3507648:904464900}
OLD_DISPATCHER={1425986:584741606}


def proc(pid):
    q=Path('/proc')/str(pid)
    try:
        raw=(q/'stat').read_text().rsplit(')',1)[1].split()
        args=[x.decode(errors='replace') for x in (q/'cmdline').read_bytes().split(b'\0') if x]
        d=dict(pid=int(pid),state=raw[0],ppid=int(raw[1]),start_ticks=int(raw[19]),
            rss_bytes=int(raw[21])*PAGE,utime_ticks=int(raw[11]),stime_ticks=int(raw[12]),
            minflt=int(raw[7]),majflt=int(raw[9]),comm=(q/'comm').read_text().strip(),
            cgroup=(q/'cgroup').read_text().strip())
        try:d['exe']=os.readlink(q/'exe');d['cwd']=os.readlink(q/'cwd')
        except OSError:d['exe']=d['cwd']='UNAVAILABLE'
        try:d['io']={k:int(v) for k,v in (l.split(':') for l in (q/'io').read_text().splitlines())}
        except OSError:d['io']='UNAVAILABLE'
        vm=re.search(r'^VmSwap:\s+(\d+)',(q/'status').read_text(),re.M)
        d['VmSwap_bytes']=int(vm.group(1))*1024 if vm else 0
        command=' '.join(args)
        relevant=any(k in command.lower() for k in ['dtc','fast64','accel-sim'])
        if relevant:d['argv']=args
        d['dtc_or_fast64_command']=relevant
        d['is_simulator']=Path(d['exe']).name=='accel-sim.out' or d['comm']=='accel-sim.out'
        return d
    except (OSError,ValueError,IndexError):
        return None


def snapshot():
    assert Path('/proc/self/cgroup').read_text().strip()=='0::/', 'Unreviewed cgroup mapping'
    cg=Path('/sys/fs/cgroup')
    names=['memory.current','memory.max','memory.swap.current','memory.swap.max','memory.events',
           'memory.pressure','io.pressure','io.stat','cpu.pressure','cpu.max']
    cgroup={n:(cg/n).read_text().strip() for n in names}
    cgroup['events']={k:int(v) for k,v in (l.split() for l in cgroup['memory.events'].splitlines())}
    processes=[r for p in Path('/proc').glob('[0-9]*') if (r:=proc(p.name)) and r['state']!='Z']
    locks=[]
    races=0
    for p in processes:
        for f in (Path('/proc')/str(p['pid'])/'fdinfo').glob('*'):
            try:
                text=f.read_text()
                if 'FLOCK' in text:
                    target=os.readlink(f.parent.parent/'fd'/f.name)
                    current=proc(p['pid'])
                    if not current or current['start_ticks']!=p['start_ticks']:
                        races+=1;continue
                    locks.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],fd=f.name,path=target,fdinfo=text))
            except OSError:races+=1
    pressure={k:{line.split()[0]:dict(v.split('=') for v in line.split()[1:])
                 for line in Path('/proc/pressure',k).read_text().splitlines()} for k in ['memory','io','cpu']}
    mem={k:int(v.split()[0])*1024 for k,v in (l.split(':',1) for l in Path('/proc/meminfo').read_text().splitlines())}
    vm=dict(l.split() for l in Path('/proc/vmstat').read_text().splitlines())
    identities=[]
    for role,pins in [('AA5',AA5_PIDS),('OLD_AUTODISPATCHER',OLD_DISPATCHER)]:
        for pid,ticks in pins.items():
            current=next((p for p in processes if p['pid']==pid),None)
            identities.append(dict(role=role,pid=pid,expected_start_ticks=ticks,current=current,
                same_instance_live=bool(current and current['start_ticks']==ticks)))
    return dict(utc=now(),monotonic_ns=time.monotonic_ns(),host=socket.gethostname(),uid=os.getuid(),
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        cgroup_membership=Path('/proc/self/cgroup').read_text(),cgroup=cgroup,pressure=pressure,
        host_MemAvailable_bytes=mem['MemAvailable'],disk_free_bytes=shutil.disk_usage(RAW).free,
        pswpin=int(vm['pswpin']),pswpout=int(vm['pswpout']),affinity=sorted(os.sched_getaffinity(0)),
        loadavg=Path('/proc/loadavg').read_text().strip(),processes=processes,
        all_process_RSS_sum_bytes=sum(p['rss_bytes'] for p in processes),
        RSS_scope='ALL_VISIBLE_PROJECTS_RSS_SUM_MAY_DOUBLE_COUNT_SHARED_PAGES',
        FLOCKs=locks,fdinfo_races=races,proc_locks_supplemental=Path('/proc/locks').read_text(),
        diskstats=Path('/proc/diskstats').read_text(),known_identity_checks=identities)


def classify_authority(s):
    rows=[]
    unresolved=[]
    for p in s['processes']:
        if not p['dtc_or_fast64_command']:
            continue
        command=' '.join(p.get('argv',[]))
        if p['is_simulator']:
            role='LIVE_SIMULATOR_REQUIRES_PROJECT_CLASSIFICATION'
        elif 'audit_site.py' in command and '/dtc-lane-ag-' not in command:
            role='OWN_CPU_AUDIT'
        elif 'monitor_fast64_3_dynamic_base_evidence_v1.py' in command:
            role='OLD_OUTPUT_MONITOR_REQUIRES_SOURCE_HASH_REVIEW'
        elif 'fast64-3-core41-candidate-closeout' in command:
            role='OLD_OUTPUT_COLLECTOR_REQUIRES_CALLEE_REVIEW'
        elif any(k in command for k in ['auto_dispatch','dispatch_fast64','run_matrix.py','service_closure_attempt.py']):
            role='POTENTIAL_DTC_DISPATCH_AUTHORITY_STOP'
            unresolved.append(p['pid'])
        else:
            role='DTC_RELATED_REVIEW_REQUIRED'
        rows.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],role=role,argv=p.get('argv',[]),exe=p['exe']))
    return dict(classification='READONLY_REVIEW_NOT_AUTHORITY_ACQUISITION',rows=rows,
        unresolved_dispatcher_pids=unresolved,all_FLOCKs=s['FLOCKs'],known_identity_checks=s['known_identity_checks'],
        foreign_signals_or_lock_changes=0,performance_launch_permission=False)


def main(label):
    dest=RAW/'site-audits'/label
    dest.mkdir(parents=True,exist_ok=False)
    first=snapshot();write(dest/'FIRST.json',first)
    time.sleep(10.1)
    second=snapshot();write(dest/'SECOND.json',second)
    checks=admission_checks(first,second)
    result=dict(utc=now(),checks=checks,all_resource_checks_pass=all(checks.values()),
        host_global_swap_deltas={k:second[k]-first[k] for k in ['pswpin','pswpout']},
        host_global_swap_is_not_process_attribution=True,actual_AG_sim_starts=0,
        source='CURRENT_ALL_PROJECTS_TWO_SAMPLES_GE10S',authority=classify_authority(second))
    write(dest/'AUDIT.json',result)
    write(PACK/'CURRENT_SITE_AUDIT.json',dict(**result,raw_audit_path=str(dest),
        resource=dict(first_memory=first['host_MemAvailable_bytes'],second_memory=second['host_MemAvailable_bytes'],
            first_io_full=first['pressure']['io']['full']['avg10'],second_io_full=second['pressure']['io']['full']['avg10'],
            first_disk=first['disk_free_bytes'],second_disk=second['disk_free_bytes'],
            cgroup_current=second['cgroup']['memory.current'],cgroup_max=second['cgroup']['memory.max'],
            cgroup_swap=second['cgroup']['memory.swap.current'],cgroup_events=second['cgroup']['events'])))
    print(json.dumps(dict(status='RESOURCE_PASS_AUTHORITY_REVIEW_PENDING' if all(checks.values()) else 'RESOURCE_FAIL',
        checks=checks,authority_rows=len(result['authority']['rows']),FLOCKs=len(second['FLOCKs']),raw_audit=str(dest))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--label',required=True)
    main(parser.parse_args().label)
