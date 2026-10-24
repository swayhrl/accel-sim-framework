import pathlib,json,hashlib,os,time,fcntl,shutil,sys
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control';N=R/'nas_rtx4080'
ident=sys.argv[1]
assert ident in ['C8_SDK42_VECTOR_SIZE4000000_A001','C8_SDK42_VECTOR_SIZE6000000_A001']
source=R/'local_staging/inflight'/ident;dest=N/'inflight'/ident
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def copy(s,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 with s.open('rb')as f,d.open('xb')as out:
  for b in iter(lambda:f.read(2**20),b''):
   start=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-start)))
  out.flush();os.fsync(out.fileno())
 assert sha(s)==sha(d)
locks=[]
try:
 for name in ['RTX4080_LOCAL_IO.lock','RTX4080_LOCAL_STAGING.lock']:
  f=open(C/name,'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 approval=C/'PARENT_C8_TWO_VECTOR_BATCH_APPROVAL_V1.json';assert sha(approval)=='90d71b258cd2a81f31f59b4c7bd680984951aa7a691d8d80322dfa3976adbd0d'
 closed=C/(ident+'_LOCAL_CLOSED.json');q=json.loads(closed.read_text());assert q['id']==ident and q['status']=='LOCAL_CLOSED_NOT_ARCHIVED_NOT_FORMAL'and q['all_files_fsync_reopen_fullSHA']
 sender=source/'SENDER_MANIFEST.json';assert sha(sender)==q['sender']['sender_manifest_sha256']
 m=json.loads(sender.read_text());assert m['asset']['asset_id']==ident
 expected={x['path']for x in m['files']}|{'SENDER_MANIFEST.json'};actual={str(p.relative_to(source))for p in source.rglob('*')if p.is_file()or p.is_symlink()};assert actual==expected
 before={}
 for x in m['files']:
  rel=pathlib.PurePosixPath(x['path']);assert not rel.is_absolute()and '..'not in rel.parts
  p=source/rel;st=p.stat();assert not p.is_symlink()and st.st_size==x['bytes']and sha(p)==x['sha256'];before[x['path']]=(st.st_ino,st.st_size,st.st_mtime_ns)
 assert not dest.exists();assert shutil.disk_usage(N).free>20*2**30;dest.mkdir()
 for x in m['files']:copy(source/x['path'],dest/x['path'])
 for name in [closed.name,ident+'_SUPERVISOR_START.json','C8_TWO_VECTOR_BATCH_LOCAL_RESULTS_V1.json','C8_TWO_VECTOR_BATCH_SUPERVISOR_IDENTITY.json',approval.name,'C8_NEXT_TWO_VECTOR_REVIEW_PACKAGE_V2.json','supervise_c8_two_vectors_v2.py','LOCAL_STAGING_CHANNEL_QUALIFICATION_V1.json','LOCAL_STAGING_PHASE_POLICY_V2.json']:
  copy(C/name,dest/'qualification/local_staging'/name)
 copy(pathlib.Path(__file__),dest/'qualification/local_staging'/pathlib.Path(__file__).name)
 for x in m['files']:
  p=source/x['path'];st=p.stat();assert(st.st_ino,st.st_size,st.st_mtime_ns)==before[x['path']]and sha(p)==x['sha256']
 files=[{'path':str(p.relative_to(dest)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(dest.rglob('*'))if p.is_file()]
 out={'asset':m['asset'],'files':files,'source_local_sender_sha256':sha(sender),'source_local_closed_receipt_sha256':sha(closed),'parent_approval_sha256':sha(approval),'source_KEEP':True,'source_released_bytes':0}
 with(dest/'SENDER_MANIFEST.json').open('x')as f:json.dump(out,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'status':'SENDER_COMPLETE','inflight':str(dest.relative_to(N)),'asset_id':ident,'sender_manifest_sha256':sha(dest/'SENDER_MANIFEST.json'),'payload_files':len(files),'payload_bytes':sum(x['bytes']for x in files)}))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
