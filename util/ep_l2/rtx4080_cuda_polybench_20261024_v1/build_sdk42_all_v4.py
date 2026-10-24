from pathlib import Path
import json,subprocess,shutil,re,time,hashlib
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');C=R/'compat_sdk42_v4';shutil.copytree(R/'compat_sdk42_v3',C)
p=C/'cutil_inline.h';p.write_text(p.read_text()+'''\n#define cutilChooseCudaDevice(argc,argv) ep_helper_findCudaDevice(argc,(const char**)(argv))
#define cutilSafeCallNoSync checkCudaErrors
#define cutilCondition(a) cutilCheckError(a)
''')
p=C/'shrUtils.h';p.write_text(p.read_text()+'''\n#define shrFindFilePath sdkFindFilePath
inline bool shrGetCmdLineArgumenti(int argc,const char**argv,const char*key,int*out){if(!checkCmdLineFlag(argc,argv,key))return false;*out=getCmdLineArgumentInt(argc,argv,key);return true;}
inline bool shrGetCmdLineArgumentstr(int argc,const char**argv,const char*key,char**out){return getCmdLineArgumentString(argc,argv,key,out);}
''')
p=C/'shrQATest.h';s=p.read_text().replace('QAstatus s)','int s)');s+='\ntemplate<class T> inline void shrQAFinish(int a,T b,int s){printf("SDK42_HOST_ADAPTER_QA_%s\\n",s==QA_PASSED?"PASSED":s==QA_WAIVED?"WAIVED":"FAILED");}\n';p.write_text(s)
rows=[]
for old in json.loads((R/'manifests/SDK42_ALL_COMPAT_V3.json').read_text()):
 if old.get('build_exit')==0 or old['build_status'].startswith('GRAPHICS'):rows.append(old);continue
 d=Path(old['cwd']);n=old['program'];cmd=[x.replace(str(R/'compat_sdk42_v3'),str(C)).replace('/bin/sdk42_v3_','/bin/sdk42_v4_') for x in old['build_command']]
 cmd.insert(1,'-I'+str(d));cmd.insert(1,'-I'+str(d/'inc'))
 # Existing CUDA12.8 already contains the complete math-library and Thrust dev headers.
 if not old['texture_reference_legacy']:
  i=cmd.index('-ccbin');del cmd[i:i+2];cmd[0]='/usr/local/cuda-12.8/bin/nvcc';cmd=[x.replace('/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/cuda11.8/lib','/usr/local/cuda-12.8/lib64') for x in cmd]
 t=time.time()
 try:cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);out=cp.stdout;rc=cp.returncode
 except subprocess.TimeoutExpired as e:out=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or '';rc='TIMEOUT'
 (R/'build'/('sdk42_'+n+'_compat_v4.log')).write_text(out);row=dict(old);row.update(build_command=cmd,build_exit=rc,build_status='BUILD_PASS_NATIVE_PENDING' if rc==0 else 'BUILD_FAILED_LOGGED',build_seconds=time.time()-t,version='4.2-source-host-adapter-v4',argv=[str(R/'bin'/('sdk42_v4_'+n))])
 if rc==0:
  row['binary_sha256']=hashlib.sha256(Path(row['argv'][0]).read_bytes()).hexdigest();row['cuobjdump_list_elf']=subprocess.run(['/usr/local/cuda-12.8/bin/cuobjdump','--list-elf',row['argv'][0]],capture_output=True,text=True).stdout;assert 'sm_89' in row['cuobjdump_list_elf']
 rows.append(row);(R/'manifests/SDK42_ALL_BUILD_PROGRESS_V4.json').write_text(json.dumps(rows,indent=2)+'\n');print(n,rc,flush=True)
(R/'manifests/SDK42_ALL_COMPAT_V4.json').write_text(json.dumps(rows,indent=2)+'\n')
