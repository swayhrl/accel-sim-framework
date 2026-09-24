#!/usr/bin/env python3
"""Parse driver/tracer interleaving into deterministic decode/kernel authority."""
import argparse,csv,json,re
from collections import Counter
from pathlib import Path

CENSUS=re.compile(r"^ROUTEB_CENSUS_LAUNCH grid_launch_id=(\d+) function=(.*) grid=([0-9,]+) block=([0-9,]+) stream=(\d+)$")
FORMAL=re.compile(r"^MEMTRACE: CTX (0x[0-9a-f]+) - LAUNCH - Kernel pc (0x[0-9a-f]+) - Kernel name (.*) - grid launch id (\d+) - grid size ([0-9,]+) - block size ([0-9,]+) - nregs (\d+) - shmem (\d+) - cuda stream id (\d+)$")
def main():
 p=argparse.ArgumentParser();p.add_argument("--stdout",type=Path,required=True);p.add_argument("--json",type=Path,required=True);p.add_argument("--tsv",type=Path,required=True);a=p.parse_args()
 active_decode=None;stack=[];rows=[];events=[];profile_open=False
 for line_number,line in enumerate(a.stdout.read_text(errors="strict").splitlines(),1):
  if line.startswith("C16_TRACE_EVENT "):
   e=json.loads(line.split(" ",1)[1]);e["stdout_line"]=line_number;events.append(e);kind=e["kind"]
   if kind=="PROFILE_RANGE_BEGIN": profile_open=True
   elif kind=="PROFILE_RANGE_END": profile_open=False
   elif kind=="DECODE_BEGIN": active_decode=e["decode_index"]
   elif kind=="DECODE_END":
    if active_decode!=e["decode_index"] or stack:raise RuntimeError("decode/semantic stack closure")
    active_decode=None
   elif kind=="SEMANTIC_BEGIN":stack.append((e["decode_index"],e["layer_index"],e["category"]))
   elif kind=="SEMANTIC_END":
    key=(e["decode_index"],e["layer_index"],e["category"])
    if not stack or stack[-1]!=key:raise RuntimeError(f"semantic stack mismatch {stack[-1:]}, {key}")
    stack.pop()
   continue
  m=CENSUS.match(line)
  if m:
   kid=int(m.group(1));rows.append({"global_dynamic_order":kid,"decode_iteration":active_decode,
    "exact_function":m.group(2),"grid":m.group(3),"block":m.group(4),"stream":int(m.group(5)),
    "semantic_layer":stack[-1][1] if stack else None,"semantic_identity":stack[-1][2] if stack else "UNKNOWN",
    "profile_range_active":profile_open,"stdout_line":line_number})
   continue
  m=FORMAL.match(line)
  if m:
   kid=int(m.group(4));rows.append({"global_dynamic_order":kid,"decode_iteration":active_decode,
    "exact_function":m.group(3),"grid":m.group(5),"block":m.group(6),"stream":int(m.group(9)),
    "semantic_layer":stack[-1][1] if stack else None,"semantic_identity":stack[-1][2] if stack else "UNKNOWN",
    "profile_range_active":profile_open,"stdout_line":line_number,"context":m.group(1),"pc":m.group(2),
    "nregs":int(m.group(7)),"shmem":int(m.group(8))})
 selected=[r for r in rows if r["decode_iteration"] in (1,2,3)]
 counts=Counter(r["decode_iteration"] for r in selected)
 bounds={str(d):{"first":min(r["global_dynamic_order"] for r in selected if r["decode_iteration"]==d),
                 "last":max(r["global_dynamic_order"] for r in selected if r["decode_iteration"]==d),
                 "kernel_count":counts[d]} for d in (1,2,3)}
 start=bounds["1"]["first"];end=bounds["3"]["last"]
 ids=[r["global_dynamic_order"] for r in selected]
 if ids!=list(range(start,end+1)):raise RuntimeError("selected dynamic sequence is not contiguous")
 if not all(r["profile_range_active"] for r in selected):raise RuntimeError("selected kernel outside profiler range")
 up_counts=Counter((r["decode_iteration"],r["semantic_layer"]) for r in selected if r["semantic_identity"]=="up_proj")
 if set(up_counts)!={(d,l) for d in (1,2,3) for l in range(28)}:raise RuntimeError("up_proj semantic occurrence closure")
 out={"status":"PASS","source":str(a.stdout),"selected_decode_indices":[1,2,3],"selected_prefix_start":start,
  "selected_prefix_end":end,"selected_kernel_count":len(selected),"per_decode":bounds,
  "sequence_contiguous":True,"all_selected_inside_profiler_range":True,
  "up_proj_occurrences_per_decode":{str(d):len({l for dd,l in up_counts if dd==d}) for d in (1,2,3)},
  "intervening_non_up_kernel_count":sum(r["semantic_identity"]!="up_proj" for r in selected),
  "all_launch_count":len(rows),"event_count":len(events)}
 a.json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 fields=["global_dynamic_order","decode_iteration","exact_function","grid","block","stream","semantic_layer","semantic_identity","profile_range_active","stdout_line"]
 with a.tsv.open("w",newline="") as f:
  w=csv.DictWriter(f,fields,delimiter="\t",extrasaction="ignore");w.writeheader();w.writerows(selected)
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
