"""Offline missing-counter regressions; no native/runtime test or application."""
import unittest
from capacity_incremental import aggregate
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
if __name__=='__main__':unittest.main()
