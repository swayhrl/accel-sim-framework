from pathlib import Path
import json,subprocess,hashlib,re,shutil,time
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');S=R/'source/sdk/4.2';C=R/'compat_sdk42_v3';shutil.copytree(R/'compat_sdk42_v2',C)
p=C/'ep_cuda_helpers.h';s=p.read_text();s=s.replace('#include <helper_cuda.h>','#define gpuDeviceInit ep_helper_gpuDeviceInit\n#define gpuGetMaxGflopsDeviceId ep_helper_gpuGetMaxGflopsDeviceId\n#define findCudaDevice ep_helper_findCudaDevice\n#include <helper_cuda.h>\n#undef gpuDeviceInit\n#undef gpuGetMaxGflopsDeviceId\n#undef findCudaDevice');p.write_text(s)
p=C/'cutil_inline.h';s=p.read_text().replace('findCudaDevice(argc,','ep_helper_findCudaDevice(argc,').replace('#define cutGetMaxGflopsDeviceId gpuGetMaxGflopsDeviceId','#define cutGetMaxGflopsDeviceId ep_helper_gpuGetMaxGflopsDeviceId');p.write_text(s)
p=C/'shrUtils.h';p.write_text(p.read_text()+'\n#ifndef CLAMP\n#define CLAMP(v,lo,hi) ((v)<(lo)?(lo):((v)>(hi)?(hi):(v)))\n#endif\n')
rows=[]
for audit in json.loads((R/'manifests/SDK42_DENOMINATOR_AUDIT_V1.json').read_text()):
 n=audit['program'];d=S/n;row=dict(audit)
 if audit['graphics_dependency']:row['build_status']='GRAPHICS_DEPENDENCY_ISOLATED_INSTALL_QUEUE';rows.append(row);continue
 mk=(d/'Makefile').read_text().replace('\\\n',' ');flags=dict(re.findall(r'^\s*(\w+)\s*:?=\s*(.*)',mk,re.M));src=[]
 for var in ['CUFILES','CCFILES','CFILES']:
  for token in flags.get(var,'').split():
   if (d/token).is_file():src.append(str(d/token))
 if not src:row['build_status']='MAKEFILE_COMPLEX_OR_EMPTY_SOURCE_LIST';rows.append(row);continue
 cuda=Path('/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/cuda11.8');gcc='/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/gcc11/usr/bin/g++-11'
 cmd=[str(cuda/'bin/nvcc'),'-ccbin',gcc,'-O3','-lineinfo','-arch=sm_89','-I'+str(C),'-I'+str(R/'source/common/inc'),'-I'+str(R/'source/cuda-samples-11.8/Common')]+src+[str(R/'source/common/lib/libcutil_x86_64.a'),'-L'+str(cuda/'lib')]
 for flag,lib in [('USECUFFT','cufft'),('USECUBLAS','cublas'),('USECURAND','curand'),('USECUSPARSE','cusparse')]:
  if flags.get(flag)=='1':cmd+=['-l'+lib]
 cmd+=['-o',str(R/'bin'/('sdk42_v3_'+n))];t=time.time()
 try:cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);out=cp.stdout;rc=cp.returncode
 except subprocess.TimeoutExpired as e:out=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or '';rc='TIMEOUT'
 (R/'build'/('sdk42_'+n+'_compat_v3.log')).write_text(out)
 row.update(build_command=cmd,build_exit=rc,build_status='BUILD_PASS_NATIVE_PENDING' if rc==0 else 'BUILD_FAILED_LOGGED',build_seconds=time.time()-t,argv=[str(R/'bin'/('sdk42_v3_'+n))],cwd=str(d),native_timeout_sec=600,capture_timeout_sec=21600,capture_max_bytes=80*1024**3,version='4.2-source-host-adapter-v3',host_adapter='compat_sdk42_v3; QA/logging/device/error helper migration only; source kernels unchanged',correctness={'exit':0,'stdout_regex':'SDK42_HOST_ADAPTER_QA_PASSED'})
 if rc==0:
  row['binary_sha256']=hashlib.sha256(Path(row['argv'][0]).read_bytes()).hexdigest();cp2=subprocess.run(['/usr/local/cuda-12.8/bin/cuobjdump','--list-elf',row['argv'][0]],capture_output=True,text=True);row['cuobjdump_list_elf']=cp2.stdout;assert 'sm_89' in cp2.stdout
 rows.append(row);(R/'manifests/SDK42_ALL_BUILD_PROGRESS_V3.json').write_text(json.dumps(rows,indent=2)+'\n');print(n,rc,flush=True)
(R/'manifests/SDK42_ALL_COMPAT_V3.json').write_text(json.dumps(rows,indent=2)+'\n')
