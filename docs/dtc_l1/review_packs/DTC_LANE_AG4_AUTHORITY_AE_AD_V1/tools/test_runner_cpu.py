"""Production runner CPU-only closure and negative gates; never --dispatch.

External scientific publication/admission/strict adapters are explicitly CPU
mocks, not claimed GPU PASS. The actual run_one config copying/start identity/
process engine/lifecycle/final resource/cleanup code executes the fixed probe.
"""
from common import *
import copy,uuid
from unittest.mock import patch
import run_screen as runner
from guarded_process import run_guarded
from mapping_roles import Reject
from audit_site import snapshot,proc


def main():
 evidence=[]
 def rejected(label,fn):
  try:fn()
  except (ValueError,FileNotFoundError,FileExistsError) as exc:
   evidence.append(dict(case=label,status='REJECTED_AS_REQUIRED',reason=repr(exc)));return
  raise AssertionError('accepted:'+label)
 fake=[dict(point=point,order=i,attempt_uuid=f'{i+1:08x}-1111-4111-8111-111111111111') for i,point in enumerate(runner.ORDER)]
 assert runner.validate_records([],fake)==[]
 assert runner.validate_records([dict(attempt_uuid=fake[0]['attempt_uuid'])],fake)==[fake[0]['attempt_uuid']]
 evidence.append(dict(case='empty_and_one_start_prefix',status='PASS_CPU_SYNTHETIC_RECORDS_ONLY'))
 rejected('duplicate_start',lambda:runner.validate_records([dict(attempt_uuid=fake[0]['attempt_uuid'])]*2,fake))
 rejected('out_of_order',lambda:runner.validate_records([dict(attempt_uuid=fake[1]['attempt_uuid'])],fake))
 rejected('foreign_UUID',lambda:runner.validate_records([dict(attempt_uuid='ffffffff-1111-4111-8111-111111111111')],fake))
 rejected('sixth_start',lambda:runner.validate_records([dict(attempt_uuid=s['attempt_uuid']) for s in fake]+[dict(attempt_uuid=fake[0]['attempt_uuid'])],fake))
 rejected('explicit_dispatch_required',lambda:runner.main(False))
 rejected('publication_receipt_absent',runner.publication_check)
 rejected('ON_without_two_calibrated_BASEs',lambda:runner.require_BASE_gate(dict(arm='AE'),fake))
 rejected('manifest_changed',lambda:runner.check_files(dict(files={'tools/mapping_roles.py':'0'*64})))
 target=BUILD/'ag4-cpu-authority';env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='')
 cpu=json.loads((Path(json.loads((PACK/'CPU_AUTHORITY_QUALIFICATION.json').read_text())['raw'])/'PREREGISTRATION.json').read_text())['manifests'];real=json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text())
 runtime=next(k for k in real if Path(k).name=='accel-sim.out')
 rejected('CPU_phase_rejects_real_simulator',lambda:run_guarded([runtime],env,real,RAW/'NEVER_CREATED_CPU_TO_SIM','CPU_FIXTURE',1))
 rejected('no_capability_no_simulation',lambda:run_guarded([str(target)],env,cpu,RAW/'NEVER_CREATED_NO_CAP','SIMULATION',1))
 bad=copy.deepcopy(cpu)
 for m in bad.values():
  next(e for e in m['files'] if e['role']=='LOADER_DATA_CACHE')['sha256']='0'*64
 rejected('cache_changed_before_fork',lambda:run_guarded([str(target)],env,bad,RAW/'NEVER_CREATED_BAD_CACHE','CPU_FIXTURE',1))
 require_no=[RAW/n for n in ['NEVER_CREATED_CPU_TO_SIM','NEVER_CREATED_NO_CAP','NEVER_CREATED_BAD_CACHE']]
 assert not any(q.exists() for q in require_no)
 phase=RAW/'cpu-qualification/production-run-one-BASE-gated-final';phase.mkdir(parents=True,exist_ok=False)
 fixturepack=phase/'fixture_pack';fixturepack.mkdir();write(fixturepack/'RUNTIME_MAPPING_MANIFESTS.json',cpu);write(fixturepack/'AG3_GEMM_BASE_REUSE_QUALIFICATION.json',dict(status='PASS_REUSE_AG3_GEMM_BASE_FOR_AG4_DISCOVERY',CPU_FIXTURE_ONLY_NOT_REAL_QUALIFICATION=True))
 spec=dict(fake[0],arm='BASE',workload='GEMM',runtime_path=str(target),runtime_environment=env,core_commit='CPU_FIXTURE_RECORD_NOT_A_SIMULATION',configs=[dict(path=str(PACK/'config/BASE.config'),sha256=sha(PACK/'config/BASE.config'))])
 original=json.loads((PACK/'inputs/T/inputs/GEMM_OO128_SPEC.json').read_text());spec.update(trace_list=original['trace_list'],trace_list_sha256=original['trace_list_sha256'],expected_kernels=1)
 specs=[spec,*fake[1:]]
 def cpu_bridge(argv,environment,manifests,destination,purpose,timeout,capability,observer):
  assert purpose=='SIMULATION' and argv[0]==str(target)
  capability(str(target),argv,environment)
  return run_guarded(argv,environment,manifests,destination,'CPU_FIXTURE',30,observer=observer)
 def cpu_collect(run,spec):
  text=(run/'simulator.stdout').read_text();assert 'AG4_CPU_ONLY_OK' in text
  term=json.loads((run/'RUN_TERMINAL.json').read_text());assert term['returncode']==0 and term['identity_pass']
  return dict(arm='BASE',status='PASS_CPU_WRAPPER_NOT_GPU_STRICT',performance_accepted=False,cycles='UNAVAILABLE_CPU_ONLY',real_simulator=False)
 with patch.object(runner,'RAW',phase),patch.object(runner,'PACK',fixturepack),patch.object(runner,'publication_check',lambda:(dict(cpu_fixture_only=True),'CPU_NOT_PUBLICATION')),patch.object(runner,'admission',lambda label,owner:snapshot()),patch.object(runner,'run_guarded',cpu_bridge),patch.object(runner,'collect',cpu_collect):
  result=runner.run_one(spec,specs,proc(os.getpid()))
  assert result['performance_accepted'] is False and result['cycles']=='UNAVAILABLE_CPU_ONLY'
  rejected('same_reservation_cannot_run_again',lambda:runner.run_one(spec,specs,proc(os.getpid())))
 evidence.append(dict(case='production_run_one_CPU_closed',status='PASS_CPU_NOT_SIMULATION',result=result,explicit_mocks=['publication/admission scientific adapters','GPU strict adapter records UNAVAILABLE/false'],real_paths_exercised=['input/stat gate','config copy/SHA','final resource/authority sample','exclusive start receipt/budget prefix','capability exact args','real production owned-process guard','all early maps/threads/helpers','final resource','lifecycle receipt','output/strict adapter','file SHA index','cleanup/signal restoration']))
 assert not list((RAW/'attempts').glob('*/RUN_START.json'))
 write(PACK/'RUNNER_CPU_QUALIFICATION.json',dict(status='PASS_PRODUCTION_RUNNER_CPU_CLOSURE_WITH_DECLARED_ADAPTERS',cases=evidence,runner_sha256=sha(PACK/'tools/run_screen.py'),guard_sha256=sha(PACK/'tools/guarded_process.py'),real_simulator_starts=0,performance_accepted=False,unqualified=['actual simulator initialization/runtime still checked in its first budgeted attempt','no-cache host positive qualification']))
 print(json.dumps(dict(status='PASS_PRODUCTION_RUNNER_CPU_CLOSURE',cases=len(evidence),real_simulator_starts=0)))
if __name__=='__main__':main()
