#!/usr/bin/env python3
"""Freeze runtime natural FFN call order and all-84 semantic identity."""

import json
from pathlib import Path


ROOT = Path("/data/c16/e1_operator_family_expansion_v1")


def identity(run):
    return [(row["layer"], row["role"], row["decode_index"], row["input_sha256"], row["output_sha256"]) for row in run["occurrences"]]


def geometry(run):
    return [(row["layer"], row["role"], row["module_class"], row["dtype"], tuple(row["shape"]), row["bytes"], row["storage_offset_bytes"], row["contiguous"]) for row in run["module_census"]]


def main():
    paths = sorted((ROOT / "order/native").glob("run[0-6].json"))
    if len(paths) != 7:
        raise RuntimeError("call-order authority requires seven runs")
    runs = [json.loads(path.read_text()) for path in paths]
    base_order, base_identity, base_geometry = runs[0]["call_order"], identity(runs[0]), geometry(runs[0])
    if not all(run["generated_token_ids_D0_D3"] == [23578, 11, 323, 3950] for run in runs):
        raise RuntimeError("call-order token drift")
    if not all(run["call_order"] == base_order for run in runs):
        raise RuntimeError("natural call-order drift")
    if not all(identity(run) == base_identity for run in runs):
        raise RuntimeError("call-order occurrence drift")
    if not all(geometry(run) == base_geometry for run in runs):
        raise RuntimeError("call-order module geometry drift")
    by_phase = {}
    for phase in ("PREFILL", "D0", "D1", "D2", "D3"):
        rows = [row for row in base_order if row["phase"] == phase]
        if len(rows) != 84 or [row["ordinal"] for row in rows] != list(range(84)):
            raise RuntimeError(f"phase call-order closure {phase}")
        by_phase[phase] = rows
    result = {"status": "PASS", "fresh_process_runs": 7, "generated_token_ids_D0_D3": [23578, 11, 323, 3950], "call_order": base_order, "call_order_by_phase": by_phase, "module_census": runs[0]["module_census"], "occurrence_bindings": [{key: row[key] for key in ("layer", "role", "decode_index", "token_id", "range", "input_sha256", "output_sha256", "input_shape", "output_shape", "module_class")} for row in runs[0]["occurrences"]]}
    (ROOT / "contracts/CALL_ORDER_AUTHORITY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "calls": len(base_order), "occurrences": len(base_identity)}, sort_keys=True))


if __name__ == "__main__":
    main()
