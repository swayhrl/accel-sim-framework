"""Detached read-only observer requested by the user before pausing the Goal."""
import fcntl
import time
from common import *


def main():
    lock = (ROOT/'BACKGROUND_MONITOR.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    authority = json.loads((ROOT/'AUTHORITY_ACTIVE_V2.json').read_text())
    owner = proc(os.getpid())
    write(ROOT/'BACKGROUND_MONITOR_ACTIVE_V1.json', dict(
        utc=now(), pid=owner['pid'], start_ticks=owner['start_ticks'],
        authority_pid=authority['pid'], authority_start_ticks=authority['start_ticks'],
        script_sha256=sha(__file__), observer_only=True, max_observation_hours=48,
        actions='READ_STATUS_AND_PID_ONLY; NO_SIGNAL; NO_LAUNCH; NO_RETRY; NO_FINALIZATION',
    ))
    deadline = time.monotonic()+48*3600
    previous = None
    while True:
        status = json.loads((ROOT/'STATUS.json').read_text())
        current = proc(authority['pid'])
        alive = bool(current and current['start_ticks']==authority['start_ticks']
                     and current['state']!='Z')
        terminal_path = ROOT/'AUTHORITY_TERMINAL.json'
        terminal = json.loads(terminal_path.read_text()) if terminal_path.exists() else None
        state = ('EXECUTION_FINISHED_READY_FOR_GOAL_RESUME' if terminal and not alive else
                 'WAIT_AUTHORITY_EXIT' if terminal else
                 'ATTENTION_AUTHORITY_MISSING_NO_TERMINAL' if not alive else
                 'HOLD_DRAINING_ACTIVE_POINTS' if status['halted'] else 'RUNNING')
        if time.monotonic() >= deadline:
            state = 'ATTENTION_OBSERVATION_DEADLINE_NO_EXECUTION_ACTION'
        evidence = dict(
            utc=now(), state=state, observer_pid=os.getpid(), authority_live=alive,
            authority_pid=authority['pid'], authority_start_ticks=authority['start_ticks'],
            execution_status_utc=status['utc'], active=status['active'],
            terminal=status['terminal'], halted=status['halted'],
            not_launched=status['not_launched'], goal_pause_requested_by_user=True,
            auto_resume_capability=False,
        )
        temporary = ROOT/'BACKGROUND_MONITOR_STATUS.tmp'
        temporary.write_text(json.dumps(evidence, indent=2)+'\n')
        temporary.replace(ROOT/'BACKGROUND_MONITOR_STATUS.json')
        signature = (state, tuple(status['active']), tuple(status['terminal'].items()),
                     status['halted'], tuple(status['not_launched']))
        if signature != previous:
            with (ROOT/'BACKGROUND_MONITOR_EVENTS.jsonl').open('a') as stream:
                stream.write(json.dumps(evidence)+'\n')
            print(json.dumps(evidence), flush=True)
            previous = signature
        if state.startswith(('EXECUTION_FINISHED', 'ATTENTION_')):
            write(ROOT/'BACKGROUND_MONITOR_TERMINAL.json', dict(
                **evidence, authority_terminal_sha256=sha(terminal_path) if terminal else None,
                instructions='Resume Goal for final audit, complete matrix, scores, push and fetch-back.',
            ))
            return
        time.sleep(30)


if __name__ == '__main__':
    main()
