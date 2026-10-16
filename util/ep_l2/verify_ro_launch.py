#!/usr/bin/env python3
"""Hash-bound oracle launch input; does not qualify or launch a simulator."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import ro_oracle


def verify(directory, repository):
    m = ro_oracle.verify(directory)
    producer = m["framework_source_commit"]
    if len(producer) != 40 or any(c not in "0123456789abcdef" for c in producer):
        raise ValueError("oracle producer is not an exact source commit")
    source = subprocess.check_output(["git", "-C", str(repository), "show",
                                      producer+":util/ep_l2/ro_oracle.py"])
    # Current full-commandlist certificates are activated after initialization.
    # A host write between listed kernels invalidates that immutable epoch.
    kernel_seen = False
    initialization_bytes = 0
    for s in Path(m["commandlist"]).read_text().splitlines():
        s = s.strip()
        if s.startswith("kernel"):
            kernel_seen = True
        elif s.startswith("MemcpyHtoD,"):
            if kernel_seen:
                raise ValueError("host write inside full-commandlist epoch; use ordinary path")
            _, address, count = s.split(",")
            if int(address,16) < 0 or int(count) < 0 or int(address,16)+int(count)>1<<64:
                raise ValueError("invalid initialization range")
            initialization_bytes += int(count)
    return dict(schema_version="EP_L2_RO_INPUT_BINDING_V1",
                status="ORACLE_INPUT_VERIFIED_NOT_RUNTIME_QUALIFICATION",
                oracle_manifest_sha256=ro_oracle.sha256(Path(directory)/"manifest.json"),
                oracle_producer_commit=producer,
                oracle_script_sha256=hashlib.sha256(source).hexdigest(),
                trace_content_sha256=hashlib.sha256(json.dumps(
                    {"commandlist":m["commandlist_sha256"],"kernels":[k["sha256"] for k in m["kernels"]]},
                    sort_keys=True,separators=(",",":")).encode()).hexdigest(),
                epoch=m["epoch"], address_domain=m["address_domain"],
                scope=m["scope"],assumptions=m["assumptions"],
                epoch_activation="after_initialization_and_prior_writeback_drain",
                initialization_bytes=initialization_bytes,
                certified_ranges=str(Path(directory).resolve()/"certified_ranges.csv"),
                certified_ranges_sha256=m["artifacts"]["certified_ranges.csv"],
                eligible_unique_lines=m["counts"].get("CERTIFIED_RO_lines",0),
                eligible_read_lane_references=m["counts"].get("CERTIFIED_RO_read_lane_references",0))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--oracle",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--accept-closed-trace-model-scope",action="store_true",required=True)
    args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    source=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if subprocess.check_output(["git","-C",str(root),"show",source+":util/ep_l2/verify_ro_launch.py"])!=Path(__file__).read_bytes():
        raise ValueError("unfrozen verifier")
    result=verify(args.oracle,root);result['verifier_source_commit']=source
    with args.output.open("x") as f:json.dump(result,f,indent=2);f.write("\n")
    print(json.dumps({"status":result['status'],"eligible_unique_lines":result['eligible_unique_lines']}))


if __name__=="__main__":main()
