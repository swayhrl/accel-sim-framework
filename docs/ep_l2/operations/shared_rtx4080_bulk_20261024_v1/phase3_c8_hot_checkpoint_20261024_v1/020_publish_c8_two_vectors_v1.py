import pathlib,json,hashlib,fcntl,subprocess,time,os
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receiver=C/'dispatch_bulk_v3.py';assert sha(receiver)=='e7a090d2baed8d0177cdf4af5132490023dad4ed60d35f46271db8f3c6f52025'
ns={};exec(compile(receiver.read_text().split('\nsingle=open(',1)[0],str(receiver),'exec'),ns)
rows=[];deadline=time.time()+1800
for ident in ['C8_SDK42_VECTOR_SIZE4000000_A001','C8_SDK42_VECTOR_SIZE6000000_A001']:
 locks=[]
 try:
  for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
   f=open(C/name,'a');locks.append(f)
   while True:
    try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
    except BlockingIOError:assert time.time()<deadline;time.sleep(1)
  p=subprocess.run(['ssh','-n','gpu109','python3 /data/c16/rtx4080_suite_fill_20261024_v1/control/import_local_c8_two_vectors_v1.py '+ident],capture_output=True,text=True,timeout=600)
  ns['save'](C/(ident+'_IMPORT_PROCESS.json'),{'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0
  commit=ns['publish'](json.loads(p.stdout));rows.append(commit);ns['save'](C/(ident+'_COMMIT_READBACK.json'),commit)
  with(C/'RTX4080_QUEUE.lock').open('a')as qf:
   fcntl.flock(qf,fcntl.LOCK_EX);q=json.loads((C/'QUEUE.json').read_text());assert all(x['id']!=ident for x in q);q.append({'id':ident,'asset_id':ident,'type':'APPROVED_C8_LOCAL_CLOSED_IMPORT','status':'COMMITTED_VERIFIED','commit':commit,'new_source_workload_coverage_increment':0});ns['save'](C/'QUEUE.json',q)
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 ns['save'](C/'C8_TWO_VECTOR_TRUE164_COMMIT_BATCH_V1.json',{'status':'COMMITTED_VERIFIED','rows':rows,'source_KEEP':True,'new_source_workload_coverage_increment':0})
print(json.dumps(rows))
