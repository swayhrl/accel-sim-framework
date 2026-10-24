#!/usr/bin/env python3
import pathlib,hashlib,json,os,subprocess,sys,fcntl,time
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
B=R/'nas_rtx4080'
def data():return hashlib.shake_256(b'RTX4080_SHARED_CHANNEL_QUALIFICATION_20261024_V1').digest(8*1024**2)
def write(p,b):
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
if len(sys.argv)>1 and sys.argv[1] in ['crash-stage','resume-stage']:
 root=pathlib.Path(sys.argv[2]);b=data();receipts=[]
 for i in range(4):
  p=root/('chunk%04d.bin'%i);part=b[i*2*1024**2:(i+1)*2*1024**2];h=hashlib.sha256(part).hexdigest()
  if p.exists():
   assert p.stat().st_size==len(part) and hashlib.sha256(p.read_bytes()).hexdigest()==h
   receipts.append({'index':i,'reused_verified_chunk':True})
  else:write(p,part);receipts.append({'index':i,'reused_verified_chunk':False})
  if sys.argv[1]=='crash-stage' and i==1:os._exit(99)
 print(json.dumps({'stage':sys.argv[1],'receipts':receipts}));sys.exit(0)
lock=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
tag='channel_qualification_'+str(int(time.time()));root=B/'inflight'/tag;root.mkdir(exist_ok=False)
b=data();rec={'tag':tag,'kind':'TRANSPORT_QUALIFICATION_ONLY','source_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'writer_pid':os.getpid(),'writer_start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'mount_source':subprocess.check_output(['findmnt','-n','-T',str(B),'-o','SOURCE,FSTYPE,TARGET'],text=True).strip(),'cases':[]}
for name in ['partial','corrupt','resume']:(root/name).mkdir()
write(root/'partial/payload.bin',b[:1024**2])
rec['cases'].append({'case':'partial','path':str((root/'partial').relative_to(B)),'expected_bytes':len(b),'expected_sha256':rec['source_sha256']})
bad=bytearray(b);bad[len(bad)//2]^=1;write(root/'corrupt/payload.bin',bad)
rec['cases'].append({'case':'corrupt','path':str((root/'corrupt').relative_to(B)),'expected_bytes':len(b),'expected_sha256':rec['source_sha256']})
c=subprocess.run([sys.executable,__file__,'crash-stage',str(root/'resume')],capture_output=True,text=True);assert c.returncode==99
assert len(list((root/'resume').glob('chunk*.bin')))==2
assert not (root/'resume/COMMIT.json').exists()
d=subprocess.run([sys.executable,__file__,'resume-stage',str(root/'resume')],capture_output=True,text=True);assert d.returncode==0,d.stderr
rr=json.loads(d.stdout);assert sum(x['reused_verified_chunk'] for x in rr['receipts'])==2
rec['cases'].append({'case':'crash_and_resume','path':str((root/'resume').relative_to(B)),'crash_child_exit':c.returncode,'resume_child_exit':d.returncode,'resume_receipt':rr,'expected_bytes':len(b),'expected_sha256':rec['source_sha256'],'chunks':[{'name':'chunk%04d.bin'%i,'bytes':2*1024**2,'sha256':hashlib.sha256(b[i*2*1024**2:(i+1)*2*1024**2]).hexdigest()} for i in range(4)]})
write(root/'SOURCE_EXPECTATIONS.json',(json.dumps(rec,indent=2)+'\n').encode())
(R/'control/CHANNEL_SOURCE_QUALIFICATION.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec));fcntl.flock(lock,fcntl.LOCK_UN)

