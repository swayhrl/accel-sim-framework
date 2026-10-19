"""Actual dispatch-AST regression; PREPARED_NOT_TESTED until a receipt exists.

Declared synthetic PID/status/identity fixtures and recording syscall stubs.
No guard import, process creation, ptrace, signal or forced kernel PID reuse.
This cannot qualify a whole guard or replace real lifecycle/helper negatives.
"""
import ast
import ctypes
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import sys
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
CHILD, PARENT = 12345, 54321
STOP = (signal.SIGSTOP << 8) | 0x7f
FORK = (1 << 16) | (signal.SIGTRAP << 8) | 0x7f


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def execute(path, events, current_tick=2, cleanup=False):
    tree = ast.parse(path.read_text())
    engine = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == 'run_guarded')
    loops = [n for n in ast.walk(engine) if isinstance(n, ast.While)]
    normal = next(n for n in loops if ast.unparse(n.test) == 'alive')
    if cleanup:
        loop = next(n for n in loops if 'quarantined or' in ast.unparse(n.test))
        fragment = [next(n for n in loop.body if isinstance(n, ast.If) and
                         ast.unparse(n.test) == 'os.WIFSTOPPED(status)')]
    else:
        start = next(i for i, n in enumerate(normal.body)
                     if isinstance(n, ast.If) and
                     ast.unparse(n.test) == 'child not in owned')
        fragment = normal.body[start:]
    resume = next(n for n in ast.walk(engine)
                  if isinstance(n, ast.FunctionDef) and n.name == 'resume')
    calls = []
    ticks = {PARENT: 100, CHILD: current_tick}

    class FixtureOwnership:
        def __init__(self):
            self.confirmed = {PARENT: {'start_ticks': 100}, CHILD: {'start_ticks': 1}}
            self.pending = {}

        def same(self, pid):
            require(pid in self.confirmed and
                    self.confirmed[pid]['start_ticks'] == ticks[pid], 'OWN_PID_REUSED')
            return self.confirmed[pid]

        def quarantine(self, pid, reason):
            self.pending[pid] = {'start_ticks': ticks[pid], 'reason': reason}
            calls.append(('quarantine', pid))

        def confirm(self, parent, child, event):
            self.same(parent)
            require(event in (1, 2, 3) and child not in self.confirmed,
                    'DECLARED_PARENT_EVENT_FIXTURE_CONTRADICTION')
            self.confirmed[child] = {'start_ticks': ticks[child]}
            self.pending.pop(child, None)
            return {'proof': 'DECLARED_SYNTHETIC_PARENT_EVENT_NOT_KERNEL_PROOF'}

    owner = FixtureOwnership()

    def state():
        return {'exe': '/fixture/cpu', 'closed': True,
                'sequence': SimpleNamespace(ever={'fixture'}, cache_disappearances=1)}

    states = {PARENT: state(), CHILD: state()}

    def image(pid, exe=None):
        states[pid] = state()
        return states[pid]

    def ptr(request, pid, data=0):
        calls.append(('ptr', request, pid))
        if request == 0x4201:
            data._obj.value = CHILD

    namespace = dict(os=SimpleNamespace(
        WIFSTOPPED=os.WIFSTOPPED, WIFEXITED=os.WIFEXITED,
        WIFSIGNALED=os.WIFSIGNALED, WSTOPSIG=os.WSTOPSIG,
        waitstatus_to_exitcode=os.waitstatus_to_exitcode,
        readlink=lambda path: '/fixture/cpu'),
        signal=signal, ctypes=ctypes, require=require, ownership=owner,
        ptr=ptr, owned={PARENT, CHILD}, alive={PARENT, CHILD}, states=states,
        parents={CHILD: PARENT}, exits={}, pid=PARENT, main_rc=None,
        quarantined=[], events=events, json=json, now=lambda: 'CPU_AST_FIXTURE',
        eventlog=io.StringIO(), image=image, OPTIONS=0,
        capture=lambda pid, stage: calls.append(('capture', pid, stage)))
    wrapper = ast.For(
        target=ast.Tuple(elts=[ast.Name(id='child', ctx=ast.Store()),
                               ast.Name(id='status', ctx=ast.Store())], ctx=ast.Store()),
        iter=ast.Name(id='events', ctx=ast.Load()), body=fragment, orelse=[])
    # Cleanup's real loop obtains event before its stop/exit dispatch fragment.
    if cleanup:
        wrapper.body.insert(0, ast.Assign(
            targets=[ast.Name(id='event', ctx=ast.Store())],
            value=ast.BinOp(left=ast.Name(id='status', ctx=ast.Load()),
                           op=ast.RShift(), right=ast.Constant(value=16))))
    module = ast.fix_missing_locations(ast.Module(body=[resume, wrapper], type_ignores=[]))
    error = None
    try:
        exec(compile(module, str(path) + ':actual_dispatch_AST', 'exec'), namespace)
    except ValueError as exc:
        error = str(exc)
    return namespace, calls, error


class RetiredPIDDispatch(unittest.TestCase):
    def setUp(self):
        self.fixed = HERE / 'vendor/guarded_process.py'
        self.frozen = HERE / 'frozen_guarded_process.py.txt'
        self.assertEqual(hashlib.sha256(self.frozen.read_bytes()).hexdigest(),
                         '2d6ed8f846bb4a83530695d8b0eace4d5c548ec6aa5156d0c63ec7ebe699d3a0')

    def test_frozen_actual_dispatch_reproduces_unconfirmed_resume(self):
        ns, calls, error = execute(self.frozen, [(CHILD, 0), (CHILD, STOP)])
        self.assertIsNone(error)
        self.assertNotIn(CHILD, ns['ownership'].confirmed)
        self.assertIn(('ptr', 7, CHILD), calls)

    def test_repaired_retired_stop_waits_for_fresh_parent_proof(self):
        ns, calls, error = execute(self.fixed, [(CHILD, 0), (CHILD, STOP)])
        self.assertIsNone(error)
        self.assertNotIn(CHILD, ns['owned'])
        self.assertNotIn(CHILD, ns['states'])
        self.assertIn(CHILD, ns['ownership'].pending)
        self.assertNotIn(('ptr', 7, CHILD), calls)

    def test_repaired_current_membership_cannot_hide_changed_start_ticks(self):
        ns, calls, error = execute(self.fixed, [(CHILD, STOP)])
        self.assertEqual(error, 'OWN_PID_REUSED')
        self.assertNotIn(('ptr', 7, CHILD), calls)

    def test_repaired_fresh_parent_event_allows_new_instance_and_image(self):
        ns, calls, error = execute(self.fixed, [(CHILD, 0), (PARENT, FORK), (CHILD, STOP)])
        self.assertIsNone(error)
        self.assertEqual(ns['ownership'].confirmed[CHILD]['start_ticks'], 2)
        self.assertFalse(ns['ownership'].pending)
        self.assertIn(('capture', CHILD, 'INHERITED_FORK_CLONE_STOP'), calls)
        self.assertIn(('ptr', 7, CHILD), calls)

    def test_repaired_same_live_instance_still_resumes(self):
        ns, calls, error = execute(self.fixed, [(CHILD, STOP)], current_tick=1)
        self.assertIsNone(error)
        self.assertIn(('ptr', 7, CHILD), calls)

    def test_repaired_cleanup_retires_history_then_quarantines_reuse(self):
        ns, calls, error = execute(self.fixed, [(CHILD, 0), (CHILD, STOP)], cleanup=True)
        self.assertIsNone(error)
        self.assertNotIn(CHILD, ns['owned'])
        self.assertNotIn(CHILD, ns['states'])
        self.assertIn(CHILD, ns['ownership'].pending)
        self.assertNotIn(('ptr', 7, CHILD), calls)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RetiredPIDDispatch))
    print(json.dumps({'cases': result.testsRun, 'successful': result.wasSuccessful(),
                      'scope': 'ACTUAL_DISPATCH_AST_WITH_DECLARED_SYNTHETIC_STATUS_IDENTITY_STUBS',
                      'real_process_creation': 0, 'ptrace_or_signal_calls': 0,
                      'whole_guard_qualified': False, 'simulation_starts': 0}))
    sys.exit(0 if result.wasSuccessful() else 1)
