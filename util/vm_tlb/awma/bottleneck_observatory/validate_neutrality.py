#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-bottleneck-observatory-v1')
RUNTIME = Path('/root/awma_bottleneck_observatory_v1_runtime')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_BOTTLENECK_OBSERVATORY_V1'


def scalar(text: str, key: str):
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*(\d+)', text, re.M)
    return int(match.group(1)) if match else None


def coverage(text: str) -> dict[str, int]:
    match = re.search(r'^AWMA_VM_COVERAGE (.+)$', text, re.M)
    return ({key: int(value) for key, value in
             re.findall(r'(\w+)=(\d+)', match.group(1))} if match else {})


def main() -> int:
    rows = []
    for command_path in sorted((RUNTIME / 'runs').glob(
            '*/10_80/L[0-3]_overhead_*/command.json')):
        run_dir = command_path.parent
        command = json.loads(command_path.read_text())
        text = (run_dir / 'run.log').read_text(errors='replace')
        cov = coverage(text)
        level = int(command['level'])
        gates = {
            'rc_zero': (run_dir / 'rc.txt').read_text().strip() == '0',
            'cycles_exact': scalar(text, 'gpu_sim_cycle') ==
                command['expected']['cycles'],
            'instructions_exact': scalar(text, 'gpu_sim_insn') ==
                command['expected']['instructions'],
            'cta_exact': scalar(text, 'gpu_tot_issued_cta') ==
                command['expected']['cta'],
            'uid_exact': cov.get('unique') == command['expected']['unique_uid'],
            'untranslated_zero': cov.get('untranslated') == 0,
            'unobserved_zero': cov.get('unobserved') == 0,
            'duplicate_zero': scalar(
                text, 'vm_ready_application_duplicate_attempts') == 0,
            'quiescent': scalar(
                text, 'vm_translation_quiescent_invariants_hold') == 1,
            'off_no_output': level != 0 or
                'awma_observatory_schema' not in text,
            'enabled_has_output': level == 0 or
                scalar(text, 'awma_observatory_level') == level,
        }
        rows.append({
            'target': command['target'], 'level': level, 'tag': command['tag'],
            'status': 'PASS' if all(gates.values()) else 'FAIL',
            **{key: int(value) for key, value in gates.items()},
            'run_dir': str(run_dir),
        })
    PACK.mkdir(parents=True, exist_ok=True)
    fields = ('target', 'level', 'tag', 'status', 'rc_zero', 'cycles_exact',
              'instructions_exact', 'cta_exact', 'uid_exact',
              'untranslated_zero', 'unobserved_zero', 'duplicate_zero',
              'quiescent', 'off_no_output', 'enabled_has_output', 'run_dir')
    with (PACK / 'NEUTRALITY_GATES.tsv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    failures = [row for row in rows if row['status'] != 'PASS']
    print(json.dumps({'rows': len(rows), 'failures': len(failures),
                      'status': 'PASS' if not failures else 'FAIL'},
                     sort_keys=True))
    return 0 if not failures and len(rows) == 48 else 1


if __name__ == '__main__':
    raise SystemExit(main())
