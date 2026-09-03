#!/usr/bin/env python3
"""Read-only streaming trace-address coverage against an M4A sidecar."""
import argparse, json, lzma, re
from pathlib import Path

REC = re.compile(r"\s(\d+)\s+[01]\s+(0x[0-9a-fA-F]+)(?:\s|$)")

def main():
    p = argparse.ArgumentParser(); p.add_argument("--run", type=Path, required=True); p.add_argument("--output", type=Path, required=True); a=p.parse_args()
    side = json.loads((a.run / "allocation-sidecar.json").read_text())
    ranges = [(int(x["simva_start"], 16), int(x["simva_start"], 16) + int(x["size_bytes"]), x["object_kind"]) for x in side["allocations"] + side["kv_cache_events"]]
    out = {"schema_version":"m4a-streaming-address-coverage-v1", "references":0, "bytes":0, "by_object":{"WEIGHT":{"references":0,"bytes":0},"KV_CACHE":{"references":0,"bytes":0},"UNKNOWN":{"references":0,"bytes":0}}}
    for f in sorted((a.run / "traces").glob("*.traceg.xz")):
        with lzma.open(f, "rt", errors="replace") as h:
            for line in h:
                m = REC.search(line)
                if not m: continue
                width, addr = int(m.group(1)), int(m.group(2),16); kind = next((k for lo,hi,k in ranges if lo <= addr < hi), "UNKNOWN")
                out["references"] += 1; out["bytes"] += width; out["by_object"][kind]["references"] += 1; out["by_object"][kind]["bytes"] += width
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
if __name__ == "__main__": main()
