#!/usr/bin/env python3
import pathlib,json,hashlib,os,time,fcntl,subprocess,traceback,shutil
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
def save(p,o):
 t=p.with_name(p.name+'.tmp')
 with t.open('w') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   t=time.monotonic();h.update(b);time.sleep(max(0,len(b)/(15*1048576)-(time.monotonic()-t)))
 return h.hexdigest()
def publish(sender):
 root=B/sender['inflight'];assert B in root.parents
 manifest=root/'SENDER_MANIFEST.json';assert sha(manifest)==sender['sender_manifest_sha256']
 m=json.loads(manifest.read_text())
 asset=m['asset']
 assert asset['kind']=='FULL_APPLICATION_TRACE' and asset['producer_semantic_qualification']=='ADA7_ORDINARY_FULL_RECORD_PASS'
 assert asset['capture_gpu_uuid']=='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59' and asset['actual_cubin_arch']==89
 assert sha(root/'bin/vectorAdd')==asset['binary_sha256'] if asset['program']=='vectorAdd' else True
 assert sha(root/'tools/producer.so')==asset['producer_sha256']
 validation=json.loads((root/'FULL_RECORD_VALIDATION.json').read_text())
 assert validation['kernels']==asset['full_application']['kernel_launches'] and validation['all_declared_warps_terminate']
 raw={p.name for p in (root/'traces').glob('kernel*.trace.xz')}
 lists=list((root/'traces').glob('kernelslist_ctx_*'));assert len(lists)==1
 named={line.strip() for line in lists[0].read_text().splitlines() if line.strip().startswith('kernel')}
 assert raw==named and len(raw)==validation['kernels']
 assert len(list((root/'traces').glob('kernel*.traceg.xz')))==len(raw)
 for x in m['files']:
  p=root/x['path'];assert root in p.parents and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x
 for name in ['PARENT_ORDINARY_BULK_RELEASE.json','CHANNEL_QUALIFICATION_RECEIPT.json','POSTPROCESS_NAS_QUALIFICATION_RECEIPT.json','POSTPROCESS_NAS_V2_QUALIFICATION_RECEIPT.json']:
  src=C/name;dst=root/('RECEIVER_'+name);assert not dst.exists();shutil.copyfile(src,dst)
 actual=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
 final={'asset_id':sender['asset_id'],'source_sender_manifest_sha256':sender['sender_manifest_sha256'],'files':actual,'file_count':len(actual),'logical_bytes':sum(x['bytes'] for x in actual)}
 save(root/'MANIFEST.json',final);digest=sha(root/'MANIFEST.json')
 commit={'schema':'RTX4080_SHARED_IMMUTABLE_COMMIT_V1','kind':'FULL_APPLICATION_TRACE','status':'COMMITTED_VERIFIED','asset_id':sender['asset_id'],'manifest_sha256':digest,'files':len(actual),'logical_bytes':final['logical_bytes'],'producer_semantic_status':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_per_profile_qualification':'NOT_AUTOMATICALLY_GRANTED','source_keep':True,'release_bytes':0,'ssd_payload_staging_bytes':0,'utc_unix':time.time(),'channel':'dedicated RTX4080 Native174 locks;109->privateSSHFS174new->true164'}
 save(root/'COMMIT.json',commit)
 dest=B/'objects'/sender['asset_id'];assert not dest.exists();root.rename(dest)
 assert sha(dest/'MANIFEST.json')==digest
 for x in actual:
  p=dest/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 commit['object_path']=str(dest);save(B/'receipts'/(sender['asset_id']+'_RECEIVER_READBACK.json'),commit)
 cat=B/'catalog/ASSETS.json';data=json.loads(cat.read_text()) if cat.exists() else {'schema':'RTX4080_ASSET_CATALOG_V1','objects':[]}
 assert all(x['asset_id']!=sender['asset_id'] for x in data['objects']);data['objects'].append(commit);save(cat,data)
 return commit
single=open(C/'RTX4080_DISPATCHER.lock','a');fcntl.flock(single,fcntl.LOCK_EX|fcntl.LOCK_NB)
ident={'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'start_unix':time.time()}
save(C/'DISPATCHER_IDENTITY.json',ident)
while not (C/'STOP_AFTER_CURRENT').exists():
 queue=json.loads((C/'QUEUE.json').read_text())
 jobs=[x for x in queue if x.get('status','PENDING')=='PENDING']
 if not jobs:save(C/'DISPATCHER_STATE.json',dict(ident,status='WAIT_QUEUE',unix=time.time()));time.sleep(5);continue
 job=jobs[0];locks=[]
 try:
  for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
   f=open(C/name,'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  job.update(status='RUNNING',started=time.time());save(C/'QUEUE.json',queue);save(C/'DISPATCHER_STATE.json',dict(ident,status='RUNNING',job=job,unix=time.time()))
  if job['type']=='IMPORT_VECTOR55':
   cmd=['ssh','-n','-o','BatchMode=yes','gpu109','python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/'+job.get('worker_script','import_first_vector.py')]
  elif job['type']=='CAPTURE_ORDINARY':
   cmd=['ssh','-n','-o','BatchMode=yes','gpu109','python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/capture_ordinary_worker.py '+job['job_path']]
  else:raise RuntimeError('unsupported queue kind')
  with (C/(job['id']+'.stderr.log')).open('x') as err:
   p=subprocess.run(cmd,capture_output=False,stdout=subprocess.PIPE,stderr=err,text=True,timeout=86400)
  (C/(job['id']+'.stdout.log')).write_text(p.stdout)
  assert p.returncode==0,('worker exit',p.returncode)
  sender=json.loads(p.stdout)
  if sender.get('status')=='SENDER_COMPLETE':
   commit=publish(sender);job.update(status='COMMITTED_VERIFIED',commit=commit)
  else:job.update(status=sender.get('status','HOLD'),result=sender)
 except BlockingIOError:
  save(C/'DISPATCHER_STATE.json',dict(ident,status='WAIT_RTX_CHANNEL_LOCK',unix=time.time()));time.sleep(5);continue
 except Exception as e:
  job.update(status='FAILED_RETAINED',error=repr(e),traceback=traceback.format_exc());save(C/(job['id']+'_FAILURE.json'),job)
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 job['end_unix']=time.time();save(C/'QUEUE.json',queue);save(C/'DISPATCHER_STATE.json',dict(ident,status=job['status'],job_id=job['id'],unix=time.time()))
 print(json.dumps({'job_id':job['id'],'status':job['status']}),flush=True)

