#!/usr/bin/env python3
"""Recursive non-executing pickle scan for embedded FX/Inductor source blobs."""
import hashlib
import json
import pickletools
from collections import Counter,deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/"docs/vm_tlb/review_packs/C16_COMPILED_PATH_ARTIFACT_ATTRIBUTION_FEASIBILITY_109_V1"
AUTH=json.loads((PACK/"COMPILE_CACHE_AUTHORITY.json").read_text())
MP02B=next(x for x in AUTH["roots"] if x["point"]=="MP02" and x["mode"]=="B")
MODEL=Path(MP02B["cache_path"])/"rank_0_0/model"
MARKERS=("Topologically Sorted Source Nodes","output_code","CompiledFxGraph","GraphModule","stack_trace",
         "gate_up_proj","down_proj","self_attn","torch._C._nn.linear","triton_poi_fused_mul_silu_slice")

def main():
    queue=deque([(0,"root",MODEL.read_bytes())]);seen=set();summary=[]
    while queue:
        depth,label,data=queue.popleft()
        digest=hashlib.sha256(data).hexdigest()
        if digest in seen:continue
        seen.add(digest)
        ops=Counter();texts=[];children=[]
        try:
            for op,arg,pos in pickletools.genops(data):
                ops[op.name]+=1
                if isinstance(arg,(str,bytes)):
                    b=arg.encode() if isinstance(arg,str) else arg
                    if len(b)>=500:
                        sample=b.decode("utf-8",errors="ignore")
                        hits=[m for m in MARKERS if m in sample]
                        if hits:
                            texts.append({"position":pos,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),
                                          "markers":hits,"prefix":sample[:180].replace("\n","\\n")})
                    if depth<4 and isinstance(arg,bytes) and len(b)>1000 and b.startswith(b"\x80\x04"):
                        child=f"{label}/{pos}"
                        children.append({"label":child,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
                        queue.append((depth+1,child,b))
            status="PASS"
        except Exception as e:status=f"UNREADABLE:{type(e).__name__}:{e}"
        summary.append({"depth":depth,"label":label,"bytes":len(data),"sha256":digest,"status":status,
                        "opcode_counts":dict(sorted(ops.items())),"matching_long_strings":sorted(texts,key=lambda x:-x["bytes"])[:80],
                        "matching_long_string_count":len(texts),"child_pickles":children})
    (PACK/"AOT_NESTED_PROVENANCE_SCAN.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","pickle_streams":len(summary),"depth_counts":dict(Counter(x["depth"] for x in summary)),
                      "matching_strings":sum(x["matching_long_string_count"] for x in summary)}))

if __name__=="__main__":main()
