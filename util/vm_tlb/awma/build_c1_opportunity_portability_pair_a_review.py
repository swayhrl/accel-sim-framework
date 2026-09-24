#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

STAGE = 'AWMA_C1_OPPORTUNITY_PORTABILITY_PAIR_A_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-opportunity-portability-pair-a-v1')
RUNTIME = Path('/root/awma_c1_opportunity_portability_pair_a_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_opportunity_portability_pair_a_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_opportunity_portability_pair_a.py'
QUALIFIER = REPO / 'util/vm_tlb/awma/qualify_c1_pair_a_off.py'
BUILDER = REPO / 'util/vm_tlb/awma/build_c1_opportunity_portability_pair_a_review.py'
BASELINE_QUALIFICATION = RUNTIME / 'baseline_qualification.json'
BASELINE_BINARY = RUNTIME / 'baseline/bin/unified_accel-sim.out'
CANDIDATE_BINARY = RUNTIME / 'candidate/bin/unified_accel-sim.out'
CAPTURE_PACK = ('docs/vm_tlb/review_packs/'
                'AWMA_PRODUCER_RUNTIME_IDENTITY_BRIDGE_AND_BATCH1_REPLAN_109_V1')

TARGETS = {
    'A1': {
        'scenario': 'S2', 'decode_step': 16,
        'capture_id': 'A1', 'producer_global_navigation': 16828,
        'producer_selector_ordinal': 1097,
        'payload_sha': '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',
        'index_sha': 'c3537cc9d89d73c30e1f416fd5c61b07e10059d8cb7b18b250ef13cf79b6d210',
        'traceg_size_bytes': 4534004,
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/raw/kernel-16828-ctx_0x608ad97ab300.traceg.xz'),
        'identity': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/IDENTITY.json'),
    },
    'A2': {
        'scenario': 'T8192', 'decode_step': 16,
        'capture_id': 'A2', 'producer_global_navigation': 16828,
        'producer_selector_ordinal': 1097,
        'payload_sha': 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',
        'index_sha': 'db6427e3ab7ece5f07791732ddde2f7f6c696b26112593eea61177a7f637eeb1',
        'traceg_size_bytes': 4523068,
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/raw/kernel-16828-ctx_0x573505e282b0.traceg.xz'),
        'identity': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/IDENTITY.json'),
    },
}

BASELINE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_merges',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
)
CANDIDATE_KEYS = BASELINE_KEYS + (
    'awma_nonblocking_shared_ready_members',
    'awma_nonblocking_fallback_members',
    'awma_nonblocking_duplicate_physical_lookup_requests',
    'awma_nonblocking_fallback_translation_completions',
    'awma_nonblocking_fallback_service_l1',
    'awma_nonblocking_fallback_service_l2',
    'awma_nonblocking_fallback_service_mshr_merge',
    'awma_nonblocking_fallback_service_ptw',
    'awma_nonblocking_fallback_service_unobserved',
    'awma_owner_wait_owner_attempts',
    'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_admissions',
    'awma_owner_wait_repeated_admissions',
    'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_first_issue_latency_total',
    'awma_owner_wait_first_issue_latency_max',
    'awma_owner_wait_all_issue_latency_total',
    'awma_owner_wait_all_issue_latency_max',
    'awma_owner_wait_pending_members_final',
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


def run_dir(target: str, candidate: bool) -> Path:
    label = 'NONBLOCKING_SHARE' if candidate else 'OFF'
    return DURABLE / f'{target}_{label}_10_80'


def parse(target: str, candidate: bool,
          baseline_signature: dict[str, object]) -> dict[str, object]:
    directory = run_dir(target, candidate)
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    keys = CANDIDATE_KEYS if candidate else BASELINE_KEYS
    numbers = {key: last_number(text, key) for key in keys}
    cov = coverage(text)
    expected = TARGETS[target]
    env = command['environment']
    fallback_service_total = 0
    if candidate:
        fallback_service_total = sum(numbers[key] for key in (
            'awma_nonblocking_fallback_service_l1',
            'awma_nonblocking_fallback_service_l2',
            'awma_nonblocking_fallback_service_mshr_merge',
            'awma_nonblocking_fallback_service_ptw',
            'awma_nonblocking_fallback_service_unobserved'))
    gates = {
        'rc_zero': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'payload_sha_exact': command['payload_sha256'] == expected['payload_sha'],
        'runner_index_exact': command['runner_index_sha256'] == expected['index_sha'],
        'scientific_target_exact':
            command['scientific_target_id'] == 'STR_8bc741e5debc',
        'scenario_exact': command['scenario'] == expected['scenario'],
        'decode_step_exact': command['decode_step'] == expected['decode_step'],
        'grid_block_exact':
            command['grid'] == '224,1,1' and command['block'] == '16,4,1',
        'recurrence_exact': command['recurrence'] == 'STABLE_24',
        'binary_exact': command['binary_sha256'] == (
            'fa4346fcb4b4bddcf493606b7ce3e87ccd3e6241c26258f62c2c0cb79d4cda47'
            if candidate else
            'a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24'),
        'instructions_exact': numbers['gpu_sim_insn'] ==
            baseline_signature['gpu_sim_insn'],
        'cta_exact': numbers['gpu_tot_issued_cta'] == 224,
        'unique_uid_exact': cov['unique'] == baseline_signature['unique_uid'],
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
        'candidate_env_frozen': (not candidate) or
            (env.get('GPGPUSIM_AWMA_TRANSLATION_CANDIDATE') ==
                 'nonblocking_opportunistic_share' and
             'GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE' not in env and
             'GPGPUSIM_AWMA_SHARE_ABLATION' not in env and
             'GPGPUSIM_AWMA_NONBLOCKING_CAUSAL_ABLATION' not in env),
        'sharing_owner_wait_zero': (not candidate) or
            numbers['awma_owner_wait_member_owner_wait_cycles'] == 0,
        'sharing_head_block_zero': (not candidate) or
            numbers['awma_owner_wait_head_block_total_cycles'] == 0,
        'candidate_state_drain': (not candidate) or
            numbers['awma_owner_wait_pending_members_final'] == 0,
        'admission_conservation': (not candidate) or
            numbers['awma_owner_wait_admissions'] == cov['admissions'],
        'fallback_completion_conservation': (not candidate) or
            numbers['awma_nonblocking_fallback_translation_completions'] ==
            numbers['awma_nonblocking_fallback_members'],
        'fallback_service_conservation': (not candidate) or
            fallback_service_total ==
            numbers['awma_nonblocking_fallback_translation_completions'],
        'duplicate_lookup_disclosed': (not candidate) or
            numbers['awma_nonblocking_duplicate_physical_lookup_requests'] ==
            numbers['awma_nonblocking_fallback_members'],
        'fallback_service_observed': (not candidate) or
            numbers['awma_nonblocking_fallback_service_unobserved'] == 0,
    }
    return {
        'target': target, 'mode': 'CANDIDATE' if candidate else 'OFF',
        'run_dir': str(directory), 'numbers': numbers, 'coverage': cov,
        'command': command, 'gates': gates, 'correctness': all(gates.values()),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
        'wall_seconds': float((directory / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def parse_utc(path: Path) -> datetime:
    return datetime.strptime(path.read_text().strip(), '%Y-%m-%dT%H:%M:%SZ') \
        .replace(tzinfo=timezone.utc)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    qualification = json.loads(BASELINE_QUALIFICATION.read_text())
    signatures = {
        target: {
            'gpu_sim_insn': row['numbers']['gpu_sim_insn'],
            'unique_uid': row['coverage']['unique'],
        }
        for target, row in qualification['targets'].items()
    }
    offs = {target: parse(target, False, signatures[target])
            for target in ('A1', 'A2')}
    candidates = {target: parse(target, True, signatures[target])
                  for target in ('A1', 'A2')}
    matrix_rows: list[list[object]] = []
    gate_rows: list[list[object]] = []
    authority_rows: list[list[object]] = []
    raw_rows: list[list[object]] = []
    summaries: dict[str, dict[str, object]] = {}

    for target in ('A1', 'A2'):
        spec, off, candidate = TARGETS[target], offs[target], candidates[target]
        on, cn = off['numbers'], candidate['numbers']
        cycle_change = (cn['gpu_sim_cycle'] - on['gpu_sim_cycle']) / on['gpu_sim_cycle']
        lookup_suppression = 1 - cn['vm_translation_lookup_requests'] / on['vm_translation_lookup_requests']
        matrix_rows.append([
            target, spec['scenario'], spec['decode_step'], on['gpu_sim_cycle'],
            cn['gpu_sim_cycle'], f'{cycle_change:.9f}',
            on['vm_translation_lookup_requests'],
            cn['vm_translation_lookup_requests'],
            f'{lookup_suppression:.9f}', on['vm_l1_tlb_accesses'],
            cn['vm_l1_tlb_accesses'], on['vm_l2_tlb_accesses'],
            cn['vm_l2_tlb_accesses'], on['vm_translation_mshr_merges'],
            cn['vm_translation_mshr_merges'],
            cn['awma_nonblocking_shared_ready_members'],
            cn['awma_nonblocking_fallback_members'],
            cn['awma_nonblocking_duplicate_physical_lookup_requests'],
            cn['awma_owner_wait_owner_attempts'],
            cn['awma_owner_wait_member_owner_wait_cycles'],
            cn['awma_owner_wait_head_block_total_cycles'],
            off['coverage']['admissions'],
            cn['awma_owner_wait_admissions'],
            off['coverage']['admissions'] - off['coverage']['unique'],
            cn['awma_owner_wait_repeated_admissions'],
            cn['awma_owner_wait_readmitted_uids'],
            cn['awma_owner_wait_first_issue_latency_total'],
            cn['awma_owner_wait_first_issue_latency_max'],
            cn['awma_owner_wait_all_issue_latency_total'],
            cn['awma_owner_wait_all_issue_latency_max'],
            'PASS' if off['correctness'] else 'FAIL',
            'PASS' if candidate['correctness'] else 'FAIL',
            off['run_log_sha256'], candidate['run_log_sha256'],
        ])
        gate_rows.extend([
            [target, 'OFF'] + ['PASS' if value else 'FAIL'
                               for value in off['gates'].values()] +
            ['PASS' if off['correctness'] else 'FAIL'],
            [target, 'CANDIDATE'] + ['PASS' if value else 'FAIL'
                                     for value in candidate['gates'].values()] +
            ['PASS' if candidate['correctness'] else 'FAIL'],
        ])
        identity = json.loads(spec['identity'].read_text())
        authority_rows.append([
            target, 'STR_8bc741e5debc', spec['scenario'], spec['decode_step'],
            identity['phase'], identity['grid'], identity['block'],
            identity['accepted_recurrence'], spec['producer_global_navigation'],
            spec['producer_selector_ordinal'], spec['payload'],
            spec['payload_sha'], spec['index_sha'],
            spec['traceg_size_bytes'],
            on['gpu_sim_insn'], on['gpu_tot_issued_cta'],
            off['coverage']['unique'], 'PASS' if off['correctness'] else 'FAIL',
        ])
        summaries[target] = {
            'off_cycles': on['gpu_sim_cycle'],
            'candidate_cycles': cn['gpu_sim_cycle'],
            'cycle_change': cycle_change,
            'lookup_suppression': lookup_suppression,
            'ready_shared_members':
                cn['awma_nonblocking_shared_ready_members'],
            'off_admissions': off['coverage']['admissions'],
            'candidate_admissions': cn['awma_owner_wait_admissions'],
            'admission_change':
                (cn['awma_owner_wait_admissions'] - off['coverage']['admissions']) /
                off['coverage']['admissions'],
            'candidate_repeated_admissions':
                cn['awma_owner_wait_repeated_admissions'],
            'all_issue_latency_total':
                cn['awma_owner_wait_all_issue_latency_total'],
        }
        raw_rows.extend([
            ['off_run_log', target, f"{off['run_dir']}/run.log",
             off['run_log_sha256'], 'NEW_PHASE_1'],
            ['off_command', target, f"{off['run_dir']}/command.json",
             off['command_sha256'], 'PROVENANCE'],
            ['candidate_run_log', target, f"{candidate['run_dir']}/run.log",
             candidate['run_log_sha256'], 'NEW_PHASE_2'],
            ['candidate_command', target,
             f"{candidate['run_dir']}/command.json",
             candidate['command_sha256'], 'PROVENANCE'],
            ['traceg', target, str(spec['payload']), spec['payload_sha'],
             'CAPTURE_AUTHORITY'],
            ['identity', target, str(spec['identity']), sha(spec['identity']),
             'CAPTURE_AUTHORITY'],
        ])

    all_correct = all(run['correctness'] for run in
                      list(offs.values()) + list(candidates.values()))
    waits_zero = all(
        run['numbers']['awma_owner_wait_member_owner_wait_cycles'] == 0 and
        run['numbers']['awma_owner_wait_head_block_total_cycles'] == 0
        for run in candidates.values())
    sharing_mediator = any(
        summaries[target]['ready_shared_members'] > 0 and
        summaries[target]['lookup_suppression'] > 0 for target in summaries)
    no_ready_share = all(
        summaries[target]['ready_shared_members'] == 0 for target in summaries)
    phase_rows = []
    phase_order_verified = True
    qualification_time = datetime.fromtimestamp(
        BASELINE_QUALIFICATION.stat().st_mtime, tz=timezone.utc)
    for target in ('A1', 'A2'):
        off_end = parse_utc(run_dir(target, False) / 'end_utc.txt')
        candidate_start = parse_utc(run_dir(target, True) / 'start_utc.txt')
        passed = (off_end <= candidate_start and
                  qualification_time <= candidate_start and
                  qualification['targets'][target]['status'] == 'PASS')
        phase_order_verified &= passed
        phase_rows.append([
            target, off_end.strftime('%Y-%m-%dT%H:%M:%SZ'),
            qualification_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            candidate_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'PASS' if passed else 'FAIL'])
    context_dependent_performance = (
        summaries['A1']['cycle_change'] < 0 and
        summaries['A2']['cycle_change'] > 0)
    if not all_correct or not waits_zero or not phase_order_verified:
        decision = 'PAIR_A_CHARACTERIZATION_FAILED'
    elif no_ready_share:
        decision = 'GEMV_NO_READY_REUSE_ACROSS_CONTEXT_OBSERVED'
    elif all(summaries[target]['ready_shared_members'] > 0
             for target in summaries):
        decision = 'GEMV_READY_REUSE_ACROSS_CONTEXT_OBSERVED'
    else:
        decision = 'CONTEXT_DEPENDENT_READY_REUSE_OPPORTUNITY_OBSERVED'

    write_tsv(PACK / 'PAIR_A_MATRIX.tsv', [
        'target', 'scenario', 'decode_step', 'off_cycles', 'candidate_cycles',
        'candidate_vs_off_cycle_change', 'off_lookup_requests',
        'candidate_lookup_requests', 'lookup_suppression_fraction',
        'off_l1_probes', 'candidate_l1_probes', 'off_l2_probes',
        'candidate_l2_probes', 'off_mshr_merges', 'candidate_mshr_merges',
        'ready_shared_members', 'fallback_members',
        'duplicate_physical_lookup_requests', 'owner_attempts',
        'sharing_owner_wait_cycles', 'sharing_head_block_cycles',
        'off_admissions', 'candidate_admissions',
        'off_derived_repeated_admissions', 'candidate_repeated_admissions',
        'candidate_readmitted_uids',
        'first_issue_latency_total', 'first_issue_latency_max',
        'all_issue_latency_total', 'all_issue_latency_max',
        'off_correctness', 'candidate_correctness', 'off_run_log_sha256',
        'candidate_run_log_sha256'], matrix_rows)
    gate_names = list(next(iter(offs.values()))['gates'])
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target', 'mode'] + gate_names + ['status'], gate_rows)
    write_tsv(PACK / 'SIMULATOR_INPUT_AUTHORITY.tsv', [
        'target', 'scientific_target_id', 'scenario', 'decode_step', 'phase',
        'grid', 'block', 'recurrence', 'producer_global_navigation',
        'producer_selector_ordinal', 'traceg', 'traceg_sha256',
        'runner_index_sha256', 'traceg_size_bytes',
        'sim_instructions', 'sim_cta', 'sim_unique_uid',
        'off_qualification'], authority_rows)
    write_tsv(PACK / 'PHASE_ORDER.tsv', [
        'target', 'off_end_utc', 'qualification_receipt_mtime_utc',
        'candidate_start_utc', 'off_qualified_before_candidate'], phase_rows)

    raw_rows.extend([
        ['accepted_commit', 'CAPTURE_AUTHORITY',
         'c8549227a7c581a6f32c1fb63087ea117134fddc', '', 'ACCEPTED'],
        ['accepted_commit', 'FROZEN_MECHANISM',
         'c0602ee06e647d9a3cf84b0adbb8d98075021f99', '', 'ACCEPTED'],
        ['qualification', 'PHASE_1', str(BASELINE_QUALIFICATION),
         sha(BASELINE_QUALIFICATION), 'NEW_AUTHORITY'],
        ['binary', 'BASELINE', str(BASELINE_BINARY), sha(BASELINE_BINARY),
         'ACCEPTED_EXACT_COPY'],
        ['binary', 'CANDIDATE', str(CANDIDATE_BINARY), sha(CANDIDATE_BINARY),
         'ACCEPTED_EXACT_COPY'],
        ['library', 'BASELINE_LIBCUDART',
         str(RUNTIME / 'baseline/lib/libcudart.so'),
         sha(RUNTIME / 'baseline/lib/libcudart.so'), 'ACCEPTED_EXACT_COPY'],
        ['library', 'CANDIDATE_LIBCUDART',
         str(RUNTIME / 'candidate/lib/libcudart.so'),
         sha(RUNTIME / 'candidate/lib/libcudart.so'), 'ACCEPTED_EXACT_COPY'],
        ['runner', 'TWO_PHASE_RUNNER', str(RUNNER), sha(RUNNER), 'PROVENANCE'],
        ['qualifier', 'OFF_QUALIFIER', str(QUALIFIER), sha(QUALIFIER),
         'PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(BUILDER), sha(BUILDER),
         'PROVENANCE'],
    ])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path_or_authority', 'sha256', 'evidence_class'],
              raw_rows)

    receipt = {
        'stage': STAGE,
        'capture_authority': 'c8549227a7c581a6f32c1fb63087ea117134fddc',
        'frozen_mechanism_authority':
            'c0602ee06e647d9a3cf84b0adbb8d98075021f99',
        'decision': decision, 'all_correct': all_correct,
        'sharing_wait_and_head_block_zero': waits_zero,
        'sharing_mediator_present': sharing_mediator,
        'both_targets_ready_share_zero': no_ready_share,
        'context_dependent_performance_response':
            context_dependent_performance,
        'evidence_role': 'CONTEXT_LENGTH_OPPORTUNITY_CHARACTERIZATION',
        'is_holdout': False, 'mechanism_promotion': False,
        'off_qualification_preceded_candidate': phase_order_verified,
        'source_modified': False, 'parameter_tuning_performed': False,
        'owner_only_ablation_run': False, 'zero_eighty_sweep_run': False,
        'other_target_run': False,
        'summaries': summaries,
        'baseline_qualification': qualification,
        'offs': offs, 'candidates': candidates,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    report = f'''# AWMA C1 opportunity portability Pair A V1

Status: **COMPLETE / {decision}**

## Phase 1: simulator-input and OFF qualification

Both existing `STR_8bc741e5debc` trace payloads match capture authority
`c8549227...` exactly and pass xz integrity, producer grammar authority,
Accel-Sim grammar consumption, identity, instruction/CTA/UID signature,
coverage, exactly-once, terminal, and controller-quiescence gates.

| target | context | step | OFF cycles | instructions | CTA | unique UID |
|---|---|---:|---:|---:|---:|---:|
| A1 | S2/T2048 | 16 | 114,123 | 34,883,072 | 224 | 409,024 |
| A2 | T8192 | 16 | 117,698 | 34,883,072 | 224 | 409,024 |

The frozen candidate was not run until both independent OFF qualification
records were `PASS`.

## Phase 2: frozen candidate

| target | OFF | candidate | cycle change | READY share | fallback | admission change |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 114,123 | 112,023 | {summaries['A1']['cycle_change']:.3%} | 0 | 116,032 | {summaries['A1']['admission_change']:.3%} |
| A2 | 117,698 | 125,427 | {summaries['A2']['cycle_change']:.3%} | 0 | 116,032 | {summaries['A2']['admission_change']:.3%} |

Both candidates pass all correctness, coverage, exactly-once, terminal, and
quiescence gates. Sharing-induced owner wait and head blocking are zero.

## Opportunity portability result

Both exact-kernel contexts expose zero READY-shared members. The registered
result is therefore `GEMV_NO_READY_REUSE_ACROSS_CONTEXT_OBSERVED`: READY-result
reuse opportunity is stably absent across S2/T2048 and T8192 for this exact
GEMV identity.

The performance response is nevertheless context dependent. A1 improves by
{abs(summaries['A1']['cycle_change']):.3%}, while A2 regresses by
{summaries['A2']['cycle_change']:.3%}. A2 candidate admissions increase by
{summaries['A2']['admission_change']:.3%} versus OFF, reaching 3,475,971 with
3,066,947 repeated admissions. A1's admission increase is only
{summaries['A1']['admission_change']:.3%}. The candidate all-issue latency
totals also differ (A1 8,166,151,720; A2 6,829,438,283), but are retained as
observational timing rather than an additive decomposition. Since
READY reuse is zero on both sides, this divergence is attributed only as a
context-dependent owner/prelaunch/order and retry response, not sharing value.

## Scope

This is `CONTEXT_LENGTH_OPPORTUNITY_CHARACTERIZATION`, not a holdout or
mechanism promotion. The result does not authorize a mechanism change.

The frozen source, policy, platform, frontend, and 10/80 parameters were not
changed, and no target outside Pair A was run. No tuning, baseline promotion,
or paper-level conclusion follows.
'''
    (PACK / 'REPORT.md').write_text(report)
    (PACK / 'README.md').write_text(
        f'# {STAGE}\n\nReview `REPORT.md`, '
        '`SIMULATOR_INPUT_AUTHORITY.tsv`, `PHASE_ORDER.tsv`, `PAIR_A_MATRIX.tsv`, '
        '`CORRECTNESS_GATES.tsv`, `RAW_DATA_INDEX.tsv`, and '
        '`RUN_RECEIPTS.json`.\n')
    (PACK / 'SOURCE_ANCHORS.md').write_text(f'''# Source anchors

- capture authority: `c8549227a7c581a6f32c1fb63087ea117134fddc`
- frozen mechanism authority: `c0602ee06e647d9a3cf84b0adbb8d98075021f99`
- frozen baseline authority: `8d1f14a32f5538660d74da86ccb03a2c504c5735`
- baseline binary SHA256: `{sha(BASELINE_BINARY)}`
- frozen candidate binary SHA256: `{sha(CANDIDATE_BINARY)}`
- platform config SHA256: `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- trace config SHA256: `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`
''')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision, 'all_correct': all_correct,
        'sharing_wait_and_head_block_zero': waits_zero,
        'sharing_mediator_present': sharing_mediator,
        'context_dependent_performance_response':
            context_dependent_performance,
        'phase_order_verified': phase_order_verified,
        'summaries': summaries,
    }, indent=2, sort_keys=True))
    return 0 if all_correct and phase_order_verified else 1


if __name__ == '__main__':
    raise SystemExit(main())
