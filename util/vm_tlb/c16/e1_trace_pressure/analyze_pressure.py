#!/usr/bin/env python3
"""Aggregate compact C16 summaries; this tool never opens traceg files."""

from __future__ import annotations

import argparse
import array
import concurrent.futures
import heapq
import hashlib
import json
import math
import multiprocessing
import shutil
import shlex
import statistics
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

CLAIM = "SET_CONFLICT_REFERENCE_PRESSURE_PROXY"
BUDGETS = {"B8": 8 << 20, "B16": 16 << 20, "B24": 24 << 20,
           "BFULL": 33_947_648}
ACCEPTED_MAPPER = {
    "accepted_mapper_schema": "C16_E1_ACCEPTED_L2_MAPPER_V1",
    "accepted_source_mode": "SOURCE_DIRECT_CORE",
    "accepted_core_sha": "a2322069b9701597db7019080b5b54d29518e3a2",
    "accepted_config_sha256": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "accepted_address_namespace": "MODELED_L2_GET_ADDR",
    "accepted_address_transform": "IDENTITY_NUMERIC_NO_ADDRESS_REWRITE",
}

_GAP_KERNELS: list[Kernel] | None = None
_GAP_STATIC: dict | None = None
_GAP_MAPPER: Mapper | None = None
_GAP_TEMP_ROOT: Path | None = None


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def dist(values: Sequence[int | float]) -> dict:
    if not values:
        return {"count": 0, "median": None, "p90": None, "p99": None,
                "max": None}
    ordered = sorted(values)
    rank = lambda q: float(ordered[max(0, math.ceil(q * len(ordered)) - 1)])
    return {"count": len(values), "median": float(statistics.median(values)),
            "p90": rank(.90), "p99": rank(.99), "max": float(ordered[-1])}


def set_distribution(values: Sequence[int]) -> dict:
    result = dist(values)
    mean = statistics.mean(values) if values else 0.0
    result.update({
        "mean": float(mean),
        "coefficient_of_variation": (statistics.pstdev(values) / mean
                                     if values and mean else None),
        "max_over_mean": (max(values) / mean if values and mean else None),
        "zero_set_fraction": (sum(value == 0 for value in values) / len(values)
                              if values else None),
    })
    return result


def resolved(base: Path, name: str | None) -> Path | None:
    if not name:
        return None
    path = Path(name)
    return path if path.is_absolute() else base / path


@dataclass(frozen=True)
class Segment:
    instructions: int
    global_refs: int
    line_refs: int
    non_target_refs: int
    all_lines: Path | None
    non_target_lines: Path | None
    all_set_refs: Path | None
    all_line_ref_pairs: Path | None
    non_target_line_ref_pairs: Path | None


@dataclass(frozen=True)
class Kernel:
    kernel_id: int
    decode: int
    semantic_layer: int | None
    semantic_identity: str
    target_refs: dict[int, int]
    boundaries: dict[int, dict]
    full: Segment
    source: Path


def segment(value: dict, base: Path, prefix: str = "") -> Segment:
    artifacts = value.get("artifacts", {})
    return Segment(int(value.get("dynamic_instructions", 0)),
                   int(value.get("global_address_references", 0)),
                   int(value.get("global_128b_line_references",
                                 value.get("line_references", 0))),
                   int(value.get("non_target_128b_line_references",
                                 value.get("non_target_address_references",
                                           value.get("line_references", 0)))),
                   resolved(base, artifacts.get("all_unique_lines_u64le") or
                            f"{prefix}all_unique_lines.u64"),
                   resolved(base, artifacts.get("non_target_unique_lines_u64le") or
                            f"{prefix}non_target_unique_lines.u64"),
                   resolved(base, artifacts.get("all_set_refs_u64le") or
                            ("all_set_refs.u64" if not prefix else f"{prefix}all_set_refs.u64")),
                   resolved(base, artifacts.get("all_line_refs_u64le") or
                            f"{prefix}all_line_refs.u64"),
                   resolved(base, artifacts.get("non_target_line_refs_u64le") or
                            f"{prefix}non_target_line_refs.u64"))


def load_kernel(path: Path) -> Kernel:
    value = json.loads(path.read_text(encoding="utf-8"))
    need(value.get("schema") in ("C16_E1_TRACE_KERNEL_SUMMARY_V1",
                                 "C16_E1_TRACE_PRESSURE_KERNEL_SUMMARY_V1"),
         f"{path}: unsupported schema")
    if isinstance(value.get("target_refs_by_class"), list):
        refs = {index + 1: int(count) for index, count in
                enumerate(value["target_refs_by_class"]) if count}
    else:
        refs = {int(k): int(v) for k, v in
                value.get("per_target_class_references", {}).items()}
    boundaries = {int(k): v for k, v in value.get("target_boundaries", {}).items()}
    expected = int(value.get("expected_target_class", 0))
    if expected and value.get("expected_target_observed") and expected not in boundaries:
        prefix = dict(value["prefix"]); suffix = dict(value["suffix"])
        prefix.update({"dynamic_instructions": max(
            int(value["first_expected_target_instruction_ordinal"]) - 1, 0),
            "global_address_references": int(prefix["address_references"])})
        suffix.update({"dynamic_instructions": max(
            int(value["dynamic_instructions"]) -
            int(value["last_expected_target_instruction_ordinal"]), 0),
            "global_address_references": int(suffix["address_references"])})
        boundaries[expected] = {"prefix": prefix, "suffix": suffix,
          "referenced_target_unique_lines": int(value.get("target_unique_128b_lines", 0))}
        if "semantic_range_first_dynamic_kernel" in value:
            boundaries[expected]["semantic_range_start_kernel"] = int(
                value["semantic_range_first_dynamic_kernel"])
            boundaries[expected]["semantic_range_end_kernel"] = int(
                value["semantic_range_last_dynamic_kernel"])
    layer = value.get("semantic_layer")
    return Kernel(int(value["kernel_id"]), int(value.get("decode_index",
                  value.get("decode_iteration"))),
                  None if layer in (None, "") else int(layer),
                  str(value.get("semantic_identity", "UNKNOWN")),
                  refs, boundaries,
                  segment(value, path.parent), path)


def load_kernels(root: Path) -> list[Kernel]:
    paths = sorted(root.glob("kernels/*/summary.json")) or sorted(root.glob("kernel-*.json"))
    need(bool(paths), f"no summaries below {root}")
    kernels = sorted(map(load_kernel, paths), key=lambda k: k.kernel_id)
    ids = [k.kernel_id for k in kernels]
    need(ids == list(range(ids[0], ids[-1] + 1)), "kernel ids not contiguous")
    need({k.decode for k in kernels} == {1, 2, 3}, "expected decode indices 1,2,3")
    return kernels


def u64s(path: Path) -> Iterator[int]:
    previous = None
    with path.open("rb") as stream:
        while raw := stream.read(1 << 20):
            need(len(raw) % 8 == 0, f"{path}: truncated u64le")
            for (value,) in struct.iter_unpack("<Q", raw):
                need(previous is None or value > previous,
                     f"{path}: lines are not sorted unique")
                previous = value
                yield value


def merged(paths: Sequence[Path]) -> Iterator[int]:
    previous = None
    for value in heapq.merge(*(u64s(path) for path in paths)):
        if value != previous:
            yield value
            previous = value


def merge_to(path: Path, inputs: Sequence[Path]) -> None:
    values = array.array("Q")
    with path.open("wb") as out:
        for value in merged(inputs):
            values.append(value)
            if len(values) == 131072:
                if sys.byteorder != "little": values.byteswap()
                values.tofile(out)
                values = array.array("Q")
        if values:
            if sys.byteorder != "little": values.byteswap()
            values.tofile(out)


def bounded_merge(paths: Sequence[Path], temporary: Path, fan_in: int = 64) -> tuple[Iterator[int], list[Path]]:
    current, created, generation = list(paths), [], 0
    while len(current) > fan_in:
        following = []
        for offset in range(0, len(current), fan_in):
            target = temporary / f"merge-{generation}-{offset // fan_in}.u64"
            merge_to(target, current[offset:offset + fan_in])
            following.append(target); created.append(target)
        current, generation = following, generation + 1
    return merged(current), created


def histogram(path: Path, bins: int) -> array.array:
    raw = path.read_bytes(); need(len(raw) == bins * 8, f"{path}: bad histogram size")
    result = array.array("Q"); result.frombytes(raw)
    if sys.byteorder != "little": result.byteswap()
    return result


def hist_sum(paths: Sequence[Path], bins: int) -> list[int]:
    total = [0] * bins
    for path in paths:
        for index, value in enumerate(histogram(path, bins)): total[index] += value
    return total


def pair_values(path: Path) -> Iterator[tuple[int, int]]:
    raw = path.read_bytes(); need(len(raw) % 16 == 0, f"{path}: bad pair file")
    previous = None
    for address, count in struct.iter_unpack("<QQ", raw):
        need(previous is None or address > previous, f"{path}: pairs not sorted unique")
        need(address % 128 == 0 and count > 0, f"{path}: invalid pair")
        previous = address
        yield address, count


class Mapper:
    """Consumes accepted mapper output; intentionally contains no address formula."""
    def __init__(self, table: Path | None, command: str | None,
                 authority_json: Path | None):
        need(bool(table) ^ bool(command), "select one mapper")
        self.command = shlex.split(command) if command else None
        self.table = None
        self.authority: dict
        if table:
            need(authority_json is not None and authority_json.is_file(),
                 "--line-mapping-tsv requires --mapper-authority-json")
            authority = json.loads(authority_json.read_text(encoding="utf-8"))
            need(isinstance(authority, dict) and authority,
                 "mapper authority sidecar must be a nonempty JSON object")
            self.authority = {
                "mode": "PRECOMPUTED_TSV_WITH_EXPLICIT_AUTHORITY_SIDECAR",
                "formal_mapper_execution_verified": False,
                "authority_path": str(authority_json.resolve()),
                "authority_sha256": sha256_path(authority_json),
                "authority": authority,
            }
            self.table = {}
            for row in table.read_text(encoding="utf-8").splitlines():
                if not row or row.startswith("#") or row.startswith("line_address"): continue
                fields = row.split("\t"); need(len(fields) >= 3, "bad mapper TSV")
                self.table[int(fields[0], 0)] = (int(fields[1]), int(fields[2]))
        else:
            need(bool(self.command), "empty mapper command")
            executable_text = shutil.which(self.command[0])
            need(executable_text is not None, "mapper executable not found")
            executable = Path(executable_text).resolve()
            need(executable.is_file(), "mapper executable is not a file")
            run = subprocess.run([str(executable), "--provenance"], text=True,
                                 capture_output=True, check=True)
            provenance = {}
            for row in run.stdout.splitlines():
                key, separator, value = row.partition("=")
                need(separator == "=" and key and value,
                     f"malformed mapper provenance row: {row!r}")
                need(key not in provenance, f"duplicate mapper provenance key: {key}")
                provenance[key] = value
            for key, expected in ACCEPTED_MAPPER.items():
                need(provenance.get(key) == expected,
                     f"mapper provenance mismatch for {key}")
            self.command[0] = str(executable)
            self.authority = {
                "mode": "FAIL_CLOSED_ACCEPTED_EXECUTABLE",
                "formal_mapper_execution_verified": True,
                "executable": str(executable),
                "executable_sha256": sha256_path(executable),
                "provenance": provenance,
                "provenance_sha256": sha256_json(provenance),
            }

    def batch(self, addresses: Sequence[int]) -> list[tuple[int, int]]:
        if self.table is not None:
            need(all(a in self.table for a in addresses), "mapper TSV misses an address")
            return [self.table[a] for a in addresses]
        run = subprocess.run(self.command, input="".join(f"{a:#x}\n" for a in addresses),
                             text=True, capture_output=True, check=True)
        found = {}
        for row in run.stdout.splitlines():
            if not row or row.startswith("#") or row.startswith("line_address"): continue
            fields = row.split("\t"); found[int(fields[0], 0)] = (int(fields[1]), int(fields[2]))
        need(len(found) == len(addresses), "mapper command omitted rows")
        return [found[a] for a in addresses]


def map_unique(values: Iterable[int], mapper: Mapper, subparts: int, sets: int) -> tuple[int, list[int]]:
    counts, total, pending = [0] * (subparts * sets), 0, []
    def consume() -> None:
        nonlocal total
        for sp, set_index in mapper.batch(pending):
            need(0 <= sp < subparts and 0 <= set_index < sets, "mapper coordinate out of range")
            counts[sp * sets + set_index] += 1; total += 1
    for value in values:
        pending.append(value)
        if len(pending) == 65536: consume(); pending = []
    if pending: consume()
    return total, counts


def map_pairs(path: Path, mapper: Mapper, subparts: int, sets: int) -> list[int]:
    counts, pending_address, pending_count = [0] * (subparts * sets), [], []
    def consume() -> None:
        for (sp, set_index), count in zip(mapper.batch(pending_address), pending_count):
            need(0 <= sp < subparts and 0 <= set_index < sets, "mapper coordinate out of range")
            counts[sp * sets + set_index] += count
    for address, count in pair_values(path):
        pending_address.append(address); pending_count.append(count)
        if len(pending_address) == 65536:
            consume(); pending_address, pending_count = [], []
    if pending_address: consume()
    return counts


def region_counts(region: dict) -> dict[tuple[int, int], int]:
    value, result = region.get("set_line_counts", {}), {}
    if isinstance(value, dict):
        for key, count in value.items():
            sp, set_index = key.replace(",", ":").split(":")
            result[int(sp), int(set_index)] = int(count)
    else:
        for item in value:
            result[int(item.get("subpartition", item.get("sp"))),
                   int(item.get("set", item.get("set_index")))] = int(item.get("line_count", item.get("count")))
    need(bool(result), f"layer {region.get('layer_index')} has no set counts")
    return result


def mapping_from_sidecar(path: Path, mapper: Mapper) -> dict:
    rows = path.read_text(encoding="utf-8").splitlines()
    need(rows and rows[0].split("\t") ==
         ["ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1", "1", "MODELED_L2_GET_ADDR"],
         "unsupported sidecar header/namespace")
    regions = []
    for row in rows[1:]:
        begin_text, end_text, tensor_name, class_text = row.split("\t")
        begin, end, target_class = int(begin_text, 0), int(end_text, 0), int(class_text)
        need(begin % 128 == 0 and end % 128 == 0 and begin < end,
             "sidecar region is not a nonempty 128B-aligned interval")
        expected = f"model.layers.{target_class - 1}.mlp.up_proj.qweight"
        need(tensor_name == expected, "sidecar target class/name mismatch")
        counts: dict[tuple[int, int], int] = {}
        pending = []
        def consume() -> None:
            for coordinate in mapper.batch(pending): counts[coordinate] = counts.get(coordinate, 0) + 1
        for address in range(begin, end, 128):
            pending.append(address)
            if len(pending) == 65536: consume(); pending = []
        if pending: consume()
        regions.append({"layer_index": target_class - 1, "target_class": target_class,
          "begin": begin, "end_exclusive": end, "tensor_name": tensor_name,
          "bytes": end - begin, "line_count": (end - begin) // 128,
          "set_line_counts": [{"subpartition": sp, "set": set_index, "line_count": count}
                              for (sp, set_index), count in sorted(counts.items())]})
    need(len(regions) == 28, "sidecar must contain 28 regions")
    return {"geometry": {"l2_bytes": 64 << 20, "line_size_bytes": 128,
      "subpartition_count": 16, "sets_per_subpartition": 2048, "associativity": 16},
      "regions": regions}


def static_mapping(value: dict) -> dict:
    geo = value.get("geometry", value)
    geometry = {"l2_bytes": int(geo.get("l2_bytes", 64 << 20)),
                "line_size_bytes": int(geo["line_size_bytes"]),
                "subpartition_count": int(geo["subpartition_count"]),
                "sets_per_subpartition": int(geo["sets_per_subpartition"]),
                "associativity": int(geo["associativity"])}
    need(geometry["line_size_bytes"] == 128, "expected 128B line mapping")
    regions = []
    for source in sorted(value["regions"], key=lambda r: int(r["layer_index"])):
        counts = region_counts(source); per_sp = [0] * geometry["subpartition_count"]
        for (sp, set_index), count in counts.items():
            need(0 <= sp < len(per_sp) and 0 <= set_index < geometry["sets_per_subpartition"], "bad set coordinate")
            per_sp[sp] += count
        total = sum(counts.values())
        identity = {key: source[key] for key in ("begin", "end_exclusive", "tensor_name")
                    if key in source}
        regions.append({**identity, "layer_index": int(source["layer_index"]),
                        "target_class": int(source.get("target_class", int(source["layer_index"]) + 1)),
                        "bytes": int(source.get("bytes", total * 128)), "line_count": total,
                        "subpartition_line_counts": per_sp,
                        "set_line_counts": [{"subpartition": sp, "set": s, "line_count": n}
                                            for (sp, s), n in sorted(counts.items())],
                        "set_distribution": set_distribution(list(counts.values()) + [0] *
                          (len(per_sp) * geometry["sets_per_subpartition"] - len(counts)))})
    need([r["layer_index"] for r in regions] == list(range(28)), "expected layers 0..27")
    overlap = []
    for left_index, left in enumerate(regions):
        for right in regions[left_index + 1:]:
            left_counts = region_counts(left)
            right_counts = region_counts(right)
            a, b = set(left_counts), set(right_counts); both = len(a & b)
            coordinates = ((sp, set_index)
                           for sp in range(geometry["subpartition_count"])
                           for set_index in range(geometry["sets_per_subpartition"]))
            weighted_intersection = 0
            equal_population = 0
            nine_line_intersection = 0
            for coordinate in coordinates:
                left_population = left_counts.get(coordinate, 0)
                right_population = right_counts.get(coordinate, 0)
                weighted_intersection += min(left_population, right_population)
                equal_population += left_population == right_population
                nine_line_intersection += left_population == 9 and right_population == 9
            overlap.append({"left_layer": left["layer_index"], "right_layer": right["layer_index"],
                            "set_intersection": both, "set_jaccard": both / len(a | b),
                            "weighted_intersection_lines": weighted_intersection,
                            "weighted_overlap_over_region_lines":
                              weighted_intersection / left["line_count"],
                            "equal_population_set_count": equal_population,
                            "nine_line_set_intersection": nine_line_intersection})
    aggregate = [0] * (geometry["subpartition_count"] * geometry["sets_per_subpartition"])
    for region in regions:
        for (sp, set_index), count in region_counts(region).items():
            aggregate[sp * geometry["sets_per_subpartition"] + set_index] += count
    provenance_keys = ("schema", "status", "claim_boundary", "address_namespace",
                       "sidecar_sha256", "mapper", "region_count", "total_target_lines")
    return {"schema": "C16_E1_QWEIGHT_L2_SET_MAPPING_V1", "status": "PASS",
            "claim_boundary": "STATIC_ACCEPTED_MAPPER_OUTPUT",
            "input_provenance": {key: value[key] for key in provenance_keys if key in value},
            "geometry": geometry, "region_count": 28,
            "total_target_lines": sum(r["line_count"] for r in regions),
            "regions": regions, "region_pair_set_overlap": overlap,
            "aggregate_target_set_population": set_distribution(aggregate)}


def boundary(kernel: Kernel, target_class: int, side: str) -> Segment:
    need(target_class in kernel.boundaries and side in kernel.boundaries[target_class],
         f"{kernel.source}: missing class {target_class} {side}")
    return segment(kernel.boundaries[target_class][side], kernel.source.parent,
                   prefix=f"{side}_")


def semantic_bounds(kernels: list[Kernel], decode: int, layer: int,
                    target_kernel: Kernel, target_class: int) -> tuple[int, int]:
    matches = [item.kernel_id for item in kernels if item.decode == decode and
               item.semantic_layer == layer and item.semantic_identity == "up_proj"]
    if matches:
        return min(matches), max(matches)
    # Synthetic/prejoined summaries may place the formal range on the target
    # boundary rather than repeat KERNEL_SEQUENCE_FORMAL columns per kernel.
    value = target_kernel.boundaries[target_class]
    need("semantic_range_start_kernel" in value and "semantic_range_end_kernel" in value,
         f"layer {layer} D{decode}: semantic up_proj range unavailable")
    return int(value["semantic_range_start_kernel"]), int(value["semantic_range_end_kernel"])


def paths(segments: Sequence[Segment], field: str) -> list[Path]:
    result = [getattr(item, field) for item in segments]
    need(all(result), f"segment misses {field}")
    return result


def segment_reference_hist(segments: Sequence[Segment], mapper: Mapper,
                           subparts: int, sets: int) -> list[int]:
    bins, total = subparts * sets, [0] * (subparts * sets)
    for item in segments:
        if item.all_set_refs is not None and item.all_set_refs.is_file():
            values = histogram(item.all_set_refs, bins)
        else:
            need(item.all_line_ref_pairs is not None and
                 item.all_line_ref_pairs.is_file(), "segment lacks all-set refs and all-line/count pairs")
            values = map_pairs(item.all_line_ref_pairs, mapper, subparts, sets)
        for index, value in enumerate(values): total[index] += value
    return total


def gap(kernels: list[Kernel], region: dict, earlier: int, later: int,
        mapper: Mapper, geometry: dict, temporary: Path) -> tuple[dict, dict]:
    cls = region["target_class"]
    prior = [k for k in kernels if k.decode == earlier and k.target_refs.get(cls, 0)][-1]
    after = [k for k in kernels if k.decode == later and k.target_refs.get(cls, 0)][0]
    by_id = {k.kernel_id: k for k in kernels}
    middle = [by_id[i].full for i in range(prior.kernel_id + 1, after.kernel_id)]
    need(all(not by_id[i].target_refs.get(cls, 0)
             for i in range(prior.kernel_id + 1, after.kernel_id)),
         f"class {cls}: current-layer target reference inside strict reuse gap")
    segments = [boundary(prior, cls, "suffix"), *middle, boundary(after, cls, "prefix")]
    bins = geometry["subpartition_count"] * geometry["sets_per_subpartition"]
    ref_hist = segment_reference_hist(segments, mapper,
                                      geometry["subpartition_count"],
                                      geometry["sets_per_subpartition"])
    all_iter, temps = bounded_merge(paths(segments, "all_lines"), temporary)
    all_unique, unique_hist = map_unique(
        all_iter, mapper, geometry["subpartition_count"],
        geometry["sets_per_subpartition"])
    for path in temps: path.unlink()
    non_iter, temps = bounded_merge(paths(segments, "non_target_lines"), temporary)
    non_unique = sum(1 for _ in non_iter)
    for path in temps: path.unlink()
    previous_semantic_start, previous_semantic_end = semantic_bounds(
        kernels, earlier, region["layer_index"], prior, cls)
    next_semantic_start, next_semantic_end = semantic_bounds(
        kernels, later, region["layer_index"], after, cls)
    need(previous_semantic_end < next_semantic_start, "overlapping semantic ranges")
    semantic_middle = [by_id[i].full for i in
                       range(previous_semantic_end + 1, next_semantic_start)]
    semantic_all, semantic_temps = bounded_merge(paths(semantic_middle, "all_lines"), temporary)
    semantic_all_unique = sum(1 for _ in semantic_all)
    for path in semantic_temps: path.unlink()
    semantic_non, semantic_temps = bounded_merge(
        paths(semantic_middle, "non_target_lines"), temporary)
    semantic_non_unique = sum(1 for _ in semantic_non)
    for path in semantic_temps: path.unlink()
    targets = region_counts(region); indices = [sp * geometry["sets_per_subpartition"] + s for sp, s in targets]
    ref_pressure, unique_pressure = [ref_hist[i] for i in indices], [unique_hist[i] for i in indices]
    ways = geometry["associativity"]
    next_unique = after.boundaries[cls].get("referenced_target_unique_lines",
                                           after.boundaries[cls].get("target_unique_128b_lines", 0))
    row = {"layer_index": region["layer_index"], "target_class": cls,
           "transition": f"D{earlier}_D{later}", "previous_target_kernel": prior.kernel_id,
           "next_target_kernel": after.kernel_id, "intervening_full_kernel_count": len(middle),
           "elapsed_dynamic_kernels": after.kernel_id - prior.kernel_id + 1,
           "kernel_id_distance": after.kernel_id - prior.kernel_id,
           "intervening_dynamic_instructions": sum(s.instructions for s in segments),
           "intervening_global_address_references": sum(s.global_refs for s in segments),
           "intervening_non_target_relative_current_layer_128b_line_references":
             sum(ref_hist),
           "intervening_unique_128b_lines": all_unique,
           "intervening_non_target_relative_current_layer_unique_128b_lines": all_unique,
           "intervening_non_target_excluding_all_28_targets_unique_128b_lines": non_unique,
           "same_subpartition_non_target_references": sum(ref_hist[i] for i in range(bins)
             if i // geometry["sets_per_subpartition"] in {sp for sp, _ in targets}),
           "conflicting_non_target_unique_128b_lines": sum(unique_hist[i] for i in indices),
           "next_reuse_target_unique_128b_lines": int(next_unique),
           "semantic_previous_range_start_kernel": previous_semantic_start,
           "semantic_previous_range_end_kernel": previous_semantic_end,
           "semantic_next_range_start_kernel": next_semantic_start,
           "semantic_next_range_end_kernel": next_semantic_end,
           "semantic_range_intervening_full_kernel_count": len(semantic_middle),
           "semantic_range_intervening_dynamic_instructions":
             sum(item.instructions for item in semantic_middle),
           "semantic_range_intervening_global_address_references":
             sum(item.global_refs for item in semantic_middle),
           "semantic_range_intervening_unique_128b_lines": semantic_all_unique,
           "semantic_range_intervening_non_target_relative_current_layer_unique_128b_lines":
             semantic_all_unique,
           "semantic_range_intervening_non_target_excluding_all_28_targets_unique_128b_lines":
             semantic_non_unique}
    pressure = {"layer_index": region["layer_index"], "target_class": cls,
                "transition": row["transition"], "claim_boundary": CLAIM,
                "target_set_count": len(indices),
                "non_target_reference_pressure": dist(ref_pressure),
                "non_target_unique_line_pressure": dist(unique_pressure),
                "hot_set_threshold_unique_lines": ways,
                "hot_set_fraction": sum(v >= ways for v in unique_pressure) / len(indices),
                "target_plus_non_target_over_associativity_fraction":
                    sum(t + p > ways for t, p in zip(targets.values(), unique_pressure)) / len(indices),
                "per_subpartition": [{"subpartition": sp,
                  "target_set_count": sum(owner == sp for owner, _ in targets),
                  "non_target_reference_pressure": dist([ref_hist[sp * geometry["sets_per_subpartition"] + s]
                    for owner, s in targets if owner == sp]),
                  "non_target_unique_line_pressure": dist([unique_hist[sp * geometry["sets_per_subpartition"] + s]
                    for owner, s in targets if owner == sp])}
                    for sp in range(geometry["subpartition_count"])]}
    return row, pressure


def configure_gap_workers(kernels: list[Kernel], static: dict, mapper: Mapper,
                          temporary: Path) -> None:
    global _GAP_KERNELS, _GAP_STATIC, _GAP_MAPPER, _GAP_TEMP_ROOT
    _GAP_KERNELS = kernels
    _GAP_STATIC = static
    _GAP_MAPPER = mapper
    _GAP_TEMP_ROOT = temporary


def run_gap_task(task: tuple[int, int, int]) -> tuple[dict, dict]:
    need(_GAP_KERNELS is not None and _GAP_STATIC is not None and
         _GAP_MAPPER is not None and _GAP_TEMP_ROOT is not None,
         "gap worker state is not initialized")
    layer, earlier, later = task
    region = next(item for item in _GAP_STATIC["regions"]
                  if item["layer_index"] == layer)
    task_temp = _GAP_TEMP_ROOT / f"layer-{layer}-D{earlier}-D{later}"
    task_temp.mkdir(parents=False, exist_ok=False)
    return gap(_GAP_KERNELS, region, earlier, later, _GAP_MAPPER,
               _GAP_STATIC["geometry"], task_temp)


def aggregate_gaps(kernels: list[Kernel], static: dict, mapper: Mapper,
                   temporary: Path, workers: int) -> tuple[list[dict], list[dict]]:
    need(workers >= 1, "--workers must be positive")
    tasks = [(region["layer_index"], earlier, later)
             for region in static["regions"]
             for earlier, later in ((1, 2), (2, 3))]
    configure_gap_workers(kernels, static, mapper, temporary)
    rows: list[dict] = []
    pressures: list[dict] = []

    def record(result: tuple[dict, dict]) -> None:
        row, pressure = result
        rows.append(row); pressures.append(pressure)
        print(f"AGGREGATE_GAP_PASS layer={row['layer_index']} "
              f"transition={row['transition']}", flush=True)

    if workers == 1:
        for task in tasks:
            record(run_gap_task(task))
    else:
        need(sys.platform.startswith("linux"),
             "--workers>1 requires Linux fork process semantics")
        context = multiprocessing.get_context("fork")
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=workers, mp_context=context) as executor:
            futures = [executor.submit(run_gap_task, task) for task in tasks]
            for future in concurrent.futures.as_completed(futures):
                record(future.result())
    rows.sort(key=lambda item: (item["layer_index"], item["transition"]))
    pressures.sort(key=lambda item: (item["layer_index"], item["transition"]))
    return rows, pressures


def quota(static: dict, pressures: list[dict]) -> dict:
    geo, single = static["geometry"], static["regions"][0]["line_count"]
    budgets = []
    for name, byte_count in BUDGETS.items():
        lines = byte_count // geo["line_size_bytes"]
        quotient, remainder = divmod(lines, geo["subpartition_count"])
        quotas = [quotient + (sp < remainder) for sp in range(geo["subpartition_count"])]
        total_sets = geo["subpartition_count"] * geo["sets_per_subpartition"]
        even_floor, even_remainder = divmod(lines, total_sets)
        even_ceil = even_floor + bool(even_remainder)
        layer_admission = []
        for region in static["regions"]:
            population = list(region_counts(region).values())
            layer_pressure = [item for item in pressures
                              if item["layer_index"] == region["layer_index"]]
            global_sufficient = lines >= single
            mean_hot = statistics.mean(item["hot_set_fraction"] for item in layer_pressure)
            mean_over_way = statistics.mean(
                item["target_plus_non_target_over_associativity_fraction"]
                for item in layer_pressure)
            set_local_unfavorable = global_sufficient and (
                any(value > even_ceil for value in population) or mean_hot > 0 or
                mean_over_way > 0)
            layer_admission.append({"layer_index": region["layer_index"],
              "single_region_protectable_fraction_under_sp_quota":
                sum(min(a, b) for a, b in zip(region["subpartition_line_counts"], quotas)) / single,
              "subpartitions_over_quota": sum(a > b for a, b in zip(region["subpartition_line_counts"], quotas)),
              "target_set_population": dist(population),
              "target_set_population_over_average_even_quota":
                dist([value / max(lines / total_sets, 1e-30) for value in population]),
              "target_sets_above_even_quota_floor": sum(value > even_floor for value in population),
              "target_sets_above_even_quota_ceil": sum(value > even_ceil for value in population),
              "global_quota_sufficient_for_single_region": global_sufficient,
              "global_quota_sufficient_but_set_local_unfavorable_proxy": set_local_unfavorable,
              "global_sufficient_set_local_proxy_rule":
                "global_lines>=single_region_lines AND (target_population>even_quota_ceil OR hot_set_fraction>0 OR target_plus_non_target_over_way_fraction>0)",
              "potential_set_local_admission_pressure_proxy": {
                "claim_boundary": CLAIM,
                "mean_hot_set_fraction_across_reuse_gaps": mean_hot,
                "mean_target_plus_non_target_over_associativity_fraction": mean_over_way,
                "actual_admission_denial_or_eviction_claimed": False}})
        budgets.append({"budget": name, "bytes": byte_count, "global_lines": lines,
          "per_subpartition_quotient": quotient, "per_subpartition_remainder": remainder,
          "per_subpartition_quota_lines": quotas,
          "quota_over_total_l2": byte_count / geo["l2_bytes"],
          "quota_over_single_qweight_footprint": lines / single,
          "average_quota_lines_per_set": lines / total_sets,
          "even_quota_lines_per_set_floor": even_floor,
          "even_quota_lines_per_set_ceil": even_ceil,
          "global_quota_equals_single_region": lines == single,
          "all_subpartition_quotas_cover_single_region": all(
              all(want <= limit for want, limit in zip(r["subpartition_line_counts"], quotas))
              for r in static["regions"]),
          "set_local_admission_limitation_still_possible": True,
          "set_local_limitation_note": "Global/per-SP capacity does not prove a protected victim is available in each target set; this is a proxy, not observed denial.",
          "per_layer_static_admission": layer_admission})
    hardest = sorted(pressures, key=lambda item: item["non_target_unique_line_pressure"]["median"],
                     reverse=True)
    easiest = list(reversed(hardest))
    return {"schema": "C16_E1_QUOTA_STATIC_MAPPING_V1", "status": "PASS",
            "performance_ranking_claimed": False,
            "claim_boundary": "STATIC_QUOTA_AND_SET_PLACEMENT_INTERPRETATION", "budgets": budgets,
            "dynamic_pressure_context": {
              "claim_boundary": CLAIM,
              "highest_median_unique_pressure": [{"layer_index": item["layer_index"],
                "transition": item["transition"],
                "median": item["non_target_unique_line_pressure"]["median"]}
                for item in hardest[:10]],
              "lowest_median_unique_pressure": [{"layer_index": item["layer_index"],
                "transition": item["transition"],
                "median": item["non_target_unique_line_pressure"]["median"]}
                for item in easiest[:10]],
              "budget_performance_order_inferred": False}}


def correlation(a: Sequence[float], b: Sequence[float]) -> float | None:
    ma, mb = statistics.mean(a), statistics.mean(b)
    numerator = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    denominator = math.sqrt(sum((x-ma)**2 for x in a) * sum((y-mb)**2 for y in b))
    return numerator / denominator if denominator else None


def stability(rows: list[dict], pressure: list[dict]) -> dict:
    by = {t: {r["layer_index"]: r for r in rows if r["transition"] == t}
          for t in ("D1_D2", "D2_D3")}
    metrics = {}
    for field in ("intervening_dynamic_instructions", "intervening_global_address_references",
                  "intervening_unique_128b_lines",
                  "intervening_non_target_relative_current_layer_unique_128b_lines",
                  "conflicting_non_target_unique_128b_lines"):
        a, b = [float(by["D1_D2"][i][field]) for i in range(28)], [float(by["D2_D3"][i][field]) for i in range(28)]
        rel = [abs(x-y)/max(abs(x), abs(y), 1) for x, y in zip(a, b)]
        metrics[field] = {"pearson": correlation(a, b),
                          "median_symmetric_relative_difference": statistics.median(rel),
                          "max_symmetric_relative_difference": max(rel)}
    pressure_by = {t: {r["layer_index"]: r for r in pressure if r["transition"] == t}
                   for t in ("D1_D2", "D2_D3")}
    for statistic in ("median", "p90", "p99", "max"):
        field = f"non_target_unique_line_pressure_{statistic}"
        a = [float(pressure_by["D1_D2"][i]["non_target_unique_line_pressure"][statistic])
             for i in range(28)]
        b = [float(pressure_by["D2_D3"][i]["non_target_unique_line_pressure"][statistic])
             for i in range(28)]
        rel = [abs(x-y)/max(abs(x), abs(y), 1) for x, y in zip(a, b)]
        metrics[field] = {"pearson": correlation(a, b),
                          "median_symmetric_relative_difference": statistics.median(rel),
                          "max_symmetric_relative_difference": max(rel)}
    return {"schema": "C16_E1_D1_D2_D2_D3_STABILITY_V1", "status": "PASS",
            "claim_boundary": CLAIM,
            "layer_count": 28, "metrics": metrics}


def write_tsv(path: Path, rows: list[dict]) -> None:
    columns = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write("\t".join(columns) + "\n")
        for row in rows: stream.write("\t".join(str(row[c]) for c in columns) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-root", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--static-mapping", type=Path)
    source.add_argument("--sidecar", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--line-mapping-tsv", type=Path); group.add_argument("--mapper-cmd")
    parser.add_argument("--mapper-authority-json", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv); args.output_dir.mkdir(parents=True, exist_ok=True)
    mapper = Mapper(args.line_mapping_tsv, args.mapper_cmd, args.mapper_authority_json)
    static_source = (json.loads(args.static_mapping.read_text(encoding="utf-8"))
                     if args.static_mapping else mapping_from_sidecar(args.sidecar, mapper))
    static = static_mapping(static_source)
    if args.sidecar:
        static["input_provenance"].update({
            "sidecar_path": str(args.sidecar.resolve()),
            "sidecar_sha256": sha256_path(args.sidecar),
            "mapper_command": args.mapper_cmd,
            "runtime_mapper_authority": mapper.authority,
            "line_mapping_tsv": (str(args.line_mapping_tsv.resolve())
                                 if args.line_mapping_tsv else None),
        })
    kernels = load_kernels(args.summary_root)
    with tempfile.TemporaryDirectory(dir=args.output_dir, prefix="merge-") as temp:
        rows, pressures = aggregate_gaps(
            kernels, static, mapper, Path(temp), args.workers)
    dump(args.output_dir / "QWEIGHT_L2_SET_MAPPING.json", static)
    dump(args.output_dir / "QUOTA_STATIC_MAPPING.json", quota(static, pressures))
    dump(args.output_dir / "PER_LAYER_REUSE_DISTANCE_MATRIX.json",
         {"schema": "C16_E1_PER_LAYER_REUSE_DISTANCE_MATRIX_V1", "status": "PASS",
          "claim_boundary": "128B_LINE_REFERENCE_PROXY",
          "boundary": "LAST_TRUE_TARGET_REFERENCE_TO_NEXT_FIRST_TRUE_TARGET_REFERENCE", "rows": rows})
    write_tsv(args.output_dir / "PER_LAYER_REUSE_DISTANCE_MATRIX.tsv", rows)
    dump(args.output_dir / "SET_CONFLICT_PRESSURE_ANALYSIS.json",
         {"schema": "C16_E1_SET_CONFLICT_PRESSURE_ANALYSIS_V1", "status": "PASS",
          "claim_boundary": CLAIM,
          "actual_l2_hit_miss_or_eviction_claimed": False, "quantile_method": "nearest_rank", "rows": pressures})
    dump(args.output_dir / "D1_D2_D2_D3_STABILITY.json", stability(rows, pressures))
    summary_index = args.summary_root / "TRACE_REFERENCE_SUMMARY.json"
    static_input_sha = sha256_path(args.static_mapping) if args.static_mapping else None
    sidecar_sha = (sha256_path(args.sidecar) if args.sidecar else
                   static.get("input_provenance", {}).get("sidecar_sha256"))
    mapper_identity = static.get("input_provenance", {}).get("mapper")
    dump(args.output_dir / "AGGREGATION_PROVENANCE.json",
         {"schema": "C16_E1_TRACE_PRESSURE_AGGREGATE_V1", "status": "PASS",
          "kernel_count": len(kernels),
          "kernel_range": [kernels[0].kernel_id, kernels[-1].kernel_id], "raw_trace_opened": False,
          "summary_root": str(args.summary_root.resolve()),
          "summary_index": str(summary_index.resolve()) if summary_index.is_file() else None,
          "summary_index_sha256": sha256_path(summary_index) if summary_index.is_file() else None,
          "static_mapping": str(args.static_mapping.resolve()) if args.static_mapping else None,
          "static_mapping_sha256": static_input_sha,
          "sidecar": str(args.sidecar.resolve()) if args.sidecar else None,
          "sidecar_sha256": sidecar_sha,
          "input_mapper_identity_sha256": sha256_json(mapper_identity) if mapper_identity else None,
          "runtime_mapper_authority": mapper.authority,
          "runtime_mapper_authority_sha256": sha256_json(mapper.authority),
          "line_mapping_tsv_sha256": sha256_path(args.line_mapping_tsv) if args.line_mapping_tsv else None,
          "line_mapper": str(args.line_mapping_tsv.resolve()) if args.line_mapping_tsv else args.mapper_cmd})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
