"""Old174 audit and exact Source unlink worker for the authorized seven assets."""
import argparse,fcntl,hashlib,json,os,pathlib,re,stat,subprocess,sys,time,traceback
P=pathlib.Path;MIB=1024**2;GIB=1024**3
T=P('/root/data/research_asset_verified_offload_20261024_v1');OUT=T/'control/second_batch7_fast_retirement_20261104_v1';BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
ASSETS=['TRACE_9d6ff92257d20b4b','TRACE_d6c21d018154d3b5','TRACE_5e9aefe64e214679','TRACE_9ad2f284f8c2a318','TRACE_777ae84f37927c4e','TRACE_cf75342164f0b212','TRACE_694a568c425385d3']
def need(v,m):
 if not v:raise RuntimeError(m)
def blob(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def put(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=blob(x);need(not p.exists(),'immutable receipt collision '+str(p))
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);need(p.read_bytes()==b,'receipt reopen mismatch')
def identity(p):
 s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink')
def same(a,b):return all(a[k]==b[k] for k in ['dev','inode','size','allocated','mtime_ns','ctime_ns','uid','gid','mode','nlink','type'])
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(MIB),b''):h.update(b)
 return h.hexdigest()
def free():
 v=os.statvfs('/root/data');return v.f_bavail*v.f_frsize
def pressure():return {line.split()[0]:{x.split('=')[0]:float(x.split('=')[1]) for x in line.split()[1:]} for line in P('/proc/pressure/io').read_text().splitlines()}
def refs(root,files):
 selected={(x['dev'],x['inode']) for x in files};bad=[];unread=[]
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
  try:
   raw=(proc/'stat').read_text().rsplit(')',1)[1].split();base=dict(pid=int(proc.name),start_ticks=int(raw[19]),state=raw[0]);cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   if str(root) in cmd:bad.append(dict(base,kind='cmdline'))
   for kind in ['cwd','exe']:
    try:v=os.readlink(proc/kind)
    except OSError:continue
    if v==str(root) or v.startswith(str(root)+'/'):bad.append(dict(base,kind=kind,value=v))
   try:fds=list((proc/'fd').iterdir())
   except PermissionError:unread.append(int(proc.name));fds=[]
   except OSError:fds=[]
   for fd in fds:
    try:s=fd.stat();v=os.readlink(fd)
    except OSError:continue
    if (s.st_dev,s.st_ino) in selected:bad.append(dict(base,kind='fd',fd=fd.name,value=v))
   try:
    if str(root) in (proc/'maps').read_text(errors='replace'):bad.append(dict(base,kind='mmap'))
   except PermissionError:unread.append(int(proc.name))
   except OSError:pass
  except PermissionError:unread.append(int(proc.name))
  except (OSError,ValueError,IndexError):pass
 return bad,sorted(set(unread))
def planned(root):
 out={}
 for name,path in [('source','/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json'),('native','/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')]:
  raw=P(path).read_bytes();out[name]={'sha256':hashlib.sha256(raw).hexdigest(),'exact_path_matches':raw.decode(errors='replace').count(str(root))}
 rg=subprocess.run(['rg','-l','-F',str(root),'/workspace/worktrees/accel-sim-decoupled-l2/scripts','/etc/cron.d'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);out['scheduled_or_script_matches']=[x for x in rg.stdout.splitlines() if x];return out
def audit_asset(aid):
 need(aid in ASSETS,'asset outside authorization');raw=(T/'manifests'/(aid+'.json')).read_bytes();m=json.loads(raw);root=P(m['source_root']);rows=[]
 for x in m['members']:
  p=root/x['relative_path'];rows.append({'relative_path':x['relative_path'],'exists':os.path.lexists(p),'identity':identity(p) if os.path.lexists(p) else None})
 existing=[x['identity'] for x in rows if x['identity']];r,u=refs(root,existing);line=next(x for x in P('/proc/self/mountinfo').read_text().splitlines() if ' - overlay overlay ' in x);upper=re.search(r'(?:^|,)upperdir=([^,]+)',line.split(' - overlay overlay ',1)[1]).group(1);v=os.statvfs('/root/data')
 return dict(asset_id=aid,manifest_sha256=hashlib.sha256(raw).hexdigest(),source_root=str(root),root_exists=root.is_dir(),root_identity=identity(root) if root.is_dir() else None,current_files=sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not p.is_symlink()) if root.is_dir() else [],members=rows,readers_writers=r,unreadable_processes=u,planned=planned(root),upperdir=upper,SSD_available_bytes=v.f_bavail*v.f_frsize,SSD_free_inodes=v.f_favail,IO=pressure())
def protected():
 paths=['/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/traces','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/ubench/9.1/atomic_add_bw/NO_ARGS/traces','/workspace/m5-trace-immutable/atax/atax/traces','/workspace/m5-trace-immutable/mvt/mvt/mvt/traces','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/srad_v1-rodinia-3.1/100_0_5_502_458/traces','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/lavaMD-rodinia-3.1/_boxes1d_10/traces','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hybridsort-rodinia-3.1/r/traces'];out={}
 for path in paths:
  root=P(path);out[path]={'root':identity(root),'members':[{'relative_path':p.relative_to(root).as_posix(),'identity':identity(p)} for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()]}
 for path in ['/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodina-3.1.tgz','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/parboil.tgz','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/accelwattch-artifact-appendix.tar','/workspace/m5-trace-immutable/syr2k/syr2k.tar.zst','/workspace/m5-trace-immutable/2mm/2mm.tar.zst']:
  p=P(path);out[path]={'exists':p.exists(),'identity':identity(p) if p.exists() else None}
 return out
def execute(aid):
 base=OUT/'assets'/aid;intent=json.loads((base/'INTENT.json').read_bytes());q=json.loads((base/'QUALIFIED_WHITELIST.json').read_bytes());need(intent['schema']=='ORIGINAL174_SECOND_BATCH7_ASSET_INTENT_V1' and q['asset_id']==aid,'transaction changed');rows=q['files'];controls=q['controls'];need(len(rows)==intent['files'] and all(x['relative_path'].endswith('.traceg') for x in rows),'whitelist changed');root=P(q['source_root']);root_before=identity(root);expected={x['relative_path'] for x in rows+controls};need(set(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not p.is_symlink())==expected,'Source membership changed')
 for x in rows+controls:need(same(identity(root/x['relative_path']),x['identity']),'Source identity changed '+x['relative_path'])
 r,u=refs(root,[x['identity'] for x in rows+controls]);need(not r and not u,'active or unreadable Source process');pl=planned(root);need(not pl['source']['exact_path_matches'] and not pl['native']['exact_path_matches'] and not pl['scheduled_or_script_matches'],'planned reader appeared');io=pressure();need(io['some']['avg60']<25 and io['full']['avg60']<20,'severe I/O pressure');base_floor=7*GIB+GIB+64*MIB;need(free()>=base_floor,'SSD below basic metadata safety floor')
 for c in controls:
  p=root/c['relative_path'];need(sha(p)==c['sha256'],'control SHA changed '+c['relative_path'])
 df0=free();logical=allocated=0;records=[]
 for i,row in enumerate(rows):
  p=root/row['relative_path'];need(same(identity(p),row['identity']),'file identity changed '+row['relative_path']);rr,uu=refs(root,[row['identity']]);need(not rr and not uu,'reader appeared '+row['relative_path'])
  fi=dict(schema='ORIGINAL174_SECOND_BATCH7_FILE_INTENT_V1',asset_id=aid,index=i,unix=time.time(),relative_path=row['relative_path'],source=str(p),sha256=row['sha256'],identity=row['identity'],reader_refs=[],df_before=free());put(base/'per_file'/('%04d.INTENT.json'%i),fi);need(same(identity(p),row['identity']),'identity changed after file INTENT');p.unlink();fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);fdone=dict(schema='ORIGINAL174_SECOND_BATCH7_FILE_DONE_V1',asset_id=aid,index=i,unix=time.time(),relative_path=row['relative_path'],sha256=row['sha256'],logical_bytes=row['size'],allocated_bytes=row['identity']['allocated'],absent=not os.path.lexists(p),df_after=free());need(fdone['absent'],'unlink failed');put(base/'per_file'/('%04d.DONE.json'%i),fdone);records.append({'INTENT':fi,'DONE':fdone});logical+=row['size'];allocated+=row['identity']['allocated']
  if (i+1)%25==0:
   io=pressure();need(io['some']['avg60']<25 and io['full']['avg60']<20,'severe I/O pressure during unlink')
 os.chown(root,root_before['uid'],root_before['gid']);os.chmod(root,root_before['mode']);os.utime(root,ns=(root_before['mtime_ns'],root_before['mtime_ns']));need(set(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not p.is_symlink())=={x['relative_path'] for x in controls},'terminal membership wrong')
 for c in controls:
  p=root/c['relative_path'];need(same(identity(p),c['identity']) and sha(p)==c['sha256'],'terminal control changed '+c['relative_path'])
 df1=free();done=dict(schema='ORIGINAL174_SECOND_BATCH7_ASSET_SOURCE_DONE_V1',status='DONE',asset_id=aid,unix=time.time(),files=len(rows),logical_bytes_unlinked=logical,allocated_bytes_unlinked=allocated,df_before=df0,df_after=df1,df_interval_delta=df1-df0,interval_delta_not_exclusive_causal_attribution=True,controls_preserved=[x['relative_path'] for x in controls],source_root_preserved=True,source_root_mtime_mode_uid_gid_restored=True,source_root_ctime_not_restorable=True,recursive_delete_used=False,capacity_precondition_waived_by_user=True);put(base/'SOURCE_DONE.json',done);print(json.dumps(done),flush=True)
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--audit-asset');g.add_argument('--execute');g.add_argument('--protected',action='store_true');a=ap.parse_args();need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'wrong endpoint');lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if a.audit_asset:print(json.dumps(audit_asset(a.audit_asset)))
 elif a.protected:print(json.dumps(protected()))
 else:execute(a.execute)
if __name__=='__main__':
 try:main()
 except BaseException as e:
  if '--execute' in sys.argv:
   try:aid=sys.argv[sys.argv.index('--execute')+1];put(OUT/'assets'/aid/('FAILURE_%d.json'%time.time_ns()),dict(error=repr(e),traceback=traceback.format_exc(),unix=time.time(),no_blind_retry=True))
   except BaseException:pass
  raise
