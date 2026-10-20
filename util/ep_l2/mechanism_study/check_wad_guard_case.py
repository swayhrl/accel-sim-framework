"""Finite WAD repair regressions; never starts an application or grants a lease."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-json', required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    case = json.loads(args.case_json)
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    assert Path(command[0]).name.startswith('ep_l2_')
    assert case['expected_exit'] in (-6, 0)
    assert not args.receipt.exists()
    raw = args.receipt.with_suffix('.native.log')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 2**20, 16 * 2**20))
    started = time.time()
    with raw.open('xb') as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
        proc = Path('/proc') / str(child.pid)
        try:
            start_ticks = int((proc / 'stat').read_text().rsplit(') ', 1)[1].split()[19])
        except FileNotFoundError:
            start_ticks = None
        identity = dict(pid=child.pid, start_ticks=start_ticks,
                        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
        actual = child.wait()
    text = raw.read_text(errors='replace')
    terminals = {t: t in text for t in case['terminals']}
    verified = actual == case['expected_exit'] and all(terminals.values())
    result = dict(case=case['id'], command=command, native_process=identity,
                  started_unix=started, wall_seconds=time.time()-started,
                  expected_exit=case['expected_exit'], actual_exit=actual,
                  expectation_verified=verified, terminal_checks=terminals,
                  binary_sha256=hashlib.sha256(Path(command[0]).read_bytes()).hexdigest(),
                  raw_log=str(raw), raw_log_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                  scientific_scope='FINITE_PRODUCTION_PATH_SYMBOLIC_VERSION_NOT_APPLICATION_ACCEPTANCE',
                  expected_old_assert_is_not_PASS=case['expected_exit'] == -6)
    args.receipt.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(case=case['id'], actual_exit=actual, expectation_verified=verified)))
    if not verified:
        print(text[-3500:])
        raise RuntimeError('WAD repair regression mismatch: '+str(args.receipt))


if __name__ == '__main__':
    main()
