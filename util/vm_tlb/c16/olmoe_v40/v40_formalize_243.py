#!/usr/bin/env python3
"""CPU-only formal admission of the immutable V40 typed-sweep shards."""
import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path

REPO = Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v39')
ROOT = Path('/data/c16/olmoe_v40/typed_sweep')
LOG = ROOT / 'ATTEMPTS.jsonl'
SELECTOR = Path('/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')
VALIDATOR = REPO / 'util/vm_tlb/c16/olmoe_v40/c16warp1_v40_validator.py'
OUT = ROOT / 'formal_admission'
EXPECTED_SELECTOR = '9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, value):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(temp, path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    selector = list(csv.DictReader(SELECTOR.open(), delimiter='\t'))
    wanted = [int(row['static_index']) for row in selector]
    attempts = [json.loads(line) for line in LOG.read_text().splitlines() if line]
    if len(wanted) != 243 or len(set(wanted)) != 243 or len(attempts) != 243:
        raise SystemExit('selector/log cardinality failure')
    if set(item['static_index'] for item in attempts) != set(wanted):
        raise SystemExit('selector/log membership failure')
    shards, tool_shas, replay_shas, function_shas = [], set(), set(), set()
    for item in sorted(attempts, key=lambda value: value['static_index']):
        root = Path(item['attempt_root'])
        receipt = json.loads((root / 'SUPERVISOR_RECEIPT.json').read_text())
        validation = root / 'C16WARP1_FORMAL_VALIDATOR_RECEIPT.json'
        run = subprocess.run(['/usr/bin/python3', str(VALIDATOR), '--trace', str(root / 'trace.bin'),
                              '--stdout', str(root / 'stdout.log'), '--static-index', str(item['static_index']),
                              '--occurrence', '0', '--receipt', str(validation)], text=True, capture_output=True)
        verdict = json.loads(validation.read_text()) if validation.exists() else {'status': 'REJECT', 'reason': 'missing validator receipt'}
        clean = item.get('result', {}).get('phase') == 'CLEAN_EXIT' and item.get('result', {}).get('timed_out') is False
        accepted = run.returncode == 0 and verdict.get('status') == 'PASS' and clean and receipt.get('selected_static') == item['static_index']
        classification = 'EXECUTED' if accepted and verdict.get('record_count', 0) > 0 else 'ZERO_EXECUTION_PROVEN' if accepted else 'FAILED_EXCLUDED'
        shards.append({'static_index': item['static_index'], 'attempt_root': str(root), 'classification': classification,
                       'record_count': verdict.get('record_count'), 'validator_receipt': str(validation),
                       'validator_status': verdict.get('status'), 'hits': item.get('hits', {})})
        tool_shas.add(receipt.get('tool_sha256')); replay_shas.add(receipt.get('canonical_replay_sha256')); function_shas.add(receipt.get('function_identity_sha256'))
    summary = {'schema_version': 1, 'status': 'PASS' if all(row['classification'] != 'FAILED_EXCLUDED' for row in shards) else 'FAIL',
               'total_selected': len(wanted), 'executed_count': sum(row['classification'] == 'EXECUTED' for row in shards),
               'zero_count': sum(row['classification'] == 'ZERO_EXECUTION_PROVEN' for row in shards),
               'failed_excluded_count': sum(row['classification'] == 'FAILED_EXCLUDED' for row in shards),
               'dynamic_event_total': sum(row['record_count'] or 0 for row in shards),
               'selector_path': str(SELECTOR), 'selector_file_sha256': sha256(SELECTOR), 'frozen_normalized_selector_sha256': EXPECTED_SELECTOR,
               'uniform_tool_sha256': sorted(tool_shas), 'uniform_replay_sha256': sorted(replay_shas), 'uniform_function_identity_sha256': sorted(function_shas),
               'shards_jsonl': str(OUT / 'FORMAL_243_SHARDS.jsonl')}
    (OUT / 'FORMAL_243_SHARDS.jsonl').write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in shards))
    atomic_json(OUT / 'FORMAL_243_SUMMARY.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
