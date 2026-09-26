#!/usr/bin/env python3
"""Retrospective minimum diagnostic for accepted Q05 prefix evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


REPO = Path("/root/workspace/accel-sim-framework-awma-post-negative-problem-pivot-v1")
SOURCE = REPO / "docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1"
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_POST_NEGATIVE_PROBLEM_PIVOT_V1"
INPUTS = {
    "warm": SOURCE / "WARM_PREFIX_RESULTS.tsv",
    "translation": SOURCE / "Q05_TRANSLATION_RESULTS.tsv",
    "data": SOURCE / "Q05_DATA_CACHE_RESULTS.tsv",
    "overlap4k": SOURCE / "TRANSLATION_RELEVANT_PAGE_OVERLAP_4K.tsv",
    "overlap64k": SOURCE / "TRANSLATION_RELEVANT_PAGE_OVERLAP_64K.tsv",
    "state": SOURCE / "F0_KERNEL_BOUNDARY_STATE_MATRIX_FINAL.tsv",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, columns, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for position in range(index, end):
            result[ordered[position][0]] = rank
        index = end
    return result


def pearson(left: list[float], right: list[float]) -> float:
    lmean = sum(left) / len(left); rmean = sum(right) / len(right)
    numerator = sum((a-lmean)*(b-rmean) for a, b in zip(left, right))
    lden = math.sqrt(sum((a-lmean)**2 for a in left)); rden = math.sqrt(sum((b-rmean)**2 for b in right))
    return numerator / (lden * rden)


def main() -> int:
    warm = {row["row"]: row for row in read(INPUTS["warm"])}
    trans = {row["row"]: row for row in read(INPUTS["translation"])}
    data = {row["row"]: row for row in read(INPUTS["data"])}
    overlap4k = {row["prefix"]: row for row in read(INPUTS["overlap4k"])}
    overlap64k = {row["prefix"]: row for row in read(INPUTS["overlap64k"])}
    rows = []
    isolated_cycles = int(warm["ISOLATED_Q05"]["gpu_sim_cycle"])
    for name in ["ISOLATED_Q05", "P1", "P2", "P4", "P8", "P16", "P34"]:
        cycles = int(warm[name]["gpu_sim_cycle"])
        row = {
            "row": name, "predecessor_members": int(warm[name]["predecessor_members"]),
            "cycles": cycles, "cycle_response_vs_isolated_percent": f"{(isolated_cycles-cycles)*100.0/isolated_cycles:.6f}",
            "instructions": int(warm[name]["gpu_sim_insn"]), "ctas": int(trans[name]["gpu_tot_issued_cta"]),
            "overlap_4k_fraction": "0" if name == "ISOLATED_Q05" else overlap4k[name]["q05_coverage_fraction"],
            "overlap_64k_fraction": "0" if name == "ISOLATED_Q05" else overlap64k[name]["q05_coverage_fraction"],
            "walk_starts": int(trans[name]["vm_translation_walk_starts"]),
            "l2_tlb_misses": int(trans[name]["vm_l2_tlb_misses"]),
            "l2_cache_misses": int(data[name]["L2_total_cache_misses"]),
        }
        rows.append(row)
    write(PACK / "CONTEXT_PREFIX_DIAGNOSTIC.tsv", rows,
          ["row", "predecessor_members", "cycles", "cycle_response_vs_isolated_percent", "instructions", "ctas",
           "overlap_4k_fraction", "overlap_64k_fraction", "walk_starts", "l2_tlb_misses", "l2_cache_misses"])

    indexed = {row["row"]: row for row in rows}
    pair_specs = [
        ("P2_P4_PRIMARY", "P2", "P4", "EQUAL_OVERLAP_AND_WALKS"),
        ("P8_P16_PRIMARY", "P8", "P16", "EQUAL_OVERLAP_AND_WALKS"),
        ("ISOLATED_P1_ENDPOINT", "ISOLATED_Q05", "P1", "ENDPOINT_CHECK"),
        ("P8_P34_ENDPOINT", "P8", "P34", "SATURATED_OVERLAP_ENDPOINT_CHECK"),
    ]
    pairs = []
    for label, left_name, right_name, role in pair_specs:
        left = indexed[left_name]; right = indexed[right_name]
        left_cycles = int(left["cycles"]); right_cycles = int(right["cycles"])
        separation = abs(left_cycles-right_cycles) * 100.0 / min(left_cycles, right_cycles)
        faster = left_name if left_cycles < right_cycles else right_name
        left_miss = int(left["l2_cache_misses"]); right_miss = int(right["l2_cache_misses"])
        lower_miss = left_name if left_miss < right_miss else right_name
        direction = "CONSISTENT" if faster == lower_miss else "CONTRADICTS_L2_MISS_MEDIATION"
        equal_gate = (left["overlap_4k_fraction"] == right["overlap_4k_fraction"] and
                      left["walk_starts"] == right["walk_starts"])
        falsifies = role == "EQUAL_OVERLAP_AND_WALKS" and equal_gate and separation > 1.0 and direction.startswith("CONTRADICTS")
        pairs.append({
            "contrast": label, "left": left_name, "right": right_name, "role": role,
            "equal_overlap_and_walk_gate": equal_gate, "cycle_separation_percent": f"{separation:.6f}",
            "faster_row": faster, "lower_l2_miss_row": lower_miss, "direction": direction,
            "falsifies_localized_state_hypothesis": falsifies,
        })
    write(PACK / "CONTEXT_MATCHED_PAIR_RESULTS.tsv", pairs,
          ["contrast", "left", "right", "role", "equal_overlap_and_walk_gate", "cycle_separation_percent",
           "faster_row", "lower_l2_miss_row", "direction", "falsifies_localized_state_hypothesis"])

    prefix = [row for row in rows if row["row"] != "ISOLATED_Q05"]
    cycle_values = [float(row["cycles"]) for row in prefix]
    correlations = []
    for name in ["overlap_4k_fraction", "walk_starts", "l2_cache_misses"]:
        values = [float(row[name]) for row in prefix]
        correlations.append({"predictor": name, "pearson_with_cycles": f"{pearson(values,cycle_values):.9f}",
                             "spearman_with_cycles": f"{pearson(ranks(values),ranks(cycle_values)):.9f}", "rows": 6})
    write(PACK / "CONTEXT_CORRELATION_SUMMARY.tsv", correlations,
          ["predictor", "pearson_with_cycles", "spearman_with_cycles", "rows"])

    falsifiers = [row["contrast"] for row in pairs if row["falsifies_localized_state_hypothesis"]]
    receipt = {
        "authority": "2640c4368aea1dc44eb6c34fdc9bb5f738ec3fb2",
        "classification": "RETROSPECTIVE_EXISTING_EVIDENCE_DIAGNOSTIC",
        "inputs": {name: {"path": str(path), "sha256": sha(path)} for name, path in INPUTS.items()},
        "row_count": len(rows), "primary_pair_count": 2,
        "falsifying_pairs": falsifiers,
        "decision": "REJECT_NO_LOCALIZED_CAUSE" if falsifiers else "LOCALIZED_MEDIATOR_NOT_FALSIFIED",
        "new_simulation_runs": 0, "new_native_runs": 0,
    }
    (PACK / "CONTEXT_DIAGNOSTIC_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
