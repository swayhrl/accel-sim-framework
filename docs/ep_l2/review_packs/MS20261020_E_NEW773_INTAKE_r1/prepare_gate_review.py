"""Independent scoped source/native review; OFF gate cannot be filled by this tool."""
from pathlib import Path
import json,sys,time,subprocess
sys.path.insert(0,str(Path.cwd()/'util/ep_l2/mechanism_e'))
import coordinator as c
root=Path.cwd();pack=Path(__file__).resolve().parent
oldpack=root/'docs/ep_l2/review_packs/MS20261020_E_MAIN_SF_QUALIFICATION_r1'
newpath=c.OUTPUT/'E_INDEPENDENT_NEW773_AFFECTED_NATIVE_r1/RECEIPT.json'
new=json.loads(newpath.read_text());assert len(new['tests'])==24 and new['status']=='E_24_AFFECTED_NATIVE_EXECUTIONS_PASS_PENDING_GATE_REVIEW'
by={x['case']:x for x in new['tests']};current=new['source_identity']
source='/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r25-ro-origin-v1'
def blob(name):return subprocess.check_output(['git','show',current['core_source_commit']+':'+name],cwd=source)
# The failed extra fixture's event cannot require another lower packet once the
# frozen production transaction has already issued all of its required sectors.
transaction=blob('src/gpgpu-sim/ep-l2-ro-transactions.h').decode()
assert 'e.required |= mask; e.reuse_seen = true;' in transaction
assert 'e.attached && !e.reuse_seen' in transaction
assert 'e.required & ~(e.issued | e.ready)' in transaction
l2=blob('src/gpgpu-sim/l2cache.cc').decode();assert 'mf->get_data_size() == MAX_MEMORY_ACCESS_SIZE' in l2
joint=dict(schema='E_INDEPENDENT_R35_SCOPE_REVIEW_V1',reviewed_by='E',reviewed_unix=time.time(),source_identity=current,
 A_r35='156adbbb5ddcd49e8adb96939837372936ac451e',
 classification='FAILED_EXTRA_FIXTURE_UNREACHABLE_EXPECTATION_NOT_A_PASSED_GATE',
 observed='Actual abort submit_ro(0) while waiting for a new lower packet: A0 attached,reuse_seen=1, required=issued=15, ready=0,waiters=5. All20 lower packets retained; no22packet completion claim.',
 independent_source_reason='Real128B parent splits into4sector requests; subsequent sectors merge and make reuse_seen persistent. Duplicate merges into original attached transaction; lower_needed=required & ~(issued|ready)=0. The fixture withholds all returns while demanding a different handle/new lower packet. That expectation contradicts frozen semantics, so its timeout does not demonstrate a production deadlock or incorrect data. Later parentUID/18descriptor assertions were not reached and remain unqualified.',
 production_policy_changed=False,reuse_seen_waived=False,B_C_joint_scenario_accepted=False,
 pending_scope=['Replacement128B-sectorized V/R/W constructed scenario, correct childUID and descriptor expected counts, independently reviewed by B/C and E; no present PASS for that scenario.', 'No claimed22packet/704byte completed result; no claim that every possible V/R/W interleave is verified.'],
 current_required_gate_scope='Original11 plus seven frozen minimum combination gates are reviewed separately using exact original scope. Existing newarchive combined_shared_pool/same_address/host_update/pinned_wb/native_ro_mux/TM modes cover all seven minimum gates. This extra fixture is not substituted for any required gate. FormalF remains conditional on these gates and newsourceOFF; any actual production failure stops affected profile.',
 minimum_combination_coverage={
 'shared_payload_lifecycle':['combined_shared_pool','combined_pinned_wb'],
 'shared_directory_cost_and_full':['combined_shared_pool'],
 'pinned_victim_wb_completion_identity':['combined_pinned_wb'],
 'ro_tag_reuse_late_sector_identity':['combined_same_address','combined_factor_tag_T1_M1'],
 'ro_victim_same_address_and_host_invalidation':['combined_same_address','combined_host_update'],
 'backpressure_complete_quiescence':['combined_shared_pool','combined_native_ro_mux'],
 'tm_trigger_default_off_and_illegal_combinations':['combined_factor_tag_T0_M0','combined_factor_tag_T0_M1','combined_factor_tag_T1_M0','combined_factor_tag_T1_M1','combined_factor_line_T0_M0','combined_factor_line_T0_M1','combined_factor_line_T1_M0','combined_factor_line_T1_M1','combined_fallback']})
# Each cited actual current test has independently executed and immutable raw.
for names in joint['minimum_combination_coverage'].values():
 for name in names:
  t=by[name];assert t['execution_expectation']=='PASS' and c.digest(t['raw_log'])==t['raw_log_sha256']
c.write_json(pack/'VRW_SCOPE_REVIEW.json',joint)
gates=pack/'gates';gates.mkdir(exist_ok=True)
for path in (oldpack/'gates').glob('*.json'):
 original=json.loads(path.read_text());name=original['gate']
 if name=='old_all_off_equivalence':continue
 tests=[]
 for case in original['actual_cases']:
  row=dict(by.get(case['case'],case));isnew=case['case'] in by
  assert c.digest(row['raw_log'])==row['raw_log_sha256'] and row['execution_expectation']=='PASS'
  assert c.digest(row['command'][0])==row['native_binary_sha256']
  row['reuse_classification']='NEW_ARCHIVE_INDEPENDENT_E_EXECUTION' if isnew else 'RETAINED_E_EXECUTION_SOURCE_PATH_DISJOINT_FROM_RO_LOWER_ALLOCATOR'
  tests.append(row)
 for name2 in joint['minimum_combination_coverage'].get(name,[]):
  if name2 not in {t['case'] for t in tests}:tests.append(dict(by[name2],reuse_classification='NEW_ARCHIVE_INDEPENDENT_E_EXECUTION'))
 if name in ['requester_exact_once','bank_service','physical_bank_clock']:
  tests.extend(dict(by[n],reuse_classification='NEW_DETAILED_DRAM_MEMSTATS14_REAL_ORIGIN_AND_BANK_CLOCK') for n in ['new_T0M0','new_T0M1','new_T1M0','new_T1M1'])
 record=dict(schema='E_INDEPENDENT_NEW773_GATE_REVIEW_V1',gate=name,status='PASS',production_driven=True,
  reviewed_by='E',reviewed_unix=time.time(),source_identity=current,actual_cases=tests,
  current_native_receipt=dict(path=str(newpath),sha256=c.digest(newpath)),
  retained_disjoint_review=dict(path=str(pack/'PRODUCER_IDENTITY_REVIEW.json'),sha256=c.digest(pack/'PRODUCER_IDENTITY_REVIEW.json')),
  prior_scope_reference=dict(path=str(path),sha256=c.digest(path)),
  reference_review='Review exact retained independent reference assertions and unchanged producerELFs for disjoint paths; replace every affected RO case with E currentarchive actual replay. New detailedDRAM regression asserts nonzero wid7/sid3/tpc3/stream17, four exact-once replies, zero origin mismatch, physicalbank<=1 and quiescence. Sameaddress/sharedpool/pinnedWB assert actual payload versions, UIDs/generations, dirty snapshots, exact response consumption and bounded resource drains. Does not validate numerical SASS application values.',
  unqualified_extra_joint_scope=dict(path=str(pack/'VRW_SCOPE_REVIEW.json'),sha256=c.digest(pack/'VRW_SCOPE_REVIEW.json')))
 c.write_json(gates/path.name,record)
print('17_GATES_REVIEWED_NEW_OFF_STILL_PENDING',len(list(gates.glob('*.json'))))
