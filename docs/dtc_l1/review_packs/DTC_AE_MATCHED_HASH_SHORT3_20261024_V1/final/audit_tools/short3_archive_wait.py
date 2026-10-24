"""Bounded COPY_ONLY outbox lock wait. Never calls experiment or a model."""
import pathlib,json,subprocess,time,datetime,sys
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1');N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2')
def archive_wait(cell,tag='OUTBOX_WAIT',max_seconds=21600):
 start=time.monotonic();attempt=0
 while True:
  attempt+=1;r=subprocess.run([str(N/'bin/result'),'archive',cell],capture_output=True,text=True,timeout=300)
  p=T/'control'/(cell+'.'+tag+'.'+str(attempt).zfill(3)+'.json')
  with p.open('x') as f:json.dump({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'copyonly':True,'new_model_starts':0},f,indent=2);f.write('\n')
  if r.returncode==0:
   x=json.loads(r.stdout);assert x['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET';return x
  try:e=json.loads(r.stderr)
  except ValueError:r.check_returncode()
  if '[Errno 11]' not in e.get('reason','') or time.monotonic()-start>=max_seconds:r.check_returncode()
  print(json.dumps({'state':'WAIT_SHARED_RECEIVER_OR_SCIENCE_LOCK_COPY_ONLY','cell':cell,'attempt':attempt,'elapsed_seconds':time.monotonic()-start,'new_model_starts':0}),flush=True);time.sleep(30)
if __name__=='__main__':print(json.dumps(archive_wait(sys.argv[1],tag='COPYONLY_LOCK_WAIT'),indent=2))
