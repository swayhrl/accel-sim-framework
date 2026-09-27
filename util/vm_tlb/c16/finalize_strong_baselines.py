#!/usr/bin/env python3
"""Build the C16 strong-baseline preparation review pack."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

GOAL = "C16_E1_STRONG_BASELINES_PREP_174NEW_V1"
STATUS = "C16_STRONG_BASELINE_PREP_PARTIAL"


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
    parser.add_argument("--qualification-dir", type=Path, required=True)
    parser.add_argument("--config-dir", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, required=True)
    parser.add_argument("--core-docs", type=Path, required=True)
    parser.add_argument("--source-diff", type=Path, required=True)
    parser.add_argument("--candidate-sha", type=Path, required=True)
    parser.add_argument("--reference-sha", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--core-commit", required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "review pack must be fresh")

    neutrality = json.loads(
        (args.qualification_dir / "OFF_NEUTRALITY.json").read_text())
    canaries = json.loads(
        (args.qualification_dir / "BOUNDED_CANARY_RESULTS.json").read_text())
    need(neutrality["status"] == "PASS", "OFF neutrality not PASS")
    need(canaries["status"] == "PASS", "bounded canaries not PASS")
    need(canaries["ship_sw"]["status"] ==
         "SHIP_SW_IMPLEMENTATION_CONTRACT_INCOMPLETE",
         "SHiP-SW boundary drift")

    args.output_dir.mkdir(parents=True)
    (args.output_dir / ".gitattributes").write_text(
        "SOURCE_DIFF.patch -whitespace\n", encoding="utf-8")
    for name in ("OFF_NEUTRALITY.json", "BOUNDED_CANARY_RESULTS.json"):
        shutil.copy2(args.qualification_dir / name, args.output_dir / name)
    for name in ("BASELINE_IMPLEMENTATION_CONTRACT.md",
                 "OLD_L2_INFRA_REUSE_AUDIT.md", "SECTOR_EVENT_MAPPING.md",
                 "DRRIP_GPU_ADAPTATION.md", "SHIP_SW_CONTRACT_STATUS.md"):
        shutil.copy2(args.core_docs / name, args.output_dir / name)
    shutil.copy2(args.source_diff, args.output_dir / "SOURCE_DIFF.patch")
    shutil.copy2(args.candidate_sha, args.output_dir / "CANDIDATE_BINARY_SHA256")
    shutil.copy2(args.reference_sha, args.output_dir / "REFERENCE_BINARY_SHA256")

    configs = args.output_dir / "configs"
    configs.mkdir()
    for path in sorted(args.config_dir.glob("*.config")):
        shutil.copy2(path, configs / path.name)
    need(len(list(configs.glob("*.config"))) == 8, "config set drift")

    dump(args.output_dir / "CURRENT_C16_AUTHORITY.json", {
        "schema": "C16_E1_STRONG_BASELINES_AUTHORITY_V1", "status": "PASS",
        "core_authority": "0271de82432db004beed43280ed01057246a0f2c",
        "core_branch": "hrl/c16-b16-reuse-canary-hostscale-v1",
        "implementation_core_commit": args.core_commit,
        "framework_parent": "f99e1c697143c02786bc34fa5c27c75a2d19e740",
        "accepted_lane1": [
            "4214398782159022907081dbcc36854cf21fb4b5",
            "1d5b3a0ad078918328efc23b108c4849f677fd75",
            "0631070779329adfee858f5e350b6c74670bcd5f",
            "a72d0f50b26c558368787318860df539950418fd",
            "a62ac8f140e3f6c9dcecd352b414c094fefe5d07",
            "f99e1c697143c02786bc34fa5c27c75a2d19e740"],
        "literature_read_only_commit":
            "350e4a0d364d65812f379ebc69412696e2a4d82a",
        "literature_files_read": ["README", "LR03", "LR04", "LR05"],
        "historical_l2_read_only": {
            "ep_l2": "0cde333340792cffed869cbbc7e7dc88667c6b8b",
            "frc": "97eb1e8301d410c8d720e6780fba40751e38000e"},
        "lane4_partial_results_used": False,
    })

    (args.output_dir / "POLICY_MATRIX.tsv").write_text(
        "policy\tfunctional_status\ttarget_information\tquota\tqualification\n"
        "NONE\tdefault_off\tnone\tnone\tOFF_NEUTRALITY_PASS\n"
        "PRIORITY_ALL\timplemented\taccepted_qweight_regions\tnone\tBOUNDED_PASS\n"
        "PRIORITY_STABLE\timplemented\taccepted_regions+frozen_selector\tnone\tBOUNDED_PASS\n"
        "DRRIP\timplemented\tnone\tnone\tBOUNDED_PASS\n"
        "SHIP_SW\tfail_closed_interface_only\taccepted_regions\tnone\tCONTRACT_INCOMPLETE\n",
        encoding="utf-8")
    (args.output_dir / "UNIT_TEST_RESULTS.tsv").write_text(
        "suite\tstatus\tevidence\n"
        "priority_and_selector\tPASS\tC16_STRONG_BASELINES_POLICY_TEST_PASS\n"
        "drrip_policy\tPASS\tC16_STRONG_BASELINES_POLICY_TEST_PASS\n"
        "sector_tag_array\tPASS\tC16_STRONG_BASELINES_TAG_ARRAY_TEST_PASS\n"
        "oracle_regression\tPASS\tORACLE_ELASTIC_QWEIGHT_RESIDENCY_TEST_SUITE_PASS\n"
        "framework_analysis\tPASS\t2 unittest cases\n",
        encoding="utf-8")
    (args.output_dir / "OPEN_ISSUES.md").write_text(
        "# Open issues\n\n"
        "- `SHIP_SW_IMPLEMENTATION_CONTRACT_INCOMPLETE`: software-region "
        "signature granularity, finite SHCT mapping/collision, sampling, and "
        "request marking need an approved contract.\n"
        "- No full timing, B8/B24/BFULL, M1F timing, or policy performance "
        "comparison was run.\n"
        "- Hardware timing/area/power remains to be evaluated.\n",
        encoding="utf-8")

    build_log = args.logs_dir / "full_build_v2.log"
    reference_build = args.logs_dir / "reference_build.log"
    need("C16_STRONG_BASELINES_REBUILD_PASS" in
         build_log.read_text(errors="replace"), "candidate build not PASS")
    need("C16_STRONG_BASELINES_REFERENCE_BUILD_PASS" in
         reference_build.read_text(errors="replace"), "reference build not PASS")
    dump(args.output_dir / "BUILD_RECEIPTS.json", {
        "schema": "C16_E1_STRONG_BASELINES_BUILD_RECEIPTS_V1",
        "status": "PASS", "parallelism_limit": 2,
        "candidate_log": str(build_log),
        "candidate_log_sha256": sha256(build_log),
        "reference_log": str(reference_build),
        "reference_log_sha256": sha256(reference_build),
    })

    raw = ["artifact\tsha256\tbytes\tpath"]
    run_names = ("REFERENCE_OFF", "CANDIDATE_OFF", "PRIORITY_ALL",
                 "PRIORITY_STABLE", "DRRIP", "SHIP_SW_REJECT",
                 "REJECT_DISABLED_NONNONE", "REJECT_ENABLED_NONE",
                 "REJECT_ORACLE_MUTUAL")
    for run in run_names:
        for name in ("stdout.log", "stderr.log"):
            path = args.runs_dir / run / name
            if path.is_file():
                raw.append(f"{run}/{name}\t{sha256(path)}\t"
                           f"{path.stat().st_size}\t{path}")
    (args.output_dir / "RAW_LOG_INDEX.tsv").write_text(
        "\n".join(raw) + "\n", encoding="utf-8")

    pa = canaries["policies"][0]["summed_counters"]
    ps = canaries["policies"][1]["summed_counters"]
    dr = canaries["policies"][2]["summed_counters"]
    readme = (
        f"# {GOAL}\n\nFinal status: `{STATUS}`.\n\n"
        "Qualified without full timing: PRIORITY_ALL, PRIORITY_STABLE, and "
        "2-bit DRRIP-HP. SHiP-SW-style remains fail-closed because its C16 "
        "software signature contract is not uniquely specified.\n\n"
        f"The OFF real-prefix signature is exact. PRIORITY_ALL prioritized "
        f"{pa['priority_selected_accesses']} / {pa['priority_target_accesses']} "
        f"target accesses; PRIORITY_STABLE prioritized "
        f"{ps['priority_selected_accesses']} / {ps['priority_target_accesses']} "
        f"and reported actual resident peak {ps['priority_peak_resident']}. "
        f"DRRIP observed {dr['drrip_srrip_insertions']} SRRIP, "
        f"{dr['drrip_brrip_long_insertions']} long BRRIP, "
        f"{dr['drrip_brrip_short_insertions']} short BRRIP insertions, and "
        f"{dr['true_hit_promotions']} true-sector promotions.\n\n"
        "These bounded runs are activation checks, not performance "
        "comparisons. No Lane 4 partial timing values were read or used.\n")
    (args.output_dir / "README.md").write_text(readme, encoding="utf-8")
    dump(args.output_dir / "VALIDATION_SUMMARY.json", {
        "schema": "C16_E1_STRONG_BASELINES_VALIDATION_V1",
        "status": STATUS,
        "priority_all": "QUALIFIED_BOUNDED_NO_FULL_TIMING",
        "priority_stable": "QUALIFIED_BOUNDED_NO_FULL_TIMING",
        "drrip": "QUALIFIED_BOUNDED_NO_FULL_TIMING",
        "ship_sw": "SHIP_SW_IMPLEMENTATION_CONTRACT_INCOMPLETE",
        "off_neutrality": "PASS", "full_timing_run": False,
    })

    checksums = []
    for path in sorted(args.output_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            checksums.append(f"{sha256(path)}  {path.relative_to(args.output_dir)}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
