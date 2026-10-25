"""Finite two-thread lstat-only preflight of remaining frozen Trace members.

No payload opens, hashing, sender/receiver ownership, queue changes or Source
writes. Main execution must independently revalidate everything at admission.
At most20 metadata operations/second across both threads, at most15 minutes.
"""
import os,sys,json,time,pathlib,gzip,hashlib,stat,threading,concurrent.futures
P=pathlib.Path
T=P('/root/data/research_asset_verified_offload_20261024_v1')
FROZEN_SHA='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04'
lock=threading.Lock();next_slot=0.;deadline=0.;checked=0

def paced_stat(path):
    global next_slot,checked
    with lock:
        now=time.monotonic();slot=max(now,next_slot);next_slot=slot+0.05
    if slot>deadline:raise TimeoutError('finite metadata-preflight deadline')
    time.sleep(max(0,slot-time.monotonic()))
    value=path.lstat()
    with lock:checked+=1
    return value

def actual(s):
    return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=s.st_mode&0o7777,type='file' if stat.S_ISREG(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'other')

def inspect(scope):
    root=P(scope['source_root']);mismatches=[];verified=0
    for row in scope['files']:
        rel=P(row['relative_path'])
        if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('untrusted frozen relative path')
        expected={k:row[k] for k in ['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','type']}
        if isinstance(expected['mode'],str):expected['mode']=int(expected['mode'],8)
        try:
            observed=actual(paced_stat(root/rel));changed=[k for k in expected if observed[k]!=expected[k]]
            if changed:mismatches.append(dict(relative_path=str(rel),changed_fields=changed))
            else:verified+=1
        except OSError as e:mismatches.append(dict(relative_path=str(rel),error=repr(e)))
    return dict(asset_id=scope['asset_id'],members=len(scope['files']),identity_matches=verified,mismatches=mismatches,status='PREFLIGHT_IDENTITIES_MATCH' if not mismatches else 'PRECHECK_ATTENTION_REQUIRED',body_SHA_verified_by_this_preflight=False,copy_admission_granted=False)

def main():
    global deadline
    assert os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
    raw=(T/'control/FROZEN_SCOPES.json.gz').read_bytes();assert hashlib.sha256(raw).hexdigest()==FROZEN_SHA
    scopes=json.loads(gzip.decompress(raw))['scopes'];rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()];done={z['asset_id'] for z in rows if z['status']=='ARCHIVED_CONTENT_VERIFIED'};state=json.loads((T/'control/STATE.json').read_bytes())
    remaining=[z for z in scopes if z['kind']=='TRACE' and z['source_alias']=='hrl' and z['asset_id'] not in done and z['asset_id']!=state['asset_id'] and not (T/'manifests'/(z['asset_id']+'.json')).exists()]
    started=time.monotonic();deadline=started+900
    print(json.dumps({'phase':'PARALLEL_METADATA_PREFLIGHT_STARTED','assets':len(remaining),'members':sum(len(z['files']) for z in remaining),'threads':2,'metadata_operations_per_second_max':20,'payload_reads':0}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(inspect,z):z['asset_id'] for z in remaining};results=[]
        for f in concurrent.futures.as_completed(futures):
            try:results.append(f.result())
            except Exception as e:results.append(dict(asset_id=futures[f],status='PRECHECK_INCOMPLETE',error=repr(e)))
    result={'schema':'FROZEN_REMAINING_TRACE_PARALLEL_METADATA_PREFLIGHT_V1','unix':time.time(),'elapsed_seconds':time.monotonic()-started,'frozen_queue_sha256':FROZEN_SHA,'assets':len(remaining),'metadata_checks':checked,'threads':2,'metadata_operations_per_second_max':20,'results':results,'Source_payload_opens_or_reads':0,'Source_writes':0,'new_senders_receivers_drivers_supervisors_publishers':0,'science_or_controller_changes':0,'queue_or_checkpoint_reset':False,'copy_admission_granted':False,'scope_limit':'Advisory frozen-file identity preflight only. Full SHA, current reader/writer/resource admission and manifest creation remain with the original Driver.'}
    dest=T/'control/parallel_metadata_preflight_v1';dest.mkdir(exist_ok=True)
    target=dest/'RESULT.json';assert not target.exists(),'preserve prior result; no blind duplicate preflight'
    with target.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'phase':'PARALLEL_METADATA_PREFLIGHT_DONE','assets':len(results),'identity_PASS':sum(z['status']=='PREFLIGHT_IDENTITIES_MATCH' for z in results),'attention':sum(z['status']!='PREFLIGHT_IDENTITIES_MATCH' for z in results),'checks':checked,'elapsed':result['elapsed_seconds'],'result':str(target)}),flush=True)

if __name__=='__main__':main()
