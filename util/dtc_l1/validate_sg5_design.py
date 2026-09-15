#!/usr/bin/env python3
"""Fail closed if the SG5 design loses a required source-qualified boundary."""
from __future__ import annotations
import argparse
import subprocess
from pathlib import Path

CORE = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
REQUIRED = {
    "src/gpgpu-sim/gpu-cache.cc": ["mf->set_data_size(m_config.get_atom_sz())", "m_miss_queue.push_back(mf)"],
    "src/gpgpu-sim/gpu-cache.h": ["m_atom_sz = (m_cache_type == SECTOR) ? SECTOR_SIZE : m_line_sz"],
    "src/gpgpu-sim/dtc-l1-common.h": ["kLogicalLineBytes = 128", "++m_pending_hits", "++m_duplicate_after_eviction"],
    "src/gpgpu-sim/shader.cc": ["m_dtc_l1_io_lower_created", "m_dtc_l1_oo_lower_created", "record.response_sector_mask == 0xFU"],
}

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--core-repo", type=Path, required=True)
    args = p.parse_args()
    for source, tokens in REQUIRED.items():
        text = subprocess.check_output(["git", "-C", str(args.core_repo), "show", f"{CORE}:{source}"], text=True)
        absent = [token for token in tokens if token not in text]
        if absent:
            raise AssertionError(f"{source}: absent {absent}")
    print("PASS SG5 observer design source anchors")

if __name__ == "__main__":
    main()
