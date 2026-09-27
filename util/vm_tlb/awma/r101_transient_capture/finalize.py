#!/usr/bin/env python3
"""Join full native trace order to exact A/B/X0/X1 region/lifetime authority."""
from __future__ import annotations

import csv
import hashlib
import json
import lzma
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
FORMAL = ROOT / 'raw/formal_full5'


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def write(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def table(path: Path) -> list[dict]:
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def write_table(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    terminal = json.loads((FORMAL / 'TERMINAL_RECEIPT.json').read_text())
    assert terminal['status'] == 'COMPLETE' and terminal['selected_kernels'] == 18
    assert terminal['drop_count'] == terminal['overflow_count'] == 0
    assert terminal['all_grammar_pass'] and terminal['all_xz_pass']
    members = table(FORMAL / 'TRACE_MEMBER_MANIFEST.tsv')
    binding = table(FORMAL / 'NATIVE_KERNEL_BINDING.tsv')
    prereg = table(ROOT / 'NATIVE_KERNEL_BINDING_PREREG.tsv')
    template = read('REGION_LIFETIME_TEMPLATE.json')
    regions_raw = json.loads((FORMAL / 'BUFFER_REGIONS_RUNTIME.json').read_text())
    assert regions_raw['region_map_frozen_before_profiler_start']
    assert regions_raw['input_payload_sha256'] == '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'
    assert len(members) == len(binding) == len(prereg) == len(template['rows']) == 18
    assert [int(row['roi_launch_index']) for row in binding] == list(range(18))
    assert len({row['context_from_filename'] for row in binding}) == 1
    assert len({row['stream_id'] for row in binding}) == 1
    assert all(row['grammar_status'] == 'PASS' for row in members)
    for actual, expected in zip(binding, prereg):
        assert actual['exact_function'] == expected['exact_function']
        assert actual['grid'] == expected['grid'] and actual['block'] == expected['block']
    region_rows = []
    spans = []
    for name in ('A', 'B', 'X0', 'X1'):
        record = regions_raw['regions'][name]
        assert record['bytes'] == 23068672
        assert record['aligned_128_bytes'] and record['shape'] == [44, 512, 512]
        base = int(record['base_device_address'])
        assert base % 128 == 0
        spans.append((base, base + record['bytes']))
        region_rows.append({'region': name, 'base_device_address_hex': record['base_hex'],
                            'base_device_address_decimal': base,
                            'end_exclusive_hex': record['end_exclusive_hex'],
                            'bytes': record['bytes'], 'aligned_128_bytes': True,
                            'allocation_identity': record['allocation_identity'],
                            'shape': json.dumps(record['shape']),
                            'stride_elements': json.dumps(record['stride_elements']),
                            'dtype': record['dtype'], 'scientific_relation': record['relation'],
                            'accepted_input_payload_sha256': regions_raw['input_payload_sha256']})
    spans.sort()
    assert all(spans[index][1] <= spans[index + 1][0] for index in range(3))
    assert regions_raw['A_B_arena_contiguous']
    write_table(ROOT / 'BUFFER_REGION_MAP.tsv', region_rows)
    lifetime_rows = []
    for expected, actual in zip(template['rows'], binding):
        assert expected['roi_launch_index'] == int(actual['roi_launch_index'])
        if expected['family'] != 'NORMALIZATION':
            assert expected['family'] == prereg[int(actual['roi_launch_index'])]['family']
        lifetime_rows.append({
            'roi_launch_index': actual['roi_launch_index'],
            'global_launch_index': actual['kernel_id'],
            'context': actual['context_from_filename'],
            'stream_id': actual['stream_id'],
            'phase': expected['phase'],
            'iteration': expected['iteration'] if expected['iteration'] is not None else '',
            'kernel_family': expected['family'],
            'exact_function': actual['exact_function'],
            'grid': actual['grid'], 'block': actual['block'],
            'A_after': expected['A_after'], 'B_after': expected['B_after'],
            'X0_after': expected['X0_after'], 'X1_after': expected['X1_after'],
            'boundary_rule': expected['boundary_rule'],
            'kernel_boundary_only': True, 'per_line_future_last_use': False,
        })
    assert lifetime_rows[-1]['X1_after'] == 'LIVE'
    write_table(ROOT / 'REGION_LIFETIME.tsv', lifetime_rows)
    shutil.copy2(FORMAL / 'NATIVE_KERNEL_BINDING.tsv', ROOT / 'NATIVE_KERNEL_BINDING.tsv')
    shutil.copy2(FORMAL / 'TRACE_MEMBER_MANIFEST.tsv', ROOT / 'TRACE_MEMBER_MANIFEST.tsv')
    opcode_totals = Counter()
    grammar_statuses = []
    for index in range(18):
        result = json.loads((FORMAL / f'grammar_{index:02d}.stdout.log').read_text())
        assert result['status'] == 'TRACEG_GRAMMAR_PASS'
        counts = result['opcode_counts']
        opcode_totals.update(counts)
        grammar_statuses.append({'roi_launch_index': index,
                                 'instructions': result['instructions'],
                                 'thread_blocks': result['thread_blocks'],
                                 'memory_opcode_count': sum(value for key, value in counts.items()
                                                            if key.startswith(('LDG', 'STG', 'ATOM', 'RED'))),
                                 'sync_control_opcode_count': sum(value for key, value in counts.items()
                                                                  if key.startswith(('BAR', 'DEPBAR', 'BRA', 'EXIT', 'LDGDEPBAR'))),
                                 'status': 'PASS'})
    assert all(row['memory_opcode_count'] > 0 for row in grammar_statuses[3:])
    assert any(key.startswith('STG') for key in opcode_totals)
    assert any(key.startswith('LDG') for key in opcode_totals)
    assert any(key.startswith(('BAR', 'DEPBAR')) for key in opcode_totals)
    parser_receipt = read('TRACE_PARSER_RECEIPT.json')
    assert parser_receipt['status'] == 'PASS' and parser_receipt['members'] == 18
    assert parser_receipt['total_parsed_instructions'] == sum(row['instructions'] for row in grammar_statuses)
    write_table(ROOT / 'TRACE_SEMANTIC_AUDIT.tsv', grammar_statuses)
    write('TRACE_SEMANTIC_SUMMARY.json', {
        'trace_schema': 'SIM_COMPAT_CAPTURE_V1 native traceg version 5',
        'all_grammar_pass': True, 'kernel_members': 18,
        'total_instructions': sum(row['instructions'] for row in grammar_statuses),
        'total_memory_opcode_count': sum(row['memory_opcode_count'] for row in grammar_statuses),
        'total_sync_control_opcode_count': sum(row['sync_control_opcode_count'] for row in grammar_statuses),
        'opcode_counts': dict(opcode_totals),
        'memory_width_and_per_lane_address_syntax_checked_by_accepted_validator': True,
    })
    run = json.loads((FORMAL / 'DRIVER_RUN_RECEIPT.json').read_text())
    assert run['output_exact'] and run['finite']
    guard = json.loads((FORMAL / 'RESOURCE_GUARD.json').read_text())
    assert guard['driver_returncode'] == 0 and guard['triggered_reason'] is None
    producer = read('TRACER_SOURCE_AND_BUILD_RECEIPT.json')
    input_binding = read('ACCEPTED_INPUT_BINDING.json')
    accepted_environment = json.loads((Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927') / 'ENVIRONMENT_RECEIPT.json').read_text())
    write('ENVIRONMENT_RECEIPT.json', {
        'accepted_r101_environment_receipt_sha256': sha(Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/ENVIRONMENT_RECEIPT.json')),
        'accepted_python_environment_reused_read_only': accepted_environment,
        'isolated_capture_cache_root': str(ROOT / 'cache'),
        'isolated_capture_tmpdir': str(ROOT / 'tmp'),
        'nvbit_version': producer['nvbit_version'],
        'capture_cuda_toolkit': producer['cuda_toolkit'],
        'native_gpu_identity': guard['gpu_identity'],
        'NO_EAGER_LOAD': '1; qualified by import probe and real canaries',
        'system_cuda_driver_or_accepted_environment_modified': False,
    })
    raw_first = FORMAL / 'raw' / members[0]['raw_member']
    header = {}
    with lzma.open(raw_first, 'rt') as stream:
        for line in stream:
            if not line.startswith('-'):
                break
            if ' = ' in line:
                key, value = line[1:].strip().split(' = ', 1)
                header[key] = value
    assert 'shmem base_addr' in header and 'local mem base_addr' in header
    max_region_end = max(end for _, end in spans)
    assert max_region_end < (1 << 49)
    write('ADDRESS_CONTEXT.json', {
        'schema_version': 'AWMA_ADDRESS_CONTEXT_V1',
        'cuda_context_observed': binding[0]['context_from_filename'],
        'context_from_trace_member': members[0]['raw_member'],
        'asid_epoch': '0',
        'va_width': 49,
        'va_width_policy': 'accepted AWMA simulator-input policy; all four region ends below 2^49; no full-trace max-VA claim',
        'full_trace_address_max_scanned': False,
        'max_region_end_exclusive_hex': hex(max_region_end),
        'page_policy': '4K',
        'shmem_base_addr': header['shmem base_addr'],
        'local_mem_base_addr': header['local mem base_addr'],
        'address_mode_policy': 'MODE1_BASE_STRIDE_OR_MODE0_LIST_ALL_ONLY',
        'traceg_grammar_pass': True,
    })
    address_sanity = read('REGION_ADDRESS_SANITY.json')
    assert address_sanity['status'] == 'PASS' and address_sanity['all_four_regions_in_simulator_native_traceg']
    capture_id_data = (input_binding['payload_sha256'] + producer['new_multi_binary_sha256'] +
                       sha(FORMAL / 'raw/kernelslist.g') + sha(ROOT / 'REGION_LIFETIME.tsv'))
    capture_id = 'R101_L512_TRANSIENT_' + hashlib.sha256(capture_id_data.encode()).hexdigest()[:16]
    manifest_members = [{**member,
                         'roi_launch_index': int(member['roi_launch_index']),
                         'raw_bytes': int(member['raw_bytes']),
                         'traceg_bytes': int(member['traceg_bytes'])}
                        for member in members]
    manifest = {
        'status': 'R101_TRANSIENT_SIM_CAPTURE_PASS',
        'sim_input_id': input_binding['sim_input_id'],
        'capture_id': capture_id,
        'trace_schema': 'SIM_COMPAT_CAPTURE_V1',
        'trace_version': 5,
        'scope_id': 'R101_L512_FULL5_WITH_NORMALIZATION_V1',
        'normalization_kernels': 3,
        'ns_iterations': 5,
        'ns_arithmetic_kernels': 15,
        'selected_kernel_count': 18,
        'kernel_order_preserved_in_one_process_and_one_kernelslist': True,
        'single_context': binding[0]['context_from_filename'],
        'single_stream': binding[0]['stream_id'],
        'native_gpu_identity': guard['gpu_identity'],
        'environment_receipt_sha256': sha(ROOT / 'ENVIRONMENT_RECEIPT.json'),
        'address_context_sha256': sha(ROOT / 'ADDRESS_CONTEXT.json'),
        'accepted_input_binding': input_binding,
        'producer_source_binary': producer,
        'driver_sha256': sha(Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1/util/vm_tlb/awma/r101_transient_capture/capture_driver.py')),
        'region_map_sha256': sha(ROOT / 'BUFFER_REGION_MAP.tsv'),
        'region_lifetime_sha256': sha(ROOT / 'REGION_LIFETIME.tsv'),
        'region_address_sanity_sha256': sha(ROOT / 'REGION_ADDRESS_SANITY.json'),
        'trace_member_manifest_sha256': sha(ROOT / 'TRACE_MEMBER_MANIFEST.tsv'),
        'kernelslist_sha256': sha(FORMAL / 'raw/kernelslist'),
        'kernelslist_g_sha256': sha(FORMAL / 'raw/kernelslist.g'),
        'all_traceg_grammar_pass': True, 'terminal_complete': True,
        'all_frozen_trace_parser_only_pass': True,
        'frozen_parser_receipt_sha256': sha(ROOT / 'TRACE_PARSER_RECEIPT.json'),
        'drop_count': 0, 'overflow_count': 0,
        'output_sha256': run['output_sha256'],
        'output_bitwise_accepted': True,
        'raw_capture_relative_path': 'raw/formal_full5',
        'member_count': len(members),
        'members': manifest_members,
        'no_simulator_run': True,
    }
    write('SIM_CAPTURE_MANIFEST.json', manifest)
    print(json.dumps({'capture_id': capture_id, 'members': 18,
                      'region_map_sha256': manifest['region_map_sha256'],
                      'lifetime_sha256': manifest['region_lifetime_sha256'],
                      'total_instructions': sum(row['instructions'] for row in grammar_statuses)}, sort_keys=True))


if __name__ == '__main__':
    main()
