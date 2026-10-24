import pathlib,ast
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1');p=T/'tools/short3_final_review_bundle.py';s=p.read_text()
s=s.replace('import pathlib,json,hashlib,datetime,subprocess,importlib.util,shutil,os,stat,tarfile,fcntl','import pathlib,json,hashlib,datetime,subprocess,importlib.util,shutil,os,stat,tarfile,fcntl,time')
marker="assert git(F,'rev-parse','HEAD')==SOURCE"
at=s.index(marker)
helper='''def acquire_copyonly_pair(science,receiver):
 started=time.monotonic()
 while True:
  held=False
  try:
   fcntl.flock(science,fcntl.LOCK_EX|fcntl.LOCK_NB);held=True
   fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB);return
  except BlockingIOError:
   if held:fcntl.flock(science,fcntl.LOCK_UN)
   if time.monotonic()-started>21600:raise
   print(json.dumps({'state':'WAIT_COPYONLY_REVIEW_SHARED_LOCK','elapsed_seconds':time.monotonic()-started,'new_model_starts':0}),flush=True);time.sleep(30)
'''
s=s[:at]+helper+s[at:]
old="science_lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(science_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)"
new="science_lock=(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');receiver=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');acquire_copyonly_pair(science_lock,receiver)"
assert old in s;s=s.replace(old,new)
old="before=m.gate(raw+16*MIB);receiver=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB)"
assert old in s;s=s.replace(old,"before=m.gate(raw+16*MIB);assert receiver is not None")
ast.parse(s);p.write_text(s)
print('COPYONLY_REVIEW_PAIR_LOCK_WAIT_BEFORE_ANY_STAGING_READY')
