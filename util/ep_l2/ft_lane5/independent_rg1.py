"""Separate real ready-path RG1 qualification replay; no compiler or applications."""
import argparse,json,re,resource,subprocess
from pathlib import Path
import independent_microopt as common
from registry import Registry,write_json
from run import require,digest,asset_manifest
from independent_headroom_r19 import safe

REPO=common.REPO
PUB='4e920696bde91618b44faab769ff490b6cddd51e'
PACK='docs/ep_l2/review_packs/RG1_RECOVERY_LANE1_PRODUCER_r1'
HAND=Path('/workspace/ep_l2_ft20261016_shared/lane1/RG1_PRODUCER_RELEASE_r1.json')
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results/independent_rg1_runtime_r1')
def published(n):return common.git('show',PUB+':'+PACK+'/'+n)
def audit():
 common.audit();h=json.loads(HAND.read_text());require(h['publication_commit']==PUB and h['status']=='PRODUCER_RG1_PASS_PENDING_LANE5' and h['same_single_formal_build_as_MQ2'] is True and h['new_builds_for_RG1']==0,'No exact official RG1 producer')
 remote=common.git('rev-parse','refs/remotes/origin/hrl/ep-l2-ft20261016-lane1-v1').decode().strip();require(subprocess.run(['git','merge-base','--is-ancestor',PUB,remote],cwd=REPO).returncode==0,'RG1 not fetched from GitHub');require(all(h[k]==v for k,v in common.IDENTITY.items()) and digest(h['binary'])==common.IDENTITY['binary_sha256'],'RG1 runtime changed')
 raw=json.loads(published('RAW_FILE_MANIFEST.json'))
 for path,row in raw.items():require(Path(path).stat().st_size==row['bytes'] and digest(path)==row['sha256'],'RG1 published raw changed')
 p=json.loads(Path(h['producer_receipt']).read_text());off=json.loads(Path(h['same_binary_OFF_ready_witness_receipt']).read_text());require(Path(h['producer_receipt']).read_bytes()==published('rg1_recovery_native_r1/RECEIPT.json') and Path(h['same_binary_OFF_ready_witness_receipt']).read_bytes()==published('rg1_recovery_off_witness_r1/RECEIPT.json'),'RG1 receipts not exact publishedbytes')
 require(p['status']=='PRODUCER_RG1_PASS_PENDING_LANE5' and len(p['tests'])==10 and off['status']=='PASS_SAME_BINARY_SIX_RG1_OFF_READY_WITNESSES' and len(off['commands'])==6,'RG1 positive/OFF coverage missing')
 prior=Path(p['reused_same_binary_OFF_receipt']['path']);require(digest(prior)==p['reused_same_binary_OFF_receipt']['sha256'] and json.loads(prior.read_text())['binary_sha256']==h['binary_sha256'],'Different OFF runtime reused')
 independent=Path('/workspace/ep_l2_potential20261017_lane5_results/independent_mq2_runtime_r3/RECEIPT.json');j=json.loads(independent.read_text());require(j['status']=='INDEPENDENT55_NATIVE_6_CONFIG_5_GUARDS_PASS_ELEVEN_REVIEW_PENDING' and j['source_identity']==common.IDENTITY,'No actual samebinary Lane5 original31/OFF evidence')
 for row in j['tests']:require(digest(row['log'])==row['sha256'] and digest(row['command'][0])==row['executable_sha256'],'Same-binary independent OFF evidence changed')
 for path,sha in p['archives_sha256'].items():require(digest(path)==sha,'RG1 native archive changed')
 for row in p['commands']+off['commands']:
  require(row.get('process') and digest(row['log'])==row['log_sha256'] and 'resource_stop' not in row,'Missing real RG1 producer execution')
  if row.get('expected_failure'):require(row['case_name'] in {'reject_combined','reject_P2','reject_Ideal','reject_quota','reject_legacy'} and row['exit_code']==134 and 'EP-L2 service candidate supports single-factor' in Path(row['log']).read_text(),'Wrong RG1 guard')
  else:require(row['exit_code']==0,'Unexpected RG1 producer failure')
 return h,p,off
def validate(name,cmd,text):
 if '_partition_' in name or name.startswith('OFF_'):
  on=int(cmd[-2]);offset=int(cmd[-1]);require(on in (0,1) and offset in (0,4096),'Wrong ready witness arguments')
  require(re.search(r'RG1 real partition response FIFO full, retained response bank[0-3], ReturnQ fill ready, services='+str(on)+' enabled='+str(on)+r' PASS',text) and 'RG1 actual partition exact-once/sector-version/physical-P1/drain PASS' in text,'Actual FIFO-full samebank-ready opportunity or identity/data/drain absent')
  peaks=re.findall(r'EPL2STRUCTV1\|BANK_PEAK\|slice=0\|ops_per_physical_cycle=1\|bank0=(\d+)\|bank1=(\d+)\|bank2=(\d+)\|bank3=(\d+)',text);require(len(peaks)==1 and max(map(int,peaks[0]))<=1,'Ready-path physical P1 violated')
 elif name=='RG1_bounded_identity_arbiter':
  for mode,s in [(1,0),(1,1),(2,0)]:require(f'RG1 bounded arbiter mode{mode} s64{s} ready-change/late-retry/age/identity/cancel/generation/P1 PASS' in text,'Bounded live/cancel/generation/age check missing')
 else:
  marker=('U_WB16 default quota-OFF actual staging17 (>16), same1168/in-place/versions/WAD/exact-once/drain PASS' if name=='RG1_Unified_WB_WAD_copy_drain' else 'S64 production versions/exact-once/release-resume/copy stages/WAD128/drain PASS');require(marker in text,'RG1 real WB/WAD/copy/reference drain suite missing')
def main():
 global OUT
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=OUT);ap.add_argument('--reuse-marker-tool-failure',type=Path);a=ap.parse_args();h,p,off=audit();OUT=a.out;OUT.mkdir(exist_ok=False);common.OUT=OUT;resource.setrlimit(resource.RLIMIT_CORE,(0,0));r=Registry();lease=None;report={'status':'RUNNING','source_identity':common.IDENTITY,'producer_publication':PUB,'compiler_started':False,'application_starts':0,'tests':[],'constructors':[],'guards':[],'scientific_certificate':False,'reused_exact_same_binary_OFF':{'path':'/workspace/ep_l2_potential20261017_lane5_results/independent_mq2_runtime_r3/RECEIPT.json','sha256':digest('/workspace/ep_l2_potential20261017_lane5_results/independent_mq2_runtime_r3/RECEIPT.json')}}
 reused={}
 if a.reuse_marker_tool_failure:
  prior=json.loads(a.reuse_marker_tool_failure.read_text());require(prior['status']=='FAILED_PRESERVE_NO_RG1_APPLICATION_AUTHORITY' and prior['source_identity']==common.IDENTITY and prior.get('error')=="InvalidEvidence('RG1 real WB/WAD/copy/reference drain suite missing')" and len(prior['tests'])==9 and prior['tests'][-1]['case']=='RG1_Unified_WB_WAD_copy_drain','Only exact audited Unified marker tool failure may reuse executions')
  for row in prior['tests']:
   require(row['exit_code']==0 and digest(row['log'])==row['sha256'] and digest(row['command'][0])==row['executable_sha256'],'Prior actual RG1 fixture changed');validate(row['case'],row['command'],Path(row['log']).read_text());row['status']='ACTUAL_ASSERTIONS_PASS';reused[row['case']]=row
  report['retained_marker_tool_failure']={'path':str(a.reuse_marker_tool_failure),'sha256':digest(a.reuse_marker_tool_failure),'reason':'Use exact actual uncapped Unified quota-OFF native marker; preserve and revalidate nine successful executions without rerun.'}
 try:
  safe();lease=r.build_lease('lane5',cpu=1,memory=4*2**30);report['lease_id']=lease
  for name,cmd in p['planned_tests']+[(Path(v['log']).stem,v['command'][2:]) for v in off['commands']]:
   row=reused.get(name) or common.execute(cmd,name,report);require(row['command']==cmd,'Reused RG1 command differs');report['tests'].append(row);write_json(OUT/'RECEIPT.json',report);require(row['exit_code']==0,'Independent RG1 execution failed');validate(name,cmd,Path(row['log']).read_text());row['status']='ACTUAL_ASSERTIONS_PASS'
  for name,profile in p['profiles'].items():
   require(asset_manifest(profile['configs'],ordered=True)==profile['ordered_config_manifest'],'RG1 config changed');old=next(v for v in p['commands'] if v.get('case_name')=='effective_'+name);cmd=old['command'][2:];require(digest(cmd[0])==p['effective_entry_sha256'],'RG1 effective exe changed');row=common.execute(cmd,'effective_'+name,report);report['constructors'].append(row);text=Path(row['log']).read_text();require(row['exit_code']==0 and common.native_options(text)==common.native_options(Path(old['log']).read_text()) and 'PARALLEL_EFFECTIVE_PASS|' in text,'RG1 native config differs');row['status']='ACTUAL_CONSTRUCTOR_PASS'
  for old in p['commands']:
   if not old.get('expected_failure'):continue
   row=common.execute(old['command'][2:],old['case_name'],report);report['guards'].append(row);require(row['exit_code']==-6 and 'EP-L2 service candidate supports single-factor' in Path(row['log']).read_text(),'RG1 expected constructor rejection failed');row['status']='EXPECTED_NATIVE_GUARD_PASS'
  audit();require(len(report['tests'])==16 and len(report['constructors'])==6 and len(report['guards'])==5,'Independent RG1 coverage incomplete');report['status']='INDEPENDENT16_RG1_READY_REFERENCE_6_CONFIG_5_GUARDS_PASS_REVIEW_PENDING'
 except BaseException as e:report['status']='FAILED_PRESERVE_NO_RG1_APPLICATION_AUTHORITY';report['error']=repr(e);raise
 finally:
  if lease:r.release_build(lease,'lane5')
  report['lease_released']=bool(lease);write_json(OUT/'RECEIPT.json',report)
 print(report['status'])
if __name__=='__main__':main()
