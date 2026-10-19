"""PREPARED_NOT_TESTED. Normalize trusted, qualified final records only.

This is not a raw-log parser, identity validator, simulator or dispatcher.
Coordinator must admit this exact file/role before any execution. Input may only
be a normalized final-complete qualified record, never an active AG4 artifact.
"""
import argparse
import json
import re
from fractions import Fraction
from pathlib import Path

UNAVAILABLE = "UNAVAILABLE"


def _uint(data, name):
    value = data.get(name)
    if value is None or value == UNAVAILABLE:
        return None
    if type(value) is not int or value < 0:
        raise ValueError("expected nonnegative integer: " + name)
    return value


def _mean(total, count):
    if total is None or count is None:
        return UNAVAILABLE
    if not count:
        return "UNDEFINED_ZERO_DENOMINATOR"
    value = Fraction(total, count)
    return {"numerator": value.numerator, "denominator": value.denominator}


def summarize(record):
    if record.get("qualified_terminal") is not True:
        raise ValueError("qualified terminal receipt required")
    if record.get("snapshot") != "LAST_COMPLETE_CUMULATIVE_ALL_64_SMS":
        raise ValueError("single final complete cumulative snapshot required")
    bindings = record.get("bindings", {})
    for key, size in (("source_commit", 40), ("stdout_sha256", 64),
                      ("qualification_receipt_sha256", 64)):
        if not re.fullmatch(r"[0-9a-f]{" + str(size) + "}", bindings.get(key, "")):
            raise ValueError("immutable binding required: " + key)
    mode = record.get("ad_enabled")
    if type(mode) is not bool:
        raise ValueError("explicit AD mode required")
    service = record.get("service", {})
    retired = _uint(service, "retired")
    result = {"status": "DESCRIPTIVE_ONLY_NOT_SCIENTIFIC_QUALIFICATION",
              "bindings": bindings, "ad_enabled": mode, "means": {}}
    for name in ("fully_ready_to_complete_sum", "ready_to_collect_sum",
                 "collection_cycles", "wb_wait"):
        result["means"][name] = _mean(_uint(service, name), retired)
    pieces = [_uint(service, name) for name in
              ("fully_ready_to_complete_sum", "ready_to_collect_sum",
               "collection_cycles", "wb_wait")]
    if all(value is not None for value in pieces):
        if pieces[0] != sum(pieces[1:]):
            raise ValueError("service interval conservation failed")
    # OFF absence stays unavailable; no default0 or causal mean subtraction.
    result["admitted_returns_to_retire_mean"] = UNAVAILABLE
    result["notification_span_mean"] = UNAVAILABLE
    result["fanout_histogram"] = UNAVAILABLE
    if mode:
        ad = record.get("ad", {})
        broadcasts = _uint(ad, "broadcasts")
        span = _uint(ad, "span_sum")
        result["notification_span_mean"] = _mean(span, broadcasts)
        common_retired = _uint(ad, "retired")
        if retired is not None and common_retired is not None and retired != common_retired:
            raise ValueError("AD and service retired populations disagree")
        result["admitted_returns_to_retire_mean"] = _mean(
            _uint(ad, "admitted_returns_to_retire_sum"), common_retired)
        first = _uint(ad, "first_notify_cycle_sum")
        last = _uint(ad, "last_notify_cycle_sum")
        # uint64 sums can overflow in the source; reject ambiguous wrap.
        if first is not None and last is not None and span is not None:
            if last < first or last - first != span:
                raise ValueError("notification spans inconsistent or overflowed")
        bins = ad.get("fanout_histogram")
        if bins is not None:
            if (type(bins) is not list or len(bins) != 33 or
                    any(type(n) is not int or n < 0 for n in bins)):
                raise ValueError("33 nonnegative integer fanout bins required")
            if broadcasts is None or sum(bins) != broadcasts:
                raise ValueError("fanout population does not equal broadcasts")
            result["fanout_histogram"] = {"counts": bins, "last_bin": ">=32"}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("normalized_qualified_final_json", type=Path)
    args = parser.parse_args()
    if args.normalized_qualified_final_json.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("expected small normalized final record, not raw log")
    record = json.loads(args.normalized_qualified_final_json.read_text())
    print(json.dumps(summarize(record), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
