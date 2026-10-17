import unittest
from native_legacy_trace_proof import native_fields
class NativeLegacy(unittest.TestCase):
    def row(self,mask,op='LDG.E.SYS',n=32):return '0 0 0 0 0190 '+mask+' 1 R21 '+op+' 1 R4 4 0 '+' '.join(hex(4096+4*x) for x in range(n))
    def test_zero_mask_retains_full32_and_classifies_no_addresses(self):self.assertEqual(native_fields(self.row('00000000'),0,0)[1:],(0,'LDG.E.SYS',True))
    def test_active_compact_addresses_are_not_extension(self):self.assertEqual(native_fields(self.row('00000003',n=2),0,0)[1:],(3,'LDG.E.SYS',False))
    def test_partial_mask_full32_is_not_silently_cleared(self):
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_TRACE_FORMAT'):native_fields(self.row('00000003'),0,0)
    def test_dependent_imm_control_not_classified_as_safe_memory(self):
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_TRACE_FORMAT'):native_fields(self.row('00000000','DEPBAR'),0,0)
if __name__=='__main__':unittest.main()
