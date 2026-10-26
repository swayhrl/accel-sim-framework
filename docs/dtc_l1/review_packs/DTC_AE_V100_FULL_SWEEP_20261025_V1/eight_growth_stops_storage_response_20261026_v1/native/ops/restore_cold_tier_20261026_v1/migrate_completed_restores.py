import pathlib,json,os,stat,hashlib,shutil,subprocess,time,datetime,uuid
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=F/'ops/restore_cold_tier_20261026_v1';NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_completed_restore_cold_tier_20261026_v1');ROOTS=[('repair23',F/'validation'),('original',T)];D.mkdir(exist_ok=True)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def manifest(root):
 rows=[]
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   p=P(base)/name;rel=str(p.relative_to(root));s=p.lstat()
   if stat.S_ISLNK(s.st_mode):rows.append(dict(path=rel,type='symlink',target=os.readlink(p)))
   elif stat.S_ISDIR(s.st_mode):rows.append(dict(path=rel,type='directory'))
   elif stat.S_ISREG(s.st_mode):rows.append(dict(path=rel,type='file',bytes=s.st_size,sha256=sha(p)))
   else:raise RuntimeError('unknown restore entry type '+str(p))
 return sorted(rows,key=lambda x:x['path'])
mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0];assert mount['fstype']=='fuse.sshfs'and mount['source']=='admin-wcx@10.208.130.164:/home/shared';reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');requests={'repair23':'DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1','original':'DTC_AE_V100_FULL_SWEEP_20261025_V1'};selected=[];cutoff=1793015340
for label,root in ROOTS:
 q=reg['registered_future_requests'][requests[label]]
 for c,row in q['consumed'].items():
  ap=root/'control'/(c+'_ARCHIVE_RECEIPT.json');dp=root/'control/qualification_ledger'/(c+'.DONE.json')
  if not(ap.exists()and dp.exists()and ap.stat().st_mtime<cutoff and'execution_receipt'in row):continue
  r=read(ap);assert r['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and r['source_disposition']=='SOURCE_KEEP'and read(dp)==row['execution_receipt'];src=P(r['native_restore']);allowed=root/'DTC/run/recovery';dst=NAS/label/src.name;assert src.parent==allowed
  if src.is_symlink():assert src.resolve()==dst.resolve()and dst.is_dir();continue
  assert src.is_dir()and src.resolve().parent==allowed.resolve()and not dst.exists();selected.append(dict(scope=label,cohort=c,uuid=row['uuid'],source=src,target=dst,old_archive_receipt_path=str(ap),old_archive_receipt_sha256=sha(ap)))
assert selected
# Active process file descriptors and mapped files must not use any selected restore.
prefixes=tuple(str(x['source'])+'/'for x in selected)
for proc in P('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  for fd in(proc/'fd').iterdir():
   try:value=os.readlink(fd)
   except OSError:continue
   assert not value.startswith(prefixes),('active restore descriptor',proc.name)
  maps=(proc/'maps').read_text()
  assert not any(prefix in maps for prefix in prefixes),('active restore mapping',proc.name)
 except(FileNotFoundError,ProcessLookupError,PermissionError):continue
v=os.statvfs(T);before=v.f_bavail*v.f_frsize;records=[];manifest_dir=D/'manifests';manifest_dir.mkdir(exist_ok=True);NAS.mkdir(parents=True,exist_ok=True);print(json.dumps(dict(status='VERIFIED_MATURE_COMPLETED_RESTORE_SELECTION',copies=len(selected),native_free_GiB=round(before/2**30,2))),flush=True)
for i,item in enumerate(selected):
 src=item['source'];dst=item['target'];dst.parent.mkdir(parents=True,exist_ok=True);m=manifest(src);logical=sum(x.get('bytes',0)for x in m);mp=manifest_dir/(item['scope']+'_'+src.name+'.json');saved=dict(source=str(src),target=str(dst),entries=m)
 if mp.exists():assert read(mp)==saved
 else:mp.write_text(json.dumps(saved,indent=2)+'\n')
 writing=dst.with_name(dst.name+'.writing-'+uuid.uuid4().hex);writing.mkdir()
 # Create all regular destinations before relative symlinks. SSHFS may reject
 # copystat on an as-yet dangling forward symlink from copytree's iteration order.
 for entry in m:
  if entry['type']=='directory':(writing/entry['path']).mkdir(parents=True,exist_ok=True)
 for entry in m:
  if entry['type']=='file':
   target=writing/entry['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/entry['path'],target)
 for entry in m:
  if entry['type']=='symlink':(writing/entry['path']).symlink_to(entry['target'])
 assert manifest(writing)==m and manifest(src)==m;writing.rename(dst);assert manifest(dst)==m
 # Preserve byte access at the same historic pathname via a transparent cold-tier
 # link. Future native-device revalidation must first rehydrate this exact copy.
 staging=src.with_name('.DTC_COLD_EVICT_'+src.name+'_'+uuid.uuid4().hex);assert not staging.exists();src.rename(staging)
 try:src.symlink_to(dst,target_is_directory=True);assert src.is_symlink()and src.resolve()==dst.resolve()and manifest(src)==m
 except BaseException:
  if src.is_symlink():src.unlink()
  staging.rename(src);raise
 assert staging.is_dir()and not staging.is_symlink()and staging.resolve().parent==src.parent.resolve()and staging.name.startswith('.DTC_COLD_EVICT_');shutil.rmtree(staging);assert manifest(src)==m
 record=dict(scope=item['scope'],cohort=item['cohort'],uuid=item['uuid'],historic_native_restore_path=str(src),cold_164_path=str(dst),bytes=logical,entries=len(m),manifest_path=str(mp),manifest_sha256=sha(mp),old_archive_receipt_path=item['old_archive_receipt_path'],old_archive_receipt_sha256=item['old_archive_receipt_sha256'],source_result_DIRECTORY_SOURCE_KEEP_unchanged=True,completed_restore_currently_on_164=True,rehydrate_to_native_before_new_native_device_verification=True);assert sha(item['old_archive_receipt_path'])==item['old_archive_receipt_sha256'];records.append(record)
 with(D/'TRANSACTIONS.jsonl').open('a')as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
 if i%20==0 or i+1==len(selected):v=os.statvfs(T);print(json.dumps(dict(migrated=i+1,of=len(selected),verified_bytes=sum(r['bytes']for r in records),native_free_GiB=round(v.f_bavail*v.f_frsize/2**30,2))),flush=True)
v=os.statvfs(T);out=dict(status='COMPLETED_RESTORE_COPIES_VERIFIED_ON_164_AND_LOCAL_PAYLOAD_EVICTED',CST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),copies=len(records),verified_logical_bytes=sum(x['bytes']for x in records),native_free_before_GiB=round(before/2**30,2),native_free_after_GiB=round(v.f_bavail*v.f_frsize/2**30,2),records=records,scientific_model_signals=0,scientific_source_or_result_or_ledger_mutations=0,old_archive_receipts_unchanged=True,historical_original_native_restore_verifications_preserved=True,new_native_device_verification_requires_rehydration=True)
with(D/'RESULT.json').open('x')as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items()if k!='records'}),flush=True)
