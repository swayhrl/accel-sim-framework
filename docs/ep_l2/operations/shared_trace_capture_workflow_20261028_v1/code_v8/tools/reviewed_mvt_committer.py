"""Root-admitted private MVT COPY_ONLY archive. No capture/POST/public publisher branch."""
import pathlib,os,json,hashlib,stat,time,fcntl,argparse,signal,resource
D=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
PARENT='MVT4096_SM89_0F40244E9865_ACTUAL_R5_A001';CHILD=PARENT+'_CTA_STRIDE_40_V1'
ROOT_ACCEPT='3386ed728ce63160697b4a2779f259d3574f46be26df538b9f9666cdf70ffd0d'
QID='ORD_PolyBench_GPU_MVT_9feea951071a_A001';RATE=10*1024**2
def need(v,m):
 if not v:raise ValueError('MVT_ARCHIVE_REJECT:'+m)
def safe(p,root=None):
 p=pathlib.Path(p);need(p.is_absolute()and '..'not in p.parts,'absolute path')
 if root is not None:need(p.is_relative_to(root),'outside exact private write root')
 for q in[p,*p.parents]:need(not q.is_symlink(),'symlink')
 return p
def raw(p,cap=262144):
 p=safe(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<=a.st_size<=cap,'bounded metadata');blocks=[];left=a.st_size
  while left:
   b=os.read(fd,min(65536,left));need(b,'short metadata');blocks.append(b);left-=len(b)
  z=os.fstat(fd);t=p.stat();sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  need(not os.read(fd,1)and sig(a)==sig(z)==sig(t),'same metadata FD/path')
 finally:os.close(fd)
 return b''.join(blocks)
def digest(b):return hashlib.sha256(b).hexdigest()
def save_new(p,x):
 b=json.dumps(x,indent=2,sort_keys=True).encode()+b'\n';tmp=p.with_name('.own_'+p.name+'_'+str(os.getpid())+'_'+str(time.time_ns()))
 with tmp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 try:os.link(tmp,p)
 finally:tmp.unlink()
def fresh(deadline):need(time.time()<deadline,'absolute Root archive deadline')
def member_rows(m):
 rows=m['files'];need(type(rows)is list and 1<=len(rows)<=256,'member count')
 names=[]
 for r in rows:
  p=pathlib.PurePosixPath(r['path']);need(not p.is_absolute()and '..'not in p.parts and str(p)==r['path']and r['path']not in ['MANIFEST.json','COMMIT.json'],'canonical relative member')
  need(type(r['bytes'])is int and 0<=r['bytes']<=128*1024**2 and type(r['sha256'])is str and len(r['sha256'])==64 and all(c in '0123456789abcdef'for c in r['sha256']),'member size/digest')
  names.append(r['path'])
 need(len(names)==len(set(names))and m['logical_bytes']==sum(r['bytes']for r in rows)<=256*1024**2,'unique bounded complete package')
 return rows
def transfer(source,dest,row,deadline,rate=RATE):
 # Both source read and target write are charged to the one engineering pacing budget.
 safe(source);safe(dest);dest.parent.mkdir(parents=True,exist_ok=True);fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  before=os.fstat(fd);need(stat.S_ISREG(before.st_mode)and before.st_size==row['bytes'],'sender regular exact size');h=hashlib.sha256();total=0
  with dest.open('xb')as out:
   while True:
    fresh(deadline);start=time.monotonic();b=os.read(fd,1048576)
    if not b:break
    h.update(b);out.write(b);total+=len(b)
    if rate:time.sleep(max(0,2*len(b)/rate-(time.monotonic()-start)))
   out.flush();os.fsync(out.fileno())
  after=os.fstat(fd);ps=source.stat();sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  need(sig(before)==sig(after)==sig(ps)and total==row['bytes']and h.hexdigest()==row['sha256'],'sender sameFD wholeSHA')
 finally:os.close(fd)
def whole_sha(path,deadline,rate=RATE):
 safe(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode),'receiver regular file');h=hashlib.sha256();total=0
  while True:
   fresh(deadline);start=time.monotonic();b=os.read(fd,1048576)
   if not b:break
   h.update(b);total+=len(b)
   if rate:time.sleep(max(0,len(b)/rate-(time.monotonic()-start)))
  z=os.fstat(fd);t=path.stat();sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);need(sig(a)==sig(z)==sig(t),'receiver stable sameFD')
  return total,h.hexdigest()
 finally:os.close(fd)
def verify_members(root,manifest_sha,deadline,rate=RATE):
 b=raw(root/'MANIFEST.json');need(digest(b)==manifest_sha,'exact closed manifest raw');m=json.loads(b);rows=member_rows(m)
 found={str(p.relative_to(root))for p in root.rglob('*')if p.is_file()and str(p.relative_to(root))not in ['MANIFEST.json','COMMIT.json']}
 need(found=={r['path']for r in rows},'no missing or foreign member')
 for r in rows:need(whole_sha(root/r['path'],deadline,rate)==(r['bytes'],r['sha256']),'receiver full member SHA '+r['path'])
 return m
def parent_dependency(root,m):
 need(m['asset_id']==CHILD,'only fixed derived')
 dep=json.loads(raw(root/'PARENT_INPUT_REFERENCE.json'));parent=root.parent/PARENT
 cb=raw(parent/'COMMIT.json');pb=raw(parent/'MANIFEST.json');commit=json.loads(cb);pm=json.loads(pb)
 need(commit['status']=='COMMITTED_VERIFIED'and commit['asset_id']==PARENT and commit['manifest_sha256']==digest(pb),'real parent closed')
 need(dep['parent_asset_id']==PARENT and dep['parent_commit_sha256']==digest(cb)and dep['parent_manifest_sha256']==digest(pb),'child exact parent hashes')
 indexed={r['path']:r for r in member_rows(pm)}
 need(len(dep['input_members'])==5 and sum(r['bytes']for r in dep['input_members'])==67174400,'all five parent inputs')
 for r in dep['input_members']:need(indexed[r['path']]==r,'exact parent input manifest member')
 need(not any(r['path'].startswith('traces/inputs/')for r in m['files']),'derived must not copy parent input payload')
 return dep
def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['FULL','DERIVED'],required=True);p.add_argument('--expected-approval-sha',required=True);p.add_argument('--expected-code-sha',required=True);a0=p.parse_args()
 need(digest(raw(pathlib.Path(__file__),65536))==a0.expected_code_sha,'Root exact committer source')
 grant=C/('ROOT_MVT4096_PRIVATE_'+a0.phase+'_ARCHIVE_APPROVAL_V1.json');fd=os.open(grant,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_size<=32768,'Native Root600 authority')
  b=os.read(fd,32769);z=os.fstat(fd);t=grant.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns)and len(b)==s.st_size,'same authority FD')
 finally:os.close(fd)
 need(digest(b)==a0.expected_approval_sha,'Root exact raw authority');a=json.loads(b);asset=PARENT if a0.phase=='FULL'else CHILD
 need(a['schema']=='ROOT_MVT4096_PRIVATE_ARCHIVE_COPY_ONLY_V1'and a['approved']is True and a['phase']==a0.phase,'new exact private archive admission')
 need(a['code_sha256']==a0.expected_code_sha and a['asset_id']==asset and a['Root_acceptance_sha256']==ROOT_ACCEPT,'code/input authority')
 need(a['not_before_unix']<=time.time()<a['absolute_deadline_unix']<=a['not_before_unix']+1800<=1793241315.9269235,'finite original campaign archive window')
 need(a['GPU_POST_PUBLIC_QUEUE_STOP_allowed']is False and a['Native_payload_bytes']==0 and a['AS_bytes']==512*1024**2 and a['CPU_max']==2,'archive-only resource boundary')
 prefix=D/'prepared'/('full'if a0.phase=='FULL'else'derived_ready');target=D/'committed'/asset
 need(a['target']==str(target),'exact private target');safe(prefix,D);safe(target,D)
 mounts=[l for l in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()if l.split(' - ',1)[0].split()[4]=='/root/share/mnt164'];need(len(mounts)==1 and mounts[0].split(' - ',1)[1].split()[:2]==['fuse.sshfs','admin-wcx@10.208.130.164:/home/shared'],'true164 fixed NAS')
 planraw=raw(prefix/'SENDER_PLAN.json');mb=raw(prefix/'MANIFEST.json');need(digest(planraw)==a['sender_plan_sha256']and digest(mb)==a['manifest_sha256'],'exact Root plan/manifest raw')
 plan=json.loads(planraw);m=json.loads(mb);rows=member_rows(m);need(m['asset_id']==asset and m['kind']==('FULL_APPLICATION_TRACE'if a0.phase=='FULL'else'DERIVED_COMPLETE_CTA_TRACE')and set(plan['sources'])=={r['path']for r in rows},'complete sender path set')
 accepted=raw(D/'metadata/ROOT_ACTUAL_DATA_ACCEPTANCE.json');need(digest(accepted)==ROOT_ACCEPT,'original Root accepted exact data')
 os.nice(19);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('ROOT_ARCHIVE_DEADLINE')));signal.alarm(max(1,int(a['absolute_deadline_unix']-time.time())))
 need(__import__('shutil').disk_usage('/root/data').free>=5*1024**3 and __import__('shutil').disk_usage(D).free>=5*1024**3+m['logical_bytes'],'Native/NAS floor+pending')
 held=[];target.parent.mkdir(exist_ok=True)
 try:
  for name in ['CAPTURE','INPUT','OUTPUT','RUNTIME']:
   path=C/'asset_operations'/QID/(name+'.lock');fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC);s=os.fstat(fd);held.append(fd)
   need(stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_size==0,'exact preexisting own asset OFD')
   while True:
    fresh(a['absolute_deadline_unix'])
    try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
    except BlockingIOError:time.sleep(.05)
  fresh(a['absolute_deadline_unix']);need(not target.exists(),'target exists: partialKEEP requires Root reconciliation');target.mkdir()
  for r in rows:
   source=safe(pathlib.Path(plan['sources'][r['path']]));need(source.is_relative_to(pathlib.Path('/root/share/mnt164/huangrulin/traces')),'fixed NAS source domain')
   transfer(source,target/r['path'],r,a['absolute_deadline_unix'])
  transfer(prefix/'MANIFEST.json',target/'MANIFEST.json',dict(bytes=len(mb),sha256=digest(mb)),a['absolute_deadline_unix'])
  verified=verify_members(target,a['manifest_sha256'],a['absolute_deadline_unix'])
  dep=parent_dependency(target,m)if a0.phase=='DERIVED'else None
  fresh(a['absolute_deadline_unix']);commit=dict(schema='RTX4080_SHARED_IMMUTABLE_COMMIT_V1'if a0.phase=='FULL'else'RTX4080_DERIVED_CTA_COMMIT_V1',kind=m['kind'],status='COMMITTED_VERIFIED',asset_id=asset,manifest_sha256=a['manifest_sha256'],files=len(rows),logical_bytes=m['logical_bytes'],Root_private_acceptance_sha256=ROOT_ACCEPT,original_worker_success=False,actual_all_DSO_mapping_coverage='UNKNOWN_NOT_PERSISTED',producer_semantic_status='C8_EXACT_MVT4096_SUPPLEMENTED_LEAF_RC0_FULL_RECORD_INPUT_SOURCE_QA',consumer_per_profile_qualification='NOT_GRANTED;EXACT_SELECTED_FUNCTIONAL_REPLAY_REQUIRED',source_keep=True,release_bytes=0,ssd_payload_staging_bytes=0,shared_catalog_publication='DEFERRED_ROOT_SEPARATE_AUTHORITY',Root_archive_authority_sha256=a0.expected_approval_sha,utc_unix=time.time())
  if dep:commit.update(parent_asset_id=PARENT,parent_commit_sha256=dep['parent_commit_sha256'],parent_manifest_sha256=dep['parent_manifest_sha256'],nominal_fraction=0.025,effective_fraction=0.0625,ctas_retained=2,records_retained=288688,identity_selection=False,no_reduction=False,input_payload_duplicate_bytes=0)
  save_new(target/'COMMIT.json',commit);need(json.loads(raw(target/'COMMIT.json'))==commit,'closed COMMIT raw readback')
  need(not pathlib.Path('/proc/self/task',str(os.getpid()),'children').read_text().strip(),'no owned descendants')
  save_new(D/('ROOT_'+a0.phase+'_ARCHIVE_RECEIVER_READBACK.json'),dict(status='COPY_ONLY_SENDER_WHOLESHA_RECEIVER_ALL_MEMBERS_SHA_COMMIT_READBACK_PASS',commit_sha256=digest(raw(target/'COMMIT.json')),manifest_sha256=a['manifest_sha256'],object=str(target),member_count=len(rows),Source_KEEP=True,public_writes=0))
  print(json.dumps(dict(status='PRIVATE_COMMIT_COMPLETE',asset_id=asset,target=str(target),Source_KEEP=True)))
 finally:
  signal.alarm(0)
  if pathlib.Path('/proc/self/task',str(os.getpid()),'children').read_text().strip():
   while True:time.sleep(1)
  for fd in reversed(held):os.close(fd)
if __name__=='__main__':main()
