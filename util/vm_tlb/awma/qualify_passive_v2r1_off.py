#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING_V2R1_BASELINE_PRESERVING'
RUNTIME = Path('/root/awma_passive_last_translation_result_forwarding_v2r1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_passive_last_translation_result_forwarding_v2r1/raw')
OUTPUT = RUNTIME / 'v2r1_off_authority.json'
EXPECTED = {
    'T0': (527896, 368696302, 224, 3090304, 3090304, 2458328),
    'T1': (665802, 369131520, 384, 7159808, 7160265, 7159808),
    'T2': (93079, 43357696, 1216, 411008, 715333, 279072),
    'SPLITKV': (73923, 36599648, 126, 233814, 233814, 233814),
    'COMBINE': (10480, 72908, 2, 1099, 1099, 1099),
    'A1': (114123, 34883072, 224, 409024, 2191027, 295936),
    'A2': (117698, 34883072, 224, 409024, 2375939, 295936),
}
NUMERIC = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
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


def last_compact_number(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)}=(\d+)$', text, re.M)
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
    memory_transactions = last_compact_number(
        text, 'icnt_total_pkts_simt_to_mem')
    cov = coverage(text)
    cycles, insn, cta, uid, admissions, memory = EXPECTED[target]
    env = command['environment']
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    gates = {
        'rc_zero': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode_none': not modes or modes[-1] == 'none',
        'passive_observer_off_env':
            env.get('GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER') == '0',
        'observer_output_absent': 'awma_passive_memo_enabled' not in text,
        'bottleneck_observer_level_one':
            env.get('GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY') == '1',
        'binary_exact': command['binary_sha256'] ==
            '84d4af7c3d4c94501261d62fff483b95625226508d80c1c3f5328cda3f527a83',
        'v2r1_accounting_enabled':
            env.get('GPGPUSIM_AWMA_V2R1_ACCOUNTING') == '1',
        'no_performance_candidate':
            'GPGPUSIM_AWMA_TRANSLATION_CANDIDATE' not in env,
        'no_threshold': 'GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE' not in env,
        'no_ready_application_v2': 'GPGPUSIM_READY_APPLICATION_V2' not in env,
        'cycles_exact': numbers['gpu_sim_cycle'] == cycles,
        'instructions_exact': numbers['gpu_sim_insn'] == insn,
        'cta_exact': numbers['gpu_tot_issued_cta'] == cta,
        'unique_uid_exact': cov['unique'] == uid,
        'coverage_admissions_exact': cov['admissions'] == admissions,
        'translated_unique_exact': cov['translated_unique'] == uid,
        'untranslated_zero': cov['untranslated'] == 0,
        'unobserved_zero': cov['unobserved'] == 0,
        'duplicate_application_zero':
            numbers['vm_ready_application_duplicate_attempts'] == 0,
        'memory_transactions_exact': memory_transactions == memory,
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
        'memory_transactions': memory_transactions,
        'run_dir': str(directory),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
    }


def main() -> int:
    targets = {target: qualify(target) for target in EXPECTED}
    receipt = {
        'stage': STAGE,
        'phase': 'OFF_AUTHORITY_CHECK',
        'source_freeze_commit': '47cde7d19393869ecae448bee76c3624f5907fb5',
        'observability_authority': 'b85d388abe98e5da70b749b52075c33fad7cede4',
        'targets': targets,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all(row['status'] == 'PASS' for row in targets.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
