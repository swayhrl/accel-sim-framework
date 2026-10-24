#!/usr/bin/env python3
"""Task-private 4..15MiB/s NAS pump; distinguish FUSE stalls from local block contention."""
import subprocess,sys,threading,time,os,pathlib,json
BASE=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control')
rate=4*1024**2;stop=threading.Event()
def disks():
 out={}
 for line in pathlib.Path('/proc/diskstats').read_text().splitlines():
  x=line.split()
  if x[2].startswith(('nvme','sd')) and not (x[2][-1].isdigit() and 'n' not in x[2]):out[x[2]]=list(map(int,x[3:]))
 return out
def pressure():
 global rate
 before=disks();last=time.monotonic()
 while not stop.is_set():
  try:
   cp=subprocess.run(['/usr/bin/ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=8','hrl174new','cat /proc/pressure/io'],capture_output=True,text=True,timeout=12);assert cp.returncode==0
   remote=max(float(x.split('avg10=')[1].split()[0]) for x in cp.stdout.splitlines() if x.startswith(('some ','full ')))
   local=max(float(x.split('avg10=')[1].split()[0]) for x in pathlib.Path('/proc/pressure/io').read_text().splitlines())
   now=time.monotonic();after=disks();busy=0.;await_ms=0.
   for dev,v in after.items():
    if dev not in before:continue
    d=[a-b for a,b in zip(v,before[dev])];busy=max(busy,d[9]/max(.1,now-last)/10);await_ms=max(await_ms,(d[3]+d[7])/max(1,d[0]+d[4]))
   before,last=after,now
   config=BASE/'SSHFS_RATE_POLICY_V2.json';policy=json.loads(config.read_text()) if config.exists() else {'requested_mib_s':4}
   requested=max(4,min(15,float(policy['requested_mib_s'])))
   # High local PSI alone includes this task's FUSE waiting and is not a block conflict.
   selected=min(requested,4 if remote>=10 or busy>=50 else 8 if remote>=5 else 15)
   if remote>=40 or busy>=90 and await_ms>=20:selected=1
   elif remote>=20 or busy>=80 and await_ms>=20:selected=2
   mem={x.split(':')[0]:int(x.split()[1]) for x in pathlib.Path('/proc/meminfo').read_text().splitlines()}
   if mem['MemAvailable']<2*1024**2:selected=1
   rate=int(selected*1024**2)
   state={'schema':'NAS_PUMP_V2','rate_bytes_s':rate,'maximum_bytes_s':15*1024**2,'requested_mib_s':requested,'remote174_io_psi':remote,'local109_io_psi_observed_not_sufficient_for_throttle':local,'local_block_busy_pct':busy,'local_block_await_ms':await_ms,'mem_available_kib':mem['MemAvailable'],'unix':time.time(),'pid':os.getpid(),'policy':policy}
   temp=BASE/'SSHFS_RATE_STATE_V2.tmp';temp.write_text(json.dumps(state));os.replace(temp,BASE/'SSHFS_RATE_STATE_V2.json')
  except Exception:rate=1024**2
  stop.wait(10)
def pump(src,dest):
 deadline=time.monotonic()
 try:
  while True:
   b=os.read(src.fileno(),65536)
   if not b:break
   now=time.monotonic();deadline=max(deadline,now)+len(b)/rate
   if deadline>now:time.sleep(deadline-now)
   dest.write(b);dest.flush()
 except (BrokenPipeError,OSError):pass
 finally:
  try:dest.close()
  except Exception:pass
p=subprocess.Popen(['/usr/bin/ssh']+sys.argv[1:],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=sys.stderr)
threads=[threading.Thread(target=pressure,daemon=True),threading.Thread(target=pump,args=(sys.stdin.buffer,p.stdin),daemon=True),threading.Thread(target=pump,args=(p.stdout,sys.stdout.buffer),daemon=True)]
for t in threads:t.start()
rc=p.wait();stop.set();threads[2].join(timeout=5);sys.exit(rc)
