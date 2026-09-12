#!/usr/bin/env python3
"""Final, read-only collector for C13 Path-A repaired evidence.

The collector deliberately requires terminal receipts and the ordered EQ1/EQ2
gate before emitting scientific tables.  It never launches a simulator and it
never reads the superseded mode-1 rows as scientific comparators.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import c13_effective_config_audit as audit
import collect_c13_diagnostics as legacy

PACK = audit.PACK
MANIFEST = audit.MANIFEST
OLD_PACK = audit.base.PACK
HANDOFF = ROOT / 'docs/vm_tlb/codex_handoff/c13_diagnostics/LATEST_REPORT.md'


def fail(message: str) -> None:
    raise SystemExit('C13 Path-A collector FAIL: ' + message)


def write_tsv(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        fail('refuses empty table ' + name)
    fields = list(rows[0])
    with (PACK / name).open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: ('NONE' if value == '' else value) for key, value in row.items()})


def fmt(value: int | float | None) -> str:
    if value is None:
        return 'NOT_EMITTED'
    if isinstance(value, float) and not value.is_integer():
        return '%.9g' % value
    return str(int(value))


def signed(value: int | float | None) -> str:
    if value is None:
        return 'NOT_EMITTED'
    return ('+' if value > 0 else '') + fmt(value)


def metric(arm: dict, name: str) -> int | float | None:
    return legacy.metric(arm, name)


def difference(arms: dict[str, dict], candidate: str, baseline: str, name: str) -> int | float | None:
    left, right = metric(arms[candidate], name), metric(arms[baseline], name)
    return None if left is None or right is None else left - right


def gate_pass() -> None:
    path = PACK / 'EQUIVALENCE_CONTROL.tsv'
    if not path.is_file():
        fail('missing ordered equivalence receipt')
    rows = list(csv.DictReader(path.open(), delimiter='\t'))
    required = {
        'EQ1_C12BIN_MANUAL_EXACTMODE_VS_C12_F7_L10',
        'EQ2_NEWBIN_DEFAULT_OFF_VS_EQ1',
        'EQ2_NEWBIN_DEFAULT_OFF_VS_C12_F7_L10',
    }
    if {row['comparison'] for row in rows} != required or any(row['status'] != 'PASS' for row in rows):
        fail('EQ1→EQ2 gate has not passed')


def load() -> tuple[dict[str, dict], dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    gate_pass()
    legacy.MANIFEST = MANIFEST
    c12 = legacy.c12_rows()
    c13, manifest = legacy.c13_rows()
    expected = {point['exp_id'] for point in audit.POINTS}
    if set(c13) != expected:
        fail('terminal repaired set mismatch missing=%s extra=%s' %
             (sorted(expected - set(c13)), sorted(set(c13) - expected)))
    mapping = legacy.load_map()
    arms = {**c12, **c13}
    for arm in arms.values():
        legacy.parse_arm(arm, mapping)
    return arms, mapping, manifest


def result_rows(arms: dict[str, dict], manifest: list[dict[str, str]]) -> list[dict[str, object]]:
    by_id = {row['exp_id']: row for row in manifest}
    metrics = ('gpu_tot_sim_cycle', 'vm_l1_tlb_misses', 'vm_l2_tlb_misses',
               'vm_translation_walk_starts', 'vm_pte_requests', 'vm_pte_dram_responses',
               'vm_translation_requester_latency_cycles_total',
               'vm_weight_segment_lookup_attempts', 'vm_weight_segment_hits',
               'vm_weight_segment_l2_suppressed')
    out = []
    for exp_id in sorted(by_id):
        arm, row = arms[exp_id], by_id[exp_id]
        final = arm['final']
        item: dict[str, object] = {
            'exp_id': exp_id, 'logical_role': row['logical_role'], 'roi': row['roi'],
            'scientific_status': 'ACCEPTED_AFTER_PATH_A_REPAIR',
            'gate_status': 'EQ1_THEN_EQ2_PASS', 'l2_mode': row['l2_mode'],
            'exact_l2_tlb_entries': row['exact_l2_tlb_entries'], 'l2_assoc': row['l2_assoc'],
            'l2_sets': row['l2_sets'], 'segment_enable': row['segment_enable'],
            'segment_n': row['segment_n'], 'lseg': row['lseg'],
            'eligibility_policy': row['eligibility_policy'], 'reuse_as': row['reuse_as'],
            'raw_log_sha256': arm['raw_sha'], 'config_sha256': row['config_sha256'],
            'binary_sha256': row['binary_sha256'], 'core_head': row['core_head'],
            'kernel_markers': len(arm['raw_kernels']), 'per_kernel_cycle_sum': arm['cycle_total'],
        }
        for name in metrics:
            item[name] = final.get(name, 'NOT_EMITTED')
        out.append(item)
    return out


def latency_rows(arms: dict[str, dict]) -> list[dict[str, object]]:
    points = (
        ('prefill', 'C12-PREFILL-F7-L5', 5, 'IMMUTABLE_C12_REFERENCE'),
        ('prefill', 'C13-LAT-P8-REPAIRED-EXACTMODE-A1', 8, 'MEASURED_C13_REPAIRED_FACT'),
        ('prefill', 'C13-LAT-P9-REPAIRED-EXACTMODE-A1', 9, 'MEASURED_C13_REPAIRED_FACT'),
        ('prefill', 'C12-PREFILL-F7-L10', 10, 'IMMUTABLE_C12_REFERENCE'),
        ('prefill', 'C12-PREFILL-F7-L20', 20, 'IMMUTABLE_C12_REFERENCE'),
        ('decode1', 'C12-DECODE1-F7-L5', 5, 'IMMUTABLE_C12_REFERENCE'),
        ('decode1', 'C12-DECODE1-F7-L10', 10, 'IMMUTABLE_C12_REFERENCE'),
        ('decode1', 'C13-LAT-D11-REPAIRED-EXACTMODE-A1', 11, 'MEASURED_C13_REPAIRED_FACT'),
        ('decode1', 'C12-DECODE1-F7-L20', 20, 'IMMUTABLE_C12_REFERENCE'),
    )
    out = []
    for roi, ident, lseg, evidence in points:
        arm = arms[ident]
        baseline = arms['C12-%s-F0-LNONE' % roi.upper()]
        cycles, base = metric(arm, 'gpu_tot_sim_cycle'), metric(baseline, 'gpu_tot_sim_cycle')
        out.append({'roi': roi, 'point_id': ident, 'lseg': lseg, 'cycles': fmt(cycles),
                    'cycle_delta_vs_f0': fmt(cycles - base), 'speedup_vs_f0': '%.9g' % (base / cycles),
                    'sign_vs_f0': 'GAIN' if cycles < base else 'REGRESSION' if cycles > base else 'TIE',
                    'evidence': evidence})
    return out


def crossover(rows: list[dict[str, object]], roi: str) -> str:
    subset = [row for row in rows if row['roi'] == roi]
    for left, right in zip(subset, subset[1:]):
        if left['sign_vs_f0'] != right['sign_vs_f0'] and 'TIE' not in (left['sign_vs_f0'], right['sign_vs_f0']):
            return '%s < Lseg* < %s (MEASURED_BRACKET_ONLY)' % (left['lseg'], right['lseg'])
    return 'CURRENT_MEASURED_POINTS_DO_NOT_BRACKET_BREAK_EVEN'


def capacity_rows(arms: dict[str, dict]) -> list[dict[str, object]]:
    ident = {'A_F0_exact768_no_segment': 'C12-PREFILL-F0-LNONE',
             'B_exact320_no_segment': 'C13-CAP-P320-REPAIRED-EXACTMODE-A1',
             'C_exact768_segmentN8_L10': 'C13-CAP-P768S10-REPAIRED-EXACTMODE-A1',
             'D_F7_exact320_segmentN8_L10': 'C12-PREFILL-F7-L10'}
    fields = ('gpu_tot_sim_cycle', 'vm_l2_tlb_misses', 'vm_translation_walk_starts',
              'vm_pte_requests', 'vm_pte_dram_responses', 'vm_translation_requester_latency_cycles_total')
    out = []
    for field in fields:
        value = {key: metric(arms[arm], field) for key, arm in ident.items()}
        out.append({'metric': field, **{key: fmt(item) for key, item in value.items()},
                    'B_minus_A': fmt(value['B_exact320_no_segment'] - value['A_F0_exact768_no_segment']),
                    'C_minus_A': fmt(value['C_exact768_segmentN8_L10'] - value['A_F0_exact768_no_segment']),
                    'D_minus_B': fmt(value['D_F7_exact320_segmentN8_L10'] - value['B_exact320_no_segment']),
                    'D_minus_C': fmt(value['D_F7_exact320_segmentN8_L10'] - value['C_exact768_segmentN8_L10']),
                    'interaction_(D-B)-(C-A)': fmt((value['D_F7_exact320_segmentN8_L10'] - value['B_exact320_no_segment']) - (value['C_exact768_segmentN8_L10'] - value['A_F0_exact768_no_segment'])),
                    'interpretation': 'DIAGNOSTIC_INTERACTION_ONLY'})
    return out


def selective_rows(arms: dict[str, dict]) -> list[dict[str, object]]:
    pairs = (('prefill', 'C13-SEL-P10-REPAIRED-EXACTMODE-A1', 'C13-EQ-P320S10-NEWBIN-EXACTMODE'),
             ('decode1', 'C13-SEL-D10-REPAIRED-EXACTMODE-A1', 'C13-SEL-D10-CTRL-NEWBIN-REPAIRED-EXACTMODE-A1'))
    fields = ('gpu_tot_sim_cycle', 'vm_l2_tlb_misses', 'vm_translation_walk_starts',
              'vm_pte_dram_responses', 'vm_translation_requester_latency_cycles_total',
              'vm_weight_segment_hits', 'vm_weight_segment_l2_suppressed')
    out = []
    for roi, candidate, control in pairs:
        row = {'roi': roi, 'candidate_id': candidate, 'same_binary_control_id': control,
               'control_reuse': 'EQ2_AS_PREFILL_CONTROL' if roi == 'prefill' else 'NONE',
               'scientific_status': 'ACCEPTED_AFTER_PATH_A_REPAIR'}
        for field in fields:
            row[field + '_candidate_minus_control'] = fmt(difference(arms, candidate, control, field))
        out.append(row)
    return out


def operator_rows(arms: dict[str, dict], mapping: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    pairs = (
        ('H3_PREFILL_L8_vs_F0', 'C13-LAT-P8-REPAIRED-EXACTMODE-A1', 'C12-PREFILL-F0-LNONE'),
        ('H3_PREFILL_L9_vs_F0', 'C13-LAT-P9-REPAIRED-EXACTMODE-A1', 'C12-PREFILL-F0-LNONE'),
        ('H3_DECODE_L11_vs_F0', 'C13-LAT-D11-REPAIRED-EXACTMODE-A1', 'C12-DECODE1-F0-LNONE'),
        ('H2_B_vs_A', 'C13-CAP-P320-REPAIRED-EXACTMODE-A1', 'C12-PREFILL-F0-LNONE'),
        ('H2_C_vs_A', 'C13-CAP-P768S10-REPAIRED-EXACTMODE-A1', 'C12-PREFILL-F0-LNONE'),
        ('H1_PREFILL_SELECTIVE_vs_CONTROL', 'C13-SEL-P10-REPAIRED-EXACTMODE-A1', 'C13-EQ-P320S10-NEWBIN-EXACTMODE'),
        ('H1_DECODE_SELECTIVE_vs_CONTROL', 'C13-SEL-D10-REPAIRED-EXACTMODE-A1', 'C13-SEL-D10-CTRL-NEWBIN-REPAIRED-EXACTMODE-A1'),
    )
    out = []
    for label, candidate, baseline in pairs:
        for row in legacy.per_operator_delta(arms[baseline], arms[candidate], mapping[arms[candidate]['roi']], label):
            row['evidence_boundary'] = 'ASSOCIATION_NOT_CAUSALITY'
            out.append(row)
    return out


def kernel691_rows(arms: dict[str, dict], mapping: list[dict[str, str]]) -> list[dict[str, object]]:
    if mapping[691]['operator_class'] != 'EMBEDDING_OUTPUT':
        fail('kernel 691 no longer maps to EMBEDDING_OUTPUT')
    ids = ('C12-PREFILL-F0-LNONE', 'C12-PREFILL-F7-L10',
           'C13-EQ-P320S10-C12BIN-EXACTMODE', 'C13-EQ-P320S10-NEWBIN-EXACTMODE',
           'C13-SEL-P10-REPAIRED-EXACTMODE-A1')
    control = 'C13-EQ-P320S10-NEWBIN-EXACTMODE'
    out = []
    for ident in ids:
        arm = arms[ident]
        cycle = legacy.kernel_cycle(arm, 691)
        out.append({'point_id': ident, 'kernel_index': 691, 'trace_filename': mapping[691]['trace_filename'],
                    'operator_class': 'EMBEDDING_OUTPUT', 'evidence_kind': mapping[691]['evidence_kind'],
                    'cycles': cycle, 'full_roi_cycles': fmt(metric(arm, 'gpu_tot_sim_cycle')),
                    'cycle_delta_vs_newbin_control': fmt(cycle - legacy.kernel_cycle(arms[control], 691)) if ident != control else '0'})
    return out


def old_vs_repaired(arms: dict[str, dict]) -> list[dict[str, object]]:
    old_by_repaired = {
        'C13-LAT-P8-REPAIRED-EXACTMODE-A1': 'C13-LAT-P8',
        'C13-LAT-P9-REPAIRED-EXACTMODE-A1': 'C13-LAT-P9',
        'C13-LAT-D11-REPAIRED-EXACTMODE-A1': 'C13-LAT-D11',
        'C13-CAP-P320-REPAIRED-EXACTMODE-A1': 'C13-CAP-P320',
        'C13-CAP-P768S10-REPAIRED-EXACTMODE-A1': 'C13-CAP-P768S10',
        'C13-EQ-P320S10-NEWBIN-EXACTMODE': 'C13-SEL-P10-CTRL-NEWBIN',
        'C13-SEL-P10-REPAIRED-EXACTMODE-A1': 'C13-SEL-P10',
        'C13-SEL-D10-CTRL-NEWBIN-REPAIRED-EXACTMODE-A1': 'C13-SEL-D10-CTRL-NEWBIN',
        'C13-SEL-D10-REPAIRED-EXACTMODE-A1': 'C13-SEL-D10',
    }
    original = {row['exp_id']: row for row in csv.DictReader((OLD_PACK / 'C13_COMMAND_MANIFEST.tsv').open(), delimiter='\t')}
    out = []
    for repaired, old in old_by_repaired.items():
        old_log = Path(original[old]['output_dir']) / 'run.log'
        old_final = audit.final_counters(old_log)
        new = arms[repaired]['final']
        for field in ('gpu_tot_sim_cycle', 'vm_l2_tlb_misses', 'vm_translation_walk_starts', 'vm_pte_dram_responses'):
            out.append({'old_mode1_id': old, 'repaired_mode0_id': repaired, 'metric': field,
                        'old_mode1_value': old_final.get(field, 'NOT_EMITTED'),
                        'repaired_mode0_value': new.get(field, 'NOT_EMITTED'),
                        'repaired_minus_old': fmt(int(new[field]) - int(old_final[field])) if field in new and field in old_final else 'NOT_EMITTED',
                        'boundary': 'ENGINEERING_POSTMORTEM_ONLY_NOT_SUBENTRY_SCIENCE'})
    return out


def reports(arms: dict[str, dict], latency: list[dict[str, object]], capacity: list[dict[str, object]], selective: list[dict[str, object]], kernel691: list[dict[str, object]]) -> None:
    h3 = {row['point_id']: row for row in latency}
    cap_cycles = next(row for row in capacity if row['metric'] == 'gpu_tot_sim_cycle')
    sp = {row['roi']: row for row in selective}
    k691 = next(row for row in kernel691 if row['point_id'] == 'C13-SEL-P10-REPAIRED-EXACTMODE-A1')
    text = ['# C13 effective-config audit — Path A final report', '',
            'Status: `C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`', '',
            '## Root cause and supersession', '',
            'C13 MANUAL config synthesis inherited `gpgpu_vm_l2_tlb_mode=1`; MANUAL does not apply F7\'s internal exact-mode override.  Independent last-option folding and raw final telemetry confirm mode 1 for all original nine C13 rows.  They remain immutable engineering evidence but are `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16` for H1/H2/H3.',
            'All repaired configs explicitly end in `gpgpu_vm_l2_tlb_mode 0`; their receipts prove intended entries, associativity/sets, Segment state, binary/Core, frozen trace/registration and exclusion-map provenance.  EQ1 reproduces C12 F7-L10 under C12 binary MANUAL exact mode; EQ2 reproduces EQ1 under new binary empty exclusion.  Equivalence is exact for kernel markers/cycles and modeled `gpu_*`/`vm_*` counters; only `gpu_total_sim_rate` is excluded because it is derived from host wall-clock time rather than simulated state.  Only then were repaired results promoted.', '',
            '## MEASURED_C13_DIAGNOSTIC_FACT', '',
            '- Prefill repaired L8 delta vs F0: `%s` cycles; L9: `%s` cycles.  Measured bracket: `%s`.' % (h3['C13-LAT-P8-REPAIRED-EXACTMODE-A1']['cycle_delta_vs_f0'], h3['C13-LAT-P9-REPAIRED-EXACTMODE-A1']['cycle_delta_vs_f0'], crossover(latency, 'prefill')),
            '- Decode repaired L11 delta vs F0: `%s` cycles.  Measured bracket: `%s`.' % (h3['C13-LAT-D11-REPAIRED-EXACTMODE-A1']['cycle_delta_vs_f0'], crossover(latency, 'decode1')),
            '- Corrected capacity cycle contrasts: B-A `%s`, C-A `%s`, D-B `%s`, D-C `%s`; interaction `%s` (`DIAGNOSTIC_INTERACTION_ONLY`).' % (cap_cycles['B_minus_A'], cap_cycles['C_minus_A'], cap_cycles['D_minus_B'], cap_cycles['D_minus_C'], cap_cycles['interaction_(D-B)-(C-A)']),
            '- Corrected selective candidate-control cycle deltas: Prefill `%s`, Decode `%s`; Prefill kernel 691 delta versus same-new-binary control `%s`.' % (sp['prefill']['gpu_tot_sim_cycle_candidate_minus_control'], sp['decode1']['gpu_tot_sim_cycle_candidate_minus_control'], k691['cycle_delta_vs_newbin_control']), '',
            '## SUPPORTED_C13_MECHANISM_SIGNAL', '',
            '- Operator deltas are reported only as observed associations between exact-mode policy/configuration and cycles/translation counters.  They do not identify a unique critical path.',
            '- The tied Embedding/Output exclusion is whole-range policy, not a final-kernel special case.  H1 comparisons use same-new-binary controls only.', '',
            '## DIAGNOSTIC_INTERACTION_ONLY', '',
            '- The repaired 2×2 is non-equal-budget and local to Prefill.  Its interaction is a decomposition, not a general causal law.', '',
            '## UNRESOLVED', '',
            '- Translation/cache associations do not by themselves prove queue, DRAM, or critical-path causality.',
            '- No execution-order inference upgrades direct/semantic/heuristic/unresolved operator evidence tiers.']
    (PACK / 'FINAL_REPORT.md').write_text('\n'.join(text) + '\n')
    HANDOFF.write_text('\n'.join(text) + '\n')
    next_stage = ['# Next-stage decision (no experiment automatically started)', '',
                  '## Evidence boundary', '',
                  'These are proposals conditioned on the repaired Path-A tables.  None is launched by this document.', '',
                  '## Maximum three minimal follow-ups', '',
                  '1. **Confirm the repaired fine-latency bracket.** Hypothesis: the repaired L8/L9/L10 sign transition is stable.  Matrix: one independently fresh Prefill point at the nearest unresolved integer only if the measured bracket remains adjacent.  Acceptance: exact-mode receipt, C12-level conservation, and same frozen ROI identity.  Estimated runtime: about 14 hours.',
                  '2. **Selective-policy decision point.** Hypothesis: any repaired H1 candidate-control difference is concentrated in the tied Embedding/Output range rather than all Weight.  Matrix: at most one complementary whole-range eligibility policy plus same-new-binary control.  Acceptance: no kernel-index special case, explicit range SHA, and same-binary paired comparison.  Estimated runtime: Prefill about 14 hours plus Decode about 7 hours.',
                  '3. **Capacity × Segment replication only if the repaired interaction is material.** Hypothesis: the corrected B/C/D decomposition persists under one neighboring exact capacity.  Matrix: one no-Segment and one Segment paired Prefill point, explicitly `DIAGNOSTIC_NON_EQUAL_BUDGET`.  Acceptance: no causal claim beyond measured interaction.  Estimated runtime: two Prefill runs, about 28 aggregate wall-clock hours (or about 14 hours at 2-way).', '',
                  '## Directions to stop absent new evidence', '',
                  '- Do not invest in the original mode-1 trends as Sub-entry science; they were unintended geometry.',
                  '- Do not infer a cache/queue cause solely from translation-counter association.']
    (PACK / 'NEXT_STAGE_DECISION.md').write_text('\n'.join(next_stage) + '\n')


def update_failure_audit() -> None:
    path = OLD_PACK / 'FAILURE_RETRY_AUDIT.md'
    prior = path.read_text()
    marker = '## Path-A effective-mode supersession'
    if marker in prior:
        prior = prior.split(marker, 1)[0].rstrip() + '\n'
    prior += ('\n' + marker + '\n\n'
              'All original nine C13 rows are retained immutable but superseded for science as `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16`.  The root cause was config synthesis for `FAIR_ARM_MANUAL`: it inherited source `gpgpu_vm_l2_tlb_mode=1` and omitted a final explicit mode-0 override.  Path-A repaired configs, receipts, and terminal evidence are in `C13_EFFECTIVE_CONFIG_AUDIT/`; no original raw log was overwritten.\n')
    path.write_text(prior)


def conservation_report(arms: dict[str, dict], manifest: list[dict[str, str]]) -> str:
    by_id = {row['exp_id']: row for row in manifest}
    lines = ['# C13 Path-A repaired per-arm conservation audit', '',
             'Each row below has a terminal runtime geometry receipt, C13 terminal validator, accepted marker-map identity, exact per-kernel cycle closure, and cumulative accepted `vm_*` snapshot/delta closure.  Raw logs remain outside git.', '',
             '| arm | ROI | mode | markers | per-kernel cycle sum | full ROI cycle total | active terminal `vm_*` fields | result |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for exp_id in sorted(by_id):
        arm, row = arms[exp_id], by_id[exp_id]
        lines.append('| %s | %s | %s | %d | %d | %s | %d | PASS |' %
                     (exp_id, row['roi'], row['l2_mode'], len(arm['raw_kernels']), arm['cycle_total'],
                      arm['final'].get('gpu_tot_sim_cycle', 'NOT_EMITTED'), len(arm['raw_kernels'][-1].cumulative)))
    return '\n'.join(lines) + '\n'


def changed_files_report() -> str:
    lines = ['# C13 Path-A changed-files boundary', '',
             'Only C13-derived scripts, repaired configs, and compact review evidence are committed.  Immutable C12 assets, C13 raw logs, traces, and binaries are excluded.', '',
             '| path | role |', '| --- | --- |',
             '| `util/vm_tlb/c13_effective_config_audit.py` | static/runtime effective-geometry gate and terminal runner |',
             '| `util/vm_tlb/collect_c13_effective_config_audit.py` | strict read-only repaired evidence collector |',
             '| `configs/vm_tlb/c13_diagnostics/effective_config_audit/` | fresh final-override configs with explicit mode 0 |',
             '| `docs/.../C13_EFFECTIVE_CONFIG_AUDIT/` | compact Path-A review evidence |']
    return '\n'.join(lines) + '\n'


def main() -> None:
    arms, mapping, manifest = load()
    results = result_rows(arms, manifest)
    latency = latency_rows(arms)
    capacity = capacity_rows(arms)
    selective = selective_rows(arms)
    operator = operator_rows(arms, mapping)
    k691 = kernel691_rows(arms, mapping['prefill'])
    postmortem = old_vs_repaired(arms)
    write_tsv('SUPERSEDING_C13_RESULTS.tsv', results)
    write_tsv('ARM_RESULTS.tsv', results)
    write_tsv('ARM_STATUS.tsv', [{'exp_id': row['exp_id'], 'logical_role': row['logical_role'],
                                  'roi': row['roi'], 'terminal_status': 'PASS',
                                  'scientific_status': row['scientific_status'],
                                  'run_dir': str(audit.OUT / row['exp_id']),
                                  'raw_log_sha256': row['raw_log_sha256'],
                                  'effective_l2_mode': row['l2_mode'],
                                  'eq_gate': row['gate_status']} for row in results])
    write_tsv('LATENCY_FINE_SWEEP.tsv', latency)
    write_tsv('CAPACITY_FACTORIAL.tsv', capacity)
    write_tsv('SELECTIVE_SEGMENT_RESULTS.tsv', selective)
    write_tsv('OPERATOR_DIAGNOSTIC_DELTAS.tsv', operator)
    write_tsv('KERNEL691_DIAGNOSTIC.tsv', k691)
    write_tsv('WRONG_MODE_VS_EXACTMODE_POSTMORTEM.tsv', postmortem)
    provenance = [{key: row[key] for key in ('exp_id', 'logical_role', 'raw_log_sha256', 'config_sha256', 'binary_sha256', 'core_head', 'l2_mode', 'exact_l2_tlb_entries', 'segment_enable', 'segment_n', 'lseg', 'eligibility_policy')} for row in results]
    write_tsv('PROVENANCE_MATRIX.tsv', provenance)
    (PACK / 'CONSERVATION_AUDIT.md').write_text(conservation_report(arms, manifest))
    (PACK / 'CHANGED_FILES.md').write_text(changed_files_report())
    reports(arms, latency, capacity, selective, k691)
    update_failure_audit()
    print('C13_PATH_A_FINAL_COLLECTION_PASS\trows=%d' % len(results))


if __name__ == '__main__':
    main()
