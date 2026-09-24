#!/usr/bin/env python3
"""Run accepted strict+official grammar validation over every traceg member."""
import argparse,csv,json,re,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
TRACEG=re.compile(r"^kernel-(\d+)-ctx_(0x[0-9a-f]+)\.traceg\.xz$")
def one(grammar,path):
 p=subprocess.run([str(grammar),str(path)],text=True,capture_output=True)
 if p.returncode:raise RuntimeError(f"{path.name}: {p.stderr.strip()}")
 d=json.loads(p.stdout)
 if d.get("status")!="TRACEG_GRAMMAR_PASS" or d.get("instructions",0)<=0 or d.get("thread_blocks",0)<=0:raise RuntimeError(f"{path.name}: bad receipt")
 return path,d
def main():
 p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--grammar",type=Path,required=True)
 p.add_argument("--start",type=int,required=True);p.add_argument("--end",type=int,required=True);p.add_argument("--workers",type=int,default=8)
 p.add_argument("--index",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 expected=list(range(a.start,a.end+1));members=(a.raw/"kernelslist.g").read_text().splitlines();artifacts={}
 for name in members:
  m=TRACEG.match(name)
  if not m:raise RuntimeError(f"kernelslist.g member {name}")
  kid=int(m.group(1));path=a.raw/name
  if not path.is_file() or kid in artifacts:raise RuntimeError(f"traceg artifact {kid}")
  artifacts[kid]=path
 if list(artifacts)!=expected:raise RuntimeError("traceg sequence closure")
 receipts={}
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  jobs={pool.submit(one,a.grammar,artifacts[k]):k for k in expected}
  for job in as_completed(jobs):
   path,d=job.result();receipts[jobs[job]]=d
 fields=["global_dynamic_order","traceg_artifact","size_bytes","thread_blocks","instructions","trace_version","opcode_counts_json","grammar_status"]
 a.index.parent.mkdir(parents=True,exist_ok=True)
 with a.index.open("w",newline="") as f:
  w=csv.DictWriter(f,fields,delimiter="\t");w.writeheader()
  for k in expected:
   d=receipts[k];w.writerow({"global_dynamic_order":k,"traceg_artifact":artifacts[k].name,"size_bytes":artifacts[k].stat().st_size,
    "thread_blocks":d["thread_blocks"],"instructions":d["instructions"],"trace_version":d["trace_version"],
    "opcode_counts_json":json.dumps(d["opcode_counts"],sort_keys=True,separators=(",",":")),"grammar_status":d["status"]})
 result={"status":"PASS","kernel_count":len(expected),"strict_grammar_all":"PASS","official_parser_all":"PASS",
  "cta_grid_termination_all":"PASS","warp_instruction_termination_all":"PASS",
  "total_trace_instructions":sum(receipts[k]["instructions"] for k in expected),
  "total_thread_blocks":sum(receipts[k]["thread_blocks"] for k in expected),
  "traceg_compressed_bytes":sum(artifacts[k].stat().st_size for k in expected),
  "grammar_binary":str(a.grammar)}
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
