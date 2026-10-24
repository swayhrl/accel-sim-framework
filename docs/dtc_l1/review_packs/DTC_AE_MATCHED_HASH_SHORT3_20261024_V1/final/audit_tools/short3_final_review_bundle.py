"""COPY_ONLY final evidence/runtime bundle. No scientific launcher or ledger API.

Reuses the pinned, already exercised V9 bundle primitives and immutable outbox
range writer. It never calls experiment, controller, model main or archive(cohort).
"""
import pathlib,json,hashlib,datetime,subprocess,importlib.util,shutil,os,stat,tarfile,fcntl,time
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1');N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2');F=T/'docs-worktree';P=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1'
SOURCE=json.loads((T/'analysis/FINAL_SCIENCE_COMMIT.json').read_text())['commit'];ROOT=T/('final_review_payload_'+SOURCE[:8]);MIB=1024**2
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
def cp(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def inventory(f):
 rows=[]
 for p in [ROOT,*sorted(ROOT.rglob('*'))]:
  s=p.lstat();r=f.ident(s);r.update(path=p.relative_to(ROOT).as_posix(),type='directory' if stat.S_ISDIR(s.st_mode) else 'file' if stat.S_ISREG(s.st_mode) else 'unsupported')
  assert r['type']!='unsupported','payload only permits reviewed regular files/directories'
  if r['type']=='file':r['sha256']=f.file_sha(p)
  rows.append(r)
 return rows
def acquire_copyonly_pair(science,receiver):
 started=time.monotonic()
 while True:
  held=False
  try:
   fcntl.flock(science,fcntl.LOCK_EX|fcntl.LOCK_NB);held=True
   fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB);return
  except BlockingIOError:
   if held:fcntl.flock(science,fcntl.LOCK_UN)
   if time.monotonic()-started>21600:raise
   print(json.dumps({'state':'WAIT_COPYONLY_REVIEW_SHARED_LOCK','elapsed_seconds':time.monotonic()-started,'new_model_starts':0}),flush=True);time.sleep(30)
assert git(F,'rev-parse','HEAD')==SOURCE and not git(F,'status','--porcelain')
pub=read(T/'analysis/FINAL_SCIENCE_PUBLICATION_READBACK.json');assert pub['verified'] and pub['commit']==SOURCE and len(pub['published_final_files'])>=12
assert not ROOT.exists() and not (T/'analysis/FINAL_REVIEW_ARCHIVE_RECEIPT.json').exists(),'one closed data-only export; inspect existing artifacts before reuse'
regfile=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';epochfile=N/'control/CURRENT_SCIENCE_EPOCH.json';regsha=sha(regfile);epochsha=sha(epochfile);q=read(regfile)['registered_future_requests']['DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'];assert q['state']=='COMPLETE' and q['remaining']==0 and len(q['consumed'])==12
science_lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');receiver=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');acquire_copyonly_pair(science_lock,receiver)
m=load('unchanged_outbox_data_primitives',T/'tools/short3_result_base_floor5_v3.py');adapter=load('qualified_current_peer_resource_gate',T/'tools/short3_result_floor5_v3.py');adapter.bind_gate(m);f,v=m.libraries()
runtime={}
for cell in read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['matrix_order']:
 for r in read(T/'control'/(cell+'_SPEC.json'))['runtime_files']:
  path=pathlib.PurePosixPath(r['target']);assert not path.is_absolute() and '..' not in path.parts
  src=T/r['target'];assert str(src.resolve())==r['actual_realpath'] and f.file_sha(src.resolve())==r['sha256']
  if r['target'] in runtime:assert runtime[r['target']]['sha256']==r['sha256']
  runtime[r['target']]=r
planned=sum(p.stat().st_size for p in P.rglob('*') if p.is_file())+sum((T/n).stat().st_size for n in runtime)+2*MIB
assert planned<=128*MIB,'bounded final payload cap';admission=m.gate(2*planned+32*MIB)
ROOT.mkdir(mode=0o700);shutil.copytree(P,ROOT/'review_pack',symlinks=True)
for name,r in runtime.items():
 destination=ROOT/'exact_runtime/original_targets'/name;cp((T/name).resolve(),destination);assert f.file_sha(destination)==r['sha256']
write(ROOT/'exact_runtime/ORIGINAL_TARGET_SHA_AND_REALPATH.json',runtime)
cp(F/'DTC_MAIN_ACTIVE_GOAL.md',ROOT/'provenance/DTC_MAIN_ACTIVE_GOAL_SCIENCE_COMMIT.md')
cp(T/'analysis/FINAL_SCIENCE_PUBLICATION_READBACK.json',ROOT/'provenance/FINAL_SCIENCE_PUBLICATION_READBACK.json')
cp(T/'analysis/FINAL_SCIENCE_COMMIT.json',ROOT/'provenance/FINAL_SCIENCE_COMMIT.json')
cp(pathlib.Path(__file__),ROOT/'provenance/final_review_bundle.py')
for name,parent in [('core','c8090115bd57512b1b23fca7d925301fa620c751'),('framework','8e43c75a5e2eb60a8466084602b7df8117111e89')]:
 dst=ROOT/'source_delta_bundles'/(name+'.bundle');dst.parent.mkdir(exist_ok=True);subprocess.run(['git','-C',str(T/name),'bundle','create',str(dst),'HEAD','^'+parent],check=True)
write(ROOT/'source_delta_bundles/PREREQUISITES.json',{'scope':'Exact new source commit deltas; full parent commits are prerequisites, not claimed embedded. Compiled runtime bytes are embedded separately.','core':{'parent':'c8090115bd57512b1b23fca7d925301fa620c751','head':'2e3bef4364e578cddd0e881c0baace2e51c55930'},'framework':{'parent':'8e43c75a5e2eb60a8466084602b7df8117111e89','head':'cfd3ff56d7ba6642dab6c7710ec4f6065168174e'}})
(ROOT/'README_RECOVERY_SCOPE.md').write_text('''# Final COPY_ONLY evidence/runtime recovery payload

This payload fixes the scientific review pack at the source scientific commit recorded in the manifest and provenance. It contains the full report/qualification/native/strict/archive/restore receipt package, current specs/configs/control snapshots, exact qualified runtime bytes and source-delta Git bundles. Runtime aliases are materialized as regular byte copies in this payload; the original target SHA and original realpaths are recorded. The twelve original full raw-result archives are referenced by their immutable true164 roots and whole-archive SHA; their payload is not duplicated here. Original trace input is also already archived and referenced, not copied again.

Source-delta bundles require their stated parent commits for source rebuilding. They are not a claim of a standalone full-history Git repository. Exact compiled binary/library bytes are recoverable independently of Git history. The scientific report's delivery paragraph is a timestamped pre-export snapshot; the subsequently published final delivery receipt closes this data-only chain without a self-referential archive.

All original data remain SOURCE_KEEP. This export, archive verification and native ext4 restore do not execute a model or grant science budget.12/12 starts were consumed before this copy. Future scientific execution requires a new exact request. Restore with the included pinned full_result_bundle.py/v9_transaction.py primitives into an absent native ext4 destination, validate full archive SHA, and check every entry's uid/gid/mode/mtime_ns/content SHA. No restore command in this package launches a simulator.
''')
entries=inventory(f);raw=sum(r['size'] for r in entries if r['type']=='file');assert raw<=128*MIB
selector=m.sha(m.canon(entries));tx=m.sha(m.canon({'source_commit':SOURCE,'selector_sha256':selector,'source_root':str(ROOT),'scope':'FINAL_REVIEW_COPY_ONLY_NO_SCIENTIFIC_START'}))
bundle=m.NAS/'FINAL_REVIEW_EVIDENCE'/tx
manifest={'schema':'DTC_AEFAIR_FINAL_REVIEW_COPY_ONLY_V1','txid':tx,'source_root':str(ROOT),'source_commit':SOURCE,'selector_sha256':selector,'entries':entries,'reused_objects':{},'source_disposition':'SOURCE_KEEP','scientific_acceptance_granted_by_this_archive':False,'scientific_starts_by_this_operation':0,'persistent164_root':str(bundle).replace('/root/share/mnt164','/home/shared',1)}
before=m.gate(raw+16*MIB);assert receiver is not None
assert not bundle.exists(),'exclusive new immutable final review transaction';bundle.mkdir(parents=True);(bundle/'chunks').mkdir();v.exclusive_json(bundle/'SOURCE_MANIFEST.json',manifest)
for name,data in [('full_result_bundle.py',(m.BASELINE/'full_result_bundle.py').read_bytes()),('v9_transaction.py',(m.BASELINE/'v9_transaction.py').read_bytes()),('RESULT_ENGINE_PIN.json',(T/'control/RESULT_ENGINE_PIN.json').read_bytes()),('final_review_bundle.py',pathlib.Path(__file__).read_bytes())]:
 with (bundle/name).open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
w=m.RangeWriter(bundle,manifest,v,f)
with tarfile.open(fileobj=w,mode='w|',format=tarfile.PAX_FORMAT) as tar:
 for r in entries:
  p=f.safe(ROOT,r['path']);item=tarfile.TarInfo(r['path']);item.uid=r['uid'];item.gid=r['gid'];item.uname=item.gname='';item.mode=r['mode'];item.mtime=r['mtime_ns']//10**9;item.pax_headers={'mtime':str(r['mtime_ns']//10**9)+'.'+str(r['mtime_ns']%10**9).zfill(9)}
  if r['type']=='directory':item.type=tarfile.DIRTYPE;tar.addfile(item)
  else:
   item.size=r['size']
   with p.open('rb') as stream:tar.addfile(item,stream)
index=w.finish();assert inventory(f)==entries,'owned payload changed during export';v.exclusive_json(bundle/'ARCHIVE_INDEX.json',index);v.exclusive_json(bundle/'COMMIT.json',{'txid':tx,'manifest_sha256':m.sha(m.canon(manifest)),'archive_index_sha256':m.sha(m.canon(index)),'policy':'EXCLUSIVE_CREATE_COMMIT_MARKER_LAST'})
f.verify_archive(bundle,manifest);rf,rv=m.libraries(bundle);rf.verify_archive(bundle,manifest)
parent=T/'analysis/final_review_recovery';parent.mkdir(exist_ok=True);destination=parent/tx;proof=rf.restore(bundle,manifest,destination,rv,gate=lambda:m.gate());assert len(proof)==len(entries);rf.check_native(destination,manifest)
v.exclusive_json(bundle/'RESTORE_VERIFIED_NATIVE_TARGET.json',{'scope':'174-new native ext4, no native164 execution','txid':tx,'rows':proof})
assert sha(regfile)==regsha and sha(epochfile)==epochsha,'data export mutated native authority';assert git(F,'rev-parse','HEAD')==SOURCE and not git(F,'status','--porcelain');assert inventory(f)==entries
receipt={'schema':'DTC_AEFAIR_FINAL_REVIEW_ARCHIVE_RECEIPT_V1','status':'FINAL_REVIEW_RUNTIME_ARCHIVE_AND_NATIVE_RESTORE_VERIFIED','source_scientific_commit':SOURCE,'source_scientific_tree':git(F,'rev-parse',SOURCE+'^{tree}'),'source_scientific_report_sha256':pub['report_sha256'],'txid':tx,'true164_root':manifest['persistent164_root'],'target_mount_path':str(bundle),'native_restore':str(destination),'source_payload_root':str(ROOT),'archive_bytes':index['archive_bytes'],'archive_sha256':index['archive_sha256'],'manifest_sha256':m.sha(m.canon(manifest)),'original_payload_bytes':raw,'regular_files':sum(r['type']=='file' for r in entries),'directories':sum(r['type']=='directory' for r in entries),'restored_entries':len(proof),'source_disposition':'SOURCE_KEEP','source_release_bytes':0,'new_model_starts':0,'science_registry_and_epoch_unchanged':True,'starts_consumed_before_after':12,'remaining_budget_before_after':0,'data_export_source_sha256':sha(pathlib.Path(__file__)),'resource_admission':admission,'resources_before_archive':before,'resources_after_restore':m.gate(),'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
v.exclusive_json(bundle/'RECEIPT.json',receipt);v.exclusive_json(T/'analysis/FINAL_REVIEW_ARCHIVE_RECEIPT.json',receipt)
print(json.dumps(receipt,indent=2))
