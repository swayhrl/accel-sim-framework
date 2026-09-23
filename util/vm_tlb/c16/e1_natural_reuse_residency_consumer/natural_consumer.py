#!/usr/bin/env python3
"""Fail-closed consumer for C16 E1 natural full-model reuse evidence.

Producer summaries are intentionally not inputs.  Timing is recomputed from
raw full-run rows and NCU traffic is recomputed from BASE + SESSION + PROFILE.
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


class NaturalConsumerError(ValueError):
    """Raw evidence is missing, ambiguous, or violates frozen identity."""


METRICS = ("l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum")
METRIC_UNIT = "byte"
EXPECTED_REPS = 7
NATURAL_MATRIX = frozenset(
    [(0, "up_proj", d) for d in range(4)]
    + [(14, "up_proj", d) for d in range(4)]
    + [(0, "down_proj", d) for d in range(4)]
)
NCU_MATRIX = frozenset(
    {(0, "up_proj", 0), (0, "up_proj", 1), (0, "up_proj", 3),
     (14, "up_proj", 0), (14, "up_proj", 3),
     (0, "down_proj", 0), (0, "down_proj", 3)}
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _first(row: Mapping[str, Any], names: Sequence[str], label: str) -> Any:
    for name in names:
        if name in row and row[name] is not None and str(row[name]).strip() != "":
            return row[name]
    raise NaturalConsumerError(f"missing {label}")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NaturalConsumerError(f"missing or empty {label}")
    return value.strip()


def _int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise NaturalConsumerError(f"invalid {label}")
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise NaturalConsumerError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() not in (str(parsed), f"{parsed}.0"):
        raise NaturalConsumerError(f"non-integral {label}: {value!r}")
    return parsed


def _sha(value: Any, label: str) -> str:
    parsed = str(value).strip().lower()
    if not HEX64.fullmatch(parsed):
        raise NaturalConsumerError(f"invalid {label}: expected lowercase SHA256")
    return parsed


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise NaturalConsumerError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed) or (positive and parsed <= 0):
        raise NaturalConsumerError(f"nonfinite/nonpositive {label}: {value!r}")
    return parsed


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _token_ids(value: Any, label: str) -> tuple[int, ...]:
    if not isinstance(value, list) or len(value) != 4:
        raise NaturalConsumerError(f"{label} must contain exactly D0..D3")
    parsed = tuple(_int(item, f"{label}[{i}]") for i, item in enumerate(value))
    if any(item < 0 for item in parsed):
        raise NaturalConsumerError(f"{label} contains a negative token ID")
    return parsed


def _parse_occurrences(value: Any, label: str) -> dict[tuple[int, str, int], dict]:
    if not isinstance(value, list):
        raise NaturalConsumerError(f"{label} must be a list")
    parsed: dict[tuple[int, str, int], dict] = {}
    for raw in value:
        if not isinstance(raw, dict):
            raise NaturalConsumerError(f"{label} entry must be an object")
        layer = _int(raw.get("layer_index"), "layer_index")
        role = _text(raw.get("role"), "role")
        decode = _int(raw.get("decode_index"), "decode_index")
        key = (layer, role, decode)
        if key in parsed:
            raise NaturalConsumerError(f"duplicate occurrence: {key!r}")
        m_value = _int(raw.get("M"), "M")
        if m_value != 1:
            raise NaturalConsumerError(f"natural target is not M1: {key!r}/M{m_value}")
        implementation = _text(raw.get("implementation"), "implementation")
        if implementation != "AWQ_FP16_INPUT":
            raise NaturalConsumerError(
                f"natural full-model target is not AWQ_FP16_INPUT: {key!r}"
            )
        parsed[key] = {
            "layer_index": layer,
            "role": role,
            "decode_index": decode,
            "M": 1,
            "implementation": implementation,
            "generated_token_id": _int(raw.get("generated_token_id"), "generated_token_id"),
            "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
            "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
            "range_name": _text(raw.get("range_name"), "range_name"),
        }
    return parsed


def validate_natural_contract(contract: Mapping[str, Any]) -> dict:
    """Validate accepted prefix, fresh replay, tokens, and all M1 occurrences."""
    if not isinstance(contract, Mapping):
        raise NaturalConsumerError("natural contract must be an object")
    accepted = _sha(contract.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    prefix = _sha(contract.get("prefix_token_sha256"), "prefix_token_sha256")
    fresh_prefix = _sha(
        contract.get("fresh_process_prefix_token_sha256"),
        "fresh_process_prefix_token_sha256",
    )
    if len({accepted, prefix, fresh_prefix}) != 1:
        raise NaturalConsumerError("accepted/fresh-process prefix SHA mismatch")
    tokens = _token_ids(contract.get("generated_token_ids"), "generated_token_ids")
    replay_tokens = _token_ids(
        contract.get("fresh_process_generated_token_ids"),
        "fresh_process_generated_token_ids",
    )
    if tokens != replay_tokens:
        raise NaturalConsumerError("fresh-process token sequence mismatch")
    occurrences = _parse_occurrences(contract.get("occurrences"), "occurrences")
    replay = _parse_occurrences(
        contract.get("fresh_process_occurrences"), "fresh_process_occurrences"
    )
    if set(occurrences) != NATURAL_MATRIX:
        raise NaturalConsumerError(
            f"natural occurrence matrix mismatch: missing={sorted(NATURAL_MATRIX-set(occurrences))}, "
            f"extra={sorted(set(occurrences)-NATURAL_MATRIX)}"
        )
    if set(replay) != NATURAL_MATRIX:
        raise NaturalConsumerError("fresh-process occurrence matrix mismatch")
    for key in sorted(NATURAL_MATRIX):
        expected = occurrences[key]
        observed = replay[key]
        if expected != observed:
            raise NaturalConsumerError(f"fresh-process occurrence SHA/identity mismatch: {key!r}")
        if expected["generated_token_id"] != tokens[key[2]]:
            raise NaturalConsumerError(f"occurrence token ID mismatch: {key!r}")
    ranges = [item["range_name"] for item in occurrences.values()]
    if len(ranges) != len(set(ranges)):
        raise NaturalConsumerError("duplicate NVTX range across occurrences")
    return {
        "accepted_prefix_sha256": accepted,
        "generated_token_ids": list(tokens),
        "occurrences": occurrences,
        "fresh_process_replay_verified": True,
    }


def _stats(samples: list[tuple[int, float]]) -> dict:
    values = [value for _, value in sorted(samples)]
    mean = statistics.fmean(values)
    return {
        "sample_count": len(values), "samples_ms": values,
        "min_ms": min(values), "median_ms": statistics.median(values),
        "max_ms": max(values), "mean_ms": mean,
        "cv": statistics.pstdev(values) / mean,
    }


def analyze_natural_timing_rows(
    rows: Iterable[Mapping[str, Any]], contract: Mapping[str, Any],
    expected_reps: int = EXPECTED_REPS,
) -> dict:
    authority = validate_natural_contract(contract)
    if expected_reps <= 0:
        raise NaturalConsumerError("expected_reps must be positive")
    grouped: dict[tuple[int, str, int], list[tuple[int, float]]] = defaultdict(list)
    seen: set[tuple[int, str, int, int]] = set()
    for row in rows:
        key = (
            _int(_first(row, ("layer_index", "layer"), "layer_index"), "layer_index"),
            _text(_first(row, ("role",), "role"), "role"),
            _int(_first(row, ("decode_index", "decode_occurrence"), "decode_index"), "decode_index"),
        )
        if key not in authority["occurrences"]:
            raise NaturalConsumerError(f"wrong layer/role/decode index: {key!r}")
        rep = _int(_first(row, ("rep", "repetition"), "rep"), "rep")
        unique = (*key, rep)
        if unique in seen:
            raise NaturalConsumerError(f"duplicate timing occurrence/rep: {unique!r}")
        seen.add(unique)
        expected = authority["occurrences"][key]
        actual = {
            "M": _int(_first(row, ("M", "m"), "M"), "M"),
            "implementation": _text(
                _first(row, ("implementation", "impl"), "implementation"),
                "implementation",
            ),
            "generated_token_id": _int(_first(row, ("generated_token_id", "token_id"), "token"), "token"),
            "input_sha256": _sha(_first(row, ("input_sha256",), "input SHA"), "input SHA"),
            "output_sha256": _sha(_first(row, ("output_sha256",), "output SHA"), "output SHA"),
            "range_name": _text(_first(row, ("range_name", "nvtx_range"), "range"), "range"),
        }
        for field, observed in actual.items():
            if observed != expected[field]:
                raise NaturalConsumerError(f"timing {field} mismatch for {key!r}")
        if _sha(_first(row, ("prefix_token_sha256", "prefix_sha256"), "prefix SHA"), "prefix SHA") != authority["accepted_prefix_sha256"]:
            raise NaturalConsumerError("timing accepted prefix SHA mismatch")
        grouped[key].append((rep, _finite(_first(row, ("timing_ms", "elapsed_ms", "target_ms"), "timing"), "timing", positive=True)))
    if set(grouped) != NATURAL_MATRIX:
        raise NaturalConsumerError("missing/extra natural timing occurrence")
    points = []
    for key in sorted(NATURAL_MATRIX):
        samples = grouped[key]
        if {rep for rep, _ in samples} != set(range(expected_reps)):
            raise NaturalConsumerError(f"missing/extra timing repetition for {key!r}")
        points.append({**authority["occurrences"][key], "statistics": _stats(samples)})
    return {
        "status": "PASS", "authority": "RAW_FULL_RUN_TIMING_ROWS_ONLY",
        "expected_repetitions": expected_reps,
        "accepted_prefix_sha256": authority["accepted_prefix_sha256"],
        "generated_token_ids": authority["generated_token_ids"], "points": points,
    }


def _session_options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text, re.MULTILINE)


def _nvtx_exact(cell: str, target: str) -> bool:
    return len(re.findall(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)", cell.strip())) == 1


def _decimal(value: str, label: str) -> Decimal:
    try:
        parsed = Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise NaturalConsumerError(f"invalid {label}") from exc
    if not parsed.is_finite() or parsed < 0:
        raise NaturalConsumerError(f"invalid/nonfinite {label}")
    return parsed


def _audit_session(path: Path, expected: Mapping[str, Any]) -> dict:
    text = path.read_text(encoding="utf-8", errors="strict")
    replay = set(_session_options(text, "--replay-mode"))
    cache = set(_session_options(text, "--cache-control"))
    ranges = {item.rstrip("/") for item in _session_options(text, "--nvtx-include")}
    metric_args = set(_session_options(text, "--metrics"))
    if replay != {"application"}:
        raise NaturalConsumerError("SESSION replay mode is not uniquely application")
    if cache != {"none"}:
        raise NaturalConsumerError("SESSION cache control is not uniquely none")
    if ranges != {expected["range_name"]}:
        raise NaturalConsumerError("SESSION NCU range mismatch")
    if len(metric_args) != 1 or set(next(iter(metric_args)).split(",")) != set(METRICS):
        raise NaturalConsumerError("SESSION exact metric set mismatch")
    return {"sha256": _hash_file(path), "replay_mode": "application", "cache_control": "none"}


def _audit_profile(path: Path, expected: Mapping[str, Any], authority: Mapping[str, Any]) -> dict:
    receipts = []
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("status") == "PASS":
            receipts.append(item)
    if len(receipts) != 1:
        raise NaturalConsumerError("PROFILE must contain exactly one PASS receipt")
    receipt = receipts[0]
    checks = {
        "layer_index": expected["layer_index"], "role": expected["role"],
        "decode_index": expected["decode_index"], "M": 1,
        "implementation": expected["implementation"],
        "generated_token_id": expected["generated_token_id"],
        "range": expected["range_name"],
        "input_sha256": expected["input_sha256"],
        "output_sha256": expected["output_sha256"],
        "prefix_token_sha256": authority["accepted_prefix_sha256"],
    }
    mismatches = {key: (value, receipt.get(key)) for key, value in checks.items() if receipt.get(key) != value}
    if mismatches:
        raise NaturalConsumerError("PROFILE natural identity mismatch: " + repr(mismatches))
    return {"sha256": _hash_file(path), **checks}


def _read_base(path: Path, expected: Mapping[str, Any], expected_names: list[str], expected_passes: int) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise NaturalConsumerError("raw BASE missing header/unit/data rows")
    header, units = table[:2]
    if not header or len(header) != len(set(header)) or len(units) != len(header):
        raise NaturalConsumerError("raw BASE malformed header/unit rows")
    index = {name: i for i, name in enumerate(header)}
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes", *METRICS}
    missing = required - set(index)
    if missing:
        raise NaturalConsumerError("raw BASE missing columns: " + ",".join(sorted(missing)))
    ranges = [i for i, name in enumerate(header) if "Push/Pop_Range" in name]
    if len(ranges) != 1:
        raise NaturalConsumerError("raw BASE ambiguous NVTX range column")
    for metric in METRICS:
        if units[index[metric]].strip() != METRIC_UNIT:
            raise NaturalConsumerError(f"raw BASE metric unit mismatch: {metric}")
    selected = []
    for row in table[2:]:
        if len(row) != len(header):
            if any(cell.strip() for cell in row):
                raise NaturalConsumerError("raw BASE malformed row width")
            continue
        if row[index["ID"]].strip() and _nvtx_exact(row[ranges[0]], expected["range_name"]):
            selected.append(row)
    if not selected:
        raise NaturalConsumerError("raw BASE has no exact target range rows")
    processes = {row[index["Process ID"]].strip() for row in selected}
    ids = [row[index["ID"]].strip() for row in selected]
    names = [row[index["Kernel Name"]].strip() for row in selected]
    if "" in processes or len(processes) != 1 or "" in ids or len(ids) != len(set(ids)):
        raise NaturalConsumerError("raw BASE ambiguous process/kernel identity")
    if names != expected_names and sorted(names) != sorted(expected_names):
        raise NaturalConsumerError("raw BASE exact kernel inventory mismatch")
    sums = {metric: Decimal(0) for metric in METRICS}
    for row in selected:
        passes = _decimal(row[index["profiler__replayer_passes"]], "replayer passes")
        if passes != Decimal(expected_passes):
            raise NaturalConsumerError("raw BASE profiler__replayer_passes mismatch")
        for metric in METRICS:
            sums[metric] += _decimal(row[index[metric]], metric)
    return {
        "sha256": _hash_file(path), "process_id": next(iter(processes)),
        "kernel_names": names, "kernel_count": len(names),
        "metric_sums": {metric: str(value) for metric, value in sums.items()},
    }


def consume_natural_ncu(document: Mapping[str, Any], root: Path = Path(".")) -> dict:
    if document.get("schema_version") != 1:
        raise NaturalConsumerError("unsupported natural NCU schema_version")
    authority = validate_natural_contract(document.get("contract"))
    profiles = document.get("profiles")
    if not isinstance(profiles, list):
        raise NaturalConsumerError("profiles must be a list")
    seen: set[tuple[int, str, int]] = set()
    output = []
    for raw in profiles:
        key = (_int(raw.get("layer_index"), "layer_index"), _text(raw.get("role"), "role"), _int(raw.get("decode_index"), "decode_index"))
        if key not in NCU_MATRIX:
            raise NaturalConsumerError(f"wrong NCU occurrence: {key!r}")
        if key in seen:
            raise NaturalConsumerError(f"duplicate NCU occurrence: {key!r}")
        seen.add(key)
        expected = authority["occurrences"][key]
        for field in ("M", "implementation", "generated_token_id", "input_sha256", "output_sha256", "range_name"):
            observed = raw.get(field)
            if field in ("M", "generated_token_id"):
                observed = _int(observed, field)
            elif field.endswith("sha256"):
                observed = _sha(observed, field)
            else:
                observed = _text(observed, field)
            if observed != expected[field]:
                raise NaturalConsumerError(f"NCU {field} mismatch for {key!r}")
        names = raw.get("expected_kernel_names")
        if not isinstance(names, list) or not names or len(names) != len(set(names)) or not all(isinstance(x, str) and x for x in names):
            raise NaturalConsumerError("invalid expected kernel inventory")
        passes = _int(raw.get("expected_pass_count"), "expected_pass_count")
        paths = {}
        for kind in ("base", "session", "profile"):
            path = root / _text(raw.get(f"{kind}_path"), f"{kind}_path")
            if not path.is_file():
                raise NaturalConsumerError(f"missing raw {kind.upper()} evidence")
            paths[kind] = path
        output.append({
            "semantic_identity": {
                "layer_index": key[0], "role": key[1], "decode_index": key[2],
                "M": 1, "implementation": expected["implementation"],
            },
            "range_name": expected["range_name"],
            "session": _audit_session(paths["session"], expected),
            "profile": _audit_profile(paths["profile"], expected, authority),
            "base": _read_base(paths["base"], expected, names, passes),
        })
    if seen != NCU_MATRIX:
        raise NaturalConsumerError(f"NCU occurrence matrix mismatch: missing={sorted(NCU_MATRIX-seen)}")
    return {
        "status": "PASS", "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY",
        "semantic_identity_fields": [
            "layer_index", "role", "decode_index", "M", "implementation"
        ],
        "accepted_prefix_sha256": authority["accepted_prefix_sha256"],
        "generated_token_ids": authority["generated_token_ids"], "profiles": output,
    }


def _fraction(natural: float, warm: float, dense: float) -> tuple[float | None, str]:
    denominator = abs(dense - warm)
    if denominator == 0:
        return None, "UNDEFINED_ZERO_DENOMINATOR"
    return abs(natural - warm) / denominator, "DEFINED_UNCLAMPED"


def compare_natural_to_isolated(
    natural_points: Iterable[Mapping[str, Any]], isolated_references: Iterable[Mapping[str, Any]],
) -> dict:
    """Compare raw-derived natural values with accepted isolated WARM/DENSE values."""
    references: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for ref in isolated_references:
        key = (_text(ref.get("role"), "role"), _text(ref.get("implementation"), "implementation"), _int(ref.get("M"), "M"))
        if key in references:
            raise NaturalConsumerError(f"duplicate isolated reference: {key!r}")
        references[key] = ref
    comparisons = []
    seen = set()
    for raw in natural_points:
        identity = (_int(raw.get("layer_index"), "layer_index"), _text(raw.get("role"), "role"), _int(raw.get("decode_index"), "decode_index"))
        if identity in seen:
            raise NaturalConsumerError(f"duplicate natural comparator occurrence: {identity!r}")
        seen.add(identity)
        ref_key = (identity[1], _text(raw.get("implementation"), "implementation"), _int(raw.get("M"), "M"))
        if ref_key not in references:
            raise NaturalConsumerError(f"missing isolated reference: {ref_key!r}")
        ref = references[ref_key]
        row = {"layer_index": identity[0], "role": identity[1], "decode_index": identity[2], "implementation": ref_key[1], "M": ref_key[2]}
        for dimension, natural_name, warm_name, dense_name in (
            ("timing", "timing_ms", "warm_timing_ms", "dense_timing_ms"),
            ("dram", "dram_bytes", "warm_dram_bytes", "dense_dram_bytes"),
        ):
            natural = _finite(raw.get(natural_name), natural_name)
            warm = _finite(ref.get(warm_name), warm_name)
            dense = _finite(ref.get(dense_name), dense_name)
            fraction, status = _fraction(natural, warm, dense)
            row[dimension] = {"natural": natural, "isolated_warm": warm, "isolated_dense": dense, "warm_fraction": fraction, "status": status, "outside_bracket": fraction is not None and fraction > 1.0}
        comparisons.append(row)
    if not comparisons:
        raise NaturalConsumerError("empty natural comparator evidence")
    return {"status": "PASS", "formula": "abs(natural-warm)/abs(dense-warm)", "clamped": False, "comparisons": comparisons}


def frame_integrated_interpretation(
    *, refill_clear: bool, natural_warm_like: bool | None,
    role_dependent: bool, capacity_observation: str,
    access_policy_observation: str, natural_interference_observation: str,
) -> dict:
    """Apply DESIGN A/B/C/D framing without authorizing a mechanism."""
    if not refill_clear:
        primary = "CASE_C_NO_CLEAR_REFILL_DYNAMICS"
    elif natural_warm_like is True:
        primary = "CASE_A_ISOLATED_REFILL_NATURAL_WARM_LIKE"
    elif natural_warm_like is False:
        primary = "CASE_B_ISOLATED_REFILL_NATURAL_DENSE_LIKE"
    else:
        primary = "UNRESOLVED_NATURAL_PROXIMITY"
    return {
        "primary_case": primary,
        "case_d_role_dependent": bool(role_dependent),
        "separable_observations": {
            "capacity_effect": _text(capacity_observation, "capacity observation"),
            "role_access_policy_effect": _text(access_policy_observation, "access-policy observation"),
            "natural_inter_module_interference_effect": _text(natural_interference_observation, "natural interference observation"),
        },
        "mechanism_authorized": False,
        "scope": "descriptive_case_framing_only",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("timing", "ncu"), required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--rows", type=Path)
    parser.add_argument("--point-spec", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "timing":
        if args.contract is None or args.rows is None:
            parser.error("timing mode requires --contract and --rows")
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        with args.rows.open(newline="", encoding="utf-8-sig") as stream:
            result = analyze_natural_timing_rows(csv.DictReader(stream), contract)
    else:
        if args.point_spec is None:
            parser.error("ncu mode requires --point-spec")
        document = json.loads(args.point_spec.read_text(encoding="utf-8"))
        result = consume_natural_ncu(document, args.point_spec.parent)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS"}))


if __name__ == "__main__":
    main()
