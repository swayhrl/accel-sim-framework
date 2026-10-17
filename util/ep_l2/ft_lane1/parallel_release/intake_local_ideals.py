"""Lane1 rolling producer intake; reuse exact author build, no runtime recompile.

A new simulator binary requires independent Lane5 qualification. This entry
runs native OFF/affected tests and exact ordered application profile checks.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,re,resource,shlex,shutil,subprocess,sys
REPO=Path(__file__).resolve().parents[4]
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-potential20261017-lane1-local-r1')
FW=Path('/workspace/worktrees/accel-sim-ep-l2-potential20261017-lane1-local-r1')
BUILD=Path('/workspace/build/ep-l2-potential20261017-lane4-local-r1')
AUTHOR=Path('/workspace/ep_l2_potential20261017_lane4_results/local_r1_build/BUILD_RECEIPT.json')
C_SHA='a26b3566744abd83c0c0ae2ce43be34e796206e7'
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
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 r={'schema':'EPL2_LANE1_ROLLING_RUNTIME_INTAKE_V1','status':'PREFLIGHT','authority':'a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900','core_source_commit':C_SHA,'framework_source_commit':F_SHA,'core_tree':subprocess.check_output(['git','rev-parse',C_SHA+'^{tree}'],cwd=CORE,text=True).strip(),'tool_source_commit':head(REPO),'runtime_recompiled_by_lane1':False,'application_starts':0,'independent_qualification':False,'commands':[],'tests':[],'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'jobs':1,'unsupported':['S64','U_CAP16','P2','I_BANK','I_L2_SERVICE','I_MEM_ALL_DATA']}
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
  author=json.loads(AUTHOR.read_text());assert author['status']=='BUILT_NOT_INDEPENDENTLY_QUALIFIED','author build not finished'
  assert author['core_source_commit']==C_SHA and author['framework_source_commit']==F_SHA
  assert head(CORE)==C_SHA and head(FW)==F_SHA
  for tree in [CORE,FW]:assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=tree)
  for row in author['commands']:assert row['exit_code']==0 and sha(row['log'])==row['log_sha256']
  original=Path(author['core']);assert head(original)==C_SHA and not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=original)
  # Guard all finite A1/B1 implementation and repair test preimages explicitly.
  preserved={}
  for f in ['src/gpgpu-sim/ep-l2-ft-cache.inc','tests/ep_l2/test_ft_a1.cc','tests/ep_l2/test_common_delta_r16.cc','tests/ep_l2/test_ft_memcpy_clock.cc','tests/ep_l2/test_ft_host_prefill.cc']:
   old=subprocess.check_output(['git','show',OLD+':'+f],cwd=CORE);assert old==(CORE/f).read_bytes();preserved[f]=sha(CORE/f)
  r['preserved_official_files']=preserved
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
  r['planned_tests']=tests;save()
  for name,cmd in tests:
   r.setdefault('test_executables_sha256',{})[cmd[0]]=sha(cmd[0]);rec=run(cmd,name);r['tests'].append(rec);save()
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
  baseline=json.loads((ROOT/'BASELINE_CONTRACT_R0_1_A1_B1_V1.json').read_text());profiles={};overlaydir=REPO/'tests/ep_l2/ft20261016/parallel_potential_v1';(out/'configs').mkdir()
  for profile,mode,ov,ideals in [('B16_OFF','B16_BANKED','off',(0,0,0)),('U_WB16_OFF','U_WB16','off',(0,0,0)),('I_WB','B16_BANKED','i_wb',(1,0,0)),('I_META','B16_BANKED','i_meta',(0,1,0)),('I_WB_META','B16_BANKED','i_wb_meta',(1,1,0)),('I_READ_HIT','B16_BANKED','i_read_hit',(0,0,1))]:
   old=baseline['modes'][mode];inputs=[Path(c['path']) for c in old['configs']]+[overlaydir/(ov+'.config')];folder=out/'configs'/profile;folder.mkdir();assets=[];ordered=[]
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
   feature=dict(old['feature_vector']);feature.update(ideal_wb=bool(ideals[0]),ideal_meta=bool(ideals[1]),ideal_read_hit=bool(ideals[2]))
   profiles[profile]={'mode':mode,'configs':assets,'ordered_config_manifest':ordered,'environment':old['environment'],'runtime_config_sha256':chash({'ordered_configs':ordered,'auxiliary_assets':[],'environment':old['environment']}),'feature_vector':feature,'ideal_vector':{'wb':bool(ideals[0]),'meta':bool(ideals[1]),'read_hit':bool(ideals[2])},'native_options':effective,'effective_log':rec,'scope':'FINITE_NATIVE' if profile.endswith('OFF') else 'LOCAL_IDEAL_NATIVE_LIFECYCLE','removed':'NONE' if profile.endswith('OFF') else {'I_WB':'WB data-slot refusal only, dynamic extra backing explicitly diagnostic','I_META':'Line-MSHR/descriptor/per-address capacities only','I_WB_META':'Both WB data and metadata capacities','I_READ_HIT':'Eligible demand lower read service including cold symbolic reference; not ALL_DATA'}[profile]}
  # Equal finite system anchors; every local ideal changes only its declared
  # switches. Runtime counters/clock/queues and instruction semantics retained.
  off=profiles['B16_OFF']['native_options'];u=profiles['U_WB16_OFF']['native_options'];assert {k for k in off if off[k]!=u[k]}=={'-gpgpu_ep_l2_ft_mode'}
  for profile in ['I_WB','I_META','I_WB_META','I_READ_HIT']:
   v=profiles[profile]['native_options'];assert {k for k in off if off[k]!=v[k]}=={'-gpgpu_ep_l2_ideal_'+k for k,x in profiles[profile]['ideal_vector'].items() if x}
  write(out/'RUNTIME_CONFIG_MANIFEST.json',{'schema':'EPL2_PARALLEL_PRODUCER_PROFILES_V1','experiment_id':'EPL2_PARALLEL_POTENTIAL_20261017_V1','core_source_commit':C_SHA,'framework_source_commit':F_SHA,'binary_sha256':r['binary_sha256'],'profiles':profiles,'independently_qualified':False})
  (out/'binaries').mkdir();dst=out/'binaries/accel-sim.out';shutil.copy2(BUILD/'accel-sim.out',dst);assert sha(dst)==r['binary_sha256'];os.chmod(dst,0o555);r['binary']=str(dst)
  assert sha(AUTHOR)==r['author_build_receipt_sha256'] and sha(BUILD/'accel-sim.out')==r['binary_sha256']
  for f,h in r['archives_sha256'].items():assert sha(f)==h
  assert head(CORE)==C_SHA and head(FW)==F_SHA
  r['status']='LOCAL_IDEALS_PRODUCER_PASS_LANE5_INDEPENDENT_QUALIFICATION_REQUIRED'
 except BaseException as e:r['status']='FAILED_RETAIN_EVIDENCE_NO_RUNTIME_RELEASE';r['error']=repr(e);raise
 finally:
  if lease:reg.release_build(lease,'lane1');r['lease_released']=True
  r['resources_after']=resources();r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(json.dumps({'status':r['status'],'tests':len(r['tests']),'binary_sha256':r.get('binary_sha256'),'lease_released':r.get('lease_released')}))
if __name__=='__main__':main()
