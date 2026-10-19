"""Read-only independent prior GEMM qualification; never runs model or writes AG3."""
from common import *
from mapping_roles import verify_file
from strict_screen import parse_full,compare_calibration,pipeline_contract,echo,input_identity
import re
AG3='2f3a8c4b27780e2bf3818949a6e5356d9fd62327'
C='c8090115bd57512b1b23fca7d925301fa620c751'
OLD=PACK.parent/'DTC_LANE_AG3_AE_AD_SCREEN_V1'
ORAW=Path('/workspace/dtc-lane-ag3-aead-screen-174-v1/raw')
RUN=ORAW/'attempts/BASE_GEMM_8b6006aa-610e-41cf-82f0-135f80e449cf'

def main():
 rows=[]
 def check(name,old,new,equal=True,source=None):
  rows.append(dict(item=name,old_AG3_authority=old,new_AG4_expected=new,difference='NONE' if equal else dict(old=old,new=new),verdict='PASS' if equal else 'STOP',source=source))
 def record(name,fn):
  try:fn()
  except Exception as e:check(name,'REQUIRED_CLOSED',repr(e),False)
 # Verify authoritative old pack bytes against fetched fixed commit.
 names=['LATEST_REPORT.md','ROOT_CAUSE_AND_FOLLOWUP.md','STOP_EVIDENCE.json','COMPLETION_AUDIT.md','FULL_MATRIX.tsv','PRODUCTION_RUNNER_CONTRACT.md','EXECUTABLE_PREREGISTRATION.json','NEW_BUILD_IDENTITY.json','ACTUAL_LOADER_LIFECYCLE_EVIDENCE.json','ACTUAL_OPTIONS_IDENTITY_REVIEW.json']
 for name in names:
  data=blob(FW_REPO,AG3,str((OLD/name).relative_to(FW)))
  check('published_AG3_'+name,hashlib.sha256(data).hexdigest(),sha(OLD/name),data==(OLD/name).read_bytes(),source=AG3)
 check('Core_HEAD_clean',C,git(CORE,'rev-parse','HEAD'),git(CORE,'rev-parse','HEAD')==C and not git(CORE,'status','--porcelain'))
 check('X2_ancestor',X2,git(CORE,'merge-base',X2,C),git(CORE,'merge-base',X2,C)==X2)
 src=json.loads((OLD/'SOURCE_FILES_SHA256.json').read_text());source_rows=[]
 for row in src:
  repo=CORE_REPO if row['repository']=='Core' else FW_REPO;commit=C if row['repository']=='Core' else FRAMEWORK_BUILD
  local=CORE/row['path'] if row['repository']=='Core' else FW/row['path']
  expected=row['sha256'];actual=sha(local) if local.is_file() else 'MISSING'
  data=blob(repo,commit,row['path'])
  source_rows.append(dict(**row,current_sha256=actual,git_sha256=hashlib.sha256(data).hexdigest(),pass_identity=expected==actual==hashlib.sha256(data).hexdigest()))
 table(PACK/'SOURCE_REUSE_SHA256.tsv',source_rows)
 check('all_original_source_files',len(src),sum(r['pass_identity'] for r in source_rows),all(r['pass_identity'] for r in source_rows),source=sha(PACK/'SOURCE_REUSE_SHA256.tsv'))
 build=json.loads((OLD/'NEW_BUILD_IDENTITY.json').read_text())
 for path,e in build['ELFs'].items():
  actual=sha(path);notes=subprocess.check_output(['/usr/bin/readelf','-nW',path],text=True)
  check('actual_ELF_SHA:'+path,e['sha256'],actual,e['sha256']==actual)
  check('actual_build_id:'+path,re.findall('Build ID: (\\w+)',e['readelf_notes']),re.findall('Build ID: (\\w+)',notes),notes==e['readelf_notes'])
 for label in ['combined-final','trace-final']:
  path=Path('/workspace/dtc-lane-ag3-aead-screen-174-v1/build')/label/'compile_commands.json'
  check('actual_compile_commands:'+label,build['compile_commands_sha'][label],sha(path),sha(path)==build['compile_commands_sha'][label])
 seen={e['path']:e for m in json.loads((OLD/'RUNTIME_MAPPING_MANIFESTS.json').read_text()).values() for e in m['files']}
 for path,e in seen.items():
  def verify(e=e):
   current=verify_file(e);check('runtime_role:'+e['path'],dict(sha256=e['sha256'],identity=e['identity'],role=e['role']),dict(sha256=current['sha256'],identity=current['identity'],role=e['role']),source=sha(OLD/'RUNTIME_MAPPING_MANIFESTS.json'))
  record('runtime_role:'+path,verify)
 # Public indices and byte-identical published receipts close old raw binding.
 public_index=list(csv.DictReader((OLD/'RUN_ARTIFACT_INDEX.tsv').open(),delimiter='\t'))
 for point in ['BASE_GEMM','BASE_Gaussian']:
  entry=next(r for r in public_index if r['point']==point);oldrun=Path(entry['raw'])
  for name,key in [('FILES_SHA256.tsv','raw_index_sha256'),('STRICT.json','strict_sha256'),('ENGINE/TERMINAL.json','engine_terminal_sha256')]:
   check('published_raw_binding:'+point+':'+name,entry[key],sha(oldrun/name),entry[key]==sha(oldrun/name),source=sha(OLD/'RUN_ARTIFACT_INDEX.tsv'))
  receipts=OLD/'execution_receipts'/(point+'_'+entry['attempt_uuid'])
  for receipt in receipts.rglob('*'):
   if receipt.is_file():
    real=oldrun/receipt.relative_to(receipts)
    check('published_receipt:'+point+':'+str(receipt.relative_to(receipts)),sha(receipt),sha(real),receipt.read_bytes()==real.read_bytes(),source='AG3 published execution_receipts')
 # Independent parses of real old stdout; no collect() call (that writes STRICT).
 spec=json.loads((OLD/'specs/BASE_GEMM.json').read_text());start=json.loads((RUN/'RUN_START.json').read_text());term=json.loads((RUN/'RUN_TERMINAL.json').read_text());strict=json.loads((RUN/'STRICT.json').read_text())
 index=list(csv.DictReader((RUN/'FILES_SHA256.tsv').open(),delimiter='\t'))
 artifact_checks=[]
 for row in index:
  path=RUN/row['path'];actual=sha(path)
  artifact_checks.append(dict(path=str(path),expected_sha256=row['sha256'],actual_sha256=actual,pass_identity=actual==row['sha256']))
 table(PACK/'AG3_GEMM_ARTIFACT_RECHECK.tsv',artifact_checks)
 check('all_AG3_original_run_artifacts',len(index),sum(r['pass_identity'] for r in artifact_checks),all(r['pass_identity'] for r in artifact_checks),source=sha(PACK/'AG3_GEMM_ARTIFACT_RECHECK.tsv'))
 text=(RUN/'simulator.stdout').read_text();parsed=parse_full(text,'GEMM');cal=compare_calibration(parsed,json.loads((OLD/'controls/GEMM_CALIBRATION_REFERENCE.json').read_text()));pipeline_contract(text,'BASE',parsed['metrics'][-1])
 check('natural_exit0_and_loaded_identity',True,term['returncode']==0 and term['forced_reason'] is None and term['identity_pass'],term['returncode']==0 and term['forced_reason'] is None and term['identity_pass'])
 check('old_strict_acceptance',True,strict['performance_accepted'],strict['performance_accepted'] is True)
 for name,key,val in [('integer_cycles','cycles',1071405),('kernels','kernel_count',1),('CTA','CTA',1024),('active_instructions','active_instructions',739246080)]:check(name,val,parsed[key],parsed[key]==val)
 check('all270effective_options',spec['expected_full_effective_options'],parsed['effective_options'],len(parsed['effective_options'])==270 and parsed['effective_options']==spec['expected_full_effective_options'])
 check('T1_C_full_common_and_traffic','PASS_FULL_INPUT_CYCLES_AND_ALL_FROZEN_COMMON_METRICS',cal['status'],cal['status']=='PASS_FULL_INPUT_CYCLES_AND_ALL_FROZEN_COMMON_METRICS')
 for e in spec['configs']+start['config_copies']:check('config:'+e['path'],e['sha256'],sha(e['path']),sha(e['path'])==e['sha256'])
 expected=json.loads((PACK/'AG4_CONTROL_ENVIRONMENT_EXPECTATION.json').read_text())
 for k,v in expected.items():
  if k=='new_config_files':
   for e in v:check('AG4_config_expected:'+e['path'],e['sha256'],sha(e['path']),e['sha256']==sha(e['path']))
  else:check('AG4_control_condition:'+k,spec[k],v,spec[k]==v,source=sha(PACK/'AG4_CONTROL_ENVIRONMENT_EXPECTATION.json'))
 record('full_original_members',lambda:check('fresh_GEMM_member_identity','PASS_FRESH_FROZEN_SHA_PLUS_CURRENT_STAT_STABILITY',input_identity(spec)['status'],source=sha(PACK/'ORIGINAL_MEMBERS_SHA256.tsv')))
 check('only_external_observer_repair',dict(Core=C,framework_build=FRAMEWORK_BUILD,binary_rebuild=False,model_changes=False),dict(Core=C,framework_build=FRAMEWORK_BUILD,binary_rebuild=False,model_changes=False))
 passed=all(r['verdict']=='PASS' for r in rows)
 result=dict(status='PASS_REUSE_AG3_GEMM_BASE_FOR_AG4_DISCOVERY' if passed else 'STOP_GEMM_BASE_REUSE_NOT_QUALIFIED',utc=now(),AG3_commit=AG3,prior_run=str(RUN),prior_UUID=spec['attempt_uuid'],prior_stdout_sha256=sha(RUN/'simulator.stdout'),prior_strict_sha256=sha(RUN/'STRICT.json'),rows=rows,baseline_role='IMPORTED_PRIOR_AG3_FULL_MEASUREMENT_INDEPENDENTLY_QUALIFIED_AS_AG4_CONTROL' if passed else 'NOT_QUALIFIED_NO_NEW_SIMULATIONS',AG4_actual_starts=0,prior_raw_copied=False,prior_raw_modified=False,comparison_cycles=1071405 if passed else 'UNAVAILABLE')
 write(PACK/'AG3_GEMM_BASE_REUSE_QUALIFICATION.json',result)
 print(json.dumps(dict(status=result['status'],checks=len(rows),failed=[r['item'] for r in rows if r['verdict']!='PASS'])))
if __name__=='__main__':main()
