"""Supersession consumer tests; no simulator or production qualification is created."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from acceptance import (bind_manifest, sha, MANIFEST, authorize_launch,
                        require_current_result, load_current_authority)
from registry import run_key
import test_lane5 as fixtures

EVIDENCE = b'{"synthetic_validator_fixture_only":true}'


def rebind(manifest, evidence=EVIDENCE):
    raw = json.dumps(manifest).encode()
    return bind_manifest(raw, {'kind': 'LOCAL_CURRENT_POINTER', 'manifest_sha256': sha(raw),
        'generation': manifest['generation'], 'revision': manifest['revision']}, lambda name: evidence)


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.identity = fixtures.identity()
        self.state = fixtures.acceptance_fixture(self.identity)
        self.row = {**{k: self.identity[k] for k in ('core_source_commit', 'framework_source_commit',
            'binary_sha256', 'runtime_config_sha256', 'trace_content_sha256', 'workload')},
            'identity': deepcopy(self.identity), 'run_key': run_key(self.identity),
            'scientific_acceptance': 'CURRENT_ACCEPTED', 'original_terminal_status': 'COMPLETE_VALID',
            'raw_log_sha256': 'b' * 64, 'observed_cycles': 50, 'instructions': 100}
        self.state['manifest']['rows'] = [self.row]
        self.state = rebind(self.state['manifest'])

    def result(self, identity=None, state=None, raw=None, cycles=50, instructions=100):
        return require_current_result(identity or self.identity, raw or 'b' * 64,
                                      cycles, instructions, state or self.state)

    def test_complete_exact_current_result_accepted(self):
        self.assertEqual(self.result()['scientific_acceptance'], 'CURRENT_ACCEPTED')

    def test_withdrawal_overrides_accepted_row_and_old_qualified_certificate(self):
        m = deepcopy(self.state['manifest'])
        m['withdrawn_releases'] = [{**{k: self.identity[k] for k in
            ('core_source_commit', 'framework_source_commit', 'binary_sha256')}, 'reason': 'later production counterexample'}]
        state = rebind(m)
        with self.assertRaisesRegex(ValueError, 'withdrawn'):
            self.result(state=state)
        with self.assertRaisesRegex(ValueError, 'withdrawn'):
            authorize_launch(self.identity, 'a' * 64, state)

    def test_alias_or_different_input_cannot_rehabilitate_withdrawn_binary(self):
        m = deepcopy(self.state['manifest'])
        m['withdrawn_releases'] = [{**{k: self.identity[k] for k in
            ('core_source_commit', 'framework_source_commit', 'binary_sha256')}, 'reason': 'bad physical clock'}]
        identity = deepcopy(self.identity)
        identity.update(core_source_commit='f' * 40, framework_source_commit='e' * 40,
                        runtime_config_sha256='d' * 64, trace_content_sha256='c' * 64)
        with self.assertRaisesRegex(ValueError, 'withdrawn'):
            authorize_launch(identity, 'a' * 64, rebind(m))

    def test_terminal_complete_does_not_override_suspended_not_run_or_unknown(self):
        for status in ('SUSPENDED_MEMCPY_PHYSICAL_CLOCK', 'NOT_RUN', 'COMPLETE_VALID', ''):
            m = deepcopy(self.state['manifest']); m['rows'][0]['scientific_acceptance'] = status
            with self.subTest(status=status), self.assertRaises(ValueError):
                self.result(state=rebind(m))

    def test_every_identity_dimension_must_match_current_row(self):
        for name in self.identity:
            identity = deepcopy(self.identity)
            if name.endswith('_commit'): identity[name] = 'f' * 40
            elif name.endswith('_sha256'): identity[name] = 'e' * 64
            elif name == 'workload': identity[name] = 'other_input_size'
            else: identity[name]['extra'] = True
            with self.subTest(dimension=name), self.assertRaises(ValueError):
                self.result(identity=identity)

    def test_raw_and_observed_metrics_bound_exactly(self):
        for kwargs in ({'raw': 'c' * 64}, {'cycles': 51}, {'instructions': 101}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): self.result(**kwargs)

    def test_missing_row_fails_closed(self):
        m = deepcopy(self.state['manifest']); m['rows'] = []
        with self.assertRaisesRegex(ValueError, 'missing'): self.result(state=rebind(m))

    def test_launch_qualification_does_not_preaccept_future_result(self):
        state = fixtures.acceptance_fixture(self.identity)
        self.assertEqual(authorize_launch(self.identity, 'a' * 64, state)['status'],
                         'CURRENT_QUALIFIED_FOR_LAUNCH')
        with self.assertRaisesRegex(ValueError, 'missing'): self.result(state=state)

    def test_changed_certificate_or_vector_cannot_launch(self):
        with self.assertRaises(ValueError): authorize_launch(self.identity, 'c' * 64, self.state)
        identity = deepcopy(self.identity); identity['feature_vector']['unified_wb'] = True
        with self.assertRaises(ValueError): authorize_launch(identity, 'a' * 64, self.state)

    def test_unrelated_ledger_revision_keeps_stable_launch_audit(self):
        old = authorize_launch(self.identity, 'a' * 64, self.state)
        m = deepcopy(self.state['manifest']); m.update(generation=2, revision='new unrelated result')
        self.assertEqual(old, authorize_launch(self.identity, 'a' * 64, rebind(m)))

    def test_duplicate_identity_and_modified_evidence_rejected(self):
        m = deepcopy(self.state['manifest']); m['rows'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate'): rebind(m)
        with self.assertRaisesRegex(ValueError, 'evidence changed'):
            rebind(self.state['manifest'], b'changed')

    def test_mutation_after_binding_rejected(self):
        self.state['manifest']['rows'][0]['scientific_acceptance'] = 'SUSPENDED'
        with self.assertRaisesRegex(ValueError, 'mutated'): self.result()

    def test_stale_current_pointer_hash_or_generation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / MANIFEST; path.parent.mkdir(parents=True)
            path.write_text(json.dumps(self.state['manifest']))
            evidence_path = root / self.state['manifest']['supersession_evidence'][0]['path']
            evidence_path.parent.mkdir(parents=True); evidence_path.write_bytes(EVIDENCE)
            client = root / 'client.json'
            pointer = {'path': str(path), 'sha256': sha(path.read_bytes()),
                       'generation': 1, 'revision': 'TEST_FIXTURE_ONLY'}
            client.write_text(json.dumps({'scientific_acceptance': pointer}))
            self.assertEqual(load_current_authority(client)['manifest']['generation'], 1)
            for name, value in [('generation', 2), ('sha256', 'c' * 64)]:
                changed = {**pointer, name: value}
                client.write_text(json.dumps({'scientific_acceptance': changed}))
                with self.subTest(field=name), self.assertRaises(ValueError): load_current_authority(client)

    def test_all_six_retained_real_runs_rejected_with_historical_certificates(self):
        root = Path(__file__).resolve().parents[3]
        raw = (root / MANIFEST).read_bytes(); meta = json.loads(raw)
        state = bind_manifest(raw, {'kind': 'LOCAL_CURRENT_POINTER', 'manifest_sha256': sha(raw),
            'generation': meta['generation'], 'revision': meta['revision']}, lambda p: (root / p).read_bytes())
        prior = root / 'docs/ep_l2/review_packs/FT20261016_LANE5_MEMCPY_CLOCK_CORRECTION_r1/R0_INDEPENDENTLY_QUALIFIED.json.prior'
        self.assertEqual(json.loads(prior.read_text())['status'], 'INDEPENDENTLY_QUALIFIED')
        retained = [r for r in meta['rows'] if r['original_terminal_status'] == 'COMPLETE_VALID'
                    and r['binary_sha256'] == '0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698']
        self.assertEqual(len(retained), 6)
        for row in retained:
            with self.subTest(run_key=row['run_key']):
                with self.assertRaisesRegex(ValueError, 'withdrawn'):
                    require_current_result(row['identity'], row['raw_log_sha256'],
                        row['observed_cycles'], row['instructions'], state)
                with self.assertRaisesRegex(ValueError, 'withdrawn'):
                    authorize_launch(row['identity'], sha(prior.read_bytes()), state)


if __name__ == '__main__': unittest.main()
