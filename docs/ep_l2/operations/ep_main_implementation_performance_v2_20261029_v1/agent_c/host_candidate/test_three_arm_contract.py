import copy,json,pathlib,unittest
import three_arm_contract as c
ROOT=pathlib.Path(__file__).resolve().parent
class ContractControls(unittest.TestCase):
 def setUp(self):
  self.parent=c.parent();self.specs=[]
  sid=dict(self.parent['source_identity']);sid.update(core_source_commit='1'*40,binary_sha256='2'*64,archive_sha256='3'*64)
  for mode,(t,fix)in c.MODES.items():
   s=copy.deepcopy(self.parent);s.update(mode=mode,M=True,T=t=='1',ordinary_ro_tag_relief=fix=='1',source_identity=sid,old_application_acceptance_inherited=False,science_request_id='MOCK_ONLY_NO_REAL_AUTHORITY_T3',cohort='MOCK_'+mode)
   s['expected_effective_options'][c.T]=t;s['expected_effective_options'][c.CORRECTION]=fix;self.specs.append(s)
  self.s=self.specs[2]
  self.source=dict(status='MAIN_REVIEWED_EXACT_NEW_SOURCE_AND_MODES_CPU_ONLY',approved_by='EP-MAIN',source_identity=sid,geometry=self.s['geometry'],modes_qualified=sorted(c.MODES),application_acceptance_inherited=False,source_keep=True,full_effective_option_keys=sorted(self.s['expected_effective_options']))
  r=json.loads(pathlib.Path(self.parent['ro_qualification_ref']['path']).read_text())
  self.ro=dict(r,status='MAIN_REVIEWED_EXACT_NEW_SOURCE_RO_LOADER_INPUT_BINDING',approved_by='EP-MAIN',source_identity=sid,epoch='whole_commandlist',line_bytes=128,address_domain='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS')
  self.cpu=dict(status='MAIN_REVIEWED_NEW_SOURCE_16X8_THREE_ARM_PRODUCTION_CPU_PASS',approved_by='EP-MAIN',source_identity=sid,geometry=self.s['geometry'],modes=sorted(c.MODES),old_source78_cpu_inherited=False,application_permission=False,passed_controls=['legacy_default_off','M1T0','legacy_M1T1','corrected_M1T1','sector_late_fill_generation','resources_negative','repeated_preview_and_drain'])
 def reject(self,fn):
  with self.assertRaises(ValueError):fn()
 def test_valid_mock3(self):
  for s in self.specs:self.assertFalse(c.preflight(s,self.source,self.ro,self.cpu)['launch_permission'])
  self.assertFalse(c.validate_triplet(self.specs)['launch_permission'])
 def test_geometry32_not_inherited(self):
  self.s['geometry']['sets']=32;self.reject(lambda:c.validate_background(self.s))
 def test_mode_unknown(self):
  self.s['mode']='F';self.reject(lambda:c.validate_background(self.s))
 def test_M0_rejected(self):
  self.s['M']=False;self.reject(lambda:c.validate_background(self.s))
 def test_T_wrong(self):
  self.s['T']=False;self.reject(lambda:c.validate_background(self.s))
 def test_correction_wrong(self):
  self.s['ordinary_ro_tag_relief']=False;self.reject(lambda:c.validate_background(self.s))
 def test_282_missing_switch(self):
  self.s['expected_effective_options'].pop(c.CORRECTION);self.reject(lambda:c.validate_background(self.s))
 def test_unexpected_option(self):
  self.s['expected_effective_options']['-fake']='1';self.reject(lambda:c.validate_background(self.s))
 def test_hardware_mutations(self):
  for key in ['-dram_latency','-gpgpu_clock_domains','-gpgpu_ep_l2_wad_entries','-gpgpu_ep_l2_bank_ops','-gpgpu_cache:dl2','-gpgpu_ep_l2_descriptor_pool_size']:
   s=copy.deepcopy(self.s);s['expected_effective_options'][key]='CHANGED';self.reject(lambda:c.validate_background(s))
 def test_observer_ON(self):
  self.s['observer_env']['EP_L2_EVENT_TIMELINE']='1';self.reject(lambda:c.validate_background(self.s))
 def test_summary_stage_supported(self):
  self.assertEqual(c.validate_background(self.s)['option_count'],283)
 def test_trace_identity(self):
  self.s['trace_entry']='/tmp/another_input';self.reject(lambda:c.validate_background(self.s))
 def test_old_ELF(self):
  self.s['source_identity']=self.parent['source_identity'];self.reject(lambda:c.validate_source(self.s,self.source))
 def test_source_not_frozen(self):
  self.s['source_identity']['binary_sha256']='NOT_FROZEN';self.reject(lambda:c.validate_source(self.s,self.source))
 def test_old_RO_seal(self):
  self.ro['source_identity']=self.parent['source_identity'];self.reject(lambda:c.validate_ro(self.s,self.ro))
 def test_RO_input(self):
  self.ro['input_identity_sha256']='0'*64;self.reject(lambda:c.validate_ro(self.s,self.ro))
 def test_RO_scope(self):
  self.ro['epoch']='kernel';self.reject(lambda:c.validate_ro(self.s,self.ro))
 def test_RO_manifest_binding(self):
  self.s['expected_effective_options']['-gpgpu_ep_l2_ro_manifest_sha256']='0'*64;self.reject(lambda:c.validate_ro(self.s,self.ro))
 def test_old_CPU_inherited(self):
  self.cpu['old_source78_cpu_inherited']=True;self.reject(lambda:c.validate_cpu_scope(self.s,self.cpu))
 def test_CPU_missing_negative(self):
  self.cpu['passed_controls'].remove('resources_negative');self.reject(lambda:c.validate_cpu_scope(self.s,self.cpu))
 def test_CPU_application_permission(self):
  self.cpu['application_permission']=True;self.reject(lambda:c.validate_cpu_scope(self.s,self.cpu))
 def test_triplet_cross_ELF(self):
  self.specs[0]['source_identity']=dict(self.specs[0]['source_identity'],binary_sha256='4'*64);self.reject(lambda:c.validate_triplet(self.specs))
 def test_triplet_missing_arm(self):self.reject(lambda:c.validate_triplet(self.specs[:2]))
 def test_triplet_duplicate_arm(self):self.reject(lambda:c.validate_triplet([self.specs[0]]*3))
 def test_no_real_authority(self):self.reject(lambda:c.validate_fresh_authority(self.s,{}))
 def test_old_budget(self):
  self.s['science_request_id']=c.OLD_REQUEST;self.reject(lambda:c.validate_fresh_authority(self.s,{}))
 def test_mock_fresh_and_spent(self):
  req=dict(science_request_id=self.s['science_request_id'],approved_by='USER_EXACT_START_AUTHORIZATION',source_identity=self.s['source_identity'],automatic_retry=False,budget=1,remaining=1,admitted_specs={self.s['cohort']:c.digest(self.s)},consumed={})
  self.assertFalse(c.validate_fresh_authority(self.s,req)['launch_permission']);req['consumed'][self.s['cohort']]={};req['remaining']=0;self.reject(lambda:c.validate_fresh_authority(self.s,req))
 def test_mock_spec_digest_drift(self):
  req=dict(science_request_id=self.s['science_request_id'],approved_by='USER_EXACT_START_AUTHORIZATION',source_identity=self.s['source_identity'],automatic_retry=False,budget=1,remaining=1,admitted_specs={self.s['cohort']:'0'*64},consumed={});self.reject(lambda:c.validate_fresh_authority(self.s,req))
if __name__=='__main__':unittest.main(verbosity=2)
