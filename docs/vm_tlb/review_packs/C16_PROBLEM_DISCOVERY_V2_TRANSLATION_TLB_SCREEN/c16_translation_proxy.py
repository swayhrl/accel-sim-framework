#!/usr/bin/env python3
"""Read existing C16WARP1 shards as virtual-page proxies (CPU only)."""

import argparse
import bisect
import csv
import hashlib
import json
import math
import statistics
import struct
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<IIIIII32Q")
ROOT = Path("/root/share/mnt164/huangrulin/c16_ai_workload/raw")
RUNS = {
    "Q30": ("C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678", "raw_shards"),
    "DEEPSEEK": ("C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23", "raw_shards"),
    "OLMOE": ("C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf", "shards"),
    "QWEN25_AWQ": ("C16R_qwen25-7b-awq_s2-text_decode_nvbit-warp-mref-shard_q7awq-decode-fused-gemm_20260915T192000Z_c81c8c3c3d3e", "raw_shards"),
}


def pct(values, p):
    if not values:
        return "UNKNOWN"
    seq = sorted(values)
    return seq[math.ceil(p * len(seq)) - 1]


def mean(values):
    return round(statistics.fmean(values), 6) if values else "UNKNOWN"


def ratio(a, b):
    return round(a / b, 6) if b else "UNKNOWN"


def context_ranges(path):
    doc = json.loads(path.read_text())
    raw = doc.get("ranges")
    if raw is None:
        raw = [dict(v, semantic_role=k) for k, v in doc.items() if isinstance(v, dict) and "ptr" in v]
    result = []
    for item in raw:
        start = item.get("ptr", item.get("address_start_hex"))
        size = item.get("bytes", item.get("storage_bytes"))
        if start is None or size is None:
            continue
        role = str(item.get("semantic_role", item.get("class", item.get("runtime_name", "UNKNOWN")))).upper()
        begin = int(start, 16) if isinstance(start, str) else int(start)
        result.append((begin, begin + int(size), role))
    result.sort()
    return result


def object_class(address, starts, ranges):
    i = bisect.bisect_right(starts, address) - 1
    if i < 0 or address >= ranges[i][1]:
        return "UNMAPPED"
    role = ranges[i][2]
    return "WEIGHT" if "WEIGHT" in role else "OTHER"


def summarize(path, page_bytes, include_unmapped=False):
    context = path.with_suffix(".ADDRESS_CONTEXT.json")
    if not context.exists():
        context = path.parent / "ADDRESS_CONTEXT.json"
    ranges = context_ranges(context)
    starts = [r[0] for r in ranges]
    blob = path.read_bytes()
    if len(blob) < HEADER.size:
        raise ValueError(f"short header: {path}")
    magic, static, occurrence, producer, zero, count = HEADER.unpack_from(blob)
    if magic != b"C16WARP1" or zero != 0 or producer != count:
        raise ValueError(f"header mismatch: {path}")
    if len(blob) != HEADER.size + RECORD.size * count:
        raise ValueError(f"size mismatch: {path}")
    pages = Counter()
    lines = Counter()
    regions = Counter()
    page_warp_touches = Counter()
    line_warp_touches = Counter()
    page_warps = defaultdict(set)
    last_record = {}
    distances = []
    unique_warp_pages = []
    transitions = 0
    comparable = 0
    prev_page = None
    first_touch_run = 0
    first_touch_runs = []
    last_first_page = None
    same_page_warps = 0
    same_page_lanes = 0
    analyzed_warps = 0
    analyzed_refs = 0
    mapped_weight_refs = 0
    other_refs = 0
    unmapped_refs = 0
    curves = []
    seen_pages = set()
    for rec_index, values in enumerate(RECORD.iter_unpack(blob[HEADER.size:])):
        idx, mask, cta_x, cta_y, cta_z, warp = values[:6]
        if idx != static:
            raise ValueError(f"static index mismatch: {path}")
        warp_key = (cta_x, cta_y, cta_z, warp)
        wp = set()
        wl = set()
        warp_page_counts = Counter()
        for lane, address in enumerate(values[6:]):
            if not (mask & (1 << lane)) or address == 0:
                continue
            cls = object_class(address, starts, ranges)
            if cls == "OTHER":
                other_refs += 1
                continue
            if cls == "UNMAPPED":
                unmapped_refs += 1
                if not include_unmapped:
                    continue
            if cls == "WEIGHT":
                mapped_weight_refs += 1
            analyzed_refs += 1
            page = address // page_bytes
            wp.add(page)
            warp_page_counts[page] += 1
            wl.add(address // 128)
            pages[page] += 1
            lines[address // 128] += 1
            regions[address // (2 * 1024 * 1024)] += 1
            page_warps[page].add(warp_key)
            if prev_page is not None:
                comparable += 1
                transitions += page != prev_page
            prev_page = page
            if page not in seen_pages:
                seen_pages.add(page)
                if last_first_page is not None and page == last_first_page + 1:
                    first_touch_run += 1
                else:
                    if first_touch_run:
                        first_touch_runs.append(first_touch_run)
                    first_touch_run = 1
                last_first_page = page
        if wp:
            analyzed_warps += 1
            page_warp_touches.update(wp)
            line_warp_touches.update(wl)
            unique_warp_pages.append(len(wp))
            same_page_warps += len(wp) == 1
            same_page_lanes += max(warp_page_counts.values())
            for page in wp:
                if page in last_record:
                    distances.append(rec_index - last_record[page])
                last_record[page] = rec_index
        if (rec_index + 1) * 4 >= count and len(curves) == 0:
            curves.append((25, len(seen_pages), rec_index + 1))
        if (rec_index + 1) * 2 >= count and len(curves) == 1:
            curves.append((50, len(seen_pages), rec_index + 1))
        if (rec_index + 1) * 4 >= count * 3 and len(curves) == 2:
            curves.append((75, len(seen_pages), rec_index + 1))
    if first_touch_run:
        first_touch_runs.append(first_touch_run)
    curves.append((100, len(seen_pages), count))
    shared_refs = sum(n for p, n in pages.items() if len(page_warps[p]) > 1)
    result = {
        "static_index": static,
        "occurrence": occurrence,
        "warp_records": count,
        "analyzed_warp_records": analyzed_warps,
        "analyzed_lane_refs": analyzed_refs,
        "mapped_weight_lane_refs": mapped_weight_refs,
        "other_lane_refs": other_refs,
        "unmapped_lane_refs": unmapped_refs,
        "unique_pages": len(pages),
        "page_id_min": min(pages) if pages else "UNKNOWN",
        "page_id_max": max(pages) if pages else "UNKNOWN",
        "page_id_set_sha256": hashlib.sha256("\n".join(str(p) for p in sorted(pages)).encode()).hexdigest() if pages else "UNKNOWN",
        "refs_per_page": ratio(analyzed_refs, len(pages)),
        "unique_128b_lines": len(lines),
        "refs_per_128b_line": ratio(analyzed_refs, len(lines)),
        "warp_touches_per_128b_line": ratio(sum(line_warp_touches.values()), len(lines)),
        "warp_touches_per_page": ratio(sum(page_warp_touches.values()), len(pages)),
        "unique_2mb_regions": len(regions),
        "unique_pages_per_warp_mean": mean(unique_warp_pages),
        "unique_pages_per_warp_p95": pct(unique_warp_pages, .95),
        "lane_ref_page_transition_rate": ratio(transitions, comparable),
        "sequential_first_touch_run_mean": mean(first_touch_runs),
        "sequential_first_touch_run_max": max(first_touch_runs) if first_touch_runs else "UNKNOWN",
        "same_page_lane_fraction": ratio(same_page_lanes, analyzed_refs),
        "single_page_warp_fraction": ratio(same_page_warps, analyzed_warps),
        "cross_warp_shared_page_ref_fraction": ratio(shared_refs, analyzed_refs),
        "page_reuse_distance_records_median": pct(distances, .5),
        "page_reuse_distance_records_p95": pct(distances, .95),
        "trace_sha256": hashlib.sha256(blob).hexdigest(),
        "context_sha256": hashlib.sha256(context.read_bytes()).hexdigest(),
    }
    return result, curves


def write_tsv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def self_test():
    assert HEADER.size == 40 and RECORD.size == 280
    assert pct([3, 1, 2], .5) == 2
    assert ratio(1, 16) == .0625
    ranges = [(0x1000, 0x2000, "WEIGHT"), (0x3000, 0x4000, "INPUT")]
    starts = [r[0] for r in ranges]
    assert object_class(0x1001, starts, ranges) == "WEIGHT"
    assert object_class(0x3001, starts, ranges) == "OTHER"
    assert object_class(0x2001, starts, ranges) == "UNMAPPED"
    with tempfile.TemporaryDirectory(prefix="c16_page_proxy_test_") as temporary:
        path = Path(temporary) / "mref_7.bin"
        context = path.with_suffix(".ADDRESS_CONTEXT.json")
        context.write_text(json.dumps({"weight": {"ptr": "0x1000", "bytes": 8192}}))
        first = RECORD.pack(7, 3, 0, 0, 0, 0, 0x1000, 0x1008, *([0] * 30))
        second = RECORD.pack(7, 3, 0, 0, 0, 1, 0x1000, 0x2000, *([0] * 30))
        path.write_bytes(HEADER.pack(b"C16WARP1", 7, 0, 2, 0, 2) + first + second)
        small, curve = summarize(path, 4096)
        large, _ = summarize(path, 65536)
        assert small["unique_pages"] == 2 and small["analyzed_lane_refs"] == 4
        assert small["same_page_lane_fraction"] == .75
        assert small["single_page_warp_fraction"] == .5
        assert small["cross_warp_shared_page_ref_fraction"] == .75
        assert large["unique_pages"] == 1 and curve[-1][1] == 2
        path.write_bytes(path.read_bytes()[:-1])
        try:
            summarize(path, 4096)
        except ValueError as exc:
            assert "size mismatch" in str(exc)
        else:
            raise AssertionError("truncated record accepted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    self_test()
    args.output.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    curve_rows = []
    selection_rows = []
    for model, (run, rel) in RUNS.items():
        folder = ROOT / run / rel
        if not folder.is_dir():
            raise FileNotFoundError(folder)
        candidates = sorted(folder.rglob("*.bin"))
        if not candidates:
            raise ValueError(f"no existing shards: {folder}")
        scored = []
        for candidate in candidates:
            result, _ = summarize(candidate, 4096)
            scored.append((result["mapped_weight_lane_refs"], str(candidate), candidate, result))
        scored.sort(key=lambda item: (-item[0], item[1]))
        fallback = scored[0][0] == 0
        if fallback:
            scored.sort(key=lambda item: (-item[3]["unmapped_lane_refs"], item[1]))
        _, _, path, selected = scored[0]
        selection_rows.append({"model": model, "selection_rule": "MAX_UNMAPPED_LANE_REFS_TIE_LEXICAL" if fallback else "MAX_MAPPED_WEIGHT_LANE_REFS_TIE_LEXICAL",
                               "candidate_shards": len(candidates),
                               "shards_with_weight_refs": sum(item[0] > 0 for item in scored),
                               "all_shards_other_lane_refs": sum(item[3]["other_lane_refs"] for item in scored),
                               "all_shards_unmapped_lane_refs": sum(item[3]["unmapped_lane_refs"] for item in scored),
                               "selected_source": str(path),
                               "selected_weight_lane_refs": selected["mapped_weight_lane_refs"],
                               "selected_other_lane_refs": selected["other_lane_refs"],
                               "selected_unmapped_lane_refs": selected["unmapped_lane_refs"],
                               "selected_trace_sha256": selected["trace_sha256"]})
        for size in (4096, 65536, 2097152):
            result, curves = summarize(path, size, include_unmapped=fallback)
            status = "UNMAPPED_OBJECT_VA_PROXY" if fallback and result["analyzed_lane_refs"] else "MAPPED_WEIGHT_VA_PROXY" if result["mapped_weight_lane_refs"] else "NO_USABLE_REFS"
            if status == "NO_USABLE_REFS":
                for field in ("unique_pages", "unique_128b_lines", "unique_2mb_regions"):
                    result[field] = "UNKNOWN"
            summary_rows.append({"model": model, "scope": "SINGLE_STATIC_MREF_SHARD", "measurement_status": status, "page_bytes": size,
                                 "source": str(path), **result})
            for percent, unique_pages, observed in curves:
                curve_rows.append({"model": model, "scope": "SINGLE_STATIC_MREF_SHARD",
                                   "page_bytes": size, "trace_progress_pct": percent,
                                   "warp_records_observed": observed, "cumulative_unique_pages": unique_pages if status != "NO_USABLE_REFS" else "UNKNOWN",
                                   "source": str(path)})
    write_tsv(args.output / "C16_VIRTUAL_PAGE_PROXY.tsv", summary_rows)
    write_tsv(args.output / "PAGE_WORKING_SET_CURVES.tsv", curve_rows)
    write_tsv(args.output / "SOURCE_SHARD_SELECTION.tsv", selection_rows)
    print("PASS: C16WARP1 headers, sizes, static indices, contexts; 4 runs x 3 page sizes")


if __name__ == "__main__":
    main()
