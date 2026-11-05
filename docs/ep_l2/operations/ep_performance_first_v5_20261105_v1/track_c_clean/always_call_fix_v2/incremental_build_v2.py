from pathlib import Path
import json,subprocess,concurrent.futures,os,time,shlex,shutil,hashlib,resource
r=Path(__file__).parent;p=r.parent;plan=json.loads((r/'INCREMENTAL_BUILD_PLAN.json').read_text());nb=Path(plan['new_build']);old=Path(json.loads((p/'BUILD_LOCATION.json').read_text())['build'])
os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(10*1024**3,10*1024**3))
started=time.time()
def ref(f):
 b=Path(f).read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def run(j):
 label=Path(j['source']).name
 with (nb/'logs'/(label+'.compile.stdout')).open('w') as out,(nb/'logs'/(label+'.compile.stderr')).open('w') as err:
  q=subprocess.run(j['argv'],cwd=j['cwd'],stdout=out,stderr=err,timeout=360)
 return dict(j,returncode=q.returncode,object_ref=ref(j['object']) if q.returncode==0 else None)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(run,plan['jobs']))
assert all(x['returncode']==0 for x in rows),rows
new_gpu=nb/'libgpgpusim.a';new_ptx=nb/'libptxsim.a'
shutil.copyfile(old/'gpgpu-sim/src/gpgpu-sim/libgpgpusim.a',new_gpu)
shutil.copyfile(old/'gpgpu-sim/src/cuda-sim/libptxsim.a',new_ptx)
subprocess.run(['ar','r',str(new_gpu),str(nb/'objects/gpu-cache.cc.o'),str(nb/'objects/l2cache.cc.o')],check=True)
subprocess.run(['ranlib',str(new_gpu)],check=True)
subprocess.run(['ar','r',str(new_ptx),str(nb/'objects/cuda-sim.cc.o')],check=True)
subprocess.run(['ranlib',str(new_ptx)],check=True)
cmd=shlex.split((old/'CMakeFiles/accel-sim.out.dir/link.txt').read_text())
new_core=str(r/'core_candidate');old_core=str(p/'core_candidate')
mapped=[];i=0
while i<len(cmd):
 x=cmd[i]
 if x=='-o':mapped+=['-o',str(nb/'accel-sim.out')];i+=2;continue
 if x=='gpgpu-sim/src/gpgpu-sim/libgpgpusim.a':x=str(new_gpu)
 elif x=='gpgpu-sim/src/cuda-sim/libptxsim.a':x=str(new_ptx)
 elif not x.startswith('-') and i and not Path(x).is_absolute():x=str(old/x)
 x=x.replace(old_core,new_core)
 mapped.append(x);i+=1
with (nb/'logs/link.stdout').open('w') as out,(nb/'logs/link.stderr').open('w') as err:
 q=subprocess.run(mapped,cwd=str(nb),stdout=out,stderr=err,timeout=120)
assert q.returncode==0,(nb/'logs/link.stderr').read_text()
result={'status':'PASS_NEW_PRIVATE_SOURCE_INCREMENTAL_COMPILE_RELINK_NOT_APPLICATION','rows':rows,'link_argv':mapped,'link_rc':q.returncode,'ELF':ref(nb/'accel-sim.out'),'gpgpusim_archive':ref(new_gpu),'ptxsim_archive':ref(new_ptx),'seconds':time.time()-started,'old_products_modified':False,'science_starts':0}
(r/'INCREMENTAL_BUILD_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'seconds':result['seconds'],'ELF':result['ELF']}),flush=True)
