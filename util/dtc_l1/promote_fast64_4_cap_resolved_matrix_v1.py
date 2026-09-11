#!/usr/bin/env python3
"""Build an explicit accepted FAST64.4 matrix from cap-resolved evidence.

This future-only bridge does not collect, rerun, or change simulator evidence.
It verifies the immutable cap-resolved package again and writes the narrow
schema consumed by FAST64.5/6, so an earlier candidate label cannot be
silently treated as acceptance.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = ("BASE", "IO", "OO")
OUT = ("workload", "mode", "evidence_path", "acceptance_status", "core_sha", "runtime_binary_sha256", "observer_overlay_sha256", "framework_sha", "payload_sha256")

def fail(s: str) -> None: raise RuntimeError(s)
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def tsv(p: Path) -> list[dict[str,str]]:
    with p.open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f, delimiter="\t"))

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    compat = a.output.parent / "fast64_4_primary_matrix.tsv"
    if a.output.exists() or compat.exists(): fail("OUTPUT_OR_COMPAT_ALREADY_EXISTS")
    primary = tsv(a.package / "fast64_4_primary_matrix.tsv")
    identity = tsv(a.package / "fast64_4_identity_manifest.tsv")
    caps = tsv(a.package / "fast64_4_cap_identity_manifest.tsv")
    status = {r["item"]: r["value"] for r in tsv(a.package / "fast64_4_collector_status.tsv")}
    expected = {(w,m) for w in ROSTER for m in MODES}
    by_id = {(r["workload"], r["mode"]): r for r in identity}
    by_cap = {(r["workload"], r["mode"]): r for r in caps}
    if len(primary) != 36 or {(r["workload"],r["mode"]) for r in primary} != expected: fail("PRIMARY_EXACT_36_REQUIRED")
    if len(by_id) != 36 or len(by_cap) != 36 or set(by_id) != expected or set(by_cap) != expected: fail("IDENTITY_OR_CAP_EXACT_36_REQUIRED")
    if status.get("formal_common_cap") != "32768": fail("FINAL_COMMON_CAP_REQUIRED")
    rows, compat_rows = [], []
    for r in primary:
        key = (r["workload"], r["mode"]); i, c = by_id[key], by_cap[key]
        if c["formal_cap"] != "32768" or c["cap_identity_class"] not in {"REACQUIRED_AT_FINAL_CAP", "SOURCE_PROVEN_CAP_INERT_REUSE_TO_FINAL"}: fail("CAP_IDENTITY_UNDECLARED="+"/".join(key))
        evidence = ROOT / r["evidence_path"]
        if not evidence.is_file() or sha(evidence) != i["evidence_sha256"]: fail("EVIDENCE_HASH_MISMATCH="+"/".join(key))
        d = json.loads(evidence.read_text(encoding="utf-8")); p, m = d.get("provenance",{}), d.get("metrics",{})
        if d.get("schema") != "dtc_l1_summary_v1" or m.get("DTC_L1_lower_cap_full_events") != 0: fail("STRICT_CAP_EVIDENCE_REQUIRED="+"/".join(key))
        if p.get("workload_id","").casefold() != r["workload"].casefold() or p.get("config_sha256") != c["expected_config_sha256"]: fail("PROVENANCE_MISMATCH="+"/".join(key))
        prefix = "docs/dtc_l1/fast64/generated/"
        if not r["evidence_path"].startswith(prefix): fail("EVIDENCE_PATH_PREFIX_INVALID="+"/".join(key))
        normalized = r["evidence_path"][len(prefix):]
        rows.append((r["workload"], r["mode"], normalized, "STRICT_TERMINAL_ACCEPTED", p["core_sha"], p["runtime_binary_sha256"], p["observer_overlay_sha256"], p["framework_sha"], d["external_artifacts"]["trace_list_sha256"]))
        compat_rows.append((r["workload"], r["mode"], normalized))
    for w in ROSTER:
        triplet = [x for x in rows if x[0] == w]
        if len(triplet) != 3 or len({(x[4],x[5],x[6],x[7],x[8]) for x in triplet}) != 1: fail("TRIPLET_IDENTITY_MISMATCH="+w)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    def write_once(path: Path, headings: tuple[str,...], values: list[tuple[str,...]]) -> None:
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent, text=True)
        with os.fdopen(fd,"w",encoding="utf-8",newline="") as f:
            w=csv.writer(f,delimiter="\t",lineterminator="\n"); w.writerow(headings); w.writerows(values)
        os.chmod(name,0o444); os.replace(name,path)
    write_once(compat, ("workload", "mode", "evidence_path"), compat_rows)
    write_once(a.output, OUT, rows)
    print(f"FAST64_4_CAP_RESOLVED_ACCEPTANCE_BRIDGE_V1_PASS output={a.output}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
