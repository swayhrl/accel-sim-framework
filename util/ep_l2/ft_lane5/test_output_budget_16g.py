"""Authorized16GiB boundary and disappeared-file race; no real allocation."""
import pathlib,socket,tempfile,unittest
from unittest.mock import patch
from registry import admit_result_output,retained_tree_bytes
from run import tree_bytes
from test_lane5 import identity
class OutputBudget16G(unittest.TestCase):
 def setUp(self):
  self.host=socket.gethostname();self.data={'hosts':{self.host:{'max_result_bytes':16*2**30,'default_run_output_limit_bytes':2*2**30,'min_disk_free_bytes':48*2**30}},'runs':{}}
  self.state={'actual_bytes':12*2**30,'resources':{'disk_free_bytes':70*2**30,'share_disk_free_bytes':41*2**30}}
 def admit(self):
  with patch('registry.live_result_output',return_value=self.state):return admit_result_output(self.data,self.host,identity(),'/unused')
 def test_12_no_longer_total_boundary(self):self.assertEqual(self.admit()['predicted_growth_bytes'],2*2**30+128*2**20)
 def test_at_and_above16_fail_closed(self):
  for size in [16*2**30,16*2**30+1]:
   self.state['actual_bytes']=size
   with self.assertRaisesRegex(ValueError,'ceiling'):self.admit()
  self.assertEqual(self.data['runs'],{})
 def test_prediction_and_cross_campaign_reservations(self):
  self.state['actual_bytes']=15*2**30
  with self.assertRaisesRegex(ValueError,'predicted growth'):self.admit()
  self.state['actual_bytes']=12*2**30;self.data['runs']['other']={'status':'RUNNING','result_directory':'/not-existing','output_budget':{'predicted_growth_bytes':2*2**30}}
  with self.assertRaisesRegex(ValueError,'predicted growth'):self.admit()
 def test_floors_still_fail_closed(self):
  for key,value in [('disk_free_bytes',49*2**30),('share_disk_free_bytes',39*2**30)]:
   old=self.state['resources'][key];self.state['resources'][key]=value
   with self.assertRaises(ValueError):self.admit()
   self.state['resources'][key]=old
class RetainedBytesRace(unittest.TestCase):
 def test_disappeared_atomic_temp_does_not_abort_monitor(self):
  with tempfile.TemporaryDirectory() as name:
   root=pathlib.Path(name);(root/'raw.log').write_bytes(b'12345');vanished=root/'.progress.json.tmp';vanished.write_bytes(b'123');original=pathlib.Path.stat
   def racing(path,*args,**kwargs):
    if path==vanished:raise FileNotFoundError(str(path))
    return original(path,*args,**kwargs)
   with patch.object(pathlib.Path,'stat',racing):self.assertEqual(retained_tree_bytes(root),5);self.assertEqual(tree_bytes(root),5)
 def test_permission_error_is_not_silenced_and_symlinks_not_counted(self):
  with tempfile.TemporaryDirectory() as name:
   root=pathlib.Path(name);p=root/'raw';p.write_bytes(b'12345');(root/'link').symlink_to(p);self.assertEqual(retained_tree_bytes(root),5);original=pathlib.Path.stat
   def denied(path,*args,**kwargs):
    if path==p:raise PermissionError(str(path))
    return original(path,*args,**kwargs)
   with patch.object(pathlib.Path,'stat',denied),self.assertRaises(PermissionError):retained_tree_bytes(root)
if __name__=='__main__':unittest.main()
