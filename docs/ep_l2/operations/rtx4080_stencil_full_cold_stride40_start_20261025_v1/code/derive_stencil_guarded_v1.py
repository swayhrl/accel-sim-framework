"""Prepare-only exact stride40. Needs Root grant and completed cold proof."""
import pathlib,json,hashlib,os,sys,time,resource,importlib.util,fcntl,marshal
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent;R=pathlib.Path(__file__).parent
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');I='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';PREFIX=I+'_TRIM_GUARDED_V1_'
PARENT_COMMIT='7d352239592c6cf91713b30b0654b7051573a68182592ed3db5e4ac25bb61d26';PARENT_MANIFEST='95c3cbe67fb077ee98fc1a617d829cc9228a8557fc930ff2303f0047b11d2e79'
ALGORITHM='0f2a6d35e5f2547aa284a075a02fae1b981483d9b10614f6275697368ef513a4';PARSER='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 q=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
def save(p,x):
 assert not p.exists();tmp=p.with_name(p.name+'.tmp')
 with tmp.open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def require_cold(g):
 assert g['root_confirmed_cold_outer_exit_code']==0
 expected={'cold_pass':'ALL_MANIFEST_MEMBERS_BOUNDED_NATIVE_COLD_RESTORE_PASS','cold_complete':'OBSERVED_WORKER_EXIT0_ALL_MANIFEST_COLD_COMPLETE','cold_terminal':'PASS'};data={}
 for key,status in expected.items():
  r=g[key];p=pathlib.Path(r['path']);assert p.parent==C and sha(p)==r['sha256'];data[key]=json.loads(p.read_text());assert data[key]['status']==status
 assert not(C/(I+'_COLD_V2_FAILURE.json')).exists()
 cp=data['cold_pass'];cc=data['cold_complete'];assert cp['asset_id']==I and cp['COMMIT_sha256_before_and_after']==PARENT_COMMIT and cp['MANIFEST_sha256_before_and_after']==PARENT_MANIFEST
 assert cp['manifest_payload_files']==502 and cp['manifest_payload_bytes']==14748350881 and cp['including_manifest_and_commit_files']==504
 assert cc['worker_returncode']==0 and cc['output_sha256']==g['cold_pass']['sha256']and data['cold_terminal']['worker_rc']==0
 release=g['root_cold_release_receipt'];assert pathlib.Path(release['path']).parent==C and sha(pathlib.Path(release['path']))==release['sha256']
 return data

def main():
 g=json.loads(pathlib.Path(sys.argv[1]).read_text());assert g['status']=='APPROVED_EXACT_STENCIL_CTA_STRIDE40_DERIVE_ONLY_V1'
 assert g['asset_id']==I and g['adapter_sha256']==sha(pathlib.Path(__file__))
 for row in g['dependencies']:
  p=pathlib.Path(row['path']);assert len(p.read_bytes())==row['bytes']and sha(p)==row['sha256']
 cold=require_cold(g)
 assert sha(C/'derive_complete_cta_v2.py')==ALGORITHM
 assert sha(C/'resource_library_copy_v10_pinned.py')=='7e5b290e330cbc1fcc845b6a9c7ce3487d181677d117a8d77a31c60d12a42521'
 assert sha(C/'read_native_foreign_reserve_v1.py')=='441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba'
 assert sha(C/'post_app_parallel_v5.py')=='c6fdc374344f4bb1d9cdec8f396807a9aef8d9b1fcf4741fc8477b18b86a0c2a'
 assert sha(R/'trim_guard_io_v1.py')==g['io_adapter_sha256']
 work=pathlib.Path(g['work']);assert work==N/(I+'_guarded_trim_v1')and not work.exists();assert pathlib.Path(g['candidate'])==work/'FINAL_CANDIDATE.json'
 assert work.parent.stat().st_dev==2128 and C.stat().st_dev==2128
 policy=load('r10',C/'resource_library_copy_v10_pinned.py');normal=policy.Resources();auth=load('auth',C/'read_native_foreign_reserve_v1.py');scan=load('scan',C/'post_app_parallel_v5.py');ioadapter=load('trim_io',R/'trim_guard_io_v1.py')
 resource.setrlimit(resource.RLIMIT_FSIZE,(128*2**20,128*2**20));resource.setrlimit(resource.RLIMIT_AS,(1536*2**20,1536*2**20))
 start=time.monotonic();last=quick=0;cache=None;cap=256*2**20
 def usage():
  total=scan.tree_size_race_safe(work)if work.exists()else 0
  for p in C.glob(PREFIX+'*'):
   try:total+=p.stat().st_size
   except OSError as e:
    if e.errno!=2:raise
  return total
 def guard(force=False,admission=False):
  nonlocal last,quick,cache
  now=time.monotonic()
  if not force and now-quick<.5:return
  assert now-start<21600
  if cache is None or now-last>=10:
   end=now+10
   while True:
    n=normal(True);a=auth.snapshot()
    if n['registered_foreign_write_reservations_bytes']==a['sum_all_records_reserved_write_bytes']:break
    assert time.monotonic()<end
   cache={'normal':n,'authority':a};last=time.monotonic()
  used=usage();assert used<=cap
  floor=5*2**30+cache['authority']['sum_all_records_reserved_write_bytes']+2**30+64*2**20
  import shutil
  assert shutil.disk_usage(N).free>=floor+max(0,cap-used)+(128*2**20 if admission else 0)
  quick=time.monotonic()
 guard(True,True);work.mkdir()
 lock=(N/(I+'_validation_hot_epoch2/AGGREGATE_NAS_READ.lock')).open('a')
 try:
  bound=ioadapter.BoundIO(B/'objects'/I,work,guard,lambda n:policy.adaptive_io_pace(n,15*2**20),lock);parent=bound.parent_path()
  assert bound.digest(parent/'COMMIT.json')==PARENT_COMMIT and bound.digest(parent/'MANIFEST.json')==PARENT_MANIFEST
  d=load('frozen_derive',C/'derive_complete_cta_v2.py');original_functions={n:getattr(d,n)for n in ['derive','blocks','consume','check_warps','verify_derived']};code_pins={n:hashlib.sha256(marshal.dumps(f.__code__)).hexdigest()for n,f in original_functions.items()}
  parser_cache=work/'frozen_parser.py';bound.copyfile(parent/'contract/validate_v7.py',parser_cache);assert bound.digest(parser_cache)==PARSER
  bound.install(d,parser_cache);dest=work/'derived';d.derive(parent,dest,40)
  for n,f in original_functions.items():assert hashlib.sha256(marshal.dumps(f.__code__)).hexdigest()==code_pins[n]
  asset=json.loads((dest/'ASSET.json').read_text());validation=json.loads((dest/'DERIVED_VALIDATION.json').read_text());assert len(asset['kernels'])==100 and validation['selected_ctas']==2600 and validation['all_selected_warps_complete']
  assert all(k['original_grid']==[8,128,1]and k['block']==[32,4,1]and k['selected_ctas']==26 for k in asset['kernels'])
  assert asset['parent_commit_sha256']==PARENT_COMMIT and asset['parent_manifest_sha256']==PARENT_MANIFEST and asset['sampling']['stride']==40
  assert bound.digest(parent/'COMMIT.json')==PARENT_COMMIT and bound.digest(parent/'MANIFEST.json')==PARENT_MANIFEST
  for p in [pathlib.Path(__file__),R/'trim_guard_io_v1.py']:bound.copyfile(p,dest/'tools'/p.name)
  provenance={'kind':'GUARDED_IO_ADAPTER_ONLY_NOT_NEW_SELECTION_ALGORITHM','algorithm_sha256':ALGORITHM,'adapter_sha256':g['adapter_sha256'],'io_adapter_sha256':g['io_adapter_sha256'],'original_function_code_before_after_equal':code_pins,'IO':bound.receipt(),'parent_cold_proof_bindings':{k:g[k]for k in ['cold_pass','cold_complete','cold_terminal','root_cold_release_receipt']},'source_KEEP':True,'no_GPU_SIM_109_or_full_record_validator_runs':True,'not_published':True}
  save(dest/'GUARDED_ADAPTER_EXECUTION.json',provenance)
  files=[{'path':str(p.relative_to(dest)),'bytes':p.stat().st_size,'sha256':bound.digest(p)}for p in sorted(dest.rglob('*'))if p.is_file()]
  guard(True);save(work/'FINAL_CANDIDATE.json',{'status':'GUARDED_DERIVE_PREPARED_NOT_PUBLISHED','asset_id':asset['asset_id'],'parent_asset_id':I,'parent_COMMIT_sha256':PARENT_COMMIT,'parent_MANIFEST_sha256':PARENT_MANIFEST,'selected_ctas':2600,'selected_records':validation['selected_records'],'derived_validation_sha256':bound.digest(dest/'DERIVED_VALIDATION.json'),'prepared_root':str(dest),'prepared_members':files,'adapter_sha256':g['adapter_sha256'],'io_adapter_sha256':g['io_adapter_sha256'],'no_consumer_timing_or_historical_crop_qualification':True});guard(True)
 finally:lock.close()
if __name__=='__main__':main()
