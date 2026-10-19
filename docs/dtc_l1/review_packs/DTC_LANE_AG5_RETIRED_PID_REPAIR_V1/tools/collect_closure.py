"""Read-only evidence collection. No simulator, dispatch, lock or signal APIs."""
from common import *
from audit_site import snapshot,proc
from review_authority import review
from resource_policy import admission_checks
import difflib

BASE='d8d0401dab0a1d9cb949302bcc05148328421cc2'

def main():
 old=PACK.parent/'DTC_LANE_AG4_AUTHORITY_AE_AD_V1'
 # Hash the original frozen operative files, not any newly generated substitute.
 registration=json.loads((old/'EXECUTABLE_PREREGISTRATION.json').read_text())
 checks=[dict(path=n,expected=h,actual=sha(old/n),pass_=sha(old/n)==h) for n,h in registration['files'].items()]
 assert len(checks)==81 and all(x['pass_'] for x in checks)
 oldpack=str(old.relative_to(FW))
 historical=[]
 for line in git(FW,'ls-tree','-r',BASE,'--',oldpack).splitlines():
  head,name=line.split('\t');data=blob(FW,BASE,name);path=FW/name
  assert path.read_bytes()==data
  historical.append(dict(path=name,blob=head.split()[2],sha256=sha(path)))
 assert len(historical)==142
 assert git(CORE,'rev-parse','HEAD')=='c8090115bd57512b1b23fca7d925301fa620c751'
 assert not git(CORE,'status','--porcelain')
 original=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-ag4-authority-aead-174-v1')
 assert not git(original,'status','--porcelain')
 write(PACK/'HISTORY_PRESERVATION.json',dict(status='PASS',old_AG4_commit=BASE,old_AG4_pack_142_blobs=historical,old_frozen_81_files=checks,old_worktree_clean=True,Core_commit=git(CORE,'rev-parse','HEAD'),Core_clean=True,AG4_actual_starts=2,AG4_capacity=5,AG4_full_strict_observations=1,AG4_accepted_optimization_results=0,AG3_actual_starts=2,AG3_full_strict=1,AG_actual_starts=1,AG_full_strict=0,AA5_actual_starts=1,AA5_full_strict=0,old_raw_write_paths_in_new_tools=False))
 bindings=[];diff=[]
 for p in sorted((PACK/'tools').iterdir()):
  if not p.is_file():continue
  previous=old/'tools'/p.name
  bindings.append(dict(path=str(p.relative_to(PACK)),sha256=sha(p),old_AG4_sha256=sha(previous) if previous.exists() else 'NEW',byte_identical_to_AG4=previous.exists() and p.read_bytes()==previous.read_bytes()))
  if previous.exists() and p.read_bytes()!=previous.read_bytes():
   diff.extend(difflib.unified_diff(previous.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='AG4/tools/'+p.name,tofile='AG5/tools/'+p.name))
 (PACK/'SOURCE_DIFF.patch').write_text(''.join(diff))
 assert sha(PACK/'tools/mapping_roles.py')==sha(old/'tools/mapping_roles.py')
 assert sha(PACK/'tools/resource_policy.py')==sha(old/'tools/resource_policy.py')
 write(PACK/'SOURCE_AND_SHA_BINDING.json',dict(parent_Framework=BASE,Core_read_only=git(CORE,'rev-parse','HEAD'),allowlist='Only new review pack paths; no Core, simulator binary, trace, old raw, paper or historical pack edits',files=bindings,CPU_fixture_source_sha256=sha(PACK/'tools/authority_cpu.cc'),CPU_fixture_ELF_sha256=sha(BUILD/'ag5-cpu-authority'),compile_argv=['g++','-O0','-pthread',str(PACK/'tools/authority_cpu.cc'),'-o',str(BUILD/'ag5-cpu-authority')],performance_dispatcher_shipped=False))
 instances={};terminals=[]
 for p in RAW.rglob('CHILD.json'):
  q=json.loads(p.read_text());instances[(q['pid'],q['start_ticks'])]=dict(pid=q['pid'],start_ticks=q['start_ticks'])
 for p in RAW.rglob('TERMINAL.json'):
  q=json.loads(p.read_text());assert q.get('simulator_starts',0)==0
  terminals.append(dict(path=str(p.relative_to(RAW)),sha256=sha(p),status=q['status'],purpose=q['purpose'],simulator_starts=q.get('simulator_starts',0)))
  o=q.get('ownership') or {}
  for r in o.get('retired',[])+o.get('confirmed',[]):instances[(r['pid'],r['start_ticks'])]=dict(pid=r['pid'],start_ticks=r['start_ticks'])
  for r in q.get('owned_process_exit_instances',[]):instances[(r['pid'],r['start_ticks'])]=dict(pid=r['pid'],start_ticks=r['start_ticks'])
 for p in RAW.rglob('MAP_EVENTS.jsonl'):
  for line in p.read_text().splitlines():
   q=json.loads(line)
   if 'new_owned_pid' in q:
    instances[(q['new_owned_pid'],q['child_start_ticks'])]=dict(pid=q['new_owned_pid'],start_ticks=q['child_start_ticks'])
 live=[]
 for r in instances.values():
  current=proc(r['pid'])
  r['same_instance_live']=bool(current and current['start_ticks']==r['start_ticks'])
  if r['same_instance_live']:live.append(r)
 assert not live
 # Current external authority may change after CPU tests. Publish its actual
 # STOP independently of bounded repair qualification; never whiten newcomers.
 s=snapshot();a=review(s,proc(os.getpid()))
 ownlocks=[l for l in s['FLOCKs'] if str(RAW.parent) in l['path']];assert not ownlocks
 write(RAW/'FINAL_SITE_SNAPSHOT.json',s)
 write(PACK/'FINAL_AUTHORITY_AND_RESOURCES.json',dict(authority=a,snapshot_path=str(RAW/'FINAL_SITE_SNAPSHOT.json'),snapshot_sha256=sha(RAW/'FINAL_SITE_SNAPSHOT.json'),host=s['host'],disk_free_bytes=s['disk_free_bytes'],performance_disk_minimum_bytes=10*1024**3,performance_disk_gate_pass=s['disk_free_bytes']>=10*1024**3,host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup=s['cgroup'],pressure=s['pressure'],formal_two_sample_performance_admission_performed=False,new_budget_assigned=False,own_FLOCKs=ownlocks,foreign_projects_in_resource_snapshot=True))
 write(PACK/'NO_SIMULATOR_STARTS.json',dict(status='PASS_CPU_ONLY_NO_NEW_SIMULATOR_START',CPU_terminal_receipts=terminals,real_CPU_instances_checked=list(instances.values()),real_CPU_instances_live=live,simulator_starts=0,new_performance_UUIDs=0,performance_budget_consumed=0,own_FLOCKs=0,foreign_signals=0,old_Goals_restarted=0,automatic_dispatch=False,scope='Recorded launch sources, fixed fixture ELF identity, per-fork receipts and final exact-instance audit; not a claim of system-wide exec tracing'))
 table(PACK/'RAW_FILES_SHA256.tsv',[dict(path=str(p.relative_to(RAW)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file()])
 totals=json.loads((PACK/'CPU_AUTHORITY_QUALIFICATION.json').read_text())
 assert all(r['passed'] for r in totals['cases'])
 prereg=json.loads((Path(totals['raw'])/'PREREGISTRATION.json').read_text())
 for key,name in [('guard_sha256','guarded_process.py'),('authority_sha256','review_authority.py'),('ownership_sha256','ownership.py')]:
  assert prereg[key]==sha(PACK/'tools'/name),('TESTED_SOURCE_CHANGED',name)
 generation=json.loads((PACK/'PRODUCTION_DISPATCH_GENERATION_TESTS.json').read_text())
 assert len(generation['cases'])==6 and all(r['status']=='PASS_EXPECTED_RESULT' for r in generation['cases'])
 assert json.loads((Path(generation['raw'])/'PREREGISTRATION.json').read_text())['fixed_source_sha']==sha(PACK/'tools/guarded_process.py')
 for name,count in [('MAPPING_ROLE_REGRESSION.json',8),('EXTERNAL_BINDING_TESTS.json',8),('NO_SIMULATOR_DISPATCH_TESTS.json',3),('RESOURCE_POLICY_CPU_TESTS.json',10)]:
  result=json.loads((PACK/name).read_text());assert result['status'].startswith('PASS') and len(result['cases'])==count,(name,result)
 decision=dict(status='PASS_BOUNDED_CPU_RETIRED_PID_REPAIR',coverage={'actual_CPU_lifecycle_cases':len(totals['cases']),'pure_original_ancestry_external_negatives':len(totals['negative_controls']),'full_guard_generation_cases':6,'mapping_role_cases':8,'unchanged_R2_cases':10,'no_simulator_launch_policy_cases':3,'exact_external_binding_cases':8},kernel_PID_reuse_forced=False,whole_guard_dispatch_generation_input='DECLARED_SYNTHETIC_OVER_REAL_CPU_LIFECYCLE',long_fixture_full_periodic_samples=totals['long_fixture_full_samples'],simulator_starts=0,performance_qualification=False,old_UUIDs_sealed=True,future_simulation_budget='UNASSIGNED_REQUIRES_EXPLICIT_USER_DECISION',future_simulation_current_authority=a['status'],future_simulation_current_resource_gate='HOLD_DISK_LT10GiB' if s['disk_free_bytes']<10*1024**3 else 'UNAVAILABLE_TWO_SAMPLE_ADMISSION_NOT_PERFORMED')
 assert decision['long_fixture_full_periodic_samples']>=3
 write(PACK/'FINAL_CPU_QUALIFICATION_DECISION.json',decision)
 print(json.dumps(dict(status=decision['status'],cases=sum(decision['coverage'].values()),real_instances=len(instances),old_frozen_files=len(checks),simulator_starts=0,disk_free_bytes=s['disk_free_bytes'])))

if __name__=='__main__':main()
