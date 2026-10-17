"""Result-FS failures must not reserve canonical identities or run simulators."""
import unittest
from unittest.mock import Mock, patch
import run


class ResultDiskGuard(unittest.TestCase):
    def test_low_share_refuses_before_hashing_or_reserving(self):
        registry = Mock()
        with patch.object(run, 'result_disk_free_bytes', return_value=39 * 1024**3), patch.object(run, 'inspect') as inspect:
            with self.assertRaisesRegex(ValueError, 'no claim'):run.run({}, registry)
            inspect.assert_not_called();registry.claim.assert_not_called();registry.update.assert_not_called()

    def test_share_drop_during_input_hashing_refuses_before_claim(self):
        registry = Mock()
        with patch.object(run, 'result_disk_free_bytes', side_effect=[41 * 1024**3,39 * 1024**3]), patch.object(run, 'inspect', return_value={'run_key':'a'*64}):
            with self.assertRaisesRegex(ValueError,'changed during input audit'):run.run({},registry)
            registry.claim.assert_not_called();registry.update.assert_not_called()


if __name__ == '__main__':unittest.main()
