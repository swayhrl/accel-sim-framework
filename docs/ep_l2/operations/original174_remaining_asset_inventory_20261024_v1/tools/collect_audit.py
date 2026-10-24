from audit_local import *
import sys
sys.stdout.reconfigure(encoding='utf-8')
SNAP=r'''
import os,json,time,subprocess,stat
from pathlib import Path
def meta(p):
 try:
  s=os.lstat(p);return dict(path=p,dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),type='symlink' if stat.S_ISLNK(s.st_mode) else 'dir' if stat.S_ISDIR(s.st_mode) else 'file',link=os.readlink(p) if stat.S_ISLNK(s.st_mode) else None)
 except OSError as e:return dict(path=p,error=str(e))
def cmd(a):return subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=10).stdout
x=dict(utc=time.time(),host=cmd(['hostname']).strip(),mountns=os.readlink('/proc/self/ns/mnt'),boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),mounts={},fs={},resources={},processes=[],discovery=[])
for p in ['/workspace','/root/data','/root/share','/root/share/mnt164']:
 x['mounts'][p]=cmd(['findmnt','-J','-T',p]);x['fs'][p]=meta(p)
 try:
  s=os.statvfs(p);x['fs'][p].update(total=s.f_blocks*s.f_frsize,available=s.f_bavail*s.f_frsize,free=s.f_bfree*s.f_frsize)
 except OSError:pass
for p in ['/proc/pressure/io','/proc/pressure/memory','/sys/fs/cgroup/memory.current','/sys/fs/cgroup/memory.max']:
 try:x['resources'][p]=Path(p).read_text()
 except OSError:pass
x['resources']['MemAvailable']=next(z for z in Path('/proc/meminfo').read_text().splitlines() if z.startswith('MemAvailable:'))
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  comm=(p/'comm').read_text().strip();cwd=os.readlink(p/'cwd');exe=os.readlink(p/'exe')
  if any(t in (comm+' '+cwd+' '+exe).lower() for t in ['accel-sim','gpgpu','aefair','dtc','awma','c16','ep_l2']):
   st=(p/'stat').read_text().rsplit(')',1)[1].split();x['processes'].append(dict(pid=int(p.name),comm=comm,cwd=cwd,exe=exe,start_ticks=st[19],state=st[0]))
 except (OSError,IndexError):pass
for base in ['/workspace','/root/data']:
 try:
  for e in os.scandir(base):
   if any(t in e.name.lower() for t in ['awma','c16','dtc','ep-l2','ep_l2','m5-','trace','accel','gpu-l2','vm-tlb']):x['discovery'].append(meta(e.path))
 except OSError:pass
print(json.dumps(x))
'''
def snapshots():
 for alias,label in [('hrl','SOURCE'),('hrl-174-new','TARGET')]:
  x=remote(alias,SNAP,60);save('evidence/'+label+'_ENDPOINT_ACTIVITY_START.json',x);print(label,'processes',len(x['processes']),'discovery',len(x['discovery']))
def rootstats():
 rows=list(csv.DictReader((P/'SOURCE_COLD_CENSUS_ROOT_LEDGER.csv').open(encoding='utf-8-sig')))
 paths=[r['source_path'] for r in rows if r['source_path'].startswith(('/workspace/','/tmp/')) and r['project'] not in ['Other_tmp_scratch','Local_software_environment','Local_software_cache']]
 code=SNAP[:SNAP.index('x=dict(')]+ '\npaths='+repr(paths)+ '\nprint(json.dumps([meta(p) for p in paths]))'
 x=remote('hrl',code,90);save('evidence/SOURCE_EXISTING_LEDGER_CURRENT_ROOT_STAT.json',x);print('current roots',len(x))
if __name__=='__main__':snapshots();rootstats()
