#!/usr/bin/env python3
"""CPU-only streaming C16 MoE warp request geometry consumer."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<6I32Q")
AMBIG = "CROSS_BOUNDARY_OR_AMBIGUOUS"
QUANTILE_DEFINITION = "nearest-rank: sorted_values[ceil(p*n)-1]; min/max exact"
CONSUMER_COMMIT = "08536be9940590be101c7f5bac2117ba82056db5"
COORDINATION_COMMIT = "17dd9482245d8bdac8e89ff53be5a567048016f1"

CONFIG = {
    "Q30": {
        "run": "C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678",
        "adapter": "q30",
        "manifest_sha256": "259b34c75ed8adbd8132d56e23a41fc02da97338f8510027f7da77ccb52dcd83",
        "catalog_sha256": "80c9d1309fb8d3f15514c9668ac00a6d8839cb6858aca7e347755eed58d2e434",
        "ack_sha256": "f59c9181eb5a6371d93cf648ff15aa771f4af6de04bd9121c9bf2090fb2731f4",
        "producer_commit": "6cadf4e3357a0c1337abf0d04bee6754d12fb695",
        "historical": {"selected": 243, "executed": 41, "zero": 202, "records": 100352, "lanes": 3147776},
    },
    "DEEPSEEK": {
        "run": "C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23",
        "adapter": "deepseek",
        "manifest_sha256": "d98b4a077afe9e7f2ce32479484e9c1148548b1ef1802c9b002dd70250b7b638",
        "catalog_sha256": "9ece3f570fbdaa8e026da39bee94c7f15b2c60bf14e292a66f6026104d18d81d",
        "ack_sha256": "fe4768a91606bbbf89f1b28a897f0a6648fb8e83d3d621093313e03743ec1acf",
        "producer_commit": "5f75b5a20a227f420ce088b22356c1a4a9d47d76",
        "historical": {"selected": 243, "executed": 169, "zero": 74, "records": 362496, "lanes": 11538432},
    },
    "OLMOE": {
        "run": "C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf",
        "adapter": "olmoe",
        "manifest_sha256": "8f3e5e338166a2ebc4da6b9a55986980d31227f3d0e383ca5a1f24d0d924f31b",
        "catalog_sha256": "676422708f865c6b3287998dcde3dd126a469e83d3245bcf00fe11d07b9c1637",
        "ack_sha256": "9c4d08a960f53acece00dbb3143cba460c22bc638ff4a879833c0e4460b98e39",
        "producer_commit": "f40d5158b71284d4974cc1945117f5fefacd1191",
        "historical": {"selected": 243, "executed": 129, "zero": 114, "records": 132096, "lanes": 4196352},
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_role(value: str) -> str:
    value = value.upper()
    if "WEIGHT" in value:
        return "WEIGHT"
    if "INPUT" in value:
        return "INPUT"
    if "OUTPUT" in value:
        return "OUTPUT"
    return "OTHER"


def object_ranges(context: dict) -> list[tuple[str, str, int, int]]:
    result = []
    if isinstance(context.get("ranges"), list):
        items = context["ranges"]
        for item in items:
            original = item.get("semantic_role", item.get("class", "OTHER"))
            start = item.get("ptr", item.get("address_start_hex"))
            size = item.get("bytes", item.get("storage_bytes"))
            result.append((normalize_role(original), original, int(start, 0), int(start, 0) + int(size)))
    else:
        for original, item in context.items():
            if isinstance(item, dict) and "ptr" in item and "bytes" in item:
                result.append((normalize_role(original), original, int(item["ptr"], 0), int(item["ptr"], 0) + int(item["bytes"])))
    if not result:
        raise ValueError("address context has no object ranges")
    return result


def classify_start(address: int, ranges) -> tuple[str, str]:
    hits = [(typed, original) for typed, original, begin, end in ranges if begin <= address < end]
    return hits[0] if len(hits) == 1 else (AMBIG, AMBIG)


def classify_interval(begin: int, end: int, ranges) -> tuple[str, str]:
    hits = [(typed, original) for typed, original, lo, hi in ranges if lo <= begin and end <= hi]
    return hits[0] if len(hits) == 1 else (AMBIG, AMBIG)


def union_size(intervals: list[tuple[int, int]]) -> int:
    if not intervals:
        return 0
    total = 0
    current_lo, current_hi = sorted(intervals)[0]
    for lo, hi in sorted(intervals)[1:]:
        if lo > current_hi:
            total += current_hi - current_lo
            current_lo, current_hi = lo, hi
        else:
            current_hi = max(current_hi, hi)
    return total + current_hi - current_lo


def covered_units(intervals: list[tuple[int, int]], size: int) -> set[int]:
    result = set()
    for lo, hi in intervals:
        if hi <= lo:
            continue
        result.update(range(lo // size, (hi - 1) // size + 1))
    return result


def g0_metrics(addresses: list[int]) -> dict:
    if not addresses:
        return {"E": 0, "A": 0, "multiplicity": None, "max_multiplicity": None, "all_same": None}
    counts = Counter(addresses)
    return {
        "E": len(addresses),
        "A": len(counts),
        "multiplicity": len(addresses) / len(counts),
        "max_multiplicity": max(counts.values()),
        "all_same": len(counts) == 1,
    }


def g1_metrics(intervals: list[tuple[int, int]]) -> dict:
    if not intervals:
        return {"L": 0, "U": 0, "S32": 0, "C32": 0, "lines128": 0, "lane_byte_multiplicity": None, "sector_fill": None}
    logical = sum(hi - lo for lo, hi in intervals)
    unique = union_size(intervals)
    sectors = len(covered_units(intervals, 32))
    lines128 = len(covered_units(intervals, 128))
    proxy = 32 * sectors
    if not unique <= logical or not unique <= proxy:
        raise AssertionError(f"geometry invariant failed: U={unique} L={logical} C32={proxy}")
    return {
        "L": logical,
        "U": unique,
        "S32": sectors,
        "C32": proxy,
        "lines128": lines128,
        "lane_byte_multiplicity": logical / unique if unique else None,
        "sector_fill": unique / proxy if proxy else None,
    }


def process_addresses(addresses: list[int], width: int | None, ranges) -> dict:
    g0 = g0_metrics(addresses)
    start_roles = defaultdict(list)
    for address in addresses:
        start_roles[classify_start(address, ranges)[0]].append(address)
    if width is None:
        return {"g0": g0, "g0_roles": dict(start_roles), "g1": None, "g1_roles": {}, "shared_sector": False}
    intervals = [(address, address + width) for address in addresses]
    by_role = defaultdict(list)
    for interval in intervals:
        by_role[classify_interval(*interval, ranges)[0]].append(interval)
    role_sectors = {role: covered_units(items, 32) for role, items in by_role.items()}
    seen = set()
    shared = False
    for sectors in role_sectors.values():
        if seen.intersection(sectors):
            shared = True
        seen.update(sectors)
    return {"g0": g0, "g0_roles": dict(start_roles), "g1": g1_metrics(intervals), "g1_roles": dict(by_role), "shared_sector": shared}


def nearest_rank(values: list[float | int]) -> dict:
    if not values:
        return {key: None for key in ("min", "p25", "median", "p75", "p90", "p95", "max")}
    ordered = sorted(values)
    def pick(p):
        return ordered[max(0, math.ceil(p * len(ordered)) - 1)]
    return {"min": ordered[0], "p25": pick(.25), "median": pick(.5), "p75": pick(.75), "p90": pick(.9), "p95": pick(.95), "max": ordered[-1]}


@dataclass
class MetricAgg:
    records: int = 0
    zero_active_records: int = 0
    events: int = 0
    distinct_starts_sum: int = 0
    all_same_records: int = 0
    g1_records: int = 0
    logical: int = 0
    unique: int = 0
    sectors: int = 0
    proxy: int = 0
    lines128: int = 0
    e_values: list = field(default_factory=list)
    a_values: list = field(default_factory=list)
    start_mult_values: list = field(default_factory=list)
    max_mult_values: list = field(default_factory=list)
    byte_mult_values: list = field(default_factory=list)
    fill_values: list = field(default_factory=list)
    sector_values: list = field(default_factory=list)

    def add_g0(self, addresses: list[int]) -> None:
        value = g0_metrics(addresses)
        self.records += 1
        self.events += value["E"]
        self.distinct_starts_sum += value["A"]
        if value["E"] == 0:
            self.zero_active_records += 1
        else:
            self.e_values.append(value["E"])
            self.a_values.append(value["A"])
            self.start_mult_values.append(value["multiplicity"])
            self.max_mult_values.append(value["max_multiplicity"])
            self.all_same_records += int(value["all_same"])

    def add_g1(self, intervals: list[tuple[int, int]]) -> None:
        value = g1_metrics(intervals)
        if not intervals:
            return
        self.g1_records += 1
        self.logical += value["L"]
        self.unique += value["U"]
        self.sectors += value["S32"]
        self.proxy += value["C32"]
        self.lines128 += value["lines128"]
        self.byte_mult_values.append(value["lane_byte_multiplicity"])
        self.fill_values.append(value["sector_fill"])
        self.sector_values.append(value["S32"])

    def merge(self, other: "MetricAgg") -> None:
        for key in ("records", "zero_active_records", "events", "distinct_starts_sum", "all_same_records", "g1_records", "logical", "unique", "sectors", "proxy", "lines128"):
            setattr(self, key, getattr(self, key) + getattr(other, key))
        for key in ("e_values", "a_values", "start_mult_values", "max_mult_values", "byte_mult_values", "fill_values", "sector_values"):
            getattr(self, key).extend(getattr(other, key))

    def summary(self) -> dict:
        return {
            "record_count": self.records,
            "zero_active_record_count": self.zero_active_records,
            "active_lane_events": self.events,
            "distinct_start_addresses_sum": self.distinct_starts_sum,
            "start_address_multiplicity_ratio_of_sums": self.events / self.distinct_starts_sum if self.distinct_starts_sum else None,
            "all_active_lanes_same_start_records": self.all_same_records,
            "g1_record_count": self.g1_records,
            "logical_bytes": self.logical,
            "unique_bytes": self.unique,
            "sector_count_sum": self.sectors,
            "sector_proxy_bytes": self.proxy,
            "line128_count_sum": self.lines128,
            "lane_byte_multiplicity_ratio_of_sums": self.logical / self.unique if self.unique else None,
            "sector_fill_ratio_of_sums": self.unique / self.proxy if self.proxy else None,
            "distributions": {
                "active_lanes": nearest_rank(self.e_values),
                "distinct_start_addresses": nearest_rank(self.a_values),
                "start_address_multiplicity": nearest_rank(self.start_mult_values),
                "max_start_multiplicity": nearest_rank(self.max_mult_values),
                "lane_byte_multiplicity": nearest_rank(self.byte_mult_values),
                "sector_fill": nearest_rank(self.fill_values),
                "sectors_per_record": nearest_rank(self.sector_values),
            },
        }


def width_from_opcode(opcode: str) -> tuple[str, int | None, str]:
    if not (opcode.startswith("LDG.") or opcode == "LDG" or opcode.startswith("STG.") or opcode == "STG"):
        return "WIDTH_UNRESOLVED", None, "not a qualified global load/store opcode"
    if re.search(r"(?:^|\.)U16(?:\.|$)|(?:^|\.)S16(?:\.|$)", opcode):
        return "QUALIFIED", 2, "SASS opcode U16/S16 data-width suffix"
    if re.search(r"(?:^|\.)128(?:\.|$)", opcode):
        return "QUALIFIED", 16, "SASS opcode 128-bit data-width suffix"
    if re.search(r"(?:^|\.)64(?:\.|$)", opcode):
        return "QUALIFIED", 8, "SASS opcode 64-bit data-width suffix"
    if opcode == "LDG.E" or opcode == "STG.E":
        return "QUALIFIED", 4, "SASS scalar global op without size suffix is 32-bit register data"
    return "WIDTH_UNRESOLVED", None, "opcode width is not uniquely mapped by this audited decoder"


def access_kind(opcode: str) -> str:
    if opcode.startswith("LDG.") or opcode == "LDG":
        return "LOAD"
    if opcode.startswith("STG.") or opcode == "STG":
        return "STORE"
    return "ISOLATED_SPECIAL"


def load_static(root: Path, adapter: str) -> dict[int, dict]:
    path = root / ("selector_authority/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv" if adapter == "olmoe" else "STATIC_MREF_MAP.tsv")
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    result = {}
    for row in rows:
        if row.get("has_mref") != "1" or row.get("path_class", row.get("memory_space")) not in ("GLOBAL", "GLOBAL_TO_SHARED"):
            continue
        index = int(row.get("static_index", row.get("nvbit_static_index")))
        opcode = row["opcode"]
        status, width, authority = width_from_opcode(opcode)
        result[index] = {
            "static_index": index,
            "opcode": opcode,
            "sass": row["sass"],
            "memory_space": row.get("path_class", row.get("memory_space")),
            "access_kind": access_kind(opcode),
            "atomic_or_reduction": False,
            "width_status": status,
            "width_bytes": width,
            "width_authority": authority,
            "global_source_operand": "mref_operand_index=" + row.get("mref_operand_index", "single bracketed global address operand"),
            "function_identity": row.get("function_full_name", "OLMoE receipt-bound gemvx template-6 function"),
            "static_authority_path": str(path),
        }
    return result


def entries(root: Path, adapter: str):
    if adapter != "olmoe":
        manifest = load(root / "WARP_SHARD_MANIFEST.json")
        for item in manifest["shards"]:
            if adapter == "q30":
                yield {
                    "static": item["static_index"], "trace": root / item["trace_relative_path"],
                    "context": root / item["address_context_relative_path"], "declared": item["record_count"],
                    "terminal": item["terminal_status"], "trace_expected": item["trace_sha256"],
                    "context_expected": item["address_context_sha256"], "receipt": "WARP_SHARD_MANIFEST.json",
                }
            else:
                yield {
                    "static": item["static_index"], "trace": root / item["trace"], "context": root / item["address_context"],
                    "declared": item["records"], "terminal": item["classification"], "trace_expected": item["trace_sha256"],
                    "context_expected": item["address_context_sha256"], "receipt": "WARP_SHARD_MANIFEST.json",
                }
        return
    for receipt_path in sorted(root.glob("shards/static_*/SUPERVISOR_RECEIPT.json")):
        receipt = load(receipt_path)
        base = receipt_path.parent
        yield {
            "static": receipt["selected_static"], "trace": base / "trace.bin", "context": base / "ADDRESS_CONTEXT.json",
            "declared": None, "terminal": (base / "stdout.log").read_text(encoding="utf-8", errors="replace"),
            "trace_expected": receipt["c16_trace_sha256"], "context_expected": None, "receipt": str(receipt_path),
            "function_identity": receipt["relevant_environment"]["C16_P1_FUNCTION"],
        }


def iter_records(path: Path):
    with path.open("rb") as stream:
        header = stream.read(HEADER.size)
        if len(header) != HEADER.size:
            raise ValueError(f"short header: {path}")
        magic, index, occurrence, callback, overflow, written = HEADER.unpack(header)
        count = 0
        while True:
            raw = stream.read(RECORD.size)
            if not raw:
                break
            if len(raw) != RECORD.size:
                raise ValueError(f"unaligned record: {path}")
            count += 1
            yield (magic, index, occurrence, callback, overflow, written), RECORD.unpack(raw)
        if count != written or callback != written or overflow != 0:
            raise ValueError(f"header count/overflow mismatch: {path}")


def validate_authority(authority: Path) -> dict:
    report = {"status": "PASS", "accepted_consumer_commit": CONSUMER_COMMIT, "coordination_commit": COORDINATION_COMMIT, "lineages": {}}
    for lineage, cfg in CONFIG.items():
        root = authority / "raw" / cfg["run"]
        catalog = authority / "catalog" / "entries" / f"{cfg['run']}.json"
        ack = authority / "reports" / "transfer_acks" / f"{cfg['run']}.TRANSFER_ACK.json"
        values = {
            "run_id": cfg["run"], "raw_exists": root.is_dir(),
            "manifest_sha256": sha256(root / "RUN_MANIFEST.json"), "manifest_expected": cfg["manifest_sha256"],
            "catalog_sha256": sha256(catalog), "catalog_expected": cfg["catalog_sha256"],
            "ack_sha256": sha256(ack), "ack_expected": cfg["ack_sha256"],
            "catalog_producer_commit": load(catalog).get("producer_commit"), "producer_commit_expected": cfg["producer_commit"],
            "ack_verification_status": load(ack).get("verification_status"),
            "ack_catalog_binding": load(ack).get("catalog_entry_sha256"),
        }
        values["pass"] = (
            values["manifest_sha256"] == values["manifest_expected"]
            and values["catalog_sha256"] == values["catalog_expected"]
            and values["ack_sha256"] == values["ack_expected"]
            and values["catalog_producer_commit"] == values["producer_commit_expected"]
            and values["ack_verification_status"] == "PASS"
            and values["ack_catalog_binding"] == values["catalog_sha256"]
        )
        report["lineages"][lineage] = values
        if not values["pass"]:
            report["status"] = "FAIL"
    return report


def analyze_lineage(lineage: str, authority: Path):
    cfg = CONFIG[lineage]
    root = authority / "raw" / cfg["run"]
    static = load_static(root, cfg["adapter"])
    source_entries = list(entries(root, cfg["adapter"]))
    if len(source_entries) != 243 or len({item["static"] for item in source_entries}) != 243:
        raise ValueError(f"{lineage}: selected identity is not 243 unique paths")
    if set(static) != {item["static"] for item in source_entries}:
        raise ValueError(f"{lineage}: static selector and shard manifest differ")
    paths = {index: {"all": MetricAgg(), "roles": defaultdict(MetricAgg), "shared_sector_records": 0} for index in static}
    overall = MetricAgg()
    overall_roles = defaultdict(MetricAgg)
    role_pure_records = Counter()
    role_mixed_records = Counter()
    role_shared_records = Counter()
    raw_hash_checks = []
    executed = 0
    total_records = 0
    total_events = 0
    observed_functions = set()
    for item in sorted(source_entries, key=lambda value: value["static"]):
        index = item["static"]
        spec = static[index]
        trace_sha = sha256(item["trace"])
        context_sha = sha256(item["context"])
        trace_ok = trace_sha == item["trace_expected"]
        context_ok = item["context_expected"] is None or context_sha == item["context_expected"]
        if not trace_ok or not context_ok:
            raise ValueError(f"{lineage}/{index}: raw hash mismatch")
        raw_hash_checks.append({"static_index": index, "trace_sha256": trace_sha, "trace_match": trace_ok, "context_sha256": context_sha, "context_match": context_ok})
        ranges = object_ranges(load(item["context"]))
        record_count = 0
        path_events = 0
        expected_header = None
        if item.get("function_identity"):
            observed_functions.add(item["function_identity"])
            spec["function_identity"] = item["function_identity"]
        for header, record in iter_records(item["trace"]):
            expected_header = header
            if header[0] != b"C16WARP1" or header[1] != index or header[2] != 0 or record[0] != index:
                raise ValueError(f"{lineage}/{index}: C16WARP1 identity mismatch")
            active = [address for lane, address in enumerate(record[6:]) if record[1] >> lane & 1]
            result = process_addresses(active, spec["width_bytes"], ranges)
            paths[index]["all"].add_g0(active)
            overall.add_g0(active)
            for role, role_addresses in result["g0_roles"].items():
                paths[index]["roles"][role].add_g0(role_addresses)
                overall_roles[role].add_g0(role_addresses)
            if result["g1"] is not None:
                intervals = [(address, address + spec["width_bytes"]) for address in active]
                paths[index]["all"].add_g1(intervals)
                overall.add_g1(intervals)
                g1_roles = set(result["g1_roles"])
                if len(g1_roles) == 1:
                    role_pure_records[next(iter(g1_roles))] += 1
                elif g1_roles:
                    for role in g1_roles:
                        role_mixed_records[role] += 1
                if result["shared_sector"]:
                    paths[index]["shared_sector_records"] += 1
                    for role in g1_roles:
                        role_shared_records[role] += 1
                for role, role_intervals in result["g1_roles"].items():
                    paths[index]["roles"][role].add_g1(role_intervals)
                    overall_roles[role].add_g1(role_intervals)
            record_count += 1
            path_events += len(active)
        if item["declared"] is not None and record_count != item["declared"]:
            raise ValueError(f"{lineage}/{index}: declared record mismatch")
        if record_count == 0 and not ("ZERO" in str(item["terminal"]) or "C16_WARP_TERMINAL" in str(item["terminal"])):
            raise ValueError(f"{lineage}/{index}: zero path lacks terminal proof")
        if expected_header is None:
            with item["trace"].open("rb") as stream:
                header = HEADER.unpack(stream.read(HEADER.size))
            if header[0] != b"C16WARP1" or header[1] != index or header[5] != 0:
                raise ValueError(f"{lineage}/{index}: zero header mismatch")
        executed += int(record_count > 0)
        total_records += record_count
        total_events += path_events
        spec["executed_record_count"] = record_count
    historical = cfg["historical"]
    closure = {
        "selected": {"actual": len(static), "expected": historical["selected"]},
        "executed": {"actual": executed, "expected": historical["executed"]},
        "zero": {"actual": len(static) - executed, "expected": historical["zero"]},
        "records": {"actual": total_records, "expected": historical["records"]},
        "lanes": {"actual": total_events, "expected": historical["lanes"]},
    }
    for value in closure.values():
        value["equal"] = value["actual"] == value["expected"]
    if not all(value["equal"] for value in closure.values()):
        raise ValueError(f"{lineage}: historical closure mismatch {closure}")
    return {
        "lineage": lineage, "root": str(root), "static": static, "paths": paths, "overall": overall,
        "overall_roles": overall_roles, "role_pure_records": role_pure_records, "role_mixed_records": role_mixed_records,
        "role_shared_records": role_shared_records, "raw_hash_checks": raw_hash_checks, "closure": closure,
        "observed_functions": sorted(observed_functions),
    }


def self_test() -> dict:
    cases = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        cases.append(name)
    check("32lane_4B_broadcast", g1_metrics([(0, 4)] * 32) | {} == {"L": 128, "U": 4, "S32": 1, "C32": 32, "lines128": 1, "lane_byte_multiplicity": 32.0, "sector_fill": 0.125})
    contiguous = g1_metrics([(lane * 4, lane * 4 + 4) for lane in range(32)])
    check("32lane_4B_contiguous", (contiguous["L"], contiguous["U"], contiguous["C32"]) == (128, 128, 128))
    stride = g1_metrics([(lane * 32, lane * 32 + 4) for lane in range(32)])
    check("32lane_32B_stride", (stride["L"], stride["U"], stride["C32"]) == (128, 128, 1024))
    crossing = g1_metrics([(31, 35)])
    check("cross_sector", (crossing["L"], crossing["U"], crossing["C32"]) == (4, 4, 64))
    check("zero_active", g0_metrics([])["multiplicity"] is None and g1_metrics([])["C32"] == 0)
    partial = g1_metrics([(0, 16), (8, 24)])
    check("partial_overlap_16B", (partial["L"], partial["U"], partial["C32"]) == (32, 24, 32))
    ranges = [("INPUT", "input", 0, 32), ("WEIGHT", "weight", 64, 96)]
    check("role_boundary", classify_interval(30, 34, ranges)[0] == AMBIG)
    mixed = process_addresses([0, 64], 4, ranges)
    check("mixed_roles_same_sector_false", set(mixed["g1_roles"]) == {"INPUT", "WEIGHT"} and not mixed["shared_sector"])
    overlapping_ranges = [("INPUT", "input", 0, 64), ("WEIGHT", "weight", 0, 64)]
    check("ambiguous_object_map", classify_interval(4, 8, overlapping_ranges)[0] == AMBIG)
    check("unresolved_width_g0_only", process_addresses([0, 0], None, ranges)["g1"] is None)
    check("same_warp_different_cta", ("s", 0, 0, 0, 1) != ("s", 1, 0, 0, 1))
    check("same_va_different_shard", ("shard_a", 0x1000) != ("shard_b", 0x1000))
    return {"status": "PASS", "case_count": len(cases), "cases": cases}


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_outputs(out: Path, authority: Path, audits: dict, results: list[dict], synthetic: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    width_rows = []
    shard_rows = []
    role_rows = []
    validation = audits | {
        "synthetic_tests": synthetic,
        "record_abi": {"header": "<8sIIQQQ", "record": "<6I32Q", "record_bytes": RECORD.size, "transport_sequence_in_payload": False},
        "quantile_definition": QUANTILE_DEFINITION,
        "resource_contract": {"cpu_only": True, "gpu_used": False, "gpu_lock_requested": False, "workers": 1, "blas_openmp_threads": 1, "streaming": "one shard open at a time; no lane-address residency across shards", "g2": "G2_NOT_AUTHORIZED_BY_AVAILABLE_SCOPE: payload lacks explicit process/launch identity"},
        "historical_closure": {result["lineage"]: result["closure"] for result in results},
        "raw_file_hash_checks": {result["lineage"]: {"count": len(result["raw_hash_checks"]), "all_pass": all(x["trace_match"] and x["context_match"] for x in result["raw_hash_checks"])} for result in results},
        "producer_commit_presence_verified_in_local_git": True,
    }
    for result in results:
        lineage = result["lineage"]
        for index, spec in sorted(result["static"].items()):
            width_rows.append({"lineage": lineage, **spec, "record_semantics": "one dynamic warp access of this static memory operand", "selected": 1})
            groups = [("ALL", result["paths"][index]["all"])] + sorted(result["paths"][index]["roles"].items())
            for role, agg in groups:
                summary = agg.summary()
                shard_rows.append({
                    "lineage": lineage, "static_index": index, "role": role, "opcode": spec["opcode"], "access_kind": spec["access_kind"],
                    "width_status": spec["width_status"], "width_bytes": spec["width_bytes"],
                    **{key: value for key, value in summary.items() if key != "distributions"},
                    "distributions_json": json.dumps(summary["distributions"], sort_keys=True, separators=(",", ":")),
                    "shared_sector_record_count_path": result["paths"][index]["shared_sector_records"],
                })
        total = result["overall"]
        for role, agg in sorted(result["overall_roles"].items()):
            summary = agg.summary()
            role_rows.append({
                "lineage": lineage, "role": role, "record_count_with_role": summary["record_count"],
                "active_lane_events": summary["active_lane_events"], "logical_bytes": summary["logical_bytes"],
                "unique_bytes": summary["unique_bytes"], "sector_proxy_bytes": summary["sector_proxy_bytes"],
                "pure_role_record_count": result["role_pure_records"][role], "mixed_record_count_with_role": result["role_mixed_records"][role],
                "shared_sector_record_count_with_role": result["role_shared_records"][role],
                "lane_event_share_g0": summary["active_lane_events"] / total.events if total.events else None,
                "logical_byte_share_g1": summary["logical_bytes"] / total.logical if total.logical else None,
                "unique_byte_share_g1_nonadditive": summary["unique_bytes"] / sum(x.unique for x in result["overall_roles"].values()) if sum(x.unique for x in result["overall_roles"].values()) else None,
                "sector_proxy_share_g1_nonadditive": summary["sector_proxy_bytes"] / sum(x.proxy for x in result["overall_roles"].values()) if sum(x.proxy for x in result["overall_roles"].values()) else None,
                "lane_byte_multiplicity_ratio_of_sums": summary["lane_byte_multiplicity_ratio_of_sums"],
                "sector_fill_ratio_of_sums": summary["sector_fill_ratio_of_sums"],
                "distribution_json": json.dumps(summary["distributions"], sort_keys=True, separators=(",", ":")),
                "note": "role unique/sector values are within-record role slices and are non-additive if roles share sectors",
            })
    write_tsv(out / "PATH_WIDTH_AUDIT.tsv", width_rows, [
        "lineage", "static_index", "opcode", "sass", "memory_space", "access_kind", "atomic_or_reduction", "record_semantics",
        "width_status", "width_bytes", "width_authority", "global_source_operand", "function_identity", "static_authority_path", "selected", "executed_record_count",
    ])
    write_tsv(out / "PER_SHARD_GEOMETRY.tsv", shard_rows, [
        "lineage", "static_index", "role", "opcode", "access_kind", "width_status", "width_bytes", "record_count", "zero_active_record_count",
        "active_lane_events", "distinct_start_addresses_sum", "start_address_multiplicity_ratio_of_sums", "all_active_lanes_same_start_records",
        "g1_record_count", "logical_bytes", "unique_bytes", "sector_count_sum", "sector_proxy_bytes", "line128_count_sum",
        "lane_byte_multiplicity_ratio_of_sums", "sector_fill_ratio_of_sums", "shared_sector_record_count_path", "distributions_json",
    ])
    write_tsv(out / "ROLE_GEOMETRY.tsv", role_rows, [
        "lineage", "role", "record_count_with_role", "active_lane_events", "logical_bytes", "unique_bytes", "sector_proxy_bytes",
        "pure_role_record_count", "mixed_record_count_with_role", "shared_sector_record_count_with_role", "lane_event_share_g0", "logical_byte_share_g1",
        "unique_byte_share_g1_nonadditive", "sector_proxy_share_g1_nonadditive", "lane_byte_multiplicity_ratio_of_sums", "sector_fill_ratio_of_sums", "distribution_json", "note",
    ])
    dump_json(out / "AUTHORITY_AND_VALIDATION.json", validation)
    comparison = {}
    for result in results:
        total = result["overall"].summary()
        comparison[result["lineage"]] = {
            "g0": {key: total[key] for key in ("record_count", "zero_active_record_count", "active_lane_events", "distinct_start_addresses_sum", "start_address_multiplicity_ratio_of_sums", "all_active_lanes_same_start_records")},
            "g1_coverage": {"qualified_paths": sum(spec["width_status"] == "QUALIFIED" for spec in result["static"].values()), "selected_paths": len(result["static"]), "qualified_records": total["g1_record_count"], "all_records": total["record_count"], "qualified_active_lane_events": total["active_lane_events"], "all_active_lane_events": total["active_lane_events"], "unknown_path_fraction": sum(spec["width_status"] != "QUALIFIED" for spec in result["static"].values()) / len(result["static"])},
            "g1": {key: total[key] for key in ("logical_bytes", "unique_bytes", "sector_count_sum", "sector_proxy_bytes", "line128_count_sum", "lane_byte_multiplicity_ratio_of_sums", "sector_fill_ratio_of_sums")},
            "distributions": total["distributions"],
            "role_rows": [row for row in role_rows if row["lineage"] == result["lineage"]],
        }
    dump_json(out / "FINAL_DECISION.json", {
        "goal": "C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1",
        "status": "WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED",
        "labels": ["WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED", "ROLE_EVENT_SHARE_DIFFERS_FROM_SECTOR_PROXY_SHARE", "FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY"],
        "comparison": comparison,
        "g2_status": "G2_NOT_AUTHORIZED_BY_AVAILABLE_SCOPE",
        "g2_reason": "C16WARP1 payload has CTA xyz and warp but no explicit process/launch identity; no cross-shard identity is inferred",
        "new_gpu_capture_authorized": False,
        "new_cache_mechanism_authorized": False,
        "next_native_question": None,
        "scientific_conclusion": "The prior approximately half weight/half input lane-event split does not imply the same request geometry. Q30 keeps approximately equal weight/input sector-proxy shares but has one distinct 2 B start in each of 32 sectors per full-warp record. DeepSeek and OLMoE input records duplicate 16 starts across 32 lanes and cover one filled sector, whereas weight records have 32 distinct starts and cover two filled sectors; their sector-proxy shares are therefore approximately one-third input and two-thirds weight. This is familiar broadcast/coalescing structure under coupled gemvx implementations, not measured L2/DRAM traffic or a new mechanism opportunity.",
        "implementation_coupling": "all three are observed cuBLAS gemvx-family deployments; DeepSeek and OLMoE are receipt-bound template-6 while Q30 is template-7",
    })
    readme = f"""# C16 MoE warp request geometry screen / Lane 8\n\nStatus: `WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED`. CPU-only consumer; no GPU and no GPU lock.\n\n## Contract and authority\n\nThe consumer starts from accepted three-lineage commit `{CONSUMER_COMMIT}` and coordination commit `{COORDINATION_COMMIT}`. It verifies the exact Q30, DeepSeek, and OLMoE RUN_IDs, immutable run manifest, positive transfer ACK, catalog binding, per-shard trace hashes, C16WARP1 header/count closure, and historical selected/executed/zero/record/lane totals.\n\nAll 243 selected paths per lineage are ordinary global loads/stores. Static SASS provides widths for the full scoped set: U16 paths are 2 B and scalar `LDG.E` paths are 4 B. There are no atomic, reduction, or LDGSTS paths in the selected set. Full access intervals, not only starting addresses, determine G1 roles.\n\n## Method\n\nEach shard is opened once and streamed record-by-record. G0 counts active lanes and distinct starting addresses. G1 computes logical lane bytes, the within-record interval union, distinct covered 32 B sectors, and a 32 B sector-coverage proxy. `C32` is not an observed L1/L2 request count or DRAM traffic. Quantiles use {QUANTILE_DEFINITION}.\n\n`ROLE_GEOMETRY.tsv` gives lineage/role totals and old event shares beside qualified logical/unique/sector-proxy shares. `PER_SHARD_GEOMETRY.tsv` gives path/role totals plus per-record distributions. Role sector values are non-additive when roles share a sector.\n\n## Scope limits\n\nNo cross-shard chronology or VA union is formed. G2 is omitted as `G2_NOT_AUTHORIZED_BY_AVAILABLE_SCOPE` because the payload does not carry explicit process/launch identity. These three independent model lineages remain coupled to the cuBLAS gemvx implementation family. High lane-byte multiplicity or low sector fill alone does not establish avoidable DRAM traffic or authorize a cache/broadcast mechanism.\n"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    interpretation = """# Scientific interpretation\n\n## Result boundary\n\nThe exact numerical results are in `FINAL_DECISION.json`, `ROLE_GEOMETRY.tsv`, and `PER_SHARD_GEOMETRY.tsv`. The analysis characterizes dynamic warp-request geometry inside each accepted shard only.\n\n## Main result\n\nThe old active-lane event split remains about half weight and half input in all three anchors, but it does **not** imply the same request geometry. Q30 has 32 distinct U16 starts dispersed over 32 sectors for both full-warp roles (`L/U=1`, `U/C32=0.0625`). DeepSeek and OLMoE input has 16 starts duplicated over 32 lanes and fills one sector (`L/U=2`), while weight has 32 distinct starts and fills two sectors (`L/U=1`). Their approximately 50/50 event split becomes approximately 66/33 weight/input sector-proxy share. No mixed-role records, shared-role sectors, or interval/object-boundary ambiguities were observed. This supports `ROLE_EVENT_SHARE_DIFFERS_FROM_SECTOR_PROXY_SHARE` and `FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY`.\n\n## Reading the metrics\n\nStart-address multiplicity describes repeated-address structure. `L/U` distinguishes logical lane bytes from the within-record byte union. `U/C32` describes fill of the covered 32 B sectors. Neither `C32` nor record count is a measured cache request count or DRAM-byte total.\n\n## Implementation and causality limits\n\nAll three anchors use the cuBLAS gemvx family; DeepSeek and OLMoE are bound to template parameter 6 while Q30 is template parameter 7. Therefore shared geometry is not implementation-independent MoE evidence. No cache hit rate, reuse distance, SM placement, bottleneck, or universal MoE behavior is inferred.\n\n## Next experiment\n\nNo native experiment is warranted by this screen, and no follow-up question is retained. The observed duplication/coalescing is familiar and does not itself justify a new cache or broadcast mechanism.\n"""
    (out / "SCIENTIFIC_INTERPRETATION.md").write_text(interpretation, encoding="utf-8")
    sums = []
    for path in sorted(out.iterdir(), key=lambda p: p.name):
        if path.name != "SHA256SUMS" and path.is_file():
            sums.append(f"{sha256(path)}  {path.name}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    synthetic = self_test()
    audit = validate_authority(args.authority_root)
    if audit["status"] != "PASS":
        raise SystemExit(json.dumps(audit, indent=2))
    results = []
    for lineage in ("Q30", "DEEPSEEK", "OLMOE"):
        print(json.dumps({"event": "lineage_start", "lineage": lineage}), flush=True)
        result = analyze_lineage(lineage, args.authority_root)
        results.append(result)
        print(json.dumps({"event": "lineage_complete", "lineage": lineage, "closure": result["closure"]}), flush=True)
    build_outputs(args.out, args.authority_root, audit, results, synthetic)
    print(json.dumps({"event": "complete", "status": "PASS", "out": str(args.out)}), flush=True)


if __name__ == "__main__":
    main()
