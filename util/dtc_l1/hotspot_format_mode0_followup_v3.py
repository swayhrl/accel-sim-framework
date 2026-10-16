#!/usr/bin/env python3
"""Read only flagged legacy mode0 members from format screening; no repair.

Disambiguates zero-mask extras from active full32 lists. The historical E-mask
contract supplies lane association for full32 lists; no interpretation is
adopted for any workload by this diagnostic.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--format-members',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a = ap.parse_args()
    if a.report.exists():
        raise ValueError('New report required')
    rows = [r for r in csv.DictReader(a.format_members.open(),delimiter='\t') if int(r['mode0_excess'])]
    counts = {}
    examples = {}
    for r in rows:
        if r['trace_version'] != '0' or r['workload'] not in ['btree','dwt2d']:
            raise ValueError('Follow-up scope differs from screened legacy extras')
        c = counts.setdefault(r['workload'],Counter())
        found = 0
        with open(r['path'],'rb') as f:
            for n,line in enumerate(f,1):
                if b' 0 0x' not in line:
                    continue
                t = line.split()
                if not t or not t[0].isdigit():
                    continue
                j = 7+int(t[6])
                width = j+2+int(t[j+1])
                if not int(t[width]) or int(t[width+1]) != 0:
                    continue
                mask = int(t[5],16)
                lanes = [i for i in range(32) if mask & (1<<i)]
                raw = [int(v,16) for v in t[width+2:]]
                if len(raw) <= len(lanes):
                    continue
                found += 1
                c['excess_records'] += 1
                c['active_excess_records' if lanes else 'zero_mask_excess_records'] += 1
                c['full32_excess_records' if len(raw)==32 else 'non32_excess_records'] += 1
                if lanes and len(raw)==32:
                    before = raw[:len(lanes)]
                    conditional = [raw[i] for i in lanes]
                    different = sum(v!=w for v,w in zip(before,conditional))
                    c['conditional_changed_records'] += bool(different)
                    c['conditional_changed_active_addresses'] += different
                    key = r['workload']+':'+t[4].decode()
                    examples.setdefault(key,dict(path=r['path'],ordinal=int(r['ordinal']),line=n,
                                                line_sha256=hashlib.sha256(line).hexdigest(),mask=f'{mask:08x}',
                                                lanes=lanes,frozen_active=before,
                                                historical_full32_active=conditional,
                                                historical_producer_binding='SOURCE_FAMILY_NOT_CAPTURE_BINARY_RECEIPT'))
        if found != int(r['mode0_excess']):
            raise ValueError('Follow-up did not account for every flagged excess record')
    report = dict(status='FLAGGED_MODE0_READ_ONLY_FOLLOWUP_COMPLETE_NOT_NEW_INPUT_ADMISSION',
                  selected_members=len(rows),workload_counts=counts,examples=examples,
                  original_trace_changed=False,normalization_selected=False,admission_changed=False)
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
