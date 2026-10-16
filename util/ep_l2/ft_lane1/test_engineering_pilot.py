"""Meaningful runner safety tests. No real registry claims or C++ builds."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import Mock, patch

import engineering_pilot as pilot
import gate_waiter

G = pilot.GIB


def fixtures():
    envelope = {
        'workspace': dict(entry_free_bytes=26*G, hard_stop_free_bytes=12*G,
            max_pilot_allocated_growth_bytes=4*G, external_write_reserve_bytes=8*G,
            monitor_and_kill_overshoot_bytes=2*G, minimum_untouched_emergency_bytes=10*G),
        'results': dict(entry_free_bytes=43*G, hard_stop_free_bytes=int(40.5*G),
            max_pilot_allocated_growth_bytes=G//2, external_write_reserve_bytes=2*G,
            monitor_and_kill_overshoot_bytes=G//2, minimum_untouched_emergency_bytes=40*G)}
    request = {'pilot_id': 'fixture', 'host': pilot.socket.gethostname(), 'boot_id': pilot.boot_id(),
        'identity': {'core_source_commit': pilot.CORE, 'framework_source_commit': pilot.FRAMEWORK,
                     'vendor_commit': pilot.VENDOR}, 'max_wall_seconds': 3600,
        'proposed_envelope': envelope, 'filesystems': {
            'workspace': {'device': 1, 'fsid': 11}, 'results': {'device': 2, 'fsid': 22}},
        'max_single_file_bytes': G//4, 'max_logical_log_bytes': 128*1024**2}
    auth = {k: copy.deepcopy(request[k]) for k in ['pilot_id', 'host', 'boot_id', 'identity']}
    auth.update(status='AUTHORIZED_ENGINEERING_ONLY', request_sha256='fixture-sha',
        not_before_unix=time.time()-60, expires_at_unix=time.time()+600,
        cpu_units=2, memory_bytes=8*G, max_wall_seconds=3600,
        monitor_interval_seconds=0.05, formal_runtime_ready=False, filesystems=copy.deepcopy(envelope))
    sample = {'utc': pilot.utc(), 'filesystems': {
        'workspace': {'device': 1, 'fsid': 11, 'available_bytes': 28*G, 'pilot_allocated_bytes': 0},
        'results': {'device': 2, 'fsid': 22, 'available_bytes': 44*G, 'pilot_allocated_bytes': 0}},
        'available_memory_bytes': 100*G, 'owned_processes': [], 'owned_rss_bytes': 0,
        'owned_cpu_ticks': 0, 'external_processes': []}
    return request, auth, sample


class AuthorizationTests(unittest.TestCase):
    def test_under_formal_floor_but_valid_pilot_envelope(self):
        request, auth, sample = fixtures()
        pilot.validate_authorization(request, auth, 'fixture-sha')
        pilot.check_resources(request, auth, sample, sample, entry=True)
        self.assertLess(sample['filesystems']['workspace']['available_bytes'], 48*G)

    def test_expired_or_not_yet_valid(self):
        for name, value in [('expires_at_unix', time.time()-1), ('not_before_unix', time.time()+600)]:
            request, auth, sample = fixtures(); auth[name] = value
            with self.subTest(name=name), self.assertRaises(pilot.Stop):
                pilot.validate_authorization(request, auth, 'fixture-sha')

    def test_wrong_host_boot_source_driver_or_request_refused(self):
        for name in ['host', 'boot_id', 'identity', 'request_sha256']:
            request, auth, sample = fixtures(); auth[name] = 'incorrect'
            with self.subTest(name=name), self.assertRaises(pilot.Stop):
                pilot.validate_authorization(request, auth, 'fixture-sha')

    def test_forged_github_authorization_refused_before_adapter(self):
        request, auth, sample = fixtures(); auth['publication_path'] = 'fixture.json'
        with patch.object(pilot.subprocess, 'run'), patch.object(pilot, 'git', return_value=b'other bytes'):
            with self.assertRaisesRegex(pilot.Stop, 'FORGED_AUTHORIZATION'):
                pilot.load_adapter(request, auth, 'a'*40, 'b'*64)

    def test_cpu_memory_and_scientific_promotion_refused(self):
        for key, value in [('cpu_units', 3), ('memory_bytes', 16*G), ('formal_runtime_ready', True)]:
            request, auth, sample = fixtures(); auth[key] = value
            with self.subTest(key=key), self.assertRaises(pilot.Stop):
                pilot.validate_authorization(request, auth, 'fixture-sha')

    def test_zero_unknown_or_insufficient_numeric_budget_refused(self):
        for key, value in [('external_write_reserve_bytes', 0), ('entry_free_bytes', 20*G),
                           ('hard_stop_free_bytes', 10*G), ('max_pilot_allocated_growth_bytes', None)]:
            request, auth, sample = fixtures(); auth['filesystems']['workspace'][key] = value
            with self.subTest(key=key), self.assertRaises((pilot.Stop, TypeError)):
                pilot.validate_authorization(request, auth, 'fixture-sha')

    def test_real_formal_driver_and_registry_stay_at48_gib(self):
        fw = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r0-1')
        self.assertEqual(pilot.OFFICIAL_DRIVER_SHA, pilot.digest(fw/'util/ep_l2/ft_lane1/build_r0_1.py'))
        shared = json.loads((pilot.SHARED/'RUN_REGISTRY.json').read_text())
        self.assertEqual(48*G, shared['hosts'][shared['authority_host']]['min_disk_free_bytes'])

    def test_other_project_and_emergency_reserves_cannot_be_reduced(self):
        for key in ['external_write_reserve_bytes', 'monitor_and_kill_overshoot_bytes',
                    'minimum_untouched_emergency_bytes']:
            request, auth, sample = fixtures()
            auth['filesystems']['workspace'][key] -= 1
            with self.subTest(key=key), self.assertRaisesRegex(pilot.Stop, 'REQUESTED_RESERVE_REDUCED'):
                pilot.validate_authorization(request, auth, 'fixture-sha')

    def test_resource_breaches_stop(self):
        for change in ['disk', 'growth', 'external', 'mount', 'ram', 'rss', 'results']:
            request, auth, baseline = fixtures(); sample = copy.deepcopy(baseline)
            if change == 'disk': sample['filesystems']['workspace']['available_bytes'] = 12*G
            if change == 'growth': sample['filesystems']['workspace']['pilot_allocated_bytes'] = 4*G+1
            if change == 'external': sample['filesystems']['workspace']['available_bytes'] = 20*G-1
            if change == 'mount': sample['filesystems']['workspace']['fsid'] = 99
            if change == 'ram': sample['available_memory_bytes'] = 64*G-1
            if change == 'rss': sample['owned_rss_bytes'] = 8*G+1
            if change == 'results': sample['filesystems']['results']['available_bytes'] = 40*G
            with self.subTest(change=change), self.assertRaises(pilot.Stop):
                pilot.check_resources(request, auth, baseline, sample)


class ExecutionTests(unittest.TestCase):
    def tearDown(self):
        pilot.STOP_REQUESTED.clear()

    def test_no_authorization_no_compiler(self):
        request, auth, sample = fixtures()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'request.json'; path.write_text(json.dumps(request))
            module = types.SimpleNamespace(repair_commands=lambda *args: [None]*21)
            request['build_root'] = temp+'/build'; request['source_paths'] = {'core': temp+'/core'}
            path.write_text(json.dumps(request))
            with patch.object(pilot, 'audit_sources', return_value=module), \
                 patch.object(pilot, 'observation', return_value=sample), \
                 patch.object(pilot, 'load_adapter', side_effect=AssertionError('must not load adapter')), \
                 patch.object(pilot.subprocess, 'Popen', side_effect=AssertionError('must not launch')), \
                 patch.object(sys, 'argv', ['pilot', '--request', str(path), '--pilot-id', 'fixture']):
                with contextlib.redirect_stdout(io.StringIO()) as stream:
                    pilot.main()
                self.assertEqual('DRY_RUN_NO_LEASE_NO_COMPILER', json.loads(stream.getvalue())['status'])
                with patch.object(sys, 'argv', ['pilot', '--request', str(path), '--pilot-id', 'fixture', '--execute-once']):
                    with self.assertRaisesRegex(pilot.Stop, 'LANE5_AUTHORIZATION_REQUIRED'):
                        pilot.main()

    def test_backend_replay_and_conflict_denial_never_falls_back(self):
        for reason in ['TOKEN_REPLAY', 'ACTIVE_BUILD_CONFLICT', 'SCAN_EXCLUSIVE', 'CPU_QUOTA', 'MEMORY_QUOTA']:
            request, auth, sample = fixtures()
            with tempfile.TemporaryDirectory() as temp:
                request.update(build_root=temp+'/build', output_root=temp+'/out', cancellation_marker_path=temp+'/cancelled')
                adapter = Mock(); adapter.claim.side_effect = pilot.Stop(reason)
                with patch.object(pilot, 'observation', return_value=sample), \
                     patch.object(pilot.subprocess, 'Popen', side_effect=AssertionError('must not launch')):
                    with self.subTest(reason=reason), self.assertRaisesRegex(pilot.Stop, reason):
                        pilot.execute(request, 'fixture-sha', auth, adapter, None)
                self.assertFalse(Path(temp+'/build').exists())

    def test_failure_and_final_monitor_error_still_release(self):
        for final_monitor_failure in [False, True]:
            request, auth, sample = fixtures()
            with tempfile.TemporaryDirectory() as temp:
                request.update(build_root=temp+'/build', output_root=temp+'/out', cancellation_marker_path=temp+'/cancelled',
                               source_paths={'core': temp+'/core', 'framework': temp+'/fw'})
                adapter = Mock(); adapter.claim.return_value = {'lease_id': 'fixture-lease', 'pilot_id': 'fixture', 'owner': 'lane1'}
                module = types.SimpleNamespace(repair_commands=lambda *args: [])
                observations = [sample, sample, sample, OSError('monitor failed') if final_monitor_failure else sample]
                with patch.object(pilot, 'observation', side_effect=observations), \
                     patch.object(pilot, 'audit_sources'), \
                     patch.object(pilot, 'monitored_command', side_effect=pilot.Stop('fixture failure')):
                    result = pilot.execute(request, 'fixture-sha', auth, adapter, module)
                self.assertTrue(result['lease_released_token_consumed'])
                self.assertTrue(result['status'].startswith('PILOT_STOPPED_'))
                adapter.finish.assert_called_once()

    def test_formal_priority_cancels_before_claim(self):
        request, auth, sample = fixtures(); sample['filesystems']['workspace']['available_bytes'] = 50*G
        adapter = Mock()
        with patch.object(pilot, 'observation', return_value=sample):
            with self.assertRaisesRegex(pilot.Stop, 'FORMAL_ENTRY_AVAILABLE_CANCEL_PILOT'):
                pilot.execute(request, 'fixture-sha', auth, adapter, None)
        adapter.claim.assert_not_called()

    def test_stop_owned_group_preserves_unrelated_child(self):
        own = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=True)
        other = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=True)
        try:
            own._pilot_start_ticks = pilot.process_info(own.pid)['start_ticks']
            own._pilot_known_members = {own.pid: own._pilot_start_ticks}
            pilot.stop_owned_group(own); own.wait(timeout=3)
            self.assertIsNone(other.poll())
        finally:
            pilot.stop_owned_group(own); other.terminate(); other.wait(timeout=3)

    def test_monitored_stop_and_watchdog_kill_only_fixture(self):
        for stalled in [False, True]:
            request, auth, baseline = fixtures(); report = {'commands': []}; adapter = Mock()
            bad = copy.deepcopy(baseline)
            bad['filesystems']['workspace']['available_bytes'] = 11*G
            def sample(*args):
                if stalled: time.sleep(2.2)
                return baseline if stalled else bad
            sentinel = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=True)
            try:
                with tempfile.TemporaryDirectory() as temp, patch.object(pilot, 'observation', side_effect=sample):
                    with self.assertRaises(pilot.Stop):
                        pilot.monitored_command([sys.executable, '-c', 'import time;time.sleep(30)'], 'fixture',
                            request, auth, adapter, {'lease_id': 'fixture'}, baseline, time.monotonic(), report,
                            Path(temp), dict(os.environ))
                    record = report['commands'][0]
                    self.assertIn('log_sha256', record)
                    self.assertIsNotNone(record['exit_code'])
                    self.assertIsNone(sentinel.poll())
            finally:
                sentinel.terminate(); sentinel.wait(timeout=3)

    def test_child_launcher_limits_affinity_and_file_size(self):
        cpus = sorted(os.sched_getaffinity(0))[:2]
        command = [sys.executable, '-c',
            'import json,os,resource;print(json.dumps([len(os.sched_getaffinity(0)),resource.getrlimit(resource.RLIMIT_FSIZE)[0]]))']
        data = subprocess.check_output(pilot.child_launcher(command, cpus, G//4), text=True)
        self.assertEqual([2, G//4], json.loads(data))


class WaiterTests(unittest.TestCase):
    def test_formal50_not48_and_no_parallel_activity(self):
        state = {'workspace': {'available_bytes': 50*G}, 'available_memory_bytes': 100*G,
                 'policy': {'min_disk_free_bytes': 48*G, 'min_available_memory_bytes': 64*G},
                 'active_builds': {}, 'active_runs': {}}
        self.assertTrue(gate_waiter.formal_ready(state))
        state['workspace']['available_bytes'] = 48*G; self.assertFalse(gate_waiter.formal_ready(state))
        state['workspace']['available_bytes'] = 50*G; state['active_builds'] = {'pilot': {}}
        self.assertFalse(gate_waiter.formal_ready(state))


if __name__ == '__main__':
    unittest.main()
