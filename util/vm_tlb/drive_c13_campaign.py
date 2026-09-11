#!/usr/bin/env python3
"""Conservative, manifest-bound C13 campaign driver.

The driver is intentionally unable to alter a simulator configuration, trace,
registration, Core, or binary.  It only selects the next already-prepared
manifest row, admits it under the C13 adaptive-addendum policy, and invokes
the existing per-arm runner.  It is safe to leave running while a simulator is
live: it never launches more than the nine full-ROI arms in the fixed C13
matrix; it cannot create an additional experiment row.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_MINIMAL_DIAGNOSTICS'
MANIFEST = PACK / 'C13_COMMAND_MANIFEST.tsv'
OUT = Path('/workspace/vm-m4b-c13-diagnostics/results')
RUNNER = ROOT / 'util/vm_tlb/c13_diagnostic_tool.py'
COLLECTOR = ROOT / 'util/vm_tlb/collect_c13_diagnostics.py'
SAMPLES = PACK / 'ADAPTIVE_ADMISSION_SAMPLES.tsv'
RSS = re.compile(r'Maximum resident set size \(kbytes\):\s*(\d+)')

# P0 must finish before the new-binary controls and their paired selective
# candidates.  This order deliberately does not react to measured values.
ORDER = ('C13-LAT-P8', 'C13-LAT-D11', 'C13-LAT-P9', 'C13-CAP-P320',
         'C13-CAP-P768S10', 'C13-SEL-P10-CTRL-NEWBIN',
         'C13-SEL-D10-CTRL-NEWBIN', 'C13-SEL-P10', 'C13-SEL-D10')
# User-authorized expansion after three GREEN host windows. This is exactly
# the complete fixed C13 matrix (seven primary rows plus two mandatory
# same-new-binary controls), never a license to add a tenth experiment.
MAX_LIVE_ARMS = 9


def fail(message: str) -> None:
    raise SystemExit('C13 DRIVER FAIL: ' + message)


def rows() -> dict[str, dict[str, str]]:
    with MANIFEST.open(newline='') as source:
        found = {row['exp_id']: row for row in csv.DictReader(source, delimiter='\t')}
    if set(found) != set(ORDER):
        fail('manifest identity differs from fixed C13 execution plan')
    return found


def process_args() -> str:
    return subprocess.check_output(['ps', '-eo', 'args='], text=True, errors='replace')


def terminal(exp: str, row: dict[str, str]) -> str:
    validation = Path(row['output_dir']) / 'C13_ARM_VALIDATION.json'
    if validation.is_file():
        result = json.loads(validation.read_text())
        return result.get('terminal_status', 'FAILED_DIAGNOSING')
    run = Path(row['output_dir'])
    if run.is_dir() and row['output_dir'] in process_args():
        return 'RUNNING'
    if run.is_dir():
        return 'INCOMPLETE_OR_FAILED'
    return 'NOT_STARTED'


def psi(kind: str) -> tuple[float, float]:
    entries = {}
    for part in Path('/proc/pressure/' + kind).read_text().split():
        if '=' in part:
            key, value = part.split('=', 1)
            entries[key] = value
    # The tokens are prefixed by "some"/"full" but subsequent avg10 values
    # have identical names. Parse lines rather than use the flattened map.
    values = {}
    for line in Path('/proc/pressure/' + kind).read_text().splitlines():
        pieces = dict(item.split('=', 1) for item in line.split()[1:])
        values[line.split()[0]] = float(pieces['avg10'])
    return values['some'], values['full']


def vmstat() -> tuple[float, float, float, float]:
    text = subprocess.check_output(['vmstat', '1', '2'], text=True)
    values = text.splitlines()[-1].split()
    # procs/memory/swap/io/system/cpu: si so ... id wa
    return float(values[6]), float(values[7]), float(values[14]), float(values[15])


def mem_available_kib() -> int:
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1])
    fail('MemAvailable unavailable')


def live_c13_rss_kib(plan: dict[str, dict[str, str]]) -> int:
    output = subprocess.check_output(['ps', '-eo', 'rss=,args='], text=True, errors='replace')
    largest = 0
    for line in output.splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) == 2 and any(row['output_dir'] in fields[1] for row in plan.values()):
            largest = max(largest, int(fields[0]))
    # The first completed C13 arm is the addendum's required peak-RSS anchor
    # for subsequent launches. Include it even if no live C13 arm remains.
    for row in plan.values():
        sidecar = Path(row['output_dir']) / 'time-v.txt'
        if sidecar.is_file():
            match = RSS.search(sidecar.read_text(errors='replace'))
            if match: largest = max(largest, int(match.group(1)))
    return largest


def sample(plan: dict[str, dict[str, str]], label: str) -> dict[str, str]:
    mem_some, mem_full = psi('memory'); io_some, io_full = psi('io')
    swap_in, swap_out, idle, iowait = vmstat()
    current = [exp for exp, row in plan.items() if terminal(exp, row) == 'RUNNING']
    row = {
        'utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'label': label, 'logical_cpus': str(os.cpu_count()),
        'mem_available_kib': str(mem_available_kib()), 'memory_psi_some_avg10': f'{mem_some:.2f}',
        'memory_psi_full_avg10': f'{mem_full:.2f}', 'io_psi_some_avg10': f'{io_some:.2f}',
        'io_psi_full_avg10': f'{io_full:.2f}', 'swap_in_kib_s': f'{swap_in:.0f}',
        'swap_out_kib_s': f'{swap_out:.0f}', 'cpu_idle_pct': f'{idle:.0f}',
        'iowait_pct': f'{iowait:.0f}', 'live_c13_arms': ','.join(current) or 'NONE',
        'largest_live_c13_rss_kib': str(live_c13_rss_kib(plan)),
        'accel_sim_processes': str(len(subprocess.check_output(['pgrep', '-f', 'accel-sim.out'], text=True).splitlines())),
    }
    new = not SAMPLES.exists()
    with SAMPLES.open('a', newline='') as sink:
        fields = list(row)
        writer = csv.DictWriter(sink, fieldnames=fields, delimiter='\t', lineterminator='\n')
        if new: writer.writeheader()
        writer.writerow(row)
    return row


def green(window: list[dict[str, str]]) -> tuple[bool, str]:
    # All three windows must pass; swap values from vmstat are KiB/s.
    for row in window:
        mem = int(row['mem_available_kib']) / (1024 * 1024)
        if float(row['cpu_idle_pct']) < 3: return False, 'cpu_idle_below_3pct'
        if mem < 48: return False, 'memavailable_below_48GiB'
        if float(row['memory_psi_full_avg10']) > 1: return False, 'memory_psi_full'
        if float(row['io_psi_full_avg10']) > 2: return False, 'io_psi_full'
        if float(row['iowait_pct']) > 12: return False, 'iowait'
        if max(float(row['swap_in_kib_s']), float(row['swap_out_kib_s'])) > 4096: return False, 'swap_rate'
    peak = max(int(row['largest_live_c13_rss_kib']) for row in window)
    # If no prior terminal C13 arm exists, use current stable RSS as a
    # conservative launch estimate. Once a terminal time sidecar exists, its
    # peak is used by the same formula on subsequent admissions.
    need_gib = 1.5 * peak / (1024 * 1024) + 2
    if min(int(row['mem_available_kib']) / (1024 * 1024) for row in window) < 32 + need_gib:
        return False, 'one_more_memory_model'
    return True, 'GREEN'


def collect() -> None:
    result = subprocess.run([sys.executable, str(COLLECTOR)], cwd=ROOT)
    if result.returncode:
        fail('collector returned %d' % result.returncode)


def revalidate(exp: str) -> None:
    """Apply the immutable-log validator repair; never replay an arm."""
    print('C13_DRIVER_REVALIDATE\tarm=' + exp, flush=True)
    result = subprocess.run([sys.executable, str(RUNNER), '--validate', exp], cwd=ROOT)
    if result.returncode:
        fail('%s immutable-log revalidation failed %d; raw evidence retained' % (exp, result.returncode))


def next_candidate(plan: dict[str, dict[str, str]]) -> str | None:
    status = {exp: terminal(exp, row) for exp, row in plan.items()}
    bad = {exp: state for exp, state in status.items() if state in {'FAILED_DIAGNOSING', 'INCOMPLETE_OR_FAILED'}}
    if bad: fail('preserved nonterminal/failed C13 attempt requires diagnosis: %s' % bad)
    p0 = ORDER[:5]
    if any(status[exp] != 'PASS' for exp in p0):
        return next(exp for exp in p0 if status[exp] == 'NOT_STARTED') if any(status[exp] == 'NOT_STARTED' for exp in p0) else None
    # Controls precede candidates, ensuring no cross-binary selective claim.
    for exp in ORDER[5:]:
        if status[exp] == 'NOT_STARTED': return exp
    return None


def needs_collection(exp: str, row: dict[str, str]) -> bool:
    validation = Path(row['output_dir']) / 'C13_ARM_VALIDATION.json'
    receipt = Path(row['output_dir']) / 'C13_ARM_COLLECTED.json'
    if not validation.is_file() or not receipt.is_file(): return validation.is_file()
    try:
        return json.loads(receipt.read_text()).get('raw_log_sha256') != json.loads(validation.read_text()).get('raw_log_sha256')
    except json.JSONDecodeError:
        return True


def once(plan: dict[str, dict[str, str]], dry_run: bool) -> bool:
    # An already exited child may still carry a failure generated by a prior
    # validator bytecode image.  Revalidate its immutable log with the current
    # source before classifying it as a scientific failure.  A genuine failure
    # remains fail-fast because --validate returns nonzero after preserving the
    # pre-repair validation JSON.
    failed = [exp for exp, row in plan.items() if terminal(exp, row) == 'FAILED_DIAGNOSING']
    if failed:
        for exp in failed:
            revalidate(exp)
        return True
    current = [exp for exp, row in plan.items() if terminal(exp, row) == 'RUNNING']
    if len(current) > MAX_LIVE_ARMS: fail('C13 observed more live full-ROI arms than the fixed matrix')
    completed_uncollected = [exp for exp, row in plan.items()
                             if terminal(exp, row) == 'PASS' and needs_collection(exp, row)]
    if completed_uncollected:
        print('C13_DRIVER_COLLECT\tarms=' + ','.join(completed_uncollected), flush=True)
        collect()
    if len(current) == MAX_LIVE_ARMS:
        print('C13_DRIVER_HOLD\tlive=%d\tarms=' % MAX_LIVE_ARMS + ','.join(current)); return False
    candidate = next_candidate(plan)
    if candidate is None:
        if not current: collect(); print('C13_DRIVER_COMPLETE')
        else: print('C13_DRIVER_HOLD\tlive=1\tno_admissible_next')
        return False
    windows=[]
    for index in range(3):
        windows.append(sample(plan, '%s_prelaunch_%d' % (candidate,index+1)))
        if index != 2: time.sleep(20)
    allowed, reason=green(windows)
    if not allowed:
        print('C13_DRIVER_HOLD\tcandidate=%s\treason=%s' % (candidate,reason)); return False
    if dry_run:
        print('C13_DRIVER_DRY_RUN_ADMIT\t' + candidate); return False
    print('C13_DRIVER_LAUNCH\t' + candidate, flush=True)
    result=subprocess.run([sys.executable,str(RUNNER),'--execute',candidate],cwd=ROOT)
    if result.returncode: fail('%s runner failed %d; raw evidence retained' % (candidate,result.returncode))
    collect()
    return True


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--dry-run',action='store_true'); parser.add_argument('--once',action='store_true'); parser.add_argument('--interval',type=int,default=30)
    args=parser.parse_args()
    if args.interval < 10 or args.interval > 60: fail('interval must be 10..60 seconds')
    if args.once:
        once(rows(),args.dry_run)
        return
    while True:
        plan=rows()
        launched=once(plan,args.dry_run)
        if args.dry_run or not launched:
            time.sleep(args.interval)
        # A launched arm completed here. Re-enter promptly to let the state
        # machine either refill the second slot or hold on a resource window.


if __name__ == '__main__':
    main()
