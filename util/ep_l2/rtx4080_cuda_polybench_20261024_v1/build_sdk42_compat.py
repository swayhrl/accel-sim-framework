from pathlib import Path
import subprocess,json,hashlib,re,time
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');S=R/'source/sdk/4.2';C=R/'compat_sdk42';C.mkdir(exist_ok=False)
(C/'sdkHelper.h').write_text('#pragma once\n#include <cuda_runtime.h>\n#include <helper_functions.h>\n')
(C/'shrQATest.h').write_text('''#pragma once
#include <stdio.h>
#include <stdlib.h>
enum QAstatus {QA_FAILED=0,QA_PASSED=1,QA_WAIVED=2};
inline void shrQAStart(int,const char**){printf("SDK42_HOST_ADAPTER_QA_START\\n");}
inline void shrQAFinishExit(int,const char**,QAstatus s){printf("SDK42_HOST_ADAPTER_QA_%s\\n",s==QA_PASSED?"PASSED":s==QA_WAIVED?"WAIVED":"FAILED");exit(s==QA_PASSED?0:s==QA_WAIVED?2:1);}
''')
(C/'shrUtils.h').write_text('''#pragma once
#include <stdio.h>
#include <stdarg.h>
#include <helper_functions.h>
#define LOGCONSOLE 1
#define LOGFILE 2
#define MASTER 4
inline void shrLog(const char *f,...){va_list a;va_start(a,f);vprintf(f,a);va_end(a);}
inline void shrLogEx(int,int,const char *f,...){va_list a;va_start(a,f);vprintf(f,a);va_end(a);}
inline void shrSetLogFileName(const char*){}
#define shrCheckCmdLineFlag checkCmdLineFlag
''')
(C/'cutil_inline.h').write_text('''#pragma once
#include <cuda_runtime.h>
#include <cutil.h>
#include <helper_cuda.h>
#include <helper_functions.h>
#define cutilSafeCall checkCudaErrors
#define cutilCheckError(a) do {if(!(a)){fprintf(stderr,"CUTIL_CHECK_FAILED %s\\n",#a);exit(1);}} while(0)
#define cutilCheckMsg getLastCudaError
#define cutilDeviceInit(argc,argv) findCudaDevice(argc,argv)
#define cutilDeviceReset() checkCudaErrors(cudaDeviceReset())
#define cutilDeviceSynchronize() checkCudaErrors(cudaDeviceSynchronize())
#define cutilSafeMalloc(p) do {if(!(p)){fprintf(stderr,"HOST_MALLOC_FAILED\\n");exit(1);}} while(0)
''')
rows=[]
for n in ['BlackScholes','convolutionSeparable','fastWalshTransform','histogram','mergeSort','scalarProd','scan','sortingNetworks','transpose','vectorAdd']:
 d=S/n;mk=(d/'Makefile').read_text().replace('\\\n',' ');flags=dict(re.findall(r'^\s*(\w+)\s*:?=\s*(.*)',mk,re.M));src=[]
 for var in ['CUFILES','CCFILES','CFILES']:
  for token in flags.get(var,'').split():
   if (d/token).is_file():src.append(str(d/token))
 cmd=['/usr/local/cuda-12.8/bin/nvcc','-O3','-lineinfo','-arch=sm_89','-I'+str(C),'-I'+str(R/'source/common/inc'),'-I'+str(R/'source/cuda-samples-11.8/Common')]+src+[str(R/'source/common/lib/libcutil_x86_64.a'),'-o',str(R/'bin'/('sdk42_'+n))]
 cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);(R/'build'/('sdk42_'+n+'_compat_v1.log')).write_text(cp.stdout)
 row=dict(suite='CUDA SDK',version='4.2-source-host-adapter-v1',source_head='b059fdae25c2aabf737486aada743fca114469ce',program=n,sources=src,build_command=cmd,build_exit=cp.returncode,argv=[str(R/'bin'/('sdk42_'+n))],cwd=str(d),native_timeout_sec=600,native_status='NOT_RUN',host_adapter='compat_sdk42, logging/timers/QA/CUDA error and device helpers; kernel source unchanged')
 if cp.returncode==0:row['binary_sha256']=hashlib.sha256((R/'bin'/('sdk42_'+n)).read_bytes()).hexdigest()
 rows.append(row); print(n,cp.returncode,cp.stdout[-400:] if cp.returncode else '',flush=True)
(R/'manifests/SDK42_ORIGINAL_10_COMPAT_V1.json').write_text(json.dumps(rows,indent=2)+'\n')
