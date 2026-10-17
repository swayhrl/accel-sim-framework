"""Passive detached status logging; never launches, retries, or signals a run."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import time


ROOT = Path('/workspace/dtc-t1c-holdout-174-v1')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def process(pid):
    try:
        directory = Path('/proc') / str(pid)
        raw = (directory / 'stat').read_text()
        fields = raw[raw.rfind(')') + 2:].split()
        return dict(pid=pid, state=fields[0], parent_pid=int(fields[1]),
                    process_group=int(fields[2]), session=int(fields[3]),
                    start_ticks=int(fields[19]))
    except (FileNotFoundError, ProcessLookupError):
        return None


def read(name):
    try:
        return json.loads((ROOT / name).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write(name, value):
    temporary = ROOT / (name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(ROOT / name)


def main():
    lock = (ROOT / 'PASSIVE_STATUS.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    owner = read('AUTHORITY_ACTIVE.json')
    assert owner and owner['pid'] == 2132794 and owner['start_ticks'] == 898867525
    identity = process(os.getpid())
    write('PASSIVE_STATUS_ACTIVE.json', dict(utc=now(), process=identity,
          role='PASSIVE_STATUS_ONLY_NO_EXECUTION_AUTHORITY',
          watches_authority=owner, interval_seconds=30, max_seconds=43200))
    end = time.monotonic() + 43200
    sequence = 0
    while True:
        sequence += 1
        authority = process(owner['pid'])
        alive = bool(authority and authority['state'] != 'Z' and
                     authority['start_ticks'] == owner['start_ticks'])
        terminal = read('AUTHORITY_TERMINAL.json')
        status = read('STATUS.json')
        sample = ROOT / 'RESOURCE_SAMPLES.jsonl'
        heartbeat = dict(utc=now(), sequence=sequence, monitor=identity,
                         authority_alive=alive, execution_status=status,
                         resource_sample_age_seconds=(time.time() - sample.stat().st_mtime)
                         if sample.exists() else None,
                         terminal_receipt_present=bool(terminal),
                         launches_or_signals_by_monitor=0)
        write('PASSIVE_STATUS_HEARTBEAT.json', heartbeat)
        if not alive or time.monotonic() >= end:
            result = ('READY_FOR_TERMINAL_AUDIT' if terminal and not alive else
                      'AUTHORITY_ABSENT_REQUIRES_AUDIT' if not alive else
                      'PASSIVE_MONITOR_DEADLINE_NO_EXECUTION_ACTION')
            write('PASSIVE_STATUS_TERMINAL.json', dict(utc=now(), result=result,
                  heartbeat=heartbeat, authority_terminal=terminal,
                  no_final_scientific_acceptance_by_monitor=True))
            return
        time.sleep(30)


if __name__ == '__main__':
    main()
