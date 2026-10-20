"""Bounded CPU-only protocol/policy qualification: DECLARED_SYNTHETIC.

This suite never forks, launches, signals, reads live resource counters, or
imports a live guard. UNIX datagram credentials are real self-sender credentials;
start ticks/image/input bindings and all resource samples are declared synthetic.
Passing cannot qualify actual postfork observation, stop/reap, production guard
wiring, source/model equivalence, or a full simulation's natural exit causality.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FROZEN_PATH = REPO / 'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/resources_v2.py'
FROZEN_SHA = 'f1844de51555384a48227affe48d70bea09c98dc787269e5b43c43ea735f94f9'
GIB = 1024 ** 3
NS = 10 ** 9
START = NS
PROVENANCE = 'DECLARED_SYNTHETIC'


def load_file(name, path, expected_sha=None):
    data = path.read_bytes()
    if expected_sha is not None and hashlib.sha256(data).hexdigest() != expected_sha:
        raise RuntimeError('FROZEN_RESOURCE_SOURCE_CHANGED')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Execute exactly the bytes checked above; avoid a preexisting pyc.
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


receiver_module = load_file('ag7_test_receiver', HERE / 'telemetry_receiver.py')
policy_module = load_file('ag7_test_runtime', HERE / 'runtime_policy_b.py')
resources = load_file('ag7_frozen_resources', FROZEN_PATH, FROZEN_SHA)


def sample(seconds=0, *, host_io=0, cg_io=0):
    def pressure(io):
        return {'memory': {'full': {'avg10': '0', 'total': '0'}},
                'io': {'full': {'avg10': str(io), 'total': str(seconds * 100)}}}
    return {'host': 'huangrulin-174', 'uid': 0,
            'monotonic_ns': START + seconds * NS,
            'host_MemAvailable_bytes': 64 * GIB,
            'disk_free_bytes': 20 * GIB, 'output_filesystem_device': 123,
            'host_oom_kill': 0, 'pswpin': 0, 'pswpout': 0,
            'pressure': pressure(host_io), 'cgroup_pressure_parsed': pressure(cg_io),
            'cgroup': {'memory.max': 128 * GIB, 'memory.current': 16 * GIB,
                       'memory.swap.current': 0, 'events': {'oom': 0, 'oom_kill': 0}}}


def binding(pid=None):
    return {'pid': os.getpid() if pid is None else pid, 'start_ticks': 12345,
            'generation': 'declared-synthetic-selfsender', 'input': 'a' * 64,
            'roi': 'b' * 64, 'proven_actual_root': True}


def record(seq=1, seconds=1, completed=0, phase='INIT', phase_epoch=1, end='NONE', **changes):
    value = {k: v for k, v in binding().items() if k != 'proven_actual_root'}
    value.update(v=1, seq=seq, mono_ns=START + seconds * NS, epoch=0,
                 phase_epoch=phase_epoch, phase=phase, stream_id=-1,
                 stream_scope='whole_input', completed=completed, end=end)
    value.update(changes)
    return value


def safety():
    return dict.fromkeys(policy_module.SAFETY_KEYS, True)


def impact():
    return {'known_scope': True, 'harm_detected': False,
            'conservative_host_episode_profile_accepted': True}


class IntegrationTests(unittest.TestCase):
    """Nine focused groups. Every numerical timeline is DECLARED_SYNTHETIC."""
    def channel(self, bound=None, opt_in=True):
        rx, tx = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.addCleanup(rx.close)
        self.addCleanup(tx.close)
        rx.setblocking(False)
        rx.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        return receiver_module.TelemetryReceiver(
            rx, binding() if bound is None else bound, started_ns=START, opt_in=opt_in), tx

    def send(self, rx, tx, value, now_seconds=None):
        raw = value if isinstance(value, bytes) else json.dumps(value).encode()
        tx.send(raw)
        now = value['mono_ns'] if now_seconds is None else START + now_seconds * NS
        return rx.drain(now)

    def policy(self):
        return policy_module.RuntimePolicyB(sample(), '/declared-synthetic-output',
            resource_module=resources, started_ns=START, opt_in=True)

    def observe(self, policy, seconds, *, current=None, progress=None, checks=None, io=None):
        if progress is None:
            progress = record(seconds=seconds, completed=seconds, phase='SIMULATE', phase_epoch=2)
        return policy.observe(sample(seconds) if current is None else current, 0, 0,
                              progress=progress,
                              safety_checks=safety() if checks is None else checks,
                              io_impact=impact() if io is None else io)

    def test_01_explicit_opt_in_and_bound_protocol(self):
        with self.assertRaisesRegex(ValueError, 'OPT_IN'):
            policy_module.RuntimePolicyB(sample(), '.', resource_module=resources, started_ns=START)
        with self.assertRaisesRegex(receiver_module.TelemetryError, 'OPT_IN'):
            self.channel(opt_in=False)
        for key in ('proven_actual_root', 'start_ticks', 'generation', 'input', 'roi'):
            with self.subTest(key=key):
                bound = binding()
                del bound[key]
                with self.assertRaises(receiver_module.TelemetryError):
                    self.channel(bound)

    def test_02_actual_unix_selfsender_credentials_and_progress(self):
        rx, tx = self.channel()
        first = self.send(rx, tx, record())
        self.assertEqual(first['latest']['pid'], os.getpid())
        second = self.send(rx, tx, record(2, 10, 40, 'SIMULATE', 2))
        self.assertEqual(second['latest_semantic']['completed'], 40)
        self.assertFalse(second['scientific_acceptance'])
        self.assertIsNone(second['terminal'])

    def test_03_declared_synthetic_parent_to_root_binding(self):
        # A different numeric PID is a synthetic admission-parent mismatch.
        # No fork is performed; kernel credentials are those of this process.
        rx, tx = self.channel(binding(os.getpid() + 1000000))
        with self.assertRaisesRegex(receiver_module.TelemetryError, 'NOT_PROVEN_ACTUAL_ROOT'):
            self.send(rx, tx, record())
        rx, tx = self.channel()
        self.assertEqual(self.send(rx, tx, record())['latest']['pid'], os.getpid())

    def test_04_invalid_stale_reverse_lost_and_scope_fail_closed(self):
        for case in ('malformed', 'stale', 'future', 'lost', 'duplicate', 'reverse_clock',
                     'counter_reset', 'root', 'ticks', 'generation', 'input', 'roi', 'epoch', 'phase_epoch'):
            with self.subTest(case=case):
                rx, tx = self.channel()
                self.send(rx, tx, record(completed=5))
                value = record(2, 10, 6, 'SIMULATE', 2)
                now = None
                if case == 'malformed':
                    value, now = b'{', 10
                elif case == 'stale':
                    now = 41
                elif case == 'future':
                    now = 9
                elif case == 'lost':
                    value['seq'] = 3
                elif case == 'duplicate':
                    value['seq'] = 1
                elif case == 'reverse_clock':
                    value['mono_ns'] = START + NS
                elif case == 'counter_reset':
                    value['completed'] = 4
                elif case == 'root':
                    value['pid'] += 1
                elif case == 'ticks':
                    value['start_ticks'] += 1
                elif case in ('generation', 'input', 'roi'):
                    value[case] = 'c' * 64
                elif case == 'epoch':
                    value['epoch'] = 1
                else:
                    value['phase_epoch'] = 3
                with self.assertRaises(receiver_module.TelemetryError):
                    self.send(rx, tx, value, now)
                with self.assertRaises(receiver_module.TelemetryError):
                    rx.drain(START + 42 * NS)
        rx, _tx = self.channel()
        with self.assertRaisesRegex(receiver_module.TelemetryError, 'MISSING_OR_STALE'):
            rx.drain(START + 31 * NS)

    def test_05_cgroup_warning_progress_and_bounded_episode(self):
        policy = self.policy()
        last = None
        # 181 deterministic observations, no sleep/real elapsed workload.
        for second in range(10, 1820, 10):
            last = self.observe(policy, second, current=sample(second, cg_io=90))
            if second < 1810:
                self.assertEqual(last['decision'], 'WARN')
                self.assertIn('RUNTIME_IO_WARNING_CGROUP_SHARED_SCOPE', last['warnings'])
            else:
                self.assertIn('MAXIMUM_CGROUP_HIGH_PSI_EPISODE_1800S', last['stop_reasons'])
        self.assertFalse(last['scientific_acceptance'])

    def test_06_original_host_three_qualified_samples_retained(self):
        policy = self.policy()
        for second in range(10, 80, 10):
            result = self.observe(policy, second, current=sample(second, host_io=90, cg_io=90))
            self.assertEqual(result['domains']['host']['io_PSI_samples'], 1 + (second - 10) // 30)
            if second < 70:
                self.assertNotEqual(result['decision'], 'STOP')
        self.assertEqual(result['decision'], 'STOP')
        self.assertIn('host:' + policy_module.OLD_CGROUP_IO_REASON, result['stop_reasons'])

    def test_07_no_retirement_nonrenewing_phase_and_freshness(self):
        policy = self.policy()
        for second in range(10, 610, 10):
            progress = record(seconds=second, completed=0,
                              phase='PARSE' if second % 20 else 'SIMULATE', phase_epoch=second // 10)
            result = self.observe(policy, second, progress=progress)
        self.assertIn('NO_SEMANTIC_RETIREMENT_600S', result['stop_reasons'])
        for case in ('missing', 'stale', 'reverse', 'gap', 'nonnatural'):
            with self.subTest(case=case):
                policy = self.policy()
                self.observe(policy, 10)
                if case == 'missing':
                    policy.observe(sample(20), 0, 0, progress=None, safety_checks=safety(), io_impact=impact())
                    result = policy.observe(sample(40), 0, 0, progress=None, safety_checks=safety(), io_impact=impact())
                elif case == 'stale':
                    self.observe(policy, 40)
                    result = self.observe(policy, 50, progress=record(seconds=10))
                elif case == 'reverse':
                    result = self.observe(policy, 20, progress=record(seconds=9))
                elif case == 'gap':
                    result = self.observe(policy, 41)
                else:
                    result = self.observe(policy, 20, progress=record(seconds=20, end='LIMIT', phase='BOUNDARY', phase_epoch=3))
                self.assertEqual(result['decision'], 'STOP')

    def test_08_hard_safety_memory_swap_disk_oom_authority_identity(self):
        for case in ('disk', 'device', 'host_memory', 'cg_memory', 'host_oom', 'cg_oom',
                     'scope', 'harm', 'unknown_safety', *policy_module.SAFETY_KEYS):
            with self.subTest(case=case):
                current, checks, io = sample(10), safety(), impact()
                if case == 'disk':
                    current['disk_free_bytes'] = 5 * GIB
                elif case == 'device':
                    current['output_filesystem_device'] += 1
                elif case == 'host_memory':
                    current['host_MemAvailable_bytes'] = 7 * GIB
                elif case == 'cg_memory':
                    current['cgroup']['memory.current'] = 122 * GIB
                elif case == 'host_oom':
                    current['host_oom_kill'] = 1
                elif case == 'cg_oom':
                    current['cgroup']['events']['oom'] = 1
                elif case == 'scope':
                    io['known_scope'] = False
                elif case == 'harm':
                    io['harm_detected'] = True
                elif case == 'unknown_safety':
                    del checks['authority']
                else:
                    checks[case] = False
                result = self.observe(self.policy(), 10, current=current, checks=checks, io=io)
                self.assertEqual(result['decision'], 'STOP')
                self.assertFalse(result['scientific_acceptance'])
        policy = self.policy()
        for second in (10, 20, 30):
            current = sample(second)
            current['cgroup']['memory.swap.current'] = 16 * 1024 ** 2
            result = self.observe(policy, second, current=current)
        self.assertEqual(result['decision'], 'STOP')
        self.assertIn('host:CGROUP_SWAP_GROWTH_GE16MiB_THREE_GE10S_SAMPLES', result['stop_reasons'])

    def test_09_terminal_candidate_never_overrides_late_conflict(self):
        rx, tx = self.channel()
        self.send(rx, tx, record())
        candidate = self.send(rx, tx, record(2, 10, 2, 'BOUNDARY', 2, 'NATURAL'))
        self.assertEqual(candidate['terminal'], 'NATURAL')
        self.assertFalse(candidate['scientific_acceptance'])
        with self.assertRaisesRegex(receiver_module.TelemetryError, 'LATE_RECORD'):
            self.send(rx, tx, record(3, 20, 2, 'BOUNDARY', 2, 'LIMIT'))
        policy = self.policy()
        candidate = self.observe(policy, 10, progress=record(seconds=10, completed=2, phase='BOUNDARY', phase_epoch=2, end='NATURAL'))
        self.assertFalse(candidate['scientific_acceptance'])
        checks = safety()
        checks['explicit_abort_clear'] = False
        result = self.observe(policy, 20, progress=record(seconds=20, completed=2, phase='BOUNDARY', phase_epoch=2, end='LIMIT'), checks=checks)
        self.assertEqual(result['decision'], 'STOP')
        self.assertIn('NONNATURAL_PRODUCER_RUN_END', result['stop_reasons'])
        self.assertEqual(self.observe(policy, 30)['decision'], 'STOP')
        complete = dict.fromkeys(policy_module.CLOSURE_KEYS, True)
        for case in ('actual_stop', 'limit', 'error', 'nonnatural_exit', 'negative_closure'):
            with self.subTest(late_conflict=case):
                join = policy_module.TerminalClosure()
                pending = join.observe(producer_end='NATURAL')
                self.assertEqual(pending['state'], 'PENDING_TERMINAL_CLOSURE')
                candidate = join.observe(run_ended=True, natural_exit_zero=True, closure=complete)
                self.assertEqual(candidate['state'], 'COMPLETE_CANDIDATE')
                self.assertFalse(candidate['scientific_acceptance'])
                self.assertFalse(candidate['performance_pass'])
                if case == 'actual_stop':
                    result = join.observe(actual_stop=True)
                elif case in ('limit', 'error'):
                    result = join.observe(producer_end=case.upper())
                elif case == 'nonnatural_exit':
                    result = join.observe(run_ended=True, natural_exit_zero=False)
                else:
                    result = join.observe(closure={'no_prior_stop': False})
                self.assertEqual(result['state'], 'STOP_UNACCEPTED')
                self.assertEqual(join.observe(producer_end='NATURAL', run_ended=True,
                    natural_exit_zero=True, closure=complete)['state'], 'STOP_UNACCEPTED')
        for case in ('missing_natural', 'missing_closure', 'exit_unproven'):
            with self.subTest(incomplete=case):
                join = policy_module.TerminalClosure()
                if case != 'missing_natural':
                    join.observe(producer_end='NATURAL')
                result = join.observe(run_ended=True,
                    natural_exit_zero=None if case == 'exit_unproven' else True,
                    closure=None if case == 'missing_closure' else complete)
                self.assertEqual(result['state'], 'STOP_UNACCEPTED')


if __name__ == '__main__':
    print('PROVENANCE=DECLARED_SYNTHETIC; actual UNIX selfsender credentials only; no fork/signal/production acceptance', flush=True)
    unittest.main(verbosity=2)
