#!/usr/bin/env python3
"""Move per-batch screening samples to raw; keep 55-row compact Git review."""
import csv
import math
import shutil
import statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path('/data/c16/awma/r17_graph_search_20260930')
PACK=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1/docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1')
SOURCE=PACK/'DISCOVERY_TIMING.tsv'
RAW=ROOT/'raw/f2_f3_discovery_timing_per_batch.tsv'

def main():
    assert not RAW.exists(),'Refuse to compact twice or overwrite raw authority'
    shutil.copy2(SOURCE,RAW)
    with RAW.open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
    assert len(rows)==9050
    groups=defaultdict(list)
    for row in rows:
        key=(row['stage'],row['arm'],int(row['query_batch']),row['mode'],int(row['itopk']),int(row['search_width']),int(row['repeat']))
        groups[key].append(float(row['complete_host_ms']))
    out=[]
    for key,values in sorted(groups.items()):
        stage,arm,q,mode,itopk,width,repeat=key
        assert len(values)==256//q
        ordered=sorted(values)
        out.append({'stage':stage,'arm':arm,'query_batch':q,'mode':mode,'itopk':itopk,
            'search_width':width,'repeat':repeat,'batch_samples':len(values),
            'complete_256_query_set_host_ms':f'{sum(values):.9f}',
            'batch_median_host_ms':f'{statistics.median(values):.9f}',
            'batch_p95_host_ms':f'{ordered[math.ceil(0.95*len(ordered))-1]:.9f}',
            'per_batch_raw':'raw/f2_f3_discovery_timing_per_batch.tsv',
            'measurement_class':'DISCOVERY_SCREEN_NOT_FORMAL'})
    assert len(out)==55
    with SOURCE.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(out)
    print(f'RAW_BATCH_ROWS={len(rows)} COMPACT_ROWS={len(out)}')

if __name__=='__main__':main()
