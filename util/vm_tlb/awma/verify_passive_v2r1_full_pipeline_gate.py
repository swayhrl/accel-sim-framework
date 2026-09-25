#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING_V2R1_BASELINE_PRESERVING'
RUNTIME = Path('/root/awma_passive_last_translation_result_forwarding_v2r1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_passive_last_translation_result_forwarding_v2r1/raw')

EXACT_KEYS = (
    'gpu_sim_cycle',
    'vm_translation_lookup_requests',
    'awma_passive_v2r1_prelaunch_attempts',
    'gpu_sim_insn',
    'gpu_tot_issued_cta',
    'vm_translation_mshr_allocations',
    'vm_translation_mshr_merges',
    'vm_functional_completed',
    'icnt_total_pkts_simt_to_mem',
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)}\s*=\s*(\d+)\s*$', text, re.M)
    if not values:
        raise RuntimeError(f'missing {key}')
    return int(values[-1])


def coverage(text: str) -> dict[str, int]:
    values = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) '
        r'untranslated=(\d+) unobserved=(\d+) unique=(\d+) '
        r'translated_unique=(\d+) untranslated_unique=(\d+)', text)
    if not values:
        raise RuntimeError('missing AWMA_VM_COVERAGE')
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, values[-1])))


def parse(label: str) -> dict[str, object]:
    directory = DURABLE / f'ZERO_M1_{label}_10_80'
    if (directory / 'rc.txt').read_text().strip() != '0':
        raise RuntimeError(f'{label}: nonzero simulator exit')
    log_path = directory / 'run.log'
    text = log_path.read_text(errors='replace')
    values = {key: number(text, key) for key in EXACT_KEYS}
    cov = coverage(text)
    values['coverage_admissions'] = cov['admissions']
    values['coverage_re_admissions'] = cov['admissions'] - cov['unique']
    values['coverage_unique_uid'] = cov['unique']
    return {
        'values': values,
        'coverage': cov,
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'duplicate_application': number(
            text, 'vm_ready_application_duplicate_attempts'),
        'quiescent': number(text, 'vm_translation_quiescent_invariants_hold'),
        'forward_hits': number(text, 'awma_passive_v2r1_hits'),
        'live_entries': number(text, 'awma_passive_v2r1_live_entries'),
        'detached_waiters': number(
            text, 'vm_passive_v2r1_detached_waiters_final'),
        'run_log_sha256': sha(log_path),
        'command_sha256': sha(directory / 'command.json'),
    }


def main() -> int:
    off = parse('OFF')
    candidate = parse('PASSIVE_V2R1')
    compared_keys = list(EXACT_KEYS) + [
        'coverage_admissions', 'coverage_re_admissions',
        'coverage_unique_uid']
    exact = {
        key: off['values'][key] == candidate['values'][key]
        for key in compared_keys
    }
    correctness = {
        'off_terminal': off['terminal'],
        'candidate_terminal': candidate['terminal'],
        'off_quiescent': off['quiescent'] == 1,
        'candidate_quiescent': candidate['quiescent'] == 1,
        'off_duplicate_application_zero': off['duplicate_application'] == 0,
        'candidate_duplicate_application_zero':
            candidate['duplicate_application'] == 0,
        'candidate_forward_hits_zero': candidate['forward_hits'] == 0,
        'candidate_live_entries_zero': candidate['live_entries'] == 0,
        'candidate_detached_waiters_zero': candidate['detached_waiters'] == 0,
        'off_coverage_complete': (
            off['coverage']['untranslated'] == 0 and
            off['coverage']['unobserved'] == 0 and
            off['coverage']['translated_unique'] ==
            off['coverage']['unique']),
        'candidate_coverage_complete': (
            candidate['coverage']['untranslated'] == 0 and
            candidate['coverage']['unobserved'] == 0 and
            candidate['coverage']['translated_unique'] ==
            candidate['coverage']['unique']),
    }
    passed = all(exact.values()) and all(correctness.values())
    receipt = {
        'stage': STAGE,
        'status': 'PASS' if passed else 'FAIL',
        'directed_case': 'ZERO_M1_REAL_SIMULATOR_FULL_PIPELINE',
        'off': off,
        'candidate': candidate,
        'exact': exact,
        'correctness': correctness,
    }
    GATE = RUNTIME / 'full_pipeline_gate.json'
    GATE.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
