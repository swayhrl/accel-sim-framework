#!/usr/bin/env python3
import pathlib,subprocess,os,json,time,hashlib
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
S=R/'assets/gpu-app-collection/src/cuda/rodinia'
T=R/'toolchains/cuda11.8';compat=R/'compat_cuda118';(compat/'bin').mkdir(parents=True,exist_ok=True)
for name in ['include','nvvm']:
 p=compat/name
 if not p.exists():p.symlink_to(T/name)
for name in ['lib','lib64']:
 p=compat/name
 if not p.exists():p.symlink_to(T/'lib')
wr='''#!/usr/bin/env python3
import os,sys
args=[];skip=False
for x in sys.argv[1:]:
 if skip:skip=False;continue
 if x in ['-arch','--gpu-architecture','-code','--gpu-code','-gencode','--generate-code']:
  skip=True;continue
 if x.startswith(('-arch=','--gpu-architecture=','-code=','--gpu-code=','-gencode=','--generate-code=')):continue
 args.append(x)
nvcc='/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/cuda11.8/bin/nvcc'
os.execv(nvcc,[nvcc,'-arch=sm_89','-lineinfo','-ccbin','/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/gcc11/usr/bin/g++-11','-I/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/opengl_headers/usr/include','-I/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Common']+args)
'''
(compat/'bin/nvcc').write_text(wr);(compat/'bin/nvcc').chmod(0o755)
env=os.environ.copy();env.update(CUDA_INSTALL_PATH=str(compat),CUDA_HOME=str(compat),PATH=str(compat/'bin')+':/usr/local/cuda-12.8/bin:'+env['PATH'],LD_LIBRARY_PATH=str(T/'lib')+':'+env.get('LD_LIBRARY_PATH',''),NVIDIA_COMPUTE_SDK_LOCATON='/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source',NVIDIA_COMPUTE_SDK_LOCATION='/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source',GPUAPPS_ROOT=str(R/'assets/gpu-app-collection'),CUDA_VERSION_MAJOR='11',CUDA_VERSION_MINOR='8')
summary=[]
for version,name in [('3.1',x) for x in ['cfd','hybridsort','kmeans','leukocyte','mummergpu']]+[('2.0-ft','kmeans')]:
 cwd=S/version/('cuda/'+name if version=='3.1' else name);out=R/'attempts'/('rodinia_'+version.replace('.','_')+'_'+name)/'build_attempt003';out.mkdir(parents=True,exist_ok=False)
 cmd=['make','-j2','CUDA_INSTALL_PATH='+str(compat),'CUDA_DIR='+str(compat)]
 rec={'suite':'Rodinia','version':version,'program':name,'attempt':'build_attempt003','reason':'original CUDA11 texture API and missing build-only headers; kernel unchanged','cwd':str(cwd),'command':cmd,'source_head':'dad09cb0487845edc7524ded814c6cde9f0ef6a1','toolchain':'CUDA11.8.89+gcc11.5','start_unix':time.time()}
 with (out/'build.log').open('x') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);rec['pid']=p.pid
  try:p.wait(timeout=180)
  except subprocess.TimeoutExpired:
   import signal;os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10);rec['bounded_stop']='180s'
 rec.update(exit=p.returncode,status='BUILD_PASS' if p.returncode==0 else 'BUILD_FAIL_RETAINED',end_unix=time.time())
 (out/'BUILD_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');summary.append(rec)
 (R/'control/RODINIA_LEGACY_TOOLCHAIN_REPAIR_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(version,name,rec['status'],flush=True)

