"""Old174 HybridSort audit and exact 68-file Source unlink worker."""
import argparse,fcntl,hashlib,json,os,pathlib,re,stat,subprocess,sys,time,traceback
P=pathlib.Path;MIB=1024**2
T=P('/root/data/research_asset_verified_offload_20261024_v1');OUT=T/'control/hybridsort_exact_retirement_v1';BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
ROOT=P('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hybridsort-rodinia-3.1/r/traces')
CONTROLS={'commandlist','kernelslist','kernelslist.g','stats.csv'}
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
def refs(files):
 selected={(x['dev'],x['inode']) for x in files};bad=[];unreadable=[]
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
  try:
   raw=(proc/'stat').read_text().rsplit(')',1)[1].split();base=dict(pid=int(proc.name),start_ticks=int(raw[19]),state=raw[0]);cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   if str(ROOT) in cmd:bad.append(dict(base,kind='cmdline'))
   for kind in ['cwd','exe']:
    try:v=os.readlink(proc/kind)
    except OSError:continue
    if v==str(ROOT) or v.startswith(str(ROOT)+'/'):bad.append(dict(base,kind=kind,value=v))
   try:fds=list((proc/'fd').iterdir())
   except PermissionError:unreadable.append(int(proc.name));fds=[]
   except OSError:fds=[]
   for fd in fds:
    try:s=fd.stat();v=os.readlink(fd)
    except OSError:continue
    if (s.st_dev,s.st_ino) in selected:bad.append(dict(base,kind='fd',fd=fd.name,value=v))
   try:
    if str(ROOT) in (proc/'maps').read_text(errors='replace'):bad.append(dict(base,kind='mmap'))
   except PermissionError:unreadable.append(int(proc.name))
   except OSError:pass
  except PermissionError:unreadable.append(int(proc.name))
  except (OSError,ValueError,IndexError):pass
 return bad,sorted(set(unreadable))
def protected():
 out={}
 for name,path in [('SRAD','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/srad_v1-rodinia-3.1/100_0_5_502_458/traces'),('lavaMD','/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/lavaMD-rodinia-3.1/_boxes1d_10/traces')]:
  r=P(path);out[name]={'root':identity(r),'members':[{'name':p.name,'identity':identity(p)} for p in sorted(r.iterdir())]}
 return out
def snapshot():
 mraw=(T/'manifests/TRACE_2f6210166d43b19e.json').read_bytes();m=json.loads(mraw);need(hashlib.sha256(mraw).hexdigest()=='b526b722d71bd08d742641ca9a2548723480cbae2e7a1b25bf6eed4e7d106a9b','manifest changed');need(m['source_root']==str(ROOT),'root changed')
 rows=[{'relative_path':x['relative_path'],'identity':identity(ROOT/x['relative_path'])} for x in m['members'] if os.path.lexists(ROOT/x['relative_path'])];r,u=refs([x['identity'] for x in rows]);regs={}
 for name,path in [('source','/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json'),('native','/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')]:
  raw=P(path).read_bytes();text=raw.decode(errors='replace');regs[name]={'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'exact_source_matches':text.count(str(ROOT)),'HybridSort_matches':text.lower().count('hybridsort')}
 search=subprocess.run(['rg','-l','--hidden','-g','!.git/**','-g','!*.traceg','hybridsort|HybridSort','/workspace/worktrees/accel-sim-decoupled-l2/scripts'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 line=next(x for x in P('/proc/self/mountinfo').read_text().splitlines() if ' - overlay overlay ' in x);upper=re.search(r'(?:^|,)upperdir=([^,]+)',line.split(' - overlay overlay ',1)[1]).group(1)
 return dict(host=os.uname().nodename,namespace=os.readlink('/proc/self/ns/mnt'),manifest_sha256=hashlib.sha256(mraw).hexdigest(),source_root=str(ROOT),root_identity=identity(ROOT),members=rows,current_names=sorted(x.name for x in ROOT.iterdir()),trace_count=sum(x['relative_path'].endswith('.traceg') for x in rows),trace_logical_bytes=sum(x['identity']['size'] for x in rows if x['relative_path'].endswith('.traceg')),trace_allocated_bytes=sum(x['identity']['allocated'] for x in rows if x['relative_path'].endswith('.traceg')),readers_writers=r,unreadable_processes=u,registries=regs,future_script_matches=[x for x in search.stdout.splitlines() if x],protected=protected(),upperdir=upper,ssd_available_bytes=free())
def execute():
 intent=json.loads((OUT/'INTENT.json').read_bytes());need(intent['schema']=='ORIGINAL174_HYBRIDSORT_EXACT_RETIREMENT_INTENT_V1','INTENT changed');q=json.loads((OUT/'QUALIFIED_WHITELIST.json').read_bytes());rows=q['files'];controls=q['controls'];need(len(rows)==68 and all(x['relative_path'].startswith('kernel-') and x['relative_path'].endswith('.traceg') for x in rows),'whitelist changed')
 need(ROOT.is_dir() and not ROOT.is_symlink(),'root changed');root_before=identity(ROOT);snap=snapshot();need(not snap['readers_writers'] and not snap['unreadable_processes'],'active or unreadable process');need({x.name for x in ROOT.iterdir()}=={x['relative_path'] for x in rows}|CONTROLS,'membership changed')
 for c in controls:
  p=ROOT/c['relative_path'];need(same(identity(p),c['identity']) and sha(p)==c['sha256'],'control changed '+c['relative_path'])
 df0=free();logical=allocated=0;records=[]
 for i,row in enumerate(rows):
  p=ROOT/row['relative_path'];need(p.is_file() and not p.is_symlink() and same(identity(p),row['identity']),'Source changed '+row['relative_path']);r,u=refs([row['identity']]);need(not r and not u,'reader appeared '+row['relative_path'])
  fi=dict(schema='ORIGINAL174_HYBRIDSORT_FILE_UNLINK_INTENT_V1',index=i,unix=time.time(),relative_path=row['relative_path'],source=str(p),sha256=row['sha256'],identity=row['identity'],reader_refs=[],df_before=free());put(OUT/'per_file'/('%03d.INTENT.json'%i),fi);need(same(identity(p),row['identity']),'Source changed after INTENT');p.unlink();fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);fdone=dict(schema='ORIGINAL174_HYBRIDSORT_FILE_UNLINK_DONE_V1',index=i,unix=time.time(),relative_path=row['relative_path'],sha256=row['sha256'],logical_bytes=row['size'],allocated_bytes=row['identity']['allocated'],absent=not os.path.lexists(p),df_after=free());need(fdone['absent'],'unlink failed');put(OUT/'per_file'/('%03d.DONE.json'%i),fdone);records.append({'INTENT':fi,'DONE':fdone});logical+=row['size'];allocated+=row['identity']['allocated']
 os.chown(ROOT,root_before['uid'],root_before['gid']);os.chmod(ROOT,root_before['mode']);os.utime(ROOT,ns=(root_before['mtime_ns'],root_before['mtime_ns']));need({x.name for x in ROOT.iterdir()}==CONTROLS,'terminal membership wrong')
 for c in controls:
  p=ROOT/c['relative_path'];need(same(identity(p),c['identity']) and sha(p)==c['sha256'],'terminal control changed '+c['relative_path'])
 df1=free();done=dict(schema='ORIGINAL174_HYBRIDSORT_SOURCE_RETIREMENT_DONE_V1',status='DONE',unix=time.time(),files=68,logical_bytes_unlinked=logical,allocated_bytes_unlinked=allocated,df_before=df0,df_after=df1,df_interval_delta=df1-df0,interval_delta_not_exclusive_causal_attribution=True,controls_preserved=sorted(CONTROLS),source_root_preserved=True,source_root_mtime_mode_uid_gid_restored=True,source_root_ctime_not_restorable=True,recursive_delete_used=False,SRAD_or_lavaMD_changes=0,capacity_precondition_waived_by_user=True,protected_after=protected());put(OUT/'SOURCE_DONE.json',done);print(json.dumps(done),flush=True)
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--audit',action='store_true');g.add_argument('--execute',action='store_true');a=ap.parse_args();need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'wrong endpoint');lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);print(json.dumps(snapshot())) if a.audit else execute()
if __name__=='__main__':
 try:main()
 except BaseException as e:
  if '--execute' in sys.argv:put(OUT/('FAILURE_%d.json'%time.time_ns()),dict(error=repr(e),traceback=traceback.format_exc(),unix=time.time(),no_blind_retry=True))
  raise
