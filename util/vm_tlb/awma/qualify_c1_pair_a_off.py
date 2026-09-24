#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_C1_OPPORTUNITY_PORTABILITY_PAIR_A_V1'
RUNTIME = Path('/root/awma_c1_opportunity_portability_pair_a_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_opportunity_portability_pair_a_v1/raw')
OUTPUT = RUNTIME / 'baseline_qualification.json'
EXPECTED = {
    'A1': {
        'payload_sha': '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',
        'index_sha': 'c3537cc9d89d73c30e1f416fd5c61b07e10059d8cb7b18b250ef13cf79b6d210',
        'scenario': 'S2', 'decode_step': 16,
        'traceg_size_bytes': 4534004,
    },
    'A2': {
        'payload_sha': 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',
        'index_sha': 'db6427e3ab7ece5f07791732ddde2f7f6c696b26112593eea61177a7f637eeb1',
        'scenario': 'T8192', 'decode_step': 16,
        'traceg_size_bytes': 4523068,
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
        'trace_grammar_authority_pass': expected['traceg_size_bytes'] > 0,
        'traceg_size_exact':
            Path(command['payload']).stat().st_size ==
            expected['traceg_size_bytes'],
        'payload_sha_exact': command['payload_sha256'] == expected['payload_sha'],
        'runner_index_sha_exact':
            command['runner_index_sha256'] == expected['index_sha'],
        'scientific_target_exact':
            command['scientific_target_id'] == 'STR_8bc741e5debc',
        'scenario_exact': command['scenario'] == expected['scenario'],
        'decode_step_exact': command['decode_step'] == expected['decode_step'],
        'grid_exact': command['grid'] == '224,1,1',
        'block_exact': command['block'] == '16,4,1',
        'recurrence_exact': command['recurrence'] == 'STABLE_24',
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
        'traceg_size_bytes': expected['traceg_size_bytes'],
        'run_dir': str(directory),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
    }


def main() -> int:
    targets = {target: qualify(target) for target in ('A1', 'A2')}
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
