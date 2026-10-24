#!/usr/bin/env python3
import pathlib,json,hashlib,os,time,fcntl,signal,sys
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');source=pathlib.Path(sys.argv[1]).resolve();assert C.parent/'derived_prepared_v1' in source.parents
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   start=time.monotonic();h.update(b);time.sleep(max(0,len(b)/(15*1048576)-(time.monotonic()-start)))
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
   start=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*1048576)-(time.monotonic()-start)))
  out.flush();os.fsync(out.fileno())
 assert sha(s)==sha(d)
asset=json.loads((source/'ASSET.json').read_text());ident=asset['asset_id'];assert asset['kind']=='DERIVED_COMPLETE_CTA_TRACE';assert asset['generator_sha256']=='0f2a6d35e5f2547aa284a075a02fae1b981483d9b10614f6275697368ef513a4'
validation=json.loads((source/'DERIVED_VALIDATION.json').read_text());assert validation['status']=='COMPLETE_CTA_PARENT_MEMBER_EQUALITY_PASS' and validation['all_selected_warps_complete'];locks=[]
try:
 signal.signal(signal.SIGALRM,lambda a,b:(_ for _ in ()).throw(TimeoutError('derived lease wait7200s')));signal.alarm(7200)
 for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
  f=open(C/name,'a');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX)
 signal.alarm(0)
 parent=B/'objects'/asset['parent_asset_id'];pcommit=json.loads((parent/'COMMIT.json').read_text());assert sha(parent/'COMMIT.json')==asset['parent_commit_sha256'] and sha(parent/'MANIFEST.json')==pcommit['manifest_sha256']==asset['parent_manifest_sha256']
 dest=B/'objects'/ident;assert not dest.exists();root=B/'inflight'/ident;root.mkdir(exist_ok=False)
 for p in sorted(source.rglob('*')):
  if p.is_file():assert not p.is_symlink();copy(p,root/p.relative_to(source))
 copy(C/'DERIVED_CTA_V2_QUALIFICATION.json',root/'qualification/DERIVED_CTA_V2_QUALIFICATION.json')
 files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
 save(root/'MANIFEST.json',{'asset_id':ident,'kind':'DERIVED_COMPLETE_CTA_TRACE','files':files,'logical_bytes':sum(x['bytes'] for x in files),'parent_manifest_sha256':asset['parent_manifest_sha256']})
 commit={'schema':'RTX4080_DERIVED_CTA_COMMIT_V1','kind':'DERIVED_COMPLETE_CTA_TRACE','status':'COMMITTED_VERIFIED','asset_id':ident,'manifest_sha256':sha(root/'MANIFEST.json'),'logical_bytes':sum(x['bytes'] for x in files),'parent_asset_id':asset['parent_asset_id'],'parent_manifest_sha256':asset['parent_manifest_sha256'],'policy':'COMPLETE_CTA_LINEAR_STRIDE_40_V1','ctas_retained':validation['selected_ctas'],'records_retained':validation['selected_records'],'consumer_qualification':'NOT_GRANTED','source_KEEP':True,'release_bytes':0,'utc_unix':time.time()};save(root/'COMMIT.json',commit);root.rename(dest)
 assert sha(dest/'MANIFEST.json')==commit['manifest_sha256']
 for x in files:assert sha(dest/x['path'])==x['sha256']
 save(B/'receipts'/(ident+'_NATIVE174_READBACK.json'),commit)
 cat=B/'catalog/DERIVED_ASSETS.json';old=sha(cat) if cat.exists() else None;o=json.loads(cat.read_text()) if cat.exists() else {'schema':'RTX4080_DERIVED_TRACE_CATALOG_V1','objects':[]};assert all(x['asset_id']!=ident for x in o['objects']);o['objects'].append(commit)
 assert (sha(cat) if cat.exists() else None)==old,'catalog CAS conflict';replace(cat,o);digest=sha(cat);version=B/'catalog/versions'/('derived_'+digest+'.json')
 if not version.exists():copy(cat,version)
 assert sha(version)==digest
 replace(B/'catalog/CURRENT_RTX4080_DERIVED_CATALOG.json',{'schema':'RTX4080_DERIVED_CATALOG_POINTER_V1','sha256':digest,'relative_path':'versions/'+version.name,'previous_catalog_sha256':old,'utc_unix':time.time()})
 save(C/(ident+'_PUBLISH_RECEIPT.json'),commit);print(json.dumps(commit))
finally:
 signal.alarm(0)
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
