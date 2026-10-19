"""Finite paired host+cgroup CPU admission. Read-only until own receipt writes.

No Popen, signal, ptrace or background retry. Every entry must bind its own
exact source and current role before calling; all resources include all projects.
"""
import json, os, shutil, socket, time
from pathlib import Path
from datetime import datetime, timezone
from ownership import identity
from shared_authority import bind_current_review
RAW=Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')
def write(path,value):
    with path.open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')
class NoOwnedChildren:
    confirmed={}
    pending={}
    tracer=os.getpid()
    def classify(self,row):return 'UNKNOWN'
class CPUAdmission:
    def __init__(self,registration,roles,external_launch_view_provider=None):
        self.registration=registration
        self.review=bind_current_review(NoOwnedChildren(),identity,lambda:[],
                         exact_controller_roles_provider=lambda:roles,
                         external_launch_view_provider=external_launch_view_provider)
    def sample(self):
        pressure = {scope: {kind: Path(path, kind).read_text() for kind in ['memory','io']}
                    for scope,path in [('host','/proc/pressure')]}
        pressure['cgroup'] = {kind:Path('/sys/fs/cgroup',kind+'.pressure').read_text() for kind in ['memory','io']}
        available = next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
        maximum = Path('/sys/fs/cgroup/memory.max').read_text().strip()
        headroom = available if maximum=='max' else int(maximum)-int(Path('/sys/fs/cgroup/memory.current').read_text())
        events = {k:int(v) for k,v in (s.split() for s in Path('/sys/fs/cgroup/memory.events').read_text().splitlines())}
        oom = next(int(s.split()[1]) for s in Path('/proc/vmstat').read_text().splitlines() if s.startswith('oom_kill '))
        _, authority = self.review(identity(os.getpid()))
        return dict(utc=datetime.now(timezone.utc).isoformat(),monotonic_ns=time.monotonic_ns(),host=socket.gethostname(),uid=os.getuid(),
                    pressure=pressure,host_available=available,cgroup_headroom=headroom,cgroup_events=events,host_oom_kill=oom,
                    disk_free=shutil.disk_usage(RAW).free,output_filesystem_device=os.stat(RAW).st_dev,
                    authority=authority)
    def checks(self, s):
        values = dict(original174=s['host']=='huangrulin-174' and s['uid']==0,
                      host_memory_headroom=s['host_available']>=32*1024**3,cgroup_memory_headroom=s['cgroup_headroom']>=32*1024**3,
                      disk=s['disk_free']>self.registration['admission']['disk_floor_exclusive_bytes'],
                      authority=s['authority']['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY')
        for scope,kinds in s['pressure'].items():
            for kind,raw in kinds.items():
                line=next(x for x in raw.splitlines() if x.startswith('full '))
                avg=float(dict(x.split('=') for x in line.split()[1:])['avg10'])
                values[scope+'_'+kind]=avg <= (1 if kind=='memory' else 25)
        return values
    def admit(self,dest):
        dest.mkdir(parents=True,exist_ok=False)
        first=self.sample();write(dest/'FIRST.json',first);decision=self.checks(first)
        if not all(decision.values()):
            write(dest/'ADMISSION.json',dict(status='WAIT_RESOURCE_OR_AUTHORITY_FIRST_SAMPLE',checks=decision,starts=0))
            return False
        time.sleep(10.1)
        second=self.sample();write(dest/'SECOND.json',second)
        decision.update({'second_'+k:v for k,v in self.checks(second).items()})
        decision['gap_ge10s']=second['monotonic_ns']-first['monotonic_ns']>=10_000_000_000
        decision['no_new_host_oom']=first['host_oom_kill']==second['host_oom_kill']
        decision['no_new_cgroup_oom']=all(first['cgroup_events'][k]==second['cgroup_events'][k] for k in ['oom','oom_kill'])
        write(dest/'ADMISSION.json',dict(status='PASS_CPU_ADMISSION_ONLY' if all(decision.values()) else 'WAIT_RESOURCE_OR_AUTHORITY_PAIR',checks=decision,starts=0))
        return all(decision.values())

def execution_binding(path,registration):
    import hashlib
    manifest=registration.get('manifests_sha256')
    if manifest is None:
        values={row['manifests_sha256'] for row in registration['requests']}
        if len(values)!=1:raise ValueError('INCOHERENT_QUALIFICATION_MANIFESTS')
        manifest=values.pop()
    return dict(registration_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                prepared_source_sha256=registration['prepared_source_sha256'],
                manifests_sha256=manifest)

def require_execution_binding(receipt,expected):
    for key,value in expected.items():
        if receipt.get(key)!=value:raise ValueError('QUALIFICATION_RECEIPT_BINDING_CHANGED:'+key)
