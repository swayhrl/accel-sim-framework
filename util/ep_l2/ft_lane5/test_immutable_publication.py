"""Atomic immutable V2 pointer compatibility; synthetic authority only."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
import acceptance
from test_lane5 import identity,acceptance_fixture

class ImmutablePublicationTests(unittest.TestCase):
 def test_pointer_snapshot_survives_canonical_staging(self):
  with tempfile.TemporaryDirectory() as t:
   repo=Path(t);p=repo/acceptance.MANIFEST;p.parent.mkdir(parents=True)
   state=acceptance_fixture(identity());manifest=state['manifest'];ev=repo/'docs/ep_l2/review_packs/fixture/evidence.json';ev.parent.mkdir(parents=True);ev.write_bytes(b'{"synthetic_validator_fixture_only":true}')
   snap=repo/'docs/ep_l2/review_packs/immutable/SCIENTIFIC_ACCEPTANCE_V2.json';snap.parent.mkdir(parents=True);raw=json.dumps(manifest).encode();snap.write_bytes(raw)
   pointer={'path':str(p),'snapshot_path':str(snap),'sha256':acceptance.sha(raw),'generation':1,'revision':'TEST_FIXTURE_ONLY'};client=repo/'CLIENT.json';client.write_text(json.dumps({'scientific_acceptance':pointer}));p.write_text('{"staged_next_manifest_not_current":true}')
   self.assertEqual(acceptance.load_current_authority(client)['manifest'],manifest)
   snap.write_text('{}')
   with self.assertRaisesRegex(ValueError,'bytes changed|schema'):acceptance.load_current_authority(client)
 def test_legacy_live_client_refuses_but_verified_new_client_allows(self):
  registry=Mock();registry.snapshot.return_value={'runs':{'key':{'status':'RUNNING'}}}
  with patch.object(Path,'read_text',return_value='{}'):
   with self.assertRaisesRegex(ValueError,'Legacy'):acceptance.require_publication_boundary(registry)
  b={'acceptance_module_sha256':'a'*64,'acceptance_source_commit':'b'*40,'immutable_scientific_pointer':True};registry.snapshot.return_value['runs']['key']['client_binding']=b
  client={'immutable_acceptance_clients':[{k:b[k] for k in ['acceptance_module_sha256','acceptance_source_commit']}]}
  with patch.object(Path,'read_text',return_value=json.dumps(client)):acceptance.require_publication_boundary(registry)
  b['acceptance_module_sha256']='f'*64
  with patch.object(Path,'read_text',return_value=json.dumps(client)):
   with self.assertRaisesRegex(ValueError,'Legacy'):acceptance.require_publication_boundary(registry)
 def test_loader_cannot_claim_unpublished_bytes(self):
  with patch.object(Path,'read_text',return_value=json.dumps({'acceptance_module_sha256':'f'*64,'acceptance_source_commit':'b'*40})):
   with self.assertRaisesRegex(ValueError,'published client'):acceptance.immutable_loader_binding()

if __name__=='__main__':unittest.main()
