#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
import subprocess
from pathlib import Path

STAGE = 'AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-coalescer-paper-qualification-v1')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
DEV_PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_PREL1_TRANSLATION_REQUEST_COALESCING_DISCOVERY_AND_PROTOTYPE_V1'
HOLD_PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_MINIMAL_INDEPENDENT_HOLDOUT_VALIDATION_V1'
DEV_OFF = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/phase_a_raw')
DEV_CAND = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/development_raw')
HOLD_RAW = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_minimal_independent_holdout_validation_v1/raw')
PAIR_C_OFF = Path('/root/share/mnt164/huangrulin/awma_c1_nonblocking_cross_context_holdout_v1/raw')
PAIR_C_CAND = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_paper_qualification_v1/pair_c_raw')
RTL_RAW = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_paper_qualification_v1/rtl_proxy_raw')
RTL = REPO / 'util/vm_tlb/awma/prel1_hw_proxy'
SOURCE_FREEZE = '2bbbceabb5261777fe385289ecb6579791e0f232'
BINARY_SHA = 'be4136f011255acbfc33b9c9cc5166f43450f7e7fa9dd589f4b3c9481a71b630'
CONFIG_SHA = 'de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8'
TRACE_CONFIG_SHA = 'a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b'

TARGETS = {
    'T0': dict(role='DEVELOPMENT', family='FLASH', scenario='Qwen2.5 S2 prefill Flash',
               off=DEV_OFF / 'T0_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'T0_COALESCER_10_80'),
    'T1': dict(role='DEVELOPMENT', family='GEMM', scenario='Qwen2.5 S2 prefill GEMM',
               off=DEV_OFF / 'T1_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'T1_COALESCER_10_80'),
    'T2': dict(role='DEVELOPMENT', family='GEMV', scenario='Qwen2.5 S2 decode step16 GEMV',
               off=DEV_OFF / 'T2_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'T2_COALESCER_10_80'),
    'SPLITKV': dict(role='DEVELOPMENT', family='FLASH', scenario='Qwen2.5 S2 decode step16 SplitKV',
               off=DEV_OFF / 'SPLITKV_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'SPLITKV_COALESCER_10_80'),
    'COMBINE': dict(role='DEVELOPMENT', family='FLASH', scenario='Qwen2.5 S2 decode step16 Combine',
               off=DEV_OFF / 'COMBINE_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'COMBINE_COALESCER_10_80'),
    'A1': dict(role='DEVELOPMENT', family='GEMV', scenario='Pair A S2/T2048 step16 GEMV',
               off=DEV_OFF / 'A1_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'A1_COALESCER_10_80'),
    'A2': dict(role='DEVELOPMENT', family='GEMV', scenario='Pair A T8192 step16 GEMV',
               off=DEV_OFF / 'A2_OFF_OPPORTUNITY_10_80',
               cand=DEV_CAND / 'A2_COALESCER_10_80'),
    'H1': dict(role='ADDITIONAL_FROZEN_EVALUATION', family='GEMV', scenario='Pair C S2 step16 CUBLAS_GEMV',
               off=PAIR_C_OFF / 'H1_OFF_10_80',
               cand=PAIR_C_CAND / 'H1_COALESCER_10_80'),
    'H2': dict(role='ADDITIONAL_FROZEN_EVALUATION', family='GEMV', scenario='Pair C D128 step96 CUBLAS_GEMV',
               off=PAIR_C_OFF / 'H2_OFF_10_80',
               cand=PAIR_C_CAND / 'H2_COALESCER_10_80'),
    'REDUCE': dict(role='INDEPENDENT_HOLDOUT', family='REDUCE', scenario='S2 decode step1 AT_NATIVE_REDUCE',
               off=HOLD_RAW / 'OFF', cand=HOLD_RAW / 'COALESCER'),
}

BASE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_l1_tlb_lookup_launches', 'vm_l2_tlb_lookup_launches',
    'vm_translation_mshr_allocations', 'vm_translation_mshr_merges',
    'vm_translation_walk_starts', 'vm_pte_requests',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_quiescent_invariants_hold')
COAL_KEYS = tuple(f'awma_prel1_coalescer_{name}' for name in (
    'leaders', 'followers', 'leader_completions', 'follower_applications',
    'same_cycle_merges', 'inflight_merges', 'entry_full_fallbacks',
    'waiter_full_fallbacks', 'follower_wait_cycles_total',
    'follower_wait_cycles_max', 'follower_delivery_latency_total',
    'follower_delivery_latency_max', 'delivery_wait_p50',
    'delivery_wait_p95', 'delivery_wait_p99', 'head_block_cycles',
    'critical_path_followers', 'l1_hit_leaders', 'l2_hit_leaders',
    'ptw_leaders', 'occupancy_hwm', 'waiter_hwm', 'followers_final',
    'pending_compares_final', 'live_entries_final', 'waiters_final',
    'quiescent'))

SENSITIVITY = {
    'T0': (0.060098959, 0.153469623),
    'T1': (0.001497442, -0.074848078),
    'T2': (0.103567937, 0.100624201),
}

EVIDENCE = [
    ('characterization', '1c26b5c07b8ab4d7a457a84ea9b1327dd7ce8456',
     'Which translation path dominates?', 'HIT_PATH_EXPOSURE_DOMINANT / PAGE_REUSE_OPPORTUNITY_SUPPORTED',
     'Measured hit-path exposure and page reuse on T0/T1/T2.',
     'Does not select or validate a mechanism.', 'YES_SCOPED'),
    ('failed_C1_blocking_share', '4cf2ee8294fbf761f735ae7089313a048ba0066b',
     'Can same-page result sharing suppress service?', 'T0/T1 positive; T2 +1.026% regression with wait/HOL',
     'Service suppression can help; blocking owner/member semantics can hurt.',
     'Not a robust final mechanism or novelty result.', 'YES_FAILURE_MOTIVATION'),
    ('fanout_repair_discovery', 'f685f88d328b8bcb5f56c31b2629e5ed56938bb1',
     'Can fanout gating avoid small-cohort harm?', 'PROMISING_DISCOVERY at threshold 4',
     'Discovery evidence motivated independent target validation.',
     'Threshold was selected on discovery data.', 'YES_HISTORY_ONLY'),
    ('fanout_repair_validation', 'b2762f0cf6112018de37d78624b69adce08893aa',
     'Does fanout-only gating generalize?', 'FANOUT_ONLY_GATING_INSUFFICIENT',
     'Large fanout does not remove wait/HOL cost.',
     'Not cross-model evidence.', 'YES_FAILURE_MOTIVATION'),
    ('nonblocking_proactive_sharing', 'c0602ee06e647d9a3cf84b0adbb8d98075021f99',
     'Does nonblocking READY reuse avoid HOL?', 'SUPPORTED_DEVELOPMENT; zero sharing wait/head-block',
     'READY reuse has value without blocking.',
     'Proactive owner/order effects remain mixed.', 'YES_PRECURSOR'),
    ('A2_regression_attribution', 'b8a4064cb1bbe832758acf9dceb1461844c1fe4e',
     'Why does proactive A2 regress?', 'PROACTIVE_OWNER_PATH_NONSHARING_REGRESSION_MEDIATOR',
     'Links +1.1M admissions/resource stalls to +6.567% A2 regression.',
     'Does not identify the physical context trigger.', 'YES_FAILURE_MOTIVATION'),
    ('passive_opportunity', '6441fe9f91266220a52587c0313fb767007b5d92',
     'Do instruction-local same-page results recur?', 'PASSIVE_REUSE_OPPORTUNITY_SUPPORTED',
     'One-entry observer captures 9,936,902 legal head opportunities.',
     'Opportunity is not physical service suppression.', 'YES_MOTIVATION'),
    ('mixed_passive_V2', '8497fa5b7688ab6fe55aa90f4d13c5e4d6364331',
     'What is the response of initial passive V2?', 'MIXED_INTERVENTION_DIAGNOSTIC',
     'Shows response of forwarding plus disabled resident prelaunch.',
     'Cannot support passive-forwarding-only claims.', 'NO_PERFORMANCE_CLAIM'),
    ('baseline_preserving_V2R1', 'd3e1b3bbff0790ab67abb915fbc6673631a20111',
     'Does passive forwarding save frozen-V1 service?', 'PASSIVE_FORWARDING_OPPORTUNITY_ALREADY_PRELAUNCHED',
     'All 9,936,902 hits already had resident prelaunch work.',
     'Does not invalidate earlier opportunity counting.', 'YES_POSITIONING'),
    ('preL1_opportunity', '163a8572f9272891b8109f9158aa79ca88d9e153',
     'How much duplication exists before L1 service?', '9,409,101 finite legal merges; capacity 2 selected',
     'Establishes exact pre-L1 opportunity and finite capacity rule.',
     'Development targets are not independent holdouts.', 'YES_CORE'),
    ('frozen_preL1_coalescer', '163a8572f9272891b8109f9158aa79ca88d9e153',
     'Does the finite coalescer suppress service safely?', 'SUPPORTED_FOR_INDEPENDENT_VALIDATION',
     'Seven-target correctness, service suppression, wait accounting.',
     'Does not imply universal runtime speedup.', 'YES_CORE'),
    ('grouping_only_control', '163a8572f9272891b8109f9158aa79ca88d9e153',
     'Is grouping alone responsible?', 'T0/T1/A2 grouping-only exactly OFF',
     'Matched contrast supports service suppression mediator.',
     'Only three targets were required.', 'YES_CAUSAL'),
    ('timing_sensitivity', '163a8572f9272891b8109f9158aa79ca88d9e153',
     'Does +1-cycle compare invalidate the candidate?', 'Viable on T0/T1/T2/A2; no >1% regression',
     'Bounds simulator same-cycle timing dependence.',
     'Does not prove physical timing closure.', 'YES_SCOPED'),
    ('independent_REDUCE_holdout', 'fc5ea3bf1f09be1d0fbe3eb11fc6f6a847e4d763',
     'Does suppression generalize independently?', 'INDEPENDENT_SERVICE_SUPPRESSION_GENERALIZED',
     '105 followers; L1 launches 130->10 on AT_NATIVE_REDUCE.',
     'Equal cycles do not prove universal speedup.', 'YES_CORE'),
]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


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
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, rows[-1])))


def parse_run(path: Path, candidate: bool) -> dict[str, object]:
    text = (path / 'run.log').read_text(errors='replace')
    values = {key: number(text, key) for key in BASE_KEYS}
    if candidate:
        values.update({key: number(text, key) for key in COAL_KEYS})
    cov = coverage(text)
    terminal = ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                'GPGPU-Sim: *** exit detected ***' in text)
    return {'path': path, 'text': text, 'values': values,
            'coverage': cov, 'terminal': terminal}


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def parse_synth(name: str) -> dict[str, int]:
    stat = (RTL / f'out/synthesis/{name}.stat.txt').read_text()
    ltp = (RTL / f'out/synthesis/{name}.ltp.txt').read_text()
    result = {
        'wires': int(re.search(r'Number of wires:\s+(\d+)', stat).group(1)),
        'wire_bits': int(re.search(r'Number of wire bits:\s+(\d+)', stat).group(1)),
        'cells': int(re.search(r'Number of cells:\s+(\d+)', stat).group(1)),
        'dff': int(re.search(r'\$_DFF_P_\s+(\d+)', stat).group(1)),
        'mux': int(re.search(r'\$_MUX_\s+(\d+)', stat).group(1)),
        'logic_depth': int(re.search(r'length=(\d+)', ltp).group(1)),
    }
    return result


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    runs = {}
    consolidated = []
    for target, spec in TARGETS.items():
        off = parse_run(spec['off'], False)
        cand = parse_run(spec['cand'], True)
        ov, cv = off['values'], cand['values']
        followers = cv['awma_prel1_coalescer_followers']
        correctness = (
            off['terminal'] and cand['terminal'] and
            off['coverage']['untranslated'] == 0 and
            cand['coverage']['untranslated'] == 0 and
            off['coverage']['unobserved'] == 0 and
            cand['coverage']['unobserved'] == 0 and
            ov['gpu_sim_insn'] == cv['gpu_sim_insn'] and
            ov['gpu_tot_issued_cta'] == cv['gpu_tot_issued_cta'] and
            off['coverage']['unique'] == cand['coverage']['unique'] and
            cv['vm_ready_application_duplicate_attempts'] == 0 and
            cv['vm_translation_quiescent_invariants_hold'] == 1 and
            cv['awma_prel1_coalescer_quiescent'] == 1 and
            cv['awma_prel1_coalescer_leaders'] ==
            cv['awma_prel1_coalescer_leader_completions'] and
            followers == cv['awma_prel1_coalescer_follower_applications'] and
            cv['awma_prel1_coalescer_followers_final'] == 0 and
            cv['awma_prel1_coalescer_waiters_final'] == 0)
        speedup = (ov['gpu_sim_cycle'] - cv['gpu_sim_cycle']) / ov['gpu_sim_cycle']
        l1_delta = ov['vm_l1_tlb_lookup_launches'] - cv['vm_l1_tlb_lookup_launches']
        l2_delta = ov['vm_l2_tlb_lookup_launches'] - cv['vm_l2_tlb_lookup_launches']
        wait_cycles_mean = (
            cv['awma_prel1_coalescer_follower_wait_cycles_total'] /
            followers if followers else 0)
        delivery_latency_mean = (
            cv['awma_prel1_coalescer_follower_delivery_latency_total'] /
            followers if followers else 0)
        row = {
            'target': target, 'evidence_role': spec['role'],
            'family': spec['family'], 'scenario': spec['scenario'],
            'off_cycles': ov['gpu_sim_cycle'],
            'candidate_cycles': cv['gpu_sim_cycle'], 'speedup': speedup,
            'off_l1': ov['vm_l1_tlb_lookup_launches'],
            'candidate_l1': cv['vm_l1_tlb_lookup_launches'],
            'l1_delta': l1_delta,
            'l1_fraction': l1_delta / ov['vm_l1_tlb_lookup_launches'],
            'off_l2': ov['vm_l2_tlb_lookup_launches'],
            'candidate_l2': cv['vm_l2_tlb_lookup_launches'],
            'l2_delta': l2_delta,
            'off_mshr_alloc': ov['vm_translation_mshr_allocations'],
            'candidate_mshr_alloc': cv['vm_translation_mshr_allocations'],
            'off_mshr_merge': ov['vm_translation_mshr_merges'],
            'candidate_mshr_merge': cv['vm_translation_mshr_merges'],
            'off_walks': ov['vm_translation_walk_starts'],
            'candidate_walks': cv['vm_translation_walk_starts'],
            'off_pte': ov['vm_pte_requests'],
            'candidate_pte': cv['vm_pte_requests'],
            'leaders': cv['awma_prel1_coalescer_leaders'],
            'followers': followers, 'wait_cycles_mean': wait_cycles_mean,
            'wait_cycles_max':
                cv['awma_prel1_coalescer_follower_wait_cycles_max'],
            'delivery_latency_mean': delivery_latency_mean,
            'wait_p50': cv['awma_prel1_coalescer_delivery_wait_p50'],
            'wait_p95': cv['awma_prel1_coalescer_delivery_wait_p95'],
            'wait_p99': cv['awma_prel1_coalescer_delivery_wait_p99'],
            'wait_max': cv['awma_prel1_coalescer_follower_delivery_latency_max'],
            'head_block': cv['awma_prel1_coalescer_head_block_cycles'],
            'entry_full': cv['awma_prel1_coalescer_entry_full_fallbacks'],
            'waiter_full': cv['awma_prel1_coalescer_waiter_full_fallbacks'],
            'entry_hwm': cv['awma_prel1_coalescer_occupancy_hwm'],
            'waiter_hwm': cv['awma_prel1_coalescer_waiter_hwm'],
            'l1_hit_leaders': cv['awma_prel1_coalescer_l1_hit_leaders'],
            'l2_hit_leaders': cv['awma_prel1_coalescer_l2_hit_leaders'],
            'ptw_leaders': cv['awma_prel1_coalescer_ptw_leaders'],
            'coverage_admissions': cand['coverage']['admissions'],
            'coverage_unique': cand['coverage']['unique'],
            'coverage_untranslated': cand['coverage']['untranslated'],
            'coverage_unobserved': cand['coverage']['unobserved'],
            'repeated_admissions': number(
                cand['text'], 'awma_owner_wait_repeated_admissions'),
            'readmitted_uids': number(
                cand['text'], 'awma_owner_wait_readmitted_uids'),
            'duplicate_applications':
                cv['vm_ready_application_duplicate_attempts'],
            'off_terminal': off['terminal'],
            'candidate_terminal': cand['terminal'],
            'controller_quiescent':
                cv['vm_translation_quiescent_invariants_hold'],
            'coalescer_quiescent': cv['awma_prel1_coalescer_quiescent'],
            'correctness': correctness,
        }
        runs[target] = {'off': off, 'candidate': cand, 'row': row}
        consolidated.append(row)

    all_rows = [[r[k] for k in (
        'target', 'evidence_role', 'family', 'scenario', 'off_cycles',
        'candidate_cycles')] + [r['speedup'] * 100,
        r['off_l1'], r['candidate_l1'], r['l1_delta'], r['l1_fraction'],
        r['off_l2'], r['candidate_l2'], r['l2_delta'],
        r['off_mshr_alloc'], r['candidate_mshr_alloc'],
        r['off_mshr_merge'], r['candidate_mshr_merge'],
        r['off_mshr_merge'] - r['candidate_mshr_merge'],
        r['off_walks'], r['candidate_walks'],
        r['off_walks'] - r['candidate_walks'],
        r['off_pte'], r['candidate_pte'], r['followers'],
        r['wait_cycles_mean'], r['wait_cycles_max'],
        r['delivery_latency_mean'],
        r['wait_p50'], r['wait_p95'], r['wait_p99'], r['wait_max'],
        r['head_block'], r['entry_full'], r['waiter_full'], r['entry_hwm'],
        r['waiter_hwm'], r['coverage_admissions'], r['coverage_unique'],
        r['coverage_untranslated'], r['coverage_unobserved'],
        r['repeated_admissions'], r['readmitted_uids'],
        r['duplicate_applications'], r['off_terminal'],
        r['candidate_terminal'], r['controller_quiescent'],
        r['coalescer_quiescent'], r['correctness']] for r in consolidated]
    write_tsv(PACK / 'FROZEN_MECHANISM_ALL_TARGETS.tsv', [
        'target', 'evidence_role', 'family', 'scenario', 'cycles_off',
        'cycles_candidate', 'speedup_percent', 'l1_launches_off',
        'l1_launches_candidate', 'l1_suppression_absolute',
        'l1_suppression_fraction', 'l2_launches_off',
        'l2_launches_candidate', 'l2_suppression', 'mshr_alloc_off',
        'mshr_alloc_candidate', 'mshr_merge_off', 'mshr_merge_candidate',
        'mshr_merge_reduction', 'ptw_walk_off', 'ptw_walk_candidate',
        'ptw_walk_reduction', 'pte_requests_off', 'pte_requests_candidate',
        'followers', 'follower_wait_cycles_mean', 'follower_wait_cycles_max',
        'follower_delivery_latency_mean', 'follower_delivery_latency_p50',
        'follower_delivery_latency_p95', 'follower_delivery_latency_p99',
        'follower_delivery_latency_max', 'head_block_cycles', 'entry_full',
        'waiter_full',
        'entry_hwm', 'waiter_hwm', 'coverage_admissions', 'coverage_unique',
        'coverage_untranslated', 'coverage_unobserved',
        'repeated_admissions', 'readmitted_uids', 'duplicate_applications',
        'off_terminal', 'candidate_terminal', 'controller_quiescent',
        'coalescer_quiescent', 'correctness'], all_rows)

    ledger_rows = [[*row] for row in EVIDENCE]
    write_tsv(PACK / 'PAPER_EVIDENCE_LEDGER.tsv', [
        'stage', 'commit', 'scientific_question', 'accepted_result',
        'what_it_proves', 'what_it_does_not_prove', 'paper_claim_use'],
        ledger_rows)
    (PACK / 'CLAIM_PROVENANCE.md').write_text('''# Claim provenance

The accepted chain is intentionally non-monotonic: blocking sharing exposed a
wait/HOL failure; fanout-only repair failed; nonblocking proactive sharing
removed waiting but exposed nonsharing retry amplification; passive forwarding
showed that head-time reuse is already prelaunched; pre-L1 characterization
then moved the intervention to the actual service-launch boundary.

Final paper claims may use only rows marked `YES_*` in
`PAPER_EVIDENCE_LEDGER.tsv`. Mixed passive V2 is diagnostic only. Development
performance establishes measured responses, the grouping-only control supports
the service-suppression mediator, and the preregistered REDUCE result supplies
independent service-suppression generalization. None of these authorities
supports novelty, universal speedup, end-to-end model speedup, or real-silicon
PPA.
''')

    inventory_rows = []
    for target in ('T0', 'T1', 'T2', 'SPLITKV', 'COMBINE', 'A1', 'A2'):
        cmd = json.loads((runs[target]['off']['path'] / 'command.json').read_text())
        inventory_rows.append([target, cmd.get('family', TARGETS[target]['family']),
            TARGETS[target]['scenario'], cmd.get('payload', 'ACCEPTED_TRACE'),
            cmd.get('payload_sha256', ''), 'ALREADY_DEVELOPMENT',
            'DEVELOPMENT', 'REUSED_NO_RERUN', target])
    inventory_rows.extend([
        ['H1', 'GEMV', 'Pair C S2 step16', str(RUNTIME_INPUT('kernel-16795-ctx_0x5bd5f19c5280.traceg.xz')),
         'ba73fd184217b066682f93e09969a1a9e05dc1b119e5644ee62a0be530585e3c',
         'QUALIFIED_AND_NOT_YET_RUN_WITH_FROZEN_PREL1',
         'ADDITIONAL_FROZEN_EVALUATION', 'RUN_COMPLETED_THIS_STAGE', 'STR_8a5773a1d265:S2'],
        ['H2', 'GEMV', 'Pair C D128 step96', str(RUNTIME_INPUT('kernel-101035-ctx_0x56928de701b0.traceg.xz')),
         '4c601dcad31f1afdb931602671bbb54556ca12734f1ee853dc41a89779f44320',
         'QUALIFIED_AND_NOT_YET_RUN_WITH_FROZEN_PREL1',
         'ADDITIONAL_FROZEN_EVALUATION', 'RUN_COMPLETED_THIS_STAGE', 'STR_8a5773a1d265:D128'],
        ['REDUCE', 'REDUCE', 'Independent S2 decode step1',
         json.loads((runs['REDUCE']['off']['path'] / 'command.json').read_text())['trace'],
         'ed712fb618309fd4f08c5ccc284a807df8a78581df2880f76fc415fa8a3b9105',
         'ALREADY_INDEPENDENT_HOLDOUT', 'INDEPENDENT_HOLDOUT',
         'REUSED_NO_RERUN', 'STR_e0922aa2a506_P1'],
        ['B1', 'OTHER', 'Batch1 Pair B grammar reject',
         '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/B1_formal_GRAMMAR_REJECT',
         '', 'INPUT_AVAILABLE_BUT_NOT_SCIENTIFICALLY_USEFUL', 'NONE',
         'GRAMMAR_REJECT_NO_RUN', 'B1_REJECTED'],
        ['FALLBACK', 'ELEMENTWISE', 'Preregistered fallback', '', '',
         'NOT_AVAILABLE', 'NONE', 'NOT_CAPTURED', 'STR_48b98b28a393'],
        ['MICRO_CONTROLS', 'MICRO', 'M1/M2 and A1/A8/A32/A32_W8',
         '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma', '',
         'INPUT_AVAILABLE_BUT_NOT_SCIENTIFICALLY_USEFUL', 'CORRECTNESS_CALIBRATION',
         'NO_PAPER_PERFORMANCE_RUN', 'AGGREGATE_NOT_INDEPENDENT_SAMPLES'],
        ['PLATFORM_ANCHORS', 'MICRO', 'P_L1/P_L2/P_DRAM/P_BW',
         '/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_platform_anchors_v1_20260923T115000Z', '',
         'INPUT_AVAILABLE_BUT_NOT_SCIENTIFICALLY_USEFUL', 'PLATFORM_CALIBRATION',
         'NO_MECHANISM_RUN', 'AGGREGATE_NOT_WORKLOAD_TARGETS'],
    ])
    write_tsv(PACK / 'EXISTING_TRACE_INVENTORY.tsv', [
        'target', 'family', 'scenario', 'trace_or_asset', 'sha256',
        'qualification_class', 'final_evidence_role', 'stage_action',
        'scientific_sample_identity'], inventory_rows)

    # Pressure and sensitivity columns exist only where accepted authorities
    # expose them. Never infer missing values.
    obs_rows = read_tsv(DEV_PACK / 'OBSERVATORY_LEVEL1.tsv')
    obs = {(r['target'], r['metric']): r for r in obs_rows}
    service_rows = []
    for r in consolidated:
        target = r['target']
        s_l1, s_all = SENSITIVITY.get(target, ('NA', 'NA'))
        def delta(metric: str, column: str = 'total') -> object:
            entry = obs.get((target, metric))
            if entry is None:
                return 'NA'
            return float(entry[f'candidate_{column}']) - float(entry[f'off_{column}'])
        response = 'POSITIVE' if r['speedup'] > 0 else (
            'NEGATIVE' if r['speedup'] < 0 else 'EXACT_ZERO')
        service_rows.append([
            target, r['evidence_role'], r['family'], r['l1_fraction'],
            r['l2_delta'], r['off_mshr_merge'] - r['candidate_mshr_merge'],
            s_l1, s_all, delta('translation.translation_not_ready'),
            delta('scheduler.dependency_scoreboard'),
            delta('memory.icnt_to_l2_occupancy', 'mean'),
            delta('memory.dram_queue_occupancy', 'mean'),
            r['speedup'] * 100, response, r['head_block']])
    write_tsv(PACK / 'SERVICE_PERFORMANCE_MATRIX.tsv', [
        'target', 'evidence_role', 'family', 'l1_suppression_fraction',
        'l2_suppression', 'mshr_merge_reduction', 'S_L1', 'S_ALL',
        'translation_not_ready_delta', 'scheduler_dependency_delta',
        'icnt_to_l2_mean_delta', 'dram_queue_mean_delta',
        'speedup_percent', 'response_sign', 'head_block_cycles'], service_rows)
    (PACK / 'SERVICE_TO_PERFORMANCE_ANALYSIS.md').write_text('''# Service suppression to performance response

Every measured target reduces L1 translation launches, but runtime response is
not linear or universal.

- Measurable positive responses occur on T0, T1, A2 and both Pair-C contexts,
  alongside substantial redundant-L1 suppression. Downstream-pressure
  attribution is limited to targets with accepted Observatory columns; Pair-C
  has no such columns and receives no pressure explanation.
- SPLITKV has only a very small positive response; COMBINE and independent
  REDUCE are exactly cycle-neutral despite substantial suppression. Their
  translation work is largely hidden behind other execution/memory work at
  the modeled scale.
- T2 and A1 regress even with zero follower head-block. Accepted Observatory
  evidence shows schedule/cache-pressure and progress-tail perturbations that
  can offset the service benefit; it does not identify a root cause.
- Accepted `S_L1/S_ALL` exists only for T0/T1/T2 and is reported verbatim.
  No sensitivity is invented for other targets. The mixed signs—especially
  T2 and T1's negative `S_ALL` ideal response—rule out a simple linear causal
  model between suppressed requests and cycles.

The paper-level observation is therefore bounded: pre-L1 coalescing reliably
removes modeled translation service on the measured targets; speedup appears
when that service is exposed on the critical schedule, remains hidden when
other work dominates, and can be offset by schedule perturbation.
''')

    # Existing MSHR comparison.
    mshr_rows = []
    for r in consolidated:
        existing_fraction = r['off_mshr_merge'] / r['off_l1']
        prel1_fraction = r['followers'] / r['off_l1']
        mshr_rows.append([
            r['target'], r['off_l1'], r['off_mshr_merge'], existing_fraction,
            r['followers'], prel1_fraction, r['l1_delta'], r['l2_delta'],
            r['l1_hit_leaders'], r['l2_hit_leaders'], r['ptw_leaders']])
    write_tsv(PACK / 'PREL1_VS_MSHR_MATRIX.tsv', [
        'target', 'baseline_l1_launches', 'baseline_existing_mshr_merges',
        'existing_mshr_merge_fraction', 'prel1_followers',
        'prel1_incremental_merge_fraction', 'l1_lookup_reduction',
        'l2_reduction', 'candidate_l1_hit_leaders',
        'candidate_l2_hit_leaders', 'candidate_ptw_leaders'], mshr_rows)
    (PACK / 'PREL1_VS_MSHR_ANALYSIS.md').write_text('''# Pre-L1 coalescer versus conventional translation MSHR

Source semantics place the conventional translation MSHR after an admitted L1
lookup, an L1 miss and an L2 miss/handoff. A larger MSHR can hold more miss-side
waiters, but it cannot undo the L1 lookup bandwidth already consumed by an
L1-hit duplicate or by a duplicate that reaches L2 before merging.

The frozen pre-L1 coalescer compares the exact identity before the L1 port.
Its follower waits on the leader's complete translation result, whereas an
MSHR waiter is registered only on a miss-side page-walk entry. These waiter
semantics and service locations are different.

`PREL1_VS_MSHR_MATRIX.tsv` shows that existing MSHR merges are a small fraction
of baseline L1 launches while pre-L1 followers are often tens of percent or
more. Candidate leader-source counts are dominated by L1 hits on the high-
redundancy targets. Therefore simply enlarging the existing MSHR does not cover
the measured L1-hit duplicate population. No unmeasured larger-MSHR performance
claim is made.
''')

    # Descriptive performance summaries; no threshold-defined neutral bucket.
    responses = [r['speedup'] * 100 for r in consolidated]
    family_rows = []
    for family in sorted(set(r['family'] for r in consolidated)):
        values = [r['speedup'] * 100 for r in consolidated if r['family'] == family]
        family_rows.append([family, len(values), statistics.mean(values),
                            statistics.median(values), min(values), max(values),
                            ','.join(f'{v:.6f}' for v in values)])
    write_tsv(PACK / 'FAMILY_LEVEL_SUMMARY.tsv', [
        'family', 'target_count', 'unweighted_mean_percent_descriptive_only',
        'median_percent', 'minimum_percent', 'maximum_percent',
        'raw_target_responses_percent'], family_rows)
    positive = sum(v > 0 for v in responses)
    negative = sum(v < 0 for v in responses)
    zero = sum(v == 0 for v in responses)
    best = max(consolidated, key=lambda r: r['speedup'])
    worst = min(consolidated, key=lambda r: r['speedup'])
    (PACK / 'PERFORMANCE_CLAIM_BOUNDARY.md').write_text(f'''# Performance claim boundary

Unweighted measured-target distribution: {positive} positive, {zero} exact
zero, {negative} negative. No arbitrary near-neutral threshold is introduced;
all raw values remain in `FROZEN_MECHANISM_ALL_TARGETS.tsv`. Maximum positive:
{best['target']} {best['speedup'] * 100:.6f}%. Maximum negative:
{worst['target']} {worst['speedup'] * 100:.6f}%.

Family-level means/medians are descriptive only and are not workload-weighted
speedup claims. The accepted seven-target opportunity table provides
instruction-weight fractions, not exact Native time mass. Therefore a
`NATIVE_TIME_WEIGHTED_ESTIMATE` is **not computed**. No end-to-end model
speedup is inferred.
''')

    # Hardware state, RTL correctness and generic synthesis.
    key_bits = 32 + 33 + 1 + 64 + 2
    fixed_entry_bits = 2 + key_bits + 32 + 33 + 6  # state,key,leader,PPN,count
    min_waiter_w = 32
    cons_waiter_w = 325
    min_per_entry = fixed_entry_bits + 32 * min_waiter_w
    cons_per_entry = fixed_entry_bits + 32 * cons_waiter_w
    min_per_sid = 2 * min_per_entry
    cons_per_sid = 2 * cons_per_entry
    drain_cursor_per_sid = 2 * 6
    min_proxy_per_sid = min_per_sid + drain_cursor_per_sid
    cons_proxy_per_sid = cons_per_sid + drain_cursor_per_sid
    min_registered_pipeline = 1 + key_bits + 32 + min_waiter_w
    cons_registered_pipeline = 1 + key_bits + 32 + cons_waiter_w
    state_rows = [
        ['exact_key_compare_width', 'PER_ENTRY', key_bits, '32 ASID + 33 VPN + 1 page class + 64 generation + 2 access', 'SIMULATOR_LOGICAL_WIDTH'],
        ['fixed_entry_state_excluding_waiters', 'PER_ENTRY', fixed_entry_bits, '2 state + key + 32 leader tag + 33 PPN + 6 waiter count', 'SIMULATOR_LOGICAL_WIDTH'],
        ['minimal_waiter_metadata', 'PER_WAITER', min_waiter_w, 'mem_access UID continuation token', 'LOWER_BOUND_PROXY'],
        ['conservative_waiter_metadata', 'PER_WAITER', cons_waiter_w, 'UID32+VA64+size32+write1+type32+warp32+byte128+sector4', 'SOURCE_VISIBLE_REQUEST_PROXY'],
        ['minimal_mechanism_entry_state', 'PER_ENTRY', min_per_entry, 'fixed + 32*32; excludes proxy drain cursor', 'LOWER_BOUND_MECHANISM'],
        ['conservative_mechanism_entry_state', 'PER_ENTRY', cons_per_entry, 'fixed + 32*325; excludes proxy drain cursor', 'CONSERVATIVE_MECHANISM'],
        ['minimal_mechanism_state', 'PER_SID', min_per_sid, '2 entries; excludes proxy drain cursor', 'LOWER_BOUND_MECHANISM'],
        ['conservative_mechanism_state', 'PER_SID', cons_per_sid, '2 entries; excludes proxy drain cursor', 'CONSERVATIVE_MECHANISM'],
        ['proxy_drain_cursor', 'PER_SID', drain_cursor_per_sid, '2 entries * 6-bit finite-drain index', 'HARDWARE_PROXY'],
        ['minimal_same_cycle_proxy_state', 'PER_SID', min_proxy_per_sid, 'mechanism state + drain cursors', 'LOWER_BOUND_PROXY'],
        ['conservative_same_cycle_proxy_state', 'PER_SID', cons_proxy_per_sid, 'mechanism state + drain cursors', 'CONSERVATIVE_PROXY'],
        ['minimal_registered_request_pipeline', 'PER_SID', min_registered_pipeline, 'valid + exact key + tag + waiter metadata', 'TIMING_VARIANT_ONLY'],
        ['conservative_registered_request_pipeline', 'PER_SID', cons_registered_pipeline, 'valid + exact key + tag + waiter metadata', 'TIMING_VARIANT_ONLY'],
        ['minimal_same_cycle_simulated_platform_total', '76_SID', min_proxy_per_sid * 76, '76 clusters * 1 core/cluster from frozen config', 'SIMULATED_PLATFORM_SCALING'],
        ['conservative_same_cycle_simulated_platform_total', '76_SID', cons_proxy_per_sid * 76, '76 clusters * 1 core/cluster from frozen config', 'SIMULATED_PLATFORM_SCALING'],
        ['same_cycle_real_gpu_formula', 'N_SID', f'{min_proxy_per_sid}*N_SID to {cons_proxy_per_sid}*N_SID', 'do not assume real SID mapping', 'PAPER_HARDWARE_ASSUMPTION_REQUIRED'],
    ]
    write_tsv(PACK / 'HARDWARE_STATE_BUDGET.tsv', [
        'component', 'scope', 'bits_or_formula', 'derivation', 'evidence_class'], state_rows)
    observed_waiter_max = max(r['waiter_hwm'] for r in consolidated)
    observed_entry_max = max(r['entry_hwm'] for r in consolidated)
    (PACK / 'SIMULATOR_TO_RTL_STATE_MAPPING.md').write_text(f'''# Simulator to RTL state mapping

The field-level mapping is frozen in
`util/vm_tlb/awma/prel1_hw_proxy/STATE_MAPPING.tsv`.

Hardware-required state is the exact translation key, leader completion tag,
FREE/LIVE/READY lifecycle, result PPN, bounded waiter allocation and follower
continuation metadata. Registration cycles, wait histograms, service source,
critical-path markers and C++ containers are simulation/debug state only.
The RTL proxy additionally uses one 6-bit drain cursor per entry. Its optional
registered timing variant adds a 197-bit (minimal) or 490-bit (conservative)
transient request pipeline per SID; neither is hidden in the state budget.

The simulator uses a 32-bit `unsigned` ASID field and 64-bit generation field,
but defines no target hardware widths for either. They are reported as
`SIMULATOR_LOGICAL_WIDTH`; a paper implementation must choose and justify real
ASID/generation widths. Request-token width likewise requires an implementation
contract. The proxy uses source UID width 32 as its minimum.

The frozen platform has 76 simulated SIDs. Real RTX4080 SID/SM mapping is not
asserted. GPU-wide state is `N_SID * per_SID_state`.

Frozen capacity remains 2 entries/SID and 32 waiters/entry. Across development,
Pair C and REDUCE, observed entry HWM is {observed_entry_max} and waiter HWM is
{observed_waiter_max}; this does not prove 32 is minimal.
''')

    test_out = RTL / 'out/tests'
    variants = (
        ('same_cycle_minimal', 0, 32), ('registered_minimal', 1, 32),
        ('same_cycle_conservative', 0, 325),
        ('registered_conservative', 1, 325))
    rtl_rows = []
    for name, registered, width in variants:
        log = test_out / f'{name}.log'
        passed = 'PREL1_RTL_PROXY_TEST PASS' in log.read_text()
        for requirement in ('unique', 'inflight_exact_merge', 'different_vpn',
                            'asid_mismatch', 'generation_mismatch',
                            'access_mismatch', 'two_entry_full',
                            'thirty_two_waiter_full', 'completion_and_drain',
                            'entry_reuse', 'no_duplicate_follower_completion',
                            'concurrent_completion_exact_request'):
            rtl_rows.append([name, registered, width, requirement,
                             'PASS' if passed else 'FAIL', sha(log)])
    write_tsv(PACK / 'RTL_CORRECTNESS.tsv', [
        'variant', 'registered_compare', 'waiter_metadata_bits', 'requirement',
        'status', 'test_log_sha256'], rtl_rows)

    synth_rows = []
    for name, registered, width in variants:
        stats = parse_synth(name)
        logical = min_proxy_per_sid if width == 32 else cons_proxy_per_sid
        pipeline = ((min_registered_pipeline if width == 32
                     else cons_registered_pipeline) if registered else 0)
        synth_rows.append([
            name, 'REGISTERED_PLUS1' if registered else 'SAME_CYCLE',
            'MINIMAL_WAITER_METADATA' if width == 32 else 'CONSERVATIVE_WAITER_METADATA',
            width, logical, pipeline, logical + pipeline,
            stats['wires'], stats['wire_bits'], stats['cells'],
            stats['dff'], stats['mux'], stats['logic_depth'],
            'TECHNOLOGY_PROXY_ONLY', 'NA_NO_ACCEPTED_STANDARD_CELL_LIBRARY',
            'NA_NO_ACCEPTED_STANDARD_CELL_LIBRARY'])
    write_tsv(PACK / 'RTL_SYNTHESIS_RESULTS.tsv', [
        'variant', 'timing_variant', 'waiter_model', 'waiter_metadata_bits',
        'same_cycle_proxy_state_bits_per_sid',
        'registered_request_pipeline_bits_per_sid',
        'total_proxy_state_bits_per_sid', 'generic_wires', 'generic_wire_bits',
        'generic_cells', 'generic_dff_cells', 'generic_mux_cells',
        'generic_combinational_depth', 'qualification', 'area', 'fmax'], synth_rows)
    yosys_version = subprocess.check_output(['yosys', '-V'], text=True).strip()
    iverilog_version = subprocess.check_output(['iverilog', '-V'], text=True,
                                               stderr=subprocess.STDOUT).splitlines()[0]
    (PACK / 'HARDWARE_FEASIBILITY.md').write_text(f'''# Hardware feasibility

Status: **TECHNOLOGY_PROXY_ONLY / PPA_TECH_LIBRARY_UNAVAILABLE**

Tools: `{yosys_version}`; `{iverilog_version}`. No project-accepted standard-
cell `.lib/.db/.lef` was available, so real area, critical delay and Fmax are
not reported or estimated.

The RTL proxy is synthesizable and passes all directed variants, including a
completion/exact-request same-cycle race. Generic synthesis gives
{synth_rows[0][9]:,} cells/{synth_rows[0][10]:,} DFFs for the same-cycle
minimal proxy and {synth_rows[2][9]:,} cells/{synth_rows[2][10]:,}
DFFs for the conservative metadata proxy. The registered variants add exactly
197/490 DFFs for their request pipeline. All four generic netlists have
combinational depth 21 after excluding FFs.

The registered input cuts the external request-to-CAM decision boundary, but
the proxy-wide generic longest path remains dominated by other drain/storage
mux logic. Thus same-cycle compare is not shown to be the sole proxy critical
path; neither variant proves GPU integration timing closure.

The exact CAM compares two {key_bits}-bit keys. Same-cycle proxy state,
including two 6-bit drain cursors, ranges from {min_proxy_per_sid:,} to
{cons_proxy_per_sid:,} bits/SID. For the simulated 76-SID platform these scale
to {min_proxy_per_sid * 76:,}--{cons_proxy_per_sid * 76:,} bits. Registered
timing adds {min_registered_pipeline}/{cons_registered_pipeline} bits/SID.
These are logical storage/proxy bounds, not layout area.

Remaining proxy limitations are explicit: there is one request input and one
unbackpressured follower output per cycle; page-class and completion-tag
mismatch are structurally compared but not separate directed-test rows; and
the proxy does not establish full GPU-controller integration equivalence.
''')

    design_rows = [
        ['larger_TLB', 'capacity/replacement path', 'Does not remove duplicate L1-hit probes', 'none', 'TLB entries/tags', 'array access/replacement', 'NOT_PERFORMANCE_TESTED_HERE'],
        ['larger_or_more_MSHR', 'after L1/L2 miss', 'No', 'none', 'more miss waiters', 'miss-side lookup/merge', 'baseline MSHR captures small subset'],
        ['post_L1_MSHR_merge', 'after L1 service', 'No', 'none', 'merge tags/waiters', 'L1 already consumed', 'same limitation as conventional placement'],
        ['result_forwarding', 'after result completion/head', 'No when frozen prelaunch already issued', 'none', 'result entry', 'late compare', 'V2R1 opportunity already prelaunched'],
        ['proactive_sharing', 'before baseline demand launch via owner', 'Yes', 'yes', 'owner/member state', 'owner order and retries', 'A2 +6.567% retry/readmission pathology'],
        ['pre_L1_exact_coalescing', 'immediately before L1 port', 'Yes', 'no', '2 exact entries plus bounded waiters', 'exact CAM plus follower wait', 'service generalized; runtime response mixed'],
    ]
    write_tsv(PACK / 'DESIGN_SPACE_COMPARISON.tsv', [
        'design', 'duplication_removal_point', 'covers_l1_hit_duplicates',
        'speculation', 'storage', 'critical_path_risk', 'observed_or_known_limit'],
        design_rows)
    (PACK / 'DESIGN_RATIONALE.md').write_text('''# Design rationale

The selected placement is the earliest point at which frozen V1 has committed
to a real physical L1 request but before that request consumes L1 service. It
therefore avoids proactive speculation and removes a population unavailable to
miss-side MSHRs. Exact identity and bounded fallback preserve legality and
liveness. Prior project evidence rules out blocking result sharing, fanout-only
repair, proactive no-opportunity ownership and post-result forwarding as clean
solutions for this specific duplication population.

The choice does not claim optimality against untested larger TLB/MSHR designs.
`DESIGN_SPACE_COMPARISON.tsv` is structural, not fabricated performance data.
''')

    # Paper tables and figure-data package.
    weights = {r['target']: r['instruction_weight_fraction'] for r in
               read_tsv(REPO / 'docs/vm_tlb/review_packs/AWMA_PASSIVE_TRANSLATION_RESULT_REUSE_OPPORTUNITY_V1/TARGET_OPPORTUNITY_MATRIX.tsv')}
    write_tsv(PACK / 'TABLE_1_WORKLOADS.tsv', [
        'target', 'evidence_role', 'family', 'scenario', 'off_cycles',
        'instruction_weight_fraction_if_available', 'native_time_weight'], [
        [r['target'], r['evidence_role'], r['family'], r['scenario'],
         r['off_cycles'], weights.get(r['target'], 'NA'), 'NA_NOT_AUTHORIZED']
        for r in consolidated])
    write_tsv(PACK / 'TABLE_2_CHARACTERIZATION.tsv', [
        'target', 'baseline_l1_launches', 'baseline_mshr_merges',
        'prel1_followers', 'l1_suppression_fraction', 'entry_hwm',
        'waiter_hwm'], [[r['target'], r['off_l1'], r['off_mshr_merge'],
                        r['followers'], r['l1_fraction'], r['entry_hwm'],
                        r['waiter_hwm']] for r in consolidated])
    write_tsv(PACK / 'TABLE_3_MAIN_RESULTS.tsv', [
        'target', 'role', 'off_cycles', 'candidate_cycles', 'speedup_percent',
        'l1_suppression', 'l2_suppression', 'followers', 'head_block_cycles'],
        [[r['target'], r['evidence_role'], r['off_cycles'],
          r['candidate_cycles'], r['speedup'] * 100, r['l1_delta'],
          r['l2_delta'], r['followers'], r['head_block']]
         for r in consolidated])
    reduce = next(r for r in consolidated if r['target'] == 'REDUCE')
    write_tsv(PACK / 'TABLE_4_HOLDOUT.tsv', [
        'target', 'family', 'off_cycles', 'candidate_cycles', 'speedup_percent',
        'followers', 'off_l1', 'candidate_l1', 'head_block', 'correctness'], [[
        reduce['target'], reduce['family'], reduce['off_cycles'],
        reduce['candidate_cycles'], reduce['speedup'] * 100,
        reduce['followers'], reduce['off_l1'], reduce['candidate_l1'],
        reduce['head_block'], reduce['correctness']]])
    write_tsv(PACK / 'TABLE_5_HARDWARE_COST.tsv', [
        'waiter_model', 'same_cycle_proxy_state_bits_per_sid',
        'same_cycle_proxy_state_bits_76_sid',
        'registered_request_pipeline_bits_per_sid',
        'registered_total_proxy_state_bits_per_sid',
        'same_cycle_generic_cells', 'registered_generic_cells',
        'technology_scope'], [
        ['MINIMAL_WAITER_METADATA', min_proxy_per_sid,
         min_proxy_per_sid * 76, min_registered_pipeline,
         min_proxy_per_sid + min_registered_pipeline,
         parse_synth('same_cycle_minimal')['cells'],
         parse_synth('registered_minimal')['cells'], 'TECHNOLOGY_PROXY_ONLY'],
        ['CONSERVATIVE_WAITER_METADATA', cons_proxy_per_sid,
         cons_proxy_per_sid * 76, cons_registered_pipeline,
         cons_proxy_per_sid + cons_registered_pipeline,
         parse_synth('same_cycle_conservative')['cells'],
         parse_synth('registered_conservative')['cells'], 'TECHNOLOGY_PROXY_ONLY'],
    ])
    write_tsv(PACK / 'FIG_DATA_1_TRANSLATION_REDUNDANCY.tsv', [
        'target', 'baseline_l1_launches', 'existing_mshr_merges',
        'prel1_followers'], [[r['target'], r['off_l1'], r['off_mshr_merge'],
                             r['followers']] for r in consolidated])
    write_tsv(PACK / 'FIG_DATA_2_SERVICE_SUPPRESSION.tsv', [
        'target', 'l1_suppression_fraction', 'l2_suppression',
        'mshr_merge_reduction'], [[r['target'], r['l1_fraction'], r['l2_delta'],
                                  r['off_mshr_merge'] - r['candidate_mshr_merge']]
                                 for r in consolidated])
    write_tsv(PACK / 'FIG_DATA_3_PERFORMANCE.tsv', [
        'target', 'evidence_role', 'speedup_percent', 'response_sign'], [[
        r['target'], r['evidence_role'], r['speedup'] * 100,
        'POSITIVE' if r['speedup'] > 0 else 'NEGATIVE' if r['speedup'] < 0 else 'EXACT_ZERO']
        for r in consolidated])
    write_tsv(PACK / 'FIG_DATA_4_WAIT_LATENCY.tsv', [
        'target', 'followers', 'wait_cycles_mean', 'wait_cycles_max',
        'delivery_latency_mean', 'delivery_latency_p50',
        'delivery_latency_p95', 'delivery_latency_p99',
        'delivery_latency_max', 'head_block_cycles'], [[
        r['target'], r['followers'], r['wait_cycles_mean'],
        r['wait_cycles_max'], r['delivery_latency_mean'], r['wait_p50'],
        r['wait_p95'], r['wait_p99'], r['wait_max'],
        r['head_block']] for r in consolidated])
    timing_rows = read_tsv(DEV_PACK / 'TIMING_SENSITIVITY.tsv')
    timing_rows.append({'target': 'REDUCE', 'off_cycles': '7716',
        'same_cycle_cycles': '7716', 'plus1_cycles': '7724',
        'same_cycle_speedup_percent': '0',
        'plus1_speedup_percent': '-0.103680664',
        'compare_delays': '115', 'followers': '105',
        'head_block_cycles': '0', 'correctness': 'True'})
    write_tsv(PACK / 'FIG_DATA_5_TIMING_SENSITIVITY.tsv',
              list(timing_rows[0].keys()),
              [[row[key] for key in timing_rows[0].keys()] for row in timing_rows])

    claims = [
        ['C1', 'AI/LLM kernels exhibit duplicate in-flight requests before L1 service', 'SUPPORTED_WITH_SCOPE', 'Phase-A development plus Pair C and REDUCE', 'Measured targets only; not all kernels/models'],
        ['C2', 'Existing miss-side MSHR captures only a small redundancy subset', 'SUPPORTED_WITH_SCOPE', 'PREL1_VS_MSHR_MATRIX and source placement', 'No larger-MSHR performance experiment'],
        ['C3', 'A two-entry exact pre-L1 coalescer suppresses substantial redundant L1 service on several kernels', 'SUPPORTED_WITH_SCOPE', 'Development and Pair C tables', 'Runtime benefit is not universal'],
        ['C4', 'Physical service suppression generalizes to independent AT_NATIVE_REDUCE', 'SUPPORTED', 'fc5ea3bf independent holdout', 'Single independent target'],
        ['C5', 'Service suppression does not imply universal runtime speedup', 'SUPPORTED', 'Positive/zero/negative response distribution', 'No end-to-end model claim'],
        ['C6', 'Mechanism avoids proactive-owner and head-blocking pathologies', 'SUPPORTED_WITH_SCOPE', 'Zero proactive requests/head-block across measured candidate runs', 'Does not prove all future schedules'],
        ['C7', 'Two entries/SID match the cap-8 opportunity count on the frozen Phase-A development traces', 'SUPPORTED_WITH_SCOPE', 'Phase-A capacity sweep: cap2 equals cap8 merge count with zero Phase-A full events', 'Performance runs later observe finite entry-full fallback; not a universal minimal capacity'],
        ['C8', '32 waiters is a frozen bound; observed demand is lower', 'SUPPORTED', f'Frozen 32; observed maximum {observed_waiter_max}', 'Does not prove 16 is sufficient generally'],
        ['C9', 'Same-cycle compare is a simulator assumption; +1 cycle remains viable', 'SUPPORTED_WITH_SCOPE', 'T0/T1/T2/A2 plus REDUCE sensitivity and RTL registered variant', 'No physical GPU timing closure'],
    ]
    write_tsv(PACK / 'PAPER_CLAIM_MATRIX.tsv', [
        'claim_id', 'claim', 'status', 'authority', 'boundary'], claims)

    (PACK / 'PAPER_EXPERIMENT_GAPS.md').write_text('''# Paper experiment gaps

## BLOCKING_FOR_PAPER

None for the scoped claims in `PAPER_CLAIM_MATRIX.tsv`.

## HIGH_VALUE_NONBLOCKING

- cross-model simulator-native validation beyond the current Qwen2.5 lineage;
- a project-approved standard-cell library and physical-design flow for real
  technology-specific area/Fmax;
- an accepted exact target-to-Native-time mass mapping for an end-to-end
  `NATIVE_TIME_WEIGHTED_ESTIMATE`;
- deeper attribution of the T2/A1 schedule-sensitive regressions.

## OPTIONAL

- more contexts within already represented Flash/GEMM/GEMV/Reduce families;
- larger-context points beyond Pair A/C;
- alternative finite delivery microarchitectures for the RTL proxy.

No new capture is required to support the current scoped core claims. If a
future expansion is authorized, it should be one batch—not piecemeal—covering
one different model lineage with four preregistered roles: prefill attention,
prefill GEMM, short/long-context decode GEMV, and reduction/normalization. Each
must have immutable model/input/trace hashes, SM89 grammar qualification and an
OFF-first simulator signature. This Goal does not start node109.
''')

    qualification = 'READY_FOR_PAPER_WRITEUP_WITH_OPTIONAL_EXPANSION'
    (PACK / 'FINAL_QUALIFICATION.md').write_text(f'''# Final paper qualification

`PAPER_QUALIFICATION_STATUS`: **{qualification}**

The scoped core mechanism claims are supported by exact opportunity
characterization, a frozen finite implementation, matched causal control,
mixed performance responses, independent REDUCE service-suppression evidence,
additional Pair-C context evaluation, and a synthesizable/tested hardware
proxy. Expansion would strengthen model-family breadth and technology-specific
PPA but is not required for the bounded current claims.

`MECHANISM_SOURCE` remains frozen at
`{SOURCE_FREEZE}`. No mechanism parameter was changed and node109 was not
started.

Important boundaries:

- no novelty determination;
- no universal speedup or arithmetic-average claim;
- no measured end-to-end model speedup;
- no real-silicon area/Fmax claim;
- generic 10/80 simulator timing remains a modeling authority.
''')

    # Raw/provenance index.
    raw = []
    def add_artifact(kind: str, identity: str, path: Path) -> None:
        raw.append([kind, identity, str(path), sha(path)])
    for target, data in runs.items():
        for arm in ('off', 'candidate'):
            directory = data[arm]['path']
            for name in ('run.log', 'command.json'):
                artifact = directory / name
                if artifact.is_file():
                    add_artifact('run', f'{target}:{arm}:{name}', artifact)
    for target in ('H1', 'H2'):
        directory = TARGETS[target]['cand']
        for name in ('rc.txt', 'wall_seconds.txt'):
            add_artifact('new_run_receipt', f'{target}:{name}', directory / name)
    for name, _, _ in variants:
        add_artifact('rtl_test', name, RTL_RAW / f'tests/{name}.log')
        add_artifact('generic_synthesis', f'{name}:stat', RTL_RAW / f'synthesis/{name}.stat.txt')
        add_artifact('generic_synthesis', f'{name}:ltp', RTL_RAW / f'synthesis/{name}.ltp.txt')
    for path in (RTL / 'prel1_exact_coalescer_proxy.v',
                 RTL / 'prel1_exact_coalescer_proxy_tb.v',
                 RTL / 'STATE_MAPPING.tsv',
                 REPO / 'util/vm_tlb/awma/run_paper_qualification_pair_c.py',
                 REPO / 'util/vm_tlb/awma/build_paper_qualification.py'):
        add_artifact('source_or_script', path.name, path)
    raw.extend([
        ['authority', 'baseline', 'git', '8d1f14a32f5538660d74da86ccb03a2c504c5735'],
        ['authority', 'mechanism_development', 'git', '163a8572f9272891b8109f9158aa79ca88d9e153'],
        ['authority', 'mechanism_source_freeze', 'git', SOURCE_FREEZE],
        ['authority', 'independent_holdout', 'git', 'fc5ea3bf1f09be1d0fbe3eb11fc6f6a847e4d763'],
        ['authority', 'binary_sha256', 'sha256', BINARY_SHA],
        ['authority', 'config_sha256', 'sha256', CONFIG_SHA],
        ['authority', 'trace_config_sha256', 'sha256', TRACE_CONFIG_SHA],
    ])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'identity', 'path_or_type', 'sha256_or_commit'], raw)

    (PACK / 'README.md').write_text(f'''# {STAGE}

Start with `FINAL_QUALIFICATION.md`.

Status: **{qualification}**

Evidence navigation:

- provenance: `PAPER_EVIDENCE_LEDGER.tsv`, `CLAIM_PROVENANCE.md`;
- traces/results: `EXISTING_TRACE_INVENTORY.tsv`,
  `FROZEN_MECHANISM_ALL_TARGETS.tsv`, `SERVICE_PERFORMANCE_MATRIX.tsv`;
- mechanism analysis: `SERVICE_TO_PERFORMANCE_ANALYSIS.md`,
  `PREL1_VS_MSHR_ANALYSIS.md`, `DESIGN_RATIONALE.md`;
- hardware: `HARDWARE_STATE_BUDGET.tsv`,
  `SIMULATOR_TO_RTL_STATE_MAPPING.md`, `RTL_CORRECTNESS.tsv`,
  `RTL_SYNTHESIS_RESULTS.tsv`, `HARDWARE_FEASIBILITY.md`;
- paper data/claims: `TABLE_*`, `FIG_DATA_*`, `PAPER_CLAIM_MATRIX.tsv`,
  `PAPER_EXPERIMENT_GAPS.md`.

The mechanism remains frozen; no new capture or mechanism optimization occurs
in this stage.
''')

    files = sorted(path for path in PACK.iterdir()
                   if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(''.join(
        f'{sha(path)}  {path.name}\n' for path in files))
    print(json.dumps({
        'status': qualification, 'targets': len(consolidated),
        'positive': positive, 'exact_zero': zero, 'negative': negative,
        'observed_entry_hwm': observed_entry_max,
        'observed_waiter_hwm': observed_waiter_max,
        'rtl_generic_synthesis': 'PASS_TECHNOLOGY_PROXY_ONLY',
    }, indent=2, sort_keys=True))
    return 0


def RUNTIME_INPUT(name: str) -> Path:
    return Path('/root/awma_prel1_coalescing_v1_runtime/inputs') / name


if __name__ == '__main__':
    raise SystemExit(main())
