from pathlib import Path
import json,hashlib,sys,subprocess,os,resource,datetime,signal
root=Path('/workspace/ep_l2_mechanism_lane3_v1');root.mkdir(exist_ok=True);contract=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());client=Path(contract['registry_client']);assert hashlib.sha256(client.read_bytes()).hexdigest()==contract['registry_client_sha256'];sys.path.insert(0,str(client.parent));from registry import Registry,local_resources,process_identity
r=Registry();x=local_resources();assert x['disk_free_bytes']>=50*2**30 and x['available_memory_bytes']-2*2**30>=64*2**30
fs=os.statvfs('/root/share');assert fs.f_bavail*fs.f_frsize>=40*2**30
lease=r.build_lease('lane3',cpu=1,memory=2*2**30);report={'lease':lease,'cpu':1,'memory_bytes':2*2**30,'before':x,'scope':'read-only raw derivation; no sim or trace body scan'}
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));resource.setrlimit(resource.RLIMIT_CPU,(180,180));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
try:
 cmd=['/usr/bin/python3','util/ep_l2/mechanism_analysis_v1/derive.py','--out',str(root/'derived_r2')];report['command']=cmd
 with (root/'derive_r2.log').open('x') as f:
  child=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits);report['process']=process_identity(child.pid)
  try:report['exit_code']=child.wait(timeout=240)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
 assert report['exit_code']==0
finally:r.release_build(lease,'lane3');report['released']=True;(root/'DERIVATION_LEASE_r2.json').write_text(json.dumps(report,indent=2)+'\n')
print((root/'derive_r2.log').read_text())
