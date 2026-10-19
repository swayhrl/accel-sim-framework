"""Read-only content-bound aggregate of exact unchanged and repaired native evidence."""
import argparse,hashlib,json,pathlib,collections,datetime
P=pathlib.Path

def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb') as f:
  for b in iter(lambda:f.read(4*2**20),b''):h.update(b)
 return h.hexdigest()

def load(path,digest=None):
 if digest:assert sha(path)==digest,str(path)
 return json.loads(P(path).read_text())

def main():
 p=argparse.ArgumentParser();p.add_argument('--repair',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--allow-r14-open',action='store_true');a=p.parse_args()
 assert not a.out.exists()
 r=load(a.repair);assert r['status'] in ('AFFECTED_FIXTURES_PASS_PENDING_AGGREGATE_AND_E','AFFECTED_FIXTURES_FAILED_NO_QUALIFICATION') and r['lease_released']
 assert r['native_invocations_completed']==r['native_invocations_attempted']==30
 source=load('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1/docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2/COMMON_FIXTURE_REPAIR_SPEC_r1.json')
 old=load(source['previous_native_receipt'],source['previous_native_receipt_sha256']);tail=load(source['E_engineering_tail_receipt'],source['E_engineering_tail_receipt_sha256']);prod=load(source['producing_build_receipt'],source['producing_build_receipt_sha256'])
 assert sha(r['binary'])==prod['binary_sha256']==r['binary_sha256']==source['runtime_binary_sha256']
 assert r['runtime_producer_core']==prod['core_source_commit'] and r['fixture_source_core']==source['fixture_source_core']
 assert r['production_tree_ids']==source['production_tree_ids'] and r['unaffected_binaries_byte_identical']
 for path,digest in old['input_sha256'].items():assert sha(path)==digest
 plans={c['id']:c for c in old['planned_tests']};fresh={t['case']:t for t in r['tests']};earlier={t['case']:t for t in old['tests']};etests={t['case']:t for t in tail['tests']};rows=[];signatures=collections.defaultdict(list)
 assert len(plans)==64
 for name,case in plans.items():
  target=case['native_command'][0];changed=case['target'] in source['targets']
  if changed:
   row=fresh[name];assert row['expectation_verified'];path=row['native_evidence'];detail=load(path,row['native_evidence_sha256']);origin='NEW_AFFECTED_EXECUTABLE_NATIVE';expected=source['terminal_corrections'].get(name,case['required_terminal'])
  elif name in earlier:
   row=earlier[name];path=row['native_evidence'];detail=load(path,row['native_evidence_sha256']);origin='REUSED_EXACT_UNCHANGED_A_NATIVE';expected=case['required_terminal']
  else:
   row=etests[name];assert row['status']=='ENGINEERING_NATIVE_EXPECTATION_PASS' and not row['timed_out'];detail=dict(command=row['native_command'],binary_sha256=row['native_binary_sha256'],actual_exit=row['actual_exit'],raw_log=row['raw_log'],raw_log_sha256=row['raw_log_sha256'],required_terminal=row['required_terminal']);path=source['E_engineering_tail_receipt'];origin='REUSED_EXACT_UNCHANGED_E_ENGINEERING_NATIVE';expected=case['required_terminal']
  assert detail['command']==case['native_command']
  digest=detail['binary_sha256'];assert sha(target)==digest
  if not changed:assert digest==prod['test_binary_sha256'][target]
  assert detail['actual_exit']==case['expected_exit'] and detail['required_terminal']==expected
  raw=P(detail['raw_log']);assert sha(raw)==detail['raw_log_sha256'];text=raw.read_text();assert expected in text
  row=dict(case=name,suite=case['suite'],evidence_origin=origin,receipt=str(path),receipt_SHA256=sha(path),native_binary=target,native_binary_SHA256=digest,native_command=detail['command'],actual_exit=detail['actual_exit'],required_terminal=expected,raw_log=str(raw),raw_SHA256=detail['raw_log_sha256'],expectation_verified=True)
  rows.append(row)
  if case.get('compare_group'):
   prefix='A_COMMON_FIXTURE|SEMANTIC|' if case['compare_group']=='F_observer' else 'EPL2MS_TEST|SEMANTIC|'
   sig=[line for line in text.splitlines() if line.startswith(prefix)];assert len(sig)==1
   signatures[case['compare_group']].append(dict(case=name,line=sig[0],raw_SHA256=detail['raw_log_sha256']))
 assert len(rows)==64 and collections.Counter(x['suite'] for x in rows)==dict(main=55,diagnostics=9)
 for group,parts in signatures.items():assert len(parts)==2 and parts[0]['line']==parts[1]['line'],group
 extra=fresh['r14_integration_gates'];r14_ok=extra['expectation_verified'] and extra['additional_terminals_verified'];assert r14_ok or a.allow_r14_open;detail=load(extra['native_evidence'],extra['native_evidence_sha256'])
 assert sha(detail['command'][0])==detail['binary_sha256']==prod['test_binary_sha256'][detail['command'][0]]
 assert sha(detail['raw_log'])==detail['raw_log_sha256'];raw=P(detail['raw_log']).read_text()
 gates=source['additional_cases'][0]
 if r14_ok:assert detail['actual_exit']==0 and all(t in raw for t in [gates['required_terminal'],*gates['additional_terminals']])
 else:assert detail['actual_exit']==-6 and not any(t in raw for t in [gates['required_terminal'],*gates['additional_terminals']])
 report=dict(schema='A_EXACT_NATIVE_AGGREGATE_R18',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FINITE_55_MAIN_9_DIAGNOSTIC_PREDICATES_VERIFIED_R14_EXTRA_UNCLOSED_PENDING_E_SCOPE_REVIEW' if not r14_ok else 'FINITE_55_MAIN_9_DIAGNOSTIC_AND_3_R14_GATE_PREDICATES_VERIFIED_PENDING_E_ACCEPTANCE',campaign_id=source['campaign_id'],authority=source['authority'],runtime_producer_core=source['runtime_producer_core'],fixture_source_core=source['fixture_source_core'],runtime_Framework=source['framework_source_commit'],vendor=source['vendor'],runtime_binary=r['binary'],runtime_binary_SHA256=r['binary_sha256'],new_repair_receipt=str(a.repair),new_repair_receipt_SHA256=sha(a.repair),aggregate_script_SHA256=sha(__file__),production_tree_ids=source['production_tree_ids'],fixture_production_archive_SHA256=r['production_archive_sha256'],production_archive_byte_identity_to_original_runtime=r.get('production_archive_byte_identity_to_original_runtime'),generated_build_string_difference_explicit=r.get('generated_build_string_difference_explicit'),metadata_source_audit=r.get('metadata_source_audit'),metadata_source_audit_sha256=r.get('metadata_source_audit_sha256'),main=55,diagnostics=9,new_affected_native_cases=29,unchanged_native_evidence_reused=35,extra_r14_invocations=1,extra_r14_gates_passed=3 if r14_ok else 0,r14_extra_scope='ALL3PASS' if r14_ok else 'TEXTURE_FIRST_ASSERTION_FAILED_CLEAN_AND_PROMOTION_NOT_RUN',observer_equality=dict(signatures),r14_evidence=extra,independent_E_acceptance=False,application_correctness_or_performance_claim=False,full_application_starts_by_A=0,original_failed_records_rewritten=False,tests=rows)
 a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
