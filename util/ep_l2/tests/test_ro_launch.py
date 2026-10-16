import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

root=Path(__file__).parents[1]
sys.path.insert(0,str(root))
import ro_oracle
import verify_ro_launch


class LaunchTest(unittest.TestCase):
    def certificate(self,commands):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        p=Path(temp.name)
        (p/'kernel-1.traceg').write_text('-grid dim = (1,1,1)\n-block dim = (32,1,1)\n#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = 1\n0 0 0 0 0 1 0 LDG 0 4 0 1000\n#END_TB\n')
        (p/'kernelslist.g').write_text(commands)
        repo=root.parents[1]
        source=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
        ro_oracle.build(p/'kernelslist.g',p/'oracle',ro_oracle.SCOPE,source)
        return p,repo

    def test_initialization_before_epoch(self):
        p,repo=self.certificate('MemcpyHtoD,0x1000,128\nkernel-1.traceg\n')
        r=verify_ro_launch.verify(p/'oracle',repo)
        self.assertEqual(r['initialization_bytes'],128)
        self.assertEqual(r['eligible_unique_lines'],1)

    def test_host_writer_between_kernels_rejected(self):
        p,repo=self.certificate('kernel-1.traceg\nMemcpyHtoD,0x1000,128\nkernel-1.traceg\n')
        with self.assertRaises(ValueError):verify_ro_launch.verify(p/'oracle',repo)

    def test_changed_trace_rejected(self):
        p,repo=self.certificate('kernel-1.traceg\n')
        with (p/'kernel-1.traceg').open('a') as f:f.write('#corruption\n')
        with self.assertRaises(ValueError):verify_ro_launch.verify(p/'oracle',repo)


if __name__=='__main__':unittest.main()
