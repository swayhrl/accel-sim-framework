"""Positive finite overlay scope plus hostile accidental changes; no simulations."""
import unittest
from headroom_config import FINITE_OVERRIDES,PARALLEL_EXPERIMENT,PARALLEL_COORDINATION
from run import asset_manifest,content_hash
from test_headroom_config import HeadroomConfigTests

class FiniteTests(unittest.TestCase):
 save=HeadroomConfigTests.save
 check=HeadroomConfigTests.check
 def setUp(self):
  HeadroomConfigTests.setUp(self)
  self.spec.update(experiment_id=PARALLEL_EXPERIMENT,regime='ROP40_H0')
  self.overlay.write_text('-gpgpu_l2_rop_latency 40\n')
  self.reseal()
 def reseal(self):
  from headroom_config import options
  self.configs=asset_manifest(self.spec['configs'],ordered=True)
  sha=content_hash({'ordered_configs':self.configs,'auxiliary_assets':[],'environment':self.spec['environment']});self.spec['identity']['runtime_config_sha256']=sha
  self.manifest.update(experiment_id=PARALLEL_EXPERIMENT,coordination_commit=PARALLEL_COORDINATION,regime=self.spec['regime'])
  self.manifest['modes']['B16_BANKED'].update(ordered_configs=self.configs,runtime_config_sha256=sha,effective_options=options([v['path'] for v in self.spec['configs']]))
  self.save()
 def test_both_positive_conditions(self):
  self.assertEqual(self.check()['experiment_id'],PARALLEL_EXPERIMENT)
  self.spec['regime']='ICNT2_H0';self.overlay.write_text('-gpgpu_clock_domains 1132.0:2264.0:1132.0:850.0\n');self.reseal();self.assertEqual(self.check()['regime'],'ICNT2_H0')
 def test_hidden_change_even_resealed_refuses(self):
  self.overlay.write_text('-gpgpu_l2_rop_latency 40\n-gpgpu_ep_l2_wad_entries 256\n');self.reseal()
  with self.assertRaisesRegex(ValueError,'forbidden'):self.check()
 def test_wrong_campaign_cannot_relabel(self):
  self.spec['experiment_id']='EPL2_DOWNSTREAM_HEADROOM_R19'
  with self.assertRaises(ValueError):self.check()
 def test_unimplemented_finite_is_not_automatically_qualified(self):
  self.spec['regime']='WAD256_Q4';self.reseal()
  with self.assertRaises(ValueError):self.check()

if __name__=='__main__':unittest.main()
