#!/usr/bin/env python3
"""Deterministic closeout validation for R21A mixed Dready STOP."""

import csv
import hashlib
import json
import statistics
import subprocess
from pathlib import Path


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
WT = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r21a-oeq-graph-readiness-109-v1")
PACK = WT / "docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    checks = {}
    source = json.loads((PACK / "SOURCE_BINDINGS.json").read_text())
    checks["source_commits_exact"] = (source["nequip"]["commit"] == "27d9d2182da918ab7be0017d8300e53278f5e00e"
                                      and source["OpenEquivariance"]["commit"] == "dc9979099c65113adcc016977c5c60974f9ddafb"
                                      and source["input_repo"]["commit"] == "8f90935ba42fd9e03df323cf03428c456d87b881")
    checks["input_identity_exact"] = (source["input_repo"]["git_blob"] == "baac4e23364d00d29b2410fa60a92ade0cbf35a3"
                                      and source["input_sha256"] == "c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770")
    checks["model_identity_exact"] = source["model_package_sha256"] == "63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa"
    inp = json.loads((PACK / "INPUT_AUTHORITY.json").read_text())
    checks["frame_selection_exact"] = inp["frame_count"] == 110 and [row["index"] for row in inp["selected"]] == [55, 18, 36, 73, 91]
    checks["frame_order_not_temporal"] = inp["frame_order_interpreted_as_time"] is False
    graph = json.loads((PACK / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    checks["natural_graph_exact"] = graph["edge_count"] == 1394 and graph["natural_receiver_major"] is True and graph["natural_sender_within_receiver_monotonic"] is False

    with (PACK / "A0_ATOMIC_QUALIFICATION.tsv").open(newline="") as stream:
        a0 = list(csv.DictReader(stream, delimiter="\t"))
    with (PACK / "DREADY_CORRECTNESS.tsv").open(newline="") as stream:
        dready = list(csv.DictReader(stream, delimiter="\t"))
    checks["a0_five_pass"] = len(a0) == 5 and all(row["status"] == "PASS" for row in a0)
    checks["dready_five_pass"] = len(dready) == 5 and all(row["status"] == "PASS" for row in dready)
    with (PACK / "DREADY_TIMING.tsv").open(newline="") as stream:
        timing_rows = list(csv.DictReader(stream, delimiter="\t"))
    formal = [row for row in timing_rows if row["phase"] == "FORMAL"]
    checks["timing_protocol_exact"] = (len(formal) == 30 and all(sum(row["group"] == str(group) and row["arm"] == arm for row in formal) == 5 for group in range(3) for arm in ("A0", "Dready")))
    status = json.loads((RAW / "DREADY_TIMING_STATUS.json").read_text())
    gains = []
    for group in range(3):
        med = {}
        for arm in ("A0", "Dready"):
            values = [float(row["wall_ms"]) for row in formal if row["group"] == str(group) and row["arm"] == arm]
            med[arm] = statistics.median(values)
        gains.append((med["A0"] - med["Dready"]) / med["A0"])
    checks["median_gain_exact"] = abs(statistics.median(gains) - status["median_relative_improvement"]) < 1e-15
    checks["mixed_stop_exact"] = (status["Dready_MATERIAL"] is False
                                  and status["classification_if_stop"] == "R21A_RESULT_MIXED_NEEDS_REVIEW"
                                  and sum(row["gap_gt_3x_larger_MAD"] for row in status["groups"]) == 1)
    checks["donline_holdout_absent"] = not any(RAW.glob("DONLINE*")) and not any(RAW.glob("HOLDOUT*"))
    run = json.loads((PACK / "RUN_RECEIPTS.json").read_text())
    checks["durable_publish_pass"] = run["remote_verify"] == run["copyback_verify"] == "PASS"
    checks["current_lock_released"] = run["current_gpu_lock_held"] is False and run["current_gpu_processes"] == []
    checks["claim_boundary"] = run["donline_run"] is False and run["holdout_run"] is False and run["node174_compute"] is False
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
              "median_relative_improvement": statistics.median(gains), "group_relative_improvements": gains}
    (PACK / "VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS": raise SystemExit(2)


if __name__ == "__main__": main()
