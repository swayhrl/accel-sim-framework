"""Small temporary fixtures only; never reads a real C16 payload or policy."""
import hashlib
import importlib.util
import importlib.machinery
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader('proposed_guard', str(HERE/'c16_outbound_supply_guard.py.proposed'))
spec = importlib.util.spec_from_loader(loader.name, loader)
guard = importlib.util.module_from_spec(spec)
loader.exec_module(guard)

class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'policy.json'
        self.previous = guard.POLICY_PATH, guard.TRUSTED_POLICY_SHA256
        guard.POLICY_PATH = self.path
        self.policy = dict(schema='C16_G_OUTBOUND_SIX_RETIREMENT_V1', state='ACTIVE_RETIRED',
                           outbound_selector_sha256=guard.SELECTOR_SHA256, producer_commit=guard.PRODUCER,
                           outbound_paths=list(guard.OUTBOUND), local_model_six='ACTIVE_KEEP', source_unlink_authorized=False)
        for key in guard.REQUIRED_REFS:
            self.policy[key] = dict(commit='a'*40,path='fixture/receipt.json',receipt_sha256='b'*64)
        self.publish()
    def tearDown(self):
        guard.POLICY_PATH,guard.TRUSTED_POLICY_SHA256=self.previous
        self.tmp.cleanup()
    def publish(self):
        raw=json.dumps(self.policy).encode();self.path.write_bytes(raw)
        guard.TRUSTED_POLICY_SHA256=hashlib.sha256(raw).hexdigest()
    def test_all_six_outbound_paths_refused(self):
        for path in guard.OUTBOUND:
            with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([path])
    def test_parent_directory_transfer_cannot_bypass_six_file_guard(self):
        with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.BASE])
    def test_both_historical_package_identities_refused(self):
        for package,sha in guard.MANIFESTS.items():
            with self.assertRaises(guard.RetirementHold):guard.check_package({'package_id':package},guard.PRODUCER,sha)
    def test_direct_payload_old_package_refused(self):
        for deployment in guard.DEPLOYMENTS:
            with self.assertRaises(guard.RetirementHold):guard.check_payload({'destination_relpath':'models/'+deployment+'/fixture'},guard.PRODUCER)
    def test_outbound_path_refused_for_new_package(self):
        with self.assertRaises(guard.RetirementHold):guard.check_payload({'local_path':guard.OUTBOUND[0]},'c'*40)
    def test_original_local_models_remain_independently_available(self):
        guard.check_payload({'local_path':'/workspace/c16_assets/c16-a/metadata/retained/model.safetensors'},'c'*40)
    def test_other_deployment_ignores_missing_retirement_policy(self):
        self.path.unlink()
        guard.check_package({'package_id':'C16_GPU_PACKAGE_P0'},guard.PRODUCER,'0'*64)
        guard.check_payload({'destination_relpath':'models/llama/fixture'},guard.PRODUCER)
    def test_missing_policy_refuses_only_scoped_request(self):
        self.path.unlink()
        with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.OUTBOUND[0]])
    def test_changed_policy_digest_refuses(self):
        self.path.write_text('{}')
        with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.OUTBOUND[0]])
    def test_pending_or_unsigned_policy_cannot_activate(self):
        self.policy['state']='PENDING_APPROVAL';self.publish()
        with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.OUTBOUND[0]])
    def test_each_owner_or_drain_reference_required(self):
        for key in guard.REQUIRED_REFS:
            saved=self.policy[key];self.policy[key]=None;self.publish()
            with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.OUTBOUND[0]])
            self.policy[key]=saved
    def test_wrong_selector_cannot_activate(self):
        self.policy['outbound_selector_sha256']='c'*64;self.publish()
        with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.OUTBOUND[0]])
    def test_local_retirement_or_unlink_expansion_refused(self):
        for key,value in [('local_model_six','RETIRED'),('source_unlink_authorized',True)]:
            old=self.policy[key];self.policy[key]=value;self.publish()
            with self.assertRaises(guard.RetirementHold):guard.check_transfer_sources([guard.OUTBOUND[0]])
            self.policy[key]=old
    def test_path_normalization_does_not_open_payload(self):
        with patch.object(Path,'open',side_effect=AssertionError('unexpected payload open')):
            # Pure path predicate does not even open the policy.
            self.assertTrue(guard._old_path(guard.OUTBOUND[0].replace('/models/','/models/./')))
    def test_unapproved_proposal_does_not_activate(self):
        guard.TRUSTED_POLICY_SHA256=None
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected policy/payload read')):
            guard.check_transfer_sources([guard.OUTBOUND[0]])
    def test_new_versioned_non_outbound_package_unchanged(self):
        guard.check_package({'package_id':'C16_GPU_PACKAGE_P2'},'c'*40,'d'*64)
        guard.check_payload({'destination_relpath':'models/'+guard.DEPLOYMENTS[0]+'/fixture','local_path':'/approved/new/location'},'c'*40)

if __name__=='__main__':unittest.main(verbosity=2)
