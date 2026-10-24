#!/usr/bin/env python3
import pathlib,subprocess,json,time,os,hashlib
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');P=R/'assets/parboil_source_verified';T=R/'toolchains/cuda11.8'
(P/'common/Makefile.conf').write_text('CUDA_PATH='+str(T)+'\nCUDA_LIB_PATH='+str(T/'lib')+'\n')
(R/'bin').mkdir(exist_ok=True)
names=['bfs','cutcp','histo','lbm','mri-gridding','mri-q','sad','sgemm','spmv','stencil','tpacf'];summary=[]
for name in names:
 out=R/'attempts'/('parboil_'+name)/'build_attempt001';out.mkdir(parents=True,exist_ok=False)
 cwd=P/'benchmarks'/name;src=cwd/'src/cuda';bd=R/'build'/('parboil_'+name+'_attempt001');binary=R/'bin'/('parboil_'+name)
 cmd=['make','-j2','-f',str(P/'common/mk/Makefile'),'PARBOIL_ROOT='+str(P),'SRCDIR='+str(src),'BUILDDIR='+str(bd),'BIN='+str(binary),'CUDAHOME='+str(R/'compat_cuda118'),'CUDACC='+str(R/'compat_cuda118/bin/nvcc'),'CUDALINK='+str(R/'compat_cuda118/bin/nvcc'),'CUDA_PATH='+str(T),'CUDA_LIB_PATH='+str(T/'lib')]
 rec={'suite':'Parboil','version':'4e0fc548','program':name,'variant':'cuda','source_commit':'4e0fc54866546efa44fe93af57c9cef62f6c8eb9','command':cmd,'cwd':str(cwd),'start_unix':time.time(),'toolchain':'CUDA11.8.89+gcc11.5 (isolated), sm89'}
 try:
  with (out/'build.log').open('x') as f:
   p=subprocess.Popen(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);rec['pid']=p.pid
   try:p.wait(timeout=180)
   except subprocess.TimeoutExpired:
    import signal;os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10);rec['bounded_stop']='180s'
  rec['exit']=p.returncode;rec['status']='BUILD_PASS' if p.returncode==0 and binary.exists() else 'BUILD_FAIL_RETAINED'
  if rec['status']=='BUILD_PASS':
   rec.update(binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),binary_bytes=binary.stat().st_size)
   elf=subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-lelf',str(binary)],text=True);rec['actual_cubin_listing']=elf;(out/'cubin_listing.txt').write_text(elf)
 except Exception as e:rec['status']='BUILD_SETUP_HOLD';rec['error']=repr(e)
 rec['end_unix']=time.time();summary.append(rec);(out/'BUILD_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');(R/'control/PARBOIL_BUILD_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(name,rec['status'],rec.get('exit'),flush=True)

