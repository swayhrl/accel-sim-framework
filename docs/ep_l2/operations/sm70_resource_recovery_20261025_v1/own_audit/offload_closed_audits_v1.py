import os,sys,json,time,pathlib,hashlib,stat,subprocess,fcntl,traceback
P=pathlib.Path
M=1024**2
ROOT=P('/root/data')
TASK=ROOT/'ep_main_closed_audit_offload_20261025_v1'
NAS=P('/root/share/mnt164/huangrulin/traces/receipts/ep_main_closed_audit_offload_20261025_v1')
NAMES=['ada9_consumer_parent_cold_restore_20261024_v1','ada9_parent_cold_review_20261024_v1','ada_input_capsule_c8_parent_restore_20261024_v1','ada_stage4_parent_cold_restore_20261024_v1','cubin_collision_parent_closeout_20261024_v1','nn_parent_cold_review_20261025_v1','rtx4080_c8_parent_native_restore_20261024_v1']
def need(x,s):
 if not x:raise RuntimeError(s)
def blob(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def atomic(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():need(p.read_bytes()==b,'immutable collision '+str(p));return
 tmp=p.with_name(p.name+'.writing')
 need(not tmp.exists(),'retained writing collision '+str(tmp))
 with tmp.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.rename(tmp,p)
 need(p.read_bytes()==b,'closed metadata mismatch')
def ident(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid]
def gate():
 need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]' and ROOT.stat().st_dev==2128,'wrong native')
 f=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
 need(f['source']=='admin-wcx@10.208.130.164:/home/shared' and f['fstype']=='fuse.sshfs','wrong true164')
 v=os.statvfs(ROOT);free=v.f_bavail*v.f_frsize
 need(free>=5*1024**3+64*M,'offload only base reserve')
 return free
def digest_file(p,native=False):
 h=hashlib.sha256();flags=os.O_RDONLY|os.O_NOFOLLOW
 if native:flags|=getattr(os,'O_NOATIME',0)
 fd=os.open(p,flags)
 with os.fdopen(fd,'rb') as f:
  while True:
   t=time.monotonic();b=f.read(M)
   if not b:break
   h.update(b);gate() if time.monotonic()-last_gate[0]>10 else None
   if time.monotonic()-last_gate[0]>10:last_gate[0]=time.monotonic()
   time.sleep(max(0,len(b)/(8*M)-(time.monotonic()-t)))
 return h.hexdigest()
last_gate=[time.monotonic()]
def inventory(root):
 out={}
 for current,dirs,files in os.walk(root,followlinks=False):
  for n in dirs+files:
   p=P(current)/n;r=str(p.relative_to(root));s=p.lstat()
   need(not p.is_symlink() and (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)),'unsupported own audit entry '+str(p))
   need(s.st_dev==2128,'non-native member')
   out[r]={'kind':'directory' if stat.S_ISDIR(s.st_mode) else 'file','identity':ident(p)}
 return out
def inactive(root):
 bad=[]
 needle=str(root)
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
  try:
   cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   if needle in cmd:bad.append([proc.name,'cmdline'])
   for fd in (proc/'fd').iterdir():
    try:s=os.readlink(fd)
    except OSError:continue
    if s==needle or s.startswith(needle+'/'):bad.append([proc.name,'fd'])
   maps=(proc/'maps').read_text()
   if needle in maps:bad.append([proc.name,'maps'])
  except (OSError,ProcessLookupError):continue
 need(not bad,'active own audit references '+repr(bad))
def run_one(name):
 source=ROOT/name;target=NAS/name;tree=target/'tree';backup=ROOT/(name+'.offload_verified_backup_v1')
 if source.is_symlink():
  need(source.resolve()==tree.resolve() and (target/'RELEASE_RECEIPT.json').exists(),'unexpected cold alias')
  return json.loads((target/'RELEASE_RECEIPT.json').read_bytes())
 need(source.is_dir() and source.parent==ROOT and not backup.exists(),'wrong exact own source or retained backup')
 inactive(source);before_free=gate();original_root=ident(source);inv=inventory(source);files=[r for r,v in inv.items() if v['kind']=='file']
 need(not target.exists(),'retained target requires explicit recovery')
 tree.mkdir(parents=True)
 for r,v in sorted(inv.items(),key=lambda x:(x[0].count('/'),x[0])):
  if v['kind']=='directory':(tree/r).mkdir()
 for idx,r in enumerate(files):
  src=source/r;dst=tree/r;need(ident(src)==inv[r]['identity'],'source changed before copy')
  tmp=dst.with_name(dst.name+'.writing');h=hashlib.sha256()
  fd=os.open(src,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb') as f,tmp.open('xb') as out:
   while True:
    t=time.monotonic();b=f.read(M)
    if not b:break
    h.update(b);out.write(b);gate()
    time.sleep(max(0,len(b)/(8*M)-(time.monotonic()-t)))
   out.flush();os.fsync(out.fileno())
  need(ident(src)==inv[r]['identity'],'source changed during copy')
  os.rename(tmp,dst);expected=h.hexdigest();need(digest_file(dst)==expected,'closed NAS fullSHA')
  inv[r]['sha256']=expected
  if idx%50==0:print(json.dumps({'event':'COPY_CLOSED_SHA','name':name,'files':idx+1,'total':len(files)}),flush=True)
 need(inventory(source)=={r:{k:v for k,v in x.items() if k!='sha256'} for r,x in inv.items()},'source inventory changed')
 expected=set(inv)
 actual=set(str(p.relative_to(tree)) for p in tree.rglob('*'));need(actual==expected,'target extra/missing members')
 for r in files:
  need(ident(source/r)==inv[r]['identity'] and digest_file(source/r,True)==inv[r]['sha256'],'final native source changed')
 inactive(source);need(ident(source)==original_root,'own source root changed')
 manifest={'schema':'OWN_CLOSED_AUDIT_NATIVE_COPY_OFFLOAD_V1','source':str(source),'target':str(tree),'source_root_identity':original_root,'members':inv,'source_trace_payload_release_bytes':0,'historical_native_restore_claims_remain_historical':True,'future_reads_use_true164':True}
 raw=blob(manifest);atomic(target/'MANIFEST.json',raw)
 commit={'status':'ALL_MEMBERS_FULL_SHA_CLOSED_REOPEN_PASS_BEFORE_OWN_NATIVE_COPY_RELEASE','manifest_sha256':sha(raw),'files':len(files),'bytes':sum(inv[r]['identity'][3] for r in files),'created_unix':time.time(),'normal_transfer_resource_guard_not_modified':True}
 atomic(target/'COMMIT.json',blob(commit))
 os.rename(source,backup)
 try:os.symlink(tree,source,target_is_directory=True)
 except BaseException:os.rename(backup,source);raise
 need(source.is_symlink() and source.resolve()==tree.resolve(),'cold alias mismatch')
 for r in files:need(digest_file(source/r)==inv[r]['sha256'],'cold alias fullSHA mismatch')
 inactive(backup)
 need(inventory(backup)=={r:{k:v for k,v in x.items() if k!='sha256'} for r,x in inv.items()},'backup inventory changed')
 released=0
 for r in files:
  p=backup/r;need(ident(p)==inv[r]['identity'],'backup changed before exact delete')
  released+=p.lstat().st_blocks*512;p.unlink()
 for r in sorted([r for r,v in inv.items() if v['kind']=='directory'],key=lambda x:x.count('/'),reverse=True):(backup/r).rmdir()
 backup.rmdir()
 receipt={'status':'OWN_CLOSED_AUDIT_COLD_ALIAS_VERIFIED_NATIVE_COPY_RELEASED','name':name,'manifest_sha256':sha(raw),'commit_sha256':sha(blob(commit)),'logical_native_copy_bytes_released':commit['bytes'],'allocated_native_file_bytes_released':released,'free_before':before_free,'free_after':gate(),'original_path':str(source),'cold_tree':str(tree),'source_trace_payload_release_bytes':0,'foreign_ledgers_or_jobs_modified':False,'all_member_cold_alias_fullSHA':True,'finished_unix':time.time()}
 atomic(target/'RELEASE_RECEIPT.json',blob(receipt));atomic(TASK/(name+'.json'),blob(receipt));print(json.dumps(receipt),flush=True);return receipt
TASK.mkdir(exist_ok=True);lease=(TASK/'OFFLOAD.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 gate();os.nice(19);receipts=[run_one(n) for n in NAMES]
 final={'status':'PASS_ALL_SEVEN_OWN_CLOSED_AUDIT_TREES_OFFLOADED','receipts':receipts,'free_after':gate(),'source_trace_payload_release_bytes':0,'normal_library_guard_unchanged':True}
 atomic(NAS/'FINAL.json',blob(final));atomic(TASK/'FINAL.json',blob(final));print(json.dumps(final),flush=True)
except BaseException as e:
 (TASK/'FAILURE.json').write_bytes(blob({'status':'FAILED_RETAINED_NO_FURTHER_RELEASE','error':repr(e),'traceback':traceback.format_exc(),'observed_unix':time.time()}));raise
