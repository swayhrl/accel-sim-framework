"""AG6 six fresh UUIDs only after source-bound CPU, runtime and full-input gates."""
from common import *
from strict_screen import input_identity
from mapping_roles import validate_manifest
import uuid,re
OLD=PACK.parent/'DTC_LANE_AG3_AE_AD_SCREEN_V1'
ORDER=['BASE_GEMM','BASE_Gaussian','AE_GEMM','AE_Gaussian','AD_GEMM','AD_Gaussian']

def main():
 assert not list((RAW/'attempts').glob('*/RUN_START.json'))
 assert not (PACK/'UUID_RESERVATIONS.json').exists(),'NO_REGENERATION_OR_REPLACEMENT'
 required={'CPU_AUTHORITY_QUALIFICATION.json':'PASS_CPU_AUTHORITY_RACE_REPAIR','MAPPING_ROLE_REGRESSION.json':'PASS','RUNNER_CPU_QUALIFICATION.json':'PASS_PRODUCTION_RUNNER_CPU_CLOSURE_WITH_DECLARED_ADAPTERS','RESOURCE_POLICY_CPU_TESTS.json':'PASS_PURE_CPU_AG_RESOURCE_POLICY','STRICT_CPU_NEGATIVES.json':'PASS_FULL_CONTROL_POSITIVE_AND_CORRUPTION_NEGATIVES','INPUT_FULL_IDENTITY.json':'PASS_FRESH_ALL_511_MEMBER_SHA256','PRODUCTION_DISPATCH_GENERATION_TESTS.json':'PASS_BOUNDED_FULL_GUARD_DISPATCH','RUNTIME_FREEZE_QUALIFICATION.json':'PASS_CURRENT_RUNTIME_IDENTITY','PAIRED_BASE_GATE_CPU_TESTS.json':'PASS_NEW_SIX_POINT_BASE_AND_BUDGET_GATES'}
 for n,s in required.items():assert json.loads((PACK/n).read_text())['status']==s,(n,s)
 runner_cpu=json.loads((PACK/'RUNNER_CPU_QUALIFICATION.json').read_text())
 assert runner_cpu['runner_sha256']==sha(PACK/'tools/run_screen.py') and runner_cpu['guard_sha256']==sha(PACK/'tools/guarded_process.py')
 for m in json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text()).values():validate_manifest(m)
 assert json.loads((PACK/'USER_AUTHORIZATION.json').read_text())['actual_start_budget']==6
 cpu_receipt=json.loads((RAW/'CPU_PUBLICATION_READBACK.json').read_text())
 assert cpu_receipt['head']==cpu_receipt['fetched_head']==git(FW,'rev-parse','refs/ag6-publication/cpu')
 for row in cpu_receipt['blobs']:
  path=FW/row['path']
  if path.parent==PACK/'tools':assert sha(path)==row['sha256'],'CPU_TESTED_SOURCE_CHANGED'
 known=set()
 for directory in ['DTC_LANE_AG3_AE_AD_SCREEN_V1','DTC_LANE_AG4_AUTHORITY_AE_AD_V1','DTC_LANE_AG_OPT_SCREEN_V1','DTC_LANE_AA5_GAUSSIAN_V1']:
  for previous in (PACK.parent/directory).glob('UUID*'):
   known.update(re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',previous.read_text()))
 rows=[];specnames=[]
 for i,point in enumerate(ORDER):
  value=str(uuid.uuid4());assert value not in known and value not in {r['attempt_uuid'] for r in rows}
  spec=json.loads((OLD/f'specs/{point}.json').read_text());spec.update(order=i,attempt_uuid=value,cohort='AG6_PAIRED_DISCOVERY_AE_AD_V1',primary_ratio='same-cohort accepted same-input BASE cycles / accepted ON cycles')
  # Reuse the exact actual ELF/library paths/environment, read-only. All outputs
  # go to AG6. Only config-copy paths move; option bytes and all270 values match.
  spec['configs']=[dict(path=str(PACK/'config'/Path(e['path']).name),sha256=e['sha256']) for e in spec['configs']]
  for e in spec['configs']:assert sha(e['path'])==e['sha256']
  spec['BASE_reference_sha256']=sha(PACK/('controls/'+spec['workload']+'_CALIBRATION_REFERENCE.json'))
  input_identity(spec);name=f'specs/{point}.json';write(PACK/name,spec,exclusive=True);specnames.append(name)
  rows.append({k:spec[k] for k in ['order','point','arm','workload','attempt_uuid']})
 write(PACK/'UUID_RESERVATIONS.json',dict(cohort='AG6_PAIRED_DISCOVERY_AE_AD_V1',actual_start_cap=6,max_concurrency=1,rows=rows,known_AG3_UUIDs=sorted(known),no_replacement=True,UUID_method='uuid.uuid4',all_generated_after_CPU_runtime_and_full_input_PASS=True),exclusive=True)
 files={str(q.relative_to(PACK)):sha(q) for q in sorted(PACK.rglob('*')) if q.is_file() and '__pycache__' not in q.parts and q.name not in {'EXECUTABLE_PREREGISTRATION.json','FILES_SHA256.tsv','LATEST_REPORT.md'}}
 write(PACK/'EXECUTABLE_PREREGISTRATION.json',dict(status='EXECUTABLE_PREREGISTERED_NOT_YET_STARTED',utc=now(),goal='USER_AUTHORIZED_AG6_SIX_POINT_COMPLETE_PAIRING',cohort='AG6_PAIRED_DISCOVERY_AE_AD_V1',core_commit='c8090115bd57512b1b23fca7d925301fa620c751',framework_compilation_source=FRAMEWORK_BUILD,ordered_specs=specnames,actual_start_cap=6,max_concurrency=1,files=files,resource_version='AG3_DISCOVERY_RESOURCE_R2_V1',timeout_seconds=7200,retries=0,real_attempts_before_registration=0,imported_BASE_controls=False,first_actual_gate='GEMM_FULL_NATURAL_EXIT0_1071405_ALL_COMMON_TRAFFIC_EXACT_THEN_GAUSSIAN_3278356_ALL_COMMON_TRAFFIC_EXACT',hard_failure='STOP_NO_RETRY_NO_REPLACEMENT_NO_SEVENTH_START',execution_gate='COMMIT_PUSH_FETCH_BACK_HEAD_TREE_ALL_BLOBS_CLEAN_PLUS_FRESH_RESOURCE_AUTHORITY_BEFORE_EACH_FORK_EXEC',no_paper_or_history_modifications=True),exclusive=True)
 print(json.dumps(dict(status='LOCAL_EXECUTABLE_PREREGISTRATION_REQUIRES_PUBLICATION',files=len(files),rows=rows)))
if __name__=='__main__':main()
