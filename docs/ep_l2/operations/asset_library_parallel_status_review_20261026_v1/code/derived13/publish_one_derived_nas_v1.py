#!/usr/bin/env python3
import pathlib,json,hashlib,os,time,fcntl,signal,sys,ctypes,importlib.util
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');R=pathlib.Path(__file__).resolve().parent;grant=pathlib.Path(sys.argv[1]);g=json.loads(grant.read_text());assert g['status']=='APPROVED_FINITE_DERIVED_CATCHUP_PUBLISH_V1';source=pathlib.Path(sys.argv[2]).resolve();
for x in g['code']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
run=pathlib.Path(g['run_root']);assert run in source.parents and source.name=='derived';scope=json.loads((R/'SCOPE.json').read_text());assert hashlib.sha256((R/'SCOPE.json').read_bytes()).hexdigest()==g['scope_sha256'];allowed={x['derived_asset_id']:x for x in scope['rows']};lockpath=R/'AGGREGATE_DERIVED_NAS_READ.lock';iolease=lockpath.open('a');receipt=run/'publish_receipts';receipt.mkdir(exist_ok=True)
def pace(n):
 fcntl.flock(iolease,fcntl.LOCK_EX)
 try:time.sleep(n/(10*1048576))
 finally:fcntl.flock(iolease,fcntl.LOCK_UN)
spec=importlib.util.spec_from_file_location('qualified_v9_noreplace',R/'v9_noreplace_frozen.py');v9=importlib.util.module_from_spec(spec);spec.loader.exec_module(v9)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   start=time.monotonic();h.update(b);pace(len(b))
 return h.hexdigest()
def save(p,o):
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def replace(p,o):
 tmp=p.with_name(p.name+'.tmp')
 with tmp.open('w') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def copy(s,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 with s.open('rb') as inp,d.open('xb') as out:
  for b in iter(lambda:inp.read(1048576),b''):
   start=time.monotonic();out.write(b);pace(len(b))
  out.flush();os.fsync(out.fileno())
 assert sha(s)==sha(d)
import resource
resource.setrlimit(resource.RLIMIT_AS,(1536*2**20,1536*2**20));signal.signal(signal.SIGALRM,lambda a,b:(_ for _ in ()).throw(TimeoutError('publisher deadline')));signal.alarm(21600)
spec=importlib.util.spec_from_file_location('prepared_closure',R/'prepared_closure_v1.py');closure=importlib.util.module_from_spec(spec);spec.loader.exec_module(closure)
asset=json.loads((source/'ASSET.json').read_text());ident=asset['asset_id'];assert ident in allowed and asset['parent_commit_sha256']==allowed[ident]['parent_commit_sha256'] and asset['parent_manifest_sha256']==allowed[ident]['parent_manifest_sha256'];assert asset['kind']=='DERIVED_COMPLETE_CTA_TRACE';assert asset['generator_sha256']=='0f2a6d35e5f2547aa284a075a02fae1b981483d9b10614f6275697368ef513a4'
prepared=closure.check(source,allowed[ident],sha)
validation=json.loads((source/'DERIVED_VALIDATION.json').read_text());assert validation['status']=='COMPLETE_CTA_PARENT_MEMBER_EQUALITY_PASS' and validation['all_selected_warps_complete'];locks=[]
try:
 signal.signal(signal.SIGALRM,lambda a,b:(_ for _ in ()).throw(TimeoutError('derived lease wait7200s')));signal.alarm(7200)
 for name in ['RTX4080_DERIVED_CATALOG.lock']:
  f=open(B/'catalog'/name,'a');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX)
 signal.alarm(21600)
 parent=B/'objects'/asset['parent_asset_id'];pcommit=json.loads((parent/'COMMIT.json').read_text());assert sha(parent/'COMMIT.json')==asset['parent_commit_sha256'] and sha(parent/'MANIFEST.json')==pcommit['manifest_sha256']==asset['parent_manifest_sha256']
 dest=B/'objects'/ident;dest.mkdir(exist_ok=False);root=dest
 for x in prepared['files']:
  p=source/x['path'];assert p.is_file() and not p.is_symlink();copy(p,root/x['path']);assert (root/x['path']).stat().st_size==x['bytes'] and sha(root/x['path'])==x['sha256']
 closure.check(source,allowed[ident],sha)
 copy(source.parent/'PREPARED.json',root/'qualification/PREPARED_CLOSURE.json')
 copy(R/'DERIVED_CTA_V2_QUALIFICATION.json',root/'qualification/DERIVED_CTA_V2_QUALIFICATION.json')
 files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
 save(root/'MANIFEST.json',{'asset_id':ident,'kind':'DERIVED_COMPLETE_CTA_TRACE','files':files,'logical_bytes':sum(x['bytes'] for x in files),'parent_manifest_sha256':asset['parent_manifest_sha256']})
 commit={'schema':'RTX4080_DERIVED_CTA_COMMIT_V1','kind':'DERIVED_COMPLETE_CTA_TRACE','status':'COMMITTED_VERIFIED','asset_id':ident,'manifest_sha256':sha(root/'MANIFEST.json'),'logical_bytes':sum(x['bytes'] for x in files),'parent_asset_id':asset['parent_asset_id'],'parent_manifest_sha256':asset['parent_manifest_sha256'],'policy':'COMPLETE_CTA_LINEAR_STRIDE_40_V1','ctas_retained':validation['selected_ctas'],'records_retained':validation['selected_records'],'consumer_qualification':'NOT_GRANTED','source_KEEP':True,'release_bytes':0,'utc_unix':time.time()};closed=receipt/(ident+'_COMMIT_CLOSED_WRITING.json');save(closed,commit);v9.rename_noreplace(closed,dest/'COMMIT.json')
 assert sha(dest/'MANIFEST.json')==commit['manifest_sha256']
 for x in files:assert sha(dest/x['path'])==x['sha256']
 save(B/'receipts'/(ident+'_NATIVE174_READBACK.json'),commit)
 cat=B/'catalog/DERIVED_ASSETS.json';old=sha(cat) if cat.exists() else None
 if cat.exists():copy(cat,receipt/(ident+'_DERIVED_CATALOG_PREIMAGE_'+old+'.json'))
 ptr=B/'catalog/CURRENT_RTX4080_DERIVED_CATALOG.json'
 if ptr.exists():copy(ptr,receipt/(ident+'_POINTER_PREIMAGE_'+sha(ptr)+'.json'))
 o=json.loads(cat.read_text()) if cat.exists() else {'schema':'RTX4080_DERIVED_TRACE_CATALOG_V1','objects':[]};assert all(x['asset_id']!=ident for x in o['objects']);o['objects'].append(commit)
 assert (sha(cat) if cat.exists() else None)==old,'catalog CAS conflict';replace(cat,o);digest=sha(cat);version=B/'catalog/versions'/('derived_'+digest+'.json')
 if not version.exists():copy(cat,version)
 assert sha(version)==digest
 replace(B/'catalog/CURRENT_RTX4080_DERIVED_CATALOG.json',{'schema':'RTX4080_DERIVED_CATALOG_POINTER_V1','sha256':digest,'relative_path':'versions/'+version.name,'previous_catalog_sha256':old,'utc_unix':time.time()})
 save(receipt/(ident+'_PUBLISH_RECEIPT.json'),commit);print(json.dumps(commit))
finally:
 signal.alarm(0)
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
