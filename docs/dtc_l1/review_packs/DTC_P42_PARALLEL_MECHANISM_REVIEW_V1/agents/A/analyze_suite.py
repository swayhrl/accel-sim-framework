"""Read-only reproduction of frozen original 23-input statistics. No simulator imports."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

BASE_COMMIT = '71584878be0c80375f9d25bcd80e171b7bf4478d'
PREFIX = 'docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1'
METRICS = {
    'CH/DH': ('CH', 'DH', 'DTC_hashed_CH_DH'),
    'CM/DM': ('CM', 'DM', 'DTC_linear_CM_DM'),
    'DM/DH': ('DM', 'DH', 'DTC_hash_DM_DH'),
    'CM/CH': ('CM', 'CH', 'traditional_hash_CM_CH'),
}
SUITES = ['PolyBench/GPU', 'Rodinia', 'CUDA Samples', 'Parboil']
HIGH = ['2DCONV', '3DCONV', '3MM', 'GEMM', 'particlefilter_naive']
checks = []


def check(condition, label):
    checks.append({'check': label, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def gm(values):
    return math.exp(math.fsum(math.log(v) for v in values) / len(values)) if values else None


def stats(rows, metric):
    vals = [r['ratios'][metric] for r in rows]
    if not vals:
        return {'n': 0, 'GM': None, 'median': None, 'positive': 0, 'zero': 0, 'negative': 0}
    return {'n': len(vals), 'GM': gm(vals), 'median': statistics.median(vals),
            'positive': sum(v > 1 for v in vals), 'zero': sum(v == 1 for v in vals),
            'negative': sum(v < 1 for v in vals), 'min': min(vals), 'max': max(vals),
            'sum_log_ratios': math.fsum(math.log(v) for v in vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-dir', type=Path, default=Path('D:/repo/tmp'))
    ap.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    inputs = {}
    for key, filename in [('performance', 'DTC_P42_PERFORMANCE.json'), ('ledger', 'DTC_P42_LEDGER_AUDIT.json'),
                          ('freeze', 'DTC_P42_REPRESENTATIVE_FREEZE.json'), ('model', 'DTC_P42_MODEL_COMPARABILITY.json')]:
        path = args.input_dir / filename
        inputs[key] = {'path': str(path), 'sha256': sha(path), 'content': json.loads(path.read_text(encoding='utf-8'))}
    p, ledger, freeze, model = [inputs[x]['content'] for x in ['performance', 'ledger', 'freeze', 'model']]
    check(inputs['freeze']['sha256'] == p['freeze_sha256'], 'identity freeze exact bytes match performance freeze SHA')
    ld = {r['input_digest']: r for r in ledger['current_original']}
    fr = {r['program']: r for r in freeze['programs_44_to_42']}
    source_records = ledger['source_records']
    rows = []
    for row in p['table_42']:
        if not row['four_accepted']:
            continue
        check(row['program'] in p['common_panel_programs'], 'common panel member ' + row['program'])
        digest = row['input_digest']
        check(fr[row['program']]['selected_input_digest'] == digest, 'frozen digest ' + row['program'])
        evidence = {}
        for mode in ['CM', 'CH', 'DM', 'DH']:
            m, old = row['modes'][mode], ld[digest]['modes'][mode]
            strict, result, done, spec, launch = [old[k] for k in ['strict', 'result', 'DONE', 'spec', 'launch']]
            check(m['state'] == 'ACCEPTED_ORIGINAL' and m['accepted'], 'original accepted ' + m['cohort'])
            check(strict['performance_accepted'] and strict['status'] == 'PASS_FULL_NATIVE_STRICT_BOUNDED_MODEL', 'strict identity ' + m['cohort'])
            check(m['accepted_cycles'] == strict['cycles'] == result['cycles'], 'triple cycles match ' + m['cohort'])
            check(m['uuid'] == done['uuid'] == strict['uuid'] == old['uuid'], 'UUID join ' + m['cohort'])
            check(m['raw_gzip_sha256'] == done['raw_sha256'] == strict['raw_sha256'], 'raw gzip SHA join ' + m['cohort'])
            check(m['raw_uncompressed_sha256'] == done['raw_uncompressed_sha256'], 'raw uncompressed SHA join ' + m['cohort'])
            check(result['archive']['status'] == 'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET', 'archive and native restore ' + m['cohort'])
            check(m['strict_core'] == strict['core_commit'] and m['strict_framework'] == strict['framework_commit'] and m['strict_binary'] == strict['binary_sha256'], 'actual build join ' + m['cohort'])
            root = Path(m['output']).as_posix()
            paths = {
                'accepted_result': m['result_path'], 'strict': m['strict_path'],
                'DONE': '/root/data/dtc_main_v100_sweep_20261025_v1/control/qualification_ledger/' + m['cohort'] + '.DONE.json',
                'original_spec': '/root/data/dtc_main_v100_sweep_20261025_v1/control/' + m['cohort'] + '_SPEC.json',
                'archive_receipt': '/root/data/dtc_main_v100_sweep_20261025_v1/control/' + m['cohort'] + '_ARCHIVE_RECEIPT.json',
                'actual_launch': root + '/NATIVE_LAUNCH.json', 'raw_counters': root + '/raw.log.gz',
            }
            refs = {k: {'path': path, **source_records.get(path, {})} for k, path in paths.items()}
            # Original specs retain historical declarations across an authorized observational rebind.
            # Actual identity is strict raw and actual launch, never overwritten by that old declaration.
            runtime = launch.get('operational_resource_profile', {})
            argv = launch['argv']
            actual_configs = [argv[i + 1] for i, a in enumerate(argv) if a == '-config']
            check(actual_configs == [c['path'] for c in spec['configs']], 'actual config paths match frozen spec ' + m['cohort'])
            check(len(actual_configs) == 4, 'four actual config files ' + m['cohort'])
            if runtime.get('framework_commit'):
                check(runtime['framework_commit'] == strict['framework_commit'], 'actual operational profile framework ' + m['cohort'])
                check(runtime['framework_binary']['sha256'] == strict['binary_sha256'], 'actual operational profile binary ' + m['cohort'])
            evidence[mode] = {
                'input_digest': digest, 'cohort': m['cohort'], 'uuid': m['uuid'], 'accepted_cycles': m['accepted_cycles'],
                'state': m['state'], 'strict_status': strict['status'], 'references': refs,
                'raw_gzip_sha256': done['raw_sha256'], 'raw_uncompressed_sha256': done['raw_uncompressed_sha256'],
                'actual_core_commit': strict['core_commit'], 'actual_framework_commit': strict['framework_commit'],
                'actual_binary_sha256': strict['binary_sha256'],
                'historical_spec_framework_commit': spec['framework_commit'], 'historical_spec_binary_sha256': spec['binary_sha256'],
                'actual_vs_historical_spec_build_different': strict['binary_sha256'] != spec['binary_sha256'],
                'original_configs': spec['configs'], 'actual_config_paths': actual_configs,
                'effective_resolved_options': strict['effective_options'],
                'effective_options_canonical_sha256': canonical_sha(strict['effective_options']),
                'archive': result['archive'], 'kernel_counter_locations': strict['kernels'],
                'raw_counter_definition': 'Final total GPU cycles from raw gpu_tot_sim_cycle; per-kernel entries from terminal kernel summaries. Ratio uses total accepted cycles, not host elapsed time.',
            }
        cycles = {m: evidence[m]['accepted_cycles'] for m in evidence}
        ratios = {k: cycles[a] / cycles[b] for k, (a, b, _) in METRICS.items()}
        ratios['relative_improvement'] = ratios['CH/DH'] / ratios['CM/DM']
        for key, (_, _, oldkey) in METRICS.items():
            check(abs(ratios[key] - row['ratios'][oldkey]) < 1e-13, 'recompute ratio ' + row['program'] + ' ' + key)
        rows.append({'program': row['program'], 'program_id': row['program_id'], 'suite': row['suite'],
                     'input_digest': digest, 'selected_trace_entry': fr[row['program']]['selected_trace_entry'],
                     'capture_scope': row['capture_scope'], 'source_version': row['source_version'],
                     'parameters': row['parameters'], 'cycles': cycles, 'ratios': ratios, 'cells': evidence,
                     'same_exact_build': row['same_exact_build_four_cells']})
    check(len(rows) == 23, 'exact 23 original complete inputs')
    check(len({r['input_digest'] for r in rows}) == 23, 'unique 23 input digests')
    check({r['program'] for r in rows} == set(p['common_panel_programs']), 'no added or removed panel members')
    overall = {k: stats(rows, k) for k in METRICS}
    overall['relative_improvement'] = stats(rows, 'relative_improvement')
    for k, (_, _, oldkey) in METRICS.items():
        check(abs(overall[k]['GM'] - p['statistics_common_panel'][oldkey]['GM']) < 1e-13, 'original published GM exact reproduction ' + k)
    suite_stats = {}
    for suite in SUITES:
        full = [r for r in p['table_42'] if r['suite'] == suite]
        complete = [r for r in rows if r['suite'] == suite]
        suite_stats[suite] = {
            'ordinary_target': len(full), 'identity_frozen': sum(r['selection_state'] == 'IDENTITY_FROZEN' for r in full),
            'UNRESOLVED': sum(r['selection_state'] == 'UNRESOLVED' for r in full), 'complete_original_four': len(complete),
            'complete_target_coverage': len(complete) / len(full),
            'accepted_selected_cells': sum(m['accepted'] for r in full for m in r['modes'].values()),
            'missing_programs': [r['program'] for r in full if not r['four_accepted']],
            'statistics': {k: stats(complete, k) for k in METRICS},
        }
    contributions = {}
    for metric in METRICS:
        total = overall[metric]['sum_log_ratios']
        positive = math.fsum(max(0, math.log(r['ratios'][metric])) for r in rows)
        negative = math.fsum(min(0, math.log(r['ratios'][metric])) for r in rows)
        entries = []
        for r in rows:
            value = math.log(r['ratios'][metric])
            entries.append({'program': r['program'], 'input_digest': r['input_digest'], 'ratio': r['ratios'][metric],
                            'log_ratio': value, 'contribution_to_mean_log_ratio': value / 23,
                            'multiplicative_factor_in_GM': math.exp(value / 23),
                            'fraction_of_net_log_gain': value / total if total else None,
                            'fraction_of_positive_log_gain': max(0, value) / positive if positive else None,
                            'leave_one_out_GM': gm([x['ratios'][metric] for x in rows if x['program'] != r['program']])})
        contributions[metric] = {'total_log_gain': total, 'positive_log_gain': positive, 'negative_log_gain': negative,
                                 'programs': sorted(entries, key=lambda e: e['log_ratio'], reverse=True)}
    sensitivity_sets = {
        'all_23_FORMAL_FROZEN_PANEL': [],
        'leave_out_2DCONV_DIAGNOSTIC_ONLY': ['2DCONV'],
        'leave_out_named_high_five_DIAGNOSTIC_ONLY': HIGH,
        'leave_out_particlefilter_float_exact_build_sensitivity_ONLY': ['particlefilter_float'],
    }
    sens = {}
    for label, excluded in sensitivity_sets.items():
        subset = [r for r in rows if r['program'] not in excluded]
        sens[label] = {'excluded_for_sensitivity_only': excluded, 'n': len(subset), 'statistics': {k: stats(subset, k) for k in METRICS}}
    high_log = math.fsum(math.log(r['ratios']['CH/DH']) for r in rows if r['program'] in HIGH)
    rest = [r for r in rows if r['program'] not in HIGH]
    missing_by_name = {r['program']: r for r in p['missing_19_or_current']}
    missing_states = collections.Counter()
    for r in p['table_42']:
        if r['selection_state'] != 'IDENTITY_FROZEN':
            continue
        for mode in ['CM', 'CH', 'DM', 'DH']:
            state = r['modes'].get(mode, {}).get('state')
            if state is None:
                state = missing_by_name[r['program']]['cells'][mode]
            missing_states[state] += 1
    check(sum(missing_states.values()) == 140, 'all140 selected cells include four unadmitted cutcp cells')
    result = {
        'schema': 'DTC_P42_AGENT_A_SUITE_PERFORMANCE_ANALYSIS_V1', 'base_framework_commit': BASE_COMMIT,
        'base_review_prefix': PREFIX, 'input_sources': {k: {a: b for a, b in v.items() if a != 'content'} for k, v in inputs.items()},
        'original_snapshot_CST': p['ledger_snapshot_observed_CST'], 'freeze_sha256': p['freeze_sha256'],
        'scope': 'Frozen 23 original complete four-configuration inputs only; no repair or downstream18 substitutions. All negative/zero results retained.',
        'metric_contract': {'ratio': 'numerator accepted total GPU model cycles / denominator accepted total GPU model cycles; >1 means denominator faster',
                            'GM': 'exp(mean(log(ratio))); equal weight per program, not per kernel/instruction/runtime/suite',
                            'sign': 'exact >1, ==1, <1; no practical-significance tolerance',
                            'contribution': 'log(r_i)/23 is the additive contribution to log GM; exp(log(r_i)/23) is the multiplicative factor. Net-log shares can exceed 100% because negative programs offset positive ones.',
                            'missing': 'Never zero or one; no imputation or repaired-cycle substitution.'},
        'coverage': p['coverage'], 'selected_cell_states': dict(missing_states), 'suite_statistics': suite_stats,
        'overall_statistics': overall, 'programs': rows, 'contributions': contributions, 'sensitivity': sens,
        'named_high_five_CH_DH': {'programs': HIGH, 'log_gain': high_log,
                                 'fraction_of_net_log_gain': high_log / overall['CH/DH']['sum_log_ratios'],
                                 'fraction_of_positive_log_gain': high_log / contributions['CH/DH']['positive_log_gain'],
                                 'remaining_18_statistics': stats(rest, 'CH/DH')},
        'missing_19': p['missing_19_or_current'],
        'limitations': [p['full_application_source_capture_scope_limit'],
                        'Complete-case availability is not random: failures, telemetry closure/resource-policy failures, pending runs and unresolved source versions are missing. No inference to the 42-program population or to workloads in general.',
                        'Observational Framework cap-only equivalence is inherited from MODEL_COMPARABILITY; particlefilter_float crosses the two Framework/binary variants. Exact-build sensitivity is diagnostic, never silently removes this negative case.',
                        'Traditional96KiB/768lines versus DTC80KiB/640physical128B lines/512logicalTags, different PIB/finite-service structures and timing mean this is not area/capacity matched. Same Hash family does not make the whole designs matched.',
                        'Ratios identify behavior, not hardware causation. Other agents audit counter semantics and microarchitectural attribution; no dominant mechanism is asserted from ratios alone.'],
        'new_simulator_starts': 0, 'original_ledger_changed': False, 'frozen_identity_changed': False,
    }
    (out / 'SUITE_PERFORMANCE_ANALYSIS.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    report(result, out)
    plot(result, out)
    check(all(c['pass'] for c in checks), 'all preceding checks pass')
    (out / 'VALIDATION.json').write_text(json.dumps({'status': 'PASS', 'checks': len(checks), 'records': checks,
              'original_cells': 92, 'new_simulator_starts': 0}, indent=2) + '\n', encoding='utf-8')
    manifest = {f.name: {'sha256': sha(f), 'bytes': f.stat().st_size} for f in sorted(out.iterdir()) if f.is_file() and f.name != 'MANIFEST.json'}
    (out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'overall': overall, 'suites': suite_stats, 'high_five': result['named_high_five_CH_DH'],
                       'sensitivity': sens, 'checks': len(checks)}, indent=2))


def report(data, out):
    lines = ['# Frozen 23-input suite performance and contribution analysis', '',
             'Base review commit: `' + BASE_COMMIT + '`. Freeze SHA: `' + data['freeze_sha256'] + '`.', '',
             '**Scope: 23 complete original four-configuration inputs, 54.76% of the 42 ordinary-program target; this is not a 42-program aggregate.** All historical failures, missing cells, zero and negative performance cases remain visible. The 18 current downstream experiments and all repair-validation runs are excluded.', '',
             '## Statistical contract', '',
             'Every ratio is numerator GPU model cycles divided by denominator GPU model cycles. Above one favors the denominator design. GM is equally weighted per program. Zero benefit means exactly equal accepted cycles. Runtime and performance did not select these identities. No missing value is imputed.', '',
             '## Overall original panel', '',
             '| Metric | N | GM | Median | Positive / zero / negative |', '|---|---:|---:|---:|---:|']
    for metric, st in data['overall_statistics'].items():
        lines.append(f"| {metric} | {st['n']} | {st['GM']:.6f} | {st['median']:.6f} | {st['positive']} / {st['zero']} / {st['negative']} |")
    lines += ['', '## Suite coverage and comparisons', '', '| Suite | Complete / target | Frozen / unresolved | CH/DH GM (median; +/0/−) | CM/DM GM | DM/DH GM | CM/CH GM |', '|---|---:|---:|---:|---:|---:|---:|']
    for suite, v in data['suite_statistics'].items():
        s = v['statistics']; h = s['CH/DH']
        lines.append(f"| {suite} | {v['complete_original_four']}/{v['ordinary_target']} ({100*v['complete_target_coverage']:.2f}%) | {v['identity_frozen']}/{v['UNRESOLVED']} | {h['GM']:.6f} ({h['median']:.6f}; {h['positive']}/{h['zero']}/{h['negative']}) | {s['CM/DM']['GM']:.6f} | {s['DM/DH']['GM']:.6f} | {s['CM/CH']['GM']:.6f} |")
    lines += ['', 'All four metrics have identical within-suite members. JSON provides all four medians, signs, ranges, program membership and per-cell evidence. The overall GM weights 23 programs equally; it is not the equal mean of four suite GMs.', '',
              '## Full per-program performance and log-GM contribution', '',
              '| Program | Suite | CH/DH | CM/DM | DM/DH | CM/CH | CH/DH net-log contribution | Leave-one-out CH/DH GM |', '|---|---|---:|---:|---:|---:|---:|---:|']
    contrib = {c['program']: c for c in data['contributions']['CH/DH']['programs']}
    for r in data['programs']:
        c = contrib[r['program']]; v = r['ratios']
        lines.append(f"| {r['program']} | {r['suite']} | {v['CH/DH']:.6f} | {v['CM/DM']:.6f} | {v['DM/DH']:.6f} | {v['CM/CH']:.6f} | {100*c['fraction_of_net_log_gain']:.2f}% | {c['leave_one_out_GM']:.6f} |")
    lines += ['', 'Contribution is log(ratio)/sum(log(ratios)), not a share of saved wall time. Negative contributions offset positives; percentages can exceed 100%. Full input digests and four accepted cycles are in the identity appendix below and JSON.', '',
              '## High-gain cases and concentration', '',
              '- **2DCONV:** CH/DH=3.347255 while CM/DM=3.314588. The DTC gain exists before Hash; DTC Hash adds only 1.6608%, conventional Hash 0.6686%, and relative advantage improves 0.9856%. This ratio evidence rules out attributing its whole 3.35x gain to Hash, but cannot identify a particular DTC mechanism.',
              '- **3DCONV:** CH/DH=1.344380, CM/DM=1.323365, DM/DH=1.015880 and CM/CH=1. Its main observed benefit likewise precedes Hash.',
              '- **3MM/GEMM:** DTC Hash improves 1.313668x/1.296961x, compared with conventional Hash 1.101613x/1.083225x. Relative DTC advantage improves 1.192495x/1.197314x. Mapping sensitivity contributes appreciably, while pre-Hash DTC gains of 1.462780x/1.410609x also remain.',
              '- **particlefilter_naive:** CM=CH and DM=DH exactly, with CH/DH=CM/DM=1.329003. Hash contributes no cycle change in this frozen input; the remaining design differences require separate causal evidence.', '',
              'These are arithmetic decompositions, not isolated causal interventions on the full design. Counter/source attribution belongs to Agent C.', '']
    h = data['named_high_five_CH_DH']; n = h['remaining_18_statistics']
    lines += [f"The five named cases supply **{100*h['fraction_of_net_log_gain']:.2f}% of the net CH/DH log gain**, or **{100*h['fraction_of_positive_log_gain']:.2f}% of positive log gain before negative cases**. The other 18 have CH/DH GM **{n['GM']:.6f}**, median **{n['median']:.6f}**, with {n['positive']} positive and {n['negative']} negative cases. The formal panel remains all 23.", '',
              '## Diagnostic sensitivity (never an alternative selected main set)', '', '| Sensitivity | N | CH/DH GM | CM/DM GM | DM/DH GM | CM/CH GM |', '|---|---:|---:|---:|---:|---:|']
    for name, case in data['sensitivity'].items():
        st = case['statistics']
        lines.append(f"| {name} | {case['n']} | {st['CH/DH']['GM']:.6f} | {st['CM/DM']['GM']:.6f} | {st['DM/DH']['GM']:.6f} | {st['CM/CH']['GM']:.6f} |")
    lines += ['', 'The particlefilter_float diagnostic preserves the published 22 same-exact-build sensitivity; it does not justify dropping an unfavorable benchmark. All 23 leave-one-out results and contributions for every metric are in JSON.', '',
              '## Negative cases and small gains', '',
              'Five CH/DH negative cases are retained: MVT 0.766303, particlefilter_float 0.885882, ATAX 0.891739, BICG 0.916784, and sad 0.995125. ATAX/MVT/BICG improve with DTC Hash but remain slower than their matched CH design. A better relative response to Hash is not the same as DTC beating CH.', '',
              'Most remaining gains are small: BlackScholes 0.245%, mri-q 0.575%, dwt2d 0.848%; lud/transpose approximately1.5%; mergeSort/heartwall approximately2.5–2.7%; convolutionSeparable/histogram/fastWalshTransform approximately3.1–3.5%; sgemm/srad approximately9.6–9.8%. Ratios alone do not establish a mechanism or meaningful real-hardware significance. Hash changes both designs by almost nothing for several of these. No equivalence or reproducibility error bars are inferred from one deterministic model run.', '',
              '## Missingness and selection bias', '',
              'There are 35 frozen identities, of which 12 lack an original accepted complete four-cell result, plus seven unresolved identities. The 140 selected cells contain111 accepted originals. Missingness is tied to telemetry-closure, resource/guard, receipt, admission and pending status; source-version ambiguity excludes seven programs. This is an availability-conditioned panel, not a random sample. The direction or magnitude of its bias cannot be estimated without the missing legal evidence. Do not extrapolate 1.123867x to42 programs, and do not convert a failure into a slowdown or neutral result.', '',
              '| Missing program | Identity | Four cell states CM / CH / DM / DH |', '|---|---|---|']
    for r in data['missing_19']:
        lines.append('| ' + r['program'] + ' | ' + r['selection_state'] + ' | ' + ' / '.join(r['cells'][m] for m in ['CM', 'CH', 'DM', 'DH']) + ' |')
    lines += ['', '## Identity and evidence appendix', '',
              'Every row below maps to `programs[i].cells[CM|CH|DM|DH]` in SUITE_PERFORMANCE_ANALYSIS.json, containing actual Core/Framework/binary identities; all four configuration path/SHA records and resolved options; cohort/UUID; accepted-result, strict, DONE and archive receipt paths/SHA; raw compressed/uncompressed SHA; original kernel counter locations; 164 archive and native restore receipt. Historical declared spec builds are stored separately from actual strict/launch builds. Some authorized observational cap-only rebinds retain an older spec declaration; that is not the actual binary identity.', '',
              '| Program | Full input digest | CM cycles | CH cycles | DM cycles | DH cycles |', '|---|---|---:|---:|---:|---:|']
    for r in data['programs']:
        c = r['cycles']; lines.append(f"| {r['program']} | `{r['input_digest']}` | {c['CM']} | {c['CH']} | {c['DM']} | {c['DH']} |")
    lines += ['', '## Limits and reproducibility', '']
    lines += ['- ' + l for l in data['limitations']]
    lines += ['', 'Reproduce: `python analyze_suite.py --input-dir <directory_with_the_four_hashed_snapshots> --output-dir <independent_output_directory>`. Plot dependencies must already be available; the script does not install packages. All file input SHA and the baseline commit are recorded in JSON. This analysis reads local closed snapshots only, scans no trace and starts no model. English manuscript v0.23 is unchanged.', '',
              'Figures: `performance_by_suite.png/.svg`, `log_gain_contributions.png/.svg`, and `coverage.png/.svg`. Labels and captions explicitly identify23 complete original inputs, retain negative cases and distinguish diagnostic exclusions.']
    (out / 'SUITE_PERFORMANCE_ANALYSIS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def plot(data, out):
    deps = Path('D:/repo/tmp/dtc_p42_plot_deps')
    if deps.exists():
        sys.path.insert(0, str(deps))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FuncFormatter
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'svg.fonttype': 'none',
                         'savefig.bbox': 'tight', 'axes.spines.right': False, 'axes.spines.top': False})
    colors = {'CH/DH': '#145a86', 'CM/DM': '#c26a22', 'DM/DH': '#29957b', 'CM/CH': '#8159a3'}
    fig, axes = plt.subplots(2, 2, figsize=(12, 6.6), sharey=True)
    for ax, suite in zip(axes.flat, SUITES):
        rows = [r for r in data['programs'] if r['suite'] == suite]
        xx = np.arange(len(rows))
        for offset, metric in enumerate(METRICS):
            ax.bar(xx + (offset - 1.5) * .18, [r['ratios'][metric] for r in rows], width=.17, label=metric, color=colors[metric])
        ax.axhline(1, color='#444444', linewidth=.8, linestyle='--')
        ax.set_yscale('log'); ax.set_ylim(.55, 3.8)
        ax.set_yticks([.6, .8, 1, 1.5, 2, 3]); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
        ax.set_xticks(xx, [r['program'] for r in rows], rotation=37, ha='right')
        cov = data['suite_statistics'][suite]
        ax.set_title(f"{suite}: {len(rows)}/{cov['ordinary_target']} ordinary targets")
        ax.grid(axis='y', alpha=.15)
    axes[0, 0].legend(ncols=4, fontsize=8, loc='upper right')
    for ax in axes[:, 0]: ax.set_ylabel('Cycle ratio (log scale; >1 favors denominator)')
    fig.suptitle('23 frozen original complete inputs: all four matched cycle-ratio comparisons', fontsize=12)
    fig.text(.5, -.025, 'Availability-conditioned trace-contract panel; not a 42-program aggregate. No repair or downstream18 data.', ha='center', fontsize=9)
    fig.tight_layout()
    savefig(fig, out, 'performance_by_suite')
    entries = data['contributions']['CH/DH']['programs']
    fig, ax = plt.subplots(figsize=(11, 6.2))
    vals = [100*e['contribution_to_mean_log_ratio'] for e in entries]
    ax.barh([e['program'] for e in entries], vals, color=['#145a86' if v > 0 else '#b54b44' for v in vals])
    ax.invert_yaxis(); ax.axvline(0, color='#333', linewidth=.8)
    ax.set_xlabel('Contribution to log(CH/DH GM), multiplied by 100 (not percent cycle savings)')
    ax.set_title('Contribution concentration: formal panel retains all 23 inputs')
    ax.grid(axis='x', alpha=.15)
    for i, e in enumerate(entries):
        v = vals[i]; ax.text(v + (.025 if v > 0 else -.025), i, f"{e['ratio']:.3f}x", va='center', ha='left' if v > 0 else 'right', fontsize=8)
    ax.margins(x=.13)
    top_share = 100 * data['named_high_five_CH_DH']['fraction_of_net_log_gain']
    fig.text(.5, -.01, f'GM=1.123867x; largest five explain {top_share:.1f}% of net log gain because regressions offset positives.', ha='center', fontsize=9)
    fig.tight_layout(); savefig(fig, out, 'log_gain_contributions')
    fig, ax = plt.subplots(figsize=(8, 3.8))
    yy = np.arange(4)
    complete = [data['suite_statistics'][s]['complete_original_four'] for s in SUITES]
    incomplete = [data['suite_statistics'][s]['identity_frozen'] - c for s, c in zip(SUITES, complete)]
    unresolved = [data['suite_statistics'][s]['UNRESOLVED'] for s in SUITES]
    ax.barh(yy, complete, color='#145a86', label='Complete original four cells')
    ax.barh(yy, incomplete, left=complete, color='#d79a44', label='Frozen, incomplete original cells')
    ax.barh(yy, unresolved, left=[a+b for a,b in zip(complete,incomplete)], color='#bdbdbd', label='Identity unresolved')
    for i,(c,n,u) in enumerate(zip(complete,incomplete,unresolved)):
        if c: ax.text(c/2,i,str(c),ha='center',va='center',color='white')
        if n: ax.text(c+n/2,i,str(n),ha='center',va='center')
        if u: ax.text(c+n+u/2,i,str(u),ha='center',va='center')
    ax.set_yticks(yy, SUITES);ax.invert_yaxis();ax.set_xlabel('Ordinary program slots (total 42)')
    ax.set_title('Coverage: 23 complete, 12 frozen incomplete, 7 unresolved')
    ax.legend(loc='upper center', bbox_to_anchor=(.5,-.18),ncols=1,frameon=False)
    ax.set_xticks(range(0,18,2));fig.tight_layout();savefig(fig,out,'coverage')


def savefig(fig, out, name):
    fig.savefig(out/(name+'.svg'))
    fig.savefig(out/(name+'.png'), dpi=240)
    import matplotlib.pyplot as plt
    plt.close(fig)


if __name__ == '__main__':
    main()
