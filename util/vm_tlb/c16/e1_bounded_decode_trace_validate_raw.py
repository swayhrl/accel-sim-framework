#!/usr/bin/env python3
"""Fail-closed raw capture and census/formal sequence validator."""
import argparse,csv,json,lzma,re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TERMINAL=re.compile(r"^ROUTEB_TERMINAL_COMPLETE kernel=(\d+) device_reported=(\d+) receiver_accepted=(\d+) raw_records=(\d+) drop_count=(\d+) overflow_count=(\d+) raw=(.*)$")
RAW=re.compile(r"^kernel-(\d+)-ctx_(0x[0-9a-f]+)\.trace\.xz$")
FIELDS=("global_dynamic_order","decode_iteration","exact_function","grid","block","stream","semantic_layer","semantic_identity")
def read_tsv(path):
 with Path(path).open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def xz_ok(path):
 with lzma.open(path,"rb") as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b""):pass
 return path.name
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",type=Path,required=True);p.add_argument("--start",type=int,required=True);p.add_argument("--end",type=int,required=True)
 p.add_argument("--census-tsv",type=Path,required=True);p.add_argument("--formal-tsv",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
 p.add_argument("--index",type=Path,required=True);p.add_argument("--workers",type=int,default=8);a=p.parse_args()
 expected=list(range(a.start,a.end+1));rawdir=a.run/"raw";stdout=(a.run/"stdout.log").read_text().splitlines()
 terminal={}
 for line in stdout:
  m=TERMINAL.match(line)
  if not m:continue
  kid,reported,accepted,written,drops,overflow,path=m.groups();kid=int(kid)
  if kid in terminal:raise RuntimeError(f"duplicate terminal {kid}")
  values=list(map(int,(reported,accepted,written,drops,overflow)))
  if values[0]<=0 or values[0]!=values[1] or values[0]!=values[2] or values[3:]!=[0,0]:raise RuntimeError(f"accounting {kid} {values}")
  terminal[kid]={"device_reported":values[0],"receiver_accepted":values[1],"raw_records":values[2],"drop_count":0,"overflow_count":0,"reported_path":path}
 if sorted(terminal)!=expected:raise RuntimeError("terminal ID closure")
 partial=list(rawdir.glob("*.partial"))
 if partial:raise RuntimeError(f"partial artifacts remain {partial[:3]}")
 artifacts={}
 for path in rawdir.glob("kernel-*.trace.xz"):
  m=RAW.match(path.name)
  if not m:raise RuntimeError(f"raw name {path.name}")
  kid=int(m.group(1))
  if kid in artifacts:raise RuntimeError(f"duplicate raw {kid}")
  artifacts[kid]={"path":path,"context":m.group(2)}
 if sorted(artifacts)!=expected:raise RuntimeError("raw artifact ID closure")
 members=(rawdir/"kernelslist").read_text().splitlines()
 if members!=[artifacts[k]["path"].name for k in expected]:raise RuntimeError("kernelslist order/membership")
 census=read_tsv(a.census_tsv);formal=read_tsv(a.formal_tsv)
 if len(census)!=len(expected) or len(formal)!=len(expected):raise RuntimeError("sequence cardinality")
 for c,f,k in zip(census,formal,expected):
  if int(c["global_dynamic_order"])!=k or int(f["global_dynamic_order"])!=k:raise RuntimeError("sequence ID")
  if any(c[x]!=f[x] for x in FIELDS):raise RuntimeError(f"formal/census mismatch {k}")
 with ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(xz_ok,[artifacts[k]["path"] for k in expected]))
 rows=[]
 for c,k in zip(census,expected):
  row={x:c[x] for x in FIELDS};row.update(terminal[k]);row.update({"trace_artifact":artifacts[k]["path"].name,
   "size_bytes":artifacts[k]["path"].stat().st_size,"context":artifacts[k]["context"],"xz_integrity":"PASS"});rows.append(row)
 fields=list(FIELDS)+["trace_artifact","size_bytes","context","device_reported","receiver_accepted","raw_records","drop_count","overflow_count","xz_integrity"]
 a.index.parent.mkdir(parents=True,exist_ok=True)
 with a.index.open("w",newline="") as f:w=csv.DictWriter(f,fields,delimiter="\t");w.writeheader();w.writerows(rows)
 result={"status":"PASS","start":a.start,"end":a.end,"kernel_count":len(rows),"sequence_contiguous":True,
  "terminal_accounting":"PASS","drop_count":0,"overflow_count":0,"partial_count":0,"xz_integrity":"PASS",
  "kernelslist_exact_match":True,"formal_census_exact_match":True,"raw_compressed_bytes":sum(x["size_bytes"] for x in rows)}
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
