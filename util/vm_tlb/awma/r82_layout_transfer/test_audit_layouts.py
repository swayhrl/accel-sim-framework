#!/usr/bin/env python3
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_layouts import classify,conversions,ptx_native_by_loc

class AuditTests(unittest.TestCase):
    def test_conversion_and_nested_loc(self):
        text='''#blocked = #ttg.blocked<{warpsPerCTA=[2]}>\n#loc7 = loc("/x/kernel.py":9:3)\n#loc8 = loc("v"(#loc7))\nmodule {\n %b = ttg.convert_layout %a : tensor<8xf32, #blocked> -> tensor<8xf32, #blocked> loc(#loc8)\n}\n'''
        c=conversions(text);self.assertEqual(len(c),1);self.assertEqual(c[0]['source_loc'],('/x/kernel.py',9,3))
    def test_ptx_and_class(self):
        p='''.file 1 "/x/kernel.py"\n.loc 1 9 3\nst.shared::cta.b32 [%r1], %r2;\nbar.sync 0;\n'''
        n=ptx_native_by_loc(p)[('/x/kernel.py',9)]
        self.assertEqual(n['shared_store'],1);self.assertEqual(n['barrier'],1);self.assertEqual(classify(n),'INTER_WARP_SHARED')
    def test_shuffle_class(self):
        self.assertEqual(classify({'shuffle':2}),'INTRA_WARP_SHUFFLE')
        self.assertEqual(classify({}),'OTHER_UNKNOWN')

if __name__=='__main__':unittest.main()
