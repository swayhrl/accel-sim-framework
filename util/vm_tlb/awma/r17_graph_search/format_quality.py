#!/usr/bin/env python3
"""Pure formatting repair of already-frozen quality TSV; no GPU work."""
import csv
from pathlib import Path

PACK=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1/docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1')
FILE=PACK/'QUALITY_CALIBRATION.tsv'

with FILE.open(newline='') as f:
    rows=list(csv.DictReader(f,delimiter='\t'))
assert len(rows)==14
for row in rows:
    if not row['identity_note']:
        row['identity_note']='MEASURED'
with FILE.open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
print('QUALITY_TSV_FORMAT_ONLY',len(rows))
