#!/usr/bin/env python3
"""Check all published bound copies against their current execution originals."""
import hashlib
import json
import pathlib

ROOT=pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
DEST=ROOT/'review/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/supplement_v1'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    index=json.loads((DEST/'BOUND_FILE_INDEX.json').read_bytes())
    for item in index['files']:
        rel=pathlib.Path(item['path'])
        assert sha(DEST/rel)==item['sha256']==sha(ROOT/rel), rel
        assert (DEST/rel).stat().st_size==item['bytes'], rel
    for family in ('gemm','stencil'):
        for spec in (DEST/'cases').glob('EP_PERF_CLEAN128_'+family.upper()+'_WV_EXT*/control/FROZEN_SPEC.json'):
            data=json.loads(spec.read_bytes())
            assert sha(pathlib.Path(data['resource_module_ref']['path']))==data['resource_module_ref']['sha256']
            assert sha(pathlib.Path(data['host_qualification_ref']['path']))==data['host_qualification_ref']['sha256']
    print('BOUND_COPIES_AND_SPEC_PINS_PASS',len(index['files']))

if __name__=='__main__':main()
