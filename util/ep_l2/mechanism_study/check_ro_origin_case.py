"""Finite native RO origin regression only; never grants resources or runs an app."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-exit', type=int, choices=(-11, 0), required=True)
    p.add_argument('--required-terminal', required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    assert Path(command[0]).name in ('ep_l2_ro_detailed_origin_old', 'ep_l2_ro_detailed_origin_new')
    assert not a.receipt.exists()
    raw = a.receipt.with_suffix('.native.log')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 2**20, 16 * 2**20))
    started = time.time()
    with raw.open('xb') as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
        actual_exit = child.wait()
    text = raw.read_text(errors='replace')
    ok = actual_exit == a.expected_exit and a.required_terminal in text
    row = dict(command=command, native_pid=child.pid, native_started_unix=started,
        expected_exit=a.expected_exit, actual_exit=actual_exit, expectation_verified=ok,
        required_terminal=a.required_terminal, raw_log=str(raw),
        raw_log_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
        binary_sha256=hashlib.sha256(Path(command[0]).read_bytes()).hexdigest(),
        scientific_scope='FINITE_REAL_DETAILED_DRAM_NOT_APPLICATION_ACCEPTANCE',
        old_source_binary_is_real=(a.expected_exit == -11))
    a.receipt.write_text(json.dumps(row, indent=2)+'\n')
    print(text[-3500:])
    if not ok:
        raise RuntimeError('native origin regression mismatch: '+str(a.receipt))


if __name__ == '__main__':
    main()
