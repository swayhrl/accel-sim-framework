#!/usr/bin/env python3
"""Deterministic CPU-only consistency checks for the reset review pack."""

import csv
import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parent


def table(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    assert rows and all(None not in row and all(value != "" for value in row.values()) for row in rows), name
    return rows


def main():
    authority = json.loads((ROOT / "AUTHORITY_INDEX.json").read_text())
    final = json.loads((ROOT / "FINAL_DECISION.json").read_text())
    archives = table("EXISTING_OBSERVATION_ARCHIVE.tsv")
    cards = table("PROBLEM_CANDIDATE_CARDS.tsv")
    observable = table("OBSERVABILITY_AUDIT.tsv")
    oracles = table("ORACLE_HEADROOM_AUDIT.tsv")
    source_urls = table("CANDIDATE_SOURCE_URLS.tsv")
    assert authority["base_commit"] == final["base_stagea_commit"] == "ccd6928bfb420d1e4c554ec0e377bb8fbe377501"
    for commit in [authority["base_commit"], *authority["accepted_or_boundary_commits"].values(), authority["literature_authority"]["commit"]]:
        assert subprocess.check_output(["git", "cat-file", "-t", commit], text=True).strip() == "commit", commit
    old = json.loads(subprocess.check_output(["git", "show", "ccd6928bfb420d1e4c554ec0e377bb8fbe377501:docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/FINAL_DECISION.json"], text=True))
    assert old["status"] == "C16_STAGEA_TIER0_TERMINAL_PARTIAL"
    assert old["mp02_b1_native_point"] == "SCIENCE_VALID"
    assert old["mp03_b4_native_point"] == "INCOMPLETE_EXECUTION_IDENTITY_STOP"
    assert old["formal_tier0_survivor_count"] == 0
    ids = {row["candidate_id"] for row in cards}
    assert len(cards) == len(ids) == final["candidate_card_count"] == 10
    assert ids == {row["candidate_id"] for row in observable} == {row["candidate_id"] for row in oracles} == {row["candidate_id"] for row in source_urls}
    assert all(row["primary_source_url"].startswith("https://") for row in source_urls)
    assert len(archives) >= 10 and len({row["phenomenon_id"] for row in archives}) == len(archives)
    assert {"OBS_MP01_PREFILL", "OBS_MP05_AWQ", "OBS_MP02_B1_MODE", "OBS_E1_RAW_AWQ_SHAPE", "OBS_E3_ROUTING", "OBS_GROUPED_RESIDUAL", "OBS_CONVERSION_DUP", "OBS_FFN_GATEUP", "OBS_DEEPSEEK_REVISIT", "OBS_TRANSLATION"}.issubset({row["phenomenon_id"] for row in archives})
    assert next(row for row in archives if row["phenomenon_id"] == "OBS_E1_RAW_AWQ_SHAPE")["archive_status"] == "HISTORICAL_GATED_NOT_PROMOTABLE"
    assert all(row["109_required"] == "NO" for row in cards)
    assert all(row["decision"] not in {"PRIMARY", "BACKUP"} for row in cards)
    assert sum(row["decision"] == "PARKED_NOT_ADMITTED" for row in cards) == final["parked_not_admitted_count"] == 2
    assert {row["observability_friction"] for row in observable}.issubset({"LOW", "MEDIUM", "HIGH"})
    assert {row["observability_friction"] for row in cards}.issubset({"LOW", "MEDIUM", "HIGH"})
    assert final["status"] == "NO_NEW_PROBLEM_READY_FOR_NATIVE_VALIDATION"
    assert final["primary_candidate_count"] == final["backup_candidate_count"] == 0
    assert final["current_109_required"] is False and final["gpu_or_model_executed"] is False
    assert final["stagea_v2_created"] is final["tier1_or_holdout_authorized"] is False
    assert "NO_NEW_PROBLEM_READY_FOR_NATIVE_VALIDATION" in (ROOT / "CANDIDATE_DECISION.md").read_text()
    assert "No PRIMARY candidate" in (ROOT / "NEXT_MINIMAL_EXPERIMENT_SET.md").read_text()
    handoff = pathlib.Path("docs/vm_tlb/chatgpt_handoff/c16/C16_PROBLEM_DISCOVERY_RESET_CURRENT_STATE.md")
    assert handoff.is_file() and "0 PRIMARY, 0 BACKUP" in handoff.read_text()
    print("PASS: authority objects, 14 scoped observations, 10 cards, route/observable/oracle joins, zero promotion and zero GPU")


if __name__ == "__main__":
    main()
