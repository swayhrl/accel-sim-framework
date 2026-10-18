"""Four direct-user forecast waivers; original hard floors, totals and dedup remain."""
import copy,hashlib,json,pathlib,socket,tempfile,unittest
from unittest.mock import patch
import registry as rg
import test_lane5 as fixtures
class FourStart(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);p=pathlib.Path(self.tmp.name)/'user.md';p.write_text('Direct user: start four now; parallel space recovery. Keep actual hard floor.')
  self.i=fixtures.identity();self.host=socket.gethostname();self.policy={'boot_id':'testboot','max_result_bytes':16*2**30,'min_disk_free_bytes':48*2**30,'default_run_output_limit_bytes':2*2**30}
  keys=[]
  for n in range(4):
   i=copy.deepcopy(self.i);i['runtime_config_sha256']=str(n)*64;keys.append(rg.run_key(i))
  keys[0]=rg.run_key(self.i)
  self.token={'schema':'USER_AUTHORIZED_FOUR_START_FORECAST_EXCEPTION_V1','status':'ACTIVE','maximum_fresh_starts':4,'run_keys':keys,'host':self.host,'boot_id':'testboot','hard_min_disk_free_bytes':48*2**30,'max_result_bytes':16*2**30,'start_before_unix':200,'authorization_file':{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}}
  self.data={'hosts':{self.host:self.policy},'runs':{},'four_start_forecast_exception':self.token};self.state={'actual_bytes':8*2**30,'resources':{'disk_free_bytes':49*2**30,'share_disk_free_bytes':41*2**30}}
  self.clock=patch('registry.time.time',return_value=100);self.clock.start();self.addCleanup(self.clock.stop)
 def admit(self,i=None):
  with patch('registry.live_result_output',return_value=self.state):return rg.admit_result_output(self.data,self.host,i or self.i,'/unused')
 def test_exact_user_key_waives_only_growth_reservation(self):
  a=self.admit();self.assertIsNotNone(a['disk_growth_reservation_exception']);self.assertEqual(self.policy['min_disk_free_bytes'],48*2**30)
 def test_other_keys_keep_normal_reservation(self):
  i=copy.deepcopy(self.i);i['binary_sha256']='f'*64
  with self.assertRaisesRegex(ValueError,'conservative'):self.admit(i)
 def test_expired_wrong_host_wrong_boot_and_cap_fail_closed(self):
  for k,v in [('start_before_unix',100),('host','wrong'),('boot_id','wrong'),('maximum_fresh_starts',5)]:
   old=self.token[k];self.token[k]=v
   with self.assertRaises(ValueError):self.admit()
   self.token[k]=old
 def test_actual48_and_share40_not_waived(self):
  for key,value in [('disk_free_bytes',48*2**30-1),('share_disk_free_bytes',40*2**30-1)]:
   old=self.state['resources'][key];self.state['resources'][key]=value
   with self.assertRaises(ValueError):self.admit()
   self.state['resources'][key]=old
 def test_total16_and_concurrent_growth_not_waived(self):
  self.state['actual_bytes']=16*2**30
  with self.assertRaisesRegex(ValueError,'ceiling'):self.admit()
  self.state['actual_bytes']=15*2**30
  with self.assertRaisesRegex(ValueError,'predicted'):self.admit()
 def test_existing_key_cannot_replay_exception_for_retry(self):
  self.data['runs'][rg.run_key(self.i)]={'status':'FAILED','result_directory':'/unused'}
  with self.assertRaisesRegex(ValueError,'conservative'):self.admit()
 def test_changed_authorization_refused(self):
  pathlib.Path(self.token['authorization_file']['path']).write_text('changed')
  with self.assertRaisesRegex(ValueError,'authorization changed'):self.admit()
if __name__=='__main__':unittest.main()
