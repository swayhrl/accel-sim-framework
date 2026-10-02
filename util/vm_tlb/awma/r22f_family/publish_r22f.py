#!/usr/bin/env python3
"""CPU-only one-way R22F raw publication and compact SHA closure."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path("/data/c16/awma/r22f_r21a_family_localization_20261002")
RAW = ROOT / "raw"
WT = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r22f-r21a-family-localization-109-v1")
PACK = WT / "docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1"
REMOTE = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r22f_r21a_family_localization_109_v1")
HOST = "hrl174new"


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    result = json.loads((PACK / "RUN_RECEIPTS.json").read_text())
    if result["status"] != "R22F_R21A_FAMILY_RESULT_MIXED" or result["formal_sample_count"] != 72:
        raise RuntimeError("Scientific decision not closed")
    files = sorted(x for x in RAW.iterdir() if x.is_file())
    if len(files) < 140 or not (RAW / "R22F_ONE_PROFILE.nsys-rep").is_file():
        raise RuntimeError("Scientific raw bundle incomplete")
    indexed=[]
    for path in files:
        indexed.append({"artifact":f"raw/{path.name}","node109_path":str(path),"bytes":path.stat().st_size,
                        "sha256":sha(path),"node164_path":str(REMOTE / "raw" / path.name)})
    manifest=ROOT / "RAW_SHA256SUMS"
    manifest.write_text("".join(f"{x['sha256']}  {x['artifact']}\n" for x in indexed))
    exists=subprocess.run(["ssh",HOST,"test","-e",str(REMOTE)]).returncode
    if exists==0:
        raise RuntimeError(f"Node164 target already exists; refusing overwrite: {REMOTE}")
    subprocess.run(["ssh",HOST,"mkdir","-p",str(REMOTE / "raw")],check=True)
    flags=["rsync","-rt","--no-owner","--no-group","--no-perms","--omit-dir-times"]
    subprocess.run(flags+[str(RAW)+"/",f"{HOST}:{REMOTE}/raw/"],check=True)
    subprocess.run(flags+[str(manifest),f"{HOST}:{REMOTE}/RAW_SHA256SUMS"],check=True)
    remote=subprocess.run(["ssh",HOST,f"cd {REMOTE} && sha256sum -c RAW_SHA256SUMS"],
                          text=True,capture_output=True,check=True)
    ok_lines=[line for line in remote.stdout.splitlines() if line.endswith(": OK")]
    if len(ok_lines)!=len(indexed):
        raise RuntimeError(f"Node164 SHA check count {len(ok_lines)} != {len(indexed)}")
    checksum=subprocess.run(["rsync","-rcn","--itemize-changes",str(RAW)+"/",f"{HOST}:{REMOTE}/raw/"],
                            text=True,capture_output=True,check=True)
    if checksum.stdout.strip():
        raise RuntimeError(f"Node164 checksum dry-run not empty: {checksum.stdout}")
    with (PACK/"RAW_DATA_INDEX.tsv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(indexed[0]),delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(indexed)
    publication={"status":"PASS","node164_root":str(REMOTE),"storage_gateway":HOST,
                 "node174_role":"storage gateway and SHA verification only; no compute",
                 "raw_file_count":len(indexed),"raw_total_bytes":sum(x["bytes"] for x in indexed),
                 "raw_manifest_sha256":sha(manifest),"remote_sha256sum_pass_count":len(ok_lines),
                 "rsync_checksum_dry_run_empty":True}
    (PACK/"PUBLICATION_VERIFICATION.json").write_text(json.dumps(publication,indent=2,sort_keys=True)+"\n")
    result["node164_publication"]=publication
    (PACK/"RUN_RECEIPTS.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    pack_files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    code_files=sorted(p for p in (WT/"util/vm_tlb/awma/r22f_family").iterdir() if p.is_file() and p.suffix==".py")
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(path)}  {path.relative_to(WT)}\n" for path in pack_files+code_files))
    print(json.dumps({"status":"PUBLISHED_AND_SHA_CLOSED","raw_files":len(indexed),
                      "remote":str(REMOTE),"manifest_sha256":sha(manifest)},sort_keys=True))


if __name__=="__main__": main()
