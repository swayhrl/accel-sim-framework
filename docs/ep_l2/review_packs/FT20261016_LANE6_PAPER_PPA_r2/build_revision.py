#!/usr/bin/python3
"""Read-only evidence audit and compact r2 figure generation. No simulation."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REVIEW = "aec01450d3c527524ee09ee59242f582fafe5354"
ORIGINAL = "6c136e2a56a008695f8c8b815723bf8f1a760db9"
L1 = "02982b65e87f170103b44c6dbd562a8ffb03841e"
L4 = "96fbcb612773900fd75268ffe4e00ed9f13d3d42"
L5 = "221c7f65cd881ca5da2d20dd0f63a50e35bbc009"
LATEST1 = "2556909e55bb43c1d819f8c0417f5fc8b93630d9"
LATEST4 = "be21c95d9c846c9af0904d24c78c10c3243dc64b"
PAIRPUB = "b47b721d1be26210ffaea178fbbf3f5c839c2b9c"
PAIRQUAL = "2fc7cdcf18afb98c5e8434b87c4ef36316644098"
R0 = "126394be46b15f55b9756d43eb9ca9a9baae1c84"
RO = "ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5"
STREAM = "a38ce9c517ad49f88f5eaea74c73d4e5b23eb1c2"
ROOT = "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/"
DIAG = "docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def blob(repo, revision, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", revision + ":" + path])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--framework-repo", type=Path, required=True)
    p.add_argument("--core-repo", type=Path, required=True)
    p.add_argument("--streaming-worktree", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    out = a.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    sources = {}
    def take(key, repo, revision, path, kind):
        data = blob(repo, revision, path)
        sources[key] = {"commit": revision, "path": path, "sha256": sha(data),
                        "bytes": len(data), "kind": kind,
                        "repository": "swayhrl/gpgpu-sim" if repo == a.core_repo else "swayhrl/accel-sim-framework"}
        return data
    for f in ("REVIEW.md", "CONTINUE.md"):
        take("review:" + f, a.framework_repo, REVIEW, "docs/ep_l2/chatgpt_handoff/fast_track_2026_10_16_review_r2/" + f, "REVIEW_AUTHORITY")
    for lane, revision in ((1, L1), (4, L4), (5, L5)):
        take(f"lane{lane}_receipt", a.framework_repo, revision, ROOT + f"lane{lane}/RECEIPT.json", "DEPENDENCY_RECEIPT")
    for lane, revision in ((1, LATEST1), (4, LATEST4)):
        take(f"lane{lane}_continuation_receipt", a.framework_repo, revision, ROOT + f"lane{lane}/RECEIPT.json", "CONTINUATION_DEPENDENCY_RECEIPT")
    contract = json.loads(take("R0_contract", a.framework_repo, L1, ROOT + "lane1/BASELINE_CONTRACT_V1.json", "R0_PRODUCER_RELEASE"))
    take("R0_port_ledger", a.framework_repo, L1, ROOT + "lane1/STORAGE_AND_PORT_LEDGER.md", "R0_PRODUCER_MODEL")
    for f in ("gpu-cache.h", "ep-l2-ft-cache.inc", "ep-l2-ft-interface.h"):
        take("R0:" + f, a.core_repo, R0, "src/gpgpu-sim/" + f, "R0_PRODUCTION_SOURCE")
    take("RO_completion", a.core_repo, RO, "src/gpgpu-sim/ep-l2-ro-transactions.h", "MODULE_ONLY_NOT_R0")
    assert contract["runtime_ready"] is True and contract["independent_qualification"] is False
    qualified_bytes = take("R0_independent_qualification", a.framework_repo, L5, ROOT + "lane5/R0_INDEPENDENTLY_QUALIFIED.json", "INDEPENDENT_QUALIFICATION")
    qualified = json.loads(qualified_bytes)
    checks = take("R0_independent_checks", a.framework_repo, L5, "docs/ep_l2/review_packs/FT20261016_LANE5_R0_QUALIFICATION_r1/INDEPENDENT_CHECKS.json", "INDEPENDENT_QUALIFICATION")
    assert qualified["status"] == "INDEPENDENTLY_QUALIFIED"
    for key in ("core_source_commit", "framework_source_commit", "binary_sha256"):
        assert qualified[key] == contract[key]
    assert all(g["status"] == "PASS" and g["production_driven"] is True and g["evidence_sha256"] == sha(checks) for g in qualified["gates"].values())
    assert take("pair_qualification_publication", a.framework_repo, PAIRQUAL, ROOT + "lane5/R0_INDEPENDENTLY_QUALIFIED.json", "PAIR_RUNTIME_QUALIFICATION") == qualified_bytes
    take("lane5_pair_receipt", a.framework_repo, PAIRPUB, ROOT + "lane5/RECEIPT.json", "PAIR_PUBLICATION")
    pair_root = "docs/ep_l2/review_packs/FT20261016_LANE5_R0_SAD_PAIR_r1/"
    pair_raw = {}
    for f in ("RESULTS.csv", "PAIR_RECEIPT.json", "COMPARISON.json", "RESOURCE_MOVEMENT.csv", "SOURCE_MANIFEST.json"):
        pair_raw[f] = take("sad_pair:" + f, a.framework_repo, PAIRPUB, pair_root + f, "FUNCTIONAL_IMPLEMENTATION")
    from native_pair_intake import read_native_packet
    from result_intake import summarize
    adapter_path = Path(__file__).with_name("NATIVE_SAD_ADAPTER.json")
    adapter = json.loads(adapter_path.read_text())
    formal_packet = read_native_packet(a.framework_repo, adapter)
    formal_result = summarize(formal_packet)
    assert len(formal_result["pairs"]) == 1 and formal_result["pairs"][0]["workload"] == "sad"
    assert formal_result["whole_group_geomean"] is None
    formal_resources = list(csv.DictReader(io.StringIO(pair_raw["RESOURCE_MOVEMENT.csv"].decode())))
    assert len(formal_resources) == 2 and all(r["staged_max_across_slice_peaks"] == "1" and r["capacity_above_C16_observed"] == "False" for r in formal_resources)
    dump(out / "FORMAL_WB_PAIR_INPUTS.json", {"summary": formal_result, "runtime_packet": formal_packet,
         "resource_movement": formal_resources, "qualification_declared_by_producer": PAIRQUAL,
         "paper_intake_adapter_sha256": file_sha(adapter_path)})
    subprocess.run(["/usr/bin/python3", str(Path(__file__).with_name("plot_qualified_pairs.py")), str(adapter_path),
                    "--framework-repo", str(a.framework_repo), "--output-dir", str(out / "formal_sad")], check=True, capture_output=True)
    dump(out / "DEPENDENCY_SNAPSHOT.json", {"R0_producer_publication": L1, "lane1_continuation": LATEST1,
         "lane4_original_diagnostic": L4, "lane4_continuation": LATEST4, "lane5_publication": L5,
         "R0_independent_qualification": qualified, "lane5_pair_publication": PAIRPUB,
         "qualification_declared_by_pair_producer": PAIRQUAL, "new_formal_completed_pairs_consumed": 1,
         "R1_formal_diagnostic_completed_rows_consumed": 0})

    # Verify the 13-row local historical checkpoint against unchanged producer
    # per-run artifacts and the exact committed aggregation implementation.
    ck = a.streaming_worktree / "docs/ep_l2/review_packs/STREAMING_REUSE_CHARACTERIZATION_r1"
    source_path = "util/ep_l2/aggregate_streaming_reuse.py"
    tool = take("streaming_aggregator", a.streaming_worktree, STREAM, source_path, "HISTORICAL_TOOL")
    assert (a.streaming_worktree / source_path).read_bytes() == tool
    spec_import = importlib.util.spec_from_file_location("lane6_verified_streaming", a.streaming_worktree / source_path)
    mod = importlib.util.module_from_spec(spec_import)
    spec_import.loader.exec_module(mod)
    formal = json.loads((ck / "formal_spec.json").read_text())
    agg = json.loads((ck / "aggregation_manifest.json").read_text())
    assert agg["formal_spec_sha256"] == file_sha(ck / "formal_spec.json")
    assert agg["inputs"] == formal["rows"]
    original_rows = list(csv.DictReader((ck / "line_vs_sector_reuse.csv").open()))
    by_name = {r["workload"]: r for r in original_rows}
    assert len(original_rows) == len(by_name) == len(formal["expected_workloads"]) == 13
    status_rows = list(csv.DictReader((ck / "formal_workload_status.csv").open()))
    assert len(status_rows) == 13 and all(r["status"] == "COMPLETE_VALID" for r in status_rows)
    verification, plot_rows = [], []
    for spec in formal["rows"]:
        s, distance, coverage, m = mod.validate(spec, formal)
        name = spec["workload"]
        computed = {"line_reuse_fraction": int(m["reuse_instances"]) / int(m["eligible_demand_references"]),
                    "sector_temporal_reuse_fraction": float(s["sector_temporal_reuse_fraction"]),
                    "spatial_new_sector_fraction": float(s["spatial_new_sector_fraction"]),
                    "one_touch_sector_fraction": float(s["one_touch_sector_fraction"])}
        for key, val in computed.items():
            assert abs(float(by_name[name][key]) - val) < 1e-12, (name, key)
        run = Path(spec["on_result_dir"])
        status = json.loads((run / "run_status.json").read_text())
        proof = {"workload": name, "core_source_commit": status["core_commit"],
                 "framework_source_commit": status["framework_commit"], "config_sha256": status["config_sha256"],
                 "binary_sha256": status.get("binary_sha256"), "binary_binding_scope": "HISTORICAL_MANIFEST_NOT_NEW_R0_RUN_KEY",
                 "status": status["status"], "raw_log_sha256": file_sha(run / "raw.log"), "files": {}}
        for rel in ("run_status.json", "sector/manifest.json", "motivation/manifest.json",
                    "sector/sector_reuse_summary.csv", "sector/sector_reuse_distance.csv", "motivation/motivation_summary.csv"):
            proof["files"][rel] = {"path": str(run / rel), "sha256": file_sha(run / rel)}
        verification.append(proof)
        plot_rows.append({"workload": name, **computed})
    ck_files = {f: {"path": str(ck / f), "sha256": file_sha(ck / f)}
                for f in ("formal_spec.json", "aggregation_manifest.json", "line_vs_sector_reuse.csv", "formal_workload_status.csv", "raw_log_index.csv")}
    dump(out / "STREAMING13_VERIFICATION.json", {"status": "PASS_HISTORICAL_LOCALITY_ONLY", "row_count": 13,
         "checkpoint_inputs": ck_files, "aggregator": sources["streaming_aggregator"],
         "verification_scope": "Original aggregator validation, raw hashes, exact numeric row reconstruction; no simulator rerun",
         "rows": verification})

    # Keep the executed historical pair's actual identities, rather than the
    # later Lane-4 build candidate's different binary and source.
    diag_rows = list(csv.DictReader(io.StringIO(take("diagnostic_csv", a.framework_repo, L4, DIAG + "CEILING_RESULTS.csv", "HISTORICAL_DIAGNOSTIC").decode())))
    take("diagnostic_build", a.framework_repo, L4, DIAG + "BUILD_MANIFEST.json", "LATER_CANDIDATE_NOT_PAIR_RUNTIME")
    take("diagnostic_limiter", a.framework_repo, L4, DIAG + "LIMITER_MOVEMENT.csv", "HISTORICAL_DIAGNOSTIC")
    completed = [r for r in diag_rows if r["status"] == "COMPLETE_VALID"]
    assert len(completed) == 2
    diag_verified = []
    for row in completed:
        r = Path(row["result_directory"])
        st = json.loads((r / "run_status.json").read_text())
        spec = json.loads((r / "input_spec.json").read_text())
        summary = json.loads((r / "reparsed_summary_r1.json").read_text())
        ident = st["identity"]
        assert ident == spec["identity"]
        assert sha(json.dumps(ident, sort_keys=True, separators=(",", ":")).encode()) == row["run_key"]
        for key in ("core_source_commit", "framework_source_commit", "binary_sha256", "runtime_config_sha256", "trace_content_sha256"):
            assert ident[key] == row[key]
        assert st["status"] == "COMPLETE_VALID" and st["exit_code"] == 0
        assert summary["raw_log_sha256"] == st["raw_log_sha256"] == file_sha(r / "raw.log")
        assert int(row["cycles"]) == summary["summary"]["cycles"]
        assert int(row["instructions"]) == summary["summary"]["instructions"]
        assert summary["summary"]["terminal_64_slice_closure"] == "PASS"
        files = {rel: {"path": str(r / rel), "sha256": file_sha(r / rel)} for rel in
                 ("run_status.json", "input_spec.json", "input_audit.json", "reparsed_summary_r1.json")}
        diag_verified.append({"csv_row": row, "identity": ident, "runtime_manifests": files,
                              "raw_log_sha256": st["raw_log_sha256"], "summary": summary["summary"]})
    b, c = diag_verified
    assert b["csv_row"]["mode"] == "OFF" and c["csv_row"]["mode"] == "I_READ_HIT"
    for key in ("core_source_commit", "framework_source_commit", "binary_sha256", "trace_content_sha256", "epoch_range", "feature_vector"):
        assert b["identity"][key] == c["identity"][key]
    assert b["identity"]["feature_vector"]["payload_capacity_per_slice"] == 1152
    speedup = int(b["csv_row"]["cycles"]) / int(c["csv_row"]["cycles"])
    assert abs(speedup - 1.7212591453469406) < 1e-12
    dump(out / "HISTORICAL_DIAGNOSTIC_VERIFICATION.json", {"status": "PASS_HISTORICAL_DIAGNOSTIC_ONLY", "rows": diag_verified, "speedup_single_workload": speedup})

    # Raw data + physically common latch, never an extra allocatable payload slot.
    ppa = []
    for n in (1160, 1168):
        for g in (8, 16, 32):
            ppa.append({"payload_slots": n, "generation_bits_assumption": g,
                        "data_bits_per_slice": n * 1024, "common_copy_latch_bits_per_slice": 1024,
                        "array_plus_latch_mib_chip": (n + 1) / 128,
                        "payload_id_bits": 11, "tag_pointer_bits": 1024 * 11,
                        "wb_handle_known_fields_bits_128_controls": 128 * (11 + g),
                        "ro_R0_enabled_completion_slots": 0, "ro_r3_module_configured_completion_slots": n,
                        "ro_completion_illustrative_known_field_bits_per_entry": 41 + 16 + 11 + g + 1 + 10 + g + 16 + 26,
                        "ro_completion_illustrative_known_field_bits": n * (41 + 16 + 11 + g + 1 + 10 + g + 16 + 26),
                        "not_total_area": True})
    dump(out / "PPA_BITS.json", {"rows": ppa, "source_R0": R0, "RO_module_source": RO,
         "unknowns": ["generation safety bound", "pin maximum", "packet binding/state", "RO ordering/response fields", "matched RTL", "process/SRAM macros/ports/constraints"],
         "area_mm2": None, "power_mw": None, "fmax_mhz": None})

    plt.rcParams.update({"font.size": 7.5, "svg.fonttype": "none", "svg.hashsalt": "EP_L2_LANE6_R2",
                         "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    def save(fig, name):
        fig.tight_layout(pad=.6)
        for ext in ("svg", "pdf"):
            dest = out / "figures" / (name + "." + ext)
            fig.savefig(dest, metadata={"Date": None} if ext == "svg" else {"CreationDate": None, "ModDate": None})
            if ext == "svg":
                dest.write_text("\n".join(x.rstrip() for x in dest.read_text().splitlines()) + "\n")
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    ax.bar([0, 1], [73873, 42918], color=["#8b9da8", "#336b8e"], width=.55)
    ax.set_xticks([0, 1], ["Old static OFF", "Optimistic read"])
    ax.set_ylim(0, 89000)
    ax.set_ylabel("Application cycles")
    for i, y in enumerate((73873, 42918)):
        ax.text(i, y + 1800, f"{y:,}", ha="center")
    ax.text(.98, .97, "1.721259×\nvectorAdd only", transform=ax.transAxes, va="top", ha="right", fontsize=7)
    ax.set_title("Historical diagnostic (1152 slots)", fontsize=8)
    save(fig, "FIG02_HISTORICAL_OPTIMISTIC_READ")
    selected = ["convolutionSeparable", "FWT_7_21", "cfd_097k", "vectorAdd_4M", "sad", "btree", "dwt2d", "scan"]
    lookup = {r["workload"]: r for r in plot_rows}
    fig, ax = plt.subplots(figsize=(3.35, 3.05))
    ys = list(range(len(selected)))
    ax.barh([y - .18 for y in ys], [100 * lookup[w]["line_reuse_fraction"] for w in selected], height=.34, label="Same-line (incl. spatial)", color="#a2b9c9")
    ax.barh([y + .18 for y in ys], [100 * lookup[w]["sector_temporal_reuse_fraction"] for w in selected], height=.34, label="Exact-sector temporal", color="#336b8e")
    ax.set_yticks(ys, ["convolution" if w == "convolutionSeparable" else w for w in selected])
    ax.invert_yaxis()
    ax.set_xlim(0, 103)
    ax.set_xlabel("Eligible demand references (%)")
    ax.legend(frameon=False, fontsize=6.7, loc="lower left", bbox_to_anchor=(0, 1.01), borderaxespad=0)
    ax.set_title("Historical locality (8 of 13 verified)", fontsize=8, pad=30)
    save(fig, "FIG03_VERIFIED_SECTOR_LOCALITY")
    dump(out / "RESULT_COVERAGE.json", {"R0_formal_completed_pairs_consumed": 1, "R1_B16_ideal_completed_rows_consumed": 0,
         "historical_diagnostic_completed_rows": 2, "historical_streaming_completed_rows": 13,
         "upstream_missing_diagnostic_rows": [r for r in diag_rows if r["status"] != "COMPLETE_VALID"],
         "R0_release_status": "INDEPENDENTLY_QUALIFIED_B16_U_WB16_ONLY",
         "implementation_workloads": [{"workload": w, "state": "COMPLETE_VALID" if w == "sad" else "AWAITING_COMPLETED_LANE5_PAIR",
                                       "speedup": formal_result["pairs"][0]["speedup"] if w == "sad" else None} for w in selected[:5]],
         "whole_group_geomean": None, "does_not_assert_current_remote_process_state": True})
    producer = subprocess.check_output(["git", "-C", str(a.framework_repo), "rev-parse", "HEAD"], text=True).strip()
    generator_rel = str(Path(__file__).resolve().relative_to(a.framework_repo.resolve()))
    assert blob(a.framework_repo, producer, generator_rel) == Path(__file__).read_bytes(), "Commit generator before producing evidence"
    dump(out / "SOURCE_EVIDENCE_MANIFEST.json", {"review_authority": REVIEW, "scientific_contract": ORIGINAL,
         "generator_source_commit": producer, "generator_path": generator_rel, "generator_sha256": file_sha(__file__), "sources": sources})
    dump(out / "FIGURE_INPUT_MANIFEST.json", {"generator_source_commit": producer, "sources": sources,
         "historical_diagnostic": diag_verified, "streaming13": {"evidence_kind": "HISTORICAL_LOCALITY_OBSERVATION", "rows": plot_rows, "selected_predeclared_order": selected},
         "figures": {"FIG02_HISTORICAL_OPTIMISTIC_READ": {"kind": "HISTORICAL_DIAGNOSTIC", "not_B16_or_EP_L2_speedup": True, "strict_upper_bound": False},
                     "FIG03_VERIFIED_SECTOR_LOCALITY": {"kind": "HISTORICAL_LOCALITY_OBSERVATION", "TVD_hits_or_borrowing_inferred": False},
                     "formal_sad/WB_PAIRS": {"kind": "FUNCTIONAL_IMPLEMENTATION", "complete_pairs": 1, "whole_group_geomean": None}},
         "implementation_results": formal_result["pairs"], "new_B16_ideal_results": []})
    print(json.dumps({"historical_streaming_rows_verified": 13, "diagnostic_rows_verified": 2, "missing_diagnostic_rows_retained": len(diag_rows) - 2,
                      "sources": len(sources), "figures": 3, "ppa_scenarios": len(ppa), "R0_formal_pairs": 1}))


if __name__ == "__main__":
    main()
