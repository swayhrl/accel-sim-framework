#!/usr/bin/env python3
"""Deterministic Stage-A decomposition for the R101R3 bounded-service Goal.

This tool consumes only accepted R101R2 B0/O2 raw evidence and immutable
CONTEXT2 trace references.  It does not invoke the simulator.  The trace
decoder reconstructs the accepted SM89 sector coalescing contract
(warp_parts=1, 32-byte global transactions) and validates its totals against
the O2 coalesced-transaction counters before publishing any table.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Iterable


STAGE = "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_V1"
R2_STAGE = "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1"
REPO = Path(__file__).resolve().parents[4]
PACK = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1"
)
R2_NODE = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r2_context2_memory_service_174_v1"
)
R3_NODE = Path(
    "/root/share/mnt164/huangrulin/"
    "awma_r101r3_bounded_service_handoff_174_v1"
)
R2_TOOL = REPO / (
    "util/vm_tlb/awma/r101r2_context2_memory_service_v1/"
    "derive_context2_input.py"
)
SIDECAR = R2_NODE / "input/transient_l2_runtime.tsv"
KERNELS = R2_NODE / "input/CONTEXT2_KERNELS.tsv"
DERIVATION = R2_NODE / "input/CONTEXT2_DERIVATION_RECEIPT.json"
FORMAL = R2_NODE / "raw/formal"
EXPECTED = {
    "scientific_parent": "97d5be184b7f7f35c06d3ee111a8c5ba6efad896",
    "r2_b0_summary": (
        "2c7e2cac39d0cbc1d0b1a1bf6eb4a0ec43c571b4595b4c282e93e9d4e966f24b"
    ),
    "r2_o2_summary": (
        "d8aba6635e29b920266964fc6e8b2c5cda70cc5ccc1b80985de32420cdc8857f"
    ),
    "sidecar": (
        "67adc56216f25bfc88c98d86aabdf1eeaae87e9f2f8e102f675d5be8ec11e7b5"
    ),
    "kernels": (
        "a9cf4bdbc3d551e9e7fc0d41b84a65e89d148085ea92940f04366c2e71704a65"
    ),
    "derivation": (
        "b560ee7a6947854f9123ce739af5befe788d2e17caa74292ca0a0b9a4597882d"
    ),
}
REGION_NAMES = {0: "A", 1: "B", 2: "X0", 3: "X1"}
SECTOR_BYTES = 32
LINE_BYTES = 128
FULL_SECTOR_MASK = (1 << SECTOR_BYTES) - 1
SERVICE_COUNTERS = (
    "awma_r101r2_service_qualified_ldg_reads",
    "awma_r101r2_service_qualified_ldgsts_reads",
    "awma_r101r2_service_qualified_ldgsts_bytes",
    "awma_r101r2_service_qualified_read_bytes",
    "awma_r101r2_service_qualified_read_active_bytes",
    "awma_r101r2_service_qualified_writes",
    "awma_r101r2_service_qualified_write_bytes",
    "awma_r101r2_service_qualified_write_active_bytes",
)


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AnalysisError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode()


def tsv_bytes(header: Iterable[str], rows: Iterable[Iterable[Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode()


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def load_r2_decoder() -> Any:
    spec = importlib.util.spec_from_file_location("r2_derive", R2_TOOL)
    require(spec is not None and spec.loader is not None, "cannot load R2 decoder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def admit_inputs() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    require(sha256(SIDECAR) == EXPECTED["sidecar"], "accepted sidecar drift")
    require(sha256(KERNELS) == EXPECTED["kernels"], "accepted kernels table drift")
    require(sha256(DERIVATION) == EXPECTED["derivation"], "derivation receipt drift")
    summaries = {
        arm: read_json(FORMAL / arm / "RUN_SUMMARY.json") for arm in ("B0", "O2")
    }
    for arm, expected in (
        ("B0", EXPECTED["r2_b0_summary"]),
        ("O2", EXPECTED["r2_o2_summary"]),
    ):
        require(sha256(FORMAL / arm / "RUN_SUMMARY.json") == expected,
                f"{arm} summary drift")
        require(summaries[arm].get("stage") == R2_STAGE, f"{arm} stage drift")
        require(summaries[arm].get("status") == "PASS", f"{arm} not PASS")
        require(len(summaries[arm].get("per_kernel_snapshots", [])) == 6,
                f"{arm} snapshot count drift")
    with KERNELS.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require([int(row["derived_ordinal"]) for row in rows] == list(range(1, 7)),
            "kernel ordinal drift")
    for row in rows:
        path = Path(row["derived_reference"])
        require(path.is_symlink() and path.is_file(),
                f"trace reference is not an admitted symlink: {path}")
        require(os.path.samefile(path, row["source_path"]),
                f"trace samefile identity failed: {path}")
    return summaries["B0"], summaries["O2"], rows


def parse_sidecar() -> dict[str, Any]:
    result: dict[str, Any] = {
        "kernels": {}, "regions": {}, "PRE": defaultdict(list),
        "POST": defaultdict(list), "context_end": None, "roi_start": None,
        "roi_end": None,
    }
    lines = SIDECAR.read_text().splitlines()
    require(lines and lines[0] == "AWMA_TRANSIENT_L2_RUNTIME_V1",
            "sidecar header drift")
    for raw in lines[1:]:
        if not raw or raw.startswith("#"):
            continue
        fields = raw.split()
        kind = fields[0]
        if kind == "LINE_SIZE":
            require(int(fields[1], 0) == LINE_BYTES, "line-size drift")
        elif kind == "EXPECTED_KERNELS":
            require(int(fields[1], 0) == 6, "kernel-count drift")
        elif kind == "EXPECTED_STREAM":
            require(int(fields[1], 0) == 0, "stream drift")
        elif kind == "CONTEXT_END":
            result["context_end"] = int(fields[1], 0)
        elif kind == "MEASURED_ROI_START":
            result["roi_start"] = int(fields[1], 0)
        elif kind == "MEASURED_ROI_END":
            result["roi_end"] = int(fields[1], 0)
        elif kind == "KERNEL":
            result["kernels"][int(fields[1])] = {
                "kernel_id": int(fields[2]), "name": fields[3]
            }
        elif kind == "REGION":
            region = int(fields[1])
            result["regions"][region] = {
                "base": int(fields[2], 0), "limit": int(fields[3], 0),
                "generation": int(fields[4], 0), "live": bool(int(fields[5], 0)),
            }
        elif kind in {"PRE", "POST"}:
            result[kind][int(fields[1])].append(
                (int(fields[2]), int(fields[3]), bool(int(fields[4], 0)))
            )
        else:
            raise AnalysisError(f"unknown sidecar record: {raw}")
    require((result["context_end"], result["roi_start"], result["roi_end"])
            == (3, 4, 6), "ROI boundary drift")
    require(set(result["regions"]) == set(REGION_NAMES), "region set drift")
    return result


def apply_transitions(state: dict[int, dict[str, Any]],
                      transitions: Iterable[tuple[int, int, bool]]) -> None:
    for region, generation, live in transitions:
        require(region in state, f"unknown region {region}")
        state[region]["generation"] = generation
        state[region]["live"] = live


def instruction_records(path: Path, decoder: Any) -> Iterable[dict[str, Any]]:
    process = subprocess.Popen(
        ["xz", "-dc", "--", str(path)], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, bufsize=1 << 20,
    )
    assert process.stdout is not None and process.stderr is not None
    in_tb = False
    warp_open = False
    declared: int | None = None
    seen = 0

    def close_warp() -> None:
        if warp_open:
            require(declared is not None and seen == declared,
                    f"warp record count mismatch in {path.name}")

    try:
        for line_number, raw in enumerate(process.stdout, 1):
            line = raw.strip()
            if not line:
                continue
            if line == b"#BEGIN_TB":
                require(not in_tb, f"nested TB in {path.name}")
                in_tb, warp_open, declared, seen = True, False, None, 0
                continue
            if line == b"#END_TB":
                close_warp()
                require(in_tb, f"orphan TB end in {path.name}")
                in_tb, warp_open = False, False
                continue
            if not in_tb or line.startswith(b"thread block = "):
                continue
            if line.startswith(b"warp = "):
                close_warp()
                warp_open, declared, seen = True, None, 0
                continue
            if line.startswith(b"insts = "):
                require(warp_open and declared is None,
                        f"malformed inst count in {path.name}")
                declared = int(line.split(b"=", 1)[1], 10)
                continue
            require(warp_open and declared is not None,
                    f"instruction outside warp: {path.name}:{line_number}")
            try:
                record = decoder.parse_instruction(line.split())
            except BaseException as exc:
                raise AnalysisError(
                    f"{path.name}:{line_number}: trace decode failed: {exc}"
                ) from exc
            seen += 1
            require(seen <= declared, f"too many records in {path.name}")
            yield record
        require(not in_tb, f"unterminated TB in {path.name}")
        close_warp()
        stderr = process.stderr.read().decode(errors="replace")
        rc = process.wait()
        require(rc == 0, f"xz failed for {path.name}: {stderr}")
    except BaseException:
        process.kill()
        process.wait()
        raise


def transaction_masks(addresses: list[int], width: int) -> dict[int, int]:
    result: dict[int, int] = {}
    low_mask = (1 << width) - 1
    for address in addresses:
        segment = address & ~(SECTOR_BYTES - 1)
        offset = address & (SECTOR_BYTES - 1)
        if offset + width <= SECTOR_BYTES:
            result[segment] = result.get(segment, 0) | (low_mask << offset)
        else:
            first = SECTOR_BYTES - offset
            result[segment] = (
                result.get(segment, 0) | (((1 << first) - 1) << offset)
            )
            remainder = width - first
            result[segment + SECTOR_BYTES] = (
                result.get(segment + SECTOR_BYTES, 0) | ((1 << remainder) - 1)
            )
    return result


def classify_segment(segment: int, state: dict[int, dict[str, Any]]
                     ) -> tuple[int, int] | None:
    matches = [
        (region, row["generation"])
        for region, row in state.items()
        if row["live"] and row["base"] <= segment
        and segment + SECTOR_BYTES <= row["limit"]
    ]
    require(len(matches) <= 1, f"segment intersects multiple live regions: {segment:#x}")
    return matches[0] if matches else None


@dataclass
class Producer:
    first_kernel: int
    last_kernel: int
    byte_mask: int
    transactions: int


@dataclass
class Consumer:
    transactions: int = 0
    request_bytes: int = 0
    active_bytes: int = 0
    prior_producer_transactions: int = 0
    byte_covered_transactions: int = 0
    same_kernel_trace_order_potential: int = 0


def delta_counters(snapshots: list[dict[str, Any]], ordinal: int
                   ) -> dict[str, int]:
    current = snapshots[ordinal - 1]["controller"]
    previous = snapshots[ordinal - 2]["controller"] if ordinal > 1 else {}
    return {
        key: int(current.get(key, 0)) - int(previous.get(key, 0))
        for key in SERVICE_COUNTERS
    }


def scan_traces(o2: dict[str, Any], kernel_rows: list[dict[str, str]],
                sidecar: dict[str, Any], decoder: Any
                ) -> tuple[list[list[Any]], list[list[Any]], dict[str, Any],
                           dict[Any, Producer], dict[Any, Consumer]]:
    state = {region: dict(row) for region, row in sidecar["regions"].items()}
    composition: Counter[tuple[int, str, int, str]] = Counter()
    request_bytes: Counter[tuple[int, str, int, str]] = Counter()
    active_bytes: Counter[tuple[int, str, int, str]] = Counter()
    producers: dict[tuple[int, int, int, int], Producer] = {}
    consumers: dict[tuple[tuple[int, int, int, int], int, str], Consumer] = {}
    per_kernel_transaction_totals: dict[int, Counter[str]] = {}

    for row in kernel_rows:
        ordinal = int(row["derived_ordinal"])
        apply_transitions(state, sidecar["PRE"].get(ordinal, []))
        current: dict[tuple[int, int, int, int], Producer] = {}
        per_kernel: Counter[str] = Counter()
        for instruction in instruction_records(Path(row["derived_reference"]), decoder):
            base_opcode = instruction["opcode"].split(".", 1)[0]
            if base_opcode not in {"LDG", "LDGSTS", "STG"}:
                continue
            width = int(instruction["effective_width"])
            if not width:
                continue
            opcode_class = {
                "LDG": "LDG", "LDGSTS": "LDGSTS", "STG": "WRITE"
            }[base_opcode]
            for segment, mask in transaction_masks(
                instruction["addresses"], width
            ).items():
                classification = classify_segment(segment, state)
                if classification is None:
                    continue
                region, generation = classification
                line = segment & ~(LINE_BYTES - 1)
                sector = (segment - line) // SECTOR_BYTES
                key = (region, generation, line, sector)
                ckey = (ordinal, REGION_NAMES[region], generation, opcode_class)
                composition[ckey] += 1
                request_bytes[ckey] += SECTOR_BYTES
                active_bytes[ckey] += mask.bit_count()
                per_kernel[opcode_class] += 1
                if opcode_class == "WRITE":
                    entry = current.get(key)
                    if entry is None:
                        current[key] = Producer(ordinal, ordinal, mask, 1)
                    else:
                        entry.byte_mask |= mask
                        entry.transactions += 1
                        entry.last_kernel = ordinal
                else:
                    consumer_key = (key, ordinal, opcode_class)
                    consumer = consumers.setdefault(consumer_key, Consumer())
                    consumer.transactions += 1
                    consumer.request_bytes += SECTOR_BYTES
                    consumer.active_bytes += mask.bit_count()
                    prior = producers.get(key)
                    if prior is not None:
                        consumer.prior_producer_transactions += 1
                        if mask & ~prior.byte_mask == 0:
                            consumer.byte_covered_transactions += 1
                    same = current.get(key)
                    if same is not None and mask & ~same.byte_mask == 0:
                        consumer.same_kernel_trace_order_potential += 1
        per_kernel_transaction_totals[ordinal] = per_kernel
        for key, incoming in current.items():
            prior = producers.get(key)
            if prior is None:
                producers[key] = incoming
            else:
                prior.last_kernel = ordinal
                prior.byte_mask |= incoming.byte_mask
                prior.transactions += incoming.transactions
        apply_transitions(state, sidecar["POST"].get(ordinal, []))

    o2_snapshots = o2["per_kernel_snapshots"]
    for ordinal in (4, 5, 6):
        expected = delta_counters(o2_snapshots, ordinal)
        actual = per_kernel_transaction_totals[ordinal]
        require(actual["LDG"] == expected[
                    "awma_r101r2_service_qualified_ldg_reads"],
                f"kernel {ordinal} LDG coalescing mismatch")
        require(actual["LDGSTS"] == expected[
                    "awma_r101r2_service_qualified_ldgsts_reads"],
                f"kernel {ordinal} LDGSTS coalescing mismatch")
        require(actual["WRITE"] == expected[
                    "awma_r101r2_service_qualified_writes"],
                f"kernel {ordinal} WRITE coalescing mismatch")
        rows_for_kernel = [key for key in composition if key[0] == ordinal]
        read_request = sum(
            request_bytes[key] for key in rows_for_kernel if key[3] != "WRITE"
        )
        read_active = sum(
            active_bytes[key] for key in rows_for_kernel if key[3] != "WRITE"
        )
        write_request = sum(
            request_bytes[key] for key in rows_for_kernel if key[3] == "WRITE"
        )
        write_active = sum(
            active_bytes[key] for key in rows_for_kernel if key[3] == "WRITE"
        )
        require(read_request == expected[
                    "awma_r101r2_service_qualified_read_bytes"],
                f"kernel {ordinal} read request-byte mismatch")
        require(read_active == expected[
                    "awma_r101r2_service_qualified_read_active_bytes"],
                f"kernel {ordinal} read active-byte mismatch")
        require(write_request == expected[
                    "awma_r101r2_service_qualified_write_bytes"],
                f"kernel {ordinal} write request-byte mismatch")
        require(write_active == expected[
                    "awma_r101r2_service_qualified_write_active_bytes"],
                f"kernel {ordinal} write active-byte mismatch")

    composition_rows = [
        [ordinal, sidecar["kernels"][ordinal]["name"],
         "CONTEXT" if ordinal <= 3 else "MEASURED_ROI",
         region, generation, opcode, composition[key],
         request_bytes[key], active_bytes[key],
         "EXACT_SM89_32B_COALESCED_RECONSTRUCTION"]
        for key in sorted(composition)
        for ordinal, region, generation, opcode in [key]
    ]

    availability_aggregate: Counter[tuple[Any, ...]] = Counter()
    for (key, consumer_kernel, opcode), consumer in consumers.items():
        region, generation, _line, _sector = key
        producer = producers.get(key)
        producer_kernel: Any = (
            producer.first_kernel if producer is not None else "NOT_IN_CONTEXT2"
        )
        status = (
            "CROSS_KERNEL_BYTE_COVERED"
            if consumer.byte_covered_transactions == consumer.transactions
            else "PARTIAL_OR_NO_PRIOR_PRODUCER"
        )
        akey = (
            REGION_NAMES[region], generation, producer_kernel,
            consumer_kernel, sidecar["kernels"][consumer_kernel]["name"],
            opcode, status,
        )
        availability_aggregate[akey + ("transactions",)] += consumer.transactions
        availability_aggregate[akey + ("eligible",)] += (
            consumer.byte_covered_transactions
        )
        availability_aggregate[akey + ("active_bytes",)] += consumer.active_bytes
        availability_aggregate[akey + ("same_kernel_trace_only",)] += (
            consumer.same_kernel_trace_order_potential
        )
        availability_aggregate[akey + ("sectors",)] += 1

    availability_rows: list[list[Any]] = []
    base_keys = sorted({key[:-1] for key in availability_aggregate},
                       key=lambda item: tuple(str(value) for value in item))
    for key in base_keys:
        availability_rows.append([
            *key,
            availability_aggregate[key + ("sectors",)],
            availability_aggregate[key + ("transactions",)],
            availability_aggregate[key + ("eligible",)],
            availability_aggregate[key + ("active_bytes",)],
            availability_aggregate[key + ("same_kernel_trace_only",)],
            (
                "Only a producer in an earlier completed kernel is counted "
                "as legally available; same-kernel serialized trace order is "
                "reported but not upgraded to runtime chronology."
            ),
        ])

    receipt = {
        "stage": STAGE,
        "status": "PASS",
        "method": {
            "simulator_rerun": False,
            "trace_bytes_modified_or_copied": False,
            "coalescing": "SM89_ARCH89_WARP_PARTS_1_EXACT_32B_SECTOR_GROUPING",
            "ledger_granularity": "128B_LINE_X_4_32B_SECTORS_WITH_BYTE_MASK",
            "same_kernel_order": "NOT_CLAIMED_AS_RUNTIME_CHRONOLOGY",
        },
        "counts": {
            "composition_rows": len(composition_rows),
            "producer_sector_keys": len(producers),
            "consumer_sector_kernel_opcode_keys": len(consumers),
            "availability_summary_rows": len(availability_rows),
            "measured_transactions": sum(
                value for key, value in composition.items() if key[0] >= 4
            ),
            "measured_request_bytes": sum(
                value for key, value in request_bytes.items() if key[0] >= 4
            ),
            "measured_active_bytes": sum(
                value for key, value in active_bytes.items() if key[0] >= 4
            ),
        },
        "coalesced_crosscheck": {
            str(ordinal): dict(sorted(per_kernel_transaction_totals[ordinal].items()))
            for ordinal in (4, 5, 6)
        },
    }
    return composition_rows, availability_rows, receipt, producers, consumers


def existing_evidence_rows(b0: dict[str, Any], o2: dict[str, Any]
                           ) -> list[list[Any]]:
    rows: list[list[Any]] = []
    o2_controller = o2["controller"]
    for metric in (
        "awma_r101r2_service_max_scheduled_depth",
        "awma_r101r2_service_max_ready_depth",
    ):
        rows.append([
            "A1_QUEUE_DEPTH", "O2", "ALL", "ALL", metric,
            o2_controller.get(metric, "NOT AVAILABLE FROM ACCEPTED RAW"),
            "transactions", "AVAILABLE" if metric in o2_controller
            else "NOT AVAILABLE FROM ACCEPTED RAW",
            EXPECTED["r2_o2_summary"],
        ])
    metrics = (
        ("total_cycles", "cycles"), ("kernel_cycles", "cycles"),
        ("total_instructions", "instructions"), ("total_ctas", "ctas"),
        ("l1d_accesses", "transactions"), ("l1d_misses", "transactions"),
        ("l1d_reservation_fails", "events"),
        ("l2_accesses", "transactions"), ("l2_misses", "transactions"),
        ("l2_reservation_fails", "events"), ("dram_n_rd", "commands"),
        ("dram_n_write", "commands"), ("dram_n_wr_bk", "commands"),
    )
    for arm, summary, source_hash in (
        ("B0", b0, EXPECTED["r2_b0_summary"]),
        ("O2", o2, EXPECTED["r2_o2_summary"]),
    ):
        for snapshot in summary["per_kernel_snapshots"][3:6]:
            for metric, units in metrics:
                available = metric in snapshot
                rows.append([
                    "A2_KERNEL_BOUNDARY", arm, snapshot["ordinal"],
                    snapshot["kernel_name"], metric,
                    snapshot.get(metric, "NOT AVAILABLE FROM ACCEPTED RAW"),
                    units, "AVAILABLE" if available
                    else "NOT AVAILABLE FROM ACCEPTED RAW", source_hash,
                ])
    return rows


def write_detailed_ledger(path: Path, producers: dict[Any, Producer],
                          consumers: dict[Any, Consumer]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
                with io.TextIOWrapper(gz, encoding="utf-8", newline="") as text:
                    writer = csv.writer(text, delimiter="\t", lineterminator="\n")
                    writer.writerow([
                        "region", "generation", "line_address_hex", "sector",
                        "producer_first_kernel", "producer_last_kernel",
                        "producer_transactions", "producer_byte_mask_hex",
                        "producer_full_sector", "consumer_kernel", "opcode",
                        "consumer_transactions", "consumer_active_bytes",
                        "prior_producer_transactions",
                        "byte_covered_transactions",
                        "same_kernel_trace_order_potential",
                    ])
                    consumer_sector_keys = {entry[0] for entry in consumers}
                    all_keys = sorted(set(producers) | consumer_sector_keys)
                    by_sector: dict[Any, list[tuple[int, str, Consumer]]] = defaultdict(list)
                    for (key, kernel, opcode), consumer in consumers.items():
                        by_sector[key].append((kernel, opcode, consumer))
                    for key in all_keys:
                        region, generation, line, sector = key
                        producer = producers.get(key)
                        entries = sorted(by_sector.get(key, []),
                                         key=lambda item: (item[0], item[1]))
                        if not entries:
                            entries = [(0, "NONE", Consumer())]
                        for kernel, opcode, consumer in entries:
                            writer.writerow([
                                REGION_NAMES[region], generation, hex(line), sector,
                                producer.first_kernel if producer else
                                "NOT_IN_CONTEXT2",
                                producer.last_kernel if producer else
                                "NOT_IN_CONTEXT2",
                                producer.transactions if producer else 0,
                                f"{producer.byte_mask:08x}" if producer else
                                "00000000",
                                int(bool(producer and
                                         producer.byte_mask == FULL_SECTOR_MASK)),
                                kernel if kernel else "NONE", opcode,
                                consumer.transactions, consumer.active_bytes,
                                consumer.prior_producer_transactions,
                                consumer.byte_covered_transactions,
                                consumer.same_kernel_trace_order_potential,
                            ])
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = arguments()
    b0, o2, kernel_rows = admit_inputs()
    sidecar = parse_sidecar()
    decoder = load_r2_decoder()
    (composition_rows, availability_rows, receipt,
     producers, consumers) = scan_traces(o2, kernel_rows, sidecar, decoder)
    existing_rows = existing_evidence_rows(b0, o2)
    artifacts = {
        "STAGE_A_EXISTING_EVIDENCE.tsv": tsv_bytes(
            ("evidence_class", "arm", "kernel_ordinal", "kernel_name",
             "metric", "value", "units", "availability", "source_sha256"),
            existing_rows,
        ),
        "REGION_OPCODE_COMPOSITION.tsv": tsv_bytes(
            ("kernel_ordinal", "kernel_name", "role", "region", "generation",
             "opcode_class", "transaction_count", "request_bytes",
             "active_bytes", "method"),
            composition_rows,
        ),
        "PRODUCER_CONSUMER_AVAILABILITY.tsv": tsv_bytes(
            ("region", "generation", "producer_first_kernel",
             "consumer_kernel", "consumer_kernel_name", "opcode_class",
             "availability_class", "unique_sector_keys",
             "consumer_transactions", "eligible_transactions",
             "consumer_active_bytes", "same_kernel_trace_order_potential",
             "interpretation"),
            availability_rows,
        ),
    }
    if args.write:
        for name, blob in artifacts.items():
            atomic_write(PACK / name, blob)
        ledger = R3_NODE / "raw/stage_a/PRODUCER_CONSUMER_LEDGER.tsv.gz"
        write_detailed_ledger(ledger, producers, consumers)
        receipt["artifacts"] = {
            **{
                name: {"path": str(PACK / name), "bytes": len(blob),
                       "sha256": hashlib.sha256(blob).hexdigest()}
                for name, blob in artifacts.items()
            },
            "detailed_ledger": {
                "path": str(ledger), "bytes": ledger.stat().st_size,
                "sha256": sha256(ledger),
            },
        }
        atomic_write(R3_NODE / "raw/stage_a/STAGE_A_RECEIPT.json",
                     canonical_json(receipt))
    print(json.dumps({
        "stage": STAGE, "status": "PASS",
        "simulator_rerun": False, "write_performed": args.write,
        "counts": receipt["counts"],
        "artifact_sha256": {
            name: hashlib.sha256(blob).hexdigest()
            for name, blob in artifacts.items()
        },
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
