"""Offline missing-counter regressions; no native/runtime test or application."""
import unittest
from capacity_incremental import aggregate,current_pair_matches
class CounterCoverageTests(unittest.TestCase):
 def test_absent_off_capacity_is_unknown(self):
  self.assertEqual(aggregate([{'highwater':None}]*64,'highwater','max'),'UNKNOWN')
 def test_partial_coverage_is_not_a_zero(self):
  self.assertEqual(aggregate([{'capacity_refusals':0},{}],'capacity_refusals','sum'),'UNKNOWN')
 def test_complete_zero_is_measured_zero(self):
  self.assertEqual(aggregate([{'capacity_refusals':0}]*64,'capacity_refusals','sum'),0)
 def test_peaks_are_not_summed(self):
  self.assertEqual(aggregate([{'highwater':5},{'highwater':17}],'highwater','max'),17)
 def test_empty_is_unknown(self):self.assertEqual(aggregate([],'highwater','max'),'UNKNOWN')
class CurrentPointerTests(unittest.TestCase):
 def setUp(self):
  self.pub=dict(baseline_attempt_id='a',variant_attempt_id='b',endpoints=dict(left=dict(attempt_id='a',path='/accepted/a',sha256='old',identity={'binary':'one'}),right=dict(attempt_id='b',path='/accepted/b',sha256='ok',identity={'binary':'one'})))
  self.now=dict(status='CURRENT_ACCEPTED',baseline_attempt_id='a',variant_attempt_id='b')
  self.refs={x['attempt_id']:dict(x) for x in self.pub['endpoints'].values()}
 def test_current_hash_bound_pair(self):self.assertTrue(current_pair_matches(self.pub,self.now,self.refs))
 def test_withdrawal_removes_current_effect(self):self.assertFalse(current_pair_matches(self.pub,None,self.refs))
 def test_repointing_does_not_reuse_old_anchor(self):
  self.refs['a']['sha256']='different'
  self.assertFalse(current_pair_matches(self.pub,self.now,self.refs))
if __name__=='__main__':unittest.main()
