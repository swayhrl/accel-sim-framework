#!/usr/bin/env python3
"""Static validator for the B9 E01--E10 future-execution package.

It opens only text manifests/configs and hashes named immutable inputs.  It
never starts a simulator, miner, worker, build, or trace decoder.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


EXPECTED = {
    "E01-pwc32": {"-gpgpu_vm_mode": "2", "-gpgpu_vm_pwc_mode": "1", "-gpgpu_vm_pwc_entries": "32", "-gpgpu_vm_page_size": "65536"},
    "E02-pwc512": {"-gpgpu_vm_mode": "2", "-gpgpu_vm_pwc_mode": "1", "-gpgpu_vm_pwc_entries": "512", "-gpgpu_vm_page_size": "65536"},
    "E03-pwcideal": {"-gpgpu_vm_mode": "2", "-gpgpu_vm_pwc_mode": "2", "-gpgpu_vm_page_size": "65536"},
    "E04-page2mb": {"-gpgpu_vm_mode": "2", "-gpgpu_vm_page_size": "2097152", "-gpgpu_vm_pwc_mode": "1", "-gpgpu_vm_pwc_entries": "128"},
    "E05-disabled": {"-gpgpu_vm_mode": "0"},
    "E06-ideal": {"-gpgpu_vm_mode": "1"},
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def digest_stack(paths: list[Path]) -> str:
    hasher = hashlib.sha256()
    for path in paths:
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def parse_effective(paths: list[Path]) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in paths:
        for raw in path.read_text().splitlines():
            text = raw.strip()
            if not text or text.startswith("#") or not text.startswith("-"):
                continue
            fields = text.split()
            if len(fields) >= 2:
                values[fields[0]] = " ".join(fields[1:])
    return values


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--whitelist", type=Path, required=True)
    parser.add_argument("--selector", type=Path, required=True)
    args = parser.parse_args()
    manifest = rows(args.manifest)
    whitelist = rows(args.whitelist)
    selector_text = args.selector.read_text()
    required = {"experiment_id", "arm_id", "arm_kind", "profile", "base_config", "trace_config", "profile_config", "extra_config", "trace_list", "object_map", "expected_binary_sha256", "expected_config_sha256"}
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit("FAIL malformed B9 manifest")
    if {row["arm_id"] for row in manifest if row["arm_kind"] == "SIM_SMOKE"} != {"E01-generic", "E01-pwc32", "E02-generic", "E02-pwc512", "E03-generic", "E03-pwcideal", "E04-generic64k", "E04-page2mb", "E05-generic", "E05-disabled", "E06-generic", "E06-ideal"}:
        raise SystemExit("FAIL incomplete exact simulator arm set")
    if selector_text.count("| prefill |") != 16 or selector_text.count("| decode1 |") != 16:
        raise SystemExit("FAIL selector is not matched 16+16")
    if len(whitelist) != 24 or any(row.get("evidence_label") != "SPECULATIVE_DIAGNOSTIC" for row in whitelist):
        raise SystemExit("FAIL whitelist cardinality/label")
    for row in manifest:
        if row["evidence_label"] != "SPECULATIVE_DIAGNOSTIC":
            raise SystemExit(f"FAIL label: {row['arm_id']}")
        required_paths = ("base_config", "trace_config", "profile_config", "trace_list") if row["arm_kind"] == "SIM_SMOKE" else ("trace_list",)
        for key in required_paths:
            path = Path(row[key])
            if not path.is_file():
                raise SystemExit(f"FAIL missing {key}: {path}")
        extra = row["extra_config"]
        if extra != "NONE" and not Path(extra).is_file():
            raise SystemExit(f"FAIL missing extra config: {extra}")
        obj = row["object_map"]
        if obj != "NONE" and not Path(obj).is_file():
            raise SystemExit(f"FAIL missing object map: {obj}")
        if row["arm_kind"] == "SIM_SMOKE":
            sources = [Path(row["base_config"]), Path(row["trace_config"]), Path(row["profile_config"])]
            if extra != "NONE":
                sources.append(Path(extra))
            effective = parse_effective(sources)
            expected = EXPECTED.get(row["arm_id"])
            if expected:
                for option, value in expected.items():
                    if effective.get(option) != value:
                        raise SystemExit(f"FAIL {row['arm_id']} realization {option}={effective.get(option)!r}, expected {value!r}")
            if row["profile"] == "generic" and row["extra_config"] == "NONE" and row["arm_id"].endswith("generic"):
                if effective.get("-gpgpu_vm_mode") != "2":
                    raise SystemExit(f"FAIL generic control realization: {row['arm_id']}")
            if digest_stack(sources) != row["expected_config_sha256"]:
                raise SystemExit(f"FAIL config stack SHA-256 mismatch: {row['arm_id']}")
        if row["expected_config_sha256"] != "NOT_APPLICABLE" and len(row["expected_config_sha256"]) != 64:
            raise SystemExit(f"FAIL malformed expected config hash: {row['arm_id']}")
    print(f"PASS B9 static_config_manifest arms={len(manifest)} whitelist_rows={len(whitelist)} selector_rows=32")


if __name__ == "__main__":
    main()
