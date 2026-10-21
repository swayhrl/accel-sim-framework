"""Existing mocked scheduler controls plus removed-deadline cases; zero apps."""
from pathlib import Path
import importlib.util,sys,unittest
from unittest.mock import patch
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'candidate'));sys.path.insert(1,str(P.parents[4]/'util/ep_l2/mechanism_e'))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=load('original_scheduler_controls',P.parent/'concurrency_amendment/test_controller_candidate.py')
new=load('none_controller',P/'candidate/controller.py');base.m=new
class Controls(base.Controls):
 def test_none_deadline_admits_after_historical_cutoff(self):
  with patch.object(new.capacity_policy,'effective_limits',return_value=dict(start_deadline_unix=None,intake_deadline_unix=None)),patch.object(new.time,'time',return_value=10**12):
   r=self.run_step(3)
  self.assertEqual(len(self.submitted),3);self.assertEqual(r['queue_remaining_count'],0)
 def test_expired_legacy_deadline_does_not_dispatch(self):
  with patch.object(new.capacity_policy,'effective_limits',return_value=dict(start_deadline_unix=100,intake_deadline_unix=200)),patch.object(new.time,'time',return_value=101):
   r=self.run_step(3)
  self.assertFalse(self.submitted);self.assertEqual(r['queue_remaining_count'],3)
if __name__=='__main__':unittest.main()
