from pathlib import Path
import os,json,subprocess,hashlib,time,re
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');gl=R/'toolchains/gl/usr';gl2=Path('/data/c16/rtx4080_suite_fill_20261024_v1/toolchains/opengl_headers/usr');env=dict(os.environ);env['CPATH']=':'.join([str(gl/'include'),str(gl2/'include')]);env['LIBRARY_PATH']=':'.join([str(gl/'lib/x86_64-linux-gnu'),str(gl2/'lib/x86_64-linux-gnu')]);env['LD_LIBRARY_PATH']=env['LIBRARY_PATH'];rows=[]
for old in json.loads((R/'manifests/SDK42_MIGRATION_V118_BUILDS_V3.json').read_text()):
 if not old.get('migration_graphics_dependency'):rows.append(old);continue
 d=Path(old['migration_path']);cmd=['make','-j2','CUDA_PATH=/usr/local/cuda-12.8','SMS=89','TARGET_ARCH=x86_64','GLPATH='+str(gl2/'lib/x86_64-linux-gnu'),'HEADER_SEARCH_PATH='+str(gl/'include')+' '+str(gl2/'include'),'GLLINK=-L'+str(gl/'lib/x86_64-linux-gnu')+' -L'+str(gl2/'lib/x86_64-linux-gnu')];t=time.time()
 try:cp=subprocess.run(cmd,cwd=d,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120);out=cp.stdout;rc=cp.returncode
 except subprocess.TimeoutExpired as e:out=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or '';rc='TIMEOUT'
 (R/'build'/('cuda118_'+old['program']+'_graphics_v3.log')).write_text(out);row=dict(old);row.update(migration_build_command=cmd,migration_build_exit=rc,migration_build_env={k:env[k] for k in ['CPATH','LIBRARY_PATH','LD_LIBRARY_PATH']},migration_build_seconds=time.time()-t,migration_status='BUILD_PASS_NATIVE_PENDING' if rc==0 else 'BUILD_FAILED_LOGGED');exe=d/d.name
 if exe.is_file():row.update(binary=str(exe),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),argv=[str(exe)],cwd=str(d),runtime_env={'LD_LIBRARY_PATH':env['LD_LIBRARY_PATH']},native_timeout_sec=300,capture_timeout_sec=21600,capture_max_bytes=80*1024**3)
 rows.append(row);(R/'manifests/SDK42_MIGRATION_V118_BUILD_GRAPHICS_PROGRESS_V3.json').write_text(json.dumps(rows,indent=2)+'\n');print(old['program'],rc,'actualELF',exe.is_file(),flush=True)
(R/'manifests/SDK42_MIGRATION_V118_BUILDS_V4.json').write_text(json.dumps(rows,indent=2)+'\n')
