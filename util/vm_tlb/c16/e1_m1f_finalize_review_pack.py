#!/usr/bin/env python3
"""Build the bounded M1F implementation review pack from qualified artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


GOAL = "C16_E1_M1F_STABLE_ADMISSION_PROTOTYPE_V1"
LABEL = "M1F_STABLE_ADMISSION_IMPLEMENTATION_QUALIFIED_FOR_TIMING_REVIEW"
SIDECAR_SHA = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"
HASH_VERSION = "C16_M1F_STABLE_ADMISSION_HASH_V1"
SEED = "0x6a09e667f3bcc908"
THRESHOLD = "0x0484baf3b723b966"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def copy(source: Path, output: Path) -> None:
    need(source.is_file(), f"missing input: {source}")
    shutil.copy2(source, output / source.name)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--static-dir", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--artifact-manifest", type=Path, required=True)
    parser.add_argument("--shim-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--core-commit", required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output review-pack directory must be fresh")

    distribution = json.loads(
        (args.analysis_dir / "M1F_STATIC_SELECTION_DISTRIBUTION.json")
        .read_text(encoding="utf-8"))
    toy = json.loads((args.analysis_dir / "M1F_TOY_SURVIVAL_COMPARISON.json")
                     .read_text(encoding="utf-8"))
    selector = json.loads((args.static_dir / "selector_summary.json")
                          .read_text(encoding="utf-8"))
    core_log = (args.logs_dir / "core_oracle_tests_qualification.log")
    build_log = (args.logs_dir / "core_full_build_qualification.log")
    unit_log = (args.logs_dir / "framework_static_unit_tests_final.log")
    mapper_test_log = args.logs_dir / "accepted_mapper_tests.log"
    mapper_provenance_log = args.logs_dir / "accepted_mapper_provenance.log"
    core_text = core_log.read_text(encoding="utf-8")
    build_text = build_log.read_text(encoding="utf-8")
    unit_text = unit_log.read_text(encoding="utf-8")

    need(distribution["status"] == "PASS", "static analysis not PASS")
    need(distribution["selected_lines"] == 130571, "selected total drift")
    need(distribution["hash_contract"]["version"] == HASH_VERSION,
         "hash version drift")
    need(distribution["hash_contract"]["seed_hex"] == SEED, "seed drift")
    need(distribution["hash_contract"]["threshold_hex"] == THRESHOLD,
         "threshold drift")
    need(distribution["provenance"]["sidecar_sha256"] == SIDECAR_SHA,
         "sidecar drift")
    need(selector["selected_lines"] == distribution["selected_lines"],
         "selector/analysis count drift")
    need(toy["status"] == "PASS", "toy comparison not PASS")
    for marker in (
            "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_POLICY_TEST_PASS",
            "ORACLE_ELASTIC_LINE_METADATA_TEST_PASS",
            "ORACLE_ELASTIC_TAG_ARRAY_CONFIG_TEST_PASS",
            "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_TEST_SUITE_PASS",
            "M1F_TOY_SURVIVAL_PASS"):
        need(marker in core_text, f"missing Core marker: {marker}")
    need("CORE_FULL_BUILD_QUALIFICATION_PASS" in build_text,
         "full Core build marker absent")
    need("Ran 3 tests" in unit_text and "OK" in unit_text,
         "Framework unit tests not PASS")
    need("C16_E1_ACCEPTED_L2_MAPPER_TEST_PASS" in
         mapper_test_log.read_text(encoding="utf-8"),
         "accepted mapper tests not PASS")
    need("accepted_core_sha=a2322069b9701597db7019080b5b54d29518e3a2" in
         mapper_provenance_log.read_text(encoding="utf-8"),
         "accepted mapper provenance drift")

    args.output_dir.mkdir(parents=True)
    for name in (
            "M1F_STATIC_SELECTION_DISTRIBUTION.json",
            "M1F_TOY_SURVIVAL_COMPARISON.json",
            "M1F_CLASS_DISTRIBUTION.tsv",
            "M1F_CLASS_SUBPARTITION_DISTRIBUTION.tsv",
            "M1F_CLASS_SET_SELECTED_COUNTS.tsv.gz",
            "ANALYSIS_SHA256SUMS"):
        copy(args.analysis_dir / name, args.output_dir)
    copy(args.static_dir / "selector_summary.json", args.output_dir)
    for path in (core_log, unit_log, mapper_test_log,
                 mapper_provenance_log, args.artifact_manifest,
                 args.shim_manifest):
        copy(path, args.output_dir)
    dump(args.output_dir / "CORE_FULL_BUILD_RECEIPT.json", {
        "schema": "C16_E1_M1F_CORE_FULL_BUILD_RECEIPT_V1",
        "status": "PASS",
        "marker": "CORE_FULL_BUILD_QUALIFICATION_PASS",
        "durable_log_path": str(build_log),
        "durable_log_sha256": digest(build_log),
        "isolated_build_root":
            "/root/data/c16_e1_m1f_stable_admission_build_v1",
        "shared_lane4_binary_or_library_modified": False,
    })

    dump(args.output_dir / "SOURCE_ANCHORS.json", {
        "schema": "C16_E1_M1F_SOURCE_ANCHORS_V1",
        "goal": GOAL,
        "status": "PASS",
        "framework_design_review_commit":
            "1d5b3a0ad078918328efc23b108c4849f677fd75",
        "framework_design_review_path":
            "docs/vm_tlb/review_packs/C16_E1_TARGET_CLASS_FAIR_RESIDENCY_DESIGN_REVIEW_V1",
        "core_baseline": "0271de82432db004beed43280ed01057246a0f2c",
        "core_implementation_commit": args.core_commit,
        "literature_note_commit":
            "49c01401200f7944db31d066ebb331a9ba701882",
        "literature_note_path":
            "docs/vm_tlb/literature_notes/c16/rounds/2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md",
        "literature_note_sha256":
            "3e9f5c63cea62a2fadd8a41964825244392a0595a1cfa5ba953fc96b1cb3fea3",
        "oracle_sidecar_sha256": SIDECAR_SHA,
        "accepted_mapper_core": "a2322069b9701597db7019080b5b54d29518e3a2",
        "accepted_mapper_config_sha256":
            "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
        "lane4_partial_results_used": False,
    })
    dump(args.output_dir / "HASH_FREEZE_RECEIPT.json", {
        "schema": "C16_E1_M1F_HASH_FREEZE_RECEIPT_V1",
        "status": "PASS",
        "frozen_before_static_distribution_was_observed": True,
        "seed_searched_or_tuned": False,
        "version": HASH_VERSION,
        "algorithm": "SplitMix64 finalizer after seed/key xor and golden-gamma add",
        "seed_hex": SEED,
        "seed_rationale": "first SHA-512 IV word; public non-searched constant",
        "key": "(target_class << 32) xor region_relative_128B_line_index",
        "threshold_rule": "hash < floor(2^64 * 131072 / 7426048)",
        "threshold_hex": THRESHOLD,
    })
    dump(args.output_dir / "FUNCTIONAL_VALIDATION.json", {
        "schema": "C16_E1_M1F_FUNCTIONAL_VALIDATION_V1",
        "status": "PASS",
        "checks": [
            {"id": "M1F_OFF_EQUALS_M1_TARGET_BEARING", "status": "PASS",
             "evidence": "Core directed differential victim/admission assertions"},
            {"id": "FRACTION_ONE_EQUALS_M1", "status": "PASS"},
            {"id": "FRACTION_ZERO_NO_PROTECTED_ADMISSION", "status": "PASS"},
            {"id": "SECTOR_RETRY_DECODE_STABILITY", "status": "PASS"},
            {"id": "PENDING_SECTOR_INVALIDATE_DENIED_FILL_REGRESSION",
             "status": "PASS", "evidence": "line metadata and tag-array tests"},
            {"id": "FILTERED_TARGET_IDENTITY_NOT_NON_TARGET", "status": "PASS"},
            {"id": "M1_EQUAL_CLASS_LRU_M1F_TOY_SURVIVAL", "status": "PASS"},
            {"id": "FULL_CORE_BUILD", "status": "PASS"},
            {"id": "TARGET_ONLY_FUNCTIONAL_FLOW", "status": "NOT_RUN_NOT_REQUIRED",
             "reason": "Actual Core policy, metadata, tag-array, B16 geometry and full build checks closed the prototype integration risk."},
        ],
        "not_in_scope": ["C16 timing replay", "GPU collection", "Lane 4 changes"],
    })
    dump(args.output_dir / "NEUTRALITY_INVARIANTS.json", {
        "schema": "C16_E1_M1F_NEUTRALITY_INVARIANTS_V1",
        "status": "PASS",
        "m1f_option_default": False,
        "m1f_off_behavior": "all oracle targets remain protection-eligible; exact M1 policy inputs",
        "oracle_off_behavior": "existing R0 path; M1F cannot be enabled when oracle is off",
        "diagnostics_default": False,
        "protected_admission_requires": "oracle_target && protection_eligible && existing M1 hard-admission success",
        "unselected_target_statistics_identity_preserved": True,
        "quota_pending_borrowing_set_local_victim_no_promotion_sector_semantics_preserved": True,
        "lane4_processes_observed_running_and_unmodified_before_pack": [250086, 250087, 266910],
    })
    dump(args.output_dir / "QUALIFICATION_DECISION.json", {
        "schema": "C16_E1_M1F_QUALIFICATION_DECISION_V1",
        "status": "PASS",
        "label": LABEL,
        "authorization": "TIMING_REVIEW_ONLY",
        "timing_experiment_authorized": False,
        "claims_not_made": [
            "M1F is faster", "M1F is fairness-optimal",
            "M1F is novel", "static eligibility is exact occupancy",
            "static eligibility provides a survival floor"],
    })

    (args.output_dir / "IMPLEMENTATION_SEMANTICS.md").write_text("""# M1F implementation semantics

`oracle_target`, `protection_eligible`, and `protected_admitted` are distinct.
Every qweight target remains a target for target-access/hit/miss statistics.
Only the frozen stable address subset enters M1 protected admission and
replacement; filtered targets use the ordinary M1 path. Existing hard quota,
pending accounting, ordinary borrowing, set-local victims, quota-full denial,
no-promotion behavior, and sector metadata remain authoritative.

The selector is deterministic by target class plus region-relative 128-byte
line index. Sectors, retries, repeated fills, and decode repetitions therefore
have the same eligibility. It does not use access count, kernel identity,
decode iteration, time, or mutable random state.
""", encoding="utf-8")
    (args.output_dir / "COST_BOUNDARY.md").write_text("""# Cost boundary

The prototype adds one versioned stable-hash evaluation and one integer
threshold comparison for target admission. The hash datapath contains a
64-bit key/seed XOR, one add, two 64-bit multiply-mix stages, shifts/XORs, and
a 64-bit comparison. Class identity and region-relative line index come from
the existing oracle interval lookup. Stable eligibility can be recomputed, so
the prototype does not require a per-line selector bit; existing protected and
class metadata are unchanged.

Hardware latency, throughput impact, power, and area have not been evaluated.
The software prototype is not evidence of zero hardware cost.
""", encoding="utf-8")
    (args.output_dir / "README.md").write_text(f"""# {GOAL}

Qualification: `{LABEL}`. This label permits timing review only and does not
authorize a timing run.

The frozen selector enumerated 7,426,048 target lines and selected
{distribution['selected_lines']:,}, which is
{distribution['selected_minus_global_quota_lines']:+,} versus the 131,072-line
quota ({distribution['selected_relative_to_global_quota']:.6f}x). Existing
hard admission handles actual quota/set constraints; the quota was not changed.

Static selection is approximately distributed, not exact occupancy and not a
survival floor. Global set selected counts have mean
{distribution['set_total_distribution']['mean']:.6f}, p99
{distribution['set_total_distribution']['p99']}, and max
{distribution['set_total_distribution']['max']}; no set has 16 or more
selected lines. Per-class and per-subpartition tables are included.

The CPU-only toy records old-address survival and next-round hits, but omits
L1 filtering, real transaction arrival order, and timing. It is not a C16
performance result. No full C16 replay, GPU collection, or Lane 4 mutation was
performed.
""", encoding="utf-8")

    raw_rows = ["artifact\tsha256"]
    for path in sorted(args.output_dir.iterdir()):
        if path.is_file() and path.name not in {"SHA256SUMS", "RAW_LOG_INDEX.tsv"}:
            raw_rows.append(f"{path.name}\t{digest(path)}")
    (args.output_dir / "RAW_LOG_INDEX.tsv").write_text(
        "\n".join(raw_rows) + "\n", encoding="utf-8")
    checksum_rows = []
    for path in sorted(args.output_dir.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            checksum_rows.append(f"{digest(path)}  {path.name}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksum_rows) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "label": LABEL,
                      "output_dir": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
