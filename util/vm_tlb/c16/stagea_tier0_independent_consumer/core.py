"""Independent, CPU-only Tier0 arithmetic. No producer postprocess imports.

Times are integer nanoseconds on one explicitly named host/GPU timeline. The
caller must prove raw CUDA/NVTX correlation; temporal overlap alone is never
used to attach a kernel to a semantic range.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
from hashlib import sha256
from math import isfinite
from pathlib import Path, PurePosixPath
import re
from statistics import median, pstdev
from typing import Iterable


@dataclass(frozen=True, order=True)
class Interval:
    start_ns: int
    end_ns: int
    identity: str

    def __post_init__(self) -> None:
        if not isinstance(self.start_ns, int) or not isinstance(self.end_ns, int):
            raise TypeError("interval timestamps must be integer ns")
        if self.end_ns < self.start_ns:
            raise ValueError("negative interval")
        if not self.identity:
            raise ValueError("missing interval identity")

    @property
    def duration_ns(self) -> int:
        return self.end_ns - self.start_ns


def clipped(interval: Interval, parent: Interval) -> Interval | None:
    start = max(interval.start_ns, parent.start_ns)
    end = min(interval.end_ns, parent.end_ns)
    return Interval(start, end, interval.identity) if end >= start else None


def union_length_ns(intervals: Iterable[Interval], parent: Interval | None = None) -> int:
    """Merge overlaps/touches; zero-length events contribute zero duration."""
    items = []
    for raw in intervals:
        item = clipped(raw, parent) if parent else raw
        if item is not None and item.duration_ns:
            items.append(item)
    items.sort(key=lambda i: (i.start_ns, i.end_ns, i.identity))
    total = 0
    last_start = last_end = None
    for item in items:
        if last_end is None:
            last_start, last_end = item.start_ns, item.end_ns
        elif item.start_ns <= last_end:
            last_end = max(last_end, item.end_ns)
        else:
            total += last_end - last_start
            last_start, last_end = item.start_ns, item.end_ns
    if last_end is not None:
        total += last_end - last_start
    return total


def attach_by_correlation(
    cuda_intervals: Iterable[Interval],
    explicit_correlations: dict[str, str],
    allowed_semantic_ids: set[str],
) -> dict[str, list[Interval]]:
    """Fail closed if *any* interval lacks an explicit semantic attachment."""
    out = {key: [] for key in allowed_semantic_ids}
    for interval in cuda_intervals:
        target = explicit_correlations.get(interval.identity)
        if target is None or target not in allowed_semantic_ids:
            raise ValueError(f"missing/invalid CUDA semantic correlation: {interval.identity}")
        out[target].append(interval)
    return out


def chronological_gaps(intervals: Iterable[Interval], parent: Interval) -> list[dict]:
    """Preserve signed gap: negative is overlap, not a positive launch gap."""
    items = [clipped(i, parent) for i in intervals]
    items = [i for i in items if i is not None and i.duration_ns]
    items.sort(key=lambda i: (i.start_ns, i.end_ns, i.identity))
    rows = []
    prior = None
    for item in items:
        if prior is not None:
            signed = item.start_ns - prior.end_ns
            rows.append({
                "predecessor": prior.identity,
                "successor": item.identity,
                "signed_gap_ns": signed,
                "positive_gap_ns": max(0, signed),
                "overlap_ns": max(0, -signed),
                "gap_start_ns": prior.end_ns if signed > 0 else None,
                "gap_end_ns": item.start_ns if signed > 0 else None,
                "classification": "OVERLAP" if signed < 0 else ("TOUCH" if signed == 0 else "GAP"),
            })
        prior = item if prior is None or item.end_ns >= prior.end_ns else prior
    return rows


def sample_statistics(values: Iterable[float]) -> dict:
    data = list(values)
    if not data or any(not isfinite(v) or v < 0 for v in data):
        raise ValueError("missing, negative or nonfinite timing sample")
    lo, hi = min(data), max(data)
    med = median(data)
    return {
        "sample_count": len(data), "median": med, "min": lo, "max": hi,
        "spread": hi - lo,
        "spread_over_median": (hi - lo) / med if med else None,
        "population_cv": pstdev(data) / (sum(data) / len(data)) if sum(data) else None,
    }


def headroom_gate(candidate_union_ns: int, parent_union_ns: int, *, comparable_whole_run_fraction: float | None = None) -> dict:
    """Graph-OFF screen; never promote its f to Graph-ON whole-run fraction."""
    if parent_union_ns <= 0 or candidate_union_ns < 0 or candidate_union_ns > parent_union_ns:
        raise ValueError("invalid parent/candidate wall union")
    f = candidate_union_ns / parent_union_ns
    zero_speedup = 1 / (1 - f) if f < 1 else None
    stop_local = f < 0.03
    whole_run_incremental = None
    if comparable_whole_run_fraction is None:
        whole_run_status = "WHOLE_RUN_CEILING_NOT_IDENTIFIABLE"
        stop_zero = None
    else:
        if not isfinite(comparable_whole_run_fraction) or not (0 <= comparable_whole_run_fraction < 1):
            raise ValueError("invalid comparable whole-run fraction")
        whole_run_incremental = 1 / (1 - comparable_whole_run_fraction) - 1
        stop_zero = whole_run_incremental < 0.02
        whole_run_status = "BELOW_2PCT" if stop_zero else "AT_OR_ABOVE_2PCT"
    return {
        "f_graph_off": f, "s_zero_graph_off_screen": zero_speedup,
        "whole_run_ceiling_incremental": whole_run_incremental,
        "whole_run_ceiling_status": whole_run_status,
        "below_3pct_local_gate": stop_local,
        "below_2pct_zero_ceiling_gate": stop_zero,
        "status": "STOPPED_BY_HEADROOM" if (stop_local or stop_zero) else "SURVIVES_HEADROOM_SCREEN",
    }


def matched_graph_absorption(off_gap: float, on_gap: float, *, commensurate: bool) -> dict:
    """Only precontract-matched gaps may be compared; no invented denominator."""
    if not commensurate or not all(isfinite(v) for v in (off_gap, on_gap)) or off_gap <= 0 or on_gap < 0:
        return {"status": "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE", "absorption": None}
    absorption = (off_gap - on_gap) / off_gap
    return {"status": "STOP_DIRECTION" if absorption >= 0.85 else "NOT_STOPPED_BY_GRAPH_CONTROL", "absorption": absorption}


def dq2_batch_matched_graph_control(medians: dict[tuple[str, str], float], sample_counts: dict[tuple[str, str], int], *, identity_ok: bool) -> dict:
    """Exact final-contract MP02/MP03 ms/generated-token estimator."""
    keys = {(point, arm) for point in ("MP02", "MP03") for arm in ("ON", "OFF")}
    if not identity_ok or not keys <= medians.keys() or any(sample_counts.get(k) != 3 for k in keys):
        return {"status": "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE", "absorption": None, "G_off_ms_per_token": None, "G_on_ms_per_token": None}
    if any(not isfinite(medians[k]) or medians[k] < 0 for k in keys):
        return {"status": "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE", "absorption": None, "G_off_ms_per_token": None, "G_on_ms_per_token": None}
    off_gap = medians[("MP02", "OFF")] / 32 - medians[("MP03", "OFF")] / 128
    on_gap = medians[("MP02", "ON")] / 32 - medians[("MP03", "ON")] / 128
    result = matched_graph_absorption(off_gap, on_gap, commensurate=True)
    return {**result, "G_off_ms_per_token": off_gap, "G_on_ms_per_token": on_gap}


QUESTION_POINTS = {
    "DQ1": {"MP01", "MP02"},
    "DQ2": {"MP02", "MP03"},
    "DQ3": {"MP01", "MP02", "MP03"},
    "DQ4a": {"MP01", "MP02"},
}
ALLOWLIST = {"MP01", "MP02", "MP03", "MP05"}


def validate_coverage(complete_points: set[str], producer_status: str) -> dict[str, str]:
    if producer_status not in {"STAGEA_TIER0_PRODUCER_COMPLETE", "STAGEA_TIER0_PRODUCER_PARTIAL"}:
        raise ValueError("producer not terminal")
    if not complete_points <= ALLOWLIST:
        raise ValueError("point matrix includes forbidden point")
    return {q: ("READY" if needed <= complete_points else "QUESTION_INCOMPLETE") for q, needed in QUESTION_POINTS.items()}


def audit_raw_file(path: str, expected_size: int, expected_sha256: str, durable_root: str) -> dict:
    """Rehash bytes at a validated 164 mount path; never trust an index digest."""
    root = Path(durable_root).resolve(strict=True)
    target = Path(path).resolve(strict=True)
    if target != root and root not in target.parents:
        raise ValueError("raw path escapes frozen durable root")
    if not target.is_file() or expected_size < 0 or len(expected_sha256) != 64:
        raise ValueError("invalid raw index record")
    size = target.stat().st_size
    digest = sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_sha = digest.hexdigest()
    return {
        "path": str(target), "expected_size": expected_size, "actual_size": size,
        "expected_sha256": expected_sha256.lower(), "actual_sha256": actual_sha,
        "status": "PASS" if size == expected_size and actual_sha == expected_sha256.lower() else "FAIL",
    }


RAW_INDEX_COLUMNS = {"artifact", "node109_path", "bytes", "sha256", "node164_path"}


def audit_raw_index(index_path: str, durable_root: str) -> list[dict]:
    """Read the producer's Git index only as a locator; independently rehash 164."""
    with Path(index_path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if set(reader.fieldnames or []) != RAW_INDEX_COLUMNS:
            raise ValueError("RAW_INDEX schema mismatch")
        rows = list(reader)
    if not rows:
        raise ValueError("empty RAW_INDEX")
    names, paths = set(), set()
    audited = []
    for row in rows:
        name = row["artifact"]
        path = row["node164_path"]
        digest = row["sha256"]
        relative = PurePosixPath(name)
        if (not name or relative.is_absolute() or relative.as_posix() != name or "\\" in name or
                any(part in {"", ".", ".."} for part in relative.parts) or
                name in names or path in paths):
            raise ValueError("duplicate/unsafe RAW_INDEX identity")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ValueError("invalid raw SHA256")
        if Path(path).resolve(strict=True).relative_to(Path(durable_root).resolve(strict=True)).as_posix() != name:
            raise ValueError("artifact/durable relative path mismatch")
        try:
            size = int(row["bytes"])
        except ValueError as exc:
            raise ValueError("noninteger raw byte count") from exc
        audit = audit_raw_file(path, size, digest, durable_root)
        names.add(name)
        paths.add(path)
        audited.append({"artifact": name, "node109_path": row["node109_path"], **audit})
    return audited


@dataclass(frozen=True)
class TimingSample:
    point_id: str
    graph_mode: str
    instrumentation: str
    repetition: int
    duration_ms: float
    input_sha256: str
    output_sha256: str
    batch: int
    effective_m: int
    backend: str
    shape: str


def recompute_timing(samples: Iterable[TimingSample], allowed_points: set[str]) -> list[dict]:
    """Only instrumentation OFF supplies native request timing."""
    buckets: dict[tuple[str, str], list[TimingSample]] = {}
    identities: dict[str, set[tuple[str, str, int, int, str, str]]] = {}
    for sample in samples:
        if sample.point_id not in allowed_points or sample.graph_mode not in {"ON", "OFF"}:
            raise ValueError("timing point/mode outside contract")
        if sample.instrumentation not in {"ON", "OFF"}:
            raise ValueError("missing instrumentation state")
        if sample.repetition < 0 or not isfinite(sample.duration_ms) or sample.duration_ms < 0:
            raise ValueError("invalid timing sample")
        if len(sample.input_sha256) != 64 or len(sample.output_sha256) != 64 or not sample.backend or not sample.shape:
            raise ValueError("incomplete timing identity")
        identities.setdefault(sample.point_id, set()).add((sample.input_sha256, sample.output_sha256, sample.batch, sample.effective_m, sample.backend, sample.shape))
        if sample.instrumentation == "OFF":
            buckets.setdefault((sample.point_id, sample.graph_mode), []).append(sample)
    if any(len(values) != 1 for values in identities.values()):
        raise ValueError("input/output/shape/backend drift within point")
    rows = []
    for (point_id, mode), group in sorted(buckets.items()):
        reps = [x.repetition for x in group]
        if len(set(reps)) != len(reps):
            raise ValueError("duplicate native timing repetition")
        stats = sample_statistics(x.duration_ms for x in group)
        identity = next(iter(identities[point_id]))
        rows.append({
            "point_id": point_id, "graph_mode": mode, **stats,
            "input_sha256": identity[0], "output_sha256": identity[1],
            "batch": identity[2], "effective_m": identity[3],
            "backend": identity[4], "shape": identity[5],
        })
    return rows
