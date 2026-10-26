"""Old174 worker: unlink exactly one qualified lavaMD upper-layer trace."""
import fcntl,hashlib,json,os,pathlib,stat,sys,time,traceback
P=pathlib.Path;MIB=1024**2
T=P('/root/data/research_asset_verified_offload_20261024_v1');OUT=T/'control/lavamd_exact_retirement_v1';BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
ROOT=P('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/lavaMD-rodinia-3.1/_boxes1d_10/traces');TRACE=ROOT/'kernel-1.traceg'
def need(v,m):
 if not v:raise RuntimeError(m)
def blob(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def put(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=blob(x);need(not p.exists(),'immutable receipt collision '+str(p))
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);need(p.read_bytes()==b,'receipt reopen mismatch')
def identity(p):
 s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
def same(a,b):return all(a[k]==b[k] for k in ['dev','inode','size','allocated','mtime_ns','ctime_ns','uid','gid','mode','nlink','type'])
def free():
 v=os.statvfs('/root/data');return v.f_bavail*v.f_frsize
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(MIB),b''):h.update(b)
 return h.hexdigest()
def references(p,root):
 target=identity(p);bad=[];unreadable=[]
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
   except PermissionError:unreadable.append(int(proc.name));fds=[]
   except OSError:fds=[]
   for fd in fds:
    try:s=fd.stat();value=os.readlink(fd)
    except OSError:continue
    if (s.st_dev,s.st_ino)==(target['dev'],target['inode']):bad.append(dict(base,kind='fd',fd=fd.name,value=value))
   try:
    if str(p) in (proc/'maps').read_text(errors='replace'):bad.append(dict(base,kind='mmap'))
   except PermissionError:unreadable.append(int(proc.name))
   except OSError:pass
  except PermissionError:unreadable.append(int(proc.name))
  except (OSError,ValueError,IndexError):pass
 return bad,sorted(set(unreadable))
def main():
 need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'wrong Source endpoint')
 lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 intent=json.loads((OUT/'CONTINUE_INTENT_AFTER_CAPACITY_OVERRIDE.json').read_bytes());need(intent['schema']=='ORIGINAL174_LAVAMD_CONTINUE_INTENT_AFTER_CAPACITY_OVERRIDE_V1','intent changed')
 q=json.loads((OUT/'CONTINUE_QUALIFIED_WHITELIST.json').read_bytes());need(q['file']['relative_path']=='kernel-1.traceg' and q['file']['size']==20776255925,'whitelist changed')
 source=json.loads((OUT/'SOURCE_FULL_SHA_REVERIFY.json').read_bytes());row=next(x for x in source['rows'] if x['relative_path']=='kernel-1.traceg');need(row['sha256']==q['file']['sha256'] and same(identity(TRACE),q['file']['identity']),'Source evidence or identity changed')
 need(ROOT.is_dir() and not ROOT.is_symlink(),'Source root changed');root_before=identity(ROOT);controls=q['controls'];need({x.name for x in ROOT.iterdir()}=={'kernel-1.traceg','commandlist','kernelslist','kernelslist.g','stats.csv'},'Source membership changed')
 for c in controls:
  p=ROOT/c['relative_path'];need(p.is_file() and not p.is_symlink() and same(identity(p),c['identity']) and sha(p)==c['sha256'],'control changed '+c['relative_path'])
 refs,unreadable=references(TRACE,ROOT);need(not refs and not unreadable,'active or unreadable Source process')
 registries={}
 for name,path in [('source','/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json'),('native','/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')]:
  raw=P(path).read_bytes();need(str(ROOT) not in raw.decode(errors='replace'),name+' planned reader appeared');registries[name]=hashlib.sha256(raw).hexdigest()
 io={line.split()[0]:{x.split('=')[0]:float(x.split('=')[1]) for x in line.split()[1:]} for line in P('/proc/pressure/io').read_text().splitlines()};need(io['some']['avg60']<25 and io['full']['avg60']<20,'severe IO pressure')
 current=identity(TRACE);df0=free();file_intent=dict(schema='ORIGINAL174_LAVAMD_EXACT_FILE_UNLINK_INTENT_AFTER_CAPACITY_OVERRIDE_V1',unix=time.time(),source=str(TRACE),relative_path='kernel-1.traceg',sha256=row['sha256'],identity=current,df_before=df0,readers=[],unreadable_processes=[],registry_sha256=registries,capacity_override_sha256=intent['capacity_override_sha256']);put(OUT/'CONTINUE_FILE_INTENT.json',file_intent)
 refs2,unreadable2=references(TRACE,ROOT);need(not refs2 and not unreadable2,'reader appeared after file INTENT');need(same(identity(TRACE),current),'Source changed after file INTENT')
 TRACE.unlink();fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);time.sleep(1);df1=free();need(not os.path.lexists(TRACE),'exact unlink failed')
 os.chown(ROOT,root_before['uid'],root_before['gid']);os.chmod(ROOT,root_before['mode']);os.utime(ROOT,ns=(root_before['mtime_ns'],root_before['mtime_ns']))
 need({x.name for x in ROOT.iterdir()}=={'commandlist','kernelslist','kernelslist.g','stats.csv'},'terminal membership wrong')
 for c in controls:
  p=ROOT/c['relative_path'];need(same(identity(p),c['identity']) and sha(p)==c['sha256'],'terminal control changed '+c['relative_path'])
 done=dict(schema='ORIGINAL174_LAVAMD_SOURCE_RETIREMENT_DONE_AFTER_CAPACITY_OVERRIDE_V1',status='DONE',unix=time.time(),file='kernel-1.traceg',logical_bytes_unlinked=current['size'],allocated_bytes_unlinked=current['allocated'],df_before=df0,df_after=df1,df_interval_delta=df1-df0,interval_delta_not_exclusive_causal_attribution=True,source_root_preserved=True,source_root_mtime_mode_uid_gid_restored=True,source_root_ctime_not_restorable=True,controls_preserved=[x['relative_path'] for x in controls],recursive_delete_used=False,HybridSort_changes=0,SRAD_changes=0,restore_capacity_preflight_waived_by_user=True);put(OUT/'CONTINUE_SOURCE_DONE.json',done);print(json.dumps(done),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as e:
  put(OUT/('CONTINUE_FAILURE_%d.json'%time.time_ns()),dict(error=repr(e),traceback=traceback.format_exc(),unix=time.time(),no_blind_retry=True));raise
