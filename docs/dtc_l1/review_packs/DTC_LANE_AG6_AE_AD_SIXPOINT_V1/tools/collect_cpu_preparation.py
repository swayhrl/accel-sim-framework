"""Collect CPU-only preparation receipts; no launch, lock, signal or body scan."""
from common import *
from audit_site import proc
import difflib

def main():
 tests={
 'CPU_AUTHORITY_QUALIFICATION.json':('PASS_CPU_AUTHORITY_RACE_REPAIR',14),
 'PRODUCTION_DISPATCH_GENERATION_TESTS.json':('PASS_BOUNDED_FULL_GUARD_DISPATCH',6),
 'RUNNER_CPU_QUALIFICATION.json':('PASS_PRODUCTION_RUNNER_CPU_CLOSURE_WITH_DECLARED_ADAPTERS',14),
 'PAIRED_BASE_GATE_CPU_TESTS.json':('PASS_NEW_SIX_POINT_BASE_AND_BUDGET_GATES',10),
 'STRICT_CPU_NEGATIVES.json':('PASS_FULL_CONTROL_POSITIVE_AND_CORRUPTION_NEGATIVES',18),
 'MAPPING_ROLE_REGRESSION.json':('PASS',8),
 'RESOURCE_POLICY_CPU_TESTS.json':('PASS_PURE_CPU_AG_RESOURCE_POLICY',10),
 'PRELAUNCH_HOLD_CPU_TESTS.json':('PASS_FAIL_CLOSED_PREPARATION',3)}
 rows=[]
 for name,(expected,count) in tests.items():
  q=json.loads((PACK/name).read_text());assert q['status']==expected and len(q['cases'])==count,(name,q)
  rows.append(dict(path=name,status=q['status'],cases=count,sha256=sha(PACK/name)))
 q=json.loads((PACK/'CPU_AUTHORITY_QUALIFICATION.json').read_text());assert all(c['passed'] for c in q['cases']) and len(q['negative_controls'])==4
 pre=json.loads((Path(q['raw'])/'PREREGISTRATION.json').read_text())
 for key,name in [('guard_sha256','guarded_process.py'),('ownership_sha256','ownership.py'),('authority_sha256','review_authority.py')]:assert pre[key]==sha(PACK/'tools'/name)
 for name in ['RUNNER_CPU_QUALIFICATION.json','PAIRED_BASE_GATE_CPU_TESTS.json']:
  r=json.loads((PACK/name).read_text());assert r['runner_sha256']==sha(PACK/'tools/run_screen.py')
 assert json.loads((PACK/'RUNNER_CPU_QUALIFICATION.json').read_text())['guard_sha256']==sha(PACK/'tools/guarded_process.py')
 assert q['long_fixture_full_samples']>=3
 write(PACK/'CPU_QUALIFICATION_SUMMARY.json',dict(status='PASS_CPU_ENGINE_WRAPPER_AND_PAIRED_GATES_ONLY',tests=rows,additional_pure_ancestry_external_cases=4,total_cases=sum(r['cases'] for r in rows)+4,long_fixture_actual_periodic_samples=q['long_fixture_full_samples'],performance_qualification=False,current_input_and_runtime_qualification=False,simulator_starts=0,source_bound=True))
 assert not list((RAW/'attempts').glob('*/RUN_START.json'))
 assert not (PACK/'UUID_RESERVATIONS.json').exists() and not (PACK/'EXECUTABLE_PREREGISTRATION.json').exists()
 assert not (RAW/'input-member-sha').exists()
 identities={}
 for p in RAW.rglob('CHILD.json'):
  r=json.loads(p.read_text());identities[(r['pid'],r['start_ticks'])]=r
 for p in RAW.rglob('MAP_EVENTS.jsonl'):
  for line in p.read_text().splitlines():
   r=json.loads(line)
   if 'new_owned_pid' in r:identities[(r['new_owned_pid'],r['child_start_ticks'])]=dict(pid=r['new_owned_pid'],start_ticks=r['child_start_ticks'])
 checked=[]
 for pid,ticks in identities:
  live=proc(pid);same=bool(live and live['start_ticks']==ticks);assert not same
  checked.append(dict(pid=pid,start_ticks=ticks,same_instance_live=same))
 write(PACK/'NO_NEW_SIMULATOR_STARTS.json',dict(status='PASS_PREPARATION_ONLY_ZERO_OF_SIX',authorized_starts=6,actual_simulator_starts=0,formal_start_reservations=0,new_performance_UUIDs=0,CPU_fake_record_UUIDs_are_not_performance=True,trace_body_bytes_read=0,actual_CPU_instances_checked=checked,live_CPU_instances=0,automatic_dispatch=False,old_UUIDs_reused=0,foreign_process_actions=0))
 assert git(CORE,'rev-parse','HEAD')=='c8090115bd57512b1b23fca7d925301fa620c751' and not git(CORE,'status','--porcelain')
 source=[];patch=[]
 ag5=PACK.parent/'DTC_LANE_AG5_RETIRED_PID_REPAIR_V1';ag4=PACK.parent/'DTC_LANE_AG4_AUTHORITY_AE_AD_V1'
 for p in sorted((PACK/'tools').iterdir()):
  if not p.is_file():continue
  previous=ag5/'tools'/p.name
  if not previous.exists():previous=ag4/'tools'/p.name
  source.append(dict(path=str(p.relative_to(PACK)),sha256=sha(p),reference_source=str(previous) if previous.exists() else 'NEW',reference_sha256=sha(previous) if previous.exists() else 'NEW',byte_identical_to_reference=previous.exists() and previous.read_bytes()==p.read_bytes()))
  if previous.exists() and previous.read_bytes()!=p.read_bytes():patch.extend(difflib.unified_diff(previous.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=str(previous.relative_to(PACK.parent)),tofile=str(p.relative_to(PACK))))
 for name in ['mapping_roles.py','resource_policy.py','strict_screen.py']:
  previous=ag5/'tools'/name if name!='strict_screen.py' else ag4/'tools'/name
  assert sha(PACK/'tools'/name)==sha(previous)
 (PACK/'SOURCE_DIFF.patch').write_text(''.join(patch))
 write(PACK/'SOURCE_AND_SHA_BINDING.json',dict(Framework_parent='9793e998d60cb5a7f064a46ecd6be242eda61b7c',Core_fixed='c8090115bd57512b1b23fca7d925301fa620c751',Core_clean=True,model_modified=False,actual_simulator_rebuilt=False,only_allowed_changes=str(PACK.relative_to(FW))+'/',files=source,CPU_fixture_source_sha256=sha(PACK/'tools/authority_cpu.cc'),CPU_fixture_ELF_sha256=sha(BUILD/'ag6-cpu-authority'),CPU_compile_argv=['g++','-O0','-pthread',str(PACK/'tools/authority_cpu.cc'),'-o',str(BUILD/'ag6-cpu-authority')],actual_runtime_current_freeze='DEFERRED_RESOURCE_NOT_QUALIFIED'))
 inherited=[]
 for previous,commit in [(ag4,'d8d0401dab0a1d9cb949302bcc05148328421cc2'),(ag5,'9793e998d60cb5a7f064a46ecd6be242eda61b7c')]:
  count=0
  for line in git(FW,'ls-tree','-r',commit,'--',str(previous.relative_to(FW))).splitlines():
   meta,name=line.split('\t');assert (FW/name).read_bytes()==blob(FW,commit,name);count+=1
  inherited.append(dict(path=str(previous.relative_to(FW)),commit=commit,all_blobs_unchanged=count))
 assert [r['all_blobs_unchanged'] for r in inherited]==[142,42]
 write(PACK/'HISTORY_PRESERVATION.json',dict(status='PASS',inherited_packs=inherited,Core_clean=True,old_worktrees_raw_locks_not_written=True,old_AG4_actual_starts=2,old_AG4_complete_strict_observations=1,old_AG4_optimization_results=0,old_AG3_actual_starts=2,old_AG3_complete_strict=1,old_AG_actual_starts=1,old_AG_complete_strict=0,AA5_actual_starts=1,AA5_complete_strict=0))
 resource=json.loads((PACK/'CURRENT_SITE_AUDIT.json').read_text())
 write(PACK/'PRELAUNCH_STATE.json',dict(status='HOLD_PRELAUNCH_RESOURCES_ZERO_OF_SIX',authorization='EXPLICIT_SIX_NEW_COMPLETE_PAIRING_STARTS',authorization_sha256=sha(PACK/'USER_AUTHORIZATION.json'),budget_total=6,budget_actual_used=0,budget_remaining=6,CPU_path='PASS_BOUNDED_SCOPE',resource=resource['status'],failed_resource_checks=[k for k,v in resource['resource_checks'].items() if not v],authority=resource['authority']['status'],input_full_member_rehash='DEFERRED_SAFE_STOP_RESOURCE_GATE_BEFORE_BODY_READ',runtime_current_freeze='DEFERRED_RESOURCE_GATE',UUIDs_generated=0,executable_preregistration_published=False,scientific_plan='PLANNED_SIX_POINT_IDENTITY.json',performance_results='UNAVAILABLE',requires_repeat_budget_authorization=False,no_background_dispatch=True))
 table(PACK/'RAW_FILES_SHA256.tsv',[dict(path=str(p.relative_to(RAW)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file()])
 print(json.dumps(dict(status='PASS_CPU_PREPARATION_HOLD_EXECUTABLE_REGISTRATION',CPU_cases=sum(r['cases'] for r in rows)+4,CPU_instances=len(checked),simulator_starts=0,new_UUIDs=0,budget_remaining=6)))
if __name__=='__main__':main()
