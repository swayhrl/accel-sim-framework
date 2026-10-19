"""Read-only final aggregate: replace one changed ELF's evidence; retain all failures."""
import argparse,datetime,hashlib,json,pathlib
P=pathlib.Path

def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(4*2**20),b''):h.update(b)
 return h.hexdigest()

def load(p,h=None):
 if h:assert sha(p)==h,str(p)
 return json.loads(P(p).read_text())

def main():
 p=argparse.ArgumentParser();p.add_argument('--repair',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args();assert not a.out.exists()
 w=P('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1');base=w/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2';s=load(base/'COMMON_R14_FAST_FIXTURE_SPEC_r1.json');old_path=base/'COMMON_NATIVE64_R14_EXTRA_OPEN_AGGREGATE_r1.json';old=load(old_path);r=load(a.repair)
 assert r['status']=='AFFECTED_FIXTURES_PASS_PENDING_AGGREGATE_AND_E' and r['lease_released']
 assert r['compiler_started'] and r['native_invocations_attempted']==r['native_invocations_completed']==4
 assert all(t['expectation_verified'] for t in r['tests'])
 assert r['runtime_producer_core']==old['runtime_producer_core']==s['runtime_producer_core']
 assert r['fixture_source_core']==s['fixture_source_core'] and r['production_tree_ids']==old['production_tree_ids']
 assert r['binary_sha256']==old['runtime_binary_SHA256']==sha(r['binary'])
 assert r['production_archive_sha256']==s['retained_production_archive_sha256']
 assert r['assertion_flags_sha256'] and all(sha(f)==h for f,h in r['assertion_flags_sha256'].items())
 assert all('-DNDEBUG' not in P(f).read_text() for f in r['assertion_flags_sha256'])
 assert all(sha(f)==h for f,h in r['dynamic_library_sha256'].items())
 for f,h in r['input_sha256'].items():assert sha(f)==h
 fresh={t['case']:t for t in r['tests']};rows=[];previous_clock=[];new_clock=[]
 for prior in old['tests']:
  item=dict(prior)
  if item['case']=='native_dirty_boundaries':
   evidence=fresh[item['case']];detail=load(evidence['native_evidence'],evidence['native_evidence_sha256'])
   assert detail['command']==item['native_command'] and detail['actual_exit']==item['actual_exit']==0
   assert detail['required_terminal']==item['required_terminal']
   previous_clock=[t for t in P(item['raw_log']).read_text().splitlines() if t.startswith('TVD_REPAIR_CLOCK|')]
   raw=P(detail['raw_log']);new_clock=[t for t in raw.read_text().splitlines() if t.startswith('TVD_REPAIR_CLOCK|')]
   assert previous_clock==new_clock, 'test observer changed existing physical clock signature'
   item.update(evidence_origin='NEW_R14_FIXTURE_EXISTING_BOUNDARY_REVALIDATION',receipt=evidence['native_evidence'],receipt_SHA256=evidence['native_evidence_sha256'],native_binary_SHA256=detail['binary_sha256'],raw_log=str(raw),raw_SHA256=detail['raw_log_sha256'])
  assert sha(item['native_binary'])==item['native_binary_SHA256']
  assert sha(item['raw_log'])==item['raw_SHA256'] and item['required_terminal'] in P(item['raw_log']).read_text()
  rows.append(item)
 assert len(rows)==64 and sum(t['suite']=='main' for t in rows)==55 and sum(t['suite']=='diagnostics' for t in rows)==9
 extra=[]
 for case in s['additional_cases']:
  ev=fresh[case['id']];d=load(ev['native_evidence'],ev['native_evidence_sha256']);assert d['actual_exit']==0 and d['expectation_verified']
  assert d['command']==case['native_command'] and sha(d['command'][0])==d['binary_sha256']
  assert sha(d['raw_log'])==d['raw_log_sha256'];text=P(d['raw_log']).read_text();assert case['required_terminal'] in text
  if case['id']=='r14_texture':assert 'R14_BYPASS_OBSERVATION|returned=1|actual_uid_lower_issues=1|cache_memport_delta=0' in text
  extra.append(dict(case=case['id'],evidence=ev,actual_native_detail=d))
 report=dict(schema='A_FINAL_NATIVE64_PLUS_REQUIRED_R14_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PRODUCER_FINITE64_AND_REQUIRED_R14_PREDICATES_VERIFIED_PENDING_E_INDEPENDENT_ACCEPTANCE',campaign_id=s['campaign_id'],authority=s['authority'],runtime_producer_core=s['runtime_producer_core'],runtime_Framework=s['framework_source_commit'],vendor=s['vendor'],runtime_binary=r['binary'],runtime_binary_SHA256=r['binary_sha256'],fixture_original_two_target_Core=s['previous_fixture_core'],fixture_r14_Core=s['fixture_source_core'],retained_archive_generated_banner_Core=s['previous_fixture_core'],production_tree_ids=s['production_tree_ids'],production_archive_byte_identity_to_runtime=False,fixture_archive_sha256=r['production_archive_sha256'],fixture_ELF_sha256=r['test_binary_sha256'],source_config_input_SHA256=r['input_sha256'],prior_original64_aggregate=str(old_path),prior_original64_aggregate_SHA256=sha(old_path),r14_repair_receipt=str(a.repair),r14_repair_receipt_SHA256=sha(a.repair),aggregate_script_SHA256=sha(__file__),main=55,diagnostics=9,required_r14_gates_passed=3,new_invocations=4,unchanged_original_evidence_reused=63,new_existing_boundary_clock_signature=new_clock,clock_signature_scope='EMITTED_AND_EQUAL' if new_clock else 'NOT_EMITTED_BY_THIS_CASE_NO_EXACT_CYCLE_EQUIVALENCE_CLAIM_PER_STEP_BANK_ASSERTIONS_RETAINED',observer_pairs_unchanged=old['observer_equality'],original_failed_receipts_changed=False,independent_E_acceptance=False,full_application_starts_by_A=0,application_numerical_or_performance_claim=False,tests=rows,r14_gates=extra)
 a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
