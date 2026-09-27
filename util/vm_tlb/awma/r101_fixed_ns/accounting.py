#!/usr/bin/env python3
"""Source-grounded BF16 square-tile intermediate accounting; no GPU use."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')


def main() -> None:
    ncu = json.loads((ROOT / 'NCU_SUMMARY.json').read_text())
    rows = []
    for fixture, filename in (
        ('discovery', 'TILE_POPULATIONS_DISCOVERY_EXACT.tsv'),
        ('holdout', 'TILE_POPULATIONS_HOLDOUT_EXACT.tsv'),
    ):
        with (ROOT / filename).open(newline='') as stream:
            entries = list(csv.DictReader(stream, delimiter='\t'))
        for edge in sorted({int(row['tile_edge']) for row in entries}):
            count = sum(int(row['tile_count']) for row in entries if int(row['tile_edge']) == edge)
            tile_bytes = count * edge * edge * 2
            target = f'K{edge}' if edge == 128 else f'L{edge}'
            metric = ncu.get(target) if fixture == 'discovery' else None
            ns = metric['three_NS_family_metric_sums_in_reported_units'] if metric else None
            rows.append({
                'fixture': fixture,
                'arm': target,
                'tile_edge': edge,
                'tile_count': count,
                'bf16_bytes_per_X_or_A_or_B_or_C_buffer': tile_bytes,
                'source_allocated_four_buffers_bytes_X_A_B_C': 4 * tile_bytes,
                'source_logical_A_B_C_writes_five_iterations_bytes': 15 * tile_bytes,
                'source_logical_X_C_pingpong_written_C_bytes': 5 * tile_bytes,
                'ncu_ns_family_dram_read_Mbyte': ns['dram__bytes_read.sum'] if ns else '',
                'ncu_ns_family_dram_write_Mbyte': ns['dram__bytes_write.sum'] if ns else '',
                'ncu_ns_family_l2_requested_Mbyte': ns['lts__t_bytes.sum'] if ns else '',
                'ncu_ns_family_dram_write_over_logical_ABC_write': (
                    ns['dram__bytes_write.sum'] * 1_000_000 / (15 * tile_bytes)
                    if ns else ''
                ),
                'source_reuse': 'X,C swap each iteration; A,B,C storage reused; no five-copy allocation',
                'qualification': 'L256/L512 not mathematically equivalent to S128; NCU only K128/L512 discovery',
            })
    with (ROOT / 'LARGE_TILE_ACCOUNTING.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
