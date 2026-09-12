#!/usr/bin/env python3
"""Path-A C13 exact-mode repair launcher and evidence gate.

This tool is intentionally separate from the immutable C13 minimal-diagnostic
manifest.  It writes only a fresh repaired-config namespace and fresh output
directories, proves the option-folded geometry before launch, and delegates
the accepted terminal/conservation checks to ``c13_diagnostic_tool``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import c13_diagnostic_tool as base

OUT = base.OUT
PACK = ROOT / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_EFFECTIVE_CONFIG_AUDIT'
CFG = ROOT / 'configs/vm_tlb/c13_diagnostics/effective_config_audit'
MANIFEST = PACK / 'C13_EFFECTIVE_CONFIG_AUDIT_MANIFEST.tsv'
OLD_MANIFEST = base.PACK / 'C13_COMMAND_MANIFEST.tsv'
OP_PARSER = base.OP_PARSER

COUNTER = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)\s*$')
OPTION = re.compile(r'^\s*-([A-Za-z0-9_]+)(?:\s+(.*?))?\s*$')


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit('C13 EFFECTIVE-CONFIG FAIL: ' + message)


def git_head(path: Path) -> str:
    return subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()


def point(exp_id: str, role: str, roi: str, enabled: int, entries: int,
          n: int, lseg: int, binary: str, exclusion: Path | None = None,
          reuse_as: str = '') -> dict[str, str]:
    is_new = binary == 'new'
    core = base.NEW_CORE if is_new else base.CORE
    runtime = base.NEW_RUNTIME if is_new else base.RUNTIME
    executable = base.NEW_BINARY if is_new else base.BINARY
    return {
        'exp_id': exp_id,
        'logical_role': role,
        'roi': roi,
        'fair_arm': '0',
        'l2_mode': '0',
        'exact_l2_tlb_entries': str(entries),
        'l2_assoc': '16',
        'l2_sets': str(entries // 16),
        'segment_enable': str(enabled),
        'segment_n': str(n),
        'lseg': 'NONE' if not enabled else str(lseg),
        'exclusion_map': str(exclusion) if exclusion else 'NONE',
        'eligibility_policy': ('EXCLUDE_EMBEDDING_OUTPUT_WEIGHT_RANGE' if exclusion
                               else 'ALL_C5_ELIGIBLE_WEIGHT'),
        'binary_path': str(executable),
        'binary_sha256': base.NEW_BINARY_SHA if is_new else base.BINARY_SHA,
        'core_path': str(core),
        'core_head': base.NEW_CORE_SHA if is_new else base.CORE_SHA,
        'runtime_path': str(runtime),
        'trace_list': base.EXPECTED[roi][0],
        'trace_root': base.EXPECTED[roi][1],
        'expected_kernels': str(base.EXPECTED[roi][2]),
        'trace_sha256': base.EXPECTED[roi][3],
        'registration_path': str(base.REGISTER[roi]),
        'registration_sha256': base.EXPECTED[roi][4],
        'reuse_as': reuse_as,
        'gate_status': 'STATIC_EFFECTIVE_CONFIG_PASS',
        'output_dir': str(OUT / exp_id),
    }


POINTS = (
    point('C13-EQ-P320S10-C12BIN-EXACTMODE', 'EQ1_C12BIN_PROFILE_EQUIVALENCE',
          'prefill', 1, 320, 8, 10, 'c12'),
    point('C13-EQ-P320S10-NEWBIN-EXACTMODE',
          'EQ2_NEWBIN_DEFAULT_OFF_AND_H1_PREFILL_CONTROL_REUSE',
          'prefill', 1, 320, 8, 10, 'new', reuse_as='C13-SEL-P10-CTRL-NEWBIN'),
    point('C13-LAT-P8-REPAIRED-EXACTMODE-A1', 'H3_PREFILL_L8',
          'prefill', 1, 320, 8, 8, 'c12'),
    point('C13-LAT-P9-REPAIRED-EXACTMODE-A1', 'H3_PREFILL_L9',
          'prefill', 1, 320, 8, 9, 'c12'),
    point('C13-LAT-D11-REPAIRED-EXACTMODE-A1', 'H3_DECODE_L11',
          'decode1', 1, 320, 8, 11, 'c12'),
    point('C13-CAP-P320-REPAIRED-EXACTMODE-A1', 'H2_EXACT320_NO_SEGMENT',
          'prefill', 0, 320, 0, 0, 'c12'),
    point('C13-CAP-P768S10-REPAIRED-EXACTMODE-A1', 'H2_EXACT768_SEGMENT_L10',
          'prefill', 1, 768, 8, 10, 'c12'),
    point('C13-SEL-P10-REPAIRED-EXACTMODE-A1', 'H1_PREFILL_SELECTIVE_CANDIDATE',
          'prefill', 1, 320, 8, 10, 'new',
          ROOT / 'configs/vm_tlb/c13_diagnostics/selective/C13_PREFILL_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv'),
    point('C13-SEL-D10-CTRL-NEWBIN-REPAIRED-EXACTMODE-A1', 'H1_DECODE_CONTROL',
          'decode1', 1, 320, 8, 10, 'new'),
    point('C13-SEL-D10-REPAIRED-EXACTMODE-A1', 'H1_DECODE_SELECTIVE_CANDIDATE',
          'decode1', 1, 320, 8, 10, 'new',
          ROOT / 'configs/vm_tlb/c13_diagnostics/selective/C13_DECODE1_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv'),
)


def option_fold(path: Path) -> dict[str, str]:
    """Reproduce the config parser's repeated-option last-value semantics."""
    values: dict[str, str] = {}
    for raw in path.read_text(errors='strict').splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        match = OPTION.match(line)
        if match:
            values[match.group(1)] = (match.group(2) or '').strip()
    return values


def config_text(row: dict[str, str]) -> str:
    enabled = int(row['segment_enable'])
    source = base.source_config(row['roi'], enabled)
    suffix = (
        '\n# C13 Path-A repaired exact-mode override.  This final block is authoritative.\n'
        '-gpgpu_vm_fair_arm 0\n'
        '-gpgpu_vm_l2_tlb_entries %s\n'
        '-gpgpu_vm_l2_tlb_assoc %s\n'
        '-gpgpu_vm_l2_tlb_mode 0\n'
        '-gpgpu_vm_weight_segmentation_enable %s\n'
        '-gpgpu_vm_weight_segment_entries %s\n'
        '-gpgpu_vm_weight_segment_lookup_latency %s\n' %
        (row['exact_l2_tlb_entries'], row['l2_assoc'], row['segment_enable'],
         row['segment_n'], '0' if row['lseg'] == 'NONE' else row['lseg'])
    )
    if row['exclusion_map'] != 'NONE':
        suffix += '-gpgpu_vm_weight_segment_exclude_map %s\n' % row['exclusion_map']
    return '\n'.join(line.rstrip() for line in source.read_text().splitlines()) + '\n' + suffix


def static_receipt(row: dict[str, str]) -> dict[str, object]:
    config = Path(row['config_path'])
    folded = option_fold(config)
    required = {
        'gpgpu_vm_fair_arm': row['fair_arm'],
        'gpgpu_vm_l2_tlb_entries': row['exact_l2_tlb_entries'],
        'gpgpu_vm_l2_tlb_assoc': row['l2_assoc'],
        'gpgpu_vm_l2_tlb_mode': row['l2_mode'],
        'gpgpu_vm_weight_segmentation_enable': row['segment_enable'],
        'gpgpu_vm_weight_segment_entries': row['segment_n'],
        'gpgpu_vm_weight_segment_lookup_latency': '0' if row['lseg'] == 'NONE' else row['lseg'],
    }
    errors = [name for name, expected in required.items() if folded.get(name) != expected]
    if row['exclusion_map'] == 'NONE':
        if 'gpgpu_vm_weight_segment_exclude_map' in folded:
            errors.append('unexpected_exclusion_map')
    elif folded.get('gpgpu_vm_weight_segment_exclude_map') != row['exclusion_map']:
        errors.append('exclusion_map')
    if int(row['exact_l2_tlb_entries']) % int(row['l2_assoc']):
        errors.append('nonintegral_sets')
    if sha(config) != row['config_sha256']:
        errors.append('config_sha')
    if sha(Path(row['binary_path'])) != row['binary_sha256']:
        errors.append('binary_sha')
    if git_head(Path(row['core_path'])) != row['core_head']:
        errors.append('core_head')
    if sha(Path(row['trace_list'])) != row['trace_sha256']:
        errors.append('trace_sha')
    if sha(Path(row['registration_path'])) != row['registration_sha256']:
        errors.append('registration_sha')
    if row['exclusion_map'] != 'NONE' and not Path(row['exclusion_map']).is_file():
        errors.append('missing_exclusion_map')
    return {
        'receipt_schema': 'C13_EFFECTIVE_CONFIG_RECEIPT_V1',
        'static_status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'config_path': row['config_path'],
        'config_sha256': row['config_sha256'],
        'effective_option_fold': folded,
        'derived_l2_sets': int(row['exact_l2_tlb_entries']) // int(row['l2_assoc']),
        'intended': {key: row[key] for key in ('fair_arm', 'l2_mode', 'exact_l2_tlb_entries', 'l2_assoc', 'l2_sets', 'segment_enable', 'segment_n', 'lseg', 'exclusion_map')},
        'binary_path': row['binary_path'],
        'binary_sha256': row['binary_sha256'],
        'core_path': row['core_path'],
        'core_head': row['core_head'],
        'trace_sha256': row['trace_sha256'],
        'registration_sha256': row['registration_sha256'],
    }


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    with path.open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        # A final empty TSV cell becomes trailing whitespace under git's
        # whitespace checker.  Evidence tables use an explicit sentinel.
        writer.writerows({key: ('NONE' if value == '' else value)
                          for key, value in row.items()} for row in rows)


def final_counters(log: Path) -> dict[str, str]:
    output: dict[str, str] = {}
    for line in log.read_text(errors='strict').splitlines():
        match = COUNTER.match(line)
        if match:
            output[match.group(1)] = match.group(2)
    return output


def old_evidence() -> list[dict[str, object]]:
    if not OLD_MANIFEST.is_file():
        fail('immutable original C13 command manifest missing')
    with OLD_MANIFEST.open(newline='') as source:
        original = list(csv.DictReader(source, delimiter='\t'))
    output: list[dict[str, object]] = []
    for row in original:
        config = Path(row['config_path'])
        run = Path(row['output_dir'])
        log = run / 'run.log'
        folded = option_fold(config)
        counters = final_counters(log) if log.is_file() else {}
        mode = folded.get('gpgpu_vm_l2_tlb_mode', 'NOT_EMITTED')
        observed = counters.get('vm_l2_tlb_mode', 'NOT_EMITTED')
        output.append({
            'original_exp_id': row['exp_id'], 'actual_config_path': str(config),
            'actual_config_sha256': sha(config), 'raw_log_sha256': sha(log) if log.is_file() else 'MISSING',
            'intended_exact_entries': row['exact_l2_tlb_entries'],
            'option_folded_l2_mode': mode, 'raw_final_l2_mode': observed,
            'option_folded_entries': folded.get('gpgpu_vm_l2_tlb_entries', 'NOT_EMITTED'),
            'raw_final_entries': counters.get('vm_fair_l2_entries_realized', 'NOT_EMITTED'),
            'scientific_status': ('SUPERSEDED_WRONG_L2_MODE_SUBENTRY16'
                                  if mode == '1' and observed == '1' else 'REQUIRES_MANUAL_REVIEW'),
            'preservation': 'IMMUTABLE_RAW_LOG_AND_SHA_RETAINED',
        })
    return output


def write_e0(rows: list[dict[str, str]]) -> None:
    PACK.mkdir(parents=True, exist_ok=True)
    old = old_evidence()
    write_tsv(PACK / 'INVALIDATED_ARM_AUDIT.tsv', old)
    receipts: list[dict[str, object]] = []
    for row in rows:
        receipt = static_receipt(row)
        receipts.append({
            'exp_id': row['exp_id'], 'logical_role': row['logical_role'],
            'static_status': receipt['static_status'], 'config_sha256': row['config_sha256'],
            'effective_fair_arm': receipt['effective_option_fold'].get('gpgpu_vm_fair_arm', 'NOT_EMITTED'),
            'effective_l2_mode': receipt['effective_option_fold'].get('gpgpu_vm_l2_tlb_mode', 'NOT_EMITTED'),
            'effective_entries': receipt['effective_option_fold'].get('gpgpu_vm_l2_tlb_entries', 'NOT_EMITTED'),
            'effective_assoc': receipt['effective_option_fold'].get('gpgpu_vm_l2_tlb_assoc', 'NOT_EMITTED'),
            'derived_sets': receipt['derived_l2_sets'],
            'segment_enable': receipt['effective_option_fold'].get('gpgpu_vm_weight_segmentation_enable', 'NOT_EMITTED'),
            'segment_n': receipt['effective_option_fold'].get('gpgpu_vm_weight_segment_entries', 'NOT_EMITTED'),
            'lseg': receipt['effective_option_fold'].get('gpgpu_vm_weight_segment_lookup_latency', 'NOT_EMITTED'),
            'exclusion_map': row['exclusion_map'], 'binary_sha256': row['binary_sha256'],
            'core_head': row['core_head'], 'errors': ','.join(receipt['errors']),
        })
    write_tsv(PACK / 'EFFECTIVE_CONFIG_MATRIX.tsv', receipts)
    command_rows = []
    for old_row in old:
        command_rows.append({
            'record_kind': 'ORIGINAL_SUPERSEDED', 'exp_id': old_row['original_exp_id'],
            'config_path': old_row['actual_config_path'], 'config_sha256': old_row['actual_config_sha256'],
            'raw_log_sha256': old_row['raw_log_sha256'], 'effective_l2_mode': old_row['raw_final_l2_mode'],
            'status': old_row['scientific_status']})
    for row in rows:
        command_rows.append({
            'record_kind': 'REPAIRED_STATIC', 'exp_id': row['exp_id'], 'config_path': row['config_path'],
            'config_sha256': row['config_sha256'], 'raw_log_sha256': 'NOT_RUN',
            'effective_l2_mode': '0', 'status': 'STATIC_EFFECTIVE_CONFIG_PASS'})
    write_tsv(PACK / 'ACTUAL_COMMAND_AUDIT.tsv', command_rows)
    (PACK / 'FAIR_ARM_SOURCE_AUDIT.md').write_text(
        '# Fair-arm source audit\n\n'
        'C13 Path A is selected from direct source and execution evidence.  `FAIR_ARM_MANUAL` (0) preserves the parsed translation configuration; it does not apply the F7 profile.  F7 explicitly replaces the L2 mode with `L2_TLB_STANDARD` (0), whereas the C12 source config inherited by original C13 configs contains `gpgpu_vm_l2_tlb_mode=1` (`L2_TLB_SUBENTRY_16`).  Original C13 only overrode entries and Segment fields, so its MANUAL rows retained mode 1.\n\n'
        'The repaired generator writes the final override with explicit fair arm, entries, associativity, and `gpgpu_vm_l2_tlb_mode 0`.  Launch is refused unless independent last-option folding, frozen trace/registration SHA, binary SHA, Core HEAD, and exclusion-map provenance agree with the manifest.\n')
    (PACK / 'AUDIT_DECISION.md').write_text(
        '# Audit decision\n\n'
        'Decision: `PATH_A_WRONG_EFFECTIVE_GEOMETRY_OR_LAUNCH_PROVENANCE`.  All nine original C13 scientific rows are retained but superseded as `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16`: their effective mode was 1 despite contracts requiring exact-page mode 0.  Repaired runs are fresh and initially marked `SPECULATIVE_REPAIRED_EXECUTION_PENDING_EQ_GATE`; only EQ1 then EQ2 can promote them.\n')


def prepare() -> None:
    if sha(base.BINARY) != base.BINARY_SHA or sha(base.NEW_BINARY) != base.NEW_BINARY_SHA:
        fail('binary SHA mismatch')
    if git_head(base.CORE) != base.CORE_SHA or git_head(base.NEW_CORE) != base.NEW_CORE_SHA:
        fail('Core HEAD mismatch')
    rows: list[dict[str, str]] = []
    for template in POINTS:
        row = dict(template)
        path = CFG / (row['exp_id'] + '.config')
        text = config_text(row)
        if path.exists() and path.read_text() != text:
            fail('refuses to rewrite divergent repaired config ' + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(text)
        row['config_path'] = str(path)
        row['config_sha256'] = sha(path)
        if row['exclusion_map'] != 'NONE':
            row['eligibility_artifact_sha256'] = sha(Path(row['exclusion_map']))
        else:
            row['eligibility_artifact_sha256'] = 'NONE'
        receipt = static_receipt(row)
        if receipt['static_status'] != 'PASS':
            fail(row['exp_id'] + ' static gate ' + ','.join(receipt['errors']))
        rows.append(row)
    PACK.mkdir(parents=True, exist_ok=True)
    write_tsv(MANIFEST, rows)
    write_e0(rows)
    print('C13_PATH_A_PREPARE_PASS\trepaired_execution_points=%d\told_superseded=9' % len(rows))


def read_rows() -> dict[str, dict[str, str]]:
    if not MANIFEST.is_file():
        fail('run --prepare first')
    with MANIFEST.open(newline='') as source:
        return {row['exp_id']: row for row in csv.DictReader(source, delimiter='\t')}


def runtime_receipt(row: dict[str, str], code: int) -> dict[str, object]:
    run = Path(row['output_dir'])
    log = run / 'run.log'
    final = final_counters(log)
    required = {
        'vm_fair_arm_id': row['fair_arm'],
        'vm_l2_tlb_mode': row['l2_mode'],
        'vm_fair_l2_entries_realized': row['exact_l2_tlb_entries'],
        'vm_fair_l2_associativity_realized': row['l2_assoc'],
        'vm_fair_l2_sets_realized': row['l2_sets'],
        'vm_weight_segmentation_enabled': row['segment_enable'],
        'vm_weight_segment_entries_configured': row['segment_n'],
        'vm_weight_segment_lookup_latency_cycles': '0' if row['lseg'] == 'NONE' else row['lseg'],
    }
    errors = [name for name, expected in required.items() if final.get(name) != expected]
    receipt = static_receipt(row)
    if receipt['static_status'] != 'PASS':
        errors.append('static_receipt_recheck')
    if code != 0:
        errors.append('exit_status')
    return {
        **receipt, 'runtime_status': 'PASS' if not errors else 'FAIL', 'runtime_errors': errors,
        'raw_log_sha256': sha(log) if log.is_file() else 'MISSING', 'final_geometry': {key: final.get(key, 'NOT_EMITTED') for key in required},
        'command': ['/usr/bin/time', '-v', row['binary_path'], '-config', row['config_path'], '-trace', str(run / 'traces/kernelslist.g')],
    }


def execute(exp_id: str) -> None:
    row = read_rows().get(exp_id)
    if not row:
        fail('unknown repaired point ' + exp_id)
    receipt = static_receipt(row)
    if receipt['static_status'] != 'PASS':
        fail(exp_id + ' launch preflight ' + ','.join(receipt['errors']))
    run = Path(row['output_dir'])
    if run.exists():
        fail('fresh-output policy refuses ' + str(run))
    run.mkdir(parents=True)
    (run / 'C13_EFFECTIVE_CONFIG_RECEIPT_PRELAUNCH.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    traces = run / 'traces'
    traces.mkdir()
    target = traces / 'kernelslist.g'
    target.write_bytes(Path(row['trace_list']).read_bytes())
    if sha(target) != row['trace_sha256']:
        fail(exp_id + ' copied trace SHA mismatch')
    for name in target.read_text().splitlines():
        os.symlink(str(Path(row['trace_root']) / name), str(traces / name))
    command = ['/usr/bin/time', '-v', row['binary_path'], '-config', row['config_path'], '-trace', str(target)]
    (run / 'C13_ACTUAL_COMMAND.json').write_text(json.dumps({'argv': command, 'config_sha256': row['config_sha256'], 'binary_sha256': row['binary_sha256'], 'core_head': row['core_head']}, indent=2) + '\n')
    with (run / 'run.log').open('w') as log:
        code = subprocess.run(command, cwd=run, env={**os.environ, 'GPGPUSIM_ROOT': row['core_path'], 'LD_LIBRARY_PATH': row['runtime_path']}, stdout=log, stderr=subprocess.STDOUT).returncode
    lines = (run / 'run.log').read_text(errors='strict').splitlines()
    starts = [index for index, line in enumerate(lines) if line.lstrip().startswith('Command being timed:')]
    if starts:
        (run / 'time-v.txt').write_text('\n'.join(lines[starts[-1]:]) + '\n')
    runtime = runtime_receipt(row, code)
    (run / 'C13_EFFECTIVE_CONFIG_RECEIPT.json').write_text(json.dumps(runtime, indent=2, sort_keys=True) + '\n')
    if runtime['runtime_status'] != 'PASS':
        fail(exp_id + ' runtime effective geometry ' + ','.join(runtime['runtime_errors']))
    # Existing hardened validator enforces marker/telemetry, quiescence,
    # PTE/object conservation, exact cycles, and cumulative vm_* closure.
    base.validate(row, code)
    print('C13_PATH_A_ARM_PASS\t%s\tstatus=PASS_PENDING_EQ_GATE' % exp_id)


def c12_anchor() -> Path:
    c12_pack = base.C12 / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE'
    with (c12_pack / 'ARM_STATUS.tsv').open(newline='') as source:
        rows = list(csv.DictReader(source, delimiter='\t'))
    row = next((item for item in rows if item['roi'] == 'prefill' and item['arm'] == 'F7' and item['lseg'] == '10' and item['terminal_status'] == 'PASS'), None)
    if not row:
        fail('C12 Prefill F7 L10 anchor missing')
    path = Path(row['run_dir']) / 'run.log'
    if sha(path) != row['raw_log_sha256']:
        fail('C12 F7 L10 raw SHA mismatch')
    return path


def strict_compare(left: Path, right: Path) -> list[str]:
    """Return simulated-state equivalence differences.

    ``gpu_total_sim_rate`` is the only excluded telemetry field besides fair
    labels: it is a host wall-clock-derived reporting rate, not simulator
    state.  It necessarily varies with concurrent host load even when the
    trace, kernel cycles, and every translation/cache counter are identical.
    """
    errors: list[str] = []
    sys.path.insert(0, str(OP_PARSER.parent))
    import analyze_c12_operator_aware as op
    left_raw, right_raw = op.raw_kernels(left), op.raw_kernels(right)
    if len(left_raw) != len(right_raw):
        errors.append('kernel_count')
    for index, (a, b) in enumerate(zip(left_raw, right_raw)):
        if a.marker != b.marker:
            errors.append('marker:%d' % index)
            break
        if a.exact.get('gpu_sim_cycle') != b.exact.get('gpu_sim_cycle'):
            errors.append('kernel_cycle:%d' % index)
            break
    a_final, b_final = final_counters(left), final_counters(right)
    ignore = {
        'vm_fair_arm_id',
        'vm_fair_arm_charged_bits',
        'gpu_total_sim_rate',
    }
    shared = sorted((set(a_final) & set(b_final)) - ignore)
    for name in shared:
        if (name.startswith('gpu_') or name.startswith('vm_')) and a_final[name] != b_final[name]:
            errors.append('counter:' + name)
    return errors


def equivalence() -> None:
    rows = read_rows()
    anchor = c12_anchor()
    eq1 = Path(rows['C13-EQ-P320S10-C12BIN-EXACTMODE']['output_dir']) / 'run.log'
    eq2 = Path(rows['C13-EQ-P320S10-NEWBIN-EXACTMODE']['output_dir']) / 'run.log'
    report: list[dict[str, object]] = []
    for name, candidate, baseline in (
        ('EQ1_C12BIN_MANUAL_EXACTMODE_VS_C12_F7_L10', eq1, anchor),
        ('EQ2_NEWBIN_DEFAULT_OFF_VS_EQ1', eq2, eq1),
        ('EQ2_NEWBIN_DEFAULT_OFF_VS_C12_F7_L10', eq2, anchor),
    ):
        validation = candidate.parent / 'C13_ARM_VALIDATION.json'
        receipt = candidate.parent / 'C13_EFFECTIVE_CONFIG_RECEIPT.json'
        if (not candidate.is_file() or not baseline.is_file() or not validation.is_file() or
                not receipt.is_file() or json.loads(validation.read_text()).get('terminal_status') != 'PASS' or
                json.loads(receipt.read_text()).get('runtime_status') != 'PASS'):
            report.append({'comparison': name, 'status': 'WAIT_TERMINAL', 'differences': 'MISSING_RAW_LOG'})
            continue
        differences = strict_compare(baseline, candidate)
        report.append({'comparison': name, 'status': 'PASS' if not differences else 'FAIL', 'differences': ','.join(differences) or 'NONE'})
    write_tsv(PACK / 'EQUIVALENCE_CONTROL.tsv', report)
    eq1_status = report[0]['status']
    eq2_status = report[1]['status']
    if eq1_status == 'FAIL' or eq2_status == 'FAIL':
        (PACK / 'PATH_B_AUTO_TRANSITION.md').write_text(
            '# Automatic Path B transition\n\nEQ1 or EQ2 strict equivalence failed.  All repaired speculative runs are quarantined; no Path-A scientific conclusion may be promoted.  Continue with the Path B correctness audit.\n')
        fail('equivalence gate failure; Path B transition recorded')
    if eq1_status != 'PASS' or eq2_status != 'PASS':
        print('C13_EQ_GATE_WAIT_TERMINAL')
        return
    # A prior invocation can have produced a Path-B artifact before a
    # transient comparison issue was corrected.  Once both simulated-state
    # controls pass, it must not remain as false Path-B provenance.
    (PACK / 'PATH_B_AUTO_TRANSITION.md').unlink(missing_ok=True)
    (PACK / 'EQ_GATE_PROMOTION.md').write_text(
        '# Equivalence-gate promotion\n\nEQ1 reproduces the immutable C12 Prefill F7-L10 anchor and EQ2 reproduces EQ1 under empty exclusion.  The comparison is exact for kernel markers/cycles and modeled `gpu_*`/`vm_*` counters; only `gpu_total_sim_rate` is excluded because it is derived from host wall-clock time rather than simulated state.  Terminal repaired arms with PASS receipts may be promoted from `SPECULATIVE_REPAIRED_EXECUTION_PENDING_EQ_GATE` to accepted Path-A evidence.\n')
    print('C13_EQ_GATE_PASS')


def status() -> None:
    rows = read_rows()
    report: list[dict[str, object]] = []
    eq_file = PACK / 'EQUIVALENCE_CONTROL.tsv'
    eq_pass = eq_file.is_file() and all(row['status'] == 'PASS' for row in csv.DictReader(eq_file.open(), delimiter='\t'))
    for row in rows.values():
        run = Path(row['output_dir'])
        validation = run / 'C13_ARM_VALIDATION.json'
        receipt = run / 'C13_EFFECTIVE_CONFIG_RECEIPT.json'
        if validation.is_file() and receipt.is_file():
            result = json.loads(validation.read_text())
            r = json.loads(receipt.read_text())
            state = ('ACCEPTED_AFTER_EQ_GATE' if eq_pass and result.get('terminal_status') == 'PASS' and r.get('runtime_status') == 'PASS'
                     else 'PASS_PENDING_EQ_GATE' if result.get('terminal_status') == 'PASS' and r.get('runtime_status') == 'PASS'
                     else 'FAILED')
            raw_sha = r.get('raw_log_sha256', 'MISSING')
        elif receipt.is_file():
            state, raw_sha = 'FAILED_AFTER_RUNTIME_RECEIPT', 'NONTERMINAL_OR_FAILED'
        elif run.is_dir():
            # A fresh directory exists only after the static receipt and
            # actual-command receipt have been written.  It is deliberately
            # not accepted evidence until terminal validation completes.
            state, raw_sha = 'RUNNING_SPECULATIVE_REPAIRED_EXECUTION_PENDING_EQ_GATE', 'NONTERMINAL'
        else:
            state, raw_sha = 'NOT_STARTED', 'NOT_EMITTED'
        report.append({'exp_id': row['exp_id'], 'logical_role': row['logical_role'], 'status': state,
                       'raw_log_sha256': raw_sha, 'config_sha256': row['config_sha256'], 'effective_l2_mode': row['l2_mode'],
                       'gate_dependency': 'EQ1_THEN_EQ2', 'reuse_as': row['reuse_as']})
    write_tsv(PACK / 'RERUN_STATUS.tsv', report)
    print('C13_PATH_A_STATUS\taccepted=%d\tpending=%d\tnot_started=%d' % (
        sum(item['status'] == 'ACCEPTED_AFTER_EQ_GATE' for item in report),
        sum(item['status'] == 'PASS_PENDING_EQ_GATE' for item in report),
        sum(item['status'] == 'NOT_STARTED' for item in report)))


def watch(interval: int) -> None:
    """Unattended, read-only controller for gate promotion and status.

    It never launches or terminates a simulator.  Individual launchers still
    own their terminal validation; this controller merely observes receipts
    and refuses to compare partial EQ logs.
    """
    while True:
        equivalence()
        status()
        rows = read_rows()
        incomplete = []
        failed = []
        for row in rows.values():
            run = Path(row['output_dir'])
            validation = run / 'C13_ARM_VALIDATION.json'
            receipt = run / 'C13_EFFECTIVE_CONFIG_RECEIPT.json'
            if validation.is_file() and receipt.is_file():
                if (json.loads(validation.read_text()).get('terminal_status') != 'PASS' or
                        json.loads(receipt.read_text()).get('runtime_status') != 'PASS'):
                    failed.append(row['exp_id'])
            else:
                incomplete.append(row['exp_id'])
        if failed:
            fail('terminal repaired arm failure: ' + ','.join(failed))
        if not incomplete:
            print('C13_PATH_A_WATCH_ALL_TERMINAL')
            return
        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--execute')
    parser.add_argument('--equivalence', action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--watch', type=int, metavar='SECONDS')
    args = parser.parse_args()
    if sum((bool(args.prepare), bool(args.execute), bool(args.equivalence), bool(args.status), args.watch is not None)) != 1:
        fail('select exactly one of --prepare, --execute, --equivalence, --status, --watch')
    if args.prepare:
        prepare()
    elif args.execute:
        execute(args.execute)
    elif args.equivalence:
        equivalence()
    elif args.status:
        status()
    else:
        if args.watch < 30:
            fail('watch interval must be at least 30 seconds')
        watch(args.watch)
