from pathlib import Path
import subprocess,json,hashlib,fcntl,os,time,base64,select
R=Path('/root/data/ada_native_extensions_stage4_20261024_v1');C=Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
plan=json.loads((R/'STAGE4_ARCHIVE_READY_PLAN.json').read_text())
target=Path(plan['target']);assert target.parent==Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/objects')
assert not target.exists()
locks=[];remote=None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'kind':'ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD','source_keep':True,'release_bytes':0,'plan_sha256':sha(R/'STAGE4_ARCHIVE_READY_PLAN.json'),'started':time.time()}
try:
 for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
  f=open(C/name,'a');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 code="import fcntl,json,sys,os,pathlib;f=open('/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);print(json.dumps({'LOCAL_IO_LOCKED':True,'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19]}),flush=True);sys.stdin.readline();fcntl.flock(f,fcntl.LOCK_UN)"
 remote=subprocess.Popen(['ssh','gpu109',"python3 -B -c 'import base64;exec(base64.b64decode(\""+base64.b64encode(code.encode()).decode()+"\"))'"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert select.select([remote.stdout],[],[],15)[0],'109 lease handshake timeout'
 line=remote.stdout.readline();lockproof=json.loads(line);assert lockproof['LOCAL_IO_LOCKED'];receipt['remote_lock']=lockproof
 receipt['mount_proof']=subprocess.check_output(['findmnt','-T',str(target.parent),'-n','-o','TARGET,SOURCE,FSTYPE'],text=True).strip()
 assert '10.208.130.164' in receipt['mount_proof']and 'fuse.sshfs'in receipt['mount_proof']
 args=['python3','-B','/root/data/ada_stage_archive_control_20261024_v1/archive_stage.py','174new',str(target)]+plan['source_roots']
 cp=subprocess.run(args,capture_output=True,text=True,timeout=85)
 (R/'STAGE4_ARCHIVE_A1.stdout').write_text(cp.stdout);(R/'STAGE4_ARCHIVE_A1.stderr').write_text(cp.stderr)
 assert cp.returncode==0,cp.stdout+cp.stderr
 proof=json.loads(cp.stdout);receipt['archive']=proof;receipt['status']='TRUE164_FULL_SOURCE_MEMBER_SHA_CLOSED_COMMIT_PASS'
 for name in ['payload.tar','MANIFEST.json','CLOSED_READBACK.json','COMMIT.json']:
  receipt[name]={'bytes':(target/name).stat().st_size,'sha256':sha(target/name)}
 receipt['elapsed']=time.time()-receipt['started']
 with(R/'STAGE4_TRUE164_CLOSEOUT_A1.json').open('x')as f:json.dump(receipt,f,indent=2);f.write('\n')
 print(json.dumps(receipt))
finally:
 if remote:
  if remote.stdin:remote.stdin.close()
  try:remote.wait(timeout=5)
  except subprocess.TimeoutExpired:remote.terminate();remote.wait(timeout=5)
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
