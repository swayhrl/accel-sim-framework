#!/usr/bin/env python3
"""Bounded, lock-held GPU producer followed by CPU-only native trace closure."""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1')
DRIVER = WORKTREE / 'util/vm_tlb/awma/r101_transient_capture/capture_driver.py'
PYTHON = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python')
TRACER = ROOT / 'bin/route_b_r101_multi.so'
POST = Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/post-traces-processing_5143')
VALIDATOR = Path('/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b')
LOCK = Path('/data/c16/locks/c16_gpu_campaign.lock')
TERMINAL = re.compile(r'^ROUTEB_TERMINAL_COMPLETE kernel=(\d+) device_reported=(\d+) receiver_accepted=(\d+) raw_records=(\d+) drop_count=(\d+) overflow_count=(\d+) raw=(.*)$')


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def write(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def size_tree(directory: Path) -> int:
    return sum(path.stat().st_size for path in directory.rglob('*') if path.is_file())


def rss_bytes(pid: int) -> int:
    try:
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            if line.startswith('VmRSS:'):
                return int(line.split()[1]) * 1024
    except FileNotFoundError:
        pass
    return 0


def trace_headers(path: Path) -> dict:
    process = subprocess.Popen(['xz', '-dc', str(path)], stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True)
    assert process.stdout is not None
    header = {}
    try:
        for line in process.stdout:
            if not line.startswith('-'):
                break
            if ' = ' in line:
                key, value = line[1:].strip().split(' = ', 1)
                header[key] = value
    finally:
        process.stdout.close()
        process.wait()
    required = ('kernel name', 'kernel id', 'grid dim', 'block dim',
                'cuda stream id', 'binary version')
    assert all(key in header for key in required), (path, header)
    return header


def close(out: Path, expected: int, mode: str) -> None:
    raw = out / 'raw'
    stdout = (out / 'driver.stdout.log').read_text()
    assert 'R101_L512_NATIVE_INVOCATION_COMPLETE' in stdout
    run = json.loads((out / 'DRIVER_RUN_RECEIPT.json').read_text())
    assert run['output_exact'] and run['finite'] and run['five_complete_iterations']
    terminal_lines = [line for line in stdout.splitlines()
                      if line.startswith('ROUTEB_TERMINAL_COMPLETE')]
    selected = [line for line in stdout.splitlines()
                if line.startswith('ROUTEB_SELECTOR_CANDIDATE') and ' selected=1 ' in line]
    assert len(terminal_lines) == expected and len(selected) == expected
    terminals = []
    for line in terminal_lines:
        match = TERMINAL.match(line)
        assert match, line
        kernel, reported, accepted, records, drop, overflow, raw_path = match.groups()
        assert int(reported) == int(accepted) == int(records)
        assert int(drop) == 0 and int(overflow) == 0
        terminals.append({'kernel_id': int(kernel), 'device_reported': int(reported),
                          'raw_records': int(records), 'drop': 0, 'overflow': 0,
                          'raw_path': raw_path})
    members = (raw / 'kernelslist').read_text().splitlines()
    assert len(members) == expected and len(set(members)) == expected
    assert [int(re.search(r'kernel-(\d+)-', member).group(1)) for member in members] == [entry['kernel_id'] for entry in terminals]
    assert all((raw / member).is_file() for member in members)
    (out / 'lifecycle.log').write_text('\n'.join(line for line in stdout.splitlines()
        if line.startswith('ROUTEB_LIFECYCLE') or line.startswith('ROUTEB_TERMINAL_COMPLETE')) + '\n')
    with (out / 'postprocess.stdout.log').open('w') as output, (out / 'postprocess.stderr.log').open('w') as error:
        subprocess.run([str(POST), str(raw)], check=True, stdout=output, stderr=error,
                       timeout=7200)
    traceg_members = (raw / 'kernelslist.g').read_text().splitlines()
    assert len(traceg_members) == expected and len(set(traceg_members)) == expected
    assert all((raw / name).is_file() for name in traceg_members)
    prereg = []
    if mode == 'formal':
        with (ROOT / 'NATIVE_KERNEL_BINDING_PREREG.tsv').open(newline='') as stream:
            prereg = list(csv.DictReader(stream, delimiter='\t'))
        assert len(prereg) == expected
    def validate_member(index: int, raw_name: str, traceg_name: str) -> tuple[dict, dict]:
        raw_path, traceg_path = raw / raw_name, raw / traceg_name
        assert traceg_name == raw_name.replace('.trace.xz', '.traceg.xz')
        subprocess.run(['xz', '-t', str(raw_path)], check=True, timeout=1200)
        deadline = time.monotonic() + 1200
        while True:
            xz = subprocess.run(['xz', '-t', str(traceg_path)], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            if xz.returncode == 0:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError(f'traceg xz completion timeout {traceg_path}')
            time.sleep(2)
        grammar_stdout = out / f'grammar_{index:02d}.stdout.log'
        grammar_stderr = out / f'grammar_{index:02d}.stderr.log'
        with grammar_stdout.open('w') as output, grammar_stderr.open('w') as error:
            subprocess.run([str(VALIDATOR), str(traceg_path)], check=True,
                           stdout=output, stderr=error, timeout=1200)
        header = trace_headers(raw_path)
        binding = {'roi_launch_index': index, 'kernel_id': int(header['kernel id']),
                   'exact_function': header['kernel name'],
                   'grid': header['grid dim'].strip('()'),
                   'block': header['block dim'].strip('()'),
                   'stream_id': header['cuda stream id'],
                   'context_from_filename': re.search(r'ctx_(0x[0-9a-fA-F]+)', raw_name).group(1),
                   'binary_version': header['binary version']}
        if mode == 'formal':
            expected_row = prereg[index]
            assert binding['exact_function'] == expected_row['exact_function']
            assert binding['grid'] == expected_row['grid']
            assert binding['block'] == expected_row['block']
        row = {'roi_launch_index': index, 'raw_member': raw_name,
                     'raw_bytes': raw_path.stat().st_size, 'raw_sha256': sha(raw_path),
                     'traceg_member': traceg_name, 'traceg_bytes': traceg_path.stat().st_size,
                     'traceg_sha256': sha(traceg_path), 'grammar_status': 'PASS',
                     'raw_xz_status': 'PASS', 'traceg_xz_status': 'PASS'}
        return row, binding

    rows_by_index = {}
    bindings_by_index = {}
    with ThreadPoolExecutor(max_workers=min(4, expected)) as executor:
        futures = {
            executor.submit(validate_member, index, raw_name, traceg_name): index
            for index, (raw_name, traceg_name) in enumerate(zip(members, traceg_members))
        }
        for future in as_completed(futures):
            index = futures[future]
            row, binding = future.result()
            rows_by_index[index] = row
            bindings_by_index[index] = binding
            print(json.dumps({'validated_member': index + 1, 'expected': expected,
                              'traceg_bytes': row['traceg_bytes']}), flush=True)
    rows = [rows_by_index[index] for index in range(expected)]
    bindings = [bindings_by_index[index] for index in range(expected)]
    with (out / 'NATIVE_KERNEL_BINDING.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(bindings[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(bindings)
    with (out / 'TRACE_MEMBER_MANIFEST.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    write(out / 'TERMINAL_RECEIPT.json', {
        'status': 'COMPLETE', 'selected_kernels': expected,
        'terminal_receipts': terminals, 'drop_count': 0, 'overflow_count': 0,
        'all_kernelslist_members_exist': True, 'all_grammar_pass': True,
        'all_xz_pass': True, 'no_extra_selected_kernels': True})
    hashes1 = [sha(raw / item['traceg_member']) for item in rows]
    hashes2 = [sha(raw / item['traceg_member']) for item in rows]
    assert hashes1 == hashes2 == [item['traceg_sha256'] for item in rows]
    write(out / 'HASH_STABILITY_RECEIPT.json', {
        'repeat_sha256_stable': True, 'traceg_members': expected,
        'kernelslist_sha256': sha(raw / 'kernelslist'),
        'kernelslist_g_sha256': sha(raw / 'kernelslist.g')})
    print(json.dumps({'mode': mode, 'status': 'COMPLETE', 'selected_kernels': expected,
                      'traceg_total_bytes': sum(item['traceg_bytes'] for item in rows)}), flush=True)


def main(mode: str, out: Path) -> None:
    if out.exists():
        raise SystemExit(f'output collision: {out}')
    frozen = json.loads((ROOT / 'CAPTURE_SELECTOR_FROZEN.json').read_text())
    scope = json.loads((ROOT / 'CAPTURE_SCOPE_PREREGISTRATION.json').read_text())
    assert frozen['all_ns_exact_function_grid_block_match_accepted_r101r1']
    assert scope['selected_count'] == 18
    expected = {'canary1': 1, 'canary_multi': 3, 'formal': 18}[mode]
    selector = {'canary1': 'XXT_kernel',
                'canary_multi': 'XXT_kernel|ba_plus_cAA_kernel|bmm_add_kernel',
                'formal': '.*'}[mode]
    out.mkdir(parents=True)
    raw = out / 'raw'
    raw.mkdir()
    env = os.environ.copy()
    env.update({
        'PATH': '/usr/local/cuda-12.8/bin:' + env.get('PATH', ''),
        'NVDISASM': '/usr/local/cuda-12.8/bin/nvdisasm',
        'NO_EAGER_LOAD': '1',
        'CUDA_INJECTION64_PATH': str(TRACER),
        'ROUTE_B_RAW_DIR': str(raw),
        'ROUTE_B_FUNCTION_REGEX': selector,
        'ROUTE_B_MULTI_SELECTED_COUNT': str(expected),
        'TOOL_VERBOSE': '0', 'PYTHONUNBUFFERED': '1',
        'HF_HOME': str(ROOT / 'cache/hf'),
        'TRITON_CACHE_DIR': str(ROOT / 'cache/triton'),
        'CUDA_CACHE_PATH': str(ROOT / 'cache/cuda'),
        'TORCHINDUCTOR_CACHE_DIR': str(ROOT / 'cache/inductor'),
        'XDG_CACHE_HOME': str(ROOT / 'cache/xdg'),
        'TMPDIR': str(ROOT / 'tmp'),
    })
    if mode == 'canary1':
        env['INSTR_END'] = '8'
    else:
        env.pop('INSTR_END', None)
    cmd = [str(PYTHON), str(DRIVER), '--mode', mode, '--outdir', str(out)]
    write(out / 'CAPTURE_COMMAND.json', {
        'argv': cmd, 'mode': mode, 'selector_regex': selector,
        'selected_kernel_count': expected, 'NO_EAGER_LOAD': '1',
        'INSTR_END': env.get('INSTR_END', 'FULL'),
        'tracer_sha256': sha(TRACER), 'driver_sha256': sha(DRIVER),
        'postprocessor_sha256': sha(POST), 'grammar_validator_sha256': sha(VALIDATOR),
        'scientific_payload_sha256': '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'})
    caps = {'canary1': (1 * 1024**3, 1200),
            'canary_multi': (8 * 1024**3, 2400),
            'formal': (scope['per_run_raw_cap_bytes'], scope['time_cap_seconds'])}
    byte_cap, time_cap = caps[mode]
    max_rss = 32 * 1024**3
    guard = {'raw_cap_bytes': byte_cap, 'time_cap_seconds': time_cap,
             'max_host_rss_bytes': max_rss, 'mode': mode}
    with LOCK.open('a+') as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name,uuid,driver_version',
            '--format=csv,noheader'], text=True).strip()
        guard['gpu_identity'] = gpu
        started = time.monotonic()
        with (out / 'driver.stdout.log').open('w') as stdout, (out / 'driver.stderr.log').open('w') as stderr:
            process = subprocess.Popen(cmd, env=env, stdout=stdout, stderr=stderr,
                                       pass_fds=(lock_handle.fileno(),))
            reason = None
            peak_rss = 0
            peak_raw = 0
            while process.poll() is None:
                current_raw = size_tree(raw)
                current_rss = rss_bytes(process.pid)
                peak_raw = max(peak_raw, current_raw)
                peak_rss = max(peak_rss, current_rss)
                if current_raw > byte_cap:
                    reason = 'RAW_SIZE_CAP'
                elif current_rss > max_rss:
                    reason = 'HOST_RSS_CAP'
                elif time.monotonic() - started > time_cap:
                    reason = 'TIME_CAP'
                if reason:
                    process.terminate()
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill(); process.wait()
                    break
                time.sleep(2)
            rc = process.wait()
        fcntl.flock(lock_handle, fcntl.LOCK_UN)
    guard.update({'driver_returncode': rc, 'triggered_reason': reason,
                  'peak_host_rss_bytes': peak_rss, 'peak_raw_bytes': peak_raw,
                  'elapsed_seconds': round(time.monotonic() - started, 3)})
    write(out / 'RESOURCE_GUARD.json', guard)
    if reason or rc != 0:
        raise SystemExit(f'capture diagnostic failure mode={mode} reason={reason} rc={rc}')
    close(out, expected, mode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['canary1', 'canary_multi', 'formal'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.mode, args.out)
