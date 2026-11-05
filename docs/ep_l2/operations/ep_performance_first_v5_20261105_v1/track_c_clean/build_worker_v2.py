from pathlib import Path
import os,json,subprocess,time,resource,signal
p=Path(__file__).parent
q=json.loads((p/'BUILD_LOCATION.json').read_text());build=Path(q['build']);bulk=Path(q['bulk']);s=p/'core_candidate'
env=os.environ.copy();env.update(GPGPUSIM_ROOT=str(s),CUDA_INSTALL_PATH='/root/data/dtc_main_20261023_v1/ae_fair_v1/toolchain',ACCELSIM_CONFIG='release')
os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(10*1024**3,10*1024**3))
started=time.time()
def write(state):
 (p/'BUILD_STATE.json').write_text(json.dumps(dict(state,started=started,updated=time.time(),science_starts=0),indent=2)+'\n')
write({'state':'CONFIGURING','pid':os.getpid()})
cmd=['cmake','-S','/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/framework/gpu-simulator','-B',str(build),'-DCUDAToolkit_ROOT=/root/data/dtc_main_20261023_v1/ae_fair_v1/toolchain']
with (bulk/'configure_final_v2.log').open('w') as out:
 r=subprocess.run(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=180)
if r.returncode:write({'state':'CONFIGURE_FAILED','rc':r.returncode});raise SystemExit(r.returncode)
flags=0
for f in build.rglob('flags.make'):
 t=f.read_text()
 if '-g3' in t:f.write_text(t.replace('-g3','-g0'));flags+=1
assert os.statvfs('/root/data').f_bavail*os.statvfs('/root/data').f_frsize>5*1024**3
cmd=['cmake','--build',str(build),'--target','ep_l2_quota_row_port_v5','ep_l2_quota_handshake_v5','accel-sim.out','--parallel','2']
write({'state':'BUILD_RUNNING','pid':os.getpid(),'command':cmd,'flags_g3_to_g0_only':flags})
with (bulk/'production_build_v2.log').open('w') as out:
 child=subprocess.Popen(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 try:r=child.wait(timeout=1800)
 except subprocess.TimeoutExpired:
  # Only this build's new isolated session. No foreign/task/model signalling.
  os.killpg(child.pid,signal.SIGTERM);r=child.wait(timeout=30)
  write({'state':'BUILD_WALL_LIMIT_OWNED_SESSION_STOPPED','rc':r});raise SystemExit(124)
write({'state':'BUILD_PASS' if r==0 else 'BUILD_FAILED','rc':r,'seconds':time.time()-started,'flags_g3_to_g0_only':flags})
