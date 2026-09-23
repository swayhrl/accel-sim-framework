#!/usr/bin/env python3
"""Independent fail-closed capacity-knee consumer.

Calculation authority is raw seven-repetition timing plus raw NCU
BASE/SESSION/PROFILE evidence.  Producer summaries are never accepted here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


MIB = 1024 * 1024
EXPECTED_REPS = 7
IMPLEMENTATION = "AWQ_FP16_INPUT"
DOMAIN = "TEXT"
M_VALUE = 1
PRESSURE_MODE = "DENSE_PREFIX_READ"
METRIC = "dram__bytes.sum"
METRIC_UNIT = "byte"
DEVICE_L2_BYTES = 67_108_864
PACKED_STATE_BYTES = {
    "q_proj": 6_680_576,
    "down_proj": 35_273_728,
    "up_proj": 35_273_728,
}
DOSE_SETS_MIB = {
    "q_proj": (0, 32, 48, 56, 60, 64, 72, 96),
    "down_proj": (0, 16, 24, 28, 32, 36, 48, 64),
    "up_proj": (0, 16, 24, 28, 30, 32, 36, 40, 48, 64),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_REP_SETS = (frozenset(range(7)), frozenset(range(1, 8)))


class KneeError(ValueError):
    """Raw evidence is absent, ambiguous, or violates the frozen contract."""


def _first(row: Mapping[str, Any], names: Sequence[str], label: str) -> Any:
    for name in names:
        if name in row and row[name] is not None and str(row[name]).strip() != "":
            return row[name]
    raise KneeError(f"missing {label} (accepted columns: {', '.join(names)})")


def _text(value: Any, label: str) -> str:
    parsed = str(value).strip()
    if not parsed:
        raise KneeError(f"missing or empty {label}")
    return parsed


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise KneeError(f"invalid {label}: {value!r}")
    raw = str(value).strip()
    try:
        parsed = int(raw)
    except (TypeError, ValueError) as exc:
        raise KneeError(f"invalid {label}: {value!r}") from exc
    if raw not in (str(parsed), f"{parsed}.0"):
        raise KneeError(f"non-integral {label}: {value!r}")
    return parsed


def _positive_float(value: Any, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise KneeError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise KneeError(f"nonpositive/nonfinite {label}: {value!r}")
    return parsed


def _sha(value: Any, label: str) -> str:
    parsed = _text(value, label).lower()
    if not SHA256_RE.fullmatch(parsed):
        raise KneeError(f"{label} must be a lowercase SHA256")
    return parsed


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _point(row: Mapping[str, Any]) -> tuple[str, int, str, int, int]:
    domain = _text(_first(row, ("domain", "input_domain"), "domain"), "domain").upper()
    role = _text(_first(row, ("role", "operator_role"), "role"), "role")
    matrix_m = _integer(_first(row, ("M", "m"), "M"), "M")
    implementation = _text(
        _first(row, ("implementation", "impl"), "implementation"), "implementation"
    )
    dose = _integer(_first(row, ("dose_mib", "pressure_mib"), "dose_mib"), "dose_mib")
    prefix = _integer(
        _first(row, ("pressure_prefix_bytes", "prefix_bytes"), "pressure_prefix_bytes"),
        "pressure_prefix_bytes",
    )
    mode = _text(_first(row, ("pressure_mode",), "pressure_mode"), "pressure_mode")
    if domain != DOMAIN or matrix_m != M_VALUE or implementation != IMPLEMENTATION:
        raise KneeError(
            f"wrong point identity: expected {DOMAIN}/M{M_VALUE}/{IMPLEMENTATION}, "
            f"got {domain}/M{matrix_m}/{implementation}"
        )
    if role not in DOSE_SETS_MIB:
        raise KneeError(f"wrong role: {role!r}")
    if dose not in DOSE_SETS_MIB[role]:
        raise KneeError(f"dose {dose} MiB is outside frozen set for {role}")
    if mode != PRESSURE_MODE:
        raise KneeError(f"wrong pressure mode: {mode!r}")
    if prefix != dose * MIB:
        raise KneeError(
            f"wrong pressure prefix for {role}/{dose}MiB: {prefix} != {dose * MIB}"
        )
    return role, matrix_m, implementation, dose, prefix


def _stats(samples: Sequence[tuple[int, float]]) -> dict[str, Any]:
    values = [value for _, value in sorted(samples)]
    mean = statistics.fmean(values)
    return {
        "sample_count": len(values),
        "samples_ms": values,
        "min_ms": min(values),
        "median_ms": statistics.median(values),
        "max_ms": max(values),
        "mean_ms": mean,
        "cv": statistics.pstdev(values) / mean,
    }


def analyze_timing_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, int], list[tuple[int, float]]] = defaultdict(list)
    seen: set[tuple[str, int, int]] = set()
    identities: dict[str, tuple[str, str]] = {}
    row_count = 0
    for row in rows:
        row_count += 1
        role, _, _, dose, _ = _point(row)
        rep = _integer(_first(row, ("rep", "repetition"), "rep"), "rep")
        key = (role, dose, rep)
        if key in seen:
            raise KneeError(f"duplicate role/dose/rep: {key!r}")
        seen.add(key)
        elapsed = _positive_float(
            _first(row, ("timing_ms", "target_ms", "elapsed_ms"), "timing_ms"),
            "timing_ms",
        )
        identity = (
            _sha(_first(row, ("input_sha256", "target_input_sha256"), "input SHA256"), "input SHA256"),
            _sha(_first(row, ("output_sha256", "target_output_sha256"), "output SHA256"), "output SHA256"),
        )
        if role in identities and identities[role] != identity:
            raise KneeError(f"input/output SHA identity drift for {role}")
        identities[role] = identity
        grouped[role, dose].append((rep, elapsed))
    if not row_count:
        raise KneeError("empty timing evidence")

    expected = {(role, dose) for role, doses in DOSE_SETS_MIB.items() for dose in doses}
    if set(grouped) != expected:
        raise KneeError(
            f"timing point matrix mismatch: missing={sorted(expected-set(grouped))}, "
            f"extra={sorted(set(grouped)-expected)}"
        )
    rep_sets = {frozenset(rep for rep, _ in samples) for samples in grouped.values()}
    if len(rep_sets) != 1 or next(iter(rep_sets)) not in VALID_REP_SETS:
        raise KneeError(f"timing repetition matrix mismatch: {sorted(map(sorted, rep_sets))}")

    roles = []
    for role, doses in DOSE_SETS_MIB.items():
        baseline = _stats(grouped[role, 0])
        dose_rows = []
        for dose in doses:
            stats = _stats(grouped[role, dose])
            ratio = stats["median_ms"] / baseline["median_ms"]
            effect = abs(ratio - 1.0)
            dispersion = math.sqrt(baseline["cv"] ** 2 + stats["cv"] ** 2)
            dose_rows.append(
                {
                    "dose_mib": dose,
                    **stats,
                    "ratio_to_0MiB": ratio,
                    "effect_abs": effect,
                    "combined_dispersion_vs_0MiB": dispersion,
                    "material_vs_0MiB": effect >= 0.05 and effect > dispersion,
                }
            )
        roles.append(
            {
                "role": role,
                "input_sha256": identities[role][0],
                "output_sha256": identities[role][1],
                "doses": dose_rows,
            }
        )
    return {
        "status": "PASS",
        "authority": "RAW_SEVEN_REPETITION_TIMING_ROWS",
        "expected_repetitions_per_dose": EXPECTED_REPS,
        "roles": roles,
        "material_timing_rule": (
            "abs(median(dose)/median(0)-1)>=0.05 and effect>"
            "sqrt(CV_0^2+CV_dose^2)"
        ),
    }


def _resolve(root: Path, value: Any, label: str) -> Path:
    root = root.resolve()
    path = (root / _text(value, label)).resolve()
    if path != root and root not in path.parents:
        raise KneeError(f"{label} escapes evidence root")
    if not path.is_file():
        raise KneeError(f"missing {label}: {path}")
    return path


def _options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text, re.MULTILINE)


def _audit_session(path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="strict")
    if not text.strip():
        raise KneeError("empty SESSION evidence")
    replay = set(_options(text, "--replay-mode"))
    cache = set(_options(text, "--cache-control"))
    ranges = {value.rstrip("/") for value in _options(text, "--nvtx-include")}
    metrics = _options(text, "--metrics")
    if replay != {"application"}:
        raise KneeError(f"SESSION replay mode mismatch: {sorted(replay)}")
    if cache != {"none"}:
        raise KneeError(f"SESSION cache control mismatch: {sorted(cache)}")
    if ranges != {spec["range_name"]}:
        raise KneeError(f"SESSION exact target range mismatch: {sorted(ranges)}")
    if len(set(metrics)) != 1 or metrics[0].split(",") != [METRIC]:
        raise KneeError(f"SESSION exact metric set mismatch: {metrics}")
    return {
        "sha256": _sha256(path),
        "replay_mode": "application",
        "cache_control": "none",
        "metric": METRIC,
        "range_name": spec["range_name"],
    }


def _audit_profile(path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    receipts = []
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if value.get("status") == "PASS":
            receipts.append(value)
    if len(receipts) != 1:
        raise KneeError(f"PROFILE must contain exactly one PASS receipt, got {len(receipts)}")
    receipt = receipts[0]
    expected = {
        "role": spec["role"],
        "M": M_VALUE,
        "implementation": IMPLEMENTATION,
        "pressure_mode": PRESSURE_MODE,
        "dose_mib": spec["dose_mib"],
        "pressure_prefix_bytes": spec["pressure_prefix_bytes"],
        "range": spec["range_name"],
        "input_sha256": spec["input_sha256"],
        "output_sha256": spec["output_sha256"],
    }
    mismatch = {
        key: {"expected": expected_value, "observed": receipt.get(key)}
        for key, expected_value in expected.items()
        if receipt.get(key) != expected_value
    }
    if mismatch:
        raise KneeError("PROFILE identity mismatch: " + json.dumps(mismatch, sort_keys=True))
    return {"sha256": _sha256(path), "status": "PASS", **expected}


def _decimal(value: str, label: str) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise KneeError(f"invalid {label}: {value!r}") from exc
    if not result.is_finite() or result < 0:
        raise KneeError(f"negative/nonfinite {label}: {value!r}")
    return result


def _range_exact(cell: str, target: str) -> bool:
    return len(re.findall(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)", cell.strip())) == 1


def _read_base(path: Path, spec: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise KneeError("raw BASE is missing header/unit/data rows")
    header, units = table[0], table[1]
    if not header or len(header) != len(set(header)):
        raise KneeError("raw BASE has empty or duplicate headers")
    if len(units) != len(header):
        raise KneeError("raw BASE unit row width mismatch")
    index = {name: offset for offset, name in enumerate(header)}
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes", METRIC}
    missing = required - set(index)
    if missing:
        raise KneeError("raw BASE missing required columns: " + ",".join(sorted(missing)))
    ranges = [offset for offset, name in enumerate(header) if "Push/Pop_Range" in name]
    if len(ranges) != 1:
        raise KneeError("raw BASE has missing or ambiguous NVTX range column")
    if units[index[METRIC]].strip() != METRIC_UNIT:
        raise KneeError(f"raw BASE metric/unit mismatch: {units[index[METRIC]]!r}")
    candidates = []
    for number, row in enumerate(table[2:], 3):
        if len(row) != len(header):
            if any(cell.strip() for cell in row):
                raise KneeError(f"raw BASE malformed row width at row {number}")
            continue
        if row[index["ID"]].strip() and _range_exact(row[ranges[0]], spec["range_name"]):
            candidates.append(row)
    if not candidates:
        raise KneeError("raw BASE contains no exact target semantic range")
    processes = {row[index["Process ID"]].strip() for row in candidates}
    if "" in processes or len(processes) != 1:
        raise KneeError("raw BASE target range has ambiguous process identity")
    names = [row[index["Kernel Name"]].strip() for row in candidates]
    if not all(names) or len(names) != len(set(zip((row[index['ID']] for row in candidates), names))):
        raise KneeError("raw BASE has empty or duplicate kernel identity")
    if set(names) != set(spec["expected_kernel_names"]):
        raise KneeError(f"raw BASE target kernel inventory mismatch: {sorted(set(names))}")
    if set(names) & set(spec["pressure_kernel_names"]):
        raise KneeError("pressure kernel entered target semantic range")
    total = Decimal(0)
    for row in candidates:
        passes = _decimal(row[index["profiler__replayer_passes"]], "replayer passes")
        if passes != Decimal(spec["expected_pass_count"]):
            raise KneeError("raw BASE replay-pass mismatch")
        total += _decimal(row[index[METRIC]], METRIC)
    if total != total.to_integral_value():
        raise KneeError("DRAM-byte sum is not integral")
    return int(total), {
        "sha256": _sha256(path),
        "target_kernel_count": len(candidates),
        "kernel_names": sorted(names),
        "process_id": next(iter(processes)),
        "expected_pass_count": spec["expected_pass_count"],
    }


def _parse_profile(raw: Mapping[str, Any], root: Path) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise KneeError("each profile spec must be an object")
    role = _text(raw.get("role"), "role")
    dose = _integer(raw.get("dose_mib"), "dose_mib")
    identity_row = {
        "domain": raw.get("domain"),
        "role": role,
        "M": raw.get("M"),
        "implementation": raw.get("implementation"),
        "dose_mib": dose,
        "pressure_prefix_bytes": raw.get("pressure_prefix_bytes"),
        "pressure_mode": raw.get("pressure_mode"),
    }
    _, _, _, _, prefix = _point(identity_row)
    names = raw.get("expected_kernel_names")
    pressure_names = raw.get("pressure_kernel_names")
    if not isinstance(names, list) or not names or len(names) != len(set(names)):
        raise KneeError("expected_kernel_names must be a nonempty unique list")
    if not isinstance(pressure_names, list) or not pressure_names or len(pressure_names) != len(set(pressure_names)):
        raise KneeError("pressure_kernel_names must be a nonempty unique list")
    if set(names) & set(pressure_names):
        raise KneeError("target and pressure kernel inventories overlap")
    passes = _integer(raw.get("expected_pass_count"), "expected_pass_count")
    if passes <= 0:
        raise KneeError("expected_pass_count must be positive")
    parsed = {
        "role": role,
        "dose_mib": dose,
        "pressure_prefix_bytes": prefix,
        "range_name": _text(raw.get("range_name"), "range_name"),
        "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
        "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
        "expected_pass_count": passes,
        "expected_kernel_names": [_text(item, "expected kernel") for item in names],
        "pressure_kernel_names": [_text(item, "pressure kernel") for item in pressure_names],
        "base_path": _resolve(root, raw.get("base_path"), "BASE evidence"),
        "session_path": _resolve(root, raw.get("session_path"), "SESSION evidence"),
        "profile_path": _resolve(root, raw.get("profile_path"), "PROFILE evidence"),
    }
    return parsed


def consume_ncu_profiles(profiles: Iterable[Mapping[str, Any]], root: Path) -> dict[str, Any]:
    parsed_profiles = []
    seen = set()
    role_identity: dict[str, tuple[str, str]] = {}
    for raw in profiles:
        spec = _parse_profile(raw, root)
        key = (spec["role"], spec["dose_mib"])
        if key in seen:
            raise KneeError(f"duplicate semantic NCU dose state: {key!r}")
        seen.add(key)
        identity = (spec["input_sha256"], spec["output_sha256"])
        if spec["role"] in role_identity and role_identity[spec["role"]] != identity:
            raise KneeError(f"NCU input/output SHA identity drift for {spec['role']}")
        role_identity[spec["role"]] = identity
        session = _audit_session(spec["session_path"], spec)
        profile = _audit_profile(spec["profile_path"], spec)
        dram_bytes, base = _read_base(spec["base_path"], spec)
        parsed_profiles.append(
            {
                "role": spec["role"],
                "dose_mib": spec["dose_mib"],
                "pressure_prefix_bytes": spec["pressure_prefix_bytes"],
                "input_sha256": spec["input_sha256"],
                "output_sha256": spec["output_sha256"],
                "dram_bytes": dram_bytes,
                "base": base,
                "session": session,
                "profile": profile,
            }
        )
    expected = {(role, dose) for role, doses in DOSE_SETS_MIB.items() for dose in doses}
    if seen != expected:
        raise KneeError(
            f"NCU point matrix mismatch: missing={sorted(expected-seen)}, extra={sorted(seen-expected)}"
        )
    return {
        "status": "PASS",
        "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY",
        "profiles": sorted(parsed_profiles, key=lambda item: (item["role"], item["dose_mib"])),
    }


def _load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise KneeError("timing TSV has missing or duplicate headers")
        return list(reader)


def consume(contract: Mapping[str, Any], root: Path) -> dict[str, Any]:
    if not isinstance(contract, Mapping) or contract.get("schema_version") != 1:
        raise KneeError("unsupported knee consumer schema_version")
    timing_path = _resolve(root, contract.get("timing_tsv"), "timing TSV")
    profiles = contract.get("profiles")
    if not isinstance(profiles, list):
        raise KneeError("profiles must be a list")
    timing = analyze_timing_rows(_load_tsv(timing_path))
    ncu = consume_ncu_profiles(profiles, root)
    timing_by_role = {item["role"]: item for item in timing["roles"]}
    ncu_by_role_dose = {(item["role"], item["dose_mib"]): item for item in ncu["profiles"]}
    analyses = []
    for role, doses in DOSE_SETS_MIB.items():
        timing_role = timing_by_role[role]
        ncu_identity = {
            (ncu_by_role_dose[role, dose]["input_sha256"], ncu_by_role_dose[role, dose]["output_sha256"])
            for dose in doses
        }
        timing_identity = (timing_role["input_sha256"], timing_role["output_sha256"])
        if ncu_identity != {timing_identity}:
            raise KneeError(f"timing/NCU identity drift for {role}")
        zero_dram = ncu_by_role_dose[role, 0]["dram_bytes"]
        packed = PACKED_STATE_BYTES[role]
        dose_rows = []
        for timing_dose in timing_role["doses"]:
            dose = timing_dose["dose_mib"]
            dram = ncu_by_role_dose[role, dose]["dram_bytes"]
            dose_rows.append(
                {
                    **timing_dose,
                    "dram_bytes": dram,
                    "dram_ratio_to_0MiB": dram / zero_dram if zero_dram else None,
                    "dram_exceeds_1MiB_and_10pct_packed": dram > MIB and dram > 0.10 * packed,
                }
            )
        dram_knee = next((row["dose_mib"] for row in dose_rows if row["dram_exceeds_1MiB_and_10pct_packed"]), None)
        timing_knee = next((row["dose_mib"] for row in dose_rows if row["dose_mib"] > 0 and row["material_vs_0MiB"]), None)
        residual = DEVICE_L2_BYTES - packed
        analyses.append(
            {
                "role": role,
                "device_l2_bytes": DEVICE_L2_BYTES,
                "packed_state_bytes": packed,
                "nominal_residual_l2_bytes": residual,
                "nominal_residual_l2_mib": residual / MIB,
                "doses": dose_rows,
                "first_dram_over_1MiB_and_10pct_packed_mib": dram_knee,
                "first_material_timing_dose_mib": timing_knee,
                "observed_dram_knee_minus_nominal_residual_l2_mib": (
                    dram_knee - residual / MIB if dram_knee is not None else None
                ),
            }
        )
    return {
        "status": "PASS",
        "authority": {
            "timing": "RAW_SEVEN_REPETITION_TIMING_ROWS",
            "ncu": "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY",
            "producer_summary_used": False,
        },
        "frozen_dose_sets_mib": {key: list(value) for key, value in DOSE_SETS_MIB.items()},
        "exact_knee_equality_is_pass_gate": False,
        "roles": analyses,
        "timing_evidence_sha256": _sha256(timing_path),
        "scope": (
            "descriptive nominal-capacity alignment; not an exact "
            "effective-cache-capacity theorem"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = consume(
        json.loads(args.contract.read_text(encoding="utf-8")), args.evidence_root
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "roles": len(result["roles"])}, sort_keys=True))
