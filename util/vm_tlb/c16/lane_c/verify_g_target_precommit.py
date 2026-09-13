#!/usr/bin/env python3
"""Pre-commit integrity gate for the fixed C16 G2/G3 target publication.

This intentionally does not import the selector implementation: the selector
source SHA was frozen before AWQ unseal.  It validates the staged worktree
payloads before the ready-named commit can be pushed; the selector's own
fixed-Git-tree verifier repeats the same checks after commit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c"
RAW_QWEN7 = "c16_qwen25_7b_raw_reference"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def die(message: str) -> None:
    raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(), delimiter="\t"))


def verify(out: Path) -> None:
    manifest_path = out / "PUBLISH_MANIFEST.json"
    if not manifest_path.is_file():
        die("missing PUBLISH_MANIFEST.json")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("status") != "C16_C_P_AWQ_FROZEN_TARGET_PLAN_READY_FOR_G" or manifest.get("native_catalog_consumed") is not True:
        die("manifest is not native AWQ target-ready")
    names: set[str] = set()
    for item in manifest.get("files", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or item["path"] in names:
            die("invalid or duplicate manifest file entry")
        names.add(item["path"])
        path = out / item["path"]
        if not path.is_file() or path.stat().st_size != item.get("size_bytes") or sha256_file(path) != item.get("sha256"):
            die(f"manifest payload missing or hash/size-mismatched: {item['path']}")
    required = {
        "G_TARGET_SELECTION_POLICY_V1.json", "P_TRAIN_SELECTOR_SOURCE_FREEZE.json",
        "P_TRAIN_TUNE_CATALOG_RECEIPT.json", "P_AWQ_CHEAP_CATALOG_RECEIPT.json",
        "P_AWQ_G_NCU_TARGET_PLAN.tsv", "P_AWQ_G_NVBIT_TARGET_PLAN.tsv",
    }
    if missing := sorted(required - names):
        die(f"missing final target payload(s): {','.join(missing)}")
    policy = json.loads((out / "G_TARGET_SELECTION_POLICY_V1.json").read_text())
    source = json.loads((out / "P_TRAIN_SELECTOR_SOURCE_FREEZE.json").read_text())
    selector_path = ROOT / "util/vm_tlb/c16/lane_c/c16_sampling_v2.py"
    if (policy.get("schema_version") != "G_TARGET_SELECTION_POLICY_V1"
            or policy.get("PRIMARY_G_TARGET_SELECTOR") != "SELECTOR_R"
            or policy.get("PRIMARY_G_TARGET_BUDGET") != "B48"
            or policy.get("SELECTOR_M_ROLE") != "AUXILIARY_REPRESENTATIVE_PLAN_NONBLOCKING"
            or policy.get("sole_operational_reason") != "COMPUTATIONAL_CRITICAL_PATH / PAID_GPU_IDLE_AVOIDANCE"
            or source.get("selector_code_sha256") != sha256_file(selector_path)
            or source.get("g_target_selection_policy_sha256") != sha256_file(out / "G_TARGET_SELECTION_POLICY_V1.json")):
        die("frozen selector/policy binding differs from required Selector-R B48 policy")
    awq = json.loads((out / "P_AWQ_CHEAP_CATALOG_RECEIPT.json").read_text())
    if not awq.get("validated_dependencies") or awq.get("awq_outcomes_read") is True:
        die("AWQ holdout receipt is absent, unvalidated, or records an outcome read")
    for modality in ("NCU", "NVBIT"):
        target_rows = rows(out / f"P_AWQ_G_{modality}_TARGET_PLAN.tsv")
        if not target_rows:
            die(f"empty {modality} target plan")
        if any(row.get("capture_modality") != modality or row.get("selector_kind") != "SELECTOR_R"
               or row.get("budget") != "48" or row.get("deployment_id") == RAW_QWEN7
               or row.get("target_status") == "PENDING_NATIVE_CATALOG" for row in target_rows):
            die(f"{modality} target violates the frozen R/B48/resource policy")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    verify(args.output_dir.resolve())
    print("PASS C16 staged fixed G2/G3 target publication")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL C16 staged fixed G2/G3 target publication: {exc}")
        raise
