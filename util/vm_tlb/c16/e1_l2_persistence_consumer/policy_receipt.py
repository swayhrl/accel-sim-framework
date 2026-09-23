#!/usr/bin/env python3
"""Fail-closed validator for CUDA persisting-L2 policy receipts.

The validator intentionally consumes the raw, per-condition receipt rather
than a producer summary.  It normalizes a small set of spelling aliases while
requiring every scientific identity field needed by the frozen intervention
contract.
"""
from __future__ import annotations

import argparse
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class PolicyReceiptError(ValueError):
    """The policy receipt is missing, ambiguous, or violates the contract."""


ACCEPTED_L2_BYTES = 67_108_864
ACCEPTED_MAX_PERSISTING_L2_BYTES = 46_137_344
ACCEPTED_MAX_ACCESS_POLICY_WINDOW_BYTES = 134_213_632

BASELINE_CONDITIONS = frozenset({"BASELINE", "ISO_BASELINE_DENSE"})
SETASIDE_ONLY_CONDITIONS = frozenset({"SETASIDE_ONLY"})
KNOWN_TARGETS = frozenset({"L0_UP", "L14_UP", "L0_DOWN"})
NONE_TARGETS = frozenset({"", "NONE", "DISABLED", "NULL", "N/A"})


def _lookup(document: Mapping[str, Any], *paths: str, required: bool = True) -> Any:
    """Return one unambiguous value from dotted-path aliases."""
    found: list[tuple[str, Any]] = []
    for path in paths:
        value: Any = document
        for part in path.split("."):
            if not isinstance(value, Mapping) or part not in value:
                break
            value = value[part]
        else:
            if value is not None and not (isinstance(value, str) and not value.strip()):
                found.append((path, value))
    if not found:
        if required:
            raise PolicyReceiptError(f"missing required field ({' | '.join(paths)})")
        return None
    reference = _comparison_value(found[0][1])
    for path, value in found[1:]:
        if _comparison_value(value) != reference:
            raise PolicyReceiptError(
                f"conflicting aliases for {paths[0]}: {found[0][0]} vs {path}"
            )
    return found[0][1]


def _comparison_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PolicyReceiptError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise PolicyReceiptError(f"invalid {label}: boolean is not an integer")
    try:
        parsed = int(str(value).strip(), 0)
    except (TypeError, ValueError) as exc:
        raise PolicyReceiptError(f"invalid {label}: {value!r}") from exc
    if str(value).strip().lower() not in {
        str(parsed), hex(parsed).lower(), f"{parsed}.0"
    }:
        raise PolicyReceiptError(f"non-integral {label}: {value!r}")
    if parsed < minimum:
        raise PolicyReceiptError(f"{label} must be >= {minimum}")
    return parsed


def _pointer(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if value is None and allow_zero:
        return 0
    parsed = _integer(value, label, minimum=0)
    if not allow_zero and parsed == 0:
        raise PolicyReceiptError(f"{label} must be a non-null address")
    return parsed


def _float(value: Any, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise PolicyReceiptError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed):
        raise PolicyReceiptError(f"nonfinite {label}: {value!r}")
    return parsed


def _boolean(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        token = value.strip().lower()
        if token in {"true", "yes", "1", "enabled", "pass"}:
            return True
        if token in {"false", "no", "0", "disabled"}:
            return False
    raise PolicyReceiptError(f"invalid {label}: expected explicit boolean")


def _target(value: Any, label: str) -> str:
    token = str(value).strip().upper()
    aliases = {
        "LAYER0_UP_PROJ": "L0_UP",
        "LAYER14_UP_PROJ": "L14_UP",
        "LAYER0_DOWN_PROJ": "L0_DOWN",
        "L0_UP_PROJ": "L0_UP",
        "L14_UP_PROJ": "L14_UP",
        "L0_DOWN_PROJ": "L0_DOWN",
    }
    token = aliases.get(token, token)
    if token not in KNOWN_TARGETS and token not in NONE_TARGETS:
        raise PolicyReceiptError(f"invalid {label}: {value!r}")
    return "NONE" if token in NONE_TARGETS else token


def _property(value: Any, label: str) -> str:
    token = _text(value, label).lower().replace("_", "")
    if "persisting" in token:
        return "PERSISTING"
    if "streaming" in token:
        return "STREAMING"
    if "normal" in token:
        return "NORMAL"
    if token in {"none", "disabled", "null"}:
        return "NONE"
    raise PolicyReceiptError(f"unknown {label}: {value!r}")


def _validate_reset(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PolicyReceiptError(f"{label} must be a receipt object")
    status = _text(_lookup(value, "status"), f"{label}.status").upper()
    if status != "PASS":
        raise PolicyReceiptError(f"{label} status is not PASS")
    executed_raw = _lookup(value, "executed", "performed", required=False)
    if executed_raw is not None and not _boolean(executed_raw, f"{label}.executed"):
        raise PolicyReceiptError(f"{label} was not executed")
    operation = _text(
        _lookup(value, "operation", "api", "name"), f"{label}.operation"
    )
    compact = operation.lower().replace("_", "").replace("-", "")
    if "reset" not in compact or "persist" not in compact:
        raise PolicyReceiptError(f"{label} is not a persisting-L2 reset operation")
    return {"status": "PASS", "executed": True, "operation": operation}


def _policy_mode(condition: str) -> str:
    if condition in BASELINE_CONDITIONS:
        return "BASELINE"
    if condition in SETASIDE_ONLY_CONDITIONS:
        return "SETASIDE_ONLY"
    if condition.startswith("PERSIST_") or condition == "ISO_QWEIGHT_PERSIST_DENSE":
        return "TARGET_PERSIST"
    raise PolicyReceiptError(f"wrong or unsupported condition label: {condition!r}")


def validate_policy_receipt(
    receipt: Mapping[str, Any],
    expected_condition: str,
    expected_target: str | None = None,
    expected_budget_bytes: int | None = None,
) -> dict[str, Any]:
    """Validate and normalize one raw CUDA persistence policy receipt.

    ``expected_target`` uses ``L0_UP``, ``L14_UP``, or ``L0_DOWN``.  It may be
    omitted for BASELINE and SETASIDE_ONLY.  For a partial-budget target point,
    ``expected_budget_bytes`` is the tested set-aside; the exact full-qweight
    window is retained and the required hit ratio is ``min(1, budget/qbytes)``.
    """
    if not isinstance(receipt, Mapping):
        raise PolicyReceiptError("policy receipt must be an object")
    condition_expected = _text(expected_condition, "expected_condition").upper()
    mode = _policy_mode(condition_expected)
    condition = _text(_lookup(receipt, "condition", "policy.condition"), "condition").upper()
    if condition != condition_expected:
        raise PolicyReceiptError(
            f"wrong condition label: expected {condition_expected}, got {condition}"
        )
    status = _text(_lookup(receipt, "status"), "status").upper()
    if status != "PASS":
        raise PolicyReceiptError("policy receipt status is not PASS")

    runtime_version = _text(
        _lookup(receipt, "cuda_runtime_version", "capability.cuda_runtime_version"),
        "cuda_runtime_version",
    )
    device_ordinal = _integer(
        _lookup(receipt, "device_ordinal", "capability.device_ordinal"),
        "device_ordinal",
    )
    device_name = _text(
        _lookup(receipt, "device_name", "capability.device_name"), "device_name"
    )
    if "RTX 4080" not in device_name.upper():
        raise PolicyReceiptError(f"unexpected device identity: {device_name!r}")
    supported = _boolean(
        _lookup(
            receipt,
            "persistence_supported",
            "persisting_l2_supported",
            "capability.persistence_supported",
            "capability.persisting_l2_supported",
        ),
        "persistence_supported",
    )
    if not supported:
        raise PolicyReceiptError("CUDA persisting-L2 capability is not supported")
    l2_bytes = _integer(
        _lookup(receipt, "l2_bytes", "capability.l2_bytes"), "l2_bytes", minimum=1
    )
    max_persist = _integer(
        _lookup(
            receipt,
            "max_persisting_l2_bytes",
            "max_persisting_l2_setaside_bytes",
            "capability.max_persisting_l2_bytes",
            "capability.max_persisting_l2_setaside_bytes",
        ),
        "max_persisting_l2_bytes",
        minimum=1,
    )
    max_window = _integer(
        _lookup(
            receipt,
            "max_access_policy_window_bytes",
            "capability.max_access_policy_window_bytes",
        ),
        "max_access_policy_window_bytes",
        minimum=1,
    )
    expected_capability = (
        ACCEPTED_L2_BYTES,
        ACCEPTED_MAX_PERSISTING_L2_BYTES,
        ACCEPTED_MAX_ACCESS_POLICY_WINDOW_BYTES,
    )
    if (l2_bytes, max_persist, max_window) != expected_capability:
        raise PolicyReceiptError(
            "runtime/device capability does not match accepted RTX4080 authority"
        )

    receipt_target_raw = _lookup(
        receipt, "target", "target_identity", "qweight.target", required=False
    )
    receipt_target = _target(receipt_target_raw or "NONE", "target")
    normalized_expected_target = (
        _target(expected_target, "expected_target") if expected_target is not None else None
    )
    if normalized_expected_target == "NONE":
        normalized_expected_target = None
    if mode == "TARGET_PERSIST":
        if normalized_expected_target is None:
            raise PolicyReceiptError("target-persist condition requires expected_target")
        if receipt_target != normalized_expected_target:
            raise PolicyReceiptError(
                f"target mismatch: expected {normalized_expected_target}, got {receipt_target}"
            )
    elif normalized_expected_target is not None and receipt_target not in {
        normalized_expected_target, "NONE"
    }:
        raise PolicyReceiptError("non-persist condition qweight identity mismatch")
    elif normalized_expected_target is None and receipt_target != "NONE":
        raise PolicyReceiptError("non-target condition ambiguously names a target region")

    qweight_pointer = _pointer(
        _lookup(
            receipt,
            "qweight_pointer",
            "target_qweight_pointer",
            "qweight.pointer",
            "qweight.data_ptr",
        ),
        "qweight_pointer",
    )
    qweight_bytes = _integer(
        _lookup(
            receipt,
            "qweight_bytes",
            "target_qweight_bytes",
            "qweight.bytes",
            "qweight.nbytes",
        ),
        "qweight_bytes",
        minimum=1,
    )
    contiguous = _boolean(
        _lookup(
            receipt,
            "qweight_contiguous",
            "target_qweight_contiguous",
            "qweight.contiguous",
            "qweight.is_contiguous",
        ),
        "qweight_contiguous",
    )
    if not contiguous:
        raise PolicyReceiptError("target qweight is not one exact contiguous interval")
    if qweight_bytes > max_window:
        raise PolicyReceiptError("target qweight exceeds maximum access-policy window")

    requested = _integer(
        _lookup(
            receipt,
            "requested_setaside_bytes",
            "setaside.requested_bytes",
            "setaside.requested_setaside_bytes",
        ),
        "requested_setaside_bytes",
    )
    actual = _integer(
        _lookup(
            receipt,
            "actual_setaside_bytes",
            "query_back_setaside_bytes",
            "setaside.actual_bytes",
            "setaside.query_back_bytes",
        ),
        "actual_setaside_bytes",
    )
    if requested > max_persist or actual > max_persist:
        raise PolicyReceiptError("set-aside exceeds runtime-reported maximum")
    alignment_raw = _lookup(
        receipt,
        "setaside_alignment_bytes",
        "setaside.alignment_bytes",
        required=False,
    )
    alignment = _integer(alignment_raw, "setaside_alignment_bytes", minimum=1) if alignment_raw is not None else 1
    rounded = ((requested + alignment - 1) // alignment) * alignment
    if actual != rounded:
        raise PolicyReceiptError(
            "actual set-aside is neither the requested value nor its declared alignment rounding"
        )
    if expected_budget_bytes is not None:
        expected_budget = _integer(expected_budget_bytes, "expected_budget_bytes")
        if requested != expected_budget:
            raise PolicyReceiptError(
                f"requested set-aside mismatch: expected {expected_budget}, got {requested}"
            )
    else:
        expected_budget = None
        if mode == "SETASIDE_ONLY":
            raise PolicyReceiptError(
                "SETASIDE_ONLY requires expected_budget_bytes to prove the matched budget"
            )
        if mode == "TARGET_PERSIST" and requested != qweight_bytes:
            raise PolicyReceiptError(
                "partial-budget target receipt requires explicit expected_budget_bytes"
            )

    stream_identity = str(
        _lookup(receipt, "stream_identity", "stream.id", "access_window.stream_identity")
    ).strip()
    if not stream_identity:
        raise PolicyReceiptError("missing stream identity")
    window_stream_raw = _lookup(
        receipt, "access_window_stream_identity", required=False
    )
    if window_stream_raw is not None and str(window_stream_raw).strip() != stream_identity:
        raise PolicyReceiptError("access-policy window is attached to a different stream")
    window_enabled = _boolean(
        _lookup(receipt, "access_window_enabled", "access_window.enabled"),
        "access_window_enabled",
    )
    base_pointer = _pointer(
        _lookup(
            receipt,
            "access_window_base_pointer",
            "access_policy_base_pointer",
            "access_window.base_pointer",
            "access_window.base_ptr",
        ),
        "access_window_base_pointer",
        allow_zero=True,
    )
    window_bytes = _integer(
        _lookup(
            receipt,
            "access_window_num_bytes",
            "access_policy_num_bytes",
            "access_window.num_bytes",
            "access_window.bytes",
        ),
        "access_window_num_bytes",
    )
    if window_bytes > max_window:
        raise PolicyReceiptError("access-policy window exceeds runtime-reported maximum")
    hit_ratio = _float(
        _lookup(receipt, "hit_ratio", "hitRatio", "access_window.hit_ratio", "access_window.hitRatio"),
        "hit_ratio",
    )
    if not 0.0 <= hit_ratio <= 1.0:
        raise PolicyReceiptError("hit_ratio must be within [0,1]")
    hit_prop = _property(
        _lookup(receipt, "hit_prop", "hitProp", "access_window.hit_prop", "access_window.hitProp"),
        "hit_prop",
    )
    miss_prop = _property(
        _lookup(receipt, "miss_prop", "missProp", "access_window.miss_prop", "access_window.missProp"),
        "miss_prop",
    )
    policy_enabled = _boolean(
        _lookup(receipt, "policy_enabled", "persistence_enabled"), "policy_enabled"
    )
    target_persisting = _boolean(
        _lookup(
            receipt,
            "target_persisting_enabled",
            "target_window_persisting",
            "access_window.target_persisting_enabled",
        ),
        "target_persisting_enabled",
    )

    before = _validate_reset(
        _lookup(receipt, "reset_before", "reset.before"), "reset_before"
    )
    after = _validate_reset(
        _lookup(receipt, "reset_after", "reset.after"), "reset_after"
    )

    if mode == "BASELINE":
        if requested != 0 or actual != 0:
            raise PolicyReceiptError("BASELINE must have zero/disabled set-aside")
        if policy_enabled or target_persisting or window_enabled:
            raise PolicyReceiptError("BASELINE does not prove persistence disabled")
        if base_pointer != 0 or window_bytes != 0 or hit_ratio != 0.0:
            raise PolicyReceiptError("BASELINE must have no access-policy window")
        if hit_prop == "PERSISTING" or miss_prop == "PERSISTING":
            raise PolicyReceiptError("BASELINE property unexpectedly marks data persisting")
    elif mode == "SETASIDE_ONLY":
        if requested == 0 or actual == 0:
            raise PolicyReceiptError("SETASIDE_ONLY requires a nonzero reserved budget")
        if not policy_enabled:
            raise PolicyReceiptError("SETASIDE_ONLY must prove set-aside policy is enabled")
        if target_persisting or window_enabled:
            raise PolicyReceiptError("SETASIDE_ONLY marks a target window persisting")
        if base_pointer != 0 or window_bytes != 0 or hit_ratio != 0.0:
            raise PolicyReceiptError("SETASIDE_ONLY must have no active target window")
        if hit_prop == "PERSISTING" or miss_prop == "PERSISTING":
            raise PolicyReceiptError("SETASIDE_ONLY has a persisting access property")
    else:
        if requested == 0 or actual == 0:
            raise PolicyReceiptError("target-persist condition requires nonzero set-aside")
        if not policy_enabled or not target_persisting or not window_enabled:
            raise PolicyReceiptError("target-persist policy/window is not explicitly enabled")
        if base_pointer != qweight_pointer or window_bytes != qweight_bytes:
            raise PolicyReceiptError("access window is not the exact qweight interval")
        if hit_prop != "PERSISTING":
            raise PolicyReceiptError("target hit property is not persisting")
        if miss_prop not in {"NORMAL", "STREAMING"}:
            raise PolicyReceiptError("target miss property must be normal or streaming")
        required_ratio = min(1.0, requested / qweight_bytes)
        if not math.isclose(hit_ratio, required_ratio, rel_tol=0.0, abs_tol=1e-12):
            raise PolicyReceiptError(
                f"hitRatio mismatch: expected {required_ratio:.17g}, got {hit_ratio:.17g}"
            )

    normalized_target = normalized_expected_target or receipt_target
    return {
        "status": "PASS",
        "authority": "RAW_POLICY_RECEIPT_ONLY",
        "condition": condition,
        "policy_mode": mode,
        "target": normalized_target,
        "cuda_runtime_version": runtime_version,
        "device_ordinal": device_ordinal,
        "device_name": device_name,
        "l2_bytes": l2_bytes,
        "max_persisting_l2_bytes": max_persist,
        "max_access_policy_window_bytes": max_window,
        "qweight_pointer": qweight_pointer,
        "qweight_bytes": qweight_bytes,
        "qweight_contiguous": True,
        "requested_setaside_bytes": requested,
        "actual_setaside_bytes": actual,
        "setaside_alignment_bytes": alignment,
        "access_window_base_pointer": base_pointer,
        "access_window_num_bytes": window_bytes,
        "hit_ratio": hit_ratio,
        "hit_prop": hit_prop,
        "miss_prop": miss_prop,
        "stream_identity": stream_identity,
        "capability": {
            "cuda_runtime_version": runtime_version,
            "device_ordinal": device_ordinal,
            "device_name": device_name,
            "persistence_supported": True,
            "l2_bytes": l2_bytes,
            "max_persisting_l2_bytes": max_persist,
            "max_access_policy_window_bytes": max_window,
            "matches_accepted_authority": True,
        },
        "qweight": {
            "target": normalized_target,
            "pointer": qweight_pointer,
            "bytes": qweight_bytes,
            "contiguous": True,
        },
        "setaside": {
            "requested_bytes": requested,
            "actual_bytes": actual,
            "alignment_bytes": alignment,
        },
        "access_window": {
            "enabled": window_enabled,
            "base_pointer": base_pointer,
            "num_bytes": window_bytes,
            "hit_ratio": hit_ratio,
            "hit_prop": hit_prop,
            "miss_prop": miss_prop,
            "stream_identity": stream_identity,
            "exact_qweight_interval": mode == "TARGET_PERSIST",
        },
        "reset": {"before": before, "after": after},
        "expected_budget_bytes": expected_budget,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--target")
    parser.add_argument("--budget-bytes", type=int)
    args = parser.parse_args(argv)
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    normalized = validate_policy_receipt(
        receipt,
        expected_condition=args.condition,
        expected_target=args.target,
        expected_budget_bytes=args.budget_bytes,
    )
    print(json.dumps(normalized, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
