#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PREL1_TRANSLATION_REQUEST_COALESCING_DISCOVERY_AND_PROTOTYPE_V1'
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/zero_duplication_gate')
KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_l1_tlb_lookup_launches', 'vm_l2_tlb_lookup_launches',
    'vm_translation_mshr_allocations', 'vm_translation_mshr_merges',
    'vm_translation_walk_starts', 'vm_pte_requests',
    'vm_functional_completed', 'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(text: str, key: str) -> int:
    rows = re.findall(rf'^{re.escape(key)}\s*=\s*(\d+)\s*$', text, re.M)
    if not rows:
        raise RuntimeError(f'missing {key}')
    return int(rows[-1])


def compact(text: str, key: str) -> int:
    rows = re.findall(rf'^{re.escape(key)}=(\d+)\s*$', text, re.M)
    if not rows:
        raise RuntimeError(f'missing {key}')
    return int(rows[-1])


def coverage(text: str) -> dict[str, int]:
    rows = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) '
        r'untranslated=(\d+) unobserved=(\d+) unique=(\d+) '
        r'translated_unique=(\d+) untranslated_unique=(\d+)', text)
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, rows[-1])))


def parse(label: str) -> dict[str, object]:
    directory = DURABLE / label
    text = (directory / 'run.log').read_text(errors='replace')
    values = {key: number(text, key) for key in KEYS}
    values['icnt_total_pkts_simt_to_mem'] = compact(
        text, 'icnt_total_pkts_simt_to_mem')
    cov = coverage(text)
    values['coverage_admissions'] = cov['admissions']
    values['coverage_unique'] = cov['unique']
    values['coverage_re_admissions'] = cov['admissions'] - cov['unique']
    return {
        'values': values, 'coverage': cov,
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
        'text': text,
    }


def main() -> int:
    off, candidate = parse('OFF'), parse('COALESCER')
    exact = {key: off['values'][key] == candidate['values'][key]
             for key in off['values']}
    ctext = candidate['text']
    candidate_state = {
        'followers_zero': number(ctext, 'awma_prel1_coalescer_followers') == 0,
        'follower_applications_zero': number(
            ctext, 'awma_prel1_coalescer_follower_applications') == 0,
        'entry_full_zero': number(
            ctext, 'awma_prel1_coalescer_entry_full_fallbacks') == 0,
        'waiter_full_zero': number(
            ctext, 'awma_prel1_coalescer_waiter_full_fallbacks') == 0,
        'followers_final_zero': number(
            ctext, 'awma_prel1_coalescer_followers_final') == 0,
        'waiters_final_zero': number(
            ctext, 'awma_prel1_coalescer_waiters_final') == 0,
        'entries_final_zero': number(
            ctext, 'awma_prel1_coalescer_live_entries_final') == 0,
        'pending_compare_zero': number(
            ctext, 'awma_prel1_coalescer_pending_compares_final') == 0,
        'coalescer_quiescent': number(
            ctext, 'awma_prel1_coalescer_quiescent') == 1,
        'off_terminal': off['terminal'],
        'candidate_terminal': candidate['terminal'],
        'off_coverage_complete': (
            off['coverage']['untranslated'] == 0 and
            off['coverage']['unobserved'] == 0),
        'candidate_coverage_complete': (
            candidate['coverage']['untranslated'] == 0 and
            candidate['coverage']['unobserved'] == 0),
    }
    passed = all(exact.values()) and all(candidate_state.values())
    receipt = {
        'stage': STAGE, 'phase': 'ZERO_DUPLICATION_FULL_PIPELINE',
        'status': 'PASS' if passed else 'FAIL', 'exact': exact,
        'candidate_state': candidate_state,
        'off': {key: value for key, value in off.items() if key != 'text'},
        'candidate': {key: value for key, value in candidate.items()
                      if key != 'text'},
    }
    (RUNTIME / 'zero_duplication_gate.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
