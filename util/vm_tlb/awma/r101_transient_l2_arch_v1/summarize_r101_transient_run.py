#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
MODES = {"B0": "none", "O1": "oracle_dead_drop",
         "M1": "bounded_live_retention"}
EXPECTED = {
    "binary": "32b38a66ba6b9eee5a9047873992fec42fcc4dbbff6adf247d425aec2b650c5d",
    "core_library": "f18cd8d4c2dd8927d6ad454295e434b902032042e83bbab03afcbd02b23921bf",
    "core_patch": "aa2637f3379f1c0b6184db98a41f276dcdd6bcef86cb72331b18c52cf6232676",
    "trace_config": "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b",
    "config": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "sidecar": "740820a195ae2bb9966a91b1e6d3423f4ded520bd91d1819aac8e78ce104b77d",
    "kernelslist": "9fce012939496008814786a0c12d32c1f97a10c07c62cdd08f1fddcee5d86588",
    "framework": "c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323",
}
EXPECTED_ARGV_SHA256 = "c42a372308798498f12402918eab1424957af811b86534c26fa33d98d1dc034d"

EXPECTED_ADMISSION_RECEIPT_SHA256 = "a6c66cb41c1ffb77f6af805534d47ccb8a8641dbe4aa3b206850be8e478f1e7a"


def last_int(text: str, key: str) -> int | None:
    values = re.findall(rf"^{re.escape(key)} = (\d+)\s*$", text, re.MULTILINE)
    return int(values[-1]) if values else None


def last_float(text: str, key: str) -> float | None:
    values = re.findall(rf"^{re.escape(key)} = ([0-9.eE+-]+)\s*$", text, re.MULTILINE)
    return float(values[-1]) if values else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    log_path = run_dir / "run.log"
    stderr_path = run_dir / "run.stderr"
    rc_path = run_dir / "rc.txt"
    text = log_path.read_text(errors="strict")
    command = json.loads((run_dir / "command.json").read_text())
    arm = run_dir.name
    argv_sha256 = hashlib.sha256(json.dumps(
        command.get("argv"), separators=(",", ":")).encode()).hexdigest()
    expected_mode = MODES.get(arm)
    mode_values = re.findall(r"^awma_transient_l2_mode = (\S+)\s*$",
                             text, re.MULTILINE)
    log_mode = mode_values[-1] if mode_values else None
    command_admission = command.get("admission", {})
    artifact_receipt = {
        "binary": command.get("binary_sha256"),
        "core_library": command.get("core_library_sha256"),
        "core_patch": command.get("source_authority", {}).get("core_patch_sha256"),
        "config": command.get("config_sha256"),
        "sidecar": command_admission.get("runtime_sidecar_sha256"),
        "trace_config": command.get("trace_config_sha256"),
        "kernelslist": command_admission.get("kernelslist_sha256"),
        "framework": command.get("framework_source_sha256"),
    }
    command_members = command_admission.get("trace_members", [])
    command_trace_binding = "".join(
        f"{Path(member['path']).name}\t{member['sha256']}\n"
        for member in command_members
    ).encode()
    command_trace_aggregate = hashlib.sha256(command_trace_binding).hexdigest()
    expected_environment = {
        "AWMA_TRANSIENT_L2_DIAGNOSTICS": "1",
        "AWMA_TRANSIENT_L2_DRAIN": "1",
        "AWMA_TRANSIENT_L2_MODE": expected_mode,
        "AWMA_TRANSIENT_L2_SIDECAR": (
            "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/"
            "input/transient_l2_runtime.tsv"
        ),
        "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH": "1",
        "GPGPUSIM_READY_APPLICATION_DIAGNOSTICS": "1",
        "GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS": "1",
        "GPGPUSIM_READY_APPLICATION_V2": "0",
        "GPGPUSIM_VM_COVERAGE_KERNEL_UID": "all",
    }
    rc = int(rc_path.read_text().strip()) if rc_path.is_file() else None
    stderr_bytes = stderr_path.stat().st_size if stderr_path.is_file() else None
    marker = text.rfind("gpu_sim_cycle =")
    final = text[marker:] if marker >= 0 else ""
    drain_matches = re.findall(
        r"AWMA_TRANSIENT_L2_DRAIN enabled=1 cycles=(\d+) gpu_active=(\d+) "
        r"l2_writeback_active=(\d+) max_limit_hit=(\d+) gpu_deadlock=(\d+)",
        text)
    drain_cycles = int(drain_matches[-1][0]) if drain_matches else None
    drain_gpu_active = int(drain_matches[-1][1]) if drain_matches else None
    drain_l2_writeback_active = (
        int(drain_matches[-1][2]) if drain_matches else None
    )
    drain_max_limit_hit = int(drain_matches[-1][3]) if drain_matches else None
    drain_gpu_deadlock = int(drain_matches[-1][4]) if drain_matches else None
    dram_latency_queues = [
        int(value) for value in re.findall(
            r"In Dram Latency Queue \(total = (\d+)\):", final)
    ]
    dram_rows = [
        tuple(map(int, match))
        for match in re.findall(
            r"n_rd=(\d+) n_rd_L2_A=(\d+) n_write=(\d+) n_wr_bk=(\d+)", final)
    ]
    coverage_lines = [
        line for line in text.splitlines() if line.startswith("AWMA_VM_COVERAGE ")
    ]
    coverage_records = [
        {key: int(value) for key, value in re.findall(r"(\w+)=(\d+)", line)}
        for line in coverage_lines
    ]
    coverage_sum_keys = (
        "admissions", "translated", "untranslated", "unobserved",
        "unique", "translated_unique", "untranslated_unique",
    )
    coverage_fields = {
        key: sum(record.get(key, 0) for record in coverage_records)
        for key in coverage_sum_keys
    }
    coverage_fields["kernels"] = len(coverage_records)
    coverage = coverage_lines[-1] if coverage_lines else ""
    coverage_records_exact = (
        len(coverage_records) == 18
        and [record.get("kernel_uid") for record in coverage_records]
        == list(range(1, 19))
        and all(
            record.get("translated") == record.get("admissions")
            and record.get("untranslated") == 0
            and record.get("unobserved") == 0
            and record.get("translated_unique") == record.get("unique")
            and record.get("untranslated_unique") == 0
            for record in coverage_records
        )
    )
    coverage_uid_identity = [
        {key: record.get(key) for key in (
            "kernel_uid", "unique", "translated_unique", "untranslated_unique"
        )}
        for record in coverage_records
    ]
    awma_keys = (
        "awma_transient_l2_expected_kernels",
        "awma_transient_l2_launched_kernels",
        "awma_transient_l2_completed_kernels",
        "awma_transient_l2_pre_transitions",
        "awma_transient_l2_post_transitions",
        "awma_transient_l2_descriptor_transitions",
        "awma_transient_l2_transient_accesses",
        "awma_transient_l2_transient_admissions",
        "awma_transient_l2_protected_victim_deflections",
        "awma_transient_l2_forced_live_evictions",
        "awma_transient_l2_completed_l2_writebacks",
        "awma_transient_l2_outstanding_l2_writebacks",
        "awma_transient_l2_dead_victim_selections",
        "awma_transient_l2_ordinary_victim_selections",
        "awma_transient_l2_fallback_count",
        "awma_transient_l2_l2_writebacks",
        "awma_transient_l2_l2_writeback_bytes",
        "awma_transient_l2_transient_writebacks",
        "awma_transient_l2_transient_writeback_bytes",
        "awma_transient_l2_dead_eviction_drops",
        "awma_transient_l2_dead_eviction_drop_bytes",
        "awma_transient_l2_oracle_drop_lines",
        "awma_transient_l2_oracle_drop_dirty_lines",
        "awma_transient_l2_oracle_drop_bytes",
        "awma_transient_l2_oracle_reserved_skips",
        "awma_transient_l2_terminal_quiescent",
    )
    awma = {key: last_int(text, key) for key in awma_keys}
    dram_n_rd = sum(row[0] for row in dram_rows)
    dram_n_rd_l2_a = sum(row[1] for row in dram_rows)
    dram_n_write = sum(row[2] for row in dram_rows)
    dram_n_wr_bk = sum(row[3] for row in dram_rows)
    dram_total_writes = dram_n_write + dram_n_wr_bk
    dram_writeback_bytes = dram_n_wr_bk * 64
    dram_regular_write_bytes = dram_n_write * 64
    dram_total_write_bytes = dram_total_writes * 64
    replacement_keys = (
        "awma_transient_l2_protected_victim_deflections",
        "awma_transient_l2_forced_live_evictions",
        "awma_transient_l2_dead_victim_selections",
        "awma_transient_l2_ordinary_victim_selections",
        "awma_transient_l2_fallback_count",
    )
    eviction_drop_keys = (
        "awma_transient_l2_dead_eviction_drops",
        "awma_transient_l2_dead_eviction_drop_bytes",
    )
    oracle_keys = (
        "awma_transient_l2_oracle_drop_lines",
        "awma_transient_l2_oracle_drop_dirty_lines",
        "awma_transient_l2_oracle_drop_bytes",
        "awma_transient_l2_oracle_reserved_skips",
    )
    if arm == "B0":
        mode_counter_separation = all(
            awma[key] == 0 for key in replacement_keys + eviction_drop_keys + oracle_keys)
    elif arm == "O1":
        mode_counter_separation = all(
            awma[key] == 0 for key in replacement_keys + eviction_drop_keys)
    else:
        mode_counter_separation = (
            all(awma[key] == 0 for key in oracle_keys)
            and awma["awma_transient_l2_fallback_count"]
            == awma["awma_transient_l2_forced_live_evictions"]
            and awma["awma_transient_l2_dead_eviction_drops"]
            <= awma["awma_transient_l2_dead_victim_selections"]
        )
    scope_activity = arm != "B0" or (
        awma["awma_transient_l2_transient_writebacks"] > 0
        and awma["awma_transient_l2_transient_writeback_bytes"] > 0
    )
    l2_writeback_bytes = awma["awma_transient_l2_l2_writeback_bytes"]
    if arm == "B0":
        cross_arm_identity = True
    else:
        b0_summary_path = Path(
            "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/"
            "raw/formal/B0/RUN_SUMMARY.json"
        )
        b0 = json.loads(b0_summary_path.read_text())
        cross_arm_identity = (
            b0.get("status") == "PASS"
            and last_int(text, "gpu_tot_sim_insn") == b0.get("instructions")
            and last_int(text, "gpu_tot_issued_cta") == b0.get("ctas")
            and coverage_uid_identity == b0.get("coverage_uid_identity")
        )
    gates = {
        "rc_zero": rc == 0,
        "stderr_empty": stderr_bytes == 0,
        "arm_known": expected_mode is not None,
        "command_arm_match": command.get("arm") == arm,
        "command_mode_match": command.get("mode") == expected_mode,
        "command_argv_exact": argv_sha256 == EXPECTED_ARGV_SHA256,
        "command_environment_exact": command.get("environment") == expected_environment,
        "log_mode_match": log_mode == expected_mode,
        "frozen_artifacts_match": artifact_receipt == EXPECTED,
        "producer_commit_match": (
            command_admission.get("producer_commit")
            == "bb902283b7ce9e1902b460383fbd3e0bedbd884d"
        ),
        "mode_counter_separation": mode_counter_separation,
        "coverage_present": bool(coverage),
        "coverage_kernel_count_exact": coverage_fields.get("kernels") == 18,
        "coverage_records_exact": coverage_records_exact,
        "scope_activity": scope_activity,
        "exit_marker_present": "GPGPU-Sim: *** exit detected ***" in text,
        "admission_receipt_match": (
            command.get("admission_receipt_sha256")
            == EXPECTED_ADMISSION_RECEIPT_SHA256
        ),
        "summarizer_receipt_match": (
            command.get("summarizer_sha256")
            == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        ),
        "cta_count_exact": last_int(text, "gpu_tot_issued_cta") == 46860,
        "cross_arm_identity": cross_arm_identity,
        "descriptor_transition_sum_exact": (
            awma["awma_transient_l2_descriptor_transitions"]
            == awma["awma_transient_l2_pre_transitions"]
            + awma["awma_transient_l2_post_transitions"]
            == 31
        ),
        "terminal_memory_drain_receipt": (
            len(drain_matches) == 1
            and drain_gpu_active == 0
            and drain_l2_writeback_active == 0
            and drain_max_limit_hit == 0
            and drain_gpu_deadlock == 0
            and drain_cycles is not None
        ),
        "dram_latency_queues_empty": (
            len(dram_latency_queues) == 8 and not any(dram_latency_queues)
        ),
        "transient_access_accounting_valid": (
            awma["awma_transient_l2_transient_accesses"]
            >= awma["awma_transient_l2_transient_admissions"] > 0
        ),
        "writeback_counter_bounds_valid": (
            awma["awma_transient_l2_transient_writebacks"]
            <= awma["awma_transient_l2_l2_writebacks"]
            and awma["awma_transient_l2_transient_writeback_bytes"]
            <= awma["awma_transient_l2_l2_writeback_bytes"]
        ),
        "writeback_completion_exact": (
            awma["awma_transient_l2_completed_l2_writebacks"]
            == awma["awma_transient_l2_l2_writebacks"]
            and awma["awma_transient_l2_outstanding_l2_writebacks"] == 0
        ),
        "translation_quiescent_invariants": (
            last_int(text, "vm_translation_quiescent_invariants_hold") == 1
        ),
        "translation_pwq_entries_empty": (
            last_int(text, "vm_translation_pwq_entries_active") == 0
        ),
        "translated_equals_admissions": (
            coverage_fields.get("translated") == coverage_fields.get("admissions")
        ),
        "translated_unique_equals_unique": (
            coverage_fields.get("translated_unique") == coverage_fields.get("unique")
        ),
        "untranslated_unique_zero": coverage_fields.get("untranslated_unique") == 0,
        "untranslated_zero": coverage_fields.get("untranslated") == 0,
        "accepted_payload_match": (
            command_admission.get("accepted_payload_sha256")
            == "1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234"
        ),
        "accepted_output_match": (
            command_admission.get("accepted_output_sha256")
            == "36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0"
        ),
        "trace_member_binding_exact": (
            len(command_members) == 18
            and command_trace_aggregate
            == "34031eebe1e25b375d9ee058328f678e4734790c40e67284bb6511130e4fec0e"
        ),
        "unobserved_zero": coverage_fields.get("unobserved") == 0,
        "unique_uid_nonzero": coverage_fields.get("unique", 0) > 0,
        "duplicate_application_zero": (
            last_int(text, "vm_ready_application_duplicate_attempts") == 0
        ),
        "translation_mshr_empty": last_int(text, "vm_translation_mshr_active") == 0,
        "translation_pwq_empty": last_int(text, "vm_translation_pwq_occupancy") == 0,
        "walkers_empty": last_int(text, "vm_translation_walkers_active") == 0,
        "kernel_count_exact": (
            awma["awma_transient_l2_expected_kernels"] == 18
            and awma["awma_transient_l2_launched_kernels"] == 18
            and awma["awma_transient_l2_completed_kernels"] == 18
        ),
        "transition_count_exact": (
            awma["awma_transient_l2_pre_transitions"] == 16
            and awma["awma_transient_l2_post_transitions"] == 15
        ),
        "terminal_quiescent": awma["awma_transient_l2_terminal_quiescent"] == 1,
        "writeback_byte_accounting_exact": (
            l2_writeback_bytes is not None
            and len(dram_rows) == 8
            and dram_writeback_bytes == l2_writeback_bytes
        ),
    }
    summary = {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "arm": arm,
        "mode": log_mode,
        "artifact_receipt": artifact_receipt,
        "expected_artifacts": EXPECTED,
        "run_dir": str(run_dir),
        "rc": rc,
        "stderr_bytes": stderr_bytes,
        "cycles": last_int(text, "gpu_tot_sim_cycle"),
        "last_kernel_cycles": last_int(text, "gpu_sim_cycle"),
        "instructions": last_int(text, "gpu_tot_sim_insn"),
        "ctas": last_int(text, "gpu_tot_issued_cta"),
        "l2_accesses": last_int(text, "L2_total_cache_accesses"),
        "l2_misses": last_int(text, "L2_total_cache_misses"),
        "l2_miss_rate": last_float(text, "L2_total_cache_miss_rate"),
        "l2_reservation_fails": last_int(text, "L2_total_cache_reservation_fails"),
        "dram_rows": len(dram_rows),
        "dram_n_rd": dram_n_rd,
        "dram_n_rd_l2_a": dram_n_rd_l2_a,
        "drain_cycles": drain_cycles,
        "drain_gpu_active": drain_gpu_active,
        "drain_l2_writeback_active": drain_l2_writeback_active,
        "drain_max_limit_hit": drain_max_limit_hit,
        "drain_gpu_deadlock": drain_gpu_deadlock,
        "dram_latency_queues": dram_latency_queues,
        "dram_n_write": dram_n_write,
        "dram_n_wr_bk": dram_n_wr_bk,
        "dram_total_writes": dram_total_writes,
        "dram_read_bytes_64B": dram_n_rd * 64,
        "dram_l2_alloc_read_bytes_64B": dram_n_rd_l2_a * 64,
        "dram_regular_write_bytes_64B": dram_regular_write_bytes,
        "dram_writeback_bytes_64B": dram_writeback_bytes,
        "coverage": coverage_fields,
        "coverage_records": coverage_records,
        "coverage_uid_identity": coverage_uid_identity,
        "coverage_line": coverage,
        "awma": awma,
        "gates": gates,
    }
    output = run_dir / "RUN_SUMMARY.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
