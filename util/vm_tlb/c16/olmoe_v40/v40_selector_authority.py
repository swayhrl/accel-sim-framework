#!/usr/bin/env python3
"""Freeze the exact V40-consumed selector using C16_SELECTOR_CANONICAL_V1."""
import csv
import hashlib
import json
import sys
from pathlib import Path

SELECTOR = Path('/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')
SHARDS = Path('/data/c16/olmoe_v40/typed_sweep/formal_admission/FORMAL_243_SHARDS.jsonl')
OUT = Path('/data/c16/olmoe_v40_publish_v1/selector_authority')
HISTORICAL = '9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33'


def sha256_bytes(value): return hashlib.sha256(value).hexdigest()
def sha256_file(path): return sha256_bytes(path.read_bytes())


def main():
    if OUT.exists(): raise SystemExit(f'refusing to overwrite authority output: {OUT}')
    with SELECTOR.open('r', encoding='utf-8', newline='') as handle:
        parsed = list(csv.reader(handle, delimiter='\t'))
    if not parsed: raise SystemExit('empty selector')
    columns = parsed[0]
    if len(columns) != len(set(columns)) or 'static_index' not in columns: raise SystemExit('invalid columns')
    rows = []
    for source in parsed[1:]:
        if len(source) != len(columns): raise SystemExit('missing/extra row fields')
        rows.append(dict(zip(columns, source)))
    indices = [int(row['static_index'], 0) for row in rows]
    if len(rows) != 243 or len(set(indices)) != 243 or any(index < 0 or index >= 1096 for index in indices): raise SystemExit('selector structural closure')
    shard_indices = {json.loads(line)['static_index'] for line in SHARDS.read_text().splitlines() if line}
    if shard_indices != set(indices): raise SystemExit('formal shard membership closure')
    if not {101, 103, 1085}.issubset(shard_indices): raise SystemExit('typed anchor closure')
    canonical_columns = sorted(columns)
    canonical_rows = [{key: row[key] for key in canonical_columns} for row in sorted(rows, key=lambda row: int(row['static_index'], 0))]
    canonical = json.dumps({'schema': 'C16_SELECTOR_CANONICAL_V1', 'columns': canonical_columns, 'rows': canonical_rows}, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
    OUT.mkdir(parents=True)
    canonical_path = OUT / 'VARIANT_A_COMPLETE_STATIC_SELECTOR.canonical_v1.json'
    canonical_path.write_bytes(canonical.encode('utf-8'))
    source = Path(__file__).resolve()
    receipt = {
        'status': 'PASS_PROVENANCE_REPAIR',
        'historical_v38_normalized_selector_sha256': HISTORICAL,
        'historical_hash_status': 'OPAQUE_HISTORICAL_CHECKSUM_SERIALIZATION_NOT_DURABLY_RETAINED',
        'v39r2_historical_report_status': 'REPORTED_REPRODUCED_BUT_PRODUCER_NOT_DURABLY_RETAINED',
        'source_raw_tsv_path': str(SELECTOR), 'selector_raw_tsv_sha256': sha256_file(SELECTOR),
        'canonicalization_schema': 'C16_SELECTOR_CANONICAL_V1', 'canonicalizer_source_path': str(source),
        'canonicalizer_source_sha256': sha256_file(source), 'canonical_selector_path': str(canonical_path),
        'selector_canonical_v1_sha256': sha256_file(canonical_path), 'row_count': len(rows),
        'column_count': len(columns), 'unique_static_count': len(set(indices)),
        'exact_formal_shard_membership_equality': True, 'typed_anchors_present': [101, 103, 1085],
        'scientific_identity_changed': False, 'gpu_recapture_required': False,
    }
    (OUT / 'SELECTOR_AUTHORITY_REPAIR_V1.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__': main()
