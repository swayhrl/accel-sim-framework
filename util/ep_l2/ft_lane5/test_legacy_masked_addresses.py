"""Actual native legacy full-address rows with masked lanes; opcode scope only."""
import unittest
from atomic_trace_scope import instruction
class LegacyMasked(unittest.TestCase):
    def row(self,mask,opcode='LDG',count=32):
        return '0 0 0 0 0100 '+mask+' 1 R1 '+opcode+' 1 R2 4 0 '+' '.join(hex(4096+4*n) for n in range(count))
    def test_zero_mask_full32_is_still_parsed(self):
        op,kind,lanes=instruction(self.row('00000000'),0,0,(0,0,0),0,{'LDG':'OP_LDG'})
        self.assertEqual((op,kind,lanes),('LDG','OP_LDG',0))
    def test_partial_mask_full32_matches_native_ignored_tail(self):
        self.assertEqual(instruction(self.row('0000000f'),0,0,(0,0,0),0,{'LDG':'OP_LDG'})[2],4)
    def test_masked_atomic_remains_present_opcode(self):
        self.assertEqual(instruction(self.row('00000000','ATOM.ADD'),0,0,(0,0,0),0,{'ATOM':'OP_ATOM'})[1],'OP_ATOM')
    def test_truncated_active_addresses_refuse(self):
        with self.assertRaises(ValueError):instruction(self.row('ffffffff',count=4),0,0,(0,0,0),0,{'LDG':'OP_LDG'})
if __name__=='__main__':unittest.main()
