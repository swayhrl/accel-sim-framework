import sys,json,time,os,hashlib,tarfile,io
from pathlib import Path as P
root,test,kind,label=sys.argv[1:];sys.path.insert(0,root);import ep_perf_common_v2 as c;import ep_perf_archive as a
b=P(test);assert str(c.GLOBAL_MAIN_ADMISSION_LOCK).endswith('execution_performance_first_20261103_v1/control/ADMISSION.lock');assert str(c.GLOBAL_MAIN_RESTORE_WINDOW_LOCK).endswith('execution_performance_first_20261103_v1/control/ARCHIVE_SHARED_WINDOW.lock')
log=b/(kind+'.jsonl')
def event(x):
 with log.open('a')as f:f.write(json.dumps(dict(event=x,label=label,time=time.monotonic_ns()))+'\n')
if kind=='admission':
 with c.locked(b/'global_admission.lock'):event('ENTER');time.sleep(.06);event('EXIT')
else:
 a.GLOBAL_MAIN_RESTORE_WINDOW_LOCK=b/'global_restore.lock'
 def body(case):
  event('ENTER');p=b/label;p.mkdir();data=('TEST_ONLY_'+label).encode();tar=p/'tiny.tar';h=hashlib.sha256(data).hexdigest()
  with tarfile.open(tar,'w')as t:
   ti=tarfile.TarInfo('payload.txt');ti.size=len(data);t.addfile(ti,io.BytesIO(data))
  mf=p/'manifest.json';mf.write_text(json.dumps(dict(archive_sha256=a.sha(tar),members=[dict(member='payload.txt',bytes=len(data),sha256=h,uid=os.getuid(),gid=os.getgid(),mode=0o600,atime_ns=1700000000000000000,mtime_ns=1700000000000000000)])))
  for i in range(2):
   r=a.restore(tar,mf,p/('native'+str(i)),1024);assert r['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS';time.sleep(.03)
  with c.locked(b/'global_admission.lock'):pass
  event('EXIT');return dict(status='CPU_ONLY_TWO_REAL_RESTORES_PASS')
 a._archive_case=body
 assert a.archive_case('TEST_ONLY')['status']=='CPU_ONLY_TWO_REAL_RESTORES_PASS'
print('PASS')
