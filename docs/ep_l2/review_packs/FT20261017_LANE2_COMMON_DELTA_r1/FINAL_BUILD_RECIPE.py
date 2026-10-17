import sys,pathlib,subprocess,json,hashlib,os,time
root=pathlib.Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane2-common-r16')
official=pathlib.Path('/workspace/build/ep-l2-ft20261017-lane1-r0-1-buildfix-r2/gpgpu-sim')
build=pathlib.Path('/workspace/build/ep-l2-ft20261017-lane2-common-r16')
results=pathlib.Path('/workspace/results/ep_l2_ft20261016/lane2/common_delta_r16')
variant=sys.argv[1];changed=sys.argv[2:];out=build/variant;out.mkdir(exist_ok=False)
assert sum(f.stat().st_blocks*512 for f in build.rglob('*') if f.is_file()) + 40*1024**2 < 512*1024**2
assert os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize > 50*1024**3
record={'variant':variant,'core_source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'commands':[],
 'compiler':subprocess.check_output(['/usr/bin/c++','--version'],text=True).splitlines()[0],
 'assertions_enabled':True,'lease':json.loads((results/('BUILD_LEASE.json' if variant.startswith(('old_b1','new_b1')) else 'C1_C2_BUILD_LEASE.json')).read_text()),'source_files':{},'archives':{}}
libs=[official/x for x in ['libentrypoint.a','libcuda/libcuda.a','src/cuda-sim/libptxsim.a','src/gpgpu-sim/libgpgpusim.a','src/intersim2/libintersim.a','src/accelwattch/libaccelwattch.a']]
for p in libs:record['archives'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,label):
 record['commands'].append(cmd);start=time.time()
 with (results/(variant+'_'+label+'.log')).open('w') as log:
  p=subprocess.run(['/usr/bin/time','-v',*cmd],cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=180)
 record.setdefault('steps',[]).append({'label':label,'exit_code':p.returncode,'seconds':time.time()-start})
 (results/(variant+'_BUILD.json')).write_text(json.dumps(record,indent=2)+'\n')
 if p.returncode:print((results/(variant+'_'+label+'.log')).read_text()[-7000:]);sys.exit(p.returncode)
common=['/usr/bin/c++','-std=gnu++17','-O0','-g0','-fPIC','-DCUDART_VERSION=11080','-DDEBUG=0','-DTRACING_ON=1',
 '-I/usr/local/cuda-11.8/targets/x86_64-linux/include','-I'+str(root/'src'),'-I'+str(root/'libcuda'),'-I'+str(root/'src/gpgpu-sim'),'-I'+str(root/'src/accelwattch')]
objects=[]
sources=['tests/ep_l2/test_common_delta_r16.cc']+changed
for i,source in enumerate(sources):
 p=root/source;record['source_files'][source]=hashlib.sha256(p.read_bytes()).hexdigest();o=out/(str(i)+'.o');objects.append(str(o))
 run(common+(['-DGPGPUSIM_POWER_MODEL'] if source.startswith('src/') else [])+['-c',str(p),'-o',str(o)],'compile'+str(i))
binary=out/'common_delta.out'
run(['/usr/bin/c++',*objects,*(['-Wl,--strip-debug'] if 'compact' in variant else []),'-o',str(binary),'-Wl,--start-group',*[str(p) for p in libs],'-Wl,--end-group','-lz','-ldl','-lpthread','-lGLX','-lOpenGL','-lm'],'link')
record['binary']=str(binary);record['binary_sha256']=hashlib.sha256(binary.read_bytes()).hexdigest()
(results/(variant+'_BUILD.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'variant':variant,'source':record['core_source'],'binary_sha256':record['binary_sha256'],'seconds':sum(x['seconds'] for x in record['steps'])}))
