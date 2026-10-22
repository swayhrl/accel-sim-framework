import copy,json,unittest
import project as p

class ProjectionControls(unittest.TestCase):
 def summary(self,**counts):
  c=dict.fromkeys(p.FIELDS,0);c.update(counts)
  return {'status':'SYNTHETIC_OBSERVER_CONTROL_ONLY','data_kind':'SYNTHETIC','global_counters':c,'slice_counters':{'0':copy.deepcopy(c)},'expected_slice_count':64,'require_closed':True,'final_cycle':20,'schema_counter_fields':list(p.FIELDS),'phase_catalog':{'0':None,'1':None,'2':1}}
 def row(self,r,k):return next(x for x in r['global']['rows'] if x['metric']==k)
 def test_all212_exactly_once(self):
  r=p.project(self.summary());self.assertEqual(r['status'],'SYNTHETIC_NUMERIC_CONTROL_ONLY');self.assertEqual(len(r['global']['rows']),212);self.assertEqual(len({x['metric'] for x in r['global']['rows']}),212)
 def test_no_pressure_scope_with_skips(self):
  r=p.project(self.summary(observed_heads=100,probe_skipped=80,skip_tvd=80,ro_admits=2));self.assertIn('NO_OBSERVED_LOCAL_PRESSURE',[x['code'] for x in r['observations']]);self.assertEqual(r['coverage']['probed_heads'],20);self.assertEqual(r['scientific_application_conclusions'],[])
 def test_raw_fail_survives_preview_rewrite(self):
  r=p.project(self.summary(observed_heads=10,raw_reservation_fail=10,pressure_T_enabled=10,pressure_eligible=10,pressure_rewrite_miss=10,eligible_rewrite_miss=10,eligible_prod_probe_reached=10));self.assertEqual(self.row(r,'raw_reservation_fail')['value'],10);self.assertEqual(self.row(r,'eligible_rewrite_miss')['ratio'],1)
 def test_exact_eligible_joints_no_marginal_product(self):
  r=p.project(self.summary(observed_heads=100,raw_reservation_fail=40,pressure_eligible=20,ro_capacity_population=100,ro_descriptor_fail=50,eligible_capacity_consulted=5,eligible_descriptor_fail=2));row=self.row(r,'eligible_descriptor_fail');self.assertEqual(row['value'],2);self.assertEqual(row['denominator_value'],5);self.assertEqual(row['ratio'],.4)
 def test_post_relief_denominator_all_relieve_calls(self):
  r=p.project(self.summary(relieve_calls=5,relieve_no_eligible=5,post_relief_fail=5));self.assertEqual(self.row(r,'post_relief_fail')['denominator_value'],5);self.assertEqual(self.row(r,'post_relief_fail')['ratio'],1)
 def test_capacity_unobserved_not_fail_or_zero(self):
  r=p.project(self.summary(ro_capacity_population=100,ro_capacity_consulted=30,ro_descriptor_checked=30,ro_descriptor_fail=20,ro_address_checked=10,ro_address_unobserved=90));self.assertEqual(self.row(r,'ro_address_fail')['denominator_value'],10);self.assertEqual(self.row(r,'ro_address_unobserved')['value'],90)
 def test_line_NA_not_double_added(self):
  r=p.project(self.summary(ro_capacity_population=10,ro_line_na_M_or_existing=10,ro_line_probe_unobserved=10));self.assertEqual(self.row(r,'ro_line_probe_unobserved')['value'],10);self.assertEqual(self.row(r,'ro_line_probe_fail')['ratio'],None)
 def test_reuse_first_reason_vs_predicate(self):
  r=p.project(self.summary(ways_examined=160,way_no_live_ro=100,way_reuse_seen=30,predicate_hist_3=20));self.assertEqual(self.row(r,'way_reuse_seen')['denominator_value'],160);self.assertEqual(self.row(r,'predicate_hist_3')['denominator_value'],60)
 def test_detach_then_denied_and_many_waiters_legal(self):
  r=p.project(self.summary(detach_calls=1,detach_success=1,detached_retired=1,trigger_denied_after_detach=1,detached_responses=9));self.assertEqual(r['global']['derived']['terminal_detached_residual'],0);self.assertEqual(self.row(r,'detached_responses')['ratio'],None);self.assertIn('DETACH_THEN_DENIED',[x['code'] for x in r['observations']])
 def test_unknown_not_zero(self):
  s=self.summary();del s['global_counters']['eligible_descriptor_fail'];r=p.project(s);self.assertEqual(self.row(r,'eligible_descriptor_fail')['measurement_state'],'UNKNOWN_NOT_EMITTED');self.assertIsNone(self.row(r,'eligible_descriptor_fail')['value']);self.assertIn('eligible_descriptor_fail',r['new_field_missing'])
 def test_zero_denominator_null(self):
  r=p.project(self.summary());self.assertIsNone(self.row(r,'pressure_eligible')['ratio']);self.assertEqual(self.row(r,'pressure_eligible')['ratio_state'],'NA_ZERO_DENOMINATOR')
 def test_bool_not_count(self):self.assertEqual(p.project(self.summary(detach_success=True))['status'],'INVALID_NUMERIC_PROJECTION')
 def test_overflow_not_count(self):self.assertEqual(p.project(self.summary(detach_success=2**64))['status'],'INVALID_NUMERIC_PROJECTION')
 def test_negative_residual_not_closed(self):self.assertEqual(p.project(self.summary(detached_retired=1))['status'],'INVALID_NUMERIC_PROJECTION')
 def test_phase_not_causal(self):
  r=p.project(self.summary());self.assertEqual(r['phase_numeric_state'],'UNKNOWN_DECODER_NOT_PROJECTED');self.assertEqual(r['phase_causal_kernel_attribution'],'NOT_MEASURED')
 def test_old_history_preserved(self):
  r=p.project(self.summary());self.assertEqual(r['historical_scope']['other_old_positive_RO']['state'],'UNKNOWN');self.assertIn('empty fallback',r['historical_scope']['old_SGEMM']['reason']);self.assertIn('131072',r['historical_scope']['old_FWT']['reason'])
 def test_invalid_decoder_not_projected(self):self.assertEqual(p.project({'status':'INCOMPLETE'})['status'],'INCOMPLETE')
 def test_native_or_synthetic_no_app_claims(self):
  r=p.project(self.summary(detach_success=1));self.assertFalse(r['scientific_application_acceptance_granted']);self.assertEqual(r['scientific_application_conclusions'],[])
 def context(self,summary):
  c=p.legacy.template();c['data_kind']='REAL_ACCEPTED';c['identity']={k:'a'*64 for k in p.legacy.IDENTITY}
  c['identity'].update(core_commit='b'*40,framework_commit='c'*40)
  ref={'commit':'a'*40,'path':'synthetic/control.json','sha256':'a'*64}
  c['acceptance'].update(status='CURRENT_ACCEPTED_DIAGNOSTIC_POINT',endpoint_status='COMPLETE_VALID',receipt_ref=ref,adapter_ref=ref,producer_schema_ref=ref,semantic_mapping_reviewed_by_E=True)
  c['normalized_summary_sha256']=p.digest(summary);return c
 def wrapped(self):
  o=self.summary();o['status']='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY';o['data_kind']='REAL_UNACCEPTED'
  return {'detach_observer_diagnostic':{'observer':o,'source_identity':{'core_source_commit':'b'*40,'framework_source_commit':'c'*40,'binary_sha256':'a'*64},'qualification_id':'a'*64}}
 def test_real_normalized_without_context_provisional(self):self.assertEqual(p.project(self.wrapped())['status'],'PROVISIONAL_NORMALIZED_PROJECTION_NOT_APPLICATION_ACCEPTANCE')
 def test_exact_context_is_consumed_not_new_acceptance(self):
  s=self.wrapped();r=p.project(s,self.context(s));self.assertEqual(r['status'],'E_ACCEPTED_NUMERIC_PROJECTION');self.assertFalse(r['scientific_application_acceptance_granted'])
 def test_context_hash_mismatch(self):
  s=self.wrapped();c=self.context(s);c['normalized_summary_sha256']='0'*64;self.assertEqual(p.project(s,c)['status'],'INVALID_NUMERIC_PROJECTION')
 def test_wrong_binary_context(self):
  s=self.wrapped();c=self.context(s);c['identity']['binary_sha256']='f'*64;self.assertEqual(p.project(s,c)['status'],'INVALID_NUMERIC_PROJECTION')
 def test_fake_pair_rejected_by_original_consumer(self):
  s=self.wrapped();c=self.context(s);c['acceptance']['pair']=True;r=p.project(s,c);self.assertNotEqual(r['status'],'E_ACCEPTED_NUMERIC_PROJECTION');self.assertEqual(r['scientific_application_conclusions'],[])

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(ProjectionControls);result=unittest.TextTestRunner(verbosity=2).run(suite)
 from pathlib import Path
 Path(__file__).with_name('CONTROL_RESULTS.json').write_text(json.dumps({'scope':'SYNTHETIC_PYTHON_METADATA_CONTROLS_NOT_NATIVE_OR_APP','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'success':result.wasSuccessful()},indent=2)+'\n')
 raise SystemExit(not result.wasSuccessful())
