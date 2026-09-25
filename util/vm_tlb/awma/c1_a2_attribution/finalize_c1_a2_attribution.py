#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-a2-nonsharing-regression-attribution-v1')
RUNTIME = Path('/root/awma_c1_a2_nonsharing_regression_attribution_v1_runtime')
PAIR_RAW = Path('/root/share/mnt164/huangrulin/awma_c1_opportunity_portability_pair_a_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_C1_A2_NONSHARING_REGRESSION_ATTRIBUTION_V1'
EXPECTED = {
    ('A1', 'off'): 114123, ('A1', 'candidate'): 112023,
    ('A2', 'off'): 117698, ('A2', 'candidate'): 125427,
}
RUNS = ((0, 'semantic_gate', 'all'), (1, 'triage', 'all'),
        (2, 'windowed', 'progress,scheduler,memory,translation'))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def scalar(text: str, key: str):
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*(\d+)', text, re.M)
    return int(match.group(1)) if match else None


def coverage(text: str) -> dict[str, int]:
    match = re.search(r'^AWMA_VM_COVERAGE (.+)$', text, re.M)
    return ({key: int(value) for key, value in
             re.findall(r'(\w+)=(\d+)', match.group(1))} if match else {})


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    gates = []
    for level, tag, domains in RUNS:
        for target, mode in EXPECTED:
            run_dir = RUNTIME / f'runs/{target}/{mode}/L{level}_{tag}'
            text = (run_dir / 'run.log').read_text(errors='replace')
            cov = coverage(text)
            checks = {
                'rc_zero': (run_dir / 'rc.txt').read_text().strip() == '0',
                'cycles_exact': scalar(text, 'gpu_sim_cycle') == EXPECTED[(target, mode)],
                'instructions_exact': scalar(text, 'gpu_sim_insn') == 34883072,
                'cta_exact': scalar(text, 'gpu_tot_issued_cta') == 224,
                'uid_exact': cov.get('unique') == 409024,
                'untranslated_zero': cov.get('untranslated') == 0,
                'unobserved_zero': cov.get('unobserved') == 0,
                'duplicate_zero': scalar(text, 'vm_ready_application_duplicate_attempts') == 0,
                'quiescent': scalar(text, 'vm_translation_quiescent_invariants_hold') == 1,
                'level_output_contract': (
                    'awma_observatory_schema' not in text if level == 0
                    else scalar(text, 'awma_observatory_level') == level),
            }
            if mode == 'candidate':
                checks.update({
                    'ready_share_zero': scalar(text, 'awma_nonblocking_shared_ready_members') == 0,
                    'fallback_exact': scalar(text, 'awma_nonblocking_fallback_members') == 116032,
                    'duplicate_lookup_exact': scalar(text, 'awma_nonblocking_duplicate_physical_lookup_requests') == 116032,
                    'owner_wait_zero': scalar(text, 'awma_owner_wait_member_owner_wait_cycles') == 0,
                    'head_block_zero': scalar(text, 'awma_owner_wait_head_block_total_cycles') == 0,
                })
            gates.append({
                'target': target, 'mode': mode, 'level': level, 'domains': domains,
                'status': 'PASS' if all(checks.values()) else 'FAIL',
                **{key: int(value) for key, value in checks.items()},
                'run_dir': str(run_dir),
            })
    gate_fields = []
    for row in gates:
        for key in row:
            if key != 'run_dir' and key not in gate_fields:
                gate_fields.append(key)
    gate_fields.append('run_dir')
    with (PACK / 'VALIDATION_GATES.tsv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=gate_fields, delimiter='\t',
                                lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(gates)

    raw_rows = []
    for path in sorted((RUNTIME / 'runs').glob('*/*/L*/*')):
        if not path.is_file() or path.name == 'gpgpu_inst_stats.txt':
            continue
        relative = path.relative_to(RUNTIME / 'runs')
        target, mode, run_name = relative.parts[:3]
        level, tag = run_name.split('_', 1)
        raw_rows.append({
            'category': 'DIAGNOSTIC_RUN', 'target': target, 'mode': mode,
            'level': level, 'tag': tag, 'artifact': path.name,
            'path': str(path), 'sha256': sha256(path),
            'bytes': path.stat().st_size, 'status': 'FORMAL',
        })
    for source_name in ('A1_OFF_10_80', 'A1_NONBLOCKING_SHARE_10_80',
                        'A2_OFF_10_80', 'A2_NONBLOCKING_SHARE_10_80'):
        for artifact in ('run.log', 'command.json'):
            path = PAIR_RAW / source_name / artifact
            raw_rows.append({
                'category': 'ACCEPTED_PAIR_A', 'target': source_name[:2],
                'mode': 'candidate' if 'NONBLOCKING' in source_name else 'off',
                'level': '', 'tag': 'accepted', 'artifact': artifact,
                'path': str(path), 'sha256': sha256(path),
                'bytes': path.stat().st_size, 'status': 'AUTHORITY',
            })
    source_files = (
        RUNTIME / 'bin/unified_accel-sim.out', RUNTIME / 'DIAGNOSTIC_BINARY.sha256',
        RUNTIME / 'core_build.log', RUNTIME / 'accelsim_build.log',
        RUNTIME / 'CANDIDATE_SOURCE_FREEZE.sha256',
        RUNTIME / 'observatory_transplant_apply.log',
        RUNTIME / 'observatory_transplant_reverse.log')
    for path in source_files:
        raw_rows.append({
            'category': 'BUILD_OR_AUDIT', 'target': '', 'mode': '', 'level': '',
            'tag': '', 'artifact': path.name, 'path': str(path),
            'sha256': sha256(path), 'bytes': path.stat().st_size,
            'status': 'FORMAL'})
    raw_fields = ('category', 'target', 'mode', 'level', 'tag', 'artifact',
                  'path', 'sha256', 'bytes', 'status')
    with (PACK / 'RAW_DATA_INDEX.tsv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=raw_fields, delimiter='\t',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(raw_rows)

    summary = {
        'status': 'PASS' if all(row['status'] == 'PASS' for row in gates) else 'FAIL',
        'gate_rows': len(gates), 'raw_rows': len(raw_rows),
        'level3': 'NOT_RUN_NOT_NEEDED',
        'decision': 'SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR',
    }
    (PACK / 'VALIDATION_SUMMARY.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary['status'] == 'PASS' and len(gates) == 12 else 1


if __name__ == '__main__':
    raise SystemExit(main())
