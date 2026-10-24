from pathlib import Path
import subprocess,json,hashlib,re,time
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1')
rows=[]
for d in sorted((R/'source/polybench-gpu-1.0/CUDA').iterdir()):
 if not d.is_dir():continue
 files=list(d.glob('*.cu'))
 if len(files)!=1:raise RuntimeError(d)
 src=files[0];p=d.name
 cmd=['/usr/local/cuda-12.8/bin/nvcc','-O3','-lineinfo','-arch=sm_89',str(src),'-o',str(R/'bin'/p)]
 t=time.time();cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
 (R/'build'/(p+'.log')).write_text(cp.stdout)
 defs=dict(re.findall(r'^#define\s+(NI|NJ|NK|NL|NM|N|M|NX|NY|NZ|tmax)\s+(\d+)\s*$',src.read_text(),re.M))
 row=dict(suite='PolyBench/GPU',version='1.0 gpu-app-collection dad09cb0487845edc7524ded814c6cde9f0ef6a1',program=p,variant='source_default_complete',source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),parameters=defs,argv=[str(R/'bin'/p)],cwd=str(d),build_command=cmd,build_exit=cp.returncode,build_seconds=time.time()-t,native_status='NOT_RUN',input_identity='deterministic source init function; no external input')
 if cp.returncode==0:row['binary_sha256']=hashlib.sha256((R/'bin'/p).read_bytes()).hexdigest()
 rows.append(row); print(p,cp.returncode,defs,flush=True)
(R/'manifests/POLYBENCH_BUILD_V1.json').write_text(json.dumps(rows,indent=2)+'\n')
