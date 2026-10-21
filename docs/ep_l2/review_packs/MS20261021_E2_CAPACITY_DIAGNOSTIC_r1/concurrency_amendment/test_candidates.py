"""Bounded synthetic admission checks only; no central transaction/app/native."""
from pathlib import Path
import copy,hashlib,json,sys,unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(HERE/'candidate'))
import coordinator as c,concurrency_policy as cp,policy_v2
from registry import Registry,FINAL_INTAKE_AUTHORITY
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
raw=REG.read_bytes();BASE=json.loads(raw)
class Guards(unittest.TestCase):
 def setUp(self):
  self.data=copy.deepcopy(BASE);self.item=self.data[c.FIELD]
  self.data['runs']={};self.data['resource_leases']={};self.host=self.item['host']
  self.data['final_intake_policy']=dict(authority_commit=FINAL_INTAKE_AUTHORITY,max_lane5_simulators=3,
    producer_build_pending=False,producer_workspace_reserve_bytes=2*c.GIB)
  self.live=dict(available_memory_bytes=256*c.GIB,disk_free_bytes=40*c.GIB,share_disk_free_bytes=44*c.GIB)
  self.usage=dict(old_bytes=13*c.GIB,new_bytes=6*c.GIB,total_bytes=19*c.GIB)
  self.enterContext(patch.object(c,'retained_tree_bytes',return_value=0))
 def row(self,cpu=1,memory=c.GIB,**changes):
  return dict(host=self.host,status='RUNNING',cpu_units=cpu,memory_bytes=memory,scan=False,
   result_directory='/workspace/never_created_e2_concurrency_synthetic',disk_growth_bytes=128*2**20,
   experiment_id=c.CAMPAIGN,**changes)
 def add(self,n,memory=c.GIB):self.data['runs']={str(i):self.row(memory=memory) for i in range(n)}
 def gate(self,kind='simulation',cpu=1,memory=c.GIB,growth=128*2**20,scan=False):
  return c.resource_gate(self.data,kind,cpu,memory,growth,self.live,self.usage,scan)
 def test_exact_approval_active(self):self.assertTrue(cp.active(self.item))
 def test_applied_status_supported(self):
  self.item['formal_simulator_concurrency']['status']='APPLIED';self.assertTrue(cp.active(self.item))
 def test_status_tamper_rejected(self):
  self.item['formal_simulator_concurrency']['status']='UNLIMITED_ALL_RESOURCES'
  with self.assertRaisesRegex(ValueError,'record'):cp.active(self.item)
 def test_sha_tamper_rejected(self):
  self.item['formal_simulator_concurrency']['approval']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'approval binding'):cp.active(self.item)
 def test_other_project_not_covered(self):
  self.item['campaign_id']='TLS'
  with self.assertRaisesRegex(ValueError,'exact E2'):cp.active(self.item)
 def test_five_simulator_count_caps_removed_when_resources_fit(self):
  self.add(5);self.gate()
 def test_four_8g_apps_allowed_by_remaining_resources(self):
  self.add(3,memory=8*c.GIB);self.gate(memory=8*c.GIB)
 def test_cpu8_still_rejects(self):
  self.add(8)
  with self.assertRaisesRegex(ValueError,'CPU quota'):self.gate()
 def test_reserved_ram32_still_rejects(self):
  self.add(4,memory=8*c.GIB)
  with self.assertRaisesRegex(ValueError,'memory reservation'):self.gate(memory=8*c.GIB)
 def test_host_available64_after_pending_still_rejects(self):
  self.add(3,memory=8*c.GIB);self.live['available_memory_bytes']=95*c.GIB
  with self.assertRaisesRegex(ValueError,'64GiB'):self.gate(memory=8*c.GIB)
 def test_workspace5_plus2_plus_growth_still_rejects(self):
  self.live['disk_free_bytes']=7*c.GIB
  with self.assertRaisesRegex(ValueError,'workspace floor'):self.gate()
 def test_pending_writes_still_reserved(self):
  self.add(3);self.live['disk_free_bytes']=7*c.GIB+128*2**20
  with self.assertRaisesRegex(ValueError,'workspace floor'):self.gate()
 def test_share40_still_rejects(self):
  self.live['share_disk_free_bytes']=40*c.GIB-1
  with self.assertRaisesRegex(ValueError,'Share'):self.gate()
 def test_new10_result_ceiling_still_rejects(self):
  self.usage['new_bytes']=10*c.GIB
  with self.assertRaisesRegex(ValueError,'new-study result'):self.gate()
 def test_total24_result_ceiling_still_rejects(self):
  self.usage['total_bytes']=24*c.GIB
  with self.assertRaisesRegex(ValueError,'old\+new'):self.gate()
 def test_requested_scan_exclusive_still_rejects(self):
  self.add(1)
  with self.assertRaisesRegex(ValueError,'scan needs exclusive'):self.gate(scan=True)
 def test_existing_scan_exclusive_still_rejects(self):
  self.data['runs']['scan']=self.row();self.data['runs']['scan']['scan']=True
  with self.assertRaisesRegex(ValueError,'scan needs exclusive'):self.gate()
 def test_engineering_pilot_exclusive_still_rejects(self):
  self.data['resource_leases']['p']=self.row(kind='ENGINEERING_PILOT')
  with self.assertRaisesRegex(ValueError,'engineering pilot'):self.gate()
 def test_exclusive_disk_build_still_rejects(self):
  self.data['resource_leases']['b']=self.row(disk_authorization_id='unchanged_scope')
  with self.assertRaisesRegex(ValueError,'exclusive task-scoped disk build'):self.gate()
 def test_malformed_final_intake_policy_rejected(self):
  self.data['final_intake_policy']['max_lane5_simulators']=9
  with self.assertRaisesRegex(ValueError,'invalid bounded final-intake'):self.gate()
 def test_legacy_registry_itself_unchanged_and_rejects_count(self):
  self.add(5);view=copy.deepcopy(self.data);view['hosts'][self.host]['min_disk_free_bytes']=5*c.GIB
  with self.assertRaisesRegex(ValueError,'producer-priority simulator quota'):Registry.admission(view,self.host,1,c.GIB,False,'simulation',self.live)
 def test_no_amendment_keeps_e_count_target(self):
  self.item.pop('formal_simulator_concurrency');self.add(2)
  with self.assertRaisesRegex(ValueError,'E campaign simulator quota'):self.gate()
 def test_screen_uses_original_count_caps(self):
  self.add(4)
  with self.assertRaisesRegex(ValueError,'global shared simulator quota'):self.gate(kind='screen')
 def test_build_test_scope_not_extended(self):
  self.assertFalse(cp.resource_only(self.item,'build'));self.assertFalse(cp.resource_only(self.item,'test'))
  with self.assertRaisesRegex(ValueError,'A build max'):self.gate(kind='build',cpu=3)
 def test_no_policy_or_history_mutation(self):
  self.add(5);before=copy.deepcopy(self.data);self.gate();self.assertEqual(before,self.data)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Guards))
 report=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,
  failures=len(result.failures),errors=len(result.errors),synthetic_non_application_controls=True,
  application_starts=0,native_invocations=0,registry_writes=0,CLIENT_writes=0,
  canonical_registry_before_sha256=hashlib.sha256(raw).hexdigest(),
  canonical_registry_after_sha256=hashlib.sha256(REG.read_bytes()).hexdigest(),
  qualifier='Canonical registry may change independently as the existing controller naturally drains; this script never opens a registry write transaction')
 (HERE/'BOUNDED_CONTROL_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
 sys.exit(0 if result.wasSuccessful() else 1)
