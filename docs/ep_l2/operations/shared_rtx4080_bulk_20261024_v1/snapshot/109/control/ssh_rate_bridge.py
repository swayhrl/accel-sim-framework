#!/usr/bin/env python3
"""Task-private SSH stdio bridge: aggregate SSHFS payload <=15MiB/s each way."""
import subprocess,sys,threading,time,os,pathlib,json
BASE=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control')
rate=15*1024**2
stop=threading.Event()
def pressure():
 global rate
 while not stop.is_set():
  try:
   p=subprocess.run(['/usr/bin/ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=8','hrl174new','cat /proc/pressure/io; cat /proc/meminfo | head -3'],capture_output=True,text=True,timeout=12)
   assert p.returncode==0
   v=[]
   for line in p.stdout.splitlines():
    if line.startswith(('some ','full ')):v.append(float(line.split('avg10=')[1].split()[0]))
   for line in pathlib.Path('/proc/pressure/io').read_text().splitlines():
    if line.startswith(('some ','full ')):v.append(float(line.split('avg10=')[1].split()[0]))
   peak=max(v or [100]);rate=(1 if peak>=20 else 4 if peak>=10 else 8 if peak>=5 else 15)*1024**2
   (BASE/'SSHFS_RATE_STATE.json').write_text(json.dumps({'rate_bytes_s':rate,'max_rate_bytes_s':15*1024**2,'io_psi_avg10_max':peak,'unix':time.time(),'pid':os.getpid()}))
  except Exception:rate=1024**2
  stop.wait(10)
def pump(src,dest):
 deadline=time.monotonic()
 try:
  while True:
   b=os.read(src.fileno(),65536)
   if not b:break
   now=time.monotonic();deadline=max(deadline,now)+len(b)/rate
   delay=deadline-now
   if delay>0:time.sleep(delay)
   dest.write(b);dest.flush()
 except (BrokenPipeError,OSError):pass
 finally:
  try:dest.close()
  except Exception:pass
p=subprocess.Popen(['/usr/bin/ssh']+sys.argv[1:],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=sys.stderr)
threads=[threading.Thread(target=pressure,daemon=True),threading.Thread(target=pump,args=(sys.stdin.buffer,p.stdin),daemon=True),threading.Thread(target=pump,args=(p.stdout,sys.stdout.buffer),daemon=True)]
for t in threads:t.start()
rc=p.wait();stop.set();threads[2].join(timeout=5);sys.exit(rc)

