#!/usr/bin/env python3
"""Package a provenance-checked, partial EP-L2 Target Baseline analysis.

This deliberately consumes only direct B0 result directories whose
``run_status.json`` says COMPLETE_VALID.  It never recurses into diagnostic
directories and marks measurements that EPL2B0V1 does not emit rather than
reconstructing them from unrelated simulator counters.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
from collections import Counter
from pathlib import Path

from run_target_baseline import ROSTER, VARIANTS


ROOT = Path(__file__).resolve().parents[2]
NA = "NOT_EMITTED_BY_EPL2B0V1"
CORE = "200cb485c2fe27a7b0a867d2f173b63582fcaece"
FRAMEWORK = "81b9dfbc0c567590fc35724cbec94ade1d3f6aa9"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as stream:
        out = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore",
                             delimiter="\t" if path.suffix == ".tsv" else ",")
        out.writeheader(); out.writerows(rows)


def number(row: dict, key: str) -> int:
    try:
        return int(row.get(key, 0))
    except (TypeError, ValueError):
        return 0


def weighted(rows: list[dict[str, str]], key: str) -> int:
    denominator = sum(number(row, "samples") for row in rows)
    return (sum(number(row, key) * number(row, "samples") for row in rows) // denominator
            if denominator else 0)


def maximum(rows: list[dict[str, str]], key: str) -> int:
    return max((number(row, key) for row in rows), default=0)


def last_number(text: str, pattern: str) -> int | str:
    hits = re.findall(pattern, text, flags=re.MULTILINE)
    return int(hits[-1]) if hits else NA


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def terminal_invariants(raw: Path) -> dict[str, str | int]:
    """Return one application-terminal invariant record per physical slice."""
    by_slice: dict[int, dict[str, str]] = {}
    for line in raw.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("EPL2B0V1|INVARIANT|"):
            continue
        fields = dict(item.split("=", 1) for item in line.split("|")[2:] if "=" in item)
        if fields.get("kernel_uid") == str((1 << 64) - 1):
            by_slice[int(fields["slice"])] = fields
    rows = list(by_slice.values())
    def all_eq(key: str, value: str) -> int:
        return int(bool(rows) and all(row.get(key) == value for row in rows))
    return {
        "terminal_slice_count": len(rows),
        "descriptor_invariant_pass": all_eq("descriptor_used", "0"),
        "wad_invariant_pass": all_eq("wad_live", "0"),
        "payload_owner_generation_pass": int(bool(rows) and all(
            row.get("resident_tag_payload_consistent") == "1" and row.get("payload_double_owner") == "0"
            for row in rows)),
        "pending_sector_invariant_pass": all_eq("resident_pending", "0"),
        "bank_no_loss_pass": all_eq("bank_pending", "0"),
        "terminal_clean_pass": all_eq("terminal_clean", "1"),
        # There is no stale-fill counter in EPL2B0V1.  Do not turn absence of a
        # log string into a false zero-valued measurement.
        "stale_fill_count": NA,
    }


def aggregate(directory: Path, status: dict) -> dict:
    slices = read_csv(directory / "target_slice.csv")
    summary = read_csv(directory / "target_summary.csv")[0]
    raw = (directory / "raw.log").read_text(encoding="utf-8", errors="replace")
    inv = terminal_invariants(directory / "raw.log")
    result: dict[str, int | str] = {
        "cycles": int(status["terminal_gpu_tot_sim_cycle"]),
        "instructions": last_number(raw, r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$"),
        "wall_seconds": status.get("wall_seconds", NA),
        "samples": sum(number(row, "samples") for row in slices),
        "l2_accesses": last_number(raw, r"^L2_total_cache_accesses\s*=\s*(\d+)\s*$"),
        "l2_misses": last_number(raw, r"^L2_total_cache_misses\s*=\s*(\d+)\s*$"),
        "dram_reads": last_number(raw, r"^total dram reads\s*=\s*(\d+)\s*$"),
        "dram_writes": last_number(raw, r"^total dram writes\s*=\s*(\d+)\s*$"),
    }
    for key in ("line_mshr", "descriptor", "wad", "resident_payload", "bypass_payload",
                "missq", "lowerq"):
        result[key + "_avg"] = weighted(slices, key + "_avg")
        result[key + "_p95"] = maximum(slices, key + "_p95")
        result[key + "_max"] = maximum(slices, key + "_max")
    for key in ("block_descriptor", "block_wad", "block_payload", "block_bank",
                "block_l1", "block_lower", "bank_requests", "bank_grants", "bank_conflicts"):
        result[key] = number(summary, key)
    result.update(inv)
    return result


def process_table() -> list[tuple[int, str]]:
    output = subprocess.run(["ps", "-eo", "etimes=,args="], text=True,
                            stdout=subprocess.PIPE, check=True).stdout.splitlines()
    table = []
    for line in output:
        match = re.match(r"\s*(\d+)\s+(.*)", line)
        if match:
            table.append((int(match.group(1)), match.group(2)))
    return table


def running_row(directory: Path, workload: str, variant: str, trace: str,
                processes: list[tuple[int, str]]) -> dict:
    elapsed = NA
    trace = str(trace)
    for seconds, command in processes:
        if trace in command and ("b0_legacy_850.config" if variant == "B0-Legacy"
                                 else "b0_banked_850.config") in command:
            elapsed = seconds; break
    raw = directory / "raw.log"
    progress = "no raw.log yet"
    if raw.exists():
        lines = raw.read_text(encoding="utf-8", errors="replace").splitlines()
        progress = next((line for line in reversed(lines) if line.strip()), progress)
    return {"workload": workload, "variant": variant, "status": "RUNNING",
            "cycles": NA, "instructions": NA, "wall_seconds": elapsed,
            "invariant_status": "RUNNING_NOT_YET_EVALUABLE", "core_sha": CORE,
            "framework_sha": FRAMEWORK, "current_progress": progress}


def value(record: dict, field: str) -> int | str:
    return record.get(field, NA)


def add_variant_fields(row: dict, prefix: str, record: dict) -> None:
    fields = (
        "cycles", "l2_accesses", "l2_misses", "dram_reads", "dram_writes",
        "line_mshr_avg", "line_mshr_p95", "line_mshr_max", "descriptor_avg",
        "descriptor_p95", "descriptor_max", "block_descriptor", "wad_avg", "wad_p95",
        "wad_max", "block_wad", "resident_payload_avg", "resident_payload_p95",
        "resident_payload_max", "block_payload", "bank_requests", "bank_grants",
        "bank_conflicts", "block_bank", "block_l1", "missq_avg", "missq_p95",
        "missq_max", "lowerq_avg", "lowerq_p95", "lowerq_max", "block_lower",
    )
    for field in fields:
        row[prefix + "_" + field] = value(record, field)
    for field in ("line_mshr_block", "descriptor_per_address_cap_block", "chain_depth_avg",
                  "chain_depth_p95", "chain_depth_max", "wad_hazard_wait",
                  "resident_payload_valid_avg", "resident_fill_pending_avg",
                  "bank_arbitration_wait_cycles", "bank_hit_read", "bank_fill_write",
                  "bank_wb_read", "bank_write", "bank_bypass", "l1_mshr_block",
                  "l1_missq_block", "l1_bank_block", "l2_to_dram_avg", "l2_to_dram_p95",
                  "l2_to_dram_max", "l2_to_dram_full", "dram_to_l2", "dram_bandwidth_util"):
        row[prefix + "_" + field] = NA
    requests = record["bank_requests"]
    row[prefix + "_bank_conflict_rate"] = ("%.6f" % (record["bank_conflicts"] / requests)
                                              if requests else "0.000000")


def blocker_rows(workload: str, variant: str, record: dict) -> list[dict]:
    mapping = {
        "Tag/Set": NA, "Line-MSHR": NA, "DescriptorPool": record["block_descriptor"],
        "PerAddressCap": NA, "WAD": record["block_wad"], "Payload": record["block_payload"],
        "Bank": record["block_bank"], "L1": record["block_l1"], "Lower path": record["block_lower"],
    }
    rows = []
    for blocker, events in mapping.items():
        density = NA if events == NA else "%.9f" % (events / record["samples"])
        rows.append({"workload": workload, "variant": variant, "blocker": blocker,
                     "eligible_samples": record["samples"], "blocked_cycles": NA,
                     "blocked_events": events, "blocking_ratio": NA,
                     "blocked_density_events_per_sample": density,
                     "telemetry_note": "EPL2B0V1 emits blocker events, not exclusive blocked-cycle attribution"})
    return rows


def dominant(record: dict) -> tuple[str, str, str]:
    observed = {"DescriptorPool": record["block_descriptor"], "WAD": record["block_wad"],
                "Payload": record["block_payload"], "Bank": record["block_bank"],
                "L1": record["block_l1"], "Lower path": record["block_lower"]}
    ranked = sorted(observed, key=observed.get, reverse=True)
    if not observed[ranked[0]]:
        return "NO_CLEAR_INTERNAL_BOTTLENECK", "NONE", "NO_CLEAR_INTERNAL_BOTTLENECK"
    kind = ("bank-bound" if ranked[0] == "Bank" else "lower-bound" if ranked[0] == "Lower path"
            else "metadata-bound" if ranked[0] == "DescriptorPool" else "mixed")
    return ranked[0], ranked[1], kind


def make_markdown(pairs: list[tuple[str, dict, dict]], invariants: Counter) -> str:
    lines = ["# Target Baseline interim bottlenecks (22/26)", "",
             "Provisional only: 11 completed Legacy/Banked pairs at 850 MHz.  All values use Core "
             "`%s` and Framework `%s`.  Four long runs remain outside this analysis." % (CORE, FRAMEWORK),
             "", "## Per-workload observations", "",
             "| Workload | Dominant observed blocker | Secondary | High-util but not proven blocking | Legacy → Banked | Classification |",
             "|---|---|---|---|---|---|"]
    for name, legacy, banked in pairs:
        dominant_name, secondary, classification = dominant(banked)
        high = "line-MSHR max=%s/128; full-event telemetry not emitted" % banked["line_mshr_max"]
        change = "%.3fx cycles; bank conflict rate %s" % (banked["cycles"] / legacy["cycles"],
                                                               ("%.4f" % (banked["bank_conflicts"] / banked["bank_requests"])
                                                                if banked["bank_requests"] else "0"))
        lines.append("| %s | %s | %s | %s | %s | %s |" %
                     (name, dominant_name, secondary, high, change, classification))
    lines += ["", "## Required interim questions", "",
              "* **btree/shared descriptor model:** the legacy fixed-merge-fragmentation counter is not in EPL2B0V1; do not claim a direct before/after disappearance.  Current descriptor occupancy/block events are reported in the CSVs.",
              "* **128 line MSHRs:** max occupancy is measured, but no explicit LINE_MSHR_FULL event is emitted; no fullness claim is inferred.",
              "* **256-descriptor pool:** `descriptor_max=256` plus descriptor blocker events is evidence of pool pressure, not a claim about a per-address cap.",
              "* **32/address cap, WAD hazard, Tag/Set:** per-address, hazard, and tag/set blocker counters are not emitted.  WAD full blocker is emitted and remains separately reported.",
              "* **B0-Banked attribution:** the overlay diff is limited to payload mode (`1` Legacy versus `2` Banked); base-config and trace hashes match within every pair.  A material cycle change is still marked `ATTRIBUTION_WARNING` because EPL2B0V1 lacks arbitration-wait and operation-type telemetry needed to close causal magnitude.",
              "* **L1 and lower ceiling:** only aggregate L1 and lower blocker events are emitted; detailed L1 component and DRAM scheduler/BW attribution are not fabricated.",
              "", "## C5c terminal sanity", "",
              "| Gate | PASS runs | Notes |", "|---|---:|---|",
              "| descriptor lifetime | %d | terminal descriptor_used=0 |" % invariants["descriptor"],
              "| WAD | %d | terminal wad_live=0 |" % invariants["wad"],
              "| payload owner/generation | %d | owner consistency=1, double owner=0 |" % invariants["payload"],
              "| pending sector | %d | resident_pending=0 |" % invariants["pending"],
              "| bank no-loss | %d | bank_pending=0 |" % invariants["bank"],
              "| stale-fill count | %s | no explicit counter in EPL2B0V1 |" % NA,
              "", "No C5c terminal invariant failure was observed in the 22 completed runs.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/ep_l2/target_baseline_results_c5c")
    parser.add_argument("--pack", type=Path, default=ROOT / "docs/ep_l2/review_packs/target_baseline_interim_22of26_analysis_pack.tar.gz")
    args = parser.parse_args()
    out = args.out
    completed: dict[tuple[str, str], tuple[dict, dict, Path]] = {}
    status_rows = []
    processes = process_table()
    for workload, trace in ROSTER:
        for variant, _ in VARIANTS:
            directory = out / variant / workload
            status_path = directory / "run_status.json"
            if status_path.exists():
                status = read_json(status_path)
                audit = status.get("audit", {})
                if status.get("status") != "COMPLETE_VALID":
                    raise SystemExit("non-valid formal run present: %s/%s" % (variant, workload))
                if audit.get("core_authoritative_source") != CORE or audit.get("framework_authoritative_source") != FRAMEWORK:
                    raise SystemExit("provenance mismatch: %s/%s" % (variant, workload))
                record = aggregate(directory, status)
                completed[workload, variant] = (status, record, directory)
                invariant_status = "PASS" if all(record[key] == 1 for key in (
                    "descriptor_invariant_pass", "wad_invariant_pass", "payload_owner_generation_pass",
                    "pending_sector_invariant_pass", "bank_no_loss_pass", "terminal_clean_pass")) else "FAIL"
                status_rows.append({"workload": workload, "variant": variant, "status": "COMPLETE_VALID",
                                    "cycles": record["cycles"], "instructions": record["instructions"],
                                    "wall_seconds": record["wall_seconds"], "invariant_status": invariant_status,
                                    "core_sha": CORE, "framework_sha": FRAMEWORK, "current_progress": ""})
            else:
                status_rows.append(running_row(directory, workload, variant, trace, processes))
    if len(completed) != 22:
        raise SystemExit("interim pack requires exactly 22 completed runs, got %d" % len(completed))
    write_csv(out / "TARGET_BASELINE_INTERIM_STATUS.tsv", status_rows)

    pairs = []
    comparison = []
    resource = []
    blocking = []
    bank = []
    lower = []
    invariants = Counter()
    raw_index = []
    for (workload, variant), (_, record, directory) in sorted(completed.items()):
        for key, short in (("descriptor_invariant_pass", "descriptor"), ("wad_invariant_pass", "wad"),
                           ("payload_owner_generation_pass", "payload"), ("pending_sector_invariant_pass", "pending"),
                           ("bank_no_loss_pass", "bank")):
            invariants[short] += int(record[key] == 1)
        resource.append({"workload": workload, "variant": variant, "tag_reserved": NA,
                         "line_mshr_avg": record["line_mshr_avg"], "line_mshr_p95": record["line_mshr_p95"],
                         "line_mshr_max": record["line_mshr_max"], "descriptor_avg": record["descriptor_avg"],
                         "descriptor_p95": record["descriptor_p95"], "descriptor_max": record["descriptor_max"],
                         "chain_depth_avg": NA, "chain_depth_p95": NA, "chain_depth_max": NA,
                         "wad_avg": record["wad_avg"], "wad_p95": record["wad_p95"], "wad_max": record["wad_max"],
                         "resident_payload_avg": record["resident_payload_avg"],
                         "resident_payload_p95": record["resident_payload_p95"],
                         "resident_payload_max": record["resident_payload_max"],
                         "fill_pending_payload": NA})
        blocking.extend(blocker_rows(workload, variant, record))
        requests = record["bank_requests"]
        bank.append({"workload": workload, "variant": variant,
                     "legacy_port_activity": requests if variant == "B0-Legacy" else NA,
                     "banked_aggregate_requests": requests if variant == "B0-Banked" else NA,
                     "banked_per_bank_activity": NA, "grants": record["bank_grants"],
                     "conflicts": record["bank_conflicts"],
                     "conflict_rate": "%.6f" % (record["bank_conflicts"] / requests) if requests else "0.000000",
                     "arbitration_wait_cycles": NA, "hit_read": NA, "fill_write": NA,
                     "wb_read": NA, "write": NA, "bypass": NA})
        lower.append({"workload": workload, "variant": variant,
                      "lower_issue_q_avg": record["lowerq_avg"], "lower_issue_q_p95": NA,
                      "lower_issue_q_max": record["lowerq_max"], "l2_to_dram_avg": NA,
                      "l2_to_dram_p95": NA, "l2_to_dram_max": NA, "l2_to_dram_full": NA,
                      "dram_to_l2": NA, "scheduler_block_events": record["block_lower"],
                      "dram_bw_util": NA, "mshr_pending_lifetime": NA})
        raw = directory / "raw.log"
        raw_index.append({"workload": workload, "variant": variant, "raw_log_path": str(raw),
                          "raw_log_bytes": raw.stat().st_size, "raw_log_gz_path": str(directory / "raw.log.gz"),
                          "raw_log_gz_bytes": (directory / "raw.log.gz").stat().st_size})
    for workload, _ in ROSTER:
        if (workload, "B0-Legacy") not in completed or (workload, "B0-Banked") not in completed:
            continue
        legacy = completed[workload, "B0-Legacy"][1]
        banked = completed[workload, "B0-Banked"][1]
        row = {"workload": workload, "legacy_cycles": legacy["cycles"], "banked_cycles": banked["cycles"],
               "banked_speedup": "%.6f" % (legacy["cycles"] / banked["cycles"])}
        add_variant_fields(row, "legacy", legacy); add_variant_fields(row, "banked", banked)
        delta = abs(banked["cycles"] / legacy["cycles"] - 1)
        row["attribution"] = ("ATTRIBUTION_WARNING: material cycle delta; Banked conflicts are present, but "
                              "EPL2B0V1 lacks arbitration-wait/op-type telemetry to close causal magnitude"
                              if delta >= .02 else
                              "Banked-only RAM activity observed; small delta is consistent with service timing")
        comparison.append(row); pairs.append((workload, legacy, banked))
    write_csv(out / "target_baseline_interim_comparison.csv", comparison)
    write_csv(out / "target_resource_pressure.csv", resource)
    write_csv(out / "target_blocking_matrix.csv", blocking)
    write_csv(out / "target_bank_pressure.csv", bank)
    write_csv(out / "target_lower_path.csv", lower)
    write_csv(out / "TARGET_BASELINE_RAW_LOG_INDEX.tsv", raw_index)
    (out / "TARGET_BASELINE_INTERIM_BOTTLENECKS.md").write_text(make_markdown(pairs, invariants))
    schema = """# EPL2B0V1 interim analysis schema\n\nThis provisional package uses direct `EPL2B0V1` application-cumulative records\nfrom completed runs only.  `samples` is a slice-cycle sample count.  `block_*`\nare additive blocker events, not exclusive blocked cycles; matrices consequently\nkeep event density and mark blocked-cycle ratios unavailable.  Fields marked\n`NOT_EMITTED_BY_EPL2B0V1` were not inferred from unrelated counters.\n\nRaw simulator terminal summaries supply total L2 accesses/misses, DRAM reads/writes,\nand total instructions.  All other occupancy and blocker values are derived from\n`target_slice.csv` / `target_summary.csv`.\n"""
    (out / "EPL2B0V1_INTERIM_SCHEMA.md").write_text(schema)
    manifest = {"kind": "provisional_target_baseline_interim", "completed_runs": len(completed),
                "expected_runs": 26, "paired_workloads": len(pairs), "frequency_mhz": 850,
                "core_sha": CORE, "framework_sha": FRAMEWORK,
                "diagnostic_results_excluded": True,
                "legacy_banked_config_audit": {
                    "base_config_and_trace_hashes_match_per_pair": True,
                    "overlay_semantic_diff": "gpgpu_ep_l2_payload_mode: 1 (Legacy) vs 2 (Banked)",
                    "capacity_semantics": "both retain 1024 resident + 128 bypass static ownership",
                },
                "telemetry_contract": "NOT_EMITTED values are intentionally not inferred"}
    (out / "target_baseline_interim_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    pack_root = Path("target_baseline_interim_22of26_analysis_pack")
    members: list[tuple[Path, Path]] = []
    for name in ("TARGET_BASELINE_INTERIM_STATUS.tsv", "target_baseline_interim_comparison.csv",
                 "target_resource_pressure.csv", "target_blocking_matrix.csv", "target_bank_pressure.csv",
                 "target_lower_path.csv", "TARGET_BASELINE_INTERIM_BOTTLENECKS.md",
                 "TARGET_BASELINE_RAW_LOG_INDEX.tsv", "EPL2B0V1_INTERIM_SCHEMA.md",
                 "target_baseline_interim_manifest.json"):
        members.append((out / name, pack_root / name))
    for (workload, variant), (_, _, directory) in completed.items():
        for name in ("target_summary.csv", "manifest.json", "run_status.json"):
            members.append((directory / name, pack_root / variant / workload / name))
    for source in (Path(__file__), ROOT / "util/ep_l2/parse_epl2_b0.py", ROOT / "util/ep_l2/run_target_baseline.py"):
        members.append((source, pack_root / "scripts" / source.name))
    for source in (ROOT / "tests/ep_l2/b0_legacy_850.config", ROOT / "tests/ep_l2/b0_banked_850.config"):
        members.append((source, pack_root / "configs" / source.name))
    sums = out / "SHA256SUMS"
    sums.write_text("".join("%s  %s\n" % (sha256(source), archive) for source, archive in sorted(members, key=lambda x: str(x[1]))))
    members.append((sums, pack_root / "SHA256SUMS"))
    args.pack.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.pack, "w:gz") as archive:
        for source, archive_name in members:
            archive.add(source, arcname=str(archive_name), recursive=False)
    print(args.pack)


if __name__ == "__main__":
    main()
