"""CPU-only arithmetic for the fixed Q1 state-supply review.

Run: python recompute.py --inputs PATH_TO_SMALL_FIXED_INPUTS --out OUTPUT_DIR
The inputs are copied, unchanged, from Q1 commit 5787826c and the frozen
GS-Scale source identified in BINARY_IDENTITY.json. No torch import.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

N = 6_720_398
F32 = 4
GIB = 1024 ** 3
SOURCE_ROOT = "docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1/"
INPUTS = [
    "BINARY_IDENTITY.json", "SOURCE_AND_INPUT_IDENTITY.json",
    "STATE_AND_NUMERIC_CONTRACT.json", "STATE_INDEPENDENT_INSPECTION.json",
    "COST_LEDGER.json", "DIAGNOSTIC_ANALYSIS.json", "RESOURCE_ANALYSIS.json",
    "SOFTWARE_EXCLUSION.md", "simple_trainer_hybrid_optimized.py", "cpu_adam.cpp",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    get = lambda name: json.loads((args.inputs / name).read_text(encoding="utf-8"))
    identity, binary, state, inspection, ledger, diag, resources = (
        get(name) for name in ["SOURCE_AND_INPUT_IDENTITY.json", "BINARY_IDENTITY.json",
        "STATE_AND_NUMERIC_CONTRACT.json", "STATE_INDEPENDENT_INSPECTION.json",
        "COST_LEDGER.json", "DIAGNOSTIC_ANALYSIS.json", "RESOURCE_ANALYSIS.json"]
    )
    assert "N6720398" in identity["workload"]
    assert state["formal_samples"] == 20 and len(inspection["states"]) == 3
    assert [s["next_step"] for s in inspection["states"]] == [15140, 15240, 15301]
    assert hashlib.sha256((args.inputs / "simple_trainer_hybrid_optimized.py").read_bytes()).hexdigest() == binary["original_source_CPUAdam"]["examples/simple_trainer_hybrid_optimized.py"]
    assert hashlib.sha256((args.inputs / "cpu_adam.cpp").read_bytes()).hexdigest() == binary["original_source_CPUAdam"]["cpu_adam/src/cpu_adam.cpp"]
    assert all(s["alias_groups"]["storage"] == [] for s in inspection["states"])

    # Each item is a distinct dense storage, not a checkpoint byte count.
    groups = {
        "gpu_existing_param": 10,
        "gpu_existing_moments": 20,
        "gpu_existing_grad_if_live": 10,
        "cpu_param": 49,
        "cpu_moments": 98,
        "cpu_grad": 49,
        "shN_param": 45,
        "shN_moments": 90,
        "shN_grad": 45,
    }
    byte_groups = {k: N * channels * F32 for k, channels in groups.items()}
    records = []
    for job in diag["jobs"]:
        tags = job["host_region_by_tag_seconds"]
        shn_forward = sum(v for k, v in tags.items() if k.startswith("cpu_parameter_forwarding_adam@L125") or k.startswith("cpu_parameter_forwarding_adam@L126"))
        # L1257/L1264/L1267: all shN chunks; other fields at L1277/L1287.
        total_forward = sum(v for k, v in tags.items() if k.startswith("cpu_parameter_forwarding_adam@"))
        records.append({"job": job["job"], "ON_seconds": job["closed_window_wall_seconds"],
                        "shN_forward_host_seconds": shn_forward,
                        "all_forward_host_seconds": total_forward,
                        "cpu_adam_host_seconds": tags["cpu_adam@L1069"]})
    for row in records:
        item = next(x for x in ledger["jobs"] if x["job"] == row["job"])
        assert abs(row["all_forward_host_seconds"] - item["CPU_parameter_forward_seconds"]) < 1e-8
        assert abs(row["cpu_adam_host_seconds"] - item["CPU_Adam_seconds"]) < 1e-8
    model = {
        "authority": {"Q1_execution_commit": "5787826ca21f7af958e6e1c1f828d62fd58a1ec4",
                      "accepted_review_commit": "06355f73caaa6f38697d9acac94ac81a47c27e62"},
        "scope": "late T16, N fixed; dense storage arithmetic only, not a measured live peak",
        "units": {"bytes": "B", "gib": "2^30 B", "time": "seconds per 51-camera ON diagnostic"},
        "N": N, "fp32_bytes": F32,
        "dense_unique_storage_bytes": byte_groups,
        "dense_unique_storage_GiB": {k: round(v / GIB, 6) for k, v in byte_groups.items()},
        "cpu_state_param_moments_grad_bytes": byte_groups["cpu_param"] + byte_groups["cpu_moments"] + byte_groups["cpu_grad"],
        "shN_resident_param_moments_bytes": byte_groups["shN_param"] + byte_groups["shN_moments"],
        "shN_resident_with_dense_grad_bytes": byte_groups["shN_param"] + byte_groups["shN_moments"] + byte_groups["shN_grad"],
        "counter_int8_bytes": N,
        "existing_observed_own_GPU_peak_MiB": [w["own_NVML_peak_MiB"] for w in resources["windows"]],
        "candidate_live_capacity_condition": "max_t [sum(bytes of distinct simultaneously live GPU storages at t) + allocator/framework reserve(t)] <= GPU capacity available under the current shared gate at t",
        "candidate_live_peak_bytes": None,
        "available_GPU_bytes_at_future_window": None,
        "old_CPU_and_new_GPU_copies_overlap_bytes": None,
        "pending_sparse_gradient_bytes": None,
        "raster_and_other_workspace_bytes": None,
        "allocator_reserve_bytes": None,
        "net_benefit_condition": "removed critical-path CPU/shN forwarding and required transfer service > new GPU deferred-update/forward work + index/metadata/conversion transfer + lost overlap + capacity side-effects",
        "removed_OFF_critical_path_seconds": None,
        "new_GPU_work_seconds": None,
        "lost_overlap_seconds": None,
        "ON_diagnostic_host_intervals": records,
        "interpretation": "ON host intervals bound candidate work location only; no subtraction from OFF, no cross-clock subtraction, no PCIe estimate from logical bytes"
    }
    (args.out / "FOOTPRINT_AND_CONDITIONS.json").write_bytes((json.dumps(model, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    rows = [
        ("means/scales/quats", "GPU", "current step", "GPU optimizer.step", "next GPU camera", "all N", "10 fp32/N params; 20 moments; grad conditional", "full resident", "trainer:314-340,716-719", "GPU grad lifetime"),
        ("opacities/sh0/shN", "CPU", "applied through t-1 + pending t", "deferred CPUAdam", "forward next visible V(t+1)", "during GPU t: U=V(t-1) union counter==15", "49 fp32/N params; 98 moments; 49 grad", "shN residency only", "trainer:1036-1069,1241-1288; cpu_adam.cpp:208-297,300-379", "GPU numerical qualification"),
        ("CPU moment step/counter", "CPU", "global step; per-ID int8 age", "step increment; update_counter", "deferred/forward correction", "U and all N counter", "3 scalar steps; N int8 counter", "must preserve", "trainer:1044-1067; cpu_adam.cpp:277-297,314-342", "counter GPU placement"),
        ("pending gradients", "GPU then CPU", "camera t pending until t+1", "D2H and scatter after join", "deferred update t+1", "V(t)", "GPU leaf grad; pinned subset; dense CPU grad", "retain exactly once", "trainer:1113-1157; state frontier", "sparse alternative bytes"),
        ("forwarded shN", "CPU pinned then GPU", "prepared camera t+1", "adam_for_next_with_counter + H2D", "raster t+1", "V(t+1)", "45 fp32/visible; pinned staging; GPU leaf", "candidate removed CPU staging", "trainer:1241-1268; cpu_adam.cpp:382-460", "GPU arithmetic/ordering"),
        ("forwarded sh0/opacity", "CPU pinned then GPU", "prepared camera t+1", "adam_for_next_with_counter + sigmoid opacity + H2D", "raster t+1", "V(t+1)", "4 fp32/visible plus temporary", "unchanged in candidate", "trainer:1270-1292", "temporary alias peaks"),
        ("visible IDs/metadata", "GPU and CPU", "camera dependent", "frustum + D2H + strategy metadata", "next forwarding/densification", "visible; all N scan for U", "ID and metadata buffers", "preserve", "trainer:1093-1106,1147-1157; cpu_adam.cpp:208-273", "natural ID trace missing"),
        ("raster/workspace", "GPU", "camera dependent", "renderer", "loss/backward", "visible", "distinct temporary storage unknown", "capacity liability", "trainer:669-728", "live storage peak unknown"),
    ]
    with (args.out / "STATE_SUPPLY_MAP.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["state_object", "owner", "version", "producer", "consumer", "update_set", "storage_alias_payload", "candidate_change", "fixed_source", "unknown"])
        writer.writerows(rows)

    sources = []
    for name in INPUTS:
        b = (args.inputs / name).read_bytes()
        source = ("frozen GS-Scale: " + ("examples/" if name.endswith("trainer_hybrid_optimized.py") else "cpu_adam/src/") + name) if name in ("simple_trainer_hybrid_optimized.py", "cpu_adam.cpp") else SOURCE_ROOT + ("windows/W2/" if name == "DIAGNOSTIC_ANALYSIS.json" else "") + name
        sources.append({"file": name, "fixed_source": source, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    (args.out / "SOURCES.json").write_bytes((json.dumps(sources, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"N": N, "shN_min_GiB": round(model["shN_resident_param_moments_bytes"] / GIB, 6), "shN_dense_GiB": round(model["shN_resident_with_dense_grad_bytes"] / GIB, 6), "ON": records}, ensure_ascii=False))


if __name__ == "__main__":
    main()
