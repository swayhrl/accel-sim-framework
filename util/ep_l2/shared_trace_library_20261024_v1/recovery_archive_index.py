"""Read the original PolyBench container to locate four disappeared source members."""
from pathlib import Path
import json,gzip,subprocess,sys,shlex,time,fcntl,os,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
lease=(R/'control/RECOVERY_ARCHIVE_INDEX.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools');import manage
sys.path.insert(0,str(R/'tools'));import library_copy
gate=library_copy.Resources();gate(True)
ticks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
(R/'control/RECOVERY_ARCHIVE_PID.json').write_text(json.dumps({'pid':os.getpid(),'start_ticks':ticks,'finite_one_archive':True,'source_writes':0})+'\n')
suffixes=['/polybench-'+name+'/NO_ARGS/traces/kernel-'+str(k)+'.traceg' for name in ['atax','bicg'] for k in [1,2]]
request={'path':'/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz','hash_member_suffixes':suffixes}
code=(R/'tools/archive_worker.py').read_text()
p=subprocess.Popen(manage.SSH+['python3 -B -c '+shlex.quote(code)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
p.stdin.write(json.dumps({'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','archives':[request]}));p.stdin.close()
try:
 for line in p.stdout:
  d=json.loads(line);gate()
  if d['event']=='ARCHIVE_DONE':
   (R/'control/RECOVERY_POLY_ARCHIVE.json.gz').write_bytes(gzip.compress(line.encode(),mtime=0))
   assert d['compressed_bytes_read']==d['archive_identity']['size'] and d['source_before_after_unchanged']
   selected=[m for m in d['members'] if m.get('sha256') and any(m['archive_member'].endswith(s) for s in suffixes)]
   assert len(selected)==4,[(m['archive_member'],m.get('size')) for m in selected]
   summary={'status':'RECOVERY_MEMBERS_FULL_SHA_FROM_STABLE_ARCHIVE','archive_sha256':d['archive_sha256'],'archive_identity':d['archive_identity'],'selected':selected,'original_disk_hash_claimed':False,'source_writes':0}
   (R/'control/RECOVERY_POLY_INDEX_COMPLETE.json').write_text(json.dumps(summary,indent=2)+'\n')
   print(json.dumps({k:v for k,v in summary.items() if k!='selected'}),flush=True)
  else:(R/'control/RECOVERY_ARCHIVE_PROGRESS.json').write_text(json.dumps(d)+'\n')
 rc=p.wait();assert rc==0,p.stderr.read()
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=15)
