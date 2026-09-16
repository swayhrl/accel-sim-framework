#!/usr/bin/env python3
"""Fail-closed AWMA simulation consumer admission and identity utilities."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


SCHEMA_VERSION = "AWMA_SIM_CONSUMER_V2"
TRACE_SCHEMA = "SIM_COMPAT_CAPTURE_V1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_TRACE = re.compile(r"^kernel[A-Za-z0-9._-]*\.traceg\.xz$")
MEMCPY_HTOD = re.compile(r"^MemcpyHtoD,(?:0x)?[0-9A-Fa-f]+,[0-9]+$")

SEMANTIC_ENCODINGS = {
    "pc": "TRACE_RECORD",
    "opcode": "TRACE_RECORD",
    "access_kind": "OPCODE_CLASS",
    "memory_space": "OPCODE_CLASS",
    "byte_width": "TRACE_RECORD_AND_OPCODE",
    "warp_id": "CTA_WARP_STREAM",
    "cta_id": "CTA_STREAM",
    "active_mask": "TRACE_RECORD",
    "lane_addresses": "TRACE_RECORD",
    "event_order": "KERNEL_LIST_CTA_WARP_INSTRUCTION_STREAM",
    "sync_control": "OPCODE_STREAM",
}

MANIFEST_FIELDS = (
    "workload_id",
    "model_id",
    "model_revision",
    "input_binding_sha256",
    "scenario_id",
    "phase",
    "backend",
    "dtype",
    "runtime_identity",
    "target_id",
    "target_launch",
    "stream_context",
    "grid",
    "block",
    "trace_schema",
    "trace_grammar_version",
    "producer_source_sha256",
    "producer_binary_sha256",
    "tracer_version",
    "tracer_build_sha256",
    "address_context_sidecar",
    "asid_epoch",
    "va_width",
    "page_policy",
    "producer_terminal_receipt",
    "kernelslist",
    "bundle_hash_root",
)

SIM_INPUT_FIELDS = (
    "producer_bundle_hash_root",
    "trace_member_hash_root",
    "kernelslist_sha256",
    "producer_terminal_receipt_sha256",
    "workload_id",
    "model_id",
    "model_revision",
    "input_binding_sha256",
    "scenario_id",
    "phase",
    "backend",
    "dtype",
    "runtime_identity",
    "target_id",
    "target_launch",
    "stream_context",
    "grid",
    "block",
    "trace_schema",
    "trace_grammar_version",
    "producer_source_sha256",
    "producer_binary_sha256",
    "tracer_version",
    "tracer_build_sha256",
    "address_context_sha256",
    "asid_epoch",
    "va_width",
    "page_policy",
)

SCHEMAS = {
    "SIM_INPUT": SIM_INPUT_FIELDS,
    "SIM_BASELINE": (
        "framework_sha",
        "core_sha",
        "binary_sha256",
        "toolchain_receipt_sha256",
        "base_config_sha256",
        "vm_overlay_sha256",
        "telemetry_exporter_sha256",
        "normalizer_sha256",
        "runtime_wrapper_sha256",
        "accepted_base_config_sha256s",
        "fixed_window_cycles",
        "qualification_scope",
    ),
    "SIM_RUN": (
        "sim_input_id",
        "sim_baseline_id",
        "config_sha256",
        "overlay_sha256",
        "runtime_command_sha256",
        "runtime_environment_sha256",
        "fixed_window_cycles",
        "raw_log_sha256",
        "normalized_telemetry_sha256",
        "execution_status",
    ),
    "SIM_EVIDENCE": (
        "sim_run_id",
        "sim_input_id",
        "sim_baseline_id",
        "raw_log_sha256",
        "normalized_telemetry_sha256",
        "claim_scope",
        "scientific_status",
    ),
}

CATALOG_ID_FIELDS = {
    "SIM_INPUT": "sim_input_id",
    "SIM_BASELINE": "sim_baseline_id",
    "SIM_RUN": "sim_run_id",
    "SIM_EVIDENCE": "sim_evidence_id",
}

PREFIXES = (
    "sim.", "vm.", "tlb.", "ptw.", "pwc.", "walker.", "l1d.", "l2.",
    "dram.", "memory.", "queue.", "stall.", "performance.", "segment.",
    "selective.", "subentry.", "cache_variant.",
)


class ContractError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_id(prefix, record):
    id_fields = {"id", "sim_input_id", "sim_baseline_id", "sim_run_id", "sim_evidence_id"}
    semantic_record = {key: value for key, value in record.items() if key not in id_fields}
    return prefix + "_" + hashlib.sha256(canonical(semantic_record).encode()).hexdigest()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def obj(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise ContractError("invalid JSON %s: %s" % (path, exc)) from exc
    if not isinstance(value, dict):
        raise ContractError("JSON root must be object")
    return value


def need(record, fields, label):
    missing = [field for field in fields if record.get(field) in (None, "", [], {})]
    if missing:
        raise ContractError("%s missing: %s" % (label, ", ".join(missing)))


def require_sha256(value, label):
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ContractError("%s must be lowercase SHA256" % label)


def identity_for(kind, record):
    if kind not in SCHEMAS:
        raise ContractError("unknown schema kind: " + kind)
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("%s schema_version must be %s" % (kind, SCHEMA_VERSION))
    need(record, SCHEMAS[kind], kind)
    for field, value in record.items():
        if field.endswith("_sha256") or field.endswith("_hash_root"):
            require_sha256(value, "%s.%s" % (kind, field))
    if kind == "SIM_BASELINE":
        if not re.fullmatch(r"[0-9a-f]{40}", record["framework_sha"]):
            raise ContractError("SIM_BASELINE.framework_sha must be a lowercase Git SHA")
        if not re.fullmatch(r"[0-9a-f]{40}", record["core_sha"]):
            raise ContractError("SIM_BASELINE.core_sha must be a lowercase Git SHA")
        configs = record["accepted_base_config_sha256s"]
        if not isinstance(configs, list) or not configs or configs != sorted(set(configs)):
            raise ContractError("SIM_BASELINE accepted_base_config_sha256s must be a sorted nonempty unique list")
        for index, value in enumerate(configs):
            require_sha256(value, "SIM_BASELINE.accepted_base_config_sha256s[%d]" % index)
        if record["qualification_scope"] != "HASH_BOUND_FIXED_WINDOW_10000":
            raise ContractError("SIM_BASELINE qualification_scope is not accepted")
    if kind == "SIM_INPUT":
        if record["phase"] not in ("PREFILL", "DECODE"):
            raise ContractError("SIM_INPUT phase must be PREFILL or DECODE")
        if record["trace_schema"] != TRACE_SCHEMA:
            raise ContractError("SIM_INPUT trace_schema is not accepted")
        for field in ("grid", "block"):
            value = record[field]
            if not isinstance(value, list) or len(value) != 3 or not all(isinstance(item, int) and item > 0 for item in value):
                raise ContractError("SIM_INPUT %s must contain three positive integers" % field)
    if kind == "SIM_RUN" and record["execution_status"] not in (
        "EXPECTED_FIXED_WINDOW_BOUNDARY", "NORMAL_COMPLETION", "PARSER_ABORT",
        "SIMULATOR_ASSERT_OR_FATAL", "EXTERNAL_RUNTIME_FAILURE",
    ):
        raise ContractError("SIM_RUN execution_status is not accepted")
    if kind == "SIM_BASELINE" and record["fixed_window_cycles"] != 10000:
        raise ContractError("SIM_BASELINE fixed_window_cycles must be 10000")
    return stable_id(kind, record)


def member(root, name):
    if not isinstance(name, str) or not name or name.startswith("/") or ".." in Path(name).parts:
        raise ContractError("unsafe member")
    path = root / name
    if not path.is_file():
        raise ContractError("missing member: %s" % name)
    return path


def hash_root(files):
    return hashlib.sha256(canonical(files).encode()).hexdigest()


def parse_kernelslist(path):
    traces = []
    commands = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if SAFE_TRACE.fullmatch(line):
            traces.append(line)
            commands.append({"kind": "KERNEL", "member": line})
        elif MEMCPY_HTOD.fullmatch(line):
            commands.append({"kind": "MEMCPY_HTOD", "command": line})
        else:
            raise ContractError("invalid kernelslist command: %s" % line)
    if not traces:
        raise ContractError("kernelslist has no kernel trace members")
    return traces, commands


def run_grammar_smoke(parser_path, root, trace_name):
    parser = Path(parser_path).resolve()
    if not parser.is_file():
        raise ContractError("traceg grammar parser not found: %s" % parser)
    integrity = subprocess.run(
        ["xz", "-t", trace_name], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if integrity.returncode != 0:
        raise ContractError("malformed xz member: %s" % trace_name)
    try:
        completed = subprocess.run(
            [str(parser), trace_name], cwd=root, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("traceg grammar parser execution failed for %s: %s" % (trace_name, exc)) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "no diagnostic"
        raise ContractError("traceg grammar rejected %s: %s" % (trace_name, detail))
    try:
        receipt = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("traceg grammar parser emitted invalid receipt for %s" % trace_name) from exc
    need(receipt, ("status", "instructions", "thread_blocks", "opcode_counts"), "grammar receipt")
    if receipt["status"] != "TRACEG_GRAMMAR_PASS" or receipt["instructions"] <= 0 or receipt["thread_blocks"] <= 0:
        raise ContractError("traceg grammar parser returned incomplete receipt for %s" % trace_name)
    return receipt


def validate_bundle(manifest_path, parser_path=None):
    manifest = obj(manifest_path)
    if manifest.get("evidence_class") in ("C16WARP1", "MREF_SHARDED_COMPLETE_SET") or manifest.get("simulator_eligibility") == "NOT_PROVEN_LOSSLESS":
        return {
            "admitted": False, "status": "NOT_PROVEN_LOSSLESS", "sim_input_id": None,
            "reason": "C16WARP1/MREF is Native evidence, not a lossless simulator trace",
        }
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("unsupported schema_version")
    if manifest.get("evidence_class") != TRACE_SCHEMA:
        raise ContractError("unsupported evidence_class")
    need(manifest, MANIFEST_FIELDS, "SIM_COMPAT_CAPTURE_V1 manifest")
    if manifest["trace_schema"] != TRACE_SCHEMA:
        raise ContractError("unsupported trace_schema")

    for field in ("input_binding_sha256", "producer_source_sha256", "producer_binary_sha256", "tracer_build_sha256", "bundle_hash_root"):
        require_sha256(manifest[field], field)
    if not isinstance(manifest["va_width"], int) or manifest["va_width"] <= 0:
        raise ContractError("va_width must be a positive integer")
    if not isinstance(manifest.get("grid"), list) or len(manifest["grid"]) != 3 or not all(isinstance(x, int) and x > 0 for x in manifest["grid"]):
        raise ContractError("grid must contain three positive integers")
    if not isinstance(manifest.get("block"), list) or len(manifest["block"]) != 3 or not all(isinstance(x, int) and x > 0 for x in manifest["block"]):
        raise ContractError("block must contain three positive integers")

    semantics = manifest.get("instruction_semantics")
    if not isinstance(semantics, dict):
        raise ContractError("instruction_semantics must be object")
    if semantics != SEMANTIC_ENCODINGS:
        missing = sorted(set(SEMANTIC_ENCODINGS) - set(semantics))
        wrong = sorted(key for key in set(semantics) & set(SEMANTIC_ENCODINGS) if semantics[key] != SEMANTIC_ENCODINGS[key])
        raise ContractError("instruction_semantics mismatch; missing=%s wrong=%s" % (missing, wrong))
    required_control = manifest.get("required_control_opcodes")
    if not isinstance(required_control, list) or not required_control or not all(isinstance(item, str) and item for item in required_control):
        raise ContractError("required_control_opcodes must be an explicit nonempty list")

    terminal = manifest.get("terminal")
    if not isinstance(terminal, dict) or terminal.get("status") != "COMPLETE":
        raise ContractError("terminal must be COMPLETE")
    if terminal.get("drop_count") != 0 or terminal.get("overflow_count") != 0:
        raise ContractError("drop/overflow must be zero")

    root = Path(manifest_path).resolve().parent
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ContractError("files hash closure required")
    closure = {}
    for name, expected in sorted(files.items()):
        require_sha256(expected, "files[%s]" % name)
        actual = sha(member(root, name))
        if actual != expected:
            raise ContractError("hash mismatch: %s" % name)
        closure[name] = actual
    if hash_root(closure) != manifest["bundle_hash_root"]:
        raise ContractError("bundle_hash_root mismatch")

    list_name = manifest["kernelslist"]
    if list_name not in files:
        raise ContractError("kernelslist not hash-closed")
    traces, commands = parse_kernelslist(member(root, list_name))
    for name in traces:
        if name not in files:
            raise ContractError("kernelslist references unhashed member: %s" % name)
        member(root, name)

    sidecar_name = manifest["address_context_sidecar"]
    if sidecar_name not in files:
        raise ContractError("address sidecar not hash-closed")
    obj(member(root, sidecar_name))
    terminal_name = manifest["producer_terminal_receipt"]
    if terminal_name not in files:
        raise ContractError("producer terminal receipt not hash-closed")
    terminal_receipt = obj(member(root, terminal_name))
    if terminal_receipt.get("status") != "COMPLETE" or terminal_receipt.get("drop_count") != 0 or terminal_receipt.get("overflow_count") != 0:
        raise ContractError("producer terminal receipt is not COMPLETE with zero drop/overflow")

    if parser_path is None:
        raise ContractError("real traceg grammar parser is required")
    grammar_receipts = [run_grammar_smoke(parser_path, root, name) for name in traces]
    opcode_counts = {}
    for receipt in grammar_receipts:
        for opcode, count in receipt["opcode_counts"].items():
            opcode_counts[opcode] = opcode_counts.get(opcode, 0) + count
    missing_control = [opcode for opcode in required_control if opcode_counts.get(opcode, 0) == 0]
    if missing_control:
        raise ContractError("required control opcode absent: %s" % ", ".join(missing_control))

    trace_hashes = {name: closure[name] for name in traces}
    identity = {
        "schema_version": SCHEMA_VERSION,
        "producer_bundle_hash_root": manifest["bundle_hash_root"],
        "trace_member_hash_root": hash_root(trace_hashes),
        "kernelslist_sha256": closure[list_name],
        "producer_terminal_receipt_sha256": closure[terminal_name],
        "address_context_sha256": closure[sidecar_name],
    }
    for field in SIM_INPUT_FIELDS:
        if field not in identity:
            identity[field] = manifest[field]
    sim_input_id = identity_for("SIM_INPUT", identity)
    identity["sim_input_id"] = sim_input_id
    return {
        "admitted": True, "status": "ADMITTED", "sim_input_id": sim_input_id,
        "trace_count": len(traces), "command_count": len(commands),
        "instruction_count": sum(item["instructions"] for item in grammar_receipts),
        "grammar_parser_sha256": sha(Path(parser_path).resolve()), "identity": identity,
    }


def normalize(rows):
    answer = []
    seen = set()
    required = ("metric_name", "metric_value", "unit", "evidence_origin", "scientific_status", "claim_scope")
    for row in rows:
        need(row, required, "telemetry row")
        if not isinstance(row["metric_name"], str) or not row["metric_name"].startswith(PREFIXES):
            raise ContractError("unknown metric namespace")
        key = canonical(row)
        if key in seen:
            raise ContractError("conflicting/duplicate telemetry")
        seen.add(key)
        answer.append({**row, "schema_version": SCHEMA_VERSION})
    return sorted(answer, key=canonical)


def catalog_put(root, category, record):
    if category not in CATALOG_ID_FIELDS:
        raise ContractError("unknown catalog category")
    id_field = CATALOG_ID_FIELDS[category]
    key = record.get(id_field)
    if not key:
        raise ContractError("record needs %s" % id_field)
    expected = identity_for(category, record)
    if key != expected:
        raise ContractError("%s does not match deterministic identity" % id_field)
    path = Path(root) / "entries" / category / (key + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = canonical(record) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != encoded:
            raise ContractError("conflicting same-ID content")
        return {"result": "NOOP_IDENTICAL", "path": str(path)}
    path.write_text(encoded, encoding="utf-8")
    return {"result": "CREATED", "path": str(path)}


def snapshot(root, category):
    if category not in CATALOG_ID_FIELDS:
        raise ContractError("unknown catalog category")
    root = Path(root)
    directory = root / "entries" / category
    rows = [{"path": str(path.relative_to(root)), "sha256": sha(path)} for path in sorted(directory.glob("*.json"))] if directory.exists() else []
    output = {"schema_version": SCHEMA_VERSION, "category": category, "entries": rows}
    output["snapshot_id"] = stable_id("SIM_SNAPSHOT", output)
    path = root / "snapshots" / (category + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(output) + "\n", encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="cmd", required=True)
    admit = commands.add_parser("admit")
    admit.add_argument("manifest")
    admit.add_argument("--parser", required=True, help="compiled official traceg grammar-smoke driver")
    identity = commands.add_parser("identity")
    identity.add_argument("kind", choices=sorted(SCHEMAS))
    identity.add_argument("record")
    normalizer = commands.add_parser("normalize")
    normalizer.add_argument("source")
    normalizer.add_argument("output")
    put = commands.add_parser("catalog-put")
    put.add_argument("root")
    put.add_argument("category", choices=sorted(CATALOG_ID_FIELDS))
    put.add_argument("record")
    snap = commands.add_parser("snapshot")
    snap.add_argument("root")
    snap.add_argument("category", choices=sorted(CATALOG_ID_FIELDS))
    args = parser.parse_args()
    try:
        if args.cmd == "admit":
            output = validate_bundle(args.manifest, args.parser)
        elif args.cmd == "identity":
            record = obj(args.record)
            output = {"kind": args.kind, "id": identity_for(args.kind, record)}
        elif args.cmd == "normalize":
            rows = json.loads(Path(args.source).read_text(encoding="utf-8"))
            if not isinstance(rows, list):
                raise ContractError("telemetry must be an array")
            normalized = normalize(rows)
            Path(args.output).write_text(canonical(normalized) + "\n", encoding="utf-8")
            output = {"rows": len(normalized), "sha256": sha(args.output)}
        elif args.cmd == "catalog-put":
            output = catalog_put(args.root, args.category, obj(args.record))
        else:
            output = snapshot(args.root, args.category)
        print(json.dumps(output, sort_keys=True, indent=2))
        return 0
    except ContractError as exc:
        print("CONTRACT_ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
