#!/usr/bin/env python3
"""Read-only C7 opportunity analysis for the frozen decode1 trace set.

This is deliberately not a simulator or a performance model.  It streams the
already frozen trace files, mirrors the trace parser's address decompression,
and produces geometry/counting proxies only.  It writes no files and never
launches Accel-Sim.
"""

import argparse
import collections
import json
import lzma
import re
import sys
from pathlib import Path


PAGE = 64 * 1024
GROUP_PAGES = 16
SECTOR = 32
LOCAL_SIZE = 1 << 14
SETS = 48                 # 768 groups / 16 ways in frozen C4 config
WAYS = 16
ROOT = Path("/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55")
TRACE_LIST = ROOT / "decode1-semantic/compute-only-kernelslist.g"
TRACE_DIR = ROOT / "m4a-llama-decode1-20260903T004138Z/traces"
WEIGHT = (int("7f7ec6000000", 16), int("7f7f02520fff", 16))
RANGES = [
    ("WEIGHT", *WEIGHT),
    ("KV_CACHE", int("7f7f5fea0000", 16), int("7f7f5ffbffff", 16)),
    ("KV_CACHE", int("7f7f5ffe0000", 16), int("7f7f5fffffff", 16)),
    ("KV_CACHE", int("7f7f69800000", 16), int("7f7f69b427ff", 16)),
    ("KV_CACHE", int("7f7f69bc0000", 16), int("7f7f69bdffff", 16)),
    ("KV_CACHE", int("7f8067a00200", 16), int("7f8067a619ff", 16)),
]


def classify(start, width):
    """Match object_range_map::classify's full-range rule."""
    end = start + width - 1
    for kind, low, high in RANGES:
        if low > end:
            break
        if high < start:
            continue
        if start >= low and end <= high:
            return kind
    return "UNKNOWN"


def instruction(line):
    """Return (width, [(lane, address), ...]) or None for a non-memory line."""
    fields = line.split()
    if len(fields) < 7 or not re.fullmatch(r"[0-9A-Fa-f]+", fields[0]):
        return None
    try:
        mask = int(fields[1], 16)
        index = 3 + int(fields[2])       # PC, mask, number of destinations
        index += 1                       # opcode
        index += 1 + int(fields[index])  # number of sources and source regs
        width = int(fields[index])
        index += 1
        if not width:
            return None
        mode = int(fields[index])
        index += 1
    except (IndexError, ValueError):
        return None
    active = [lane for lane in range(32) if (mask >> lane) & 1]
    if not active:
        return None
    try:
        if mode == 0:
            return width, [(lane, int(fields[index + n], 16))
                           for n, lane in enumerate(active)]
        if mode == 1:
            base, stride = int(fields[index], 16), int(fields[index + 1])
            # This follows base_stride_decompress exactly, including its
            # conservative stop at the first inactive lane after the run.
            result, started, stopped, current = [], False, False, base
            for lane in range(32):
                enabled = (mask >> lane) & 1
                if enabled and not started:
                    started = True
                    result.append((lane, base))
                elif started and not stopped:
                    if enabled:
                        current += stride
                        result.append((lane, current))
                    else:
                        stopped = True
            return width, result
        if mode == 2:
            base = int(fields[index], 16)
            deltas = [int(fields[index + 1 + n]) for n in range(len(active))]
            result, current = [(active[0], base)], base
            for n, lane in enumerate(active[1:]):
                current += deltas[n]
                result.append((lane, current))
            return width, result
    except (IndexError, ValueError):
        return None
    return None


def trace_metadata(line, current):
    if line.startswith("-kernel id = "):
        current["id"] = line.split("=", 1)[1].strip()
    elif line.startswith("-kernel name = "):
        current["name"] = line.split("=", 1)[1].strip()
    elif line.startswith("-shmem base_addr = "):
        current["shared"] = int(line.split("=", 1)[1], 16)
    elif line.startswith("-local mem base_addr = "):
        current["local"] = int(line.split("=", 1)[1], 16)


def field(counter, name):
    return counter.get(name, 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-kernel", action="store_true",
                        help="emit all 740 per-kernel geometry rows")
    parser.add_argument("--start", type=int, default=0,
                        help="inclusive trace-list ordinal for a bounded offline chunk")
    parser.add_argument("--stop", type=int,
                        help="exclusive trace-list ordinal for a bounded offline chunk")
    parser.add_argument("--json", type=Path,
                        help="explicit scratch-only JSON output for chunk reduction")
    args = parser.parse_args()
    all_names = [line.strip() for line in TRACE_LIST.read_text().splitlines()
                 if line.strip()]
    stop = len(all_names) if args.stop is None else args.stop
    if args.start < 0 or stop < args.start or stop > len(all_names):
        raise SystemExit("invalid [start, stop) trace range")
    names = list(enumerate(all_names))[args.start:stop]
    total = collections.Counter()
    all_pages, all_groups = set(), set()
    leaves = collections.defaultdict(set)
    first_pages, first_groups = set(), set()
    new_leaf_in_existing_group = 0
    set_groups = collections.defaultdict(set)
    lru = [collections.OrderedDict() for _ in range(SETS)]
    lru_stats = collections.Counter()
    rows = []

    for ordinal, name in names:
        meta = {"id": "?", "name": "UNKNOWN", "shared": 0, "local": 0}
        count = collections.Counter()
        pages, groups, kernel_leaves = set(), set(), collections.defaultdict(set)
        with lzma.open(TRACE_DIR / name, "rt", encoding="utf-8") as trace:
            for line in trace:
                trace_metadata(line, meta)
                decoded = instruction(line)
                if decoded is None:
                    continue
                width, lane_addresses = decoded
                count["memory_instructions"] += 1
                total["memory_instructions"] += 1
                global_lanes = []
                for _, address in lane_addresses:
                    if (meta["shared"] <= address < meta["local"] or
                            meta["local"] <= address < meta["local"] + LOCAL_SIZE):
                        count["non_global_lanes"] += 1
                        total["non_global_lanes"] += 1
                        continue
                    global_lanes.append((address, width))
                    kind = classify(address, width)
                    count["lane_" + kind] += 1
                    total["lane_" + kind] += 1
                    end = address + width - 1
                    if kind == "WEIGHT":
                        count["descriptor_full_lanes"] += 1
                        total["descriptor_full_lanes"] += 1
                    if WEIGHT[0] <= address <= WEIGHT[1] < end:
                        count["descriptor_boundary_cross_lanes"] += 1
                        total["descriptor_boundary_cross_lanes"] += 1
                    if address // PAGE != end // PAGE:
                        count["page_boundary_cross_lanes"] += 1
                        total["page_boundary_cross_lanes"] += 1
                    if address // (PAGE * GROUP_PAGES) != end // (PAGE * GROUP_PAGES):
                        count["group_boundary_cross_lanes"] += 1
                        total["group_boundary_cross_lanes"] += 1

                # A per-instruction de-duplicated 32-byte-sector proxy.  This
                # deliberately is not claimed to be an Accel-Sim transaction.
                sectors = set()
                for address, width in global_lanes:
                    sectors.update(range(address // SECTOR,
                                         (address + width - 1) // SECTOR + 1))
                for sector in sectors:
                    address = sector * SECTOR
                    kind = classify(address, SECTOR)
                    count["sector_" + kind] += 1
                    total["sector_" + kind] += 1
                    vpn, group = address // PAGE, address // (PAGE * GROUP_PAGES)
                    leaf = vpn % GROUP_PAGES
                    pages.add(vpn); groups.add(group); kernel_leaves[group].add(leaf)
                    all_pages.add(vpn); all_groups.add(group); leaves[group].add(leaf)
                    if vpn not in first_pages:
                        if group in first_groups:
                            new_leaf_in_existing_group += 1
                        else:
                            first_groups.add(group)
                        first_pages.add(vpn)
                    # C1 frozen generic hash with ASID=0 and 64KiB page size.
                    set_id = (group ^ (PAGE >> 12)) % SETS
                    set_groups[set_id].add(group)
                    bucket = lru[set_id]
                    lru_stats["references"] += 1
                    if group in bucket:
                        lru_stats["hits"] += 1
                        bucket.move_to_end(group)
                    else:
                        lru_stats["misses"] += 1
                        if len(bucket) == WAYS:
                            bucket.popitem(last=False)
                            lru_stats["evictions"] += 1
                        bucket[group] = None
        rows.append((ordinal, meta["id"], name, count, len(pages), len(groups),
                     sum(len(x) for x in kernel_leaves.values()) - len(kernel_leaves),
                     max(map(len, kernel_leaves.values())) if kernel_leaves else 0))
        if ordinal and ordinal % 100 == 0:
            print("PROGRESS", ordinal, file=sys.stderr, flush=True)

    total_sectors = field(total, "sector_WEIGHT") + field(total, "sector_KV_CACHE") + field(total, "sector_UNKNOWN")
    total_lanes = field(total, "lane_WEIGHT") + field(total, "lane_KV_CACHE") + field(total, "lane_UNKNOWN")
    histogram = collections.Counter(len(value) for value in leaves.values())
    print("TRACE_RANGE\t%d\t%d" % (args.start, stop))
    print("TRACE_FILES\t%d" % len(names))
    print("MEMORY_INSTRUCTIONS\t%d" % field(total, "memory_instructions"))
    print("GLOBAL_LANES\t%d" % total_lanes)
    print("WEIGHT_LANES\t%d" % field(total, "lane_WEIGHT"))
    print("WEIGHT_LANE_COVERAGE_PCT\t%.6f" % (100 * field(total, "lane_WEIGHT") / total_lanes))
    print("GLOBAL_32B_SECTOR_PROXY\t%d" % total_sectors)
    print("WEIGHT_32B_SECTOR_PROXY\t%d" % field(total, "sector_WEIGHT"))
    print("WEIGHT_SECTOR_PROXY_COVERAGE_PCT\t%.6f" % (100 * field(total, "sector_WEIGHT") / total_sectors))
    print("WEIGHT_DESCRIPTOR_FULL_LANES\t%d" % field(total, "descriptor_full_lanes"))
    print("WEIGHT_DESCRIPTOR_BOUNDARY_CROSS_LANES\t%d" % field(total, "descriptor_boundary_cross_lanes"))
    print("PAGE_BOUNDARY_CROSS_LANES\t%d" % field(total, "page_boundary_cross_lanes"))
    print("GROUP_BOUNDARY_CROSS_LANES\t%d" % field(total, "group_boundary_cross_lanes"))
    print("UNIQUE_64K_PAGES\t%d" % len(all_pages))
    print("UNIQUE_16_LEAF_GROUPS\t%d" % len(all_groups))
    print("THEORETICAL_GROUP_ENTRY_COMPRESSION_PCT\t%.6f" %
          (100 * (1 - len(all_groups) / len(all_pages))))
    print("AVG_LEAVES_PER_GROUP\t%.6f" % (len(all_pages) / len(all_groups)))
    print("MAX_LEAVES_PER_GROUP\t%d" % max(histogram))
    print("LEAF_OCCUPANCY_HISTOGRAM\t%s" % ",".join("%d:%d" % item for item in sorted(histogram.items())))
    print("UNIQUE_NEW_LEAF_IN_EXISTING_GROUP\t%d" % new_leaf_in_existing_group)
    print("STATIC_MAX_GROUPS_PER_SET\t%d" % max(map(len, set_groups.values())))
    print("GROUP_LRU_SECTOR_PROXY_REFERENCES\t%d" % field(lru_stats, "references"))
    print("GROUP_LRU_SECTOR_PROXY_HITS\t%d" % field(lru_stats, "hits"))
    print("GROUP_LRU_SECTOR_PROXY_MISSES\t%d" % field(lru_stats, "misses"))
    print("GROUP_LRU_SECTOR_PROXY_EVICTIONS\t%d" % field(lru_stats, "evictions"))
    print("BOUNDED_THREE_KERNEL_ROWS")
    for row in rows[:3]:
        ordinal, kid, name, count, pages, groups, extra, maximum = row
        sectors = field(count, "sector_WEIGHT") + field(count, "sector_KV_CACHE") + field(count, "sector_UNKNOWN")
        print("KERNEL\t%d\t%s\t%s\tglobal_sectors=%d\tweight_sectors=%d\tweight_pct=%.6f\tpages=%d\tgroups=%d\tpage_cross=%d\tdescriptor_cross=%d" %
              (ordinal, kid, name, sectors, field(count, "sector_WEIGHT"),
               100 * field(count, "sector_WEIGHT") / sectors if sectors else 0,
               pages, groups, field(count, "page_boundary_cross_lanes"),
               field(count, "descriptor_boundary_cross_lanes")))
    print("TOP_WEIGHT_KERNELS")
    for row in sorted(rows, key=lambda x: (field(x[3], "sector_WEIGHT"), field(x[3], "sector_UNKNOWN")), reverse=True)[:12]:
        ordinal, kid, name, count, pages, groups, extra, maximum = row
        sectors = field(count, "sector_WEIGHT") + field(count, "sector_KV_CACHE") + field(count, "sector_UNKNOWN")
        print("KERNEL\t%d\t%s\tweight_sectors=%d\tglobal_sectors=%d\tweight_pct=%.6f\tpages=%d\tgroups=%d" %
              (ordinal, kid, field(count, "sector_WEIGHT"), sectors,
               100 * field(count, "sector_WEIGHT") / sectors if sectors else 0,
               pages, groups))
    print("TOP_MULTI_LEAF_KERNELS")
    for row in sorted(rows, key=lambda x: (x[6], x[5]), reverse=True)[:12]:
        ordinal, kid, name, count, pages, groups, extra, maximum = row
        print("KERNEL\t%d\t%s\tunique_pages=%d\tgroups=%d\tnew_leaf_in_existing_group=%d\tmax_leaves=%d" %
              (ordinal, kid, pages, groups, extra, maximum))
    if args.per_kernel:
        print("ALL_KERNEL_ROWS")
        for row in rows:
            ordinal, kid, name, count, pages, groups, extra, maximum = row
            sectors = field(count, "sector_WEIGHT") + field(count, "sector_KV_CACHE") + field(count, "sector_UNKNOWN")
            print("KERNEL\t%d\t%s\t%s\tglobal_sectors=%d\tweight_sectors=%d\tpages=%d\tgroups=%d\tnew_leaf_in_existing_group=%d\tmax_leaves=%d" %
                  (ordinal, kid, name, sectors, field(count, "sector_WEIGHT"), pages,
                   groups, extra, maximum))
    if args.json is not None:
        # The caller supplies a Window-C scratch path.  The JSON has only
        # derived counters/identities; no trace content is copied or modified.
        payload = {
            "range": [args.start, stop],
            "total": dict(total),
            "pages": sorted(all_pages),
            "leaves": {str(group): sorted(values) for group, values in leaves.items()},
            "set_groups": {str(group): sorted(values) for group, values in set_groups.items()},
            "rows": [[ordinal, kid, name, dict(count), pages, groups, extra, maximum]
                     for ordinal, kid, name, count, pages, groups, extra, maximum in rows],
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
