#!/usr/bin/env python3
"""CPU-only compact snapshot/B0 table and node164 raw SHA closure."""

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
RAW = ROOT / "raw"
PACK = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r20r1-solver-entry-local-contract-109-v1/docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1")
NODE164 = "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20r1_solver_entry_local_contract_109_v1"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    g0 = json.loads((RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").read_text())
    r2 = json.loads((RAW / "R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    initial_b0 = json.loads((RAW / "B0_T128_REPEATABILITY.json").read_text())
    initial_validator = json.loads((RAW / "LOCAL_CONTRACT_B0_VALIDATOR.json").read_text())
    four = json.loads((RAW / "FOUR_ENTRY_B0_SUMMARY.json").read_text())
    stop = json.loads((RAW / "T152_STOP_SIGNATURE_DIAGNOSTIC.json").read_text())
    stop_worlds = [detail["world"] for comparison in stop["comparisons"] for detail in comparison["details"]]
    snapshots = [{
        "lineage": "G0_FIRST_LEGAL_REALIZATION",
        "step": 128,
        "entry_sha256": g0["entry_snapshot"]["sha256"],
        "exit_sha256": g0["exit_snapshot"]["sha256"],
        "entry_fields": g0["entry_snapshot"]["field_count"],
        "exit_fields": g0["exit_snapshot"]["field_count"],
        "classification": g0["classification"],
    }]
    for row in r2["entrances"]:
        snapshots.append({
            "lineage": "R2_NEW_CONTINUOUS_B0_REALIZATION",
            "step": row["step"],
            "entry_sha256": row["entry_snapshot"]["sha256"],
            "exit_sha256": row["exit_snapshot"]["sha256"],
            "entry_fields": row["entry_snapshot"]["field_count"],
            "exit_fields": row["exit_snapshot"]["field_count"],
            "classification": r2["classification"],
        })
    write_tsv(PACK / "SNAPSHOT_INDEX.tsv", snapshots)

    initial_qualified = (
        initial_validator["baseline_all_pass"]
        and initial_validator["negative_controls_all_rejected"]
        and initial_b0["solver_niter_bitwise_stable"]
        and initial_b0["overflow_bitwise_stable"]
        and initial_b0["nefc_bitwise_stable"]
    )
    b0_rows = [{
        "lineage": "G0_FIRST_LEGAL_REALIZATION",
        "step": 128,
        "entry_sha256": g0["entry_snapshot"]["sha256"],
        "same_graph_B0_repeats": 5,
        "fresh_graph_B0_repeats": 1,
        "discrete_stop_signature_exact": True,
        "floating_contract_pass": initial_validator["baseline_all_pass"],
        "source_relation_pass": True,
        "B0_qualified": initial_qualified,
        "failure_detail": "NONE",
    }]
    for row in four["rows"]:
        b0_rows.append({
            "lineage": "R2_NEW_CONTINUOUS_B0_REALIZATION",
            "step": row["step"],
            "entry_sha256": row["entry_sha256"],
            "same_graph_B0_repeats": row["same_graph_repeat_count"],
            "fresh_graph_B0_repeats": row["fresh_graph_repeat_count"],
            "discrete_stop_signature_exact": row["all_discrete_signatures_exact"],
            "floating_contract_pass": all(
                all(value["max_world_pass"] and value["rms_global_pass"]
                    for value in item["floating"].values())
                for item in json.loads((RAW / f"T{row['step']}_B0_QUALIFICATION.json").read_text())["B0_comparisons_to_first"]
            ),
            "source_relation_pass": row["source_relation_pass"],
            "B0_qualified": row["B0_qualified"],
            "failure_detail": "LS_ITERATIONS_new_bit_world_413_one_of_five" if row["step"] == 152 else "NONE",
        })
    if stop_worlds != [413]:
        raise RuntimeError(f"Frozen stop witness changed: {stop_worlds}")
    write_tsv(PACK / "B0_REPEATABILITY.tsv", b0_rows)

    index = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file():
            continue
        index.append({"relative_path": f"raw/{path.name}", "bytes": path.stat().st_size,
                      "sha256": sha(path), "node164_path": f"{NODE164}/raw/{path.name}"})
    write_tsv(PACK / "RAW_DATA_INDEX.tsv", index)
    with (ROOT / "RAW_SHA256SUMS").open("w", encoding="utf-8") as stream:
        for row in index:
            stream.write(f"{row['sha256']}  {row['relative_path']}\n")
    print(json.dumps({"snapshots": len(snapshots), "B0_rows": len(b0_rows), "raw_files": len(index),
                      "all_four_R2_qualified": four["all_four_B0_qualified"], "t152_stop_worlds": stop_worlds}, sort_keys=True))


if __name__ == "__main__":
    main()
