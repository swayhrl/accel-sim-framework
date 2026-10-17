"""r19 narrow production check; reuse immutable official native objects, no CMake.

Stage D4 publishes first; Q4 uses the same small fixture executable afterward.
Application execution/current V2 acceptance belongs only to Lane5.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,re,resource,shlex,shutil,subprocess,sys
REPO=Path(__file__).resolve().parents[4]
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-fixed-r1')
FW=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261017-lane1-a1-fixed-r1')
NATIVE=Path('/workspace/build/ep-l2-ft20261017-lane1-a1-fixed-r1')
BUILD=Path('/workspace/build/ep-l2-ft20261017-lane1-headroom-r19-r4')
BINARY=Path('/root/share/workspace_migrated_20260905/results/ep_l2_ft20261016/lane1/r0_1_a1_b1_release_20261017_r1/binaries/accel-sim.out')
BINARY_SHA='23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee'
SOURCE_SHA='7b8e6ac70b8fe0f1bd37efca11acb5284938825d'
FRAMEWORK_SHA='9bd17f9db3e8cbbc3fdad7283d1e292918546fd5'
ROOT=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1'
CONFIGS=REPO/'tests/ep_l2/ft20261016/headroom_r19'
ENV={'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
LIMITS={'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30}
Q4={'-gpgpu_dram_partition_queues':'64:512:256:64','-gpgpu_frfcfs_dram_sched_queue_size':'512','-gpgpu_dram_return_queue_size':'768'}
D4={**Q4,'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:3400.0'}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');tmp.replace(p)
def content_hash(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def head(p):return subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()
def options(log):
 text=Path(log).read_text();s=text.split('R19_NATIVE_EFFECTIVE_OPTIONS_BEGIN\n',1)[1].split('R19_NATIVE_EFFECTIVE_OPTIONS_END',1)[0]
 result={}
 for line in s.splitlines():
  pair=line.split('#',1)[0].strip().split(None,1)
  if pair and pair[0].startswith('-'):result[pair[0]]=pair[1].strip() if len(pair)>1 else ''
 return result

def authored_options(paths):
 result={}
 for path in paths:
  tokens=shlex.split(Path(path).read_text(),comments=True);assert len(tokens)%2==0
  for key,value in zip(tokens[::2],tokens[1::2]):assert key.startswith('-') and key!='-config';result[key]=value
 return result

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--regime',choices=['D4','Q4'],required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--build-fixture',action='store_true');args=parser.parse_args()
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());assert digest(client['registry_client'])==client['registry_client_sha256'];sys.path.insert(0,str(Path(client['registry_client']).parent))
 from registry import Registry,local_resources,process_identity,ACTIVE
 spec=importlib.util.spec_from_file_location('frozen_guard',FW/'util/ep_l2/ft_lane1/build_r0_1.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 registry=Registry(client['canonical_root']);baseline=json.loads((ROOT/'BASELINE_CONTRACT_R0_1_A1_B1_V1.json').read_text())
 assert head(CORE)==SOURCE_SHA and head(FW)==FRAMEWORK_SHA and digest(BINARY)==BINARY_SHA
 for p in [CORE,FW]:assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=p)
 fixture=Path(__file__).with_name('production_probe.cc');r={'schema':'EPL2_LANE1_R19_AFFECTED_CHECKS_V1','status':'PREFLIGHT','regime':args.regime,'runtime_core':SOURCE_SHA,'runtime_framework':FRAMEWORK_SHA,'official_binary':str(BINARY),'official_binary_sha256':BINARY_SHA,'tool_source_commit':head(REPO),'fixture_source_sha256':digest(fixture),'runner_sha256':digest(__file__),'runtime_code_recompiled':False,'full_simulator_builds':0,'application_runs':0,'independent_qualification':False,'affected_scope':'One real production partition/two subpartitions, detailed DRAM and native clock scheduler; remaining62 slices/config capacity saturation are not dynamically tested here',**LIMITS,'tests':[]}
 def save():write(out/'PRODUCTION_CHECK_RECEIPT.json',r)
 def safe():
  now=local_resources();assert now['disk_free_bytes']>=50*2**30 and now['available_memory_bytes']-4*2**30>=64*2**30
  fs=os.statvfs('/root/share');assert fs.f_bavail*fs.f_frsize>=40*2**30
  return now
 def run(cmd,name):
  safe();wrapped=['/usr/bin/time','-v',*cmd]
  return guard.run_owned(wrapped,name,out,dict(os.environ,**ENV,PYTHONDONTWRITEBYTECODE='1'),r,save,local_resources,process_identity,180)
 r['resources_before']=safe();lease=None
 try:
  lease=registry.build_lease('lane1',cpu=1,memory=4*2**30);r['lease_id']=lease;save()
  if args.build_fixture:
   assert not BUILD.exists();BUILD.mkdir(parents=True);flags={}
   for line in (NATIVE/'gpgpu-sim/CMakeFiles/ep_l2_ft_a1.dir/flags.make').read_text().splitlines():
    if line.startswith('CXX_'):k,v=line.split(' = ',1);flags[k]=v
   inc=[]
   for line in (NATIVE/'CMakeFiles/accel-sim.out.dir/flags.make').read_text().splitlines():
    if line.startswith('CXX_INCLUDES = '):inc=shlex.split(line.split(' = ',1)[1])
   obj=BUILD/'production_probe.o';cmd=['/usr/bin/c++',*shlex.split(flags['CXX_DEFINES']),*inc,*shlex.split(flags['CXX_INCLUDES']),'-O0','-g0','-fPIC','-std=gnu++17','-c',str(fixture),'-o',str(obj)]
   run(cmd,'compile_fixture')
   libs=[NATIVE/'gpgpu-sim'/p for p in ['libentrypoint.a','libcuda/libcuda.a','src/cuda-sim/libptxsim.a','src/gpgpu-sim/libgpgpusim.a','src/intersim2/libintersim.a','src/accelwattch/libaccelwattch.a']]+[NATIVE/'trace-driven/libtrace-driven.a',NATIVE/'trace-parser/libtrace-parser.a']
   arches={str(p):digest(p) for p in libs};run(['/usr/bin/c++',str(obj),'-o',str(BUILD/'production_probe'),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'link_fixture')
   write(BUILD/'BUILD_IDENTITY.json',{'fixture_source_sha256':digest(fixture),'fixture_source_commit':r['tool_source_commit'],'archives_sha256':arches,'binary_sha256':digest(BUILD/'production_probe'),'runtime_source':SOURCE_SHA,'runtime_framework':FRAMEWORK_SHA,'actual_compile_and_link':r['commands'],'runtime_recompiled':False})
  binding=json.loads((BUILD/'BUILD_IDENTITY.json').read_text());assert binding['fixture_source_sha256']==digest(fixture) and binding['binary_sha256']==digest(BUILD/'production_probe')
  for p,h in binding['archives_sha256'].items():assert digest(p)==h
  r['fixture_build_identity']=binding;manifest={'schema':'EP_L2_HEADROOM_CONFIG_MANIFEST_V1','experiment_id':'EPL2_DOWNSTREAM_HEADROOM_R19','regime':args.regime,'runtime_core':SOURCE_SHA,'runtime_framework':FRAMEWORK_SHA,'official_binary_sha256':BINARY_SHA,'runtime_code_changed':False,'allowed_overlay_values':D4 if args.regime=='D4' else Q4,'all_other_effective_parameters_must_equal_H0_same_mode':True,'semantic_scope':'Detailed DRAM; all base integer timings/banks/atom/mapping/cache resources unchanged; shared credit1279 vs319 is extra cost, D4 retains fixed100GPUcycles','identity':{'core_source_commit':SOURCE_SHA,'framework_source_commit':FRAMEWORK_SHA,'binary_sha256':BINARY_SHA},'status':'PRODUCER_CHECKS_ONLY_NOT_INDEPENDENTLY_QUALIFIED','modes':{}}
  overlay_paths=[CONFIGS/'q4.config']+([CONFIGS/'d4_clock.config'] if args.regime=='D4' else [])
  (out/'overlays').mkdir();manifest['overlays']=[]
  for p in overlay_paths:
   dest=out/'overlays'/p.name;shutil.copy2(p,dest);os.chmod(dest,0o444);manifest['overlays'].append({'path':str(dest),'sha256':digest(dest)})
  for mode in ['B16_BANKED','U_WB16']:
   original=baseline['modes'][mode];base=[Path(v['path']) for v in original['configs']]
   configs=base+[CONFIGS/'q4.config']+([CONFIGS/'d4_clock.config'] if args.regime=='D4' else [])
   # One new H0 short production control per mode establishes native option
   # dump/clock scheduler equivalence. It is not a full application replay.
   cached=BUILD/f'H0_{mode}_EFFECTIVE.json'
   if not cached.exists():
    rec=run([str(BUILD/'production_probe'),'H0',*map(str,base)],f'H0_{mode}')
    log=Path(rec['log']);assert 'R19_PRODUCTION_PASS|regime=H0' in log.read_text();write(cached,{'options':options(log),'log':str(log),'sha256':digest(log),'process':rec['process']});r['tests'].append(rec)
   reference=json.loads(cached.read_text());assert digest(reference['log'])==reference['sha256']
   rec=run([str(BUILD/'production_probe'),args.regime,*map(str,configs)],f'{args.regime}_{mode}')
   text=Path(rec['log']).read_text();assert f'R19_PRODUCTION_PASS|regime={args.regime}' in text and 'credit_drained=1' in text
   actual=options(rec['log']);old=reference['options'];allowed=manifest['allowed_overlay_values'];changes={k:{'H0':old.get(k),'condition':actual.get(k)} for k in set(actual)|set(old) if actual.get(k)!=old.get(k)}
   assert set(changes)==set(allowed),changes
   for k,v in allowed.items():assert actual[k]==v,(k,actual[k],v)
   clocks=re.findall(r'GPGPU-Sim uArch: clock freqs: ([0-9.:]+)',text);expected='1132000000.000000:1132000000.000000:1132000000.000000:'+('3400000000.000000' if args.regime=='D4' else '850000000.000000');assert clocks==[expected],clocks
   frozen=out/'configs'/mode;frozen.mkdir(parents=True);assets=[];ordered=[]
   for i,p in enumerate(configs):
    name=f'config-{i}.config';dst=frozen/name;shutil.copy2(p,dst);os.chmod(dst,0o444);assets.append({'name':name,'path':str(dst),'source_path':str(p)});ordered.append({'name':name,'sha256':digest(dst),'bytes':dst.stat().st_size})
   config_hash=content_hash({'ordered_configs':ordered,'auxiliary_assets':[],'environment':original['environment']})
   assert config_hash!=original['runtime_config_sha256'];r['tests'].append(rec)
   write(out/f'{mode}_EFFECTIVE_OPTIONS.json',actual)
   manifest['modes'][mode]={'configs':assets,'ordered_config_manifest':ordered,'runtime_config_sha256':config_hash,'H0_runtime_config_sha256':original['runtime_config_sha256'],'environment':original['environment'],'feature_vector':original['feature_vector'],'ideal_vector':original['ideal_vector'],'effective_options':authored_options(configs),'actual_native_effective_parameter_count':len(actual),'actual_changes_vs_H0':changes,'effective_options_path':str(out/f'{mode}_EFFECTIVE_OPTIONS.json'),'effective_options_sha256':digest(out/f'{mode}_EFFECTIVE_OPTIONS.json'),'native_clock_dump':clocks[0],'production_evidence':{'log':rec['log'],'log_sha256':rec['log_sha256'],'process':rec['process'],'exit_code':0},'H0_affected_control':reference}
  # Across modes only original FT organization differs, budgets stay equal.
  b=options(manifest['modes']['B16_BANKED']['production_evidence']['log']);u=options(manifest['modes']['U_WB16']['production_evidence']['log']);assert {k for k in b if b[k]!=u[k]}=={'-gpgpu_ep_l2_ft_mode'}
  write(out/'HEADROOM_CONFIG_MANIFEST.json',manifest);r['status']='AFFECTED_PRODUCTION_CHECKS_PASS_READY_FOR_LANE5_INDEPENDENT_REVIEW';r['headroom_manifest_sha256']=digest(out/'HEADROOM_CONFIG_MANIFEST.json');assert digest(BINARY)==BINARY_SHA
 except BaseException as error:r['status']='FAILED_OR_HOLD_RETAIN_DIAGNOSTICS';r['error']=repr(error);raise
 finally:
  if lease:registry.release_build(lease,'lane1');r['lease_released']=True
  r['resources_after']=local_resources();r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(json.dumps({'status':r['status'],'regime':args.regime,'tests':len(r['tests']),'lease_released':r.get('lease_released'),'manifest':str(out/'HEADROOM_CONFIG_MANIFEST.json')}))
if __name__=='__main__':main()
