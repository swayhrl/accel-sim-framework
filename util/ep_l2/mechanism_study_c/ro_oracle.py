#!/usr/bin/env python3
"""Conservative, external-memory full-commandlist RO oracle (experiment input)."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import lzma
from pathlib import Path
import re
import sqlite3
import subprocess


SCHEMA = "EP_L2_RO_ORACLE_V1"
SCOPE = "TRACE_MODEL_CLOSED_WORLD"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def open_trace(path):
    with Path(path).open("rb") as f:
        magic = f.read(6)
    if magic.startswith(b"\x1f\x8b"):
        return gzip.open(path, "rt")
    if magic.startswith(b"\xfd7zXZ"):
        return lzma.open(path, "rt")
    return Path(path).open()


def instruction(text, version=0, lineinfo=0):
    """Decode the upstream SASS grammar; fail closed on ambiguity."""
    t = text.split()
    pos = (4 if version < 3 else 0) + int(bool(lineinfo))
    pc, mask = int(t[pos], 16), int(t[pos + 1], 16)
    if mask >= 1 << 32:
        raise ValueError("active mask wider than warp")
    pos += 2
    ndst = int(t[pos]); pos += 1 + ndst
    opcode = t[pos]; pos += 1
    nsrc = int(t[pos]); pos += 1 + nsrc
    mem = int(t[pos]); pos += 1
    if not mem and mask and opcode.split(".")[0] in ("LDG", "LDGSTS", "STG", "ATOM", "ATOMG", "RED"):
        raise ValueError("executed global memory operation without addresses")
    if not mem or not mask:
        return opcode, 0, []
    width = 4
    for part in opcode.split("."):
        if re.fullmatch(r"U?\d+", part):
            bits = int(part.lstrip("U"))
            if bits not in (8, 16, 32, 64, 128):
                raise ValueError("unsupported memory width")
            width = bits // 8
            break
    mode = int(t[pos]); pos += 1
    lanes = [i for i in range(32) if mask >> i & 1]
    if mode == 0:
        addresses = [int(t[pos + i], 16) for i in range(len(lanes))]
    elif mode == 1:
        # The upstream decompressor stops at the first inactive lane.
        # Reject non-contiguous masks rather than silently certify bad addresses.
        if lanes != list(range(lanes[0], lanes[-1] + 1)):
            raise ValueError("non-contiguous base-stride mask unsupported upstream")
        base, stride = int(t[pos], 16), int(t[pos + 1])
        addresses = [base + i * stride for i in range(len(lanes))]
    elif mode == 2:
        base = int(t[pos], 16)
        addresses = [base]
        for i in range(len(lanes) - 1):
            addresses.append(addresses[-1] + int(t[pos + 1 + i]))
    else:
        raise ValueError("unknown address compression")
    if any(a < 0 or a + width > 1 << 64 for a in addresses):
        raise ValueError("invalid address range")
    return opcode, width, addresses


def memory_kind(opcode):
    op = opcode.split(".")[0]
    if op in ("LDG", "LDGSTS"):
        return "R"
    if op == "STG":
        return "W"
    if op in ("ATOM", "ATOMG", "RED"):
        return "A"
    if op in ("LDS", "STS", "LDSM", "ATOMS", "LDC"):
        return "NON_GLOBAL"
    # Generic and local addresses need runtime translation/alias proof.
    # Unknown memory instructions may be writers, so poison the whole epoch.
    return "UNKNOWN"


def stream_kernel(path):
    version = lineinfo = 0
    grid = None
    grid_dims = None
    block = None
    blocks = ends = insts = 0
    expected = seen = None
    in_block = False
    warps = 0
    next_warp = 0
    tb_identified = False
    with open_trace(path) as f:
        for lineno, raw in enumerate(f, 1):
            s = raw.strip()
            if not s:
                continue
            if s.startswith("-accelsim tracer version"):
                version = int(s.split("=")[1])
            elif s.startswith("-enable lineinfo"):
                lineinfo = int(s.split("=")[1])
            elif s.startswith("-grid dim"):
                a = list(map(int, re.findall(r"\d+", s)))
                grid_dims = a
                grid = a[0] * a[1] * a[2]
            elif s.startswith("-block dim"):
                a = list(map(int, re.findall(r"\d+", s)))
                block = (a[0] * a[1] * a[2] + 31) // 32
            elif s == "#BEGIN_TB":
                if in_block:
                    raise ValueError("nested threadblock")
                in_block = True; blocks += 1; warps = 0; next_warp = 0
                tb_identified = False
            elif s == "#END_TB":
                if not in_block or (expected is not None and seen != expected):
                    raise ValueError("incomplete warp")
                if block is None or warps != block or next_warp != warps or not tb_identified:
                    raise ValueError("missing warp")
                ends += 1; in_block = False; expected = seen = None
            elif s.startswith("insts ="):
                if expected is not None and seen != expected:
                    raise ValueError("truncated warp")
                expected = int(s.split("=")[1]); seen = 0; warps += 1
            elif s.startswith("thread block ="):
                coords = list(map(int, re.findall(r"\d+", s)))
                if not in_block or tb_identified or len(coords) != 3 or grid_dims is None:
                    raise ValueError("missing/duplicate threadblock identity")
                ordinal = coords[0] + grid_dims[0] * (coords[1] + grid_dims[1] * coords[2])
                if ordinal != blocks - 1 or any(c >= n for c,n in zip(coords, grid_dims)):
                    raise ValueError("threadblocks missing, duplicated or not canonical trace order")
                tb_identified = True
            elif s.startswith("warp ="):
                if int(s.split("=")[1]) != next_warp:
                    raise ValueError("missing or duplicate warp identity")
                next_warp += 1
            elif s.startswith(("#", "-")):
                continue
            else:
                if not in_block or expected is None:
                    raise ValueError("instruction outside declared warp")
                try:
                    event = instruction(s, version, lineinfo)
                    if version < 3 and list(map(int, s.split()[:3])) != coords:
                        raise ValueError("instruction threadblock identity mismatch")
                    if version < 3 and int(s.split()[3]) != next_warp - 1:
                        raise ValueError("instruction warp identity mismatch")
                except (ValueError, IndexError) as e:
                    raise ValueError(f"{path}:{lineno}: {e}") from e
                seen += 1; insts += 1
                if seen > expected:
                    raise ValueError("excess instructions")
                yield event
    if in_block or grid is None or blocks != grid or ends != grid:
        raise ValueError(f"incomplete kernel {path}: grid={grid}, blocks={blocks}/{ends}")


def build(commandlist, output, scope, framework_source):
    if scope != SCOPE:
        raise ValueError("explicit closed-world model scope required; otherwise no certification")
    commandlist = Path(commandlist).resolve()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    dbpath = output / "oracle.sqlite3"
    db = sqlite3.connect(dbpath)
    db.executescript("""
      PRAGMA cache_size=-16384; PRAGMA temp_store=FILE;
      CREATE TABLE lines (address TEXT PRIMARY KEY, reads INTEGER NOT NULL,
                          writes INTEGER NOT NULL, atomics INTEGER NOT NULL);
    """)
    inputs = []
    commands = commandlist.read_text().splitlines()
    kernels = []
    host_updates = []
    for s in commands:
        s = s.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("kernel"):
            kernels.append(commandlist.parent / s)
        elif s.startswith(("MemcpyHtoD,", "MemcpyDtoH,")):
            fields=s.split(",")
            if len(fields)!=3:raise ValueError("malformed host copy command")
            address=int(fields[1],16);count=int(fields[2],10)
            if address<0 or count<0 or address+count>1<<64:raise ValueError("invalid host copy range")
            if s.startswith("MemcpyHtoD,") and kernels and count:
                host_updates.append((address&~127,(address+count-1)&~127))
        else:
            raise ValueError("unrecognized command; unseen agents cannot be excluded")
    if not kernels:
        raise ValueError("no complete kernels")
    command_hash = sha256(commandlist)
    unknown = collections.Counter()
    stats = collections.Counter()
    for kernel in kernels:
        before = sha256(kernel)
        kstats = collections.Counter()
        batch = []
        for op, width, addresses in stream_kernel(kernel):
            if not width:
                continue
            kind = memory_kind(op)
            kstats[op.split(".")[0]] += 1
            if kind == "NON_GLOBAL":
                continue
            if kind == "UNKNOWN":
                unknown[op] += 1
                continue
            # One canonical global VA domain across every visible GPU agent,
            # lane, warp and kernel, including misaligned multi-line accesses.
            touched = collections.Counter()
            for a in addresses:
                for line in range(a // 128, (a + width - 1) // 128 + 1):
                    touched[line * 128] += 1
            for line, count in touched.items():
                row = (f"{line:016x}", count if kind == "R" else 0,
                       count if kind == "W" else 0, count if kind == "A" else 0)
                batch.append(row)
            if len(batch) >= 8192:
                db.executemany("INSERT INTO lines VALUES(?,?,?,?) ON CONFLICT(address) DO UPDATE SET reads=reads+excluded.reads,writes=writes+excluded.writes,atomics=atomics+excluded.atomics", batch)
                batch.clear()
        if batch:
            db.executemany("INSERT INTO lines VALUES(?,?,?,?) ON CONFLICT(address) DO UPDATE SET reads=reads+excluded.reads,writes=writes+excluded.writes,atomics=atomics+excluded.atomics", batch)
        db.commit()
        if sha256(kernel) != before:
            raise ValueError("trace changed during certification")
        inputs.append(dict(path=str(kernel), sha256=before, opcodes=dict(kstats)))
    if sha256(commandlist) != command_hash:
        raise ValueError("commandlist changed during certification")
    # Exclude the whole128B line of every post-initialization host update,
    # including aliases through another kernel/lane and partial-sector copies.
    # These are explicit input commands, never an inferred absence of writers.
    for first,last in host_updates:
        db.execute("UPDATE lines SET writes=writes+1 WHERE address>=? AND address<=?",
                   (f"{first:016x}",f"{last:016x}"))
    db.commit()
    for row in db.execute("SELECT address,reads,writes,atomics FROM lines ORDER BY address"):
        _, reads, writes, atomics = row
        if not reads:
            reason = "NO_GLOBAL_READ"
        elif unknown:
            reason = "UNRESOLVED_ADDRESS_OR_OPCODE_IN_EPOCH"
        elif atomics:
            reason = "SAME_LINE_ATOMIC"
        elif writes:
            reason = "SAME_LINE_STORE"
        else:
            reason = "CERTIFIED_RO"
        stats[reason + "_lines"] += 1
        stats[reason + "_read_lane_references"] += reads
    with (output / "coverage.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["reason", "lines", "read_lane_references"])
        for key in sorted(k for k in stats if k.endswith("_lines")):
            reason = key[:-6]
            w.writerow([reason, stats[key], stats[reason + "_read_lane_references"]])
    with (output / "exclusion.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["reason", "lines", "read_lane_references"])
        for key in sorted(k for k in stats if k.endswith("_lines") and not k.startswith("CERTIFIED_RO")):
            reason = key[:-6]
            w.writerow([reason, stats[key], stats[reason + "_read_lane_references"]])
    with (output / "certified_lines.txt").open("w") as f:
        if not unknown:
            for (address,) in db.execute("SELECT address FROM lines WHERE reads>0 AND writes=0 AND atomics=0 ORDER BY address"):
                f.write(address + "\n")
    with (output / "certified_ranges.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["first_line", "last_line_inclusive"])
        start = end = None
        if not unknown:
            for (address,) in db.execute("SELECT address FROM lines WHERE reads>0 AND writes=0 AND atomics=0 ORDER BY address"):
                current = int(address,16)
                if end is not None and current != end + 128:
                    w.writerow([f"{start:016x}", f"{end:016x}"]); start = None
                if start is None: start = current
                end = current
        if start is not None: w.writerow([f"{start:016x}", f"{end:016x}"])
    db.close()
    manifest = dict(schema=SCHEMA, status="CERTIFIED_WITH_MODEL_SCOPE" if not unknown else "NO_CERTIFIED_LINES_UNRESOLVED_EPOCH",
                    framework_source_commit=framework_source, epoch="whole_commandlist",
                    address_domain="CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS",
                    scope=scope, assumptions=["All listed kernels/all traced lanes are visible agents", "No external/CPU/DMA/device-side concurrent writers during epoch", "Pre-epoch writes/writebacks are drained before oracle activation", "No virtual aliases to different canonical addresses; no MMIO", "Memcpy commands occur at drained command boundaries"],
                    host_updates_excluded=host_updates,
                    kernel_count=len(kernels), commandlist=str(commandlist), commandlist_sha256=command_hash,
                    kernels=inputs, unresolved_opcodes=dict(unknown), counts=dict(stats),
                    oracle_cost="offline SQLite O(unique lines), 16 MiB SQLite page cache; runtime oracle idealized input, not free hardware",
                    artifacts={n:sha256(output/n) for n in ["oracle.sqlite3", "coverage.csv", "exclusion.csv", "certified_lines.txt", "certified_ranges.csv"]})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def verify(output):
    output = Path(output)
    m = json.loads((output / "manifest.json").read_text())
    if m["schema"] != SCHEMA or m["scope"] != SCOPE or m["epoch"] != "whole_commandlist":
        raise ValueError("unsupported oracle contract")
    if sha256(m["commandlist"]) != m["commandlist_sha256"]:
        raise ValueError("changed commandlist")
    kernels = [str((Path(m["commandlist"]).parent/s.strip()).resolve())
               for s in Path(m["commandlist"]).read_text().splitlines()
               if s.strip().startswith("kernel")]
    if kernels != [str(Path(k["path"]).resolve()) for k in m["kernels"]]:
        raise ValueError("partial or reordered oracle epoch")
    for k in m["kernels"]:
        if sha256(k["path"]) != k["sha256"]:
            raise ValueError("changed trace input")
    for name, digest in m["artifacts"].items():
        if Path(name).name != name or sha256(output/name) != digest:
            raise ValueError("changed oracle artifact")
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--verify", type=Path)
    p.add_argument("--commandlist")
    p.add_argument("--output")
    p.add_argument("--model-scope", choices=[SCOPE])
    p.add_argument("--framework-source")
    args = p.parse_args()
    if args.verify:
        m = verify(args.verify)
        print(json.dumps({"status":"INPUT_AND_ARTIFACT_HASHES_VERIFIED", "manifest_sha256":sha256(args.verify/"manifest.json")}))
        return
    if not all([args.commandlist, args.output, args.model_scope, args.framework_source]):
        p.error("build requires commandlist, output, model-scope and framework-source")
    # Bind the exact script bytes to an existing producer commit before work.
    root = Path(__file__).resolve().parents[2]
    frozen = subprocess.check_output(["git", "-C", str(root), "show",
                                     args.framework_source + ":util/ep_l2/ro_oracle.py"])
    if frozen != Path(__file__).read_bytes():
        raise ValueError("oracle script is not frozen at declared source commit")
    m = build(args.commandlist, args.output, args.model_scope, args.framework_source)
    print(json.dumps({"status":m["status"], "kernels":m["kernel_count"], "counts":m["counts"]}))


if __name__ == "__main__":
    main()
