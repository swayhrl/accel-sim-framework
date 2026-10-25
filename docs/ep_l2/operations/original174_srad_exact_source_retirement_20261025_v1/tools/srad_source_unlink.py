"""Old174 exact SRAD source retirement worker; invoked by the new174 controller."""
import fcntl,hashlib,io,json,os,pathlib,stat,sys,time,traceback
P=pathlib.Path;MIB=1024**2;RATE=15*MIB
T=P('/root/data/research_asset_verified_offload_20261024_v1');OUT=T/'control/srad_exact_retirement_v1';BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
ROOT=P('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/srad_v1-rodinia-3.1/100_0_5_502_458/traces')

def need(v,m):
    if not v:raise RuntimeError(m)
def blob(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def put(p,x):
    p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=blob(x);need(not p.exists(),'immutable receipt collision '+str(p))
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    need(p.read_bytes()==b,'receipt reopen mismatch')
def identity(p):
    s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
def same(a,b):return all(a[k]==b[k] for k in ['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','nlink','type'])
def same_numeric(a,b):return all(a[k]==b[k] for k in ['size','mtime_ns','uid','gid','mode'])
def free():
    v=os.statvfs('/root/data');return v.f_bavail*v.f_frsize
def pressure():
    return {line.split()[0]:{x.split('=')[0]:float(x.split('=')[1]) for x in line.split()[1:]} for line in P('/proc/pressure/io').read_text().splitlines()}
def gate():
    io=pressure();need(io['some']['avg60']<25 and io['full']['avg60']<20,'RESOURCE_HOLD_SUSTAINED_SEVERE_HOST_IO');return io
def full_hash(p):
    before=identity(p);h=hashlib.sha256();count=0;started=time.monotonic()
    with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0)),'rb',buffering=0) as f:
        while True:
            b=f.read(MIB)
            if not b:break
            h.update(b);count+=len(b);time.sleep(max(0,count/RATE-(time.monotonic()-started)))
            if count%(256*MIB)<MIB:gate()
    need(same(before,identity(p)),'identity changed during SHA '+str(p));return h.hexdigest(),before
def references(p,root):
    target=identity(p);bad=[]
    for proc in P('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
        try:
            raw=(proc/'stat').read_text().rsplit(')',1)[1].split();base=dict(pid=int(proc.name),start_ticks=int(raw[19]),state=raw[0]);cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            if str(root) in cmd:bad.append(dict(base,kind='cmdline'))
            for kind in ['cwd','exe']:
                try:value=os.readlink(proc/kind)
                except OSError:continue
                if value==str(root) or value.startswith(str(root)+'/'):bad.append(dict(base,kind=kind,value=value))
            try:fds=list((proc/'fd').iterdir())
            except OSError:fds=[]
            for fd in fds:
                try:s=fd.stat();value=os.readlink(fd)
                except OSError:continue
                if (s.st_dev,s.st_ino)==(target['dev'],target['inode']):bad.append(dict(base,kind='fd',fd=fd.name,value=value))
            try:
                if str(p) in (proc/'maps').read_text(errors='replace'):bad.append(dict(base,kind='maps'))
            except OSError:pass
        except (OSError,ValueError,IndexError):pass
    return bad
def planned_reader_check():
    out={}
    for name,path in [('source','/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json'),('native','/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')]:
        raw=P(path).read_bytes();need(str(ROOT) not in raw.decode(errors='replace'),name.upper()+'_REGISTRY_PLANNED_READER_APPEARED');out[name]=hashlib.sha256(raw).hexdigest()
    return out
def restore_test(row,payload):
    dest=ROOT/row['relative_path'];temp=dest.with_name(dest.name+'.SRAD_test_restore.writing');need(not os.path.lexists(dest) and not os.path.lexists(temp),'test restore collision');h=hashlib.sha256()
    with io.BytesIO(payload) as src,temp.open('xb') as out:
        while True:
            b=src.read(MIB)
            if not b:break
            out.write(b);h.update(b)
        out.flush();os.fsync(out.fileno())
    need(h.hexdigest()==row['sha256'] and temp.stat().st_size==row['size'],'test payload restore SHA mismatch');os.chown(temp,row['uid'],row['gid']);os.chmod(temp,row['mode']);os.utime(temp,ns=(row['mtime_ns'],row['mtime_ns']));os.link(temp,dest);temp.unlink();need(full_hash(dest)[0]==row['sha256'] and same_numeric(identity(dest),row),'test source restore verification failed')
def main(test_payload):
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'wrong Source endpoint')
    lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    intent=json.loads((OUT/'INTENT.json').read_bytes());need(intent['schema']=='ORIGINAL174_SRAD_EXACT_RETIREMENT_INTENT_V1','INTENT identity changed')
    qualification=json.loads((OUT/'QUALIFIED_WHITELIST.json').read_bytes());rows=qualification['files'];need(len(rows)==502 and all(x['relative_path'].endswith('.traceg') for x in rows),'whitelist changed')
    source_sha=json.loads((OUT/'SOURCE_FULL_SHA_REVERIFY.json').read_bytes());byname={x['relative_path']:x for x in source_sha['rows']};need(source_sha['all_manifest_SHA_identity_match'] and set(byname)>={x['relative_path'] for x in rows},'Source SHA evidence changed')
    need(ROOT.is_dir() and not ROOT.is_symlink(),'Source root changed');root_before=identity(ROOT);controls=intent['controls']
    for row in controls:
        p=ROOT/row['relative_path'];need(p.is_file() and not p.is_symlink() and same(identity(p),row['identity']) and full_hash(p)[0]==row['sha256'],'control changed '+str(p))
    need(not references(ROOT/rows[0]['relative_path'],ROOT),'Source reader appeared');registry_sha=planned_reader_check();gate();before_df=free();smallest=min(rows,key=lambda x:(x['size'],x['relative_path']));need(len(test_payload)==smallest['size'] and hashlib.sha256(test_payload).hexdigest()==smallest['sha256'],'test recovery payload mismatch')
    ordered=sorted(rows,key=lambda x:(x['size'],x['relative_path']));logical=0;allocated=0;done=[];last_registry=time.monotonic()
    for index,row in enumerate(ordered):
        p=ROOT/row['relative_path'];need(p.is_file() and not p.is_symlink(),'whitelisted Source missing '+str(p));q=byname[row['relative_path']];need(same(identity(p),row['identity']),'qualified Source identity changed')
        sha,current=full_hash(p);need(sha==row['sha256']==q['sha256'],'final Source full SHA mismatch');need(not references(p,ROOT),'active Source reader appeared '+str(p));gate()
        if time.monotonic()-last_registry>=20:registry_sha=planned_reader_check();last_registry=time.monotonic()
        df0=free();file_intent=dict(schema='SRAD_EXACT_FILE_UNLINK_INTENT_V1',index=index,relative_path=row['relative_path'],source=str(p),sha256=sha,identity=current,df_before=df0,registry_sha256=registry_sha,reader_refs=[],unix=time.time());put(OUT/'per_file'/('%06d.INTENT.json'%index),file_intent)
        need(same(identity(p),current),'Source changed after INTENT');p.unlink();fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
        df1=free();record=dict(schema='SRAD_EXACT_FILE_UNLINK_DONE_V1',index=index,relative_path=row['relative_path'],sha256=sha,logical_bytes=current['size'],allocated_bytes=current['allocated'],absent=not p.exists(),df_before=df0,df_after=df1,df_interval_delta=df1-df0,unix=time.time());need(record['absent'],'unlink did not remove exact path');put(OUT/'per_file'/('%06d.DONE.json'%index),record)
        if index==0:
            if df1<=df0:
                restore_test(row,test_payload);os.chown(ROOT,root_before['uid'],root_before['gid']);os.chmod(ROOT,root_before['mode']);os.utime(ROOT,ns=(root_before['mtime_ns'],root_before['mtime_ns']));put(OUT/'TEST_RECLAIM_FAILED_AND_SOURCE_RESTORED.json',dict(test_file=row['relative_path'],allocated_bytes=current['allocated'],df_before=df0,df_after=df1,df_delta=df1-df0,restored_full_SHA=True,unix=time.time()));raise RuntimeError('NO_POSITIVE_SSD_DF_RECLAIM_TEST_SOURCE_RESTORED')
            put(OUT/'TEST_RECLAIM_PASS.json',dict(test_file=row['relative_path'],logical_bytes=current['size'],allocated_bytes=current['allocated'],df_before=df0,df_after=df1,df_delta=df1-df0,unix=time.time()))
        done.append(record);logical+=current['size'];allocated+=current['allocated']
        if len(done)%25==0:print(json.dumps({'phase':'SRAD_EXACT_UNLINK','done':len(done),'logical':logical,'allocated':allocated,'df_available':df1}),flush=True)
    os.chown(ROOT,root_before['uid'],root_before['gid']);os.chmod(ROOT,root_before['mode']);os.utime(ROOT,ns=(root_before['mtime_ns'],root_before['mtime_ns']))
    need(not any(ROOT.rglob('*.traceg')),'whitelisted traceg remains')
    for row in controls:
        p=ROOT/row['relative_path'];need(p.is_file() and not p.is_symlink() and same(identity(p),row['identity']) and full_hash(p)[0]==row['sha256'],'control changed after retirement')
    after_df=free();result=dict(schema='ORIGINAL174_SRAD_EXACT_SOURCE_RETIREMENT_DONE_V1',status='DONE',unix=time.time(),files=len(done),logical_bytes_unlinked=logical,allocated_bytes_unlinked=allocated,df_before=before_df,df_after=after_df,df_interval_delta=after_df-before_df,interval_delta_not_exclusive_causal_attribution=True,controls_preserved=[x['relative_path'] for x in controls],source_root_preserved=True,source_root_mtime_mode_uid_gid_restored=True,source_root_ctime_not_restorable=True,recursive_delete_used=False,lavaMD_or_HybridSort_changes=0,science_or_controller_changes=0)
    put(OUT/'DONE.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
    try:main(sys.stdin.buffer.read())
    except BaseException as e:
        p=OUT/('FAILURE_%d.json'%time.time_ns());put(p,dict(error=repr(e),traceback=traceback.format_exc(),unix=time.time(),no_blind_retry=True));raise
