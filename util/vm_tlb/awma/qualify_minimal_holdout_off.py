#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import lzma
import re
from pathlib import Path

STAGE = 'AWMA_PREL1_COALESCER_MINIMAL_INDEPENDENT_HOLDOUT_VALIDATION_V1'
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_minimal_independent_holdout_validation_v1/raw')
TRACE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/prel1_coalescer_independent_holdout_capture_20260925/primary_formal/raw/kernel-994-ctx_0x60474d7c4d80.traceg.xz')
TRACE_SHA = 'ed712fb618309fd4f08c5ccc284a807df8a78581df2880f76fc415fa8a3b9105'
BINARY_SHA = 'be4136f011255acbfc33b9c9cc5166f43450f7e7fa9dd589f4b3c9481a71b630'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(text: str, key: str) -> int:
    rows = re.findall(rf'^{re.escape(key)}\s*=\s*(\d+)\s*$', text, re.M)
    if not rows:
        raise RuntimeError(f'missing {key}')
    return int(rows[-1])


def coverage(text: str) -> dict[str, int]:
    rows = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) '
        r'untranslated=(\d+) unobserved=(\d+) unique=(\d+) '
        r'translated_unique=(\d+) untranslated_unique=(\d+)', text)
    if not rows:
        raise RuntimeError('missing coverage')
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, rows[-1])))


def trace_record_count() -> int:
    count = 0
    with lzma.open(TRACE, 'rt', errors='replace') as stream:
        for line in stream:
            if re.match(r'^[0-9a-fA-F]{4}\s', line):
                count += 1
    return count


def main() -> int:
    directory = DURABLE / 'OFF'
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    cov = coverage(text)
    values = {key: number(text, key) for key in (
        'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
        'vm_functional_completed', 'vm_ready_application_duplicate_attempts',
        'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
        'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
        'vm_translation_active_walks',
        'vm_translation_quiescent_invariants_hold')}
    records = trace_record_count()
    identity = command['trace_identity']
    gates = {
        'rc_zero': (directory / 'rc.txt').read_text().strip() == '0',
        'trace_sha_exact': sha(TRACE) == TRACE_SHA,
        'binary_sha_exact': command['binary_sha256'] == BINARY_SHA,
        'grammar_consumer_pass': (
            'GPGPU-Sim: *** simulation thread exiting ***' in text and
            'GPGPU-Sim: *** exit detected ***' in text),
        'target_kernel_id_exact': identity['kernel_id'] == 994,
        'target_family_exact': 'at::native::reduce_kernel' in identity['kernel_name'],
        'grid_exact': identity['grid'] == '1,1,1',
        'block_exact': identity['block'] == '128,1,1',
        'trace_instruction_records_exact': records == 710,
        'simulator_instructions_nonzero': values['gpu_sim_insn'] > 0,
        'cta_exact': values['gpu_tot_issued_cta'] == 1,
        'unique_uid_nonzero': cov['unique'] > 0,
        'translated_unique_exact': cov['translated_unique'] == cov['unique'],
        'untranslated_zero': cov['untranslated'] == 0,
        'unobserved_zero': cov['unobserved'] == 0,
        'functional_completion_exact': values['vm_functional_completed'] == cov['unique'],
        'duplicate_application_zero': values['vm_ready_application_duplicate_attempts'] == 0,
        'lookup_drain': (values['vm_translation_lookup_entries'] == 0 and
                         values['vm_translation_lookup_ready'] == 0),
        'controller_quiescence': (
            values['vm_translation_mshrs_entries'] == 0 and
            values['vm_translation_pwq_entries_active'] == 0 and
            values['vm_translation_active_walks'] == 0 and
            values['vm_translation_quiescent_invariants_hold'] == 1),
    }
    receipt = {
        'stage': STAGE, 'status': 'PASS' if all(gates.values()) else 'FAIL',
        'gates': gates, 'trace_instruction_records': records,
        'values': values, 'coverage': cov,
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
    }
    (directory / 'qualification.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
