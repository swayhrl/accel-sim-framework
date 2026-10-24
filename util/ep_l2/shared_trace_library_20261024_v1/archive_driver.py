"""Finite sequential inventory, including verified retired-source NAS package."""
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
code=(R/'tools/archive_worker.py').read_text()
auth=R/'control/USER_BULK_4080_AND_IO_AUTHORIZATION_20261024.json'
assert auth.exists()
qualification=json.loads((R/'control/ARCHIVE_V2_QUALIFICATION.json').read_text());assert qualification['status']=='PASS'
for i,original in enumerate(requests):
    dest=R/'control'/f'ARCHIVE_{i}.json.gz';prior=json.loads(gzip.decompress(dest.read_bytes())) if dest.exists() else None
    if prior and prior.get('inventory_format')=='V2_FULL_DECODED_EOF_IGNORE_ZEROS':continue
    request=dict(original)
    if prior:request['prior_index']=prior
    if original['path'].endswith('/polybench.tgz'):
        proof_path=Path('/root/data/research_asset_verified_offload_20261024_v1/control/EXISTING_POLYBENCH_CURRENT_FULL_SHA.json')
        proof=json.loads(proof_path.read_text())
        request.update(actual_path='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz',source_host='174-new',expected_archive_sha256='9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca',retirement_proof_reference=str(proof_path))
        p=subprocess.Popen(['python3','-B',str(R/'tools/archive_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    else:p=subprocess.Popen(manage.SSH+['python3 -B -c '+shlex.quote(code)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    payload={'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','authorization_sha256':hashlib.sha256(auth.read_bytes()).hexdigest(),'archives':[request]}
    p.stdin.write(json.dumps(payload));p.stdin.close();done=False
    try:
        for line in p.stdout:
            d=json.loads(line);gate()
            if d['event']=='ARCHIVE_DONE':
                assert d['path']==original['path']
                temp=dest.with_name(dest.name+'.v2-writing');temp.write_bytes(gzip.compress(line.encode(),mtime=0));os.replace(temp,dest);done=True
                print(json.dumps({'archive_done':i,'path':d['path'],'entries':len(d['members']),'hashed_bytes':d['hashed_member_bytes'],'reused_member_bytes':d['reused_same_archive_SHA_member_bytes']}),flush=True)
            (R/'control/ARCHIVE_PROGRESS.json').write_text(json.dumps({k:v for k,v in d.items() if k!='members'})+'\n')
        rc=p.wait();assert rc==0 and done,p.stderr.read()
    finally:
        if p.poll() is None:p.terminate();p.wait(timeout=15)
(R/'control/ARCHIVE_COMPLETE.json').write_text(json.dumps({'status':'PASS','archives':len(requests),'inventory_format':'V2_FULL_DECODED_EOF_IGNORE_ZEROS'})+'\n')
