#!/usr/bin/env python3
import pathlib,os,json,subprocess,time,hashlib
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
S=R/'assets/gpu-app-collection/src/cuda/rodinia'
compat=R/'compat_cuda';(compat/'bin').mkdir(parents=True,exist_ok=True)
for name in ['include','lib64','lib','nvvm','targets']:
 p=compat/name
 if not p.exists():p.symlink_to('/usr/local/cuda-12.8/'+name)
wrapper='''#!/usr/bin/env python3
import os,sys
args=[];skip=False
for x in sys.argv[1:]:
 if skip:skip=False;continue
 if x in ['-arch','--gpu-architecture','-code','--gpu-code','-gencode','--generate-code']:
  skip=True;continue
 if x.startswith(('-arch=','--gpu-architecture=','-code=','--gpu-code=','-gencode=','--generate-code=')):continue
 args.append(x)
os.execv('/usr/local/cuda-12.8/bin/nvcc',['nvcc','-arch=sm_89','-lineinfo']+args)
'''
(compat/'bin/nvcc').write_text(wrapper);(compat/'bin/nvcc').chmod(0o755)
env=os.environ.copy();env.update(CUDA_INSTALL_PATH=str(compat),CUDA_HOME=str(compat),PATH=str(compat/'bin')+':/usr/local/cuda-12.8/bin:'+env['PATH'],LD_LIBRARY_PATH='/usr/local/cuda-12.8/lib64:'+env.get('LD_LIBRARY_PATH',''))
# Exact family directories only; split implementations remain explicit build children.
families=['b+tree','backprop','bfs','cfd','dwt2d','gaussian','heartwall','hotspot','hotspot3D','huffman','hybridsort','kmeans','lavaMD','leukocyte','lud','mummergpu','myocyte','nn','nw','particlefilter','pathfinder','srad','streamcluster']
legacy=['backprop','bfs','heartwall','hotspot','kmeans','lud','nn','nw','pathfinder','srad','streamcluster']
summary=[]
for version,items in [('3.1',families),('2.0-ft',legacy)]:
 for name in items:
  ident='rodinia_'+version.replace('.','_')+'_'+name.replace('+','p')
  out=R/'attempts'/ident/'build_attempt001';out.mkdir(parents=True,exist_ok=False)
  cwd=S/version/('cuda/'+name if version=='3.1' else name)
  cmd=['make','-j2','CUDA_INSTALL_PATH='+str(compat),'CUDA_DIR='+str(compat)]
  rec={'suite':'Rodinia','version':version,'program':name,'attempt':'build_attempt001','cwd':str(cwd),'command':cmd,'source_commit':'dad09cb0487845edc7524ded814c6cde9f0ef6a1','cuda_wrapper':str(compat/'bin/nvcc'),'start_unix':time.time()}
  try:
   with (out/'build.log').open('w') as f:
    p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    rec['pid']=p.pid
    try:p.wait(timeout=180)
    except subprocess.TimeoutExpired:
     import signal;os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10);rec['bounded_stop']='180s'
   rec['exit']=p.returncode;rec['status']='BUILD_PASS' if p.returncode==0 else 'BUILD_FAIL_RETAINED'
  except Exception as e:rec['status']='BUILD_ERROR_RETAINED';rec['error']=repr(e)
  rec['end_unix']=time.time()
  binaries=[]
  for path in cwd.rglob('*'):
   if path.is_file() and os.access(path,os.X_OK) and path.stat().st_size>1000:
    with path.open('rb') as f:magic=f.read(4)
    if magic==b'\x7fELF':binaries.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  rec['elf_binaries']=binaries;summary.append(rec)
  (out/'BUILD_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
  (R/'control/RODINIA_BUILD_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
  print(version,name,rec['status'],len(binaries),flush=True)

