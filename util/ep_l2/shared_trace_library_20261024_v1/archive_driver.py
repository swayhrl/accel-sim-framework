from pathlib import Path
import json,sys,subprocess,shlex,gzip,time,fcntl,hashlib,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools');import manage
sys.path.insert(0,str(R/'tools'));import library_copy
gate=library_copy.Resources();gate(True)
lease=(R/'control/ARCHIVE_INVENTORY.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
ticks=int(open('/proc/self/stat').read().rsplit(')',1)[1].split()[19])
(R/'control/ARCHIVE_DRIVER_PID.json').write_text(json.dumps({'pid':os.getpid(),'start_ticks':ticks,'finite_archives':4,'read_only':True})+'\n')
requests=json.loads((R/'control/SOURCE_ARCHIVES.json').read_text())
pending=[r for i,r in enumerate(requests) if not (R/'control'/f'ARCHIVE_{i}.json.gz').exists()]
code=(R/'tools/archive_worker.py').read_text();p=subprocess.Popen(manage.SSH+['python3 -B -c '+shlex.quote(code)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
auth=R/'control/USER_BULK_4080_AND_IO_AUTHORIZATION_20261024.json'
if auth.exists():
 request={'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','authorization_sha256':hashlib.sha256(auth.read_bytes()).hexdigest(),'archives':pending}
else:request=pending
p.stdin.write(json.dumps(request));p.stdin.close()
try:
 for line in p.stdout:
  d=json.loads(line);gate()
  if d['event']=='ARCHIVE_DONE':
   i=next(i for i,r in enumerate(requests) if r['path']==d['path']);(R/'control'/f'ARCHIVE_{i}.json.gz').write_bytes(gzip.compress(line.encode(),mtime=0))
   print(json.dumps({'archive_done':i,'path':d['path'],'entries':len(d['members']),'hashed_bytes':d['hashed_member_bytes']}),flush=True)
  (R/'control/ARCHIVE_PROGRESS.json').write_text(json.dumps({k:v for k,v in d.items() if k!='members'})+'\n')
 rc=p.wait();assert rc==0,p.stderr.read()
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=15)
(R/'control/ARCHIVE_COMPLETE.json').write_text(json.dumps({'status':'PASS','archives':len(requests)})+'\n')
