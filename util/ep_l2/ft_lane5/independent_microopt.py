"""Independently replay the published finite-service producer; never compile."""
import argparse,json,os,re,resource,subprocess,time
from pathlib import Path
from registry import Registry,write_json,process_identity
from run import digest,require,process_tree_rss,terminate_owned,asset_manifest
from independent_headroom_r19 import safe
from qualify_r0_1 import check_directed_log

REPO=Path(__file__).resolve().parents[3]
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-microopt20261018-lane1-v1')
FW=Path('/workspace/worktrees/accel-sim-ep-l2-microopt20261018-lane1-v1')
IDENTITY={'core_source_commit':'84359d4ba492acb639a2092fa271e9169038bf7d','framework_source_commit':'197741be9be9b8e390a557d639503b416d8e95f0','binary_sha256':'f0af8515057e315af708a0e3c2fde4a3098b0c0fb3f7014471d8d8c9426f1f30'}
PUB='d035f11e465f8acd9764a3055ae967e62bb5b47f'
PACK='docs/ep_l2/review_packs/MQ2_RECOVERY_LANE1_PRODUCER_r1'
HAND=Path('/workspace/ep_l2_ft20261016_shared/lane1/MQ2_PRODUCER_RELEASE_r1.json')
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results/independent_mq2_runtime_r1')

def git(*a,cwd=REPO):return subprocess.check_output(['git',*a],cwd=cwd)
def published(name):return git('show',PUB+':'+PACK+'/'+name)

def native_options(text):
 section=text.split('NATIVE_EFFECTIVE_OPTIONS_BEGIN\n',1)[1].split('NATIVE_EFFECTIVE_OPTIONS_END',1)[0];out={}
 for line in section.splitlines():
  fields=line.split('#',1)[0].strip().split(None,1)
  if fields and fields[0].startswith('-'):
   value=fields[1].strip() if len(fields)>1 else '';require(fields[0] not in out or out[fields[0]]==value,'Conflicting repeated native option');out[fields[0]]=value
 return out

def audit():
 h=json.loads(HAND.read_text());require(h['publication_commit']==PUB and h['status']=='PRODUCER_MQ2_PASS_PENDING_LANE5','No exact published MQ2 producer')
 remote=git('rev-parse','refs/remotes/origin/hrl/ep-l2-ft20261016-lane1-v1').decode().strip();require(subprocess.run(['git','merge-base','--is-ancestor',PUB,remote],cwd=REPO).returncode==0,'Producer not fetched from GitHub')
 for k,v in IDENTITY.items():require(h[k]==v,'Producer source changed')
 require(digest(h['binary'])==IDENTITY['binary_sha256'],'Released binary changed')
 for root,key in [(CORE,'core_source_commit'),(FW,'framework_source_commit')]:
  require(git('rev-parse','HEAD',cwd=root).decode().strip()==IDENTITY[key] and not git('status','--porcelain','--untracked-files=no',cwd=root),'Dirty or moved producing source')
 vendor=FW/'gpu-simulator/extern/pybind11';require(git('rev-parse','HEAD',cwd=vendor).decode().strip()=='f90c430c3a1ce8f08c09942a5a1c3a797bb2295b' and not git('status','--porcelain','--untracked-files=no',cwd=vendor),'Vendor changed')
 raw=json.loads(published('RAW_FILE_MANIFEST.json'));exes=json.loads(published('TEST_EXECUTABLE_MANIFEST.json'))
 for p,row in {**raw,**exes}.items():require(Path(p).stat().st_size==row['bytes'] and digest(p)==row['sha256'],'Published asset changed: '+p)
 for key,name in [('build_receipt','mq2_recovery_formal_build_r1/BUILD_RECEIPT.json'),('producer_receipt','mq2_recovery_native_r3/RECEIPT.json'),('supplementary_OFF_receipt','mq2_recovery_off_anchors_r1/RECEIPT.json'),('config_manifest','CONFIG_MANIFEST.json')]:require(Path(h[key]).read_bytes()==published(name),'Unpublished receipt/config')
 build=json.loads(Path(h['build_receipt']).read_text());p=json.loads(Path(h['producer_receipt']).read_text());off=json.loads(Path(h['supplementary_OFF_receipt']).read_text())
 require(build['status']=='BUILT_NOT_TESTED_NOT_INDEPENDENTLY_QUALIFIED' and build['compiler_started'] and build['jobs']==2 and build['lease_released'] and build['owned_lock_released'],'Missing formal producer build')
 require(p['status']=='PRODUCER_MQ2_PASS_PENDING_LANE5' and len(p['tests'])==52 and len(set(p['tests']))==52 and len(p['actual_tests'])==52,'Incomplete real producer tests')
 for name,sha in build['assertion_flags_sha256'].items():require(digest(name)==sha and '-DNDEBUG' not in Path(name).read_text(),'Assertions disabled/flags changed')
 for name,sha in {**p['archives_sha256'],**p['fixture_archives_sha256']}.items():require(digest(name)==sha,'Candidate archive changed')
 require(digest(Path(h['producer_receipt']).parent/'clock_s64_fixture')==p['corrected_fixture_executable_sha256'],'Corrected fixture changed')
 old=git('show',IDENTITY['core_source_commit']+':tests/ep_l2/test_ft_memcpy_clock.cc',cwd=CORE).decode();new=git('show',PUB+':util/ep_l2/ft_lane1/mq2_recovery_fixtures/test_ft_memcpy_clock_s64.cc').decode()
 before='  if(mode==1) assert(peak==c && sp->ep_l2_wad_occupancy()>c);'
 after='''  const auto &payload=sp->ft_cache_for_test()->ep_l2_payload_for_test();
  const unsigned actual_fixed_capacity=payload.static_wb_capacity();
  printf("CLOCK_CAPACITY|static_s64=%u|configured_C=%u|actual_fixed_capacity=%u|peak=%u|wad=%u\\n",
      payload.static_s64(),c,actual_fixed_capacity,peak,sp->ep_l2_wad_occupancy());
  if(mode==1) {
    assert(actual_fixed_capacity==(payload.static_s64()?64:c));
    assert(peak==actual_fixed_capacity && sp->ep_l2_wad_occupancy()>actual_fixed_capacity);
  }'''
 require(old.count(before)==1 and old.replace(before,after)==new,'Fixture correction extends beyond actual S64 capacity assertion')
 require(off['status']=='PASS_SAME_BINARY_THREE_MODE_OFF_ANCHORS' and len(off['commands'])==3,'Same-binary OFF opportunity missing')
 for row in p['commands']+off['commands']:
  require(digest(row['log'])==row['log_sha256'] and 'resource_stop' not in row and row.get('process'),'Producer real execution changed')
  if row.get('expected_failure'):require(row['case_name'] in {'reject_combined','reject_P2','reject_Ideal','reject_quota','reject_legacy'} and row['exit_code']==134 and 'EP-L2 service candidate supports single-factor' in Path(row['log']).read_text(),'Wrong expected rejection')
  else:require(row['exit_code']==0,'Unexpected producer failure')
 return h,p,off

def validate_case(name,command,text):
 if name.startswith('MQ2_') and any(name.endswith('_'+v) for v in ['ordinary','unknown','lower-full']):
  mode=int(command[3]);variant=command[-1];require(f'MQ2 opportunity real fill-bank/WB-head/independent-read mode={mode} enabled=1 bypass={int(variant=="ordinary")} PASS' in text and 'MQ2 native exact-once/versions/lower-accept/WAD/head-priority/physical-P1/drain PASS' in text,'MQ2 opportunity/order/version closure absent')
 elif name.startswith('OFF_'):
  require(f'MQ2 opportunity real fill-bank/WB-head/independent-read mode={int(command[3])} enabled=0 bypass=0 PASS' in text and 'MQ2 native exact-once/versions/lower-accept/WAD/head-priority/physical-P1/drain PASS' in text,'OFF opportunities changed')
 elif name.startswith('MQ2_'):
  if '_ft_host_prefill_' in name:base='host_prefill_'+command[-2]+'_16'
  elif '_ft_a1_' in name:base='a1_'+command[-2]+'_16'
  else:base='physical_clock_'+command[-3]+'_16_'+command[-1]
  # The legacy helper assumes all fixed banks have C16 WB slots. S64 is exactly64.
  if '_S64_ft_memcpy_clock_' in name:
   require('CLOCK_CAPACITY|static_s64=1|configured_C=16|actual_fixed_capacity=64|peak=64|' in text and 'FT real partition lower-full/WBUF/WAD/set_done mode=1 C=16 peak=64 PASS' in text,'S64 actual fixed capacity boundary absent')
   require(f'CLOCK_AUDIT|offset={command[-1]}|violations=0|max_grants_per_physical_bank_cycle=1' in text and 'CLOCK_VIOLATION|' not in text,'S64 physical clock failure')
  else:
   case={'case':base,'argv':command[1:]}
   if 'clock' in base:case['required_clock']={'offset':int(command[-1])}
   check_directed_log(case,text)
 else:
  case={'case':name,'argv':command[1:]}
  if 'clock' in name:case['required_clock']={'offset':int(command[-2]) if name.startswith('warm_clock') else int(command[-1])}
  check_directed_log(case,text)

def execute(command,name,report):
 safe();log=OUT/(name+'.log');p=None;started=time.monotonic();peak=0
 try:
  with log.open('xb') as stream:
   p=subprocess.Popen(command,cwd=OUT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
   identity=process_identity(p.pid)
   while p.poll() is None:
    safe();peak=max(peak,process_tree_rss(p.pid));require(peak<4*2**30 and time.monotonic()-started<180 and log.stat().st_size<32*2**20,'Independent directed resource bound');time.sleep(.1)
  return {'case':name,'command':command,'process':identity,'exit_code':p.returncode,'log':str(log),'sha256':digest(log),'executable_sha256':digest(command[0]),'wall_seconds':time.monotonic()-started,'peak_rss_bytes':peak}
 finally:
  if p is not None and p.poll() is None:terminate_owned(p)

def main():
 global OUT
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--execute',action='store_true');ap.add_argument('--out',type=Path,default=OUT);ap.add_argument('--reuse-tool-failure',type=Path);a=ap.parse_args();h,p,off=audit();require(a.execute,'Use explicit --execute after producer audit');OUT=a.out;OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0));r=Registry();lease=None
 report={'status':'RUNNING','source_identity':IDENTITY,'producer_publication':PUB,'producer_receipt_sha256':digest(h['producer_receipt']),'compiler_started':False,'application_starts':0,'scientific_certificate':False,'tests':[],'constructors':[],'guards':[]}
 reused={};reused_constructors={}
 if a.reuse_tool_failure:
  prior=json.loads(a.reuse_tool_failure.read_text());warm=(prior.get('error')=="ValueError('Physical bank clock counterexample or missing exact audit')" and len(prior['tests'])==4 and prior['tests'][-1]['case']=='warm_clock_1_8');duplicate=(prior.get('error')=="InvalidEvidence('Repeated native option')" and len(prior['tests'])==55 and len(prior['constructors'])==1);require(prior['source_identity']==IDENTITY and prior['status']=='FAILED_FROZEN_NO_APPLICATION_AUTHORITY' and (warm or duplicate),'Only exact audited tool failures may reuse executions')
  for row in prior['tests']:
   require(row['exit_code']==0 and digest(row['log'])==row['sha256'] and digest(row['command'][0])==row['executable_sha256'],'Prior actual execution changed');validate_case(row['case'],row['command'],Path(row['log']).read_text());row['status']='ACTUAL_ASSERTIONS_PASS';reused[row['case']]=row
  for row in prior['constructors']:
   require(row['exit_code']==0 and digest(row['log'])==row['sha256'] and digest(row['command'][0])==row['executable_sha256'],'Prior constructor changed');native_options(Path(row['log']).read_text());reused_constructors[row['case']]=row
  report['retained_tool_failure']={'path':str(a.reuse_tool_failure),'sha256':digest(a.reuse_tool_failure),'reason':'Correct warm4096 offset / identical repeated native registration values; preserve and revalidate actual executions, no simulator or fixture change or rerun'}
 try:
  safe();lease=r.build_lease('lane5',cpu=1,memory=4*2**30);report['lease_id']=lease
  for name,command in p['actual_tests']+[(Path(v['log']).stem,v['command'][2:]) for v in off['commands']]:
   result=reused.get(name) or execute(command,name,report);require(result['command']==command,'Reused command mismatch');report['tests'].append(result);write_json(OUT/'RECEIPT.json',report);require(result['exit_code']==0,'Independent native fixture failed '+name);validate_case(name,command,Path(result['log']).read_text());result['status']='ACTUAL_ASSERTIONS_PASS'
  for name,row in p['profiles'].items():
   require(asset_manifest(row['configs'],ordered=True)==row['ordered_config_manifest'],'Producer config changed');old=next(v for v in p['commands'] if v.get('case_name')=='effective_'+name);command=old['command'][2:];require(digest(command[0])==p['effective_entry_sha256'],'Effective executable changed');result=reused_constructors.get('effective_'+name) or execute(command,'effective_'+name,report);require(result['command']==command,'Reused constructor command changed');report['constructors'].append(result);text=Path(result['log']).read_text();require(result['exit_code']==0 and native_options(text)==native_options(Path(old['log']).read_text()) and 'PARALLEL_EFFECTIVE_PASS|' in text,'Native effective option mismatch');result['status']='ACTUAL_CONSTRUCTOR_PASS'
  for old in p['commands']:
   if not old.get('expected_failure'):continue
   result=execute(old['command'][2:],old['case_name'],report);report['guards'].append(result);require(result['exit_code']==-6 and 'EP-L2 service candidate supports single-factor' in Path(result['log']).read_text(),'Wrong independent rejection');result['status']='EXPECTED_NATIVE_GUARD_PASS'
  audit();require(len(report['tests'])==55 and len(report['constructors'])==6 and len(report['guards'])==5,'Incomplete independent replay');report['status']='INDEPENDENT55_NATIVE_6_CONFIG_5_GUARDS_PASS_ELEVEN_REVIEW_PENDING'
 except BaseException as e:report['status']='FAILED_FROZEN_NO_APPLICATION_AUTHORITY';report['error']=repr(e);raise
 finally:
  if lease:r.release_build(lease,'lane5')
  report['lease_released']=bool(lease);write_json(OUT/'RECEIPT.json',report)
 print(report['status'])

if __name__=='__main__':main()
