#!/usr/bin/env python3
"""Adopt an already completed GPU capture; independently verify closed bytes, resume CPU only."""
import pathlib,json,hashlib,os,subprocess,time,shutil,shlex,lzma,re,traceback
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
OLD='ORD_PolyBench_GPU_3MM_f1a41d8f9e59_A001';NEW='ORD_PolyBench_GPU_3MM_f1a41d8f9e59_A002_CPU_RESUME'
src=B/'inflight'/OLD;root=B/'inflight'/NEW
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   t=time.monotonic();h.update(b);time.sleep(max(0,1/15-(time.monotonic()-t)))
 return h.hexdigest()
def save(p,o):
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def copy(s,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 with s.open('rb') as inp,d.open('xb') as out:
  for b in iter(lambda:inp.read(1048576),b''):
   t=time.monotonic();out.write(b);time.sleep(max(0,1/15-(time.monotonic()-t)))
  out.flush();os.fsync(out.fileno())
 assert sha(s)==sha(d)
def remote_json(path):return json.loads(subprocess.check_output(['ssh','-n','-o','BatchMode=yes','gpu109','cat -- '+shlex.quote(path)]))
def remote_copy(path,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.Popen(['ssh','-n','-o','BatchMode=yes','gpu109','cat -- '+shlex.quote(path)],stdout=subprocess.PIPE)
 with d.open('xb') as out:
  for b in iter(lambda:p.stdout.read(1048576),b''):
   t=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*1048576)-(time.monotonic()-t)))
  out.flush();os.fsync(out.fileno())
 assert p.wait()==0
def link_closed(s,d,expected):
 assert sha(s)==expected
 d.parent.mkdir(parents=True,exist_ok=True)
 try:os.link(s,d);mode='NAS_HARDLINK_CLOSED_IMMUTABLE'
 except OSError:copy(s,d);mode='PACED_COPY'
 assert sha(d)==expected
 return {'source':str(s),'dest':str(d),'sha256':expected,'mode':mode,'bytes':d.stat().st_size}
try:
 assert not root.exists();root.mkdir()
 execution=json.loads((src/'EXECUTION.json').read_text());validation=json.loads((src/'FULL_RECORD_VALIDATION.json').read_text())
 assert execution['exit_code']==0 and not execution.get('bounded_stop')
 assert validation['status']=='ADA7_ORDINARY_FULL_RECORD_PASS' and validation['all_declared_warps_terminate']
 assert validation['validator_sha256']=='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
 assert validation['capture_map_binary_binding'] and validation['kernel_commandlist_exact_set']
 job=remote_json('/data/c16/rtx4080_suite_fill_20261024_v1/control/capture_jobs/'+OLD+'.json');task=job['task']
 assert execution['binary_sha256']==task['binary_sha256']
 proof={'schema':'CLOSED_CAPTURE_ADOPTION_V1','origin_attempt':OLD,'derived_attempt':NEW,'origin_capture_pid':execution['capture_pid'],'origin_capture_start_ticks':execution['capture_start_ticks'],'gpu_capture_repeated':False,'old_attempt_keep':True,'source_validation_sha256':sha(src/'FULL_RECORD_VALIDATION.json'),'source_execution_sha256':sha(src/'EXECUTION.json'),'raw_files':[],'negative_cases':[],'utc_unix':time.time(),'postprocess_host':'109 qualified V2 private SSHFS through Native174/true164; Native174 orchestrates and independently adopts/verifies all raw'}
 # Reject mismatched declared identity without creating a destination.
 firstpath,first=next(iter(validation['source_files'].items()));assert first!='0'*64
 negative_dest=root/'NEGATIVE_MUST_NOT_EXIST'
 try:link_closed(src/'traces'/pathlib.Path(firstpath).name,negative_dest,'0'*64)
 except AssertionError:pass
 else:raise AssertionError('negative SHA accepted')
 assert not negative_dest.exists()
 proof['negative_cases'].append({'case':'wrong_full_SHA','status':'REJECTED_BEFORE_LINK','destination_absent':True})
 listed={line.strip() for line in next((src/'traces').glob('kernelslist_ctx_*')).read_text().splitlines() if line.startswith('kernel')}
 assert listed=={pathlib.Path(p).name for p in validation['source_files']}
 for oldpath,digest in validation['source_files'].items():proof['raw_files'].append(link_closed(src/'traces'/pathlib.Path(oldpath).name,root/'traces'/pathlib.Path(oldpath).name,digest))
 for name in ['EXECUTION.json','PROCESS_START.json','stdout.log','stderr.log','FULL_RECORD_VALIDATION.json','MAP_PREFLIGHT.log']:
  copy(src/name,root/name)
 for folder in ['map','runtime']:
  (root/folder).mkdir(exist_ok=True)
  for p in (src/folder).rglob('*'):
   if p.is_file():copy(p,root/folder/p.relative_to(src/folder))
 for p in (src/'traces').iterdir():
  if p.is_file() and not p.name.endswith(('.trace.xz','.traceg.xz')):copy(p,root/'traces'/p.name)
 # Reuse only checkpoint-declared, fully hashed closed partition/group files.
 for cp in (src/'postprocess_work').glob('*/CHECKPOINT.json'):
  state=json.loads(cp.read_text());assert state['partition_complete'];dest=root/'postprocess_work'/cp.parent.name;dest.mkdir(parents=True)
  copy(cp,dest/'CHECKPOINT.json')
  for x in state['partition_members']:link_closed(cp.parent/x['name'],dest/x['name'],x['sha256'])
  for idx,x in state['groups'].items():link_closed(cp.parent/('group-%08d.xz'%int(idx)),dest/('group-%08d.xz'%int(idx)),x['sha256'])
 proof['raw_files_total_bytes']=sum(x['bytes'] for x in proof['raw_files']);save(root/'CLOSED_CAPTURE_ADOPTION.json',proof)
 (root/'tools').mkdir();remote='/data/c16/rtx4080_suite_fill_20261024_v1/control/'
 remote_copy(task['argv'][0],root/'bin/application');assert sha(root/'bin/application')==task['binary_sha256']
 remote_copy('/data/c16/ada_trace_semantics_20261024_v1/frozen/producer_v7_55c6f482/producer.so',root/'tools/producer.so')
 for name in ['validate_v7_stream_v3.py','make_semantic_map_v2.py','ssh_rate_bridge.py']:
  remote_copy(remote+name,root/'tools'/name)
 remote_copy(remote+'pipeline_versions/'+execution['pipeline_sha256']+'.py',root/'tools/capture_origin_worker.py')
 assert sha(root/'tools/capture_origin_worker.py')==execution['pipeline_sha256']
 for n in ['CONTRACT.json','validate_v7.py','make_semantic_map.py']:
  remote_copy('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/'+n,root/'contract'/n)
 if task.get('source'):
  remote_copy(task['source'],root/'source'/pathlib.Path(task['source']).name);assert sha(root/'source'/pathlib.Path(task['source']).name)==task['source_sha256']
 assert sha(C/'postprocess_nas_sharded_v2.py')=='91ccc18db2a9859b565f4a210506554d3866ee63ca78149fe1972023465826c5'
 copy(C/'postprocess_nas_sharded_v2.py',root/'tools/postprocess_nas_sharded_v2.py');copy(pathlib.Path(__file__),root/'tools/resume_3mm_native174_v1.py')
 numerical=job['numerical_policy'];stdout=(root/'stdout.log').read_text();assert re.search(task['correctness']['stdout_regex'],stdout)
 post=[]
 for raw in sorted((root/'traces').glob('*.trace.xz')):
  dest=raw.with_name(raw.name.replace('.trace.xz','.traceg.xz'));work=root/'postprocess_work'/raw.stem
  def on109(p):return '/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/'+str(p.relative_to(B))
  cmd=['flock','-n','/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','nice','-n','15','ionice','-c','2','-n','7','python3','/data/c16/rtx4080_suite_fill_20261024_v1/control/postprocess_nas_sharded_v2.py',on109(raw),on109(dest),on109(work)]
  cp=subprocess.run(['ssh','-n','-o','BatchMode=yes','gpu109',' '.join(shlex.quote(x) for x in cmd)],capture_output=True,text=True,timeout=86400)
  (root/('POSTPROCESS_'+raw.name+'.log')).write_text(cp.stdout+cp.stderr);assert cp.returncode==0,cp.stderr
  post.append(json.loads(cp.stdout));shutil.rmtree(work)
 save(root/'POSTPROCESS_NAS.json',post)
 ctx=next((root/'traces').glob('kernelslist_ctx_*'));(root/'traces/kernelslist.g').write_text(ctx.read_text().replace('.trace.xz','.traceg.xz'))
 save(root/'TASK.json',task);save(root/'NATIVE_QUALIFICATION.json',job['native_receipt'])
 m=json.loads((root/'map/manifest.json').read_text())
 asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':NEW,'suite':task['suite'],'source_version':task['version'],'program':task['program'],'variant':task['variant'],'input_identity':task.get('input_identity'),'argv':task['argv'],'binary_member':'bin/application','binary_sha256':task['binary_sha256'],'capture_gpu_uuid':execution['actual_gpu_uuid'],'actual_cubin_arch':89,'producer_sha256':sha(root/'tools/producer.so'),'contract_sha256':sha(root/'contract/CONTRACT.json'),'validator_sha256':validation['validator_sha256'],'frozen_parser_sha256':validation['frozen_parser_sha256'],'map_manifest_sha256':sha(root/'map/manifest.json'),'map_maker_sha256':sha(root/'tools/make_semantic_map_v2.py'),'postprocessor_sha256':sha(C/'postprocess_nas_sharded_v2.py'),'pump_sha256':sha(root/'tools/ssh_rate_bridge.py'),'worker_sha256':execution['pipeline_sha256'],'resume_worker_sha256':sha(pathlib.Path(__file__)),'capture_origin':proof,'postprocess_host':'native174 directly reads true164 via existing validated mount; no109GPU','full_application':{'kernel_launches':validation['kernels'],'ctas':validation['ctas'],'warps':validation['warps'],'records':validation['counts']['sass_records'],'all_warps_terminate':True,'expected_kernel_presence':'YES_SOURCE_ORACLE','expected_kernel_count':3,'context_count':1,'stream_ids':validation['stream_ids'],'sampling':'NONE','commandlist':'traces/kernelslist.g'},'numerical_status':numerical,'producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_AUTOMATICALLY_GRANTED; per-profile required','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0}
 asset['postprocess_host']=proof['postprocess_host'];asset['postprocess_pump_sha256']='8ff3e634870ae34071362afb834245291a49f8d9e37e524462515e3a95771295';asset['capture_pump_epoch']='V1 original immutable tool; preserved';asset['postprocess_pump_epoch']='V2 A/B 4+8MiB/s fullSHA qualified'
 save(root/'ASSET.json',asset)
 files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
 save(root/'SENDER_MANIFEST.json',{'asset':asset,'files':files})
 print(json.dumps({'status':'SENDER_COMPLETE','inflight':str(root.relative_to(B)),'asset_id':NEW,'sender_manifest_sha256':sha(root/'SENDER_MANIFEST.json'),'payload_files':len(files),'payload_bytes':sum(x['bytes'] for x in files)}))
except Exception as e:
 if root.exists() and not (root/'FAILURE.json').exists():save(root/'FAILURE.json',{'status':'FAILED_RETAINED','error':repr(e),'traceback':traceback.format_exc(),'no_gpu_recapture':True})
 print(json.dumps({'status':'FAILED_RETAINED','error':repr(e)}))
