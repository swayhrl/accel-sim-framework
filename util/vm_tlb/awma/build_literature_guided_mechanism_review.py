#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-174-literature-guided-mechanism-exploration-v1')
RUNTIME = Path('/root/awma_literature_guided_mechanism_exploration_v1_runtime')
DURABLE_ROOTS = (
    ('v0', Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw')),
    ('r1', Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw_r1')),
    ('r2', Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw_r2')),
)
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
RUNNER = REPO / 'util/vm_tlb/awma/run_literature_guided_mechanism_exploration.py'

EXPECTED = {
    'T0': (368696302, 224, 3090304),
    'T1': (369131520, 384, 7159808),
    'T2': (43357696, 1216, 411008),
    'A1_CONTROL': (2795248, 2, 51250),
}
ACCEPTED_V1 = {
    ('T0', '10/80'): 527896, ('T1', '10/80'): 665802,
    ('T2', '10/80'): 93079, ('T0', '0/80'): 496170,
}
NUMERIC_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_l2_tlb_misses', 'vm_l2_tlb_evictions',
    'vm_translation_walk_starts', 'vm_translation_walk_completions',
    'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'vm_awma_refill_history_inserts', 'vm_awma_refill_history_resets',
    'vm_awma_refill_history_hits', 'vm_awma_refill_pending_allocations',
    'vm_awma_refill_pending_merges', 'vm_awma_refill_pending_drops',
    'vm_awma_refill_protected_refills', 'vm_awma_refill_protected_hits',
    'vm_awma_refill_protected_victim_skips',
    'vm_awma_refill_all_protected_lru_fallbacks',
    'vm_awma_refill_timer_wrap_resets', 'vm_awma_refill_pending_final',
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


def parse_run(run_dir: Path, revision: str) -> dict[str, object]:
    command = json.loads((run_dir / 'command.json').read_text())
    text = (run_dir / 'run.log').read_text(errors='replace')
    target = str(command['target'])
    expected_insn, expected_cta, expected_uid = EXPECTED[target]
    numbers = {key: last_number(text, key) for key in NUMERIC_KEYS}
    cov = coverage(text)
    mode_values = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    mode = mode_values[-1] if mode_values else 'MISSING'
    gates = {
        'rc': (run_dir / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'mode': mode == command.get('mechanism_mode', command['candidate']),
        'instructions': numbers['gpu_sim_insn'] == expected_insn,
        'cta': numbers['gpu_tot_issued_cta'] == expected_cta,
        'unique_uid': cov['unique'] == expected_uid,
        'translated_unique': cov['translated_unique'] == expected_uid,
        'untranslated_zero': cov['untranslated'] == 0,
        'unobserved_zero': cov['unobserved'] == 0,
        'duplicates_zero': numbers['vm_ready_application_duplicate_attempts'] == 0,
        'lookup_drain': (numbers['vm_translation_lookup_entries'] == 0 and
                         numbers['vm_translation_lookup_ready'] == 0),
        'controller_drain': (
            numbers['vm_translation_mshrs_entries'] == 0 and
            numbers['vm_translation_pwq_entries_active'] == 0 and
            numbers['vm_translation_active_walks'] == 0 and
            numbers['vm_translation_quiescent_invariants_hold'] == 1),
        'candidate_drain': numbers['vm_awma_refill_pending_final'] == 0,
    }
    pre_fix = revision == 'v0' and command['candidate'] == 'same_page_share'
    status = 'PASS' if all(gates.values()) else 'FAIL'
    if pre_fix:
        status = ('PRE_FIX_OBSOLETE' if all(gates.values())
                  else 'PRE_FIX_INVALID_READY_LEAK')
    return {
        'target': target, 'candidate': str(command['candidate']),
        'revision': revision, 'pre_fix': pre_fix,
        'vm_config': str(command['vm_config']), 'run_dir': str(run_dir),
        'cycles': numbers['gpu_sim_cycle'], 'instructions': numbers['gpu_sim_insn'],
        'cta': numbers['gpu_tot_issued_cta'], 'coverage': cov,
        'numbers': numbers, 'gates': gates,
        'status': status,
        'binary_sha256': str(command['binary_sha256']),
        'run_log_sha256': sha(run_dir / 'run.log'),
        'command_sha256': sha(run_dir / 'command.json'),
        'wall_seconds': float((run_dir / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    runs = []
    for revision, durable in DURABLE_ROOTS:
        if not durable.is_dir():
            continue
        for run_dir in sorted(durable.iterdir()):
            if ((run_dir / 'command.json').is_file() and
                    (run_dir / 'run.log').is_file() and
                    (run_dir / 'rc.txt').is_file()):
                runs.append(parse_run(run_dir, revision))
    baseline_cycles = {
        (str(run['target']), str(run['vm_config'])): int(run['cycles'])
        for run in runs if run['candidate'] == 'none'
    }
    matrix_rows = []
    gate_rows = []
    raw_rows = []
    for run in runs:
        target = str(run['target'])
        baseline = baseline_cycles.get((target, str(run['vm_config'])))
        speedup = '' if baseline is None else f"{(baseline / int(run['cycles']) - 1):.9f}"
        accepted = ACCEPTED_V1.get((target, str(run['vm_config'])))
        accepted_delta = '' if accepted is None else str(int(run['cycles']) - accepted)
        n = run['numbers']
        c = run['coverage']
        matrix_rows.append([
            target, run['candidate'], run['revision'], run['vm_config'],
            run['cycles'], speedup,
            accepted_delta, run['instructions'], run['cta'], c['admissions'],
            c['translated'], c['unique'], c['translated_unique'],
            c['untranslated'], c['unobserved'],
            n['vm_translation_lookup_requests'], n['vm_l1_tlb_accesses'],
            n['vm_l2_tlb_accesses'], n['vm_l2_tlb_misses'],
            n['vm_l2_tlb_evictions'], n['vm_translation_walk_starts'],
            n['vm_awma_same_page_share_owner_ready'],
            n['vm_awma_same_page_share_deliveries'],
            n['vm_awma_refill_history_hits'],
            n['vm_awma_refill_protected_refills'],
            n['vm_awma_refill_protected_hits'],
            n['vm_awma_refill_protected_victim_skips'],
            n['vm_awma_refill_all_protected_lru_fallbacks'],
            n['vm_awma_refill_pending_drops'],
            n['vm_awma_refill_pending_final'], run['run_log_sha256'],
            run['binary_sha256'], run['status'],
        ])
        gate_rows.append([target, run['candidate'], run['revision'],
                          run['vm_config']] +
                         ['PASS' if value else 'FAIL'
                          for value in run['gates'].values()] + [run['status']])
        raw_rows.append([
            'run_log',
            f"{target}:{run['candidate']}:{run['revision']}:{run['vm_config']}",
            f"{run['run_dir']}/run.log", run['run_log_sha256'],
            'PRE_FIX_OBSOLETE' if run['pre_fix'] else 'P1_DISCOVERY'])
        raw_rows.append([
            'command',
            f"{target}:{run['candidate']}:{run['revision']}:{run['vm_config']}",
            f"{run['run_dir']}/command.json", run['command_sha256'], 'P3_PROVENANCE'])
    write_tsv(PACK / 'EXPLORATION_MATRIX.tsv', [
        'target', 'candidate', 'revision', 'vm_config', 'cycles',
        'speedup_vs_local_off',
        'cycle_delta_vs_accepted_v1_same_vm_config', 'instructions', 'cta',
        'coverage_admissions', 'coverage_translated', 'unique_uid',
        'translated_unique_uid', 'untranslated', 'unobserved',
        'physical_lookup_requests', 'l1_tlb_accesses', 'l2_tlb_accesses',
        'l2_tlb_misses', 'l2_tlb_evictions', 'walk_starts',
        'share_owner_ready', 'share_deliveries', 'history_hits',
        'protected_refills', 'protected_hits', 'protected_victim_skips',
        'all_protected_lru_fallbacks', 'pending_drops', 'candidate_pending_final',
        'run_log_sha256', 'binary_sha256', 'status'], matrix_rows)
    gate_names = list(runs[0]['gates']) if runs else []
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target', 'candidate', 'revision', 'vm_config'] + gate_names +
              ['status'],
              gate_rows)
    raw_rows.extend([
        ['build_log', 'UNIFIED_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'P4_RUNTIME'],
        ['binary', 'CANDIDATE_UNIFIED', str(BINARY), sha(BINARY), 'P3_PROVENANCE'],
        ['build_log', 'UNIFIED_BUILD_R1',
         '/root/awma_literature_guided_mechanism_exploration_v1r1_runtime/unified_build.log',
         sha(Path('/root/awma_literature_guided_mechanism_exploration_v1r1_runtime/unified_build.log')),
         'P4_RUNTIME'],
        ['binary', 'CANDIDATE_UNIFIED_R1',
         '/root/awma_literature_guided_mechanism_exploration_v1r1_runtime/bin/unified_accel-sim.out',
         sha(Path('/root/awma_literature_guided_mechanism_exploration_v1r1_runtime/bin/unified_accel-sim.out')),
         'P3_PROVENANCE'],
        ['build_log', 'UNIFIED_BUILD_R2',
         '/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/unified_build.log',
         sha(Path('/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/unified_build.log')),
         'P4_RUNTIME'],
        ['binary', 'CANDIDATE_UNIFIED_R2',
         '/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/bin/unified_accel-sim.out',
         sha(Path('/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/bin/unified_accel-sim.out')),
         'P3_PROVENANCE'],
    ])
    core_patch = PACK / 'CANDIDATE_CORE.patch'
    test_source = REPO / 'util/vm_tlb/awma/awma_literature_mechanism_test.cc'
    raw_rows.extend([
        ['source_patch', 'FINAL_CANDIDATE_CORE', str(core_patch),
         sha(core_patch), 'P3_PROVENANCE'],
        ['test_source', 'DIRECTED_MECHANISM_TEST', str(test_source),
         sha(test_source), 'P3_PROVENANCE'],
        ['runner', 'EXPLORATION_RUNNER', str(RUNNER), sha(RUNNER),
         'P3_PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(Path(__file__)), sha(Path(__file__)),
         'P3_PROVENANCE'],
        ['test_log', 'CANDIDATE_CORE_PATCH_DRY_RUN',
         '/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/tests/candidate_core_patch_dry_run.log',
         sha(Path('/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/tests/candidate_core_patch_dry_run.log')),
         'VERIFIED_RUN'],
    ])
    for test in (
            'awma_literature_mechanism_test',
            'vm_m3_g3_4b_tlb_timing_test',
            'vm_m2_rf_pending_retry_test',
            'vm_c10b_runtime_validation_test'):
        for mode in ('none', 'refill_protect'):
            log = Path(
                '/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/tests') / f'{test}_{mode}.log'
            raw_rows.append(['test_log', f'{test}:{mode}', str(log), sha(log),
                             'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw_rows)
    required = {
        *(('v0', target, 'none', '10/80') for target in ('T0', 'T1', 'T2')),
        *(('v0', target, 'refill_protect', '10/80')
          for target in ('T0', 'T1', 'T2')),
        *(('r1', target, 'same_page_share', '10/80')
          for target in ('T0', 'T1', 'T2')),
        ('r2', 'T0', 'none', '0/80'),
        ('r2', 'T0', 'same_page_share', '0/80'),
        ('r2', 'T0', 'same_page_share_service_control', '10/80'),
    }
    passing = {
        (str(run['revision']), str(run['target']), str(run['candidate']),
         str(run['vm_config']))
        for run in runs if run['status'] == 'PASS'
    }
    first_screen_complete = required <= passing
    receipt = {
        'stage': 'AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1',
        'framework_start': '77b46eb432a308e3e971ea1a0daf98f321d0f7f3',
        'frozen_baseline_authority': '8d1f14a32f5538660d74da86ccb03a2c504c5735',
        'candidate_binary_sha256_v0': sha(BINARY),
        'candidate_binary_sha256_r1': sha(
            Path('/root/awma_literature_guided_mechanism_exploration_v1r1_runtime/bin/unified_accel-sim.out')),
        'candidate_binary_sha256_r2': sha(
            Path('/root/awma_literature_guided_mechanism_exploration_v1r2_runtime/bin/unified_accel-sim.out')),
        'runner_sha256': sha(RUNNER), 'runs': runs,
        'all_admitted_correct': bool(runs) and all(
            run['status'] == 'PASS' for run in runs if not run['pre_fix']),
        'first_screen_complete': first_screen_complete,
        'missing_first_screen_points': sorted(':'.join(point)
                                              for point in required - passing),
        'discovery_not_holdout': True, 'platform_tuning': False,
        'large_parameter_scan': False,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({'runs': len(runs),
                      'all_admitted_correct': receipt['all_admitted_correct'],
                      'first_screen_complete': first_screen_complete,
                      'binary_sha256_v0': receipt['candidate_binary_sha256_v0'],
                      'binary_sha256_r1': receipt['candidate_binary_sha256_r1']},
                     indent=2, sort_keys=True))
    return 0 if receipt['all_admitted_correct'] and first_screen_complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
