#!/usr/bin/env python3
"""Leased affected-path fixture; no full build, app launch or science acceptance."""
import argparse, copy, datetime, hashlib, json, os, resource, shlex, signal, subprocess, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
TASK=Path(__file__).parent
BUILD=Path('/workspace/build/ep-l2-potential20261017-lane3-icnt-r1')
RAW=Path('/workspace/ep-l2-potential20261017-lane3')
ORIGINAL=Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs')
OLD=Path('/workspace/results/ep_l2_ft20261016/lane1/review_r19/d2_r1/PRODUCTION_CHECK_RECEIPT.json')
PROFILES={'ROP40_H0':{'-gpgpu_l2_rop_latency':'40'},
 'ICNT2_H0':{'-gpgpu_clock_domains':'1132.0:2264.0:1132.0:850.0'},
 'WAD256_Q4':{'-gpgpu_dram_partition_queues':'64:512:256:64','-gpgpu_frfcfs_dram_sched_queue_size':'512','-gpgpu_dram_return_queue_size':'768','-gpgpu_ep_l2_wad_entries':'256'}}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def options(log):
 text=Path(log).read_text().split('R19_NATIVE_EFFECTIVE_OPTIONS_BEGIN\n')[1].split('R19_NATIVE_EFFECTIVE_OPTIONS_END')[0]
 return {s[0]:s[1].strip() if len(s)>1 else '' for line in text.splitlines() if (s:=line.split('#',1)[0].strip().split(None,1)) and s[0].startswith('-')}
def authored(paths):
 result={}
 for p in paths:
  tokens=shlex.split(Path(p).read_text(),comments=True);assert len(tokens)%2==0
  result.update(zip(tokens[::2],tokens[1::2]))
 return result
def limits():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_CPU,(90,90))
 resource.setrlimit(resource.RLIMIT_AS,(4*2**30,4*2**30));resource.setrlimit(resource.RLIMIT_FSIZE,(256*2**20,256*2**20))
def main():
 p=argparse.ArgumentParser();p.add_argument('profile',choices=['ICNT2_H0']);p.add_argument('--build',action='store_true');p.add_argument('--revision',default=None);a=p.parse_args()
 out=RAW/(a.profile+'_'+(a.revision or 'r2'));out.mkdir(parents=True,exist_ok=False)
 client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
 module_path=Path(client['registry_client'])
 if digest(module_path)!=client['registry_client_sha256']:
  # Owner may be editing its worktree. Consume only the immutable published
  # client named by CLIENT_CONTRACT, never its uncommitted replacement.
  owner=module_path.parents[3];relative=module_path.relative_to(owner)
  data=subprocess.check_output(['git','show',client['registry_source_commit']+':'+str(relative)],cwd=owner)
  assert hashlib.sha256(data).hexdigest()==client['registry_client_sha256']
  cache=RAW/'.published_registry'/client['registry_client_sha256'];cache.mkdir(parents=True,exist_ok=True)
  module_path=cache/'registry.py'
  if module_path.exists():assert module_path.read_bytes()==data
  else:module_path.write_bytes(data);module_path.chmod(0o444)
 sys.path.insert(0,str(module_path.parent));from registry import Registry,local_resources,process_identity
 reg=Registry();old=json.loads(OLD.read_text());binding=old['fixture_build_identity']
 fixture=TASK/'icnt_probe.cc';r={'schema':'LANE3_PARALLEL_AFFECTED_V1','profile':a.profile,'status':'STARTED','application_starts':0,'full_builds':0,'runtime_code_recompiled':False,'commands':[],'registry_client_sha256':digest(module_path),'registry_import_path':str(module_path),'fixture_source_sha256':digest(fixture),'tool_parent_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()}
 def safe():
  live=local_resources();assert live['disk_free_bytes']>=50*2**30 and live['available_memory_bytes']-4*2**30>=64*2**30
  f=os.statvfs('/root/share');assert f.f_bavail*f.f_frsize>=40*2**30
  f=os.statvfs(out);assert f.f_bavail*f.f_frsize>=50*2**30 and os.stat(out).st_dev==os.stat('/workspace').st_dev
  return {**live,'output_realpath':str(out.resolve()),'output_st_dev':os.stat(out).st_dev,'output_available':f.f_bavail*f.f_frsize}
 def run(cmd,name):
  safe();log=out/(name+'.log');wrapped=['/usr/bin/time','-v',*cmd]
  with log.open('x') as f:
   child=subprocess.Popen(wrapped,stdout=f,stderr=subprocess.STDOUT,cwd=out,start_new_session=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'),preexec_fn=limits)
   row={'command':wrapped,'process':process_identity(child.pid),'log':str(log)};r['commands'].append(row)
   try:row['exit_code']=child.wait(timeout=100)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  row['sha256']=digest(log);assert row['exit_code']==0,(name,row['exit_code']);return row
 r['resources_before']=safe();lease=None
 try:
  lease=reg.build_lease('lane3',cpu=1,memory=4*2**30);r['lease_id']=lease;r['resources_after_lease']=safe()
  for path,h in binding['archives_sha256'].items():assert digest(path)==h
  native=json.loads((ORIGINAL/'convolutionSeparable_B16_BANKED.json').read_text());assert digest(native['binary'])==native['identity']['binary_sha256']==old['official_binary_sha256']
  if a.build:
   BUILD.mkdir(parents=True,exist_ok=False)
   commands=old['commands'];compile_cmd=next(c['command'][2:] for c in commands if c['command'][2].endswith('c++') and '-c' in c['command'])
   compile_cmd[compile_cmd.index('-c')+1]=str(fixture);compile_cmd[compile_cmd.index('-o')+1]=str(BUILD/'probe.o');run(compile_cmd,'compile')
   link_cmd=next(c['command'][2:] for c in commands if c['command'][2].endswith('c++') and '-Wl,--start-group' in c['command'])
   link_cmd[1]=str(BUILD/'probe.o');link_cmd[link_cmd.index('-o')+1]=str(BUILD/'probe');run(link_cmd,'link')
   write(BUILD/'BUILD_IDENTITY.json',{'fixture_source_sha256':digest(fixture),'binary_sha256':digest(BUILD/'probe'),'archives_sha256':binding['archives_sha256'],'runtime_core':old['runtime_core'],'runtime_framework':old['runtime_framework']})
  b=json.loads((BUILD/'BUILD_IDENTITY.json').read_text());assert b['fixture_source_sha256']==digest(fixture) and b['binary_sha256']==digest(BUILD/'probe');r['fixture_build_identity']=b
  manifest={'schema':'LANE3_FINITE_PROFILE_V1','experiment_id':'EPL2_PARALLEL_POTENTIAL_20261017_V1','coordination_commit':'a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900','profile':a.profile,'status':'PRODUCER_AFFECTED_PASS_LANE5_INDEPENDENT_ADMISSION_PENDING','identity':{k:native['identity'][k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},'binary':native['binary'],'allowed_overlay':PROFILES[a.profile],'modes':{},'application_starts':0,'scope':'Real production partition/two subpartitions + native clocks linked to frozen archives; not a full application or independent science qualification.'}
  overlay=REPO/'tests/ep_l2/parallel_potential_lane3'/(a.profile.lower()+'.config');assert authored([overlay])==PROFILES[a.profile]
  for mode in ['B16_BANKED','U_WB16']:
   source=json.loads((ORIGINAL/('convolutionSeparable_'+mode+'.json')).read_text());base=[v['path'] for v in source['configs']]
   configs=base+[str(overlay)];rec=run([str(BUILD/'probe'),a.profile,*configs],mode)
   actual=options(rec['log']);assert 'L3_PRODUCTION_PASS|' in Path(rec['log']).read_text()
   ref=next(c for c in old['tests'] if Path(c['log']).name=='H0_'+mode+'.log');assert digest(ref['log'])==ref['log_sha256'];reference=options(ref['log'])
   delta={k:{'H0':reference.get(k),'condition':actual.get(k)} for k in set(actual)|set(reference) if reference.get(k)!=actual.get(k)}
   assert set(delta)==set(PROFILES[a.profile]),delta
   assert all(actual[k]==v for k,v in PROFILES[a.profile].items())
   frozen=out/'configs'/mode;frozen.mkdir(parents=True);rows=[];assets=[]
   for i,path in enumerate(configs):
    dest=frozen/f'config-{i}.config';dest.write_bytes(Path(path).read_bytes());dest.chmod(0o444)
    rows.append({'name':dest.name,'sha256':digest(dest),'bytes':dest.stat().st_size});assets.append({'name':dest.name,'path':str(dest)})
   runtime_hash=hashlib.sha256(canonical({'ordered_configs':rows,'auxiliary_assets':[],'environment':source['environment']})).hexdigest()
   assert hashlib.sha256(canonical({'ordered_configs':rows[:5],'auxiliary_assets':[],'environment':source['environment']})).hexdigest()==source['identity']['runtime_config_sha256']
   write(out/(mode+'_EFFECTIVE_DUMP.json'),actual)
   manifest['modes'][mode]={'configs':assets,'ordered_configs':rows,'environment':source['environment'],'runtime_config_sha256':runtime_hash,'effective_options':authored(configs),'native_effective_options':actual,'actual_changes_vs_H0':delta,'production_evidence':rec,'H0_control_evidence':ref,'feature_vector':source['identity']['feature_vector'],'ideal_vector':source['identity']['ideal_vector']}
   for workload in ['convolutionSeparable','FWT_7_21']:
    s=copy.deepcopy(json.loads((ORIGINAL/(workload+'_'+mode+'.json')).read_text()));s.update(configs=assets,experiment_id=manifest['experiment_id'],regime=a.profile,qualified_release='PENDING_LANE5_INDEPENDENT_PROFILE_QUALIFICATION')
    s['identity']['runtime_config_sha256']=runtime_hash;s['producer_profile_manifest']=str(out/'PROFILE_MANIFEST.json');write(out/(workload+'_'+mode+'.json'),s)
  bd=manifest['modes']['B16_BANKED']['native_effective_options'];ud=manifest['modes']['U_WB16']['native_effective_options'];assert {k for k in bd if bd[k]!=ud[k]}=={'-gpgpu_ep_l2_ft_mode'}
  write(out/'PROFILE_MANIFEST.json',manifest);r['manifest_sha256']=digest(out/'PROFILE_MANIFEST.json');r['status']='AFFECTED_PRODUCTION_PASS_PENDING_INDEPENDENT_ADMISSION'
 except BaseException as e:r['status']='FAILED_ATTEMPT_RETAINED';r['error']=repr(e);raise
 finally:
  if lease:reg.release_build(lease,'lane3');r['lease_released']=True
  r['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(out/'RECEIPT.json',r)
 print(json.dumps({'profile':a.profile,'status':r['status'],'out':str(out)}))
if __name__=='__main__':main()
