import unittest
from absolute_ep_gate import decide
class Test(unittest.TestCase):
 def test_two1pct(self):self.assertTrue(decide(10000,9900,9900)["release_combination_candidate"])
 def test_3pct_and0(self):self.assertTrue(decide(10000,9700,10000)["release_combination_candidate"])
 def test_one_regression(self):self.assertFalse(decide(10000,9600,10001)["release_combination_candidate"])
 def test_subthreshold(self):self.assertFalse(decide(10000,9950,9950)["release_combination_candidate"])
 def test_no_EP_gain_despite_S_slow(self):self.assertFalse(decide(550642,551783,551783)["release_combination_candidate"])
 def test_zero_invalid(self):
  with self.assertRaises(ValueError):decide(0,1,1)
if __name__=="__main__":unittest.main()
