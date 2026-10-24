import pathlib,json,hashlib,os,time,fcntl,shutil
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control';N=R/'nas_rtx4080';ID='C8_CUDA118_SIMPLEVOTE_DEFAULT_A001';source=R/'local_staging/inflight'/ID;dest=N/'inflight'/ID
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(s,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 with s.open('rb')as inp,d.open('xb')as out:
  for b in iter(lambda:inp.read(2**20),b''):
   start=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-start)))
  out.flush();os.fsync(out.fileno())
 assert sha(s)==sha(d)
locks=[]
try:
 for n in ['RTX4080_LOCAL_IO.lock','RTX4080_LOCAL_STAGING.lock']:
  f=open(C/n,'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 grant=C/'PARENT_C8_VOTE_SINGLE_JOB_APPROVAL_V1.json';assert sha(grant)=='d10e4c8688ce0ca1b9cd48a53f578649561375b7fd2f4989ba7e4265b24c185f'
 closed=C/(ID+'_LOCAL_CLOSED.json');q=json.loads(closed.read_text());assert q['status']=='LOCAL_CLOSED_NOT_ARCHIVED_NOT_FORMAL'and q['all_files_fsync_reopen_fullSHA']
 sender=source/'SENDER_MANIFEST.json';assert sha(sender)==q['sender']['sender_manifest_sha256'];m=json.loads(sender.read_text());assert m['asset']['asset_id']==ID and m['asset']['worker_sha256']=='f30fa26022d424aa75c61cbfa7398999376ad4e953b3f2a2ee8cd3d920c4106d'
 assert m['asset']['full_application']['kernel_launches']==3 and m['asset']['full_application']['records']==153
 assert {str(p.relative_to(source))for p in source.rglob('*')if p.is_file()or p.is_symlink()}=={x['path']for x in m['files']}|{'SENDER_MANIFEST.json'}
 before={}
 for x in m['files']:
  rel=pathlib.PurePosixPath(x['path']);assert not rel.is_absolute()and '..'not in rel.parts
  p=source/rel;st=p.stat();assert not p.is_symlink()and st.st_size==x['bytes']and sha(p)==x['sha256'];before[x['path']]=(st.st_size,st.st_mtime_ns)
 assert not dest.exists()and shutil.disk_usage(N).free>20*2**30;dest.mkdir()
 for x in m['files']:copy(source/x['path'],dest/x['path'])
 for n in[closed.name,ID+'_SUPERVISOR_START.json','C8_VOTE_APPROVED_V5_LAUNCH.json','C8_VOTE_SINGLE_REVIEW_PACKAGE_V5.json','C8_VOTE_SINGLE_LOCAL_RESULTS_V1.json','supervise_c8_vote_single_v5.py',grant.name]:copy(C/n,dest/'qualification/local_staging'/n)
 copy(pathlib.Path(__file__),dest/'qualification/local_staging'/pathlib.Path(__file__).name)
 for x in m['files']:
  p=source/x['path'];st=p.stat();assert(st.st_size,st.st_mtime_ns)==before[x['path']]and sha(p)==x['sha256']
 files=[{'path':str(p.relative_to(dest)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(dest.rglob('*'))if p.is_file()]
 out={'asset':m['asset'],'files':files,'source_local_sender_sha256':sha(sender),'source_local_closed_receipt_sha256':sha(closed),'source_KEEP':True,'new_source_coverage_pending_independent_Native_coldread':True}
 with(dest/'SENDER_MANIFEST.json').open('x')as f:json.dump(out,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'status':'SENDER_COMPLETE','asset_id':ID,'inflight':str(dest.relative_to(N)),'sender_manifest_sha256':sha(dest/'SENDER_MANIFEST.json')}))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
