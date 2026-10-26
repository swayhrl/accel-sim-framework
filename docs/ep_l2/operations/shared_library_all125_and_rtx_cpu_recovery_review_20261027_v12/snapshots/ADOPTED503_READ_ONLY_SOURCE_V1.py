#!/usr/bin/python3
"""Exact finite read-only SM70 adopted-object two-pass SHA audit. No children or publishers."""
import argparse,hashlib,json,os,pathlib,resource,signal,stat,time,select
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def stable(s):return (s.st_dev,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def fullstat(s):return dict(dev=s.st_dev,inode=s.st_ino,mode=s.st_mode,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def write_new(p,x):
 raw=canonical(x)
 with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def small_ref(path,expected,cap=4*1024**2):
 raw=path.read_bytes()
 if len(raw)>cap or hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('Pinned metadata mismatch')
 return json.loads(raw)
def mount_proof():
 lines=[l for l in pathlib.Path('/proc/self/mountinfo').read_text().splitlines() if ' /root/share/mnt164 ' in l]
 if len(lines)!=1 or ' - fuse.sshfs admin-wcx@10.208.130.164:/home/shared ' not in lines[0]:raise RuntimeError('True164 mount binding changed')
 return lines[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',required=True);ap.add_argument('--plan-sha',required=True);ap.add_argument('--approval',required=True);ap.add_argument('--approval-sha',required=True);ap.add_argument('--work',required=True);ap.add_argument('--gate-fd',type=int,required=True);a=ap.parse_args()
 work=pathlib.Path(a.work);started=time.time();total=0;results=[]
 def term(sig,frame):raise TimeoutError('Finite deadline or exact worker termination')
 signal.signal(signal.SIGALRM,term);signal.signal(signal.SIGTERM,term);signal.alarm(10800)
 try:
  approval=small_ref(pathlib.Path(a.approval),a.approval_sha)
  plan=small_ref(pathlib.Path(a.plan),a.plan_sha)
  assert approval['status']=='ROOT_APPROVED_EXACT_READONLY_ADOPTED503_FULL_SHA_V1'
  assert approval['plan_sha256']==a.plan_sha and approval['script_sha256']==hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
  assert approval['work']==str(work) and not (work/'STARTED.json').exists()
  assert plan['objects_count']==503 and len(plan['objects'])==503
  assert len({r['sha256'] for r in plan['objects']})==503
  assert sum(r['bytes'] for r in plan['objects'])==plan['unique_bytes']==21565136675
  assert approval['rate_bytes_per_second']==10485760 and approval['passes']==2
  assert approval['source_KEEP'] is True and approval['public_writes_allowed'] is False
  assert approval['host']==os.uname().nodename and approval['boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  assert started<approval['absolute_deadline_unix'] and approval['absolute_deadline_unix']-approval['not_before_unix']<=10800
  assert sorted(os.sched_getaffinity(0))==approval['cpu_ids'] and os.getpriority(os.PRIO_PROCESS,0)>=15
  assert 0<resource.getrlimit(resource.RLIMIT_AS)[0]<=512*1024**2
  assert hashlib.sha256(pathlib.Path(plan['frozen_allobjects_path']).read_bytes()).hexdigest()==plan['frozen_allobjects_sha256']
  current_mount=mount_proof();assert current_mount==plan['mountinfo']
  ready=select.select([a.gate_fd],[],[],120)[0]
  assert ready and os.read(a.gate_fd,1)==b'G';os.close(a.gate_fd)
  write_new(work/'STARTED.json',dict(status='RUNNING_READONLY_TWO_PASS_FULL_SHA',pid=os.getpid(),unix=time.time(),objects=503,unique_bytes=plan['unique_bytes'],total_planned_read_bytes=2*plan['unique_bytes'],rate_bytes_per_second=10485760,source_KEEP=True))
  mono=time.monotonic()
  def check():
   if time.time()>=approval['absolute_deadline_unix']:raise TimeoutError('Absolute deadline')
  def hash_pass(row,expected_identity):
   nonlocal total
   p=pathlib.Path(row['resolved_path'])
   assert p.is_absolute() and p.resolve()==p and p.is_relative_to('/root/share/mnt164')
   before=p.stat(follow_symlinks=False)
   assert stat.S_ISREG(before.st_mode) and stable(before)==tuple(expected_identity)
   fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
   h=hashlib.sha256();n=0
   try:
    fst=os.fstat(fd);assert stable(fst)==stable(before) and fst.st_ino==before.st_ino
    while True:
     check();buf=os.read(fd,1024**2)
     if not buf:break
     h.update(buf);n+=len(buf);total+=len(buf)
     target=mono+total/approval['rate_bytes_per_second']
     while time.monotonic()<target:
      check();time.sleep(max(0,min(.25,target-time.monotonic())))
    after_fd=os.fstat(fd)
    assert stable(after_fd)==stable(fst) and after_fd.st_ino==fst.st_ino
   finally:os.close(fd)
   after_path=p.stat(follow_symlinks=False)
   assert stable(after_path)==stable(before)
   assert p.resolve()==p and n==row['bytes'] and h.hexdigest()==row['sha256']
   return dict(bytes=n,sha256=h.hexdigest(),before=fullstat(before),after_fd=fullstat(after_fd),after_path=fullstat(after_path),closed=True)
  for i,row in enumerate(plan['objects']):
   check();assert mount_proof()==current_mount
   first=hash_pass(row,row['stable_identity'])
   second=hash_pass(row,row['stable_identity'])
   proof=dict(schema='SM70_ADOPTED_OBJECT_TWO_PASS_CURRENT_FULL_SHA_V1',object_sha256=row['sha256'],frozen_storage_path=row['storage_path'],resolved_path=row['resolved_path'],passes=[first,second],source_KEEP=True,qualification_scope='CURRENT_TRUE164_STORAGE_BODY_ONLY_NOT_NATIVE_OR_CONSUMER')
   rr=write_new(work/'objects'/('object_'+str(i).zfill(4)+'.json'),proof);results.append(rr)
   write_new(work/'progress'/('progress_'+str(i).zfill(4)+'.json'),dict(completed=i+1,total_read_bytes=total,unix=time.time(),last_receipt=rr))
  assert total==2*plan['unique_bytes']
  write_new(work/'TERMINAL.json',dict(schema='SM70_ADOPTED503_FULL_SHA_AUDIT_TERMINAL_V1',status='ALL503_TWO_PASS_CURRENT_TRUE164_FULL_SHA_PASS',objects=503,unique_bytes=plan['unique_bytes'],total_read_bytes=total,started_unix=started,ended_unix=time.time(),result_refs=results,source_KEEP=True,source_release_bytes=0,Native_payload_bytes=0,GPU_or_simulation_executions=0,qualification_scope='CURRENT_TRUE164_STORAGE_BODY_ONLY_NOT_NATIVE_OR_CONSUMER'))
 except BaseException as e:
  if not (work/'TERMINAL.json').exists():
   write_new(work/'TERMINAL.json',dict(status='FAILED_RETAINED_ROOT_DIAGNOSIS_REQUIRED',error=repr(e),completed=len(results),total_read_bytes=total,unix=time.time(),source_KEEP=True,public_writes=False))
  raise
 finally:signal.alarm(0)
if __name__=='__main__':main()
