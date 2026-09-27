#!/usr/bin/env python3
"""Create the bounded M1F real-trace activation review pack."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


GOAL = "C16_E1_M1F_REAL_TRACE_ACTIVATION_CANARY_V1"
LABEL = "M1F_REAL_TRACE_ACTIVATION_QUALIFIED_V1"


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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--config-dir", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--binary-sha-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--core-commit", required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "review pack must be fresh")

    names = (
        "REAL_TRACE_M1F_ACTIVATION_CANARIES.json",
        "M1F_REAL_TRACE_SELECTION_DISTRIBUTION.json",
        "M1F_ADMISSION_ACCOUNTING.json",
        "NON_TARGET_EXCLUSION.json",
        "DETERMINISM_CHECK.json",
        "REAL_TRACE_NEUTRALITY.json",
        "RUN_RECEIPTS.json",
        "VALIDATION_SUMMARY.json",
    )
    values = {}
    for name in names:
        path = args.analysis_dir / name
        need(path.is_file(), f"missing deliverable {name}")
        values[name] = json.loads(path.read_text(encoding="utf-8"))
        need(values[name]["status"] == "PASS", f"{name} not PASS")
    need(values["VALIDATION_SUMMARY.json"]["qualification"] == LABEL,
         "qualification label drift")

    args.output_dir.mkdir(parents=True)
    for name in names:
        shutil.copy2(args.analysis_dir / name, args.output_dir / name)
    config_output = args.output_dir / "configs"
    config_output.mkdir()
    for path in sorted(args.config_dir.glob("*.config")):
        shutil.copy2(path, config_output / path.name)
    need(len(list(config_output.glob("*.config"))) == 6,
         "exact config set drift")
    shutil.copy2(args.binary_sha_file,
                 args.output_dir / "SOURCE_BINARY_SHA256")
    for name in ("core_oracle_tests_v1.log",
                 "trace_pressure_tests.log", "real_trace_analysis_unit_tests.log",
                 "m1f_activation_probe.log"):
        source = args.logs_dir / name
        need(source.is_file(), f"missing validation log {name}")
        shutil.copy2(source, args.output_dir / name)
    build_log = args.logs_dir / "full_accelsim_build.log"
    need(build_log.is_file() and
         "M1F_REAL_TRACE_ACCELSIM_BUILD_PASS" in
         build_log.read_text(encoding="utf-8", errors="replace"),
         "full Accel-Sim build not PASS")
    dump(args.output_dir / "FULL_ACCELSIM_BUILD_RECEIPT.json", {
        "schema": "C16_E1_M1F_REAL_TRACE_BUILD_RECEIPT_V1",
        "status": "PASS",
        "durable_log_path": str(build_log),
        "durable_log_sha256": sha256(build_log),
        "isolated_core_worktree":
            "/root/workspace/gpgpu-sim-c16-e1-m1f-real-trace-activation-canary-v1",
        "isolated_framework_worktree":
            "/root/workspace/accel-sim-framework-c16-e1-m1f-real-trace-activation-canary-174new-v1",
    })

    dump(args.output_dir / "SOURCE_ANCHORS.json", {
        "schema": "C16_E1_M1F_REAL_TRACE_SOURCE_ANCHORS_V1",
        "status": "PASS", "goal": GOAL,
        "m1f_frozen_core": "0631070779329adfee858f5e350b6c74670bcd5f",
        "m1f_frozen_framework": "a72d0f50b26c558368787318860df539950418fd",
        "activation_core_commit": args.core_commit,
        "trace_producer": "df0d0484875ec62f2b2f0c4aaf03f9d904328528",
        "trace_qualification": "C16_E1_BOUNDED_DECODE_TRACE_QUALIFIED_V1",
        "trace_manifest_sha256":
            "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389",
        "namespace_framework": "2fa207fbc37a48f12641d810319b03ba1cf4e381",
        "sidecar_sha256":
            "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6",
        "selector": {"version": "C16_M1F_STABLE_ADMISSION_HASH_V1",
                     "seed": "0x6a09e667f3bcc908",
                     "threshold": "0x0484baf3b723b966",
                     "quota_bytes": 16777216, "quota_lines": 131072},
        "selector_or_quota_changed": False,
        "lane4_partial_results_used": False,
    })
    (args.output_dir / "CHANGED_FILES.txt").write_text(
        "Core:\n"
        "src/gpgpu-sim/oracle_elastic_residency.h\n"
        "src/gpgpu-sim/oracle_elastic_residency.cc\n"
        "src/gpgpu-sim/gpu-cache.h\n"
        "src/gpgpu-sim/gpu-cache.cc\n"
        "src/gpgpu-sim/gpu-sim.cc\n"
        "src/gpgpu-sim/tests/test_oracle_elastic_residency.cc\n\n"
        "Framework:\n"
        "util/vm_tlb/c16/m1f_real_trace_activation_probe.cc\n"
        "util/vm_tlb/c16/e1_m1f_real_trace_analysis.py\n"
        "util/vm_tlb/c16/test_e1_m1f_real_trace_analysis.py\n"
        "util/vm_tlb/c16/e1_m1f_real_trace_finalize.py\n"
        f"docs/vm_tlb/review_packs/{GOAL}/\n",
        encoding="utf-8")
    (args.output_dir / "COMMIT_HISTORY.txt").write_text(
        "Core frozen parent 0631070779329adfee858f5e350b6c74670bcd5f\n"
        f"Core activation commit {args.core_commit}\n"
        "Framework frozen parent a72d0f50b26c558368787318860df539950418fd\n"
        "Framework activation commit is the commit containing this review pack.\n",
        encoding="utf-8")
    dump(args.output_dir / "OPEN_ISSUES.json", {
        "schema": "C16_E1_M1F_REAL_TRACE_OPEN_ISSUES_V1",
        "status": "NO_BLOCKING_ISSUES",
        "not_answered_by_this_goal": [
            "full-window performance", "M1F versus M1 speedup",
            "cross-decode survival", "local timing improvement",
            "novelty", "hardware latency/area/power"],
    })

    raw_rows = ["artifact\tsha256\tbytes\tlocation"]
    for run in ("N2_L0_RUN1", "N2_L0_RUN2", "N2_L14", "N2_L27",
                "FROZEN_N0", "INSTRUMENTED_N0", "FROZEN_N1",
                "INSTRUMENTED_N1"):
        for name in ("stdout.log", "activation.tsv", "stderr.time.log",
                     "stderr.log"):
            path = args.runs_root / run / name
            if path.is_file():
                raw_rows.append(f"{run}/{name}\t{sha256(path)}\t"
                                f"{path.stat().st_size}\t{path}")
    (args.output_dir / "RAW_LOG_INDEX.tsv").write_text(
        "\n".join(raw_rows) + "\n", encoding="utf-8")

    selection = values["M1F_REAL_TRACE_SELECTION_DISTRIBUTION.json"]
    admission = values["M1F_ADMISSION_ACCOUNTING.json"]
    summary_rows = []
    for selected, admitted in zip(selection["kernels"], admission["kernels"]):
        totals = admitted["simulator_l2_totals"]
        summary_rows.append(
            f"| {selected['kernel_id']} | {selected['target_class']} | "
            f"{selected['selected_unique_target_lines']} / "
            f"{selected['target_unique_128b_lines']} | "
            f"{totals['selected_target_accesses']} / {totals['target_accesses']} | "
            f"{totals['protected_fills']} | "
            f"{totals['target_protection_admission_denied']} |")
    (args.output_dir / "README.md").write_text(f"""# {GOAL}

Qualification: `{LABEL}`.

This pack establishes that the three frozen real C16 kernels traverse oracle
target recognition, the frozen stable selector, and the existing M1 hard
admission path. It does not authorize a full timing run.

| kernel | class | selected / target unique lines | selected / target simulator L2 accesses | successful protected fills | hard denials |
|---:|---:|---:|---:|---:|---:|
{chr(10).join(summary_rows)}

The trace scanner counts active-lane address and 128-byte line-reference
proxies. Simulator admission counters count modeled L2 transactions. These
denominators are intentionally reported separately. Repeated accesses explain
any reference-weighted versus unique-line fraction difference.

N0 and N1 are exact frozen-versus-instrumented 50,000-cycle real-prefix
neutrality checks. N2 cycle values are activation evidence only and are not a
performance comparison. Lane 4 results were not read or used.
""", encoding="utf-8")
    (args.output_dir / "CLAIM_BOUNDARY.md").write_text("""# Claim boundary

`M1F_REAL_TRACE_ACTIVATION_QUALIFIED_V1` means only that qualified real C16
trace accesses are recognized as qweight targets, receive deterministic frozen
M1F identities, and pass correctly into the existing M1 hard-admission chain.

It does not establish speedup, whole-window behavior, cross-decode survival,
local-timing improvement, superiority to M1, or novelty. The three isolated
kernel executions are activation canaries, not the 1565-kernel reuse window or
D1-D3 timing replay. No new GPU collection, NCU, or NVBit work was performed.
""", encoding="utf-8")
    (args.output_dir / "VALIDATION_SUMMARY.md").write_text("""# Validation summary

- Full isolated Core/Accel-Sim build: PASS.
- Core policy/metadata/tag-array regression: PASS.
- Three complete real kernel canaries: PASS with natural termination.
- Frozen static selector versus each full-region trace enumeration: exact on
  unique target lines.
- Selected/filtered/admitted/denied accounting closure: PASS.
- Fixed real addresses plus selected protected-admission witnesses: PASS.
- L0 repeated-run selector determinism: PASS.
- Gate/down/qzeros/scales/ordinary reads and write/PTE/synthetic exclusions:
  PASS.
- N0 and N1 frozen-versus-instrumented real-prefix neutrality: PASS.
""", encoding="utf-8")

    checksums = []
    for path in sorted(args.output_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            checksums.append(f"{sha256(path)}  {path.relative_to(args.output_dir)}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "qualification": LABEL,
                      "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
