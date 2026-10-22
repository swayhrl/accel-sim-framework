"""Finite authorized synthetic V9 pilot. No scientific dispatch or Source release.

Run on174-new only, after the explicit approval sidecars and pinned V9 module
have been installed in the newly owned scratch controls directory. Every data
path is confined to the two approved roots. All staged/fault data are retained.
"""
import copy
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True
SCRATCH=Path('/root/data/result_offload_pilot_20261023_v1')
RECEIVER_LOCK=Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock')
NAS=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_result_offload_pilot_v1')
NATIVE=str(NAS).replace('/root/share/mnt164','/home/shared',1)
V9_SHA='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
APPROVED_REQUEST_SHA='2700fb709872651b695b4deddf5f9842f8b45920ea1af578ac4ead7b07e6161c'
GIB=1024**3
MIB=1024**2
CHUNK=65536
RATE=MIB
PEAKS={'scratch_allocated_bytes':0,'NAS_allocated_bytes':0,'host_MemAvailable_min':None,'Share_available_min':None}
ROOTS=[SCRATCH,NAS]

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(j):return (json.dumps(j,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,reason):
    if not ok:raise RuntimeError(reason)
def allocated(root):
    if not root.exists():return 0
    seen=set();total=0;count=0
    for p in [root,*root.rglob('*')]:
        s=p.lstat();require(not stat.S_ISLNK(s.st_mode),'owned root acquired symlink')
        key=(s.st_dev,s.st_ino)
        if key not in seen:total+=s.st_blocks*512;seen.add(key)
        count+=1;require(count<=1000,'owned path count cap')
    return total
def gates():
    require(os.uname().nodename=='huangrulin-sshfs-174','wrong execution host')
    m=subprocess.check_output(['findmnt','-n','-T',str(NAS.parent),'-o','TARGET,SOURCE,FSTYPE'],text=True).split()
    require(m==['/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs'],'wrong genuine164 mount')
    fs=subprocess.check_output(['findmnt','-n','-T',str(SCRATCH.parent),'-o','FSTYPE'],text=True).strip()
    require(fs=='ext4','scratch is not approved native ext4')
    mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
    sv=os.statvfs('/root/share');free=sv.f_bavail*sv.f_frsize
    datafs=os.statvfs('/root/data');datafree=datafs.f_bavail*datafs.f_frsize
    require(datafree-20*MIB>=7*GIB and mem>=64*GIB,'native SSD/RAM admission HOLD')
    require((SCRATCH.parent).stat().st_dev==2128,'native scratch device changed')
    # DRAFT: execute only after explicit approval of ZERO_SHARE_SCOPE_AMENDMENT.json.
    # Share remains observed; all new files are on native SSD or genuine164.
    a,b=allocated(SCRATCH),allocated(NAS)
    require(a<=16*MIB and b<=8*MIB,'approved allocated cap exceeded')
    PEAKS['scratch_allocated_bytes']=max(PEAKS['scratch_allocated_bytes'],a)
    PEAKS['NAS_allocated_bytes']=max(PEAKS['NAS_allocated_bytes'],b)
    for k,value in [('host_MemAvailable_min',mem),('Share_available_min',free)]:PEAKS[k]=value if PEAKS[k] is None else min(PEAKS[k],value)
    return {'utc':utc(),'scratch_allocated_bytes':a,'NAS_allocated_bytes':b,'Share_available':free,'MemAvailable':mem}
def init_v9():
    raw=(SCRATCH/'controls/v9_transaction.py').read_bytes();require(sha(raw)==V9_SHA,'V9 bytes changed')
    sys.path.insert(0,str(SCRATCH/'controls'))
    import v9_transaction
    return v9_transaction
def write_new(p,raw):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():require(p.read_bytes()==raw,'owned immutable bytes changed');return
    with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def manifest_for(v,base,files,dirs,publication):
    m={'source_filesystem_identity':{'host':os.uname().nodename,'mount_namespace':os.readlink('/proc/self/ns/mnt'),'dev':(SCRATCH/'fixtures').stat().st_dev,'inode':(SCRATCH/'fixtures').stat().st_ino},'source_root':str(SCRATCH/'fixtures'),'source_frozen_commit':publication,'files':files,'directories':dirs,'symlink_policy':'REFUSE','hardlink_policy':'REFUSE','genuine164_destination_root':str(base).replace('/root/share/mnt164','/home/shared',1),'destination_path_on_174new':str(base),'source_originals_action':'SOURCE_KEEP','identity_encoding':'CANONICAL_JSON_V1'}
    m['selector_sha256']=v.digest(v.canonical({k:m[k] for k in ['files','directories','symlink_policy','hardlink_policy']}))
    return m
def transaction(v,base,m):
    base.mkdir(exist_ok=True);t=v.Transaction(base,m);t.throttle=v.Throttle(RATE);return t
def chunk_key(v,name,offset):return v.digest(name.encode())+'.%016d'%offset
def worker():
    v=init_v9();mode,manifest_path,name,offset,stage,expected=sys.argv[2:]
    m=json.loads(Path(manifest_path).read_bytes());t=transaction(v,Path(m['destination_path_on_174new']),m);gates()
    if mode=='incomplete':
        target=t.work/'chunks'/(chunk_key(v,name,int(offset))+'.partial')
        with target.open('xb') as f:f.write(Path(stage).read_bytes()[:32768]);f.flush();os.fsync(f.fileno())
        os._exit(93)
    try:t.accept_chunk(name,int(offset),Path(stage),expected,txid=t.txid,crash=mode)
    except v.Hold as e:
        if str(e).startswith('injected '):os._exit(91 if mode=='before_chunk_record' else 92)
        raise
    raise RuntimeError('injection did not exit')
def run():
    resource.setrlimit(resource.RLIMIT_AS,(256*MIB,256*MIB))
    os.nice(19)
    if hasattr(os,'sched_setaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    # Bootstrap already performed a separate prewrite resource admission and
    # exclusive scratch reservation. Revalidate it before any test operation.
    approval=json.loads((SCRATCH/'controls/USER_APPROVAL.json').read_bytes())
    require(approval['status']=='APPROVED' and approval['approved_request_sha256']==APPROVED_REQUEST_SHA,'missing exact explicit approval')
    reservation=json.loads((SCRATCH/'PILOT_RESERVATION.json').read_bytes());publication=reservation['tool_publication_commit']
    require(len(publication)==40,'missing published code identity')
    lock=RECEIVER_LOCK.open('rb')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('sole existing receiver busy: HOLD')
    require((NAS/'PILOT_RESERVATION.json').read_bytes()==canonical(reservation),'NAS reservation differs')
    v=init_v9();start=time.monotonic();initial=gates();cases=[]
    def passed(name,proof):
        item={'case':name,'status':'PASS','proof':proof};v.exclusive_json(SCRATCH/'controls'/('CASE_'+name+'.json'),item);cases.append(item);gates()
    def refuses(name,fn):
        try:fn()
        except (v.Hold,RuntimeError,FileExistsError,KeyError) as e:
            passed(name,{'expected_refusal':type(e).__name__,'reason':str(e)});return
        raise RuntimeError('negative accepted: '+name)
    fixtures=SCRATCH/'fixtures'
    if not (SCRATCH/'controls/SOURCE_MANIFEST.json').exists():
        require(not fixtures.exists(),'unfrozen existing fixture directory')
        fixtures.mkdir();(fixtures/'meta').mkdir();(fixtures/'empty').mkdir()
        data={'meta/metadata.json':b'{"synthetic":true,"project":"RESULT_OFFLOAD_PILOT_V1"}\n'.ljust(4096,b' '),'events.txt':(b'SYNTHETIC_EVENT\n'*18000)[:262144],'payload.bin':hashlib.shake_256(b'RESULT_OFFLOAD_SYNTHETIC_V1').digest(1048576),'empty.zero':b''}
        require(sum(map(len,data.values()))==1314816,'fixture exact byte count')
        for i,(name,b) in enumerate(data.items()):
            p=fixtures/name;write_new(p,b);os.chmod(p,[0o640,0o644,0o600,0o444][i]);os.utime(p,ns=(1792684800123456789+i,1792684800123456789+i))
        for i,name in enumerate(['meta','empty','.']):os.chmod(fixtures/name,0o750);os.utime(fixtures/name,ns=(1792684801123456789+i,1792684801123456789+i))
        rows=[dict(v.identity((fixtures/n).stat()),relative_path=n,type='regular',sha256=sha(b)) for n,b in data.items()]
        dirs=[dict(v.identity((fixtures/n).stat()),relative_path=n,type='directory') for n in ['.','meta','empty']]
        m=manifest_for(v,NAS/'archive',rows,dirs,publication);v.exclusive_json(SCRATCH/'controls/SOURCE_MANIFEST.json',m)
    m=json.loads((SCRATCH/'controls/SOURCE_MANIFEST.json').read_bytes())
    for row in m['files']:require(v.hash_file(fixtures/row['relative_path'],expected={k:row[k] for k in v.identity((fixtures/row['relative_path']).stat())})==row['sha256'],'fixture source changed')
    require(len(m['files'])==4 and len(m['directories'])==3 and sum(r['size'] for r in m['files'])==1314816,'wrong frozen fixture scope')
    ranges=[]
    for row in m['files']:
        p=fixtures/row['relative_path']
        with p.open('rb') as f:
            for offset in range(0,row['size'],CHUNK):
                b=f.read(CHUNK);s=SCRATCH/'stage'/chunk_key(v,row['relative_path'],offset);write_new(s,b);ranges.append({'name':row['relative_path'],'offset':offset,'length':len(b),'sha256':sha(b),'stage':str(s)})
    require(len(ranges)==21,'range count');gates()
    tx=transaction(v,NAS/'archive',m)
    def invoke(mode,path,c):
        command=[sys.executable,'-B',__file__,'--child',mode,str(path),c['name'],str(c['offset']),c['stage'],c['sha256']]
        r=subprocess.run(command,capture_output=True,text=True,timeout=35)
        require(r.returncode in [91,92,93],'worker failed unexpectedly: '+r.stderr[-2000:])
        return r.returncode
    first=ranges[0];mp=SCRATCH/'controls/SOURCE_MANIFEST.json'
    rc=invoke('before_chunk_record',mp,first);require(rc==91,'wrong first crash')
    tx=transaction(v,NAS/'archive',m)
    tx.reconcile_partial_chunk(first['name'],first['offset'],first['sha256'],first['length'])
    tx.accept_chunk(first['name'],first['offset'],first['stage'],first['sha256'],txid=tx.txid)
    passed('actual_process_crash_before_receipt_and_exact_orphan_adoption',{'worker_exit':rc,'txid':tx.txid,'range_bytes':first['length'],'new_payload_reuploaded_on_adoption':0})
    second=ranges[1];rc=invoke('after_chunk_record',mp,second);require(rc==92,'wrong second crash')
    tx=transaction(v,NAS/'archive',m);key=chunk_key(v,second['name'],second['offset']);old=(tx.work/'chunks'/(key+'.json')).read_bytes();s=(tx.work/'chunks'/key).stat()
    tx.accept_chunk(second['name'],second['offset'],second['stage'],second['sha256'],txid=tx.txid)
    require((tx.work/'chunks'/(key+'.json')).read_bytes()==old and (tx.work/'chunks'/key).stat().st_mtime_ns==s.st_mtime_ns,'duplicate overwrote receipt/chunk')
    passed('actual_process_crash_after_receipt_duplicate_reuse',{'worker_exit':rc,'new_payload_reuploaded':0,'record_bytes_unchanged':True})
    # Isolated incomplete partial and range-gap negatives retain at most96KiB.
    payload=next(c for c in ranges if c['name']=='payload.bin' and c['offset']==0)
    negm=copy.deepcopy(m);negm['genuine164_destination_root']=NATIVE+'/negative_incomplete';negm['destination_path_on_174new']=str(NAS/'negative_incomplete')
    negmp=SCRATCH/'controls/INCOMPLETE_MANIFEST.json';v.exclusive_json(negmp,negm)
    rc=invoke('incomplete',negmp,payload);require(rc==93,'wrong incomplete crash');nt=transaction(v,NAS/'negative_incomplete',negm)
    refuses('truncated_network_partial_HOLD',lambda:nt.reconcile_partial_chunk(payload['name'],0,payload['sha256'],payload['length']))
    require(not nt.final.exists(),'incomplete transaction has final')
    payloadrow=next(r for r in m['files'] if r['relative_path']=='payload.bin')
    gapm=manifest_for(v,NAS/'negative_gap',[payloadrow],[m['directories'][0]],publication)
    gt=transaction(v,NAS/'negative_gap',gapm);g=next(c for c in ranges if c['name']=='payload.bin' and c['offset']==CHUNK)
    gt.accept_chunk(g['name'],g['offset'],g['stage'],g['sha256'],txid=gt.txid)
    refuses('gap_refuses_COMMIT',gt.finalize);require(not (gt.final/'COMMIT.json').exists(),'gap committed')
    refuses('wrong_txid',lambda:tx.accept_chunk(first['name'],0,first['stage'],first['sha256'],txid='0'*64))
    refuses('wrong_chunk_SHA',lambda:tx.accept_chunk(first['name'],0,first['stage'],'0'*64,txid=tx.txid))
    bad=copy.deepcopy(m);bad['files'][0]['sha256']='0'*64
    refuses('changed_manifest_selector',lambda:v.validate_manifest(bad))
    refuses('path_traversal',lambda:v.relpath('../outside'))
    refuses('wrong_mount_projection',lambda:v.mount_identity(NAS,observed={'target':'/root/share','source':'/dev/md127','fstype':'ext4'}))
    collision=NAS/'negative_collision.json';v.exclusive_json(collision,{'frozen':1});before=collision.read_bytes()
    refuses('differing_existing_destination_no_overwrite',lambda:v.exclusive_json(collision,{'frozen':2}));require(collision.read_bytes()==before,'collision changed')
    for c in ranges[2:]:
        gates();tx.accept_chunk(c['name'],c['offset'],c['stage'],c['sha256'],txid=tx.txid);gates()
    final=tx.finalize();gates();commit=(final/'COMMIT.json').read_bytes()
    for row in m['files']:require(v.hash_file(final/'tree'/row['relative_path'])==row['sha256'],'archive whole raw SHA')
    passed('whole_archive_COMMIT_last_and_SHA',{'txid':tx.txid,'ranges':21,'files':4,'original_bytes':1314816,'archive_root':str(final),'commit_sha256':sha(commit)})
    require(tx.finalize()==final and (final/'COMMIT.json').read_bytes()==commit,'duplicate final changed')
    passed('duplicate_final_commit_reused',{'commit_sha256':sha(commit),'no_overwrite':True})
    dst=SCRATCH/'restored'
    restored=v.native_restore(final/'tree',m,dst)
    require(restored['numeric_metadata_verified'] and len(restored['files'])==4,'native restore incomplete')
    passed('independent_native_Target_restore',{'status':'RESTORE_VERIFIED_NATIVE_TARGET','files':4,'directories':3,'raw_bytes':1314816,'uid_gid_mode_mtime_ns':True,'target':str(dst),'not_native164':True})
    refuses('populated_restore_refused',lambda:v.native_restore(final/'tree',m,dst))
    for row in m['files']:require(v.hash_file(fixtures/row['relative_path'],expected={k:row[k] for k in v.identity((fixtures/row['relative_path']).stat())})==row['sha256'],'synthetic source changed')
    passed('four_axes_SOURCE_KEEP',{'science':'NOT_EVALUATED_SYNTHETIC_ONLY','archive':'ARCHIVE_VERIFIED','restore':'RESTORE_VERIFIED_NATIVE_TARGET','local_reclaim':'SOURCE_KEEP','source_released_bytes':0})
    report={'schema':'RESULT_OFFLOAD_PHASE2_SYNTHETIC_RESULT_V1','status':'PASS','utc':utc(),'txid':tx.txid,'manifest_sha256':sha(canonical(m)),'tool_publication_commit':publication,'driver_sha256':sha(Path(__file__).read_bytes()),'v9_sha256':V9_SHA,'cases':cases,'case_count':len(cases),'files':4,'directories':3,'raw_bytes':1314816,'nonempty_ranges':21,'archive':'ARCHIVE_VERIFIED','restore':'RESTORE_VERIFIED_NATIVE_TARGET','persistent_archive_root':str(final),'native_restore_root':str(dst),'science':'NOT_EVALUATED_SYNTHETIC_ONLY','source_action':'SOURCE_KEEP','existing_files_deleted_moved_overwritten':0,'source_released_bytes':0,'retained_fault_and_stage_evidence':True,'initial_admission':initial,'observed_peaks_before_result_receipts':dict(PEAKS),'parent_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'largest_child_maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'elapsed_seconds':time.monotonic()-start,'peak_accounting':'All new stage/fault data retained; only V9 LINK alias finalization removes owned temporary names without releasing underlying blocks. Allocated st_blocks inventory deduplicates hardlink identities.'}
    v.exclusive_json(SCRATCH/'controls/FINAL_SYNTHETIC_RESULT.json',report);v.exclusive_json(NAS/'FINAL_SYNTHETIC_RESULT.json',report);v.exclusive_json(NAS/'SOURCE_MANIFEST.json',m)
    final_resource=gates();output={'result':report,'final_resource_including_result_receipts':final_resource,'observed_peaks_including_receipts':PEAKS,'persistent_result_receipt_sha256':sha((NAS/'FINAL_SYNTHETIC_RESULT.json').read_bytes())}
    print(json.dumps(output),flush=True)
    # Closing releases only this process's existing flock; never unlink the lock.
    lock.close()

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child':worker()
    else:run()
