"""Bounded read-only environment inventory; no compile, trace scan, install or output-root creation."""
import datetime,json,os,platform,resource,shutil,subprocess,time
from pathlib import Path

def read(p):
 try:return Path(p).read_text().strip()
 except OSError as e:return {'error':str(e)}
def run(cmd,timeout=8):
 try:
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,env=dict(os.environ,LC_ALL='C',PYTHONDONTWRITEBYTECODE='1'))
  return {'command':cmd,'rc':r.returncode,'stdout':r.stdout[:16000],'stderr':r.stderr[:2000]}
 except (OSError,subprocess.TimeoutExpired) as e:return {'command':cmd,'error':str(e)}
paths=['/','/workspace','/root','/root/workspace','/root/data','/root/share','/root/share/mnt164','/tmp','/var/tmp','/dev/shm','/cache','/toolchain','/mnt','/media','/opt','/root/.cache','/root/.local']
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.node(),'uid':os.getuid(),'gid':os.getgid(),'boot_id':read('/proc/sys/kernel/random/boot_id'),'paths':[]}
for name in paths:
 p=Path(name)
 if not p.exists():out['paths'].append({'path':name,'exists':False});continue
 try:
  st=p.stat();fs=os.statvfs(p)
  out['paths'].append({'path':name,'exists':True,'realpath':str(p.resolve()),'st_dev':st.st_dev,'mode':oct(st.st_mode&0o7777),'owner_uid':st.st_uid,'owner_gid':st.st_gid,'access_wx':os.access(p,os.W_OK|os.X_OK),'readonly_flag':bool(fs.f_flag&os.ST_RDONLY),'fsid':fs.f_fsid,'total_bytes':fs.f_blocks*fs.f_frsize,'available_bytes':fs.f_bavail*fs.f_frsize,'free_bytes_including_reserved':fs.f_bfree*fs.f_frsize,'free_inodes':fs.f_favail,'mount':run(['findmnt','-T',name,'-J','-o','TARGET,SOURCE,FSTYPE,OPTIONS,MAJ:MIN'])})
 except OSError as e:out['paths'].append({'path':name,'error':str(e)})
out['block_devices']=run(['lsblk','-J','-d','-b','-o','NAME,MAJ:MIN,SIZE,TYPE'])
out['memory']=read('/proc/meminfo');out['load']=read('/proc/loadavg');out['cpu_affinity']=sorted(os.sched_getaffinity(0));out['cgroup']=read('/proc/self/cgroup')
out['cgroup_limits']={p:read('/sys/fs/cgroup/'+p) for p in ['cpu.max','cpu.stat','cpuset.cpus.effective','memory.max','memory.high','memory.current','memory.swap.max','io.max','io.stat','pids.max']}
out['pressure_start']={p:read('/proc/pressure/'+p) for p in ['cpu','memory','io']};out['diskstats_start']=read('/proc/diskstats');time.sleep(1);out['pressure_end']={p:read('/proc/pressure/'+p) for p in ['cpu','memory','io']};out['diskstats_end']=read('/proc/diskstats')
vars_=['TMPDIR','TMP','TEMP','XDG_CACHE_HOME','CCACHE_DIR','CCACHE_TEMPDIR','SCCACHE_DIR','PIP_CACHE_DIR','PYTHONPYCACHEPREFIX','PYTHONDONTWRITEBYTECODE','CUDA_CACHE_PATH','CUDA_CACHE_DISABLE','HOME','PATH','CUDA_HOME','CUDA_PATH']
out['write_environment']={k:os.environ.get(k) for k in vars_};out['core_pattern']=read('/proc/sys/kernel/core_pattern');out['core_rlimit']=resource.getrlimit(resource.RLIMIT_CORE)
out['tool_versions']={cmd:run([cmd,'--version']) for cmd in ['gcc','g++','ld','make','cmake','python3','bison','flex','nvcc','ccache','sccache']}
out['cuda_existing']={p:run([p,'--version']) for p in ['/toolchain/cuda-12.4/bin/nvcc','/usr/local/cuda/bin/nvcc','/toolchain/bison-3.8.2/bin/bison','/toolchain/flex-2.6.4/bin/flex'] if Path(p).exists()}
out['quota']=run(['quota','-u','root']) if shutil.which('quota') else {'status':'tool_unavailable_no_quota_assertion'}
out['root_data_entries']=[{'name':p.name,'symlink':p.is_symlink()} for p in Path('/root/data').iterdir()] if Path('/root/data').is_dir() else []
print(json.dumps(out,indent=2))
