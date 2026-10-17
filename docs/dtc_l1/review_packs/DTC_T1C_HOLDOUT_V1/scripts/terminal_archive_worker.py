"""Wait for the original finite authority, then archive evidence once, without Git."""
import fcntl
import sys
import time
from common import *


def main():
    lock = (ROOT / 'TERMINAL_ARCHIVE.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not (ROOT / 'TERMINAL_ARCHIVE_ACTIVE.json').exists()
    owner = json.loads((ROOT / 'AUTHORITY_ACTIVE.json').read_text())
    assert owner['pid'] == 2132794 and owner['start_ticks'] == 898867525
    write(ROOT / 'TERMINAL_ARCHIVE_ACTIVE.json', dict(utc=now(), process=proc(os.getpid()),
        authority=owner, role='TERMINAL_CPU_ARCHIVE_ONLY_NO_SIMULATOR_OR_GIT',
        wall_wait_seconds=43200, interval_seconds=30))
    deadline = time.monotonic() + 43200
    steps = []
    try:
        while True:
            current = proc(owner['pid'])
            alive = bool(current and current['state'] != 'Z' and
                         current['start_ticks'] == owner['start_ticks'])
            if not alive:
                terminal = json.loads((ROOT / 'AUTHORITY_TERMINAL.json').read_text())
                assert terminal['status'] == 'NATURAL_FOREGROUND_AUTHORITY_END'
                assert not terminal['final']['active']
                for path in (ROOT / 'attempts').glob('*/PID.json'):
                    pid = json.loads(path.read_text())
                    for key, ticks in [('runner_pid', 'runner_start_ticks'),
                                       ('process_pid', 'process_start_ticks')]:
                        process = proc(pid[key])
                        assert not process or process['state'] == 'Z' or process['start_ticks'] != pid[ticks]
                break
            assert time.monotonic() < deadline, 'Archive wait deadline; leave original execution untouched'
            time.sleep(30)
        assert not (PACK / 'FULL_MATRIX.tsv').exists(), 'Inspect previous archive before any rerun'
        for name in ['finalize_holdout.py', 'summarize_terminal_resources.py',
                     'audit_terminal_evidence.py', 'render_review_report.py']:
            step = dict(script=name, start_utc=now(), script_sha256=sha(PACK / 'scripts' / name))
            result = subprocess.run([sys.executable, '-E', '-B', str(PACK / 'scripts' / name)],
                                    cwd=FW, check=False)
            step.update(exit_status=result.returncode, end_utc=now())
            steps.append(step)
            assert result.returncode == 0, 'Archive step failed: ' + name
        write(ROOT / 'TERMINAL_ARCHIVE_TERMINAL.json', dict(utc=now(),
            status='READY_FOR_FINAL_HUMAN_CONTRACT_AND_PUBLICATION_AUDIT', steps=steps,
            no_simulator_launches=True, no_Git_mutations=True, goal_completion_not_claimed=True))
    except Exception as exc:
        write(ROOT / 'TERMINAL_ARCHIVE_TERMINAL.json', dict(utc=now(),
            status='ARCHIVE_FAILURE_PRESERVED_NO_AUTOMATIC_RETRY', error=repr(exc), steps=steps,
            no_simulator_launches=True, no_Git_mutations=True, goal_completion_not_claimed=True))
        raise


if __name__ == '__main__':
    main()
