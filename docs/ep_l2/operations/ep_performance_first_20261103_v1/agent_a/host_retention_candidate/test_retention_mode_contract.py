import copy,json,unittest
import retention_mode_contract as m
class ContractTests(unittest.TestCase):
 def setUp(self): self.s=m.build_candidate('fastWalshTransform_CLEAN_ONLY')
 def reject(self,fn):
  s=copy.deepcopy(self.s);fn(s)
  with self.assertRaises(ValueError):m.check_candidate(s,candidate_enabled=True)
 def test_all_four_exact_candidates(self):
  for key in m.pins():
   with self.subTest(key=key):
    r=m.check_candidate(m.build_candidate(key),candidate_enabled=True)
    self.assertFalse(r['scientific_acceptance_granted']);self.assertFalse(r['launch_permission']);self.assertFalse(r['native_qualified']);self.assertNotEqual(r['numeric_profile'],'F_MINUS_R');self.assertTrue(r['TVD_summary_required'])
 def test_default_disabled(self):
  with self.assertRaises(ValueError):m.check_candidate(self.s)
 def test_source_drift(self): self.reject(lambda s:s['source_identity'].update(core_source_commit='0'*40))
 def test_input_drift(self): self.reject(lambda s:s.update(input_identity_sha256='0'*64))
 def test_mode_fallback(self): self.reject(lambda s:s.update(mode='WV_ZERO_RO'))
 def test_program_alias(self): self.reject(lambda s:s.update(program='FWT'))
 def test_RO_authority(self): self.reject(lambda s:s.update(ro_qualification_ref={'path':'old_RO.json'}))
 def test_M_enabled(self): self.reject(lambda s:s.update(M=True))
 def test_T_enabled(self): self.reject(lambda s:s.update(T=True))
 def test_M_integer_not_bool(self): self.reject(lambda s:s.update(M=0))
 def test_numeric_WV_fallback(self): self.reject(lambda s:s.update(numeric_profile='F_MINUS_R'))
 def test_geometry(self): self.reject(lambda s:s['geometry'].update(sets=16))
 def test_observer(self): self.reject(lambda s:s['observer_env'].update(EPL2_LIFE_WIRE='OFF'))
 def test_bank_capacity(self): self.reject(lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_bank_ops':'2'}))
 def test_WAD(self): self.reject(lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_wad_entries':'256'}))
 def test_bothclasses(self): self.reject(lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_tvd_dirty':'1'}))
 def test_wrong_ft(self): self.reject(lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_ft_mode':'1'}))
 def test_options_typed(self): self.reject(lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_tvd_clean':1}))
 def test_options_extra(self): self.reject(lambda s:s['expected_effective_options'].update({'-not_real':'0'}))
 def test_wrong_S_reference(self): self.reject(lambda s:s.update(matched_S_anchor_qualification_ref=None))
 def test_pack_mutation(self): self.reject(lambda s:s['option_pack_ref'].update(sha256='0'*64))
 def test_extra_authority(self): self.reject(lambda s:s.update(launch_permission=True))
 def test_input_trace(self): self.reject(lambda s:s['expected_effective_options'].update({'-trace':'different/kernelslist.g'}))
if __name__=='__main__':unittest.main(verbosity=2)
