#!/usr/bin/env python3
"""Read-only C12 operator-aware characterization.

This tool deliberately consumes immutable traces and terminal C12 arm outputs
only.  It does not invoke a simulator and writes only the requested review-pack
directory.  Its main safety property is that every operator label is derived
from either a trace address intersecting the runtime ``weight_layout`` or an
embedded trace-header kernel name; execution-order inference is never used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import re
import subprocess
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / "util" / "llm_trace_capture"))
from analyze_trace_address_coverage import decode  # exact frozen NVBit decoder


DEFAULT_STAGE = Path("/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55")
DEFAULT_C12 = Path("/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN")
DEFAULT_STATUS = ROOT / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/ARM_STATUS.tsv"
DEFAULT_RESULTS = ROOT / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/ARM_RESULTS.tsv"
OUT_ROOT = ROOT / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION"

EXPECTED = {
    "prefill": {
        "count": 692,
        "sha": "a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f",
        "registration_sha256": "6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0",
    },
    "decode1": {
        "count": 740,
        "sha": "b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc",
        "registration_sha256": "3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48",
    },
}
FROZEN = {
    "framework_anchor": "d64408a97d76a320a6d49468653d416e33677af8",
    "core_head": "57bb71ecd015b6ec0ab32e45b0815e5beaf69172",
    "binary_sha256": "2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for piece in iter(lambda: source.read(1024 * 1024), b""):
            h.update(piece)
    return h.hexdigest()


def tsv_read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict]) -> None:
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def fmt(value: float | int) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.12g}"


def read_manifest(path: Path) -> dict:
    value: dict[str, str] = {}
    for line in path.read_text().splitlines():
        bits = line.split("\t", 1)
        if len(bits) == 2:
            value[bits[0]] = bits[1]
    return value


def trace_header(path: Path) -> tuple[str | None, int]:
    names: list[str] = []
    with lzma.open(path, "rt", errors="replace") as source:
        for line in source:
            if line.startswith("-kernel name = "):
                names.append(line.rstrip().split("= ", 1)[1])
            if line.startswith("#traces format"):
                break
    return (names[0] if len(names) == 1 and names[0] else None), len(names)


def group_for(cls: str) -> str:
    return {
        "ATTENTION_PROJECTION": "ATTENTION", "ATTENTION_CORE": "ATTENTION",
        "FFN_MLP": "FFN", "NORM": "OTHER_MODEL", "ROPE": "OTHER_MODEL",
        "EMBEDDING_OUTPUT": "OTHER_MODEL", "OTHER_COMPUTE": "OTHER_COMPUTE",
        "MIXED_DIRECT": "MIXED", "UNRESOLVED": "UNRESOLVED",
    }[cls]


def parameter_class(name: str) -> str:
    lower = name.lower()
    if any(x in lower for x in ("q_proj", "k_proj", "v_proj", "o_proj")):
        return "ATTENTION_PROJECTION"
    if any(x in lower for x in ("gate_proj", "up_proj", "down_proj")):
        return "FFN_MLP"
    if "norm" in lower or "layernorm" in lower:
        return "NORM"
    if "embed_tokens" in lower or "lm_head" in lower:
        return "EMBEDDING_OUTPUT"
    return "OTHER_COMPUTE"


def semantic_class(name: str) -> str | None:
    lower = name.lower()
    if "rotary" in lower or "rope" in lower:
        return "ROPE"
    if "rmsnorm" in lower or "layernorm" in lower:
        return "NORM"
    # The embedded PyTorch Flash kernel symbol is a direct semantic name.  Keep
    # this deliberately narrow: generic GEMM/reduction names are not attention
    # evidence, while the Flash spellings below are.
    if any(token in lower for token in ("flashatt", "flash_attention", "pytorch_flash", "flash_fwd", "flash_bwd", "scaled_dot_product_attention")):
        return "ATTENTION_CORE"
    # The patterns below spell out a generic operation in the embedded name;
    # they are not derived from a filename or an execution position.
    if any(x in lower for x in ("elementwise", "reduce", "indexselect", "indexing", "fill", "copy", "arange")):
        return "OTHER_COMPUTE"
    return None


LAYER = re.compile(r"(?:^|\.)layers\.(\d+)(?:\.|$)")


@dataclass(frozen=True)
class Parameter:
    start: int
    end: int
    name: str


@dataclass
class Kernel:
    roi: str
    index: int
    filename: str
    semantic_name: str
    header_count: int
    params: list[str]
    weight_refs: int
    kv_refs: int
    unknown_refs: int
    pages: dict[str, set[int]]
    operator_class: str = "UNRESOLVED"
    evidence_kind: str = "UNRESOLVED"
    evidence_detail: str = "no direct parameter-range or semantic-name evidence"
    layer_id: str = "NA"

    @property
    def group(self) -> str:
        return group_for(self.operator_class)

    @property
    def direct(self) -> bool:
        return self.evidence_kind in {"DIRECT_PARAMETER_RANGE", "DIRECT_SEMANTIC_NAME", "MIXED_DIRECT"}


def range_index(sidecar: Path) -> tuple[list[Parameter], list[int], dict]:
    data = json.loads(sidecar.read_text())
    allocations = [row for row in data["allocations"] if row.get("object_kind") == "WEIGHT"]
    if len(allocations) != 1:
        raise RuntimeError(f"{sidecar}: expected one WEIGHT allocation, got {len(allocations)}")
    allocation = allocations[0]
    base = int(allocation["simva_start"], 0)
    size = int(allocation["size_bytes"])
    params = [Parameter(base + int(row["offset_bytes"]), base + int(row["offset_bytes"]) + int(row["size_bytes"]), row["name"])
              for row in data["weight_layout"]["tensors"]]
    params.sort(key=lambda row: (row.start, row.end, row.name))
    if not params or params[0].start < base or params[-1].end > base + size:
        raise RuntimeError(f"{sidecar}: parameter ranges fall outside flat WEIGHT allocation")
    for earlier, later in zip(params, params[1:]):
        if earlier.end > later.start:
            raise RuntimeError(f"{sidecar}: overlapping parameter ranges {earlier.name} and {later.name}")
    return params, [row.start for row in params], {"base": base, "size": size, "allocation": allocation, "data": data}


def matching_parameters(address: int, width: int, params: list[Parameter], starts: list[int]) -> list[str]:
    # A trace memory operand can cross an aligned parameter boundary; retain
    # every exact range that intersects it instead of assigning it arbitrarily.
    end = address + width
    i = bisect_right(starts, address) - 1
    result: list[str] = []
    for j in (i, i + 1):
        if 0 <= j < len(params) and max(address, params[j].start) < min(end, params[j].end):
            result.append(params[j].name)
    return result


def object_ranges(sidecar_data: dict, roi: str) -> list[tuple[int, int, str]]:
    result: list[tuple[int, int, str]] = []
    for row in sidecar_data["allocations"]:
        if row.get("object_kind") == "WEIGHT":
            start = int(row["simva_start"], 0)
            result.append((start, start + int(row["size_bytes"]), "WEIGHT"))
    for row in selected_kv_events(sidecar_data, roi):
        start = int(row["simva_start"], 0)
        result.append((start, start + int(row["size_bytes"]), "KV_CACHE"))
    result.sort()
    for left, right in zip(result, result[1:]):
        if left[2] != right[2] and left[1] > right[0]:
            raise RuntimeError("runtime WEIGHT/KV SimVA ranges overlap")
    return result


def selected_kv_events(sidecar_data: dict, roi: str) -> list[dict]:
    """Return exactly the runtime KV events admitted by the frozen C4 contract.

    This selection deliberately retains the historical Prefill step-0 events
    in Decode1 as well as Decode step-1 replacements.  It is a range contract,
    not a per-instruction tensor-lifetime proof; the KV audit makes that limit
    visible rather than silently assigning semantic ownership.
    """
    result: list[dict] = []
    for row in sidecar_data.get("kv_cache_events", []):
        phase, step = row.get("phase"), row.get("step")
        keep = (roi == "prefill" and phase == "PREFILL" and step == 0) or (
            roi == "decode1" and ((phase == "PREFILL" and step == 0) or (phase == "DECODE" and step == 1)))
        if keep:
            result.append(row)
    return result


def interval_union_stats(events: list[dict]) -> tuple[int, int, int]:
    """Return (event-byte sum, union bytes, merged spans) for a sidecar view."""
    intervals = sorted((int(row["simva_start"], 0), int(row["simva_start"], 0) + int(row["size_bytes"])) for row in events)
    merged: list[tuple[int, int]] = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    total = sum(end - start for start, end in intervals)
    union = sum(end - start for start, end in merged)
    return total, union, len(merged)


def semantic_family(kernel: Kernel) -> str:
    lower = kernel.semantic_name.lower()
    if "cutlass" in lower:
        return "CUTLASS_GEMM"
    if "ampere" in lower and "gemm" in lower:
        return "AMPERE_GEMM"
    if "flash" in lower:
        return "FLASH_ATTENTION"
    return "OTHER_SEMANTIC_SYMBOL"


def merged_object_ranges(sidecar_data: dict, roi: str) -> list[tuple[int, int, str]]:
    """Merge same-kind runtime intervals for the fast scanner, rejecting aliases."""
    grouped: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for start, end, kind in object_ranges(sidecar_data, roi):
        grouped[kind].append((start, end))
    merged: list[tuple[int, int, str]] = []
    for kind, ranges in grouped.items():
        for start, end in sorted(ranges):
            if merged and merged[-1][2] == kind and start <= merged[-1][1]:
                old_start, old_end, _ = merged[-1]
                merged[-1] = (old_start, max(old_end, end), kind)
            else:
                merged.append((start, end, kind))
    merged.sort()
    for left, right in zip(merged, merged[1:]):
        if left[1] > right[0]:
            raise RuntimeError("merged runtime object intervals overlap across kinds")
    return merged


def parse_pages(value: str | None) -> set[int]:
    return {int(part) for part in (value or "").split(",") if part}


def fast_scan_traces(scanner: Path, roi: str, listed: list[str], trace_list: Path, trace_dir: Path,
                     params: list[Parameter], sidecar_data: dict, out: Path) -> list[Kernel]:
    """Use the compiled analytical scanner without weakening full-lane accounting."""
    if not scanner.is_file() or not scanner.stat().st_mode & 0o111:
        raise RuntimeError(f"fast trace scanner is absent or not executable: {scanner}")
    param_path = out / f"PARAMETER_RANGES_{roi}.tsv"
    object_path = out / f"OBJECT_RANGES_{roi}.tsv"
    with param_path.open("w") as output:
        for row in params:
            output.write(f"{row.start}\t{row.end}\t{row.name}\n")
    with object_path.open("w") as output:
        for start, end, kind in merged_object_ranges(sidecar_data, roi):
            output.write(f"{start}\t{end}\t{kind}\n")
    # Four bounded workers are used only after the caller's resource check.  A
    # worker consumes a disjoint ordered list, so output ordering is restored
    # exactly below and the scanner never writes a shared output file.
    chunks = [listed[part::4] for part in range(4)]
    prior_rows: list[dict[str, str]] = []
    jobs: list[tuple[Path, Path, subprocess.Popen]] = []
    for part, names in enumerate(chunks):
        prior_path = out / f"TRACE_SCAN_{roi}_{part}.tsv"
        resume_path = out / f"TRACE_SCAN_{roi}_{part}_resume.tsv"
        for existing in (prior_path, resume_path):
            if existing.exists():
                prior_rows.extend(tsv_read(existing))
        prior_names = {row["trace_filename"] for row in prior_rows if row["trace_filename"] in names}
        pending = [name for name in names if name not in prior_names]
        if not pending:
            continue
        list_path = out / f"TRACE_SCAN_INPUT_{roi}_{part}.list"
        scan_path = out / f"TRACE_SCAN_{roi}_{part}_resume.tsv"
        list_path.write_text("\n".join(pending) + "\n")
        jobs.append((list_path, scan_path, subprocess.Popen([str(scanner), str(list_path), str(trace_dir), str(object_path), str(param_path), str(scan_path)])))
    for _, scan_path, process in jobs:
        if process.wait() != 0:
            raise RuntimeError(f"{roi}: fast trace scanner failed for {scan_path}")
    scanned = {row["trace_filename"]: row for row in prior_rows}
    scanned.update({row["trace_filename"]: row for _, scan_path, _ in jobs for row in tsv_read(scan_path)})
    for original_index, name in enumerate(listed):
        if name not in scanned:
            raise RuntimeError(f"{roi}: scanner omitted {name}")
        scanned[name]["compute_index"] = str(original_index)
        # Keep the final TSV field nonempty.  Besides being more readable than
        # a trailing tab, this gives a stable explicit representation of "no
        # direct parameter range" in audit artifacts.
        scanned[name]["parameter_names"] = scanned[name].get("parameter_names") or "NONE"
    scan_path = out / f"TRACE_SCAN_{roi}.tsv"
    write_tsv(scan_path, ["compute_index", "trace_filename", "weight_refs", "kv_refs", "unknown_refs", "weight_pages", "kv_pages", "unknown_pages", "parameter_names"],
              [scanned[name] for name in listed])
    if set(scanned) != set(listed) or len(scanned) != len(listed):
        raise RuntimeError(f"{roi}: scanner output does not preserve trace-list order")
    result: list[Kernel] = []
    for index, filename in enumerate(listed):
        row = scanned[filename]
        if int(row["compute_index"]) != index:
            raise RuntimeError(f"{roi}: scanner index mismatch at {index}")
        semantic, header_count = trace_header(trace_dir / filename)
        kernel = Kernel(roi, index, filename, semantic or "MISSING_OR_NONUNIQUE_HEADER", header_count,
                        [name for name in (row["parameter_names"] or "").split(";") if name and name != "NONE"], int(row["weight_refs"]),
                        int(row["kv_refs"]), int(row["unknown_refs"]),
                        {"WEIGHT": parse_pages(row["weight_pages"]), "KV_CACHE": parse_pages(row["kv_pages"]),
                         "UNKNOWN": parse_pages(row["unknown_pages"])})
        classify_kernel(kernel)
        result.append(kernel)
    return result


def object_kind(address: int, width: int, ranges: list[tuple[int, int, str]]) -> str:
    hits = [kind for start, end, kind in ranges if start <= address and address + width <= end]
    return hits[0] if len(hits) == 1 else "UNKNOWN"


def classify_kernel(kernel: Kernel) -> None:
    pclasses = {parameter_class(name) for name in kernel.params}
    if len(pclasses) > 1:
        kernel.operator_class = "MIXED_DIRECT"
        kernel.evidence_kind = "MIXED_DIRECT"
        kernel.evidence_detail = "cross-class parameter ranges: " + ";".join(kernel.params)
    elif len(pclasses) == 1:
        kernel.operator_class = next(iter(pclasses))
        kernel.evidence_kind = "DIRECT_PARAMETER_RANGE"
        kernel.evidence_detail = "trace SimVA intersects: " + ";".join(kernel.params)
    else:
        semantic = semantic_class(kernel.semantic_name)
        if semantic:
            kernel.operator_class = semantic
            kernel.evidence_kind = "DIRECT_SEMANTIC_NAME"
            kernel.evidence_detail = "embedded header directly names " + semantic
    layers = sorted({match.group(1) for name in kernel.params if (match := LAYER.search(name))}, key=int)
    if len(layers) == 1:
        kernel.layer_id = layers[0]
    elif len(layers) > 1:
        kernel.layer_id = "MULTI_LAYER:" + ",".join(layers)


def scan_trace(roi: str, index: int, filename: str, trace: Path, params: list[Parameter], starts: list[int], sidecar: dict) -> Kernel:
    semantic, header_count = trace_header(trace)
    if semantic is None:
        semantic = "MISSING_OR_NONUNIQUE_HEADER"
    objects = object_ranges(sidecar, roi)
    refs = Counter()
    pages: dict[str, set[int]] = {"WEIGHT": set(), "KV_CACHE": set(), "UNKNOWN": set()}
    touched: set[str] = set()
    with lzma.open(trace, "rt", errors="strict") as source:
        for raw in source:
            record = decode(raw)
            if record is None or record[1] == 0:
                continue
            _, width, addresses, _ = record
            for address in addresses:
                kind = object_kind(address, width, objects)
                refs[kind] += 1
                pages[kind].update(range(address // 65536, (address + width - 1) // 65536 + 1))
                touched.update(matching_parameters(address, width, params, starts))
    kernel = Kernel(roi, index, filename, semantic, header_count, sorted(touched), refs["WEIGHT"], refs["KV_CACHE"], refs["UNKNOWN"], pages)
    classify_kernel(kernel)
    return kernel


MARKER = re.compile(r"^Processing kernel .*/([^/]+\.traceg\.xz)\s*$")
COUNTER = re.compile(r"^([A-Za-z0-9_]+) = (-?\d+)\s*$")


@dataclass
class RawKernel:
    marker: str
    index: int | None = None
    exact: dict[str, int] = field(default_factory=dict)
    cumulative: dict[str, int] = field(default_factory=dict)
    cache: Counter = field(default_factory=Counter)
    cross: Counter = field(default_factory=Counter)


def raw_kernels(path: Path) -> list[RawKernel]:
    """Parse kernel-local cache telemetry plus checkpoint counters.

    ``vm_*`` counters are cumulative at each end-of-kernel dump.  They become
    exact per-kernel deltas only after ``delta_counters`` verifies their final
    values against the immutable C12 validation sidecar.
    """
    output: list[RawKernel] = []
    current: RawKernel | None = None
    with path.open(errors="replace") as source:
        for line in source:
            marker = MARKER.match(line)
            if marker:
                current = RawKernel(marker.group(1))
                output.append(current)
                continue
            if current is None:
                continue
            counter = COUNTER.match(line)
            if counter:
                name, value = counter.group(1), int(counter.group(2))
                if name in {"gpu_sim_cycle", "gpu_sim_insn"}:
                    current.exact[name] = value
                elif name.startswith("vm_"):
                    current.cumulative[name] = value
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 7 and fields[0] in {"m4c_telemetry", "m4c_telemetry_l2"} and fields[1] == "KERNEL":
                # tag, scope, source, kernel-index, object, outcome, count
                try:
                    current.cache[(fields[0], fields[4], fields[5])] += int(fields[6])
                except ValueError:
                    raise RuntimeError(f"{path}: malformed kernel cache telemetry {line[:180]!r}")
            elif len(fields) >= 8 and fields[0] == "m4c_telemetry_cross_l1" and fields[1] == "KERNEL":
                # object, translation source, L1 outcome, count
                try:
                    current.cross[(fields[4], fields[5], fields[6])] += int(fields[7])
                except ValueError:
                    raise RuntimeError(f"{path}: malformed cross-layer telemetry {line[:180]!r}")
    return output


def delta_counters(rows: list[RawKernel], validation: dict, raw_path: Path) -> list[dict[str, int]]:
    # Raw dumps include both monotonic event counters and instantaneous gauges
    # (for example sub-entry valid occupancy).  Only the listed event counters
    # may be differenced across kernels; treating a gauge as a counter would
    # manufacture a negative event count after a legitimate replacement.
    cumulative_metrics = {
        "vm_l1_tlb_accesses", "vm_l1_tlb_hits", "vm_l1_tlb_misses",
        "vm_l2_tlb_accesses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
        "vm_translation_walk_starts", "vm_pte_requests", "vm_pte_l2_only_responses", "vm_pte_dram_responses",
        "vm_translation_requester_latency_cycles_total", "vm_weight_segment_hits",
        "vm_weight_segment_l2_suppressed", "vm_l2_tlb_subentry_hits", "vm_l2_tlb_subentry_misses",
    }
    prior: Counter = Counter()
    deltas: list[dict[str, int]] = []
    for row in rows:
        now = Counter({key: value for key, value in row.cumulative.items() if key in cumulative_metrics})
        delta = {key: now[key] - prior[key] for key in now}
        if any(value < 0 for value in delta.values()):
            bad = [key for key, value in delta.items() if value < 0]
            raise RuntimeError(f"{raw_path}: cumulative counter decreased: {bad[:5]}")
        deltas.append(delta)
        prior = now
    checks = {
        "vm_l1_tlb_accesses": "vm_l1_tlb_accesses", "vm_l1_tlb_hits": "vm_l1_tlb_hits",
        "vm_l1_tlb_misses": "vm_l1_tlb_misses", "vm_l2_tlb_accesses": "vm_l2_tlb_accesses",
        "vm_l2_tlb_hits": "vm_l2_tlb_hits", "vm_l2_tlb_misses": "vm_l2_tlb_misses",
        "vm_translation_walk_starts": "vm_translation_walk_starts", "vm_pte_requests": "vm_pte_requests",
    }
    for raw_name, sidecar_name in checks.items():
        if raw_name in prior and sidecar_name in validation and validation[sidecar_name] not in {"NOT_EMITTED", ""}:
            if prior[raw_name] != int(validation[sidecar_name]):
                raise RuntimeError(f"{raw_path}: final {raw_name}={prior[raw_name]} != validation {validation[sidecar_name]}")
    return deltas


def arm_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["roi"], row["arm"], row["lseg"]


def arm_label(row: dict[str, str]) -> str:
    return row["arm"] if row["lseg"] in {"", "NONE"} else f"{row['arm']}-L{row['lseg']}"


def safe_status_rows(status: list[dict[str, str]], results: list[dict[str, str]]) -> list[dict[str, str]]:
    result_by_key = {arm_key(row): row for row in results}
    accepted: list[dict[str, str]] = []
    for row in status:
        if row.get("terminal_status") != "PASS":
            continue
        key = arm_key(row)
        result = result_by_key.get(key)
        if not result or result.get("terminal_status") != "PASS":
            raise RuntimeError(f"terminal PASS status lacks matching PASS result: {key}")
        for field, expected in FROZEN.items():
            if result.get(field) != expected:
                raise RuntimeError(f"{key}: frozen {field} mismatch {result.get(field)}")
        if result.get("trace_sha256") != EXPECTED[row["roi"]]["sha"]:
            raise RuntimeError(f"{key}: trace hash mismatch")
        if result.get("registration_sha256") != EXPECTED[row["roi"]]["registration_sha256"]:
            raise RuntimeError(f"{key}: registration hash mismatch")
        raw = Path(row["run_dir"]) / "run.log"
        validation = Path(row["run_dir"]) / "C12_ARM_VALIDATION.json"
        if not raw.is_file() or not validation.is_file():
            raise RuntimeError(f"{key}: missing terminal immutable raw evidence")
        if sha256(raw) != row["raw_log_sha256"] or sha256(raw) != result.get("raw_log_sha256"):
            raise RuntimeError(f"{key}: raw log SHA mismatch")
        accepted.append({**row, **{f"result_{k}": v for k, v in result.items()}})
    return accepted


def add_metric(rows: list[dict], roi: str, operator: str, metric: str, scope: str, unit: str, value: int | float,
               source: str, numerator: str = "", denominator: str = "") -> None:
    rows.append({"roi": roi, "operator_class": operator, "metric": metric, "metric_scope": scope, "unit": unit,
                 "numerator": numerator, "denominator": denominator, "value": fmt(value), "source": source})


def sum_by_operator(kernels: list[Kernel], values: dict[int, int], include_all: bool = True) -> dict[str, int]:
    total: Counter = Counter()
    for kernel in kernels:
        if include_all or kernel.direct:
            total[kernel.operator_class] += values.get(kernel.index, 0)
    return dict(total)


def comparison_pairs(rows: list[dict[str, str]], roi: str) -> list[tuple[str, dict, dict]]:
    by = {(row["arm"], row["lseg"]): row for row in rows if row["roi"] == roi}
    pairs: list[tuple[str, dict, dict]] = []
    def use(label: str, left: tuple[str, str], right: tuple[str, str]) -> None:
        if left in by and right in by:
            pairs.append((label, by[left], by[right]))
    use("F1_vs_F2", ("F2", "NONE"), ("F1", "NONE"))
    use("F5_vs_F0", ("F0", "NONE"), ("F5", "NONE"))
    for arm in ("F7", "F8"):
        for lseg in ("5", "10", "20"):
            use(f"{arm}-L{lseg}_vs_F0", ("F0", "NONE"), (arm, lseg))
    for lseg in ("5", "10", "20"):
        use(f"F8-L{lseg}_vs_F7-L{lseg}", ("F7", lseg), ("F8", lseg))
    use("F8-L10_vs_F9", ("F9", "NONE"), ("F8", "10"))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-root", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--c12-root", type=Path, default=DEFAULT_C12)
    parser.add_argument("--arm-status", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--arm-results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--scanner", type=Path, required=True, help="compiled c12_operator_trace_scan executable")
    parser.add_argument("--resume", action="store_true", help="resume an interrupted trace scan in this output directory")
    parser.add_argument("--source-commit", required=True, help="C12 source commit whose formal tables were consumed")
    parser.add_argument("--output-dir", type=Path, default=OUT_ROOT)
    args = parser.parse_args()
    out = args.output_dir
    if out.exists() and any(out.iterdir()) and not args.resume:
        raise SystemExit(f"refusing to overwrite nonempty output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    status, results = tsv_read(args.arm_status), tsv_read(args.arm_results)
    terminal = safe_status_rows(status, results)
    terminal_by_key = {arm_key(row): row for row in terminal}
    f0_rows = {row["roi"]: row for row in terminal if row["arm"] == "F0" and row["lseg"] == "NONE"}
    if set(f0_rows) != {"prefill", "decode1"}:
        raise RuntimeError("both terminal C5 F0 baselines are required")

    all_kernels: dict[str, list[Kernel]] = {}
    sidecar_data_by_roi: dict[str, dict] = {}
    index_rows: list[dict] = []
    provenance_lines = ["# C12 Operator-aware provenance", "", f"Consumed formal C12 source commit: `{args.source_commit}`.",
                        "Only rows marked terminal `PASS` in both ARM_STATUS.tsv and ARM_RESULTS.tsv were parsed.", ""]
    provenance_lines += ["## Frozen execution identity", "", *[f"- {key}: `{value}`" for key, value in FROZEN.items()], ""]
    for roi in ("prefill", "decode1"):
        run_dir = Path(f0_rows[roi]["run_dir"])
        trace_list = run_dir / "traces/kernelslist.g"
        trace_dir = run_dir / "traces"
        stage_run = args.stage_root / ("m4a-llama-prefill-20260902T182016Z" if roi == "prefill" else "m4a-llama-decode1-20260903T004138Z")
        semantic_dir = args.stage_root / ("prefill-semantic" if roi == "prefill" else "decode1-semantic")
        semantic_list = semantic_dir / "compute-only-kernelslist.g"
        semantic_manifest = semantic_dir / "semantic-full-kernel-manifest.json"
        sidecar = stage_run / "allocation-sidecar.json"
        for path in (trace_list, trace_dir, semantic_list, semantic_manifest, sidecar):
            if not path.exists():
                raise RuntimeError(f"{roi}: missing provenance input {path}")
        listed = trace_list.read_text().splitlines()
        semantic_listed = semantic_list.read_text().splitlines()
        digest = sha256(trace_list)
        if len(listed) != EXPECTED[roi]["count"] or digest != EXPECTED[roi]["sha"] or listed != semantic_listed:
            raise RuntimeError(f"{roi}: C12/semantic compute-only list identity failed")
        semantic_data = json.loads(semantic_manifest.read_text())
        compute_from_raw = [item["raw"] for item in semantic_data["kernels"] if item["classification"] == "COMPUTE"]
        if compute_from_raw != listed:
            raise RuntimeError(f"{roi}: raw semantic manifest NCCL filtering does not reproduce compute list")
        params, starts, address = range_index(sidecar)
        sidecar_data_by_roi[roi] = address["data"]
        if any(not (trace_dir / filename).is_file() for filename in listed):
            raise RuntimeError(f"{roi}: a C12 trace-list entry is unavailable")
        kernels = fast_scan_traces(args.scanner, roi, listed, trace_list, trace_dir, params, address["data"], out)
        raw = run_dir / "run.log"
        raw_rows = raw_kernels(raw)
        markers = [row.marker for row in raw_rows]
        if markers != listed:
            raise RuntimeError(f"{roi}: processing-kernel marker sequence does not exactly match compute-only list")
        for kernel, marker in zip(kernels, raw_rows):
            marker.index = kernel.index
            index_rows.append({"roi": roi, "compute_index": kernel.index, "trace_filename": kernel.filename,
                               "semantic_kernel_name": kernel.semantic_name, "simulator_marker_index": kernel.index,
                               "alignment_status": "PASS" if kernel.header_count == 1 else "FAIL",
                               "evidence": f"list_sha256={digest}; raw_marker={marker.marker}; embedded_header_count={kernel.header_count}; raw_manifest_compute_index_exact"})
        if any(kernel.header_count != 1 for kernel in kernels):
            raise RuntimeError(f"{roi}: a compute trace does not contain exactly one embedded semantic header")
        all_kernels[roi] = kernels
        provenance_lines += [f"## {roi}", "", f"- C12 F0 compute-only list: `{trace_list}`", f"- list SHA-256: `{digest}` ({len(listed)} entries)",
                             f"- semantic derivative: `{semantic_list}` (byte-identical)",
                             f"- raw semantic manifest: `{semantic_manifest}`; raw COMPUTE filtering exactly recreates C12 list (NCCL removal has no index shift)",
                             f"- runtime sidecar: `{sidecar}`; sha256 `{sha256(sidecar)}`; weight base `{address['allocation']['simva_start']}`, size `{address['allocation']['size_bytes']}`, {len(params)} non-overlapping parameter ranges", ""]

    write_tsv(out / "INDEX_ALIGNMENT_AUDIT.tsv",
              ["roi", "compute_index", "trace_filename", "semantic_kernel_name", "simulator_marker_index", "alignment_status", "evidence"], index_rows)
    (out / "PROVENANCE.md").write_text("\n".join(provenance_lines).rstrip() + "\n")

    map_rows: list[dict] = []
    coverage_rows: list[dict] = []
    f0_characterization: list[dict] = []
    object_rows: list[dict] = []
    translation_rows: list[dict] = []
    cache_rows: list[dict] = []
    kv_audit_rows: list[dict] = []
    raw_by_arm: dict[tuple[str, str, str], tuple[list[RawKernel], list[dict[str, int]]]] = {}

    for roi, kernels in all_kernels.items():
        for kernel in kernels:
            status = "DIRECT" if kernel.direct else "UNRESOLVED"
            map_rows.append({"roi": roi, "compute_index": kernel.index, "trace_filename": kernel.filename,
                             "semantic_kernel_name": kernel.semantic_name, "operator_class": kernel.operator_class,
                             "operator_group": kernel.group, "evidence_kind": kernel.evidence_kind,
                             "evidence_detail": kernel.evidence_detail, "parameter_names": ";".join(kernel.params) if kernel.params else "NONE",
                             "layer_id": kernel.layer_id, "weight_refs": kernel.weight_refs, "kv_refs": kernel.kv_refs,
                             "unknown_refs": kernel.unknown_refs, "weight_unique_pages_64k": len(kernel.pages["WEIGHT"]),
                             "kv_unique_pages_64k": len(kernel.pages["KV_CACHE"]), "classification_status": status})
        f0_key = (roi, "F0", "NONE")
        f0 = terminal_by_key[f0_key]
        validations = json.loads((Path(f0["run_dir"]) / "C12_ARM_VALIDATION.json").read_text())
        raw_rows = raw_kernels(Path(f0["run_dir"]) / "run.log")
        if [row.marker for row in raw_rows] != [kernel.filename for kernel in kernels]:
            raise RuntimeError(f"{roi} F0 marker/map mismatch while parsing telemetry")
        deltas = delta_counters(raw_rows, validations, Path(f0["run_dir"]) / "run.log")
        raw_by_arm[f0_key] = (raw_rows, deltas)
        for i, raw in enumerate(raw_rows):
            if raw.index is None:
                raw.index = i
        direct_kernels = sum(kernel.direct for kernel in kernels)
        total_refs = sum(kernel.weight_refs + kernel.kv_refs + kernel.unknown_refs for kernel in kernels)
        direct_refs = sum(kernel.weight_refs + kernel.kv_refs + kernel.unknown_refs for kernel in kernels if kernel.direct)
        cycles = {i: row.exact.get("gpu_sim_cycle", 0) for i, row in enumerate(raw_rows)}
        insns = {i: row.exact.get("gpu_sim_insn", 0) for i, row in enumerate(raw_rows)}
        for basis, total, direct in (("kernel_count", len(kernels), direct_kernels), ("trace_memory_refs", total_refs, direct_refs),
                                     ("instructions", sum(insns.values()), sum(insns[i] for i, k in enumerate(kernels) if k.direct)),
                                     ("cycles", sum(cycles.values()), sum(cycles[i] for i, k in enumerate(kernels) if k.direct))):
            coverage_rows.append({"roi": roi, "coverage_basis": basis, "direct_fraction": fmt(direct / total if total else 0),
                                  "heuristic_fraction": "0", "unresolved_fraction": fmt((total - direct) / total if total else 0),
                                  "numerator": direct, "denominator": total})
        source = f"{f0['run_dir']}/run.log sha256={f0['raw_log_sha256']}"
        for metric, unit, values, scope in (("kernel_count", "kernels", {k.index: 1 for k in kernels}, "EXACT_PER_KERNEL"),
                                           ("gpu_sim_cycle", "cycles", cycles, "EXACT_PER_KERNEL"),
                                           ("gpu_sim_insn", "instructions", insns, "EXACT_PER_KERNEL")):
            for operator, value in sorted(sum_by_operator(kernels, values).items()):
                add_metric(f0_characterization, roi, operator, metric, scope, unit, value, source)
        for object_name, attribute in (("WEIGHT", "weight_refs"), ("KV_CACHE", "kv_refs"), ("UNKNOWN", "unknown_refs")):
            for operator in sorted({kernel.operator_class for kernel in kernels}):
                selected = [kernel for kernel in kernels if kernel.operator_class == operator]
                refs = sum(getattr(kernel, attribute) for kernel in selected)
                union = set().union(*(kernel.pages[object_name] for kernel in selected)) if selected else set()
                object_rows.append({"roi": roi, "operator_class": operator, "object_class": object_name,
                                    "metric": "lane_references", "metric_scope": "TRACE_DERIVED", "unit": "lane_refs",
                                    "value": refs, "source": f"immutable traces; C12 list sha256={EXPECTED[roi]['sha']}"})
                object_rows.append({"roi": roi, "operator_class": operator, "object_class": object_name,
                                    "metric": "unique_64kb_pages", "metric_scope": "TRACE_DERIVED", "unit": "pages",
                                    "value": len(union), "source": f"immutable traces; C12 list sha256={EXPECTED[roi]['sha']}"})
        # Translation values come from end-of-kernel cumulative snapshots after
        # a final-sidecar conservation check, so every delta is exact per kernel.
        translation_names = ("vm_l1_tlb_accesses", "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l2_tlb_accesses",
                             "vm_l2_tlb_hits", "vm_l2_tlb_misses", "vm_translation_walk_starts", "vm_pte_requests",
                             "vm_pte_l2_only_responses", "vm_pte_dram_responses", "vm_translation_requester_latency_cycles_total")
        for metric in translation_names:
            values = {i: delta.get(metric, 0) for i, delta in enumerate(deltas)}
            if metric not in deltas[-1]:
                continue
            for operator, value in sorted(sum_by_operator(kernels, values).items()):
                translation_rows.append({"roi": roi, "operator_class": operator, "metric": metric,
                                         "metric_scope": "EXACT_PER_KERNEL", "unit": "events" if "cycles" not in metric else "cycles",
                                         "value": value, "source": source})
        # m4c KERNEL-scope cache rows are emitted for the current kernel.  The
        # distinct FIXED_WINDOW_PARTIAL rows are intentionally excluded: they
        # cannot be assigned to a kernel without inventing attribution.
        cache_sum: Counter = Counter()
        for kernel, raw in zip(kernels, raw_rows):
            for (level, object_name, outcome), value in raw.cache.items():
                cache_sum[(kernel.operator_class, level, object_name, outcome)] += value
        for (operator, level, object_name, outcome), value in sorted(cache_sum.items()):
            cache_rows.append({"roi": roi, "operator_class": operator, "cache_level": "L1D" if level == "m4c_telemetry" else "L2",
                               "object_class": object_name, "outcome": outcome, "metric_scope": "EXACT_PER_KERNEL",
                               "unit": "cache_transactions", "value": value, "source": source + "; scope=KERNEL only"})

        # The taxonomy assigns FFN/Embedding from a direct Weight parameter
        # range, whereas DATA_KV_CACHE is a runtime object-range label.  Audit
        # their conjunction explicitly: it establishes what was observed in a
        # single trace/marker, but never promotes that fact to semantic FFN/KV
        # ownership or a fusion claim.
        events = selected_kv_events(sidecar_data_by_roi[roi], roi)
        event_bytes, event_union_bytes, event_spans = interval_union_stats(events)
        event_contract = "; ".join(f"{phase}/step{step}/{state}={count}" for (phase, step, state), count in
                                   sorted(Counter((row.get("phase"), row.get("step"), row.get("state")) for row in events).items()))
        for operator in ("FFN_MLP", "EMBEDDING_OUTPUT"):
            selected = [kernel for kernel in kernels if kernel.operator_class == operator]
            cross_object = [kernel for kernel in selected if kernel.weight_refs and kernel.kv_refs]
            cross_indices = {kernel.index for kernel in cross_object}

            def cache_value(rows: list[RawKernel], level: str, outcome: str | None = None) -> int:
                return sum(value for raw in rows for (cache_level, object_name, cache_outcome), value in raw.cache.items()
                           if cache_level == level and object_name == "DATA_KV_CACHE" and
                           (outcome is None or cache_outcome == outcome))

            class_raw = [raw_rows[kernel.index] for kernel in selected]
            cross_raw = [raw_rows[index] for index in sorted(cross_indices)]
            names = ";".join(sorted({semantic_family(kernel) for kernel in cross_object})) if cross_object else "NONE"
            kv_audit_rows.append({
                "roi": roi,
                "operator_class": operator,
                "class_kernel_count": len(selected),
                "same_kernel_weight_and_kv_trace_count": len(cross_object),
                "same_kernel_compute_indices": ",".join(str(kernel.index) for kernel in cross_object) if cross_object else "NONE",
                "same_kernel_semantic_families": names,
                "same_kernel_weight_lane_refs": sum(kernel.weight_refs for kernel in cross_object),
                "same_kernel_kv_lane_refs": sum(kernel.kv_refs for kernel in cross_object),
                "same_kernel_kv_unique_64kb_pages": len(set().union(*(kernel.pages["KV_CACHE"] for kernel in cross_object))) if cross_object else 0,
                "class_l1d_kv_transactions": cache_value(class_raw, "m4c_telemetry"),
                "same_kernel_l1d_kv_transactions": cache_value(cross_raw, "m4c_telemetry"),
                "class_l2_kv_transactions": cache_value(class_raw, "m4c_telemetry_l2"),
                "same_kernel_l2_kv_transactions": cache_value(cross_raw, "m4c_telemetry_l2"),
                "same_kernel_l2_kv_hits": cache_value(cross_raw, "m4c_telemetry_l2", "HIT"),
                "same_kernel_l2_kv_misses": cache_value(cross_raw, "m4c_telemetry_l2", "MISS"),
                "same_kernel_l2_kv_reservation_fails": cache_value(cross_raw, "m4c_telemetry_l2", "RESERVATION_FAIL"),
                "selected_runtime_kv_events": len(events),
                "runtime_event_contract": event_contract,
                "runtime_kv_event_bytes": event_bytes,
                "runtime_kv_union_bytes": event_union_bytes,
                "runtime_kv_merged_spans": event_spans,
                "runtime_kv_interval_overlap_bytes": event_bytes - event_union_bytes,
                "lifetime_limit": "all selected events end_phase=UNKNOWN_ACTIVE; range matching is not per-instruction tensor-lifetime attribution",
                "auditable_conclusion": "observed same-kernel direct-Weight and KV-runtime-range intersections; no semantic FFN/Embedding-to-KV ownership or fusion conclusion",
            })

    write_tsv(out / "KERNEL_OPERATOR_MAP.tsv",
              ["roi", "compute_index", "trace_filename", "semantic_kernel_name", "operator_class", "operator_group", "evidence_kind",
               "evidence_detail", "parameter_names", "layer_id", "weight_refs", "kv_refs", "unknown_refs", "weight_unique_pages_64k",
               "kv_unique_pages_64k", "classification_status"], map_rows)
    write_tsv(out / "OPERATOR_COVERAGE.tsv", ["roi", "coverage_basis", "direct_fraction", "heuristic_fraction", "unresolved_fraction", "numerator", "denominator"], coverage_rows)
    write_tsv(out / "F0_OPERATOR_CHARACTERIZATION.tsv", ["roi", "operator_class", "metric", "metric_scope", "unit", "numerator", "denominator", "value", "source"], f0_characterization)
    write_tsv(out / "F0_OPERATOR_OBJECT_SUMMARY.tsv", ["roi", "operator_class", "object_class", "metric", "metric_scope", "unit", "value", "source"], object_rows)
    write_tsv(out / "F0_OPERATOR_TRANSLATION_SUMMARY.tsv", ["roi", "operator_class", "metric", "metric_scope", "unit", "value", "source"], translation_rows)
    write_tsv(out / "F0_OPERATOR_CACHE_SUMMARY.tsv", ["roi", "operator_class", "cache_level", "object_class", "outcome", "metric_scope", "unit", "value", "source"], cache_rows)
    write_tsv(out / "KV_CLASS_TRANSACTION_AUDIT.tsv", [
        "roi", "operator_class", "class_kernel_count", "same_kernel_weight_and_kv_trace_count", "same_kernel_compute_indices",
        "same_kernel_semantic_families", "same_kernel_weight_lane_refs", "same_kernel_kv_lane_refs",
        "same_kernel_kv_unique_64kb_pages", "class_l1d_kv_transactions", "same_kernel_l1d_kv_transactions",
        "class_l2_kv_transactions", "same_kernel_l2_kv_transactions", "same_kernel_l2_kv_hits",
        "same_kernel_l2_kv_misses", "same_kernel_l2_kv_reservation_fails", "selected_runtime_kv_events",
        "runtime_event_contract", "runtime_kv_event_bytes", "runtime_kv_union_bytes", "runtime_kv_merged_spans",
        "runtime_kv_interval_overlap_bytes", "lifetime_limit", "auditable_conclusion",
    ], kv_audit_rows)

    # OA3: parse only the terminal PASS rows, use the immutable F0 mapping for
    # every arm, and retain full-ROI performance separately from per-kernel data.
    arm_rows: list[dict] = []
    arm_metrics: dict[tuple[str, str, str], dict[str, dict[str, int]]] = {}
    for arm in terminal:
        key = arm_key(arm)
        roi, arm_name, lseg = key
        kernels = all_kernels[roi]
        if key in raw_by_arm:
            raw_rows, deltas = raw_by_arm[key]
        else:
            validation = json.loads((Path(arm["run_dir"]) / "C12_ARM_VALIDATION.json").read_text())
            raw_rows = raw_kernels(Path(arm["run_dir"]) / "run.log")
            if [row.marker for row in raw_rows] != [kernel.filename for kernel in kernels]:
                raise RuntimeError(f"{key}: marker sequence does not match F0-proven operator map")
            deltas = delta_counters(raw_rows, validation, Path(arm["run_dir"]) / "run.log")
            raw_by_arm[key] = (raw_rows, deltas)
        source = arm["raw_log_sha256"]
        metrics: dict[str, dict[str, int]] = {}
        metric_values = {
            "gpu_sim_cycle": {i: raw.exact.get("gpu_sim_cycle", 0) for i, raw in enumerate(raw_rows)},
            "vm_weight_segment_hits": {i: delta.get("vm_weight_segment_hits", 0) for i, delta in enumerate(deltas)},
            "vm_weight_segment_l2_suppressed": {i: delta.get("vm_weight_segment_l2_suppressed", 0) for i, delta in enumerate(deltas)},
            "vm_l2_tlb_subentry_hits": {i: delta.get("vm_l2_tlb_subentry_hits", 0) for i, delta in enumerate(deltas)},
            "vm_l2_tlb_subentry_misses": {i: delta.get("vm_l2_tlb_subentry_misses", 0) for i, delta in enumerate(deltas)},
        }
        for metric, values in metric_values.items():
            if metric != "gpu_sim_cycle" and metric not in deltas[-1]:
                continue
            metrics[metric] = sum_by_operator(kernels, values)
            for operator, value in sorted(metrics[metric].items()):
                arm_rows.append({"roi": roi, "arm": arm_name, "lseg": lseg, "operator_class": operator, "metric": metric,
                                 "metric_scope": "EXACT_PER_KERNEL", "unit": "cycles" if metric == "gpu_sim_cycle" else "events",
                                 "value": value, "source_raw_log_sha256": source})
        # The formal C12 cycles are intentionally one FULL_ROI_ONLY row; this
        # prevents a sum of operator cycles from being mistaken for a cache or
        # translation counter and gives reviewers the immutable result anchor.
        arm_rows.append({"roi": roi, "arm": arm_name, "lseg": lseg, "operator_class": "FULL_ROI", "metric": "gpu_tot_sim_cycle",
                         "metric_scope": "FULL_ROI_ONLY", "unit": "cycles", "value": arm["result_gpu_tot_sim_cycle"], "source_raw_log_sha256": source})
        arm_rows.append({"roi": roi, "arm": arm_name, "lseg": lseg, "operator_class": "FULL_ROI", "metric": "speedup_vs_f0",
                         "metric_scope": "FULL_ROI_ONLY", "unit": "ratio", "value": arm["result_speedup_vs_f0"], "source_raw_log_sha256": source})
        arm_metrics[key] = metrics

    delta_rows: list[dict] = []
    for roi in ("prefill", "decode1"):
        for comparison, baseline, candidate in comparison_pairs(terminal, roi):
            left, right = arm_key(baseline), arm_key(candidate)
            for metric in sorted(set(arm_metrics[left]) & set(arm_metrics[right])):
                operators = sorted(set(arm_metrics[left][metric]) | set(arm_metrics[right][metric]))
                for operator in operators:
                    a, b = arm_metrics[left][metric].get(operator, 0), arm_metrics[right][metric].get(operator, 0)
                    delta_rows.append({"roi": roi, "comparison": comparison, "operator_class": operator, "metric": metric,
                                       "baseline_value": a, "candidate_value": b, "delta_abs": b - a,
                                       "delta_rel": fmt((b - a) / a) if a else "NA", "claim_scope": "MEASURED_OPERATOR_FACT"})
            a, b = float(baseline["result_gpu_tot_sim_cycle"]), float(candidate["result_gpu_tot_sim_cycle"])
            delta_rows.append({"roi": roi, "comparison": comparison, "operator_class": "FULL_ROI", "metric": "gpu_tot_sim_cycle",
                               "baseline_value": fmt(a), "candidate_value": fmt(b), "delta_abs": fmt(b - a), "delta_rel": fmt((b - a) / a),
                               "claim_scope": "FULL_ROI_ONLY"})

    sensitivity_rows: list[dict] = []
    for roi in ("prefill", "decode1"):
        for family in ("F7", "F8"):
            for lseg in ("5", "10", "20"):
                key = (roi, family, lseg)
                if key not in arm_metrics:
                    continue
                for metric, by_operator in arm_metrics[key].items():
                    if metric not in {"gpu_sim_cycle", "vm_weight_segment_hits", "vm_weight_segment_l2_suppressed", "vm_l2_tlb_subentry_hits"}:
                        continue
                    for operator, value in sorted(by_operator.items()):
                        sensitivity_rows.append({"roi": roi, "arm_family": family, "lseg": lseg, "operator_class": operator,
                                                 "metric": metric, "value": value,
                                                 "note": "exact per-kernel raw-log attribution; no causal performance claim"})
                result = terminal_by_key.get(key)
                if result:
                    sensitivity_rows.append({"roi": roi, "arm_family": family, "lseg": lseg, "operator_class": "FULL_ROI",
                                             "metric": "gpu_tot_sim_cycle", "value": result["result_gpu_tot_sim_cycle"],
                                             "note": "full-ROI anchor; compare only within same ROI"})

    write_tsv(out / "ARM_OPERATOR_CHARACTERIZATION.tsv",
              ["roi", "arm", "lseg", "operator_class", "metric", "metric_scope", "unit", "value", "source_raw_log_sha256"], arm_rows)
    write_tsv(out / "OPERATOR_ARM_DELTAS.tsv",
              ["roi", "comparison", "operator_class", "metric", "baseline_value", "candidate_value", "delta_abs", "delta_rel", "claim_scope"], delta_rows)
    write_tsv(out / "LSEG_OPERATOR_SENSITIVITY.tsv",
              ["roi", "arm_family", "lseg", "operator_class", "metric", "value", "note"], sensitivity_rows)

    observability = """# C12 operator-aware observability audit

## Exact per kernel

- `Processing kernel` markers are ordered exactly as the C12 compute-only list; `INDEX_ALIGNMENT_AUDIT.tsv` records every mapping.
- `gpu_sim_cycle` and `gpu_sim_insn` appear once per processed kernel in each terminal raw log.
- `vm_*` translation, Segment, and Sub-entry fields are end-of-kernel cumulative snapshots.  This parser differences adjacent snapshots and verifies selected final totals against immutable `C12_ARM_VALIDATION.json`; the resulting deltas are exact per-kernel events.
- `m4c_telemetry` and `m4c_telemetry_l2` rows with scope `KERNEL` are exact per-kernel cache transactions.  Reservation fails remain a distinct outcome.

## Trace derived

- Weight/KV/UNKNOWN lane references and 64 KiB page sets are reconstructed from all predicated lanes in immutable trace records, using runtime SimVA ranges.  These are trace references, not coalesced cache transactions.
- Direct parameter labels are derived only by exact intersection of those trace addresses with `weight_layout` ranges.

## Full ROI only / deliberately unattributed

- Formal C12 cycles and speedup are also retained as `FULL_ROI_ONLY` anchors in `ARM_OPERATOR_CHARACTERIZATION.tsv`.
- `m4c_*` rows scoped `FIXED_WINDOW_PARTIAL` are intentionally excluded from operator cache totals: their scope cannot be made kernel-exact.
- No counter is divided by kernel count, trace refs, or cycle share.  No filename is used for semantic classification.
"""
    (out / "OBSERVABILITY_AUDIT.md").write_text(observability)
    print(f"PASS operator-aware outputs: {out}")
    print(f"terminal_pass_arms={len(terminal)}")


if __name__ == "__main__":
    main()
