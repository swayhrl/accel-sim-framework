from copy import deepcopy
import unittest
from feature_schema import legacy_view, ro_bits, V2
from registry import run_key
from test_lane5 import identity
import test_lane5 as runner_tests
from run import inspect


class FeatureSchemaTests(unittest.TestCase):
    def test_r0_projection_preserves_exact_original_key_and_input(self):
        original = identity()
        before = deepcopy(original)
        view = legacy_view(original)
        self.assertEqual(view['original_run_key'], run_key(original))
        self.assertEqual(view['original_identity'], original)
        self.assertEqual(original, before)
        self.assertFalse(view['new_run_key_issued'])
        self.assertEqual(set(view['feature_vector_display']), V2)

    def test_legacy_enabled_ro_cannot_be_guessed(self):
        vector = identity()['feature_vector']
        vector['ro'] = True
        with self.assertRaisesRegex(ValueError, 'no certified'):
            ro_bits(vector)

    def test_four_explicit_ro_modes_have_distinct_identities(self):
        keys = set()
        for detach in (False, True):
            for bypass in (False, True):
                row = identity()
                del row['feature_vector']['ro']
                row['feature_vector'].update(ro_tag_detach=detach, ro_line_mshr_bypass=bypass)
                self.assertEqual(ro_bits(row['feature_vector']), (detach, bypass))
                keys.add(run_key(row))
        self.assertEqual(len(keys), 4)

    def test_missing_or_mixed_flags_fail_closed(self):
        vector = identity()['feature_vector']
        vector['ro_tag_detach'] = False
        with self.assertRaises(ValueError):
            ro_bits(vector)
        del vector['ro']
        with self.assertRaises(ValueError):
            ro_bits(vector)

    def test_non_boolean_flags_fail_closed(self):
        vector = identity()['feature_vector']
        del vector['ro']
        vector.update(ro_tag_detach=1, ro_line_mshr_bypass=False)
        with self.assertRaises(ValueError):
            ro_bits(vector)


class NewVectorQualificationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = runner_tests.RunnerInputTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.addCleanup(self.fixture.doCleanups)

    def test_v2_vector_needs_its_own_qualification(self):
        vector = self.fixture.spec['identity']['feature_vector']
        del vector['ro']
        vector.update(ro_tag_detach=False, ro_line_mshr_bypass=False)
        with self.assertRaisesRegex(ValueError, 'not independently qualified'):
            inspect(self.fixture.spec)

    def test_v2_explicit_qualified_off_projection_can_be_inspected(self):
        vector = self.fixture.spec['identity']['feature_vector']
        del vector['ro']
        vector.update(ro_tag_detach=False, ro_line_mshr_bypass=False)
        self.fixture.release['qualified_feature_vectors'] = [vector]
        self.fixture.write_release()
        self.assertEqual(inspect(self.fixture.spec)['run_key'], run_key(self.fixture.spec['identity']))


if __name__ == '__main__':
    unittest.main()
