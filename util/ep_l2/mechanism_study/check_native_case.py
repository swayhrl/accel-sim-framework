"""Bounded exit/terminal evidence wrapper; grants no resource admission."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import resource
import time
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-exit', type=int, required=True)
    p.add_argument('--required-terminal', required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    assert command and a.expected_exit in (0, 21)
    assert Path(command[0]).name.startswith('ep_l2_'), 'finite test targets only, no application'
    assert not a.receipt.exists(), 'retain previous evidence'
    # The outer A-owned supervisor enforces the same lease, timeout, memory,
    # disk and process-group stop for this wrapper and every descendant.
    raw = a.receipt.with_suffix('.native.log')
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 2**20, 16 * 2**20))
    with raw.open('xb') as f:
        child = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT)
        native_pid = child.pid
        native_started_unix = time.time()
        actual_exit = child.wait()
    # The outer supervisor continuously budgets this actual file. Do not
    # buffer an unbounded native log invisibly in the Python wrapper's RAM.
    assert raw.stat().st_size <= 16 * 2**20, 'finite case output exceeded16MiB'
    data = raw.read_bytes()
    text = data.decode(errors='replace')
    ok = actual_exit == a.expected_exit and a.required_terminal in text
    report = dict(command=command, native_pid=native_pid, native_started_unix=native_started_unix, expected_exit=a.expected_exit,
        actual_exit=actual_exit, required_terminal=a.required_terminal,
        expectation_verified=ok, raw_log=str(raw),
        raw_log_sha256=hashlib.sha256(data).hexdigest(),
        binary_sha256=hashlib.sha256(Path(command[0]).read_bytes()).hexdigest(),
        scientific_scope='FINITE_NATIVE_EXPECTATION_ONLY_NOT_E_QUALIFICATION',
        legacy_toggle_is_old_source_binary_evidence=False)
    a.receipt.write_text(json.dumps(report, indent=2) + '\n')
    sys.stdout.write(text[-4096:])
    if not ok:
        raise RuntimeError('native exit/terminal mismatch: ' + str(a.receipt))
    print('COMMON_NATIVE_EXPECTATION_VERIFIED|' + a.receipt.name)


if __name__ == '__main__':
    main()
