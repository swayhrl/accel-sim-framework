#!/usr/bin/env python3
"""CPU-only recomputation from fixed public Q1 Git blobs; no runner imports."""

import csv
import io
import json
import statistics
import subprocess
from collections import Counter, defaultdict

REPO = "/home/huangrulin/workspace/accel-sim-framework"
Q1 = "5787826ca21f7af958e6e1c1f828d62fd58a1ec4"
BASE = "docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1/"


def blob(name):
    return subprocess.check_output(["git", "-C", REPO, "show", f"{Q1}:{BASE}{name}"])


def document(name):
    return json.loads(blob(name))


rows = list(csv.DictReader(io.StringIO(blob("FORMAL_SAMPLES.tsv").decode()), delimiter="\t"))
published = document("FORMAL_ANALYSIS.json")
identity = document("NATIVE_INPUT_WINDOW_IDENTITY.json")
assert len(rows) == published["formal_samples"] == 20
assert len({row["job"] for row in rows}) == 20
assert all(row["valid"] == "True" and int(row["actual_steps"]) == 51 for row in rows)
assert all(int(row["N_total_min"]) == int(row["N_total_max"]) == 6720398 for row in rows)

groups = defaultdict(list)
ordered_rounds = defaultdict(list)
for row in rows:
    phase, policy, round_number = row["phase"], int(row["policy"]), int(row["round"])
    assert phase in {"DISCOVERY", "VALIDATION"} and policy in {8, 16}
    assert round_number in range(3, 8)
    groups[(phase, policy)].append(float(row["closed_window_wall_seconds"]))
    ordered_rounds[(phase, round_number)].append(policy)
    assert row["numeric_scope"].startswith("NOT_ESTABLISHED")

assert all(len(values) == 5 for values in groups.values()) and len(groups) == 4
assert all(set(values) == {8, 16} for values in ordered_rounds.values())
assert len(ordered_rounds) == 10
for phase in ("DISCOVERY", "VALIDATION"):
    assert [ordered_rounds[(phase, n)] for n in range(3, 8)] == [
        [16, 8], [8, 16], [16, 8], [8, 16], [16, 8]
    ]

result = {"source_commit": Q1, "formal_rows": len(rows), "groups": {}, "phases": {}}
for (phase, policy), values in sorted(groups.items()):
    median = statistics.median(values)
    mad = statistics.median(abs(x - median) for x in values)
    expected = published["stats"][phase][str(policy)]
    assert abs(median - expected["median"]) < 1e-12
    assert abs(mad - expected["MAD"]) < 1e-12
    assert abs(min(values) - expected["min"]) < 1e-12
    assert abs(max(values) - expected["max"]) < 1e-12
    result["groups"][f"{phase}_T{policy}"] = {
        "n": len(values), "median_seconds": median, "MAD_seconds": mad,
        "min_seconds": min(values), "max_seconds": max(values),
    }

for phase in ("DISCOVERY", "VALIDATION"):
    phase_rows = [row for row in rows if row["phase"] == phase]
    camera_sha = {row["camera_SHA256"] for row in phase_rows}
    assert len(camera_sha) == 1
    sequence = next(iter(identity["camera_sequences"][phase].values()))
    assert len(sequence) == 51
    ids = [item[0] for item in sequence]
    assert len(set(ids)) == 51
    assert camera_sha == set(identity["camera_sequences"][phase])
    t8 = result["groups"][f"{phase}_T8"]["median_seconds"]
    t16 = result["groups"][f"{phase}_T16"]["median_seconds"]
    reduction = (t8 - t16) / t8 * 100
    expected = document("COST_LEDGER.json")["formal_ratios"][phase]
    assert abs(reduction - expected["T16_latency_reduction_pct"]) < 1e-10
    result["phases"][phase] = {
        "camera_SHA256": next(iter(camera_sha)), "camera_ids": 51,
        "T8_minus_T16_seconds": t8 - t16,
        "T16_vs_T8_latency_reduction_pct": reduction,
        "T8_over_T16_ratio": t8 / t16,
    }

discovery_ids = {x[0] for x in next(iter(identity["camera_sequences"]["DISCOVERY"].values()))}
validation_ids = {x[0] for x in next(iter(identity["camera_sequences"]["VALIDATION"].values()))}
assert not discovery_ids & validation_ids
assert identity["camera_ID_intersection"] == []
assert not published["final_semantic_fingerprints_all_equal"]
assert len({row["final_semantic_fingerprint"] for row in rows}) > 1
result["camera_id_intersection"] = 0
result["final_fingerprint_identical"] = False
diagnostics = document("DIAGNOSTIC_ANALYSIS.json")["jobs"]
ledger = document("COST_LEDGER.json")["jobs"]
assert len(diagnostics) == len(ledger) == 3
result["diagnostics"] = {}
for observed, classified in zip(diagnostics, ledger):
    assert observed["job"] == classified["job"] and observed["valid"]
    assert abs(observed["main_host_regions_union_seconds"] - classified["main_host_classified_union_seconds"]) < 1e-12
    assert abs(observed["host_wait_join_sync_union_seconds"] - classified["host_join_sync_union_seconds"]) < 1e-12
    assert observed["main_host_regions_union_seconds"] <= observed["closed_window_wall_seconds"]
    assert observed["host_wait_join_sync_union_seconds"] <= observed["main_host_regions_union_seconds"]
    assert observed["no_cross_clock_subtraction"] and classified["no_cross_domain_subtraction"]
    event_values = observed["GPU_event_span_ms"]["all_samples"]
    assert len(event_values) == 51
    assert abs(statistics.median(event_values) - classified["GPU_event_span_median_ms"]) < 1e-9
    adam_forward = classified["CPU_Adam_seconds"] + classified["CPU_parameter_forward_seconds"]
    assert abs(adam_forward / classified["closed_ON_seconds"] * 100 - classified["CPU_Adam_plus_forward_pct"]) < 1e-9
    assert abs(classified["host_join_sync_union_seconds"] / classified["closed_ON_seconds"] * 100 - classified["host_join_sync_pct"]) < 1e-9
    result["diagnostics"][observed["job"]] = {
        "ON_window_seconds": classified["closed_ON_seconds"],
        "main_host_union_seconds": observed["main_host_regions_union_seconds"],
        "Adam_plus_forward_pct": classified["CPU_Adam_plus_forward_pct"],
        "join_sync_union_pct": classified["host_join_sync_pct"],
        "GPU_event_span_median_ms": statistics.median(event_values),
    }
result["checks"] = "PASS: fixed public TSV and JSON consistency only"
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
