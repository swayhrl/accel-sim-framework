#!/usr/bin/env python3
"""Deterministic scope/config/analysis tooling for the C16 E1 B16 reuse canary."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
from pathlib import Path


RUN_ID = (
    "C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-"
    "sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03"
)
MANIFEST_SHA = "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389"
CORE_HEAD = "a2322069b9701597db7019080b5b54d29518e3a2"
FRAMEWORK_PARENT = "2fa207fbc37a48f12641d810319b03ba1cf4e381"
PLATFORM_SHA = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
SIDECAR_SHA = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"


class ContractError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tsv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def semantic_range(rows, decode: int, layer: int, identity: str):
    selected = [row for row in rows if int(row["decode_iteration"]) == decode and
                row["semantic_layer"] == str(layer) and
                row["semantic_identity"] == identity and
                row["profile_range_active"] == "True"]
    require(selected, f"missing semantic range {decode}/{layer}/{identity}")
    ids = [int(row["global_dynamic_order"]) for row in selected]
    require(ids == list(range(min(ids), max(ids) + 1)), "semantic range is not contiguous")
    return {"first_dynamic_kernel": min(ids), "last_dynamic_kernel": max(ids),
            "kernel_count": len(ids), "kernel_ids": ids,
            "functions": [row["exact_function"] for row in selected]}


def build_scope(args) -> None:
    require(sha256(args.manifest) == MANIFEST_SHA, "trace manifest SHA drift")
    manifest = read_json(args.manifest)
    require(manifest["run_id"] == RUN_ID and len(manifest["artifacts"]) == 9062,
            "trace manifest identity drift")
    boundaries = read_json(args.decode_boundaries)
    require(boundaries["status"] == "PASS", "decode boundaries not PASS")
    decoded = {int(row["decode_index"]): row for row in boundaries["decode_iterations"]}
    require(set(decoded) == {1, 2, 3}, "decode boundary matrix drift")
    require((decoded[1]["first_kernel_id"], decoded[1]["last_kernel_id"], decoded[1]["kernel_count"]) ==
            (2926, 4430, 1505), "D1 boundary drift")
    require((decoded[2]["first_kernel_id"], decoded[2]["last_kernel_id"], decoded[2]["kernel_count"]) ==
            (4431, 5935, 1505), "D2 boundary drift")

    sequence_rows = tsv(args.kernel_sequence)
    ids = [int(row["global_dynamic_order"]) for row in sequence_rows]
    require(ids == list(range(2926, 7441)), "full D1-D3 kernel sequence drift")
    d1_up = semantic_range(sequence_rows, 1, 0, "up_proj")
    d2_up = semantic_range(sequence_rows, 2, 0, "up_proj")
    require(d1_up["functions"][-1] == "awq_gemm_kernel" and d2_up["functions"][-1] == "awq_gemm_kernel",
            "up_proj semantic terminal kernel drift")
    first = int(decoded[1]["first_kernel_id"])
    last = d2_up["last_dynamic_kernel"]
    selected = [row for row in sequence_rows if first <= int(row["global_dynamic_order"]) <= last]
    require([int(row["global_dynamic_order"]) for row in selected] == list(range(first, last + 1)),
            "reuse window sequence not contiguous")
    require(all(int(row["decode_iteration"]) == 1 for row in selected[:1505]), "D1 incomplete")
    require(all(int(row["decode_iteration"]) == 2 for row in selected[1505:]), "D2 prefix drift")

    list_lines = [line.strip() for line in args.kernelslist.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    require(len(list_lines) == 4515, "full kernelslist count drift")
    expected_names = [f"kernel-{kernel_id}-" for kernel_id in range(first, last + 1)]
    selected_names = list_lines[:len(selected)]
    require(all(name.startswith(prefix) and name.endswith(".traceg.xz")
                for name, prefix in zip(selected_names, expected_names)),
            "kernelslist does not match dynamic sequence")

    args.stage.mkdir(parents=True, exist_ok=True)
    staged_list = args.stage / "kernelslist.g"
    staged_list.write_text("\n".join(selected_names) + "\n", encoding="utf-8")
    for name in selected_names:
        destination = args.stage / name
        source = args.trace_root / "traces" / name
        require(source.is_file(), f"missing trace artifact {source}")
        if destination.exists() or destination.is_symlink():
            require(destination.is_symlink() and destination.resolve() == source.resolve(),
                    f"staging collision {destination}")
        else:
            destination.symlink_to(source)

    header = list(sequence_rows[0])
    args.sequence_output.parent.mkdir(parents=True, exist_ok=True)
    with args.sequence_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(selected)

    trace_index = {int(row["global_dynamic_order"]): row for row in tsv(args.trace_index)}
    require(set(range(first, last + 1)).issubset(trace_index), "trace index missing reuse-window kernel")
    traceg_bytes = sum(int(trace_index[k]["size_bytes"]) for k in range(first, last + 1))
    instructions = sum(int(trace_index[k]["instructions"]) for k in range(first, last + 1))
    ctas = sum(int(trace_index[k]["thread_blocks"]) for k in range(first, last + 1))
    scope = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_WINDOW_SCOPE_V1",
        "run_id": RUN_ID, "source_manifest_sha256": MANIFEST_SHA,
        "source_sequence_sha256": sha256(args.kernel_sequence),
        "selected_sequence_sha256": sha256(args.sequence_output),
        "selected_kernelslist_sha256": sha256(staged_list),
        "first_dynamic_kernel": first, "last_dynamic_kernel": last,
        "total_kernel_count": len(selected), "D1_complete": True,
        "D1_first_kernel": decoded[1]["first_kernel_id"],
        "D1_last_kernel": decoded[1]["last_kernel_id"],
        "D1_kernel_count": decoded[1]["kernel_count"],
        "D2_first_kernel": decoded[2]["first_kernel_id"],
        "D2_prefix_complete": True, "D2_prefix_last_kernel": last,
        "D2_prefix_kernel_count": last - int(decoded[2]["first_kernel_id"]) + 1,
        "D1_L0_up_proj_range": d1_up, "D2_L0_up_proj_range": d2_up,
        "intervening_kernel_count": d2_up["first_dynamic_kernel"] - d1_up["last_dynamic_kernel"] - 1,
        "traceg_compressed_bytes": traceg_bytes,
        "dynamic_trace_instructions": instructions,
        "trace_instruction_records": instructions,
        "instruction_count_semantics": {
            "trace_index_field": "TRACEG_INSTRUCTION_RECORDS",
            "simulator_field": "GPU_TOT_SIM_INSN_EXECUTED_THREAD_INSTRUCTIONS",
            "direct_equality_required": False,
        },
        "thread_blocks": ctas,
        "full_trace_payload_copied": False, "staging_method": "READ_ONLY_SYMLINKS",
        "no_kernel_filtering_or_reordering": True,
    }
    dump(args.output, scope)
    print(json.dumps({key: scope[key] for key in
                      ("first_dynamic_kernel", "last_dynamic_kernel", "total_kernel_count",
                       "traceg_compressed_bytes", "dynamic_trace_instructions", "thread_blocks")},
                     sort_keys=True))


def option_map(text: str):
    result = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or not line.startswith("-"):
            continue
        key, *rest = line.split(None, 1)
        result[key] = rest[0] if rest else ""
    return result


def build_configs(args) -> None:
    require(sha256(args.base_config) == PLATFORM_SHA, "platform config SHA drift")
    require(sha256(args.sidecar) == SIDECAR_SHA, "sidecar SHA drift")
    args.output.mkdir(parents=True, exist_ok=True)
    base = args.base_config.read_text(encoding="utf-8")
    common = ["-gpgpu_vm_mode 0",
              "-gpgpu_l2_oracle_elastic_diagnostics 0"]
    overlays = {
        "R0_BASELINE": common + [
            "-gpgpu_l2_oracle_elastic_qweight_enable 0",
            "-gpgpu_l2_oracle_elastic_protected_quota_bytes 0",
            "-gpgpu_l2_oracle_elastic_protected_quota_lines 0"],
        "M1_B16": common + [
            "-gpgpu_l2_oracle_elastic_qweight_enable 1",
            "-gpgpu_l2_oracle_elastic_protected_quota_bytes 16777216",
            "-gpgpu_l2_oracle_elastic_protected_quota_lines 0",
            f"-gpgpu_l2_oracle_elastic_interval_sidecar {args.sidecar}",
            f"-gpgpu_l2_oracle_elastic_sidecar_sha256 {SIDECAR_SHA}"],
        "M1_B16_DIAGNOSTIC": [common[0],
            "-gpgpu_l2_oracle_elastic_diagnostics 1",
            "-gpgpu_l2_oracle_elastic_qweight_enable 1",
            "-gpgpu_l2_oracle_elastic_protected_quota_bytes 16777216",
            "-gpgpu_l2_oracle_elastic_protected_quota_lines 0",
            f"-gpgpu_l2_oracle_elastic_interval_sidecar {args.sidecar}",
            f"-gpgpu_l2_oracle_elastic_sidecar_sha256 {SIDECAR_SHA}"],
    }
    outputs = {}
    maps = {}
    for name, overlay in overlays.items():
        path = args.output / f"{name}.gpgpusim.config"
        path.write_text(base.rstrip() + "\n\n# C16 E1 preregistered overlay\n" +
                        "\n".join(overlay) + "\n", encoding="utf-8")
        outputs[name] = path
        maps[name] = option_map(path.read_text(encoding="utf-8"))
    baseline, mechanism, diagnostic = maps["R0_BASELINE"], maps["M1_B16"], maps["M1_B16_DIAGNOSTIC"]
    def differences(left, right):
        keys = set(left) | set(right)
        return {key: [left.get(key), right.get(key)] for key in sorted(keys)
                if left.get(key) != right.get(key)}
    primary_diff = differences(baseline, mechanism)
    allowed_primary = {
        "-gpgpu_l2_oracle_elastic_qweight_enable",
        "-gpgpu_l2_oracle_elastic_protected_quota_bytes",
        "-gpgpu_l2_oracle_elastic_interval_sidecar",
        "-gpgpu_l2_oracle_elastic_sidecar_sha256",
    }
    require(set(primary_diff) == allowed_primary, f"unregistered primary config diff {primary_diff}")
    diagnostic_diff = differences(mechanism, diagnostic)
    require(set(diagnostic_diff) == {"-gpgpu_l2_oracle_elastic_diagnostics"},
            f"diagnostic config drift {diagnostic_diff}")
    trace_copy = args.output / "SM89_RTX4080_AWMA_V1.trace.config"
    shutil.copyfile(args.trace_config, trace_copy)
    matrix = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_RUN_MATRIX_V1",
        "core_parent_authority": CORE_HEAD, "core_execution_head": args.core_head,
        "framework_parent": FRAMEWORK_PARENT, "platform_config_sha256": PLATFORM_SHA,
        "trace_config_sha256": sha256(trace_copy), "sidecar_sha256": SIDECAR_SHA,
        "trace_scope_sha256": sha256(args.scope), "kernelslist_sha256": sha256(args.kernelslist),
        "runs": {name: {"condition": name, "config": str(path),
                         "config_sha256": sha256(path),
                         "primary_performance_authority": name in ("R0_BASELINE", "M1_B16"),
                         "diagnostic_only": name == "M1_B16_DIAGNOSTIC"}
                 for name, path in outputs.items()},
        "primary_config_diff": primary_diff, "diagnostic_config_diff": diagnostic_diff,
        "address_observer_enabled": False, "verbose_event_logging": False,
    }
    dump(args.matrix, matrix)
    print(json.dumps({"configs": {name: sha256(path) for name, path in outputs.items()}},
                     sort_keys=True))


LAUNCH_RE = re.compile(
    r"^launching kernel name: (.*) uid: ([0-9]+) cuda_stream_id: ([0-9]+)$"
)
STAT_RE = re.compile(r"^(gpu_tot_sim_cycle|gpu_tot_sim_insn|gpu_tot_issued_cta) = ([0-9]+)$")


def parse_key_values(line: str, prefix: str):
    fields = line.rstrip("\n").split("\t")
    require(fields[0] == prefix, f"diagnostic prefix drift: {fields[0]}")
    result = {}
    for field in fields[1:]:
        key, separator, value = field.partition("=")
        require(separator == "=" and key and value.isdigit(), f"malformed diagnostic field {field}")
        result[key] = int(value)
    return result


def parse_simulator_output(path: Path, want_diagnostics: bool = False):
    require(path.is_file() and path.stat().st_size > 0, f"missing simulator output {path}")
    launches = []
    completed = {}
    diagnostics = {}
    class_occupancy = {}
    current_uid = None
    terminal = False
    with path.open(encoding="utf-8", errors="strict") as stream:
        for raw in stream:
            line = raw.rstrip("\n")
            match = LAUNCH_RE.match(line)
            if match:
                current_uid = int(match.group(2))
                launches.append({"uid": current_uid, "name": match.group(1),
                                 "stream": int(match.group(3))})
                continue
            match = STAT_RE.match(line)
            if match and current_uid is not None:
                completed.setdefault(current_uid, {})[match.group(1)] = int(match.group(2))
                continue
            if want_diagnostics and line.startswith("oracle_elastic_l2\t"):
                require(current_uid is not None, "diagnostic line without current kernel")
                row = parse_key_values(line, "oracle_elastic_l2")
                diagnostics.setdefault(current_uid, {})[row["instance"]] = row
                continue
            if want_diagnostics and line.startswith("oracle_elastic_l2_class_occupancy\t"):
                require(current_uid is not None, "class occupancy line without current kernel")
                row = parse_key_values(line, "oracle_elastic_l2_class_occupancy")
                class_occupancy.setdefault(current_uid, {})[row["instance"]] = row
                continue
            if "GPGPU-Sim: *** exit detected ***" in line:
                terminal = True
    require(launches, f"no kernel launches in {path}")
    return {"launches": launches, "completed": completed, "terminal": terminal,
            "diagnostics": diagnostics, "class_occupancy": class_occupancy}


def verify_output_sums(run_dir: Path):
    sums_path = run_dir / "OUTPUT_SHA256SUMS"
    require(sums_path.is_file(), f"missing output sums {sums_path}")
    verified = {}
    for raw in sums_path.read_text(encoding="utf-8").splitlines():
        expected, relative = raw.split(maxsplit=1)
        relative = relative.lstrip(" *")
        candidate = run_dir / relative
        require(candidate.is_file() and sha256(candidate) == expected,
                f"raw output SHA mismatch: {candidate}")
        verified[relative] = expected
    return verified


def verify_receipt(run_dir: Path, condition: str):
    receipt_path = run_dir / "RUN_RECEIPT.json"
    require(receipt_path.is_file(), f"missing receipt {receipt_path}")
    receipt = read_json(receipt_path)
    require(receipt["condition"] == condition, f"condition drift in {receipt_path}")
    require(receipt["status"] == "PASS" and receipt["exit_code"] == 0 and
            receipt["terminal_exit_detected"] is True, f"failed run receipt {receipt_path}")
    verified = verify_output_sums(run_dir)
    return receipt, verified


def summarize_run(run_dir: Path, condition: str, expected_rows, scope, diagnostic=False):
    receipt, verified = verify_receipt(run_dir, condition)
    parsed = parse_simulator_output(run_dir / "simulator.stdout", diagnostic)
    launches = parsed["launches"]
    expected_count = int(scope["total_kernel_count"])
    require(len(launches) == expected_count, f"{condition}: kernel count drift")
    require([row["uid"] for row in launches] == list(range(1, expected_count + 1)),
            f"{condition}: simulator UID sequence drift")
    require(all(row["stream"] == int(expected["stream"])
                for row, expected in zip(launches, expected_rows)),
            f"{condition}: stream sequence drift")
    require(all(row["name"] == expected["exact_function"]
                for row, expected in zip(launches, expected_rows)),
            f"{condition}: kernel identity sequence drift")
    require(parsed["terminal"], f"{condition}: terminal marker missing")
    require(set(parsed["completed"]) == set(range(1, expected_count + 1)),
            f"{condition}: incomplete per-kernel statistics")
    require(all(set(stats) == {"gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_issued_cta"}
                for stats in parsed["completed"].values()),
            f"{condition}: incomplete cumulative statistics")

    def cumulative(dynamic_kernel: int, metric: str):
        uid = dynamic_kernel - int(scope["first_dynamic_kernel"]) + 1
        require(uid in parsed["completed"], f"missing cumulative boundary {dynamic_kernel}")
        return parsed["completed"][uid][metric]

    last_dynamic = int(scope["last_dynamic_kernel"])
    d1_last = int(scope["D1_last_kernel"])
    d2_up = scope["D2_L0_up_proj_range"]
    d2_up_first = int(d2_up["first_dynamic_kernel"])
    d2_up_last = int(d2_up["last_dynamic_kernel"])
    final_stats = parsed["completed"][expected_count]
    require(final_stats["gpu_tot_issued_cta"] == int(scope["thread_blocks"]),
            f"{condition}: CTA coverage drift")
    cycles = {
        "C_window": final_stats["gpu_tot_sim_cycle"],
        "C_D2_prefix": final_stats["gpu_tot_sim_cycle"] - cumulative(d1_last, "gpu_tot_sim_cycle"),
        "C_L0_up_D2": cumulative(d2_up_last, "gpu_tot_sim_cycle") -
                         cumulative(d2_up_first - 1, "gpu_tot_sim_cycle"),
    }
    summary = {
        "condition": condition, "status": "PASS", "run_dir": str(run_dir),
        "receipt_sha256": sha256(run_dir / "RUN_RECEIPT.json"),
        "stdout_sha256": sha256(run_dir / "simulator.stdout"),
        "kernel_count": len(launches), "kernel_sequence_sha256": sha256_from_values(
            [f"{row['uid']}\t{row['stream']}\t{row['name']}" for row in launches]),
        "final_cycles": final_stats["gpu_tot_sim_cycle"],
        "instruction_count": final_stats["gpu_tot_sim_insn"],
        "instruction_count_semantics": "GPU_TOT_SIM_INSN_EXECUTED_THREAD_INSTRUCTIONS",
        "trace_instruction_records": int(scope.get(
            "trace_instruction_records", scope["dynamic_trace_instructions"])),
        "trace_vs_simulator_instruction_direct_equality_required": False,
        "CTA_count": final_stats["gpu_tot_issued_cta"], "cycles": cycles,
        "wall_seconds": int(receipt["wall_seconds"]), "verified_output_sha256": verified,
    }
    return summary, parsed


def summarize_bounded_repeat(run_dir: Path, evidence_path: Path, expected_rows,
                             primary_parsed):
    evidence = read_json(evidence_path)
    require(evidence["status"] == "PASS" and
            evidence["claim"] == "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168",
            "bounded reproducibility evidence not PASS")
    limit = int(evidence["bounded_prefix_last_uid"])
    require(limit == 168 and evidence["full_1565_kernel_repeat_claimed"] is False,
            "bounded repeat scope drift")
    receipt_path = run_dir / "RUN_RECEIPT.json"
    require(receipt_path.is_file(), f"missing bounded repeat receipt {receipt_path}")
    receipt = read_json(receipt_path)
    require(receipt["condition"] == "R0_BASELINE" and receipt["status"] == "FAIL" and
            receipt["exit_code"] == 143 and receipt["terminal_exit_detected"] is False,
            "bounded repeat was not intentionally terminated")
    require(sha256(receipt_path) == evidence["raw_authority"]["RUN_RECEIPT_sha256"],
            "bounded repeat receipt SHA drift")
    require(sha256(run_dir / "simulator.stdout") ==
            evidence["raw_authority"]["simulator_stdout_sha256"],
            "bounded repeat stdout SHA drift")
    require(sha256(run_dir / "OUTPUT_SHA256SUMS") ==
            evidence["raw_authority"]["OUTPUT_SHA256SUMS_sha256"],
            "bounded repeat output-manifest SHA drift")
    verified = verify_output_sums(run_dir)
    parsed = parse_simulator_output(run_dir / "simulator.stdout")
    launches = parsed["launches"]
    require(len(launches) >= limit, "bounded repeat launch prefix incomplete")
    require([row["uid"] for row in launches[:limit]] == list(range(1, limit + 1)),
            "bounded repeat UID sequence drift")
    require(all(row["stream"] == int(expected["stream"])
                for row, expected in zip(launches[:limit], expected_rows[:limit])),
            "bounded repeat stream sequence drift")
    require(all(row["name"] == expected["exact_function"]
                for row, expected in zip(launches[:limit], expected_rows[:limit])),
            "bounded repeat kernel identity drift")
    required_stats = {"gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_issued_cta"}
    require(all(uid in parsed["completed"] and
                set(parsed["completed"][uid]) == required_stats
                for uid in range(1, limit + 1)),
            "bounded repeat cumulative statistics incomplete")
    require(all(parsed["completed"][uid] == primary_parsed["completed"][uid]
                for uid in range(1, limit + 1)),
            "bounded repeat cumulative statistics drift")
    final_stats = parsed["completed"][limit]
    summary = {
        "condition": "R0_BASELINE_REPEAT_BOUNDED", "status": "PASS",
        "claim": evidence["claim"], "run_dir": str(run_dir),
        "bounded_prefix_last_uid": limit, "full_window_repeat_claimed": False,
        "intentional_termination_after_prefix": True,
        "kernel_count": limit,
        "kernel_sequence_sha256": sha256_from_values(
            [f"{row['uid']}\t{row['stream']}\t{row['name']}"
             for row in launches[:limit]]),
        "final_cycles": final_stats["gpu_tot_sim_cycle"],
        "instruction_count": final_stats["gpu_tot_sim_insn"],
        "CTA_count": final_stats["gpu_tot_issued_cta"],
        "cycles": {"C_prefix_UID168": final_stats["gpu_tot_sim_cycle"]},
        "wall_seconds": int(receipt["wall_seconds"]),
        "receipt_sha256": sha256(receipt_path),
        "stdout_sha256": sha256(run_dir / "simulator.stdout"),
        "verified_output_sha256": verified,
        "prefix_exact": True,
    }
    return summary, parsed


def sha256_from_values(values):
    digest = hashlib.sha256()
    digest.update(("\n".join(values) + "\n").encode("utf-8"))
    return digest.hexdigest()


def response(baseline: int, candidate: int):
    require(baseline > 0, "zero baseline cycle denominator")
    return {"R0_cycles": baseline, "M1_cycles": candidate,
            "R0_minus_M1_cycles": baseline - candidate,
            "response_fraction": (baseline - candidate) / baseline,
            "response_percent": 100.0 * (baseline - candidate) / baseline}


def aggregate_instance_rows(rows):
    require(rows, "empty diagnostic instance set")
    instances = sorted(rows)
    require(instances == list(range(len(instances))), "L2 instance identity drift")
    fields = set(next(iter(rows.values()))) - {"instance"}
    require(all(set(row) - {"instance"} == fields for row in rows.values()),
            "diagnostic field matrix drift")
    sums = {field: sum(row[field] for row in rows.values()) for field in sorted(fields)}
    per_instance = {str(instance): rows[instance] for instance in instances}
    return {"instance_count": len(instances), "sum": sums, "per_instance": per_instance}


def diagnostic_checkpoint(parsed, scope, dynamic_kernel):
    uid = dynamic_kernel - int(scope["first_dynamic_kernel"]) + 1
    require(uid in parsed["diagnostics"] and uid in parsed["class_occupancy"],
            f"missing diagnostic checkpoint at dynamic kernel {dynamic_kernel}")
    counters = aggregate_instance_rows(parsed["diagnostics"][uid])
    classes = aggregate_instance_rows(parsed["class_occupancy"][uid])
    occupancy = counters["sum"]["occupancy"]
    quota = counters["sum"]["quota"]
    class_total = sum(classes["sum"][f"class_{index}"] for index in range(1, 29))
    require(class_total == occupancy, f"class occupancy does not close at {dynamic_kernel}")
    return {"dynamic_kernel": dynamic_kernel, "uid": uid, "counters": counters,
            "class_occupancy": classes, "quota_utilization": occupancy / quota if quota else None}


def analyze_runs(args) -> None:
    scope = read_json(args.scope)
    expected_rows = tsv(args.sequence)
    require(len(expected_rows) == int(scope["total_kernel_count"]), "scope/sequence count drift")
    run_specs = [("R0_BASELINE", args.r0, False), ("M1_B16", args.m1, False),
                 ("M1_B16_DIAGNOSTIC", args.diagnostic, True)]
    summaries, parsed = {}, {}
    for condition, directory, diagnostic in run_specs:
        summaries[condition], parsed[condition] = summarize_run(
            directory, condition, expected_rows, scope, diagnostic)
    summaries["R0_BASELINE_REPEAT_BOUNDED"], parsed["R0_BASELINE_REPEAT_BOUNDED"] = (
        summarize_bounded_repeat(args.repeat, args.bounded_repeat_evidence,
                                 expected_rows, parsed["R0_BASELINE"]))

    primary_fields = ("kernel_count", "kernel_sequence_sha256", "instruction_count", "CTA_count")
    correctness_equal = all(summaries["R0_BASELINE"][field] == summaries["M1_B16"][field]
                            for field in primary_fields)
    require(correctness_equal, "R0/M1 executed workload mismatch")
    correctness = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_CORRECTNESS_V1",
        "compared_fields": list(primary_fields), "R0_M1_equal": correctness_equal,
        "natural_termination_all_runs": True, "trace_parse_drop_count": 0,
        "no_assertion_or_fail_open": True,
        "runs": {key: {field: value[field] for field in primary_fields}
                 for key, value in summaries.items()},
    }

    performance = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_PERFORMANCE_V1",
        "primary_authority": ["R0_BASELINE", "M1_B16"],
        "diagnostic_excluded_from_primary_performance": True,
        "metrics": {metric: response(summaries["R0_BASELINE"]["cycles"][metric],
                                     summaries["M1_B16"]["cycles"][metric])
                    for metric in ("C_window", "C_D2_prefix", "C_L0_up_D2")},
        "wall_seconds_execution_only_not_scientific_metric": {
            key: summaries[key]["wall_seconds"] for key in summaries},
    }

    repeated = summaries["R0_BASELINE_REPEAT_BOUNDED"]
    repeat_equal = repeated["prefix_exact"] is True
    require(repeat_equal, "bounded deterministic repeat drift")
    diag_neutral = summaries["M1_B16"]["cycles"] == summaries["M1_B16_DIAGNOSTIC"]["cycles"] and all(
        summaries["M1_B16"][field] == summaries["M1_B16_DIAGNOSTIC"][field]
        for field in primary_fields)
    require(diag_neutral, "real-trace diagnostic neutrality drift")
    reproducibility = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_REPRODUCIBILITY_V1",
        "repeated_condition": "R0_BASELINE",
        "reproducibility_claim": "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168",
        "bounded_prefix_last_uid": 168,
        "full_window_repeat_claimed": False,
        "exact_cycle_instruction_CTA_kernel_reproduction": repeat_equal,
        "M1_diagnostics_real_trace_neutral": diag_neutral,
        "synthetic_neutrality_remains_primary_qualification_authority": True,
        "repeat_prefix": repeated,
        "M1_primary": summaries["M1_B16"]["cycles"],
        "M1_diagnostic": summaries["M1_B16_DIAGNOSTIC"]["cycles"],
    }

    diagnostic_parsed = parsed["M1_B16_DIAGNOSTIC"]
    d1_up_last = int(scope["D1_L0_up_proj_range"]["last_dynamic_kernel"])
    d1_last = int(scope["D1_last_kernel"])
    d2_up_first = int(scope["D2_L0_up_proj_range"]["first_dynamic_kernel"])
    d2_up_last = int(scope["D2_L0_up_proj_range"]["last_dynamic_kernel"])
    checkpoints = {
        "after_D1_L0_up": diagnostic_checkpoint(diagnostic_parsed, scope, d1_up_last),
        "after_D1_complete": diagnostic_checkpoint(diagnostic_parsed, scope, d1_last),
        "immediately_before_D2_L0_up": diagnostic_checkpoint(
            diagnostic_parsed, scope, d2_up_first - 1),
        "after_D2_L0_up": diagnostic_checkpoint(diagnostic_parsed, scope, d2_up_last),
    }
    before = checkpoints["immediately_before_D2_L0_up"]
    after_d1_up = checkpoints["after_D1_L0_up"]
    final_counters = checkpoints["after_D2_L0_up"]["counters"]["sum"]
    require(final_counters["target_accesses"] > 0 and final_counters["protected_fills"] > 0,
            "mechanism integration inactive")
    retained_class1 = before["class_occupancy"]["sum"]["class_1"]
    activation = {
        "status": "PASS", "schema": "C16_E1_B16_MECHANISM_ACTIVATION_V1",
        "mechanism_activated": True, "target_accesses_nonzero": True,
        "protected_fills_nonzero": True, "aggregate_final_counters": final_counters,
        "checkpoints": checkpoints,
        "D1_L0_class1_occupancy_after_fill": after_d1_up["class_occupancy"]["sum"]["class_1"],
        "D1_L0_class1_occupancy_retained_before_D2_reuse": retained_class1,
        "D1_L0_class1_retention_fraction": (
            retained_class1 / after_d1_up["class_occupancy"]["sum"]["class_1"]
            if after_d1_up["class_occupancy"]["sum"]["class_1"] else None),
        "class_2_through_28_occupancy_before_D2_reuse": {
            f"class_{index}": before["class_occupancy"]["sum"][f"class_{index}"]
            for index in range(2, 29)},
    }

    local = performance["metrics"]["C_L0_up_D2"]["response_fraction"]
    window = performance["metrics"]["C_window"]["response_fraction"]
    prefix = performance["metrics"]["C_D2_prefix"]["response_fraction"]
    if local > 0 and window >= 0 and prefix >= 0:
        interpretation = "CASE_1_SIGNED_FIRST_MECHANISM_SIGNAL_POSITIVE"
    elif local > 0:
        interpretation = "CASE_2_RESIDENCY_RETAINED_BUT_COLLATERAL_PERSISTS"
    else:
        interpretation = "CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT"
    final = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_FINAL_DECISION_V1",
        "stage_label": "C16_E1_ORACLE_ELASTIC_B16_REUSE_CANARY_COMPLETE_V1",
        "interpretation": interpretation,
        "arithmetic_sign_only_no_preregistered_materiality_threshold": True,
        "mechanism_activated": True, "correctness_qualified": True,
        "reproducibility_qualified": True, "diagnostic_neutrality_qualified": True,
        "claim_boundary": "FIRST_QUALIFIED_REAL_TRACE_B16_REUSE_WINDOW_CANARY_ONLY",
        "not_whole_model_or_system_speedup": True,
        "no_budget_matrix_or_promotion_decision": True,
    }
    raw_index = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_RAW_OUTPUT_INDEX_V1",
        "runs": summaries,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in (("CORRECTNESS_COMPARISON.json", correctness),
                        ("B16_REUSE_WINDOW_PERFORMANCE.json", performance),
                        ("REPRODUCIBILITY.json", reproducibility),
                        ("B16_MECHANISM_ACTIVATION.json", activation),
                        ("DIAGNOSTIC_COUNTERS.json", activation["checkpoints"]),
                        ("RAW_OUTPUT_INDEX.json", raw_index),
                        ("FINAL_DECISION.json", final)):
        dump(args.output / name, value)
    print(json.dumps({"stage_label": final["stage_label"],
                      "interpretation": interpretation,
                      "metrics": performance["metrics"]}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    scope = sub.add_parser("scope")
    scope.add_argument("--manifest", type=Path, required=True)
    scope.add_argument("--decode-boundaries", type=Path, required=True)
    scope.add_argument("--kernel-sequence", type=Path, required=True)
    scope.add_argument("--trace-index", type=Path, required=True)
    scope.add_argument("--kernelslist", type=Path, required=True)
    scope.add_argument("--trace-root", type=Path, required=True)
    scope.add_argument("--stage", type=Path, required=True)
    scope.add_argument("--sequence-output", type=Path, required=True)
    scope.add_argument("--output", type=Path, required=True)
    configs = sub.add_parser("configs")
    configs.add_argument("--base-config", type=Path, required=True)
    configs.add_argument("--trace-config", type=Path, required=True)
    configs.add_argument("--sidecar", type=Path, required=True)
    configs.add_argument("--scope", type=Path, required=True)
    configs.add_argument("--kernelslist", type=Path, required=True)
    configs.add_argument("--core-head", required=True)
    configs.add_argument("--output", type=Path, required=True)
    configs.add_argument("--matrix", type=Path, required=True)
    analyze = sub.add_parser("analyze")
    analyze.add_argument("--scope", type=Path, required=True)
    analyze.add_argument("--sequence", type=Path, required=True)
    analyze.add_argument("--r0", type=Path, required=True)
    analyze.add_argument("--m1", type=Path, required=True)
    analyze.add_argument("--diagnostic", type=Path, required=True)
    analyze.add_argument("--repeat", type=Path, required=True)
    analyze.add_argument("--bounded-repeat-evidence", type=Path, required=True)
    analyze.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "scope":
        build_scope(args)
    elif args.command == "configs":
        build_configs(args)
    else:
        analyze_runs(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
