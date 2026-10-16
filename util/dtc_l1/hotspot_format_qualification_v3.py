#!/usr/bin/env python3
"""Independent read-only original/candidate differential receipt and full index.

Does not import the normalizer, write a trace, launch a consumer or admit input.
Run after the separate full source-profile verifier. Output directory must be new.
"""
import argparse
from collections import Counter
import gzip
import hashlib
from itertools import zip_longest
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original', required=True, type=Path)
    ap.add_argument('--candidate', required=True, type=Path)
    ap.add_argument('--output-dir', required=True, type=Path)
    a = ap.parse_args()
    require(a.original.resolve() != a.candidate.resolve(), 'Distinct input files required')
    require(a.original.resolve().parent not in a.output_dir.resolve().parents, 'Separate output namespace required')
    a.output_dir.mkdir(parents=True, exist_ok=False)
    index = a.output_dir/'CANDIDATE_CHANGED_RECORDS.tsv.gz'
    original_hash, candidate_hash, index_hash = (hashlib.sha256() for _ in range(3))
    records, lanes = Counter(), Counter()
    offsets = [0, 0]
    identical = 0
    changed = 0
    with a.original.open('rb') as original, a.candidate.open('rb') as candidate, index.open('xb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed:
            def emit(row):
                b = ('\t'.join(map(str, row))+'\n').encode()
                compressed.write(b)
                index_hash.update(b)
            emit(['line','original_offset','candidate_offset','cta','warp','pc','mask','changed_active_lanes','original_line_sha256','candidate_line_sha256','frozen_active_addresses','candidate_active_addresses','evidence_class'])
            for n, pair in enumerate(zip_longest(original, candidate), 1):
                old, new = pair
                require(old is not None and new is not None, 'Line count changed')
                original_hash.update(old)
                candidate_hash.update(new)
                if old == new:
                    identical += 1
                else:
                    t, u = old.split(), new.split()
                    pc = t[4].decode()
                    require(pc in ['0180','0190','0290','02a0','0ab0','0ac0'], 'Unexpected changed PC')
                    j = 7 + int(t[6])
                    m = j + 3 + int(t[j+1])
                    require(t[:m] == u[:m] and int(u[m]) == 0, 'Instruction operands/mask/width changed')
                    mask = int(t[5],16)
                    active = [i for i in range(32) if mask & (1 << i)]
                    require(active, 'Empty-mask record changed')
                    after = [int(v,16) for v in u[m+1:]]
                    require(len(after) == len(active), 'Explicit list count mismatch')
                    if pc in ['0180','0190']:
                        require(int(t[m]) == 0 and len(t[m+1:]) == 32, 'Missing independent full raw vector')
                        vector = [int(v,16) for v in t[m+1:]]
                        before = vector[:len(active)]
                        expected = [vector[i] for i in active]
                        evidence = 'RAW_FULL32_VECTOR_PLUS_HISTORICAL_E_MASK_CONTRACT'
                    else:
                        require(int(t[m]) == 1, 'Expected compressed shared record')
                        base, stride = int(t[m+1],16), int(t[m+2])
                        # Frozen decoder fills its first contiguous printed run;
                        # its zero-initialized array leaves later runs at zero.
                        first_run = []
                        for i in active:
                            if first_run and i != first_run[-1]+1:
                                break
                            first_run.append(i)
                        before = [base+(i-active[0])*stride if i in first_run else 0 for i in active]
                        offset = {'0290':0,'02a0':1024,'0ab0':2048,'0ac0':0}[pc]
                        expected = [4*(32*int(t[3])+i)+offset for i in active]
                        # An E interval containing every P lane can have any
                        # first lane <= first(P). Require a unique anchor under
                        # the reconstructed independent effective-address model.
                        anchors = [first for first in range(min(active[0],30)+1)
                                   if [base+(i-first)*stride for i in active] == expected]
                        require(len(anchors) == 1, 'Nonunique model-conditioned anchor')
                        evidence = 'RECONSTRUCTED_SOURCE_SASS_MODEL_WITH_RAW_CROSSCHECK'
                    require(after == expected and before != after, 'Candidate vector mismatch')
                    count = sum(x != y for x,y in zip(before,after))
                    records[pc] += 1
                    lanes[pc] += count
                    changed += 1
                    emit([n,*offsets,','.join(v.decode() for v in t[:3]),t[3].decode(),pc,t[5].decode(),count,
                          hashlib.sha256(old).hexdigest(),hashlib.sha256(new).hexdigest(),
                          ','.join(hex(v) for v in before),','.join(hex(v) for v in after),evidence])
                offsets[0] += len(old)
                offsets[1] += len(new)
    require(original_hash.hexdigest() == 'ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8', 'Original identity mismatch')
    require(candidate_hash.hexdigest() == '21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985', 'Candidate identity mismatch')
    require(dict(records) == {'0180':1364,'0190':1364,'0290':1364,'02a0':1364,'0ab0':58652,'0ac0':58652}, 'Delta record counts mismatch')
    require(sum(lanes.values()) == 2944024 and changed == 122760, 'Delta lane counts mismatch')
    result = dict(status='PASS_DERIVED_CANDIDATE_DIFF_NOT_CAPTURE_EQUIVALENCE',
                  original_sha256=original_hash.hexdigest(),candidate_sha256=candidate_hash.hexdigest(),
                  original_bytes=offsets[0],candidate_bytes=offsets[1],changed_records=changed,
                  changed_records_by_pc=dict(records),changed_active_lanes_by_pc=dict(lanes),
                  byte_identical_lines=identical,total_lines=identical+changed,
                  index=dict(path=str(index),records=changed,bytes=index.stat().st_size,
                             sha256=digest(index),decoded_sha256=index_hash.hexdigest()),
                  reconstructed_shared_address_scope='0290/02a0/0ab0/0ac0 only; model-conditioned anchors, not original ELF identity',
                  simulation_authorized=False,hold_released=False)
    (a.output_dir/'DIFFERENTIAL_RECHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
