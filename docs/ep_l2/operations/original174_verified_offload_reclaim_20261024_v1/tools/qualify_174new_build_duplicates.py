"""One finite read-only qualification of cold compiler duplicates on genuine164.

No archive payload writes, unlink, process signals or task-state modification.
Run remotely in the 174-new mount namespace. Bodies read serially at <=15MiB/s.
"""
import os, sys, stat, json, hashlib, time, pathlib, subprocess
P = pathlib.Path
T = P('/root/data/research_asset_verified_offload_20261024_v1')
OUT = T / 'control/174new_build_duplicate_retirement_v1'
NAS = P('/root/share/mnt164/huangrulin/archived_runtimes_174new')
RATE = 15 * 1024**2

def identity(p):
    s=p.lstat()
    return {k:getattr(s,'st_'+k) for k in ('dev','ino','mode','size','mtime_ns','ctime_ns','uid','gid','nlink','blocks')}

def digest(p):
    before=identity(p); assert stat.S_ISREG(before['mode']) and before['nlink']==1
    h=hashlib.sha256(); start=time.monotonic(); n=0
    with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0)), 'rb') as f:
        while True:
            b=f.read(1024**2)
            if not b: break
            h.update(b); n+=len(b)
            time.sleep(max(0,n/RATE-(time.monotonic()-start)))
    assert identity(p)==before, 'identity drift '+str(p)
    return h.hexdigest(),before

def mount_check():
    assert os.uname().nodename=='huangrulin-sshfs-174'
    assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
    m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS)],text=True))['filesystems'][0]
    assert m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs'

def references(roots, selected=None):
    bad=[]; needles=[str(p) for p in roots]; keys=set(selected or [])
    for proc in P('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
        try:
            cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            if any(n in cmd for n in needles):bad.append([proc.name,'cmdline',cmd[:500]])
            for what in ['cwd','exe']:
                try:s=os.readlink(proc/what)
                except OSError:continue
                if any(s==n or s.startswith(n+'/') for n in needles):bad.append([proc.name,what,s])
            for fd in (proc/'fd').iterdir():
                try:
                    s=os.readlink(fd); v=fd.stat()
                    if any(s==n or s.startswith(n+'/') for n in needles) or (v.st_dev,v.st_ino) in keys:bad.append([proc.name,'fd',s])
                except OSError:pass
            maps=(proc/'maps').read_text()
            if any(n in maps for n in needles):bad.append([proc.name,'maps'])
        except (OSError,ProcessLookupError):continue
    return bad

def atomic(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    assert p.read_bytes()==b

def main():
    mount_check(); assert not (OUT/'QUALIFIED.json').exists(),'qualification already exists; inspect and reuse'
    index={}
    for top in sorted(NAS.iterdir()):
        root=top/'src/gpgpu-sim/build'
        for d,ds,fs in os.walk(root,followlinks=False):
            ds[:]=[n for n in ds if n!='.git' and not (P(d)/n).is_symlink()]
            for n in fs:
                p=P(d)/n; s=p.lstat()
                if p.suffix in ('.o','.a') and stat.S_ISREG(s.st_mode) and 0<s.st_size<=128*1024**2:
                    index.setdefault(s.st_size,[]).append(p)
    roots=[]; candidates=[]
    for root in sorted(P('/root').glob('awma_*_runtime')):
        if root.is_symlink() or not root.is_dir():continue
        build=root/'src/gpgpu-sim/build'
        if not build.is_dir() or build.is_symlink():continue
        roots.append(root)
        for d,ds,fs in os.walk(build,followlinks=False):
            ds[:]=[n for n in ds if n!='.git' and not (P(d)/n).is_symlink()]
            for n in fs:
                p=P(d)/n;s=p.lstat()
                if p.suffix in ('.o','.a') and stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size in index:
                    candidates.append((p,root))
    active=references(roots); active_roots={r for r in roots if any(str(r) in json.dumps(b) for b in active)}
    registry=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
    regraw=registry.read_bytes(); reg=json.loads(regraw)
    planned=json.dumps(reg.get('registered_future_requests',{}))
    planned_roots={r for r in roots if str(r) in planned}
    excluded=active_roots|planned_roots
    needed={p.stat().st_size for p,r in candidates if r not in excluded}
    hashes={}; count=0
    for size in sorted(needed):
        for p in index[size]:
            h,i=digest(p);hashes.setdefault((size,h),[]).append({'path':str(p),'identity':i})
            count+=1
        if count%25==0:print(json.dumps({'phase':'TRUE164_FULL_SHA','files':count}),flush=True)
    admitted=[]; mismatch=0
    for k,(p,root) in enumerate(candidates):
        if root in excluded:continue
        h,i=digest(p); matches=hashes.get((i['size'],h))
        if matches:admitted.append({'source':str(p),'runtime_root':str(root),'identity':i,'sha256':h,'archive':matches[0]})
        else:mismatch+=1
        if k%100==0:print(json.dumps({'phase':'LOCAL_FULL_SHA','examined':k+1,'qualified':len(admitted),'allocated':sum(x['identity']['blocks']*512 for x in admitted)}),flush=True)
    final_roots=sorted({P(x['runtime_root']) for x in admitted})
    assert not references(final_roots,[(x['identity']['dev'],x['identity']['ino']) for x in admitted]),'reader appeared'
    # Active DTC science may legitimately update its counters during hashing.
    # Recheck only the dependency question; never freeze a foreign registry.
    latest=json.loads(registry.read_bytes())
    assert not any(str(r) in json.dumps(latest.get('registered_future_requests',{})) for r in final_roots),'new planned dependency appeared'
    out={'schema':'174NEW_COLD_COMPILER_DUPLICATES_QUALIFIED_V1','created_unix':time.time(),'mount_namespace':os.readlink('/proc/self/ns/mnt'),'rate_bytes_per_second':RATE,'scope':'ONLY .o/.a compiler intermediates, not source/Git/binaries/inputs/results/controllers/models','planned_reader_audit':{'registry_path':str(registry),'registry_sha256':hashlib.sha256(regraw).hexdigest(),'matching_planned_roots':[str(r) for r in planned_roots]},'active_exclusions':active,'excluded_roots':[str(r) for r in excluded],'size_only_mismatches_not_admitted':mismatch,'files':admitted,'logical_bytes':sum(x['identity']['size'] for x in admitted),'allocated_bytes':sum(x['identity']['blocks']*512 for x in admitted),'deletion_performed':False}
    atomic(OUT/'QUALIFIED.json',out)
    print(json.dumps({'phase':'QUALIFIED','files':len(admitted),'logical':out['logical_bytes'],'allocated':out['allocated_bytes'],'path':str(OUT/'QUALIFIED.json')}),flush=True)

if __name__=='__main__':main()
