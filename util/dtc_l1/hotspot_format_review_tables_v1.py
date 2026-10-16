#!/usr/bin/env python3
"""Derive compact review tables from the one-pass diagnostic and frozen ledgers."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def write(path, rows):
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def bank_cycles(addresses):
    # Diagnostic of the frozen 32 banks, 4-byte words, one warp part,
    # unlimited-broadcast branch. This does not execute the simulator.
    banks = defaultdict(set)
    for a in addresses:
        banks[(a//4)%32].add(a//4)
    return max(map(len,banks.values()), default=0)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--diagnostics', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    a=ap.parse_args();out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
    delta=read(a.diagnostics/'DECODER_DELTA.tsv')
    groups=Counter();banks=Counter()
    for row in delta:
        n=int(row['records']);groups[(row['opcode'],row['pc'],row['category'])]+=n
        if row['mode']=='1':
            d=json.loads(row['address_example_json'])
            before=bank_cycles(d['frozen'])
            for hypothesis in ['hypothetical_ordinal','hypothetical_lane_first','hypothetical_anchor0']:
                banks[(hypothesis,before,bank_cycles(d[hypothesis]))]+=n
    write(out/'AFFECTED_PC_COUNTS.tsv',[dict(opcode=op,pc=pc,category=cat,records=n)
                                       for (op,pc,cat),n in sorted(groups.items())])
    write(out/'BANK_SERVICE_HYPOTHESES.tsv',[dict(hypothesis=h,frozen_word_bank_cycles=b,
                                                hypothetical_word_bank_cycles=c,records=n,
                                                qualification='CONDITIONAL_GEOMETRY_NOT_EXECUTED_TIMING')
                                          for (h,b,c),n in sorted(banks.items())])
    base=a.repo/'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack'
    records=[]
    def add(label,arm,terminal,source,path,identity='',core='',binary='',action='PRESERVE_REVIEW_BEFORE_PAIRED_REEXECUTION'):
        records.append(dict(label=label,workload='Hotspot1',arm=arm,
                            terminal_validation=terminal,scientific_promotion='HOLD_INPUT_INTERPRETATION',
                            source_table=source,receipt_or_run=path,identity=identity,core=core,
                            binary_sha256=binary,action=action,
                            affected_scope='SHARED_MODE1_AND_CACHEABLE_GLOBAL_MODE0',
                            trace_member_sha256='ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8'))
    rel='r0/ROW_REUSE_LEDGER.tsv'
    for r in read(base/rel):
        if r['workload']=='Hotspot1':
            add('HISTORICAL_PRIMARY_'+r['mode'],r['mode'],r['historical_acceptance'],rel,
                r['evidence_path'],r['evidence_sha256'],r['source_core'],r['binary_sha256'])
    rel='r0/TC80_REUSE_LEDGER.tsv'
    for r in read(base/rel):
        if r['workload']=='Hotspot1':
            add('HISTORICAL_TC80_CAPACITY_MATCHED','TC80',r.get('status','PRIOR_RECEIPT_PRESERVED'),
                rel,r['run_dir'],r['attempt_uuid'],r['core_source_head'],r['runtime_sha256'])
    rel='r2/CANONICAL_BASELINE_REUSE.tsv'
    for r in read(base/rel):
        if r['workload']=='Hotspot1':
            add('CANONICAL_'+r['variant'],r['variant'],'EXACT_CANONICAL_BASELINE_REUSE',rel,
                r['run_dir'],r['attempt_uuid'],r.get('core',''),r.get('binary_sha256',''))
    attempts={r['label']:r for r in read(base/'checkpoint_20261016T094353Z/ALL_ATTEMPTS.tsv')}
    rel='r2/REGISTERED_ROWS_V2.tsv'
    for r in read(base/rel):
        if r['workload']=='Hotspot1':
            t=attempts.get(r['label'],{})
            add(r['label'],r['arm'],t.get('status','ADMISSION_HOLD_NO_ATTEMPT'),rel,
                t.get('run_dir',r['spec_path']),t.get('attempt_uuid',r['spec_sha256']),
                t.get('core',''),t.get('binary_sha256',''),
                'PRESERVE_REVIEW_BEFORE_PAIRED_REEXECUTION' if t else 'KEEP_ADMISSION_HOLD')
    t=attempts['B0_RTX4080_OLD_SASS_Hotspot1']
    add(t['label'],'RTX4080_BASELINE_ONLY',t['status'],'checkpoint_20261016T094353Z/ALL_ATTEMPTS.tsv',
        t['run_dir'],t['attempt_uuid'],t['core'],t['binary_sha256'])
    write(out/'AFFECTED_ROWS.tsv',records)
    # Supplementary discovery of tracked Hotspot JSON receipts, not new admission
    # or a claim that every historical sensitivity row was a primary result.
    historical=[]
    for p in sorted((a.repo/'docs/dtc_l1/fast64/generated').rglob('*')):
        if p.is_file() and p.suffix=='.json' and 'hotspot' in p.name.lower():
            data=p.read_bytes()
            historical.append(dict(path=str(p.relative_to(a.repo)),sha256=hashlib.sha256(data).hexdigest(),
                                   bytes=len(data),status='DISCOVERY_ONLY_INSPECT_ROW_IDENTITY_BEFORE_REUSE'))
    if historical:
        write(out/'HISTORICAL_RECEIPT_DISCOVERY.tsv',historical)
    print(json.dumps(dict(registered_and_reused_rows=len(records),pc_groups=len(groups),
                          bank_hypotheses=len(banks),historical_receipt_files=len(historical))))


if __name__=='__main__':
    main()
