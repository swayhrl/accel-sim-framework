from pathlib import Path
import json,subprocess,hashlib,os,sys,signal,resource,shlex
fw=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane3-v1');root=Path('/workspace/ep_l2_mechanism_lane3_v1');out=root/'minimal_cpp_r1';out.mkdir(exist_ok=False);core=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-fixed-r1')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();c=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());assert sha(c['registry_client'])==c['registry_client_sha256'];sys.path.insert(0,str(Path(c['registry_client']).parent));from registry import Registry,local_resources,process_identity
old=json.loads(Path('/workspace/results/ep_l2_ft20261016/lane1/review_r19/d2_r1/PRODUCTION_CHECK_RECEIPT.json').read_text());binding=old['fixture_build_identity'];reg=Registry();lease=None;r={'scope':'ACTUAL_FROZEN_CACHE_MASK_SECTOR_SNAPSHOT_AND_HANDLE_CHECKS_NOT_NUMERIC_BYTE_OR_FULL_PARTITION_PROOF','commands':[],'source_core':old['runtime_core'],'source_framework':old['runtime_framework'],'new_apps':0}
def safe():
 s=local_resources();assert s['disk_free_bytes']>=50*2**30 and s['available_memory_bytes']-4*2**30>=64*2**30;fs=os.statvfs('/root/share');assert fs.f_bavail*fs.f_frsize>=40*2**30
 return s
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(4*2**30,4*2**30));resource.setrlimit(resource.RLIMIT_CPU,(90,90));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def run(cmd,name):
 safe();log=out/(name+'.log')
 with log.open('x') as f:
  p=subprocess.Popen(['/usr/bin/time','-v',*cmd],cwd=out,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits);row={'command':cmd,'process':process_identity(p.pid),'log':str(log)};r['commands'].append(row)
  try:row['exit']=p.wait(timeout=100)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();raise
 row['sha256']=sha(log);assert row['exit']==0,row
try:
 r['before']=safe();lease=reg.build_lease('lane3',cpu=1,memory=4*2**30);r['lease']=lease
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip()==old['runtime_core'];assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=core)
 for path,d in binding['archives_sha256'].items():assert sha(path)==d
 source=fw/'util/ep_l2/mechanism_analysis_v1/minimal_cache_probe.cc';r['source_sha256']=sha(source);r['archives']=binding['archives_sha256']
 cc=next(v['command'][2:] for v in old['commands'] if '-c' in v['command']);cc[cc.index('-c')+1]=str(source);cc[cc.index('-o')+1]=str(out/'probe.o');run(cc,'compile')
 link=next(v['command'][2:] for v in old['commands'] if '-Wl,--start-group' in v['command']);link[1]=str(out/'probe.o');link[link.index('-o')+1]=str(out/'probe');run(link,'link');r['binary_sha256']=sha(out/'probe')
 base=Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs')
 for mode in ['B16_BANKED','U_WB16']:
  spec=json.loads((base/('convolutionSeparable_'+mode+'.json')).read_text());configs=[p['path'] for p in spec['configs']]
  for case in ['mask32','mask64','snapshot','stale_handle']:run([str(out/'probe'),case,*configs],mode+'_'+case)
 r['status']='EIGHT_FROZEN_PRODUCTION_CACHE_OR_TYPE_CHECKS_PASS_BYTE_VALUES_UNOBSERVABLE'
except BaseException as e:r.update(status='FAILED_RETAINED',error=repr(e));raise
finally:
 if lease:reg.release_build(lease,'lane3');r['released']=True
 (out/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'status':r['status'],'directory':str(out)}))
