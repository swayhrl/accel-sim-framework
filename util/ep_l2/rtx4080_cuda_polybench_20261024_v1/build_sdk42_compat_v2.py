from pathlib import Path
import json,subprocess,hashlib,re
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');C=R/'compat_sdk42_v2';C.mkdir(exist_ok=False)
(C/'ep_cuda_helpers.h').write_text('''#pragma once
#define __getLastCudaError ep_helper_lastCudaError
#include <helper_cuda.h>
#undef __getLastCudaError
#ifndef ConvertSMVer2Cores
#define ConvertSMVer2Cores _ConvertSMVer2Cores
#endif
''')
(C/'sdkHelper.h').write_text('#pragma once\n#include <cuda_runtime.h>\n#include <helper_functions.h>\n#include "ep_cuda_helpers.h"\n')
(C/'shrQATest.h').write_text('''#pragma once
#include <stdio.h>
#include <stdlib.h>
enum QAstatus {QA_FAILED=0,QA_PASSED=1,QA_WAIVED=2};
template<class T> inline void shrQAStart(int,T){printf("SDK42_HOST_ADAPTER_QA_START\\n");}
template<class T> inline void shrQAFinishExit(int,T,QAstatus s){printf("SDK42_HOST_ADAPTER_QA_%s\\n",s==QA_PASSED?"PASSED":s==QA_WAIVED?"WAIVED":"FAILED");exit(s==QA_PASSED?0:s==QA_WAIVED?2:1);}
''')
(C/'shrUtils.h').write_text('''#pragma once
#include <stdio.h>
#include <stdarg.h>
#include <helper_functions.h>
#define LOGCONSOLE 1
#define LOGFILE 2
#define LOGBOTH 3
#define MASTER 4
inline void shrLog(const char *f,...){va_list a;va_start(a,f);vprintf(f,a);va_end(a);}
inline void shrLogEx(int,int,const char *f,...){va_list a;va_start(a,f);vprintf(f,a);va_end(a);}
inline void shrSetLogFileName(const char*){}
#define shrCheckCmdLineFlag(argc,argv,name) checkCmdLineFlag(argc,(const char**)(argv),name)
''')
(C/'cutil_inline.h').write_text('''#pragma once
#include <cuda_runtime.h>
#include <cutil.h>
#include "ep_cuda_helpers.h"
#include <helper_functions.h>
#define cutilSafeCall checkCudaErrors
#define cutilCheckError(a) do {if(!(a)){fprintf(stderr,"CUTIL_CHECK_FAILED %s\\n",#a);exit(1);}} while(0)
#define cutilCheckMsg(msg) ep_helper_lastCudaError(msg,__FILE__,__LINE__)
#define cutilDeviceInit(argc,argv) findCudaDevice(argc,(const char**)(argv))
#define cutilDeviceReset cudaDeviceReset
#define cutilDeviceSynchronize cudaDeviceSynchronize
#define cutGetMaxGflopsDeviceId gpuGetMaxGflopsDeviceId
#define cutilSafeMalloc(p) do {if(!(p)){fprintf(stderr,"HOST_MALLOC_FAILED\\n");exit(1);}} while(0)
''')
rows=[]
for old in json.loads((R/'manifests/SDK42_ORIGINAL_10_COMPAT_V1.json').read_text()):
 n=old['program'];cmd=[x.replace(str(R/'compat_sdk42'),str(C)).replace('/bin/sdk42_'+n,'/bin/sdk42_v2_'+n) for x in old['build_command']]
 cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);(R/'build'/('sdk42_'+n+'_compat_v2.log')).write_text(cp.stdout)
 row=dict(old);row.update(build_command=cmd,build_exit=cp.returncode,argv=[str(R/'bin'/('sdk42_v2_'+n))],version='4.2-source-host-adapter-v2',host_adapter='compat_sdk42_v2; host-only QA/logging/CUDA device/error helpers; kernels unchanged')
 if cp.returncode==0:
  row['binary_sha256']=hashlib.sha256(Path(row['argv'][0]).read_bytes()).hexdigest();row['correctness']={'exit':0,'stdout_regex':'SDK42_HOST_ADAPTER_QA_PASSED'}
  cp2=subprocess.run(['/usr/local/cuda-12.8/bin/cuobjdump','--list-elf',row['argv'][0]],capture_output=True,text=True);row['cuobjdump_list_elf']=cp2.stdout;assert 'sm_89' in cp2.stdout
 rows.append(row);print(n,cp.returncode,cp.stdout[-200:] if cp.returncode else '',flush=True)
(R/'manifests/SDK42_ORIGINAL_10_COMPAT_V2.json').write_text(json.dumps(rows,indent=2)+'\n')
