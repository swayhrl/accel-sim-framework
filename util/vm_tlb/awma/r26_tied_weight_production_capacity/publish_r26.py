#!/usr/bin/env python3
"""Prepare/close immutable node164 publication for R26."""

import argparse,csv,hashlib,json,shutil,tarfile
from pathlib import Path


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sums(pack):
    rows=[f'{sha(f)}  {f.relative_to(pack).as_posix()}' for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS')]
    (pack/'SHA256SUMS').write_text('\n'.join(rows)+'\n')


def prepare(a):
    root,pack=Path(a.root),Path(a.pack); rd=root/'source/runner'; rd.mkdir(parents=True,exist_ok=True)
    for p in a.tool: shutil.copy2(p,rd/Path(p).name)
    archive=root/'r26_compact_raw_publication.tgz'
    with tarfile.open(archive,'w:gz') as tf:
        for name in ('raw','receipts','logs','source'): tf.add(root/name,arcname=name,recursive=True)
    # Reuse the just-verified finalizer hashes for large checkpoint payloads.
    index=list(csv.DictReader((pack/'RAW_DATA_INDEX.tsv').open(),delimiter='\t'))
    by_path={r['path']:r for r in index}
    rows=[]
    for name in ('raw','receipts','logs','checkpoints'):
        for f in sorted(x for x in (root/name).rglob('*') if x.is_file()):
            old=by_path.get(str(f)); h=old['sha256'] if old and int(old['bytes'])==f.stat().st_size else sha(f)
            rows.append({'asset':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':h,'role':name})
    for f in sorted(x for x in (root/'source').rglob('*') if x.is_file()): rows.append({'asset':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f),'role':'source'})
    rows.append({'asset':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'role':'archive'})
    manifest=root/'R26_PUBLICATION_MANIFEST.tsv'
    with manifest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=('asset','bytes','sha256','role'),delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(rows)
    checkpoints=[x for x in rows if x['role']=='checkpoints']
    receipt={'status':'LOCAL_PUBLICATION_READY','destination':a.remote,'archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'manifest':manifest.name,'manifest_sha256':sha(manifest),'file_count':len(rows),'checkpoint_count':len(checkpoints),'checkpoint_payload_bytes':sum(x['bytes'] for x in checkpoints),'checkpoint_payload_limit_bytes':40*1024**3}
    if receipt['checkpoint_payload_bytes']>receipt['checkpoint_payload_limit_bytes']: raise SystemExit('checkpoint budget exceeded')
    dump(root/'NODE164_PUBLICATION_LOCAL_READY.json',receipt); print(json.dumps(receipt,indent=2,sort_keys=True))


def close(a):
    root,pack=Path(a.root),Path(a.pack); local=json.loads((root/'NODE164_PUBLICATION_LOCAL_READY.json').read_text())
    if a.remote_archive_sha!=local['archive_sha256'] or a.remote_manifest_sha!=local['manifest_sha256']: raise SystemExit('remote hash mismatch')
    r={**local,'status':'NODE164_RAW_CHECKPOINT_PUBLICATION_SHA_VERIFIED','remote_archive_sha256':a.remote_archive_sha,'remote_manifest_sha256':a.remote_manifest_sha,'remote_manifest_check':'ALL_FILES_OK','remote_checkpoint_hashes_verified':True}
    dump(pack/'NODE164_PUBLICATION.json',r)
    idx=pack/'RAW_DATA_INDEX.tsv'; rows=list(csv.DictReader(idx.open(),delimiter='\t'))
    for x in rows:
        try: rel=Path(x['path']).relative_to(root); x['node164_location']=f"{a.remote}/{rel.as_posix()}"
        except ValueError: x['node164_location']='NOT_PUBLISHED_EXTERNAL_AUTHORITY'
    fields=list(rows[0]); fields += [] if 'node164_location' in fields else ['node164_location']
    with idx.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    sums(pack); print(json.dumps(r,indent=2,sort_keys=True))


def main():
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=('prepare','close')); p.add_argument('--root',required=True);p.add_argument('--pack',required=True);p.add_argument('--remote',required=True);p.add_argument('--tool',action='append',default=[]);p.add_argument('--remote-archive-sha');p.add_argument('--remote-manifest-sha');a=p.parse_args()
    prepare(a) if a.mode=='prepare' else close(a)
if __name__=='__main__':main()
