#!/usr/bin/env python3
"""Build and independently validate the TC80 CM6 review package.

This is an evidence-only tool: it cannot launch a simulator and it refuses to
build a READY package unless it can reconstruct every contractual acceptance
fact from CM0--CM5 receipts, the frozen authority, and the immutable run
directories.  It is intentionally separate from the campaign controller so
CM6 is a second consumer of the evidence, rather than a self-declared PASS.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path


getcontext().prec = 80
START_COMMIT = "f16e75960f9e97a4ea51c9b997a24d52bb96c7bb"
AUTHORITY_SHA256 = "662d8973a5ff34e6039a7823b4417ba8be38bd5b13348aa779defa1356837a62"
PRIMARY_GEOMETRY = "32x20x128=640_lines=81920_bytes"
CM5_GEOMETRY = "128x5x128=640_lines=81920_bytes"
PRIMARY_ORDER = ["ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q"]
CM5_ORDER = ["BICG", "Btree", "2DConvolution"]


class FinalizationError(RuntimeError):
    """A CM6 acceptance fact was not independently established."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv_read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def tsv_write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def kv_read(path: Path) -> dict[str, str]:
    rows = tsv_read(path)
    if not rows or set(rows[0]) != {"key", "value"}:
        raise FinalizationError(f"not a key/value receipt: {path}")
    result: dict[str, str] = {}
    for row in rows:
        key, value = row["key"], row["value"]
        if key in result and result[key] != value:
            raise FinalizationError(f"conflicting receipt key {key!r}: {path}")
        result[key] = value
    return result


def display(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.000000000001"), rounding=ROUND_HALF_UP))


def geometric_mean(values: list[Decimal]) -> Decimal:
    if not values or any(value <= 0 for value in values):
        raise FinalizationError("geometric mean requires positive values")
    return (sum((value.ln() for value in values), Decimal(0)) / Decimal(len(values))).exp()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalizationError(message)


def status_value(path: Path, stage: str) -> str:
    rows = tsv_read(path)
    require(len(rows) == 1 and rows[0].get("stage") == stage, f"malformed {stage} status: {path}")
    return rows[0].get("status", "")


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git_paths(root: Path) -> list[str]:
    result = git(root, "status", "--porcelain=v1")
    require(result.returncode == 0, f"cannot inspect git worktree: {result.stderr.strip()}")
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        # A rename/copy records the destination after an arrow.  Either side
        # must be in the bounded TC80 scope, so preserve both for the audit.
        payload = line[3:]
        paths.extend(part.strip() for part in payload.split(" -> "))
    return paths


def git_diff_clean(root: Path, start: str, paths: list[str]) -> bool:
    return git(root, "diff", "--quiet", start, "--", *paths).returncode == 0


def root_paths(root: Path) -> dict[str, Path]:
    tc80 = root / "docs/dtc_l1/iscas2027/tc80"
    return {
        "tc80": tc80,
        "authority": tc80 / "TC80_WORKLOAD_AUTHORITY.tsv",
        "summary": tc80 / "CM3_TC80_FAST12_SUMMARY.tsv",
        "cm3_runs": tc80 / "CM3_TC80_FAST12_RUN_MANIFEST.tsv",
        "cm3_bindings": tc80 / "CM3_TC80_INPUT_AND_OUTPUT_MANIFEST.tsv",
        "cm4": tc80 / "CM4_CAPACITY_MATCHED_COMPARISON.tsv",
        "cm5": tc80 / "CM5_GEOMETRY_ROBUSTNESS_RUNS.tsv",
    }


def audit(root: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Return independently recomputed CM6 gate rows and derived paper values."""
    paths = root_paths(root)
    tc80 = paths["tc80"]
    rows: list[dict[str, object]] = []

    def gate(name: str, condition: bool, detail: str, evidence: str) -> None:
        require(condition, f"{name}: {detail}")
        rows.append({"gate": name, "status": "PASS", "detail": detail, "evidence": evidence})

    for stage in ("CM0", "CM1", "CM2", "CM3", "CM4", "CM5"):
        stage_path = tc80 / "status" / f"{stage}_STATUS.tsv"
        gate(f"{stage}_status", status_value(stage_path, stage) == "PASS", "machine-readable stage status is PASS", str(stage_path.relative_to(root)))

    authority_rows = tsv_read(paths["authority"])
    gate("authority_hash", sha256(paths["authority"]) == AUTHORITY_SHA256, "frozen FAST12 authority hash matches CM0/CM2 binding", str(paths["authority"].relative_to(root)))
    gate("authority_membership", [row.get("workload") for row in authority_rows] == PRIMARY_ORDER and
         [row.get("ordinal") for row in authority_rows] == [str(index) for index in range(1, 13)],
         "authority carries the exact ordered 12-member FAST12 membership", str(paths["authority"].relative_to(root)))

    overlay = tc80 / "config/TC80_CAPACITY_MATCHED_OVERLAY.config"
    gate("canonical_overlay_hash", sha256(overlay) == "92496d3664f24539df8ec4d17fe717b526a8eb5a1a391ef4a2db86e9a3ba44f4",
         "canonical 32x20 overlay is hash-bound", str(overlay.relative_to(root)))
    diff_rows = tsv_read(tc80 / "CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv")
    expected_fields = ["-gpgpu_cache:dl1", "-gpgpu_cache:dl1PrefL1", "-gpgpu_cache:dl1PrefShared", "-gpgpu_unified_l1d_size"]
    gate("only_sanctioned_config_differences", [row.get("field") for row in diff_rows] == expected_fields and
         all(row.get("check") == "PASS" for row in diff_rows) and
         all(row.get("classification") in {"REQUIRED_TC80_CAPACITY_GEOMETRY", "DERIVED_FROM_REQUIRED_GEOMETRY"} for row in diff_rows),
         "CM1 records exactly the three L1 geometry strings plus the required unified-size companion", str((tc80 / "CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv").relative_to(root)))
    frozen_fields = tsv_read(tc80 / "CM1_FROZEN_FIELD_AUDIT.tsv")
    gate("frozen_base_fields", bool(frozen_fields) and all(row.get("result") == "PASS" for row in frozen_fields),
         "all B16 fields outside the sanctioned capacity representation remain fixed", str((tc80 / "CM1_FROZEN_FIELD_AUDIT.tsv").relative_to(root)))

    smoke_rows = tsv_read(tc80 / "CM2_SMOKE_VALIDATION.tsv")
    gate("cm2_smoke", [row.get("workload") for row in smoke_rows] == ["NN", "Btree", "BICG"] and
         all(row.get("strict_status") == "PASS" and row.get("all_subchecks_pass") == "YES" for row in smoke_rows),
         "NN, Btree, and BICG smoke rows independently report strict PASS", str((tc80 / "CM2_SMOKE_VALIDATION.tsv").relative_to(root)))

    run_rows = tsv_read(paths["cm3_runs"])
    gate("cm3_exact_primary_manifest", [row.get("workload") for row in run_rows] == PRIMARY_ORDER and len(run_rows) == 12 and
         all(row.get("geometry") == PRIMARY_GEOMETRY and row.get("natural_exit") == "0" and row.get("disposition") == "ACCEPTED_STRICT_PASS" for row in run_rows),
         "exactly 12 primary rows use the fixed 32x20 exact-80-KiB geometry and naturally exit", str(paths["cm3_runs"].relative_to(root)))

    authority = {row["workload"]: row for row in authority_rows}
    primary_cycles: dict[str, int] = {}
    for row in run_rows:
        workload, run_dir = row["workload"], Path(row["run_dir"])
        manifest, terminal = kv_read(run_dir / "RUN_MANIFEST.tsv"), kv_read(run_dir / "RUN_TERMINAL.tsv")
        validation = json.loads((run_dir / "VALIDATION.json").read_text(encoding="utf-8"))
        checks = validation.get("checks", {})
        correct = (manifest.get("stage") == "CM3" and manifest.get("geometry") == PRIMARY_GEOMETRY and
                   manifest.get("effective_pib") == "8" and manifest.get("effective_mshr") == "32" and
                   manifest.get("trace_list_sha256") == authority[workload]["trace_list_sha256"] and
                   manifest.get("expected_instructions") == authority[workload]["instructions"] and
                   terminal.get("simulator_exit_status") == "0" and validation.get("status") == "PASS" and
                   validation.get("instructions") == int(authority[workload]["instructions"]) and bool(checks) and all(checks.values()))
        require(correct, f"CM3 strict receipt rejected for {workload}: {run_dir}")
        primary_cycles[workload] = int(validation["cycles"])
    gate("cm3_strict_identity_and_pib_mshr", True,
         "all 12 immutable receipts bind their frozen traces/instructions, 8/32 Base values, natural exits, and strict subchecks", str(paths["cm3_runs"].relative_to(root)))

    summary_rows = tsv_read(paths["summary"])
    gate("cm3_summary_binding", [row.get("workload") for row in summary_rows] == PRIMARY_ORDER and len(summary_rows) == 12 and
         all(int(row["tc80_cycles"]) == primary_cycles[row["workload"]] and row["b16_cycles"] == authority[row["workload"]]["b16_cycles"] and
             row["io_cycles"] == authority[row["workload"]]["io_cycles"] and row["oo_cycles"] == authority[row["workload"]]["oo_cycles"]
             for row in summary_rows),
         "primary table binds TC80 receipts and frozen B16/IO/OO cycles without rerunning them", str(paths["summary"].relative_to(root)))

    ratios: dict[str, Decimal] = {}
    metric_sources = {
        "GM_TC80_OVER_B16": ("b16_cycles", "tc80_cycles"),
        "GM_IO_OVER_B16": ("b16_cycles", "io_cycles"),
        "GM_OO_OVER_B16": ("b16_cycles", "oo_cycles"),
        "GM_IO_OVER_TC80": ("tc80_cycles", "io_cycles"),
        "GM_OO_OVER_TC80": ("tc80_cycles", "oo_cycles"),
    }
    for name, (numerator, denominator) in metric_sources.items():
        ratios[name] = geometric_mean([Decimal(row[numerator]) / Decimal(row[denominator]) for row in summary_rows])
    cm4_rows = {row.get("workload"): row for row in tsv_read(paths["cm4"])}
    cm4_fields = {
        "GM_TC80_OVER_B16": "tc80_over_b16", "GM_IO_OVER_B16": "io_over_b16", "GM_OO_OVER_B16": "oo_over_b16",
        "GM_IO_OVER_TC80": "io_over_tc80", "GM_OO_OVER_TC80": "oo_over_tc80",
    }
    gate("cm4_five_gms", all(name in cm4_rows and cm4_rows[name].get(cm4_fields[name]) == display(value)
         for name, value in ratios.items()), "all five CM4 geometric means are regenerated from the 12 integer-cycle rows", str(paths["cm4"].relative_to(root)))
    gate("frozen_io_oo_gms", display(ratios["GM_IO_OVER_B16"]) == "1.326143376158" and display(ratios["GM_OO_OVER_B16"]) == "1.592062401603",
         "frozen IO/B16 and OO/B16 geometric means reproduce under the declared 12-decimal formatting", str(paths["cm4"].relative_to(root)))

    trigger_rows = tsv_read(tc80 / "CM5_TRIGGER_DECISION.tsv")
    trigger = {row.get("criterion"): row for row in trigger_rows}
    gate("cm5_trigger", trigger.get("overall", {}).get("decision") == "TRIGGERED", "20-way primary and multiple exact legal geometries make CM5 mandatory", str((tc80 / "CM5_TRIGGER_DECISION.tsv").relative_to(root)))
    cm5_rows = tsv_read(paths["cm5"])
    gate("cm5_diagnostic_exclusion", [row.get("workload") for row in cm5_rows] == CM5_ORDER and len(cm5_rows) == 3 and
         all(row.get("alternate_geometry") == CM5_GEOMETRY and row.get("primary_gm_membership") == "EXCLUDED" and
             row.get("disposition") == "ACCEPTED_STRICT_PASS_DIAGNOSTIC" for row in cm5_rows),
         "the three predeclared alternate-geometry rows are strict diagnostics and excluded from every primary GM", str(paths["cm5"].relative_to(root)))

    head = git(root, "rev-parse", "HEAD")
    gate("start_head", head.returncode == 0 and head.stdout.strip() == START_COMMIT, "CM6 was built from the expected TC80 branch start commit plus bounded uncommitted TC80 artifacts", "git rev-parse HEAD")
    frozen_paths = ["docs/dtc_l1/post_fast64", "configs/dtc_l1/fast64"]
    gate("frozen_fast64_lane_e_unchanged", git_diff_clean(root, START_COMMIT, frozen_paths),
         "no tracked change versus start commit under frozen post-FAST64/Lane-E evidence or FAST64 config", "git diff --quiet START -- frozen paths")
    source_paths = ["src", "gpu-simulator", "configs/dtc_l1/fast64", "docs/dtc_l1/post_fast64"]
    gate("no_core_simulator_or_frozen_science_change", git_diff_clean(root, START_COMMIT, source_paths),
         "no tracked Core, simulator, FAST64 config, or frozen science path changed", "git diff --quiet START -- source/frozen paths")
    changes = git_paths(root)
    allowed = ("docs/dtc_l1/iscas2027/tc80/", "util/dtc_l1/tc80_campaign.py", "util/dtc_l1/tc80_evidence.py", "util/dtc_l1/tc80_finalize.py")
    gate("bounded_git_scope", all(path.startswith(allowed) for path in changes),
         "all working-tree changes are within the TC80 documentation/controller/evidence scope", "git status --porcelain=v1")

    return rows, {"gms": ratios, "authority": authority, "primary_cycles": primary_cycles}


def write_claims(path: Path, gms: dict[str, Decimal]) -> None:
    path.write_text(
        "# TC80 claim/evidence boundary\n\n"
        "The capacity-matched experiment compares a conventional, searchable 80-KiB L1D (TC80: 640 conventional 128-B lines) "
        "against the frozen DTC configuration that has a 16-KiB logical searchable Tag capacity and an 80-KiB physical pool. "
        "It therefore asks about ordinary locality capacity versus decoupled in-flight physical state under an equal data-array-byte budget. "
        "TC80 has more searchable conventional Tag entries and is deliberately a strong conventional-capacity baseline.\n\n"
        "The five recomputed FAST12 geometric mean ratios are:\n\n" +
        "\n".join(f"- `{name}` = `{display(value)}`" for name, value in gms.items()) +
        "\n\nThese are measured simulation-cycle comparisons. They do not establish total-area equality, metadata equivalence, RTL timing, "
        "power equality, or a causal attribution to any one DTC mechanism. TC80 deliberately retains the frozen Base PIB=8 and effective "
        "MSHR=32; it is not a large-PIB or large-MSHR conventional-cache ablation. CM5 is a predeclared exact-capacity geometry diagnostic, "
        "not a performance-selected alternate primary baseline.\n",
        encoding="utf-8")


def write_limitations(path: Path) -> None:
    path.write_text(
        "# Limitations\n\n"
        "- Equal 80-KiB data-array capacity is not a total-area, metadata, power, or timing match.\n"
        "- TC80 preserves B16's Base-mode PIB=8 and effective MSHR=32; large conventional PIB/MSHR variants require a separate handoff.\n"
        "- The only newly run rows are TC80 conventional-cache rows. B16, IO, and OO cycle values are hash-bound frozen inputs and were not rerun.\n"
        "- CM5 changes only legal exact-80-KiB set/way geometry for three diagnostics. It is excluded from primary geometric means and does not select the primary geometry by performance.\n"
        "- The result is a cycle-level model result, not a standalone causal proof of a microarchitectural mediator.\n",
        encoding="utf-8")


def write_reproduction(path: Path, root: Path) -> None:
    path.write_text(
        "# Reproduction and provenance\n\n"
        "This sealed evidence package was built from the TC80 branch start commit `f16e75960f9e97a4ea51c9b997a24d52bb96c7bb`. "
        "The primary controller refuses B16/IO/OO runs and records each new TC80 attempt in a new immutable directory. "
        "The run paths, trace hashes, runtime hashes, stdout hashes, validation hashes, and frozen B16/IO/OO source bindings are in the copied manifests.\n\n"
        "Historical primary invocation shape (one per authority workload):\n\n"
        "```sh\npython3 util/dtc_l1/tc80_campaign.py run --authority docs/dtc_l1/iscas2027/tc80/TC80_WORKLOAD_AUTHORITY.tsv "
        "--workload <FAST12-member> --stage CM3 --runs-root /workspace/tc80-capacity-matched-runs "
        "--base-config configs/dtc_l1/fast64/FAST64_BASE.config --overlay docs/dtc_l1/iscas2027/tc80/config/TC80_CAPACITY_MATCHED_OVERLAY.config "
        "--overlay-sha256 92496d3664f24539df8ec4d17fe717b526a8eb5a1a391ef4a2db86e9a3ba44f4 "
        "--trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config --geometry-profile TC80_S32_W20\n```\n\n"
        "CM5 used the separately predeclared 128x5 exact-80-KiB overlay and the `CM5_S128_W5` profile only for BICG, Btree, and 2DConvolution. "
        "It never contributes to CM3 or primary geometric means. The final checks can be repeated without simulation:\n\n"
        "```sh\npython3 util/dtc_l1/tc80_finalize.py validate --repo-root " + str(root) + " --output docs/dtc_l1/iscas2027/tc80/review_pack\n```\n",
        encoding="utf-8")


def copy_sources(root: Path, stage: Path) -> list[tuple[str, Path]]:
    tc80 = root / "docs/dtc_l1/iscas2027/tc80"
    source_names = [
        "CM0_SOURCE_AND_CONFIG_AUDIT.md", "CM0_GEOMETRY_CANDIDATES.tsv", "CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv",
        "CM1_CONFIG_SHA256.tsv", "CM1_FROZEN_FIELD_AUDIT.tsv", "CM1_TC80_CONFIG_LOCK.md", "CM2_SMOKE_RUN_MANIFEST.tsv",
        "CM2_SMOKE_VALIDATION.tsv", "CM2_RAW_PROVENANCE.tsv", "CM3_ORDER_RECONCILIATION.md", "CM3_TC80_FAST12_RUN_MANIFEST.tsv",
        "CM3_TC80_FAST12_SUMMARY.tsv", "CM3_TC80_INPUT_AND_OUTPUT_MANIFEST.tsv", "CM4_CAPACITY_MATCHED_COMPARISON.tsv",
        "CM4_CAPACITY_MATCHED_ANALYSIS.md", "CM4_PAPER_PLOT_READY.tsv", "CM5_TRIGGER_DECISION.tsv",
        "CM5_PREDECLARED_GEOMETRY_RATIONALE.md", "CM5_GEOMETRY_ROBUSTNESS_RUNS.tsv", "CM5_GEOMETRY_ROBUSTNESS_ANALYSIS.md",
        "TC80_WORKLOAD_AUTHORITY.tsv", "TC80_CONTROLLER_GENEALOGY.md",
    ]
    copied: list[tuple[str, Path]] = []
    for name in source_names:
        source, destination = tc80 / name, stage / "evidence" / name
        require(source.is_file(), f"missing required review-pack source: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append((str(destination.relative_to(stage)), source))
    for name in ("TC80_CAPACITY_MATCHED_OVERLAY.config", "TC80_RESOLVED_EFFECTIVE_CONFIG.tsv", "CM5_S128_W5_EXACT80_DIAGNOSTIC_OVERLAY.config"):
        source, destination = tc80 / "config" / name, stage / "config" / name
        shutil.copy2(source, destination)
        copied.append((str(destination.relative_to(stage)), source))
    for stage_name in ("CM0", "CM1", "CM2", "CM3", "CM4", "CM5"):
        source, destination = tc80 / "status" / f"{stage_name}_STATUS.tsv", stage / "status" / f"{stage_name}_STATUS.tsv"
        shutil.copy2(source, destination)
        copied.append((str(destination.relative_to(stage)), source))
    for name in ("tc80_campaign.py", "tc80_evidence.py", "tc80_finalize.py"):
        source, destination = root / "util/dtc_l1" / name, stage / "tools" / name
        shutil.copy2(source, destination)
        copied.append((str(destination.relative_to(stage)), source))
    return copied


def output_manifest(stage: Path, source_map: dict[str, str]) -> None:
    entries: list[dict[str, object]] = []
    for file_path in sorted(path for path in stage.rglob("*") if path.is_file() and path.name != "INPUT_OUTPUT_SHA256.tsv"):
        relative = str(file_path.relative_to(stage))
        entries.append({"relative_path": relative, "sha256": sha256(file_path), "bytes": file_path.stat().st_size,
                        "source_or_generator": source_map.get(relative, "GENERATED_BY_TC80_FINALIZER")})
    tsv_write(stage / "INPUT_OUTPUT_SHA256.tsv", ["relative_path", "sha256", "bytes", "source_or_generator"], entries)


def build(args: argparse.Namespace) -> None:
    root, output = Path(args.repo_root).resolve(), Path(args.output).resolve()
    require(not output.exists(), f"refusing to overwrite an existing review package: {output}")
    validation_rows, derived = audit(root)
    staging = Path(tempfile.mkdtemp(prefix="tc80-review-pack-", dir=output.parent))
    try:
        copied = copy_sources(root, staging)
        source_map = {relative: str(source.relative_to(root)) for relative, source in copied}
        tsv_write(staging / "review" / "FINAL_VALIDATION.tsv", ["gate", "status", "detail", "evidence"], validation_rows)
        source_map["review/FINAL_VALIDATION.tsv"] = "INDEPENDENT_AUDIT_AT_CM6_BUILD"
        write_claims(staging / "review" / "CLAIM_EVIDENCE_BOUNDARIES.md", derived["gms"])
        write_limitations(staging / "review" / "LIMITATIONS.md")
        write_reproduction(staging / "REPRODUCTION.md", root)
        stage_status = [{"stage": row["gate"], "status": row["status"], "detail": row["detail"]} for row in validation_rows]
        stage_status.append({"stage": "CM6", "status": "PASS", "detail": "Independent raw-evidence audit completed before READY package emission."})
        tsv_write(staging / "review" / "STAGE_STATUS_AND_GATES.tsv", ["stage", "status", "detail"], stage_status)
        output_manifest(staging, source_map)
        os.replace(staging, output)
    except BaseException:
        # Staging is an explicitly created temporary directory; leave it for
        # diagnosis rather than deleting evidence after a failed package build.
        raise
    status_path = root / "docs/dtc_l1/iscas2027/tc80/status/CM6_STATUS.tsv"
    tsv_write(status_path, ["stage", "status", "input_commit_or_hash", "output_artifacts", "blocking_reason", "detail"], [{
        "stage": "CM6", "status": "ISCAS2027_TC80_CAPACITY_MATCHED_BASELINE_READY_FOR_PAPER",
        "input_commit_or_hash": f"start_commit={START_COMMIT};authority_sha256={AUTHORITY_SHA256}",
        "output_artifacts": str(output.relative_to(root)), "blocking_reason": "NONE",
        "detail": "Independent CM6 audit passed before review-pack emission; primary CM3 has 12 exact TC80 rows and CM5 diagnostics are excluded from all primary GMs.",
    }])
    print(output)


def validate(args: argparse.Namespace) -> None:
    root, output = Path(args.repo_root).resolve(), Path(args.output).resolve()
    require(output.is_dir(), f"missing review package: {output}")
    validation_rows, _ = audit(root)
    stored_rows = tsv_read(output / "review" / "FINAL_VALIDATION.tsv")
    require(stored_rows == [{key: str(value) for key, value in row.items()} for row in validation_rows],
            "stored CM6 validation does not equal a fresh independent audit")
    manifest_rows = tsv_read(output / "INPUT_OUTPUT_SHA256.tsv")
    recorded = {row["relative_path"]: row for row in manifest_rows}
    actual_files = {str(path.relative_to(output)): path for path in output.rglob("*") if path.is_file() and path.name != "INPUT_OUTPUT_SHA256.tsv"}
    require(set(recorded) == set(actual_files), "review-pack output manifest path set mismatch")
    for relative, file_path in actual_files.items():
        row = recorded[relative]
        require(row["sha256"] == sha256(file_path) and int(row["bytes"]) == file_path.stat().st_size,
                f"review-pack output manifest content mismatch: {relative}")
    cm6 = root / "docs/dtc_l1/iscas2027/tc80/status/CM6_STATUS.tsv"
    gate = status_value(cm6, "CM6")
    require(gate == "ISCAS2027_TC80_CAPACITY_MATCHED_BASELINE_READY_FOR_PAPER", "CM6 READY status missing")
    print("TC80 CM6 independent validation PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("build", build), ("validate", validate)):
        command = commands.add_parser(name)
        command.add_argument("--repo-root", required=True)
        command.add_argument("--output", required=True)
        command.set_defaults(handler=handler)
    args = parser.parse_args()
    try:
        args.handler(args)
    except (FinalizationError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"TC80 finalization rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
