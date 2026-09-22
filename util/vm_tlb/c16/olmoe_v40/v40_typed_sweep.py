#!/usr/bin/env python3
"""Sequential, append-only P5 typed-canary selector sweep."""
import csv
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v39')
SUP = REPO / 'util/vm_tlb/c16/olmoe_v40/run_nvbit_supervised.py'
VALIDATOR = REPO / 'util/vm_tlb/c16/olmoe_v40/c16warp1_v40_validator.py'
TOOL = '/data/c16/tools/v40_p5_c16warp1/mem_trace.so'
SELECTOR = Path('/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')
ROOT = Path('/data/c16/olmoe_v40/typed_sweep')
FUNCTION = Path('/data/c16/olmoe_v39r2/function.txt')
ROLES = ('EXPERT_DOWN_INPUT', 'EXPERT_DOWN_WEIGHT', 'EXPERT_DOWN_OUTPUT')
MAX_ATTEMPTS_PER_STATIC = 2


def atomic_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(temporary, path)


def classify(trace, context):
    ranges = [(item['semantic_role'], int(item['ptr'], 16), int(item['ptr'], 16) + item['bytes'])
              for item in json.loads(context.read_text())['ranges']]
    hits = {role: 0 for role, _, _ in ranges}
    raw = trace.read_bytes()
    for offset in range(40, len(raw), 280):
        record = struct.unpack_from('<6I32Q', raw, offset)
        for lane, address in enumerate(record[6:]):
            if record[1] >> lane & 1:
                for role, low, high in ranges:
                    if low <= address < high:
                        hits[role] += 1
    return hits


def rebuild(log):
    attempts, found = [], {}
    if log.exists():
        for line in log.read_text().splitlines():
            item = json.loads(line)
            attempts.append(item)
            if item.get('validator_status') == 'PASS':
                for role, count in item.get('hits', {}).items():
                    if count and role not in found:
                        found[role] = item['static_index']
    return attempts, found


def append(log, item):
    with log.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(item, sort_keys=True) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    log = ROOT / 'ATTEMPTS.jsonl'
    summary = ROOT / 'TYPED_SWEEP_SUMMARY.json'
    rows = list(csv.DictReader(SELECTOR.open(), delimiter='\t'))
    attempts, found = rebuild(log)
    for row in rows:
        if all(role in found for role in ROLES):
            break
        static = int(row['static_index'])
        prior = [item for item in attempts if item['static_index'] == static]
        accepted = any(item.get('validator_status') == 'PASS' for item in prior)
        if accepted or len(prior) >= MAX_ATTEMPTS_PER_STATIC:
            continue
        tag = f'static_{static}'
        command = [sys.executable, str(SUP), '--tag', tag, '--tool', TOOL,
                   '--nvbit-version', '1.7.7.1-p5', '--nvbit-root', '/data/c16/env/nvbit-1.7.7.1', '--instr-begin', '0', '--instr-end', '1096',
                   '--target-function-file', str(FUNCTION), '--selected-static', str(static),
                   '--c16-output', 'trace.bin', '--timeout-seconds', '180']
        run = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
        data = json.loads(run.stdout.splitlines()[-1]) if run.stdout.splitlines() else {}
        attempt_root = Path(data.get('attempt_root', ''))
        item = {'static_index': static, 'supervisor_rc': run.returncode, 'supervisor_stdout': run.stdout,
                'supervisor_stderr': run.stderr, 'attempt_root': str(attempt_root), 'result': {}}
        result_path = attempt_root / 'result.json'
        if result_path.is_file():
            item['result'] = json.loads(result_path.read_text())
        trace, context = attempt_root / 'trace.bin', attempt_root / 'ADDRESS_CONTEXT.json'
        validator_receipt = attempt_root / 'C16WARP1_VALIDATOR_RECEIPT.json'
        if item['result'].get('phase') == 'CLEAN_EXIT' and trace.is_file() and context.is_file():
            validation = subprocess.run([sys.executable, str(VALIDATOR), '--trace', str(trace), '--stdout',
                                         str(attempt_root / 'stdout.log'), '--static-index', str(static),
                                         '--occurrence', '0', '--receipt', str(validator_receipt)], text=True,
                                        capture_output=True)
            item['validator_status'] = 'PASS' if validation.returncode == 0 else 'REJECT'
            item['validator_receipt'] = str(validator_receipt)
            if item['validator_status'] == 'PASS':
                item['hits'] = classify(trace, context)
        else:
            item['validator_status'] = 'NOT_ELIGIBLE'
        append(log, item)
        attempts, found = rebuild(log)
        atomic_json(summary, {'schema_version': 2, 'source_log': str(log), 'found': found, 'attempts': attempts})
    atomic_json(summary, {'schema_version': 2, 'source_log': str(log), 'found': found, 'attempts': attempts})
    print(json.dumps(found, sort_keys=True))


if __name__ == '__main__':
    main()
