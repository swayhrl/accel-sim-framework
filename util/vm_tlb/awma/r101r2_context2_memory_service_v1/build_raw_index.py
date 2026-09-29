#!/usr/bin/env python3
"""Hash-close R101R2 CONTEXT2 raw evidence without re-reading trace payloads."""

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


STAGE = "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-r101r2-context2-memory-service-174-v1"
)
PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1"
)
TOOL_DIR = REPO / "util/vm_tlb/awma/r101r2_context2_memory_service_v1"
NODE_ROOT = Path(
    "/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1"
)
PRODUCER_ROOT = Path(
    "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/"
    "r101_transient_l2_sim_capture_20260927"
)
FULL5_PACK = REPO / (
    "docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1"
)
R101_PACK = REPO / (
    "docs/vm_tlb/review_packs/AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1"
)
R101R1_PACK = REPO / (
    "docs/vm_tlb/review_packs/AWMA_R101_L2_LIFETIME_CONTROL_V1R1"
)
FORMAL = NODE_ROOT / "raw/formal"
RUNTIME = NODE_ROOT / "runtime"
NODE_MANIFEST_NAME = "NODE164_EVIDENCE_SHA256SUMS"
INDEX_NAME = "RAW_DATA_INDEX.tsv"
ARMS = ("B0", "O2")
MODES = {"B0": "none", "O2": "oracle_1c"}
FORMAL_ARTIFACTS = (
    "command.json",
    "start_utc.txt",
    "end_utc.txt",
    "rc.txt",
    "wall_seconds.txt",
    "run.log",
    "run.stderr",
    "gpgpu_inst_stats.txt",
    "RUN_SUMMARY.json",
    "ORCHESTRATION_RECOVERY.json",
)
EXPECTED = {
    "coordination_commit": "8542a4d37372d586591ff9911929e523645e88f5",
    "full5_commit": "8da4057b3c168543603401b1b42a99b556d98042",
    "producer_commit": "bb902283b7ce9e1902b460383fbd3e0bedbd884d",
    "baseline_commit": "8d1f14a32f5538660d74da86ccb03a2c504c5735",
    "accepted_payload_sha256": (
        "1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234"
    ),
    "accepted_output_sha256": (
        "36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0"
    ),
    "source_admission_sha256": (
        "a6c66cb41c1ffb77f6af805534d47ccb8a8641dbe4aa3b206850be8e478f1e7a"
    ),
    "source_kernelslist_sha256": (
        "9fce012939496008814786a0c12d32c1f97a10c07c62cdd08f1fddcee5d86588"
    ),
    "source_sidecar_sha256": (
        "740820a195ae2bb9966a91b1e6d3423f4ded520bd91d1819aac8e78ce104b77d"
    ),
    "derivation_receipt": (
        "b560ee7a6947854f9123ce739af5befe788d2e17caa74292ca0a0b9a4597882d"
    ),
    "kernels_table": (
        "a9cf4bdbc3d551e9e7fc0d41b84a65e89d148085ea92940f04366c2e71704a65"
    ),
    "kernelslist": (
        "73f3d8c9546c06fb81aee209868c9e15e61b0bcfb900b5435c83d520e782748a"
    ),
    "sidecar": (
        "67adc56216f25bfc88c98d86aabdf1eeaae87e9f2f8e102f675d5be8ec11e7b5"
    ),
    "trace_aggregate": (
        "4fee01b73c9076378aeb583ea65254c5d3882c71ab2d0f2aeac857bc25edf2ce"
    ),
    "binary": "c43ff6c13c70300c52d2a5cee0611f900ef03d7332292a4227a80f0977b23705",
    "core_library": (
        "7ec99fdb6539d1daa7b499b19f5921d3e742255dcc59f971c2a39e5c1f64c05e"
    ),
    "core_patch": (
        "cfa2dcc9b9089f884bd1cb1f2d58526fb04f803ed81a8c1d7f6a265653edbc63"
    ),
    "framework": (
        "c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323"
    ),
    "config": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "trace_config": (
        "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b"
    ),
    "formal_runner": (
        "1b55fd7e325dd63496bdb45285bc3f10a63740e2a502873a6c9217aef3305158"
    ),
    "formal_summarizer": (
        "cb012f08d7f8ea1c099bb3c4b86e4a13e184ad28f5e2ce20df1c2a4aaa6f8949"
    ),
    "recovery_runner": (
        "bfcc4bf0e067dff0a97987ac4b8f7b3ac2637e740d7403a62b007dcc1b8363db"
    ),
    "recovery_summarizer": (
        "f3b0beb411f26329c3023f9af80a5a334b1847ba57986bd7936d2542e626a694"
    ),
    "recovery_finalizer": (
        "78dec875d6481ea75333955a55e19efc3c4c62f179c03e96707b84e28b7376bf"
    ),
}


class ClosureError(RuntimeError):
    """Fail-closed evidence validation error."""


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ClosureError(f"invalid JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def make_row(role: str, arm: str, artifact: str, path: Path, status: str,
             notes: str) -> Row:
    require(path.is_file(), f"missing evidence artifact: {path}")
    require(not path.is_symlink(), f"symlink must not be indexed directly: {path}")
    require(not any(char in notes for char in "\t\r\n"),
            f"notes are not TSV-safe: {notes!r}")
    return Row(role, arm, artifact, str(path.resolve()), path.stat().st_size,
               sha256(path), status, notes)


def regular_files(root: Path) -> Iterable[Path]:
    require(root.is_dir(), f"missing evidence directory: {root}")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_file():
            yield path


def validate_derived_input() -> dict[str, Any]:
    receipt_path = NODE_ROOT / "input/CONTEXT2_DERIVATION_RECEIPT.json"
    receipt = load_json(receipt_path)
    require(receipt.get("schema_version") ==
            "AWMA_R101R2_CONTEXT2_DERIVATION_RECEIPT_V1",
            "derived-input receipt schema drift")
    require(receipt.get("derived_input_identity") ==
            "R101_L512_NS_CONTEXT2_EXECORG_V1",
            "derived-input identity drift")
    authorities = receipt.get("authorities")
    require(isinstance(authorities, dict), "derived authorities missing")
    require(authorities.get("producer_commit") == EXPECTED["producer_commit"],
            "producer authority drift")
    require(authorities.get("coordination_handoff_commit") ==
            EXPECTED["coordination_commit"], "coordination authority drift")
    require(authorities.get("accepted_payload_sha256") ==
            EXPECTED["accepted_payload_sha256"], "accepted payload drift")
    require(authorities.get("accepted_output_sha256") ==
            EXPECTED["accepted_output_sha256"], "accepted output drift")
    require(authorities.get("source_admission_receipt_sha256") ==
            EXPECTED["source_admission_sha256"], "source admission drift")

    derived = receipt.get("derived_artifacts")
    require(isinstance(derived, dict), "derived artifact binding missing")
    paths = {
        "derivation_receipt": receipt_path,
        "kernels_table": NODE_ROOT / "input/CONTEXT2_KERNELS.tsv",
        "kernelslist": NODE_ROOT / "input/traces/kernelslist.g",
        "sidecar": NODE_ROOT / "input/transient_l2_runtime.tsv",
    }
    for key, path in paths.items():
        require(path.is_file() and not path.is_symlink(),
                f"small derived artifact missing/not regular: {path}")
        require(sha256(path) == EXPECTED[key], f"derived artifact hash drift: {key}")
    require(derived.get("kernels_table_sha256") == EXPECTED["kernels_table"],
            "receipt kernels-table binding drift")
    require(derived.get("kernelslist_sha256") == EXPECTED["kernelslist"],
            "receipt kernelslist binding drift")
    require(derived.get("runtime_sidecar_sha256") == EXPECTED["sidecar"],
            "receipt sidecar binding drift")

    selection = receipt.get("selection")
    require(isinstance(selection, list) and len(selection) == 6,
            "derived selection is not exactly six members")
    require([item.get("source_launch_index") for item in selection] ==
            list(range(3, 9)), "source launch selection is not exact 3..8")
    require([item.get("derived_ordinal") for item in selection] ==
            list(range(1, 7)), "derived ordinal sequence drift")
    binding = bytearray()
    symlinks = []
    for item in selection:
        name = item.get("member")
        claimed_hash = item.get("sha256")
        require(isinstance(name, str) and isinstance(claimed_hash, str),
                "derived selection member/hash malformed")
        link = NODE_ROOT / "input/traces" / name
        require(link.is_symlink(), f"derived trace is not a zero-copy symlink: {link}")
        require(link.resolve() == Path(item.get("source_realpath", "")).resolve(),
                f"derived trace target mismatch: {link}")
        require(item.get("samefile_with_accepted_reference") is True,
                f"derived samefile authority missing: {name}")
        binding.extend(f"{name}\t{claimed_hash}\n".encode())
        symlinks.append(str(link))
    aggregate = hashlib.sha256(binding).hexdigest()
    require(aggregate == EXPECTED["trace_aggregate"],
            "ordered six-member derivation binding drift")
    return {
        "receipt": receipt,
        "small_paths": paths,
        "trace_symlinks": symlinks,
        "ordered_trace_aggregate_sha256": aggregate,
    }


def validate_formal_recovery() -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    baseline: dict[str, Any] | None = None
    for arm in ARMS:
        run_dir = FORMAL / arm
        for name in FORMAL_ARTIFACTS:
            require((run_dir / name).is_file(), f"{arm}: missing formal artifact {name}")
        summary = load_json(run_dir / "RUN_SUMMARY.json")
        recovery = load_json(run_dir / "ORCHESTRATION_RECOVERY.json")
        require(summary.get("arm") == arm and summary.get("mode") == MODES[arm],
                f"{arm}: arm/mode mismatch")
        require(summary.get("status") == "PASS" and summary.get("rc") == 0,
                f"{arm}: summary is not PASS/rc0")
        require((run_dir / "rc.txt").read_text().strip() == "0",
                f"{arm}: durable rc.txt is not zero")
        require(summary.get("stderr_bytes") == 0 and
                (run_dir / "run.stderr").stat().st_size == 0,
                f"{arm}: simulator stderr is nonempty")
        gates = summary.get("gates")
        require(isinstance(gates, dict) and gates and
                all(type(value) is bool for value in gates.values()) and
                all(gates.values()), f"{arm}: not all recovered summary gates pass")
        coverage = summary.get("coverage")
        require(isinstance(coverage, dict) and coverage.get("kernels") == 6,
                f"{arm}: coverage is not 6 kernels")
        require(coverage.get("translated") == coverage.get("admissions") and
                coverage.get("translated_unique") == coverage.get("unique") and
                coverage.get("untranslated") == 0 and
                coverage.get("untranslated_unique") == 0 and
                coverage.get("unobserved") == 0,
                f"{arm}: coverage closure failed")
        drain = summary.get("drain")
        require(isinstance(drain, dict) and drain.get("gpu_active") == 0 and
                drain.get("l2_writeback_active") == 0 and
                drain.get("max_limit_hit") == 0 and
                drain.get("gpu_deadlock") == 0,
                f"{arm}: terminal drain failed")
        queues = summary.get("dram_latency_queues")
        require(isinstance(queues, list) and len(queues) == 8 and not any(queues),
                f"{arm}: DRAM latency queues are not empty")

        post = summary.get("POSTPROCESS_RECOVERY")
        require(isinstance(post, dict) and
                post.get("status") == "RECOVERED_FROM_FORMAL_POSTPROCESS_FAILURE" and
                post.get("simulator_rerun") is False and
                post.get("raw_command_log_rc_stderr_immutable") is True,
                f"{arm}: summary recovery boundary missing")
        require(recovery.get("status") == "PASS" and
                recovery.get("original_summarizer_outcome") ==
                "FAIL_CLOSED_BEFORE_RUN_SUMMARY_WRITE" and
                recovery.get("reason") ==
                "FORMAL_AT_RUN_SUMMARIZER_USED_ATOMIC_INFLIGHT_DIRECTORY_NAME_AS_ARM" and
                recovery.get("simulator_rerun") is False and
                recovery.get("simulator_rc") == 0 and
                recovery.get("simulator_stderr_bytes") == 0 and
                recovery.get("all_summary_gates_pass") is True and
                recovery.get("atomic_promote") is True,
                f"{arm}: orchestration recovery receipt invalid")
        require(recovery.get("formal_at_run", {}).get("runner_sha256") ==
                EXPECTED["formal_runner"] and
                recovery.get("formal_at_run", {}).get("summarizer_sha256") ==
                EXPECTED["formal_summarizer"],
                f"{arm}: formal-at-run tool authority drift")
        rec_tools = recovery.get("recovery", {})
        require(rec_tools.get("runner_sha256") == EXPECTED["recovery_runner"] and
                rec_tools.get("summarizer_sha256") ==
                EXPECTED["recovery_summarizer"] and
                rec_tools.get("finalizer_sha256") == EXPECTED["recovery_finalizer"],
                f"{arm}: recovery tool authority drift")
        require(recovery.get("run_summary_sha256") == sha256(run_dir / "RUN_SUMMARY.json"),
                f"{arm}: recovered summary hash mismatch")
        immutable = recovery.get("immutable_raw_artifacts")
        require(isinstance(immutable, dict) and
                set(immutable) == {"command.json", "rc.txt", "run.log", "run.stderr"},
                f"{arm}: immutable-raw receipt incomplete")
        for name, receipt in immutable.items():
            require(receipt.get("sha256_before") == receipt.get("sha256_after") ==
                    sha256(run_dir / name), f"{arm}: recovered raw hash changed: {name}")
            require(receipt.get("size_bytes_before") == receipt.get("size_bytes_after") ==
                    (run_dir / name).stat().st_size,
                    f"{arm}: recovered raw size changed: {name}")
        require(summary.get("artifact_receipt", {}).get("binary") == EXPECTED["binary"],
                f"{arm}: binary authority drift")
        require(summary.get("ordered_trace_aggregate_sha256") ==
                EXPECTED["trace_aggregate"], f"{arm}: trace binding drift")
        if baseline is None:
            baseline = summary
        else:
            matched_context_fields = (
                "total_cycles", "total_instructions", "total_ctas",
                "l1d_core_rows", "l1d_accesses", "l1d_misses",
                "l1d_reservation_fails", "l2_accesses", "l2_misses",
                "l2_reservation_fails", "dram_rows", "dram_n_rd",
                "dram_n_rd_l2_a", "dram_n_write", "dram_n_wr_bk",
            )
            base_context = baseline.get("context_end_snapshot", {})
            arm_context = summary.get("context_end_snapshot", {})
            require(summary.get("instructions") == baseline.get("instructions") and
                    summary.get("ctas") == baseline.get("ctas") and
                    all(arm_context.get(key) == base_context.get(key)
                        for key in matched_context_fields) and
                    summary.get("gates", {}).get("context_snapshot_exact") is True and
                    summary.get("coverage_uid_identity") ==
                    baseline.get("coverage_uid_identity") and
                    summary.get("artifact_receipt") == baseline.get("artifact_receipt"),
                    f"{arm}: cross-arm context/identity mismatch")
        summaries[arm] = summary
    return summaries


def validate_smokes_and_regressions() -> None:
    smoke_root = NODE_ROOT / "raw/smoke"
    expected = {"default_off", "explicit_none", "oracle_positive"}
    actual = {path.name for path in smoke_root.iterdir() if path.is_dir()}
    require(actual == expected, f"smoke arm set mismatch: {actual}")
    for arm in sorted(expected):
        root = smoke_root / arm
        receipt = load_json(root / "OFF_EQUIVALENCE.json")
        require(receipt.get("status") == "PASS" and receipt.get("rc") == 0,
                f"smoke {arm} did not PASS")
        require((root / "rc.txt").read_text().strip() == "0" and
                (root / "run.stderr").stat().st_size == 0,
                f"smoke {arm} raw rc/stderr failed")
        require(receipt.get("run_log_sha256") == sha256(root / "run.log"),
                f"smoke {arm} run-log hash mismatch")
    regressions = NODE_ROOT / "raw/regressions"
    required_logs = {
        "awma_transient_l2_policy_test.log": "AWMA_TRANSIENT_L2_POLICY_TEST_PASS",
        "o2_directed_and_hooks.log": "AWMA_R101R2_O2_INTEGRATION_HOOKS PASS",
        "vm_c10b_runtime_validation_test.log": "vm_c10b_runtime_validation_test PASS",
        "vm_m2_rf_pending_retry_test.log": "vm_m2_rf_pending_retry_test PASS",
        "vm_m3_g3_4b_tlb_timing_test.log": "vm_m3_g3_4b_tlb_timing_test PASS",
    }
    for name, marker in required_logs.items():
        path = regressions / name
        require(path.is_file() and marker in path.read_text(),
                f"regression marker missing: {name}")


def frozen_paths() -> dict[str, Path]:
    return {
        "binary": RUNTIME / "bin/unified_accel-sim.out",
        "core_library": RUNTIME / "lib/gcc-11.4.0/cuda-12040/release/libcudart.so",
        "core_patch": PACK / "O2_CORE.patch",
        "framework": REPO / "gpu-simulator/accel-sim.cc",
        "config": REPO / "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config",
        "trace_config": REPO / (
            "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
        ),
    }


def validate_frozen() -> None:
    for key, path in frozen_paths().items():
        require(path.is_file(), f"missing frozen artifact: {path}")
        require(sha256(path) == EXPECTED[key], f"frozen hash drift: {key}")
    require(sha256(RUNTIME / "O2_CORE.patch") == EXPECTED["core_patch"],
            "node164 runtime patch differs from review-pack patch")
    current_tools = {
        "run_context2_matrix.py": EXPECTED["recovery_runner"],
        "summarize_context2_run.py": EXPECTED["recovery_summarizer"],
        "finalize_context2_results.py": EXPECTED["recovery_finalizer"],
    }
    for name, expected_hash in current_tools.items():
        require(sha256(TOOL_DIR / name) == expected_hash,
                f"current recovery tool drift: {name}")


def node_files() -> list[Path]:
    files = [
        NODE_ROOT / "input/CONTEXT2_DERIVATION_RECEIPT.json",
        NODE_ROOT / "input/CONTEXT2_KERNELS.tsv",
        NODE_ROOT / "input/transient_l2_runtime.tsv",
        NODE_ROOT / "input/traces/kernelslist.g",
    ]
    for root in (NODE_ROOT / "raw/formal", NODE_ROOT / "raw/smoke",
                 NODE_ROOT / "raw/regressions"):
        files.extend(regular_files(root))
    files.extend((
        RUNTIME / "O2_CORE.patch",
        RUNTIME / "bin/unified_accel-sim.out",
        RUNTIME / "lib/gcc-11.4.0/cuda-12040/release/libcudart.so",
        RUNTIME / "unified_build.log",
    ))
    result = sorted(set(path.resolve() for path in files))
    for path in result:
        require(path.is_file() and not path.is_symlink(),
                f"node164 evidence path invalid: {path}")
    return result


def classify_node(path: Path) -> tuple[str, str, str, str]:
    relative = path.relative_to(NODE_ROOT).as_posix()
    parts = relative.split("/")
    if relative.startswith("input/"):
        return ("DERIVED_INPUT", "R101_L512_NS_CONTEXT2_EXECORG_V1", "PASS",
                "small receipt/table/sidecar/kernelslist; six trace symlinks excluded")
    if relative.startswith("raw/formal/"):
        arm = parts[2]
        require(arm in ARMS, f"unexpected formal arm path: {relative}")
        artifact = parts[-1]
        status = ("PASS_RECOVERED_POSTPROCESS_ONLY" if artifact in
                  {"RUN_SUMMARY.json", "ORCHESTRATION_RECOVERY.json"}
                  else "PASS_RAW_IMMUTABLE_RECOVERED_POSTPROCESS_ONLY")
        return (
            "FORMAL_PRIMARY_RECOVERED_POSTPROCESS_ONLY",
            arm,
            status,
            "formal-at-run summarizer failed on in-flight dirname; raw unchanged; no simulator rerun",
        )
    if relative.startswith("raw/smoke/"):
        return ("SMOKE_QUALIFICATION", parts[2], "PASS_EXCLUDED_FROM_FORMAL",
                "default-off/explicit-none/oracle-positive engineering smoke")
    if relative.startswith("raw/regressions/"):
        return ("REGRESSION_QUALIFICATION", "POST_IMPLEMENTATION", "PASS",
                "directed/integration/accepted regression evidence")
    if relative.startswith("runtime/"):
        return ("FROZEN_RUNTIME", "B0_O2_FORMAL", "FROZEN",
                "node164 runtime/build artifact used by recovered formal arms")
    raise ClosureError(f"unclassified node164 path: {relative}")


def manifest_text(paths: list[Path]) -> str:
    return "".join(
        f"{sha256(path)}  {path.relative_to(NODE_ROOT).as_posix()}\n"
        for path in paths
    )


def verify_manifest(path: Path) -> int:
    count = 0
    seen: set[str] = set()
    for number, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split("  ", 1)
        require(len(parts) == 2 and len(parts[0]) == 64,
                f"manifest line malformed: {number}")
        expected, relative = parts
        require(relative not in seen, f"manifest duplicate path: {relative}")
        seen.add(relative)
        artifact = NODE_ROOT / relative
        require(artifact.is_file() and not artifact.is_symlink(),
                f"manifest artifact invalid: {artifact}")
        require(sha256(artifact) == expected, f"manifest hash mismatch: {artifact}")
        count += 1
    require(count > 0, "node164 evidence manifest is empty")
    return count


def authority_rows() -> list[Row]:
    rows: list[Row] = []
    producer_pack = PRODUCER_ROOT / "review_pack"
    for name in (
        "ACCEPTED_INPUT_BINDING.json", "SIM_CAPTURE_MANIFEST.json",
        "TRACE_MEMBER_MANIFEST.tsv", "RAW_DATA_INDEX.tsv", "SHA256SUMS",
        "TRANSFER_RECEIPT.md",
    ):
        note = "accepted producer authority; six selected traces referenced by derivation binding"
        if name == "ACCEPTED_INPUT_BINDING.json":
            note += (f"; payload={EXPECTED['accepted_payload_sha256']}; "
                     f"output={EXPECTED['accepted_output_sha256']}")
        rows.append(make_row("PRODUCER_AUTHORITY_REFERENCE",
                             EXPECTED["producer_commit"], name,
                             producer_pack / name, "ACCEPTED_REFERENCE", note))
    rows.append(make_row(
        "PRODUCER_AUTHORITY_REFERENCE", EXPECTED["producer_commit"],
        "NODE164_SHA256SUMS", PRODUCER_ROOT / "NODE164_SHA256SUMS",
        "ACCEPTED_REFERENCE", "producer manifest file only; trace payloads not rehashed",
    ))

    source_input = Path(
        "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/input"
    )
    source_small = (
        ("ADMISSION_RECEIPT.json", source_input / "ADMISSION_RECEIPT.json",
         EXPECTED["source_admission_sha256"]),
        ("SOURCE_KERNELSLIST.g", source_input / "traces/kernelslist.g",
         EXPECTED["source_kernelslist_sha256"]),
        ("SOURCE_RUNTIME_SIDECAR.tsv", source_input / "transient_l2_runtime.tsv",
         EXPECTED["source_sidecar_sha256"]),
    )
    for name, path, expected_hash in source_small:
        require(sha256(path) == expected_hash, f"accepted FULL5 source input drift: {name}")
        rows.append(make_row(
            "ACCEPTED_FULL5_INPUT_REFERENCE", EXPECTED["full5_commit"], name,
            path, "ACCEPTED_REFERENCE",
            "small source input authority used by deterministic CONTEXT2 derivation",
        ))

    for name in ("FINAL_DECISION.md", "RUN_RECEIPTS.json", "RAW_DATA_INDEX.tsv",
                 "SHA256SUMS"):
        rows.append(make_row(
            "ACCEPTED_FULL5_AUTHORITY", EXPECTED["full5_commit"], name,
            FULL5_PACK / name, "ACCEPTED_REFERENCE",
            "accepted FULL5 traffic-response/no-cycle-gain authority",
        ))
    for name in ("R101_SOURCE_RECEIPT.json", "R101_INPUT_RECEIPT.json",
                 "R101_DECISION.md", "RAW_DATA_INDEX.tsv", "SHA256SUMS"):
        rows.append(make_row(
            "ACCEPTED_R101_NATIVE_AUTHORITY", "cfbe6503585fa1b10d979db5d26fb9be3a80e563",
            name, R101_PACK / name, "ACCEPTED_REFERENCE",
            "accepted R101 Native structural/scientific authority",
        ))
    for name in ("FINAL_DECISION.md", "R101_INHERITANCE.md", "RAW_DATA_INDEX.tsv",
                 "SHA256SUMS"):
        rows.append(make_row(
            "ACCEPTED_R101R1_NATIVE_AUTHORITY", "422faf4d8fcdb5ac49068dcf19a6e783954a29a8",
            name, R101R1_PACK / name, "ACCEPTED_REFERENCE",
            "accepted R101R1 Native lifetime-control authority",
        ))
    return rows


def build_rows(paths: list[Path], manifest_path: Path, builder: Path) -> list[Row]:
    rows = authority_rows()
    for path in paths:
        role, arm, status, note = classify_node(path)
        rows.append(make_row(role, arm, path.relative_to(NODE_ROOT).as_posix(),
                             path, status, note))
    rows.append(make_row(
        "NODE164_EVIDENCE_MANIFEST", "B0_O2_RECOVERED_AND_QUALIFICATION",
        NODE_MANIFEST_NAME, manifest_path, "PASS",
        "atomic manifest; immediate equivalent sha256sum verification; trace symlinks excluded",
    ))

    # Binary and Core library are already indexed from the node164 runtime
    # subtree above; add only repository-resident source/config authorities.
    for key, path in frozen_paths().items():
        if key in {"binary", "core_library"}:
            continue
        rows.append(make_row(
            "FROZEN_SOURCE_OR_CONFIG", "B0_O2_FORMAL", path.name, path, "FROZEN",
            f"frozen {key} authority for recovered formal matrix",
        ))

    tool_files = sorted(
        path for path in TOOL_DIR.iterdir()
        if path.is_file() and not path.is_symlink()
    )
    require(builder in tool_files, "raw-index builder absent from tool inventory")
    for path in tool_files:
        rows.append(make_row(
            "STAGE_TOOL", "R101R2_CONTEXT2", path.name, path, "FROZEN",
            "new isolated R101R2 derivation/build/test/run/recovery/finalization tool",
        ))

    derived = sorted(
        path for path in PACK.iterdir()
        if path.is_file() and path.suffix in {".tsv", ".json"}
        and path.name != INDEX_NAME
    )
    require(derived, "no derived result TSV/JSON files found")
    for path in derived:
        rows.append(make_row(
            "DERIVED_RESULT", "B0_O2_CONTEXT2", path.name, path, "PASS",
            "derived from accepted input or validated recovered formal summaries",
        ))

    indexed = [item.path for item in rows]
    require(len(indexed) == len(set(indexed)), "RAW index contains duplicate paths")
    return rows


def rows_tsv(rows: list[Row]) -> str:
    output = io.StringIO()
    fields = list(Row.__dataclass_fields__)
    writer = csv.DictWriter(output, fields, delimiter="\t", lineterminator="\n")
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
        artifact = Path(item["path"])
        require(item["path"] not in seen, f"duplicate index path at line {number}")
        seen.add(item["path"])
        require(artifact.is_absolute() and artifact.is_file() and not artifact.is_symlink(),
                f"invalid index path at line {number}: {artifact}")
        require(int(item["size_bytes"]) == artifact.stat().st_size,
                f"size mismatch at line {number}: {artifact}")
        require(item["sha256"] == sha256(artifact),
                f"hash mismatch at line {number}: {artifact}")
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
    args = parser.parse_args()
    manifest_path = NODE_ROOT / NODE_MANIFEST_NAME
    index_path = PACK / INDEX_NAME
    builder = Path(__file__).resolve()
    try:
        derived = validate_derived_input()
        summaries = validate_formal_recovery()
        validate_smokes_and_regressions()
        validate_frozen()
        paths = node_files()
        for path in paths:
            classify_node(path)
        # Preflight every non-manifest row before the first permitted write.
        authority_rows()
        require(builder.is_file(), "builder source missing")
        require(all(path.is_file() for path in TOOL_DIR.iterdir()
                    if path.name != "__pycache__"), "tool inventory contains invalid entry")
        manifest = manifest_text(paths)
        if args.write:
            atomic_write(manifest_path, manifest)
            manifest_count = verify_manifest(manifest_path)
        else:
            require(manifest_path.is_file(), "--write required: node164 manifest missing")
            require(manifest_path.read_text() == manifest,
                    "node164 manifest stale; rerun with --write")
            manifest_count = verify_manifest(manifest_path)
        rows = build_rows(paths, manifest_path, builder)
        index = rows_tsv(rows)
        if args.write:
            atomic_write(index_path, index)
            row_count = verify_index(index_path)
        else:
            require(index_path.is_file(), "--write required: RAW index missing")
            require(index_path.read_text() == index,
                    "RAW index stale; rerun with --write")
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
                "evidence_class": "RECOVERED_POSTPROCESS_ONLY",
                "summary_sha256": sha256(FORMAL / arm / "RUN_SUMMARY.json"),
            }
            for arm in ARMS
        },
        "derived_input": {
            "identity": "R101_L512_NS_CONTEXT2_EXECORG_V1",
            "ordered_trace_aggregate_sha256": (
                derived["ordered_trace_aggregate_sha256"]
            ),
            "trace_symlink_count": len(derived["trace_symlinks"]),
            "trace_payloads_rehashed": False,
        },
        "node164_manifest": str(manifest_path),
        "node164_manifest_sha256": sha256(manifest_path),
        "node164_manifest_entries": manifest_count,
        "raw_data_index": str(index_path),
        "raw_data_index_sha256": sha256(index_path),
        "raw_data_index_rows": row_count,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
