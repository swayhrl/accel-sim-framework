#!/usr/bin/env python3
"""Analyze OFF neutrality and bounded C16 strong-baseline canaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def scalar(text: str, key: str) -> int:
    values = re.findall(rf"^{re.escape(key)}\s*=\s*(\d+)\s*$", text,
                        re.MULTILINE)
    need(bool(values), f"missing scalar {key}")
    return int(values[-1])


def metrics(text: str) -> dict:
    result = {key: scalar(text, key) for key in (
        "gpu_sim_cycle", "gpu_sim_insn", "gpu_tot_sim_cycle",
        "gpu_tot_sim_insn", "gpu_tot_issued_cta")}
    kernel = re.findall(r"Processing kernel (.+)$", text, re.MULTILINE)
    need(bool(kernel), "kernel identity absent")
    result["kernel_artifact"] = Path(kernel[-1]).name
    result["simulation_thread_exiting"] = (
        "GPGPU-Sim: *** simulation thread exiting ***" in text)
    result["max_cycle_termination"] = (
        "break due to reaching the maximum cycles" in text)
    return result


def canonical_behavior(text: str) -> list[str]:
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines)
                  if line.startswith("gpu_sim_cycle =")), None)
    need(start is not None, "statistics boundary absent")
    result = []
    for raw in lines[start:]:
        line = raw.rstrip()
        if line.startswith(("gpgpu_simulation_rate", "gpgpu_simulation_time",
                            "gpgpu_silicon_slowdown", "gpu_total_sim_rate")):
            continue
        result.append(line)
    return result


def parse_tab_fields(line: str) -> tuple[dict[str, int], dict[str, str]]:
    numbers, strings = {}, {}
    for field in line.split("\t")[1:]:
        if "=" not in field:
            continue
        key, value = field.split("=", 1)
        try:
            numbers[key] = int(value)
        except ValueError:
            strings[key] = value
    return numbers, strings


def policy_snapshot(path: Path, expected_policy: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line for line in text.splitlines()
             if line.startswith("c16_strong_baseline_l2\t")]
    need(len(lines) == 16, f"{expected_policy}: expected 16 L2 rows")
    summed = {}
    psel = []
    policies = set()
    instances = set()
    for line in lines:
        numbers, strings = parse_tab_fields(line)
        policies.add(strings["policy"])
        instances.add(numbers.pop("instance"))
        psel.append(numbers.pop("drrip_psel"))
        for key, value in numbers.items():
            summed[key] = summed.get(key, 0) + value
    need(policies == {expected_policy}, "policy dump drift")
    need(instances == set(range(16)), "subpartition closure failed")
    need("c16_strong_baseline_config" in text and
         f"policy={expected_policy}" in text, "human-readable config absent")
    run_metrics = metrics(text)
    need(run_metrics["simulation_thread_exiting"] and
         run_metrics["max_cycle_termination"], "bounded termination drift")
    result = {"policy": expected_policy, "status": "PASS",
              "metrics": run_metrics, "summed_counters": summed,
              "per_subpartition_psel": psel,
              "stdout_sha256": sha256(path)}
    if expected_policy == "PRIORITY_ALL":
        need(summed["priority_target_accesses"] ==
             summed["priority_selected_accesses"],
             "PRIORITY_ALL did not prioritize every target")
        need(summed["priority_allocations"] > 0, "PRIORITY_ALL inactive")
    elif expected_policy == "PRIORITY_STABLE":
        need(0 < summed["priority_selected_accesses"] <
             summed["priority_target_accesses"],
             "PRIORITY_STABLE selected/unselected separation absent")
        need(summed["priority_allocations"] > 0, "PRIORITY_STABLE inactive")
    elif expected_policy == "DRRIP":
        need(summed["accepted_new_line_allocations"] > 0,
             "DRRIP insertion path inactive")
        need(summed["drrip_srrip_insertions"] > 0 and
             summed["drrip_brrip_long_insertions"] > 0 and
             summed["drrip_brrip_short_insertions"] > 0,
             "DRRIP insertion modes not all observed")
        need(summed["true_hit_promotions"] > 0,
             "DRRIP true-sector hit promotion absent")
        need(summed["sector_miss_no_promotion"] > 0 and
             summed["mshr_merge_no_promotion"] > 0,
             "DRRIP sector/merge exclusions not observed")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output directory must be fresh")

    reference_path = args.runs / "REFERENCE_OFF" / "stdout.log"
    candidate_path = args.runs / "CANDIDATE_OFF" / "stdout.log"
    reference = reference_path.read_text(encoding="utf-8", errors="replace")
    candidate = candidate_path.read_text(encoding="utf-8", errors="replace")
    reference_metrics, candidate_metrics = metrics(reference), metrics(candidate)
    need(reference_metrics == candidate_metrics, "OFF scalar neutrality drift")
    reference_behavior = canonical_behavior(reference)
    candidate_behavior = canonical_behavior(candidate)
    need(reference_behavior == candidate_behavior,
         "OFF architectural/cache/DRAM signature drift")
    need("c16_strong_baseline_l2" not in reference and
         "c16_strong_baseline_l2" not in candidate,
         "OFF emitted baseline policy counters")
    need("oracle_elastic_l2\t" not in reference and
         "oracle_elastic_l2\t" not in candidate,
         "OFF unexpectedly enabled oracle/M1")
    neutrality = {
        "schema": "C16_E1_STRONG_BASELINES_OFF_NEUTRALITY_V1",
        "status": "PASS", "reference_core":
            "0271de82432db004beed43280ed01057246a0f2c",
        "candidate_baseline_enable": False,
        "metrics": reference_metrics,
        "canonical_behavior_sha256": hashlib.sha256(
            "\n".join(reference_behavior).encode()).hexdigest(),
        "exact_fields": [
            "kernel identity", "instructions", "CTA", "cycles",
            "L2 access/hit/miss", "DRAM requests", "replacement counters",
            "oracle/M1 counter absence", "baseline-policy counter absence"],
        "reference_stdout_sha256": sha256(reference_path),
        "candidate_stdout_sha256": sha256(candidate_path),
    }

    canaries = [
        policy_snapshot(args.runs / "PRIORITY_ALL" / "stdout.log",
                        "PRIORITY_ALL"),
        policy_snapshot(args.runs / "PRIORITY_STABLE" / "stdout.log",
                        "PRIORITY_STABLE"),
        policy_snapshot(args.runs / "DRRIP" / "stdout.log", "DRRIP"),
    ]
    ship_stderr = (args.runs / "SHIP_SW_REJECT" / "stderr.log")
    ship_text = ship_stderr.read_text(encoding="utf-8", errors="replace")
    need("SHIP_SW_IMPLEMENTATION_CONTRACT_INCOMPLETE" in ship_text,
         "SHIP_SW fail-closed marker absent")
    fail_closed = []
    for name, marker in (
            ("REJECT_DISABLED_NONNONE",
             "C16 strong baseline fail-closed enable/policy mismatch"),
            ("REJECT_ENABLED_NONE",
             "C16 strong baseline fail-closed enable/policy mismatch"),
            ("REJECT_ORACLE_MUTUAL",
             "C16 strong baseline and oracle elastic functional enables are mutually exclusive")):
        path = args.runs / name / "stderr.log"
        text = path.read_text(encoding="utf-8", errors="replace")
        need(marker in text, f"{name}: fail-closed marker absent")
        fail_closed.append({"case": name, "status": "PASS",
                            "expected_rejection": marker,
                            "stderr_sha256": sha256(path)})

    args.output_dir.mkdir(parents=True)
    dump(args.output_dir / "OFF_NEUTRALITY.json", neutrality)
    dump(args.output_dir / "BOUNDED_CANARY_RESULTS.json", {
        "schema": "C16_E1_STRONG_BASELINES_BOUNDED_CANARIES_V1",
        "status": "PASS", "run_scope": "KERNEL_4490_MAX_50000_CYCLES",
        "performance_comparison": False, "policies": canaries,
        "ship_sw": {"status": "SHIP_SW_IMPLEMENTATION_CONTRACT_INCOMPLETE",
                     "functional_enable_rejected": True,
                     "stderr_sha256": sha256(ship_stderr)},
        "fail_closed_configuration_checks": fail_closed,
    })
    checksums = []
    for path in sorted(args.output_dir.iterdir()):
        checksums.append(f"{sha256(path)}  {path.name}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
