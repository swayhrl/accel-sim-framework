"""Verify the actual runner index mapping, not a producer's logical filename."""
import hashlib,tempfile,unittest
from pathlib import Path
from review_r0_1_pair import verify_snapshot_assets

class Snapshot(unittest.TestCase):
 def test_named_service_overlay_maps_to_exact_executed_index(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);(d/'config-0.config').write_bytes(b'base');(d/'config-1.config').write_bytes(b'service');(d/'network.icnt').write_bytes(b'net')
   row=lambda name,value:{'name':name,'sha256':hashlib.sha256(value).hexdigest()}
   audit={'configs':[row('config-0.config',b'base'),row('service.config',b'service')],'auxiliary_assets':[row('network.icnt',b'net')]};verify_snapshot_assets(d,audit)
   (d/'service.config').write_bytes(b'service');(d/'config-1.config').write_bytes(b'corrupt')
   with self.assertRaises(ValueError):verify_snapshot_assets(d,audit)
   (d/'config-1.config').write_bytes(b'service');(d/'network.icnt').write_bytes(b'corrupt')
   with self.assertRaises(ValueError):verify_snapshot_assets(d,audit)

if __name__=='__main__':unittest.main()
