#!/usr/bin/env python3
"""Fail-closed source-object and semantic-anchor check for SG0."""
from __future__ import annotations
import argparse
import subprocess
from pathlib import Path

CORE = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
OBJECTS = {
    "src/gpgpu-sim/gpu-cache.h": "f270808bb0d2cf6e0c6a77fa2f8c7185073b812c",
    "src/gpgpu-sim/gpu-cache.cc": "351b4d89f587897b4113730db7f534189b652687",
    "src/gpgpu-sim/dtc-l1-common.h": "adf8a0ecc8ea53f26bc8984bd85d53c25514f736",
    "src/gpgpu-sim/shader.cc": "efed7d77d340e14b5c57c1ff0788c8304e043bb6",
}
TOKENS = {
    "src/gpgpu-sim/gpu-cache.h": ["case 'S':", "m_cache_type = SECTOR", "m_atom_sz = (m_cache_type == SECTOR) ? SECTOR_SIZE", "mshr_addr"],
    "src/gpgpu-sim/gpu-cache.cc": ["new sector_cache_block", "mf->set_data_size(m_config.get_atom_sz())", "mf->set_addr(mshr_addr)"],
    "src/gpgpu-sim/dtc-l1-common.h": ["kLogicalLineBytes = 128", "kSectorsPerLogicalLine = 4", "m_evicted_pending_lines", "++m_duplicate_after_eviction", "line.ready = true"],
    "src/gpgpu-sim/shader.cc": ["dtc_l1::kLogicalLineBytes", "m_dtc_l1_io_lower_created", "m_dtc_l1_oo_lower_created", "record.response_sector_mask == 0xFU"],
}

def show(repo: Path, path: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{CORE}:{path}"], text=True)

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--core-repo", type=Path, required=True)
    args = p.parse_args()
    subprocess.run(["git", "-C", str(args.core_repo), "cat-file", "-e", f"{CORE}^{{commit}}"], check=True)
    for path, expected in OBJECTS.items():
        actual = subprocess.check_output(["git", "-C", str(args.core_repo), "rev-parse", f"{CORE}:{path}"], text=True).strip()
        if actual != expected:
            raise AssertionError(f"object mismatch {path}: {actual}")
        contents = show(args.core_repo, path)
        missing = [token for token in TOKENS[path] if token not in contents]
        if missing:
            raise AssertionError(f"semantic anchors absent from {path}: {missing}")
    print("PASS SG0 Core95 identity and conventional/DTC semantic anchors")

if __name__ == "__main__":
    main()
