"""Temporary CPU filesystem/owner-ACK fixtures, never a real administrative run."""
from pathlib import Path
import copy,importlib.util,json,tempfile,time,unittest
p=Path(__file__).with_name('unused_binding_admin_helper.py');s=importlib.util.spec_from_file_location('CPU_ONLY_ADMIN',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Fixture:
 def __init__(self,root,mutation=None):
  self.root=root;self.pause=root.parent/'control/ENGINEERING_PAUSE_NEW.json';self.pause.parent.mkdir(parents=True);self.binding=root/'control/dispatch_bindings/C.json';self.binding.parent.mkdir(parents=True)
  self.binding.write_bytes(m.encoded(dict(cohort='C',host_cpu=135)));self.bs=m.sha(self.binding);self.calls=0;self.mutation=mutation
  self.base=dict(q=dict(request=m.REQUEST,owner_pid=m.OWNER,owner_start_ticks=m.START,budget=96,remaining=96,consumed={},admitted_specs={'C':'MOCK'}),
   intents=[],claims={'OTHER':dict(cohort='OTHER',host_cpu=135)},stage_claims={'OTHER':dict(cohort='OTHER',host_cpu=135)},
   running=['OTHER'],preparing=['OTHER'],mapped_live_cohorts=['OTHER'],binding_sha256=self.bs,
   errors={'HISTORICAL_ARM_ERROR':'RETAINED'},cycle_fingerprints={},gates={},batch_mtime_ns=time.time_ns()+10**10,pool_mtime_ns=time.time_ns()+10**10,pool_owner=(m.OWNER,m.START))
 def snapshot(self,cohort):
  self.calls+=1;v=copy.deepcopy(self.base);v['binding_sha256']=m.sha(self.binding)if self.binding.exists()else None
  if self.mutation:self.mutation(self,v,self.calls)
  return v
 def observation(self):
  return dict(target=dict(cohort='C',binding_sha256=self.bs,binding_cpu=135,picker_free_cpu=69),snapshot=copy.deepcopy(self.base))
class Tests(unittest.TestCase):
 def setup_fixture(self,root,mutation=None):
  m.ROOT=root;return Fixture(root,mutation)
 def test_default_inert(self):self.assertEqual(m.main([])['registry_writes'],0)
 def test_safe_repair_keeps_binding_bytes_and_only_clears_own_pause(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_ADMIN_ONLY_')as d:
   f=self.setup_fixture(Path(d)/'new/remaining24');audit=Path(d)/'AUDIT';m.repair(f,f.observation(),audit)
   self.assertFalse(f.binding.exists());self.assertFalse(f.pause.exists());self.assertEqual(m.sha(audit/'ORIGINAL_UNUSED_BINDING.json'),f.bs);self.assertTrue((audit/'ORIGINAL_SELF_PAUSE.json').exists())
 def mutation_case(self,mutation,expect_binding=True):
  with tempfile.TemporaryDirectory(prefix='MOCK_ADMIN_ONLY_')as d:
   f=self.setup_fixture(Path(d)/'new/remaining24',mutation);audit=Path(d)/'AUDIT'
   with self.assertRaises(m.Hold):m.repair(f,f.observation(),audit)
   self.assertTrue(f.pause.exists());self.assertEqual(f.binding.exists(),expect_binding)
 def test_new_other_error_during_ACK_never_clears_pause(self):
  self.mutation_case(lambda f,v,n:v['errors'].update({'OTHER':'UNEXPECTED'})if n>=2 else None)
 def test_new_other_error_after_rename_never_clears_pause(self):
  self.mutation_case(lambda f,v,n:v['errors'].update({'OTHER':'UNEXPECTED'})if n>=4 else None,False)
 def test_consumed_race_after_ACK_keeps_pause(self):
  def mutate(f,v,n):
   if n>=3:v['q']['consumed']['C']={'uuid':'MOCK'};v['q']['remaining']=95
  self.mutation_case(mutate)
 def test_INTENT_race_after_ACK_keeps_pause(self):
  self.mutation_case(lambda f,v,n:v['intents'].append('C')if n>=3 else None)
 def test_claim_race_after_ACK_keeps_pause(self):
  self.mutation_case(lambda f,v,n:v['claims'].update({'C':dict(cohort='C')})if n>=3 else None)
 def test_running_race_after_ACK_keeps_pause(self):
  self.mutation_case(lambda f,v,n:v['preparing'].append('C')if n>=3 else None)
 def test_foreign_pause_replacement_refused_before_binding_mutation(self):
  def mutate(f,v,n):
   if n==3:f.pause.write_bytes(b'FOREIGN_PAUSE')
  self.mutation_case(mutate)
 def test_bindinghash_race_refused(self):
  def mutate(f,v,n):
   if n==3:f.binding.write_bytes(b'CHANGED');v['binding_sha256']=m.sha(f.binding)
  self.mutation_case(mutate)
 def test_natural_collision_disappearance_is_skip(self):
  def mutate(f,v,n):
   if n>=3:v['claims']={};v['stage_claims']={};v['mapped_live_cohorts']=[]
  with tempfile.TemporaryDirectory(prefix='MOCK_ADMIN_ONLY_')as d:
   f=self.setup_fixture(Path(d)/'new/remaining24',mutate);value=m.repair(f,f.observation(),Path(d)/'AUDIT')
   self.assertEqual(value['status'],'SKIP_NO_LONGER_BLOCKED');self.assertTrue(f.binding.exists());self.assertFalse(f.pause.exists())
 def test_foreign_owner_refused(self):
  with tempfile.TemporaryDirectory()as d:
   f=self.setup_fixture(Path(d)/'new/remaining24');v=copy.deepcopy(f.base);v['q']['owner_pid']=1
   with self.assertRaises(m.Hold):m.inspect_unused(v,'C',f.bs)
 def test_resource_busy_not_misclassified_as_binding_conflict(self):
  with tempfile.TemporaryDirectory()as d:
   f=self.setup_fixture(Path(d)/'new/remaining24');resources=dict(physical_RAM_pass=False,physical_disk_pass=True,admission_disk_pass=True,admission_pressure_pass=True)
   with self.assertRaises(m.Hold):m.target_from_picker(dict(cohort='C',host_cpu=69),dict(cohort='C',host_cpu=135),f.base,resources)
 def test_actual_claim_without_mapped_live_not_enough(self):
  with tempfile.TemporaryDirectory()as d:
   f=self.setup_fixture(Path(d)/'new/remaining24');f.base['mapped_live_cohorts']=[];resources=dict.fromkeys(['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass'],True)
   with self.assertRaises(m.Hold):m.target_from_picker(dict(cohort='C',host_cpu=69),dict(cohort='C',host_cpu=135),f.base,resources)
 def test_no_double_repair_of_same_audit_directory(self):
  with tempfile.TemporaryDirectory()as d:
   f=self.setup_fixture(Path(d)/'new/remaining24');a=Path(d)/'AUDIT';m.repair(f,f.observation(),a)
   with self.assertRaises(FileExistsError):m.repair(f,f.observation(),a)
if __name__=='__main__':unittest.main()
