#!/usr/bin/env python3
"""Freeze the seven-run full FFN census authority before coverage experiments."""

import json
from pathlib import Path


ROOT = Path("/data/c16/e1_coverage_scaling_v1")


def identity(run):
    return [(row["layer"], row["role"], row["decode_index"], row["input_sha256"], row["output_sha256"]) for row in run["occurrences"]]


def geometry(run):
    rows = []
    for row in run["module_census"]:
        rows.append((row["layer"], row["role"], row["module_class"], row["supported_qweight_family"], row.get("dtype"), tuple(row.get("shape", [])), row.get("bytes"), row.get("storage_offset_bytes"), row.get("contiguous")))
    return rows


def main():
    paths = sorted((ROOT / "census/native").glob("run[0-6].json"))
    if len(paths) != 7:
        raise RuntimeError("census requires seven fresh runs")
    runs = [json.loads(path.read_text()) for path in paths]
    base_identity, base_geometry = identity(runs[0]), geometry(runs[0])
    if not all(run["generated_token_ids_D0_D3"] == [23578, 11, 323, 3950] for run in runs):
        raise RuntimeError("census token drift")
    if not all(identity(run) == base_identity for run in runs):
        raise RuntimeError("census occurrence drift")
    if not all(geometry(run) == base_geometry for run in runs):
        raise RuntimeError("census geometry drift")
    if len(base_geometry) != 84 or any(not row[3] for row in base_geometry):
        raise RuntimeError("not all 84 FFN projections are qweight-backed")
    result = {
        "status": "PASS",
        "fresh_process_runs": 7,
        "generated_token_ids_D0_D3": [23578, 11, 323, 3950],
        "all_occurrence_sha_sequences_identical": True,
        "all_module_geometry_identical": True,
        "module_census": runs[0]["module_census"],
        "occurrence_bindings": [{key: row[key] for key in ("layer", "role", "decode_index", "token_id", "range", "input_sha256", "output_sha256", "input_shape", "output_shape", "module_class")} for row in runs[0]["occurrences"]],
    }
    (ROOT / "contracts/CENSUS_AUTHORITY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "modules": len(base_geometry), "occurrences": len(base_identity)}, sort_keys=True))


if __name__ == "__main__":
    main()
