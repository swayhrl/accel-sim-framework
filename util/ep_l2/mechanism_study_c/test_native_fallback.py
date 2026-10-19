"""Small input-binding/control tests, never native correctness or RO proof."""
import json
from pathlib import Path
import tempfile
import unittest
import native_fallback as n

class FallbackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.command = self.root / 'kernelslist.g'
        self.command.write_text('MemcpyHtoD,0x1000,128\nkernel-1.traceg\nMemcpyHtoD,0x1000,1\nkernel-2.traceg\n')
        for i in [1, 2]: (self.root / f'kernel-{i}.traceg').write_text('uncertified fixture bytes\n')
        self.out = self.root / 'fallback'
    def build(self): return n.build(self.command, self.out, 'unknown aliases; all lines native', 'a'*40)
    def test_empty_scope_full_binding_and_later_host_copy(self):
        m=self.build(); self.assertEqual(n.verify(self.out), m)
        self.assertEqual(m['kernel_count'], 2);self.assertEqual(m['scope'], n.SCOPE)
        self.assertEqual(m['counts']['CERTIFIED_RO_lines'], 0)
    def test_changed_body_is_not_reused(self):
        self.build();(self.root/'kernel-2.traceg').write_text('changed\n')
        with self.assertRaises(ValueError):n.verify(self.out)
    def test_nonempty_ranges_rejected_even_with_new_hash(self):
        m=self.build();(self.out/'certified_ranges.csv').write_text('first_line,last_line_inclusive\n0000000000001000,0000000000001000\n')
        m['artifacts']['certified_ranges.csv']=n.ro_oracle.sha256(self.out/'certified_ranges.csv')
        (self.out/'manifest.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError):n.verify(self.out)
    def test_partial_epoch_rejected(self):
        m=self.build();m['kernels']=m['kernels'][:1];m['kernel_count']=1;(self.out/'manifest.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError):n.verify(self.out)
    def test_no_overwrite_or_missing_input(self):
        self.build()
        with self.assertRaises(FileExistsError):self.build()
        (self.root/'kernel-2.traceg').unlink()
        with self.assertRaises(FileNotFoundError):n.build(self.command,self.root/'other','missing is not certified','a'*40)

if __name__=='__main__':unittest.main()
