"""SYNTHETIC small helper adversarial checks only, no native/app acceptance."""
import copy,unittest
from pathlib import Path
import terminal_analysis as m

def scenario():
 spec={'identity':{'counter_fixture':'SYNTHETIC'},'qualification_id':'q'};a={'attempt_id':'E999_deadbeef','state':'COMPLETE_VALID','actual_start':True,'scientific_scope':m.SCI,'identity':spec['identity'],'qualification_id':'q','run_key':m.csha(spec['identity'])};entry={k:a[k] for k in ['identity','qualification_id','run_key','scientific_scope']};qr={'path':'/tmp/SYNTHETIC_Q','sha256':'q'};return {'attempts':[a],'accepted_results':{a['attempt_id']:entry},'qualifications':{'q':qr},'scientific_holds':{}},spec
class SyntheticHelpers(unittest.TestCase):
 def check(self,item,spec):return m.require_accepted(item,'E999_deadbeef',spec,Path('/tmp/SYNTHETIC_Q'))
 def test_realstatus_withoutacceptedpointer_refused(self):
  i,s=scenario();i['accepted_results']={}
  with self.assertRaises(ValueError):self.check(i,s)
 def test_exit0_or_processgone_not_accepted(self):
  i,s=scenario();i['attempts'][0].update(state='FAILED',exit_code=0)
  with self.assertRaises(ValueError):self.check(i,s)
 def test_changed_qid_refused(self):
  i,s=scenario();i['accepted_results']['E999_deadbeef']['qualification_id']='other'
  with self.assertRaises(ValueError):self.check(i,s)
 def test_false_actualstart_refused(self):
  i,s=scenario();i['attempts'][0]['actual_start']=False
  with self.assertRaises(ValueError):self.check(i,s)
 def test_even_empty_activehold_refused(self):
  i,s=scenario();i['scientific_holds']['qualification:q']={}
  with self.assertRaises(ValueError):self.check(i,s)
 def test_duplicate_attempt_refused(self):
  i,s=scenario();i['attempts'].append(copy.deepcopy(i['attempts'][0]))
  with self.assertRaises(ValueError):self.check(i,s)
 def test_complete_metadatastructure_only_not_science(self):
  i,s=scenario();a,e,q=self.check(i,s);self.assertEqual(a['attempt_id'],'E999_deadbeef');self.assertNotIn('scientific_application_acceptance_granted',a)
 def counters(self):
  keys=['detach_success','detached_retired','trigger_accepted_after_detach','trigger_denied_after_detach','ro_admits','ro_merges','certified_resident_hits','candidate_deferred_or_native','raw_reservation_fail','observed_heads','probe_skipped','pressure_no_live_ro','pressure_live_ro_no_eligible','way_reuse_seen','way_no_missing','eligible_prod_probe_not_reached','eligible_relief_not_consulted','eligible_frontend_denied'];return dict.fromkeys(keys,0)
 def test_nonzero_detach_is_valid_fact_triggerdenied_distinct(self):
  c=self.counters();c.update(detach_success=2,detached_retired=2,trigger_denied_after_detach=1,ro_admits=5,observed_heads=100,raw_reservation_fail=12)
  r=m.causal_observations(c,{'transactions':5});self.assertIn('NONZERO_DETACH',[x['code'] for x in r]);self.assertIn('DETACHED_VICTIM_TRIGGER_DENIED',[x['code'] for x in r])
 def test_different_populations_not_forced_equal(self):
  c=self.counters();c.update(ro_admits=7,ro_merges=20,observed_heads=100,raw_reservation_fail=4)
  r=m.causal_observations(c,{'transactions':7,'accepted_ro':27});self.assertIsInstance(r,list)
 def test_missing_counter_not_zero_filled(self):
  c=self.counters();del c['way_reuse_seen']
  with self.assertRaises(ValueError):m.causal_observations(c,{'transactions':0})
 def test_noeligible_and_notconsulted_distinct(self):
  c=self.counters();c.update(pressure_live_ro_no_eligible=2,eligible_relief_not_consulted=3)
  r=m.causal_observations(c,{'transactions':0});self.assertIn('LIVE_BUT_NO_ELIGIBLE',[x['code'] for x in r]);self.assertIn('ELIGIBLE_NOT_CONSULTED',[x['code'] for x in r])
 def test_incomplete_phasepopulation_refused(self):
  class Panels:
   def panels(self,c):return {'errors':[]}
  with self.assertRaises(ValueError):m.phase_projection({}, {'phase_catalog':{0:None,1:None},'schema_counter_fields':[]},Panels())
if __name__=='__main__':unittest.main()
