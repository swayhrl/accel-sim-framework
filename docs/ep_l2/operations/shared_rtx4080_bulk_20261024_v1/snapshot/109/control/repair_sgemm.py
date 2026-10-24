#!/usr/bin/env python3
import pathlib,shutil,subprocess,json,hashlib,time
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');P=R/'assets/parboil_source_verified'
S=R/'adapted/parboil_sgemm_host_return_v1';S.mkdir(parents=True,exist_ok=False)
for p in (P/'benchmarks/sgemm/src/cuda').iterdir():
 if p.is_file():shutil.copy2(p,S/p.name)
p=S/'io.cc';s=p.read_text();anchor='v.pop_back(); // remove the duplicated last element\n'
assert s.count(anchor)==1;s=s.replace(anchor,anchor+'  return true; // Defined successful return; original fallthrough is C++ undefined behavior.\n');p.write_text(s)
out=R/'attempts/parboil_sgemm_host_io_return_fix/build_attempt001';out.mkdir(parents=True,exist_ok=False)
bd=R/'build/parboil_sgemm_hostfix_attempt001';bd.mkdir(exist_ok=False);b=R/'bin/parboil_sgemm_host_return_v1'
cmd=['make','-j2','-f',str(P/'common/mk/Makefile'),'PARBOIL_ROOT='+str(P),'SRCDIR='+str(S),'BUILDDIR='+str(bd),'BIN='+str(b),'CUDAHOME='+str(R/'compat_cuda118'),'CUDACC='+str(R/'compat_cuda118/bin/nvcc'),'CUDALINK='+str(R/'compat_cuda118/bin/nvcc'),'CUDA_PATH='+str(R/'toolchains/cuda11.8'),'CUDA_LIB_PATH='+str(R/'toolchains/cuda11.8/lib'),'default']
with (out/'build.log').open('x') as f:cp=subprocess.run(cmd,cwd=P/'benchmarks/sgemm',stdout=f,stderr=subprocess.STDOUT,timeout=180)
assert cp.returncode==0
tasks=json.loads((R/'control/PARBOIL_EXACT_INPUT_QUEUE_V2.json').read_text());new=[]
for q in tasks:
 if q['program']!='sgemm':continue
 q['variant']+='__host_io_return_defined_v1';q['argv'][0]=str(b);q['binary_sha256']=hashlib.sha256(b.read_bytes()).hexdigest()
 q['host_patch']={'file':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'change':'return true on successful read; no kernel changes','original_source_commit':'4e0fc54866546efa44fe93af57c9cef62f6c8eb9','canonical_failure':'SIGILL -4 before kernel launch; retained'}
 q['kernel_patch']='NONE';new.append(q)
(R/'control/PARBOIL_SGEMM_HOST_RETURN_REPAIR_QUEUE_V1.json').write_text(json.dumps(new,indent=2)+'\n')
only=[q for q in tasks if q['program']=='stencil' and q['variant']=='default_complete_official_input']
(R/'control/PARBOIL_STENCIL_DEFAULT_LATE_QUEUE_V1.json').write_text(json.dumps(only,indent=2)+'\n')
print('SGEMM_HOST_REPAIR_BUILD_PASS',len(new),'STENCIL_READY',len(only))

