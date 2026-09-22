#!/usr/bin/env python3
"""Per-shard-only locality analysis for admitted V40 C16WARP1 shards."""
import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/olmoe_v40/typed_sweep/formal_admission')
SHARDS = ROOT / 'FORMAL_243_SHARDS.jsonl'
REC = struct.Struct('<6I32Q')


def atomic_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def main():
    rows, aggregate_roles = [], Counter()
    sums = {size: 0 for size in (128, 4096, 65536, 2 * 1024 * 1024)}
    for shard in (json.loads(line) for line in SHARDS.read_text().splitlines() if line):
        root = Path(shard['attempt_root'])
        raw = (root / 'trace.bin').read_bytes()
        ranges = [(entry['semantic_role'], int(entry['ptr'], 16), int(entry['ptr'], 16) + entry['bytes'])
                  for entry in json.loads((root / 'ADDRESS_CONTEXT.json').read_text())['ranges']]
        unique = {size: set() for size in sums}
        roles, lane_events = Counter(), 0
        for offset in range(40, len(raw), REC.size):
            record = REC.unpack_from(raw, offset)
            for lane, address in enumerate(record[6:]):
                if record[1] >> lane & 1:
                    lane_events += 1
                    role = next((name for name, low, high in ranges if low <= address < high), 'OTHER')
                    roles[role] += 1
                    for size, values in unique.items(): values.add(address // size)
        for size, values in unique.items(): sums[size] += len(values)
        aggregate_roles.update(roles)
        rows.append({'static_index': shard['static_index'], 'classification': shard['classification'],
                     'warp_records': shard['record_count'], 'active_lane_events': lane_events,
                     'role_events': dict(roles), 'unique_128B_lines': len(unique[128]),
                     'unique_4K_pages': len(unique[4096]), 'unique_64K_pages': len(unique[65536]),
                     'unique_2M_pages': len(unique[2 * 1024 * 1024])})
    (ROOT / 'FORMAL_243_PER_SHARD_ANALYSIS.jsonl').write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows))
    total = sum(aggregate_roles.values())
    atomic_json(ROOT / 'FORMAL_243_ANALYSIS.json', {
        'status': 'PASS_PER_SHARD_ONLY', 'evidence_condition': 'actual JIT variant A',
        'total_shards': len(rows), 'executed_count': sum(row['classification'] == 'EXECUTED' for row in rows),
        'zero_count': sum(row['classification'] == 'ZERO_EXECUTION_PROVEN' for row in rows),
        'dynamic_warp_records': sum(row['warp_records'] or 0 for row in rows),
        'active_lane_events': total, 'role_events': dict(aggregate_roles),
        'role_fractions': {role: count / total for role, count in sorted(aggregate_roles.items())},
        'SUM_OF_PER_SHARD_UNIQUES': {'128B_lines': sums[128], '4K_pages': sums[4096],
                                     '64K_pages': sums[65536], '2M_pages': sums[2 * 1024 * 1024]},
        'per_shard_analysis_jsonl': str(ROOT / 'FORMAL_243_PER_SHARD_ANALYSIS.jsonl'),
        'prohibited_analyses': ['cross-shard absolute VA union', 'cross-shard global chronology',
                                'cross-shard reuse distance', 'fresh-process absolute VA comparison']})


if __name__ == '__main__':
    main()
