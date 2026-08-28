#!/usr/bin/env python3
"""Early, non-invasive L2CHARV1 audit for COMPLETE_VALID Round-1 runs.

The audit intentionally streams raw logs: a campaign result may contain a
multi-GiB log, while this tool only needs terminal simulator fields, final
L2CHARV1 HIST/INVARIANT records, and existing CSV artifacts.
"""
import argparse
import csv
import json
import math
import pathlib
import re
import statistics
from collections import defaultdict

EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"
HIST_METRICS = ("reserved", "mshr", "mshr_target", "merge_depth", "missq",
                "missq_wb", "icntl2q", "l2dramq", "draml2q", "l2icntq",
                "rop")
REQUEST_BLOCKERS = ("block_set", "block_mshr_new", "block_mshr_merge",
                    "block_missq", "block_dataport", "block_respq", "fill")
CAUSAL_BLOCKERS = ("rop_input", "mshr_response", "lower_drain", "dram_return")
REQUIRED_FILES = ("raw.log", "summary.csv", "slice.csv", "window.csv",
                  "manifest.json", "run_status.json")


def number(value, default=None):
    if value in (None, "", "NA"):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def integer(value, default=None):
    value = number(value, default)
    return int(value) if value is not None else default


def na(value):
    return "NA" if value is None else value


def ratio(numerator, denominator):
    return None if not denominator else numerator / denominator


def mean(values):
    return sum(values) / len(values) if values else None


def percentile_from_bins(bins, q):
    samples = sum(bins.values())
    if not samples:
        return None
    rank = (samples * q + 99) // 100
    seen = 0
    for index in sorted(bins):
        count = bins[index]
        seen += count
        if seen >= rank:
            return index
    return None


def parse_fields(line):
    fields = {}
    for item in line.rstrip().split("|")[2:]:
        if "=" in item:
            key, value = item.split("=", 1)
            fields[key] = value
    return fields


def parse_histogram(fields):
    """Parse dense or sparse HIST data without allocating up to ROP maximum."""
    raw = fields.get("bins", "")
    if fields.get("encoding", "dense") == "sparse":
        bins = {}
        for item in raw.split(","):
            if not item:
                continue
            value, count = item.split(":", 1)
            bins[int(value)] = int(count)
        return bins
    return {index: int(count) for index, count in enumerate(raw.split(","))
            if count != ""}


def stream_raw(path):
    """Return final-snapshot invariant/HIST data and terminal standard stats."""
    hists, invariants = {}, []
    prior_snapshot = False
    exit_seen = False
    cycle = insn = None
    cache = defaultdict(dict)
    port_util = {"data": None, "fill": None}
    stat_re = re.compile(r"L2_cache_stats_breakdown\[([^]]+)\]\[([^]]+)\]\s*=\s*(-?\d+)")
    port_re = re.compile(r"L2_cache_(data|fill)_port_util\s*=\s*([0-9.]+)")
    with path.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            if EXIT_MARKER in line:
                exit_seen = True
            stripped = line.lstrip()
            if stripped.startswith("gpu_tot_sim_cycle") and "=" in stripped:
                cycle = integer(stripped.split("=", 1)[1].strip())
            elif stripped.startswith("gpu_tot_sim_insn") and "=" in stripped:
                insn = integer(stripped.split("=", 1)[1].strip())
            match = stat_re.search(line)
            if match:
                cache[match.group(1)][match.group(2)] = int(match.group(3))
            match = port_re.search(line)
            if match:
                port_util[match.group(1)] = float(match.group(2))
            if not line.startswith("L2CHARV1|"):
                continue
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            kind, fields = parts[1], parse_fields(line)
            if kind == "SLICE" and fields.get("slice") == "0":
                if prior_snapshot:
                    hists, invariants = {}, []
                prior_snapshot = True
            elif kind == "HIST":
                hists[(integer(fields.get("slice")), fields.get("metric"))] = {
                    "bins": parse_histogram(fields), "capacity": integer(fields.get("capacity")),
                    "unbounded": integer(fields.get("unbounded"), 0),
                    "samples": integer(fields.get("samples")),
                }
            elif kind == "INVARIANT":
                invariants.append(fields)
    return {"exit_seen": exit_seen, "cycle": cycle, "insn": insn,
            "hists": hists, "invariants": invariants, "cache": cache, "port_util": port_util}


def read_csv(path):
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def write_csv(path, rows):
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=keys, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def workload_class(run):
    suite = run["suite"]
    if suite == "Accel-Sim ubench":
        return "reference"
    if suite in ("ISPASS", "Mars", "SHOC") or "V100" in run["input"]:
        return "secondary"
    return "primary"


def standard_l2_stats(cache):
    total = reads = writes = hits = misses = 0
    for access, values in cache.items():
        accesses = values.get("TOTAL_ACCESS", 0)
        total += accesses
        if access.endswith("_R"):
            reads += accesses
        elif access.endswith("_W"):
            writes += accesses
        hits += values.get("HIT", 0) + values.get("HIT_RESERVED", 0) + values.get("MSHR_HIT", 0)
        misses += values.get("MISS", 0) + values.get("SECTOR_MISS", 0)
    return {"l2_accesses": total, "l2_read_accesses": reads, "l2_write_accesses": writes,
            "l2_hits": hits, "l2_misses": misses, "l2_hit_rate": ratio(hits, total)}


def audit_histograms(summary, slices, raw, errors, warnings):
    result = {}
    for metric in HIST_METRICS:
        records = [value for (slice_id, name), value in raw["hists"].items() if name == metric]
        if len(records) != 64:
            errors.append(f"hist:{metric}:expected_64_got_{len(records)}")
            continue
        cap = records[0]["capacity"]
        if any(record["capacity"] != cap for record in records):
            errors.append(f"hist:{metric}:inconsistent_capacity")
            continue
        bins = defaultdict(int)
        for record in records:
            if sum(record["bins"].values()) != record["samples"]:
                errors.append(f"hist:{metric}:slice_sample_mismatch")
            for index, count in record["bins"].items():
                bins[index] += count
        samples = sum(bins.values())
        observed_max = max(index for index, count in bins.items() if count > 0)
        observed_avg = sum(index * count for index, count in bins.items()) / samples
        observed_p50 = percentile_from_bins(bins, 50)
        observed_p95 = percentile_from_bins(bins, 95)
        summary_values = {"max": integer(summary.get(metric + "_global_max")),
                          "avg": number(summary.get(metric + "_global_avg")),
                          "p50": integer(summary.get(metric + "_global_p50")),
                          "p95": integer(summary.get(metric + "_global_p95"))}
        expected_values = {"max": observed_max, "avg": observed_avg,
                           "p50": observed_p50, "p95": observed_p95}
        for key, expected in expected_values.items():
            actual = summary_values[key]
            if actual is None or abs(actual - expected) > 1e-9:
                errors.append(f"hist:{metric}:{key}:summary={actual}:expected={expected}")
        slice_max = max(integer(row.get(metric + "_max"), -1) for row in slices)
        if observed_max != slice_max:
            errors.append(f"hist:{metric}:global_max={observed_max}:slice_max={slice_max}")
        bounded = not any(record["unbounded"] for record in records)
        if not (observed_p50 <= observed_p95 <= observed_max and
                (not bounded or observed_max <= cap)):
            errors.append(f"hist:{metric}:percentile_or_capacity_order")
        result[metric] = {"samples": samples, "capacity": cap, "max": observed_max,
                          "avg": observed_avg, "p50": observed_p50, "p95": observed_p95}
    return result, []


def audit_windows(slices, windows, errors, warnings):
    by_slice = defaultdict(list)
    for row in windows:
        by_slice[integer(row.get("slice"))].append(row)
    variation = {}
    for slice_id, rows in by_slice.items():
        rows.sort(key=lambda row: integer(row.get("window"), -1))
        ids = [integer(row.get("window"), -1) for row in rows]
        if ids != list(range(len(ids))):
            errors.append(f"window:slice={slice_id}:non_contiguous_ids")
        slice_cycles = integer(next(row["cycles"] for row in slices if integer(row["slice"]) == slice_id))
        samples = [integer(row.get("samples"), 0) for row in rows]
        if sum(samples) != slice_cycles:
            errors.append(f"window:slice={slice_id}:sample_sum={sum(samples)}:cycles={slice_cycles}")
        # A simulator statistics dump at a kernel boundary closes the current
        # partial window.  Thus a multi-kernel application can legitimately
        # contain several short windows, not just the terminal one.  The
        # portable correctness condition is contiguous intervals plus exact
        # sample conservation, verified below.
        for row in rows:
            start, end, count = integer(row.get("start_l2_cycle")), integer(row.get("end_l2_cycle")), integer(row.get("samples"))
            if None in (start, end, count) or end - start + 1 != count:
                errors.append(f"window:slice={slice_id}:invalid_bounds")
                break
        if len(rows) > 2:
            series = [number(row.get("mshr_avg"), 0.0) for row in rows]
            blocked = [ratio(number(row.get("block_set_blocked"), 0.0), number(row.get("block_set_eligible"), 0.0))
                       for row in rows]
            variation[slice_id] = {"windows": len(rows),
                                   "mshr_avg_cv": ratio(statistics.pstdev(series), mean(series)) if mean(series) else None,
                                   "set_block_ratio_range": (max(x for x in blocked if x is not None) - min(x for x in blocked if x is not None))
                                   if any(x is not None for x in blocked) else None}
    if set(by_slice) != set(range(64)):
        errors.append(f"window:slice_coverage={len(by_slice)}")
    return variation


def audit_blockers(slices, errors, warnings):
    data = {}
    for blocker in REQUEST_BLOCKERS + CAUSAL_BLOCKERS:
        eligible = sum(integer(row.get(blocker + "_eligible"), 0) for row in slices)
        blocked = sum(integer(row.get(blocker + "_blocked"), 0) for row in slices)
        episodes = sum(integer(row.get(blocker + "_episodes"), 0) for row in slices)
        requests = sum(integer(row.get(blocker + "_requests"), 0) for row in slices)
        ratios = [number(row.get(blocker + "_ratio")) for row in slices]
        for row, item_ratio in zip(slices, ratios):
            e, b = integer(row.get(blocker + "_eligible"), 0), integer(row.get(blocker + "_blocked"), 0)
            if not 0 <= b <= e:
                errors.append(f"blocker:{blocker}:blocked_out_of_range")
            expected = ratio(b, e)
            if expected is None:
                if row.get(blocker + "_ratio") not in ("NA", ""):
                    errors.append(f"blocker:{blocker}:zero_eligible_ratio_not_NA")
            elif item_ratio is None or abs(item_ratio - expected) > 5e-7:
                errors.append(f"blocker:{blocker}:ratio_mismatch")
        if blocker in REQUEST_BLOCKERS and not (requests <= episodes <= blocked):
            # A zero-duration episode is not representable; flag only a true inversion.
            errors.append(f"blocker:{blocker}:requests={requests}:episodes={episodes}:blocked={blocked}")
        data[blocker] = {"eligible": eligible, "blocked": blocked, "episodes": episodes,
                         "requests": requests, "ratio": ratio(blocked, eligible)}
    return data


def causal_sanity(slices, blockers, raw, errors, warnings):
    def any_positive(field):
        return any(number(row.get(field), 0.0) > 0.0 for row in slices)
    if blockers["block_dataport"]["blocked"] and not any_positive("data_busy_ratio"):
        errors.append("causal:dataport_block_without_busy")
    if blockers["fill"]["blocked"] and not any_positive("fill_busy_ratio"):
        errors.append("causal:fill_block_without_busy")
    # Native cache_stats and L2CHAR use the same pre-replenish snapshot.
    # These integer equalities are the primary evidence; rounded utilization
    # is deliberately not used as an invariant.
    for char, native in (("char_data_busy_cycles", "native_data_busy_cycles"),
                         ("char_fill_busy_cycles", "native_fill_busy_cycles"),
                         ("char_port_samples", "native_port_samples")):
        values = [(integer(row.get(char)), integer(row.get(native))) for row in slices]
        if any(left is None or right is None for left, right in values):
            errors.append(f"production:{char}:missing_integer_crosscheck")
        elif any(left != right for left, right in values):
            errors.append(f"production:{char}:native_mismatch")
    if blockers["block_mshr_new"]["blocked"] and not any(integer(row.get("mshr_max"), 0) >= integer(row.get("mshr_cap"), 1) for row in slices):
        warnings.append("causal:mshr_new_block_without_sampled_full_mshr")
    if blockers["block_mshr_merge"]["blocked"] and not any(integer(row.get("merge_limit_entries_max"), 0) >= integer(row.get("merge_limit_entries_cap"), 1) for row in slices):
        warnings.append("causal:mshr_merge_block_without_sampled_merge_limit_full")
    # RESPQ is the immediate L2-to-ICNT response queue.  Event-time blocker
    # accounting is exact; a cycle sample that misses a full queue only warns.
    if blockers["block_respq"]["blocked"] and not any(integer(row.get("l2icntq_max"), 0) >= integer(row.get("l2icntq_cap"), 1) for row in slices):
        warnings.append("causal:respq_block_without_sampled_l2icntq_full")
    if blockers["lower_drain"]["blocked"] and not any(integer(row.get("l2dramq_max"), 0) >= integer(row.get("l2dramq_cap"), 1) for row in slices):
        warnings.append("causal:lower_drain_block_without_sampled_l2dramq_full")
    if blockers["dram_return"]["blocked"] and not any(integer(row.get("draml2q_max"), 0) >= integer(row.get("draml2q_cap"), 1) for row in slices):
        warnings.append("causal:dram_return_block_without_sampled_draml2q_full")


def audit_run(directory):
    errors, warnings = [], []
    status = json.loads((directory / "run_status.json").read_text())
    for name in REQUIRED_FILES:
        if not (directory / name).is_file():
            errors.append("missing:" + name)
    if errors:
        return {"directory": directory, "status": status, "errors": errors, "warnings": warnings}
    summary_rows, slices, windows = read_csv(directory / "summary.csv"), read_csv(directory / "slice.csv"), read_csv(directory / "window.csv")
    if len(summary_rows) != 1:
        errors.append("summary:not_exactly_one_row")
    summary = summary_rows[0] if summary_rows else {}
    manifest = json.loads((directory / "manifest.json").read_text())
    raw = stream_raw(directory / "raw.log")
    run = {"directory": directory, "status": status, "summary": summary, "slices": slices,
           "windows": windows, "manifest": manifest, "raw": raw, "errors": errors, "warnings": warnings}
    if len(slices) != 64 or {integer(row.get("slice")) for row in slices} != set(range(64)):
        errors.append(f"slice_coverage={len(slices)}")
    mandatory = ("workload", "input", "kernel", "kernel_id", "core_commit", "core_branch",
                 "framework_commit", "framework_branch", "trace", "trace_sha256", "gpu_config",
                 "gpu_config_sha256", "command", "gpu_tot_sim_cycle", "gpu_tot_sim_insn")
    for key in mandatory:
        if summary.get(key) in (None, "", "NA"):
            errors.append("summary_missing:" + key)
    if not raw["exit_seen"]:
        errors.append("raw_missing_exit_marker")
    if integer(summary.get("gpu_tot_sim_cycle")) != raw["cycle"] or integer(summary.get("gpu_tot_sim_insn")) != raw["insn"]:
        errors.append("terminal_cycle_or_instruction_mismatch")
    if summary.get("invariants_pass") != "1" or integer(summary.get("invariant_records")) != 64:
        errors.append("summary_invariant_status")
    if len(raw["invariants"]) != 64 or any(item.get("status") != "PASS" for item in raw["invariants"]):
        errors.append("final_slice_invariant_status")
    characterization = manifest.get("characterization", {})
    audit = manifest.get("campaign_audit", {})
    if characterization != {"enabled": True, "window_l2_cycles": 5000, "set_detail": True, "emit_windows": True}:
        errors.append("manifest_characterization_config")
    hooks = audit.get("test_hooks", {})
    if not hooks or any(str(value) not in ("0", "0.0") for value in hooks.values()):
        errors.append("test_hooks_not_all_off")
    if not audit.get("config_bundle_sha256") or not audit.get("trace_config_sha256") or not audit.get("overlay_sha256"):
        errors.append("manifest_missing_config_provenance")
    run["hist"], run["unsupported_hists"] = audit_histograms(summary, slices, raw, errors, warnings)
    run["windows_variation"] = audit_windows(slices, windows, errors, warnings)
    run["blockers"] = audit_blockers(slices, errors, warnings)
    causal_sanity(slices, run["blockers"], raw, errors, warnings)
    # WB ratios use actual lower requests/bytes; only these are meaningful when nonzero.
    wb_requests = sum(integer(row.get("l2dram_wb_requests"), 0) for row in slices)
    l2dram_requests = sum(integer(row.get("l2dram_requests"), 0) for row in slices)
    wb_bytes = sum(integer(row.get("l2dram_wb_bytes"), 0) for row in slices)
    l2dram_bytes = sum(integer(row.get("l2dram_bytes"), 0) for row in slices)
    if not (0 <= ratio(wb_requests, l2dram_requests) <= 1 if l2dram_requests else True):
        errors.append("wb_request_fraction_range")
    if not (0 <= ratio(wb_bytes, l2dram_bytes) <= 1 if l2dram_bytes else True):
        errors.append("wb_byte_fraction_range")
    if number(summary.get("wb_request_fraction")) != ratio(wb_requests, l2dram_requests):
        errors.append("wb_request_fraction_mismatch")
    if number(summary.get("wb_byte_fraction")) != ratio(wb_bytes, l2dram_bytes):
        errors.append("wb_byte_fraction_mismatch")
    run["wb"] = {"requests": wb_requests, "bytes": wb_bytes,
                 "request_fraction": ratio(wb_requests, l2dram_requests),
                 "byte_fraction": ratio(wb_bytes, l2dram_bytes)}
    run["performance"] = standard_l2_stats(raw["cache"])
    return run


def correlation(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return None
    xs, ys = zip(*pairs)
    sx, sy = statistics.pstdev(xs), statistics.pstdev(ys)
    return None if not sx or not sy else sum((a - mean(xs)) * (b - mean(ys)) for a, b in pairs) / len(pairs) / sx / sy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=pathlib.Path, default=pathlib.Path("docs/l2_char_v1/round1_results"))
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("docs/l2_char_v1/round1_early_sanity"))
    parser.add_argument("--report", type=pathlib.Path, default=pathlib.Path("docs/l2_char_v1/ROUND1_EARLY_SANITY_REPORT.md"))
    parser.add_argument("--table", type=pathlib.Path, default=pathlib.Path("docs/l2_char_v1/ROUND1_EARLY_SANITY_TABLE.tsv"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    completed = []
    for status_path in sorted(args.results.rglob("run_status.json")):
        try:
            status = json.loads(status_path.read_text())
        except json.JSONDecodeError:
            continue
        if status.get("status") == "COMPLETE_VALID":
            completed.append(audit_run(status_path.parent))
    rows, util_rows, block_rows, spatial_rows, temporal_rows = [], [], [], [], []
    for run in completed:
        summary, slices = run["summary"], run["slices"]
        status = "FAIL" if run["errors"] else ("WARN" if run["warnings"] else "PASS")
        ident = {"suite": run["status"].get("suite"), "workload": summary.get("workload"), "input": summary.get("input"),
                 "class": workload_class(run["status"]), "audit_status": status}
        rows.append({**ident, "reason": ";".join(run["errors"] + run["warnings"]),
                     "instructions": summary.get("gpu_tot_sim_insn"), "cycles": summary.get("gpu_tot_sim_cycle"),
                     "sim_instructions_per_cycle": ratio(number(summary.get("gpu_tot_sim_insn")), number(summary.get("gpu_tot_sim_cycle"))),
                     **run["performance"], "wb_requests": run["wb"]["requests"], "wb_bytes": run["wb"]["bytes"],
                     "slice_records": len(slices), "window_records": len(run["windows"]),
                     "standard_data_port_util": run["raw"]["port_util"].get("data"),
                     "standard_fill_port_util": run["raw"]["port_util"].get("fill"),
                     "core_commit": summary.get("core_commit"), "framework_commit": summary.get("framework_commit")})
        util_rows.append({**ident, "reserved_p95": summary.get("reserved_global_p95"),
                          "mshr_entry_p95": summary.get("mshr_global_p95"),
                          "merge_depth_p95": summary.get("merge_depth_global_p95"),
                          "missq_p95": summary.get("missq_global_p95"), "fill_busy_ratio": summary.get("fill_busy_ratio"),
                          "wb_request_fraction": summary.get("wb_request_fraction"), "data_busy_ratio": summary.get("data_busy_ratio")})
        block_rows.append({**ident, **{name + "_ratio": run["blockers"][name]["ratio"] for name in REQUEST_BLOCKERS}})
        for metric in ("reserved_util_avg", "mshr_util_avg", "missq_util_avg", "fill_busy_ratio", "data_busy_ratio", "draml2q_util_avg", "missq_wb_util_avg"):
            values = [number(row.get(metric), 0.0) for row in slices]
            spatial_rows.append({**ident, "metric": metric, "mean": mean(values),
                                 "max": max(values), "cv": ratio(statistics.pstdev(values), mean(values)),
                                 "max_over_mean": ratio(max(values), mean(values))})
        variation = run["windows_variation"]
        if variation:
            temporal_rows.append({**ident, "slices_with_gt2_windows": len(variation),
                                  "max_mshr_window_cv": max(na(item["mshr_avg_cv"]) for item in variation.values() if item["mshr_avg_cv"] is not None) if any(item["mshr_avg_cv"] is not None for item in variation.values()) else "NA",
                                  "max_set_block_ratio_range": max(na(item["set_block_ratio_range"]) for item in variation.values() if item["set_block_ratio_range"] is not None) if any(item["set_block_ratio_range"] is not None for item in variation.values()) else "NA"})
    write_csv(args.table, rows)
    write_csv(args.out / "utilization_matrix.csv", util_rows)
    write_csv(args.out / "blocking_matrix.csv", block_rows)
    write_csv(args.out / "spatial_summary.csv", spatial_rows)
    write_csv(args.out / "temporal_summary.csv", temporal_rows)
    errors = [run for run in completed if run["errors"]]
    warnings = [run for run in completed if run["warnings"]]
    # Workload-level diagnostic correlations, never a performance claim.
    correlations = {}
    for util, block in (("mshr_entry_p95", "block_mshr_new_ratio"), ("missq_p95", "block_missq_ratio"),
                        ("fill_busy_ratio", "fill_ratio"), ("data_busy_ratio", "block_dataport_ratio")):
        correlations[f"{util}__vs__{block}"] = correlation([number(row.get(util)) for row in util_rows],
                                                              [number(row.get(block)) for row in block_rows])
    resource_summary = []
    for field in ("reserved_p95", "mshr_entry_p95", "merge_depth_p95", "missq_p95", "fill_busy_ratio", "wb_request_fraction", "data_busy_ratio"):
        values = [(number(row.get(field)), row["workload"]) for row in util_rows if number(row.get(field)) is not None]
        values.sort(reverse=True)
        numbers = [value for value, _ in values]
        resource_summary.append((field, min(numbers) if numbers else None, statistics.median(numbers) if numbers else None,
                                 max(numbers) if numbers else None, ", ".join(name for _, name in values[:5])))
    pass_count = sum(1 for row in rows if row["audit_status"] == "PASS")
    warn_count = sum(1 for row in rows if row["audit_status"] == "WARN")
    fail_count = sum(1 for row in rows if row["audit_status"] == "FAIL")
    unsupported = sorted({metric for run in completed for metric in run.get("unsupported_hists", [])})
    conclusion = ("STOP_AND_FIX" if errors else
                  "CONDITIONAL_CONTINUE" if warnings or unsupported else
                  "PASS_CONTINUE_CAMPAIGN")
    report = ["# Round-1 Early Sanity Audit", "", f"**Conclusion: `{conclusion}`**", "",
              f"Scope: {len(completed)} completed `COMPLETE_VALID` runs only. This is a preliminary, scheduling-biased audit; it does not select workloads or state paper conclusions.", "",
              "## Run completeness", "",
              f"- Files, identity/provenance, 64-slice coverage, final terminal cycle/instruction matching, final 64 slice invariants, and 5K-window continuity were checked for every scoped run.",
              f"- `PASS` rows: {pass_count}; `WARN` rows: {warn_count}; `FAIL` rows: {fail_count}.",
              "- Detailed per-run status and basic performance fields: `ROUND1_EARLY_SANITY_TABLE.tsv`.", "",
              "## Histogram / aggregation", "",
              "- Streamed final-snapshot HIST records verify exact weighted AVG/P50/P95/MAX and sample conservation for `reserved`, `mshr`, `mshr_target`, `merge_depth`, `missq`, `missq_wb`, ICNT→L2, L2→DRAM, DRAM→L2, L2→ICNT, and ROP. Sparse ROP bins are merged exactly without materializing a capacity-sized vector.",
              "",
              "## Blocking / causal semantics", "",
              "- Every emitted blocker was checked per slice for `0 <= blocked <= eligible`, exact ratio/NA semantics, and request≤episode≤blocked for request-level blockers.",
              "- Causal checks cross-reference DataPort/Fill busy, sampled MSHR/merge saturation, and queue maxima. Warnings identify only evidence that v1 cannot establish at its sampling granularity.",
              "",
              "## Diversity (PRELIMINARY)", "", "| resource | min | median | max | top-5 |", "|---|---:|---:|---:|---|"]
    for field, lo, med, hi, top in resource_summary:
        report.append(f"| {field} | {na(lo)} | {na(med)} | {na(hi)} | {top} |")
    report += ["", "Matrices: `round1_early_sanity/utilization_matrix.csv`, `blocking_matrix.csv`, `spatial_summary.csv`, and `temporal_summary.csv`. `mem_lat` is marked `reference`; V100/special workloads are marked `secondary`.",
               "", "## Utilization vs blocking diagnostic correlations", "", "| pair | Pearson r |", "|---|---:|"]
    for key, value in correlations.items():
        report.append(f"| {key} | {na(value)} |")
    report += ["", "These correlations are diagnostic only; utilization and blocking are intentionally distinct metrics.", "",
               "## Required follow-up / known unsupported observations", ""]
    report += ["- Event-time blocker records are production evidence. Cycle-sampled occupancy only supplies supporting context: a sampled queue that did not hit capacity is a warning, not a contradiction of a recorded blocker."]
    if errors:
        report += [f"- **FAIL**: {run['summary'].get('workload', run['directory'])}: {'; '.join(run['errors'])}" for run in errors]
    if unsupported:
        report.append("- Global exact HIST aggregation is not emitted for: " + ", ".join(unsupported) + ". Per-slice extrema/averages remain available, but global weighted P50/P95 cannot be validated from v1 raw records.")
    if warnings:
        report += [f"- **WARN**: {run['summary'].get('workload', run['directory'])}: {'; '.join(run['warnings'])}" for run in warnings]
    if not errors and not warnings:
        report.append("- None.")
    report += ["", "No frozen Core/Framework instrumentation was modified by this audit. Raw logs were stream-read only."]
    args.report.write_text("\n".join(report) + "\n")
    print(f"{conclusion}: completed={len(completed)} warn={len(warnings)} fail={len(errors)}")


if __name__ == "__main__":
    main()
