from pathlib import Path
import shutil,re,json,subprocess,hashlib,time,difflib
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');O=R/'source/polybench-gpu-1.0';A=R/'adapted/polybench-gpu-1.0';shutil.copytree(O,A)
H=A/'common/polybenchUtilFuncts.h';s=H.read_text();s=s.replace('//polybenchUtilFuncts.h','#include <math.h>\nstatic int ep_correctness_fail = 0;\n//polybenchUtilFuncts.h');s=s.replace('float percentDiff(double val1, double val2)\n{','float percentDiff(double val1, double val2)\n{\n if (!isfinite(val1) || !isfinite(val2)) return INFINITY;')
H.write_text(s)
wrapper='''#include <cuda_runtime.h>
#include <stdio.h>
#include <stdlib.h>
static inline cudaError_t ep_cuda_checked(cudaError_t e,const char *op,int line){if(e!=cudaSuccess){fprintf(stderr,"CUDA_ERROR line=%d op=%s err=%s\\n",line,op,cudaGetErrorString(e));exit(3);}return e;}
'''
for name in ['cudaMalloc','cudaMemcpy','cudaFree','cudaSetDevice','cudaGetDeviceProperties','cudaGetDeviceCount','cudaThreadSynchronize']:
 wrapper+='#define '+name+'(...) ep_cuda_checked('+name+'(__VA_ARGS__),"'+name+'",__LINE__)\n'
(R/'build/cuda_checks.h').write_text(wrapper)
rows=[];patches=[]
for d in sorted((A/'CUDA').iterdir()):
 if not d.is_dir():continue
 src=list(d.glob('*.cu'))[0];orig=O/'CUDA'/d.name/src.name;s=src.read_text()
 assert s.count(', fail);')==1,src
 s=s.replace(', fail);',', fail);\n ep_correctness_fail += fail;')
 pos=s.rfind('return 0;');assert pos>0;s=s[:pos]+'return ep_correctness_fail ? 2 : 0;'+s[pos+len('return 0;'):];src.write_text(s)
 patches.extend(difflib.unified_diff(orig.read_text().splitlines(True),s.splitlines(True),fromfile=str(orig),tofile=str(src)))
 cmd=['/usr/local/cuda-12.8/bin/nvcc','-O3','-lineinfo','-arch=sm_89','-include',str(R/'build/cuda_checks.h'),str(src),'-o',str(R/'bin'/(d.name+'_checked'))]
 t=time.time();cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);(R/'build'/(d.name+'_checked.log')).write_text(cp.stdout)
 defs=dict(re.findall(r'^\s*#define\s+(NI|NJ|NK|NL|NM|N|M|NX|NY|NZ|tmax)\s+(\d+)',s,re.M))
 row=dict(suite='PolyBench/GPU',version='1.0',source_head='dad09cb0487845edc7524ded814c6cde9f0ef6a1',program=d.name,variant='source_default_complete_host_checks_v2',source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),original_source_sha256=hashlib.sha256(orig.read_bytes()).hexdigest(),parameters=defs,argv=[str(R/'bin'/(d.name+'_checked'))],cwd=str(d),build_command=cmd,build_exit=cp.returncode,build_seconds=time.time()-t,native_status='NOT_RUN',input_identity='deterministic original init function; no external input',native_timeout_sec=600,capture_timeout_sec=21600,capture_max_bytes=80*1024**3,correctness={'returncode':0,'stdout_regex':'Non-Matching CPU-GPU Outputs Beyond Error Threshold of .* Percent: 0','nan_inf':'reject on compared output','all_cuda_api_checked':True},kernel_patch='NONE; host validation and error handling only')
 if cp.returncode==0:row['binary_sha256']=hashlib.sha256((R/'bin'/(d.name+'_checked')).read_bytes()).hexdigest()
 rows.append(row);print(d.name,cp.returncode,defs,flush=True)
patches.extend(difflib.unified_diff((O/'common/polybenchUtilFuncts.h').read_text().splitlines(True),H.read_text().splitlines(True),fromfile='original/common/polybenchUtilFuncts.h',tofile='adapted/common/polybenchUtilFuncts.h'))
(R/'build/POLY_HOST_CHECKS.patch').write_text(''.join(patches));(R/'manifests/POLYBENCH_QUEUE_V2.json').write_text(json.dumps(rows,indent=2)+'\n')
