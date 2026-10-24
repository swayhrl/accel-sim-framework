from pathlib import Path
import json,subprocess,re,hashlib,time
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');S=R/'source/cuda-samples-11.8';old=json.loads((R/'manifests/SDK42_DENOMINATOR_AUDIT_V1.json').read_text());modern={d.name.casefold():d for c in (S/'Samples').iterdir() if c.is_dir() for d in c.iterdir() if d.is_dir()};rows=[]
mapextra={'clock':'clock','MonteCarlo':'MonteCarloMultiGPU','Interval':'interval','radixSortThrust':'radixSortThrust','newdelete':'newdelete','template':'template'}
for x in old:
 key=mapextra.get(x['program'],x['program']).casefold();d=modern.get(key)
 row=dict(x);row['migration_version']='CUDA Samples v11.8';row['migration_head']='81992093d2b8c33cab22dbf6852c070c330f1715'
 if not d:row.update(migration_status='NO_SAME_NAME_SAMPLE_IN_V118');rows.append(row);print(x['program'],'NO_V118_MATCH',flush=True);continue
 row['migration_path']=str(d)
 txt='\n'.join(p.read_text(errors='replace') for p in d.glob('*') if p.suffix in ['.cu','.cpp','.h','.cuh']);mk=(d/'Makefile').read_text();gl=bool(re.search(r'(lGL|GLUT|glutMainLoop|<GL/|cudaGraphicsGL)',mk+'\n'+txt));row['migration_graphics_dependency']=gl
 if gl:row.update(migration_status='NEEDS_ISOLATED_GL_HEADERS_LIBS_HEADLESS_QA_VALIDATION');rows.append(row);print(x['program'],'GRAPHICS_QUEUE',flush=True);continue
 cmd=['make','-j2','CUDA_PATH=/usr/local/cuda-12.8','SMS=89','TARGET_ARCH=x86_64'];t=time.time()
 try:cp=subprocess.run(cmd,cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);out=cp.stdout;rc=cp.returncode
 except subprocess.TimeoutExpired as e:out=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or '');rc='TIMEOUT'
 (R/'build'/('cuda118_'+x['program']+'.log')).write_text(out)
 row.update(migration_build_command=cmd,migration_build_exit=rc,migration_build_seconds=time.time()-t,migration_status='BUILD_PASS_NATIVE_PENDING' if rc==0 else 'BUILD_FAILED_LOGGED')
 exe=d/d.name
 if exe.is_file():row.update(binary=str(exe),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),argv=[str(exe)],cwd=str(d),native_timeout_sec=300,capture_timeout_sec=21600,capture_max_bytes=80*1024**3)
 rows.append(row);(R/'manifests/SDK42_MIGRATION_BUILD_PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(x['program'],rc,flush=True)
(R/'manifests/SDK42_MIGRATION_V118_BUILDS.json').write_text(json.dumps(rows,indent=2)+'\n')
