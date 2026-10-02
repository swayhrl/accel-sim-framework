#!/usr/bin/env python3
"""Mechanical post-finalizer hash closure for R26 compact evidence."""

import argparse, csv, hashlib
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--pack',required=True);a=p.parse_args();pack=Path(a.pack)
    idx=pack/'RAW_DATA_INDEX.tsv';rows=list(csv.DictReader(idx.open(),delimiter='\t'));fields=list(rows[0])
    repaired=[]
    for r in rows:
        f=Path(r['path'])
        if f.exists() and f.stat().st_size!=int(r['bytes']):
            r['bytes']=str(f.stat().st_size);r['sha256']=sha(f);repaired.append(str(f))
    with idx.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    sums=[f'{sha(f)}  {f.relative_to(pack).as_posix()}' for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS')]
    (pack/'SHA256SUMS').write_text('\n'.join(sums)+'\n')
    print('repaired',repaired);print('sha256sums',sha(pack/'SHA256SUMS'))


if __name__=='__main__':main()
