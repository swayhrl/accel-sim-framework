#!/usr/bin/env python3
"""Fail closed on the default-off SG5 observer's source placement.

This is intentionally a source-only check: it neither builds nor launches a
simulator.  Runtime fixtures remain a separate host-gated acceptance stage.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def require_order(text: str, source: str, *tokens: str) -> None:
    offsets = [text.find(token) for token in tokens]
    if any(offset < 0 for offset in offsets):
        absent = [token for token, offset in zip(tokens, offsets) if offset < 0]
        raise AssertionError(f"{source}: absent {absent}")
    if offsets != sorted(offsets):
        raise AssertionError(f"{source}: required observer ordering lost: {tokens}")


def read(root: Path, source: str) -> str:
    path = root / source
    if not path.is_file():
        raise AssertionError(f"missing {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observer-core", type=Path, required=True)
    args = parser.parse_args()
    root = args.observer_core

    shader_h = read(root, "src/gpgpu-sim/shader.h")
    gpu_sim_cc = read(root, "src/gpgpu-sim/gpu-sim.cc")
    gpu_sim_h = read(root, "src/gpgpu-sim/gpu-sim.h")
    gpu_cache_cc = read(root, "src/gpgpu-sim/gpu-cache.cc")
    shader_cc = read(root, "src/gpgpu-sim/shader.cc")

    for token in (
        "unsigned gpgpu_l1_lower_traffic_observer;",
        "-gpgpu_l1_lower_traffic_observer",
        '"Default-off observer-only comparable L1 lower-read traffic", "0"',
        "void observe_l1_lower_read(",
        "if (!m_shader_config->gpgpu_l1_lower_traffic_observer) return;",
        "SG5_l1_lower_traffic_observer = 1",
        "SG5_conventional_lower_read_transactions",
        "SG5_dtc_io_lower_transactions",
        "SG5_dtc_oo_lower_transactions",
        "SG5_dtc_sector_lower_transactions",
    ):
        if not any(token in text for text in
                   (shader_h, gpu_sim_cc, gpu_sim_h, gpu_cache_cc, shader_cc)):
            raise AssertionError(f"observer implementation missing {token!r}")

    require_order(gpu_cache_cc, "gpu-cache.cc",
                  "mf->set_data_size(m_config.get_atom_sz())",
                  "l1_lower_traffic_observer_path::CONVENTIONAL",
                  "m_miss_queue.push_back(mf)")
    require_order(shader_cc, "shader.cc IO",
                  "++m_dtc_l1_io_lower_created;",
                  "l1_lower_traffic_observer_path::DTC_IO")
    require_order(shader_cc, "shader.cc OO",
                  "++m_dtc_l1_oo_lower_created;",
                  "l1_lower_traffic_observer_path::DTC_OO")
    if "dtc_l1_sector_oo_active()\n            ? l1_lower_traffic_observer_path::DTC_SECTOR" not in shader_cc:
        raise AssertionError("shader.cc: sector traffic is not isolated from PAPER_OO")
    print("PASS SG5 observer implementation source placement")


if __name__ == "__main__":
    main()
