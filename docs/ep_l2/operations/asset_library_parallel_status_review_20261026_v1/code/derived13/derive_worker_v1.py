#!/usr/bin/env python3
"""Bounded prepare-only wrapper. Exact qualified generator/IO adapter remain unchanged."""
import pathlib,json,hashlib,importlib.util,os,sys,time,resource,fcntl,marshal
R=pathlib.Path(__file__).resolve().parent; B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ALG='0f2a6d35e5f2547aa284a075a02fae1b981483d9b10614f6275697368ef513a4'
IO='19a5274933da2ec0c83852ac7d87bddcff3b3fdd70d47d0d51769266fe93116e'
PARSER='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(p,x):
 temp=p.with_name(p.name+'.closed_writing')
 with temp.open('x') as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 module=load('metadata_noreplace',R/'v9_noreplace_frozen.py');module.rename_noreplace(temp,p)
def main():
 g=json.loads(pathlib.Path(sys.argv[1]).read_text());idx=int(sys.argv[2]);assert g['status']=='APPROVED_FINITE_DERIVED_CATCHUP_PREPARE_V1'
 for x in g['code']:
  p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 scopep=R/'SCOPE.json';assert sha(scopep)==g['scope_sha256'];s=json.loads(scopep.read_text());row=s['rows'][idx]
 parent=B/'objects'/row['parent_asset_id'];assert sha(parent/'COMMIT.json')==row['parent_commit_sha256'];assert sha(parent/'MANIFEST.json')==row['parent_manifest_sha256']
 assert not(B/'objects'/row['derived_asset_id']).exists()
 run=pathlib.Path(g['run_root']);assert R in run.parents and '/root/share/mnt164/' in str(run)
 work=run/'work'/row['parent_asset_id'];work.mkdir(parents=True,exist_ok=False)
 resource.setrlimit(resource.RLIMIT_AS,(1536*2**20,1536*2**20))
 resource.setrlimit(resource.RLIMIT_FSIZE,(2*2**30,2*2**30))
 os.nice(15);start=time.monotonic();last=0
 def guard():
  nonlocal last
  now=time.monotonic()
  if now-last<.5:return
  assert now-start<6*3600,'job deadline'
  v=os.statvfs(run);assert v.f_bavail*v.f_frsize>=5*2**30,'NAS free floor'
  v=os.statvfs('/root/data');assert v.f_bavail*v.f_frsize>=5*2**30,'Native free floor'
  if now-last>=.5:
   total=sum(p.stat().st_size for p in work.rglob('*') if p.is_file());assert total<=2*2**30,'derived output cap'
  last=now
 d=load('frozen_derive',R/'derive_complete_cta_v2.py');a=load('frozen_boundio',R/'trim_guard_io_v1.py')
 assert sha(R/'derive_complete_cta_v2.py')==ALG and sha(R/'trim_guard_io_v1.py')==IO
 codepins={n:hashlib.sha256(marshal.dumps(getattr(d,n).__code__)).hexdigest() for n in ['derive','blocks','consume','check_warps','verify_derived']}
 lock=(R/'AGGREGATE_DERIVED_NAS_READ.lock').open('a')
 try:
  bound=a.BoundIO(parent,work,guard,lambda n:time.sleep(n/(10*2**20)),lock)
  parser=work/'frozen_parser.py';bound.copyfile(parent/'contract/validate_v7.py',parser);assert sha(parser)==PARSER
  bound.install(d,parser);dest=work/'derived';d.derive(bound.parent_path(),dest,40)
  proof=json.loads((dest/'DERIVED_VALIDATION.json').read_text());asset=json.loads((dest/'ASSET.json').read_text())
  assert proof['status']=='COMPLETE_CTA_PARENT_MEMBER_EQUALITY_PASS' and asset['asset_id']==row['derived_asset_id']
  assert asset['parent_commit_sha256']==row['parent_commit_sha256'] and asset['parent_manifest_sha256']==row['parent_manifest_sha256'] and asset['generator_sha256']==ALG
  assert sha(parent/'COMMIT.json')==row['parent_commit_sha256'] and sha(parent/'MANIFEST.json')==row['parent_manifest_sha256']
  files=[{'path':str(p.relative_to(dest)),'bytes':p.stat().st_size,'sha256':bound.digest(p)} for p in sorted(dest.rglob('*')) if p.is_file()]
  save(work/'PREPARED.json',{'status':'PREPARED_VALIDATED_NOT_PUBLISHED','scope_row':row,'prepared_root':str(dest),'generator_sha256':ALG,'IO_adapter_sha256':IO,'IO':bound.receipt(),'original_function_code_pins':codepins,'files':files,'source_KEEP':True,'release_bytes':0,'scientific_qualification_granted':False})
 finally:lock.close()
if __name__=='__main__':main()
