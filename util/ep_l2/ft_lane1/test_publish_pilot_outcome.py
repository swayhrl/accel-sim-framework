import copy
import unittest
import publish_pilot_outcome as publication
import engineering_pilot as pilot


class OutcomeTests(unittest.TestCase):
    def fixture(self):
        request = {'pilot_id': 'fixture', 'identity': {'source': 'exact'},
                   'planned_directed_commands': [{'name': str(i)} for i in range(21)]}
        state = {'status': 'PILOT_RUNNER_FINISHED_NO_AUTOMATIC_RETRY', 'invocations': 1}
        raw = {'classification': 'ENGINEERING_ONLY', 'pilot_id': 'fixture', 'identity': {'source': 'exact'},
               'runtime_ready': False, 'independent_qualification': False, 'formal_binary_sha256': None,
               'engineering_binary_sha256': 'a'*64, 'commands': [{'name': str(i), 'exit_code': 0} for i in range(21)],
               'status': 'COMPLETE_ENGINEERING_ONLY'}
        return request, state, raw

    def test_success_counts_actual_cases_and_never_promotes(self):
        request, state, raw = self.fixture(); out = publication.classify(request, state, raw)
        self.assertEqual(21, out['actual_directed_passes']); self.assertFalse(out['runtime_ready'])
        self.assertFalse(out['formal_promotion'])

    def test_missing_test_or_wrong_identity_refused(self):
        for scenario in ['test', 'source', 'promotion']:
            request, state, raw = self.fixture()
            if scenario == 'test': raw['commands'].pop()
            if scenario == 'source': raw['identity'] = {'source': 'other'}
            if scenario == 'promotion': raw['runtime_ready'] = True
            with self.subTest(scenario=scenario), self.assertRaises(pilot.Stop):
                publication.classify(request, state, raw)

    def test_preserves_current_formal_and_scientific_fields(self):
        request, state, raw = self.fixture(); out = publication.classify(request, state, raw)
        current = {'runtime_ready': True, 'binary_sha256': 'formal', 'independent_qualification': True,
                   'accepted_formal_pairs': 2, 'engineering_pilot': {}, 'artifacts': []}
        merged = publication.merge_receipt(current, request, state, out, 'new-pack')
        for name in ['runtime_ready', 'binary_sha256', 'independent_qualification', 'accepted_formal_pairs']:
            self.assertEqual(current[name], merged[name])
        self.assertEqual('a'*64, merged['engineering_pilot']['binary_sha256'])
        self.assertEqual({}, current['engineering_pilot'])

    def test_no_receipt_is_not_a_success_or_binary(self):
        request, state, raw = self.fixture(); out = publication.classify(request, state, None)
        self.assertIn('NOT_STARTED', out['status']); self.assertIsNone(out['engineering_binary_sha256'])

    def test_timeout_and_formal_event_do_not_claim_engineering_passes(self):
        request, state, raw = self.fixture()
        state['status'] = 'RESOURCE_WAIT_EXPIRED'
        self.assertEqual(0, publication.classify(request, state, None)['actual_directed_passes'])
        state['status'] = 'FORMAL_DRIVER_FINISHED_NO_AUTOMATIC_RETRY'
        out = publication.classify(request, state, {'binary_sha256': 'formal', 'status': 'producer-pass'})
        self.assertTrue(out['pilot_cancelled']); self.assertFalse(out['runtime_ready'])


if __name__ == '__main__':
    unittest.main()
