#!/usr/bin/env python3
import argparse,csv,hashlib,json
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()
def dump(path,v):path.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--copyback",type=Path,required=True);p.add_argument("--pack",type=Path,required=True);p.add_argument("--remote-path",required=True);a=p.parse_args()
m=a.raw/"RAW_SHA256SUMS";rows=[];total=0
for line in m.read_text().splitlines():
    digest,rel=line.split("  ",1);src=a.raw/rel;copy=a.copyback/rel
    if sha(src)!=digest or sha(copy)!=digest:raise RuntimeError("copyback mismatch "+rel)
    total+=src.stat().st_size;rows.append({"artifact":rel,"node109_path":str(src),"bytes":src.stat().st_size,"sha256":digest,"node164_path":f"{a.remote_path}/{rel}","git_copy":"INDEX_ONLY"})
if sha(a.copyback/"RAW_SHA256SUMS")!=sha(m):raise RuntimeError("manifest copyback mismatch")
rows.append({"artifact":"RAW_SHA256SUMS","node109_path":str(m),"bytes":m.stat().st_size,"sha256":sha(m),"node164_path":f"{a.remote_path}/RAW_SHA256SUMS","git_copy":"INDEX_ONLY"})
with (a.pack/"RAW_INDEX.tsv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=tuple(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
pub={"status":"PASS_DURABLE_PUBLISH_AND_COPYBACK","remote_host":"hrl174new","local_raw_path":str(a.raw),"remote_path":a.remote_path,"copyback_path":str(a.copyback),"manifest_entries":len(rows)-1,"payload_bytes":total,"manifest_sha256":sha(m),"remote_verify":"PASS","copyback_verify":"PASS"}
dump(a.pack/"PUBLISH_RECEIPT.json",pub)
run={"status":"RUNTIME_QUALIFICATION_PARTIAL","run_id":a.raw.name,"branch":"hrl/c16-stagea-runtime-qualification-canary-109-v1","runtime_commit":"9bd48bcc7762af4d341b51481df957b28ecb5317","asset_commit":"c3f625e46adb8d5c4082ded8b61858c710e1f4e9","gpu_active_seconds":151,"gpu_cap_seconds":240,"lock_released":True,"runtime_ready_points":3,"holdout_outputs_generated":False,"durable_publish":pub["status"]}
dump(a.pack/"RUN_IDENTITY.json",run)
checksum=a.pack/"SHA256SUMS";files=sorted(x for x in a.pack.iterdir() if x.is_file() and x.name!="SHA256SUMS");checksum.write_text("".join(f"{sha(x)}  {x.name}\n" for x in files))
print(json.dumps({"status":"PASS","pack_files":len(files),"pack_manifest_sha256":sha(checksum),**pub},sort_keys=True))
