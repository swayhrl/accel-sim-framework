#!/usr/bin/env python3
"""CPU arithmetic/address/port checks; consumes committed audit tables, never traces."""
import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIB = 1024


def table(name):
    with (HERE / 'inputs' / name).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def verify_core(root, identities):
    checked = 0
    for item in identities['identities']:
        if item['source_commit'].startswith('6fba0136'):
            data = (root / item['source_path']).read_bytes()
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256']
            checked += 1
    source = (root / 'src/gpgpu-sim/shader.cc').read_text()
    findings = json.loads((HERE / 'CPU_SOURCE_FINDINGS.json').read_text())
    for item in findings['findings']:
        start = source.index('void ' + item['function'] + '()')
        opening = source.index('{', start)
        depth = 0
        for end in range(opening, len(source)):
            if source[end] == '{':
                depth += 1
            elif source[end] == '}':
                depth -= 1
                if depth == 0:
                    break
        body = source[start:end+1]
        assert hashlib.sha256(body.encode()).hexdigest() == item['body_sha256']
        assert source[:start].count('\n')+1 == item['line']
        if item['function'].endswith('L1_latency_queue_cycle'):
            assert 'm_L1D->access(' in body and 'data_port_free(' not in body
        else:
            assert 'm_L1D->fill(' in body and 'm_L1D->fill_port_free(' not in body
    assert checked == 7
    return checked


def run(core_root):
    identities = json.loads((HERE / 'INPUT_IDENTITY.json').read_text())
    core_hashes = verify_core(core_root, identities)
    for item in identities['identities']:
        if 'snapshot' in item:
            data = (HERE / item['snapshot']).read_bytes()
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256']
    payload = table('PAYLOAD_MEMBERS.tsv')
    audit = table('FROZEN629_CAPACITY_CALCULATION_V1.tsv')
    assert len(payload) == len(audit) == 629
    original = {(r['workload'], r['ordinal']): r for r in payload}
    assert len(original) == 629
    keys = {(r['workload'], r['ordinal']) for r in audit}
    assert keys == set(original)
    shared_histogram = Counter()
    for row in audit:
        old = original[row['workload'], row['ordinal']]
        assert row['member_sha256'] == old['expected_sha256'] == old['actual_sha256']
        assert old['identity'] == 'PASS'
        assert row['kernel'] == old['kernel']
        assert int(row['shared_per_cta_bytes']) == int(old['shared_bytes'])
        shared = int(row['computed_shared_partition_kib'])
        conventional = 48 - shared
        assert shared in (0, 8, 16, 32)
        assert int(row['computed_effective_l1_kib']) == 128 - shared
        assert int(row['proposed_dtc_kib']) == 80
        assert int(row['proposed_remaining_conventional_kib']) == conventional
        assert int(row['proposed_total_data_shared_kib']) == 128
        assert int(row['computed_resident_shared_bytes']) <= shared * KIB
        assert row['capacity_arithmetic'] == 'FITS'
        shared_histogram[shared] += 1

    layouts = []
    for shared in (0, 8, 16, 32, 64, 100):
        c = 48 - shared
        fits = c >= 16
        result = dict(shared_kib=shared, baseline_l1_kib=128-shared,
                      dtc_kib=80, conventional_kib=c, bytes_feasible_for_candidate=fits)
        if fits:
            # Half-open capacity coordinates, not global or shared ISA addresses.
            ranges = [(0, 80*KIB), (80*KIB, (128-shared)*KIB),
                      ((128-shared)*KIB, 128*KIB)]
            assert all(a <= b for a, b in ranges)
            assert all(ranges[i][1] == ranges[i+1][0] for i in range(2))
            assert sum(b-a for a, b in ranges) == 128*KIB
            assoc = c*KIB // (4*128)
            assert assoc in (96, 80, 64, 32)
            assert 4*assoc*128 == c*KIB
            # SAME 48KiB tail cells in every epoch: 32 banks x384 x4B.
            # C line's four sectors each span a group of eight word banks.
            # Bank j: rows [0,8C) ordinary; rows [8C,384) shared.
            c_coords = {80*KIB + bank*1536 + line*4
                        for line in range(4*assoc) for bank in range(32)}
            assert len(c_coords)*4 == c*KIB
            s_coords = {80*KIB + bank*1536 + (8*c+word)*4
                        for bank in range(32) for word in range(8*shared)}
            assert len(s_coords)*4 == shared*KIB
            assert c_coords.isdisjoint(s_coords)
            assert c_coords | s_coords == set(range(80*KIB, 128*KIB, 4))
            result.update(conventional_assoc=assoc, capacity_rank_ranges_bytes=ranges,
                          tail_conventional_rows_per_bank=8*c,
                          tail_shared_rows_per_bank=8*shared)
        else:
            # Preserve at least 16KiB side cache. These are capacity deficits.
            result['excess_kib_if_fixed_pool_and_c16'] = 80+16+shared-128
        layouts.append(result)

    # DTC bank=id mod4; row=id//4. Each bank has 160 x128B =20KiB.
    coords = {bank*20*KIB + row*128 + sector*32
              for bank in range(4) for row in range(160) for sector in range(4)}
    assert len(coords) == 640*4
    assert coords == set(range(0, 80*KIB, 32))
    for physical_id in range(640):
        bank, row = physical_id % 4, physical_id // 4
        assert all(bank*20*KIB + row*128 + sec*32 in coords for sec in range(4))

    # Any four 32B collections must be served under unchanged R1 aggregate quota.
    patterns = list(itertools.product(range(4), repeat=4))
    single_read_conflicts = 0
    for pattern in patterns:
        demand = Counter(pattern)
        assert sum(demand.values()) == 4 and max(demand.values()) <= 4
        if max(demand.values()) > 1:
            single_read_conflicts += 1
    # Tail banks: C data 1RW + C fill 1W + shared 1RW are dedicated role ports.
    # Enumerate C sector group, fill group, shared bank, and both RW directions.
    tail_cases = 0
    for data_group, fill_group, shared_bank, data_write, shared_write in itertools.product(
            range(4), range(4), range(32), (0, 1), (0, 1)):
        for bank in range(32):
            data = bank//8 == data_group
            fill = bank//8 == fill_group
            sh = bank == shared_bank
            reads = int(data and not data_write) + int(sh and not shared_write)
            writes = int(data and data_write) + int(fill) + int(sh and shared_write)
            assert reads <= 2 and writes <= 3 and reads+writes <= 3
        tail_cases += 1
    assert single_read_conflicts == 232
    return dict(status='PASS_CPU_LAYOUT_ONLY_MODERN_DTC_HOLD',
                core_source_hash_matches=core_hashes, source_guard_findings_rechecked=2,
                trace_payloads_opened=0, reused_member_hash_matches=629,
                shared_histogram=dict(sorted(shared_histogram.items())),
                layouts=layouts, dtc_sector_locations=len(coords),
                four_read_bank_patterns=len(patterns),
                patterns_requiring_more_than_one_read_per_bank=single_read_conflicts,
                tail_role_port_cases=tail_cases,
                port_claim='Necessary provisioning check, not RTL/area/timing validation',
                scope='Single partition epoch; no concurrent mixed kernels or transitions proven')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core-root', type=Path, default=Path(
        '/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1'))
    args = parser.parse_args()
    print(json.dumps(run(args.core_root), ensure_ascii=False, indent=2))
