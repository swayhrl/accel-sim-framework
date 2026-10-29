import argparse, pathlib, subprocess, time, hashlib, os, json, resource
O=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--family',choices=['module','geometry16'],required=True);a=p.parse_args()
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
rows=[];env=dict(os.environ,EPL2_DETACH_DIAG='0',EP_L2_EVENT_TIMELINE='0',EPL2_TAGPRESSURE_DIAG='0',EPL2_TAG_LIFETIME='0')
old=pathlib.Path('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/cpu_fixture_inputs')
jobs=[]
if a.family=='module':
 for T in ['T0','T1']:
  for obs in ['OFF','ON']:jobs.append((T+'_'+obs,[str(O/'test_mt_sector_counter'),obs,T]))
else:
 for T in [0,1]:
  for c in (['PRESSURE_IDENTITY'] if T==0 else ['PRESSURE_IDENTITY','SECTOR_MERGE_REORDER','RESPONSE_BACKPRESSURE']):jobs.append((f'G16_T{T}_{c}',[str(O/'test_mt_geometry16'),str(old/'base.config'),str(old/f'T{T}M1.config'),'2','16','0','0','1',str(old/'commandlist.g'),c,'16','8',str(T)]))
for name,cmd in jobs:
 t=time.monotonic();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30,cwd=O,env=env);log=O/(name+'.log');log.write_bytes(p.stdout);s=p.stdout.decode(errors='replace');rows.append(dict(name=name,argv=cmd,rc=p.returncode,seconds=time.monotonic()-t,log_sha256=hashlib.sha256(p.stdout).hexdigest(),lines=[x for x in s.splitlines() if x.startswith(('MT_CPU|','TAG_CAPACITY_SEMANTIC|','TAG_CAPACITY_CONTROL_PASS'))]));print(name,p.returncode)
filename='CPU_EXECUTION.json' if a.family=='module' else 'GEOMETRY16_CPU_EXECUTION.json';binary=O/('test_mt_sector_counter' if a.family=='module' else 'test_mt_geometry16')
(O/filename).write_text(json.dumps(dict(rows=rows,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),child_ru_maxrss_KiB=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,new_models=0,production_hook=False,scope='CPU only; module uses reference payload port; geometry16 uses real cache/subpartition with manual returns, no DRAM timing/app NI'),indent=2)+'\n')
assert all(x['rc']==0 for x in rows)
