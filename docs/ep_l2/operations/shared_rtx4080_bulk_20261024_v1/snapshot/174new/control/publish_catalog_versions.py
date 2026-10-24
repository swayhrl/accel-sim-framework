#!/usr/bin/env python3
import pathlib,json,hashlib,time,fcntl,os
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/catalog');(B/'versions').mkdir(exist_ok=True)
singleton=open(C/'RTX4080_CATALOG_PUBLISHER.lock','a');fcntl.flock(singleton,fcntl.LOCK_EX|fcntl.LOCK_NB)
(C/'CATALOG_PUBLISHER_IDENTITY.json').write_text(json.dumps({'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19]})+'\n')
while True:
 locks=[]
 try:
  for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
   f=open(C/name,'a');fcntl.flock(f,fcntl.LOCK_EX);locks.append(f)
  b=(B/'ASSETS.json').read_bytes();q=json.loads(b);h=hashlib.sha256(b).hexdigest();dst=B/'versions'/(h+'.json')
  if not dst.exists():
   with dst.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
  assert hashlib.sha256(dst.read_bytes()).hexdigest()==h
  curr={'relative_path':'versions/'+h+'.json','sha256':h,'objects':len(q['objects']),'unix':time.time()}
  tmp=B/'CURRENT_RTX4080_CATALOG.tmp'
  with tmp.open('w')as f:json.dump(curr,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(tmp,B/'CURRENT_RTX4080_CATALOG.json')
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 time.sleep(5)

