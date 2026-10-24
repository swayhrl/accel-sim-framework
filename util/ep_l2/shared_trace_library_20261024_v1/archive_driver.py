from pathlib import Path
import json,sys,subprocess,shlex,gzip,time
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools');import manage
sys.path.insert(0,str(R/'tools'));import library_copy
gate=library_copy.Resources();gate(True)
requests=json.loads((R/'control/SOURCE_ARCHIVES.json').read_text())
pending=[r for i,r in enumerate(requests) if not (R/'control'/f'ARCHIVE_{i}.json.gz').exists()]
code=(R/'tools/archive_worker.py').read_text();p=subprocess.Popen(manage.SSH+['python3 -B -c '+shlex.quote(code)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
p.stdin.write(json.dumps(pending));p.stdin.close()
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
