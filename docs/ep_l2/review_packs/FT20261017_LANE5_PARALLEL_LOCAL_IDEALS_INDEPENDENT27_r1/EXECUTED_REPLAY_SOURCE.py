"""Independent changed-runtime checks; uses only official existing executables."""
import sys,json,subprocess,os,time,signal,resource
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'util/ep_l2/ft_lane5'))
from registry import Registry,write_json,process_identity,local_resources
from run import digest,require,process_tree_rss,terminate_owned
from independent_headroom_r19 import safe
repo=Path.cwd();shared=Path('/workspace/ep_l2_ft20261016_shared');hand=json.loads((shared/'lane1/PARALLEL_LOCAL_IDEALS_RELEASE_r1.json').read_text());pub=hand['publication']
remote=subprocess.check_output(['git','rev-parse','refs/remotes/origin/hrl/ep-l2-ft20261016-lane1-v1'],text=True).strip();require(subprocess.run(['git','merge-base','--is-ancestor',pub,remote]).returncode==0,'Official release absent from fetched branch')
raw=Path(hand['producer_receipt_path']).read_bytes();require(raw==subprocess.check_output(['git','show',pub+':'+hand['producer_receipt_repository_path']]) and digest(hand['producer_receipt_path'])==hand['producer_receipt_sha256'],'Published producer receipt mismatch');prod=json.loads(raw)
require(len(prod['tests'])==39 and len(prod['planned_tests'])==39,'Producer39 incomplete')
require(digest(hand['binary'])==hand['binary_sha256']==prod['binary_sha256'],'Changed official binary')
for root,key in [(hand['lane1_frozen_equivalent_core'],'core_source_commit'),(hand['lane1_frozen_framework'],'framework_source_commit')]:
 require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==hand[key] and not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root),'Frozen source moved/dirty')
for p,h in prod['assertion_flags_sha256'].items():require(digest(p)==h and '-DNDEBUG' not in Path(p).read_text(),'Assertions/flags changed')
for p,h in prod['archives_sha256'].items():require(digest(p)==h,'Native archive changed')
for p,h in prod['test_executables_sha256'].items():require(digest(p)==h,'Native test binary changed')
for case,row in zip(prod['planned_tests'],prod['tests']):
 require(row['exit_code']==0 and digest(row['log'])==row['log_sha256'] and row['command'][2:]==case[1],'Actual producer matrix/raw changed')
# Minimal affected C16 envelope: both FT modes, host identity, physical clock0/4096/warm,
# lower-full/WAD, A1 competing fill, full directed/reference, symbolic B1 regressions,
# and all8 local-ideal paths. Existing C8-only historical matrix is not replayed.
cases=[v for v in prod['planned_tests'] if not ('_1_8' in v[0] or '_2_8' in v[0])]
out=Path('/workspace/ep_l2_potential20261017_lane5_results/independent_local_ideals_runtime_r1');require(not out.exists(),'Preserve existing independent revision')
r=Registry();safe();lease=r.build_lease('lane5',cpu=1,memory=4*2**30);out.mkdir();report={'status':'RUNNING_NEW_RUNTIME_INDEPENDENT_SCOPE_CHECKS','source_identity':{k:hand[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},'official_publication':pub,'producer39_verified':True,'minimal_case_names':[v[0] for v in cases],'not_replayed':'C8-only OFF variants; no unchanged old7b applications or old producer matrix rerun','lease_id':lease,'tests':[],'compiler_started':False,'application_starts':0};proc=None;resource.setrlimit(resource.RLIMIT_CORE,(0,0))
try:
 for name,cmd in cases:
  safe();log=out/(name+'.log');expected=next(v for v in prod['tests'] if Path(v['log']).stem==name) if any(Path(v['log']).stem==name for v in prod['tests']) else None
  with log.open('xb') as f:
   proc=subprocess.Popen(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'));pid=process_identity(proc.pid);start=time.monotonic();peak=0
   while proc.poll() is None:
    safe();peak=max(peak,process_tree_rss(proc.pid));require(peak<=4*2**30 and time.monotonic()-start<180 and log.stat().st_size<128*2**20,'Independent fixture cap');time.sleep(.2)
  case={'case':name,'command':cmd,'process':pid,'exit_code':proc.returncode,'log':str(log),'sha256':digest(log),'peak_rss_bytes':peak};report['tests'].append(case);require(proc.returncode==0,'Independent actual assertion failure '+name)
  text=log.read_text();require('PASS' in text and 'CLOCK_VIOLATION|' not in text,'Native pass/clock closure absent')
  if 'physical_clock' in name or 'warm_clock' in name:require('violations=0|max_grants_per_physical_bank_cycle=1' in text,'Physical-clock gate')
  case['status']='ACTUAL_ASSERTIONS_PASS';write_json(out/'RECEIPT.json',report);print(name,'PASS',flush=True);proc=None
 for p,h in prod['archives_sha256'].items():require(digest(p)==h,'Archive moved during independent checks')
 report['status']='AFFECTED_NEW_RUNTIME_ASSERTIONS_PASS_ELEVEN_AND_MODE_REVIEW_PENDING'
except BaseException as e:
 report.update(status='FAILED_RETAIN_ALL_NO_APPLICATION',error=repr(e));raise
finally:
 if proc:terminate_owned(proc)
 r.release_build(lease,'lane5');report['lease_released']=True;write_json(out/'RECEIPT.json',report)
print(json.dumps({'status':report['status'],'actual_checks':len(report['tests'])}))
