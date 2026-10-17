"""Lane1 structural producer intake: exact new S64/U_CAP16 build, local ideals kept.

A new simulator binary requires independent Lane5 qualification. This entry
runs native OFF/affected tests and exact ordered application profile checks.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,re,resource,shlex,shutil,subprocess,sys
REPO=Path(__file__).resolve().parents[4]
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-potential20261017-lane1-all-data-r1')
FW=Path('/workspace/worktrees/accel-sim-ep-l2-potential20261017-lane1-local-r1')
BUILD=Path('/workspace/build/ep-l2-potential20261017-lane1-all-data-r1')
AUTHOR=Path('/workspace/ep_l2_parallel_lane1/all_data_build_r2/BUILD_RECEIPT.json')
C_SHA='9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f'
F_SHA='8ab6013ea90755fdc74819e92090c2de50f4f199'
OLD='7b8e6ac70b8fe0f1bd37efca11acb5284938825d'
ROOT=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1'
ENV={'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def head(p):return subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()
def write(p,v):p=Path(p);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(v,indent=2)+'\n');q.replace(p)
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def loadmod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--reuse-prefix-receipt',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 r={'schema':'EPL2_LANE1_ROLLING_RUNTIME_INTAKE_V1','status':'PREFLIGHT','authority':'a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900','core_source_commit':C_SHA,'framework_source_commit':F_SHA,'core_tree':subprocess.check_output(['git','rev-parse',C_SHA+'^{tree}'],cwd=CORE,text=True).strip(),'tool_source_commit':head(REPO),'runtime_recompiled_by_lane1':True,'runtime_recompiled_during_intake':False,'application_starts':0,'independent_qualification':False,'commands':[],'tests':[],'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'jobs':1,'unsupported':['I_BANK','I_L2_SERVICE']}
 def save():write(out/'INTAKE_RECEIPT.json',r)
 clpath=Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json');cl=json.loads(clpath.read_text());r['client_contract_sha256']=sha(clpath);r['actual_registry_sha256']=sha(cl['registry_client']);r['published_registry_sha256']=cl['registry_client_sha256']
 if r['actual_registry_sha256']!=r['published_registry_sha256']:
  r['status']='CLIENT_BINDING_HOLD_PRELEASE_NO_COMPILER';save();print(r['status']);return
 sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
 reg=Registry(cl['canonical_root']);guard=loadmod('official_guard',REPO/'util/ep_l2/ft_lane1/build_r0_1.py')
 def resources():
  live=local_resources();share=os.statvfs('/root/share');assert share.f_bavail*share.f_frsize>=40*2**30,'Share floor crossed'
  for key,path in [('output_free_bytes',out),('build_free_bytes',BUILD)]:s=os.statvfs(path);live[key]=s.f_bavail*s.f_frsize;assert live[key]>=48*2**30
  return live
 def run(cmd,name):return guard.run_owned(['/usr/bin/time','-v',*cmd],name,out,dict(os.environ,**ENV,PYTHONDONTWRITEBYTECODE='1'),r,save,resources,process_identity,180)
 lease=None
 try:
  author=json.loads(AUTHOR.read_text());assert author['status']=='BUILT_NOT_TESTED_NOT_INDEPENDENTLY_QUALIFIED','author build not finished'
  assert author['core_source_commit']==C_SHA and author['framework_source_commit']==F_SHA
  assert head(CORE)==C_SHA and head(FW)==F_SHA
  for tree in [CORE,FW]:assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=tree)
  for row in author['commands']:assert row['exit_code']==0 and sha(row['log'])==row['log_sha256']
  original=Path(author['core']);assert head(original)==C_SHA and not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=original)
  # Guard all finite A1/B1 implementation and repair test preimages explicitly.
  preserved={}
  for f in ['tests/ep_l2/test_ft_a1.cc','tests/ep_l2/test_common_delta_r16.cc','tests/ep_l2/test_ft_memcpy_clock.cc','tests/ep_l2/test_ft_host_prefill.cc']:
   old=subprocess.check_output(['git','show',OLD+':'+f],cwd=CORE);assert old==(CORE/f).read_bytes();preserved[f]=sha(CORE/f)
  r['preserved_official_files']=preserved;r['preserved_official_functions']={}
  for f,start,end in [('src/gpgpu-sim/gpu-cache.cc','void mshr_table::atomic_fill_masks(','void mshr_table::mark_ready('),('src/gpgpu-sim/ep-l2-ft-cache.inc','unsigned long long l2_cache::ft_physical_cycle()','void l2_cache::descriptor_admitted(')]:
   prior=subprocess.check_output(['git','show',OLD+':'+f],cwd=CORE,text=True);current=(CORE/f).read_text();a1=prior[prior.index(start):prior.index(end,prior.index(start))];b1=current[current.index(start):current.index(end,current.index(start))];assert a1==b1;r['preserved_official_functions'][start]=hashlib.sha256(a1.encode()).hexdigest()
  r['author_build_receipt']=str(AUTHOR);r['author_build_receipt_sha256']=sha(AUTHOR);shutil.copy2(AUTHOR,out/'AUTHOR_BUILD_RECEIPT.json')
  assert sha(BUILD/'accel-sim.out')==author['binary_sha256'];r['binary_sha256']=author['binary_sha256']
  flags=list(BUILD.rglob('flags.make'));assert flags and all('-DNDEBUG' not in f.read_text() for f in flags);r['assertion_flags_sha256']={str(f):sha(f) for f in flags}
  r['filesystem_identity']={str(p):{'realpath':str(p.resolve()),'st_dev':p.stat().st_dev} for p in [out,BUILD,Path('/root/share')]}
  before=resources();assert before['disk_free_bytes']>=50*2**30 and before['available_memory_bytes']-4*2**30>=64*2**30
  r['resources_before']=before;lease=reg.build_lease('lane1',cpu=1,memory=4*2**30);r['lease_id']=lease;save()
  # Link-input hashes are frozen before any reuse; author runtime objects are
  # not rewritten, deleted or recompiled by this producer intake.
  libs=[BUILD/'gpgpu-sim'/f for f in ['libentrypoint.a','libcuda/libcuda.a','src/cuda-sim/libptxsim.a','src/gpgpu-sim/libgpgpusim.a','src/intersim2/libintersim.a','src/accelwattch/libaccelwattch.a']]+[BUILD/'trace-driven/libtrace-driven.a',BUILD/'trace-parser/libtrace-parser.a']
  r['archives_sha256']={str(x):sha(x) for x in libs}
  base=str(CORE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config');testdir=CORE/'tests/ep_l2'
  tests=guard.repair_commands(BUILD,CORE)
  for name,cfg in [('ideal_wb','ft_wbuf.config'),('ideal_meta',None),('ideal_meta_integrated','ideal_meta_integrated.config'),('ideal_read_hit','ideal_read_hit.config'),('ideal_host_prefill_reference',None),('ideal_host_prefill_partition','ideal_host_prefill_b16.config')]:tests.append((name,[str(BUILD/'gpgpu-sim'/('ep_l2_'+name))]+([base,str(testdir/cfg)] if cfg else [])))
  for name in ['ideal_meta_integrated','ideal_read_hit']:
   cfg=out/(name+'_B16.config');cfg.write_text((testdir/(name+'.config')).read_text()+'\n-gpgpu_ep_l2_ft_mode 1\n-gpgpu_ep_l2_wbuf_entries 16\n-gpgpu_ep_l2_wad_entries 128\n')
   tests.append((name+'_B16',[str(BUILD/'gpgpu-sim'/('ep_l2_'+name)),base,str(cfg)]))
  structural=[('S64_capacity', 'potential_s64',['1','16','1','0']),('UCAP_capacity','potential_ucap',['2','16','0','16']),('UCAP_bank_retry','potential_ucap_retry',[]),('A1_S64','potential_a1',['1','16','1','0']),('A1_UCAP','potential_a1',['2','16','0','16']),('A1_UCAP_rollback','potential_a1',['2','16','0','16','rollback']),('A1_UCAP_mixed','potential_a1',['2','16','0','16','mixed'])]
  structural=[(name,target,(args[:-1]+['1',args[-1]] if args and args[-1] in ['rollback','mixed'] else args+['1']) if target!='potential_ucap_retry' else args) for name,target,args in structural]
  structural += [('B16_static_control','potential_s64',['1','16','0','0','1']),('U_uncapped_control','potential_ucap',['2','16','0','0','1'])]
  for name,target,args in structural:tests.append((name,[str(BUILD/'gpgpu-sim'/('ep_l2_'+target)),base,str(testdir/'ft_wbuf.config'),*args]))
  for mode in [1,2]:
   for ports in [1,2]:tests.append((f'P{ports}_mode{mode}',[str(BUILD/'gpgpu-sim/ep_l2_potential_p2'),base,str(testdir/'ft_wbuf.config'),str(mode),str(ports)]))
  # The old allocator fixture used invalid low pointer tokens; B1 now reads
  # real atomic request state during sector completion. Fix the fixture only.
  fmap={}
  for line in (BUILD/'gpgpu-sim/CMakeFiles/ep_l2_ft_a1.dir/flags.make').read_text().splitlines():
   if line.startswith('CXX_'):k,v=line.split(' = ',1);fmap[k]=v
  fixedsrc=Path(__file__).with_name('test_ideal_meta_real.cc');fixedexe=out/'test_ideal_meta_real'
  prior_unit=json.loads(a.reuse_prefix_receipt.read_text()) if a.reuse_prefix_receipt else {}
  if prior_unit.get('repaired_unit_fixture',{}).get('source_sha256')==sha(fixedsrc):
   fixedexe=Path(dict(prior_unit['planned_tests'])['ideal_meta'][0]);assert sha(fixedexe)==prior_unit['repaired_unit_fixture']['executable_sha256']
  else:
   run(['/usr/bin/c++',*shlex.split(fmap['CXX_DEFINES']),*shlex.split(fmap['CXX_INCLUDES']),'-I'+str(CORE/'tests/ep_l2'),'-O0','-g0','-fPIC','-std=gnu++17',str(fixedsrc),'-o',str(fixedexe),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'compile_real_request_unit')
  r['repaired_unit_fixture']={'source_sha256':sha(fixedsrc),'source_commit':head(REPO),'executable_sha256':sha(fixedexe),'runtime_changes':False,'old_failed_test_retained':'/workspace/ep_l2_parallel_lane1/local_ideals_release_r2/ideal_meta.log'}
  tests=[(name,[str(fixedexe),base,str(testdir/'ideal_meta_integrated.config')]) if name=='ideal_meta' else (name,cmd) for name,cmd in tests]
  cached={}
  if a.reuse_prefix_receipt:
   prior=json.loads(a.reuse_prefix_receipt.read_text());assert prior['core_source_commit']==C_SHA and prior['framework_source_commit']==F_SHA and prior['binary_sha256']==r['binary_sha256']
   for rec in prior['tests']:
    assert rec['exit_code']==0 and sha(rec['log'])==rec['log_sha256']
    cmd=rec['command'][2:];assert sha(cmd[0])==prior['test_executables_sha256'][cmd[0]];cached[tuple(cmd)]=rec
   r['reused_prefix_receipt']={'path':str(a.reuse_prefix_receipt),'sha256':sha(a.reuse_prefix_receipt),'verified_tests':len(cached)}
  # Read-hit160 verifies the actual configured application ROP latency.
  cfg=out/'ideal_read_hit_rop160_B16.config';cfg.write_text((testdir/'ideal_read_hit_rop160.config').read_text()+'\n-gpgpu_ep_l2_ft_mode 1\n-gpgpu_ep_l2_wbuf_entries 16\n-gpgpu_ep_l2_wad_entries 128\n')
  tests += [('I_READ_HIT_ROP160',[str(BUILD/'gpgpu-sim/ep_l2_ideal_read_hit'),base,str(testdir/'ideal_read_hit_rop160.config')]),('I_READ_HIT_ROP160_B16',[str(BUILD/'gpgpu-sim/ep_l2_ideal_read_hit'),base,str(cfg)]),('ALL_DATA_reference',[str(BUILD/'gpgpu-sim/ep_l2_all_data_reference')]),('ALL_DATA_native_ldst',[str(BUILD/'gpgpu-sim/ep_l2_all_data_ldst'),base,str(testdir/'all_data_reference.config')])]
  clocksrc=Path(__file__).with_name('test_all_data_clock.cc');clockexe=out/'all_data_clock'
  run(['/usr/bin/c++',*shlex.split(fmap['CXX_DEFINES']),*shlex.split(fmap['CXX_INCLUDES']),'-I'+str(CORE/'tests/ep_l2'),'-O0','-g0','-fPIC','-std=gnu++17',str(clocksrc),'-o',str(clockexe),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'compile_all_data_clock')
  r['physical_clock_fixture']={'author_source':'809320da3ea57270ad0a600d5af87c23c51a3117','fixture_source_commit':head(REPO),'fixture_source_sha256':sha(clocksrc),'executable_sha256':sha(clockexe)}
  tests += [('ALL_DATA_native_offset4096',[str(clockexe),base,str(testdir/'all_data_reference.config'),'--offset4096'])]
  r['planned_tests']=tests;save()
  for name,cmd in tests:
   r.setdefault('test_executables_sha256',{})[cmd[0]]=sha(cmd[0])
   if tuple(cmd) in cached:rec=dict(cached[tuple(cmd)],reused_content_immutable=True)
   else:rec=run(cmd,name)
   r['tests'].append(rec);save()
  # Compile only an independent native parser/constructor entry against exact
  # production+trace libraries. This is not a simulator runtime rebuild.
  small=out/'effective_entry';small.mkdir();flagmap={}
  for line in (BUILD/'gpgpu-sim/CMakeFiles/ep_l2_ft_a1.dir/flags.make').read_text().splitlines():
   if line.startswith('CXX_'):k,v=line.split(' = ',1);flagmap[k]=v
  includes=[]
  for line in (BUILD/'CMakeFiles/accel-sim.out.dir/flags.make').read_text().splitlines():
   if line.startswith('CXX_INCLUDES = '):includes=shlex.split(line.split(' = ',1)[1])
  src=Path(__file__).with_name('effective_config.cc');obj=small/'effective.o';exe=small/'effective_config';r['effective_entry_source_sha256']=sha(src)
  run(['/usr/bin/c++',*shlex.split(flagmap['CXX_DEFINES']),*includes,*shlex.split(flagmap['CXX_INCLUDES']),'-O0','-g0','-fPIC','-std=gnu++17','-c',str(src),'-o',str(obj)],'effective_compile')
  run(['/usr/bin/c++',str(obj),'-o',str(exe),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'effective_link');r['effective_entry_sha256']=sha(exe)
  probe_source=Path(__file__).with_name('production_probe_p2.cc');probe_obj=small/'p2_probe.o';probe_exe=small/'p2_probe'
  run(['/usr/bin/c++',*shlex.split(flagmap['CXX_DEFINES']),*includes,*shlex.split(flagmap['CXX_INCLUDES']),'-O0','-g0','-fPIC','-std=gnu++17','-c',str(probe_source),'-o',str(probe_obj)],'p2_probe_compile')
  run(['/usr/bin/c++',str(probe_obj),'-o',str(probe_exe),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'p2_probe_link')
  r['production_p2_probe']={'source_sha256':sha(probe_source),'executable_sha256':sha(probe_exe),'source_commit':head(REPO)}
  baseline=json.loads((ROOT/'BASELINE_CONTRACT_R0_1_A1_B1_V1.json').read_text());profiles={};overlaydir=REPO/'tests/ep_l2/ft20261016/parallel_potential_v1';(out/'configs').mkdir()
  for profile,mode,ov,ideals in [('B16_OFF','B16_BANKED','off',(0,0,0)),('U_WB16_OFF','U_WB16','off',(0,0,0)),('I_WB','B16_BANKED','i_wb',(1,0,0)),('I_META','B16_BANKED','i_meta',(0,1,0)),('I_WB_META','B16_BANKED','i_wb_meta',(1,1,0)),('I_READ_HIT','B16_BANKED','i_read_hit',(0,0,1)),('S64','B16_BANKED','s64',(0,0,0)),('U_CAP16','U_WB16','u_cap16',(0,0,0)),('P2_B16','B16_BANKED','p2',(0,0,0)),('P2_U_WB16','U_WB16','p2',(0,0,0)),('I_MEM_ALL_DATA','B16_BANKED','all_data',(0,0,0))]:
   old=baseline['modes'][mode];inputs=[Path(c['path']) for c in old['configs']]+([overlaydir/'off.config'] if profile in ['S64','U_CAP16','P2_B16','P2_U_WB16','I_MEM_ALL_DATA'] else [])+[overlaydir/(ov+'.config')];folder=out/'configs'/profile;folder.mkdir();assets=[];ordered=[]
   for i,x in enumerate(inputs):
    dst=folder/f'config-{i}.config';shutil.copy2(x,dst);os.chmod(dst,0o444);assets.append({'name':dst.name,'path':str(dst),'source_path':str(x)});ordered.append({'name':dst.name,'sha256':sha(dst),'bytes':dst.stat().st_size})
   cmd=[str(exe),*[x['path'] for x in assets]];rec=run(cmd,profile+'_effective');text=Path(rec['log']).read_text();assert 'PARALLEL_EFFECTIVE_PASS|' in text
   data=text.split('NATIVE_EFFECTIVE_OPTIONS_BEGIN\n',1)[1].split('NATIVE_EFFECTIVE_OPTIONS_END',1)[0];effective={}
   for line in data.splitlines():
    v=line.split('#',1)[0].strip().split(None,1)
    if v and v[0].startswith('-'):effective[v[0]]=v[1].strip() if len(v)>1 else ''
   for k,v in zip(['wb','meta','read_hit'],ideals):assert effective['-gpgpu_ep_l2_ideal_'+k]==str(v)
   assert effective['-gpgpu_ep_l2_ft_mode']==('2' if mode=='U_WB16' else '1')
   write(out/(profile+'_EFFECTIVE.json'),effective)
   feature=dict(old['feature_vector']);feature.update(static_s64=profile=='S64',wb_local_cap=16 if profile=='U_CAP16' else 0,bypass_capacity=80 if profile=='S64' else 128,static_wb_capacity=64 if profile=='S64' else 16,ideal_wb=bool(ideals[0]),ideal_meta=bool(ideals[1]),ideal_read_hit=bool(ideals[2]),nominal_payload_capacity_per_slice=1168,diagnostic_extra_payload_backing=bool(ideals[0]),wb_data_capacity_non_binding=bool(ideals[0]))
   if profile.startswith('P2_'):feature['ops_per_bank_cycle']=2
   feature['nominal_static_wb_anchor']=16
   if mode=='U_WB16' or ideals[0]:feature['static_wb_capacity']=None
   if ideals[0]:feature['payload_capacity_per_slice']=None # explicit unbounded diagnostic backing, never finite1168 qualification
   profiles[profile]={'mode':mode,'configs':assets,'ordered_config_manifest':ordered,'environment':old['environment'],'runtime_config_sha256':chash({'ordered_configs':ordered,'auxiliary_assets':[],'environment':old['environment']}),'feature_vector':feature,'ideal_vector':{'wb':bool(ideals[0]),'meta':bool(ideals[1]),'read_hit':bool(ideals[2])},'native_options':effective,'effective_log':rec,'scope':'FINITE_NATIVE' if profile.endswith('OFF') or profile in ['S64','U_CAP16','P2_B16','P2_U_WB16'] else 'LOCAL_IDEAL_NATIVE_LIFECYCLE','removed':'NONE' if profile.endswith('OFF') else {'I_WB':'WB data-slot refusal only, dynamic extra backing explicitly diagnostic','I_META':'Line-MSHR/descriptor/per-address capacities only','I_WB_META':'Both WB data and metadata capacities','I_READ_HIT':'Eligible demand lower read service including cold symbolic reference; not ALL_DATA','S64':'No ideal removal: finite1024/80/64 static partition, same1168 payload/4banks1op','U_CAP16':'No ideal removal: finite U protocol with at most16 reserved+live WB data tokens, released at lower acceptance; WAD separately to set_done','P2_B16':'Finite same4bank/1168 capacity,2 real line operations per bank physical GPUcycle','P2_U_WB16':'Finite same4bank/1168 capacity,2 real line operations per bank physical GPUcycle','I_MEM_ALL_DATA':'End-to-end non-atomic issued global/local/shared/constant/texture/parameter data reference ready=eligible+1 physical GPUcycle; native issue/register/scoreboard/CTA/membar/producer identities retained, no memory queues/admission/quota'}[profile]}
   if profile.startswith('P2_'):
    rec=run([str(probe_exe),'P2',*[x['path'] for x in assets]],profile+'_native_partition')
    assert 'R19_PRODUCTION_PASS|regime=P2' in Path(rec['log']).read_text();r['tests'].append(rec);profiles[profile]['native_partition_evidence']=rec;save()
  for profile,v in profiles.items():v['ideal_vector']['mem_all_data']=profile=='I_MEM_ALL_DATA'
  end=profiles['I_MEM_ALL_DATA'];end['scope']='END_TO_END_DATA_REFERENCE_NATIVE_LDST'
  end['feature_vector'].update(i_mem_all_data=True,configured_finite_wbuf=True,finite_wbuf=False,nominal_background='B16_OFF',data_hierarchy='NOT_APPLICABLE',payload_capacity_per_slice=None,bank_count=None,ops_per_bank_cycle=None,static_wb_capacity=None,reference_ready_latency_physical_GPUcycles=1,instruction_fetch='NATIVE_UNCHANGED',numerical_SASS_output_validated=False)
  off=profiles['B16_OFF']['native_options'];assert {k for k in off if off[k]!=end['native_options'][k]}=={'-gpgpu_ep_l2_i_mem_all_data'}
  # Negative gates must reject for the exact intended guard, not a crash or
  # parser typo. Preserve each actual abnormal exit and its whole raw log.
  invalid=out/'all_data_p2_forbidden.config';invalid.write_text('-gpgpu_ep_l2_bank_ops 2\n')
  negatives=[('ALL_DATA_duplicate_original',[str(BUILD/'gpgpu-sim/ep_l2_all_data_reference'),'--duplicate'],'EPL2MEMREF_DUPLICATE_ORIGINAL_INSTRUCTION'),('ALL_DATA_unsupported',[str(BUILD/'gpgpu-sim/ep_l2_all_data_ldst'),base,str(testdir/'all_data_reference.config'),'--unsupported'],'EPL2MEMREF_UNSUPPORTED'),('ALL_DATA_P2_forbidden',[str(exe),*[x['path'] for x in end['configs']],str(invalid)],'ALL_DATA requires separate B16 OFF')]
  for name,cmd,marker in negatives:
   try:run(cmd,name)
   except RuntimeError:
    rec=r['commands'][-1];assert rec['exit_code']==134 and marker in Path(rec['log']).read_text();rec['expected_rejection']=True;r.setdefault('expected_rejections',[]).append(rec);save()
   else:raise AssertionError('unsupported/duplicate case was accepted')
  # Equal finite system anchors; every local ideal changes only its declared
  # switches. Runtime counters/clock/queues and instruction semantics retained.
  off=profiles['B16_OFF']['native_options'];u=profiles['U_WB16_OFF']['native_options'];assert {k for k in off if off[k]!=u[k]}=={'-gpgpu_ep_l2_ft_mode'}
  for profile in ['I_WB','I_META','I_WB_META','I_READ_HIT']:
   v=profiles[profile]['native_options'];assert {k for k in off if off[k]!=v[k]}=={'-gpgpu_ep_l2_ideal_'+k for k,x in profiles[profile]['ideal_vector'].items() if x}
  for profile,key,value,reference in [('S64','-gpgpu_ep_l2_static_s64','1','B16_OFF'),('U_CAP16','-gpgpu_ep_l2_wb_local_cap','16','U_WB16_OFF'),('P2_B16','-gpgpu_ep_l2_bank_ops','2','B16_OFF'),('P2_U_WB16','-gpgpu_ep_l2_bank_ops','2','U_WB16_OFF')]:
   v=profiles[profile]['native_options'];ref=profiles[reference]['native_options'];assert v[key]==value and {k for k in ref if ref[k]!=v[k]}=={key}
  write(out/'RUNTIME_CONFIG_MANIFEST.json',{'schema':'EPL2_PARALLEL_PRODUCER_PROFILES_V1','experiment_id':'EPL2_PARALLEL_POTENTIAL_20261017_V1','core_source_commit':C_SHA,'framework_source_commit':F_SHA,'binary_sha256':r['binary_sha256'],'profiles':profiles,'independently_qualified':False})
  (out/'binaries').mkdir();dst=out/'binaries/accel-sim.out';shutil.copy2(BUILD/'accel-sim.out',dst);assert sha(dst)==r['binary_sha256'];os.chmod(dst,0o555);r['binary']=str(dst)
  assert sha(AUTHOR)==r['author_build_receipt_sha256'] and sha(BUILD/'accel-sim.out')==r['binary_sha256']
  for f,h in r['archives_sha256'].items():assert sha(f)==h
  assert head(CORE)==C_SHA and head(FW)==F_SHA
  r['status']='ALL_DATA_P2_STRUCTURAL_LOCAL_IDEALS_PRODUCER_PASS_LANE5_INDEPENDENT_QUALIFICATION_REQUIRED'
 except BaseException as e:r['status']='FAILED_RETAIN_EVIDENCE_NO_RUNTIME_RELEASE';r['error']=repr(e);raise
 finally:
  if lease:reg.release_build(lease,'lane1');r['lease_released']=True
  r['resources_after']=resources();r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(json.dumps({'status':r['status'],'tests':len(r['tests']),'binary_sha256':r.get('binary_sha256'),'lease_released':r.get('lease_released')}))
if __name__=='__main__':main()
