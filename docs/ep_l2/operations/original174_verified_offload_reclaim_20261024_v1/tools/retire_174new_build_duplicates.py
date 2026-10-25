"""Retire only the exact qualified cold 174-new compiler copies.

Uses existing global locks without replacing them. No frozen115 state edits.
Keeps directories and all non-whitelisted files. Each unlink has durable intent
and a closed/reopened genuine164 SHA, plus a final native full SHA check.
"""
import os, sys, json, time, hashlib, pathlib, fcntl, stat, traceback
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import qualify_174new_build_duplicates as q
P=pathlib.Path
OUT=q.OUT
DEST=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/174new_build_duplicate_retirement_v1')
BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
RESTORE = r'''#!/usr/bin/env python3
"""Explicit exact restoration; never overwrites an existing local file."""
import os,json,hashlib,pathlib,sys,time,fcntl
P=pathlib.Path
sys.path.insert(0,'/root/data/research_asset_verified_offload_20261024_v1/tools')
import server_resources as resources
lease=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock','rb')
fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
M=json.loads((P(__file__).parent/'QUALIFIED.json').read_bytes())
for x in M['files']:
 p=P(x['source']); a=P(x['archive']['path']); expected=x['sha256']
 assert p.is_relative_to('/root') and '/src/gpgpu-sim/build/' in str(p) and p.suffix in ('.o','.a')
 if p.exists():
  assert p.is_file() and not p.is_symlink()
  with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected,'existing file differs: '+str(p)
  continue
 assert p.parent.is_dir() and p.parent.resolve()==p.parent,'restore parents changed'
 gate=resources.admission('TARGET',allowed_lock_pids=(os.getpid(),))
 s=os.statvfs('/root/data');assert s.f_bavail*s.f_frsize>=gate['SSD_required_bytes']+x['identity']['size'],'restore requires original admission plus complete-file temporary capacity'
 tmp=p.with_name(p.name+'.T2_exact_restore.writing');h=hashlib.sha256()
 with a.open('rb') as src,tmp.open('xb') as out:
  while True:
   t=time.monotonic();b=src.read(1024**2)
   if not b:break
   h.update(b);out.write(b);time.sleep(max(0,len(b)/(15*1024**2)-(time.monotonic()-t)))
  out.flush();os.fsync(out.fileno())
 assert h.hexdigest()==expected and tmp.stat().st_size==x['identity']['size']
 with tmp.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
 i=x['identity'];os.chown(tmp,i['uid'],i['gid']);os.chmod(tmp,i['mode']&0o7777)
 os.utime(tmp,ns=(i['mtime_ns'],i['mtime_ns']))
 os.link(tmp,p);tmp.unlink()
print('Exact compiler copies restored; ctime is historical provenance only.')
'''

def free():
    v=os.statvfs('/root/data');return v.f_bavail*v.f_frsize

def blob(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()

def put(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==b,'immutable collision '+str(p);return
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    assert p.read_bytes()==b,'closed receipt mismatch'
    fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def pair(name,x):
    b=blob(x);put(DEST/name,b);put(OUT/name,b)

def deps(roots,files):
    bad=q.references(roots,[(x['identity']['dev'],x['identity']['ino']) for x in files])
    assert not bad,'current reader/writer or working directory appeared '+repr(bad)
    p=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
    r=json.loads(p.read_bytes());future=json.dumps(r.get('registered_future_requests',{}))
    assert not any(str(root) in future for root in roots),'planned scientific reader appeared'
    return {'current_users':bad,'planned_reader_registry_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'review_scope':'cold compiler intermediates only; runtime binaries/source/inputs/results remain local; future compilation can regenerate or explicitly restore exact copies'}

def main():
    q.mount_check(); assert not (OUT/'DONE.json').exists(),'already DONE; never replay'
    raw=(OUT/'QUALIFIED.json').read_bytes();m=json.loads(raw);files=m['files']
    assert files and sum(x['identity']['blocks']*512 for x in files)>=1024**3,'insufficient exact qualified copies'
    assert not (OUT/'INTENT.json').exists(),'existing INTENT requires per-file transaction recovery, not blind rerun'
    locks=[]
    for name in ['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock']:
        f=(BRIDGE/name).open('rb');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
    own=(OUT/'RETIREMENT.lock').open('a+b');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
    roots=sorted({P(x['runtime_root']) for x in files});before=free()
    dep=deps(roots,files)
    for x in files:
        p=P(x['source']);a=P(x['archive']['path'])
        assert p.is_relative_to('/root') and p.resolve()==p and p.suffix in ('.o','.a')
        assert p.is_relative_to(P(x['runtime_root'])/'src/gpgpu-sim/build')
        assert '.git' not in p.parts and q.identity(p)==x['identity'],'local frozen identity changed'
        assert a.is_relative_to(q.NAS) and a.resolve()==a and q.identity(a)==x['archive']['identity'],'true164 reference changed'
    put(DEST/'QUALIFIED.json',raw)
    put(DEST/'RESTORE.py',RESTORE.encode());put(OUT/'RESTORE.py',RESTORE.encode())
    # Exercise one complete largest-file restoration under the unchanged
    # <=256MiB staging contract; it is removed only after closed SHA/metadata.
    x=max(files,key=lambda x:x['identity']['size']);a=P(x['archive']['path'])
    test=OUT/'INDEPENDENT_RESTORE_TEST.payload';assert not test.exists()
    assert x['identity']['size']<=128*1024**2 and before>=7*1024**3+256*1024**2
    h=hashlib.sha256()
    with a.open('rb') as src,test.open('xb') as dst:
        while True:
            t=time.monotonic();b=src.read(1024**2)
            if not b:break
            dst.write(b);h.update(b);time.sleep(max(0,len(b)/q.RATE-(time.monotonic()-t)))
        dst.flush();os.fsync(dst.fileno())
    assert h.hexdigest()==x['sha256']
    i=x['identity'];os.chown(test,i['uid'],i['gid']);os.chmod(test,i['mode']&0o7777);os.utime(test,ns=(i['mtime_ns'],i['mtime_ns']))
    h,ti=q.digest(test)
    assert h==x['sha256'] and all(ti[k]==i[k] for k in ['size','uid','gid','mtime_ns','mode'])
    pair('RESTORE_TEST.json',{'source':x['source'],'archive':str(a),'sha256':h,'bytes':ti['size'],'closed_native_full_SHA_and_numeric_metadata':True,'scope':'one largest complete compiler file, not all files restored','temporary_test_unlink_intent':str(test),'test_identity':ti})
    assert q.identity(test)==ti;test.unlink()
    pair('RESTORE_TEST_DONE.json',{'test_path':str(test),'absent':not test.exists(),'verified_test_allocated_bytes_unlinked':ti['blocks']*512,'not_counted_as_original_copy_reclaim':True})
    pair('COMMIT.json',{'schema':'EXISTING_TRUE164_EXACT_COMPILER_COPY_REFERENCE_COMMIT_V1','qualified_sha256':hashlib.sha256(raw).hexdigest(),'files':len(files),'logical_bytes':m['logical_bytes'],'all_referenced_true164_files_closed_full_SHA_verified':True,'restore_script_sha256':hashlib.sha256(RESTORE.encode()).hexdigest(),'new_frozen115_archive_bytes':0,'created_unix':time.time()})
    dep=deps(roots,files)
    pair('INTENT.json',{'schema':'EXACT_174NEW_COMPILER_DUPLICATE_UNLINK_INTENT_V1','qualification_sha256':hashlib.sha256(raw).hexdigest(),'files':len(files),'logical_bytes':m['logical_bytes'],'allocated_bytes':m['allocated_bytes'],'SSD_free_before':before,'reader_audit':dep,'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'created_unix':time.time(),'authorization':'User 2026-10-25 additional 174-new verified-copy retirement instruction; original protection and resource contract preserved'})
    records=[]; last=time.monotonic()
    for k,x in enumerate(files):
        p=P(x['source']);a=P(x['archive']['path']);q.mount_check()
        if time.monotonic()-last>=20:deps(roots,files);last=time.monotonic()
        assert q.identity(p)==x['identity'] and q.identity(a)==x['archive']['identity']
        ah,ai=q.digest(a);assert ah==x['sha256'] and ai==x['archive']['identity'],'true164 full SHA drift'
        sh,si=q.digest(p);assert sh==x['sha256'] and si==x['identity'],'local final full SHA drift'
        assert not q.references([P(x['runtime_root'])],[(si['dev'],si['ino'])]),'user appeared before unlink'
        assert q.identity(p)==si and q.identity(a)==ai
        # Per-file intent binds the final two full SHA reads before unlink.
        pair('per_file/%06d.INTENT.json'%k,{'index':k,'source':str(p),'sha256':sh,'identity':si,'archive_identity':ai,'created_unix':time.time()})
        p.unlink()
        record={'index':k,'source':str(p),'sha256':sh,'logical_bytes':si['size'],'allocated_bytes':si['blocks']*512,'absent_after_unlink':not p.exists(),'finished_unix':time.time()}
        pair('per_file/%06d.DONE.json'%k,record);records.append(record)
        if k%100==0:print(json.dumps({'phase':'UNLINK_VERIFIED_DUPLICATES','files':len(records),'allocated':sum(r['allocated_bytes'] for r in records),'SSD_free':free()}),flush=True)
    after=free();pair('DONE.json',{'status':'EXACT_VERIFIED_174NEW_COMPILER_DUPLICATES_RETIRED','files':len(records),'logical_bytes_unlinked':sum(r['logical_bytes'] for r in records),'allocated_bytes_unlinked':sum(r['allocated_bytes'] for r in records),'SSD_free_before':before,'SSD_free_after':after,'observed_SSD_free_interval_delta':after-before,'interval_delta_is_not_exclusive_causal_attribution':True,'new_frozen115_archive_bytes':0,'source_old174_unlink_bytes':0,'all_whitelisted_paths_absent':all(not P(x['source']).exists() for x in files),'directories_and_nonwhitelisted_files_preserved':True,'recovery_entry':str(DEST/'RESTORE.py'),'finished_unix':time.time()})
    assert after>before,'no measurable SSD free-space recovery; stop further retirement'
    print(json.dumps(json.loads((OUT/'DONE.json').read_bytes())),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as e:
        OUT.mkdir(parents=True,exist_ok=True)
        # Never overwrite an existing failure/intent/done record.
        p=OUT/('FAILURE_%d.json'%time.time_ns())
        put(p,blob({'error':repr(e),'traceback':traceback.format_exc(),'observed_unix':time.time(),'no_automatic_blind_replay':True}))
        raise
