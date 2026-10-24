import pathlib,json,re,os,subprocess,hashlib,time,concurrent.futures
R=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');P=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');off=R/'toolchains/sdk429_unpacked/sdk/C';C=R/'compat_sdk42_v14';out=R/'official429_failed28_build_v2';out.mkdir(exist_ok=False);baseline={t['program']:t for t in json.loads((R/'manifests/SDK42_ALL_COMPAT_V6.json').read_text())};failed=json.loads((R/'manifests/SDK429_OFFICIAL_FAILED28_BUILD_V2_TERMINAL.json').read_text())['records'];base={t['program']:baseline[t['program']] for t in failed if not t.get('binary_path')};cuda=P/'toolchains/cuda11.8';gcc=P/'toolchains/gcc11/usr/bin/g++-11';math=R/'toolchains/math_cuda118_v1/prefix/usr/local/cuda-11.8/targets/x86_64-linux';incs=[C,math/'include',R/'toolchains/cccl118/usr/local/cuda-11.8/targets/x86_64-linux/include',R/'source/common/inc',off/'common/inc',R/'source/cuda-samples-11.8/Common',R/'toolchains/gl/usr/include',P/'toolchains/opengl_headers/usr/include',R/'toolchains/mpi/usr/lib/x86_64-linux-gnu/openmpi/include',R/'toolchains/mpi/usr/lib/x86_64-linux-gnu/openmpi/include/openmpi'];libs=[cuda/'lib',math/'lib',R/'toolchains/gl/usr/lib/x86_64-linux-gnu',P/'toolchains/opengl_headers/usr/lib/x86_64-linux-gnu',R/'toolchains/mpi/usr/lib/x86_64-linux-gnu/openmpi/lib',R/'toolchains/mpi/usr/lib/x86_64-linux-gnu'];env=os.environ.copy();env.update(LD_LIBRARY_PATH=':'.join(map(str,libs)),LIBRARY_PATH=':'.join(map(str,libs)),OPAL_PREFIX=str(R/'toolchains/mpi/usr'))
def one(name):
 p=off/'src'/name;mk=(p/'Makefile').read_text().replace('\\\n',' ');mk='\n'.join(line.split('#',1)[0] for line in mk.splitlines());flags={}
 for k,op,v in re.findall(r'^[ \t]*(\w+)[ \t]*([+:?]?=)[ \t]*(.*)',mk,re.M):flags[k]=(flags.get(k,'')+' '+v) if op=='+=' else v
 sources=[];unresolved=[]
 for var in [k for k in flags if k.startswith(('CUFILES','CCFILES','CFILES'))]:
  for token in flags.get(var,'').split():
   q=p/token
   if q.is_file():sources.append(str(q))
   else:
    matches=[q for q in p.rglob(token) if q.is_file()] if '$' not in token else []
    if len(matches)==1:sources.append(str(matches[0]))
    else:unresolved.append({'variable':var,'token':token})
 rec={'program':name,'version':'official NVIDIA GPU Computing SDK4.2.9 full source','source_archive_sha256':'b6a53afcf8f8422b5075aa37cec6730b0b9896d50867ee9105da05d62e95b8bb','source_path':str(p),'source_files':[{'path':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in sorted(p.rglob('*')) if q.is_file() and q.suffix in ['.cpp','.cu','.c','.h','.cuh']],'makefile_sha256':hashlib.sha256((p/'Makefile').read_bytes()).hexdigest(),'unresolved_make_tokens':unresolved,'runtime_env':{'LD_LIBRARY_PATH':env['LD_LIBRARY_PATH'],'OPAL_PREFIX':env['OPAL_PREFIX']},'GPU_source_modified':False,'host_toolchain_adapter':str(C),'cpu_compile_receipts':[]}
 if not sources or unresolved:rec.update(exit='MAKE_SOURCE_RESOLUTION_PENDING');return rec
 graphics=bool(base[name].get('graphics_dependency'))
 if flags.get('USEPARAMGL')=='1':sources+=[str(off/'common/src/paramgl.cpp'),str(off/'common/src/param.cpp')]
 if graphics:sources.append(str(off/'common/src/rendercheck_gl.cpp'))
 for filename in ['bilateralFilter_gold.cpp','bmploader.cpp']:
  for src in [x for x in sources if pathlib.Path(x).name==filename]:
   obj=out/(name+'_'+filename+'.o');cmd=[str(gcc),'-O3','-c',src,'-o',str(obj)];z=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);rec['cpu_compile_receipts'].append({'command':cmd,'exit':z.returncode,'log':z.stdout,'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest() if obj.exists() else None});sources[sources.index(src)]=str(obj)
 binary=out/('sdk429_'+name);cmd=[str(cuda/'bin/nvcc'),'-ccbin',str(gcc),'-O3','-lineinfo','-arch=sm_89','-include',str(C/'cutil_inline.h'),'-I'+str(p),'-I'+str(p/'inc')]+['-I'+str(x) for x in incs]+['-L'+str(x) for x in libs]+sources+[str(R/'source/common/lib/libcutil_x86_64.a')]
 for flag,lib in [('USECUFFT','cufft'),('USECUBLAS','cublas'),('USECURAND','curand'),('USECUSPARSE','cusparse')]:
  if flags.get(flag)=='1':cmd+=['-l'+lib]
 if graphics:cmd+=['-lGL','-lGLU','-lglut','-lGLEW','-l:libX11.so.6']
 if name=='simpleMPI':cmd+=['-lmpi_cxx','-lmpi']
 
 if name=='matrixMulDynlinkJIT':
  ii=cmd.index('-include');del cmd[ii:ii+2]
 cmd+=['-o',str(binary)];log=out/(name+'.log');start=time.time()
 try:
  with log.open('w') as f:rc=subprocess.run(cmd,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
 except subprocess.TimeoutExpired:rc='TIMEOUT_180SEC'
 rec.update(command=cmd,exit=rc,wall_seconds=time.time()-start,log=str(log),graphics=graphics)
 if rc==0 and binary.exists():rec.update(binary_path=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
 (out/(name+'.json')).write_text(json.dumps(rec,indent=2)+'\n');print(name,rc,flush=True);return rec
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for rec in ex.map(one,sorted(base)):
  results.append(rec);(R/'manifests/SDK429_OFFICIAL_FAILED28_BUILD_V2.json').write_text(json.dumps(results,indent=2)+'\n')
(R/'manifests/SDK429_OFFICIAL_FAILED28_BUILD_V2_TERMINAL.json').write_text(json.dumps({'program_count':len(results),'ELF_count':sum(bool(x.get('binary_path')) for x in results),'records':results},indent=2)+'\n')
