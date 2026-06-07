#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, REPO_ROOT, ensure_local_dirs, latest, rel, ts, write_csv, write_stage_report

SCAN_ROOTS = [
    REPO_ROOT / "gpu-simulator/gpgpu-sim/src",
    REPO_ROOT / "gpu-simulator/trace-driven",
]

PATTERNS = [
    ("warp_address", re.compile(r"warp_inst_t|generate_mem_accesses|memory_coalescing_arch|memreqaddr|set_addr|get_addr")),
    ("tlb", re.compile(r"\b[Tt][Ll][Bb]\b|m_num_tlb")),
    ("mshr", re.compile(r"\bMSHR\b|mshr|MSHR_RC_FAIL|intrawarp_mshr")),
    ("ptw_page_walk", re.compile(r"PTW|ptw|page_walk|page walk|pagewalker|page table walker")),
    ("pwc", re.compile(r"\bPWC\b|pwc|page walk cache")),
    ("queue", re.compile(r"queue|enqueue|dequeue|fifo_pipeline")),
    ("stats_print", re.compile(r"print_stats|gpu_print_stat|shader_core_stats::print|fprintf\\(|printf\\(")),
    ("mem_fetch", re.compile(r"mem_fetch|new_addr_type|addrdec|partition_address")),
]


def confidence(module: str, path: Path, line: str) -> str:
    text = f"{path} {line}".lower()
    if module == "warp_address" and any(s in text for s in ["generate_mem_accesses", "memreqaddr", "trace_driven"]):
        return "HIGH"
    if module == "stats_print" and any(s in text for s in ["gpu_print_stat", "shader_core_stats::print"]):
        return "HIGH"
    if module == "tlb" and "m_num_tlb" in text:
        return "MEDIUM"
    if module in {"ptw_page_walk", "pwc"}:
        return "LOW"
    if module == "mshr" and "tlb" not in text:
        return "MEDIUM"
    return "LOW"


def safe_hook(module: str, conf: str, line: str) -> str:
    if module in {"warp_address", "stats_print"} and conf == "HIGH":
        return "yes_read_only_or_print_only"
    if module == "tlb" and "m_num_tlb" in line:
        return "no_producer_not_confirmed"
    if module == "mshr":
        return "no_generic_data_cache_not_translation_specific"
    return "no"


def symbol_name(line: str) -> str:
    match = re.search(r"([A-Za-z_][A-Za-z0-9_:~<>]*)\s*\\(", line)
    if match:
        return match.group(1)
    for token in ["m_num_tlb_hits", "m_num_tlb_accesses", "gpgpu_n_intrawarp_mshr_merge", "memreqaddr", "MSHR_RC_FAIL"]:
        if token in line:
            return token
    return line.strip()[:80]


def scan() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for root in SCAN_ROOTS:
        for path in root.rglob("*"):
            if path.suffix not in {".cc", ".cpp", ".h", ".hpp", ".tup", ".xml"}:
                continue
            if any(part in {"build", ".git"} for part in path.parts):
                continue
            try:
                lines = path.read_text(errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                for module, pattern in PATTERNS:
                    if pattern.search(line):
                        conf = confidence(module, path, line)
                        rows.append(
                            {
                                "module": module,
                                "path": rel(path),
                                "line": str(line_no),
                                "symbol": symbol_name(line),
                                "evidence": line.strip()[:240],
                                "confidence": conf,
                                "preliminary_safe_hook": safe_hook(module, conf, line),
                            }
                        )
                        break
                if len(rows) >= 1800:
                    return rows
    return rows


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    csv_path = REPORT_DIR / f"A19B_latpc_vm_module_scan_{stamp}.csv"
    report = REPORT_DIR / f"A19B_latpc_vm_module_scan_{stamp}.md"
    scope = latest("A19A_latpc_vm_tlb_ptw_scope_*.csv")
    rows = scan()
    write_csv(
        csv_path,
        rows,
        ["module", "path", "line", "symbol", "evidence", "confidence", "preliminary_safe_hook"],
    )
    counts: dict[str, int] = {}
    high_counts: dict[str, int] = {}
    for row in rows:
        counts[row["module"]] = counts.get(row["module"], 0) + 1
        if row["confidence"] == "HIGH":
            high_counts[row["module"]] = high_counts.get(row["module"], 0) + 1
    missing = [m for m in ["ptw_page_walk", "pwc"] if high_counts.get(m, 0) == 0]
    status = "PASS_WITH_WARNINGS" if missing else "PASS"
    blocker = "no high-confidence PTW/PWC implementation localized" if missing else "none"
    extra = "## Scan Counts\n\n" + "\n".join(f"- {module}: {count}" for module, count in sorted(counts.items()))
    extra += "\n\n## High Confidence Counts\n\n" + "\n".join(f"- {module}: {count}" for module, count in sorted(high_counts.items()))
    write_stage_report(
        report,
        "A19B LATPC VM Module Scan",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a19b_latpc_module_scan.py"],
        [rel(scope) if scope else "", "gpu-simulator/gpgpu-sim/src", "gpu-simulator/trace-driven"],
        [rel(csv_path), rel(report)],
        blocker,
        [
            "Scan is bounded to simulator and trace-driven source roots.",
            "Confidence labels are conservative and are not mechanism implementation approval.",
        ],
        extra,
    )
    print(f"A19B status: {status}")
    print(f"A19B report: {rel(report)}")
    print(f"A19B scan CSV: {rel(csv_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
