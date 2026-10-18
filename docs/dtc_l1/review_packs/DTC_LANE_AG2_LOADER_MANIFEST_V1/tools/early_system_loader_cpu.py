"""Only fixed AG2 C probe can be exec'd. No simulator/trace/dispatch interface.

Owned-child PTRACE_TRACEME and syscall stops provide complete early file maps,
including a cache mmap before any munmap can run. No foreign PID is accepted.
Linux x86-64 only. Never attach to an existing process.
"""
import ctypes
import json
import os
from pathlib import Path
import platform
import signal
import time
from mapping_roles import Sequence, freeze, require, sha

ROOT = Path('/workspace/dtc-lane-ag2-loader-manifest-174-v1')
BUILD = ROOT / 'build'
RAW = ROOT / 'raw' / 'final-cpu'
PROBE = BUILD / 'ag2-cpu-system-loader-probe'
LIBRARY = BUILD / 'libag2_cpu_fixture.so'
LIBC = Path('/usr/lib/x86_64-linux-gnu/libc.so.6')
LOADER = Path('/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2')
TOOLS = Path(__file__).resolve().parent

class Regs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in
                'r15 r14 r13 r12 rbp rbx r11 r10 r9 r8 rax rcx rdx rsi rdi orig_rax rip cs eflags rsp ss fs_base gs_base ds es fs gs'.split()]

def write_new(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')

def launch_gate(receipt):
    require(platform.machine() == 'x86_64', 'UNQUALIFIED_ARCHITECTURE')
    require(receipt['target'] == str(PROBE), 'ONLY_FIXED_CPU_PROBE_ALLOWED')
    require(receipt['library'] == str(LIBRARY), 'ONLY_FIXED_CPU_LIBRARY_ALLOWED')
    require(receipt['probe_sha256'] == sha(PROBE), 'CPU_PROBE_BUILD_BINDING_CHANGED')
    require(receipt['library_sha256'] == sha(LIBRARY), 'CPU_LIBRARY_BUILD_BINDING_CHANGED')
    for name, digest in receipt['sources'].items():
        require(name in ('cpu_probe.c', 'cpu_fixture_library.c'), 'UNKNOWN_CPU_BUILD_SOURCE')
        require(sha(TOOLS / name) == digest, 'CPU_BUILD_SOURCE_CHANGED')
    require(set(receipt['sources']) == {'cpu_probe.c', 'cpu_fixture_library.c'}, 'CPU_SOURCE_BINDING_MISSING')
    # PT_INTERP / DT_NEEDED were statically inspected by readelf, never loader --list.
    require(receipt['interpreter'] == '/lib64/ld-linux-x86-64.so.2', 'CPU_INTERPRETER_CHANGED')
    require(receipt['needed'] == ['libag2_cpu_fixture.so', 'libc.so.6'], 'CPU_DEPENDENCIES_CHANGED')

def main():
    require(not (RAW / 'CPU_TRACE_TERMINAL.json').exists(), 'CPU_TEST_ALREADY_TERMINAL_NO_OVERWRITE')
    receipt = json.loads((RAW / 'CPU_BUILD_RECEIPT.json').read_text())
    launch_gate(receipt)
    specs = [(str(PROBE), 'ELF_EXECUTABLE', 'AG2 fixed C CPU source / CPU_BUILD_RECEIPT'),
             (str(LOADER), 'ELF_INTERPRETER', 'CPU probe PT_INTERP canonical resolution'),
             (str(LIBC), 'ELF_SHARED_OBJECT', 'CPU probe DT_NEEDED libc.so.6 exact host path'),
             (str(LIBRARY), 'ELF_SHARED_OBJECT', 'CPU probe DT_NEEDED exact private fixture'),
             ('/etc/ld.so.cache', 'LOADER_DATA_CACHE', 'system loader input explicitly frozen before fork')]
    manifest = freeze(specs, PROBE, LOADER)
    manifest['tool_sha256'] = {p.name: sha(p) for p in [TOOLS / 'mapping_roles.py', Path(__file__).resolve()]}
    write_new(RAW / 'CPU_MAPPING_PREREGISTRATION.json', manifest)
    (RAW / 'CPU_MAPPING_PREREGISTRATION.json').chmod(0o444)
    sequence = Sequence(manifest)
    write_new(RAW / 'PRE_FORK.json', dict(monotonic_ns=time.monotonic_ns(),
              manifest_sha256=sha(RAW / 'CPU_MAPPING_PREREGISTRATION.json'),
              argv=[str(PROBE)], environment={'PATH':'/usr/bin:/bin', 'LANG':'C', 'LC_ALL':'C', 'LD_BIND_NOW':'1'},
              target_purpose='NO_GPU_TINY_C_PROBE', simulation_authority=False))
    libc = ctypes.CDLL(None, use_errno=True)
    libc.ptrace.restype = ctypes.c_long
    def trace(request, pid, data=0):
        ctypes.set_errno(0)
        result = libc.ptrace(request, pid, ctypes.c_void_p(0), data)
        if result == -1 and ctypes.get_errno():
            raise OSError(ctypes.get_errno(), 'owned CPU child ptrace request ' + str(request))
        return result
    output_fd = os.open(RAW / 'CPU_PROBE_STDOUT.txt', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    fork_ns = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        try:
            os.dup2(output_fd, 1)
            os.dup2(output_fd, 2)
            if libc.ptrace(0, 0, None, None) == -1:  # PTRACE_TRACEME, never attach
                os._exit(125)
            os.execve(str(PROBE), [str(PROBE)],
                      {'PATH':'/usr/bin:/bin', 'LANG':'C', 'LC_ALL':'C', 'LD_BIND_NOW':'1'})
        except BaseException:
            os._exit(126)
    os.close(output_fd)
    reaped = False
    started = time.monotonic()
    events = []
    error = None
    rc = None
    snapshots = RAW / 'snapshots'
    snapshots.mkdir(exist_ok=False)
    try:
        _, status = os.waitpid(pid, 0)
        require(os.WIFSTOPPED(status) and os.WSTOPSIG(status) == signal.SIGTRAP,
                'INITIAL_EXEC_STOP_MISSING')
        start_ticks = int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19])
        write_new(RAW / 'CPU_CHILD.json', dict(pid=pid, start_ticks=start_ticks, fork_monotonic_ns=fork_ns,
                  freeze_monotonic_ns=manifest['frozen_monotonic_ns'],
                  child_only_ptrace=True, argv=[str(PROBE)], executable=os.readlink(f'/proc/{pid}/exe')))
        require(fork_ns > manifest['frozen_monotonic_ns'], 'FREEZE_NOT_BEFORE_TARGET_START')
        trace(0x4200, pid, 0x1 | 0x100000)  # SETOPTIONS TRACESYSGOOD | EXITKILL
        def capture(stage, syscall=None, regs=None):
            text = Path(f'/proc/{pid}/maps').read_text()
            exe = os.readlink(f'/proc/{pid}/exe')
            validation = sequence.observe(text, exe)
            index = len(events)
            name = f'{index:04d}.maps'
            (snapshots / name).write_text(text)
            event = dict(index=index, monotonic_ns=time.monotonic_ns(), stage=stage,
                         syscall=syscall, maps=name, maps_sha256=sha(snapshots / name),
                         exe=exe, cache_present='/etc/ld.so.cache' in validation['files'],
                         validation=validation)
            if regs is not None:
                event['syscall_registers'] = dict(result=ctypes.c_longlong(regs.rax).value,
                      address=regs.rdi, length=regs.rsi, arg3=regs.rdx, arg4=regs.r10, arg5=regs.r8, arg6=regs.r9)
            events.append(event)
        capture('INITIAL_KERNEL_EXEC_STOP')
        entry = True
        while True:
            require(time.monotonic() - started < 30, 'CPU_PROBE_TIMEOUT_30S')
            require(len(events) < 2000, 'CPU_PROBE_SNAPSHOT_BOUND')
            trace(24, pid, 0)  # PTRACE_SYSCALL
            _, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                reaped = True
                rc = os.waitstatus_to_exitcode(status)
                break
            require(os.WIFSTOPPED(status) and os.WSTOPSIG(status) == signal.SIGTRAP | 0x80,
                    'UNEXPECTED_CPU_CHILD_STOP')
            regs = Regs()
            trace(12, pid, ctypes.byref(regs))  # PTRACE_GETREGS
            capture('SYSCALL_ENTRY' if entry else 'SYSCALL_EXIT', int(regs.orig_rax), regs)
            entry = not entry
        summary = sequence.close(rc == 0)
        require((RAW / 'CPU_PROBE_STDOUT.txt').read_text() == 'AG2_CPU_ONLY_SYSTEM_LOADER_PROBE_OK\n',
                'CPU_PROBE_OUTPUT_MISMATCH')
    except BaseException as exc:
        error = repr(exc)
        summary = dict(status='PARTIAL_OR_STOP_CPU_QUALIFICATION', reason=error)
    finally:
        if not reaped:
            # Only our unreaped fork child; EXITKILL also protects parent death.
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            reaped = True
        write_new(RAW / 'CPU_MAP_EVENTS.json', events)
        write_new(RAW / 'CPU_TRACE_TERMINAL.json', dict(**summary, returncode=rc,
                  exception=error, own_child_reaped=reaped, simulator_starts=0,
                  wall_seconds_nonperformance=time.monotonic()-started))
    print(json.dumps(summary))
    return 0 if error is None else 1

if __name__ == '__main__':
    raise SystemExit(main())
