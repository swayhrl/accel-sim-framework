from pathlib import Path
import json,subprocess,shlex,os,hashlib,resource,time
r=Path(__file__).parent;p=r.parent;s=r/'core_candidate'
base=Path(json.loads((p/'BUILD_LOCATION.json').read_text())['build'])
build=json.loads((r/'FINAL_INCREMENTAL_BUILD_RESULT.json').read_text());nb=Path(build['ELF']['path']).parent
cpu=nb/'new_install_cpu';cpu.mkdir(exist_ok=True);os.nice(15)
def ref(f):
 b=Path(f).read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
commands=json.loads((base/'compile_commands.json').read_text())
oldcore=p/'core_candidate'
e=next(e for e in commands if e['file'].endswith('/test_tvd_production.cc'))
a=shlex.split(e['command'])
a=[x.replace(str(oldcore),str(s)).replace('-g3','-g0').replace('-O3','-O0') for x in a]
a[a.index('-c')+1]=str(s/'tests/ep_l2/test_quota_clean_install_v4.cc')
obj=cpu/'test_new_frontend.o';a[a.index('-o')+1]=str(obj)
q=subprocess.run(a,cwd=str(cpu),capture_output=True,text=True,timeout=90)
(cpu/'compile.stdout').write_text(q.stdout);(cpu/'compile.stderr').write_text(q.stderr)
assert q.returncode==0,q.stderr
link=shlex.split((base/'gpgpu-sim/CMakeFiles/ep_l2_quota_handshake_v5.dir/link.txt').read_text())
new=[];i=0;exe=cpu/'clean_install.cpu'
while i<len(link):
 x=link[i]
 if x=='-o':new+=['-o',str(exe)];i+=2;continue
 if x.endswith('test_quota_handshake_v5.cc.o'):x=str(obj)
 elif x=='src/gpgpu-sim/libgpgpusim.a':x=build['gpgpusim_archive']['path']
 elif x=='src/cuda-sim/libptxsim.a':x=build['ptxsim_archive']['path']
 elif i and not x.startswith('-') and not Path(x).is_absolute():x=str(base/'gpgpu-sim'/x)
 new.append(x.replace(str(oldcore),str(s)));i+=1
q=subprocess.run(new,cwd=str(cpu),capture_output=True,text=True,timeout=60)
(cpu/'link.stdout').write_text(q.stdout);(cpu/'link.stderr').write_text(q.stderr);assert q.returncode==0,q.stderr
# Actual layout equality of reused objects, not a guess based on line counts.
size_source='#include <cstdio>\n#include "gpu-cache.h"\nint main(){printf("%zu %zu %zu\\n",sizeof(l2_cache),sizeof(ep_l2_tvd_directory<>),sizeof(ep_l2_quota_row_port));}\n'
sizes=[]
for label,core in [('old_0ab',p/'frontend_followup_v3/core_candidate'),('new',s)]:
 src=cpu/(label+'_sizes.cc');src.write_text(size_source);out=cpu/(label+'_sizes')
 cmd=['/usr/bin/c++','-O0','-g0','-std=c++17','-DCUDART_VERSION=12040','-I'+str(core/'src/gpgpu-sim'),'-I/root/data/dtc_main_20261023_v1/ae_fair_v1/toolchain/include',str(src),'-o',str(out)]
 z=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert z.returncode==0,z.stderr
 z=subprocess.run([str(out)],capture_output=True,text=True,timeout=10);assert z.returncode==0
 sizes.append({'label':label,'stdout':z.stdout.strip(),'compile_argv':cmd})
assert sizes[0]['stdout']==sizes[1]['stdout'],sizes
rows=[]
for k,case in [(1,'plus1'),(2,'plus1'),(1,'net0'),(2,'net0'),(1,'pin'),(2,'pin'),(1,'rollback'),(2,'rollback'),(1,'directory'),(1,'overflow')]:
 label='K'+str(k)+'_'+case;work=cpu/(label+'_work');work.mkdir(exist_ok=True)
 cmd=[str(exe),'/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/cpu_fixture_inputs/base.config',str(r/('cpu_K'+str(k)+'_cap'+('128' if case=='plus1' else '1')+'.config')),case]
 with (cpu/(label+'.stdout')).open('w') as out,(cpu/(label+'.stderr')).open('w') as err:
  q=subprocess.run(cmd,cwd=str(work),stdout=out,stderr=err,timeout=60)
 text=(cpu/(label+'.stdout')).read_text(errors='replace');passes=[x for x in text.splitlines() if x.startswith('PASS ')]
 row={'label':label,'argv':cmd,'returncode':q.returncode,'PASS':passes,'stdout':ref(cpu/(label+'.stdout')),'stderr':ref(cpu/(label+'.stderr'))}
 rows.append(row);print(json.dumps(row),flush=True)
 if q.returncode or not passes:
  (r/'NEW_INSTALL_CPU_ATTENTION.json').write_text(json.dumps({'rows':rows,'status':'FAIL_RETAINED_NO_APPLICATION'},indent=2)+'\n');raise SystemExit(1)
(r/'NEW_INSTALL_CPU_RECEIPT.json').write_text(json.dumps({'status':'PASS10_NEW_ORDINARY_CLEAN_INSTALL_CASES','compile_argv':a,'link_argv':new,'layout_equality':sizes,'rows':rows,'executable':ref(exe),'old12_3185_4_handshake_rerun':False,'scientific_models':0,'full_quota_qualified':False},indent=2)+'\n')
