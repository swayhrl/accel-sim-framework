#!/usr/bin/env python3
"""Build a future-only FAST64.4 registry from explicit final Stage3 inputs.

V2 deliberately never defaults to the obsolete Core-41 registry.  It reuses
the V1 schema validator only after pinning the V1 source bytes, and requires
callers to name every input and output path explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "util/dtc_l1/prepare_fast64_4_primary_registry_v1.py"
FROZEN_SHA256 = "219d1830f9dd0e05470d59e76cb996f4a04f8358a9332f075e25739d19e9daf3"


def load_frozen() -> object:
    if hashlib.sha256(FROZEN.read_bytes()).hexdigest() != FROZEN_SHA256:
        raise RuntimeError("FROZEN_V1_PREPARER_SHA_MISMATCH")
    spec = importlib.util.spec_from_file_location("fast64_4_registry_v1_frozen", FROZEN)
    if spec is None or spec.loader is None:
        raise RuntimeError("FROZEN_V1_PREPARER_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--base-registry", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    frozen = load_frozen()
    base = frozen.validate_base(
        frozen.read_tsv(args.base_registry, frozen.BASE_HEADINGS, "BASE_REGISTRY"),
        args.generated_root,
    )
    coverage = frozen.validate_coverage(
        frozen.read_tsv(args.coverage, frozen.COVERAGE_HEADINGS, "IO_OO_COVERAGE"),
        args.generated_root,
    )
    rows = frozen.rows_for_collector(base, coverage)
    if args.dry_run:
        print("FAST64_4_PRIMARY_REGISTRY_V2_DRY_RUN_PASS rows=" + str(len(rows)))
    else:
        frozen.write_once(args.output, rows)
        print("FAST64_4_PRIMARY_REGISTRY_V2_PREPARED output=" + str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
