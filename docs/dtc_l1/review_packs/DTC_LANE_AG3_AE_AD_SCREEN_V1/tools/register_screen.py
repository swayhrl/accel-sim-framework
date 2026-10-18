"""Freeze executable AG3 six-point preregistration; does not launch any target."""
from common import *
from mapping_roles import validate_manifest
from strict_screen import ordered,input_identity
import uuid,re,xml.etree.ElementTree as ET


def main():
 assert not list((RAW/'attempts').glob('*/RUN_START.json'))
 core=git(CORE,'rev-parse','HEAD');assert core=='c8090115bd57512b1b23fca7d925301fa620c751' and not git(CORE,'status','--porcelain')
 assert git(CORE,'rev-parse','refs/ag3-publication/core-final')==core
 expected={
  'SOURCE_ALLOWLIST.json':'PASS_STATIC_ALLOWLIST_AND_PROTECTED_BODIES',
  'CPU_CTEST_QUALIFICATION.json':'PASS_11_OF_11_INCLUDING_ORIGINAL_7_AE_AD_AND_FOUR_COMBINATIONS',
  'X2_REFERENCE_7_CTEST.json':'PASS_7_OF_7_ORIGINAL_X2',
  'X2_REFERENCE_NORMAL_EXPORT_CPU.json':'PASS_X2_REFERENCE_REAL_NORMAL_PRINT_CPU',
  'CPU_CASES.json':'PASS_BOUNDED_CPU_FRONTEND',
  'AD_OFF_CPU.json':'PASS_CPU_OFF_DIFFERENTIAL_ONLY',
  'AD_NORMAL_CPU.json':'PASS_EXISTING_CPU_NORMAL_ON_EXPORT_SPARSE_FRONTEND_SCOPE_ONLY',
  'AD_MODE_CPU.json':'PASS_EXISTING_PRODUCTION_OO_CONSTRUCTOR_MODE_GUARD_ONLY',
  'ACTUAL-LDST-FINAL_RESULT.json':'PASS_ACTUAL_LDST_OFF_EQUIVALENCE_AND_AE_K1_SAFETY',
  'OPTIONS-FINAL_RESULT.json':'PASS_ALL_OPTIONS_OFF_EQUALS_X2_AND_OLD_T_PUBLIC_CONFIG',
  'PRODUCTION_WRAPPER_CPU.json':'PASS_INITIAL_PRODUCTION_GUARD_CPU_CASES',
  'RUNNER_CPU_QUALIFICATION.json':'PASS_PRODUCTION_RUNNER_CPU_CLOSURE_WITH_DECLARED_ADAPTERS',
  'GUARD_EXCEPTION_CPU_TESTS.json':'PASS_FIVE_PARENT_FAULT_AND_FORCE_STOP_CASES',
  'OOM_WATCHDOG_CPU_TESTS.json':'PASS_CPU_OWNED_PIDFD_STOP_AND_READER_FAILURE',
  'RESOURCE_POLICY_CPU_TESTS.json':'PASS_PURE_CPU_AG_RESOURCE_POLICY',
  'STRICT_CPU_NEGATIVES.json':'PASS_FULL_CONTROL_POSITIVE_AND_CORRUPTION_NEGATIVES',
  'INPUT_FULL_IDENTITY.json':'PASS_FRESH_ALL_511_MEMBER_SHA256'}
 for name,status in expected.items():assert json.loads((PACK/name).read_text())['status']==status,(name,status)
 for result,key,path in [('RUNNER_CPU_QUALIFICATION.json','runner_sha256','tools/run_screen.py'),('RUNNER_CPU_QUALIFICATION.json','guard_sha256','tools/guarded_process.py'),('PRODUCTION_WRAPPER_CPU.json','guard_sha256','tools/guarded_process.py'),('STRICT_CPU_NEGATIVES.json','strict_sha256','tools/strict_screen.py')]:assert json.loads((PACK/result).read_text())[key]==sha(PACK/path),result
 component=Path('/workspace/dtc-lane-ag3-aead-screen-174-v1/ag2-component/raw')
 assert len(json.loads((component/'LEGACY_NINE_REPLAY.json').read_text())['cases'])==9
 c=json.loads((component/'final-cpu/MAPPING_ROLE_TEST_RESULTS_V2.json').read_text());assert c['status']=='PASS_ALL_CPU_CASES' and len(c['cases'])==34
 write(PACK/'AG2_COMPONENT_REQUAL.json',dict(status='PASS_OLD_NINE_AND_34_CURRENT_CPU_REQUAL',legacy=json.loads((component/'LEGACY_NINE_REPLAY.json').read_text()),cases=c,raw_root=str(component),real_simulator_starts=0))
 role_manifests=json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text())
 for m in role_manifests.values():validate_manifest(m)
 identities=json.loads((PACK/'NEW_BUILD_IDENTITY.json').read_text());assert identities['assertions_enabled']
 runtime=str(BUILD/'trace-final/accel-sim.out');library=str(BUILD/'combined-final/libcudart.so');assert runtime in role_manifests
 assert any(x['path']==library for x in role_manifests[runtime]['files'])
 # Fixed-object Git records only; no filesystem-wide UUID or alternate-trace scan.
 known=set();regex=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
 for ref in ['refs/ag3-inputs/ag2','refs/ag3-inputs/ag','refs/ag3-inputs/aa5','refs/ag3-inputs/ae','refs/ag3-inputs/ad','refs/ag3-inputs/t-control']:
  p=subprocess.run(['git','-C',str(FW_REPO),'grep','-hoE',regex,ref,'--','docs/dtc_l1'],capture_output=True,text=True)
  assert p.returncode in (0,1);known.update(re.findall(regex,p.stdout))
 reservations=PACK/'UUID_RESERVATIONS.json'
 if not reservations.exists():
  rows=[]
  for i,point in enumerate(['BASE_GEMM','BASE_Gaussian','AE_GEMM','AE_Gaussian','AD_GEMM','AD_Gaussian']):
   value=str(uuid.uuid4());assert value not in known and value not in [r['attempt_uuid'] for r in rows]
   arm,workload=point.split('_');rows.append(dict(order=i,point=point,arm=arm,workload=workload,attempt_uuid=value))
  write(reservations,dict(cohort='AG3_DISCOVERY_OPT_AE_AD_V1',actual_start_cap=6,max_concurrency=1,UUID_method='uuid.uuid4 standard library',known_frozen_Git_UUID_count=len(known),known_UUID_set_sha256=hashlib.sha256('\n'.join(sorted(known)).encode()).hexdigest(),rows=rows,no_replacement=True),exclusive=True)
 rows=json.loads(reservations.read_text())['rows'];assert len(rows)==len({r['attempt_uuid'] for r in rows})==6
 options=json.loads((PACK/'OPTIONS-FINAL_RESULT.json').read_text())['expected'];specs=[]
 for row in rows:
  workload=row['workload'];arm=row['arm'];old=json.loads((PACK/f'inputs/T/inputs/{workload}_OO128_SPEC.json').read_text());body=ordered(workload)
  commands=(PACK/f'inputs/T/inputs/{workload}_kernelslist.g').read_text().splitlines();control=json.loads((PACK/f'controls/{workload}_CALIBRATION_REFERENCE.json').read_text());values=options[workload+'_'+arm]
  assert int(values['-gpgpu_dtc_l1_tag_hash_bankrow'][0])+int(values['-gpgpu_dtc_l1_progressive_wakeup'][0])==int(arm!='BASE')
  assert values['-gpgpu_dtc_l1_invalidate_on_source_event']==['0']
  if workload=='Gaussian':assert len(body)==510 and len(commands)==513 and control['CTA']==65790 and old['expected_instructions']==283685120
  spec=dict(**row,cohort='AG3_DISCOVERY_OPT_AE_AD_V1',core_commit=core,source_base=X2,framework_source=FRAMEWORK_BUILD,
     trace_list=old['trace_list'],trace_list_sha256=old['trace_list_sha256'],expected_kernels=len(body),expected_commands=commands,
     expected_instructions=old['expected_instructions'],expected_CTA=control['CTA'],full_processing_window='ALL_COMMANDS_ALL_KERNELS_ALL_CTA_NO_PREFIX_NATURAL_EXIT0',
     runtime_path=runtime,runtime_sha256=sha(runtime),runtime_library_path=library,runtime_library_sha256=sha(library),
     runtime_environment=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',LD_LIBRARY_PATH=str(BUILD/'combined-final'),CUDA_VISIBLE_DEVICES=''),
     expected_embedded_core_version=re.search(r'="(.*?)"',identities['Core_version_text'])[1],expected_embedded_framework_version=re.search(r'="(.*?)"',identities['Framework_version_text'])[1],
     expected_full_effective_options=values,configs=[dict(path=str(PACK/'config'/n),sha256=sha(PACK/'config'/n)) for n in ['FAST64_OO.config','FINITE_PRIMARY_COMMON.config','trace.config',arm+'.config']],
     timeout_seconds=7200,retries=0,max_new_sim_concurrency=1,resource_policy_version='AG3_DISCOVERY_RESOURCE_R2_V1',primary_ratio='same-input new AG3 BASE cycles / same-input new single-ON cycles',BASE_reference_sha256=sha(PACK/f'controls/{workload}_CALIBRATION_REFERENCE.json'))
  input_identity(spec);path='specs/'+row['point']+'.json';write(PACK/path,spec);specs.append(path)
 write(PACK/'QUALIFICATION_DECISION.json',dict(status='CPU_QUALIFIED_NEW_AE_AD_CORE_AND_PRODUCTION_WRAPPER_NOT_YET_GPU_PASS',core=core,evidence={n:sha(PACK/n) for n in expected},AG2='9/9 and34/34 reproduced',full_GPU_correctness='UNPROVEN',new_simulator_starts=0))
 files={}
 for prefix in ['tools','inputs','source_patches','config','controls']:
  for path in sorted((PACK/prefix).rglob('*')):
   if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ['.pyc','.log']:files[str(path.relative_to(PACK))]=sha(path)
 for name in ['USER_AUTHORIZATION.txt','INPUT_FETCH_READBACK.json','SOURCE_ALLOWLIST.json','SOURCE_DIFF.patch','SOURCE_SHA256.tsv','SOURCE_FILES_SHA256.json','NEW_BUILD_IDENTITY.json','CORE_PUBLICATION_READBACK.json','UUID_RESERVATIONS.json','RUNTIME_MAPPING_MANIFESTS.json','RUNTIME_STATIC_ELF_CLOSURE.json','RESOURCE_CONTRACT.md','METRIC_DICTIONARY.tsv','COMPARISON_FORMULAS.json','CAPACITIES_QUOTAS.json','SCIENTIFIC_POLICY.md','PRODUCTION_RUNNER_CONTRACT.md','INTEGRATION_REVIEW.md','HARDWARE_AND_METRIC_BOUNDARIES.md','EXTERNAL_PROJECT_LOCK_BINDING.json','INPUT_FULL_IDENTITY.json','INPUT_STAT_IDENTITIES.json','ORIGINAL_MEMBERS_SHA256.tsv','AG2_COMPONENT_REQUAL.json','QUALIFICATION_DECISION.json']+list(expected)+specs:
  files[name]=sha(PACK/name)
 write(PACK/'EXECUTABLE_PREREGISTRATION.json',dict(status='EXECUTABLE_PREREGISTERED_NOT_YET_STARTED',goal='DTC_LANE_AG3_AE_AD_DISCOVERY_CONVERGENCE_174_V1',cohort='AG3_DISCOVERY_OPT_AE_AD_V1',utc=now(),core_commit=core,framework_compilation_source=FRAMEWORK_BUILD,ordered_specs=specs,actual_start_cap=6,max_concurrency=1,files=files,resource_version='AG3_DISCOVERY_RESOURCE_R2_V1',real_attempts_before_registration=0,hard_failure='STOP_NO_RETRY_NO_REPLACEMENT_NO_SEVENTH_START',BASE_gate='BOTH_FULL_STRICT_AND_ALL_COMMON_CALIBRATION',execution_gate='COMMIT_PUSH_FETCH_BACK_AND_FRESH_RESOURCE_AUTHORITY_BEFORE_EACH_EXCLUSIVE_FORK_EXEC',no_paper_or_history_modifications=True))
 print(json.dumps(dict(status='EXECUTABLE_LOCAL_REGISTRATION_REQUIRES_PUSH_FETCH_BACK',files=len(files),core=core,UUIDs=[r['attempt_uuid'] for r in rows],real_simulator_starts=0)))
if __name__=='__main__':main()
