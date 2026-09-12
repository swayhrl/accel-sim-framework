#!/usr/bin/env python3
"""Build and validate the small, offline-safe C16 Lane G GPU package."""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, PLANNING_SHA, atomic_json, repo_root, sha256_file
from run_schema import schema_markdown


ROOT = repo_root()
DEFAULT_OUT = ROOT / "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g"
DEFAULT_HANDOFF = ROOT / "docs/vm_tlb/codex_handoff/c16/lane_g/LATEST_REPORT.md"
SOURCE_ROOT = ROOT / "util/vm_tlb/c16/lane_g"
SOURCE_FILES = (
    "__init__.py", "bootstrap_autodl.sh", "requirements.lock", "WHEELHOUSE_MANIFEST.tsv",
    "c16_native_common.py", "wheelhouse_verify.py", "model_adapters.py", "run_schema.py",
    "run_model.py", "scenario_driver.py", "identity_guard.py", "profiler_wrapper.py", "nsys_wrapper.py",
    "ncu_wrapper.py", "nvbit_wrapper.py", "prepare_gpu_package.py", "offline_dry_run.py",
    "autodl_instance_receipt.py", "transfer_verify.py",
    "native_catalog.py",
    "consume_upstreams.py",
    "execution_budget.py",
)
EXPECTED_COLUMNS = ("artifact_id", "kind", "path_or_commit", "sha256", "required_for", "closure_status", "note")
PACKAGE_COLUMNS = ("package_component", "path_or_ref", "sha256", "required_for", "availability", "transfer_action", "scientific_use")
ENV_COLUMNS = ("component", "version_or_constraint", "source", "wheel_sha256", "closure_status", "purpose")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def write_tsv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def source_rows() -> list[dict[str, str]]:
    rows = []
    for name in SOURCE_FILES:
        path = SOURCE_ROOT / name
        if not path.is_file():
            raise ContractError(f"declared package source missing: {path}")
        rows.append({
            "artifact_id": f"G_SOURCE_{name}", "kind": "LANE_G_SOURCE", "path_or_commit": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path), "required_for": "C16-0.3/C16-0.4", "closure_status": "LOCAL_HASH_CLOSED",
            "note": "small committed source; no model/profiler raw data",
        })
    return rows


def upstream_rows() -> list[dict[str, str]]:
    return [
        {"artifact_id": "A_MODEL_ASSET_MANIFEST", "kind": "UPSTREAM_A_MANIFEST", "path_or_commit": "hrl/vm-c16-a-static-coord-v0:MODEL_ASSET_MANIFEST.tsv", "sha256": "NA", "required_for": "C16-1.2+", "closure_status": "UPSTREAM_A_COMMITTED_MANIFEST_REQUIRED", "note": "do not invent model-weight hashes"},
        {"artifact_id": "A_INPUT_AND_TOKEN_RECEIPTS", "kind": "UPSTREAM_A_MANIFEST", "path_or_commit": "hrl/vm-c16-a-static-coord-v0:INPUT_CORPUS.tsv;TOKEN_RECEIPTS/", "sha256": "NA", "required_for": "C16-1.3+", "closure_status": "UPSTREAM_A_COMMITTED_MANIFEST_REQUIRED", "note": "actual per-deployment token IDs required"},
        {"artifact_id": "A_SCENARIO_MATRIX", "kind": "UPSTREAM_A_MANIFEST", "path_or_commit": "hrl/vm-c16-a-static-coord-v0:SCENARIO_MATRIX.tsv", "sha256": "NA", "required_for": "C16-1.3+", "closure_status": "UPSTREAM_A_COMMITTED_MANIFEST_REQUIRED", "note": "S0-S4 must be frozen before GPU run"},
        {"artifact_id": "A_C16_GPU_PACKAGE", "kind": "UPSTREAM_A_MANIFEST", "path_or_commit": "hrl/vm-c16-a-static-coord-v0:C16_GPU_PACKAGE_MANIFEST.tsv", "sha256": "NA", "required_for": "C16-0.9/C16-1.2", "closure_status": "UPSTREAM_A_COMMITTED_MANIFEST_REQUIRED", "note": "A owns asset/input/package closure"},
    ]


def env_rows() -> list[dict[str, str]]:
    return [
        {"component": "CPython", "version_or_constraint": "3.10.x", "source": "AutoDL base image or local wheelhouse", "wheel_sha256": "NA", "closure_status": "RUNTIME_VERIFY_REQUIRED", "purpose": "C16 native runner"},
        {"component": "PyTorch", "version_or_constraint": "2.5.1+cu124", "source": "hash-closed C16 wheelhouse", "wheel_sha256": "RECORDED_IN_WHEELHOUSE_MANIFEST_AT_C16-1.2", "closure_status": "LOGICALLY_LOCKED_IMPORT_PENDING", "purpose": "native CUDA inference"},
        {"component": "transformers", "version_or_constraint": "4.46.3", "source": "hash-closed C16 wheelhouse", "wheel_sha256": "RECORDED_IN_WHEELHOUSE_MANIFEST_AT_C16-1.2", "closure_status": "LOGICALLY_LOCKED_IMPORT_PENDING", "purpose": "HF causal-LM adapter"},
        {"component": "accelerate", "version_or_constraint": "1.1.1", "source": "hash-closed C16 wheelhouse", "wheel_sha256": "RECORDED_IN_WHEELHOUSE_MANIFEST_AT_C16-1.2", "closure_status": "LOGICALLY_LOCKED_IMPORT_PENDING", "purpose": "runtime dependency"},
        {"component": "safetensors", "version_or_constraint": "0.4.5", "source": "hash-closed C16 wheelhouse", "wheel_sha256": "RECORDED_IN_WHEELHOUSE_MANIFEST_AT_C16-1.2", "closure_status": "LOGICALLY_LOCKED_IMPORT_PENDING", "purpose": "local weight format"},
        {"component": "AutoAWQ", "version_or_constraint": "0.2.8", "source": "hash-closed C16 wheelhouse", "wheel_sha256": "RECORDED_IN_WHEELHOUSE_MANIFEST_AT_C16-1.2", "closure_status": "LOGICALLY_LOCKED_IMPORT_PENDING", "purpose": "Qwen2.5-7B AWQ adapter only"},
    ]


def tool_compatibility_markdown() -> str:
    return """# C16 Lane G tool compatibility expectations

This is an offline expectation matrix, not a claim that the current local host or an AutoDL instance has these capabilities. C16-1.1 records the actual GPU/driver/CUDA values before a scientific run.

| Tool | Required C16 behavior | Offline state | Runtime gate |
| --- | --- | --- | --- |
| `nsys` | CUDA/NVTX lightweight census; capture-range bounded to NVTX | wrapper dry-run passed | G1 checks launch/stream/name/correlation/NVTX linkage and measures overhead |
| `ncu` | query and freeze a compact available metric list; one target only | wrapper dry-run passed | G2 records `COUNTER_UNAVAILABLE` rather than substituting a similar counter |
| NVBit launcher/tool | target-in/out filter, terminal trace, identity closure, 4 GiB/20 min guard | wrapper dry-run passed | G3 tiny CUDA fixture then one revalidated model target |
| PyTorch/HF/AutoAWQ | local-files-only model import with exact dtype/quantization | logical lock only | G0 rejects CPU/dtype/backend fallback |
| execution-budget ledger | shared 24 GPU-instance-hour wall-time / 64 GiB raw accounting, serialized capture lease | ledger unit test passed | C16-1.1 initializes it; every real runner/profiler command requires it |

No wrapper uses `ncu --set full`; no wrapper requests full SASS; no wrapper invokes Accel-Sim or GPGPU-Sim.
"""


def transfer_plan_markdown() -> str:
    return """# C16 Lane G transfer plan

1. A publishes a fixed-commit C16 GPU package manifest with Wave-1 asset/input/scenario hashes.
2. G copies only that fixed package and this G source bundle with `rsync -avP --partial` to the recorded AutoDL work root.
3. G runs `bootstrap_autodl.sh --install --wheelhouse ...`; the script refuses an empty or hash-mismatched wheelhouse manifest.
4. G records an instance receipt, then compares every used asset/input/wheel SHA256 to `EXPECTED_HASHES.tsv` before G0.
5. C16-1.1 records an observed provider/AutoDL instance-start timestamp and initializes one shared execution-budget ledger in the AutoDL work root. Every real runner/profiler command receives that ledger; NVBit obtains an exclusive bounded lease before launch.
6. Profiler databases and raw NVBit output remain outside Git. Each bounded capture is returned through an exchange path and represented by path/host/size/SHA256/run/target/terminal status in `RAW_INDEX.tsv`.

This package is deliberately incomplete until A's committed asset/input/scenario package is available. It is not permission to download models on rented GPU or to begin G0.
"""


def gap_markdown() -> str:
    return """# C16 Lane G offline-package gap receipt

G's code, logical dependency lock, receipt schema, target second-pass guard, and no-GPU dry-runs are locally hash-closed. A's fixed integration release supplies hash-verified metadata, frozen input/token receipts, and scenarios, and H's dedicated manifest now supplies a hash-verified offline admission/object-map protocol. C16-0.9 still cannot be marked fully complete because A has not published its required GPU package and wheel closure. The final transferred asset/wheel hashes are intentionally `NA` rather than fabricated.

Consequences: do not open an AutoDL scientific run, transfer models, or start G0 until C16-1.2 verifies a published A GPU package and wheelhouse closure. This is a dependency gap, not a GPU or model capability result.
"""


def readme() -> str:
    return """# C16 Lane G offline GPU package

Start with `LATEST_REPORT.md`, then `STAGE_STATUS.tsv`, `C16_GPU_PACKAGE_MANIFEST.tsv`, `EXPECTED_HASHES.tsv`, `RUN_SCHEMA.md`, and `EXECUTION_BUDGET_GUARD.md`. This review pack contains only offline preparation and non-scientific dry-run evidence. It contains no native baseline, profiler result, raw trace, or simulator output.
"""


def handoff_text() -> str:
    return """# C16 Lane G handoff

Status: `C16_G_OFFLINE_PACKAGE_PARTIAL_READY_FOR_UPSTREAM_CLOSURE`.

C16-0.3/0.4 offline infrastructure is ready: idempotent offline bootstrap, logical env lock, unified native runner, explicit Wave-1 adapters, nsys/NCU/NVBit wrappers, receipt schema, target second-pass identity guard, shared execution-budget ledger guard, and no-GPU dry-run validation. All mock outputs are marked non-scientific and cannot enter a native catalog.

C16-0.9 is prepared but cannot close: A's fixed integration receipt hash-verifies model/input/scenario metadata, H's dedicated offline manifest is consumed as a non-dynamic protocol, and A's required GPU package and wheel closure remain unpublished. No AutoDL SSH/GPU was used, no models were downloaded, and no simulator run was started. Once A publishes a fixed hash-bound package and the user provides AutoDL SSH, proceed with C16-1 inline G0/G1/G2/G3 qualification; G0/G1 success immediately releases its corresponding work while G2/G3 remain nonblocking.

Execution safety closure: C16-1.1 must initialize the shared execution-budget ledger from an observed provider/AutoDL instance-start timestamp and its receipt path. Every real native runner, nsys, NCU, and NVBit command then requires that initialized ledger; it enforces the 24 GPU-instance-hour wall-clock envelope and separately records GPU-active operation time. NVBit additionally receives the remaining/per-window raw and time guard. Dry-runs need no ledger and remain non-scientific.
"""


def offline_rows(status: str) -> list[dict[str, str]]:
    return [
        {"check_id": "G-DRY-BOOTSTRAP", "command_or_fixture": "bootstrap_autodl.sh --dry-run", "status": status, "scientific_eligible": "FALSE", "scope": "no GPU query/download/install"},
        {"check_id": "G-DRY-RUNNER", "command_or_fixture": "run_model.py --mock", "status": status, "scientific_eligible": "FALSE", "scope": "receipt schema only"},
        {"check_id": "G-DRY-PROFILERS", "command_or_fixture": "nsys/ncu/nvbit wrappers --dry-run", "status": status, "scientific_eligible": "FALSE", "scope": "command/guard schemas only"},
        {"check_id": "G-DRY-IDENTITY", "command_or_fixture": "identity_guard fixture", "status": status, "scientific_eligible": "FALSE", "scope": "second-pass identity closure"},
    ]


def refresh_manifest(out: Path) -> None:
    files = []
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name != "PUBLISH_MANIFEST.json":
            files.append({"path": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    manifest = {
        "schema_version": "C16_G_OFFLINE_PACKAGE_V1",
        "planning_sha": PLANNING_SHA,
        "producer_source_sha": git_head(),
        "lane": "G",
        "status": "C16_G_OFFLINE_PACKAGE_PARTIAL_READY_FOR_UPSTREAM_CLOSURE",
        "capture_state": "NO_AUTODL_SSH_NO_NATIVE_RUN",
        "scientific_evidence": "NONE_OFFLINE_INFRASTRUCTURE_ONLY",
        "blocked_on": "UPSTREAM_A_GPU_PACKAGE_AND_WHEEL_CLOSURE_REQUIRED",
        "files": files,
    }
    atomic_json(out / "PUBLISH_MANIFEST.json", manifest)


def record_offline_dry_run(out: Path) -> None:
    write_tsv(out / "OFFLINE_DRY_RUN.tsv", ("check_id", "command_or_fixture", "status", "scientific_eligible", "scope"), offline_rows("PASS"))
    refresh_manifest(out)


def prepare(out: Path, handoff: Path | None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    expected = source_rows() + upstream_rows()
    write_tsv(out / "EXPECTED_HASHES.tsv", EXPECTED_COLUMNS, expected)
    package_rows = [
        {"package_component": row["artifact_id"], "path_or_ref": row["path_or_commit"], "sha256": row["sha256"], "required_for": row["required_for"], "availability": row["closure_status"], "transfer_action": "COMMIT_OR_RSYNC_AS_NAMED", "scientific_use": "OFFLINE_INFRASTRUCTURE"}
        for row in expected
    ]
    write_tsv(out / "C16_GPU_PACKAGE_MANIFEST.tsv", PACKAGE_COLUMNS, package_rows)
    write_tsv(out / "ENV_LOCK.tsv", ENV_COLUMNS, env_rows())
    atomic_text(out / "TOOL_COMPATIBILITY.md", tool_compatibility_markdown())
    atomic_text(out / "RUN_SCHEMA.md", schema_markdown())
    from native_catalog import schema_markdown as catalog_schema_markdown
    atomic_text(out / "NATIVE_CATALOG_SCHEMA.md", catalog_schema_markdown())
    from execution_budget import ledger_markdown
    atomic_text(out / "EXECUTION_BUDGET_GUARD.md", ledger_markdown())
    atomic_text(out / "TRANSFER_PLAN.md", transfer_plan_markdown())
    atomic_text(out / "C16_G_GAP_RECEIPT.md", gap_markdown())
    atomic_text(out / "README.md", readme())
    write_tsv(out / "OFFLINE_DRY_RUN.tsv", ("check_id", "command_or_fixture", "status", "scientific_eligible", "scope"), offline_rows("PENDING_EXECUTION_BY_OFFLINE_DRY_RUN"))
    write_tsv(out / "STAGE_STATUS.tsv", ("stage_id", "owner", "execution_status", "scientific_status", "evidence_tier", "blocking_dependency", "note"), [
        {"stage_id": "C16-0.3", "owner": "G", "execution_status": "OFFLINE_READY", "scientific_status": "NOT_APPLICABLE", "evidence_tier": "UNRESOLVED", "blocking_dependency": "NA", "note": "bootstrap/logical lock/tool expectations are ready; wheel hashes close at C16-1.2"},
        {"stage_id": "C16-0.4", "owner": "G", "execution_status": "OFFLINE_READY", "scientific_status": "NOT_APPLICABLE", "evidence_tier": "UNRESOLVED", "blocking_dependency": "NA", "note": "runner/wrappers/schema/budget guard/mock fixtures are ready; no GPU result exists"},
        {"stage_id": "C16-0.9", "owner": "A,G", "execution_status": "PARTIAL_READY", "scientific_status": "NOT_APPLICABLE", "evidence_tier": "UNRESOLVED", "blocking_dependency": "A_C16_GPU_PACKAGE_AND_WHEEL_CLOSURE_REQUIRED", "note": "A fixed integration and H offline-protocol releases are hash-verified, but A's required GPU package/wheel closure remains unpublished"},
        {"stage_id": "C16-2.6", "owner": "G", "execution_status": "OFFLINE_SCHEMA_READY", "scientific_status": "NOT_APPLICABLE", "evidence_tier": "UNRESOLVED", "blocking_dependency": "C16-1.3_AND_C16-1.4_REQUIRED", "note": "Wave-1 catalog validator/publisher is ready; no native catalog exists"},
    ])
    if handoff is not None:
        atomic_text(handoff, handoff_text())
    refresh_manifest(out)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate(out: Path) -> None:
    expected = rows(out / "EXPECTED_HASHES.tsv")
    for row in expected:
        if row["kind"] == "LANE_G_SOURCE":
            path = ROOT / row["path_or_commit"]
            if not path.is_file() or sha256_file(path) != row["sha256"]:
                raise ContractError(f"source hash mismatch: {row['artifact_id']}")
        elif row["closure_status"] != "UPSTREAM_A_COMMITTED_MANIFEST_REQUIRED" or row["sha256"] != "NA":
            raise ContractError(f"upstream gap contract changed: {row['artifact_id']}")
    manifest = json.loads((out / "PUBLISH_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["status"] != "C16_G_OFFLINE_PACKAGE_PARTIAL_READY_FOR_UPSTREAM_CLOSURE" or manifest["capture_state"] != "NO_AUTODL_SSH_NO_NATIVE_RUN":
        raise ContractError("offline package state is not provenance-safe")
    listed = {item["path"]: item for item in manifest["files"]}
    actual = {path.name for path in out.iterdir() if path.is_file() and path.name != "PUBLISH_MANIFEST.json"}
    if set(listed) != actual:
        raise ContractError("package manifest file set mismatch")
    for name, item in listed.items():
        path = out / name
        if sha256_file(path) != item["sha256"] or path.stat().st_size != item["size_bytes"]:
            raise ContractError(f"package manifest digest mismatch: {name}")
    consumed = out / "CONSUMED_INPUTS.tsv"
    if consumed.is_file():
        with consumed.open(newline="", encoding="utf-8") as handle:
            consumed_rows = list(csv.DictReader(handle, delimiter="\t"))
        by_lane = {row.get("producer_lane"): row for row in consumed_rows}
        if by_lane.get("A", {}).get("consumption_status") != "HASH_VERIFIED_METADATA_INPUTS_ONLY":
            raise ContractError("A consumption receipt is missing or overclaims GPU-package eligibility")
        if by_lane.get("C", {}).get("dynamic_eligibility") != "NO_NATIVE_NVBIT_TARGET_YET":
            raise ContractError("C consumption receipt is missing or overclaims native target eligibility")
        if by_lane.get("H", {}).get("consumption_status") != "HASH_VERIFIED_MEMORY_PROTOCOL_ONLY" or by_lane.get("H", {}).get("dynamic_eligibility") != "NO_DYNAMIC_ADDRESS_OR_CAPTURE_INPUT":
            raise ContractError("H consumption receipt overclaims dynamic capture eligibility")
    print(f"PASS C16 G offline package validation: {len(listed)} files; upstream asset closure remains explicit")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--handoff-report", type=Path)
    args = parser.parse_args()
    if args.prepare == args.validate:
        parser.error("choose exactly one of --prepare or --validate")
    if args.prepare:
        handoff = args.handoff_report if args.handoff_report else (DEFAULT_HANDOFF if args.output_dir == DEFAULT_OUT else None)
        prepare(args.output_dir, handoff)
    else:
        validate(args.output_dir)


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 G package contract: {exc}", file=sys.stderr)
        raise SystemExit(2)
