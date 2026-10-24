"""One finite archive inventory; concurrent archives use distinct leases."""
from pathlib import Path
import json,sys,subprocess,shlex,gzip,time,fcntl,hashlib,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools');import manage
sys.path.insert(0,str(R/'tools'));import library_copy as e
i=int(sys.argv[1]);assert i in [2,3]
lease=(R/'control'/f'ARCHIVE_ONE_{i}.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
requests=json.loads((R/'control/SOURCE_ARCHIVES.json').read_text());request=dict(requests[i]);dest=R/'control'/f'ARCHIVE_{i}.json.gz'
if dest.exists() and json.loads(gzip.decompress(dest.read_bytes())).get('inventory_format')=='V2_FULL_DECODED_EOF_IGNORE_ZEROS':raise SystemExit(0)
gate=e.Resources();gate(True);auth=R/'control/USER_BULK_4080_AND_IO_AUTHORIZATION_20261024.json';assert auth.exists()
q=json.loads((R/'control/ARCHIVE_V2_QUALIFICATION.json').read_text());code=(R/'tools/archive_worker.py').read_text();assert q['status']=='PASS' and q['worker_sha256']==hashlib.sha256(code.encode()).hexdigest()
if i==2:
    request.update(actual_path='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz',source_host='174-new',expected_archive_sha256='9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca')
    p=subprocess.Popen(['python3','-B',str(R/'tools/archive_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
else:p=subprocess.Popen(manage.SSH+['python3 -B -c '+shlex.quote(code)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
payload={'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','authorization_sha256':hashlib.sha256(auth.read_bytes()).hexdigest(),'archives':[request]}
p.stdin.write(json.dumps(payload));p.stdin.close();done=False
try:
    for line in p.stdout:
        d=json.loads(line);gate()
        if d['event']=='ARCHIVE_DONE':
            assert d['path']==request['path']
            temp=dest.with_name(dest.name+f'.one{i}-writing');temp.write_bytes(gzip.compress(line.encode(),mtime=0));os.replace(temp,dest);done=True
        progress={k:v for k,v in d.items() if k!='members'}
        (R/'control'/f'ARCHIVE_{i}_PROGRESS.json').write_text(json.dumps(progress)+'\n')
        print(json.dumps({k:v for k,v in progress.items() if k not in ['archive_identity']}),flush=True)
    rc=p.wait();assert rc==0 and done,p.stderr.read()
finally:
    if p.poll() is None:p.terminate();p.wait(timeout=15)
complete=[]
for j in range(4):
    path=R/'control'/f'ARCHIVE_{j}.json.gz'
    if path.exists():
        d=json.loads(gzip.decompress(path.read_bytes()))
        if d.get('inventory_format')=='V2_FULL_DECODED_EOF_IGNORE_ZEROS' and d['decoded_compression_EOF_integrity_checked']:complete.append(j)
if len(complete)==4:(R/'control/ARCHIVE_COMPLETE.json').write_text(json.dumps({'status':'PASS','archives':4,'inventory_format':'V2_FULL_DECODED_EOF_IGNORE_ZEROS','finite_parallel_indices':[2,3]})+'\n')
