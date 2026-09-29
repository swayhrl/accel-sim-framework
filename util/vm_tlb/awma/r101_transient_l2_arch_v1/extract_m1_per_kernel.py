#!/usr/bin/env python3
"""Fail-closed extraction of the formal M1 per-kernel telemetry snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path


DURABLE_M1 = Path(
    "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/"
    "raw/formal/M1"
)
SIDECAR = Path(
    "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/"
    "input/transient_l2_runtime.tsv"
)
PACK_OUTPUT = Path(
    "/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1/"
    "docs/vm_tlb/review_packs/"
    "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1/"
    "PER_KERNEL_M1_TELEMETRY.tsv"
)
MODE = "bounded_live_retention"

AWMA_FIELDS = {
    "pre_transitions": "awma_transient_l2_pre_transitions",
    "post_transitions": "awma_transient_l2_post_transitions",
    "dead_victim_selections": "awma_transient_l2_dead_victim_selections",
    "dirty_dead_drops": "awma_transient_l2_dead_eviction_drops",
    "dirty_dead_drop_bytes": "awma_transient_l2_dead_eviction_drop_bytes",
    "forced_live_evictions": "awma_transient_l2_forced_live_evictions",
    "fallback_count": "awma_transient_l2_fallback_count",
    "ordinary_victim_selections":
        "awma_transient_l2_ordinary_victim_selections",
    "protected_victim_deflections_observational":
        "awma_transient_l2_protected_victim_deflections",
    "generated_l2_writebacks": "awma_transient_l2_l2_writebacks",
    "completed_l2_writebacks":
        "awma_transient_l2_completed_l2_writebacks",
    "outstanding_l2_writebacks":
        "awma_transient_l2_outstanding_l2_writebacks",
    "transient_writebacks": "awma_transient_l2_transient_writebacks",
    "transient_writeback_bytes":
        "awma_transient_l2_transient_writeback_bytes",
}
OUTPUT_FIELDS = (
    "ordinal", "name", "cumulative_cycles", "pre_transitions",
    "post_transitions", "dead_victim_selections", "dirty_dead_drops",
    "dirty_dead_drop_bytes", "forced_live_evictions", "fallback_count",
    "ordinary_victim_selections",
    "protected_victim_deflections_observational",
    "generated_l2_writebacks", "completed_l2_writebacks",
    "outstanding_l2_writebacks", "transient_writebacks",
    "transient_writeback_bytes", "l2_misses", "l2_reservation_fails",
)
MONOTONIC_FIELDS = tuple(field for field in OUTPUT_FIELDS if field not in {
    "ordinal", "name", "outstanding_l2_writebacks",
})


class DurableNotReady(RuntimeError):
    """The atomically published durable M1 result is not available yet."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def exactly_one_int(text: str, key: str) -> int:
    values = re.findall(
        rf"^{re.escape(key)} = (\d+)\s*$", text, re.MULTILINE)
    if len(values) != 1:
        raise RuntimeError(f"expected one {key}, found {len(values)}")
    return int(values[0])


def exactly_one_mode(text: str) -> str:
    values = re.findall(
        r"^awma_transient_l2_mode = (\S+)\s*$", text, re.MULTILINE)
    if len(values) != 1:
        raise RuntimeError(f"expected one M1 mode record, found {len(values)}")
    return values[0]


def parse_sidecar(path: Path) -> tuple[list[str], dict[int, int], dict[int, int]]:
    lines = path.read_text(errors="strict").splitlines()
    if not lines or lines[0] != "AWMA_TRANSIENT_L2_RUNTIME_V1":
        raise RuntimeError("unexpected transient-L2 sidecar header")
    expected_kernels = []
    expected_stream = []
    identities: dict[int, str] = {}
    pre_ordinals: list[int] = []
    post_ordinals: list[int] = []
    for line in lines[1:]:
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "EXPECTED_KERNELS":
            expected_kernels.append(int(fields[1]))
        elif fields[0] == "EXPECTED_STREAM":
            expected_stream.append(int(fields[1]))
        elif fields[0] == "KERNEL":
            if len(fields) != 4:
                raise RuntimeError(f"malformed KERNEL record: {line}")
            ordinal = int(fields[1])
            if ordinal in identities:
                raise RuntimeError(f"duplicate sidecar kernel ordinal {ordinal}")
            identities[ordinal] = fields[3]
        elif fields[0] in {"PRE", "POST"}:
            if len(fields) != 5:
                raise RuntimeError(f"malformed transition record: {line}")
            ordinal = int(fields[1])
            (pre_ordinals if fields[0] == "PRE" else post_ordinals).append(
                ordinal)
    if expected_kernels != [18] or expected_stream != [0]:
        raise RuntimeError("sidecar is not the exact 18-kernel stream-0 input")
    if sorted(identities) != list(range(1, 19)):
        raise RuntimeError("sidecar kernel identities are not exactly 1..18")
    if len(pre_ordinals) != 16 or len(post_ordinals) != 15:
        raise RuntimeError("sidecar transition budget is not PRE=16/POST=15")
    pre_counts = {
        ordinal: sum(event <= ordinal for event in pre_ordinals)
        for ordinal in range(1, 19)
    }
    post_counts = {
        ordinal: sum(event <= ordinal for event in post_ordinals)
        for ordinal in range(1, 19)
    }
    return [identities[i] for i in range(1, 19)], pre_counts, post_counts


def kernel_blocks(text: str) -> list[tuple[str, str]]:
    markers = list(re.finditer(r"^kernel_name =[ \t]*(.*?)[ \t]*$", text,
                               re.MULTILINE))
    result = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        result.append((marker.group(1), text[marker.start():end]))
    return result


def parse_snapshot(block: str, ordinal: int, name: str) -> dict[str, object]:
    if exactly_one_mode(block) != MODE:
        raise RuntimeError(f"kernel {ordinal} is not M1 mode")
    completed = exactly_one_int(block, "awma_transient_l2_completed_kernels")
    launched = exactly_one_int(block, "awma_transient_l2_launched_kernels")
    if completed != ordinal or launched != ordinal:
        raise RuntimeError(
            f"kernel {ordinal} snapshot has launched/completed={launched}/{completed}")
    row: dict[str, object] = {
        "ordinal": ordinal,
        "name": name,
        "cumulative_cycles": exactly_one_int(block, "gpu_tot_sim_cycle"),
        "l2_misses": exactly_one_int(block, "L2_total_cache_misses"),
        "l2_reservation_fails": exactly_one_int(
            block, "L2_total_cache_reservation_fails"),
    }
    for output_name, log_name in AWMA_FIELDS.items():
        row[output_name] = exactly_one_int(block, log_name)
    generated = int(row["generated_l2_writebacks"])
    completed_wb = int(row["completed_l2_writebacks"])
    outstanding = int(row["outstanding_l2_writebacks"])
    if completed_wb > generated or outstanding != generated - completed_wb:
        raise RuntimeError(f"kernel {ordinal} writeback accounting does not close")
    if row["fallback_count"] != row["forced_live_evictions"]:
        raise RuntimeError(f"kernel {ordinal} fallback/live selection mismatch")
    if row["dirty_dead_drops"] > row["dead_victim_selections"]:
        raise RuntimeError(f"kernel {ordinal} drops exceed dead selections")
    oracle_fields = (
        "awma_transient_l2_oracle_drop_lines",
        "awma_transient_l2_oracle_drop_dirty_lines",
        "awma_transient_l2_oracle_drop_bytes",
        "awma_transient_l2_oracle_reserved_skips",
    )
    if any(exactly_one_int(block, key) != 0 for key in oracle_fields):
        raise RuntimeError(f"kernel {ordinal} has nonzero oracle activity")
    return row


def render_tsv(rows: list[dict[str, object]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS,
                            delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def atomic_write(path: Path, text: str) -> None:
    if not path.parent.is_dir():
        raise RuntimeError(f"review-pack directory missing: {path.parent}")
    temporary = path.parent / f".{path.name}.tmp.{os.getpid()}"
    try:
        with temporary.open("x", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def extract(write: bool) -> dict[str, object]:
    required = (
        DURABLE_M1 / "run.log", DURABLE_M1 / "run.stderr",
        DURABLE_M1 / "rc.txt", DURABLE_M1 / "RUN_SUMMARY.json",
        DURABLE_M1 / "command.json", SIDECAR,
    )
    if not DURABLE_M1.is_dir() or any(not path.is_file() for path in required):
        raise DurableNotReady("durable formal M1 has not been atomically published")
    if (DURABLE_M1 / "rc.txt").read_text().strip() != "0":
        raise RuntimeError("durable M1 rc is not zero")
    if (DURABLE_M1 / "run.stderr").stat().st_size != 0:
        raise RuntimeError("durable M1 stderr is not empty")
    summary = json.loads((DURABLE_M1 / "RUN_SUMMARY.json").read_text())
    command = json.loads((DURABLE_M1 / "command.json").read_text())
    if (summary.get("status"), summary.get("arm"), summary.get("mode")) != (
            "PASS", "M1", MODE):
        raise RuntimeError("durable RUN_SUMMARY is not a passing formal M1")
    if command.get("arm") != "M1" or command.get("mode") != MODE:
        raise RuntimeError("durable command receipt is not formal M1")
    if summary.get("artifact_receipt", {}).get("sidecar") != sha256(SIDECAR):
        raise RuntimeError("durable M1 is not bound to the current sidecar")

    identities, pre_counts, post_counts = parse_sidecar(SIDECAR)
    text = (DURABLE_M1 / "run.log").read_text(errors="strict")
    launches = re.findall(
        r"^launching kernel name: (.*?) uid: (\d+) cuda_stream_id: (\d+)\s*$",
        text, re.MULTILINE)
    if len(launches) != 18:
        raise RuntimeError(f"expected 18 launch identities, found {len(launches)}")
    for ordinal, (name, uid, stream) in enumerate(launches, 1):
        if name != identities[ordinal - 1] or int(uid) != ordinal or stream != "0":
            raise RuntimeError(f"launch identity mismatch at ordinal {ordinal}")

    blocks = kernel_blocks(text)
    regular = [(name, block) for name, block in blocks if name]
    drains = [(name, block) for name, block in blocks if not name]
    if len(regular) != 18 or len(drains) != 1:
        raise RuntimeError(
            f"expected 18 kernel snapshots and one drain snapshot; got "
            f"{len(regular)} and {len(drains)}")
    rows = []
    for ordinal, ((name, block), expected_name) in enumerate(
            zip(regular, identities), 1):
        if name != expected_name:
            raise RuntimeError(f"snapshot identity mismatch at ordinal {ordinal}")
        row = parse_snapshot(block, ordinal, name)
        if row["pre_transitions"] != pre_counts[ordinal] or \
                row["post_transitions"] != post_counts[ordinal]:
            raise RuntimeError(f"transition count mismatch at ordinal {ordinal}")
        if rows:
            for field in MONOTONIC_FIELDS:
                if int(row[field]) < int(rows[-1][field]):
                    raise RuntimeError(
                        f"non-monotonic {field} at ordinal {ordinal}")
        rows.append(row)

    drain = drains[0][1]
    if exactly_one_mode(drain) != MODE:
        raise RuntimeError("final drain snapshot is not M1 mode")
    drain_values = {
        "cycles": exactly_one_int(drain, "gpu_tot_sim_cycle"),
        "completed_kernels": exactly_one_int(
            drain, "awma_transient_l2_completed_kernels"),
        "launched_kernels": exactly_one_int(
            drain, "awma_transient_l2_launched_kernels"),
        "pre_transitions": exactly_one_int(
            drain, "awma_transient_l2_pre_transitions"),
        "post_transitions": exactly_one_int(
            drain, "awma_transient_l2_post_transitions"),
        "generated_l2_writebacks": exactly_one_int(
            drain, "awma_transient_l2_l2_writebacks"),
        "completed_l2_writebacks": exactly_one_int(
            drain, "awma_transient_l2_completed_l2_writebacks"),
        "outstanding_l2_writebacks": exactly_one_int(
            drain, "awma_transient_l2_outstanding_l2_writebacks"),
        "terminal_quiescent": exactly_one_int(
            drain, "awma_transient_l2_terminal_quiescent"),
    }
    expected_drain = {
        "cycles": drain_values["cycles"],
        "completed_kernels": 18,
        "launched_kernels": 18,
        "pre_transitions": 16,
        "post_transitions": 15,
        "generated_l2_writebacks": rows[-1]["generated_l2_writebacks"],
        "completed_l2_writebacks": rows[-1]["generated_l2_writebacks"],
        "outstanding_l2_writebacks": 0,
        "terminal_quiescent": 1,
    }
    if (drain_values != expected_drain or
            drain_values["cycles"] < rows[-1]["cumulative_cycles"]):
        raise RuntimeError("final drain snapshot does not close")
    stable_during_drain = tuple(
        field for field in AWMA_FIELDS
        if field not in {
            "completed_l2_writebacks", "outstanding_l2_writebacks",
        }
    )
    for field in stable_during_drain:
        value = exactly_one_int(drain, AWMA_FIELDS[field])
        if value != rows[-1][field]:
            raise RuntimeError(f"{field} changed during terminal drain")
    if exactly_one_int(drain, "L2_total_cache_misses") != rows[-1]["l2_misses"] or \
            exactly_one_int(drain, "L2_total_cache_reservation_fails") != \
            rows[-1]["l2_reservation_fails"]:
        raise RuntimeError("L2 demand counters changed during terminal drain")
    drain_receipts = re.findall(
        r"^AWMA_TRANSIENT_L2_DRAIN enabled=1 cycles=(\d+) gpu_active=(\d+) "
        r"l2_writeback_active=(\d+) max_limit_hit=(\d+) gpu_deadlock=(\d+)\s*$",
        text, re.MULTILINE)
    if (len(drain_receipts) != 1 or
            drain_receipts[0][1:] != ("0", "0", "0", "0")):
        raise RuntimeError("final drain receipt missing or non-quiescent")

    tsv = render_tsv(rows)
    if write:
        atomic_write(PACK_OUTPUT, tsv)
    return {
        "status": "PASS",
        "arm": "M1",
        "mode": MODE,
        "rows": rows,
        "row_count": len(rows),
        "run_log_sha256": sha256(DURABLE_M1 / "run.log"),
        "sidecar_sha256": sha256(SIDECAR),
        "tsv_sha256": hashlib.sha256(tsv.encode()).hexdigest(),
        "output": str(PACK_OUTPUT) if write else None,
        "written": write,
        "final_drain": drain_values,
        "protected_victim_deflections_caveat": (
            "observational counter; do not treat as an exact causal fraction"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = extract(args.write)
    except DurableNotReady as error:
        print(json.dumps({"status": "NOT_READY", "error": str(error)},
                         sort_keys=True), file=sys.stderr)
        return 2
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)},
                         sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
