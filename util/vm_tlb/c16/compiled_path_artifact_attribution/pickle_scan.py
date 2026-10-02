#!/usr/bin/env python3
"""Non-executing pickle opcode/string scan of pinned AOT model blobs."""
import hashlib
import json
import pickletools
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"
KEYS=("Qwen2","qwen2","gate_up_proj","down_proj","act_fn","self_attn","output_code","stack_trace",
      "source_fn_stack","triton_poi","triton_red","inductor_cache","GraphModule","fx_graph","original_aten")

def main():
    authority=json.loads((PACK/"COMPILE_CACHE_AUTHORITY.json").read_text())
    result=[]
    for row in authority["roots"]:
        if row["mode"]!="B" or row["point"]!="MP02":
            continue
        path=Path(row["cache_path"])/"rank_0_0/model"
        data=path.read_bytes()
        opcounts=Counter();strings=[];hits=[];nested=[]
        try:
            for opcode,arg,pos in pickletools.genops(data):
                opcounts[opcode.name]+=1
                if isinstance(arg,(str,bytes)):
                    payload=arg.encode() if isinstance(arg,str) else arg
                    strings.append((pos,len(payload),hashlib.sha256(payload).hexdigest()))
                    sample=payload[:1000000].decode("utf-8",errors="ignore")
                    matched=[key for key in KEYS if key in sample]
                    if matched:
                        hits.append({"pickle_position":pos,"length_bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest(),
                                     "matched_markers":matched,"prefix":sample[:220].replace("\n","\\n")})
                    if isinstance(arg,bytes) and len(arg)>100000 and arg.startswith(b"\x80"):
                        child_ops=Counter();child_strings=[]
                        try:
                            for child_op,child_arg,child_pos in pickletools.genops(arg):
                                child_ops[child_op.name]+=1
                                if isinstance(child_arg,(str,bytes)):
                                    child_data=child_arg.encode() if isinstance(child_arg,str) else child_arg
                                    if len(child_data)>1000:
                                        child_text=child_data.decode("utf-8",errors="ignore")
                                        child_strings.append({"nested_position":child_pos,"length_bytes":len(child_data),
                                                              "sha256":hashlib.sha256(child_data).hexdigest(),
                                                              "markers":[key for key in KEYS if key in child_text],
                                                              "prefix":child_text[:180].replace("\n","\\n")})
                            child_status="PASS"
                        except Exception as child_error:
                            child_status=f"UNREADABLE:{type(child_error).__name__}:{child_error}"
                        nested.append({"parent_pickle_position":pos,"parent_length_bytes":len(arg),
                                       "status":child_status,"opcode_counts":dict(sorted(child_ops.items())),
                                       "long_string_count":len(child_strings),
                                       "long_strings":sorted(child_strings,key=lambda x:-x["length_bytes"])[:30]})
            parse_status="PASS"
        except Exception as e:
            parse_status=f"UNREADABLE:{type(e).__name__}:{e}"
        result.append({"point":row["point"],"mode":row["mode"],"path":str(path),"sha256":hashlib.sha256(data).hexdigest(),
                       "parse_status":parse_status,"opcode_counts":dict(sorted(opcounts.items())),
                       "string_count":len(strings),"max_string_bytes":max((x[1] for x in strings),default=0),
                       "marker_hits":hits[:150],"marker_hit_count":len(hits),
                       "nested_pickles":nested,
                       "safety":"pickletools opcode scan only; no pickle.load and no torch/vLLM import"})
    (PACK/"AOT_PICKLE_OPCODE_SCAN.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","blobs":len(result),"marker_hits":[x["marker_hit_count"] for x in result],"max_string":[x["max_string_bytes"] for x in result]}))

if __name__=="__main__":main()
