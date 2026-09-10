#!/usr/bin/env python3
"""Generate the frozen, machine-readable FAST64.6 acquisition matrix."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/dtc_l1/fast64/generated/FAST64_6_SENSITIVITY_MATRIX_V1.tsv"
CONFIG_ROOT = ROOT / "configs/dtc_l1/fast64/sensitivity_frozen_v2"
PAYLOAD = ROOT / "docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
WORKLOADS = ("BICG", "GESUMMV", "Btree")
CLASS = "PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payloads() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in PAYLOAD.read_text(encoding="utf-8").splitlines()[1:]:
        fields = line.split("\t")
        if len(fields) >= 3:
            result[fields[0].casefold()] = fields[2]
    return result


def config(family: str, point: str, mode: str) -> Path:
    if family == "logical":
        label = f"FAST64_SENS_LOGICAL_{point}KB_{mode}.config"
    elif family == "physical":
        label = f"FAST64_SENS_PHYSICAL_{'16p5' if point == '16.5' else point}KB_{mode}.config"
    else:
        label = f"FAST64_SENS_PIB_{point}ENTRIES_{mode}.config"
    return CONFIG_ROOT / f"{family}_{point}" / label


def main() -> None:
    values = payloads()
    lines = [
        "schema\tFAST64_6_SENSITIVITY_MATRIX_V1",
        "status\tFROZEN_PRE_DISPATCH",
        "scientific_framework_sha\t037f008b330eb230353b60edf126d6be9f45afdc",
        "config_materialization_sha\t180e81c68816012165c26dab577e693b3b798292",
        "formal_core_sha\t95ccdb7a056f2d53f740d90869785cac6d4ee0f5",
        "formal_runtime_sha256\t462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9",
        "observer_sha256\t2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e",
        "workload\tpayload_sha256\tdimension\tpoint\tmodeled_value\tmode\tconfig_path\tconfig_sha256\treference_point\treference_mode\tmode_policy\treuse_candidate\tclassification",
    ]
    families = (
        ("logical", (("16", "16384"), ("32", "32768"), ("64", "65536")), ("IO", "OO"), "logical_16_same_mode", "FORMAL_IO_OO;BASE_SUPPLEMENTAL_ONLY"),
        ("physical", (("16.5", "132_lines_16896B"), ("24", "192_lines_24576B"), ("32", "256_lines_32768B"), ("40", "320_lines_40960B"), ("48", "384_lines_49152B")), ("IO", "OO"), "physical_32_IO", "FORMAL_IO_OO"),
        ("pib", (("32", "32_entries"), ("64", "64_entries"), ("128", "128_entries"), ("192", "192_entries"), ("256", "256_entries")), ("IO", "OO"), "pib_128_IO", "FORMAL_IO_OO;256_DIAGNOSTIC_SATURATION_POINT"),
    )
    for workload in WORKLOADS:
        payload = values[workload.casefold()]
        for family, points, modes, reference, policy in families:
            for point, modeled in points:
                for mode in modes:
                    path = config(family, point, mode)
                    if not path.is_file():
                        raise SystemExit(f"missing frozen config: {path}")
                    lines.append("\t".join((workload, payload, family, point, modeled, mode, str(path.relative_to(ROOT)), sha(path), reference, "IO" if reference.endswith("_IO") else mode, policy, "PENDING_EXACT_REPAIRED_CORE_TERMINAL_MATCH", CLASS)))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"FAST64_6_SENSITIVITY_MATRIX_V1_WRITTEN\trows={len(lines) - 8}\t{OUT}")


if __name__ == "__main__":
    main()
