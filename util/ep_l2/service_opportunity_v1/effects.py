#!/usr/bin/env python3
"""Arithmetic for a Lane5-reviewed endpoint export; not a qualifier/launcher.

Input is matched_endpoints_TEMPLATE.json filled from one qualified release.
Lane5 must bind each endpoint to the latest immutable acceptance publication,
effective dump, same-background config projection, raw and independent review.
This calculator does not turn a filled template into scientific acceptance.
"""
import argparse
import json
from pathlib import Path

ARCHITECTURES = ('B16', 'S64', 'Unified')
IDENTITY = ('core', 'framework', 'binary', 'trace', 'epoch_range', 'condition',
            'non_mechanism_config_projection_sha256')


def ratios(cycles, off):
    for values in (cycles, off):
        assert set(values) == set(ARCHITECTURES)
        assert all(type(v) is int and v > 0 for v in values.values())
    ep = cycles['B16'] / cycles['Unified']
    static = cycles['S64'] / cycles['Unified']
    return dict(C_B=cycles['B16'], C_S64=cycles['S64'], C_U=cycles['Unified'],
                S_EP=ep, S_static=static,
                interaction_EP_vs_OFF=ep / (off['B16'] / off['Unified']),
                interaction_static_vs_OFF=static / (off['S64'] / off['Unified']),
                absolute_speedup_B_vs_OFF=off['B16'] / cycles['B16'],
                absolute_speedup_S64_vs_OFF=off['S64'] / cycles['S64'],
                absolute_speedup_U_vs_OFF=off['Unified'] / cycles['Unified'])


def calculate(rows):
    results = []
    for work in sorted({r['workload'] for r in rows}):
        for optimization in ('OFF', 'MQ2', 'RG1'):
            cell = [r for r in rows if r['workload'] == work and r['optimization'] == optimization]
            off = [r for r in rows if r['workload'] == work and r['optimization'] == 'OFF']
            base = dict(workload=work, optimization=optimization)
            needed = cell + off
            if len(cell) != 3 or len(off) != 3 or any(r.get('status') != 'LANE5_CURRENT_ACCEPTED_EXPORT' or r.get('cycles') is None for r in needed):
                results.append(dict(base, status='PENDING_NO_ACCEPTED_MATCHED_EXPORT', cycles=None))
                continue
            assert {r['architecture'] for r in cell} == {r['architecture'] for r in off} == set(ARCHITECTURES)
            # Architecture changes only the reviewed architectural projection;
            # mechanism changes only the declared switch projection. All other
            # input, source, clock, queue and timing controls remain matched.
            for key in IDENTITY:
                assert all(r.get(key) for r in needed), 'missing identity: ' + key
                assert len({str(r[key]) for r in needed}) == 1, 'unmatched identity: ' + key
            for key in ('config', 'effective_config_sha256', 'qualification_receipt', 'source_run_key', 'raw_sha256', 'acceptance_generation'):
                assert all(r.get(key) is not None for r in needed), 'missing reviewed provenance: ' + key
            assert len({r['acceptance_generation'] for r in needed}) == 1
            assert len({r['instructions'] for r in needed}) == 1 and all(r['instructions'] > 0 for r in needed)
            result = ratios({r['architecture']: r['cycles'] for r in cell}, {r['architecture']: r['cycles'] for r in off})
            results.append(dict(base, **result, status='ARITHMETIC_ONLY_REQUIRES_CURRENT_LANE5_REVIEW', binary=cell[0]['binary']))
    return results


def self_check():
    # Synthetic arithmetic only: a common 2x gain leaves EP interaction at one.
    off = dict(B16=200, S64=180, Unified=160)
    common = ratios(dict(B16=100, S64=90, Unified=80), off)
    assert common['interaction_EP_vs_OFF'] == 1 and common['absolute_speedup_U_vs_OFF'] == 2
    negative = ratios(dict(B16=210, S64=189, Unified=176), off)
    assert negative['absolute_speedup_U_vs_OFF'] < 1 and negative['interaction_EP_vs_OFF'] < 1
    zero = ratios(off, off)
    assert zero['interaction_EP_vs_OFF'] == 1
    rows = []
    for opt in ('OFF', 'MQ2', 'RG1'):
        for arch in ARCHITECTURES:
            rows.append(dict(workload='SYNTHETIC_NOT_MEASURED', optimization=opt, architecture=arch,
                status='LANE5_CURRENT_ACCEPTED_EXPORT', cycles=off[arch], instructions=100,
                **{key: 'synthetic' for key in IDENTITY}, config='synthetic', effective_config_sha256='synthetic',
                qualification_receipt='synthetic', source_run_key=opt + arch, raw_sha256='synthetic', acceptance_generation=1))
    assert len(calculate(rows)) == 3
    for key in ('binary', 'trace', 'non_mechanism_config_projection_sha256', 'acceptance_generation'):
        altered = [dict(r) for r in rows]
        altered[-1][key] = 'UNMATCHED'
        try:
            calculate(altered)
        except AssertionError:
            pass
        else:
            raise AssertionError('failed to reject ' + key)
    for r in rows:
        r['status'] = 'WITHDRAWN'
    assert all(r['status'].startswith('PENDING') for r in calculate(rows))
    return dict(status='PASS_SYNTHETIC_ARITHMETIC_AND_IDENTITY_GUARDS', measured_endpoints=0,
                common_gain_is_not_EP_interaction=True, negative_retained=True, withdrawal_quarantined=True,
                mismatched_binary_trace_background_generation_rejected=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoints', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    result = self_check() if args.self_check else calculate(json.loads(args.endpoints.read_text()))
    args.out.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
