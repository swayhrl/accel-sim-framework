#!/usr/bin/env python3
"""Build B4 jobs from the B-owned, immutable conventional trace staging set."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


WORKLOADS = ("bfs", "hotspot", "srad")
CONFIGS = (
    ("ideal-identity", "ideal", "NONE"),
    ("l2tlb-256", "generic", "-gpgpu_vm_l2_tlb_entries 256\n"),
    ("l2tlb-768", "generic", "NONE"),
    ("l2tlb-1536", "generic", "-gpgpu_vm_l2_tlb_entries 1536\n"),
)


def smoke_list(source: Path, output: Path) -> None:
    lines: list[str] = []
    first_kernel = False
    for raw in source.read_text().splitlines():
        if raw.startswith("MemcpyHtoD,") and not first_kernel:
            lines.append(raw)
        elif raw.endswith(".traceg"):
            lines.append(raw)
            first_kernel = True
            break
    if not first_kernel:
        raise SystemExit(f"FAIL no kernel trace in {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f"FAIL refusing to overwrite {output}")
    output.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--kind", choices=("smoke", "full"), required=True)
    parser.add_argument("--jobs", type=Path, required=True)
    args = parser.parse_args()
    if args.jobs.exists():
        raise SystemExit(f"FAIL refusing to overwrite existing jobs TSV: {args.jobs}")
    rows: list[dict[str, str]] = []
    for workload in WORKLOADS:
        trace_dir = args.scratch_root / "staging" / "nonllm" / workload / "traces"
        full_list = trace_dir / "kernelslist.g"
        trace_list = full_list
        if args.kind == "smoke":
            trace_list = args.scratch_root / "inputs" / "nonllm" / "smoke" / f"{workload}.kernelslist.g"
            smoke_list(full_list, trace_list)
        for config_id, profile, contents in CONFIGS:
            extra = "NONE"
            if contents != "NONE":
                config = args.scratch_root / "configs" / "b4" / f"{config_id}.config"
                config.parent.mkdir(parents=True, exist_ok=True)
                if config.exists() and config.read_text() != "# Window-B B4 conventional-trace overlay\n" + contents:
                    raise SystemExit(f"FAIL overlay mismatch: {config}")
                if not config.exists():
                    config.write_text("# Window-B B4 conventional-trace overlay\n" + contents)
                extra = str(config)
            rows.append({
                "run_id": f"b4-{args.kind}-{workload}-{config_id}",
                "stage": f"B4_NONLLM_{args.kind.upper()}", "roi": "nonllm", "profile": profile,
                "trace_list": str(trace_list), "trace_dir": str(trace_dir),
                "run_dir": str(args.scratch_root / "runs" / f"b4-{args.kind}" / workload / config_id),
                "evidence_label": "SPECULATIVE_DIAGNOSTIC", "max_kernels": "0",
                "telemetry_level": "1" if args.kind == "smoke" else "2", "window_transactions": "1000000",
                "extra_config": extra, "object_map": "NONE", "workload": workload, "config_id": config_id,
            })
    args.jobs.parent.mkdir(parents=True, exist_ok=True)
    with args.jobs.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS kind={args.kind} jobs={len(rows)} output={args.jobs}")


if __name__ == "__main__":
    main()
