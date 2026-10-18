"""Final continuation safety: build priority, explicit recovery, bounded live additions."""
import copy,hashlib,json,pathlib,socket,tempfile,unittest
from unittest.mock import patch
import registry as rg
import continue_matrix as cm
import test_lane5 as fixtures
class FinalIntake(unittest.TestCase):
 def setUp(self):
  self.host=socket.gethostname();self.policy={'max_simulators':4,'max_cpu_units':8,'max_reserved_memory_bytes':32*2**30,'max_build_jobs':4,'default_run_memory_bytes':8*2**30,'min_available_memory_bytes':64*2**30,'min_disk_free_bytes':48*2**30,'max_result_bytes':20*2**30,'default_run_output_limit_bytes':2*2**30,'scan_exclusive':True}
  self.intake={'authority_commit':rg.FINAL_INTAKE_AUTHORITY,'max_lane5_simulators':1,'producer_build_pending':True,'producer_workspace_reserve_bytes':2*2**30,'approved_units':[]}
  self.data={'hosts':{self.host:self.policy},'runs':{},'resource_leases':{},'final_intake_policy':self.intake};self.resources={'disk_free_bytes':56*2**30,'share_disk_free_bytes':41*2**30,'available_memory_bytes':160*2**30}
 def test_invalid_final_scope_and_slot_expansion_refused(self):
  for k,v in [('authority_commit','bad'),('max_lane5_simulators',4),('producer_workspace_reserve_bytes',0),('producer_build_pending',1)]:
   old=self.intake[k];self.intake[k]=v
   with self.assertRaises(ValueError):rg.final_intake_policy(self.data)
   self.intake[k]=old
 def test_one_sim_preserves_producer50g_gate(self):
  state={'actual_bytes':12*2**30,'resources':self.resources}
  with patch('registry.live_result_output',return_value=state):a=rg.admit_result_output(self.data,self.host,fixtures.identity(),'/unused')
  self.assertEqual(a['producer_workspace_reserved_bytes'],2*2**30)
  self.data['runs']['a']={'host':self.host,'status':'RUNNING','cpu_units':1,'memory_bytes':4*2**30,'scan':False,'result_directory':'/not-existing'}
  with self.assertRaisesRegex(ValueError,'priority simulator'):rg.Registry.admission(self.data,self.host,1,4*2**30,False,'simulation',self.resources)
  rg.Registry.admission(self.data,self.host,2,8*2**30,False,'build',self.resources)
 def test_build_and_sim_growth_cannot_both_spend_same_space(self):
  self.data['runs']['a']={'host':self.host,'status':'RUNNING','cpu_units':1,'memory_bytes':4*2**30,'scan':False,'result_directory':'/not-existing'}
  self.resources['disk_free_bytes']=52*2**30
  with self.assertRaisesRegex(ValueError,'producer50GiB'):rg.Registry.admission(self.data,self.host,2,8*2**30,False,'build',self.resources)
 def test_release_priority_allows_three_but_not_four_slots(self):
  self.intake['producer_build_pending']=False;self.intake['max_lane5_simulators']=3
  for n in range(3):self.data['runs'][str(n)]={'host':self.host,'status':'RUNNING','cpu_units':1,'memory_bytes':8*2**30,'scan':False,'result_directory':'/not-existing'}
  with self.assertRaisesRegex(ValueError,'priority simulator'):rg.Registry.admission(self.data,self.host,1,4*2**30,False,'simulation',self.resources)
 def test_actual_hard_floor_and_total20_not_waived(self):
  self.resources['disk_free_bytes']=48*2**30-1
  with self.assertRaises(ValueError):rg.Registry.admission(self.data,self.host,1,4*2**30,False,'simulation',self.resources)
  with patch('registry.live_result_output',return_value={'actual_bytes':20*2**30,'resources':self.resources}),self.assertRaisesRegex(ValueError,'ceiling'):rg.admit_result_output(self.data,self.host,fixtures.identity(),'/unused')
 def test_scheduler_lock_excludes_second_owner(self):
  with tempfile.TemporaryDirectory() as name:
   p=pathlib.Path(name)/'controller.lock'
   with cm.controller_guard(p):
    with self.assertRaises(ValueError):
     with cm.controller_guard(p):pass
   with cm.controller_guard(p):pass
 def test_audited_retry_is_explicit_and_never_replays_next_failure(self):
  with tempfile.TemporaryDirectory() as name:
   root=pathlib.Path(name);old=root/'old';old.mkdir();(old/'raw.log').write_text('old preserved raw');(old/'run_status.json').write_text('{}');i=fixtures.identity();key=rg.run_key(i);proof=root/'retry.json';recovery={'run_key':key,'previous_lease_id':'previous','new_result_directory':str(root/'new'),'engineering_reason':'documented resource recovery','old_raw_sha256':cm.digest(old/'raw.log'),'old_terminal_sha256':cm.digest(old/'run_status.json')};proof.write_text(json.dumps(recovery));spec={'identity':i,'retry_checkpoint':{'path':str(proof),'sha256':cm.digest(proof)}};row={'run_key':key,'identity':i,'owner':'lane5','status':'RESOURCE_LIMIT','result_directory':str(old),'lease_id':'previous'};snapshot={'runs':{key:row}};before=copy.deepcopy(snapshot)
   with patch.object(cm,'OUT',root):
    cm.validate_adopted_retry(spec,snapshot);self.assertEqual(cm.disposition(spec,snapshot,set()),'AUDITED_RETRY_READY');self.assertEqual(snapshot,before)
    self.assertEqual(cm.disposition({'identity':i},snapshot,set()),'RESOURCE_LIMIT')
    row['lease_id']='next-failed-attempt'
    with self.assertRaises(ValueError):cm.validate_adopted_retry(spec,snapshot)
 def test_unbound_live_units_and_existing_rebinding_refused(self):
  with self.assertRaises(ValueError):cm.approved_intake_units([],{ 'final_intake_policy':{'approved_units':[{'id':'x'}]}})
  u={'id':'existing','kind':'single','specs':[]};changed={**u,'kind':'pair'};payload=json.dumps([changed],sort_keys=True,separators=(',',':'),allow_nan=False).encode();s={'final_intake_policy':{'approved_units':[changed],'approved_units_sha256':hashlib.sha256(payload).hexdigest(),'approved_units_publication':'a'*40}}
  with self.assertRaises(ValueError):cm.approved_intake_units([(u,[])],s)
if __name__=='__main__':unittest.main()
