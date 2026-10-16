#!/usr/bin/env python3
"""Read existing immutable evidence; never launch, retry, signal or change a model.

Run from any directory with --output naming a fresh JSON receipt. Original629
current bytes are separately bound by ORIGINAL_INPUT_REVALIDATION.json. This
audit checks terminal/config/source chains and preserves a failed receipt.
"""
import argparse
import collections
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / 'util/dtc_l1/collect_service_closure_attempts.py').exists())
BASE = REPO / 'docs/dtc_l1/iscas2027/service_closure_174_v1'
RAW = Path('/workspace/dtc-service-closure-174-v1')
sys.path.insert(0, str(REPO / 'util/dtc_l1'))
from collect_service_closure_attempts import collect, sha
from launch_hotspot_derived_174 import simulators


def read(path):
    return json.loads(Path(path).read_text())


def table(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def require(value, label):
    if not value:
        raise AssertionError(label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'status': 'IN_PROGRESS',
              'audit_source_sha256': sha(Path(__file__)), 'simulations_launched': 0,
              'native_jobs_launched': 0, 'process_signals': 0}
    try:
        pack = BASE / 'review_pack/checkpoint_20261016T2133Z'
        plan_path = BASE / 'review_pack/r2/REGISTERED_ROWS_V2.tsv'
        plan = table(plan_path)
        require(len(plan) == 44 and sha(plan_path) == '281b2d22ace3bbf105711473516f075fc11c495a1d6c214d9f4a3e42414892e1', 'Original44 plan changed')
        labels = {x['label'] for x in plan}
        holds_path = RAW / 'r2-attempts/ROW_ADMISSION_HOLDS.json'
        held = set(read(holds_path)['held_labels'])
        require(sha(holds_path) == '4a374a41a9c711aa5bb2b68be79faa8080775971e8b7646292b274ee1c9e025c' and len(held) == 3, 'Original holds changed')
        require(sha(RAW / 'r2-attempts/HOLD_LAUNCHES') == '070fe0146a778e5d12e960dafeaf17985273a8f4fc65936569b31c15b341300e', 'Authority token changed')
        require(sha(REPO / 'util/dtc_l1/collect_service_closure_attempts.py') == 'a5a1f4018fbfa90b91ad2d3eab4df64f351f905ce74385dbb3a73ec7ca837819', 'Strict collector changed')
        body = {x['path']: x for x in table(BASE / 'review_pack/trace_body_v1/KERNEL_BODY_AUDIT.tsv')}
        starts = [p for p in (RAW / 'r2-attempts').glob('*/RUN_START.json') if read(p)['spec']['label'] in labels]
        counts = collections.Counter(read(p)['spec']['label'] for p in starts)
        require(len(starts) == 41 and set(counts) == labels - held and all(n == 1 for n in counts.values()), 'Original launch cardinality/retry/held-label mismatch')
        original = []
        for start_path in starts:
            start = read(start_path)
            spec = start['spec']
            planned = next(x for x in plan if x['label'] == spec['label'])
            require(sha(Path(planned['spec_path'])) == planned['spec_sha256'], 'Registered spec SHA mismatch')
            row = collect(start_path.parent)
            frozen = read(RAW / 'r2-attempts/strict_reviews_v2' / (row['attempt_uuid'] + '.json'))
            require(row == frozen['terminal_review'] and row['status'] == 'PASS_CHECKED_SCOPE', 'Strict recollection mismatch: ' + row['label'])
            text = (start_path.parent / 'simulator.stdout').read_text()
            kernels = re.findall(r'^kernel_name\s*=\s*(\S+)', text, re.M)
            insns = [int(x) for x in re.findall(r'^gpu_sim_insn\s*=\s*(\d+)', text, re.M)]
            bodies = [body[m['path']] for m in spec['members']]
            require(kernels == [x['kernel'] for x in bodies], 'Ordered kernel mismatch')
            require(insns == [int(x['active_thread_instructions']) for x in bodies], 'Per-kernel complete instruction mismatch')
            require(sum(insns) == spec['expected_instructions'], 'Whole-workload instruction mismatch')
            original.append({'label': row['label'], 'uuid': row['attempt_uuid'], 'cycles': int(row['cycles']),
                             'strict_sha256': sha(RAW / 'r2-attempts/strict_reviews_v2' / (row['attempt_uuid'] + '.json')),
                             'kernels': len(kernels), 'instructions': sum(insns), 'launch_utc': start['launch_utc']})
        result['original41_full_strict_and_ordered_scope'] = original
        require(not simulators(), 'Own simulator still live')
        result['own_simulators'] = []

        baselines = table(BASE / 'review_pack/r2/CANONICAL_BASELINE_REUSE.tsv')
        require(len(baselines) == 24, 'Canonical baseline count')
        for x in baselines:
            require(sha(Path(x['strict_receipt_path'])) == x['strict_receipt_sha256'], 'Baseline strict SHA')
            require(sha(Path(x['run_dir']) / 'simulator.stdout') == x['stdout_sha256'], 'Baseline stdout SHA')
            require(int(x['lower_cap_events']) == 0 and int(x['lower_cap_peak']) < 8192, 'Baseline cap reuse premise')
        result['canonical24_current_strict_stdout_and_nonbinding_cap'] = 'PASS'
        old = table(BASE / 'review_pack/r0/ROW_REUSE_LEDGER.tsv')
        for x in old:
            require(sha(REPO / x['evidence_path']) == x['evidence_sha256'] and sha(Path(x['raw_log'])) == x['raw_log_sha256'], 'Historical receipt/raw mutated')
        require(len(old) == 36, 'Historical36 receipt count')
        result['historical36_receipt_and_raw_SHA'] = 'PASS'

        derived_uuids = set()
        derived = []
        checked_inputs = {}
        for name, count, namespace, source_name in [
            ('hotspot', 5, 'hotspot-derived-paired-v2', 'collect_hotspot_derived_174.py'),
            ('btree', 6, 'btree-derived-paired-v1', 'collect_btree_derived_174.py')]:
            group = BASE / ('review_pack/' + name + '_derived_complete_v1')
            rows = table(group / 'DERIVED_ROWS_STATE.tsv')
            require(len(rows) == count, 'Derived arm count')
            ids = {x['attempt_uuid'] for x in rows}
            require(len(ids) == count and not derived_uuids.intersection(ids), 'Derived UUID overlap')
            derived_uuids.update(ids)
            scopes = set()
            for x in rows:
                run = Path(x['raw_dir'])
                frozen = read(group / (x['attempt_uuid'] + '.strict.json'))
                require(frozen['terminal_review']['status'] == x['status'] == 'PASS_CHECKED_SCOPE', 'Derived strict status')
                require(all(json.loads(x['scientific_checks']).values()), 'Derived admission/strict checks')
                require(sha(RAW / namespace / 'execution_sources' / source_name) == frozen['collector_sha256'], 'Frozen derived collector source')
                require(sha(run / 'RUN_TERMINAL.json') == x['terminal_sha256'] and sha(run / 'simulator.stdout') == x['stdout_sha256'], 'Derived terminal/stdout SHA')
                spec = read(run / 'SPEC.json')
                scopes.add(json.dumps([spec['members'], spec['trace_list_sha256'], spec['expected_instructions']], sort_keys=True))
                require(collect(run)['status'] == 'PASS_CHECKED_SCOPE', 'Derived base strict re-collection')
                for inp in spec['members'] + [{'path': spec['trace_list'], 'sha256': spec['trace_list_sha256']}]:
                    path = Path(inp['path'])
                    if str(path) not in checked_inputs:
                        checked_inputs[str(path)] = sha(path)
                    require(checked_inputs[str(path)] == inp['sha256'] and not path.is_symlink() and path.stat().st_mode & 0o222 == 0, 'Derived immutable input')
            require(len(scopes) == 1 and len({x['input_bundle_sha256'] for x in rows}) == 1, 'Derived arm input/ROI mismatch')
            for pair in table(group / 'SAME_DERIVED_INPUT_PAIRS.tsv'):
                for key, value in pair.items():
                    if 'uuid' in key.lower():
                        require(value in ids, 'Mixed old/new denominator UUID')
            derived.append({'lineage': name, 'arms': count, 'bundle': rows[0]['input_bundle_sha256'], 'UUIDs': sorted(ids)})
        result['derived11_separate_identity_frozen_strict_and_same_input_pairs'] = derived
        result['derived_current_readonly_input_hashes'] = checked_inputs

        modern = table(pack / 'MODERN_BASELINE_ONLY.tsv')
        require(len(modern) == 4 and all(x['status'] == 'PASS_BASELINE_COUNTERFACTUAL_SCOPE' for x in modern), 'Modern baseline-only status')
        result['modern_baseline_only4'] = 'PASS_IN_DECLARED_COUNTERFACTUAL_SCOPE'
        native = BASE / 'review_pack/producer109_v1/CONSUMER_ARCHIVE_VERIFICATION_V2.json'
        n = read(native)
        directory = Path(n['payload_root'])
        index = directory / 'PAYLOAD_FILES.json'
        require(sha(index) == n['index_sha256'], 'Native producer index identity')
        payload = read(index)
        for x in payload:
            path = directory / x['relative_path']
            require(path.stat().st_size == x['bytes'] and sha(path) == x['sha256'], 'Native payload current SHA')
        require(len(payload) == n['files_verified'] == 285, 'Native payload count')
        require(len(table(BASE / 'review_pack/producer109_v1/NATIVE109_TIMING_SUMMARY.tsv')) == 15, 'Native15 scope count')
        result['native109_current285_payload_files_and15_cases'] = 'PASS_NATIVE_SCOPE_NO_RERUN'

        gate = read(BASE / 'review_pack/r1/GATE.json')
        require(sha(Path(gate['ctest_log'])) == gate['ctest_log_sha256'] and '100% tests passed, 0 tests failed out of 4' in Path(gate['ctest_log']).read_text(), 'R1 CTest receipt')
        final_r1 = table(BASE / 'review_pack/r1/FINAL_CHECKS_V2.tsv')
        off = {x['mode']: int(x['cycles']) for x in table(BASE / 'review_pack/r1/OFF_EQUIVALENCE.tsv')}
        for x in final_r1:
            require(collect(Path(x['run_dir']))['status'] == 'PASS_CHECKED_SCOPE', 'Current R1 full check')
            if x['label'].endswith('new-off'):
                mode = x['label'].split('_')[3]
                require(int(x['cycles']) == off[mode] and int(x['instructions']) == 1284872, 'R1 exact OFF equivalence')
        require(len(final_r1) == 5, 'R1 final5 check count')
        guards = read(BASE / 'review_pack/matched128_v1/CONTRACT_GUARD_CHECKS_V2.json')
        require(len(guards['checks']) == 24 and all(x['result'] == 'PASS' for x in guards['checks']), 'Matched24 guard receipt')
        result['R1_CTest4_OFF3_ON2_matched24_existing_receipts'] = 'PASS_UNCHANGED_NOT_RERUN'
        result['all_attempts_status_including_old_failures'] = dict(collections.Counter(x['status'] for x in table(pack / 'ALL_ATTEMPTS.tsv')))
        result['status'] = 'PASS_FINAL_EVIDENCE_INTEGRITY_WITH_SCIENTIFIC_HOLDS_UNCHANGED'
    except Exception as exc:
        result['status'] = 'FAIL_PRESERVED'
        result['error'] = type(exc).__name__ + ': ' + str(exc)
    with Path(args.output).open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'receipt': args.output, 'error': result.get('error')}))
    if result['status'] == 'FAIL_PRESERVED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
