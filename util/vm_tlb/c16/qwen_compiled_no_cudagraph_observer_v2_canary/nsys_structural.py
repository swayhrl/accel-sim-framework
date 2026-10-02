#!/usr/bin/env python3
"""CPU-only NVTX/CUDA structural check for one selected NSYS target request."""
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

def check(sqlite_path,point,runner_path,expected_path):
    raw=json.loads(runner_path.read_text())
    assert raw["point"]==point and raw["arm"]=="STRUCTURAL" and raw["status"]=="PASS"
    db=sqlite3.connect(sqlite_path)
    strings={key:value for key,value in db.execute("select id,value from StringIds")}
    nvtx=[]
    for start,end,text,text_id in db.execute("select start,end,text,textId from NVTX_EVENTS where end is not null"):
        name=text if text is not None else strings.get(text_id)
        if name is not None:nvtx.append((start,end,name))
    outer_name=f"C16_MODE_B_{point}_ON"
    outers=sorted((x for x in nvtx if x[2]==outer_name),key=lambda x:x[0])
    if not outers:
        return {"status":"FAIL","reason":"OUTER_NVTX_RANGE_MISSING","point":point}
    outer=outers[-1]
    selected=[x for x in nvtx if x[2].startswith("C16_STAGEA_") and x[0]>=outer[0] and x[1]<=outer[1]]
    selected.sort(key=lambda x:x[0])
    with expected_path.open(newline="") as f:
        expected=[row for row in csv.DictReader(f,delimiter="\t") if row["point_id"]==point]
    actual=[]
    for start,end,name in selected:
        match=re.fullmatch(r"C16_STAGEA_(\d+)_(.+)",name)
        if match:actual.append({"ordinal":int(match.group(1)),"module":match.group(2),"start":start,"end":end})
    ordinals=[row["ordinal"] for row in actual]
    semantic_exact=len(actual)==len(expected)==4608 and ordinals==list(range(4608)) and all(row["module"]==target["module_name"] for row,target in zip(actual,expected))
    runtime_count=db.execute("select count(*) from CUPTI_ACTIVITY_KIND_RUNTIME where start>=? and end<=?",(outer[0],outer[1])).fetchone()[0]
    kernel_count=db.execute("select count(*) from CUPTI_ACTIVITY_KIND_KERNEL where start>=? and end<=?",(outer[0],outer[1])).fetchone()[0]
    outer_receipt=raw["measured"][0]["semantic"]
    host_semantic_count=len(outer_receipt["semantic_order"]) if outer_receipt is not None else 0
    checks={"target_outer_selected":bool(outer),"semantic_4608_exact":semantic_exact,
            "host_semantic_4608":host_semantic_count==4608,"cuda_runtime_inside_target":runtime_count>0,
            "cuda_kernel_inside_target":kernel_count>0}
    return {"status":"PASS" if all(checks.values()) else "FAIL","point":point,"checks":checks,
            "outer_ranges_in_full_capture":len(outers),"selected_target_outer_index":len(outers)-1,
            "selected_target_outer":{"start":outer[0],"end":outer[1],"label":outer[2]},
            "semantic_range_count":len(actual),"ordinal_min":min(ordinals) if ordinals else None,
            "ordinal_max":max(ordinals) if ordinals else None,
            "cuda_runtime_activity_count_inside_target":runtime_count,
            "cuda_kernel_activity_count_inside_target":kernel_count,
            "duration_role":"STRUCTURAL_ONLY_NOT_NATIVE_TIMING"}

if __name__=="__main__":
    result=check(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),Path(sys.argv[4]))
    Path(sys.argv[5]).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"point":result["point"],"status":result["status"],"semantic_range_count":result.get("semantic_range_count")}))
    if result["status"]!="PASS":raise SystemExit(2)
