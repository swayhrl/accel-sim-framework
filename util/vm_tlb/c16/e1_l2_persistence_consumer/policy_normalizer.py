#!/usr/bin/env python3
"""Deterministically assemble a rich policy receipt from split raw authority."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

try:
    from policy_receipt import PolicyReceiptError, validate_policy_receipt
except ImportError:
    from .policy_receipt import PolicyReceiptError, validate_policy_receipt


HEX64 = re.compile(r"^[0-9a-f]{64}$")
TARGET_CONDITION = {
    "PERSIST_L0_UP": "L0_UP",
    "PERSIST_L14_UP": "L14_UP",
    "PERSIST_L0_DOWN": "L0_DOWN",
    "ISO_QWEIGHT_PERSIST_DENSE": "L0_UP",
}


class PolicyNormalizationError(ValueError):
    """Split raw authority is incomplete, ambiguous, or internally inconsistent."""


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PolicyNormalizationError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise PolicyNormalizationError(f"invalid {label}")
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise PolicyNormalizationError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() not in {str(parsed), f"{parsed}.0"} or parsed < minimum:
        raise PolicyNormalizationError(f"invalid {label}: {value!r}")
    return parsed


def _sha(value: Any, label: str) -> str:
    parsed = str(value).strip().lower()
    if not HEX64.fullmatch(parsed):
        raise PolicyNormalizationError(f"invalid {label}")
    return parsed


def _canonical_sha(document: Mapping[str, Any]) -> str:
    data = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def _provenance(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise PolicyNormalizationError("source_provenance must be a nonempty list")
    output = []
    labels = set()
    for item in value:
        if not isinstance(item, Mapping):
            raise PolicyNormalizationError("source provenance entry must be an object")
        label = _text(item.get("label"), "source label")
        if label in labels:
            raise PolicyNormalizationError(f"duplicate source label: {label}")
        labels.add(label)
        output.append({"label": label, "path": _text(item.get("path"), "source path"),
                       "sha256": _sha(item.get("sha256"), "source sha256")})
    if not {"capability", "carrier"}.issubset(labels):
        raise PolicyNormalizationError("capability and carrier source provenance are required")
    return output


def _operations(receipt: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    raw = receipt.get(key)
    if not isinstance(raw, list) or not raw:
        raise PolicyNormalizationError(f"missing {key}")
    output = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise PolicyNormalizationError(f"malformed {key} operation")
        operation = _text(item.get("operation"), f"{key}.operation")
        status = _integer(item.get("status"), f"{key}.status")
        if status != 0:
            raise PolicyNormalizationError(f"failed CUDA policy operation: {operation}")
        output.append({"operation": operation, "status": status,
                       "error_string": str(item.get("error_string", ""))})
    return output


def _require_operation(operations: Sequence[Mapping[str, Any]], *tokens: str) -> str:
    matches = []
    for item in operations:
        compact = str(item["operation"]).lower()
        if all(token in compact for token in tokens):
            matches.append(str(item["operation"]))
    if len(matches) != 1:
        raise PolicyNormalizationError(
            f"required operation is missing or ambiguous: {'+'.join(tokens)}"
        )
    return matches[0]


def _region(carrier: Mapping[str, Any], target: str) -> Mapping[str, Any]:
    regions = carrier.get("qweight_regions")
    if isinstance(regions, Mapping):
        raw = regions.get(target)
    else:
        raw = carrier.get("qweight_region")
    if not isinstance(raw, Mapping):
        raise PolicyNormalizationError(f"missing exact qweight region for {target}")
    pointer = _integer(raw.get("data_ptr"), "qweight.data_ptr", 1)
    size = _integer(raw.get("bytes"), "qweight.bytes", 1)
    if raw.get("contiguous") is not True:
        raise PolicyNormalizationError("qweight is not contiguous")
    if _integer(raw.get("storage_offset_bytes"), "storage_offset_bytes") != 0:
        raise PolicyNormalizationError("qweight storage offset is not zero")
    if _integer(raw.get("storage_offset_elements"), "storage_offset_elements") != 0:
        raise PolicyNormalizationError("qweight element storage offset is not zero")
    if _integer(raw.get("storage_nbytes"), "storage_nbytes", 1) != size:
        raise PolicyNormalizationError("qweight storage size differs from tensor bytes")
    if _integer(raw.get("exact_tensor_span_begin"), "span begin", 1) != pointer:
        raise PolicyNormalizationError("qweight span begin differs from data_ptr")
    if _integer(raw.get("exact_tensor_span_end_exclusive"), "span end", 1) != pointer + size:
        raise PolicyNormalizationError("qweight span is not the exact independent interval")
    return raw


def normalize_raw_policy_receipt(
    capability: Mapping[str, Any],
    carrier: Mapping[str, Any],
    *,
    expected_condition: str,
    expected_target: str | None = None,
    expected_budget_bytes: int | None = None,
    source_provenance: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Assemble and validate one policy receipt without inventing authority."""
    if not isinstance(capability, Mapping) or capability.get("status") != "PASS":
        raise PolicyNormalizationError("raw capability authority is not PASS")
    if not isinstance(carrier, Mapping) or carrier.get("status", "PASS") != "PASS":
        raise PolicyNormalizationError("raw carrier is not PASS")
    sources = _provenance(source_provenance)
    runtime = capability.get("runtime_execution_authority")
    if not isinstance(runtime, Mapping):
        raise PolicyNormalizationError("missing runtime execution authority")
    for key in ("l2_bytes", "max_persisting_l2_bytes", "max_access_policy_window_bytes"):
        if capability.get("runtime_matches_accepted", {}).get(key) is not True:
            raise PolicyNormalizationError(f"runtime capability mismatch: {key}")
    low = carrier.get("policy_receipt")
    if not isinstance(low, Mapping):
        raise PolicyNormalizationError("carrier lacks low-level policy_receipt")

    expected = _text(expected_condition, "expected_condition").upper()
    raw_condition = _text(low.get("condition", carrier.get("condition")), "raw condition").upper()
    carrier_condition = _text(carrier.get("condition", raw_condition), "carrier condition").upper()
    if carrier_condition != raw_condition:
        raise PolicyNormalizationError("carrier/policy condition mismatch")
    budget_mode = raw_condition == "BUDGET_L0_UP"
    if budget_mode:
        if not expected.startswith("PERSIST_L0_UP_BUDGET_") or expected_target != "L0_UP":
            raise PolicyNormalizationError("BUDGET_L0_UP cannot be normalized to requested class")
        if expected_budget_bytes is None:
            raise PolicyNormalizationError("budget normalization requires tested budget")
    elif raw_condition != expected:
        raise PolicyNormalizationError(
            f"raw condition mismatch: expected {expected}, got {raw_condition}"
        )

    before, after = _operations(low, "operations_before"), _operations(low, "operations_after")
    reset_before_op = _require_operation(before, "reset", "persist")
    reset_after_op = _require_operation(after, "reset", "persist")
    _require_operation(before, "clear", "stream", "access-policy")
    _require_operation(before, "set", "persisting-l2", "limit")
    _require_operation(after, "clear", "stream", "access-policy")
    _require_operation(after, "clear", "persisting-l2", "limit")
    if low.get("reset_before") is not True or low.get("reset_after") is not True:
        raise PolicyNormalizationError("reset flags are not closed")
    if _integer(low.get("actual_setaside_after_reset_bytes"), "post-reset set-aside") != 0:
        raise PolicyNormalizationError("set-aside remains active after reset")

    requested = _integer(low.get("requested_setaside_bytes"), "requested set-aside")
    actual = _integer(low.get("actual_setaside_bytes"), "actual set-aside")
    max_persist = _integer(runtime.get("max_persisting_l2_bytes"), "max persisting", 1)
    if not requested <= actual <= max_persist:
        raise PolicyNormalizationError("runtime set-aside query-back is outside request/max bounds")
    if expected_budget_bytes is not None and requested != _integer(expected_budget_bytes, "expected budget"):
        raise PolicyNormalizationError("tested requested budget mismatch")

    target = expected_target
    target_mode = expected in TARGET_CONDITION or expected.startswith("PERSIST_L0_UP_BUDGET_")
    if target_mode:
        canonical_target = TARGET_CONDITION.get(expected, "L0_UP")
        if target != canonical_target:
            raise PolicyNormalizationError("expected target does not match policy class")
        region = _region(carrier, canonical_target)
        qptr, qbytes = _integer(region["data_ptr"], "qweight pointer", 1), _integer(region["bytes"], "qweight bytes", 1)
        window = low.get("access_policy_window")
        if not isinstance(window, Mapping):
            raise PolicyNormalizationError("target persistence lacks access-policy window")
        _require_operation(before, "set", "stream", "access-policy", "window")
        base = _integer(window.get("base_ptr"), "window base", 1)
        size = _integer(window.get("num_bytes"), "window bytes", 1)
        if base != qptr or size != qbytes:
            raise PolicyNormalizationError("access window is not exact target qweight interval")
        ratio = float(window.get("hit_ratio"))
        required_ratio = min(1.0, requested / qbytes)
        if not abs(ratio - required_ratio) <= 1e-12:
            raise PolicyNormalizationError("raw hitRatio violates tested budget formula")
        if window.get("hit_property") != "cudaAccessPropertyPersisting":
            raise PolicyNormalizationError("raw hit property is not persisting")
        rich_qweight = {"target": canonical_target, "pointer": qptr, "bytes": qbytes,
                        "contiguous": True}
        window_fields = {
            "access_window_enabled": True, "access_window_base_pointer": base,
            "access_window_num_bytes": size, "hit_ratio": ratio,
            "hit_prop": window.get("hit_property"), "miss_prop": window.get("miss_property"),
            "target_persisting_enabled": True,
        }
    else:
        if low.get("access_policy_window") is not None:
            raise PolicyNormalizationError("non-target condition has active access-policy window")
        if expected in {"BASELINE", "ISO_BASELINE_DENSE"} and (requested != 0 or actual != 0):
            raise PolicyNormalizationError("baseline set-aside is not disabled")
        if expected == "SETASIDE_ONLY" and (requested == 0 or actual == 0):
            raise PolicyNormalizationError("SETASIDE_ONLY lacks matched nonzero budget")
        rich_qweight = None
        window_fields = {
            "access_window_enabled": False, "access_window_base_pointer": 0,
            "access_window_num_bytes": 0, "hit_ratio": 0.0,
            "target_persisting_enabled": False,
        }

    rich: dict[str, Any] = {
        "status": "PASS", "condition": expected, "raw_condition": raw_condition,
        "cuda_runtime_version": str(runtime.get("runtime_version")),
        "device_ordinal": runtime.get("device_ordinal"),
        "device_name": runtime.get("device_name"), "persistence_supported": True,
        "l2_bytes": runtime.get("l2_bytes"),
        "max_persisting_l2_bytes": runtime.get("max_persisting_l2_bytes"),
        "max_access_policy_window_bytes": runtime.get("max_access_policy_window_bytes"),
        "target": target or "NONE", "requested_setaside_bytes": requested,
        "actual_setaside_bytes": actual, "stream_identity": str(low.get("stream_value")),
        "policy_enabled": actual > 0, **window_fields,
        "reset_before": {"status": "PASS", "executed": True, "operation": reset_before_op},
        "reset_after": {"status": "PASS", "executed": True, "operation": reset_after_op},
        "source_provenance": sources,
        "raw_policy_receipt_sha256": _canonical_sha(low),
        "normalized_field_sources": {
            "capability": "capability", "qweight_region": "carrier" if target_mode else None,
            "policy_receipt": "carrier", "semantic_condition": "carrier",
        },
        "runtime_setaside_rounding_observed": actual > requested,
        "rounding_interpretation": (
            "RUNTIME_SETASIDE_ROUNDING_OBSERVED_NO_GENERAL_ALIGNMENT_THEOREM"
            if actual > requested else "REQUEST_EQUALS_RUNTIME_QUERY_BACK"
        ),
    }
    if rich_qweight is not None:
        rich["qweight"] = rich_qweight
    try:
        validated = validate_policy_receipt(
            rich, expected_condition=expected, expected_target=target,
            expected_budget_bytes=expected_budget_bytes,
        )
    except PolicyReceiptError as exc:
        raise PolicyNormalizationError(f"normalized receipt validation failed: {exc}") from exc
    rich["normalization_validation"] = {
        "status": "PASS", "policy_mode": validated["policy_mode"],
        "runtime_setaside_rounding_observed": validated["runtime_setaside_rounding_observed"],
    }
    return rich
