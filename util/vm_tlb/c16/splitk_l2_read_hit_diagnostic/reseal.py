#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--pack',type=Path,required=True);a=p.parse_args();files=[{'path':str(q.relative_to(a.raw)),'bytes':q.stat().st_size,'sha256':sha(q)} for q in sorted(a.raw.rglob('*')) if q.is_file() and q.name!='RAW_MANIFEST.json'];(a.raw/'RAW_MANIFEST.json').write_text(json.dumps({'status':'SEALED','files':files},indent=2,sort_keys=True)+'\n');lines=[f'{sha(q)}  {q.name}' for q in sorted(a.pack.iterdir()) if q.is_file() and q.name!='SHA256SUMS'];(a.pack/'SHA256SUMS').write_text('\n'.join(lines)+'\n');print(json.dumps({'status':'PASS_RESEAL','raw_files':len(files),'pack_files':len(lines)}))
if __name__=='__main__':main()
