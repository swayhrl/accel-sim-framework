"""Private exact one-asset restore candidate. No public CLI/policy installation or bulk authority."""
from pathlib import Path
import argparse,hashlib,json,os,re,stat,time,resource,shutil,signal,math
LIB=Path('/root/share/mnt164/huangrulin/traces')
PAYLOAD=LIB/'bundles/_payload'
AUTH=Path('/root/data/shared_trace_assets_platform_v3/authority/restore_one')
NATIVE=Path('/root/data/trace_assets_restore_one')
EVIDENCE=LIB/'receipts/sm70_restore_one_runs'
G=2**30;M=2**20
def need(x,m):
 if not x:raise RuntimeError('RESTORE_ONE_HOLD_'+m)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def no_links(p):
 p=Path(p);need(p.is_absolute()and'..'not in p.parts,'ABSOLUTE_NO_PARENT_PATH')
 for q in[p,*p.parents]:need(not q.is_symlink(),'NO_SYMLINK')
 return p
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def mount_for(path):
 path=Path(path);matches=[]
 for line in Path('/proc/self/mountinfo').read_text().splitlines():
  left,right=line.split(' - ',1);fields=left.split();mp=Path(fields[4].replace('\\040',' '));after=right.split()
  if path.is_relative_to(mp):matches.append((len(mp.parts),dict(target=str(mp),fstype=after[0],source=after[1])))
 need(matches,'ACTUAL_MOUNT_METADATA')
 depth=max(x[0]for x in matches);rows=[v for n,v in matches if n==depth];need(len(rows)==1,'UNAMBIGUOUS_ACTUAL_MOUNT')
 return rows[0]

def digest64(s):return type(s)is str and re.fullmatch('[0-9a-f]{64}',s)is not None
def relative(s):
 p=Path(s);need(type(s)is str and s and not p.is_absolute()and'..'not in p.parts and'.'not in p.parts,'SAFE_RELATIVE_MEMBER');return p
def raw_json(p,maximum=8*M,account=None):
 p=no_links(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<a.st_size<=maximum,'SMALL_REGULAR_METADATA');raw=b''
  while len(raw)<=maximum:
   b=os.read(fd,min(65536,maximum+1-len(raw)))
   if not b:break
   raw+=b
  z=os.fstat(fd);need(ident(a)==ident(z)and len(raw)==a.st_size,'METADATA_SAME_FD')
 finally:os.close(fd)
 if account:account(len(raw),'metadata')
 def pairs(items):
  d={}
  for k,v in items:need(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs),raw
def pinned(r,account=None):
 p=Path(r['path']);need(p.is_relative_to(LIB)and type(r['bytes'])is int and 0<r['bytes']<=8*M and digest64(r['sha256']),'PINNED_LIBRARY_METADATA')
 x,b=raw_json(p,account=account);need(len(b)==r['bytes']and sha(b)==r['sha256'],'RAW_METADATA_PIN');return x

def validate_registered_asset(request,asset,public,account):
 r=request['registration'];need(Path(r['current_pointer_ref']['path'])==LIB/'catalog/CURRENT_UNIFIED_DISCOVERY.json','CURRENT_REGISTRATION_POINTER_ONLY')
 ptr=pinned(r['current_pointer_ref'],account)
 need(ptr['schema']=='PUBLIC_METADATA_DISCOVERY_POINTER_V1'and ptr['metadata_only']is True,'CURRENT_METADATA_REGISTRATION_POINTER')
 need(Path(r['current_snapshot_ref']['path'])==LIB/'catalog'/ptr['relative_path']and r['current_snapshot_ref']['sha256']==ptr['sha256']and r['current_snapshot_ref']['bytes']==ptr['bytes'],'CURRENT_IMMUTABLE_REGISTRATION_SNAPSHOT_PIN')
 current=pinned(r['current_snapshot_ref'],account);need(current['schema']=='PRIVATE_UNIFIED_TRACE_DISCOVERY_INDEX_V1','SUPPORTED_REGISTERED_SM70_INDEX_SCHEMA')
 rows=current['SM70_exact_inputs'];need(len(rows)==public['bundles'],'REGISTERED_SM70_DENOMINATOR_MATCHES_PRIOR_NAS_ACCEPTANCE')
 exact=[x for x in rows if x['id']==asset['bundle_id']];need(len(exact)==1,'EXACT_CURRENT_REGISTERED_SM70_ASSET_ID')
 a=exact[0];need(a['architecture']=='SM70'and a['members']==asset['members']and a['ordered_kernel_members']==asset['ordered_kernel_members'],'CURRENT_REGISTERED_ASSET_MEMBER_BYTES_JOIN')
 nas=a['current_shared_NAS_access'];need(nas['Root_acceptance_sha256']==request['NAS_access_proof_ref']['sha256']and nas['evidence_sha256']==public['snapshot_ref']['sha256'],'REGISTERED_ASSET_NAS_ACCEPTANCE_BINDING')
 need(current['SM70_current_NAS_access_acceptance']['Root_acceptance_ref']==request['NAS_access_proof_ref'],'CURRENT_SM70_ACCESS_PROOF_JOIN')
 return dict(current_registry_sha256=r['current_snapshot_ref']['sha256'],asset_id=a['id'],registered_member_count=len(a['members']))

def build_plan(request,account=None,stat_chunks=True):
 parent_account=account;metadata_used=[0]
 def account(n,kind):
  metadata_used[0]+=n;need(metadata_used[0]<=16*M,'PLAN_TOTAL_METADATA16MIB_BOUND')
  if parent_account:parent_account(n,kind)
 need(request['schema']=='ROOT_EXACT_SINGLE_SM70_ASSET_RESTORE_REQUEST_V1','REQUEST_SCHEMA')
 ar=request['asset_manifest_ref'];ap=Path(ar['path']);need(ap.parent==LIB/'catalog/bundle_manifests'and ap.name==ar['sha256']+'.json','CONTENT_ADDRESSED_ASSET_MANIFEST')
 asset=pinned(ar,account);need(asset['bundle_id']==request['asset_id']and digest64(asset['bundle_id']),'ONE_EXACT_ASSET_ID')
 public=pinned(request['NAS_access_proof_ref'],account)
 need(public['schema']=='ROOT_FORMAL_ALL125_SHARED_NAS_ACCESS_ACCEPTANCE_V1'and public['status']=='ALL125_25149_SHARED_NAS_ACCESS_ACCEPTED_NOT_NATIVE_CONSUMER','PRIOR_SHARED_NAS_ACCESS_BASIS_NOT_NATIVE_PROOF')
 registration=validate_registered_asset(request,asset,public,account)
 need(asset['architecture']=='70','EXACT_SM70_ASSET')
 members=asset['members'];by={m['relative_path']:m for m in members}
 need(asset['logical_bytes']==sum(m['size']for m in members),'ASSET_LOGICAL_MEMBER_SUM')
 need(len(by)==len(members)and all(type(m['size'])is int and m['size']>=0 and digest64(m['sha256'])for m in members),'UNIQUE_ASSET_MEMBERS')
 selected=request['selected_output_paths'];need(selected and len(selected)==len(set(selected))and set(selected)<=set(by),'EXPLICIT_MEMBER_SET')
 mode=request['selection_mode'];need(mode in['ALL_DECLARED_ASSET_MEMBERS','EXACT_MEMBER_SUBSET'],'RESTORE_SELECTION_MODE')
 if mode=='ALL_DECLARED_ASSET_MEMBERS':need(set(selected)==set(by),'NO_MISSING_ASSET_MEMBERS')
 bindings=request['bindings'];need([r['output_relative_path']for r in bindings]==selected,'EXACT_OUTPUT_BINDING_ORDER')
 for p in selected:
  relative(p);need(not any(q!=p and Path(q).is_relative_to(Path(p))for q in selected),'NO_OUTPUT_FILE_PARENT_COLLISION')
 loaded={};rows=[]
 for binding in bindings:
  key=binding['backing_id'];need(key in request['backings'],'MISSING_SELECTED_MEMBER_BACKING');back=request['backings'][key];bundle=Path(back['bundle'])
  need(all(k in back for k in['commit_ref','manifest_ref','range_index_ref']),'UNSUPPORTED_LAYOUT_REQUIRES_COMMIT_MANIFEST_RANGE_INDEX_NO_TAR_FALLBACK')
  need(bundle.parent==PAYLOAD and re.fullmatch('[0-9a-f]{20,64}',bundle.name)is not None and key==bundle.name,'EXACT_PAYLOAD_NAMESPACE')
  if key not in loaded:
   for k,n in[('commit_ref','COMMIT.json'),('manifest_ref','SOURCE_MANIFEST.json'),('range_index_ref','RANGE_INDEX.json')]:need(Path(back[k]['path'])==bundle/n,'FIXED_COMMIT_METADATA_NAMES')
   commit=pinned(back['commit_ref'],account);manifest=pinned(back['manifest_ref'],account);index=pinned(back['range_index_ref'],account)
   need(commit['schema']=='IMMUTABLE_MULTI_MEMBER_TRACE_INPUT_COMMIT_V1'and commit['object_id']==manifest['object_id']and commit['object_id'].startswith(key),'COMMITTED_OBJECT_ID')
   need(commit['manifest_sha256']==sha(canon(manifest))and commit['range_index_sha256']==sha(canon(index)),'ORIGINAL_CANONICAL_COMMIT_MANIFEST_AND_RANGE_SHA')
   loaded[key]=(commit,manifest,index)
  commit,manifest,index=loaded[key];rel=binding['source_member_relative_path'];relative(rel)
  mm=[m for m in manifest['members']if m['relative_path']==rel];need(len(mm)==1,'ONE_COMMITTED_SOURCE_MEMBER');m=mm[0];a=by[binding['output_relative_path']]
  need(m['type']=='file'and m['sha256']==binding['member_sha256']==a['sha256']and m['size']==binding['size']==a['size'],'ASSET_TO_COMMITTED_MEMBER_BYTE_JOIN')
  need(rel in index,'NO_SELECTED_MEMBER_RANGE_INDEX_NO_TAR_FALLBACK');chunks=index[rel];need(type(chunks)is list and(bool(chunks)or m['size']==0),'COMMITTED_SELECTED_MEMBER_RANGES');off=0;cr=[]
  for c in chunks:
   need(type(c['offset'])is int and c['offset']==off and type(c['size'])is int and 0<c['size']<=128*M and c['name']==str(off).zfill(20)+'.part'and digest64(c['sha256']),'CONTIGUOUS_EXACT_CHUNK_RANGE')
   cp=bundle/'chunks'/sha(rel.encode())/c['name'];no_links(cp)
   if stat_chunks:
    st=cp.stat();need(stat.S_ISREG(st.st_mode)and st.st_size==c['size'],'SELECTED_CHUNK_METADATA_PRESENT_NOT_FRESH_HASH')
   cr.append(dict(c,path=str(cp)));off+=c['size']
  need(off==m['size'],'MEMBER_RANGE_TOTAL')
  rows.append(dict(output_relative_path=a['relative_path'],source_member=m,source_bundle=str(bundle),chunks=cr,commit_ref=back['commit_ref']))
 total=sum(r['source_member']['size']for r in rows)
 return dict(schema='EXACT_SINGLE_ASSET_MEMBER_CHUNK_RESTORE_PLAN_V1',asset_id=asset['bundle_id'],registration=registration,metadata_read_bytes=metadata_used[0],selection_mode=mode,all_declared_members_selected=set(selected)==set(by),members=rows,logical_bytes=total,source_chunk_read_bytes=total,native_closed_readback_bytes=total,native_write_bytes=total,source_tar_scan_bytes=0,chunk_body_SHA_fresh=False,selected_chunk_access='STAT_ONLY_UNTIL_ROOT_EXECUTE',whole_library_readback_required=False,scientific_or_consumer_qualification=False)
class Budget:
 def __init__(self,grant):
  self.a=grant;self.used={k:0 for k in['metadata','source','write','readback']};self.start=time.monotonic()
 def account(self,n,kind):
  self.used[kind]+=n;need(self.used[kind]<=self.a['max_'+kind+'_bytes'],'EXACT_'+kind.upper()+'_BUDGET');self.check()
 def check(self):
  need(self.a['not_before_unix']<=time.time()<self.a['deadline_unix']and time.monotonic()-self.start<=self.a['wall_seconds'],'FINITE_ROOT_CLOCK')
  need(shutil.disk_usage(NATIVE).free>=5*G,'NATIVE_ACTUAL5G_FLOOR')
  mem=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
  need(mem>=self.a['min_host_MemAvailable_bytes'],'CURRENT_ROOT_EXACT_MEMORY_FLOOR')
 def pace(self,n):
  target=n/self.a['source_rate_bytes_s']
  while target>time.monotonic()-self.start:
   time.sleep(min(target-(time.monotonic()-self.start),.25));self.check()
def dirfd(p):
 p=no_links(p);fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:
  for part in p.parts[1:]:
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);os.close(fd);fd=child
  return fd
 except BaseException:os.close(fd);raise
def output_parent(rootfd,rel):
 parts=relative(rel).parts;fd=os.dup(rootfd)
 try:
  for part in parts[:-1]:
   try:os.mkdir(part,mode=0o700,dir_fd=fd)
   except FileExistsError:pass
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);os.close(fd);fd=child
  return fd,parts[-1]
 except BaseException:os.close(fd);raise
def write_json_new(path,obj):
 raw=json.dumps(obj,indent=2,sort_keys=True).encode()+b'\n';need(len(raw)<=M,'BOUNDED_CONTROL_RECEIPT')
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def validate_grant(a,request_raw,code_sha,now=None):
 now=time.time()if now is None else now
 need(a['schema']=='ROOT_EXACT_SINGLE_ASSET_RESTORE_ONE_GRANT_V1'and a['status']=='ROOT_APPROVED_EXACT_SINGLE_ASSET_RESTORE_ONCE','NEW_ROOT_RESTORE_ONE_AUTHORITY_REQUIRED')
 need(a['request_sha256']==sha(request_raw)and a['source_code_sha256']==code_sha,'EXACT_REQUEST_AND_NEW_CODE')
 req=json.loads(request_raw);reg=a['registered_SM70_asset_confirmation']
 need(reg['status']=='ROOT_CONFIRMED_CURRENT_REGISTERED_SM70_ASSET'and reg['asset_id']==req['asset_id']and reg['asset_manifest_sha256']==req['asset_manifest_ref']['sha256']and reg['NAS_access_proof_sha256']==req['NAS_access_proof_ref']['sha256'],'ROOT_EXACT_ASSET_REGISTRATION_CONFIRMATION_NO_ALL_OBJECTS_LEDGER')
 need(re.fullmatch('[A-Za-z0-9_-]{1,80}',a['scope_id'])is not None and re.fullmatch('[A-Za-z0-9_-]{1,80}',a['destination_name'])is not None,'EXACT_SCOPE_AND_TARGET_LEAF')
 need(a['not_before_unix']<=now<a['deadline_unix']<=a['not_before_unix']+a['wall_seconds']and 0<a['wall_seconds']<=3600,'FRESH_BOUNDED_ROOT_WINDOW')
 need(a['Native_floor_bytes']==5*G and a['AS_bytes']==512*M and type(a['CPU_ids'])is list and len(a['CPU_ids'])==1 and type(a['CPU_ids'][0])is int,'ROOT_DISK_MEMORY_CPU_PROFILE')
 need(0<a['max_metadata_bytes']<=16*M,'EXACT_METADATA16MIB_IMPLEMENTATION_LIMIT')
 need(0<a['source_rate_bytes_s']<=64*M and a['min_host_MemAvailable_bytes']>=16*G+512*M,'EXACT_RATE_AND_MEMORY_BUDGET')
 need(a['NAS_mount']==dict(target='/root/share/mnt164',fstype='fuse.sshfs',source='admin-wcx@10.208.130.164:/home/shared'),'EXACT_ROOT_GENUINE164_NAS_PROFILE')
 need(a['Source_KEEP']is True and a['consumer_or_science_qualification_granted']is False,'NO_SOURCE_OR_SCIENCE_CHANGES')
 return a
def execute(a,request,request_raw,plan,budget):
 parent=Path(a['destination_parent_ref']['path']);need(parent.is_relative_to(NATIVE)and parent!=NATIVE.parent,'NEW_DEDICATED_NATIVE_NAMESPACE_ONLY')
 need(mount_for(LIB)==a['NAS_mount'],'CURRENT_GENUINE164_NAS_MOUNT')
 pfd=dirfd(parent);ps=os.fstat(pfd);r=a['destination_parent_ref']
 need((ps.st_dev,ps.st_ino,ps.st_uid)==(r['dev'],r['inode'],0)and stat.S_IMODE(ps.st_mode)==0o700,'ROOT_PINNED_PRIVATE_NATIVE_PARENT')
 need(ps.st_dev==a['native_device']and ps.st_dev==NATIVE.stat().st_dev==Path('/root/data').stat().st_dev,'EXACT_NATIVE_DEVICE')
 need(mount_for(parent)['fstype']=='ext4','ACTUAL_NATIVE_EXT4')
 need(shutil.disk_usage(parent).free>=5*G+plan['logical_bytes'],'PREALLOCATION_PLUS5G_FLOOR')
 need(a['max_source_bytes']==a['max_write_bytes']==a['max_readback_bytes']==plan['logical_bytes'],'NO_BULK_OR_UNSELECTED_PAYLOAD_BUDGET')
 ev=EVIDENCE/a['scope_id'];no_links(EVIDENCE);ev.mkdir(mode=0o700);target=parent/a['destination_name'];dfd=None;proofs=[]
 try:
  os.mkdir(a['destination_name'],mode=0o700,dir_fd=pfd);dfd=os.open(a['destination_name'],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=pfd);destination_identity=os.fstat(dfd)
  write_json_new(ev/'START.json',dict(scope_id=a['scope_id'],request_sha256=sha(request_raw),asset_id=plan['asset_id'],destination=str(target),source_KEEP=True,new_grant_not_old_R5_authority=True))
  for row in plan['members']:
   budget.check();m=row['source_member'];ofd,name=output_parent(dfd,row['output_relative_path']);fd=None
   try:
    fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=ofd)
    if m['size']:os.posix_fallocate(fd,0,m['size'])
    need(os.fstat(fd).st_size==m['size']and(m['size']==0 or os.fstat(fd).st_blocks*512>=m['size']),'REAL_OWNED_PREALLOCATION')
    whole=hashlib.sha256();count=0;chunk_proofs=[]
    for chunk in row['chunks']:
     sfd=dirfd(Path(chunk['path']).parent);sf=os.open(Path(chunk['path']).name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=sfd);os.close(sfd);h=hashlib.sha256();n=0
     try:
      before=os.fstat(sf);need(stat.S_ISREG(before.st_mode)and before.st_size==chunk['size']and before.st_dev==LIB.stat().st_dev,'SOURCE_CHUNK_EXACT_NAS_DEVICE_AND_SIZE')
      while n<chunk['size']:
       b=os.read(sf,min(M,chunk['size']-n));need(b,'SOURCE_CHUNK_EOF');budget.account(len(b),'source');h.update(b);whole.update(b);left=memoryview(b)
       while left:
        z=os.write(fd,left);need(z>0,'SHORT_NATIVE_WRITE');budget.account(z,'write');left=left[z:]
       n+=len(b);count+=len(b);budget.pace(budget.used['source'])
      need(n==before.st_size and ident(os.fstat(sf))==ident(before)and h.hexdigest()==chunk['sha256'],'FRESH_CHUNK_WHOLESHA_AND_STABLE_FD')
     finally:os.close(sf)
     chunk_proofs.append(dict(path=chunk['path'],bytes=n,sha256=h.hexdigest(),full_SHA_fresh=True))
    need(count==m['size']and whole.hexdigest()==m['sha256'],'FRESH_MEMBER_WHOLESHA')
    os.fsync(fd);os.fchown(fd,m['uid'],m['gid']);os.fchmod(fd,m['mode']);os.utime(fd,ns=(m['mtime_ns'],m['mtime_ns']));closed=os.fstat(fd);os.close(fd);fd=None
    rf=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=ofd);h=hashlib.sha256();n=0
    try:
     rb=os.fstat(rf);need(ident(rb)==ident(closed)and rb.st_nlink==1,'CLOSED_REOPEN_SAME_NATIVE_OBJECT')
     while n<m['size']:
      b=os.read(rf,min(M,m['size']-n));need(b,'CLOSED_NATIVE_EOF');h.update(b);n+=len(b);budget.account(len(b),'readback')
     need(ident(os.fstat(rf))==ident(rb)and n==m['size']and h.hexdigest()==m['sha256'],'CLOSED_REOPEN_NATIVE_WHOLESHA')
    finally:os.close(rf)
    need((closed.st_uid,closed.st_gid,stat.S_IMODE(closed.st_mode),closed.st_mtime_ns)==(m['uid'],m['gid'],m['mode'],m['mtime_ns']),'ORIGINAL_MEMBER_NUMERIC_METADATA')
    proofs.append(dict(relative_path=row['output_relative_path'],bytes=n,member_sha256=m['sha256'],native_closed_reopen_sha256=h.hexdigest(),chunks=chunk_proofs,original_member_numeric_metadata_preserved=True))
   finally:
    if fd is not None:os.close(fd)
    os.close(ofd)
  now=os.stat(a['destination_name'],dir_fd=pfd,follow_symlinks=False);need((now.st_dev,now.st_ino)==(destination_identity.st_dev,destination_identity.st_ino),'FINAL_DESTINATION_NAMESPACE')
  result=dict(schema='ROOT_EXACT_SINGLE_ASSET_FRESH_NATIVE_RESTORE_RECEIPT_V1',status='EXACT_SELECTED_MEMBERS_NATIVE_WHOLESHA_CLOSED',asset_id=plan['asset_id'],scope_id=a['scope_id'],request_sha256=sha(request_raw),source_code_sha256=a['source_code_sha256'],destination=str(target),selection_mode=plan['selection_mode'],all_declared_members_materialized=plan['all_declared_members_selected'],members=proofs,budget_used=budget.used,source_tar_scan_bytes=0,whole_library_restored=False,consumer_or_scientific_qualification=False,Source_KEEP=True,release_bytes=0,destination_root_metadata='NEW_ROOT_OWNED_DIRECTORY_NOT_HISTORICAL_ROOT')
  write_json_new(ev/'RESULT.json',result);return result
 except BaseException as error:
  write_json_new(ev/'FAILURE_RETAINED.json',dict(status='FAILED_PARTIAL_RETAINED_NOT_RESTORE_PASS',error=repr(error),destination=str(target),completed_members=proofs,budget_used=budget.used,Source_KEEP=True,partial_destination_KEEP=True));raise
 finally:
  if dfd is not None:os.close(dfd)
  os.close(pfd)
def main():
 p=argparse.ArgumentParser();p.add_argument('--asset',required=True);p.add_argument('--request',required=True);p.add_argument('--request-sha',required=True);p.add_argument('--inspect-metadata',action='store_true');p.add_argument('--grant');p.add_argument('--grant-sha');p.add_argument('--execute',action='store_true');a=p.parse_args()
 rp=Path(a.request);need(rp.is_relative_to(LIB/'receipts'),'PRIVATE_REQUEST_METADATA_NAMESPACE');request,raw=raw_json(rp,M);need(sha(raw)==a.request_sha and request['asset_id']==a.asset,'EXACT_ASSET_REQUEST_RAW_SHA')
 if a.inspect_metadata:
  need(not a.execute and not a.grant and not a.grant_sha,'INSPECT_HAS_NO_BODY_PERMISSION');print(json.dumps(build_plan(request),indent=2));return
 need(a.execute and a.grant and a.grant_sha,'EXPLICIT_FRESH_ROOT_GRANT_AND_EXECUTE')
 gp=no_links(a.grant);need(gp.parent==AUTH,'NEW_SEPARATE_RESTORE_ONE_AUTHORITY');st=gp.stat();need(st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o600,'ROOT0600_GRANT')
 grant,graw=raw_json(gp,M);need(sha(graw)==a.grant_sha,'GRANT_RAW_SHA');code_raw=Path(__file__).read_bytes();validate_grant(grant,raw,sha(code_raw))
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('ROOT_RESTORE_ONE_ABSOLUTE_DEADLINE')));signal.alarm(max(1,math.ceil(grant['deadline_unix']-time.time())))
 need(os.geteuid()==0,'NATIVE_NUMERIC_RESTORE_ROOT');resource.setrlimit(resource.RLIMIT_AS,(512*M,512*M));resource.setrlimit(resource.RLIMIT_CORE,(0,0));need(set(grant['CPU_ids'])<=os.sched_getaffinity(0),'ROOT_CPU_CURRENTLY_ALLOWED');os.sched_setaffinity(0,set(grant['CPU_ids']))
 if os.getpriority(os.PRIO_PROCESS,0)<15:os.nice(15-os.getpriority(os.PRIO_PROCESS,0))
 budget=Budget(grant);budget.account(len(raw)+len(graw)+len(code_raw),'metadata');plan=build_plan(request,budget.account)
 result=execute(grant,request,raw,plan,budget);signal.alarm(0);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
