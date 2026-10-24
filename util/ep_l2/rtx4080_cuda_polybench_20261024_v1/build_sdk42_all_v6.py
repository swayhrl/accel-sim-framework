from pathlib import Path
import json,subprocess,shutil,re,time,hashlib,os
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');C=R/'compat_sdk42_v6';shutil.copytree(R/'compat_sdk42_v5',C)
(C/'cutil_gl_inline.h').write_text('#pragma once\n#include <cutil_inline.h>\n#include <helper_cuda_gl.h>\n#define cutilGLDeviceInit(argc,argv) findCudaGLDevice(argc,(const char**)(argv))\n')
(C/'cudaHelper.h').write_text('#pragma once\n#include <sdkHelper.h>\n#include <cutil_inline.h>\n')
p=C/'shrQATest.h';p.write_text(p.read_text()+'\n#define shrQAFinishExit2 shrQAFinishExit\n')
p=C/'shrUtils.h';p.write_text(p.read_text()+'''\n#include <chrono>
inline double shrDeltaT(int i){static std::chrono::steady_clock::time_point t[16];if(i<0||i>=16)return 0.0;auto n=std::chrono::steady_clock::now();double x=std::chrono::duration<double>(n-t[i]).count();t[i]=n;return x;}
''')
M=R/'toolchains/cufft12_headers';M.mkdir(exist_ok=False)
for n in ['cufft.h','cufftXt.h','cufftXtDesc.h']:
 p=Path('/usr/local/cuda-12.8/targets/x86_64-linux/include')/n
 if p.exists():shutil.copy2(p,M/n)
rows=[];cuda=Path('/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/cuda11.8');gcc='/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/gcc11/usr/bin/g++-11';cccl=R/'toolchains/cccl118/usr/local/cuda-11.8/targets/x86_64-linux/include';gl=R/'toolchains/gl/usr';gl2=Path('/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/opengl_headers/usr')
for old in json.loads((R/'manifests/SDK42_ALL_COMPAT_V5.json').read_text()):
 if old.get('build_exit')==0:rows.append(old);continue
 n=old['program'];d=R/'source/sdk/4.2'/n;mk=(d/'Makefile').read_text().replace('\\\n',' ');flags={}
 for k,op,v in re.findall(r'^\s*(\w+)\s*([+:?]?=)\s*(.*)',mk,re.M):flags[k]=(flags.get(k,'')+' '+v) if op=='+=' else v
 src=[]
 for var in ['CUFILES','CCFILES','CFILES']:
  for token in flags.get(var,'').split():
   if (d/token).is_file():src.append(str(d/token))
   else:
    matches=[p for p in d.rglob(token) if p.is_file()] if '$' not in token else []
    if len(matches)==1:src.append(str(matches[0]))
 if not src:row=dict(old);row['build_status']='MAKEFILE_COMPLEX_OR_EMPTY_SOURCE_LIST';rows.append(row);continue
 if flags.get('USEPARAMGL')=='1':src+=[str(R/'source/cuda-samples-11.8/Common/paramgl.cpp')]
 cmd=[str(cuda/'bin/nvcc'),'-ccbin',gcc,'-O3','-lineinfo','-arch=sm_89','-I'+str(d),'-I'+str(d/'inc'),'-I'+str(C),'-I'+str(M),'-I'+str(R/'source/common/inc'),'-I'+str(R/'source/cuda-samples-11.8/Common'),'-I'+str(cccl),'-I'+str(gl/'include'),'-I'+str(gl2/'include')]+src+[str(R/'source/common/lib/libcutil_x86_64.a'),'-L/usr/local/cuda-12.8/lib64','-L'+str(gl/'lib/x86_64-linux-gnu'),'-L'+str(gl2/'lib/x86_64-linux-gnu')]
 for flag,lib in [('USECUFFT','cufft'),('USECUBLAS','cublas'),('USECURAND','curand'),('USECUSPARSE','cusparse')]:
  if flags.get(flag)=='1':cmd+=['-l'+lib]
 if old['graphics_dependency']:cmd+=['-lGL','-lGLU','-lglut','-lGLEW','-lX11']
 cmd+=['-o',str(R/'bin'/('sdk42_v6_'+n))];t=time.time();env=dict(os.environ);env['LD_LIBRARY_PATH']=':'.join([str(gl/'lib/x86_64-linux-gnu'),str(gl2/'lib/x86_64-linux-gnu'),'/usr/local/cuda-12.8/lib64'])
 try:cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120,env=env);out=cp.stdout;rc=cp.returncode
 except subprocess.TimeoutExpired as e:out=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or '';rc='TIMEOUT'
 (R/'build'/('sdk42_'+n+'_compat_v6.log')).write_text(out);row=dict(old);row.update(build_command=cmd,build_exit=rc,build_status='BUILD_PASS_NATIVE_PENDING' if rc==0 else 'BUILD_FAILED_LOGGED',build_seconds=time.time()-t,version='4.2-source-host-adapter-v6',argv=[str(R/'bin'/('sdk42_v6_'+n))],cwd=str(d),native_timeout_sec=600,capture_timeout_sec=21600,capture_max_bytes=80*1024**3,correctness={'exit':0,'stdout_regex':'SDK42_HOST_ADAPTER_QA_PASSED'},runtime_env={'LD_LIBRARY_PATH':env['LD_LIBRARY_PATH']},host_adapter='compat_sdk42_v6, original source kernels, GL/CUDA timer/QA helpers; optional library link CUDA12.8cuFFT/cublas explicitly differs from compiler11.8')
 if rc==0:
  row['binary_sha256']=hashlib.sha256(Path(row['argv'][0]).read_bytes()).hexdigest();row['cuobjdump_list_elf']=subprocess.run(['/usr/local/cuda-12.8/bin/cuobjdump','--list-elf',row['argv'][0]],capture_output=True,text=True).stdout;assert 'sm_89' in row['cuobjdump_list_elf']
 rows.append(row);(R/'manifests/SDK42_ALL_BUILD_PROGRESS_V6.json').write_text(json.dumps(rows,indent=2)+'\n');print(n,rc,flush=True)
(R/'manifests/SDK42_ALL_COMPAT_V6.json').write_text(json.dumps(rows,indent=2)+'\n')
