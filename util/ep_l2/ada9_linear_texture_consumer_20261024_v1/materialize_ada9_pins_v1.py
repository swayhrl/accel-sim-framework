"""Restore verified exact-pin aliases from a frozen ADA9 engineering pack.

This reconstructs files under OUTPUT/original/<absolute source path> only.
It does not execute a simulator, mutate original paths or grant qualification.
"""
from pathlib import Path
import argparse,hashlib,json,os,stat
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('pack');a.add_argument('output');args=a.parse_args()
 P=Path(args.pack).resolve();O=Path(args.output).resolve()
 assert P.is_dir()and not O.exists()
 doc=json.loads((P/'FROZEN_PATH_MAP.json').read_text());rows=doc['pins']
 assert len(rows)==174 and len({x['source']for x in rows})==174
 seen={}
 for x in rows:
  src=Path(x['source']);member=Path(x['member'])
  assert src.is_absolute()and '..'not in src.parts and not member.is_absolute()and '..'not in member.parts
  assert member.parts==('pinned_blobs',x['sha256'])and len(x['sha256'])==64
  b=P/member;assert b.is_file()and not b.is_symlink()and b.stat().st_size==x['bytes']
  if x['sha256']not in seen:assert sha(b)==x['sha256'];seen[x['sha256']]=x['bytes']
  assert stat.S_IMODE(x['mode'])==x['mode']and x['mode']<4096
 O.mkdir()
 outputs=[]
 for x in rows:
  dest=O/'original'/x['source'].lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True)
  with (P/x['member']).open('rb')as fi,dest.open('xb')as fo:
   for b in iter(lambda:fi.read(2**20),b''):fo.write(b)
   fo.flush();os.fsync(fo.fileno())
  dest.chmod(x['mode']);assert sha(dest)==x['sha256']
  outputs.append(dict(source=x['source'],restored=str(dest),sha256=x['sha256'],bytes=x['bytes'],mode=x['mode']))
 proof=dict(schema='ADA9_EXACT_PIN_COLD_MATERIALIZATION_V1',verified_unique_blobs=len(seen),verified_pin_aliases=len(outputs),total_alias_bytes=sum(x['bytes']for x in outputs),original_paths_modified=False,application_executed=False,scope='Verified file restoration only; no native or science qualification implied',files=outputs)
 with (O/'RESTORE.json').open('x')as f:json.dump(proof,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in proof.items()if k!='files'}))
if __name__=='__main__':main()
