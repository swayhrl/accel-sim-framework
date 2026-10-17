"""AA4 evidence helpers. All writes stay in this pack or the new AA4 raw root."""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone

PACK=Path(__file__).resolve().parents[1]
FW=PACK.parents[3]
ROOT=Path('/workspace/dtc-lane-aa4-gaussian-174-v1')
FW_REPO=Path('/workspace/repos/accel-sim-framework')
CORE_REPO=Path('/workspace/repos/gpgpu-sim_distribution')
AA_SHA='c381b6e49b483e01c1c8a73118a3d450eeaf3b7f'
T_SHA='f520a445436b57c0a0f2494fb858a1636f04d2bc'
V_SHA='26abd496417d9392245052e54fbd9ba27c6ffd96'
BASE_CORE='6fba0136f8465b59fe5858a950fa39efb265f654'
CANDIDATE_CORE='c0a5e2c31e407c57e3a4af3ce529c921e8059a05'
OLD_PACK='docs/dtc_l1/review_packs/DTC_LANE_AA_GAUSSIAN_V1'
T_PACK='docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1'
V_PACK='docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1'
K_OPTION='-gpgpu_dtc_l1_invalidate_on_source_event'
POINTS=[('K0_32x4','d0a29a82-c171-46e4-b077-d7ccfd2c4b7a',0,32,4,3798174),
        ('K0_64x8','aba7a8eb-e82c-4a18-b410-5d568f819f27',0,64,8,3278356),
        ('K1_32x4','dd65b440-dc75-4632-9f7b-3e8a1062d5a1',1,32,4,3798174),
        ('K1_64x8','a9d64a6f-4fb5-4e3d-883c-ae75f1ac5f89',1,64,8,3278356)]


def now():return datetime.now(timezone.utc).isoformat()


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def write(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')


def table(p,rows):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def blob(repo,commit,path):
    return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path])


def git_json(repo,commit,path):return json.loads(blob(repo,commit,path))


def copy_blob(repo,commit,path,destination):
    data=blob(repo,commit,path);destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('xb') as f:f.write(data)
    return dict(repository=str(repo),commit=commit,path=path,
                blob=git(repo,'rev-parse',commit+':'+path),
                sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
                destination=str(destination.relative_to(PACK)))


def options(paths):
    result={}
    for path in paths:
        key=None
        for token in shlex.split(Path(path).read_text(),comments=True):
            if re.match(r'^-[A-Za-z_]',token):key=token;result[key]=[]
            else:
                assert key is not None
                result[key].extend(token.split())
    return result


def proc(pid):
    p=Path('/proc')/str(pid)
    try:
        s=(p/'stat').read_text().rsplit(')',1)[1].split()
        return dict(pid=int(pid),state=s[0],start_ticks=int(s[19]),
                    rss_bytes=int(s[21])*os.sysconf('SC_PAGE_SIZE'),
                    argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\0') if v])
    except (FileNotFoundError,ProcessLookupError):return None


def snapshot():
    cg=Path('/sys/fs/cgroup')
    cgroup={k:(cg/k).read_text().strip() for k in ['memory.current','memory.max','memory.swap.current',
            'memory.swap.max','memory.events','memory.pressure','io.pressure','io.stat','cpu.pressure']}
    processes=[r for p in Path('/proc').glob('[0-9]*') if (r:=proc(p.name)) and r['state']!='Z']
    vm=dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
    memory={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
    pressure={k:{line.split()[0]:dict(t.split('=') for t in line.split()[1:])
                    for line in Path('/proc/pressure',k).read_text().splitlines()} for k in ['memory','io','cpu']}
    return dict(utc=now(),monotonic_ns=time.monotonic_ns(),host=socket.gethostname(),uid=os.getuid(),
          boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
          cgroup_membership=Path('/proc/self/cgroup').read_text(),cgroup=cgroup,pressure=pressure,
          host_MemAvailable_bytes=memory['MemAvailable'],pswpin=int(vm['pswpin']),pswpout=int(vm['pswpout']),
          disk_free_bytes=shutil.disk_usage(ROOT).free,processes=processes,
          proc_RSS_sum_bytes=sum(p['rss_bytes'] for p in processes),
          RSS_scope='ALL_VISIBLE_PROCESSES_SHARED_PAGES_MAY_BE_COUNTED_MULTIPLE_TIMES',
          proc_locks=Path('/proc/locks').read_text(),diskstats=Path('/proc/diskstats').read_text())


def lock_observation(p,snapshot_data):
    p=Path(p)
    if not p.exists():return dict(path=str(p),exists=False,owners=[])
    st=p.stat();owners=[]
    for line in snapshot_data['proc_locks'].splitlines():
        fields=line.split()
        if len(fields)>6 and len(d:=fields[5].split(':'))==3:
            if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):owners.append(line)
    return dict(path=str(p),exists=True,inode=st.st_ino,device=st.st_dev,owners=owners)


def resource_checks(first,second):
    checks={}
    for label,s in [('first',first),('second',second)]:
        cg=s['cgroup'];limit=cg['memory.max']
        head=int(limit)-int(cg['memory.current']) if limit!='max' else s['host_MemAvailable_bytes']
        checks[label+'_host']=s['host']=='huangrulin-174' and s['uid']==0
        checks[label+'_host_memory']=s['host_MemAvailable_bytes']>=32*1024**3
        checks[label+'_cgroup_headroom']=head>=32*1024**3
        checks[label+'_disk']=s['disk_free_bytes']>=10*1024**3
        checks[label+'_memory_PSI']=float(s['pressure']['memory']['full']['avg10'])<=1
        checks[label+'_io_PSI']=float(s['pressure']['io']['full']['avg10'])<=25
    checks['probe_at_least_10_seconds']=second['monotonic_ns']-first['monotonic_ns']>=10_000_000_000
    checks['no_new_swap']=all(second[k]==first[k] for k in ['pswpin','pswpout'])
    events=[dict(line.split() for line in s['cgroup']['memory.events'].splitlines()) for s in [first,second]]
    checks['no_new_oom']=all(events[0][k]==events[1][k] for k in ['oom','oom_kill'])
    return checks
