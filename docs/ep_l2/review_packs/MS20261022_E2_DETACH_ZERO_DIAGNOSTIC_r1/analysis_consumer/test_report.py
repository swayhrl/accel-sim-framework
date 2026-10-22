import copy
import unittest
from report import analyze,template,SEMANTICS

def doc():
 d=template();d['data_kind']='SYNTHETIC';d['identity']={k:('a'*40 if k.endswith('_commit') else 'a'*64) for k in d['identity']};d['identity']['run_id']='synthetic-run';return d

def add(d,name,value,status='MEASURED',**changes):
 domain,unit,kind=SEMANTICS[name];cid='c_'+name
 d['coverage'][cid]={'complete':True,'overflow':False,'run_id':'synthetic-run','domain':domain,'scope_id':'whole','interval':[0,100],'level':'GLOBAL','accepted_slice_ids':list(range(64))}
 d['metrics'][name]={'value':value,'status':status,'domain':domain,'unit':unit,'measurement_kind':kind,'coverage_id':cid,'scope_id':'whole','mapping_evidence_ref':'synthetic-mapping-only'};d['metrics'][name].update(changes)

class Controls(unittest.TestCase):
 def test_template_no_fake_science(self):
  r=analyze(template());self.assertEqual(r['status'],'INCOMPLETE');self.assertFalse(r['scientific_application_conclusions']);self.assertFalse(r['measured_facts'])
 def test_absence_never_zero(self):
  d=doc();r=analyze(d);self.assertFalse(r['measured_facts']);self.assertFalse(r['synthetic_observations']);self.assertTrue(any('UNKNOWN_NOT_EMITTED' in s for s in r['unknowns']))
 def test_not_consulted_distinct(self):
  d=doc();add(d,'relief_preview_not_consulted',3);r=analyze(d);self.assertEqual([c['code'] for c in r['synthetic_observations']],['PREVIEW_NOT_CONSULTED'])
 def test_missing_pressure_cannot_infer_no_pressure(self):
  d=doc();add(d,'accepted_ro',20);r=analyze(d);self.assertNotIn('NO_OBSERVED_PRESSURE',[c['code'] for c in r['synthetic_observations']])
 def test_head_cycles_never_unique_requests(self):
  d=doc();add(d,'raw_probe_reservation_fail',400);r=analyze(d);self.assertEqual(r['measured_facts']['raw_probe_reservation_fail']['unit'],'head_cycle');d['metrics']['raw_probe_reservation_fail']['unit']='unique_request';self.assertEqual(analyze(d)['status'],'INVALID')
 def test_missing_slice_no_numerical_claim(self):
  d=doc();add(d,'detach_success',0);d['coverage']['c_detach_success']['accepted_slice_ids']=list(range(63));self.assertFalse(analyze(d)['measured_facts'])
 def test_bool_rejected(self):
  d=doc();add(d,'detach_success',False);self.assertEqual(analyze(d)['status'],'INVALID')
 def test_overflow_rejected(self):
  d=doc();add(d,'detach_success',0);d['coverage']['c_detach_success']['overflow']=True;self.assertEqual(analyze(d)['status'],'INVALID')
 def test_sticky_vs_ready_nonexclusive_not_summed(self):
  d=doc();add(d,'sticky_reuse_predicate',8);add(d,'no_required_not_ready_sector_predicate',7);r=analyze(d);self.assertEqual(len(r['measured_facts']),2);self.assertFalse(r['synthetic_observations']);self.assertTrue(all(x['scope_warning'] for x in r['measured_facts'].values()))
 def test_victim_not_trigger_or_response(self):
  d=doc();add(d,'detach_success',2);add(d,'detached_victim_response_count',7);add(d,'trigger_first_call_refused_after_detach',2);r=analyze(d);self.assertIn('DETACH_THEN_DENIED',[c['code'] for c in r['synthetic_observations']]);self.assertFalse(r['scientific_application_conclusions']);self.assertEqual(r['status'],'SYNTHETIC_CONTROL_ONLY')
 def test_scope_mismatch_no_joint_inference(self):
  d=doc();add(d,'accepted_ro',2);add(d,'raw_probe_reservation_fail',0);d['coverage']['c_raw_probe_reservation_fail']['interval']=[100,200];self.assertFalse(analyze(d)['synthetic_observations'])
 def test_real_requires_actual_E_acceptance(self):
  d=doc();d['data_kind']='REAL_ACCEPTED';add(d,'detach_success',0);r=analyze(d);self.assertEqual(r['status'],'INCOMPLETE');self.assertFalse(r['measured_facts'])
 def test_na_with_number_invalid(self):
  d=doc();add(d,'relief_preview_not_consulted',0,status='NA_NOT_CONSULTED');self.assertEqual(analyze(d)['status'],'INVALID')


# Root-review adversarial controls, synthetic declarations only.
def real_point():
 d=doc();d['data_kind']='REAL_ACCEPTED';ref={'commit':'a'*40,'path':'docs/synthetic-point-only.json','sha256':'b'*64}
 d['acceptance']={'status':'CURRENT_ACCEPTED_DIAGNOSTIC_POINT','endpoint_status':'COMPLETE_VALID',
 'scientific_scope':'DETACH_OBSERVER_DIAGNOSTIC_POINT_V1','pair':False,'owner':'E2',
 'semantic_mapping_reviewed_by_E':True,'receipt_ref':ref.copy(),'adapter_ref':ref.copy(),'producer_schema_ref':ref.copy()}
 add(d,'detach_success',0);return d

class RootReviewControls(unittest.TestCase):
 def test_valid_E_accepted_point_declaration(self):
  d=real_point();r=analyze(d);self.assertEqual(r['status'],'E_ACCEPTED_SEMANTIC_PROJECTION_WITH_EXPLICIT_UNKNOWNS');self.assertIs(r['pair'],False);self.assertEqual(r['scientific_scope'],'DETACH_OBSERVER_DIAGNOSTIC_POINT_V1')
 def test_generic_pair_label_refused(self):
  d=real_point();d['acceptance']['status']='CURRENT_ACCEPTED';d['acceptance']['pair']=True;self.assertEqual(analyze(d)['status'],'INVALID')
 def test_point_label_cannot_disguise_pair(self):
  d=real_point();d['acceptance']['pair']=True;self.assertEqual(analyze(d)['status'],'INVALID')
 def test_wrong_scientific_scope(self):
  d=real_point();d['acceptance']['scientific_scope']='S_F_FORMAL_PAIR';self.assertEqual(analyze(d)['status'],'INVALID')
 def test_negative_interval(self):
  d=doc();add(d,'detach_success',0);d['coverage']['c_detach_success']['interval']=[-1,10];self.assertEqual(analyze(d)['status'],'INVALID')
 def test_bool_interval(self):
  d=doc();add(d,'detach_success',0);d['coverage']['c_detach_success']['interval']=[False,10];self.assertEqual(analyze(d)['status'],'INVALID')
 def test_above_uint64(self):
  d=doc();add(d,'detach_success',2**64);self.assertEqual(analyze(d)['status'],'INVALID')
 def test_uint64_max_valid(self):
  d=doc();add(d,'detach_success',2**64-1);self.assertEqual(analyze(d)['status'],'SYNTHETIC_CONTROL_ONLY')
 def test_missing_Q(self):
  d=real_point();del d['identity']['qualification_id'];r=analyze(d);self.assertEqual(r['status'],'INCOMPLETE');self.assertFalse(r['measured_facts'])
 def test_malformed_Q(self):
  d=real_point();d['identity']['qualification_id']='unbound-Q';r=analyze(d);self.assertEqual(r['status'],'INVALID');self.assertFalse(r['measured_facts'])
 def test_missing_binary_identity(self):
  d=real_point();del d['identity']['binary_sha256'];self.assertEqual(analyze(d)['status'],'INCOMPLETE')
 def test_incomplete_reference(self):
  d=real_point();del d['acceptance']['adapter_ref']['sha256'];self.assertEqual(analyze(d)['status'],'INVALID')

if __name__=='__main__':unittest.main()
