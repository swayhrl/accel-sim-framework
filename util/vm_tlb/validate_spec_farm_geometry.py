#!/usr/bin/env python3
"""Validate planned or realized B3/B5 cache geometry without conflating them."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


GEOMETRY = re.compile(r"S:(\d+):(\d+):(\d+),")


def final_options(configs: list[Path]) -> dict[str, str]:
    options: dict[str, str] = {}
    for config in configs:
        for raw in config.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, *rest = line.split(maxsplit=1)
            if key.startswith("-"):
                options[key] = rest[0] if rest else ""
    return options


def geometry(value: str) -> tuple[int, int, int]:
    match = GEOMETRY.search(value)
    if not match:
        raise ValueError(f"unparseable cache geometry: {value}")
    return tuple(int(part) for part in match.groups())


def expected(config_id: str) -> tuple[int, int, int]:
    l1 = 128 * 1024
    l2 = 3 * 1024 * 1024
    assoc = 16
    for label, size in (("32kb", 32), ("64kb", 64), ("256kb", 256)):
        if f"l1d-{label}" in config_id:
            l1 = size * 1024
    for label, size in (("1p5mb", 1536), ("3mb", 3072), ("6mb", 6144), ("12mb", 12288)):
        if f"l2-{label}" in config_id:
            l2 = size * 1024
    if "assoc-8" in config_id:
        assoc = 8
    if "assoc-32" in config_id:
        assoc = 32
    return l1, l2, assoc


def config_paths(job: dict[str, str], args: argparse.Namespace) -> tuple[list[Path], str]:
    if args.mode == "realized":
        path = Path(job["run_dir"]) / "gpgpusim.config"
        if not path.is_file():
            raise FileNotFoundError(path)
        return [path], str(path)
    if args.framework_root is None or args.core_root is None:
        raise ValueError("planned mode requires --framework-root and --core-root")
    profiles = {
        "disabled": "M4C_CONTROL_VM_DISABLED.config",
        "ideal": "M4C_CONTROL_VM_IDEAL_IDENTITY.config",
        "generic": "M4C_GENERIC_M3_LLM_BASELINE.config",
        "paper": "M4C_PAPER_PLATFORM_SHELL_NO_SUBENTRY.config",
    }
    profile = profiles.get(job["profile"])
    if profile is None:
        raise ValueError(f"unknown profile: {job['profile']}")
    paths = [
        args.core_root / "configs/tested-cfgs/SM86_RTX3070/gpgpusim.config",
        args.framework_root / "gpu-simulator/configs/tested-cfgs/SM86_RTX3070/trace.config",
        args.framework_root / "configs/vm_tlb" / profile,
    ]
    overlay = job.get("extra_config", "NONE")
    if overlay and overlay != "NONE":
        paths.append(Path(overlay))
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    return paths, ";".join(str(path) for path in paths)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("planned", "realized"), default="realized")
    parser.add_argument("--framework-root", type=Path)
    parser.add_argument("--core-root", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"FAIL refusing to overwrite {args.output}")
    with args.jobs.open(newline="") as stream:
        jobs = list(csv.DictReader(stream, delimiter="\t"))
    rows: list[dict[str, object]] = []
    failed = 0
    for job in jobs:
        source = "MISSING"
        try:
            paths, source = config_paths(job, args)
            options = final_options(paths)
            l1_sets, l1_line, l1_ways = geometry(options["-gpgpu_cache:dl1"])
            l2_sets, l2_line, l2_ways = geometry(options["-gpgpu_cache:dl2"])
            nmem = int(options["-gpgpu_n_mem"])
            subparts = int(options["-gpgpu_n_sub_partition_per_mchannel"])
            l1_bytes = l1_sets * l1_line * l1_ways
            l2_per_subpartition = l2_sets * l2_line * l2_ways
            l2_bytes = l2_per_subpartition * nmem * subparts
            want_l1, want_l2, want_assoc = expected(job["config_id"])
            result = "PASS" if (l1_bytes, l2_bytes, l2_ways) == (want_l1, want_l2, want_assoc) else "FAIL"
            if "global-l1d-bypass" in job["config_id"] and options.get("-gpgpu_gmem_skip_L1D") != "1":
                result = "FAIL:global_l1d_bypass_not_1"
        except (FileNotFoundError, KeyError, ValueError) as error:
            l1_sets = l1_line = l1_ways = l2_sets = l2_line = l2_ways = nmem = subparts = "MISSING"
            l1_bytes = l2_per_subpartition = l2_bytes = "MISSING"
            want_l1, want_l2, want_assoc = expected(job["config_id"])
            result = "FAIL:" + str(error)
        failed += not result.startswith("PASS")
        rows.append({
            "run_id": job["run_id"], "config_id": job["config_id"], "roi": job["roi"],
            "validation_mode": args.mode, "config_source": source,
            "l1_sets": l1_sets, "l1_line_bytes": l1_line, "l1_ways": l1_ways,
            "effective_l1_bytes_per_sm": l1_bytes, "l2_sets": l2_sets, "l2_line_bytes": l2_line,
            "effective_l2_assoc": l2_ways, "n_mem": nmem, "subpartitions_per_channel": subparts,
            "effective_l2_bytes_per_subpartition": l2_per_subpartition,
            "effective_l2_total_bytes": l2_bytes, "expected_l1_bytes_per_sm": want_l1,
            "expected_l2_total_bytes": want_l2, "expected_l2_assoc": want_assoc,
            "global_l1d_bypass": options.get("-gpgpu_gmem_skip_L1D", "MISSING"), "result": result,
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS rows={len(rows)} failed={failed} output={args.output}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
