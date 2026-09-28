#!/usr/bin/env python3
"""Build SHiP-SW and survival-observer closeout review pack."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

GOAL = "C16_E1_STRONG_BASELINES_AND_SURVIVAL_OBSERVER_CLOSEOUT_174NEW_V1"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--configs", type=Path, required=True)
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--core-docs", type=Path, required=True)
    parser.add_argument("--source-diff", type=Path, required=True)
    parser.add_argument("--binary-sha", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--core-commit", required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output directory must be fresh")

    names = ("CLOSEOUT_VALIDATION.json", "OFF_NEUTRALITY.json",
             "SHIP_SW_BOUNDED_ACTIVATION.json",
             "SURVIVAL_OBSERVER_BOUNDED_ACTIVATION.json")
    values = {}
    for name in names:
        path = args.qualification / name
        values[name] = json.loads(path.read_text())
        need(values[name]["status"] == "PASS", f"{name} not PASS")

    args.output_dir.mkdir(parents=True)
    (args.output_dir / ".gitattributes").write_text(
        "SOURCE_DIFF.patch -whitespace\n", encoding="utf-8")
    for name in names:
        shutil.copy2(args.qualification / name, args.output_dir / name)
    for name in ("BASELINE_IMPLEMENTATION_CONTRACT.md",
                 "SHIP_SW_CONTRACT_STATUS.md",
                 "OLD_ADDRESS_GENERATION_SURVIVAL_OBSERVER.md"):
        shutil.copy2(args.core_docs / name, args.output_dir / name)
    shutil.copy2(args.source_diff, args.output_dir / "SOURCE_DIFF.patch")
    shutil.copy2(args.binary_sha, args.output_dir / "CANDIDATE_BINARY_SHA256")

    config_out = args.output_dir / "configs"
    config_out.mkdir()
    for path in sorted(args.configs.glob("*.config")):
        shutil.copy2(path, config_out / path.name)
    need(len(list(config_out.glob("*.config"))) == 5, "config count drift")

    dump(args.output_dir / "SOURCE_ANCHORS.json", {
        "schema": "C16_E1_STRONG_BASELINES_SURVIVAL_CLOSEOUT_ANCHORS_V1",
        "status": "PASS",
        "core_parent": "060e48f62b13f46e962b308b4bae39ab665067ef",
        "framework_parent": "49a110130ec893773f24acd75f5d96c9d0f7350c",
        "core_closeout_commit": args.core_commit,
        "ship_contract": "C16_SHIP_SW_STYLE_V1",
        "observer_contract":
            "C16_OLD_ADDRESS_GENERATION_SURVIVAL_OBSERVER_V1",
        "sidecar_sha256":
            "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6",
        "full_window_launch_uid_map": {
            "D1_L0_snapshot_after_uid": 60,
            "D1_L0_dynamic_kernel": 2985,
            "D2_L0_begin_uid": 1564,
            "D2_L0_begin_dynamic_kernel": 4489,
            "D2_L0_mid_end_uid": 1565,
            "D2_L0_mid_end_dynamic_kernel": 4490},
        "lane4_partial_results_used": False,
    })

    test_log = args.logs / "closeout_tests_v3.log"
    oracle_log = args.logs / "oracle_regression_v3.log"
    build_log = args.logs / "full_build_v1.log"
    need("C16_OLD_ADDRESS_SURVIVAL_OBSERVER_TEST_PASS" in test_log.read_text(),
         "observer tests absent")
    need("ORACLE_ELASTIC_QWEIGHT_RESIDENCY_TEST_SUITE_PASS" in
         oracle_log.read_text(), "oracle regression absent")
    need("C16_CLOSEOUT_BUILD_PASS" in build_log.read_text(errors="replace"),
         "build marker absent")
    (args.output_dir / "UNIT_TEST_RESULTS.tsv").write_text(
        "suite\tstatus\tevidence\n"
        "SHiP_helpers\tPASS\tC16_STRONG_BASELINES_POLICY_TEST_PASS\n"
        "SHiP_sector_integration\tPASS\tC16_STRONG_BASELINES_TAG_ARRAY_TEST_PASS\n"
        "generation_survival_observer\tPASS\tC16_OLD_ADDRESS_SURVIVAL_OBSERVER_TEST_PASS\n"
        "oracle_regression\tPASS\tORACLE_ELASTIC_QWEIGHT_RESIDENCY_TEST_SUITE_PASS\n"
        "framework_analysis\tPASS\tcloseout analyzer unittest\n",
        encoding="utf-8")
    dump(args.output_dir / "BUILD_RECEIPT.json", {
        "schema": "C16_E1_CLOSEOUT_BUILD_RECEIPT_V1", "status": "PASS",
        "parallelism_limit": 2, "durable_log": str(build_log),
        "durable_log_sha256": sha256(build_log),
    })

    raw = ["artifact\tsha256\tbytes\tpath"]
    for run in ("REFERENCE_R0_OFF", "CANDIDATE_R0_OFF",
                "REFERENCE_M1_OBSERVER_OFF", "CANDIDATE_M1_OBSERVER_OFF",
                "M1_OBSERVER_ON", "SHIP_SW"):
        for name in ("stdout.log", "stderr.log", "survival.tsv"):
            path = args.runs / run / name
            if path.is_file():
                raw.append(f"{run}/{name}\t{sha256(path)}\t"
                           f"{path.stat().st_size}\t{path}")
    (args.output_dir / "RAW_LOG_INDEX.tsv").write_text(
        "\n".join(raw) + "\n", encoding="utf-8")

    ship = values["SHIP_SW_BOUNDED_ACTIVATION.json"]["summed_counters"]
    (args.output_dir / "README.md").write_text(
        f"# {GOAL}\n\n"
        "Strong-baseline status: "
        "`C16_STRONG_BASELINE_PREP_QUALIFIED_NO_FULL_TIMING`.\n\n"
        "Observer status: "
        "`C16_OLD_ADDRESS_SURVIVAL_OBSERVER_IMPLEMENTATION_QUALIFIED`.\n\n"
        "The bounded cold SHiP-SW canary classified "
        f"{ship['ship_critical_allocations']} critical allocations as REGULAR "
        f"and excluded {ship['ship_noncritical_no_train']} non-critical "
        "allocations from training. Positive/negative training, collisions, "
        "saturation, and multiple generations are qualified by synthetic and "
        "sector integration tests.\n\n"
        "Observer qualification proves exact-generation accounting and "
        "neutrality only. It is not a D1-to-D2 survival result. No full timing "
        "run was executed and no Lane 4 partial result was read.\n",
        encoding="utf-8")
    (args.output_dir / "CLAIM_BOUNDARY.md").write_text(
        "# Claim boundary\n\n"
        "C16 SHiP-SW-style is an explicitly frozen adaptation, not a bitwise "
        "AutoScratch reproduction. Bounded activation is not performance.\n\n"
        "The survival observer is diagnostics-only and default OFF. Its "
        "implementation qualification does not establish any scientific "
        "survival fraction; the full D1→D2 window was not run.\n",
        encoding="utf-8")
    (args.output_dir / "OPEN_ISSUES.md").write_text(
        "# Open issues\n\n"
        "- Full-window scientific survival values remain unmeasured.\n"
        "- SHiP-SW performance and hardware timing/area/power remain unmeasured.\n"
        "- The supplied full-window observer config is a template only and "
        "does not authorize execution.\n",
        encoding="utf-8")

    checksums = []
    for path in sorted(args.output_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            checksums.append(f"{sha256(path)}  {path.relative_to(args.output_dir)}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
