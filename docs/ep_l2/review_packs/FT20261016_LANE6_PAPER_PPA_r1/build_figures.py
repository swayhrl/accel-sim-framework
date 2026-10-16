#!/usr/bin/python3
"""Render pinned historical evidence and design-budget figures; never run a simulator."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COORD = "6c136e2a56a008695f8c8b815723bf8f1a760db9"
CAL = "aa44f9e8d685b6f9bbe410b996e07ef185a8de96"
MAIN = "b7dbdecb94054f08aaf2e33bfef48e453747ceb5"
STREAM = "cdab5765b65f6e1575d9c185de127a1c1c49dd70"
M1 = "c0a71e204715289895028d27ac82190041d83b85"
M0B = "7ad2b240fee32492e778611cb6deb45516c29bcf"
M3A = "4f198e307361a2a5e4a38b4db478c5165f89752d"
CORE = "1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e"
LANE1 = "cb7d92e4edde97e81520cfdd00762dfe81ee9b20"
LANE4 = "1657e77020321e0095acb2e7922056b27d8edf50"
LANE5 = "cc97ee2ad9feb4ff57482cb7d826a53a3a4d07a0"
PREFIX = "docs/ep_l2/review_packs/"
SOURCES = [
    ("contract", COORD, "docs/ep_l2/chatgpt_handoff/fast_track_2026_10_16_v1/COMMON_CONTRACT.md", "CONTRACT_DEFINED"),
    ("cal_matrix", CAL, PREFIX + "FINAL_CALIBRATION_CONVERGENCE_r1/CALIBRATION_MATRIX_FINAL.csv", "HISTORICAL_CALIBRATION"),
    ("cal_delta", CAL, PREFIX + "FINAL_CALIBRATION_CONVERGENCE_r1/CALIBRATION_DELTAS_FINAL.csv", "HISTORICAL_CALIBRATION"),
    ("cal_manifest", CAL, PREFIX + "FINAL_CALIBRATION_CONVERGENCE_r1/ANALYSIS_MANIFEST.json", "HISTORICAL_CALIBRATION"),
    ("conv", MAIN, PREFIX + "LINE_MSHR_CAUSALITY_r1/CONVOLUTION_2X2.csv", "HISTORICAL_CALIBRATION"),
    ("conv_config", MAIN, PREFIX + "LINE_MSHR_CAUSALITY_r1/CONFIG_DIFF.csv", "HISTORICAL_CALIBRATION"),
    ("sector", STREAM, PREFIX + "STREAMING_REUSE_PREFINAL_r1/line_vs_sector_reuse.csv", "SHADOW_OBSERVATION"),
    ("sector_validation", STREAM, PREFIX + "STREAMING_REUSE_PREFINAL_r1/VALIDATION_SUMMARY.md", "SHADOW_OBSERVATION"),
    ("m1_pairs", M1, PREFIX + "M1_ELASTIC_SUBSTRATE_r1/PARENT_EQUIVALENCE.csv", "HISTORICAL_CALIBRATION"),
    ("m1_bits", M1, PREFIX + "M1_ELASTIC_SUBSTRATE_r1/METADATA_STORAGE_ACCOUNTING.md", "HISTORICAL_SOURCE"),
    ("m0b_dirty", M0B, PREFIX + "M0B_OPPORTUNITY_PREFINAL_9OF10_r1/DIRTY_VICTIM_TVD_PREMISE_9OF10.csv", "SHADOW_OBSERVATION"),
    ("m3a", M3A, "docs/ep_l2/codex_handoff/LANE_M3A_LATEST.md", "HISTORICAL_SOURCE"),
    ("lane1_interface", LANE1, "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/INTERFACE_CONTRACT_V1.md", "INTERFACE_PUBLISHED_RUNTIME_PENDING"),
    ("lane1_baseline", LANE1, "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/BASELINE_CONTRACT_V1.json", "INTERFACE_PUBLISHED_RUNTIME_PENDING"),
    ("lane1_receipt", LANE1, "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/RECEIPT.json", "INTERFACE_PUBLISHED_RUNTIME_PENDING"),
    ("lane4_receipt", LANE4, "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane4/RECEIPT.json", "DEPENDENCY_PENDING"),
    ("lane5_receipt", LANE5, "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/RECEIPT.json", "DEPENDENCY_PENDING"),
]


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def read_blob(repo, revision, path):
    data = git(repo, "show", revision + ":" + path)
    blob = git(repo, "rev-parse", revision + ":" + path).decode().strip()
    return data, {"commit": revision, "path": path, "git_blob_sha1": blob,
                  "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def budgets():
    return [{"mode": name, "slots_per_slice": n, "banks": 4,
             "rows_per_bank": n // 4, "data_bits_per_slice": n * 1024,
             "data_bytes_per_slice": n * 128, "data_kib_per_slice": n / 8,
             "data_mib_chip": n * 128 * 64 / 2**20, "payload_id_bits": math.ceil(math.log2(n)),
             "max_line_ops_per_bank_cycle": 1}
            for name, n in [("OLD_D512_STATIC", 1152), ("B8 / U_WB8", 1160), ("B16 / U_WB16", 1168)]]


def storage_scenarios():
    rows = []
    for c in (8, 16):
        n = 1152 + c
        for g in (8, 16, 32):
            parts = {
                "tag_pointer_bits": 1024 * 11,
                "tag_generation_bits": 1024 * g,
                "payload_explicit_state_bits": n * (4 + 12 + 6 + g),
                "descriptor_next_and_valid_common_bits": 512 * 10,
                "normal_chain_common_bits": 128 * 26,
                "ro_completion_known_fields_bits": 128 * (41 + 16 + 11 + g + 1 + 10 + g + 16 + 26),
                "wad_tvd_pointer_generation_bits": 128 * (11 + g),
                "tvd_role_sector_age_pin_bits": 128 * 20,
                "allocator_bitmap_bits": n,
                "role_conservation_counters_bits": 10 * math.ceil(math.log2(n + 1)),
                "bank_metadata_queue_bits": 4 * 8 * (11 + g + 3 + 8 + 1),
            }
            rows.append({"wbuf_c": c, "slots": n, "generation_bits_assumed": g,
                         "scenario_only": "NOT_AN_IMPLEMENTATION_OR_AREA_ESTIMATE",
                         **parts,
                         "illustrative_subtotal_bits_excluding_unknowns": sum(parts.values()),
                         "unknowns_excluded": "routing/request_id/order/response/ECC/oracle/Tag_base/lower_data_queues/logic/wires"})
    return rows


def save(fig, out, name, caption, metadata):
    fig.text(0.01, 0.012, caption, fontsize=7, va="bottom")
    fig.subplots_adjust(bottom=0.22)
    for suffix in ("svg", "pdf"):
        target = out / "figures" / (name + "." + suffix)
        # No creation time in PDF/SVG metadata: repeated runs have stable content.
        meta = {"Date": None} if suffix == "svg" else {"CreationDate": None, "ModDate": None}
        fig.savefig(target, metadata=meta, bbox_inches="tight")
        if suffix == "svg":
            target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
    plt.close(fig)
    metadata[name] = {"caption": caption, "outputs": ["figures/" + name + ".svg", "figures/" + name + ".pdf"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework-repo", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--core-repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    producer_commit = git(args.framework_repo, "rev-parse", "HEAD").decode().strip()
    repo_root = Path(git(args.framework_repo, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    generator_path = str(Path(__file__).resolve().relative_to(repo_root))
    committed_generator, generator_record = read_blob(args.framework_repo, producer_commit, generator_path)
    if committed_generator != Path(__file__).read_bytes():
        raise ValueError("Freeze the generator source commit before producing evidence")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "svg.hashsalt": "EP_L2_LANE6_V1",
                         "axes.spines.top": False, "axes.spines.right": False})
    raw, records = {}, {}
    for key, revision, path, kind in SOURCES:
        raw[key], record = read_blob(args.framework_repo, revision, path)
        records[key] = {**record, "repository": "swayhrl/accel-sim-framework", "evidence_kind": kind}
    for path in ["src/gpgpu-sim/gpu-cache.h", "src/gpgpu-sim/gpu-cache.cc",
                 "src/gpgpu-sim/l2cache.h", "src/gpgpu-sim/l2cache.cc",
                 "tests/ep_l2/run_descriptor_mshr_integrated.sh", "tests/ep_l2/test_payload_sector_lifetime.cc"]:
        # Exact source assets are required; a missing file is an error, not an empty anchor.
        _, record = read_blob(args.core_repo, CORE, path)
        records["core:" + path] = {**record, "repository": "swayhrl/gpgpu-sim", "evidence_kind": "HISTORICAL_SOURCE"}
    def table(key):
        return list(csv.DictReader(io.StringIO(raw[key].decode())))
    matrix = table("cal_matrix")
    if len(matrix) != 80 or json.loads(raw["cal_manifest"])["matrix_records"] != 80:
        raise ValueError("Historical convergence cardinality changed")
    delta = [r for r in table("cal_delta") if r["comparison"] == "D256_BASE_TO_D512_BASE" and r["variant"] == "B0-Banked"]
    if len(delta) != 13 or len({r["workload"] for r in delta}) != 13:
        raise ValueError("Must retain all thirteen historical Banked workloads")
    conv = table("conv")
    if len(conv) != 4 or any(r["run_status"] != "COMPLETE_VALID" for r in conv):
        raise ValueError("Historical Line-MSHR rows are not complete")
    sector = table("sector")
    if len(sector) != 12 or any(r["workload"] == "scan" for r in sector):
        raise ValueError("Only the exact twelve archival prefinal sector rows may enter this figure")
    budget = budgets()
    scenario = storage_scenarios()
    write_csv(out / "DATA_BUDGET.csv", budget)
    write_csv(out / "PPA_STORAGE_SCENARIOS.csv", scenario)
    write_json(out / "PPA_BITS.json", {"status": "PARAMETERIZED_RAW_BITS_ONLY", "data_budget": budget,
               "tag_pointer_bits_per_slice": 11264, "wad_pointer_bits_per_slice": 1408,
               "known_logic_widths": {"descriptor_index": 9, "explicit_requester_count_0_through_32": 6},
               "generation_width": None, "area_mm2": None, "power_mw": None, "fmax_mhz": None,
               "scenario_count": len(scenario), "no_matched_candidate_rtl": True})
    figmeta = {}
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.bar(range(3), [b["data_kib_per_slice"] for b in budget], color=["#a0a0a0", "#72a9cf", "#3b6f8f"])
    ax.set_xticks(range(3), [b["mode"] for b in budget])
    ax.set_ylabel("Raw payload data (KiB / slice)")
    ax.set_ylim(0, 162)
    for i, b in enumerate(budget):
        ax.text(i, b["data_kib_per_slice"] + 2, f'{b["data_kib_per_slice"]:g} KiB; {b["slots_per_slice"]} slots', ha="center", fontsize=8)
    ax.set_title("Design budget: static and unified have equal data capacity")
    save(fig, out, "FIG02_DATA_BUDGET", "CONTRACT_DEFINED; raw data bits only. Metadata, queue data, ports and logic are accounted separately.", figmeta)
    figmeta["FIG02_DATA_BUDGET"].update({"source_keys": ["contract"], "evidence_kind": "CONTRACT_DEFINED"})
    fig, ax = plt.subplots(figsize=(9.2, 4.0))
    values = [(float(r["speedup"]) - 1) * 100 for r in delta]
    ax.bar(range(13), values, color=["#3b6f8f" if v >= 0 else "#bd765d" for v in values])
    ax.axhline(0, color="black", linewidth=.6)
    ax.set_xticks(range(13), [r["workload"].replace("convolutionSeparable", "convolution") for r in delta], rotation=35, ha="right")
    ax.set_ylabel("(D256 cycles / D512 cycles − 1) × 100 (%)")
    ax.set_ylim(-.95, .15)
    ax.set_title("Historical descriptor calibration — every Banked workload")
    save(fig, out, "FIG03_HISTORICAL_D512", "HISTORICAL_CALIBRATION: 1152-slot model. These are not B16/U_WB16 results; zero and slowdowns retained.", figmeta)
    figmeta["FIG03_HISTORICAL_D512"].update({"source_keys": ["cal_matrix", "cal_delta", "cal_manifest"], "evidence_kind": "HISTORICAL_CALIBRATION", "row_count": 13})
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.5))
    labels = [r["label"].replace("_", "\n") for r in conv]
    for ax, key, ylabel, scale in [(axes[0], "cycles", "Application cycles (thousands)", 1000),
                                    (axes[1], "line_mshr_full_block", "Line-MSHR-full events (thousands)", 1000)]:
        values = [int(r[key]) / scale for r in conv]
        ax.bar(range(4), values, color=["#999999", "#aaaaaa", "#3b6f8f", "#72a9cf"])
        ax.set_xticks(range(4), labels)
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, max(values) * 1.2)
        for i, r in enumerate(conv):
            ax.text(i, values[i] + max(values) * .03, f'{int(r[key]):,}', ha="center", fontsize=8)
    fig.suptitle("Historical convolution: removing MSHR-full is not a system ceiling")
    save(fig, out, "FIG04_HISTORICAL_MSHR", "HISTORICAL_CALIBRATION: D512 M128→M256 gives 292211 / 291108 = 1.003789×; lower-path constraints remain.", figmeta)
    figmeta["FIG04_HISTORICAL_MSHR"].update({"source_keys": ["conv", "conv_config"], "evidence_kind": "HISTORICAL_CALIBRATION", "row_count": 4})
    fig, ax = plt.subplots(figsize=(9.2, 4.1))
    xs = list(range(len(sector)))
    ax.bar([x - .18 for x in xs], [100 * float(r["line_reuse_fraction"]) for r in sector], width=.36, label="Same-line reuse (includes spatial)", color="#a2b9c9")
    ax.bar([x + .18 for x in xs], [100 * float(r["sector_temporal_reuse_fraction"]) for r in sector], width=.36, label="Exact-sector temporal reuse", color="#3b6f8f")
    ax.set_xticks(xs, [r["workload"].replace("convolutionSeparable", "convolution") for r in sector], rotation=35, ha="right")
    ax.set_ylabel("Fraction of eligible references (%)")
    ax.set_ylim(0, 112)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title("Archived prefinal observation — 12 rows; scan excluded")
    save(fig, out, "FIG05_ARCHIVAL_SECTOR_REUSE", "SHADOW_OBSERVATION; fixed-stream locality. Neither TVD hits nor borrowing performance is inferred.", figmeta)
    figmeta["FIG05_ARCHIVAL_SECTOR_REUSE"].update({"source_keys": ["sector", "sector_validation"], "evidence_kind": "SHADOW_OBSERVATION", "row_count": 12,
        "runtime_framework_commit": "db1c90182fad02aacbd282b67ecdc57b8e4cc365", "core_commit": "ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919"})
    write_json(out / "SOURCE_EVIDENCE_MANIFEST.json", {"schema": "EP_L2_LANE6_SOURCE_EVIDENCE_V1", "coordination_commit": COORD,
        "generator_source": generator_record, "records": records, "new_implementation_results_consumed": 0, "new_ideal_results_consumed": 0})
    write_json(out / "DEPENDENCY_SNAPSHOT.json", {"coordination_commit": COORD,
        "lane1": {"publication_commit": LANE1, "runtime_ready": json.loads(raw["lane1_baseline"])["runtime_ready"],
                  "core_interface_source": "4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617", "receipt": records["lane1_receipt"]},
        "lane4": {"publication_commit": LANE4, "receipt": records["lane4_receipt"], "result_manifest": None},
        "lane5": {"publication_commit": LANE5, "receipt": records["lane5_receipt"], "result_manifest": None},
        "new_runtime_binary": None, "new_runtime_config": None, "new_results_consumed": 0})
    write_json(out / "FIGURE_INPUT_MANIFEST.json", {"schema": "EP_L2_LANE6_FIGURE_INPUT_V1", "coordination_commit": COORD,
        "generator_source": generator_record, "figures": figmeta, "source_records": records, "implementation_results": [], "ideal_results": [],
        "missing_results": "DEPENDENCY_PENDING_LANE4_LANE5", "excluded_local_unarchived_streaming_rows": True})
    print(json.dumps({"figures": len(figmeta), "scenarios": len(scenario), "source_blobs": len(records),
                      "historical_new_model_substitution": False, "output_dir": str(out)}, sort_keys=True))


if __name__ == "__main__":
    main()
