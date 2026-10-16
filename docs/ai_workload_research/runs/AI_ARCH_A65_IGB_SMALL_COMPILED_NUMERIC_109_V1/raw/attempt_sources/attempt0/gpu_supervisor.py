"""A65 original nonblocking shared lease, one bounded child, owned-group cleanup."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import time
from paths import R, ROOT, W, CLEANUP, save, sha, allocated

LOCK = Path('/data/c16/locks/c16_gpu_campaign.lock')


def apps():
    text = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,used_memory',
                                    '--format=csv,noheader,nounits'], text=True, timeout=3)
    return [(int(s.split(',')[0]), int(s.split(',')[1])) for s in text.splitlines() if s.strip()]


def group_pids(pgid):
    result = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            row = (p / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(row[2]) == pgid and row[0] != 'Z':
                result.append(int(p.name))
        except (OSError, ValueError, IndexError):
            pass
    return result


def tree_rss(pids):
    total = 0
    for pid in pids:
        try:
            line = next(x for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('VmRSS:'))
            total += int(line.split()[1]) * 1024
        except (OSError, StopIteration):
            pass
    return total


def end_group(child):
    if child is None:
        return
    if group_pids(child.pid):
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        until = time.monotonic() + 2
        while group_pids(child.pid) and time.monotonic() < until:
            time.sleep(.05)
        if group_pids(child.pid):
            os.killpg(child.pid, signal.SIGKILL)
    child.wait(timeout=3)
    assert not group_pids(child.pid), 'OWN_PROCESS_GROUP_NOT_CLEAN'


def main():
    assert json.loads((CLEANUP / 'finished.json').read_text())['status'] == 'PASS_FIRST_BATCH_CLEANUP'
    for name in ['CPU_preflight.json', 'library_RECORD_pre.json', 'comparator_cpu_tests.json']:
        assert json.loads((R / name).read_text())['status'] == 'PASS'
    assert shutil.disk_usage(R).free >= 64 * 1024**3
    assert allocated() + 8 * 1024**2 < 112 * 1024**2
    prior_path = R / 'gpu_ledger.json'
    ledger = json.loads(prior_path.read_text()) if prior_path.exists() else {'cumulative_seconds': 0, 'attempts': []}
    prior = ledger['cumulative_seconds']
    assert prior < 160 and not (R / 'numeric_result.json').exists()
    selected = ['numeric.py', 'math_copy.py', 'paths.py', 'compare.py', 'gpu_supervisor.py']
    sources = {str((W / 'tools/aiarch_a65' / name).relative_to(W)): sha(W / 'tools/aiarch_a65' / name)
               for name in selected}
    guard = R / 'runtime/lib/python3.10/site-packages/sitecustomize.py'
    sources[str(guard)] = sha(guard)
    save('pre_GPU_script_identity.json', sources)
    save('pre_GPU_script_identity_attempt' + str(len(ledger['attempts'])) + '.json', sources)
    source_dir = R / 'attempt_sources' / ('attempt' + str(len(ledger['attempts'])))
    source_dir.mkdir(parents=True)
    for name in selected:
        shutil.copyfile(W / 'tools/aiarch_a65' / name, source_dir / name)
    shutil.copyfile(guard, source_dir / 'sitecustomize.py')
    fd = None
    started = None
    child = None
    reason = None
    samples = []
    code = None
    final_apps = None
    try:
        before = LOCK.lstat()
        assert stat.S_ISREG(before.st_mode) and not LOCK.is_symlink()
        fd = os.open(LOCK, os.O_RDWR | os.O_NOFOLLOW)
        assert os.fstat(fd).st_ino == before.st_ino
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            reason = 'GPU_LOCK_DEFERRED'
            return
        started = time.monotonic()
        deadline = started + 180 - prior
        assert not apps(), 'EXTERNAL_GPU_TASK_STOP'
        device = subprocess.check_output(['nvidia-smi', '--query-gpu=name,uuid,driver_version,memory.total,memory.free',
                                         '--format=csv,noheader,nounits'], text=True, timeout=3)
        old_device = json.loads((Path('/data/c16/aiarch_a61_igb_small_gnn_native_109_v1') / 'gpu_admission_metadata.json').read_text())['device']
        assert device.split(',')[2].strip() == old_device.split(',')[1].strip(), 'DRIVER_VERSION_IDENTITY_CHANGED'
        save('GPU_admission.json', {'device_csv': device, 'lock_path': str(LOCK),
                                    'lock_dev': before.st_dev, 'lock_inode': before.st_ino,
                                    'deadline_seconds': 180 - prior, 'nonblocking': True})
        env = os.environ.copy()
        env.update(A65_GPU_LOCK_HELD='1', A65_GPU_DEADLINE=str(deadline), CUDA_VISIBLE_DEVICES='0',
                   DGLBACKEND='pytorch', HOME=str(R / 'cache/home'), TMPDIR=str(R / 'tmp'),
                   XDG_CACHE_HOME=str(R / 'cache'), TORCH_HOME=str(R / 'cache/torch'),
                   TORCHINDUCTOR_CACHE_DIR=str(R / 'cache/inductor'), TRITON_CACHE_DIR=str(R / 'cache/triton'),
                   TORCH_EXTENSIONS_DIR=str(R / 'cache/extensions'), CUDA_CACHE_PATH=str(R / 'cache/driver'),
                   PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
                   LD_LIBRARY_PATH='/data/c16/env/cpython-3.10.12/lib', OMP_NUM_THREADS='1',
                   OMP_THREAD_LIMIT='4', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   NUMEXPR_NUM_THREADS='1', TORCHINDUCTOR_COMPILE_THREADS='1', MAX_JOBS='4')
        for key in ['PYTHONPATH', 'CUDA_HOME', 'CUDA_PATH']:
            env.pop(key, None)
        with (R / 'native_attempt0.log').open('w') as log:
            child = subprocess.Popen([str(R / 'runtime/bin/python'), str(W / 'tools/aiarch_a65/numeric.py')],
                                     env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            while child.poll() is None:
                current = apps()
                owned = group_pids(child.pid)
                if any(pid not in owned for pid, _ in current):
                    reason = 'EXTERNAL_GPU_TASK_STOP'
                controller = int(os.environ.get('A65_CONTROLLER_PID', str(os.getpid())))
                rss = tree_rss(sorted(set(owned + [os.getpid(), controller])))
                vram = sum(size for _, size in current)
                disk = allocated() + 8 * 1024**2
                free = shutil.disk_usage(R).free
                if rss > int(11.5 * 1024**3):
                    reason = 'BUDGET_STOP_RAM_EARLY_MARGIN'
                if vram > 11520:
                    reason = 'BUDGET_STOP_VRAM_EARLY_MARGIN'
                if disk > 112 * 1024**2:
                    reason = 'BUDGET_STOP_DISK_EARLY_MARGIN'
                if free < 64 * 1024**3:
                    reason = 'BUDGET_STOP_FREE_FS'
                if time.monotonic() > deadline - 12:
                    reason = 'BUDGET_STOP_GPU_TIME'
                if LOCK.stat().st_ino != before.st_ino:
                    reason = 'SHARED_LOCK_IDENTITY_CHANGED'
                phase = json.loads((R / 'current_phase.json').read_text()) if (R / 'current_phase.json').exists() else {}
                samples.append({'monotonic': time.monotonic(), 'phase': phase.get('phase'),
                                'tree_RSS_bytes': rss, 'GPU_MiB': vram,
                                'new_disk_conservative_bytes': disk, 'free_bytes': free})
                if reason:
                    break
                time.sleep(.2)
            end_group(child)
            code = child.returncode
            if code and reason is None:
                reason = 'RUNNER_EXIT_NONZERO_INSPECT_RAW'
    except BaseException as exc:
        reason = reason or repr(exc)
    finally:
        try:
            end_group(child)
            if started is not None:
                final_apps = apps()
                if child is not None and any(pid == child.pid for pid, _ in final_apps):
                    reason = reason or 'OWN_GPU_CONTEXT_STILL_REPORTED_AFTER_EXIT'
        finally:
            held = 0 if started is None else time.monotonic() - started
            if fd is not None:
                if started is not None:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
            receipt = {'status': 'COMPLETE' if reason is None else 'STOP', 'reason': reason,
                       'lock_seconds_this_attempt': held, 'child_returncode': code,
                       'owned_child_pid': None if child is None else child.pid,
                       'peak_sampled_tree_RSS_bytes': max((x['tree_RSS_bytes'] for x in samples), default=0),
                       'peak_sampled_GPU_MiB': max((x['GPU_MiB'] for x in samples), default=0),
                       'samples': samples, 'all_owned_processes_ended': child is None or not group_pids(child.pid),
                       'NVML_apps_after_owned_exit': final_apps,
                       'shared_lock_released': fd is not None and started is not None,
                       'peak_sampling_limit': 'sampled; transient peaks can be missed, early margins and allocator .70 retained',
                       'no_automatic_next_GPU_task': True}
            ledger['cumulative_seconds'] = prior + held
            ledger['attempts'].append(receipt)
            save('gpu_ledger.json', ledger)
            print('A65_GPU_TERMINAL', reason, ledger['cumulative_seconds'], flush=True)


if __name__ == '__main__':
    main()
