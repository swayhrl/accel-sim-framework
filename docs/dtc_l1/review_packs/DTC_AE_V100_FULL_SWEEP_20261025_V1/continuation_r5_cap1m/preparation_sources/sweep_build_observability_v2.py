"""Isolated observational Framework build only; never executes a simulator."""
import pathlib,json,hashlib,subprocess,os,shutil,concurrent.futures,datetime,importlib.util,time
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');B=P('/root/data/dtc_main_20261023_v1/ae_fair_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');R=T/'telemetry_v2';FW=R/'framework';BUILD=R/'framework-build';BASE='cfd3ff56d7ba6642dab6c7710ec4f6065168174e';CORE='2e3bef4364e578cddd0e881c0baace2e51c55930'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+chr(10))
old_receipt=B.parent/'accel-sim-framework/docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1/BUILD_AND_TARGETED_CPU_QUALIFICATION.json';receipt=read(old_receipt)
assert receipt['framework_commit']==BASE and receipt['core_commit']==CORE and git(B/'framework','rev-parse','HEAD')==BASE and not git(B/'framework','status','--porcelain')
oldbinary=P(receipt['framework_binary']['path']);oldlib=P(receipt['core_library']['path']);originals={str(p):sha(p) for p in [oldbinary,oldlib,T/'DTC/bin/accel-sim.out']}
assert originals[str(oldbinary)]==receipt['framework_binary']['sha256'] and originals[str(oldlib)]==receipt['core_library']['sha256']
spec=importlib.util.spec_from_file_location('qualified_live_resource_read_only',T/'tools/sweep_native.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native);resources=native.resources({'cohort':'OBSERVATIONAL_CPU_BUILD'},False)
assert resources['physical_RAM_pass'] and resources['native_free_bytes']>resources['required_free_bytes']+1024**3
compiler=subprocess.check_output(['/usr/bin/g++','--version'],text=True).splitlines()[0];assert compiler==receipt['compiler']
assert not R.exists();R.mkdir();BUILD.mkdir();(R/'logs').mkdir()
write(R/'BUILD_ADMISSION.json',{'status':'CPU_ONLY_BUILD_ADMITTED','resources':resources,'additional_disk_upper_bound_bytes':1024**3,'compiler_processes_max':2,'address_space_per_compiler_bytes':4*1024**3,'scientific_starts':0,'old_build_receipt_sha256':sha(old_receipt)})
branch='hrl/dtc-v100-telemetry-cap-174new-20261025-v1';subprocess.run(['git','-C',str(B/'framework'),'worktree','add','-b',branch,str(FW),BASE],check=True)
header=FW/'gpu-simulator/ag7_policyb_progress.h';before=header.read_bytes();needle=b'static constexpr uint64_t kMaximumRecords = 8192;';assert before.count(needle)==1;header.write_bytes(before.replace(needle,b'static constexpr uint64_t kMaximumRecords = 1048576;'))
assert git(FW,'diff','--name-only')=='gpu-simulator/ag7_policyb_progress.h';subprocess.run(['git','-C',str(FW),'diff','--check'],check=True);subprocess.run(['git','-C',str(FW),'add','gpu-simulator/ag7_policyb_progress.h'],check=True);subprocess.run(['git','-C',str(FW),'commit','-m','Extend observational whole-input progress record budget only'],check=True)
head=git(FW,'rev-parse','HEAD');assert not git(FW,'status','--porcelain')
version=(B/'framework-build/accelsim_version.h').read_text();assert version.count(BASE)==1;(BUILD/'accelsim_version.h').write_text(version.replace(BASE,head))
commands=[]
for command in receipt['framework_compile_link_commands']:
 commands.append([arg.replace(str(B/'framework-build'),str(BUILD)).replace(str(B/'framework'),str(FW)) for arg in command])
available=sorted(os.sched_getaffinity(0));reserved=set(read(T/'control/HOST_CALIBRATION.json')['selected_model_CPUs'])|{1,2};cpus=[x for x in available if x not in reserved][:2];assert len(cpus)==2 and shutil.which('prlimit') and shutil.which('taskset')
def run(item):
 i,args=item;cpu=cpus[i%2];argv=['prlimit','--as='+str(4*1024**3),'--','taskset','-c',str(cpu),*args];log=R/'logs'/('command-'+str(i)+'.log');started=time.monotonic()
 with log.open('xb') as f:p=subprocess.Popen(argv,stdout=f,stderr=subprocess.STDOUT,cwd=FW);code=p.wait()
 row={'index':i,'CPU':cpu,'compiler_argv':args,'bounded_wrapper_argv':argv,'pid':p.pid,'returncode':code,'log_sha256':sha(log),'elapsed_seconds':time.monotonic()-started,'scientific_starts':0};write(R/'logs'/('command-'+str(i)+'.json'),row)
 if code:raise RuntimeError('Isolated compile failed;preserve log and inspect,no model was started:'+str(log))
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:closed=list(pool.map(run,enumerate(commands[:-1])) )
closed.append(run((len(commands)-1,commands[-1])))
receiver=N/'DTC/src/owner-control/docs/dtc_l1/review_packs/DTC_AG8R1_FINITE_RESUME_20261021_V1/prepared_ag8r1/telemetry_receiver.py';r=receiver.read_text();assert r.count('MAX_RECORDS = 8192')==1 and r.count('range(self.MAX_RECORDS + 1)')==1
newreceiver=R/'telemetry_receiver_cap1m.py';newreceiver.write_text(r.replace('MAX_RECORDS = 8192','MAX_RECORDS = 1048576').replace('range(self.MAX_RECORDS + 1)','range(8192 + 1)'))
assert originals=={p:sha(P(p)) for p in originals} and git(B/'framework','rev-parse','HEAD')==BASE and not git(B/'framework','status','--porcelain') and not git(FW,'status','--porcelain')
binary=BUILD/'accel-sim.out';dynamic=subprocess.check_output(['readelf','-d',str(binary)],text=True);(R/'DYNAMIC_LINKS.txt').write_text(dynamic)
result={'status':'ISOLATED_OBSERVATIONAL_FRAMEWORK_BUILD_PASS_NOT_SCIENCE_QUALIFIED','framework_worktree':str(FW),'framework_branch':branch,'framework_parent':BASE,'framework_commit':head,'framework_delta':git(FW,'diff',BASE,head,'--stat'),'only_source_file_changed':'gpu-simulator/ag7_policyb_progress.h','only_model_export_change':'kMaximumRecords8192->1048576;no simulation pointer/cache/timing/geometry changes','header_sha256':sha(header),'core_commit':CORE,'core_library':{'path':str(oldlib),'sha256':sha(oldlib),'unchanged':True},'framework_binary':{'path':str(binary),'sha256':sha(binary),'bytes':binary.stat().st_size},'compiler':compiler,'compiler_recipe_parent_sha256':sha(old_receipt),'commands':closed,'receiver':{'original_source':str(receiver),'original_sha256':sha(receiver),'new_source':str(newreceiver),'new_sha256':sha(newreceiver),'delta':'Only total record cap1048576;per-drain cap remains original8193. All other authentication/schema/clock/freshness/sequence/phase/terminal checks exact.'},'old_source_and_runtime_SHA_unchanged':originals,'compiled_simulator_executed':False,'scientific_starts':0,'next_action':'Qualify observational producer/receiver beyond8192 with CPU-only fixtures;preserve all old105spent attempts. Register per-unused-cell versioned effective specs/new runtime/source worktree under same356finite budget,all oldinput/config/performance options unchanged. Do not start newmodels until exact amendment qualification/publication/readback.','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
write(R/'BUILD_RESULT.json',result);write(T/'analysis/OBSERVATIONAL_CAP1M_BUILD_RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='commands'},indent=2))
