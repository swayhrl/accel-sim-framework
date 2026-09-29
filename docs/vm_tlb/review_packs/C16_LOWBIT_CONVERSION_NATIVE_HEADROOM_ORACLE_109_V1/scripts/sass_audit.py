#!/usr/bin/env python3
"""Static accepted/baseline/oracle SASS isolation audit."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

KEYS = ("LDG", "LDS", "STS", "STG", "HMMA", "HADD2", "HFMA2", "LOP3", "PRMT", "SHF", "BAR.SYNC")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(path):
    text = path.read_text()
    return {key: text.count(key) for key in KEYS} | {"lines": len(text.splitlines())}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accepted", type=Path, required=True)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--oracle", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--json", type=Path, required=True)
    p.add_argument("--tsv", type=Path, required=True)
    args = p.parse_args()
    c = {"accepted": counts(args.accepted), "baseline": counts(args.baseline), "oracle": counts(args.oracle)}
    accepted_equal = all(c["accepted"][k] == c["baseline"][k] for k in KEYS)
    structural = all(c["baseline"][k] == c["oracle"][k] for k in ("LDG", "LDS", "STS", "STG", "HMMA", "BAR.SYNC"))
    conversion_removed = c["baseline"]["HADD2"] > 0 and c["baseline"]["HFMA2"] > 0 and c["oracle"]["HADD2"] == 0 and c["oracle"]["HFMA2"] == 0
    source = args.source.read_text()
    dependency_source = all(x in source for x in ("B_loaded ^ zeros_loaded ^ B_loaded_scale.x", "DEPENDENCY_LSB_MASK", "gemm_forward_cuda_impl<true>"))
    passed = accepted_equal and structural and conversion_removed and dependency_source
    result = {"status": "ORACLE_ISOLATION_PASS" if passed else "ORACLE_NOT_ISOLATABLE",
              "accepted_baseline_key_counts_equal": accepted_equal,
              "compressed_load_shared_mma_output_structure_equal": structural,
              "conversion_half_ops_removed": conversion_removed,
              "compressed_source_dependency_present": dependency_source,
              "counts": c, "sha256": {"accepted": sha(args.accepted), "baseline": sha(args.baseline), "oracle": sha(args.oracle)}}
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with args.tsv.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(("condition", *KEYS, "lines", "sha256"))
        for name in ("accepted", "baseline", "oracle"):
            w.writerow((name, *(c[name][k] for k in KEYS), c[name]["lines"], result["sha256"][name]))
    if not passed:
        raise SystemExit(2)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
