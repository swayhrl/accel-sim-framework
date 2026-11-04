from pathlib import Path
import json,datetime,os,time,subprocess
A2=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');O=A2/'agents/A_resource_config_v1';O.mkdir(parents=True,exist_ok=True);cg=Path('/sys/fs/cgroup');fields=['memory.current','memory.max','memory.swap.current','memory.events','memory.stat','memory.pressure','io.pressure','cpu.pressure','cpu.max','cpuset.cpus.effective'];
def vm():return {k:int(v)for k,v in (l.split()for l in Path('/proc/vmstat').read_text().splitlines())if k in ['pswpout','pswpin','oom_kill']}
a=vm();t=time.monotonic();time.sleep(2);b=vm();elapsed=time.monotonic()-t
mem={}
for l in Path('/proc/meminfo').read_text().splitlines():
 k,v=l.split(':',1)
 if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']:mem[k]=int(v.strip().split()[0])*1024
x=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),host_memory_bytes=mem,cgroup={f:(cg/f).read_text()for f in fields},host_PSI={n:Path('/proc/pressure',n).read_text()for n in ['memory','cpu','io']},swap_sample_before=a,swap_sample_after=b,swap_sample_seconds=elapsed,active_swap_out_bytes_per_second=max(0,b['pswpout']-a['pswpout'])*os.sysconf('SC_PAGE_SIZE')/elapsed,owner_main_affinity=sorted(os.sched_getaffinity(1498278)),inspector_affinity=sorted(os.sched_getaffinity(0)),NUMA=[dict(node=p.name,cpulist=(p/'cpulist').read_text().strip(),meminfo=(p/'meminfo').read_text())for p in sorted(Path('/sys/devices/system/node').glob('node[0-9]*'))],storage={})
for n,p in [('native',Path('/root/data')),('true164',O)]:
 v=os.statvfs(p);x['storage'][n]=dict(path=str(p),available_bytes=v.f_bavail*v.f_frsize,free_inodes=v.f_favail,device=p.stat().st_dev,findmnt=json.loads(subprocess.check_output(['findmnt','-J','-T',str(p)],text=True)))
(O/'INITIAL_REAL_RESOURCE_OBSERVATION.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'swap_rate_Bps':x['active_swap_out_bytes_per_second'],'host_available_GiB':mem['MemAvailable']/1024**3,'nativeFreeGiB':x['storage']['native']['available_bytes']/1024**3,'hostPSI':x['host_PSI']}))
