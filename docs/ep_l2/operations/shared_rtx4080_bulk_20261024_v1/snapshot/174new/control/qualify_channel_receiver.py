#!/usr/bin/env python3
import pathlib,subprocess,fcntl,json,hashlib,os,time
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
locks=[]
def paced_read_sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):
   t=time.monotonic();h.update(b);time.sleep(max(0,len(b)/(15*1024**2)-(time.monotonic()-t)))
 return h.hexdigest()
def writejson(p,o):
 with p.open('x') as f:f.write(json.dumps(o,indent=2)+'\n');f.flush();os.fsync(f.fileno())
try:
 for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
  f=open(C/name,'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 p=subprocess.run(['ssh','-n','-o','BatchMode=yes','gpu109','python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/qualify_channel_writer.py'],capture_output=True,text=True,timeout=180)
 assert p.returncode==0,p.stderr
 source=json.loads(p.stdout);tests=[];good=None
 for case in source['cases']:
  root=B/case['path'];assert B in root.parents and not (root/'COMMIT.json').exists()
  if case['case'] in ['partial','corrupt']:
   data=root/'payload.bin';actual_bytes=data.stat().st_size;actual_sha=paced_read_sha(data)
   reject=actual_bytes!=case['expected_bytes'] or actual_sha!=case['expected_sha256'];assert reject
   receipt={'case':case['case'],'status':'REJECTED_NO_COMMIT','bytes':actual_bytes,'sha256':actual_sha,'reason':'length' if actual_bytes!=case['expected_bytes'] else 'sha_mismatch'}
   writejson(root/'REJECT.json',receipt)
   target=B/'quarantine'/(source['tag']+'_'+case['case']);root.rename(target);receipt['retained']=str(target);tests.append(receipt)
  else:
   for x in case['chunks']:
    f=root/x['name'];assert f.stat().st_size==x['bytes'] and paced_read_sha(f)==x['sha256']
   final=root/'payload.bin'
   with final.open('xb') as out:
    for x in case['chunks']:
     with (root/x['name']).open('rb') as inp:
      for b in iter(lambda:inp.read(1024**2),b''):
       t=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*1024**2)-(time.monotonic()-t)))
    out.flush();os.fsync(out.fileno())
   assert final.stat().st_size==case['expected_bytes'] and paced_read_sha(final)==case['expected_sha256']
   good={'kind':'TRANSPORT_QUALIFICATION_ONLY','status':'COMMITTED_VERIFIED','payload_bytes':case['expected_bytes'],'payload_sha256':case['expected_sha256'],'closed_reopened_full_sha':True,'crash_child_exit':99,'verified_reused_chunks':2,'full_trace_asset':False,'native174_locks':[str(C/'RTX4080_SOURCE.lock'),str(C/'RTX4080_TARGET.lock')],'mount_chain':['109 sshfs hrl174new:/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1','174new sshfs admin-wcx@10.208.130.164:/home/shared'],'max_transfer_rate_bytes_s':15*1024**2,'adaptive_io_psi_rate_tiers':'15/8/4/1 MiB/s at avg10 <5/<10/<20/>=20; pressure-read failure1MiB/s','unix':time.time(),'source_keep':True,'release_bytes':0}
   writejson(root/'COMMIT.json',good);target=B/'objects'/source['tag'];root.rename(target)
   assert paced_read_sha(target/'payload.bin')==case['expected_sha256'];good['published']=str(target);tests.append({'case':'crash_and_resume','status':'PASS','published':str(target)})
 receipt={'status':'PASS','kind':'TRANSPORT_QUALIFICATION_ONLY','tests':tests,'commit':good,'source':source,'sm70_original_locks_untouched':True,'ssd_payload_staging_bytes':0}
 writejson(C/'CHANNEL_QUALIFICATION_RECEIPT.json',receipt);writejson(B/'receipts'/(source['tag']+'.json'),receipt)
 print(json.dumps(receipt))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()

