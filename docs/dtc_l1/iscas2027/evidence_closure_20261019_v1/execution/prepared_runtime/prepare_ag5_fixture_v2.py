"""One finite registered CPU fixture preparation. No guard/test/model invocation."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')
REG = HERE.parent / 'CPU_AG5_V2_BUILD_REGISTRATION.json'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'vendor'))
from ownership import identity
from shared_authority import bind_current_review

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, value):
    with path.open('x') as stream: stream.write(json.dumps(value, indent=2)+'\n')

class NoOwnedChildren:
    confirmed = {}
    pending = {}
    tracer = os.getpid()
    def classify(self, row): return 'UNKNOWN'

def main():
    registration = json.loads(REG.read_text())
    if registration['status'] != 'REGISTERED_FOR_ONE_BOUNDED_CPU_FIXTURE_BUILD_AND_STATIC_FREEZE_ONLY_AFTER_FRESH_FULL_R2_AUTHORITY':
        raise ValueError('BUILD_RELEASE_REQUIRED')
    if list(os.sys.argv) != [str(HERE / 'prepare_ag5_fixture_v2.py')]:
        raise ValueError('EXACT_BUILD_ENTRY_REQUIRED')
    for path, digest in registration['all_source_and_tool_sha256'].items():
        if sha(path) != digest: raise ValueError('BUILD_SOURCE_OR_TOOL_CHANGED:'+path)
    if str(Path.cwd()) != registration['cwd']: raise ValueError('BUILD_CWD_CHANGED')
    dest = Path(registration['receipt_output']);dest.mkdir(parents=True, exist_ok=False)
    review = bind_current_review(NoOwnedChildren(), identity, lambda: [],
            exact_controller_roles_provider=lambda: registration['controller_roles'])
    def sample():
        pressure = {scope: {kind: Path(path, kind).read_text() for kind in ['memory','io']}
                    for scope,path in [('host','/proc/pressure')]}
        pressure['cgroup'] = {kind:Path('/sys/fs/cgroup',kind+'.pressure').read_text() for kind in ['memory','io']}
        available = next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
        maximum = Path('/sys/fs/cgroup/memory.max').read_text().strip()
        headroom = available if maximum=='max' else int(maximum)-int(Path('/sys/fs/cgroup/memory.current').read_text())
        events = {k:int(v) for k,v in (s.split() for s in Path('/sys/fs/cgroup/memory.events').read_text().splitlines())}
        oom = next(int(s.split()[1]) for s in Path('/proc/vmstat').read_text().splitlines() if s.startswith('oom_kill '))
        _, authority = review(identity(os.getpid()))
        return dict(utc=datetime.now(timezone.utc).isoformat(),monotonic_ns=time.monotonic_ns(),host=socket.gethostname(),uid=os.getuid(),
                    pressure=pressure,host_available=available,cgroup_headroom=headroom,cgroup_events=events,host_oom_kill=oom,
                    disk_free=shutil.disk_usage(RAW).free,output_filesystem_device=os.stat(RAW).st_dev,
                    authority=authority)
    def checks(s):
        values = dict(original174=s['host']=='huangrulin-174' and s['uid']==0,
                      host_memory=s['host_available']>=32*1024**3,cgroup_memory=s['cgroup_headroom']>=32*1024**3,
                      disk=s['disk_free']>=registration['admission']['CPU_disk_floor_plus_output_bytes'],
                      authority=s['authority']['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY')
        for scope,kinds in s['pressure'].items():
            for kind,raw in kinds.items():
                line=next(x for x in raw.splitlines() if x.startswith('full '))
                avg=float(dict(x.split('=') for x in line.split()[1:])['avg10'])
                values[scope+'_'+kind]=avg <= (1 if kind=='memory' else 25)
        return values
    first=sample();write(dest/'FIRST.json',first);decision=checks(first)
    if not all(decision.values()):
        write(dest/'ADMISSION.json',dict(status='WAIT_RESOURCE_OR_AUTHORITY_FIRST_SAMPLE',checks=decision,starts=0));return 3
    time.sleep(10.1)
    second=sample();write(dest/'SECOND.json',second)
    decision.update({'second_'+k:v for k,v in checks(second).items()})
    decision['gap_ge10s']=second['monotonic_ns']-first['monotonic_ns']>=10_000_000_000
    decision['no_new_host_oom']=first['host_oom_kill']==second['host_oom_kill']
    decision['no_new_cgroup_oom']=all(first['cgroup_events'][k]==second['cgroup_events'][k] for k in ['oom','oom_kill'])
    write(dest/'ADMISSION.json',dict(status='PASS_CPU_BUILD_ONLY' if all(decision.values()) else 'WAIT_RESOURCE_OR_AUTHORITY_PAIR',checks=decision,starts=0))
    if not all(decision.values()):return 3
    env=registration['environment']
    def bounded(label,argv,timeout):
        def limits():
            resource.setrlimit(resource.RLIMIT_CORE,(0,0))
            resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
            resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,32*1024**2))
            resource.setrlimit(resource.RLIMIT_CPU,(30,30))
        with (dest/(label+'.stdout')).open('xb') as out,(dest/(label+'.stderr')).open('xb') as err:
            child=subprocess.Popen(argv,cwd=registration['cwd'],env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits)
            initial=identity(child.pid)
            if initial['ppid']!=os.getpid():raise ValueError('NOT_OWN_DIRECT_POPEN')
            write(dest/(label+'_START.json'),dict(argv=argv,pid=child.pid,start_ticks=initial['start_ticks'],purpose='BOUNDED_CPU_PREPARATION_ONLY',simulator_starts=0))
            timed_out=False
            try:rc=child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # wait(timeout) has not reaped the root. Its live, exact instance
                # reserves its PID/PGID; no post-reap group signal is permitted.
                fresh=identity(child.pid)
                if fresh['start_ticks']!=initial['start_ticks'] or os.getpgid(child.pid)!=child.pid:
                    raise ValueError('OWN_PROCESS_GROUP_IDENTITY_CHANGED')
                os.killpg(child.pid,signal.SIGKILL);timed_out=True;rc=child.wait(timeout=5)
        leftovers=[]
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():continue
            try:
                fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
                if int(fields[2])==child.pid:leftovers.append(dict(pid=int(entry.name),start_ticks=int(fields[19]),state=fields[0]))
            except (FileNotFoundError,ProcessLookupError):pass
        result=dict(returncode=rc,timed_out=timed_out,root_reaped=True,leftover_group_instances=leftovers,post_reap_signals=0,
                    stdout_sha256=sha(dest/(label+'.stdout')),stderr_sha256=sha(dest/(label+'.stderr')),simulator_starts=0)
        write(dest/(label+'_TERMINAL.json'),result)
        output_ok=sum((dest/(label+'.'+name)).stat().st_size for name in ['stdout','stderr'])<=registration['log_bound_bytes']
        return rc==0 and not leftovers and not timed_out and output_ok
    target=Path(registration['output'])
    if target.exists():raise ValueError('NEVER_OVERWRITE_EXISTING_FIXTURE')
    if not bounded('compile',registration['compiler_argv'],registration['build_timeout_seconds']):return 4
    if target.stat().st_size>registration['binary_size_bound_bytes']:raise ValueError('FIXTURE_BINARY_SIZE_BOUND')
    current=sample();write(dest/'PRE_FREEZE.json',current)
    if not all(checks(current).values()):
        write(dest/'RESULT.json',dict(status='BUILT_NOT_FROZEN_RESOURCE_HOLD',binary_sha256=sha(target),simulator_starts=0));return 3
    if not bounded('freeze',registration['freeze_argv'],30):return 4
    write(dest/'RESULT.json',dict(status='PASS_CPU_FIXTURE_BUILT_STATIC_FROZEN_NOT_EXECUTED',binary_sha256=sha(target),binary_bytes=target.stat().st_size,
                                target_executions=0,simulation_starts=0,registration_sha256=sha(REG)))
    return 0

if __name__=='__main__':sys.exit(main())
