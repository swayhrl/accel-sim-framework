#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_C1_NONBLOCKING_CROSS_CONTEXT_HOLDOUT_V1'
RUNTIME = Path('/root/awma_c1_nonblocking_cross_context_holdout_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_nonblocking_cross_context_holdout_v1/raw')
OUTPUT = RUNTIME / 'baseline_qualification.json'
EXPECTED = {
    'H1': {
        'payload_sha': 'ba73fd184217b066682f93e09969a1a9e05dc1b119e5644ee62a0be530585e3c',
        'index_sha': 'd360aca779313f32465f11a8e8188059256e2066eb47bb222afade9fb8ab7a4c',
        'scenario': 'S2', 'decode_step': 16,
        'trace_grammar_instructions': 70908,
    },
    'H2': {
        'payload_sha': '4c601dcad31f1afdb931602671bbb54556ca12734f1ee853dc41a89779f44320',
        'index_sha': 'ed9a504b276f09fcf30cd1452a104dfdc07bb72bc94cf730035fbc222ab67af1',
        'scenario': 'D128', 'decode_step': 96,
        'trace_grammar_instructions': 70996,
    },
}
NUMERIC = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_merges',
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def last_number(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)} = (\d+)$', text, re.M)
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


def qualify(target: str) -> dict[str, object]:
    directory = DURABLE / f'{target}_OFF_10_80'
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in NUMERIC}
    cov = coverage(text)
    expected = EXPECTED[target]
    gates = {
        'trace_grammar_authority_pass':
            expected['trace_grammar_instructions'] > 0,
        'payload_sha_exact': command['payload_sha256'] == expected['payload_sha'],
        'runner_index_sha_exact':
            command['runner_index_sha256'] == expected['index_sha'],
        'scientific_target_exact':
            command['scientific_target_id'] == 'STR_8a5773a1d265',
        'scenario_exact': command['scenario'] == expected['scenario'],
        'decode_step_exact': command['decode_step'] == expected['decode_step'],
        'grid_exact': command['grid'] == '224,1,1',
        'block_exact': command['block'] == '32,4,1',
        'recurrence_exact': command['recurrence'] == 'STABLE_48',
        'baseline_binary_exact': command['binary_sha256'] ==
            'a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24',
        'rc_zero': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'instructions_nonzero': numbers['gpu_sim_insn'] > 0,
        'cta_exact': numbers['gpu_tot_issued_cta'] == 224,
        'unique_uid_nonzero': cov['unique'] > 0,
        'translated_unique_exact': cov['translated_unique'] == cov['unique'],
        'untranslated_zero': cov['untranslated'] == 0,
        'unobserved_zero': cov['unobserved'] == 0,
        'duplicate_application_zero':
            numbers['vm_ready_application_duplicate_attempts'] == 0,
        'lookup_drain': (numbers['vm_translation_lookup_entries'] == 0 and
                         numbers['vm_translation_lookup_ready'] == 0),
        'controller_quiescence': (
            numbers['vm_translation_mshrs_entries'] == 0 and
            numbers['vm_translation_pwq_entries_active'] == 0 and
            numbers['vm_translation_active_walks'] == 0 and
            numbers['vm_translation_quiescent_invariants_hold'] == 1),
    }
    return {
        'target': target, 'status': 'PASS' if all(gates.values()) else 'FAIL',
        'gates': gates, 'numbers': numbers, 'coverage': cov,
        'trace_grammar_instruction_count':
            expected['trace_grammar_instructions'],
        'run_dir': str(directory),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
    }


def main() -> int:
    targets = {target: qualify(target) for target in ('H1', 'H2')}
    receipt = {
        'stage': STAGE,
        'phase': 'PHASE_1_SIMULATOR_INPUT_BASELINE_QUALIFICATION',
        'capture_authority': 'c8549227a7c581a6f32c1fb63087ea117134fddc',
        'baseline_authority': '8d1f14a32f5538660d74da86ccb03a2c504c5735',
        'targets': targets,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all(row['status'] == 'PASS' for row in targets.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
