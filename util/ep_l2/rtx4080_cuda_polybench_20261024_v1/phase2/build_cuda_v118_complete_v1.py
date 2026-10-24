import pathlib,json,os,subprocess,tarfile,time,hashlib,concurrent.futures
R=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');P=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');a=json.loads((R/'manifests/CUDA_V118_COMPLETE_SOURCE_DENOMINATOR_V2.json').read_text());base=R/'modern_complete_build_v1';base.mkdir(exist_ok=False)
with tarfile.open(R/'source/cuda-samples-v11.8.tar.gz') as tf:tf.extractall(base,filter='data')
root=base/'cuda-samples-11.8';control=R/'build/modern_complete_v1';control.mkdir(exist_ok=False)
incs=[R/'toolchains/gl/usr/include',P/'toolchains/opengl_headers/usr/include',R/'toolchains/egl/usr/include'];libs=[R/'toolchains/gl/usr/lib/x86_64-linux-gnu',P/'toolchains/opengl_headers/usr/lib/x86_64-linux-gnu',R/'toolchains/egl/usr/lib/x86_64-linux-gnu']
env=os.environ.copy();env['CPATH']=':'.join(map(str,incs));env['LIBRARY_PATH']=':'.join(map(str,libs));env['LD_LIBRARY_PATH']=':'.join(map(str,libs));env['LC_ALL']='C';env.pop('LD_PRELOAD',None)
def one(t):
 p=root/'Samples'/t['sample_relative_path'];log=control/(t['program']+'.log');cmd=['make','-j2','CUDA_PATH=/usr/local/cuda-12.8','SMS=89','GENCODE_FLAGS=-gencode arch=compute_89,code=sm_89','GLPATH='+str(libs[1]),'HEADER_SEARCH_PATH='+' '.join(map(str,incs)),'GLLINK='+' '.join('-L'+str(x) for x in libs)];start=time.time()
 try:
  with log.open('w') as f:r=subprocess.run(cmd,cwd=p,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
  rc=r.returncode
 except subprocess.TimeoutExpired:rc='TIMEOUT_900SEC'
 elfs=[]
 for q in p.iterdir():
  if q.is_file() and q.suffix not in ['.o','.so']:
   with q.open('rb') as f:magic=f.read(4)
   if magic==b'\x7fELF':elfs.append({'path':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size})
 rec={'program':t['program'],'sample_relative_path':t['sample_relative_path'],'command':cmd,'exit':rc,'wall_seconds':time.time()-start,'log':str(log),'elfs':elfs,'status':'BUILT_ACTUAL_ELF' if rc==0 and elfs else 'WAIVED_OR_BUILD_FAILED_NOT_PERMANENT_EXCLUSION','profile_or_platform_flags':t['profile_or_platform_flags']};(control/(t['program']+'.json')).write_text(json.dumps(rec,indent=2)+'\n');print(t['program'],rc,rec['status'],flush=True);return rec
items=[t for t in a['programs'] if not t['prior_73_mapped_source_covered']];results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for rec in ex.map(one,items):results.append(rec);(R/'manifests/CUDA_V118_COMPLETE_INCREMENTAL_BUILD_V1.json').write_text(json.dumps(results,indent=2)+'\n')
(R/'manifests/CUDA_V118_COMPLETE_INCREMENTAL_BUILD_V1_TERMINAL.json').write_text(json.dumps({'programs':len(results),'actual_ELF':sum(bool(x['elfs']) for x in results),'records':results},indent=2)+'\n')
