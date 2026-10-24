from pathlib import Path
import json,re,subprocess,hashlib,os,time
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');S=R/'toolchains/sdk429_unpacked/sdk/C';C=R/'compat_sdk42_v6';cuda=Path('/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/cuda11.8');gcc='/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/gcc11/usr/bin/g++-11';rows=[]
for n in ['MonteCarloMultiGPU','deviceQuery','deviceQueryDrv','matrixMulDrv','ptxjit','simplePrintf','simpleTextureDrv','threadMigration','vectorAddDrv']:
 d=S/'src'/n;mk=(d/'Makefile').read_text().replace('\\\n',' ');flags={}
 for k,op,v in re.findall(r'^\s*(\w+)\s*([+:?]?=)\s*(.*)',mk,re.M):flags[k]=(flags.get(k,'')+' '+v) if op=='+=' else v
 src=[]
 for key in ['CUFILES','CUFILES_sm_10','CUFILES_sm_13','CCFILES','CFILES']:
  for token in flags.get(key,'').split():
   if (d/token).is_file() and str(d/token) not in src:src.append(str(d/token))
 inc=['-I'+str(d),'-I'+str(C),'-I'+str(R/'source/common/inc'),'-I'+str(R/'source/cuda-samples-11.8/Common'),'-I'+str(S/'common/inc'),'-I'+str(S.parent/'shared/inc'),'-I'+str(R/'toolchains/cccl118/usr/local/cuda-11.8/targets/x86_64-linux/include')]
 inputs=R/'official429_extra_inputs'/n;inputs.mkdir(parents=True,exist_ok=False)
 if (d/'data').is_dir():
  import shutil
  for p in (d/'data').rglob('*'):
   if p.is_file():z=inputs/p.relative_to(d/'data');z.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,z)
 ptxlogs=[]
 for token in flags.get('PTXFILES','').split():
  if not (d/token).is_file():continue
  dst=inputs/(Path(token).stem+'.ptx');cmd=[str(cuda/'bin/nvcc'),'-ccbin',gcc,'-O3','-lineinfo','-arch=compute_89','-ptx']+inc+[str(d/token),'-o',str(dst)];cp=subprocess.run(cmd,capture_output=True,text=True,timeout=120);ptxlogs.append({'cmd':cmd,'exit':cp.returncode,'log':cp.stdout+cp.stderr})
 cmd=[str(cuda/'bin/nvcc'),'-ccbin',gcc,'-O3','-lineinfo','-arch=sm_89']+inc+src+[str(R/'source/common/lib/libcutil_x86_64.a'),'-L/usr/local/cuda-12.8/lib64','-lcuda','-lpthread','-o',str(R/'bin'/('sdk429_'+n))];cp=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(R/'build'/('sdk429_extra_'+n+'.log')).write_text(cp.stdout+cp.stderr);row={'program':n,'suite':'CUDA SDK','version':'4.2.9-official-source-host-adapter-v6','release_installer_sha256':'b6a53afcf8f8422b5075aa37cec6730b0b9896d50867ee9105da05d62e95b8bb','build_command':cmd,'build_exit':cp.returncode,'ptx_builds':ptxlogs,'argv':[str(R/'bin'/('sdk429_'+n))],'source_files':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in d.rglob('*') if p.is_file() and p.suffix in ['.cu','.cpp','.cuh','.h']],'input_files':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in inputs.rglob('*') if p.is_file()],'runtime_links':[{'name':'data','target':str(inputs)}],'runtime_env':{'LD_LIBRARY_PATH':'/usr/local/cuda-12.8/lib64'},'correctness':{'exit':0,'stdout_regex':'SDK42_HOST_ADAPTER_QA_PASSED'},'native_timeout_sec':600,'capture_timeout_sec':21600,'capture_max_bytes':80*1024**3,'task_id':'sdk429_extra_'+n,'variant':'official429_default_complete','workload_kind':'DEVICE_QUERY_API_ONLY_NO_KERNEL' if n in ['deviceQuery','deviceQueryDrv'] else 'FINITE_GPU_WORKLOAD','capture_eligibility':'NO_SASS_EXPECTED_DEVICE_QUERY' if n in ['deviceQuery','deviceQueryDrv'] else 'PENDING_NATIVE_AND_LOADED_CODE_IDENTITY'}
 if cp.returncode==0:row['binary_sha256']=hashlib.sha256(Path(row['argv'][0]).read_bytes()).hexdigest()
 rows.append(row);print(n,cp.returncode,'PTX',[x['exit'] for x in ptxlogs],flush=True)
(R/'manifests/SDK429_OFFICIAL_EXTRA9_BUILD_V1.json').open('x').write(json.dumps(rows,indent=2)+'\n')
