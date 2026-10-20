"""One bounded native child collector; no admissions, queue or registry writer.

The controller remains foreground and owns the sole central controller lock.
The collector is the native child's real parent and persists waitpid status
before returning it. Parent death requests a guarded stop, never orphan replay.
"""
from contextlib import contextmanager
import ctypes
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import threading
import time

STOP = threading.Event()
STOP_SIGNAL = None


class ExitEvidenceMissing(RuntimeError):
    pass


def identity(pid):
    raw = Path(f'/proc/{pid}/stat').read_text()
    fields = raw[raw.rfind(')') + 2:].split()
    return dict(pid=pid, start_ticks=int(fields[19]),
                boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())


def durable_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + f'.{os.getpid()}.tmp')
    with temporary.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


@contextmanager
def controller_signals():
    global STOP_SIGNAL
    def stop(signum, frame):
        global STOP_SIGNAL
        STOP_SIGNAL = signum; STOP.set()
    old = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    try: yield
    finally:
        for s, handler in old.items(): signal.signal(s, handler)


def parent_death_signal(signum):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signum, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')


def resource_stop(request, native_pid, started):
    # Same physical guards as runner.execute; independently enforced if its
    # controller dies. These helpers do not admit work or mutate the registry.
    import coordinator as c
    import disk_policy
    import run as legacy
    bounds = request['bounds']; resources = c.local_resources(); usage = c.output_usage()
    if time.monotonic() - started >= bounds['timeout_seconds'] or time.time() >= c.INTAKE_DEADLINE:
        return dict(kind='TIMEOUT', reason='original bounded native timeout/intake freeze')
    disk = disk_policy.stop_detail(resources, bounds)
    if (disk or resources['share_disk_free_bytes'] < 40*c.GIB or
        resources['available_memory_bytes'] < 64*c.GIB or
        legacy.process_tree_rss(native_pid) > bounds['memory_bytes'] or
        c.retained_tree_bytes(Path(request['directory'])) >= bounds['maximum_result_bytes'] or
        usage['new_bytes'] >= 6*c.GIB or usage['total_bytes'] >= 20*c.GIB):
        return dict(kind='RESOURCE_LIMIT', reason='unchanged physical/RAM/output guard',
                    disk=disk, resources=resources, output_usage=usage)
    return None


def collect(request_path):
    request = json.loads(Path(request_path).read_text()); directory = Path(request['directory'])
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    received = []
    def interrupted(signum, frame): received.append(dict(signal=signum, at_unix=time.time()))
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, interrupted)
    parent_death_signal(signal.SIGTERM)
    owner = request['controller_process']
    if os.getppid() != owner['pid'] or identity(owner['pid']) != owner:
        raise RuntimeError('controller identity lost before native fork')
    guardian = identity(os.getpid()); started = time.monotonic(); raw_fd = request['raw_fd']
    child = os.fork()
    if child == 0:
        try:
            for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, signal.SIG_DFL)
            parent_death_signal(signal.SIGKILL)
            if os.getppid() != guardian['pid']: os._exit(125)
            os.setsid()
            os.dup2(raw_fd, 1); os.dup2(raw_fd, 2)
            # Same native PID/start identity across exec. Central accounting is
            # committed before SIGCONT allows any native application execution.
            os.kill(os.getpid(), signal.SIGSTOP)
            os.chdir(directory); os.execvpe(request['command'][0], request['command'], os.environ)
        except BaseException: os._exit(126)
    _, stopped = os.waitpid(child, os.WUNTRACED)
    if not os.WIFSTOPPED(stopped): raise RuntimeError('native startup gate did not stop')
    native = identity(child)
    ready = dict(schema='E2_NATIVE_DIRECT_PARENT_READY_V1', native_process=native,
                 guardian_process=guardian, controller_process=owner, native_ppid=os.getpid(),
                 command=request['command'], binding=request['binding'], at_unix=time.time())
    durable_json(directory/'NATIVE_EXECUTION_READY.json', ready)
    reason = None; stopping = None; released = False; status = None; rusage = None
    while True:
        done, status, rusage = os.wait4(child, os.WNOHANG)
        if done: break
        if not released and (directory/'NATIVE_EXECUTION_RELEASE.json').exists():
            release = json.loads((directory/'NATIVE_EXECUTION_RELEASE.json').read_text())
            if release['native_process'] != native or release['controller_process'] != owner:
                reason = dict(kind='SUPERVISION_INCOMPLETE', reason='startup release identity mismatch')
            else: os.kill(child, signal.SIGCONT); released = True
        if received and reason is None:
            reason = dict(kind='SUPERVISION_INCOMPLETE', reason='collector received termination or controller died', signals=received[:])
        if not released and time.monotonic()-started > 15 and reason is None:
            reason = dict(kind='SUPERVISION_INCOMPLETE', reason='central start release timeout')
        if reason is None: reason = resource_stop(request, child, started)
        if reason is not None:
            if stopping is None:
                assert identity(child) == native and os.getpgid(child) == child
                os.killpg(child, signal.SIGTERM); os.kill(child, signal.SIGCONT); stopping = time.monotonic()
            elif time.monotonic()-stopping >= request['bounds']['termination_grace_seconds']:
                assert identity(child) == native; os.killpg(child, signal.SIGKILL)
        time.sleep(request['bounds']['monitor_interval_seconds'])
    os.fsync(raw_fd)
    receipt = dict(schema='E2_NATIVE_WAITPID_DURABLE_EXIT_V1', native_process=native,
                   guardian_process=guardian, controller_process=owner, native_ppid=guardian['pid'],
                   wait_status=status, exit_code=os.waitstatus_to_exitcode(status),
                   exited_normally=os.WIFEXITED(status), signaled=os.WIFSIGNALED(status),
                   signal=os.WTERMSIG(status) if os.WIFSIGNALED(status) else None,
                   core_dumped=os.WCOREDUMP(status), binding=request['binding'],
                   command=request['command'], released_to_native=released,
                   stop_reason=reason, collector_signals=received, collected_unix=time.time(),
                   collection_method='direct-parent os.wait4; child reaped before durable receipt',
                   child_rusage=dict(user_seconds=rusage.ru_utime, system_seconds=rusage.ru_stime,
                                     maxrss_kib=rusage.ru_maxrss), scientific_acceptance='NOT_EVALUATED')
    durable_json(directory/'NATIVE_EXIT.json', receipt)


class NativeProcess:
    def __init__(self, command, cwd, stdout, env, bounds, binding):
        self.directory = Path(cwd); self.returncode = None; self.binding = binding
        self.owner = identity(os.getpid()); self.command = list(command)
        request = dict(directory=str(self.directory), command=self.command, raw_fd=stdout.fileno(),
                       controller_process=self.owner, bounds=bounds, binding=binding)
        self.request_path = self.directory/'NATIVE_EXECUTION_REQUEST.json'
        durable_json(self.request_path, request)
        with (self.directory/'EXECUTION_GUARDIAN.log').open('xb') as log:
            # This is a foreground child, never nohup/tmux/disowned. Parent
            # death is actively handled; the native retains its original PGID.
            self.collector = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), str(self.request_path)],
                cwd=self.directory, env=env, stdout=log, stderr=-2, pass_fds=(stdout.fileno(),), start_new_session=False)
        until = time.monotonic()+10
        while not (self.directory/'NATIVE_EXECUTION_READY.json').exists():
            if self.collector.poll() is not None: raise ExitEvidenceMissing('collector failed before ready; preserve start intent')
            if time.monotonic() >= until:
                self.collector.terminate(); self.collector.wait(timeout=5)
                raise ExitEvidenceMissing('bounded native readiness timeout')
            time.sleep(.01)
        self.ready = json.loads((self.directory/'NATIVE_EXECUTION_READY.json').read_text())
        assert self.ready['controller_process'] == self.owner and self.ready['binding'] == binding
        self.pid = self.ready['native_process']['pid']; self.guardian_identity = self.ready['guardian_process']
        assert identity(self.pid) == self.ready['native_process']

    def release(self):
        durable_json(self.directory/'NATIVE_EXECUTION_RELEASE.json', dict(native_process=self.ready['native_process'],
                     controller_process=self.owner, at_unix=time.time(), central_start_committed=True))

    def exit_evidence(self):
        path = self.directory/'NATIVE_EXIT.json'
        if not path.exists(): raise ExitEvidenceMissing('no durable direct-parent native exit receipt')
        value = json.loads(path.read_text())
        assert value['native_process'] == self.ready['native_process'] and value['binding'] == self.binding
        assert value['guardian_process'] == self.guardian_identity and value['controller_process'] == self.owner
        assert value['command'] == self.command
        assert value['exit_code'] == os.waitstatus_to_exitcode(value['wait_status'])
        return value

    def poll(self):
        if self.returncode is not None: return self.returncode
        if (self.directory/'NATIVE_EXIT.json').exists():
            self.collector.wait(timeout=5); self.returncode = self.exit_evidence()['exit_code']
            return self.returncode
        if self.collector.poll() is not None:
            raise ExitEvidenceMissing('collector exited without durable native wait status; never infer success')
        return None

    def wait(self, timeout=None):
        until = time.monotonic()+timeout if timeout is not None else float('inf')
        while self.poll() is None:
            if time.monotonic() >= until: raise subprocess.TimeoutExpired(self.command, timeout)
            time.sleep(.01)
        return self.returncode


def popen_factory(spec, attempt, audit):
    bounds = {k: attempt[k] for k in ('policy_id','disk_floor_bytes','monitor_reserve_bytes','maximum_result_bytes',
                                    'monitor_interval_seconds','termination_grace_seconds')}
    bounds.update(memory_bytes=spec.get('memory_bytes',8*2**30), timeout_seconds=spec['timeout_seconds'])
    binding = dict(attempt_id=attempt['attempt_id'], run_key=attempt['run_key'], identity=spec['identity'],
                   qualification_id=spec['qualification_id'], comparison_invariants_sha256=audit['comparison_invariants_sha256'])
    def spawn(command, cwd, stdout, stderr, env, start_new_session):
        assert stderr == -2 and start_new_session is True
        return NativeProcess(command,cwd,stdout,env,bounds,binding)
    return spawn


if __name__ == '__main__': collect(sys.argv[1])
