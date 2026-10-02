#!/usr/bin/env python3
"""CPU-only R22F1 raw/tensor node164 publication, SHA checks and compact closure."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path("/data/c16/awma/r22f1_oeq_lowoverhead_replay_20261002")
RAW=ROOT/"raw"
TENSORS=ROOT/"tensors"
WT=Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f1-oeq-lowoverhead-replay-109-v1")
PACK=WT/"docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1"
REMOTE=Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r22f1_oeq_lowoverhead_replay_109_v1")
HOST="hrl174new"


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(8<<20),b""):
            h.update(block)
    return h.hexdigest()


def main():
    decision=json.loads((PACK/"RUN_RECEIPTS.json").read_text())
    if decision["status"]!="R22F1_FAMILY_GAP_UNRESOLVED" or not decision["all_320_formal_numerical_pass"]:
        raise RuntimeError("Scientific STOP authority not closed")
    files=[*sorted(p for p in RAW.iterdir() if p.is_file()),*sorted(p for p in TENSORS.iterdir() if p.is_file())]
    if len(files)<325 or len(list(TENSORS.glob("TP_CALL_*.npz")))!=2:
        raise RuntimeError("Captured tensors/raw incomplete")
    if any(p.suffix in (".sqlite",".nsys-rep",".ncu-rep") for p in files):
        raise RuntimeError("Forbidden profiler artifact in this Goal")
    indexed=[]
    for path in files:
        rel=f"{path.parent.name}/{path.name}"
        indexed.append({"artifact":rel,"node109_path":str(path),"bytes":path.stat().st_size,
                        "sha256":sha(path),"node164_path":str(REMOTE/rel)})
    manifest=ROOT/"NODE164_SHA256SUMS"
    manifest.write_text("".join(f"{x['sha256']}  {x['artifact']}\n" for x in indexed))
    if subprocess.run(["ssh",HOST,"test","-e",str(REMOTE)]).returncode==0:
        raise RuntimeError(f"Refusing existing node164 target {REMOTE}")
    subprocess.run(["ssh",HOST,"mkdir","-p",str(REMOTE/"raw"),str(REMOTE/"tensors")],check=True)
    flags=["rsync","-rt","--no-owner","--no-group","--no-perms","--omit-dir-times"]
    for subdir,source in (("raw",RAW),("tensors",TENSORS)):
        subprocess.run(flags+[str(source)+"/",f"{HOST}:{REMOTE}/{subdir}/"],check=True)
    subprocess.run(flags+[str(manifest),f"{HOST}:{REMOTE}/NODE164_SHA256SUMS"],check=True)
    remote=subprocess.run(["ssh",HOST,f"cd {REMOTE} && sha256sum -c NODE164_SHA256SUMS"],
                          capture_output=True,text=True,check=True)
    oks=[line for line in remote.stdout.splitlines() if line.endswith(": OK")]
    if len(oks)!=len(indexed):
        raise RuntimeError(f"Remote SHA checks {len(oks)} != {len(indexed)}")
    for subdir,source in (("raw",RAW),("tensors",TENSORS)):
        dry=subprocess.run(["rsync","-rcn","--itemize-changes",str(source)+"/",f"{HOST}:{REMOTE}/{subdir}/"],
                           capture_output=True,text=True,check=True)
        if dry.stdout.strip():
            raise RuntimeError(f"Remote checksum-dry-run mismatch {subdir}: {dry.stdout}")
    with (PACK/"RAW_DATA_INDEX.tsv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(indexed[0]),delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(indexed)
    publication={"status":"PASS","node164_root":str(REMOTE),"storage_gateway":HOST,
                 "gateway_role":"node164 storage/SHA only; no node174 scientific compute",
                 "file_count":len(indexed),"total_bytes":sum(x["bytes"] for x in indexed),
                 "manifest_sha256":sha(manifest),"remote_sha256sum_pass_count":len(oks),
                 "rsync_checksum_dry_run_empty":True}
    (PACK/"PUBLICATION_VERIFICATION.json").write_text(json.dumps(publication,indent=2,sort_keys=True)+"\n")
    decision["node164_publication"]=publication
    (PACK/"RUN_RECEIPTS.json").write_text(json.dumps(decision,indent=2,sort_keys=True)+"\n")
    pack_files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    code_files=sorted(p for p in (WT/"util/vm_tlb/awma/r22f1_oeq").iterdir() if p.is_file() and p.suffix==".py")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(WT)}\n" for p in pack_files+code_files))
    print(json.dumps({"status":"PUBLISHED_SHA_CLOSED","file_count":len(indexed),"total_bytes":publication["total_bytes"],
                      "node164_root":str(REMOTE),"manifest_sha256":publication["manifest_sha256"]},sort_keys=True))


if __name__=="__main__":main()
