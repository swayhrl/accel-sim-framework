#!/usr/bin/env python3
"""Non-destructive semantic classification of NVBit trace-list entries."""
from __future__ import annotations
import argparse, hashlib, json, lzma, re, sys, tempfile
from collections import Counter
from pathlib import Path
NCCL=re.compile(r"(?:nccl|allreduce|all_gather|allgather|reduce_scatter|reducescatter|broadcast)",re.I); MEMCPY=re.compile(r"(?:^|[^a-z])memcpy(?:htod|dtoh|dtod|peer|async)?",re.I)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cls(n): return "MEMCPY" if MEMCPY.search(n) else "NCCL_COLLECTIVE" if NCCL.search(n) else "COMPUTE"
def header(p):
  op=lzma.open if p.suffix==".xz" else open; names=[]
  with op(p,"rt",errors="replace") as f:
    for line in f:
      if line.startswith("-kernel name = "): names.append(line.rstrip().split("= ",1)[1])
      if line.startswith("#traces format"): break
  return names[0] if len(names)==1 and names[0] else None
def build(lines,td):
  out=[]
  for i,raw in enumerate(lines):
    r={"index":i,"raw":raw,"trace_filename":None,"semantic_kernel_name":None,"classification":"UNKNOWN_OTHER"}
    if MEMCPY.search(raw): r["classification"]="MEMCPY"
    elif raw.startswith("kernel"):
      p=td/raw; r["trace_filename"]=raw
      if p.is_file(): r["semantic_kernel_name"]=header(p)
      if r["semantic_kernel_name"]: r["classification"]=cls(r["semantic_kernel_name"])
    out.append(r)
  return out
def selftest():
  with tempfile.TemporaryDirectory() as d:
    p=Path(d); (p/"kernel-a.traceg.xz").write_bytes(lzma.compress(b"-kernel name = ncclDevKernel_AllReduce_Sum\n#traces format\n")); (p/"kernel-b.traceg.xz").write_bytes(lzma.compress(b"-kernel name = gemm\n#traces format\n")); assert [x["classification"] for x in build(["kernel-a.traceg.xz","kernel-b.traceg.xz","MemcpyHtoD,0,4","missing"],p)]==["NCCL_COLLECTIVE","COMPUTE","MEMCPY","UNKNOWN_OTHER"]
def main():
  a=argparse.ArgumentParser(); a.add_argument("--kernelslist",type=Path); a.add_argument("--trace-dir",type=Path); a.add_argument("--output-dir",type=Path); a.add_argument("--self-test",action="store_true"); x=a.parse_args()
  if x.self_test: selftest(); print("PASS semantic classifier self-test"); return
  if not(x.kernelslist and x.trace_dir and x.output_dir): a.error("paths required")
  lines=x.kernelslist.read_text().splitlines(); rows=build(lines,x.trace_dir); assert len(rows)==len(lines); x.output_dir.mkdir(parents=True,exist_ok=True); counts=Counter(y["classification"] for y in rows)
  m={"schema_version":"m4a-semantic-kernel-classification-v1","source":str(x.kernelslist),"source_sha256":sha(x.kernelslist),"trace_dir":str(x.trace_dir),"counts":counts,"unique_semantic_names":{c:len({y["semantic_kernel_name"] for y in rows if y["classification"]==c}) for c in counts},"kernels":rows}
  (x.output_dir/"semantic-full-kernel-manifest.json").write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
  for c,n in (("COMPUTE","compute-only-kernelslist.g"),("NCCL_COLLECTIVE","nccl-only-kernelslist.g")): (x.output_dir/n).write_text("\n".join(y["raw"] for y in rows if y["classification"]==c)+"\n")
  (x.output_dir/"classification-command.txt").write_text(" ".join(sys.argv)+"\n"); print(json.dumps({"counts":counts,"source_sha256":m["source_sha256"]},sort_keys=True))
if __name__=="__main__": main()
