#!/usr/bin/env python3
"""One-pass, CPU-only audit of the published C16 E1 B16 terminal evidence.

Reads only the four completed hash-bound stdout paths in the fixed publication's
RAW_OUTPUT_INDEX. Each stdout is hashed while it is parsed exactly once. This
does not invoke a simulator, GPU tool, or another Lane's output directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUBLICATION = "71324d46435293edab3b7a0ff6ee999e675be0d0"
PUBLICATION_TREE = "9d022115e0407eceb145e4f6f6dc69b1907f865f"
SNAPSHOT = "8dfd9c0fdc98314c2aa11710da9b89f59e4c7a66"
CORE = "0271de82432db004beed43280ed01057246a0f2c"
BINARY = "6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186"
PACK = "docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1"
OUT = ROOT / "docs/vm_tlb/review_packs/C16_E1_LANE4_TERMINAL_REVIEW_V1"
RAW_ROOT = Path("/root/share/mnt164/huangrulin/c16_ai_workload/consumer_runs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1_20260926T0506Z")
CONDITIONS = ("R0_BASELINE", "M1_B16", "M1_B16_DIAGNOSTIC", "R0_BASELINE_REPEAT_BOUNDED")
RAW_NAMES = {"R0_BASELINE_REPEAT_BOUNDED": "R0_BASELINE_REPEAT"}
LAUNCH = re.compile(r"^launching kernel name: (.*) uid: ([0-9]+) cuda_stream_id: ([0-9]+)$")
STAT = re.compile(r"^(gpu_tot_sim_cycle|gpu_tot_sim_insn|gpu_tot_issued_cta) = ([0-9]+)$")
STAT_KEYS = {"gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_issued_cta"}
COUNTER_KEYS = {
    "quota", "occupancy", "occupancy_max", "target_accesses", "target_hits",
    "target_misses", "protected_fills", "protected_hits", "target_normal_victims",
    "target_protected_victims", "normal_normal_victims",
    "normal_fallback_protected_victims", "quota_full_events",
    "ordinary_borrowing_fills", "ordinary_borrowing_current",
    "ordinary_borrowing_max", "protected_protected_replacements",
    "target_protection_admission_denied", "denial_quota_full_invalid_priority",
    "denial_quota_full_no_local_protected",
}
ADDITIVE_COUNTERS = sorted(COUNTER_KEYS - {"quota", "occupancy", "occupancy_max",
                                           "ordinary_borrowing_current", "ordinary_borrowing_max"})
WINDOWS = ("C_window", "C_D2_prefix", "C_L0_up_D2")
CHECKPOINT_UIDS = {"after_D1_L0_up": 60, "after_D1_complete": 1505,
                   "immediately_before_D2_L0_up": 1563, "after_D2_L0_up": 1565}


class AuditError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AuditError(reason)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], stderr=subprocess.PIPE)


def committed_bytes(name: str) -> bytes:
    return git("show", f"{PUBLICATION}:{PACK}/{name}")


def committed_json(name: str, validation: dict | None = None) -> tuple[dict, str]:
    raw = committed_bytes(name)
    digest = hashlib.sha256(raw).hexdigest()
    if validation and name in validation.get("input_artifacts", {}):
        expected = validation["input_artifacts"][name]
        require(digest == expected["sha256"] and len(raw) == expected["bytes"],
                f"published source hash/size mismatch: {name}")
    value = json.loads(raw)
    require(isinstance(value, dict), f"non-object source: {name}")
    return value, digest


def parse_fields(line: str, prefix: str) -> dict[str, int]:
    fields = line.split("\t")
    require(fields[0] == prefix, f"diagnostic prefix mismatch: {prefix}")
    result: dict[str, int] = {}
    for field in fields[1:]:
        key, sep, value = field.partition("=")
        require(sep == "=" and key and value.isdigit() and key not in result,
                "malformed/duplicate diagnostic field")
        result[key] = int(value)
    return result


def parse_stdout(path: Path, expected_sha: str, expected_rows: list[dict],
                 diagnostic: bool, bounded_repeat: bool) -> dict:
    sha = hashlib.sha256()
    launches: list[tuple[int, int, str]] = []
    completed: dict[int, dict[str, int]] = {}
    checkpoint: dict[str, dict] = {}
    current_uid: int | None = None
    terminal = False
    counter_rows: dict[int, dict[str, int]] = {}
    class_rows: dict[int, dict[str, int]] = {}
    total_counter_rows = total_class_rows = 0

    def finish_uid(uid: int | None) -> None:
        nonlocal total_counter_rows, total_class_rows
        if uid is None or not diagnostic:
            return
        require(set(counter_rows) == set(range(16)) and set(class_rows) == set(range(16)),
                f"diagnostic UID {uid} missing/duplicate instance row")
        totals = {key: 0 for key in COUNTER_KEYS}
        class_totals = {f"class_{i}": 0 for i in range(1, 29)}
        for instance in range(16):
            counters = counter_rows[instance]
            classes = class_rows[instance]
            require(set(counters) == COUNTER_KEYS | {"instance"}, "counter schema drift")
            require(set(classes) == set(class_totals) | {"instance"}, "class schema drift")
            require(counters["quota"] == 8192 and counters["occupancy"] <= 8192,
                    "per-instance quota/occupancy drift")
            require(sum(classes[f"class_{i}"] for i in range(1, 29)) == counters["occupancy"],
                    "per-instance class occupancy does not close")
            for key in totals:
                totals[key] += counters[key]
            for key in class_totals:
                class_totals[key] += classes[key]
        require(totals["quota"] == 131072 and sum(class_totals.values()) == totals["occupancy"],
                "aggregate diagnostic quota/class drift")
        total_counter_rows += 16
        total_class_rows += 16
        for label, wanted in CHECKPOINT_UIDS.items():
            if uid == wanted:
                checkpoint[label] = {"uid": uid, "dynamic_kernel": 2925 + uid,
                                     "counters_sum": totals, "class_1_occupancy": class_totals["class_1"],
                                     "class_occupancy_sum": class_totals}
        counter_rows.clear()
        class_rows.clear()

    with path.open("rb") as stream:
        for binary_line in stream:
            sha.update(binary_line)
            line = binary_line.decode("utf-8", errors="strict").rstrip("\r\n")
            match = LAUNCH.match(line)
            if match:
                finish_uid(current_uid)
                current_uid = int(match.group(2))
                launches.append((current_uid, int(match.group(3)), match.group(1)))
                require(current_uid == len(launches), "UID sequence drift")
                require(current_uid <= len(expected_rows), "more launches than frozen sequence")
                expected = expected_rows[current_uid - 1]
                require(int(expected["stream"]) == int(match.group(3)) and
                        expected["exact_function"] == match.group(1),
                        f"frozen ordered kernel mismatch at UID {current_uid}")
                continue
            match = STAT.match(line)
            if match and current_uid is not None:
                slot = completed.setdefault(current_uid, {})
                require(match.group(1) not in slot, f"duplicate cumulative field at UID {current_uid}")
                slot[match.group(1)] = int(match.group(2))
                continue
            if line.startswith("oracle_elastic_l2\t"):
                require(diagnostic and current_uid is not None, "unexpected diagnostic counter line")
                row = parse_fields(line, "oracle_elastic_l2")
                instance = row["instance"]
                require(instance not in counter_rows, "duplicate diagnostic instance counter")
                counter_rows[instance] = row
                continue
            if line.startswith("oracle_elastic_l2_class_occupancy\t"):
                require(diagnostic and current_uid is not None, "unexpected class occupancy line")
                row = parse_fields(line, "oracle_elastic_l2_class_occupancy")
                instance = row["instance"]
                require(instance not in class_rows, "duplicate diagnostic instance class")
                class_rows[instance] = row
                continue
            if "GPGPU-Sim: *** exit detected ***" in line:
                terminal = True
    finish_uid(current_uid)
    require(sha.hexdigest() == expected_sha, f"raw stdout SHA mismatch: {path}")
    require(len(launches) >= (168 if bounded_repeat else 1565), "incomplete launch coverage")
    if not bounded_repeat:
        require(len(launches) == 1565 and terminal, "primary/diagnostic terminal coverage missing")
    else:
        require(not terminal, "bounded repeat must retain nonterminal receipt")
    require(set(completed) >= set(range(1, 169)) if bounded_repeat else
            set(completed) == set(range(1, 1566)), "cumulative UID coverage missing")
    require(all(set(completed[uid]) == STAT_KEYS for uid in
                (range(1, 169) if bounded_repeat else range(1, 1566))),
            "incomplete cumulative fields")
    if diagnostic:
        require(total_counter_rows == 25040 and total_class_rows == 25040 and
                set(checkpoint) == set(CHECKPOINT_UIDS), "diagnostic coverage mismatch")
    launch_values = [f"{uid}\t{stream}\t{name}" for uid, stream, name in
                     (launches[:168] if bounded_repeat else launches)]
    sequence_sha = hashlib.sha256(("\n".join(launch_values) + "\n").encode()).hexdigest()
    per_uid_sha = hashlib.sha256("".join(
        f"{uid}\t{completed[uid]['gpu_tot_sim_cycle']}\t{completed[uid]['gpu_tot_sim_insn']}\t{completed[uid]['gpu_tot_issued_cta']}\n"
        for uid in range(1, 169 if bounded_repeat else 1566)).encode()).hexdigest()
    return {"stdout_sha256": sha.hexdigest(), "terminal_marker": terminal,
            "launches": launches, "completed": completed,
            "kernel_count": len(launches), "kernel_sequence_sha256": sequence_sha,
            "per_uid_stats_sha256": per_uid_sha,
            "diagnostic_counter_rows": total_counter_rows,
            "diagnostic_class_rows": total_class_rows, "checkpoints": checkpoint}


def verify_raw_run(condition: str, index: dict, receipts: dict, expected_rows: list[dict]) -> tuple[dict, dict]:
    raw_name = RAW_NAMES.get(condition, condition)
    info = index["runs"][condition]
    receipt_pack = receipts["runs"][condition]
    run_dir = Path(info["run_dir"])
    require(run_dir.resolve() == (RAW_ROOT / raw_name).resolve(), f"out-of-scope raw dir: {condition}")
    require(receipt_pack["run_dir"] == info["run_dir"], "receipt/index run dir mismatch")
    require(receipt_pack["output_manifest_sha256"] == info["output_manifest_sha256"],
            "receipt/index output manifest mismatch")
    receipt_bytes = (run_dir / "RUN_RECEIPT.json").read_bytes()
    receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()
    require(receipt_sha == info["receipt_sha256"] == receipt_pack["receipt_sha256"],
            f"raw receipt SHA mismatch: {condition}")
    receipt = json.loads(receipt_bytes)
    require(receipt == receipt_pack["receipt"], f"raw receipt differs from published copy: {condition}")
    require(receipt["core_head_at_launch"] == CORE and receipt["binary_sha256"] == BINARY,
            f"execution Core/binary drift: {condition}")
    launch_bytes = (run_dir / "LAUNCH_AUTHORITY.json").read_bytes()
    require(hashlib.sha256(launch_bytes).hexdigest() ==
            info["verified_output_sha256"]["LAUNCH_AUTHORITY.json"] ==
            receipt["launch_authority_sha256"],
            f"launch authority SHA mismatch: {condition}")
    launch_authority = json.loads(launch_bytes)
    for field in ("core_head_at_launch", "framework_head_at_launch", "binary_sha256",
                  "config_sha256", "trace_config_sha256", "kernelslist_sha256", "runner_sha256"):
        require(launch_authority[field] == receipt[field],
                f"launch authority/receipt identity mismatch: {condition}/{field}")
    require(receipt["kernelslist_sha256"] == "f9a952e2d52420a850dc28554be208a2dd1d7894260d8bff87153637740a5ae8",
            "kernelslist launch drift")
    manifest_bytes = (run_dir / "OUTPUT_SHA256SUMS").read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() == info["output_manifest_sha256"],
            f"raw manifest SHA mismatch: {condition}")
    manifest = {}
    for line in manifest_bytes.decode().splitlines():
        digest, name = line.split(maxsplit=1)
        manifest[name.lstrip(" *")] = digest
    require(manifest.get("simulator.stdout") == info["stdout_sha256"] and
            manifest.get("RUN_RECEIPT.json") == receipt_sha,
            f"stdout/receipt not bound in raw manifest: {condition}")
    repeat = condition == "R0_BASELINE_REPEAT_BOUNDED"
    if repeat:
        require(receipt["status"] == "FAIL" and receipt["exit_code"] == 143 and
                receipt["terminal_exit_detected"] is False, "bounded repeat receipt rewritten")
    else:
        require(receipt["status"] == "PASS" and receipt["exit_code"] == 0 and
                receipt["terminal_exit_detected"] is True, f"nonterminal primary/diagnostic: {condition}")
    parsed = parse_stdout(run_dir / "simulator.stdout", info["stdout_sha256"], expected_rows,
                          diagnostic=condition == "M1_B16_DIAGNOSTIC", bounded_repeat=repeat)
    require(parsed["kernel_sequence_sha256"] == info["kernel_sequence_sha256"],
            f"kernel sequence digest mismatch: {condition}")
    if not repeat:
        final = parsed["completed"][1565]
        require(final["gpu_tot_issued_cta"] == 1259187 and
                final["gpu_tot_sim_insn"] == info["instruction_count"] and
                final["gpu_tot_sim_cycle"] == info["final_cycles"],
                f"final cumulative stats mismatch: {condition}")
    return parsed, receipt


def cycle_windows(completed: dict[int, dict[str, int]]) -> dict[str, int]:
    c = lambda uid: completed[uid]["gpu_tot_sim_cycle"]
    return {"C_window": c(1565), "C_D2_prefix": c(1565) - c(1505),
            "C_L0_up_D2": c(1565) - c(1563)}


def main(output_dir: Path) -> None:
    require(git("rev-parse", f"{PUBLICATION}^{{tree}}").decode().strip() == PUBLICATION_TREE,
            "publication tree mismatch")
    require(git("merge-base", SNAPSHOT, PUBLICATION).decode().strip() == SNAPSHOT,
            "publication does not descend from frozen snapshot")
    validation, _ = committed_json("VALIDATION_SUMMARY.json")
    require(validation["status"] == "PASS", "publication validation not PASS")
    index, index_sha = committed_json("RAW_OUTPUT_INDEX.json", validation)
    receipts, receipt_pack_sha = committed_json("RUN_RECEIPTS.json", validation)
    activation, activation_sha = committed_json("B16_MECHANISM_ACTIVATION.json", validation)
    correctness, correctness_sha = committed_json("CORRECTNESS_COMPARISON.json", validation)
    performance, performance_sha = committed_json("B16_REUSE_WINDOW_PERFORMANCE.json", validation)
    reproducibility, reproducibility_sha = committed_json("REPRODUCIBILITY.json", validation)
    admission, admission_sha = committed_json("PRIMARY_DIAGNOSTIC_ADMISSION_GATE.json", validation)
    decision, decision_sha = committed_json("FINAL_DECISION.json", validation)
    scope, scope_sha = committed_json("REUSE_WINDOW_SCOPE.json", validation)
    matrix, matrix_sha = committed_json("RUN_MATRIX.json", validation)
    host, host_sha = committed_json("HOST_SCALE_AND_TELEMETRY_QUALIFICATION.json", validation)
    final_diagnostic_admission, final_diagnostic_admission_sha = committed_json(
        "M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json", validation)
    original_diagnostic_admission_bytes = git("show", f"{SNAPSHOT}:{PACK}/M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json")
    original_diagnostic_admission = json.loads(original_diagnostic_admission_bytes)
    require(original_diagnostic_admission["scientific_admission"] == "SPECULATIVE_PRE_GATE" and
            final_diagnostic_admission["scientific_admission"] == "ADMITTED",
            "diagnostic launch/admission states conflated")
    selected_raw = committed_bytes("REUSE_WINDOW_SEQUENCE.tsv")
    selected_sha = hashlib.sha256(selected_raw).hexdigest()
    require(selected_sha == validation["input_artifacts"]["REUSE_WINDOW_SEQUENCE.tsv"]["sha256"],
            "frozen ordered sequence SHA mismatch")
    rows = list(csv.DictReader(io.StringIO(selected_raw.decode()), delimiter="\t"))
    require(len(rows) == 1565 and [int(r["global_dynamic_order"]) for r in rows] ==
            list(range(2926, 4491)), "frozen ordered sequence length/order drift")
    require(scope["total_kernel_count"] == 1565 and scope["selected_sequence_sha256"] == selected_sha and
            matrix["trace_scope_sha256"] == scope_sha and matrix["kernelslist_sha256"] == scope["selected_kernelslist_sha256"],
            "run matrix / reuse scope identity mismatch")
    require(matrix["core_execution_head"] == CORE and host["core_execution_head"] == CORE and
            host["binary_sha256"] == BINARY, "committed execution authority mismatch")
    require(set(index["runs"]) == set(CONDITIONS) and set(receipts["runs"]) == set(CONDITIONS),
            "raw index/receipt condition matrix drift")

    parsed = {}
    raw_receipts = {}
    for condition in CONDITIONS:
        parsed[condition], raw_receipts[condition] = verify_raw_run(condition, index, receipts, rows)
        print(f"verified one-pass stdout: {condition}", flush=True)
        config_condition = "R0_BASELINE" if condition == "R0_BASELINE_REPEAT_BOUNDED" else condition
        require(raw_receipts[condition]["config_sha256"] == matrix["runs"][config_condition]["config_sha256"] and
                raw_receipts[condition]["trace_config_sha256"] == matrix["trace_config_sha256"] and
                raw_receipts[condition]["kernelslist_sha256"] == matrix["kernelslist_sha256"],
                f"launch config/trace/list identity drift: {condition}")
        if condition != "R0_BASELINE_REPEAT_BOUNDED":
            calculated = cycle_windows(parsed[condition]["completed"])
            require(calculated == index["runs"][condition]["cycles"],
                    f"published primary/diagnostic cycle mismatch: {condition}")

    r0, m1, diagnostic, repeat = (parsed[name] for name in CONDITIONS)
    for uid in range(1, 1566):
        require(r0["launches"][uid - 1] == m1["launches"][uid - 1] == diagnostic["launches"][uid - 1],
                f"launch identity mismatch at UID {uid}")
        for metric in ("gpu_tot_sim_insn", "gpu_tot_issued_cta"):
            require(r0["completed"][uid][metric] == m1["completed"][uid][metric],
                    f"R0/M1 workload metric mismatch at UID {uid}: {metric}")
        require(m1["completed"][uid] == diagnostic["completed"][uid],
                f"primary/diagnostic neutrality mismatch at UID {uid}")
    for uid in range(1, 169):
        require(r0["launches"][uid - 1] == repeat["launches"][uid - 1] and
                r0["completed"][uid] == repeat["completed"][uid],
                f"bounded repeat prefix mismatch at UID {uid}")
    require(reproducibility["reproducibility_claim"] ==
            "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168" and
            reproducibility["full_window_repeat_claimed"] is False and
            correctness["R0_M1_equal"] is True and admission["status"] == "PASS",
            "published correctness/admission/repeat boundary mismatch")

    responses = {}
    for window in WINDOWS:
        base = cycle_windows(r0["completed"])[window]
        candidate = cycle_windows(m1["completed"])[window]
        responses[window] = {"R0_cycles": base, "M1_cycles": candidate,
                             "R0_minus_M1_cycles": base - candidate,
                             "response_fraction": (base - candidate) / base}
        published = performance["metrics"][window]
        require(responses[window]["R0_cycles"] == published["R0_cycles"] and
                responses[window]["M1_cycles"] == published["M1_cycles"] and
                responses[window]["R0_minus_M1_cycles"] == published["R0_minus_M1_cycles"] and
                abs(responses[window]["response_fraction"] - published["response_fraction"]) < 1e-15,
                f"independent timing mismatch: {window}")

    checkpoints = diagnostic["checkpoints"]
    for label, got in checkpoints.items():
        published = activation["checkpoints"][label]
        require(got["counters_sum"] == published["counters"]["sum"] and
                got["class_occupancy_sum"] == published["class_occupancy"]["sum"],
                f"independent diagnostic checkpoint mismatch: {label}")
    final = checkpoints["after_D2_L0_up"]["counters_sum"]
    require(final == activation["aggregate_final_counters"], "final mechanism counters mismatch")
    require(final["target_accesses"] == 57099207 and final["protected_fills"] == 7691289 and
            final["protected_protected_replacements"] == 7560217 and
            final["target_protection_admission_denied"] == 0 and
            final["normal_fallback_protected_victims"] == 0 and
            checkpoints["after_D1_L0_up"]["class_1_occupancy"] == 131072 and
            checkpoints["immediately_before_D2_L0_up"]["class_1_occupancy"] == 0,
            "requested mechanism/census invariants drift")
    before = checkpoints["after_D1_L0_up"]["counters_sum"]
    after = checkpoints["immediately_before_D2_L0_up"]["counters_sum"]
    delta = {key: after[key] - before[key] for key in ADDITIVE_COUNTERS}
    require(all(value >= 0 for value in delta.values()), "nonmonotone cumulative diagnostic")

    ancestry = {}
    for condition, receipt in raw_receipts.items():
        head = receipt["framework_head_at_launch"]
        require(git("merge-base", head, PUBLICATION).decode().strip() == head and
                git("merge-base", head, SNAPSHOT).decode().strip() == head,
                f"launch source is not an ancestor of snapshot/publication: {condition}")
        ancestry[condition] = {"actual_launch_framework_head": head,
                               "ancestor_of_historical_snapshot": True,
                               "ancestor_of_publication": True}

    independent = {
        "schema": "C16_E1_LANE4_TERMINAL_INDEPENDENT_RECOMPUTE_V1",
        "status": "PASS_CPU_ONLY_DERIVED",
        "publication_commit": PUBLICATION, "publication_tree": PUBLICATION_TREE,
        "historical_contract_snapshot": SNAPSHOT, "core_execution_commit": CORE,
        "binary_sha256": BINARY, "actual_launch_framework_heads": ancestry,
        "ordered_scope": {"first_dynamic_kernel": 2926, "last_dynamic_kernel": 4490,
                          "D1_kernel_count": 1505, "D2_prefix_kernel_count": 60,
                          "kernel_count": 1565, "selected_sequence_sha256": selected_sha},
        "raw_stdout_sha256": {name: parsed[name]["stdout_sha256"] for name in CONDITIONS},
        "per_uid_stats_sha256": {name: parsed[name]["per_uid_stats_sha256"] for name in CONDITIONS},
        "primary_and_diagnostic_1565_UID_identity": "PASS",
        "primary_diagnostic_per_UID_cycle_instruction_CTA_neutrality": "PASS",
        "diagnostic_counter_rows": diagnostic["diagnostic_counter_rows"],
        "diagnostic_class_rows": diagnostic["diagnostic_class_rows"],
        "bounded_repeat": {"claim": "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168",
                           "raw_receipt_status": "FAIL_INTENTIONAL_EXIT_143_NONTERMINAL",
                           "prefix_exact": True, "full_window_repeat_claimed": False},
        "primary_timing": responses,
        "mechanism_final_counters": final,
        "checkpoints": checkpoints,
        "D1_L0_end_to_pre_D2_L0_additive_counter_delta": delta,
        "D1_L0_end_to_pre_D2_L0_class1_occupancy_change": -131072,
        "delta_scope_caveat": "ALL_L2_INSTANCES_ALL_TARGET_CLASSES_NOT_CLASS1_CAUSAL_ATTRIBUTION",
        "old_address_or_fill_generation_survival": None,
        "whole_decode_claimed": False,
        "statistical_materiality_claimed": False,
    }

    packet = {
        "schema": "C16_LANE4_TERMINAL_GATE_INPUT_V1",
        "publication_status": "TERMINAL_REVIEW_READY",
        "authority": {
            "lane3_commit": "a402828860ced26124ddbf3c9d87baa6f6774d55",
            "literature_commit": "350e4a0d364d65812f379ebc69412696e2a4d82a",
            "lane4_framework_snapshot": SNAPSHOT, "core_commit": CORE,
        },
        "identity": {
            "run_matrix_sha256": matrix_sha, "binary_sha256": BINARY,
            "r0_config_sha256": matrix["runs"]["R0_BASELINE"]["config_sha256"],
            "m1_b16_config_sha256": matrix["runs"]["M1_B16"]["config_sha256"],
            "diagnostic_config_sha256": matrix["runs"]["M1_B16_DIAGNOSTIC"]["config_sha256"],
            "kernelslist_sha256": matrix["kernelslist_sha256"],
            "platform_sha256": matrix["platform_config_sha256"],
            "sidecar_sha256": matrix["sidecar_sha256"],
            "trace_scope_sha256": scope_sha, "reuse_sequence_sha256": selected_sha,
            "source_manifest_sha256": scope["source_manifest_sha256"],
            "total_kernels": 1565,
        },
        "terminal_receipts": {
            name: {"status": "PASS", "exit_code": 0, "terminal_marker": True,
                   "receipt_sha256": index["runs"][name]["receipt_sha256"]}
            for name in ("R0_BASELINE", "M1_B16", "M1_B16_DIAGNOSTIC")
        },
        "reuse_window_scope": {
            "status": "PASS", "first_dynamic_kernel": scope["first_dynamic_kernel"],
            "D1_last_kernel": scope["D1_last_kernel"],
            "D2_prefix_last_kernel": scope["D2_prefix_last_kernel"],
            "last_dynamic_kernel": scope["last_dynamic_kernel"],
            "D1_kernel_count": scope["D1_kernel_count"],
            "D2_prefix_kernel_count": scope["D2_prefix_kernel_count"],
            "total_kernel_count": scope["total_kernel_count"],
            "thread_blocks": scope["thread_blocks"],
            "no_kernel_filtering_or_reordering": scope["no_kernel_filtering_or_reordering"],
            "selected_sequence_sha256": selected_sha,
        },
        "workload_identity": {
            name: {"kernel_count": parsed[name]["kernel_count"],
                   "kernel_sequence_sha256": parsed[name]["kernel_sequence_sha256"],
                   "instruction_count": parsed[name]["completed"][1565]["gpu_tot_sim_insn"],
                   "CTA_count": parsed[name]["completed"][1565]["gpu_tot_issued_cta"]}
            for name in ("R0_BASELINE", "M1_B16")
        },
        "primary_correctness": {"status": "PASS", "R0_M1_equal": True,
                                "comparison_sha256": correctness_sha},
        "primary_timing": {"status": "PASS", "performance_sha256": performance_sha,
                           "cycles": {name: {"R0_cycles": responses[name]["R0_cycles"],
                                             "M1_cycles": responses[name]["M1_cycles"]}
                                      for name in WINDOWS}},
        "diagnostic": {
            "pre_gate_status": "SPECULATIVE_PRE_GATE",
            "neutrality_status": "PASS", "counters_status": "PASS",
            "diagnostic_sha256": activation_sha,
            "counters": {
                "target_accesses": final["target_accesses"],
                "protected_fills": final["protected_fills"],
                "protected_protected_evictions": final["protected_protected_replacements"],
                "protected_victim_evictions": final["target_protected_victims"],
                "eligible_target_fills": final["protected_fills"] +
                                         final["target_protection_admission_denied"],
                "quota_denials_invalid_priority": final["denial_quota_full_invalid_priority"],
                "quota_denials_no_local_protected_victim": final["denial_quota_full_no_local_protected"],
                "D1_class1_after_fill": checkpoints["after_D1_L0_up"]["class_1_occupancy"],
                "D1_class1_before_D2": checkpoints["immediately_before_D2_L0_up"]["class_1_occupancy"],
                "old_address_survivors": None, "old_address_population": None,
            },
        },
    }
    require(packet["diagnostic"]["counters"]["eligible_target_fills"] == final["protected_fills"] and
            final["target_protection_admission_denied"] == 0,
            "target fill-outcome denominator not closed for this packet")
    provenance = {
        "schema": "C16_E1_LANE4_TERMINAL_PACKET_FIELD_PROVENANCE_V1",
        "status": "DERIVED_RECONSTRUCTED_FROM_COMMITTED_TERMINAL_EVIDENCE",
        "publication_commit": PUBLICATION, "publication_tree": PUBLICATION_TREE,
        "not_lane4_original_packet": True,
        "source_files": {
            "RAW_OUTPUT_INDEX.json": index_sha, "RUN_RECEIPTS.json": receipt_pack_sha,
            "B16_MECHANISM_ACTIVATION.json": activation_sha,
            "CORRECTNESS_COMPARISON.json": correctness_sha,
            "B16_REUSE_WINDOW_PERFORMANCE.json": performance_sha,
            "REPRODUCIBILITY.json": reproducibility_sha,
            "PRIMARY_DIAGNOSTIC_ADMISSION_GATE.json": admission_sha,
            "FINAL_DECISION.json": decision_sha, "REUSE_WINDOW_SCOPE.json": scope_sha,
            "REUSE_WINDOW_SEQUENCE.tsv": selected_sha, "RUN_MATRIX.json": matrix_sha,
            "HOST_SCALE_AND_TELEMETRY_QUALIFICATION.json": host_sha,
            "M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json": final_diagnostic_admission_sha,
            "M1_B16_DIAGNOSTIC_ADMISSION_STATUS_at_8dfd9c0f.json":
                hashlib.sha256(original_diagnostic_admission_bytes).hexdigest(),
        },
        "packet_fields": {
            "authority.lane4_framework_snapshot": "HISTORICAL_PREREG_SNAPSHOT_8dfd9c0f_NOT_PUBLICATION_OR_LAUNCH",
            "identity.binary_sha256": "HOST_SCALE_AND_TELEMETRY_QUALIFICATION_AND_EXACT_RAW_RUN_RECEIPTS",
            "terminal_receipts": "RUN_RECEIPTS_COPY_PLUS_RAW_RECEIPT_SHA_VERIFICATION",
            "reuse_window_scope": "COMMITTED_REUSE_WINDOW_SCOPE_AND_ORDERED_SEQUENCE_SHA",
            "workload_identity": "ONE_PASS_RAW_STDOUT_PER_UID_RECOMPUTE_AND_CORRECTNESS_COMPARISON",
            "primary_timing": "ONE_PASS_RAW_STDOUT_CUMULATIVE_BOUNDARIES_1565_1505_1563",
            "diagnostic.neutrality_status": "M1_VS_DIAGNOSTIC_EXACT_ALL_1565_UID_CYCLE_INSN_CTA",
            "diagnostic.counters.protected_protected_evictions": "Core_gpu-cache.cc_target_miss_quota_full_protected_victim_event:protected_protected_replacements",
            "diagnostic.counters.protected_victim_evictions": "Core_gpu-cache.cc_target_miss_valid_protected_victim_event:target_protected_victims",
            "diagnostic.counters.eligible_target_fills": "DERIVED_TARGET_FILL_DECISION_OUTCOMES=committed_protected_fills+target_protection_admission_denied;denied=0;NOT_target_misses_or_accesses",
            "diagnostic.counters.quota_denials_invalid_priority": "Core_gpu-cache.cc:denial_quota_full_invalid_priority",
            "diagnostic.counters.quota_denials_no_local_protected_victim": "Core_gpu-cache.cc:denial_quota_full_no_local_protected",
            "diagnostic.counters.D1_class1_after_fill": "UID60_class_occupancy_sum.class_1",
            "diagnostic.counters.D1_class1_before_D2": "UID1563_class_occupancy_sum.class_1",
            "diagnostic.counters.old_address_survivors": "UNOBSERVED_NULL",
            "diagnostic.counters.old_address_population": "UNOBSERVED_NULL",
        },
        "core_counter_source": {
            "commit": CORE, "gpu_cache_cc_sha256": "f33ff9f94facfbc4c20ca6020763305615dce4caee66eb3ff7ea9d9a17981dee",
            "oracle_elastic_residency_cc_sha256": "6b7155a6689c5d18370ce85604b57ccd06688217a24141a4c889a63bbfe8f220",
            "protected_fills_commit_event_line": 346,
            "target_victim_and_denial_events_lines": [622, 633],
        },
        "interpretation_boundaries": [
            "eligible_target_fills_is_outcome_denominator_not_all_tagged_accesses",
            "checkpoint_interval_counter_deltas_are_global_not_class1_specific",
            "class_occupancy_is_not_exact_old_address_or_fill_generation_survival",
            "bounded_repeat_is_not_full_terminal_PASS",
            "no_posthoc_high_low_materiality_threshold",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in (("INDEPENDENT_RECOMPUTE.json", independent),
                        ("TERMINAL_REVIEW_PACKET.json", packet),
                        ("PACKET_FIELD_PROVENANCE.json", provenance)):
        (output_dir / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    main(args.output_dir)
