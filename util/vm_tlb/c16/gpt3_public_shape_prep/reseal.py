#!/usr/bin/env python3
"""Hash-close producer raw and review artifacts without interpreting partial data."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as stream:
  for block in iter(lambda:stream.read(1<<20),b""):h.update(block)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--pack",type=Path,required=True);a=p.parse_args()
 raw=[{"path":str(x.relative_to(a.raw)),"bytes":x.stat().st_size,"sha256":sha(x)} for x in sorted(a.raw.rglob("*")) if x.is_file()]
 (a.raw/"RAW_MANIFEST.json").write_text(json.dumps({"status":"SEALED","files":raw},indent=2,sort_keys=True)+"\n")
 lines=[f"{sha(x)}  {x.name}" for x in sorted(a.pack.iterdir()) if x.is_file() and x.name!="SHA256SUMS"]
 (a.pack/"SHA256SUMS").write_text("\n".join(lines)+"\n")
 print(json.dumps({"status":"PASS_RESEAL","raw_files":len(raw),"pack_files":len(lines)}))
if __name__=="__main__":main()
