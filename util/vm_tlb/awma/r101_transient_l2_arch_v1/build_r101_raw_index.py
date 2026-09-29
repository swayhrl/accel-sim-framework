#!/usr/bin/env python3
"""Build the hash-closed R101 raw-data index and node164 evidence manifest.

The script deliberately does not follow the 18 simulator-trace symlinks.  Their
accepted hashes remain bound by the producer manifest and the independently
validated consumer admission receipt.  ``--write`` is required for mutation;
without it the script validates and reports the prospective closure only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


STAGE = "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1"
REPO = Path("/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1")
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1"
NODE_ROOT = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1")
PRODUCER_ROOT = Path(
    "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/"
    "r101_transient_l2_sim_capture_20260927"
)
RUNTIME = NODE_ROOT / "runtime"
FORMAL = NODE_ROOT / "raw/formal"
NODE_MANIFEST_NAME = "NODE164_EVIDENCE_SHA256SUMS"
INDEX_NAME = "RAW_DATA_INDEX.tsv"

ARMS = ("B0", "O1", "M1")
ARM_MODES = {
    "B0": "none",
    "O1": "oracle_dead_drop",
    "M1": "bounded_live_retention",
}
FORMAL_ARTIFACTS = (
    "command.json",
    "start_utc.txt",
    "rc.txt",
    "wall_seconds.txt",
    "run.log",
    "run.stderr",
    "gpgpu_inst_stats.txt",
    "RUN_SUMMARY.json",
)
EXPECTED = {
    "producer_commit": "bb902283b7ce9e1902b460383fbd3e0bedbd884d",
    "payload_sha256": "1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234",
    "output_sha256": "36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0",
    "trace_aggregate_sha256": "34031eebe1e25b375d9ee058328f678e4734790c40e67284bb6511130e4fec0e",
    "sidecar_sha256": "740820a195ae2bb9966a91b1e6d3423f4ded520bd91d1819aac8e78ce104b77d",
    "kernelslist_sha256": "9fce012939496008814786a0c12d32c1f97a10c07c62cdd08f1fddcee5d86588",
    "binary_sha256": "32b38a66ba6b9eee5a9047873992fec42fcc4dbbff6adf247d425aec2b650c5d",
    "core_library_sha256": "f18cd8d4c2dd8927d6ad454295e434b902032042e83bbab03afcbd02b23921bf",
    "core_patch_sha256": "aa2637f3379f1c0b6184db98a41f276dcdd6bcef86cb72331b18c52cf6232676",
    "framework_sha256": "c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323",
    "config_sha256": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "trace_config_sha256": "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b",
    "summarizer_sha256": "05eda1f021336bba4ebed018ba8657492a0df0b1318c00eecd2c1378b161a1d4",
}


class ClosureError(RuntimeError):
    """An input needed for a hash-closed index is absent or invalid."""


@dataclass(frozen=True)
class Row:
    evidence_role: str
    arm_or_attempt: str
    artifact: str
    path: str
    size_bytes: int
    sha256: str
    status: str
    notes: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_note(note: str) -> str:
    require("\t" not in note and "\n" not in note and "\r" not in note,
            f"note is not TSV-safe: {note!r}")
    return note


def row(role: str, arm: str, artifact: str, path: Path, status: str,
        notes: str) -> Row:
    require(path.is_file(), f"missing evidence file: {path}")
    require(not path.is_symlink(), f"symlink cannot be directly indexed: {path}")
    return Row(
        role,
        arm,
        artifact,
        str(path.resolve()),
        path.stat().st_size,
        file_sha256(path),
        status,
        clean_note(notes),
    )


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ClosureError(f"invalid JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def trace_aggregate(admission: dict[str, Any]) -> str:
    members = admission.get("trace_members")
    require(isinstance(members, list) and len(members) == 18,
            "consumer admission does not contain exactly 18 trace members")
    binding = "".join(
        f"{Path(member['path']).name}\t{member['sha256']}\n"
        for member in members
    ).encode()
    return hashlib.sha256(binding).hexdigest()


def validate_authorities() -> dict[str, str]:
    producer_pack = PRODUCER_ROOT / "review_pack"
    producer_manifest_path = producer_pack / "SIM_CAPTURE_MANIFEST.json"
    producer_binding_path = producer_pack / "ACCEPTED_INPUT_BINDING.json"
    producer_manifest = load_json(producer_manifest_path)
    producer_binding = load_json(producer_binding_path)
    admission_path = NODE_ROOT / "input/ADMISSION_RECEIPT.json"
    admission = load_json(admission_path)

    require(producer_manifest.get("status") == "R101_TRANSIENT_SIM_CAPTURE_PASS",
            "producer manifest status is not accepted PASS")
    require(producer_manifest.get("member_count") == 18,
            "producer manifest member count is not 18")
    require(producer_manifest.get("drop_count") == 0,
            "producer manifest drop count is nonzero")
    require(producer_manifest.get("overflow_count") == 0,
            "producer manifest overflow count is nonzero")
    require(producer_manifest.get("terminal_complete") is True,
            "producer manifest terminal is incomplete")
    require(producer_binding.get("payload_sha256") == EXPECTED["payload_sha256"],
            "producer accepted payload hash drift")
    require(producer_binding.get("accepted_output_sha256") == EXPECTED["output_sha256"],
            "producer accepted output hash drift")

    require(admission.get("status") == "PASS", "consumer admission is not PASS")
    require(admission.get("producer_commit") == EXPECTED["producer_commit"],
            "consumer producer-commit authority drift")
    require(admission.get("accepted_payload_sha256") == EXPECTED["payload_sha256"],
            "consumer payload authority drift")
    require(admission.get("accepted_output_sha256") == EXPECTED["output_sha256"],
            "consumer output authority drift")
    require(admission.get("runtime_sidecar_sha256") == EXPECTED["sidecar_sha256"],
            "consumer sidecar authority drift")
    require(admission.get("kernelslist_sha256") == EXPECTED["kernelslist_sha256"],
            "consumer kernelslist authority drift")
    require(trace_aggregate(admission) == EXPECTED["trace_aggregate_sha256"],
            "consumer ordered trace aggregate drift")

    sidecar = NODE_ROOT / "input/transient_l2_runtime.tsv"
    kernelslist = NODE_ROOT / "input/traces/kernelslist.g"
    require(file_sha256(sidecar) == EXPECTED["sidecar_sha256"],
            "consumer sidecar bytes drift")
    require(file_sha256(kernelslist) == EXPECTED["kernelslist_sha256"],
            "consumer kernelslist bytes drift")
    return {
        "producer_manifest": str(producer_manifest_path),
        "producer_binding": str(producer_binding_path),
        "admission": str(admission_path),
    }


def validate_formal() -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    baseline: dict[str, Any] | None = None
    for arm in ARMS:
        run_dir = FORMAL / arm
        for name in FORMAL_ARTIFACTS:
            require((run_dir / name).is_file(), f"{arm}: missing formal artifact {name}")
        summary = load_json(run_dir / "RUN_SUMMARY.json")
        require(summary.get("arm") == arm, f"{arm}: summary arm mismatch")
        require(summary.get("mode") == ARM_MODES[arm], f"{arm}: mode mismatch")
        require(summary.get("status") == "PASS", f"{arm}: status is not PASS")
        require(summary.get("rc") == 0, f"{arm}: summary rc is not zero")
        require((run_dir / "rc.txt").read_text().strip() == "0",
                f"{arm}: rc.txt is not zero")
        require(summary.get("stderr_bytes") == 0, f"{arm}: stderr_bytes is nonzero")
        require((run_dir / "run.stderr").stat().st_size == 0,
                f"{arm}: durable stderr is nonempty")
        gates = summary.get("gates")
        require(isinstance(gates, dict) and gates, f"{arm}: gates missing")
        require(all(type(value) is bool for value in gates.values()),
                f"{arm}: gate value is not boolean")
        failed = sorted(key for key, value in gates.items() if value is not True)
        require(not failed, f"{arm}: failed gates: {failed}")
        for key in (
            "coverage_records_exact",
            "cross_arm_identity",
            "terminal_memory_drain_receipt",
            "dram_latency_queues_empty",
            "writeback_completion_exact",
            "translation_quiescent_invariants",
            "kernel_count_exact",
            "terminal_quiescent",
            "writeback_byte_accounting_exact",
        ):
            require(gates.get(key) is True, f"{arm}: required gate absent/false: {key}")
        coverage = summary.get("coverage")
        require(isinstance(coverage, dict) and coverage.get("kernels") == 18,
                f"{arm}: coverage is not exactly 18 kernels")
        require(coverage.get("translated") == coverage.get("admissions"),
                f"{arm}: translated/admissions mismatch")
        require(coverage.get("translated_unique") == coverage.get("unique"),
                f"{arm}: translated_unique/unique mismatch")
        require(coverage.get("untranslated") == 0 and
                coverage.get("untranslated_unique") == 0 and
                coverage.get("unobserved") == 0,
                f"{arm}: incomplete translation coverage")
        require(summary.get("drain_gpu_active") == 0 and
                summary.get("drain_l2_writeback_active") == 0 and
                summary.get("drain_max_limit_hit") == 0 and
                summary.get("drain_gpu_deadlock") == 0,
                f"{arm}: full drain failed")
        queues = summary.get("dram_latency_queues")
        require(isinstance(queues, list) and len(queues) == 8 and not any(queues),
                f"{arm}: DRAM latency queues are not empty")
        awma = summary.get("awma")
        require(isinstance(awma, dict), f"{arm}: AWMA counters missing")
        require(awma.get("awma_transient_l2_terminal_quiescent") == 1,
                f"{arm}: controller not quiescent")
        require(awma.get("awma_transient_l2_outstanding_l2_writebacks") == 0,
                f"{arm}: outstanding writebacks remain")
        require(awma.get("awma_transient_l2_completed_l2_writebacks") ==
                awma.get("awma_transient_l2_l2_writebacks"),
                f"{arm}: writeback completion mismatch")
        require(isinstance(summary.get("coverage_uid_identity"), list) and
                len(summary["coverage_uid_identity"]) == 18,
                f"{arm}: UID identity is not 18 records")
        require(isinstance(summary.get("artifact_receipt"), dict),
                f"{arm}: artifact receipt missing")
        if baseline is None:
            baseline = summary
        else:
            require(summary.get("instructions") == baseline.get("instructions"),
                    f"{arm}: instructions differ from B0")
            require(summary.get("ctas") == baseline.get("ctas"),
                    f"{arm}: CTAs differ from B0")
            require(summary["coverage_uid_identity"] == baseline["coverage_uid_identity"],
                    f"{arm}: coverage UID identity differs from B0")
            require(summary["artifact_receipt"] == baseline["artifact_receipt"],
                    f"{arm}: artifact receipt differs from B0")
        summaries[arm] = summary
    return summaries


def regular_files(root: Path) -> Iterable[Path]:
    require(root.is_dir(), f"missing evidence directory: {root}")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_file():
            yield path


def node_evidence_files() -> list[Path]:
    files = [
        NODE_ROOT / "input/ADMISSION_RECEIPT.json",
        NODE_ROOT / "input/transient_l2_runtime.tsv",
        NODE_ROOT / "input/traces/kernelslist.g",
    ]
    raw_roots = (
        NODE_ROOT / "raw/formal",
        NODE_ROOT / "raw/engineering",
        NODE_ROOT / "raw/pilot",
        NODE_ROOT / "raw/off_equivalence_t2",
        NODE_ROOT / "raw/explicit_none_equivalence_t2",
        NODE_ROOT / "raw/oracle_no_overlap_t2",
        NODE_ROOT / "raw/m1_no_overlap_t2",
        NODE_ROOT / "raw/preimplementation_regressions",
        NODE_ROOT / "raw/postimplementation_regressions",
    )
    for root in raw_roots:
        files.extend(regular_files(root))
    files.extend((
        RUNTIME / "bin/unified_accel-sim.out",
        RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release/libcudart.so",
        RUNTIME / "awma_transient_l2_policy_test",
        RUNTIME / "awma_transient_l2_policy_test.cc",
        RUNTIME / "unified_build.log",
    ))
    result = sorted(set(path.resolve() for path in files))
    for path in result:
        require(path.is_file(), f"missing node164 evidence artifact: {path}")
        require(not path.is_symlink(), f"trace symlink escaped exclusion: {path}")
    return result


def validate_frozen_hashes() -> None:
    checks = {
        RUNTIME / "bin/unified_accel-sim.out": EXPECTED["binary_sha256"],
        RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release/libcudart.so": (
            EXPECTED["core_library_sha256"]
        ),
        PACK / "TRANSIENT_L2_CORE.patch": EXPECTED["core_patch_sha256"],
        REPO / "gpu-simulator/accel-sim.cc": EXPECTED["framework_sha256"],
        REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config": (
            EXPECTED["config_sha256"]
        ),
        REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config": (
            EXPECTED["trace_config_sha256"]
        ),
        REPO / "util/vm_tlb/awma/r101_transient_l2_arch_v1/"
        "summarize_r101_transient_run.py": EXPECTED["summarizer_sha256"],
    }
    for path, expected in checks.items():
        require(path.is_file(), f"missing frozen artifact: {path}")
        actual = file_sha256(path)
        require(actual == expected,
                f"frozen artifact hash drift: {path}: {actual} != {expected}")


def manifest_text(paths: list[Path]) -> str:
    lines = []
    for path in paths:
        relative = path.relative_to(NODE_ROOT)
        lines.append(f"{file_sha256(path)}  {relative.as_posix()}\n")
    return "".join(lines)


def verify_manifest(path: Path) -> int:
    count = 0
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"manifest line {line_number} malformed")
        expected, relative = parts
        require(len(expected) == 64, f"manifest line {line_number} hash malformed")
        require(relative not in seen, f"manifest duplicate path: {relative}")
        seen.add(relative)
        artifact = NODE_ROOT / relative
        require(artifact.is_file() and not artifact.is_symlink(),
                f"manifest artifact missing/not regular: {artifact}")
        require(file_sha256(artifact) == expected,
                f"manifest hash mismatch: {artifact}")
        count += 1
    require(count > 0, "node164 evidence manifest is empty")
    return count


def classify_node_file(path: Path) -> tuple[str, str, str, str]:
    relative = path.relative_to(NODE_ROOT).as_posix()
    parts = relative.split("/")
    if relative.startswith("raw/formal/"):
        return "FORMAL_PRIMARY", parts[2], "PASS", "accepted B0/O1/M1 formal artifact"
    if relative.startswith("raw/engineering/"):
        return ("ENGINEERING_EXCLUDED", parts[2], "EXCLUDED_FROM_FORMAL",
                "old-B0 engineering drain attempt; not in formal contrasts")
    if relative.startswith("raw/pilot/"):
        return ("PILOT_EXCLUDED", parts[2], "EXCLUDED_FROM_FORMAL",
                "UID1 nonformal scope pilot")
    if (relative.startswith("raw/") and len(parts) > 1 and parts[1] in {
            "off_equivalence_t2",
            "explicit_none_equivalence_t2",
            "oracle_no_overlap_t2",
            "m1_no_overlap_t2",
    }):
        return ("SMOKE_EXCLUDED", parts[1], "PASS_EXCLUDED_FROM_FORMAL",
                "accepted T2 engineering smoke/equivalence evidence")
    if relative.startswith("raw/preimplementation_regressions/"):
        return ("REGRESSION_QUALIFICATION", "PRE_IMPLEMENTATION", "PASS",
                "producer-independent regression evidence")
    if relative.startswith("raw/postimplementation_regressions/"):
        return ("REGRESSION_QUALIFICATION", "POST_IMPLEMENTATION", "PASS",
                "candidate regression/directed-test evidence")
    if relative.startswith("input/"):
        return ("CONSUMER_INPUT", "SIM_INPUT_R101_L512_TRANSIENT_V1", "PASS",
                "small admitted input receipt/sidecar/list; trace symlinks excluded")
    if relative.startswith("runtime/"):
        return ("FROZEN_RUNTIME", "FROZEN_FORMAL_RUNTIME", "FROZEN",
                "runtime/build artifact used by formal matrix")
    raise ClosureError(f"unclassified node164 evidence path: {relative}")


def build_rows(node_files: list[Path], manifest_path: Path,
               builder_path: Path) -> list[Row]:
    rows: list[Row] = []
    producer_pack = PRODUCER_ROOT / "review_pack"
    producer_files = (
        "ACCEPTED_INPUT_BINDING.json",
        "SIM_CAPTURE_MANIFEST.json",
        "TRACE_MEMBER_MANIFEST.tsv",
        "RAW_DATA_INDEX.tsv",
        "SHA256SUMS",
        "TRANSFER_RECEIPT.md",
    )
    for name in producer_files:
        notes = "accepted producer authority; giant trace members referenced, not rehashed"
        if name == "ACCEPTED_INPUT_BINDING.json":
            notes += (f"; payload={EXPECTED['payload_sha256']}; "
                      f"output={EXPECTED['output_sha256']}")
        if name == "SIM_CAPTURE_MANIFEST.json":
            notes += f"; ordered_trace_aggregate={EXPECTED['trace_aggregate_sha256']}"
        rows.append(row("PRODUCER_AUTHORITY_REFERENCE", EXPECTED["producer_commit"],
                        name, producer_pack / name, "ACCEPTED_REFERENCE", notes))
    rows.append(row(
        "PRODUCER_AUTHORITY_REFERENCE",
        EXPECTED["producer_commit"],
        "NODE164_SHA256SUMS",
        PRODUCER_ROOT / "NODE164_SHA256SUMS",
        "ACCEPTED_REFERENCE",
        "producer node164 manifest file only; giant members not rehashed by this stage",
    ))

    for path in node_files:
        role, arm, status, notes = classify_node_file(path)
        rows.append(row(role, arm, path.relative_to(NODE_ROOT).as_posix(),
                        path, status, notes))

    rows.append(row(
        "NODE164_EVIDENCE_MANIFEST",
        "B0_O1_M1_AND_ENGINEERING",
        NODE_MANIFEST_NAME,
        manifest_path,
        "PASS",
        "atomically generated and immediately hash-verified; excludes trace symlinks",
    ))

    repo_artifacts = (
        ("FROZEN_SOURCE", "FROZEN_FORMAL_RUNTIME", "TRANSIENT_L2_CORE.patch",
         PACK / "TRANSIENT_L2_CORE.patch", "FROZEN", "frozen Core patch"),
        ("FROZEN_SOURCE", "FROZEN_FORMAL_RUNTIME", "accel-sim.cc",
         REPO / "gpu-simulator/accel-sim.cc", "FROZEN", "matched full-drain framework source"),
        ("FROZEN_SOURCE", "FROZEN_FORMAL_RUNTIME", "gpgpusim.config",
         REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config",
         "FROZEN", "accepted RTX4080/V1 platform config"),
        ("FROZEN_SOURCE", "FROZEN_FORMAL_RUNTIME", "trace.config",
         REPO / "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config",
         "FROZEN", "accepted trace config"),
    )
    for args in repo_artifacts:
        rows.append(row(*args))

    tool_dir = REPO / "util/vm_tlb/awma/r101_transient_l2_arch_v1"
    tools = (
        "run_r101_transient_matrix.py",
        "summarize_r101_transient_run.py",
        "finalize_r101_results.py",
        "extract_m1_per_kernel.py",
    )
    for name in tools:
        rows.append(row("ANALYSIS_TOOL", "FINAL_CLOSURE", name, tool_dir / name,
                        "FROZEN", "formal runner/summarizer/finalizer/extractor"))
    rows.append(row("ANALYSIS_TOOL", "FINAL_CLOSURE", builder_path.name,
                    builder_path, "FROZEN", "raw index and node164 manifest builder"))

    derived = (
        "BASELINE_L2_ACCOUNTING.tsv",
        "O1_ORACLE_RESULTS.tsv",
        "EXPLORATION_MATRIX.tsv",
        "TRAFFIC_AND_CYCLE_RESULTS.tsv",
        "RUN_RECEIPTS.json",
        "PER_KERNEL_M1_TELEMETRY.tsv",
    )
    for name in derived:
        note = "derived from validated durable formal summaries"
        if name == "PER_KERNEL_M1_TELEMETRY.tsv":
            note = "per-kernel M1 telemetry derived by frozen extractor"
        rows.append(row("DERIVED_RESULT", "B0_O1_M1", name, PACK / name,
                        "PASS", note))

    paths = [item.path for item in rows]
    require(len(paths) == len(set(paths)), "RAW index contains duplicate file paths")
    return rows


def rows_to_tsv(rows: list[Row]) -> str:
    output = io.StringIO()
    fieldnames = list(Row.__dataclass_fields__)
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    for item in rows:
        writer.writerow(asdict(item))
    return output.getvalue()


def verify_index(path: Path) -> int:
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames == list(Row.__dataclass_fields__),
                "RAW index header mismatch")
        rows = list(reader)
    require(rows, "RAW index is empty")
    seen: set[str] = set()
    for number, item in enumerate(rows, 2):
        evidence = Path(item["path"])
        require(item["path"] not in seen, f"RAW index duplicate path at line {number}")
        seen.add(item["path"])
        require(evidence.is_absolute(), f"RAW index path not absolute at line {number}")
        require(evidence.is_file() and not evidence.is_symlink(),
                f"RAW index path missing/not regular at line {number}: {evidence}")
        require(int(item["size_bytes"]) == evidence.stat().st_size,
                f"RAW index size mismatch at line {number}: {evidence}")
        require(item["sha256"] == file_sha256(evidence),
                f"RAW index hash mismatch at line {number}: {evidence}")
    return len(rows)


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        temporary.write_text(text)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def fail_closed(message: str) -> int:
    print(json.dumps({
        "stage": STAGE,
        "status": "FAIL_CLOSED",
        "error": message,
        "write_performed": False,
    }, sort_keys=True))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--node-root", type=Path, default=NODE_ROOT)
    parser.add_argument("--producer-root", type=Path, default=PRODUCER_ROOT)
    args = parser.parse_args()
    builder_path = Path(__file__).resolve()
    manifest_path = NODE_ROOT / NODE_MANIFEST_NAME
    index_path = PACK / INDEX_NAME
    try:
        require(args.repo.resolve() == REPO, "alternate repo root is not authorized")
        require(args.node_root.resolve() == NODE_ROOT,
                "alternate node root is not authorized")
        require(args.producer_root.resolve() == PRODUCER_ROOT,
                "alternate producer root is not authorized")
        validate_authorities()
        summaries = validate_formal()
        validate_frozen_hashes()
        node_files = node_evidence_files()
        # Classify every node artifact before the first permitted write so an
        # unexpected evidence path cannot leave a partial two-file closure.
        for node_file in node_files:
            classify_node_file(node_file)
        manifest = manifest_text(node_files)
        if args.write:
            atomic_write(manifest_path, manifest)
            manifest_count = verify_manifest(manifest_path)
        else:
            # Validate the prospective manifest without creating a file.
            require(bool(manifest), "prospective node164 evidence manifest is empty")
            manifest_count = len(manifest.splitlines())
            require(manifest_path.is_file(),
                    "--write is required before RAW index can bind node164 manifest")
            require(manifest_path.read_text() == manifest,
                    "existing node164 evidence manifest is stale; rerun with --write")
            verify_manifest(manifest_path)
        rows = build_rows(node_files, manifest_path, builder_path)
        index_text = rows_to_tsv(rows)
        if args.write:
            atomic_write(index_path, index_text)
            row_count = verify_index(index_path)
        else:
            require(index_path.is_file(),
                    "--write is required before RAW index can be verified")
            require(index_path.read_text() == index_text,
                    "existing RAW index is stale; rerun with --write")
            row_count = verify_index(index_path)
    except (ClosureError, OSError, ValueError, KeyError) as exc:
        return fail_closed(str(exc))

    result = {
        "stage": STAGE,
        "status": "PASS",
        "write_performed": args.write,
        "formal_arms": {
            arm: {
                "status": summaries[arm]["status"],
                "summary_sha256": file_sha256(FORMAL / arm / "RUN_SUMMARY.json"),
            }
            for arm in ARMS
        },
        "node164_manifest": str(manifest_path),
        "node164_manifest_sha256": file_sha256(manifest_path),
        "node164_manifest_entries": manifest_count,
        "raw_data_index": str(index_path),
        "raw_data_index_sha256": file_sha256(index_path),
        "raw_data_index_rows": row_count,
        "giant_trace_members_rehashed": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
