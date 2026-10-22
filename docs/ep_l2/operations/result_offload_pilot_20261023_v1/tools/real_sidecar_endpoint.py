"""Finite COPY_ONLY endpoint for the two exact owner-published sidecar offers.

Injected CONFIG is frozen by the Windows foreground relay. Source mode only
reads exact no-follow/no-atime files. Target mode reuses the original sole
receiver lock and pinned V9 library. There is no scheduler or deletion API.
"""
import base64,datetime,fcntl,hashlib,json,os,stat,subprocess,sys,time,types
from pathlib import Path,PurePosixPath
sys.dont_write_bytecode=True
MIB=1024**2;GIB=1024**3
BRIDGE=Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
SYN=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_result_offload_pilot_v1')
REAL='/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_result_offload_real_sidecars_v1/'
ALLOWED={'EP_L2_E057':{'NATIVE_EXIT.json','config-0.config','config-1.config','config-2.config','config-3.config'},'DTC_L1_AD_GEMM':{'RUN_START.json','RUN_TERMINAL.json','ACTUAL_PRODUCER_BINDING.json','STRICT.json'}}
def require(x,why):
 if not x:raise RuntimeError(why)
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(s):return dict(dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,allocated=s.st_blocks*512,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def scope():
 m=CONFIG['manifest'];slug=CONFIG['slug'];require(slug in ALLOWED,'unapproved project')
 require({PurePosixPath(r['relative_path']).name for r in m['files']}==ALLOWED[slug],'exact sidecar selector')
 require(sum(r['size'] for r in m['files'])<= (65536 if slug=='EP_L2_E057' else 262144),'owner sidecar size scope')
 require(sha(base64.b64decode(CONFIG['owner_raw']))==m['source_owner_ready_sha256'],'owner READY changed')
 require(m['genuine164_destination_root']==REAL+slug,'new target scope')
 require(m['source_action']=='SOURCE_KEEP' and m['sidecar_subset_only'],'copy disposition')
 return m,slug
def source():
 m,slug=scope();fs=m['source_filesystem_identity']
 require(os.uname().nodename==fs['host'] and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==fs['boot_id'] and os.readlink('/proc/self/ns/mnt')==fs['mount_namespace'],'Source identity')
 lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 selected={(r['dev'],r['inode']) for r in m['files']};writers=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:fds=list((p/'fd').iterdir())
  except FileNotFoundError:continue
  for fd in fds:
   try:
    s=fd.stat()
    if (s.st_dev,s.st_ino) not in selected:continue
    flags=int(next(x.split()[1] for x in (p/'fdinfo'/fd.name).read_text().splitlines() if x.startswith('flags:')),8)
    if flags&os.O_ACCMODE in (os.O_WRONLY,os.O_RDWR):writers.append({'pid':int(p.name),'fd':fd.name})
   except FileNotFoundError:continue
 require(not writers,'selected Source writer is active')
 def directories():
  for d in m['directories']:
   p=Path(m['source_root'])/d['relative_path'];s=p.lstat()
   require(stat.S_ISDIR(s.st_mode) and not p.is_symlink(),'Source directory type')
   for k in ['dev','inode','uid','gid','mode','mtime_ns','ctime_ns']:require(ident(s)[k]==d[k],'Source directory drift '+str(p)+' '+k)
 directories();rows=[];missing=set(CONFIG['missing_names']);require(missing<={r['relative_path'] for r in m['files']},'requested unselected path')
 for row in m['files']:
  rel=PurePosixPath(row['relative_path']);require(not rel.is_absolute() and '..' not in rel.parts,'Source path escape')
  p=Path(m['source_root'])/str(rel)
  for q in [p,*p.parents]:require(not q.is_symlink(),'Source symlink traversal')
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb',buffering=0) as f:
   before=ident(os.fstat(f.fileno()));require(before=={k:row[k] for k in before},'Source file identity drift')
   b=f.read(row['size']+1);require(len(b)==row['size'] and sha(b)==row['sha256'],'Source complete SHA/size')
   require(ident(os.fstat(f.fileno()))==before==ident(p.lstat()),'Source changed during read')
  r={'relative_path':row['relative_path'],'sha256':sha(b),'identity':before,'noatime_read':True}
  if row['relative_path'] in missing:r['data_base64']=base64.b64encode(b).decode()
  rows.append(r)
 directories();out=canon({'status':'SOURCE_READONLY_BYTES_VERIFIED_SOURCE_KEEP','source_role':'T_READONLY_BYTE_CHECK_NOT_OWNER_IMPERSONATION','owner_ready_sha256':m['source_owner_ready_sha256'],'txid':CONFIG['txid'],'files':rows,'selected_writers':writers,'source_action':'SOURCE_KEEP','source_released_bytes':0,'utc':utc()})
 require(len(out)<=512*1024,'finite source packet cap')
 for start in range(0,len(out),32768):
  part=out[start:start+32768];time.sleep(len(part)/MIB);sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
 lock.close()
def allocated(root):
 if not root.exists():return 0
 seen=set();n=0
 for p in [root,*root.rglob('*')]:
  s=p.lstat();require(not stat.S_ISLNK(s.st_mode),'owned destination symlink');key=(s.st_dev,s.st_ino)
  if key not in seen:seen.add(key);n+=s.st_blocks*512
 require(len(seen)<=500,'owned path count');return n
def target():
 m,slug=scope();native=Path('/root/data/result_offload_real_sidecars_20261023_v1')/slug;nas=Path(m['destination_path_on_174new']);peak={'scratch':0,'NAS':0}
 require(os.uname().nodename=='huangrulin-sshfs-174','wrong target host')
 for p in [native,nas]:
  for q in [p,*p.parents]:require(not q.is_symlink(),'target symlink')
 def gates():
  mount=subprocess.check_output(['findmnt','-n','-T',str(SYN.parent),'-o','TARGET,SOURCE,FSTYPE'],text=True).split();require(mount==['/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs'],'genuine164 mount')
  require(Path('/root/data').stat().st_dev==2128 and subprocess.check_output(['findmnt','-n','-T','/root/data','-o','FSTYPE'],text=True).strip()=='ext4','native SSD identity')
  v=os.statvfs('/root/data');mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
  require(v.f_bavail*v.f_frsize-20*MIB>=7*GIB and mem>=64*GIB,'SSD/RAM budget')
  cg=Path('/sys/fs/cgroup');mx=(cg/'memory.max').read_text().strip();cur=int((cg/'memory.current').read_text());require(mx=='max' or int(mx)-cur>=256*MIB,'cgroup memory headroom')
  a,b=allocated(native),allocated(nas);require(a<=2*MIB and b<=2*MIB,'separate real2MiB cap');peak['scratch']=max(peak['scratch'],a);peak['NAS']=max(peak['NAS'],b)
  return {'utc':utc(),'native_SSD_free':v.f_bavail*v.f_frsize,'MemAvailable':mem,'scratch_allocated':a,'NAS_allocated':b,'Share_new_allocated':0}
 gates();qualified=json.loads((SYN/'FINAL_SYNTHETIC_RESULT.json').read_bytes())
 require(qualified['status']=='PASS' and qualified['files']==4 and qualified['directories']==3 and qualified['raw_bytes']==1314816 and qualified['restore']=='RESTORE_VERIFIED_NATIVE_TARGET' and all(x['status']=='PASS' for x in qualified['cases']),'synthetic qualification absent')
 require(qualified['driver_sha256']=='b2c850227f70150dce67474c6cec234f4b0daf109c7b33a0758fae1838701440','wrong zero-Share qualification')
 lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 lib=base64.b64decode(CONFIG['v9_raw']);require(sha(lib)=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe','V9 changed')
 v=types.ModuleType('pinned_v9');exec(compile(lib,'pinned_v9_transaction.py','exec'),v.__dict__);txid=v.validate_manifest(m);require(txid==CONFIG['txid'],'txid mismatch')
 reservation={'txid':txid,'manifest_sha256':sha(canon(m)),'owner_ready_sha256':m['source_owner_ready_sha256'],'tool_publication':CONFIG['tool_publication'],'native_scratch':str(native),'NAS_root':str(nas),'source_action':'SOURCE_KEEP','zero_share_confirmation_sha256':CONFIG['zero_share_confirmation_sha256']}
 def raw_new(p,b):
  p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():require(p.read_bytes()==b,'immutable local/remote bytes differ');return
  with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 for root in [native,nas]:
  if root.exists():require((root/'T_RESERVATION.json').read_bytes()==canon(reservation),'unowned or mismatched existing real root')
  else:root.mkdir(parents=True,mode=0o700)
  raw_new(root/'T_RESERVATION.json',canon(reservation));raw_new(root/'OWNER_COPY_READY.json',base64.b64decode(CONFIG['owner_raw']))
 raw_new(native/'v9_transaction.py',lib);raw_new(nas/'v9_transaction.py',lib)
 t=v.Transaction(nas,m);t.throttle=v.Throttle(MIB);missing=[]
 for row in m['files']:
  key=v.digest(row['relative_path'].encode())+'.0000000000000000';chunk=t.work/'chunks'/key
  if chunk.exists():require(v.hash_file(chunk)==row['sha256'],'existing chunk corruption')
  else:missing.append(row['relative_path'])
 print(json.dumps({'event':'READY','txid':txid,'missing_names':missing,'resources':gates()}),flush=True)
 raw=sys.stdin.buffer.readline(512*1024+1);require(0<len(raw)<=512*1024,'packet cap/EOF');packet=json.loads(raw)
 require(packet['txid']==txid and packet['owner_ready_sha256']==m['source_owner_ready_sha256'] and packet['source_action']=='SOURCE_KEEP','Source packet binding')
 require({r['relative_path'] for r in packet['files']}=={r['relative_path'] for r in m['files']},'Source file set')
 newbytes=0
 for row in m['files']:
  r=next(x for x in packet['files'] if x['relative_path']==row['relative_path']);require(r['sha256']==row['sha256'] and r['identity']=={k:row[k] for k in r['identity']},'Source independent identity join')
  key=v.digest(row['relative_path'].encode())+'.0000000000000000'
  if row['relative_path'] in missing:
   data=base64.b64decode(r['data_base64'],validate=True);require(len(data)==row['size'] and sha(data)==row['sha256'],'Target full received SHA')
   stage=native/'stage'/key;raw_new(stage,data);newbytes+=len(data)
  else:stage=t.work/'chunks'/key
  t.accept_chunk(row['relative_path'],0,stage,row['sha256'],txid=txid);gates()
 proof={k:val for k,val in packet.items() if k!='files'};proof['files']=[{k:z for k,z in x.items() if k!='data_base64'} for x in packet['files']]
 raw_new(nas/'source_checks'/(sha(canon(proof))+'.json'),canon(proof))
 final=t.finalize();gates();restored=native/'restored';rr=v.native_restore(final/'tree',m,restored);gates()
 paths=[]
 for row in m['files']:
  p=restored/row['relative_path'];require(v.hash_file(p)==row['sha256'],'final native bytes');paths.append({'source':m['source_root']+'/'+row['relative_path'],'archive':str(final/'tree'/row['relative_path']).replace('/root/share/mnt164','/home/shared',1),'native_restore':str(p),'sha256':row['sha256'],'size':row['size'],'source_identity':{k:row[k] for k in ['dev','inode','uid','gid','mode','mtime_ns','ctime_ns']},'restored_identity':ident(p.stat())})
 receipt={'schema':'FINITE_REAL_SIDECAR_ARCHIVE_RESTORE_RECEIPT_V1','status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','project':slug,'utc':utc(),'txid':txid,'manifest_sha256':sha(canon(m)),'owner_ready_sha256':m['source_owner_ready_sha256'],'owner_publication':m['source_frozen_commit'],'files':len(m['files']),'directories':len(m['directories']),'raw_bytes':sum(x['size'] for x in m['files']),'effective_new_transferred_bytes':newbytes,'whole_raw_SHA_and_numeric_metadata':True,'archive_root':str(final).replace('/root/share/mnt164','/home/shared',1),'native_restore_root':str(restored),'source_readonly_proof_sha256':sha(canon(proof)),'source_disposition':'SOURCE_KEEP','source_released_bytes':0,'Share_new_allocated':0,'science_state':'UNCHANGED_OWNER_ACCEPTANCE','owner_postcopy_reconfirmation':'REQUESTED_NOT_IMPERSONATED','paths':paths,'resources':gates(),'observed_allocated_peaks':dict(peak)}
 for root in [native,nas]:raw_new(root/'RECEIPT.json',canon(receipt));raw_new(root/'PATH_MAP.json',canon(paths))
 request={'request':'OWNER_INDEPENDENT_POSTCOPY_SOURCE_KEEP_RECONFIRM','project':slug,'txid':txid,'target_receipt_sha256':sha(canon(receipt)),'Source_paths':[x['source'] for x in paths],'source_action':'SOURCE_KEEP','no_source_delete_authority':True}
 raw_new(nas/'OWNER_RECONFIRM_REQUEST.json',canon(request));gates()
 print(json.dumps({'event':'DONE','receipt':receipt,'final_resources':gates(),'observed_allocated_peaks_including_receipts':peak,'receipt_sha256':sha(canon(receipt))}),flush=True);lock.close()
if __name__=='__main__':
 os.nice(19)
 if CONFIG['role']=='source':source()
 else:target()
