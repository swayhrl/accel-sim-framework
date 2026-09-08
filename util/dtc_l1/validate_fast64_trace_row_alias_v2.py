#!/usr/bin/env python3
"""Versioned FAST64 validator that recognizes the simulator's perf alias.

It leaves the frozen validator untouched.  The only normalization is the
documented ``perf_counter.csv.gz`` symlink alias to exactly one timestamped
``perf_counter_*.csv.gz`` stream.  Any additional stream, regular alias, or
different symlink target remains fail-closed.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent
FROZEN = ROOT / "validate_fast64_trace_row.py"
FROZEN_SHA256 = "125c32256846949f2b93e7e71687017229ba3435c0d66206ab3d28af59f7af6c"


def argument(flag: str) -> pathlib.Path:
    try:
        return pathlib.Path(sys.argv[sys.argv.index(flag) + 1])
    except (ValueError, IndexError) as error:
        raise SystemExit(f"required argument absent: {flag}") from error


def validate_alias(run_dir: pathlib.Path) -> dict[str, str]:
    paths = sorted(run_dir.glob("perf_counter*.csv.gz"))
    timestamped = [p for p in paths if p.name.startswith("perf_counter_")]
    alias = run_dir / "perf_counter.csv.gz"
    if len(timestamped) != 1 or not timestamped[0].is_file() or timestamped[0].is_symlink():
        raise SystemExit(f"alias-v2 requires exactly one regular timestamped perf stream, found {len(timestamped)}")
    canonical = timestamped[0]
    unexpected = [p for p in paths if p not in (canonical, alias)]
    if unexpected:
        raise SystemExit("alias-v2 rejects unexpected perf paths: " + ", ".join(map(str, unexpected)))
    if alias.exists() or alias.is_symlink():
        if not alias.is_symlink() or alias.resolve() != canonical.resolve():
            raise SystemExit("alias-v2 rejects noncanonical perf_counter.csv.gz alias")
    if len(paths) not in (1, 2):
        raise SystemExit(f"alias-v2 rejects perf path count {len(paths)}")
    return {"canonical_perf_stream": str(canonical), "canonical_perf_stream_sha256": frozen.sha256(canonical),
            "perf_counter_alias": str(alias) if alias.is_symlink() else "ABSENT"}


spec = importlib.util.spec_from_file_location("fast64_frozen_validator", FROZEN)
if spec is None or spec.loader is None:
    raise SystemExit("cannot load frozen FAST64 validator")
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
if frozen.sha256(FROZEN) != FROZEN_SHA256:
    raise SystemExit("frozen validator SHA mismatch")

run_dir = argument("--run-dir")
output = argument("--output")
alias_evidence = validate_alias(run_dir)
original_glob = pathlib.Path.glob


def normalized_glob(path: pathlib.Path, pattern: str):
    values = list(original_glob(path, pattern))
    if path == run_dir and pattern == "perf_counter*.csv.gz":
        return iter([p for p in values if p.name != "perf_counter.csv.gz"])
    return iter(values)


pathlib.Path.glob = normalized_glob
try:
    status = frozen.main()
finally:
    pathlib.Path.glob = original_glob
if status != 0:
    raise SystemExit(status)
result = json.loads(output.read_text(encoding="utf-8"))
result["immutable_attempt"]["perf_alias_normalization"] = alias_evidence
result["immutable_attempt"]["frozen_validator_sha256"] = FROZEN_SHA256
output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("FAST64_ALIAS_V2_ROW_PASS output=" + str(output))
