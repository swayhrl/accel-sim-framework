"""CPU fake identities only; original review runner is never executed."""
from pathlib import Path
import copy,importlib.util,json,tempfile,unittest
P=Path(__file__).with_name('oracle_actual_review_watch.py');s=importlib.util.spec_from_file_location('MOCK_REVIEW_WATCH',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class Tests(unittest.TestCase):
 def data(self):
  modes=['OFF_MATCHED','M_DATAREAD','L2_DATAREAD','L1_DATAREADY'];points=[]
  for i in range(8):
   for mode in modes:points.append(dict(cohort='MOCK_'+str(i)+'_'+mode,input_digest='MOCK_SHA'+str(i),plan_id='MOCK_PLAN'+str(i)+mode,mode=mode))
  plan=dict(qualified_modes=modes[1:],initial_qualifiers={mode:'MOCK_0_'+mode for mode in modes})
  results={x['cohort']:dict(MOCK_NOT_SCIENCE=True)for x in points}
  return plan,points,results

 def test_fixed8_three_modes_share_off8(self):
  plan,p,r=self.data();existing=set(plan['initial_qualifiers'].values())
  jobs=m.select_ready(plan,p,r,existing,{})
  self.assertEqual({x['subject']for x in jobs},set(plan['qualified_modes']))

 def test_scan_off_missing_holds_all_modes(self):
  plan,p,r=self.data();r['MOCK_7_OFF_MATCHED']=None
  self.assertEqual(m.select_ready(plan,p,r,set(plan['initial_qualifiers'].values()),{}),[])

 def test_one_mode_missing_does_not_hold_other_modes(self):
  plan,p,r=self.data();r['MOCK_7_M_DATAREAD']=None
  jobs=m.select_ready(plan,p,r,set(plan['initial_qualifiers'].values()),{})
  self.assertEqual({x['subject']for x in jobs},{'L2_DATAREAD','L1_DATAREADY'})

 def test_missing_qualifier_review_precedes_own_mode_gate(self):
  plan,p,r=self.data();existing=set(plan['initial_qualifiers'].values())-{'MOCK_0_M_DATAREAD'}
  jobs=m.select_ready(plan,p,r,existing,{})
  self.assertIn(dict(kind='cohort',subject='MOCK_0_M_DATAREAD'),jobs)
  self.assertNotIn(dict(kind='mode',subject='M_DATAREAD'),jobs)

 def test_existing_reviews_are_not_scheduled_again(self):
  plan,p,r=self.data()
  self.assertEqual(m.select_ready(plan,p,r,set(plan['initial_qualifiers'].values()),set(plan['qualified_modes'])),[])

 def test_capture_duplicate_or_non32_refused(self):
  plan,p,r=self.data()
  with self.assertRaises(m.Hold):m.select_ready(plan,p[:-1],r,set(),set())
  q=copy.deepcopy(p);q[1]=copy.deepcopy(q[0])
  with self.assertRaises(m.Hold):m.select_ready(plan,q,r,set(),set())

 def test_result_requires_exact_identity_and_accepted_status(self):
  plan,p,r=self.data();row=p[0]
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_REVIEW_')as d:
   path=Path(d)/'analysis'/(row['cohort']+'.RESULT.json');path.parent.mkdir()
   v=dict(state=m.PASS,cohort=row['cohort'],input_digest=row['input_digest'],plan_id=row['plan_id'],oracle_mode=row['mode'],uuid='MOCK_UUID',proof=dict(performance_accepted=True))
   path.write_text(json.dumps(v)+'\n');self.assertEqual(m.closed_result(d,row)['uuid'],'MOCK_UUID')
   for status in ['HOLD','NEGATIVE','PENDING']:
    path.write_text(json.dumps(dict(v,state=status))+'\n');self.assertIsNone(m.closed_result(d,row))
   path.write_text(json.dumps(dict(v,input_digest='WRONG'))+'\n')
   with self.assertRaises(m.Hold):m.closed_result(d,row)

 def test_partially_written_result_never_becomes_a_gate(self):
  plan,p,r=self.data();row=p[0]
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_REVIEW_PARTIAL_')as d:
   path=Path(d)/'analysis'/(row['cohort']+'.RESULT.json');path.parent.mkdir();path.write_bytes(b'{"state":')
   self.assertIsNone(m.closed_result(d,row))

 def test_no_speed_threshold_or_per_program_selection(self):
  plan,p,r=self.data()
  for c in r:r[c]['cycles']=10**30 if 'M_DATAREAD'in c else 1
  self.assertEqual(len(m.select_ready(plan,p,r,set(plan['initial_qualifiers'].values()),{})),3)

if __name__=='__main__':unittest.main(verbosity=2)
