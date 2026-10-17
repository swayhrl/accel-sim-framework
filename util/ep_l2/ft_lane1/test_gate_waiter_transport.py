"""Unavailable Git transport must grant no cached pilot authority."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import gate_waiter


class DependencyTransport(unittest.TestCase):
    def test_fetch_timeout_never_reads_cached_authorization(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / 'cached_approval.json').write_text('{"status":"APPROVED_ENGINEERING_ONLY"}')
            status = {}
            with mock.patch.object(gate_waiter.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['git', 'fetch'], 45)), mock.patch.object(gate_waiter.pilot, 'git') as read_ref:
                self.assertIsNone(gate_waiter.authorization_from_lane5({'pilot_id': 'p'}, cache, status))
            read_ref.assert_not_called()
            self.assertEqual(status['lane5_dependency']['status'], 'FETCH_UNAVAILABLE_NO_AUTHORIZATION')
            self.assertEqual(len(list(cache.iterdir())), 1)

    def test_fetch_failure_writes_no_authorization(self):
        with tempfile.TemporaryDirectory() as directory:
            status = {}
            with mock.patch.object(gate_waiter.subprocess, 'run', side_effect=subprocess.CalledProcessError(128, ['git', 'fetch'])), mock.patch.object(gate_waiter.pilot, 'git') as read_ref:
                self.assertIsNone(gate_waiter.authorization_from_lane5({'pilot_id': 'p'}, Path(directory), status))
            read_ref.assert_not_called()
            self.assertEqual(list(Path(directory).iterdir()), [])
            self.assertIn('128', status['lane5_dependency']['error'])

    def test_fresh_malformed_authorization_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(gate_waiter.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), mock.patch.object(gate_waiter.pilot, 'git', side_effect=[b'a' * 40, b'{']):
                with self.assertRaises(json.JSONDecodeError):
                    gate_waiter.authorization_from_lane5({'pilot_id': 'p'}, Path(directory), {})
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
