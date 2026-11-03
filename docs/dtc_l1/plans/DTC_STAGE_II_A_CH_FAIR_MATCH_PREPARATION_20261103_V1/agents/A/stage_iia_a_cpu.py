from pathlib import Path
import json,hashlib,subprocess,shutil,importlib.util
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/A');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/A');C=Path('/root/data/dtc_failure_repair_20261025_v1/core');R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fixture=O/'cpu_only/option_parser_fixture.cc';fixture.parent.mkdir(exist_ok=True);shutil.copyfile(A/'option_parser_fixture.cc',fixture)
exe=O/'cpu_only/option_parser_fixture';r=subprocess.run(['g++','-std=c++11','-O2','-I'+str(C/'src'),str(fixture),str(C/'src/option_parser.cc'),'-o',str(exe)],capture_output=True,text=True);assert r.returncode==0,r.stderr
spec=importlib.util.spec_from_file_location('g',R/'tools/l2_config_generator.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
rows=[]
for cell in ['CH','DH']:
 p=R/'control/specs/E2-DTCL2MLP-d984ea5475a581ad-{}-P0-V1.json'.format(cell) if False else R/'control/specs'/f'E2-DTCL2MLP-d984ea5475a581ad-{cell}-P0-V1.json'
 z=json.loads(p.read_text());base=[Path(c['path']).read_text()for c in z['configs']]
 for prof in ['P0','F128','F256']:
  txt,manifest=g.generate(base,prof);case=O/'cpu_only/cases'/f'{cell}_{prof}';case.mkdir(parents=True,exist_ok=True);paths=[]
  relevant={g.L2,g.FR,*g.FIXED,'-dram_seperate_write_queue_enable'}
  for i,t in enumerate(txt):
   s='\n'.join(l for l in t.splitlines()if l.split('#',1)[0].strip().split(' ',1)[0]in relevant)+'\n';p=case/f'config-{i}.config';p.write_text(s);paths.append(str(p))
  r=subprocess.run([str(exe),*paths],text=True,capture_output=True,timeout=10);assert r.returncode==0,(r.stdout,r.stderr);x=json.loads(r.stdout);assert x['cache_bytes']==10485760;assert x['entries']==192 and x['merge']==4 and x['miss_queue']==32;assert x['frfcfs']=={'P0':64,'F128':128,'F256':256}[prof]
  rows.append({'cell':cell,'profile':prof,'returncode':r.returncode,'actual':x,'fixture_input_files':[{'path':str(p),'sha256':H(p)}for p in paths]})
neg=[]
for name,key,value in [('reject_clock','-gpgpu_clock_domains','1410.0:1410.0:1410.0:1700.0'),('reject_L2capacity',g.L2,'S:128:128:32,L:B:m:L:L,A:192:4,32:0,32'),('reject_unlimited',g.FR,'0')]:
 p=O/'cpu_only'/f'{name}.config';p.write_text('\n'.join(f'{k} {v}'for k,v in g.effective_options(base).items()if k in relevant)+'\n'+key+' '+value+'\n');r=subprocess.run([str(exe),str(p)],text=True,capture_output=True,timeout=10,cwd=str(O/'cpu_only'));assert r.returncode!=0;neg.append({'name':name,'returncode':r.returncode,'expected':'reject','stderr':r.stderr[:700]})
# Binary/library only hashed, NEVER executed.
build=[]
for p in ['/root/data/dtc_failure_repair_20261025_v1/framework-build/accel-sim.out','/root/data/dtc_failure_repair_20261025_v1/core-build/libcudart.so']:
 build.append({'path':p,'sha256':H(p),'executed':False})
assert build[0]['sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d';assert build[1]['sha256']=='694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56'
x={'schema':'DTC_STAGE_IIA_CPU_ONLY_REAL_OPTION_PARSER_V1','status':'PASS','positive_cases':rows,'negative_cases':neg,'source':{'path':str(C/'src/option_parser.cc'),'sha256':H(C/'src/option_parser.cc')},'fixture_sha256':H(fixture),'fixture_executable_sha256':H(exe),'compile_returncode':0,'compile_stderr':r.stderr,'models_started':0,'model_cycles':0,'runtime_binary_and_library_reread':build,'limitations':['Links only option_parser.cc; exact cache sscanf format and fixed assertions mirrored, no full simulator/cache construction.','Successful parsing is not runtime memory/liveness/scientific execution qualification.','Simulator executable never invoked; negative fixtures CPU abort expected.']}
(O/'CPU_ONLY_PARSER_QUALIFICATION.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'status':'PASS','positive':len(rows),'negative':len(neg),'buildpins':build}))
