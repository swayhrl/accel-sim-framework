"""New174 controller for the authorized seven-asset fast retirement."""
import fcntl,gzip,hashlib,json,os,pathlib,re,shlex,stat,subprocess,sys,time,traceback
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');OUT=T/'control/second_batch7_fast_retirement_20261104_v1';sys.path.insert(0,str(T/'tools'));import retire_174new_build_duplicates as audit
N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/second_batch7_fast_retirement_20261104_v1');ASSET_ROOT=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets');BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
ORDER=[('cutcp','TRACE_9d6ff92257d20b4b'),('scan','TRACE_d6c21d018154d3b5'),('stencil','TRACE_5e9aefe64e214679'),('kmeans','TRACE_9ad2f284f8c2a318'),('histo','TRACE_777ae84f37927c4e'),('3MM','TRACE_cf75342164f0b212'),('3DConvolution','TRACE_694a568c425385d3')]
def need(v,m):
 if not v:raise RuntimeError(m)
def blob(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def putpair(local,remote,x):b=blob(x);audit.put(local,b);audit.put(remote,b)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def identity(p):
 s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory')
def ssh_worker(args,timeout=900):
 worker=T/'tools/second_batch7_source_worker.py';cmd=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174','nice -n 19 ionice -c 3 python3 -B '+shlex.quote(str(worker))+' '+args];r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout);return r
def parse_ok(r):need(r.returncode==0,r.stderr.decode(errors='replace')[-3000:]);return json.loads(r.stdout)
def target_check(aid,m):
 B=ASSET_ROOT/aid;mraw=(B/'SOURCE_MANIFEST.json').read_bytes();need(mraw==(T/'manifests'/(aid+'.json')).read_bytes(),'true164 manifest changed');craw=(B/'COMMIT.json').read_bytes();c=json.loads(craw);need(c['manifest_sha256']==hashlib.sha256(mraw).hexdigest(),'COMMIT manifest link changed');need(sha(B/'RANGE_INDEX.json')==c['range_index_sha256'] and sha(B/'TREE_VERIFICATION.json')==c['tree_verification_sha256'],'range/tree receipt changed');expected={x['relative_path']:x for x in m['members']};actual={p.relative_to(B/'tree').as_posix() for p in (B/'tree').rglob('*') if p.is_file() and not p.is_symlink()};need(actual==set(expected),'true164 member set changed');rows=[]
 for name,x in expected.items():
  p=B/'tree'/name;need(p.stat().st_size==x['size'],'true164 size changed '+name);prefix=bytes.fromhex(x['header_prefix_hex']);need(p.open('rb').read(len(prefix))==prefix,'true164 header changed '+name);rows.append({'relative_path':name,'identity':identity(p)})
 need((B/'RESTORE.sh').is_file() and (B/'NATIVE_RESTORE_STATUS.json').is_file(),'restore entry missing');return dict(bundle=str(B),manifest_sha256=hashlib.sha256(mraw).hexdigest(),commit_sha256=hashlib.sha256(craw).hexdigest(),members=rows,restore_entry=str(B/'RESTORE.sh').replace('/root/share/mnt164','/home/shared',1))
def physical(source,files):
 base='/'+source['upperdir'].removeprefix('/mnt/data/').strip('/');parents={str((P(source['source_root'])/x['relative_path']).parent) for x in files};entries={}
 for parent in parents:
  r=subprocess.run(['debugfs','-n','-R','ls -l '+base+parent,'/dev/sdf'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
  for line in r.stdout.splitlines():
   z=line.split()
   if len(z)>=9 and z[0].isdigit():
    try:entries[(parent,z[-1])]=(int(z[0]),int(z[5]))
    except:pass
 proof=[]
 for x in files:
  full=P(source['source_root'])/x['relative_path'];need(entries.get((str(full.parent),full.name))==(x['identity']['inode'],x['identity']['size']),'not exact upper '+x['relative_path']);proof.append({'relative_path':x['relative_path'],'inode':x['identity']['inode'],'size':x['identity']['size'],'allocated_bytes':x['identity']['allocated']})
 return dict(status='PASS',method='read-only debugfs ls of exact current overlay upperdir',files=proof,total_allocated_bytes=sum(x['allocated_bytes'] for x in proof))
def asset_pair(aid,name,x):putpair(OUT/'assets'/aid/name,N/'assets'/aid/name,x)
def main():
 audit.q.mount_check();lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);need(not (OUT/'EXECUTION_START.json').exists() and not (N/'EXECUTION_START.json').exists(),'execution exists');auth=OUT/'USER_AUTHORIZATION.md';need(auth.is_file(),'authorization missing');protected_before=parse_ok(ssh_worker('--protected'));start_free=os.statvfs('/root/data').f_bavail*os.statvfs('/root/data').f_frsize;start=dict(schema='ORIGINAL174_SECOND_BATCH7_EXECUTION_START_V1',unix=time.time(),order=[a for _,a in ORDER],authorization_sha256=sha(auth),start_SSD_available_bytes=start_free,full_body_SHA_rescan=False,full_native_restore=False,capacity_precondition_waived=True);putpair(OUT/'EXECUTION_START.json',N/'EXECUTION_START.json',start);results=[]
 for workload,aid in ORDER:
  intent_written=False
  try:
   audit_source=parse_ok(ssh_worker('--audit-asset '+aid));mraw=(T/'manifests'/(aid+'.json')).read_bytes();m=json.loads(mraw);expected={x['relative_path']:x for x in m['members']};need(audit_source['root_exists'] and set(audit_source['current_files'])==set(expected),'Source membership changed');by={x['relative_path']:x for x in audit_source['members']};need(all(by[n]['exists'] for n in expected),'Source member missing')
   for n,x in expected.items():
    cur=by[n]['identity'];need(all(cur[k]==x[k] for k in ['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','nlink','type']),'Source identity changed '+n)
   need(not audit_source['readers_writers'] and not audit_source['unreadable_processes'],'active/unreadable Source process');pl=audit_source['planned'];need(not pl['source']['exact_path_matches'] and not pl['native']['exact_path_matches'] and not pl['scheduled_or_script_matches'],'planned reader appeared');need(audit_source['IO']['some']['avg60']<25 and audit_source['IO']['full']['avg60']<20,'severe I/O pressure');need(audit_source['SSD_available_bytes']>=7*1024**3+1024**3+64*1024**2,'below basic SSD safety floor')
   target=target_check(aid,m);files=[];controls=[]
   for n,x in expected.items():
    row=dict(x,identity=by[n]['identity']);(files if n.endswith('.traceg') else controls).append(row)
   need(files and all(x['relative_path'].endswith('.traceg') for x in files),'trace whitelist empty');phys=physical(audit_source,files);pre=dict(schema='ORIGINAL174_SECOND_BATCH7_ASSET_PRE_DELETE_AUDIT_V1',status='PASS',unix=time.time(),workload=workload,asset_id=aid,source=audit_source,true164=target,reused_full_SHA_and_COMMIT=True,physical=phys,capacity_precondition_waived=True);asset_pair(aid,'PRE_DELETE_AUDIT.json',pre)
   q=dict(schema='ORIGINAL174_SECOND_BATCH7_QUALIFIED_WHITELIST_V1',asset_id=aid,workload=workload,source_root=m['source_root'],files=files,controls=controls,logical_trace_bytes=sum(x['size'] for x in files),allocated_trace_bytes=sum(x['identity']['allocated'] for x in files),manifest_sha256=hashlib.sha256(mraw).hexdigest(),commit_sha256=target['commit_sha256'],pre_audit_sha256=sha(OUT/'assets'/aid/'PRE_DELETE_AUDIT.json'),authorization_sha256=sha(auth));asset_pair(aid,'QUALIFIED_WHITELIST.json',q)
   intent=dict(schema='ORIGINAL174_SECOND_BATCH7_ASSET_INTENT_V1',unix=time.time(),workload=workload,asset_id=aid,source_root=m['source_root'],files=len(files),logical_bytes=q['logical_trace_bytes'],allocated_bytes=q['allocated_trace_bytes'],qualified_whitelist_sha256=sha(OUT/'assets'/aid/'QUALIFIED_WHITELIST.json'),capacity_precondition_waived=True,full_native_restore_required_before_unlink=False,recursive_delete_authorized=False);asset_pair(aid,'INTENT.json',intent);intent_written=True
   run=ssh_worker('--execute '+aid,1800);log={'returncode':run.returncode,'stdout':run.stdout.decode(errors='replace'),'stderr':run.stderr.decode(errors='replace'),'unix':time.time()};asset_pair(aid,'SOURCE_WORKER_LOG.json',log);need(run.returncode==0,'worker failed '+log['stderr'][-2000:]);done=json.loads((OUT/'assets'/aid/'SOURCE_DONE.json').read_bytes());need(done['status']=='DONE' and done['files']==len(files),'Source DONE changed');target_check(aid,m)
   records=[]
   for i in range(len(files)):records.append({'INTENT':json.loads((OUT/'assets'/aid/'per_file'/('%04d.INTENT.json'%i)).read_bytes()),'DONE':json.loads((OUT/'assets'/aid/'per_file'/('%04d.DONE.json'%i)).read_bytes())})
   raw=b''.join((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode() for x in records);gz=gzip.compress(raw,compresslevel=9,mtime=0);audit.put(N/'assets'/aid/'PER_FILE_INTENT_DONE.jsonl.gz',gz);audit.put(N/'assets'/aid/'SOURCE_DONE.json',(OUT/'assets'/aid/'SOURCE_DONE.json').read_bytes());final=dict(done,schema='ORIGINAL174_SECOND_BATCH7_ASSET_DONE_CONTROLLER_V1',workload=workload,per_file_transactions=len(files),per_file_journal_uncompressed_sha256=hashlib.sha256(raw).hexdigest(),per_file_journal_gzip_sha256=hashlib.sha256(gz).hexdigest(),true164_unchanged=True,restore_entry=target['restore_entry'],full_native_restore_performed=False);asset_pair(aid,'DONE_CONTROLLER.json',final);results.append({'workload':workload,'asset_id':aid,'status':'DONE','files':len(files),'logical_bytes':done['logical_bytes_unlinked'],'allocated_bytes':done['allocated_bytes_unlinked'],'df_delta':done['df_interval_delta']})
  except BaseException as e:
   hold=dict(schema='ORIGINAL174_SECOND_BATCH7_ASSET_HOLD_V1',status='HOLD_PARTIAL_REVIEW_REQUIRED' if intent_written else 'HOLD_BEFORE_INTENT',unix=time.time(),workload=workload,asset_id=aid,error=repr(e),traceback=traceback.format_exc(),intent_written=intent_written,no_forced_delete=True);asset_pair(aid,'HOLD.json',hold);results.append({'workload':workload,'asset_id':aid,'status':hold['status'],'error':repr(e)})
 protected_after=parse_ok(ssh_worker('--protected'));need(protected_before==protected_after,'protected asset changed');end_free=os.statvfs('/root/data').f_bavail*os.statvfs('/root/data').f_frsize;final=dict(schema='ORIGINAL174_SECOND_BATCH7_FINAL_CONTROLLER_V1',status='DONE' if all(x['status']=='DONE' for x in results) else 'DONE_WITH_HOLDS',unix=time.time(),results=results,DONE_count=sum(x['status']=='DONE' for x in results),HOLD_count=sum(x['status']!='DONE' for x in results),files_unlinked=sum(x.get('files',0) for x in results if x['status']=='DONE'),logical_bytes_unlinked=sum(x.get('logical_bytes',0) for x in results if x['status']=='DONE'),allocated_bytes_unlinked=sum(x.get('allocated_bytes',0) for x in results if x['status']=='DONE'),SSD_available_before_bytes=start_free,SSD_available_after_bytes=end_free,SSD_interval_delta=end_free-start_free,protected_assets_exactly_unchanged=True,no_other_assets_modified=True);putpair(OUT/'FINAL_CONTROLLER.json',N/'FINAL_CONTROLLER.json',final);print(json.dumps(final),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as e:audit.put(N/('GLOBAL_CONTROLLER_FAILURE_%d.json'%time.time_ns()),audit.blob({'error':repr(e),'traceback':traceback.format_exc(),'unix':time.time(),'no_blind_retry':True}));raise
