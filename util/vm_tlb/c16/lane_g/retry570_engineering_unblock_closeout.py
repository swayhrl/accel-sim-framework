#!/usr/bin/env python3
"""Publish Retry570 NVBit first-use/version-differential engineering evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256

STATUS = "NVBIT_RETRY570_V175_ENGINEERING_UNBLOCK_QUALIFIED"
SCHEMA = "C16_G_RETRY570_ENGINEERING_UNBLOCK_CLOSEOUT_V1"
P1 = "first_use_completion_v18_empty_eager_9a12ff1a"
OFFICIAL = "version_differential_v175_official_ac4f678a"
EMPTY = "version_differential_v175_empty_lazy_ac4f678a"
LANE = "version_differential_v175_lane_g_first_kernel_ac4f678a"
P1_RUN = "b3591474-e92b-475c-96eb-a0d1f6b27ff9"
OFFICIAL_RUN = "d1cff89a-bb99-4896-8cc7-02939187877a"
EMPTY_RUN = "97979f32-df6e-4555-abc7-f3ea7d97f89e"
LANE_RUN = "2844eab2-8e9d-4447-9e06-fe5a047e1e03"
P1_RUNTIME_COMMIT = "9a12ff1aec0410f6795b68c7df1710c3d5610fec"
LEDGER_FIX_COMMIT = "f56b33e501366b01ffc7d60252de8ce2044202c7"
VERSION_RUNTIME_COMMIT = "ac4f678a815954e4ddb22c15d9a8d3841fca86a3"
ROOT_CAUSE_COMMIT = "82498cc792a1e0c9705c313e392a91aedcde1242"
NVBIT_175_ARCHIVE_SHA = "e2290da5e35a43fc4c74917dd08e1d41ece3e21bfca6fd7c6dc590c9c8385328"
NVBIT_175_CORE_SHA = "562348c32b88bf3e5b32d1895202893adb79f32b896e3cac56b29a306de40a12"
NVBIT_175_OFFICIAL_SHA = "fc19c2254a7f6978fe543a826070edeed391b344ca174804719714d2bc8912a3"
NVBIT_175_EMPTY_SHA = "0610336515903df3e329d53c1c709ac0bd9eacc98b470aba5e8ed58e074047a5"
NVBIT_175_LANE_SHA = "9e059b6a5b17a74e597169e365ad05d1e82517decad9974868b2b8a195132ae5"
LIBTORCH_SHA = "761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a"
LEDGER_SHA = "3f12212d9d7af287f8130f86b9016fa25015ea253bb8523b233e2a46bc92352f"

REMOTE_HASHES = {
    f"{P1}/final_state.json": "b6eac32a803e0546e1e51d6393bb3201f507c4aa318e078d19651da937edb7ed",
    f"{P1}/remote_transaction.json": "af7338f06942c9fe8016aa643a3e567597694d5f68b9f5f2872e0daec08b90a8",
    f"{P1}/stage.json": "4be5d46748f2f6d75323400c55bac1a50765aa311d0c7652fb2ddf056eba219e",
    f"{P1}/stderr.log": "171eb9c99d526824344626019f59b3e174847dd29b963f681c7689ae25a4f51a",
    f"{P1}/stdout.log": "b6f0c0d07e100bd5d23b6b552add3c7516187bd1065b48acb0ef126808a29636",
    f"{EMPTY}/analysis.json": "c81796a59dcadc46242d2d0b745371f56b551658380411a179c1c7abbc6be9b1",
    f"{EMPTY}/child_receipt.json": "124d5f17f79862db81afbfd7da2a704338b1b9834b54519914984f74b8c0cfc8",
    f"{EMPTY}/receipt.json": "b49dd8f6ac07aeaab9648e2bb2b152dd97de1da4c73b0ae50c77c92e4aaff387",
    f"{EMPTY}/remote_transaction.json": "cc0893cf44d3dd24c780c7a648996a27e7fd105da42a028e06e8ab6786b4cc5a",
    f"{EMPTY}/stage.json": "e63bab354c3eb4210fdeb766d622814b7f144f3d9f17485861698f64f0e3b48c",
    f"{EMPTY}/stderr.log": "171eb9c99d526824344626019f59b3e174847dd29b963f681c7689ae25a4f51a",
    f"{EMPTY}/stdout.log": "d685ec530a719055f5db183b3db9f76106a52363eda20f883b598187c3422706",
    f"{LANE}/child_receipt.json": "64813afd45d34ec5b640c69eeeda3de3c3adb1c9346803fd9e7c29641df19cd0",
    f"{LANE}/receipt.json": "88b3c34a54252e7d0eaa75a171994410c906ccf5f73501931c01069453534d4e",
    f"{LANE}/remote_transaction.json": "6fbebe44f51a2c86b14e5d630b7db9b7186398e0e4a55a3fc9763a9b6d7debae",
    f"{LANE}/samples.jsonl": "95226482dd7f97757e1623d681ff239b2972eee2dd829504976452f5600b98cc",
    f"{LANE}/stacks/stack_snapshot_000.txt": "8db4f61b47361993056a1fd741c090dc32a6d72eefcf18032528cc1f0c2da561",
    f"{LANE}/stacks/stack_snapshot_001.txt": "84e0808cd224027cc36f432b09f58ce0482ec4b0956137fc08e11fdb33aedb9d",
    f"{LANE}/stage.json": "a2423f6e790861389dc31a7a83547b223a4e074ca3b4169aeb3e95e99c79d143",
    f"{LANE}/stderr.log": "171eb9c99d526824344626019f59b3e174847dd29b963f681c7689ae25a4f51a",
    f"{LANE}/stdout.log": "42cc957f743a93904c76cb292e84de00ff8349a4a29e7cd1f39d02170fdda789",
    f"{LANE}/traces/kernelslist_ctx_0x555f6c9f1d10": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    f"{LANE}/traces/stats_ctx_0x555f6c9f1d10": "4a3d6acc005fe389b8a395707e0b397e62685c5087840a0988a8108f523c438d",
    f"{OFFICIAL}/receipt.json": "b24cb3b94813594d880f77a8f90b93927e3991a4d3372770798221fd2bae49fe",
    f"{OFFICIAL}/stderr.log": "171eb9c99d526824344626019f59b3e174847dd29b963f681c7689ae25a4f51a",
    f"{OFFICIAL}/stdout.log": "a7b7fb169d5e61d39b5cf5739950e23d996d173e50c66faa95fafd6e0b409a24",
}

REPORT = "NVBIT_ENGINEERING_UNBLOCK_REPORT.md"
MATRIX = "NVBIT_VERSION_DIFFERENTIAL.tsv"
READY = "PREWARM_READY_MEASUREMENT_CONTRACT.md"
RECEIPT = "NVBIT_ENGINEERING_UNBLOCK_RECEIPT.json"
RAW_INDEX = "RAW_ARTIFACT_INDEX.json"
TRANSFER = "NVBIT_ENGINEERING_UNBLOCK_TRANSFER_RECEIPT.json"
MANIFEST = "PUBLISH_MANIFEST.json"
VALIDATION = "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (REPORT, MATRIX, READY, RECEIPT, RAW_INDEX, TRANSFER)


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot load JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def ledger_entry(ledger: dict[str, Any], run_id: str) -> dict[str, Any]:
    rows = [row for row in ledger.get("entries", []) if row.get("run_id") == run_id]
    if len(rows) != 1:
        raise ContractError(f"expected exactly one ledger entry for {run_id}")
    row = rows[0]
    if row.get("evidence_classification") != "NON_SCIENTIFIC_DIAGNOSTIC" or row.get("raw_bytes") != 0:
        raise ContractError(f"diagnostic ledger classification differs for {run_id}")
    return row


def observe(raw: Path, p1_local_wall: float, official_local_wall: float,
            empty_local_wall: float, lane_local_wall: float) -> dict[str, Any]:
    found = {p.relative_to(raw).as_posix() for name in (P1, OFFICIAL, EMPTY, LANE)
             for p in (raw / name).rglob("*") if p.is_file()}
    if found != set(REMOTE_HASHES):
        raise ContractError("local raw payload set differs from fixed remote inventory")
    entries = []
    for relative, expected in sorted(REMOTE_HASHES.items()):
        path = raw / relative
        if sha256_file(path) != expected:
            raise ContractError(f"dual-endpoint SHA mismatch: {relative}")
        entries.append({"relative_path": relative, "size_bytes": path.stat().st_size,
                        "remote_sha256": expected, "local_sha256": expected, "match": True})
    ledger_path = raw / "EXECUTION_BUDGET_LEDGER.json"
    if sha256_file(ledger_path) != LEDGER_SHA:
        raise ContractError("execution budget ledger differs from transferred remote SHA")
    ledger = load(ledger_path)
    ledgers = {run: ledger_entry(ledger, run) for run in (P1_RUN, OFFICIAL_RUN, EMPTY_RUN, LANE_RUN)}

    p1_stdout = (raw / P1 / "stdout.log").read_text(encoding="utf-8", errors="replace")
    p1_stage = load(raw / P1 / "stage.json")
    p1_final = load(raw / P1 / "final_state.json")
    p1_tx = load(raw / P1 / "remote_transaction.json")
    if ("NVidia Binary Instrumentation Tool v1.8" not in p1_stdout or p1_stage.get("event") != "INPUT_PREPARATION_BEGIN" or
            any(marker in p1_stdout for marker in ("event=READY", "event=ROUND1_BEGIN", "event=ROUND2_BEGIN")) or
            p1_tx.get("remote_transaction_cap_s") != 68 or p1_tx.get("remote_transaction_wall_s") > 68 or
            not p1_final.get("child_pid_present_in_gpu_processes") or p1_final.get("gpu_utilization_and_memory", "").split(",")[0] != "0"):
        raise ContractError("v1.8 first-use timeout boundary differs")
    if ledgers[P1_RUN].get("terminal_status") != "FAILED_OR_ABORTED" or ledgers[P1_RUN].get("elapsed_seconds", 0) < 60:
        raise ContractError("v1.8 first-use ledger row does not retain the bounded failure")

    official = load(raw / OFFICIAL / "receipt.json")
    empty = load(raw / EMPTY / "receipt.json")
    lane = load(raw / LANE / "receipt.json")
    if (official.get("status") != "NVBIT_OFFICIAL_VECTORADD_SMOKE_PASS" or official.get("nvbit_version") != "1.7.5" or
            official.get("tool", {}).get("sha256") != NVBIT_175_OFFICIAL_SHA or official.get("trace_generated") is not False):
        raise ContractError("NVBit 1.7.5 official smoke differs")
    empty_stdout = (raw / EMPTY / "stdout.log").read_text(encoding="utf-8", errors="replace")
    if (empty.get("status") != "MODULE_FIRST_USE_2X2_COMPLETE" or empty.get("nvbit_version") != "1.7.5" or
            empty.get("tool", {}).get("sha256") != NVBIT_175_EMPTY_SHA or empty.get("trace_generated") is not False or
            "mode_name=CU_MODULE_EAGER_LOADING" not in empty_stdout or "event=EXACT_OPERATION_RETURN" not in empty_stdout):
        raise ContractError("NVBit 1.7.5 EMPTY exact result differs")
    lane_tx = load(raw / LANE / "remote_transaction.json")
    trace_files = list((raw / LANE).rglob("*.trace")) + list((raw / LANE).rglob("*.trace.xz"))
    if (lane.get("terminal_status") != "COMPLETE" or lane.get("nvbit_tool", {}).get("sha256") != NVBIT_175_LANE_SHA or
            lane.get("first_cuda_completion_elapsed_seconds") is None or lane.get("trace_generated") is not False or
            trace_files or lane_tx.get("trace_file_count") != 0):
        raise ContractError("NVBit 1.7.5 Lane G first-kernel smoke differs or emitted trace")
    if any(value <= 0 for value in (p1_local_wall, official_local_wall, empty_local_wall, lane_local_wall)):
        raise ContractError("local SSH wall observations must be positive")
    return {"entries": entries, "ledger": ledgers, "p1_tx": p1_tx, "official": official,
            "empty": empty, "lane": lane, "lane_tx": lane_tx,
            "walls": {"p1": p1_local_wall, "official": official_local_wall,
                      "empty": empty_local_wall, "lane": lane_local_wall}}


def matrix(data: dict[str, Any]) -> str:
    p1_elapsed = data["ledger"][P1_RUN]["elapsed_seconds"]
    return (
        "nvbit_version\ttool\tworkload\trequested_loading\tobserved_loading\tstatus\ttarget_wall_s\tremote_transaction_wall_s\tlocal_ssh_wall_s\tprocess_to_ready_s\tround1_s\tround2_s\ttrace_generated\tscientific_eligible\n"
        f"1.8\tEMPTY_CALLBACK\tEXACT_INDEX_SELECT_TWO_ROUND_QUALIFICATION\tEAGER\tNOT_CAPTURED_BEFORE_READY\tHANG_BEFORE_READY\t{p1_elapsed:.6f}\t{data['p1_tx']['remote_transaction_wall_s']:.6f}\t{data['walls']['p1']:.6f}\tNA\tNA\tNA\tFALSE\tFALSE\n"
        f"1.7.5\tOFFICIAL_INSTR_COUNT_BB\tVECTORADD\tVENDOR_DEFAULT\tVENDOR_EAGER_DEFAULT\tPASS\t{data['official']['elapsed_seconds']:.6f}\tNOT_CAPTURED_POST_RUN_RECEIPT_WRITE_FAILURE\t{data['walls']['official']:.6f}\tNA\tNA\tNA\tFALSE\tFALSE\n"
        f"1.7.5\tEMPTY_CALLBACK\tEXACT_INDEX_SELECT\tLAZY\tCU_MODULE_EAGER_LOADING\tPASS\t{data['empty']['target_wall_s']:.6f}\t5.772390\t{data['walls']['empty']:.6f}\tNA\tNA\tNA\tFALSE\tFALSE\n"
        f"1.7.5\tLANE_G_C16_TRACER_NO_MATCH_RANGE\tC2_TENSOR_FILL_FIRST_KERNEL\tEAGER\tVENDOR_EAGER_DEFAULT\tPASS\t{data['lane']['elapsed_seconds']:.6f}\t{data['lane_tx']['remote_transaction_wall_s']:.6f}\t{data['walls']['lane']:.6f}\t{data['lane']['first_cuda_completion_elapsed_seconds']:.6f}\tNA\tNA\tFALSE\tFALSE\n")


def ready_contract() -> str:
    return """# Retry570 prewarm/READY/measurement contract

This is an engineering qualification, not permission to run a model, trace,
scientific capture, or C target.

The only currently qualified unblock candidate is the frozen NVBit 1.7.5
archive/core combined with the existing Lane G tracer source. A future,
separately authorized process must follow this order:

1. verify GPU, driver 570.124.04, CUDA 12.4, torch 2.5.1+cu124,
   `libtorch_cuda.so`, NVBit archive/core, and Lane G tool hashes;
2. set `CUDA_MODULE_LOADING=EAGER` before process start;
3. outside `MEASUREMENT_ACTIVE`, execute a bounded no-trace prewarm;
4. require normal exit, first-kernel completion, zero `.trace` payloads, and
   no surviving child before emitting `READY`;
5. only after `READY`, acquire the shared budget lease and create
   `MEASUREMENT_ACTIVE` for a separately authorized formal capture.

Prewarm artifacts and timing are diagnostic-only and must never enter native
timing or C/H scientific inputs. A version switch is an implementation change,
so any future model/capture requires a clean source/tool checkpoint plus model-
level identity/correctness requalification. NVBit 1.8 remains unqualified on
this node; no timeout extension is implied.
"""


def receipt(data: dict[str, Any], producer: str, raw_index_path: Path) -> dict[str, Any]:
    return {"schema_version": SCHEMA, "status": STATUS, "scientific_eligible": False,
            "scope": "ENGINEERING_UNBLOCK_DIAGNOSTIC_ONLY_NO_MODEL_NO_TRACE_NO_CAPTURE_NO_C_TARGET",
            "producer_implementation_commit": producer, "root_cause_milestone_commit": ROOT_CAUSE_COMMIT,
            "runtime_commits": {"v1_8_first_use": P1_RUNTIME_COMMIT, "ledger_enum_fix_no_rerun": LEDGER_FIX_COMMIT,
                                "version_differential_and_lane_smoke": VERSION_RUNTIME_COMMIT},
            "environment": {"gpu": "NVIDIA GeForce RTX 3090/SM86", "gpu_uuid": "GPU-0c257cc7-45dd-5533-5435-7f42e7008e0e",
                            "driver": "570.124.04", "cuda_toolkit": "12.4", "torch": "2.5.1+cu124",
                            "libtorch_cuda_sha256": LIBTORCH_SHA},
            "nvbit_1_7_5": {"official_release_url": "https://github.com/NVlabs/NVBit/releases/download/v1.7.5/nvbit-Linux-x86_64-1.7.5.tar.bz2",
                            "archive_sha256": NVBIT_175_ARCHIVE_SHA, "core_libnvbit_sha256": NVBIT_175_CORE_SHA,
                            "official_instr_count_bb_sha256": NVBIT_175_OFFICIAL_SHA,
                            "empty_callback_sha256": NVBIT_175_EMPTY_SHA, "lane_g_tracer_sha256": NVBIT_175_LANE_SHA},
            "decision": {"v1_8_first_use_qualification": "HANG_BEFORE_READY_WITHIN_60_SECOND_TARGET_CAP",
                         "process_to_ready_s": None, "round1_s": None, "round2_s": None,
                         "one_time_or_repeated": "NOT_DETERMINED_V1_8_NEVER_REACHED_READY",
                         "version_differential": "NVBIT_VERSION_SENSITIVE_CORE_PATH",
                         "v1_7_5_official_smoke": "PASS", "v1_7_5_empty_exact": "PASS",
                         "v1_7_5_lane_g_first_kernel_smoke": "PASS_ZERO_TRACE",
                         "recommended_unblock": "PIN_NVBIT_1_7_5_EAGER_PREWARM_THEN_READY_THEN_MEASUREMENT_ACTIVE"},
            "loading_mode_caveat": "1.7.5_REQUESTED_LAZY_BUT_VENDOR_CORE_REPORTED_AND_QUERY_CONFIRMED_EAGER",
            "raw_artifact_index": {"path": RAW_INDEX, "sha256": sha256_file(raw_index_path)},
            "remote_only_required_artifact_count": 0, "active_gpu_process_count_at_closeout": 0,
            "active_diagnostic_process_count_at_closeout": 0, "measurement_active_present_at_closeout": False,
            "still_forbidden_without_new_authorization": ["model", "Llama", "Qwen", "trace", "scientific_capture", "C_target", "300s_long_watch"]}


def report(data: dict[str, Any]) -> str:
    return f"""# Retry570 NVBit engineering unblock qualification

Status: `{STATUS}` (diagnostic/engineering only).

The prior root cause remains `NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED`.
The unique NVBit 1.8 EMPTY+EAGER first-use window reached CUDA init and input
preparation but not `READY` in {data['ledger'][P1_RUN]['elapsed_seconds']:.6f}s.
Consequently `process_to_ready_s`, `round1_s`, and `round2_s` are absent, and
one-time versus repeated behavior is **not determined** for 1.8. Its failed
run remains in the budget ledger; a later source-only fix corrected an invalid
classification name without rerunning the GPU window.

With GPU, driver, CUDA, torch, libtorch and exact reproducer held fixed, NVBit
1.7.5 passed official `instr_count_bb + vectoradd`, then its EMPTY exact
reproducer completed in {data['empty']['target_wall_s']:.6f}s. The requested
LAZY setting was overridden by the vendor version: banner and CUDA query both
show EAGER. This caveat is preserved rather than calling the observed modes
identical. The contrast remains version-sensitive because the independent 1.8
EAGER window did not reach READY.

The normal Lane G C16 tracer rebuilt against frozen NVBit 1.7.5 then completed
one EAGER C2 tensor-fill first-kernel smoke. Submission was at
{data['lane']['first_cuda_submission_elapsed_seconds']:.6f}s and completion at
{data['lane']['first_cuda_completion_elapsed_seconds']:.6f}s; total target and
remote transaction wall were {data['lane']['elapsed_seconds']:.6f}s and
{data['lane_tx']['remote_transaction_wall_s']:.6f}s. An impossible dynamic
range kept tracing inactive: the post-run scan found zero `.trace`/`.trace.xz`
files. This qualifies a minimal engineering path, not any model or capture.

Recommended unblock: pin exact NVBit 1.7.5 archive/core/tool hashes, use EAGER,
perform a bounded zero-trace prewarm outside `MEASUREMENT_ACTIVE`, emit READY
only after terminal/identity/zero-trace/process-cleanup checks, and create the
measurement gate afterward. Any future model/capture still needs explicit
authorization and model-level correctness/identity requalification.

All 25 retained remote payloads plus the final execution ledger are locally
SHA-closed. `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`, active GPU and diagnostic
process counts are zero, and no measurement marker remains. No model, Llama,
Qwen, trace, scientific capture, C target, 300-second watch, or 6+6 rerun was
performed.
"""


def manifest(directory: Path, producer: str) -> dict[str, Any]:
    return {"schema_version": "C16_G_RETRY570_ENGINEERING_UNBLOCK_PUBLISH_V1", "status": STATUS,
            "scientific_eligible": False, "producer_implementation_commit": producer,
            "files": [{"path": name, "size_bytes": (directory / name).stat().st_size,
                       "sha256": sha256_file(directory / name)} for name in PAYLOADS],
            "raw_payloads_committed": False, "remote_only_required_artifact_count": 0}


def validate(directory: Path) -> dict[str, Any]:
    publication, seen = load(directory / MANIFEST), set()
    rows = publication.get("files")
    if publication.get("status") != STATUS or publication.get("scientific_eligible") is not False or not isinstance(rows, list):
        raise ContractError("engineering-unblock manifest header differs")
    for row in rows:
        path = row.get("path") if isinstance(row, dict) else None
        if path not in PAYLOADS or path in seen or not isinstance(row.get("size_bytes"), int) or not valid_sha256(row.get("sha256")):
            raise ContractError("manifest row differs, duplicates, or is malformed")
        payload = directory / path
        if not payload.is_file() or payload.stat().st_size != row["size_bytes"] or sha256_file(payload) != row["sha256"]:
            raise ContractError(f"manifest payload fails existence/size/SHA: {path}")
        seen.add(path)
    if seen != set(PAYLOADS) or load(directory / RECEIPT).get("status") != STATUS:
        raise ContractError("manifest payload set is incomplete")
    return {"schema_version": "C16_G_RETRY570_ENGINEERING_UNBLOCK_VALIDATION_V1", "status": "PASS",
            "publish_manifest": {"path": MANIFEST, "sha256": sha256_file(directory / MANIFEST)},
            "checks": {"payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0,
                       "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True}}


def write(directory: Path, raw: Path, producer: str, walls: tuple[float, float, float, float]) -> None:
    data = observe(raw, *walls)
    directory.mkdir(parents=True, exist_ok=True)
    index = {"schema_version": "C16_G_RETRY570_ENGINEERING_UNBLOCK_RAW_INDEX_V1",
             "status": "PASS_DUAL_ENDPOINT_SIZE_SHA256_CLOSED", "scientific_eligible": False,
             "remote_raw_base": "/root/autodl-tmp/c16_retry570/raw", "local_raw_base": str(raw),
             "entries": data["entries"], "execution_budget_ledger": {"size_bytes": (raw / "EXECUTION_BUDGET_LEDGER.json").stat().st_size,
                 "remote_sha256": LEDGER_SHA, "local_sha256": LEDGER_SHA, "match": True},
             "remote_only_required_artifact_count": 0, "raw_payloads_committed": False}
    atomic_json(directory / RAW_INDEX, index)
    atomic_json(directory / RECEIPT, receipt(data, producer, directory / RAW_INDEX))
    atomic_json(directory / TRANSFER, {"schema_version": "C16_G_RETRY570_ENGINEERING_UNBLOCK_TRANSFER_V1",
        "status": "PASS_REMOTE_TO_LOCAL_SIZE_SHA256_CLOSURE", "payload_count": len(data["entries"]) + 1,
        "mismatch_count": 0, "remote_only_required_artifact_count": 0,
        "raw_artifact_index": {"path": RAW_INDEX, "sha256": sha256_file(directory / RAW_INDEX)}})
    (directory / MATRIX).write_text(matrix(data), encoding="utf-8")
    (directory / READY).write_text(ready_contract(), encoding="utf-8")
    (directory / REPORT).write_text(report(data), encoding="utf-8")
    atomic_json(directory / MANIFEST, manifest(directory, producer))
    atomic_json(directory / VALIDATION, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-base", type=Path)
    parser.add_argument("--producer-implementation-commit")
    parser.add_argument("--p1-local-ssh-wall-s", type=float, default=61.171210)
    parser.add_argument("--official-local-ssh-wall-s", type=float, default=1.2239590724930167)
    parser.add_argument("--empty-local-ssh-wall-s", type=float, default=6.147798411548138)
    parser.add_argument("--lane-local-ssh-wall-s", type=float, default=7.177604727447033)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        if args.raw_base is None or not valid_sha256(args.producer_implementation_commit or ""):
            raise ContractError("write requires raw base and exact producer implementation commit")
        write(args.directory, args.raw_base, args.producer_implementation_commit,
              (args.p1_local_ssh_wall_s, args.official_local_ssh_wall_s,
               args.empty_local_ssh_wall_s, args.lane_local_ssh_wall_s))
        print(f"PASS Retry570 engineering-unblock publication write: {args.directory}")
    else:
        print("PASS Retry570 engineering-unblock validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 engineering-unblock closeout: {exc}")
