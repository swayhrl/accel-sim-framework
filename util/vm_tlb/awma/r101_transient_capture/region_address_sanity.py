#!/usr/bin/env python3
"""Observe actual traceg per-lane addresses inside each declared region."""
from __future__ import annotations

import csv
import json
import lzma
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
FORMAL = ROOT / 'raw/formal_full5'


def main() -> None:
    region_map = json.loads((FORMAL / 'BUFFER_REGIONS_RUNTIME.json').read_text())['regions']
    members = (FORMAL / 'raw/kernelslist.g').read_text().splitlines()
    assert len(members) == 18
    targets = [
        ('X0', 3, 'LDG'),
        ('A', 3, 'STG'),
        ('B', 4, 'STG'),
        ('X1', 5, 'STG'),
    ]
    rows = []
    for region, index, opcode_prefix in targets:
        record = region_map[region]
        base = int(record['base_device_address'])
        end = base + int(record['bytes'])
        found = None
        count = 0
        path = FORMAL / 'raw' / members[index]
        with lzma.open(path, 'rt') as stream:
            for line in stream:
                count += 1
                if '0x' not in line or opcode_prefix not in line:
                    continue
                tokens = line.split()
                for pos, token in enumerate(tokens):
                    if token.startswith(opcode_prefix):
                        opcode_index = pos
                        break
                else:
                    continue
                for token in tokens[opcode_index + 1:]:
                    if not token.startswith('0x'):
                        continue
                    address = int(token, 16)
                    if base <= address < end:
                        src_count = int(tokens[opcode_index + 1])
                        width = int(tokens[opcode_index + 2 + src_count])
                        assert width > 0 and int(tokens[1], 16) > 0
                        found = {'region': region, 'roi_launch_index': index,
                                 'traceg_member': members[index],
                                 'access_opcode': tokens[opcode_index],
                                 'access_kind': 'READ' if opcode_prefix == 'LDG' else 'WRITE',
                                 'memory_width_bytes': width,
                                 'sample_lane_address_hex': hex(address),
                                 'region_base_hex': record['base_hex'],
                                 'region_end_exclusive_hex': record['end_exclusive_hex'],
                                 'active_mask_hex': tokens[1],
                                 'line_number_in_decompressed_traceg': count,
                                 'address_inside_declared_region': True}
                        break
                if found is not None:
                    break
        assert found is not None, (region, members[index], count)
        rows.append(found)
        print(json.dumps(found, sort_keys=True), flush=True)
    with (ROOT / 'REGION_ADDRESS_OBSERVED.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    (ROOT / 'REGION_ADDRESS_SANITY.json').write_text(json.dumps({
        'status': 'PASS', 'regions_observed': [row['region'] for row in rows],
        'all_four_regions_in_simulator_native_traceg': True,
        'access_width_and_per_lane_address_observed': True,
    }, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
