"""Guard tests only; no Git fetch, build, simulator, lease or sleep."""
import hashlib
import tempfile
from pathlib import Path
import unittest
from release_event import bounds, inspect_release

CORE = 'c948184504d82b80e23eb3f4ff6cdfd328ba9355'
FRAMEWORK = '3ab150b3e99ff3ed759b8cdc5154cfb5744042a7'


class ReleaseGuard(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'producer.out'
        self.binary.write_bytes(b'not an executable, just an identity fixture')
        self.receipt = {'lane_id': 1, 'core_source_commit': CORE,
            'framework_source_commit': FRAMEWORK, 'runtime_ready': True,
            'binary_sha256': hashlib.sha256(self.binary.read_bytes()).hexdigest(),
            'binary': str(self.binary), 'status': 'PRODUCER_READY_NOT_INDEPENDENTLY_QUALIFIED'}
        self.authority = {'schema_version': 'EPL2_SCIENTIFIC_ACCEPTANCE_V2',
            'authority': {'lane_id': 5}, 'withdrawn_releases': []}

    def check_state(self, name):
        result = inspect_release(self.receipt, self.authority, CORE, FRAMEWORK, [self.root])
        self.assertEqual(result['state'], name)
        self.assertFalse(result['admission_granted'])
        self.assertFalse(result['independent_qualification'])
        self.assertFalse(result['compiler_or_simulator_started'])

    def test_unpublished_source_is_wait_not_pass(self):
        self.receipt.update(runtime_ready=False, binary_sha256=None)
        self.check_state('WAIT_OFFICIAL_BINARY')

    def test_event_is_never_resource_or_science_admission(self):
        self.check_state('RELEASE_CANDIDATE_VERIFIED')

    def test_engineering_marker_is_not_official_release(self):
        self.receipt['status'] = 'ENGINEERING_BUILD_EVIDENCE_ONLY'
        self.check_state('WAIT_OFFICIAL_BINARY')

    def test_engineering_flag_is_not_official_release(self):
        self.receipt['engineering_only'] = True
        self.check_state('WAIT_OFFICIAL_BINARY')

    def test_changed_core_requires_new_static_binding(self):
        self.receipt['core_source_commit'] = 'a' * 40
        self.check_state('SOURCE_REBIND_REQUIRED')

    def test_changed_framework_requires_new_binding(self):
        self.receipt['framework_source_commit'] = 'b' * 40
        self.check_state('SOURCE_REBIND_REQUIRED')

    def test_withdrawn_core_vetoes_ready_text(self):
        self.authority['withdrawn_releases'] = [{'core_source_commit': CORE}]
        self.check_state('WITHDRAWN_RELEASE_REFUSED')

    def test_withdrawn_binary_vetoes_new_source_text(self):
        self.authority['withdrawn_releases'] = [{'binary_sha256': self.receipt['binary_sha256']}]
        self.check_state('WITHDRAWN_RELEASE_REFUSED')

    def test_missing_current_authority_fails_closed(self):
        self.authority = {}
        self.check_state('ACCEPTANCE_AUTHORITY_REFUSED')

    def test_missing_local_binary_is_not_release(self):
        self.binary.unlink()
        self.check_state('BINARY_LOCAL_MISSING')

    def test_binary_bytes_must_match(self):
        self.binary.write_bytes(b'changed')
        self.check_state('BINARY_HASH_REFUSED')

    def test_do_not_guess_missing_published_path(self):
        self.receipt.pop('binary')
        self.check_state('BINARY_PATH_REQUIRED')

    def test_unrelated_namespace_is_never_read(self):
        self.receipt['binary'] = '/workspace/unrelated-protected-project/binary'
        self.check_state('BINARY_PATH_REFUSED')

    def test_failed_producer_is_not_event(self):
        self.receipt['status'] = 'FAILED_RETAIN_DIAGNOSTICS_NO_RUNTIME_RELEASE'
        self.check_state('PRODUCER_STATE_REFUSED')

    def test_poll_horizon_is_finite_and_slow(self):
        bounds(600, 1200)
        for interval, duration in [(1, 600), (600, 0), (600, 172801), (901, 1200)]:
            with self.assertRaises(ValueError):
                bounds(interval, duration)


if __name__ == '__main__':
    unittest.main()
