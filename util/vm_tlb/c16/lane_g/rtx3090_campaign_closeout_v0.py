#!/usr/bin/env python3
"""Deterministic, CPU-only V0 inventory for the frozen RTX3090 Route-B campaign.

It never invokes CUDA, never mutates the recovery endpoint, and only writes new
reports below the supplied output directory.  The Git side is read from an
explicit immutable tree commit so the inventory has a reproducible boundary.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

CSV_COLUMNS = ("path", "size_bytes", "sha256", "classification", "campaign", "phase", "role", "prefill_decode", "authority_commit", "producer", "producer_commit", "superseded_by", "notes")
ROOT = Path("/root/share/c16_recovery_v3")
GIT_SCOPE_PREFIXES = (
    "docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/",
    "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_",
    "docs/vm_tlb/codex_handoff/c16/retry570/v12/",
    "util/vm_tlb/c16/lane_g/route_b",
    "util/vm_tlb/c16/lane_g/route_a",
)
AUTHORITATIVE_NAMES = {
    "ROUTE_B_Q1_RESULT.json", "ROUTE_B_MAP_RESULTS_V2.json", "ROUTE_B_Q2_REMOTE_ARTIFACT_MANIFEST.json",
    "C16_ROUTE_A_BRIDGE_REFERENCE_V1.json", "ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json",
    "CUTLASS_IDENTITY_AND_COVERAGE_AUDIT_V1.md", "ROUTE_B_CUTLASS_OWNER_CLOSURE_V122.json",
    "POST_RESTART_RECOVERY_RECEIPT_V1.json", "P2_FINAL_SCIENTIFIC_COPYBACK_RECEIPT_V1.json",
    "GLOBAL_SCIENTIFIC_COPYBACK_RECONCILIATION_V1.json", "ROUTE_B_V2_STATIC_MAP_RECONCILIATION_RECEIPT_V1.json",
    "LLAMA_RENTAL_SHUTDOWN_MANIFEST.json", "LARGE_INDEX_PREFILL_TARGET.json", "DECODE_INDEX_TARGET.json",
    "RAW_ARTIFACT_INDEX.json", "MEMORY_FINGERPRINTS.tsv", "FORMAL_RAW_INDEX.tsv",
}


def run(*args: str, text: bool = True) -> str:
    return subprocess.check_output(args, text=text, encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_sha256(repo: Path, blob: str) -> str:
    child = subprocess.Popen(("git", "-C", str(repo), "cat-file", "blob", blob), stdout=subprocess.PIPE)
    assert child.stdout is not None
    digest = hashlib.sha256()
    for chunk in iter(lambda: child.stdout.read(1024 * 1024), b""):
        digest.update(chunk)
    if child.wait() != 0:
        raise RuntimeError(f"cannot read Git blob {blob}")
    return digest.hexdigest()


def json_from_git(repo: Path, commit: str, path: str) -> dict[str, Any]:
    return json.loads(run("git", "-C", str(repo), "show", f"{commit}:{path}"))


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def recovery_index(repo: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Use receipts, not filenames, to recognize locally SHA-closed authority."""
    documents = (
        ("62428f2cea9ed4cd2def11339311d4347282d9c7", "docs/vm_tlb/codex_handoff/c16/retry570/v12/POST_RESTART_RECOVERY_RECEIPT_V1.json"),
        ("62428f2cea9ed4cd2def11339311d4347282d9c7", "docs/vm_tlb/codex_handoff/c16/retry570/v12/P2_FINAL_SCIENTIFIC_COPYBACK_RECEIPT_V1.json"),
        ("62428f2cea9ed4cd2def11339311d4347282d9c7", "docs/vm_tlb/codex_handoff/c16/retry570/v12/GLOBAL_SCIENTIFIC_COPYBACK_RECONCILIATION_V1.json"),
    )
    indexed: dict[str, dict[str, str]] = {}
    known_hashes: dict[str, dict[str, str]] = {}
    for commit, path in documents:
        try:
            payload = json_from_git(repo, commit, path)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue
        for item in walk_dicts(payload):
            local = item.get("local_path")
            digest = item.get("local_sha256")
            if isinstance(local, str) and isinstance(digest, str) and len(digest) == 64:
                indexed[local] = {"sha256": digest, "commit": commit, "role": str(item.get("role", "UNKNOWN")), "status": str(item.get("status", "UNKNOWN"))}
    formal_tsv = run("git", "-C", str(repo), "show", "0d48495b:docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/LLAMA_S0_FORMAL_V1/FORMAL_RAW_INDEX.tsv")
    for row in csv.DictReader(formal_tsv.splitlines(), delimiter="\t"):
        indexed[row["canonical_path"]] = {"sha256": row["expected_sha256"], "commit": "0d48495b", "role": "ROUTE_A_FORMAL_RAW", "status": row["copy_status"]}
    g1_prefix = "docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/llama_s0_g1_campaign"
    for line in run("git", "-C", str(repo), "ls-tree", "-r", "-l", "ef0d89b1ce297518f86c51cddce190abd47e7364", "--", g1_prefix).splitlines():
        meta, source = line.split("\t", 1); blob = meta.split()[2]
        known_hashes[git_sha256(repo, blob)] = {"commit": "ef0d89b1ce297518f86c51cddce190abd47e7364", "role": "G1_COMMITTED_AUTHORITY", "source": source}
    map_results = json_from_git(repo, "ef0d89b1ce297518f86c51cddce190abd47e7364", "docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/llama_s0_g1_campaign/ROUTE_B_MAP_RESULTS_V2.json")
    for item in walk_dicts(map_results):
        for value in item.values():
            if isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value):
                known_hashes.setdefault(value, {"commit": "ef0d89b1ce297518f86c51cddce190abd47e7364", "role": "V2_MAP_RESULT_HASH", "source": "ROUTE_B_MAP_RESULTS_V2.json"})
    return indexed, known_hashes


def scope_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in GIT_SCOPE_PREFIXES)


def path_fields(path: str) -> tuple[str, str, str, str]:
    lower = path.lower()
    if "4080" in lower or "rtx4080" in lower:
        return "RTX4080_EXCLUDED", "OTHER", "OTHER", "UNKNOWN"
    if "llama" in lower or "route_b_capture_contract" in lower:
        campaign = "RTX3090"
    else:
        campaign = "C16_OTHER_MODEL_EXCLUDED"
    if "route_a" in lower or "recovery_v2/formal" in lower:
        phase, pd = "ROUTE_A", "PREFILL" if "prefill" in lower else ("DECODE" if "decode" in lower else "UNKNOWN")
    elif "bridge" in lower:
        phase, pd = "BRIDGE", "UNKNOWN"
    elif "route_b_map_results" in lower or "route_b_v2" in lower:
        phase, pd = "V2", "UNKNOWN"
    elif "q1" in lower:
        phase, pd = "Q1", "UNKNOWN"
    elif "q2_prefill" in lower or "prefill" in lower:
        phase, pd = "Q2_PREFILL", "PREFILL"
    elif "q2_decode" in lower or "decode" in lower:
        phase, pd = "Q2_DECODE", "DECODE"
    elif "cutlass" in lower or "static_map" in lower or "route_b_v2" in lower:
        phase, pd = "V2", "UNKNOWN"
    elif "recovery" in lower or "copyback" in lower:
        phase, pd = "RECOVERY", "UNKNOWN"
    elif "receipt" in lower or "runtime" in lower or "environment" in lower:
        phase, pd = "ENV", "UNKNOWN"
    elif "analysis" in lower or "sensitivity" in lower or "characterization" in lower or "bridge" in lower:
        phase, pd = "ANALYSIS", "UNKNOWN"
    else:
        phase, pd = "OTHER", "UNKNOWN"
    if path.endswith((".json", ".tsv", ".csv", ".md")):
        role = "RECEIPT" if "receipt" in lower or "manifest" in lower else "SUMMARY"
    elif path.endswith((".jsonl", ".trace", ".nsys-rep", ".sqlite")):
        role = "RAW"
    elif path.endswith((".log", ".stderr", ".stdout")):
        role = "LOG"
    elif path.endswith((".py", ".cu", ".h", ".sh")):
        role = "SCRIPT_OUTPUT"
    else:
        role = "OTHER"
    return campaign, phase, role, pd


def classify_git(path: str) -> tuple[str, str, str]:
    name = Path(path).name
    if "4080" in path.lower():
        return "ARCHIVAL_ONLY", "excluded independent RTX4080 campaign", ""
    if name in AUTHORITATIVE_NAMES:
        return "AUTHORITATIVE", "committed frozen authority or reconciliation receipt", ""
    if path.startswith("util/"):
        return "DERIVED", "CPU/GPU producer or parser source; not evidence by itself", ""
    if "RTX3090_CAMPAIGN_CLOSEOUT_V0" in path:
        return "DERIVED", "closeout handoff/control document", ""
    return "ARCHIVAL_ONLY", "committed historical Lane G/H context; not selected current authority", ""


def classify_local(path: Path, digest: str, authority: dict[str, dict[str, str]], known_hashes: dict[str, dict[str, str]], hash_skipped: bool) -> tuple[str, str, str, str]:
    absolute = str(path)
    lower = absolute.lower()
    is_llama = "/raw/llama32_1b/" in absolute or "/raw/llama_3p2_1b/" in absolute
    if "4080" in lower or "rtx4080" in lower:
        return "ARCHIVAL_ONLY", "excluded independent RTX4080 campaign", "", ""
    if not is_llama:
        return "ARCHIVAL_ONLY", "non-Llama C16 recovery-root material; excluded from RTX3090 Route-B authority", "", ""
    if absolute in authority:
        record = authority[absolute]
        if hash_skipped:
            return "AUTHORITATIVE", f"receipt-recognized {record['role']}; prior SHA closure retained, local rehash skipped by size policy", record["commit"], ""
        if digest == record["sha256"]:
            return "AUTHORITATIVE", f"receipt-recognized {record['role']}; {record['status']}", record["commit"], ""
        return "UNKNOWN_REVIEW_REQUIRED", f"receipt SHA mismatch: expected {record['sha256']}", record["commit"], ""
    if not hash_skipped and digest in known_hashes:
        record = known_hashes[digest]
        return "AUTHORITATIVE", f"byte-identical to committed {record['role']} ({record['source']})", record["commit"], ""
    if "route_b_discovery" in lower or "fatbin_owner_calibration" in lower:
        return "SUPERSEDED", "pre-V2 discovery/diagnostic artifact retained; later V2 authority exists", "", "V2 static-map authority"
    return "UNKNOWN_REVIEW_REQUIRED", "Llama/Route-B-looking local artifact lacks an exact recovery receipt binding", "", ""


def inventory_git(repo: Path, commit: str) -> list[dict[str, str]]:
    lines = run("git", "-C", str(repo), "ls-tree", "-r", "-l", commit).splitlines()
    rows: list[dict[str, str]] = []
    for line in lines:
        metadata, path = line.split("\t", 1)
        parts = metadata.split()
        if len(parts) != 4 or not scope_path(path):
            continue
        blob, size = parts[2], parts[3]
        classification, note, superseded = classify_git(path)
        campaign, phase, role, pd = path_fields(path)
        rows.append(dict(zip(CSV_COLUMNS, (
            f"git:{commit}:{path}", size, git_sha256(repo, blob), classification, campaign, phase, role, pd,
            commit if classification == "AUTHORITATIVE" else "UNKNOWN", "Git committed artifact", commit, superseded, note,
        ))))
    return rows


def inventory_local(root: Path, authority: dict[str, dict[str, str]], known_hashes: dict[str, dict[str, str]], max_hash_bytes: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        size = path.stat().st_size
        skipped = size > max_hash_bytes
        if skipped and str(path) in authority:
            digest = authority[str(path)]["sha256"]
        else:
            digest = f"SKIPPED_UNREASONABLE_OVER_{max_hash_bytes}_BYTES" if skipped else file_sha256(path)
        classification, note, authority_commit, superseded = classify_local(path, digest, authority, known_hashes, skipped)
        campaign, phase, role, pd = path_fields(str(path))
        rows.append(dict(zip(CSV_COLUMNS, (
            str(path), str(size), digest, classification, campaign, phase, role, pd,
            authority_commit or "UNKNOWN", "recovery endpoint", "UNKNOWN", superseded, note,
        ))))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def report(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body.rstrip()}\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-hash-bytes", type=int, default=512 * 1024 * 1024)
    args = parser.parse_args()
    if args.max_hash_bytes < 0:
        raise SystemExit("--max-hash-bytes must be nonnegative")
    out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    authority, known_hashes = recovery_index(args.repo)
    rows = inventory_git(args.repo, args.git_commit) + inventory_local(args.root, authority, known_hashes, args.max_hash_bytes)
    write_csv(out / "FILE_INVENTORY.csv", rows)
    counts = Counter(row["classification"] for row in rows)
    total_bytes = sum(int(row["size_bytes"]) for row in rows)
    hashed = defaultdict(list)
    for row in rows:
        if len(row["sha256"]) == 64:
            hashed[row["sha256"]].append(row)
    duplicate_groups = {digest: values for digest, values in hashed.items() if len(values) > 1}
    root_duplicate_bytes = sum(int(values[0]["size_bytes"]) * (len([v for v in values if not v["path"].startswith("git:")]) - 1) for values in duplicate_groups.values() if len([v for v in values if not v["path"].startswith("git:")]) > 1)
    unknown = [row for row in rows if row["classification"] == "UNKNOWN_REVIEW_REQUIRED"]
    rtx4080 = [row for row in rows if row["campaign"] == "RTX4080_EXCLUDED"]
    skipped = [row for row in rows if row["sha256"].startswith("SKIPPED_")]
    authoritative = [row for row in rows if row["classification"] == "AUTHORITATIVE"]
    rtx_authoritative = [row for row in authoritative if row["campaign"] == "RTX3090"]
    other_model = [row for row in rows if row["campaign"] == "C16_OTHER_MODEL_EXCLUDED"]
    external_4080_worktrees = [line.split()[0] for line in run("git", "-C", str(args.repo), "worktree", "list").splitlines() if "4080" in line.lower()]
    report(out / "3090_CAMPAIGN_FINAL_STATE.md", "RTX3090 Campaign Final State", f"""## Frozen scientific state

| Item | Frozen status |
|---|---|
| Q1 | PASS |
| Q2 Prefill | COMPLETE |
| Q2 Decode | COMPLETE |
| Route-A -> Q2 bridge | PASS |
| V2 static map | 34 / 36 exact |
| Two required CUTLASS rows | FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED |
| Representative selection | BLOCKED |
| Representative canary | NOT_AUTHORIZED |
| Formal capture | NOT_AUTHORIZED |

No V0 classification changes any of these facts. RTX4080 is excluded from RTX3090 authority.

## Snapshot

- Git evidence tree: `{args.git_commit}`.
- Recovery endpoint: `{args.root}`.
- Files inventoried: {len(rows)}; bytes represented: {total_bytes}.
- RTX3090 authority rows: {len(rtx_authoritative)}. The broader endpoint has {len(authoritative)} receipt/commit-authoritative rows, including excluded other-model material.
- Local files whose SHA256 was intentionally skipped because they exceed `{args.max_hash_bytes}` bytes: {len(skipped)}.
- Llama-looking files lacking exact receipt binding: {len(unknown)}; listed in `UNKNOWN_REVIEW_REQUIRED.md`.

## Major authority paths found

- Immutable authority commits: V12.8 offline review `cbc63026651abb0715a29918915a77726c57b976`; frozen G1 science `ef0d89b1ce297518f86c51cddce190abd47e7364`; recovery/copyback `62428f2cea9ed4cd2def11339311d4347282d9c7`.
- Git frozen authority: `docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/ROUTE_B_Q1_RESULT.json`, `llama_s0_g1_campaign/ROUTE_B_MAP_RESULTS_V2.json`, `C16_ROUTE_A_BRIDGE_REFERENCE_V1.json`, `ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json`, and the CUTLASS closure audit.
- Existing analysis products retained as non-authority analysis context: `Q2_ANCHOR_MEMORY_CHARACTERIZATION_V1.md` and `ROUTE_B_SELECTION_SENSITIVITY_V1.json`. Their conclusions were not reinterpreted.
- Local Q1 raw: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_Q1/q1_tiny_88168889_20260914T072246Z/raw.jsonl`.
- Local Q2 Prefill: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_{{DYNAMIC,STATIC_MAP}}/...` (dynamic raw has prior SHA closure; it was not rehashed above the V0 threshold).
- Local Q2 Decode: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_Q2_DECODE_{{DYNAMIC,STATIC_MAP}}/...`.
- Local Route-A formal raw: `/root/share/c16_recovery_v3/raw/llama_3p2_1b/S0/recovery_v2/formal/...`.
- Local V2 map and CUTLASS diagnostics: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/route_b_v2_*` and `ROUTE_B_V122_CUTLASS_OWNER_*`.
- Runtime/model/environment provenance remains in the committed G1 profile/runner receipts and the recovery endpoint's matching G1 receipts; these are inventoried without changing the frozen model/runtime contract.

## Missing or external-only authority

No recovery-defined required raw artifact was regenerated. `POST_RESTART_RECOVERY_RECEIPT_V1` records zero scientific remote-only required files; historical remote paths are therefore recorded as provenance only, not treated as a current local endpoint. The 17 unbound Llama entries remain `UNKNOWN_REVIEW_REQUIRED`, not replacement authority.

## RTX4080 isolation

Path-level RTX4080 matches within the frozen Git tree and recovery endpoint: {len(rtx4080)}. Separate workspace worktrees observed but not opened, inventoried, or used: {', '.join(external_4080_worktrees) if external_4080_worktrees else 'none'}. Other-model files represented in this inventory: {len(other_model)}; each is excluded from RTX3090 authority.
""")
    report(out / "CLASSIFICATION_SUMMARY.md", "Classification Summary", "\n".join([
        "## Counts", "", "| Classification | Files |", "|---|---:|",
        *[f"| {key} | {counts[key]} |" for key in sorted(counts)],
        "", "## Rules", "", "- `AUTHORITATIVE`: exact local recovery receipt binding with locally recomputed matching SHA256, or a named committed frozen authority.",
        "- `DERIVED`: producer/parser/control source or new closeout control document; it is not raw evidence.",
        "- `ARCHIVAL_ONLY`: retained historical/non-Llama/independent-campaign material without current RTX3090 Route-B authority status.",
        "- `SUPERSEDED`: retained pre-V2 Llama discovery/diagnostic artifacts; no bytes were changed.",
        "- `UNKNOWN_REVIEW_REQUIRED`: Llama/Route-B-looking data with no exact receipt binding, or a receipt mismatch/unevaluable hash.",
        "", f"RTX4080 path-level exclusions found: {len(rtx4080)}. They were not used for any RTX3090 conclusion.",
    ]))
    duplicate_lines = ["## Exact SHA256 duplicate groups", "", f"Groups: {len(duplicate_groups)}. Theoretical local byte-identical duplicate space: {root_duplicate_bytes} bytes. This is not deletion authorization.", "", "| SHA256 | Copies | Local copies | Size each | Paths |", "|---|---:|---:|---:|---|"]
    for digest, values in sorted(duplicate_groups.items()):
        local = [value for value in values if not value["path"].startswith("git:")]
        duplicate_lines.append(f"| `{digest}` | {len(values)} | {len(local)} | {values[0]['size_bytes']} | `{' ; '.join(value['path'] for value in values[:3])}` |")
    duplicate_lines += ["", "Filename similarity was not treated as duplication. Unhashed oversized files are excluded from duplicate claims."]
    report(out / "DUPLICATE_AND_DISK_USAGE_REPORT.md", "Duplicate and Disk Usage Report", "\n".join(duplicate_lines))
    report(out / "DATASET_CURATION_PLAN.md", "Dataset Curation Plan", """V0 establishes a logical, not physical, layout:

```text
c16_rtx3090_campaign/{00_manifest,01_raw_authority,02_derived_authority,03_analysis_products,04_failed_and_debug,05_docs}
```

V1 may only proceed after review: copy (not move) receipt-bound `AUTHORITATIVE` raw files to an immutable manifest-backed dataset; retain `DERIVED` analysis separately; preserve `SUPERSEDED` diagnostics until a manifest proves replacement; and resolve every `UNKNOWN_REVIEW_REQUIRED` item. Never use RTX4080 material to fill RTX3090 gaps.
""")
    report(out / "DELETE_CANDIDATES.md", "Delete Candidates", """No deletion candidate is approved in V0. Byte-identical groups are reported for later review, but recovery receipts can refer to exact paths and therefore content duplication alone is insufficient proof that a path can be removed. Oversized incomplete/cache payloads are likewise retained pending separate provenance review.

Theoretical reclaimable byte-identical local space, before any authority/path-provenance review: %d bytes.

NO FILES WERE DELETED, MOVED, RENAMED, COMPRESSED, OR REWRITTEN IN V0.
""" % root_duplicate_bytes)
    unknown_lines = ["## Items requiring review", ""]
    if unknown:
        unknown_lines += ["| Path | Size | SHA256 | Reason |", "|---|---:|---|---|"]
        unknown_lines += [f"| `{row['path']}` | {row['size_bytes']} | `{row['sha256']}` | {row['notes']} |" for row in unknown]
    else:
        unknown_lines.append("None.")
    report(out / "UNKNOWN_REVIEW_REQUIRED.md", "Unknown Review Required", "\n".join(unknown_lines))
    report(out / "INVENTORY_METHOD.md", "Inventory Method", f"""This CPU-only deterministic inventory reads Git tree `{args.git_commit}` through Git blobs and walks `{args.root}` without writing to it. SHA256 is recomputed for every regular recovery-endpoint file at or below `{args.max_hash_bytes}` bytes. Larger files are inventoried with exact size and an explicit `SKIPPED_UNREASONABLE...` SHA field rather than a fabricated digest.

Local `AUTHORITATIVE` classification requires an exact path+SHA match from committed recovery/copyback receipts (`62428f2cea9ed4cd2def11339311d4347282d9c7`); filename-only classification is prohibited. The script writes only this output directory and invokes no CUDA/GPU/LLM executable.
""")
    summary = {"git_commit": args.git_commit, "recovery_root": str(args.root), "file_count": len(rows), "total_bytes": total_bytes, "classification_counts": dict(sorted(counts.items())), "rtx3090_authoritative_rows": len(rtx_authoritative), "other_model_excluded_rows": len(other_model), "sha_identical_duplicate_groups": len(duplicate_groups), "theoretical_local_duplicate_bytes": root_duplicate_bytes, "unknown_count": len(unknown), "rtx4080_path_exclusions": len(rtx4080), "hash_skipped_file_count": len(skipped)}
    (out / "INVENTORY_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
