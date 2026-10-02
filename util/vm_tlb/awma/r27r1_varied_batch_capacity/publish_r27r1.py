#!/usr/bin/env python3
"""Publish compact CPU-only R27R1 Gate-B0 STOP evidence."""

import argparse,csv,hashlib,json,shutil,tarfile
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sums(pack):(pack/'SHA256SUMS').write_text('\n'.join(f'{sha(f)}  {f.relative_to(pack).as_posix()}' for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS'))+'\n')
def prepare(a):
 root,pack=Path(a.root),Path(a.pack);rd=root/'source/runner';rd.mkdir(parents=True,exist_ok=True)
 for p in a.tool:shutil.copy2(p,rd/Path(p).name)
 archive=root/'r27r1_gate_a_b0_stop_publication.tgz'
 with tarfile.open(archive,'w:gz') as tf:
  for n in ('raw','receipts','logs','source'):tf.add(root/n,arcname=n,recursive=True)
 rows=[]
 for n in ('raw','receipts','logs','source'):
  for f in sorted(x for x in (root/n).rglob('*') if x.is_file()):rows.append({'asset':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f),'role':n})
 rows.append({'asset':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'role':'archive'})
 manifest=root/'R27R1_PUBLICATION_MANIFEST.tsv'
 with manifest.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=('asset','bytes','sha256','role'),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 r={'status':'LOCAL_PUBLICATION_READY','destination':a.remote,'archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'manifest':manifest.name,'manifest_sha256':sha(manifest),'manifest_items':len(rows),'exact_input_admitted':False,'CUDA_JIT_operations':0,'external_parent_common_checkpoint':{'path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r26_tied_weight_production_capacity_boundary_109_v1_20261002/checkpoints/COMMON_POST_BOOTSTRAP.pt','bytes':2626691315,'sha256':'09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55','R27R1_recheck_passed':True}}
 dump(root/'NODE164_PUBLICATION_LOCAL_READY.json',r);print(json.dumps(r,indent=2,sort_keys=True))
def close(a):
 root,pack=Path(a.root),Path(a.pack);r=json.loads((root/'NODE164_PUBLICATION_LOCAL_READY.json').read_text())
 if r['archive_sha256']!=a.remote_archive_sha or r['manifest_sha256']!=a.remote_manifest_sha:raise SystemExit('remote mismatch')
 r.update({'status':'NODE164_R27R1_GATE_A_B0_STOP_PUBLICATION_VERIFIED','remote_archive_sha256':a.remote_archive_sha,'remote_manifest_sha256':a.remote_manifest_sha,'remote_items_verified':r['manifest_items']});dump(pack/'NODE164_PUBLICATION.json',r)
 idx=pack/'RAW_DATA_INDEX.tsv';rows=list(csv.DictReader(idx.open(),delimiter='\t'));fields=list(rows[0]);
 if 'node164_location' not in fields:fields.append('node164_location')
 for x in rows:
  try:x['node164_location']=f"{a.remote}/{Path(x['path']).relative_to(root).as_posix()}"
  except ValueError:x['node164_location']=x['path'] if x['role']=='external_parent_checkpoint' else 'NOT_PUBLISHED_EXTERNAL'
 with idx.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 sums(pack);print(json.dumps(r,indent=2,sort_keys=True))
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('prepare','close'));p.add_argument('--root',required=True);p.add_argument('--pack',required=True);p.add_argument('--remote',required=True);p.add_argument('--tool',action='append',default=[]);p.add_argument('--remote-archive-sha');p.add_argument('--remote-manifest-sha');a=p.parse_args();prepare(a) if a.mode=='prepare' else close(a)
if __name__=='__main__':main()
