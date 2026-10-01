"""Independent raw Graph ON/OFF token comparison; excludes failed points."""
from __future__ import annotations

import json
from pathlib import Path


def _measured_rows(raw: dict) -> list[list[dict]]:
    samples = raw.get("samples")
    if not isinstance(samples, list):
        raise ValueError("missing raw measured requests")
    if len(samples) == 3 and isinstance(raw.get("warmup_excluded"), dict):
        measured = samples
    elif len(samples) == 4 and raw.get("warmup_excluded") in (None, False):
        measured = samples[1:]
    else:
        raise ValueError(f"warmup/measured raw schema mismatch: {raw.get('point')} {raw.get('arm')} count={len(samples)}")
    out = []
    for sample in measured:
        rows = sample.get("rows")
        if not isinstance(rows, list) or not rows:
            raise ValueError("missing raw per-request response rows")
        ids = [r.get("source_id") for r in rows]
        if any(not x for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("duplicate/missing source ID in raw response")
        out.append(sorted(rows, key=lambda r: r["source_id"]))
    return out


def compare_raw_graph_tokens(graph_on_path: str, graph_off_path: str, point_id: str) -> list[dict]:
    on = json.loads(Path(graph_on_path).read_text(encoding="utf-8"))
    off = json.loads(Path(graph_off_path).read_text(encoding="utf-8"))
    if on.get("point") != point_id or off.get("point") != point_id:
        raise ValueError("raw token point identity mismatch")
    on_rows, off_rows = _measured_rows(on), _measured_rows(off)
    report = []
    for sample_index, (on_group, off_group) in enumerate(zip(on_rows, off_rows)):
        if [r["source_id"] for r in on_group] != [r["source_id"] for r in off_group]:
            raise ValueError("Graph modes use different source roster")
        for a, b in zip(on_group, off_group):
            if a.get("input_file_sha256") != b.get("input_file_sha256") or a.get("input_token_ids_sha256") != b.get("input_token_ids_sha256"):
                raise ValueError("Graph-mode input SHA drift")
            x = a["completion"]["tokens"]
            y = b["completion"]["tokens"]
            if not isinstance(x, list) or not isinstance(y, list):
                raise ValueError("missing raw generated token list")
            first_diff = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), None)
            if first_diff is None and len(x) != len(y):
                first_diff = min(len(x), len(y))
            report.append({
                "point_id": point_id, "sample_index": sample_index,
                "source_id": a["source_id"],
                "graph_on_generated_tokens": len(x), "graph_off_generated_tokens": len(y),
                "first_mismatch_index_or_NA": first_diff if first_diff is not None else "NA",
                "graph_on_token_at_mismatch_or_NA": x[first_diff] if first_diff is not None and first_diff < len(x) else "NA",
                "graph_off_token_at_mismatch_or_NA": y[first_diff] if first_diff is not None and first_diff < len(y) else "NA",
                "status": "MATCH" if first_diff is None else "TOKEN_MISMATCH_STOP_POINT",
            })
    return report
