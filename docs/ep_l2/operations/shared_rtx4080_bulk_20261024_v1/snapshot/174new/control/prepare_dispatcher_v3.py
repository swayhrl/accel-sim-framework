#!/usr/bin/env python3
import pathlib,py_compile
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
s=(C/'dispatch_bulk.py').read_text()
s=s.replace("assert sha(root/'bin/vectorAdd')==asset['binary_sha256'] if asset['program']=='vectorAdd' else True","assert sha(root/asset.get('binary_member','bin/vectorAdd'))==asset['binary_sha256']")
s=s.replace("single=open(C/'RTX4080_DISPATCHER.lock','a');",'''def update_job(job):
 f=open(C/'RTX4080_QUEUE.lock','a');fcntl.flock(f,fcntl.LOCK_EX)
 try:
  fresh=json.loads((C/'QUEUE.json').read_text());found=False
  for i,x in enumerate(fresh):
   if x['id']==job['id']:fresh[i]=job;found=True;break
  assert found,'job lost from queue'
  save(C/'QUEUE.json',fresh)
 finally:fcntl.flock(f,fcntl.LOCK_UN);f.close()
single=open(C/'RTX4080_DISPATCHER.lock','a');''')
s=s.replace("save(C/'QUEUE.json',queue)","update_job(job)")
s=s.replace("cmd=['ssh','-n','-o','BatchMode=yes','gpu109','python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/capture_ordinary_worker.py '+job['job_path']]","worker=job.get('worker_script','/data/c16/rtx4080_suite_fill_20261024_v1/control/capture_ordinary_worker.py')\n   cmd=['ssh','-n','-o','BatchMode=yes','gpu109','python3 '+worker+' '+job['job_path']]\n  elif job['type']=='RESUME_POST_NATIVE174':\n   cmd=['python3','-B',job['worker_script']]")
s=s.replace("'POSTPROCESS_NAS_V2_QUALIFICATION_RECEIPT.json']","'POSTPROCESS_NAS_V2_QUALIFICATION_RECEIPT.json','PUMP_V2_AB_RECEIVER_QUALIFICATION.json']")
p=C/'dispatch_bulk_v3.py';p.write_text(s);py_compile.compile(str(p),doraise=True)
print(p)
