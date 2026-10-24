#!/usr/bin/env python3
import pathlib,os,fcntl,subprocess,json,hashlib,shutil,time
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';S=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1');P=pathlib.Path('/data/c16/rtx4080_asset_pilot_20261024_v1')
root=N/'inflight/ordinary_vector4m_ada7_final55_import_v1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def copy(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 with src.open('rb') as inp,dest.open('xb') as out:
  for b in iter(lambda:inp.read(1048576),b''):out.write(b)
  out.flush();os.fsync(out.fileno())
 assert sha(src)==sha(dest)
lock=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
root.mkdir(exist_ok=False)
origin=S/'attempts/vector4m_v7_final_attempt1'
execution=json.loads((origin/'EXECUTION.json').read_text());assert execution['exit_code']==0 and execution['binary_sha256']=='1819fe6c9720b417e34a122e9b013bf1b09835850e23606d901fdf1ca8b2227f'
assert execution['tool_sha256']=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
for p in sorted(origin.rglob('*')):
 if not p.is_file() or p.name.endswith('.traceg.xz') or p.name=='POSTPROCESS_V7.json':continue
 copy(p,root/p.relative_to(origin))
for group,src in [('source',P/'source'),('map',S/'vector-map-v2'),('contract',S/'frozen/ada7_contract_v1')]:
 for p in sorted(src.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:copy(p,root/group/p.relative_to(src))
copy(P/'bin/vectorAdd',root/'bin/vectorAdd')
copy(S/'frozen/producer_v7_55c6f482/producer.so',root/'tools/producer.so')
for name in ['postprocess_nas_sharded_v1.py','ssh_rate_bridge.py']:
 copy(R/'control'/name,root/'tools'/name)
validation=json.loads((root/'FULL_RECORD_VALIDATION.json').read_text())
assert validation['source_files'][str(origin/'traces/kernel-1-ctx_0x6400dd7235b0.trace.xz')]==sha(root/'traces/kernel-1-ctx_0x6400dd7235b0.trace.xz')
(root/'FULL_RECORD_VALIDATION.json').rename(root/'SOURCE_FULL_RECORD_VALIDATION.json')
validator=root/'contract/validate_v7.py'
vp=subprocess.run(['python3',str(validator),str(root),str(root/'map/manifest.json')],capture_output=True,text=True,timeout=600)
(root/'VALIDATOR_NAS_RECHECK.log').write_text(vp.stdout+vp.stderr)
assert vp.returncode==0,vp.stderr
ptx_listing=subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-lptx',str(root/'bin/vectorAdd')],text=True)
(root/'BINARY_PTX_LISTING.txt').write_text(ptx_listing)
post=R/'control/postprocess_nas_sharded_v1.py';receipts=[]
for raw in sorted((root/'traces').glob('*.trace.xz')):
 dest=raw.with_name(raw.name.replace('.trace.xz','.traceg.xz'));work=root/'postprocess_work'/raw.stem
 cmd=['python3',str(post),str(raw),str(dest),str(work)]
 cp=subprocess.run(cmd,capture_output=True,text=True,timeout=1800)
 (root/('POSTPROCESS_'+raw.name+'.log')).write_text(cp.stdout+cp.stderr)
 assert cp.returncode==0,cp.stderr
 rec=json.loads(cp.stdout);assert rec['records']==2125000 and rec['ctas']==15625 and rec['warps']==125000
 receipts.append(rec)
 # Full original/reference grouped stream equality independent of compression/member boundaries.
 original=origin/'traces'/dest.name
 a=subprocess.Popen(['xz','-dc',str(dest)],stdout=subprocess.PIPE)
 b=subprocess.Popen(['xz','-dc',str(original)],stdout=subprocess.PIPE)
 h=hashlib.sha256();size=0
 while True:
  x=a.stdout.read(1048576);y=b.stdout.read(1048576);assert x==y
  if not x:break
  h.update(x);size+=len(x)
 assert a.wait()==0 and b.wait()==0
 rec['reference_plain_sha256']=h.hexdigest();rec['reference_plain_bytes']=size;rec['reference_byte_equal']=True
 receipts[-1]=rec
 cleanup={'derived_only':True,'path':str(work),'source_raw_keep':str(raw),'grouped_sha256':sha(dest),'full_crc_and_reference_equal_before_cleanup':True}
 (root/'POSTPROCESS_DERIVED_CLEANUP.json').write_text(json.dumps(cleanup,indent=2)+'\n')
 assert root.resolve() in work.resolve().parents and 'postprocess_work' in work.parts
 shutil.rmtree(work)
(root/'POSTPROCESS_NAS.json').write_text(json.dumps(receipts,indent=2)+'\n')
asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':'CUDA_SAMPLES_DB3EEA_VECTORADD_4M_ADA7_55C6_V1','suite':'CUDA Samples','source_version':'db3eea23946bca2e90a75eca2b5b3e07158a9e11','program':'vectorAdd','input':{'elements':4000000,'seed':1,'threads_per_block':256},'capture_gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','actual_cubin_arch':89,'embedded_PTX':{'listing':ptx_listing,'loaded_code':'SM89 cubin validated to exact function/PC map; no JIT substitute'},'producer_sha256':execution['tool_sha256'],'contract_sha256':sha(root/'contract/CONTRACT.json'),'binary_sha256':execution['binary_sha256'],'map_manifest_sha256':sha(root/'map/manifest.json'),'validator_sha256':sha(validator),'semantic_map_maker_sha256':sha(root/'contract/make_semantic_map.py'),'full_validation_rechecked_on_NAS_copy':True,'postprocessor_sha256':sha(post),'pump_sha256':sha(R/'control/ssh_rate_bridge.py'),'original_capture':{'path':str(origin),'execution':execution,'reuse_existing_capture':True,'additional_gpu_processes':0},'full_application':{'kernel_launches':1,'ctas':15625,'warps':125000,'records':2125000,'active_lane_instruction_instances':64000000,'all_warps_terminate':True,'sampling':'NONE','context_count':1,'h2d_copies':2,'h2d_bytes':32000000,'commandlist':'traces/kernelslist.g','stream_ids':[0]},'numerical_status':'PASS_MAX_ABS_ERROR_0','output_digest_fnv64':'0a8162dae8a16ac5','producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_AUTOMATICALLY_GRANTED; per profile independent qualification required','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0}
assert asset['contract_sha256']=='97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184'
assert 'max_abs_error=0' in (root/'native.stdout').read_text()
(root/'ASSET.json').write_text(json.dumps(asset,indent=2)+'\n')
manifest=[]
for p in sorted(root.rglob('*')):
 if p.is_file():manifest.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)})
(root/'SENDER_MANIFEST.json').write_text(json.dumps({'asset':asset,'files':manifest},indent=2)+'\n')
print(json.dumps({'status':'SENDER_COMPLETE','inflight':str(root.relative_to(N)),'asset_id':asset['asset_id'],'sender_manifest_sha256':sha(root/'SENDER_MANIFEST.json'),'payload_files':len(manifest),'payload_bytes':sum(x['bytes'] for x in manifest)}))
fcntl.flock(lock,fcntl.LOCK_UN)

