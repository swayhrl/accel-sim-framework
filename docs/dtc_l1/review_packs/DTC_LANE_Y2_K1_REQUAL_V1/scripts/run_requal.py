#!/usr/bin/env python3
"""Independent CPU-only K1 requalification. Never dispatches GPU simulation."""
import argparse,copy,csv,hashlib,json,os,resource,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
from check_observation import subset
from extract_production import generate
from capture_toolchain import capture
from capture_unchanged import capture as capture_unchanged
PACK=Path(__file__).resolve().parent.parent
SCRIPTS=PACK/'scripts'
FROZEN='6fba0136f8465b59fe5858a950fa39efb265f654'
LANE_V='26abd496417d9392245052e54fbd9ba27c6ffd96'
X_BRANCH='hrl/iscas2027-dtc-lane-x-invalidate-optin-core-174-v1'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,data):Path(path).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--core-repo',type=Path,required=True);ap.add_argument('--framework-repo',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--core-sha',required=True);ap.add_argument('--x-review-sha',required=True);ap.add_argument('--external',type=Path,required=True);ap.add_argument('--run-label',default='final_run');a=ap.parse_args()
 ext=a.external.resolve();ext.mkdir(parents=True,exist_ok=True);logs=ext/a.run_label;logs.mkdir(exist_ok=True)
 if list(logs.iterdir()):raise RuntimeError('Use a new external/final_run directory; do not overwrite receipts')
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));receipts=[];results=[];matrix=[]
 gate=dict(schema=2,goal='DTC_LANE_Y2_INDEPENDENT_K1_REQUAL_174',status='PENDING',reason='AWAITING_X_EXECUTABLE_SOURCE',lane_v_commit=LANE_V,frozen_core=FROZEN,target_core=a.core_sha,full_simulations_dispatched=0,new_execution_authorities=0,production_source_modified=False)
 dump(PACK/'VALIDATION_GATE_V2.json',gate)
 def run(argv,label,expected=0,env=None):
  argv=[str(x) for x in argv];r=subprocess.run(argv,capture_output=True,text=True,env=env)
  output={}
  for stream in ['stdout','stderr']:
   p=logs/(label+'.'+stream);p.write_text(getattr(r,stream));output[stream]=dict(path=str(p),sha256=digest(p))
  receipts.append(dict(label=label,argv=argv,expected_exit_code=expected,exit_code=r.returncode,environment_overrides={'LD_LIBRARY_PATH':env['LD_LIBRARY_PATH']} if env and 'LD_LIBRARY_PATH'in env else {},**output))
  if r.returncode!=expected:
   dump(PACK/'BUILD_RECEIPTS.json',dict(commands=receipts,status='FAIL_TEST_COMMAND'))
   gate.update(status='FAIL_K1_OO_MODEL_SCOPE',reason='Unexpected exit in '+label);dump(PACK/'VALIDATION_GATE_V2.json',gate)
   raise RuntimeError(label+': expected '+str(expected)+' observed '+str(r.returncode))
  return r
 def git(repo,*args):return run(['git','-C',repo,*args],'git_'+str(len(receipts))).stdout.strip()
 remote=git(a.core_repo,'ls-remote','--heads','origin',X_BRANCH)
 if not remote or remote.split()[0]!=a.core_sha:
  gate.update(reason='AWAITING_X_EXECUTABLE_SOURCE: target is not current published X HEAD');dump(PACK/'VALIDATION_GATE_V2.json',gate);return 3
 assert git(a.source,'rev-parse','HEAD')==a.core_sha
 assert git(a.source,'status','--porcelain','--untracked-files=no')==''
 run(['git','-C',a.core_repo,'merge-base','--is-ancestor',FROZEN,a.core_sha],'frozen_ancestor')
 header=a.source/'src/gpgpu-sim/dtc-l1-invalidation.h'
 if not header.exists() or 'register_source_invalidation_option' not in header.read_text() or '-gpgpu_dtc_l1_invalidate_on_source_event' not in header.read_text() or 'invalidate_lookup' not in (a.source/'src/gpgpu-sim/dtc-l1-common.h').read_text():
  gate.update(reason='AWAITING_X_EXECUTABLE_SOURCE: no known executable switch and OO hook');dump(PACK/'VALIDATION_GATE_V2.json',gate);return 3
 delivery_path='docs/dtc_l1/review_packs/DTC_LANE_X_OPTIN_INVALIDATION_V1/GIT_DELIVERY.json'
 delivery_raw=git(a.framework_repo,'show',a.x_review_sha+':'+delivery_path);delivery=json.loads(delivery_raw)
 assert delivery['core']['sha']==a.core_sha and delivery['core']['exact_match'] and delivery['core']['fetch_back_exit_code']==0
 bindings=[]
 for commit,paths in [(LANE_V,['docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/K1_SEMANTIC_CONTRACT.md','docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/SOURCE_EVENT_MAP.md']),(a.x_review_sha,[delivery_path])]:
  for path in paths:
   data=subprocess.check_output(['git','-C',str(a.framework_repo),'show',commit+':'+path]);bindings.append(dict(commit=commit,path=path,blob=git(a.framework_repo,'rev-parse',commit+':'+path),sha256=hashlib.sha256(data).hexdigest()))
 source_files=[]
 for path in ['src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/dtc-l1-invalidation.h','src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/gpu-sim.cc','src/option_parser.cc']:
  source_files.append(dict(path=path,commit=a.core_sha,blob=git(a.core_repo,'rev-parse',a.core_sha+':'+path),sha256=digest(a.source/path)))
 for path in ['src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h']:
  assert git(a.core_repo,'rev-parse',a.core_sha+':'+path)==git(a.core_repo,'rev-parse',FROZEN+':'+path)
 dump(PACK/'SOURCE_BINDING.json',dict(target=a.core_sha,remote=remote,frozen=FROZEN,contracts=bindings,source_files=source_files,changed_paths=git(a.core_repo,'diff','--name-only',FROZEN,a.core_sha).splitlines(),x_fetch_back_receipt=delivery['core']))
 build=ext/('build-'+a.core_sha[:8]);generated=ext/('generated-'+a.core_sha[:8]);generated.mkdir(exist_ok=True)
 generate(a.source,generated);dump(PACK/'EXTRACTED_BODY_BINDING.json',json.loads((generated/'EXTRACTED_BODY_BINDING.json').read_text()))
 run(['g++','--version'],'compiler');run(['cmake','--version'],'cmake_version')
 run(['cmake','-S',a.source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCUDAToolkit_ROOT=/usr/local/cuda-11.8','-DGPGPUSIM_BUILD_DTC_L1_TESTS=ON','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'],'configure')
 run(['cmake','--build',build,'-j4'],'full_core_build')
 env=dict(os.environ,LD_LIBRARY_PATH=str(build));binaries=[]
 def compile(name,source,includes,linked=True):
  binary=ext/name;binary.unlink(missing_ok=True)
  args=['g++','-std=c++17','-UNDEBUG','-DCUDART_VERSION=11080',*['-I'+str(p) for p in includes],'-I/usr/local/cuda-11.8/include',source]
  if linked:args+=['-L'+str(build),'-Wl,-rpath,'+str(build),'-lcudart']
  run(args+['-o',binary],'compile_'+name);binaries.append(dict(name=name,path=str(binary),sha256=digest(binary)))
  if linked:
   binding=run(['ldd',binary],'ldd_'+name,env=env);assert str(build/'libcudart.so') in binding.stdout
  return binary
 include=[a.source/'src/gpgpu-sim',generated]
 production=compile('production_cases_final',SCRIPTS/'production_cases.cc',include)
 api=compile('public_api_cases_final',SCRIPTS/'public_api_cases.cc',include)
 options=compile('options_cpu_probe_final',SCRIPTS/'options_cpu_probe.cc',[a.source/'src',a.source/'libcuda'])
 def compare_negative(expected,observed,label):
  bad=copy.deepcopy(expected);bad['INTENTIONAL_IMPOSSIBLE_FIELD']='NEGATIVE_CONTROL'
  # A false field guaranteed absent detects accidental comparator bypass.
  ep=logs/(label+'_wrong_expected.json');op=logs/(label+'_observed.json');dump(ep,bad);dump(op,observed)
  return run([sys.executable,SCRIPTS/'check_observation.py',ep,op],'negative_'+label,expected=1).returncode
 for c in json.loads((PACK/'inputs/production_cases.json').read_text())['cases']:
  r=run([production,c['id']],'production_'+c['id'],c['expected_exit_code'],env)
  observations={v['phase']:v['state'] for line in r.stdout.splitlines() if line.startswith('{') for v in [json.loads(line)]}
  subset(c['expected_phases'],observations)
  if c['expected_assertion']:assert c['expected_assertion'] in r.stderr
  expected=c['expected_phases'] if c['expected_exit_code']==0 else {'assertion_matched':True}
  observed=observations if c['expected_exit_code']==0 else {'assertion_matched':c['expected_assertion'] in r.stderr}
  negative=compare_negative(expected,observed,c['id'])
  result=dict(id=c['id'],layer='EXACT_PRODUCTION_BODY_WITH_FIXTURES',contract=c['contract'],input='scripts/production_cases.cc#'+c['id'],expected=expected,observed=observed,expected_exit_code=c['expected_exit_code'],exit_code=r.returncode,negative_oracle_exit_code=negative,status='PASS_EXPECTED_CPU_OBSERVATION');results.append(result)
  matrix.append(dict(id=c['id'],layer=result['layer'],contract=','.join(c['contract']),input=result['input'],expected='inputs/production_cases.json#'+c['id'],observed='EXPECTED_VS_OBSERVED.json#'+c['id'],exit_code=r.returncode,negative_exit_code=negative,status=result['status']))
 for finite in [0,1]:
  expected=dict(allocated=0,refs=0,pib=0,requests=4,changed=3,noops=1,ordinary_commits=4,generation_jump=2,map_loss_count=3 if finite else 0,map_loss_sum=2 if finite else 0)
  r=run([api,'finite'+str(finite)],'api_finite'+str(finite),env=env);observed=json.loads(r.stdout);subset(expected,observed);neg=compare_negative(expected,observed,'api'+str(finite))
  results.append(dict(id='public_api_finite'+str(finite),layer='DIRECT_PRODUCTION_API_REAL_ORDINARY_CACHE',expected=expected,observed=observed,exit_code=r.returncode,negative_oracle_exit_code=neg))
 # Omitted, explicit OFF and frozen original LDST body have identical CPU states.
 states={r['id']:r['observed'] for r in results}
 assert states['k0_default']==states['k0_explicit_off']==states['k0_frozen']
 option_cases=[('default',[],0,{'-gpgpu_dtc_l1_mode':'0','-gpgpu_dtc_l1_invalidate_on_source_event':'0','-gpgpu_dtc_l1_finite_service':'0'}),('omitted_oo',['-gpgpu_dtc_l1_mode','3','-gpgpu_dtc_l1_finite_service','1'],0,{'-gpgpu_dtc_l1_mode':'3','-gpgpu_dtc_l1_invalidate_on_source_event':'0','-gpgpu_dtc_l1_finite_service':'1'}),('off_oo',['-gpgpu_dtc_l1_mode','3','-gpgpu_dtc_l1_invalidate_on_source_event','0','-gpgpu_dtc_l1_finite_service','1'],0,{'-gpgpu_dtc_l1_mode':'3','-gpgpu_dtc_l1_invalidate_on_source_event':'0','-gpgpu_dtc_l1_finite_service':'1'}),('on_oo',['-gpgpu_dtc_l1_mode','3','-gpgpu_dtc_l1_invalidate_on_source_event','1','-gpgpu_dtc_l1_finite_service','1'],0,{'-gpgpu_dtc_l1_mode':'3','-gpgpu_dtc_l1_invalidate_on_source_event':'1','-gpgpu_dtc_l1_finite_service':'1'}),('on_oo_no_finite',['-gpgpu_dtc_l1_mode','3','-gpgpu_dtc_l1_invalidate_on_source_event','1'],0,{'-gpgpu_dtc_l1_mode':'3','-gpgpu_dtc_l1_invalidate_on_source_event':'1','-gpgpu_dtc_l1_finite_service':'0'}),('unknown',['-lane_y2_nonexistent','1'],1,{'unknown_rejected':True})]
 for label,argv,rc,expected in option_cases:
  r=run([options,*argv],'options_'+label,rc,env)
  observed={l.split()[0]:l.split()[1] for l in r.stdout.splitlines() if l.startswith('-gpgpu_')}
  if rc:observed={'unknown_rejected':"Unknown Option: '-lane_y2_nonexistent'" in r.stderr}
  subset(expected,observed);negative=compare_negative(expected,observed,'options_'+label)
  results.append(dict(id='options_'+label,layer='REAL_CORE_LIBRARY_CONFIG_AND_PARSER',input=argv,expected=expected,observed={k:observed[k] for k in expected},exit_code=r.returncode,negative_oracle_exit_code=negative))
 frozen=ext/'frozen';frozen.mkdir(exist_ok=True)
 (frozen/'dtc-l1-common.h').write_bytes(subprocess.check_output(['git','-C',str(a.core_repo),'show',FROZEN+':src/gpgpu-sim/dtc-l1-common.h']))
 paired={}
 for lineage,inc in [('new_off',a.source/'src/gpgpu-sim'),('frozen',frozen)]:
  binary=compile('k0_'+lineage,SCRIPTS/'k0_regression.cc',[inc],linked=False)
  for c in json.loads((PACK/'inputs/k0_regression.json').read_text())['cases']:
   r=run([binary,c['id']],lineage+'_'+c['id'],c['exit_code'])
   observed=json.loads(r.stdout) if r.returncode==0 else {'assertion_matched':c['expected_assert'] in r.stderr};expected=c.get('expected',{'assertion_matched':True});subset(expected,observed)
   neg=compare_negative(expected,observed,lineage+'_'+c['id']);paired[(lineage,c['id'])]=(observed,r.returncode)
   results.append(dict(id=lineage+'_'+c['id'],layer='K0_FROZEN_COMMON_HEADER_PAIRED',expected=expected,observed=observed,exit_code=r.returncode,negative_oracle_exit_code=neg))
 for c in json.loads((PACK/'inputs/k0_regression.json').read_text())['cases']:assert paired[('new_off',c['id'])]==paired[('frozen',c['id'])]
 run(['ctest','--test-dir',build,'--output-on-failure'],'upstream_regressions',env=env)
 assert git(a.source,'status','--porcelain','--untracked-files=no')==''
 assert git(a.core_repo,'ls-remote','--heads','origin',X_BRANCH).split()[0]==a.core_sha
 # Preserve V1 as immutable inherited evidence; do not rerun its Goal or outputs.
 old='docs/dtc_l1/review_packs/DTC_LANE_Y_INVALIDATION_V1'
 assert git(a.framework_repo,'rev-parse','b673d046b38f61159b5db67a477d58d1afa4662f:'+old)==git(Path.cwd(),'rev-parse','HEAD:'+old)
 dump(PACK/'EXPECTED_VS_OBSERVED.json',dict(schema=2,core=a.core_sha,results=results,full_simulations_dispatched=0,architectural_values='UNPROVEN',cross_sm_coherence='UNPROVEN'))
 for r in results:
  if r['layer']=='EXACT_PRODUCTION_BODY_WITH_FIXTURES':continue
  matrix.append(dict(id=r['id'],layer=r['layer'],contract='K0'if'k0_'in r['id']or r['id'].startswith(('new_off','frozen','options'))else'K1-02',input=str(r.get('input',r['id'])),expected='EXPECTED_VS_OBSERVED.json#'+r['id'],observed='EXPECTED_VS_OBSERVED.json#'+r['id'],exit_code=r['exit_code'],negative_exit_code=r['negative_oracle_exit_code'],status='PASS_EXPECTED_CPU_OBSERVATION'))
 with (PACK/'TEST_MATRIX.tsv').open('w')as f:
  writer=csv.DictWriter(f,fieldnames=['id','layer','contract','input','expected','observed','exit_code','negative_exit_code','status'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(matrix)
 binaries.append(dict(name='libcudart',path=str(build/'libcudart.so'),sha256=digest(build/'libcudart.so')))
 dump(PACK/'BUILD_RECEIPTS.json',dict(core=a.core_sha,compiler=receipts[[r['label']for r in receipts].index('compiler')],compile_commands_sha256=digest(build/'compile_commands.json'),cmake_cache_sha256=digest(build/'CMakeCache.txt'),binaries=binaries,commands=receipts,logs_committed=False))
 capture(build,PACK/'TOOLCHAIN_IDENTITY.json')
 capture_unchanged(a.source,PACK/'UNCHANGED_PATHS.json')
 gate.update(status='PASS_K1_OO_MODEL_SCOPE',reason='Real published K1 OO APIs and exact production source statements passed CPU structural/timing contracts within disclosed fixture scope',as_of=datetime.now(timezone(timedelta(hours=8))).isoformat(),production_k1_executed=True,x_producer_fetch_back_verified=True,checks=len(results),positive_control=dict(case='source_idle',changed=1,old_tag_queryable_before=True,old_tag_queryable_after=False),negative_control=dict(case='source_negative',changed=0,tag_queryable_after=True),k0_cpu_default_off_equivalent=True,io='IO_K1_UNIMPLEMENTED_STOP',modern='HOLD',architectural_value_correctness='UNPROVEN',cross_sm_coherence='UNPROVEN',qualification_scope='OO logical mapping/lifetime and explicit zero-added-cycle source-request model; not full GPU/NoC integration or PPA',full_input_pairing='NOT_RUN_CPU_ONLY; Lane AA owns complete identical-input K0/K1 dispatch',execution_authority='Lane AA only; this runner creates no execution authority',fixture_limits=['clock and scoreboard inputs','packet accessor/ownership fixture, no real mem_fetch constructor/NoC','WB grant fixture; real production failure branch executed, operand collector arbitration not simulated','register scoreboard completion shim uses production completion_accounting','ordinary L1D protected custom-Tag constructor; GPU perf-counter registration not exercised','cache configuration aftermath omitted from source-selected block','no complete shader_core/ldst ABI object or full gpgpu_sim cycle executed','full lower-create/ICNT issue integration not executed; unchanged method bodies independently hash-checked'],unchanged_collateral_methods=7)
 dump(PACK/'VALIDATION_GATE_V2.json',gate);print(json.dumps(dict(status=gate['status'],checks=len(results),matrix_rows=len(matrix))));return 0

if __name__=='__main__':
 try:sys.exit(main())
 except Exception as error:
  path=PACK/'VALIDATION_GATE_V2.json'
  gate=json.loads(path.read_text()) if path.exists() else {}
  gate.update(status='FAIL_K1_OO_MODEL_SCOPE',reason=type(error).__name__+': '+str(error),full_simulations_dispatched=0,new_execution_authorities=0)
  dump(path,gate)
  raise
