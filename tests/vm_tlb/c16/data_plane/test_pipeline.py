import sys,tempfile,json,unittest
from pathlib import Path
sys.path.insert(0,'util/vm_tlb/c16/data_plane')
from pipeline import *
class T(unittest.TestCase):
 def test_all(self):
  ids={run_id('m','s','p','i','t') for _ in range(10000)};self.assertEqual(len(ids),10000)
  with tempfile.TemporaryDirectory() as x:
   root=Path(x);s=root/'staging';r=root/'ready';s.mkdir();r.mkdir();(s/'a').write_text('x')
   m={'schema_version':1,'run_id':next(iter(ids)),'scientific_status':'FORMAL','producer':{},'git':{},'model':{},'input':{},'scenario':{},'runtime':{},'capture':{},'artifacts':[]}
   d=finalize(s,r,m);self.assertTrue((d/'READY').exists());self.assertRaises(FileExistsError,finalize,d,r,m)
   a=root/'a.json';a.write_text(json.dumps({'verification_status':'PASS','source_manifest_sha256':'x','destination_raw_path':'raw/x'}));self.assertTrue(ack(a,'x','raw/x'))
if __name__=='__main__':unittest.main()
