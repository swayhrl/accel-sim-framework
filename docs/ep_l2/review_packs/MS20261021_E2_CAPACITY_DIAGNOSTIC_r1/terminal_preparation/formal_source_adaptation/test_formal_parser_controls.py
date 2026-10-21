"""Only synthetic negative engineering controls; no complete/native PASS."""
import ast,importlib.util,pathlib,tempfile,unittest
P=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('capacity_parser_draft',P/'parse_capacity_terminal.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class NegativeControls(unittest.TestCase):
 def raw(self,text):
  f=tempfile.NamedTemporaryFile(mode='w',prefix='synthetic_negative_',dir=P,delete=False);f.write(text);f.close();self.addCleanup(pathlib.Path(f.name).unlink);return pathlib.Path(f.name)
 def test_valid_replacement_negative_is_not_correctness_rejected(self):
  row=m.large_numbers(['slice=0','name=Tag','capacity=65536','highwater=100','capacity_denial_checks=0','valid_victim_replacements=1','near_nonbinding=0','coverage=CONSERVATIVE_RESIDENT_IDENTITY_BOUND'])
  self.assertFalse(m.validate_resource_predicate(row))
 def test_replacement_scope_enum_exact(self):
  row=m.large_numbers(['slice=0','timed_clean=0','timed_dirty=0','host_prefill_clean=1','scope=SUCCESSFUL_VALID_VICTIM_REPLACEMENTS'])
  self.assertEqual(m.validate_tag_replacement_record(row)['host_prefill_clean'],1)
  row['scope']='GLOBAL_OCCUPANCY_LOW'
  with self.assertRaises(ValueError):m.validate_tag_replacement_record(row)
 def test_replacement_cannot_keep_native_near_label(self):
  with self.assertRaises(ValueError):m.validate_resource_predicate(dict(name='Tag',capacity=65536,highwater=100,capacity_denial_checks=0,valid_victim_replacements=1,near_nonbinding=1))
 def test_no_duplicate_definitions(self):
  t=ast.parse((P/'parse_capacity_terminal.py').read_text());names=[x.name for x in t.body if isinstance(x,ast.FunctionDef)];self.assertEqual(len(names),len(set(names)))
 def test_duplicate_native_field_rejected(self):
  with self.assertRaises(ValueError):m.large_numbers(['slice=0','slice=0'])
 def test_signed_native_counter_rejected(self):
  with self.assertRaises(ValueError):m.large_numbers(['highwater=-1'])
 def test_missing_separator_rejected(self):
  with self.assertRaises(ValueError):m.large_numbers(['slice'])
 def test_clock_regression_rejected(self):
  with self.assertRaisesRegex(ValueError,'clock regressed'):m.decode(self.raw('gpu_tot_sim_cycle = 100\ngpu_tot_sim_cycle = 99\n'))
 def test_cutoff_rejected(self):
  with self.assertRaisesRegex(ValueError,'cutoff'):m.decode(self.raw('GPGPU-Sim: ** break due to reaching the maximum cycles (or instructions) **\n'))
 def test_process_text_is_not_complete(self):
  with self.assertRaisesRegex(ValueError,'complete counters'):m.decode(self.raw('GPGPU-Sim: *** exit detected ***\n'))
 def test_missing64slice_rejected(self):
  with self.assertRaisesRegex(ValueError,'exact64'):m.decode(self.raw('gpu_tot_sim_cycle = 100\ngpu_tot_sim_insn = 1000\nGPGPU-Sim: *** exit detected ***\n'))
 def test_conflicting_sameclock_rejected(self):
  with self.assertRaisesRegex(ValueError,'conflicting'):m.decode(self.raw('gpu_tot_sim_cycle = 1\nEPL2LARGEV1|CONFIG|slice=0|sets=1\nEPL2LARGEV1|CONFIG|slice=0|sets=2\n'))
 def test_wrong_wait_namespace_rejected(self):
  with self.assertRaisesRegex(ValueError,'namespace'):m.decode(self.raw('gpu_tot_sim_cycle = 1\nEPL2MSV1|WAIT|slice=0|reason=16\n'))
 def test_unsupported_resource_rejected(self):
  with self.assertRaisesRegex(ValueError,'unreviewed native capacity resource'):m.decode(self.raw('gpu_tot_sim_cycle = 1\nEPL2LARGEV1|RESOURCE|slice=0|name=UNKNOWN_NEW_RESOURCE\n'))
 def test_unsupported_ro_scope_rejected(self):
  with self.assertRaisesRegex(ValueError,'outside traditional-S'):m.decode(self.raw('gpu_tot_sim_cycle = 1\nEPL2ROV1|SUMMARY|slice=0\n'))
 def test_requested_master_mismatch_rejected(self):
  with self.assertRaisesRegex(ValueError,'whitelist'):m.validate_requested({'requested_options':{'-gpgpu_ep_l2_diag_l2_large_capacity':'0'}},{'profile_semantics':{'effective_options':{'-gpgpu_ep_l2_diag_l2_large_capacity':'1'}}})
 def test_off_fifo_without_source_constructor_evidence_rejected(self):
  with self.assertRaisesRegex(ValueError,'constructor evidence'):m.off_fifo_capacity('icnt_to_l2_queue',{'-gpgpu_dram_partition_queues':'32:32:32:32'},{'capacity_diagnostic':{}})
 def test_rop_unchanged_fields_are_numeric_not_resource_capacity(self):
  # This is field decoding only, never native correctness/acceptance PASS.
  d=m.large_numbers(['slice=0','ROP_storage=NATIVE_DYNAMIC','ROP_highwater=7','ROP_capacity_denial_checks=0','DRAM_ICNT_timing=UNCHANGED'])
  self.assertEqual(d['ROP_highwater'],7);self.assertEqual(d['ROP_storage'],'NATIVE_DYNAMIC');self.assertNotIn('ROP',m.RESOURCE_MAP)
 def test_off_fifo_malformed_config_rejected(self):
  with self.assertRaisesRegex(ValueError,'malformed'):m.off_fifo_capacity('icnt_to_l2_queue',{'-gpgpu_dram_partition_queues':'32:32:32'},{'capacity_diagnostic':{}})

if __name__=='__main__':unittest.main()
