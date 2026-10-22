"""SYNTHETIC phase event/population counterexamples; no native/application claims."""
import json,sys,unittest
from pathlib import Path
import terminal_analysis as m
sys.path.insert(0,str(m.PACK/'analysis_r4'))
project=m.load_code(m.PACK/'analysis_r4/project.py','_phase_test_projection')
def counts():return dict.fromkeys(project.FIELDS,0)
def witness():
 phases={};fields=project.FIELDS
 for sid in range(64):
  for phase in range(4):
   c=counts()
   if sid==0 and phase==2:c.update(detach_calls=1,detach_success=1)
   if sid==0 and phase==3:c.update(detached_retired=1)
   phases[(sid,phase)]={'kernel_scope':'UNASSIGNED' if phase==0 else 'OVERLAP_UNKNOWN' if phase==1 else 'SINGLE_ACTIVE_INTERVAL','counters':c,'live_detached':0,'epoch_closed':True}
 globalcounts={f:sum(r['counters'][f] for r in phases.values()) for f in fields}
 observer={'phase_catalog':{0:None,1:None,2:1,3:2},'schema_counter_fields':fields,'global_counters':globalcounts}
 return phases,observer
class PhasePopulationControls(unittest.TestCase):
 def test_real_project_prior_false_error_witness_preserved(self):
  c=counts();c['detached_retired']=1;r=project.panels(c);self.assertIn('negative derived detach_success-detached_retired',r['errors'])
 def test_crossphase_detach_and_retire_legal_numeric_projection(self):
  p,o=witness();r=m.phase_projection(p,o,project);self.assertEqual(r['rows']['2']['global_samephase_counters']['detach_success'],1);self.assertEqual(r['rows']['3']['global_samephase_counters']['detached_retired'],1)
  for row in r['rows'].values():self.assertIsNone(row['global_panels']['derived']['terminal_detached_residual']);self.assertEqual(row['global_panels']['phase_population_state']['terminal_detached_residual'],'NA_NOT_A_PHASE_LOCAL_POPULATION')
 def test_positive_phase_balance_also_not_live_population(self):
  c=counts();c['detach_success']=1;r=m.phase_panels(c,project);self.assertEqual(r['counts']['detach_success'],1);self.assertIsNone(r['derived']['terminal_detached_residual']);self.assertEqual(r['errors'],[])
 def test_real_other_negative_probed_denominator_still_rejected(self):
  p,o=witness();p[(0,2)]['counters']['probe_skipped']=1;o['global_counters']['probe_skipped']=1
  with self.assertRaisesRegex(ValueError,'invalid phase numeric values'):m.phase_projection(p,o,project)
 def test_invalid_uint64_retirement_still_rejected(self):
  c=counts();c['detached_retired']=-1;r=m.phase_panels(c,project);self.assertIn('invalid uint64 detached_retired',r['errors'])
 def test_phase_counter_rollup_mismatch_still_rejected(self):
  p,o=witness();o['global_counters']['detached_retired']=2
  with self.assertRaisesRegex(ValueError,'numeric phase rollup differs'):m.phase_projection(p,o,project)
if __name__=='__main__':unittest.main()
