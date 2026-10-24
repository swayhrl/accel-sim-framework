import pathlib,json,fcntl,time,hashlib,subprocess
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');ID='C8_CUDA118_SIMPLEVOTE_DEFAULT_A001';receiver=C/'dispatch_bulk_v3.py';assert hashlib.sha256(receiver.read_bytes()).hexdigest()=='e7a090d2baed8d0177cdf4af5132490023dad4ed60d35f46271db8f3c6f52025';ns={};exec(compile(receiver.read_text().split('\nsingle=open(',1)[0],str(receiver),'exec'),ns)
locks=[];deadline=time.time()+7200
try:
 for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
  f=open(C/name,'a');locks.append(f)
  while True:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:assert time.time()<deadline;time.sleep(.05)
 p=subprocess.run(['ssh','-n','gpu109','python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/import_local_c8_vote_v1.py'],capture_output=True,text=True,timeout=300);ns['save'](C/(ID+'_IMPORT_PROCESS.json'),{'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0
 commit=ns['publish'](json.loads(p.stdout));ns['save'](C/(ID+'_COMMIT_READBACK.json'),commit)
 with(C/'RTX4080_QUEUE.lock').open('a')as f:
  fcntl.flock(f,fcntl.LOCK_EX);queue=json.loads((C/'QUEUE.json').read_text());assert all(x['id']!=ID for x in queue);queue.append({'id':ID,'asset_id':ID,'type':'APPROVED_C8_EXACT_NEW_FULL_GAP','status':'COMMITTED_VERIFIED','commit':commit,'scientific_content_id':'c48c574773ad10247fa6c7fe23b1002dba9ad68c6c3d626341a7c7ce939d817d','source_coverage_pending_native_coldread':True});ns['save'](C/'QUEUE.json',queue)
 print(json.dumps(commit))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
