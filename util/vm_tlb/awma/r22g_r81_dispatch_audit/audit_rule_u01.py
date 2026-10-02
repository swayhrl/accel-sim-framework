#!/usr/bin/env python3
"""CPU-only retrospective accounting for frozen R81 RULE_U01."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path


COHORTS = [
    "C0_SHARED_DISCOVERY",
    "C1_HETEROGENEOUS_DISCOVERY",
    "H0_HETEROGENEOUS_HOLDOUT",
]
A0 = "A0_DENSE_VENDOR"
A3 = "A3_RAGGED_DIRECT"
VOCAB = 151936


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def median(values):
    return statistics.median(values)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent-pack", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    parent_index = {
        row["relative_path"]: row for row in read_tsv(args.parent_pack / "RAW_DATA_INDEX.tsv")
    }
    selected = [
        ("MASK_WORK_SUMMARY.tsv", "MASK_WORK_SUMMARY.tsv"),
        ("CONTROL_STRATIFICATION_SUMMARY.tsv", "CONTROL_STRATIFICATION_SUMMARY.tsv"),
    ]
    selected += [
        (
            f"raw/head_replay/{cohort}/{name}",
            f"raw/measurements/head_replay/{cohort}/{name}",
        )
        for cohort in COHORTS
        for name in ("TIMING_STEPS.tsv", "TIMING_REPETITIONS.tsv")
    ]
    verified = []
    for local_rel, authority_rel in selected:
        path = args.raw_root / local_rel
        authority = parent_index[authority_rel]
        observed = {"size_bytes": path.stat().st_size, "sha256": sha256(path)}
        if observed["size_bytes"] != int(authority["size_bytes"]):
            raise ValueError(f"size mismatch: {local_rel}")
        if observed["sha256"] != authority["sha256"]:
            raise ValueError(f"sha mismatch: {local_rel}")
        verified.append(
            {
                "local_relative_path": local_rel,
                "parent_index_relative_path": authority_rel,
                **observed,
            }
        )

    masks = {}
    for row in read_tsv(args.raw_root / "MASK_WORK_SUMMARY.tsv"):
        key = (row["cohort"], int(row["step"]))
        if key in masks:
            raise ValueError(f"duplicate mask row {key}")
        masks[key] = row

    rule_rows = []
    oracle_rows = []
    step_rows = []
    audit = {"rule": "legal_union_fraction < 0.01 -> A3; else A0", "cohorts": {}}
    for cohort in COHORTS:
        timing_path = args.raw_root / "raw" / "head_replay" / cohort / "TIMING_STEPS.tsv"
        timing = read_tsv(timing_path)
        values = {}
        for row in timing:
            key = (int(row["rep"]), row["arm"], int(row["step"]))
            if key in values:
                raise ValueError(f"duplicate timing row {key}")
            values[key] = float(row["elapsed_head_region_ms"])
        reps = sorted({int(row["rep"]) for row in timing})
        steps = sorted({int(row["step"]) for row in timing})
        if reps != list(range(7)):
            raise ValueError(f"unexpected reps for {cohort}: {reps}")

        for rep in reps:
            for arm in (A0, A3):
                missing = [step for step in steps if (rep, arm, step) not in values]
                if missing:
                    raise ValueError(f"missing matched rows {cohort}/{rep}/{arm}: {missing}")

        chosen = {}
        for step in steps:
            m = masks[(cohort, step)]
            fraction = float(m["union_fraction_of_model_vocab"])
            if abs(fraction - int(m["union_count"]) / VOCAB) > 1e-15:
                raise ValueError(f"union fraction mismatch {cohort}/{step}")
            arm = A3 if fraction < 0.01 else A0
            chosen[step] = arm
            step_rows.append(
                {
                    "cohort": cohort,
                    "step": step,
                    "union_count": int(m["union_count"]),
                    "legal_union_fraction": f"{fraction:.17g}",
                    "rule_arm": arm,
                    "active_requests": int(m["active_requests"]),
                    "singleton_active_requests": int(m["singleton_active_requests"]),
                    "mask_sha256": m["mask_sha256"],
                    "matched_A0_A3_reps": len(reps),
                }
            )

        per_rep = []
        for rep in reps:
            a0_sum = sum(values[(rep, A0, step)] for step in steps)
            rule_sum = sum(values[(rep, chosen[step], step)] for step in steps)
            oracle_winners = {
                step: A3 if values[(rep, A3, step)] < values[(rep, A0, step)] else A0
                for step in steps
            }
            oracle_sum = sum(
                min(values[(rep, A0, step)], values[(rep, A3, step)]) for step in steps
            )
            saved = a0_sum - rule_sum
            gap = rule_sum - oracle_sum
            per_rep.append(
                {
                    "rep": rep,
                    "all_A0_ms": a0_sum,
                    "rule_ms": rule_sum,
                    "oracle_ms": oracle_sum,
                    "saved_ms": saved,
                    "saved_fraction": saved / a0_sum,
                    "gap_ms": gap,
                    "gap_fraction_of_rule": gap / rule_sum,
                    "oracle_A0_steps": sum(v == A0 for v in oracle_winners.values()),
                    "oracle_A3_steps": sum(v == A3 for v in oracle_winners.values()),
                }
            )
            rule_rows.append(
                {
                    "cohort": cohort,
                    "rep": rep,
                    "retained_steps": len(steps),
                    "rule_A3_steps": sum(v == A3 for v in chosen.values()),
                    "rule_A0_steps": sum(v == A0 for v in chosen.values()),
                    "all_A0_head_region_ms": f"{a0_sum:.9f}",
                    "RULE_U01_head_region_ms_before_dispatch_cost": f"{rule_sum:.9f}",
                    "head_region_saved_ms_before_dispatch_cost": f"{saved:.9f}",
                    "head_region_saved_fraction_before_dispatch_cost": f"{saved / a0_sum:.12f}",
                    "dispatch_signal_cost_ms": "UNKNOWN",
                    "deployable_net_ms": "UNKNOWN",
                    "matched_per_step_A0_A3": "TRUE",
                }
            )
            oracle_rows.append(
                {
                    "cohort": cohort,
                    "rep": rep,
                    "retained_steps": len(steps),
                    "oracle_A3_steps": per_rep[-1]["oracle_A3_steps"],
                    "oracle_A0_steps": per_rep[-1]["oracle_A0_steps"],
                    "best_of_A0_A3_oracle_ms": f"{oracle_sum:.9f}",
                    "RULE_U01_ms_before_dispatch_cost": f"{rule_sum:.9f}",
                    "RULE_U01_gap_to_oracle_ms": f"{gap:.9f}",
                    "RULE_U01_gap_fraction_of_rule": f"{gap / rule_sum:.12f}",
                    "deployability": "NONDEPLOYABLE_PER_STEP_TIMING_ORACLE",
                }
            )

        rule_rows.append(
            {
                "cohort": cohort,
                "rep": "MEDIAN_OF_7_MATCHED_REPS",
                "retained_steps": len(steps),
                "rule_A3_steps": sum(v == A3 for v in chosen.values()),
                "rule_A0_steps": sum(v == A0 for v in chosen.values()),
                "all_A0_head_region_ms": f"{median([x['all_A0_ms'] for x in per_rep]):.9f}",
                "RULE_U01_head_region_ms_before_dispatch_cost": f"{median([x['rule_ms'] for x in per_rep]):.9f}",
                "head_region_saved_ms_before_dispatch_cost": f"{median([x['saved_ms'] for x in per_rep]):.9f}",
                "head_region_saved_fraction_before_dispatch_cost": f"{median([x['saved_fraction'] for x in per_rep]):.12f}",
                "dispatch_signal_cost_ms": "UNKNOWN",
                "deployable_net_ms": "UNKNOWN",
                "matched_per_step_A0_A3": "TRUE",
            }
        )
        oracle_rows.append(
            {
                "cohort": cohort,
                "rep": "MEDIAN_OF_7_MATCHED_REPS",
                "retained_steps": len(steps),
                "oracle_A3_steps": "VARIES_BY_REP",
                "oracle_A0_steps": "VARIES_BY_REP",
                "best_of_A0_A3_oracle_ms": f"{median([x['oracle_ms'] for x in per_rep]):.9f}",
                "RULE_U01_ms_before_dispatch_cost": f"{median([x['rule_ms'] for x in per_rep]):.9f}",
                "RULE_U01_gap_to_oracle_ms": f"{median([x['gap_ms'] for x in per_rep]):.9f}",
                "RULE_U01_gap_fraction_of_rule": f"{median([x['gap_fraction_of_rule'] for x in per_rep]):.12f}",
                "deployability": "NONDEPLOYABLE_PER_STEP_TIMING_ORACLE",
            }
        )
        audit["cohorts"][cohort] = {
            "steps": len(steps),
            "reps": reps,
            "matched_timing_rows": len(timing),
            "rule_A3_steps": sum(v == A3 for v in chosen.values()),
            "rule_A0_steps": sum(v == A0 for v in chosen.values()),
            "median_saved_fraction_before_dispatch_cost": median(
                [x["saved_fraction"] for x in per_rep]
            ),
            "favorable_reps_before_dispatch_cost": sum(x["saved_ms"] > 0 for x in per_rep),
            "dispatch_signal_cost": "UNKNOWN",
        }

    write_tsv(args.output_dir / "RULE_U01_RETROSPECTIVE.tsv", rule_rows)
    write_tsv(args.output_dir / "BEST_OF_ORACLE.tsv", oracle_rows)
    write_tsv(args.output_dir / "RULE_U01_STEP_CLASSIFICATION.tsv", step_rows)
    audit["verified_parent_files"] = verified
    (args.output_dir / "AUTHORITY_VERIFICATION.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
