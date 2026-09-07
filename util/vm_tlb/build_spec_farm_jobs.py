#!/usr/bin/env python3
"""Materialize the committed Window-B sweep matrix in B-owned scratch.

The generated overlays are append-only configuration deltas.  Thus a row with
an overlay changes exactly the named factor from its selected committed profile;
the launcher records both the profile and the overlay hash in every run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def write_if_identical(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() != text:
        raise SystemExit(f"FAIL refusing to replace a different generated overlay: {path}")
    if not path.exists():
        path.write_text(text)


def overlay(config_id: str, lines: list[str]) -> tuple[str, str, str]:
    if not lines:
        return config_id, "NONE", ""
    return (config_id, "OVERLAY", "# Window-B generated OFAT overlay: " + config_id + "\n" +
            "\n".join(lines) + "\n")


def b2_cases() -> list[tuple[str, str, str]]:
    cases = [overlay("b2-baseline", [])]
    cases += [overlay(f"b2-l1tlb-e{value}", [
        f"-gpgpu_vm_l1_tlb_entries {value}", f"-gpgpu_vm_l1_tlb_assoc {value}"])
              for value in (16, 64, 128)]
    cases += [overlay(f"b2-l2tlb-e{value}", [f"-gpgpu_vm_l2_tlb_entries {value}"])
              for value in (128, 256, 512, 1536, 3072)]
    cases += [overlay(f"b2-mshr-{value}", [f"-gpgpu_vm_translation_mshr_entries {value}"])
              for value in (8, 16, 64, 128)]
    cases += [overlay(f"b2-pwq-{value}", [f"-gpgpu_vm_pwq_entries {value}"])
              for value in (8, 16, 64)]
    cases += [overlay(f"b2-walkers-{value}", [f"-gpgpu_vm_walkers {value}"])
              for value in (1, 4, 8, 32)]
    cases += [
        overlay("b2-pwc-off", ["-gpgpu_vm_pwc_mode 0"]),
        overlay("b2-pwc-finite32", ["-gpgpu_vm_pwc_mode 1", "-gpgpu_vm_pwc_entries 32"]),
        overlay("b2-pwc-finite512", ["-gpgpu_vm_pwc_mode 1", "-gpgpu_vm_pwc_entries 512"]),
        overlay("b2-pwc-ideal", ["-gpgpu_vm_pwc_mode 2"]),
        overlay("b2-page-2mb-diagnostic", ["-gpgpu_vm_page_size 2097152"]),
        ("b2-control-vm-disabled", "PROFILE:disabled", ""),
        ("b2-control-ideal-identity", "PROFILE:ideal", ""),
    ]
    return cases


def b3_cases() -> list[tuple[str, str, str]]:
    # dl1 byte capacity is sets * 128B line * 256 ways.  dl2 total bytes is
    # sets * 128B * ways * 12 channels * 2 subpartitions.
    cases = [overlay("b3-cache-baseline", [])]
    cases += [overlay(f"b3-l1d-{label}", [
        f"-gpgpu_unified_l1d_size {size_kb}",
        f"-gpgpu_cache:dl1 S:{sets}:128:256,L:T:m:L:L,A:384:48,16:0,32",
    ]) for label, size_kb, sets in (("32kb", 32, 1), ("64kb", 64, 2), ("256kb", 256, 8))]
    cases += [overlay(f"b3-l2-{label}", [
        f"-gpgpu_cache:dl2 S:{sets}:128:16,L:B:m:L:P,A:192:4,32:0,32",
    ]) for label, sets in (("1p5mb", 32), ("6mb", 128), ("12mb", 256))]
    cases += [
        overlay("b3-l2-assoc-8", ["-gpgpu_cache:dl2 S:128:128:8,L:B:m:L:P,A:192:4,32:0,32"]),
        overlay("b3-l2-assoc-32", ["-gpgpu_cache:dl2 S:32:128:32,L:B:m:L:P,A:192:4,32:0,32"]),
        overlay("b3-global-l1d-bypass", ["-gpgpu_gmem_skip_L1D 1"]),
    ]
    return cases


def b5_cases() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for tlb in (256, 768, 1536):
        for label, sets in (("1p5mb", 32), ("3mb", 64), ("6mb", 128)):
            rows.append(overlay(f"b5-l2tlb-{tlb}-l2-{label}", [
                f"-gpgpu_vm_l2_tlb_entries {tlb}",
                f"-gpgpu_cache:dl2 S:{sets}:128:16,L:B:m:L:P,A:192:4,32:0,32",
            ]))
    return rows


def cases_for(stage: str) -> list[tuple[str, str, str]]:
    return {"b2": b2_cases, "b3": b3_cases, "b5": b5_cases}[stage]()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--stage", choices=("b2", "b3", "b5"), required=True)
    parser.add_argument("--kind", choices=("smoke", "full"), required=True)
    parser.add_argument("--jobs", type=Path, required=True)
    parser.add_argument("--config-ids", default="", help="comma-separated retry subset")
    parser.add_argument("--rois", default="prefill,decode1", help="comma-separated ROI subset")
    parser.add_argument("--attempt", default="", help="fresh run-directory suffix, e.g. -retry1")
    args = parser.parse_args()
    if args.jobs.exists():
        raise SystemExit(f"FAIL refusing to overwrite existing jobs TSV: {args.jobs}")

    trace_root = args.scratch_root / "staging" / "llama-f96b7ea9-5bdd4b55"
    inputs_root = args.scratch_root / "inputs" / "semantic-rebuilt"
    overlays = args.scratch_root / "configs" / args.stage
    rows: list[dict[str, str]] = []
    stage_title = {"b2": "B2_VM", "b3": "B3_CACHE", "b5": "B5_TLB_L2_GRID"}[args.stage]
    requested = set(filter(None, args.config_ids.split(",")))
    rois = tuple(filter(None, args.rois.split(",")))
    if not rois or set(rois) - {"prefill", "decode1"}:
        raise SystemExit(f"FAIL invalid ROI subset: {args.rois}")
    available = {item[0] for item in cases_for(args.stage)}
    if requested - available:
        raise SystemExit(f"FAIL unknown config ids: {sorted(requested - available)}")
    selected = [item for item in cases_for(args.stage) if not requested or item[0] in requested]
    for config_id, config_value, config_text in selected:
        if config_value.startswith("PROFILE:"):
            profile, extra = config_value.split(":", 1)[1], "NONE"
        else:
            profile = "generic" if args.stage == "b2" else "paper"
            if config_value == "NONE":
                extra = "NONE"
            else:
                extra_path = overlays / f"{config_id}.config"
                write_if_identical(extra_path, config_text)
                extra = str(extra_path)
        for roi, archive_name in (("prefill", "m4a-llama-prefill-20260902T182016Z"),
                                  ("decode1", "m4a-llama-decode1-20260903T004138Z")):
            if roi not in rois:
                continue
            rows.append({
                "run_id": f"{args.stage}-{args.kind}{args.attempt}-{config_id}-{roi}",
                "stage": f"{stage_title}_{args.kind.upper()}", "roi": roi, "profile": profile,
                "trace_list": str(inputs_root / roi / "compute-only-kernelslist.g"),
                "trace_dir": str(trace_root / roi / archive_name / "traces"),
                "run_dir": str(args.scratch_root / "runs" / f"{args.stage}-{args.kind}{args.attempt}" / config_id / roi),
                "evidence_label": "SPECULATIVE_DIAGNOSTIC", "max_kernels": "1" if args.kind == "smoke" else "0",
                "telemetry_level": "1" if args.kind == "smoke" else "2",
                "window_transactions": "1000000", "extra_config": extra, "config_id": config_id,
            })
    args.jobs.parent.mkdir(parents=True, exist_ok=True)
    with args.jobs.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(args.jobs.read_bytes()).hexdigest()
    print(f"PASS stage={args.stage} kind={args.kind} configs={len(selected)} jobs={len(rows)} sha256={digest}")


if __name__ == "__main__":
    main()
