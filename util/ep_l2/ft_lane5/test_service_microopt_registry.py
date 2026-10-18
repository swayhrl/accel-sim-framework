"""Incremental stage only: old ledger, qualification,24/72 and deadline boundaries."""
import copy,hashlib,json,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import registry as rg
import test_lane5 as fixtures

class ServiceStage(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.host=socket.gethostname()
  self.campaign={'authority_commit':'a'*40,'t0_unix':1792236614.5007188,'deadline_unix':1792323014.5007188,'maximum_starts':72,'seed_cells':[{'cell_id':'OLD','condition':'H0','mode':'B16_OFF','workload_alias':'convolutionSeparable'}],'extra_cells':[]}
  data={'authority_host':self.host,'hosts':{self.host:{'max_result_bytes':16*2**30}},'resource_leases':{'other':{'owner':'lane2','status':'RESERVED'}},'runs':{'old':{'experiment_id':rg.PARALLEL,'cell_id':'OLD','status':'FAILED','attempt_history':[{}]*27}},'campaigns':{rg.PARALLEL:self.campaign}}
  rg.write_json(self.root/'RUN_REGISTRY.json',data);self.registry=rg.Registry(self.root)
  self.clock=patch('registry.time.time',return_value=1792292400);self.clock.start();self.addCleanup(self.clock.stop)
 def snapshot(self):return json.loads((self.root/'RUN_REGISTRY.json').read_text())
 def register(self):return self.registry.register_service_microopt_stage(rg.MICROOPT_AUTHORITY)
 def candidate(self):
  i=fixtures.identity();i['workload']='convolutionSeparable';i['ideal_vector']={k:False for k in i['ideal_vector']};logical='MOPT_CONV_B16_OFF_MQ2';q=self.root/'qualified.json';q.write_text('{}')
  p=self.root/'proof.json';rg.write_json(p,{'status':'INDEPENDENTLY_QUALIFIED_FOR_SERVICE_MICROOPT','identity':i,'logical_cell_id':logical,'authority_commit':rg.MICROOPT_AUTHORITY,'qualified_release':{'path':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}})
  return i,logical,{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 def bind(self):
  self.register();i,l,p=self.candidate()
  with patch('acceptance.load_current_authority',return_value={}),patch('acceptance.authorize_launch') as auth:cell=self.registry.register_service_microopt_cell(i,l,p);auth.assert_called_once()
  return i,l,p,cell
 def experiment(self,c):return {'experiment_id':rg.PARALLEL,'cell_id':c['cell_id'],'profile':c['mode'],'regime':c['condition'],'deadline_unix':self.campaign['deadline_unix']}
 def test_registration_is_idempotent_without_reset_or_resource_change(self):
  before=self.snapshot();s=self.register();self.assertEqual(len(s['logical_cells']),18);self.assertEqual(s['baseline_total_starts'],28);self.assertEqual(s,self.register());after=self.snapshot()
  for k in ['hosts','runs','resource_leases']:self.assertEqual(before[k],after[k])
  for k,v in self.campaign.items():self.assertEqual(after['campaigns'][rg.PARALLEL][k],v)
 def test_wrong_authority_expiry_and_budget_rebinding_fail(self):
  with self.assertRaises(ValueError):self.registry.register_service_microopt_stage('f'*40)
  self.register()
  with self.registry.locked() as d:d['campaigns'][rg.PARALLEL]['incremental_stages'][rg.MICROOPT_STAGE]['maximum_new_starts']=25
  with self.assertRaises(ValueError):self.register()
  with patch('registry.time.time',return_value=self.campaign['deadline_unix']),self.assertRaises(ValueError):self.register()
 def test_no_producer_or_current_qualification_no_cell(self):
  self.register();i,l,p=self.candidate()
  with patch('acceptance.load_current_authority',side_effect=ValueError('No new current candidate')),self.assertRaises(ValueError):self.registry.register_service_microopt_cell(i,l,p)
  self.assertEqual(self.snapshot()['campaigns'][rg.PARALLEL]['incremental_stages'][rg.MICROOPT_STAGE]['registered_cells'],[])
 def test_bind_exact_new_key_and_refuse_changed_proof(self):
  i,l,p,c=self.bind();d=self.snapshot();self.assertEqual(c['expected_run_key'],rg.run_key(i));self.assertEqual(len(d['runs']),1)
  rg.Registry.check_experiment(d,self.experiment(c),i,'lane5')
  wrong=copy.deepcopy(i);wrong['binary_sha256']='e'*64
  with self.assertRaisesRegex(ValueError,'identity'):rg.Registry.check_experiment(d,self.experiment(c),wrong,'lane5')
  Path(p['path']).write_text('{"changed":true}')
  with self.assertRaises(ValueError):self.registry.register_service_microopt_cell(i,l,p)
 def test_24_limit_includes_failed_reserved_and_retries(self):
  i,l,p,c=self.bind();d=self.snapshot();e=self.experiment(c)
  d['runs']['stage']={'experiment_id':rg.PARALLEL,'cell_id':c['cell_id'],'status':'FAILED','attempt_history':[{}]*23}
  with self.assertRaisesRegex(ValueError,'microopt24'):rg.Registry.check_experiment(d,e,i,'lane5',retry_key='stage')
  d['runs']['stage']['status']='RESERVED'
  with self.assertRaisesRegex(ValueError,'microopt24'):rg.Registry.check_experiment(d,e,i,'lane5',retry_key='stage')
 def test_72_global_and_original_deadline_still_enforced(self):
  i,l,p,c=self.bind();d=self.snapshot();e=self.experiment(c);d['runs']['other']={'experiment_id':rg.PARALLEL,'cell_id':'old-other','status':'FAILED','attempt_history':[{}]*43}
  with self.assertRaisesRegex(ValueError,'campaign.*cap'):rg.Registry.check_experiment(d,e,i,'lane5')
  d['runs'].pop('other')
  with patch('registry.time.time',return_value=e['deadline_unix']),self.assertRaisesRegex(ValueError,'deadline'):rg.Registry.check_experiment(d,e,i,'lane5')
 def test_necessary_new_binary_off_canary_also_spends_stage24(self):
  i,l,p,c=self.bind();d=self.snapshot();e=self.experiment(c)
  d['runs']['canary']={'experiment_id':rg.PARALLEL,'cell_id':'E_NATIVE_OFF_SERVICE_F0AF_R1','status':'COMPLETE_VALID'}
  d['runs']['stage']={'experiment_id':rg.PARALLEL,'cell_id':c['cell_id'],'status':'FAILED','attempt_history':[{}]*22}
  with self.assertRaisesRegex(ValueError,'microopt24'):rg.Registry.check_experiment(d,e,i,'lane5',retry_key='stage')
 def test_logical_plan_is_not_launch_authorization(self):
  self.register();d=self.snapshot();i,l,p=self.candidate();e={'experiment_id':rg.PARALLEL,'cell_id':l,'profile':'B16_OFF','regime':'SERVICE_MQ2','deadline_unix':self.campaign['deadline_unix']}
  with self.assertRaisesRegex(ValueError,'unknown'):rg.Registry.check_experiment(d,e,i,'lane5')
if __name__=='__main__':unittest.main()
