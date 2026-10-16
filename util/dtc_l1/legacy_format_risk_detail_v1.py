#!/usr/bin/env python3
"""Bounded read-only detail for three already-screened scientific format risks.

Reads only members flagged by the V3 format screen, reuses r0 SHA receipts, and
never writes a trace or chooses an address interpretation. Geometry projections
are CPU set calculations, not a simulator or performance prediction.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import time

MASK64 = (1 << 64) - 1
EXPECTED = {'btree': (1,6000,0), 'lud': (63,0,57536), '2DConvolution': (1,0,40940)}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def width_from_opcode(op):
    for t in op.split('.'):
        if t.isdigit():
            return int(t)//8
        if t.startswith('U') and t[1:].isdigit():
            return int(t[1:])//8
    return 4


def footprints(values, width, size):
    return frozenset(q for v in values for q in range(v//size,(v+width-1)//size+1))


def shared_service(values):
    banks = defaultdict(set)
    for v in values:
        banks[(v//4)%32].add(v//4)
    return max(map(len,banks.values()),default=0)


def classify(op):
    t = op.split('.')
    if t[0]=='LDG':
        return 'BYPASS_GLOBAL_LOAD' if ('STRONG' in t and 'GPU' in t) or 'BYPASS' in t else 'CACHEABLE_GLOBAL_LOAD'
    if t[0] in ['STG','ATOM','ATOMG','RED']:
        return 'GLOBAL_STORE_OR_ATOMIC'
    if t[0] in ['LDS','STS','LDSM','ATOMS']:
        return 'SHARED'
    return 'OTHER_REQUIRES_REVIEW'


def projections(before, alternatives, width, path):
    c = Counter()
    c['records_with_different_active_addresses'] = int(any(v!=before for v in alternatives))
    if path in ['CACHEABLE_GLOBAL_LOAD','BYPASS_GLOBAL_LOAD','GLOBAL_STORE_OR_ATOMIC']:
        for size,label in [(32,'sector32'),(128,'line128')]:
            old = footprints(before,width,size)
            new = [footprints(v,width,size) for v in alternatives]
            c['possible_'+label+'_identity_change_records'] = int(any(v!=old for v in new))
            c['possible_'+label+'_count_change_records'] = int(any(len(v)!=len(old) for v in new))
    if path=='SHARED':
        old = shared_service(before)
        possible = {shared_service(v) for v in alternatives}
        c['possible_shared_service_change_records'] = int(possible!={old})
        c['shared_service_invariant_all_anchors_records'] = int(possible=={old})
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--format-members',type=Path,required=True)
    ap.add_argument('--inventory',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    a = ap.parse_args()
    screened = list(csv.DictReader(a.format_members.open(),delimiter='\t'))
    inventory = {r['path']:r for r in csv.DictReader(a.inventory.open(),delimiter='\t')}
    selected = [r for r in screened if r['workload'] in EXPECTED and
                (int(r['mode0_excess']) or int(r['mode1_nonzero_first_nonzero_stride']))]
    for workload,expected in EXPECTED.items():
        rows = [r for r in selected if r['workload']==workload]
        require((len(rows),sum(int(r['mode0_excess']) for r in rows),
                 sum(int(r['mode1_nonzero_first_nonzero_stride']) for r in rows))==expected,'Fixed bounded selection differs')
    require(len(selected)==65,'Exactly65 previously flagged members required')
    for r in selected:
        require(Path(r['path']).parent not in a.output_dir.resolve().parents,'Separate output namespace required')
    a.output_dir.mkdir(parents=True,exist_ok=False)
    summaries = defaultdict(Counter)
    groups = defaultdict(Counter)
    examples = {}
    masks = defaultdict(set)
    member_receipts = []
    index = a.output_dir/'FLAGGED_RECORDS.tsv.gz'
    index_hash = hashlib.sha256()
    started = time.time()
    with index.open('xb') as raw, gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as compressed:
        def emit(fields):
            b = ('\t'.join(map(str,fields))+'\n').encode()
            compressed.write(b)
            index_hash.update(b)
        emit(['workload','ordinal','kernel','pc','opcode','mode','flag','line','byte_offset','mask','active_lanes','frozen_addresses','firstE0_or_full32_addresses','latest_compatible_firstE_addresses','anchor_count','original_line_sha256'])
        for number,r in enumerate(selected,1):
            p = Path(r['path'])
            previous = inventory[str(p)]
            require(p.stat().st_size==int(previous['bytes']),'Input size changed')
            require(previous['actual_sha256']==previous['expected_sha256'],'Prior identity audit failed')
            offset = 0
            found = Counter()
            with p.open('rb') as f:
                for n,line in enumerate(f,1):
                    begin = offset
                    offset += len(line)
                    if not line[:1] in b'0123456789abcdef' or not line.strip():
                        continue
                    t = line.split()
                    off = 0 if int(r['trace_version'])>=3 else 4
                    mask = int(t[off+1],16)
                    j = off+3+int(t[off+2])
                    w = j+2+int(t[j+1])
                    if not int(t[w]):
                        continue
                    mode = int(t[w+1])
                    lanes = [i for i in range(32) if mask & (1<<i)]
                    alternatives = None
                    if mode==0 and len(t[w+2:])>len(lanes):
                        found['mode0_excess'] += 1
                        require(r['workload']=='btree' and len(t[w+2:])==32 and lanes,'Unexpected mode0 scope')
                        raw_addresses = [int(v,16) for v in t[w+2:]]
                        before = raw_addresses[:len(lanes)]
                        alternatives = [[raw_addresses[i] for i in lanes]]
                        flag = 'FULL32_LIST_ASSOCIATION_SOURCE_FAMILY_CONDITIONAL'
                    elif mode==1 and lanes and lanes[0] and int(t[w+3]):
                        found['mode1_nonzero_first_nonzero_stride'] += 1
                        require(lanes==list(range(lanes[0],lanes[-1]+1)),'Sparse mask outside known scope')
                        base,stride = int(t[w+2],16),int(t[w+3])
                        before = [(base+(i-lanes[0])*stride)&MASK64 for i in lanes]
                        alternatives = [[(base+(i-first)*stride)&MASK64 for i in lanes]
                                        for first in range(min(lanes[0],30)+1)]
                        flag = 'NONZERO_EXECUTION_ANCHOR_UNRESOLVED'
                    if alternatives is None:
                        continue
                    op = t[j].decode()
                    width = width_from_opcode(op)
                    path = classify(op)
                    require(path!='OTHER_REQUIRES_REVIEW','New memory form requires bounded investigation')
                    pc = t[off].decode()
                    key = (r['workload'],previous['kernel'],pc,op,str(mode),str(width),path,flag)
                    c = projections(before,alternatives,width,path)
                    c['flagged_records'] += 1
                    c['active_lane_addresses'] += len(lanes)
                    if mode==0:
                        c['different_active_lane_addresses'] += sum(x!=y for x,y in zip(before,alternatives[0]))
                    else:
                        c['different_active_lane_addresses'] += len(lanes)
                    groups[key].update(c)
                    summaries[r['workload']].update(c)
                    masks[key].add(f'{mask:08x}')
                    line_sha = hashlib.sha256(line).hexdigest()
                    examples.setdefault(key,dict(path=str(p),ordinal=int(r['ordinal']),line=n,byte_offset=begin,
                                                  original_line_sha256=line_sha,mask=f'{mask:08x}',lanes=lanes,
                                                  frozen=before,firstE0_or_full32=alternatives[0],
                                                  latest_compatible_firstE=alternatives[-1],anchor_count=len(alternatives),
                                                  raw_record=line.decode().rstrip('\n')))
                    emit([r['workload'],r['ordinal'],previous['kernel'],pc,op,mode,flag,n,begin,f'{mask:08x}',
                          ','.join(map(str,lanes)),','.join(hex(v) for v in before),
                          ','.join(hex(v) for v in alternatives[0]),','.join(hex(v) for v in alternatives[-1]),
                          len(alternatives),line_sha])
            require(found['mode0_excess']==int(r['mode0_excess']) and
                    found['mode1_nonzero_first_nonzero_stride']==int(r['mode1_nonzero_first_nonzero_stride']),
                    'Detail count disagrees with reused screening')
            member_receipts.append(dict(workload=r['workload'],ordinal=int(r['ordinal']),path=str(p),
                                        prior_sha256=previous['actual_sha256'],identity_check='PRIOR_BODY_SHA_REUSED_CURRENT_SIZE_CHECK_ONLY',
                                        bytes_read=offset,matched_screen_counts=dict(found)))
            if number%10==0:
                print(json.dumps(dict(flagged_members_detailed=number,total=65)),flush=True)
    columns = ['workload','kernel','pc','opcode','mode','parser_width','memory_path','risk_indicator']
    metrics = sorted({k for c in groups.values() for k in c})
    with (a.output_dir/'PC_OPCODE_RISK_COUNTS.tsv').open('x') as f:
        writer = csv.writer(f,delimiter='\t',lineterminator='\n')
        writer.writerow(columns+metrics+['distinct_masks','first_example_json'])
        for key,c in sorted(groups.items()):
            writer.writerow([*key,*[c[k] for k in metrics],len(masks[key]),json.dumps(examples[key],separators=(',',':'))])
    result = dict(status='BOUNDED_SCIENTIFIC_RISK_DETAIL_NOT_CORRECTION_OR_EXEMPTION',selected_members=65,
                  selection='Only prior-format-screen flagged members: Btree1, LUD63, 2DConvolution1; no full629 audit',
                  bytes_read=sum(r['bytes_read'] for r in member_receipts),workload_counts=dict(summaries),
                  member_receipts=member_receipts,index=dict(path=str(index),sha256=sha(index),decoded_sha256=index_hash.hexdigest(),
                  records=sum(c['flagged_records'] for c in summaries.values())),
                  shared_geometry='32 banks,4-byte words,warp_parts1,unlimited broadcast; first address per active lane as frozen Core model',
                  address_projection='Enumerate every compatible firstE from0 to min(firstP,30); full32 raw-list association for mode0. All conditional; no anchor selected.',
                  global_projection='32B sector and128B line byte-footprint sets; geometry only, not executed cache/speedup prediction',
                  original_trace_changed=False,parser_changed=False,admission_changed=False,simulator_launches=0,
                  elapsed_seconds=time.time()-started)
    (a.output_dir/'RISK_DETAIL_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],workload_counts=result['workload_counts'],index=result['index'])),flush=True)


if __name__=='__main__':
    main()
