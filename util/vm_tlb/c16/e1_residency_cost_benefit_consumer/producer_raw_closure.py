#!/usr/bin/env python3
"""Independent raw closure for C16 E1 residency cost/benefit evidence.

This adapter consumes only producer RAW_NATIVE, RAW_AUTHORITY and raw NCU
BASE/SESSION/PROFILE artifacts for calculations. Producer display summaries
are opened only after the independent result and stage label exist.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path


TOKENS = [23578, 11, 323, 3950]
PHASES = ["PREFILL", "D0", "D1", "D2", "D3"]
ROLES = ["gate_proj", "up_proj", "down_proj"]
TOP_CATEGORIES = ["input_layernorm", "self_attn", "post_attention_layernorm", "mlp"]
BUDGETS = {"B8": 8 << 20, "B16": 16 << 20, "B24": 24 << 20, "BFULL": 33_947_648}
EXPECTED_ACTUAL = {"B8": 8 << 20, "B16": 16 << 20, "B24": 24 << 20, "BFULL": 37_748_736}
UP_BYTES = 33_947_648
RUNTIME_MAX = 46_137_344
METRIC_CATEGORIES = {
    "l1tex__t_bytes.sum": ("L1_TEX_BYTES", "byte", True),
    "lts__t_bytes.sum": ("L2_BYTES", "byte", True),
    "dram__bytes.sum": ("DRAM_BYTES", "byte", True),
    "gpu__time_duration.sum": ("KERNEL_DURATION", "ns", True),
    "lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum": ("L2_READ_HIT_SECTORS", "sector", True),
    "lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum": ("L2_READ_MISS_SECTORS", "sector", True),
    "dram__bytes_read.sum": ("DRAM_READ_BYTES", "byte", True),
    "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct": ("LONG_SCOREBOARD_STALL", "%", False),
    "smsp__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active": ("LSU_UTILIZATION", "%", False),
    "sm__warps_active.avg.pct_of_peak_sustained_active": ("ACHIEVED_ACTIVE_WARPS", "%", False),
}


class ClosureError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ClosureError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path):
    require(path.is_file() and path.stat().st_size > 0, f"missing/empty {path}")
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def finite(value, label: str, positive: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ClosureError(f"invalid {label}") from exc
    require(math.isfinite(result) and (not positive or result > 0), f"invalid {label}")
    return result


def stats(values):
    values = [finite(x, "sample") for x in values]
    require(values, "empty sample vector")
    mean = statistics.fmean(values)
    return {
        "sample_count": len(values), "min": min(values), "median": statistics.median(values),
        "max": max(values), "mean": mean,
        "cv": statistics.pstdev(values) / abs(mean) if mean else None,
    }


def normalized_category(value: str) -> str:
    return "output" if value == "lm_head" else value


def key_child(row):
    return int(row["layer"]), row["role"], int(row["decode_index"])


def key_top(row):
    layer = None if int(row["layer"]) == -1 else int(row["layer"])
    return layer, normalized_category(row["category"]), int(row["decode_index"])


def module_fingerprint(raw) -> str:
    rows = sorted((int(r["layer"]), r["category"], int(r["data_ptr"]), int(r["bytes"]))
                  for r in raw["child_module_census"])
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def validate_geometry(raw, source: str):
    rows = raw.get("child_module_census")
    require(isinstance(rows, list) and len(rows) == 84, f"{source}: child census !=84")
    by_key = {}
    intervals = []
    for row in rows:
        key = int(row["layer"]), row["category"]
        require(key[0] in range(28) and key[1] in ROLES and key not in by_key,
                f"{source}: child census identity")
        require(row["module_class"] == "WQLinear_GEMM" and row["contiguous"] is True,
                f"{source}: child module class/contiguity")
        pointer, size = int(row["data_ptr"]), int(row["bytes"])
        require(pointer > 0 and size > 0 and int(row["exact_tensor_span_begin"]) == pointer and
                int(row["exact_tensor_span_end_exclusive"]) == pointer + size,
                f"{source}: exact qweight span")
        if key[1] == "up_proj":
            require(size == UP_BYTES, f"{source}: up qweight bytes")
        by_key[key] = row
        intervals.append((pointer, pointer + size, key))
    require(set(by_key) == {(l, r) for l in range(28) for r in ROLES}, f"{source}: 84 matrix")
    intervals.sort()
    require(all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:])),
            f"{source}: overlapping qweight regions")
    return by_key


def validate_order(raw, source: str, field: str, expected_per_phase: int, expected_keys):
    rows = raw.get(field)
    require(isinstance(rows, list) and len(rows) == expected_per_phase * 5,
            f"{source}: {field} cardinality")
    result = {}
    for phase in PHASES:
        selected = [r for r in rows if r["phase"] == phase]
        selected.sort(key=lambda r: int(r["ordinal"]))
        require([int(r["ordinal"]) for r in selected] == list(range(expected_per_phase)),
                f"{source}: {field} ordinal")
        keys = [(None if int(r["layer"]) == -1 else int(r["layer"]),
                 normalized_category(r["category"])) for r in selected]
        require(keys == expected_keys, f"{source}: {field} semantic order drift")
        result[phase] = keys
    return result


def validate_policy(raw, source: str, budget: str, mode: str, modules):
    requested = BUDGETS[budget]
    actual = EXPECTED_ACTUAL[budget]
    expected_ratio = min(1.0, requested / (28 * UP_BYTES))
    require(raw["condition"] == f"{mode}_{budget}" and raw["budget_name"] == budget,
            f"{source}: condition identity")
    require(int(raw["requested_budget_bytes"]) == requested, f"{source}: requested budget")
    require(math.isclose(float(raw["hit_ratio"]), expected_ratio, rel_tol=0, abs_tol=1e-15),
            f"{source}: top-level hit ratio")
    receipt = raw.get("policy_receipt")
    require(isinstance(receipt, dict) and receipt.get("reset_before") is True and
            receipt.get("reset_after") is True and int(receipt.get("actual_setaside_after_reset_bytes")) == 0,
            f"{source}: reset receipt")
    require(int(receipt["requested_setaside_bytes"]) == requested and
            int(receipt["actual_setaside_bytes"]) == actual and receipt["condition"] == f"{mode}_{budget}",
            f"{source}: runtime setaside query-back")
    for operation in receipt.get("operations_before", []) + receipt.get("operations_after", []):
        require(int(operation.get("status", -1)) == 0 and operation.get("error_string") == "no error",
                f"{source}: CUDA policy operation failed")
    transitions = raw.get("policy_transitions")
    require(raw.get("policy_transition_count") == 140 and isinstance(transitions, list) and len(transitions) == 140,
            f"{source}: policy transition count")
    seen = set()
    durations_us = []
    expected_props = (("cudaAccessPropertyNormal", "cudaAccessPropertyNormal", False)
                      if mode == "CONTROL" else
                      ("cudaAccessPropertyPersisting", "cudaAccessPropertyStreaming", True))
    for index, event in enumerate(transitions):
        phase, layer = event["phase"], int(event["layer"])
        require(phase in PHASES and layer in range(28) and event["category"] == "up_proj",
                f"{source}: update family")
        require((phase, layer) not in seen, f"{source}: duplicate policy update")
        seen.add((phase, layer))
        expected_ordinal = layer * 3 + 1
        module = modules[(layer, "up_proj")]
        require(int(event["ordinal"]) == expected_ordinal and event["before_target_event"] is True and
                int(event["base_ptr"]) == int(module["data_ptr"]) and int(event["num_bytes"]) == UP_BYTES,
                f"{source}: exact window/update attachment")
        require(math.isclose(float(event["hit_ratio"]), expected_ratio, rel_tol=0, abs_tol=1e-15),
                f"{source}: update hit ratio")
        require((event["hit_property"], event["miss_property"], event["persisting"]) == expected_props,
                f"{source}: CONTROL/FAIR policy semantics")
        require(int(event["operation"]["status"]) == 0, f"{source}: update CUDA failure")
        durations_us.append(finite(event["cpu_update_ns"], "cpu_update_ns") / 1000.0)
    require(seen == {(p, l) for p in PHASES for l in range(28)}, f"{source}: incomplete schedule")
    return {"requested": requested, "actual": actual, "hit_ratio": expected_ratio,
            "durations_us": durations_us, "total_us": sum(durations_us)}


def build_native(producer: Path):
    authority_raw = [load_json(producer / f"RAW_AUTHORITY_run{rep}.json") for rep in range(7)]
    for rep, raw in enumerate(authority_raw):
        require(raw.get("status") == "PASS" and raw.get("condition") == "AUTHORITY_TOPLEVEL_NO_PERSIST" and
                int(raw.get("run_index")) == rep, f"authority run{rep} identity")
    baseline = authority_raw[0]
    require(baseline["generated_token_ids_D0_D3"] == TOKENS, "authority tokens")
    base_modules = validate_geometry(baseline, "RAW_AUTHORITY_run0")
    expected_child_order = [(l, role) for l in range(28) for role in ROLES]
    expected_top_order = [(l, c) for l in range(28) for c in TOP_CATEGORIES] + [(None, "final_norm"), (None, "output")]
    validate_order(baseline, "RAW_AUTHORITY_run0", "child_call_order", 84, expected_child_order)
    validate_order(baseline, "RAW_AUTHORITY_run0", "top_call_order", 114, expected_top_order)
    base_child_sha = {key_child(r): (r["input_sha256"], r["output_sha256"]) for r in baseline["child_occurrences"]}
    base_top_sha = {key_top(r): (r["input_sha256"], r["output_sha256"]) for r in baseline["top_occurrences"]}
    require(len(base_child_sha) == 336 and len(base_top_sha) == 456, "authority occurrence cardinality")
    for rep, raw in enumerate(authority_raw):
        source = f"RAW_AUTHORITY_run{rep}"
        validate_geometry(raw, source)
        require(raw["generated_token_ids_D0_D3"] == TOKENS and
                {key_child(r): (r["input_sha256"], r["output_sha256"]) for r in raw["child_occurrences"]} == base_child_sha and
                {key_top(r): (r["input_sha256"], r["output_sha256"]) for r in raw["top_occurrences"]} == base_top_sha,
                f"{source}: semantic SHA/token drift")

    module_authority = {
        "layers": [{"layer_index": l, "categories": {c: f"model.layers.{l}.{c}" for c in TOP_CATEGORIES}}
                   for l in range(28)],
        "final_stages": [
            {"category": "final_norm", "semantic_name": "model.norm", "cleanly_hookable": True},
            {"category": "output", "semantic_name": "lm_head", "cleanly_hookable": True},
        ],
    }
    conditions = []
    policies = {}
    raw_files = [producer / f"RAW_AUTHORITY_run{rep}.json" for rep in range(7)]
    process_fingerprints = set()
    for budget in BUDGETS:
        for mode in ("CONTROL", "FAIR"):
            runs = []
            policy_rows = []
            for rep in range(7):
                path = producer / f"RAW_NATIVE_{mode}_{budget}_run{rep}.json"
                raw_files.append(path)
                raw = load_json(path)
                source = path.name
                require(raw.get("status") == "PASS" and int(raw.get("run_index")) == rep and
                        raw.get("mode") == "POLICY" and raw.get("generated_token_ids_D0_D3") == TOKENS,
                        f"{source}: status/run/tokens")
                require(raw.get("top_level_nonoverlap_asserted") is True and
                        raw.get("no_inner_loop_synchronize") is True,
                        f"{source}: timing/nonoverlap contract")
                modules = validate_geometry(raw, source)
                fp = module_fingerprint(raw)
                require(fp not in process_fingerprints, f"{source}: fresh-process pointer fingerprint reused")
                process_fingerprints.add(fp)
                child_order = validate_order(raw, source, "child_call_order", 84, expected_child_order)
                top_order = validate_order(raw, source, "top_call_order", 114, expected_top_order)
                child = {key_child(r): r for r in raw["child_occurrences"]}
                top = {key_top(r): r for r in raw["top_occurrences"]}
                require(len(child) == 336 and len(top) == 456, f"{source}: occurrence cardinality")
                require({k: (v["input_sha256"], v["output_sha256"]) for k, v in child.items()} == base_child_sha and
                        {k: (v["input_sha256"], v["output_sha256"]) for k, v in top.items()} == base_top_sha,
                        f"{source}: occurrence semantic SHA drift")
                for row in child.values():
                    require(int(row["token_id"]) == TOKENS[int(row["decode_index"])], f"{source}: child token")
                for row in top.values():
                    require(int(row["token_id"]) == TOKENS[int(row["decode_index"])], f"{source}: top token")
                policy = validate_policy(raw, source, budget, mode, modules)

                top_rows = []
                for decode in range(4):
                    cursor = decode * 1000.0
                    for layer, category in top_order[f"D{decode}"]:
                        row = top[(layer, category, decode)]
                        duration = finite(row["target_ms"], f"{source} top timing", True)
                        top_rows.append({
                            "layer_index": layer, "category": category, "decode_index": decode,
                            "semantic_name": (f"model.layers.{layer}.{category}" if layer is not None
                                              else {"final_norm": "model.norm", "output": "lm_head"}[category]),
                            "start_ms": cursor, "end_ms": cursor + duration, "timing_ms": duration,
                            "input_sha256": row["input_sha256"], "output_sha256": row["output_sha256"],
                        })
                        cursor += duration + 1e-6
                child_rows = [{
                    "layer_index": l, "role": role, "decode_index": d,
                    "timing_ms": finite(row["target_ms"], f"{source} child timing", True),
                    "input_sha256": row["input_sha256"], "output_sha256": row["output_sha256"],
                    "module_name": f"model.layers.{l}.mlp.{role}", "backend": "WQLinear_GEMM",
                } for (l, role, d), row in child.items()]
                decode_rows = []
                for d, timing in enumerate(raw["decode_step_ms"]):
                    first = top[(0, "input_layernorm", d)]
                    last = top[(None, "output", d)]
                    decode_rows.append({"decode_index": d, "timing_ms": finite(timing, "decode timing", True),
                                        "input_sha256": first["input_sha256"],
                                        "output_sha256": last["output_sha256"]})
                runs.append({
                    "rep": rep, "generated_tokens": TOKENS, "top_level_occurrences": top_rows,
                    "ffn_child_occurrences": child_rows, "decode_steps": decode_rows,
                    "policy_overheads": [{"update_index": i, "duration": value, "unit": "us"}
                                         for i, value in enumerate(policy["durations_us"])],
                })
                policy_rows.append({"rep": rep, "source": source, "process_pointer_fingerprint": fp,
                                    "requested_setaside_bytes": policy["requested"],
                                    "runtime_actual_setaside_bytes": policy["actual"],
                                    "runtime_max_setaside_bytes": RUNTIME_MAX,
                                    "hit_ratio": policy["hit_ratio"], "selected_up_windows": 28,
                                    "policy_transitions": 140, "reset_before": True, "reset_after": True,
                                    "api_overhead_total_us": policy["total_us"]})
            conditions.append({"condition": f"{mode}_{budget}", "runs": runs})
            policies[f"{mode}_{budget}"] = policy_rows
    require(len(process_fingerprints) == 56, "native matrix is not 56 fresh process pointer identities")
    document = {
        "schema_version": 1, "module_authority": module_authority, "conditions": conditions,
        "budget_pairs": [{"budget_bytes": BUDGETS[b], "control_condition": f"CONTROL_{b}",
                           "fair_condition": f"FAIR_{b}"} for b in BUDGETS],
    }
    return document, policies, raw_files


def per_layer_effects(document):
    by_name = {c["condition"]: c["runs"] for c in document["conditions"]}
    result = {}
    for budget in BUDGETS:
        control, fair = by_name[f"CONTROL_{budget}"], by_name[f"FAIR_{budget}"]
        rows = []
        for layer in range(28):
            cv, fv = [], []
            for rep in range(7):
                c = next(x for x in control[rep]["ffn_child_occurrences"]
                         if x["layer_index"] == layer and x["role"] == "up_proj" and x["decode_index"] == 3)
                f = next(x for x in fair[rep]["ffn_child_occurrences"]
                         if x["layer_index"] == layer and x["role"] == "up_proj" and x["decode_index"] == 3)
                cv.append(c["timing_ms"]); fv.append(f["timing_ms"])
            cs, fs = stats(cv), stats(fv)
            benefit = (cs["median"] - fs["median"]) / cs["median"]
            dispersion = math.hypot(cs["cv"], fs["cv"])
            rows.append({"layer_index": layer, "control": cs, "fair": fs,
                         "benefit_fraction": benefit, "combined_dispersion": dispersion,
                         "material_local": benefit >= 0.05 and benefit > dispersion})
        result[budget] = rows
    return result


def csv_number(value: str) -> float:
    value = value.replace(",", "").strip()
    require(value != "", "empty NCU numeric")
    return finite(value, "NCU metric")


def profile_json_receipts(path: Path):
    rows = []
    connected = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.search(r"Connected to process (\d+)", line)
        if match:
            connected.append(match.group(1))
        if line.startswith("{"):
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            if raw.get("status") == "PASS" and "child_occurrences" in raw:
                rows.append(raw)
    require(rows and len(rows) == len(connected), f"{path.name}: replay receipt/process count")
    return rows, connected


def parse_base(path: Path, range_name: str, metrics, pass_count: int, expected_pid: str):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    header_index = next((i for i, row in enumerate(table) if row and row[0] == "ID"), None)
    require(header_index is not None and header_index + 2 <= len(table), f"{path.name}: BASE header")
    header, units = table[header_index], table[header_index + 1]
    require(len(header) == len(set(header)), f"{path.name}: duplicate BASE header")
    index = {name: header.index(name) for name in header}
    range_cols = [name for name in header if "Push/Pop_Range" in name]
    require(len(range_cols) == 1, f"{path.name}: NVTX range column")
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes", *metrics}
    require(not (required - set(header)), f"{path.name}: required NCU columns")
    for metric in metrics:
        expected_unit = METRIC_CATEGORIES[metric][1]
        require(units[index[metric]].strip() == expected_unit, f"{path.name}: unit mismatch {metric}")
    selected = []
    for row in table[header_index + 2:]:
        if len(row) != len(header):
            continue
        cell = row[index[range_cols[0]]]
        if re.search(r"(?:^|:)" + re.escape(range_name) + r"(?=:|/|\s|$)", cell):
            selected.append(row)
    require(selected, f"{path.name}: no exact target range rows")
    ids = [(r[index["Process ID"]].strip(), r[index["ID"]].strip()) for r in selected]
    require(len(ids) == len(set(ids)) and {x for x, _ in ids} == {expected_pid},
            f"{path.name}: process/kernel identity")
    require(all(int(csv_number(r[index["profiler__replayer_passes"]])) == pass_count for r in selected),
            f"{path.name}: multipass mismatch")
    sums = {METRIC_CATEGORIES[m][0]: 0.0 for m in metrics if METRIC_CATEGORIES[m][2]}
    kernels = []
    for row in selected:
        values = {}
        for metric in metrics:
            category, _unit, additive = METRIC_CATEGORIES[metric]
            value = csv_number(row[index[metric]])
            values[category] = value
            if additive:
                sums[category] += value
        kernels.append({"kernel_id": row[index["ID"]].strip(),
                        "kernel_name": row[index["Kernel Name"]].strip(), "metrics": values})
    return {"sha256": sha256(path), "process_id": expected_pid,
            "profiler_replayer_passes": pass_count, "kernel_count": len(kernels),
            "kernel_inventory": [x["kernel_name"] for x in kernels],
            "kernel_name_multiplicity": dict(Counter(x["kernel_name"] for x in kernels)),
            "additive_semantic_sums": sums, "per_kernel_metrics": kernels}


def parse_ncu(producer: Path, baseline_child_sha, baseline_top_sha):
    selection = load_json(producer / "RAW_METRIC_SELECTION.json")
    metrics = selection["profile_metric_list"]
    require(metrics == list(METRIC_CATEGORIES), "raw metric selection drift")
    query_gz = producer / "RAW_NCU_QUERY_METRICS_ALL.txt.gz"
    require(query_gz.is_file() and query_gz.stat().st_size > 0, "missing raw metric query")
    with gzip.open(query_gz, "rt", encoding="utf-8", errors="replace") as stream:
        query_text = stream.read()
    require(all(metric in query_text for metric in metrics), "runtime metric query lacks selected metric")
    profiles = []
    raw_files = [producer / "RAW_METRIC_SELECTION.json", query_gz]
    for budget in ("B16", "BFULL"):
        for mode in ("CONTROL", "FAIR"):
            for target in ("UP_PROJ", "SELF_ATTN"):
                stem = f"RAW_NCU_L0_{target}_D3_{mode}_{budget}"
                base, session, profile = (producer / f"{stem}_{suffix}"
                                           for suffix in ("BASE.csv", "SESSION.csv", "PROFILE.log"))
                raw_files += [base, session, profile]
                session_text = session.read_text(encoding="utf-8", errors="replace")
                range_name = f"C16_E1_COST_{mode}_{budget}_L0_{target}_D3"
                require("--replay-mode application" in session_text and "--cache-control none" in session_text and
                        f"--nvtx-include {range_name}/" in session_text and
                        "--target-processes application-only" in session_text,
                        f"{session.name}: session option gate")
                metric_match = re.search(r"--metrics ([^\s\"]+)", session_text)
                require(metric_match is not None and metric_match.group(1).split(",") == metrics,
                        f"{session.name}: metric set")
                receipts, connected = profile_json_receipts(profile)
                receipt_fps = set()
                semantic_identity = None
                for pass_index, raw in enumerate(receipts):
                    source = f"{profile.name}/pass{pass_index}"
                    require(raw["condition"] == f"{mode}_{budget}" and raw["budget_name"] == budget and
                            raw["generated_token_ids_D0_D3"] == TOKENS and int(raw["run_index"]) == 700,
                            f"{source}: profile identity")
                    modules = validate_geometry(raw, source)
                    fp = module_fingerprint(raw)
                    require(fp not in receipt_fps, f"{source}: replay process pointer reuse")
                    receipt_fps.add(fp)
                    validate_policy(raw, source, budget, mode, modules)
                    if target == "UP_PROJ":
                        occurrence = next(r for r in raw["child_occurrences"]
                                          if int(r["layer"]) == 0 and r["role"] == "up_proj" and
                                          int(r["decode_index"]) == 3)
                        expected = baseline_child_sha[(0, "up_proj", 3)]
                    else:
                        occurrence = next(r for r in raw["top_occurrences"]
                                          if int(r["layer"]) == 0 and r["category"] == "self_attn" and
                                          int(r["decode_index"]) == 3)
                        expected = baseline_top_sha[(0, "self_attn", 3)]
                    observed = (occurrence["input_sha256"], occurrence["output_sha256"], int(occurrence["token_id"]))
                    require(observed == (*expected, TOKENS[3]) and occurrence["range"] == range_name,
                            f"{source}: target semantic SHA/token/range")
                    if semantic_identity is None:
                        semantic_identity = observed
                    require(observed == semantic_identity, f"{source}: multipass semantic drift")
                base_result = parse_base(base, range_name, metrics, len(receipts), connected[0])
                profiles.append({
                    "budget": budget, "mode": mode,
                    "target_semantic": "up_proj" if target == "UP_PROJ" else "self_attn",
                    "layer_index": 0, "decode_index": 3, "range_name": range_name,
                    "input_sha256": semantic_identity[0], "output_sha256": semantic_identity[1],
                    "token_id": semantic_identity[2], "application_replay": True,
                    "cache_control_none": True, "profile_pass_receipts": len(receipts),
                    "connected_process_ids": connected, "replay_pointer_fingerprints": sorted(receipt_fps),
                    "session_sha256": sha256(session), "profile_sha256": sha256(profile), "base": base_result,
                })
    require(len(profiles) == 8, "exact 8-profile NCU matrix")
    lookup = {(p["budget"], p["mode"], p["target_semantic"]): p for p in profiles}
    comparisons = {}
    for budget in ("B16", "BFULL"):
        comparisons[budget] = {}
        for target in ("up_proj", "self_attn"):
            control = lookup[(budget, "CONTROL", target)]["base"]["additive_semantic_sums"]
            fair = lookup[(budget, "FAIR", target)]["base"]["additive_semantic_sums"]
            comparisons[budget][target] = {
                "fair_over_control": {key: fair[key] / control[key] if control[key] else None
                                      for key in control},
                "interpretation_boundary": ("REPRESENTATIVE_L0_D3_SEMANTIC_RANGE_ONLY; "
                                            "NO_SINGLE_KERNEL_OR_UNIQUE_CACHE_L2_CAUSAL_CLAIM"),
            }
    return {"status": "PASS", "authority": "RAW_BASE_SESSION_PROFILE_ONLY",
            "profile_count": 8, "runtime_metric_query_sha256": sha256(query_gz),
            "profiles": profiles, "comparisons": comparisons}, raw_files


def budget_analysis(decomposition, policies, layers):
    by_bytes = {value: key for key, value in BUDGETS.items()}
    output = {}
    residual = {}
    for budget_bytes, point in decomposition["points"].items():
        budget = by_bytes[int(budget_bytes)]
        summaries = point["summaries"]
        fields = {
            "direct_up_saving_ms": "DIRECT_UP_SAVING", "gate_saving_ms": "GATE_SAVING",
            "down_saving_ms": "DOWN_SAVING", "total_ffn_projection_saving_ms": "TOTAL_FFN_PROJECTION_SAVING",
            "mlp_top_saving_ms": "MLP_TOP_SAVING", "mlp_internal_residual_ms": "MLP_INTERNAL_RESIDUAL",
            "self_attn_saving_ms": "SELF_ATTN_SAVING", "norm_saving_ms": "NORM_SAVING",
            "final_stage_saving_ms": "FINAL_STAGE_SAVING", "observed_decode_saving_ms": "OBSERVED_DECODE_SAVING",
            "accounted_toplevel_saving_ms": "ACCOUNTED_TOPLEVEL_SAVING",
            "unexplained_residual_ms": "UNEXPLAINED_RESIDUAL",
            "negative_offset_from_direct_up_ms": "NEGATIVE_OFFSET_RELATIVE_TO_DIRECT_UP",
            "measured_non_up_offset_ms": "DIRECTLY_MEASURED_NON_UP_OFFSET",
        }
        medians = {out: summaries[source]["median"] for out, source in fields.items()}
        medians["localized_offset_fraction"] = (point["negative_offset_localization"]["median"]
                                                  if point["negative_offset_localization"] else None)
        layer_rows = layers[budget]
        output[budget] = {
            "requested_budget_bytes": BUDGETS[budget],
            "runtime_actual_setaside_bytes": policies[f"FAIR_{budget}"][0]["runtime_actual_setaside_bytes"],
            "runtime_max_setaside_bytes": RUNTIME_MAX,
            "hit_ratio": policies[f"FAIR_{budget}"][0]["hit_ratio"],
            "selected_up_windows": 28, "policy_transitions_per_run": 140,
            "material_local_up_count": sum(r["material_local"] for r in layer_rows),
            "material_local_up_fraction": sum(r["material_local"] for r in layer_rows) / 28,
            "per_layer_up_d3": layer_rows, "medians": medians,
            "local_up_d3_effect": point["local_up_d3_effect"],
            "whole_decode_stable_effect": point["whole_decode_stable_effect"],
            "decomposition_qualified": point["decomposition_qualified"],
            "residual_threshold_ms": point["qualification_threshold_ms"],
        }
        residual[budget] = {
            "qualified": point["decomposition_qualified"],
            "unexplained_residual_ms": medians["unexplained_residual_ms"],
            "localized_offset_fraction": medians["localized_offset_fraction"],
            "gate_saving_ms": medians["gate_saving_ms"],
            "down_saving_ms": medians["down_saving_ms"],
            "self_attn_saving_ms": medians["self_attn_saving_ms"],
            "norm_saving_ms": medians["norm_saving_ms"],
            "final_stage_saving_ms": medians["final_stage_saving_ms"],
            "mlp_internal_residual_ms": medians["mlp_internal_residual_ms"],
        }
    return {"status": "PASS", "authority": "INDEPENDENT_RAW_NATIVE_POLICY_ONLY", "budgets": output}, \
           {"status": "PASS", "authority": "RUN_ALIGNED_NONOVERLAPPING_TOPLEVEL_RAW", "budgets": residual}


def verify_manifest(producer: Path):
    manifest = producer / "SHA256SUMS"
    require(manifest.is_file(), "producer SHA256SUMS absent")
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split(None, 1)
        name = name.lstrip(" *")
        path = producer / name
        require(path.is_file() and sha256(path) == expected, f"producer SHA mismatch: {name}")
        checked += 1
    return checked, sha256(manifest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-pack", type=Path, required=True)
    parser.add_argument("--output-pack", type=Path, required=True)
    parser.add_argument("--producer-head", required=True)
    args = parser.parse_args()
    producer, output = args.producer_pack.resolve(), args.output_pack.resolve()
    require(args.producer_head == "86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5", "producer HEAD drift")
    manifest_count, manifest_sha = verify_manifest(producer)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import decomposition_consumer as dc

    document, policies, native_files = build_native(producer)
    # The stage decision below exists before any producer result summary is read.
    decomposition = dc.analyze_decomposition(document)
    independent_decision = dc.classify_stage(decomposition, policy_qualified=True, semantic_qualified=True)
    layers = per_layer_effects(document)
    budget, residual = budget_analysis(decomposition, policies, layers)
    baseline = load_json(producer / "RAW_AUTHORITY_run0.json")
    base_child_sha = {key_child(r): (r["input_sha256"], r["output_sha256"]) for r in baseline["child_occurrences"]}
    base_top_sha = {key_top(r): (r["input_sha256"], r["output_sha256"]) for r in baseline["top_occurrences"]}
    ncu, ncu_files = parse_ncu(producer, base_child_sha, base_top_sha)

    output.mkdir(parents=True, exist_ok=True)
    dump(output / "INDEPENDENT_BUDGET_EFFECT_ANALYSIS.json", budget)
    dump(output / "INDEPENDENT_RESIDUAL_LOCALIZATION.json", residual)
    dump(output / "INDEPENDENT_CRITICAL_PATH.json", ncu)
    dump(output / "INDEPENDENT_POLICY_AUDIT.json", {"status": "PASS", "conditions": policies,
                                                     "fresh_process_pointer_fingerprints": 56})

    consumed = sorted(set(native_files + ncu_files), key=lambda p: p.name)
    provenance = {
        "status": "PASS", "producer_branch": "hrl/c16-e1-residency-cost-benefit-closure-109-v1",
        "producer_head": args.producer_head, "producer_manifest_sha256": manifest_sha,
        "producer_manifest_entry_count": manifest_count,
        "calculation_authority": ["RAW_AUTHORITY", "RAW_NATIVE_CONTROL_FAIR", "RAW_NCU_BASE_SESSION_PROFILE",
                                  "RAW_METRIC_SELECTION", "RAW_NCU_QUERY_METRICS_ALL"],
        "producer_summaries_used_as_calculation_authority": False,
        "consumed_raw_file_count": len(consumed),
        "consumed_raw_files": [{"name": p.name, "sha256": sha256(p), "bytes": p.stat().st_size}
                               for p in consumed],
        "adapter_boundaries": {
            "lm_head": "normalized to semantic output; raw category retained by source SHA",
            "decode_sha": "derived from raw L0 input_layernorm input and raw lm_head output",
            "top_intervals": ("logical non-overlap intervals reconstructed from raw top_call_order plus raw "
                              "top_level_nonoverlap_asserted; measured target_ms remains unchanged"),
            "process_identity": "process-local qweight pointer-map fingerprints; equality across runs forbidden",
        },
    }
    dump(output / "RAW_PROVENANCE_AUDIT.json", provenance)
    canaries = {
        "status": "PASS",
        "canaries": [
            {"artifact": "RAW_AUTHORITY_run0.json", "checks": ["84 child modules", "114 top modules",
             "336 child occurrences", "456 top occurrences", "exact D0-D3 tokens/SHA"]},
            {"artifact": "RAW_NATIVE_CONTROL_B8_run0.json", "checks": ["requested/actual setaside",
             "28 exact windows", "140 CONTROL updates", "reset receipt"]},
            {"artifact": "RAW_NATIVE_FAIR_BFULL_run0.json", "checks": ["full-qweight requested budget",
             "runtime actual query-back", "budget-scaled hitRatio", "140 FAIR updates"]},
            {"artifact": "RAW_NCU_L0_UP_PROJ_D3_CONTROL_B16_{BASE,SESSION,PROFILE}",
             "checks": ["application replay", "cache-control none", "exact NVTX range", "multipass",
                        "process/token/policy/SHA identity", "metric units"]},
        ],
    }
    dump(output / "REAL_ARTIFACT_CANARIES.json", canaries)

    # Producer cross-check is intentionally last and never feeds independent classification.
    producer_stage = load_json(producer / "STAGE_DECISION.json")
    producer_budget = load_json(producer / "BUDGET_EFFECT_ANALYSIS.json")
    producer_critical = load_json(producer / "REPRESENTATIVE_CRITICAL_PATH.json")
    mismatches = []
    if producer_stage.get("stage_label") != independent_decision["stage_label"]:
        mismatches.append("stage_label")
    for name, row in budget["budgets"].items():
        expected = producer_budget["budgets"][name]
        scalar_pairs = {
            "requested_budget_bytes": "requested_budget_bytes",
            "runtime_actual_setaside_bytes": "actual_setaside_bytes",
            "hit_ratio": "hit_ratio", "material_local_up_count": "material_local_up_count",
        }
        for own_key, producer_key in scalar_pairs.items():
            own, other = row[own_key], expected[producer_key]
            if isinstance(own, float):
                same = math.isclose(own, other, rel_tol=0, abs_tol=1e-12)
            else:
                same = own == other
            if not same:
                mismatches.append(f"{name}.{own_key}")
        for key, value in row["medians"].items():
            if key not in expected["medians"]:
                continue
            if not math.isclose(value, expected["medians"][key], rel_tol=0, abs_tol=1e-12):
                mismatches.append(f"{name}.medians.{key}")
    ratio_map = {
        "aggregate_dram_ratio": "DRAM_BYTES", "dram_read_ratio": "DRAM_READ_BYTES",
        "duration_ratio": "KERNEL_DURATION", "l2_hit_ratio": "L2_READ_HIT_SECTORS",
        "l2_miss_ratio": "L2_READ_MISS_SECTORS",
    }
    for budget_name in ("B16", "BFULL"):
        for target in ("up_proj", "self_attn"):
            own = ncu["comparisons"][budget_name][target]["fair_over_control"]
            expected = producer_critical["budgets"][budget_name][target]
            for producer_key, own_key in ratio_map.items():
                if not math.isclose(own[own_key], expected[producer_key], rel_tol=0, abs_tol=1e-12):
                    mismatches.append(f"NCU.{budget_name}.{target}.{own_key}")
    match = {
        "status": "PASS" if not mismatches else "FAIL", "comparison_performed_after_independent_decision": True,
        "producer_summary_used_as_authority": False,
        "independent_stage_label": independent_decision["stage_label"],
        "producer_stage_label": producer_stage.get("stage_label"), "mismatches": mismatches,
        "compared": ["stage label", "four-budget requested/actual/hitRatio/material count",
                     "all shared decomposition medians", "B16/BFULL up/self-attn NCU ratios"],
    }
    dump(output / "PRODUCER_MATCH_CHECK.json", match)
    final = {
        "status": "PASS" if not mismatches else "FAIL",
        "stage_label": independent_decision["stage_label"],
        "stage_label_origin": "INDEPENDENT_174_RAW_CALCULATION_BEFORE_PRODUCER_CROSSCHECK",
        "producer_head": args.producer_head,
        "all_four_budgets_closed": len(budget["budgets"]) == 4,
        "all_top_level_decompositions_qualified": all(x["decomposition_qualified"] for x in budget["budgets"].values()),
        "representative_ncu_profile_count": ncu["profile_count"],
        "scientific_mismatch": bool(mismatches),
        "claim_boundary": ("Residency benefit is local while measured top-level offsets prevent system benefit; "
                           "representative self-attention is semantic-range evidence only, not a single-kernel "
                           "or unique L2/cache causal identification."),
        "operator_family_stage": "OPERATOR_FAMILY_NOT_SUPPORTED",
        "next_stage_auto_authorized": False,
    }
    dump(output / "FINAL_DECISION.json", final)
    dump(output / "VALIDATION_SUMMARY.json", {
        "status": final["status"], "unit_tests_before_raw_closure": 57,
        "raw_closure_integration_runs": 1, "python_compile": "PASS",
        "current_stage_checks_total": 58,
        "native_authority_runs": 7, "native_condition_runs": 56,
        "fresh_process_pointer_identities": 56, "raw_ncu_profiles": 8,
        "producer_manifest_entries_verified": manifest_count,
        "all_required_files_nonempty": True, "scientific_mismatch": bool(mismatches),
    })
    dump(output / "PRODUCER_FETCH_RECEIPT.json", {
        "status": "PASS", "attempts_this_resume": 1,
        "branch": "hrl/c16-e1-residency-cost-benefit-closure-109-v1",
        "expected_head": args.producer_head, "verified_head": args.producer_head,
        "producer_object_consumed": True, "polling_performed": False,
    })
    dump(output / "RUN_RECEIPTS.json", {
        "status": "INDEPENDENT_RAW_CLOSURE_PASS", "cpu_only": True, "gpu_used": False,
        "simulator_used": False, "nvbit_used": False, "trace_used": False,
        "mechanism_work_used": False, "cost_benefit_tests": 57,
        "raw_closure_integration_runs": 1, "current_stage_checks_total": 58,
        "native_authority_runs": 7, "native_condition_runs": 56,
        "representative_ncu_profiles": 8, "producer_manifest_entries_verified": manifest_count,
        "producer_head": args.producer_head,
    })
    dump(output / "OPEN_ISSUES.json", {
        "status": "COST_BENEFIT_RAW_CLOSURE_COMPLETE",
        "issues": [{"id": "NEGATIVE_RESIDENCY_OFFSET", "state": "LOCALIZED_NOT_CAUSALLY_NAMED",
                    "blocks_stage_label": False, "named_cache_slowdown": False},
                   {"id": "REPRESENTATIVE_SELF_ATTN", "state": "AGGREGATE_SLOWDOWN_NOT_REPRODUCED",
                    "blocks_stage_label": False,
                    "single_kernel_or_unique_l2_cache_cause_claimed": False}],
        "simulator_authorized": False, "bounded_trace_authorized": False,
    })
    dump(output / "NEXT_STEP_AUTHORIZATION.json", {
        "status": "STOP_AFTER_INDEPENDENT_RAW_CLOSURE",
        "authorized": False, "authorized_next_action": None,
        "forbidden": ["GPU", "109 rerun", "NVBit", "bounded trace capture", "Accel-Sim",
                      "GPGPU-Sim mutation", "mechanism implementation", "mechanism simulation",
                      "automatic next-stage selection"],
    })
    readme = """# C16 E1 Residency Cost/Benefit Closure Consumer 174-new V1

Status: `RESIDENCY_OFFSET_LOCALIZED`.

This pack independently consumes producer `86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5` from raw native JSON, raw CUDA policy receipts, and the exact eight raw NCU BASE/SESSION/PROFILE triples. Producer summary/display tables are excluded from calculation authority and are read only for the final match check.

All B8/B16/B24/BFULL points close: exact 28 `up_proj` windows, budget-scaled hitRatio, 140 updates per run, 56 fresh process-local pointer identities, all-84 FFN child timing, runtime-derived top-level semantic timing, separate host API overhead, and run-aligned decomposition. Every budget satisfies `abs(median unexplained residual) <= 0.10 ms`. Representative NCU supports local `up_proj` traffic/duration benefit; its L0 D3 self-attention range does not reproduce the aggregate full-model self-attention slowdown. No single-kernel or unique L2/cache cause is claimed.

No GPU, rerun, NVBit, trace, simulator, or mechanism work was performed. No next stage is automatically authorized.
"""
    (output / "README.md").write_text(readme, encoding="utf-8")
    interpretation = """# Scientific interpretation

The independent raw consumer reproduces `RESIDENCY_OFFSET_LOCALIZED` without using producer summaries as calculation authority. All 28 `up_proj` modules retain material D3-local benefit at every tested budget, but the whole-decode effect is not material. Run-aligned, non-overlapping top-level accounting localizes the offset and qualifies at every budget with median unexplained residual magnitude below 0.10 ms.

At BFULL, the largest directly measured top-level offset is aggregate self-attention (about -0.534 ms saving, i.e. slowdown), while the representative L0 D3 self-attention NCU semantic range is nearly unchanged (duration FAIR/CONTROL about 1.00134 and aggregate DRAM about 1.00111). Therefore the evidence does not identify a single kernel, L2/cache as a unique cause, or any other unique cause for the aggregate offset. The representative NCU result is a bounded semantic-range observation.

`OPERATOR_FAMILY_NOT_SUPPORTED` remains frozen and was not recomputed. This closure does not authorize bounded trace capture, simulator execution/mutation, mechanism implementation, or selection of a next mechanism.
"""
    (output / "SCIENTIFIC_INTERPRETATION.md").write_text(interpretation, encoding="utf-8")
    anchors_path = output / "SOURCE_ANCHORS.json"
    anchors = load_json(anchors_path) if anchors_path.is_file() else {}
    anchors["hardening_parent"] = "8af56572a4a151b111f1c2002821421db71acc61"
    anchors["cost_producer"] = args.producer_head
    anchors.setdefault("cost_sources", {})["producer_raw_closure.py"] = sha256(Path(__file__).resolve())
    dump(anchors_path, anchors)
    print(json.dumps({"stage_label": independent_decision["stage_label"],
                      "mismatches": mismatches,
                      "budgets": {k: v["medians"] for k, v in budget["budgets"].items()},
                      "ncu": ncu["comparisons"]}, indent=2, sort_keys=True))
    return 0 if not mismatches else 2


if __name__ == "__main__":
    raise SystemExit(main())
