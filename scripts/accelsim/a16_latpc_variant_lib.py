#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def latest(pattern: str) -> Path | None:
    files = sorted((REPO_ROOT / ".local_reports").glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def clean(value: object) -> str:
    return str(value or "").replace("\r", "").replace("\n", "").strip()


def abs_path(value: str) -> str:
    p = Path(clean(value))
    return str(p if p.is_absolute() else REPO_ROOT / p)


def load_latest_selected_workload() -> dict:
    path = latest("A16A_latpc_selected_workload_*.json")
    if not path:
        raise FileNotFoundError("missing A16A selected workload JSON")
    data = json.loads(path.read_text())
    data["_source_path"] = str(path)
    return data


def get_latpc_variants() -> list[dict[str, str]]:
    return [
        {
            "variant_id": "baseline",
            "variant_kind": "baseline",
            "command_role": "control",
            "behavior": "baseline",
            "config_mode": "original",
            "semantic_delta": "none",
            "expected_stats_relation_to_baseline": "identity",
        },
        {
            "variant_id": "latpc_noop",
            "variant_kind": "noop_variant_slot",
            "command_role": "variant",
            "behavior": "no-op",
            "config_mode": "same_as_baseline",
            "semantic_delta": "none",
            "expected_stats_relation_to_baseline": "identity",
            "purpose": "validate LATPC baseline-vs-variant pipeline before mechanism implementation",
        },
    ]


def simulator_binary() -> str:
    return str(REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out")


def simulator_args_signature() -> str:
    return "accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g"


def build_variant_manifest(selected: dict | None = None) -> dict:
    selected = selected or load_latest_selected_workload()
    kernels = abs_path(selected.get("kernelslist_path", ""))
    config = abs_path(selected.get("config_path", "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"))
    trace_config = abs_path("gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config")
    variants = []
    for variant in get_latpc_variants():
        row = dict(variant)
        row.update({
            "kernelslist_path": kernels,
            "config_path": config,
            "trace_config_path": trace_config,
            "simulator_binary": simulator_binary(),
            "simulator_args_signature": simulator_args_signature(),
        })
        variants.append(row)
    return {
        "paper": "LATPC",
        "round": "A16",
        "selected_workload": selected.get("selected_workload", ""),
        "paper_workload": selected.get("paper_workload", ""),
        "workload_class": selected.get("workload_class", ""),
        "variants": variants,
        "baseline": variants[0],
        "latpc_noop": variants[1],
        "kernelslist_path": kernels,
        "config_path": config,
        "trace_config_path": trace_config,
        "simulator_delta": "none",
        "noop_equivalence_expected": True,
        "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        "status": "PASS",
    }


def validate_noop_manifest(manifest: dict) -> tuple[bool, list[str]]:
    base = manifest["baseline"]
    noop = manifest["latpc_noop"]
    keys = ["kernelslist_path", "config_path", "trace_config_path", "simulator_binary", "simulator_args_signature"]
    diffs = [key for key in keys if clean(base.get(key)) != clean(noop.get(key))]
    return (not diffs, diffs)


def write_variant_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, indent=2))
