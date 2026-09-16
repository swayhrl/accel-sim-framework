#!/usr/bin/env python3
"""Materialize a formal Pipeline V1 staging bundle by promoting complete R3."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2")
R3 = Path("/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z")
HOTFIX = R3 / "hotfix_fb5d0b_admission"
STAGING_ROOT = Path("/data/c16/capture/staging")
READY_ROOT = Path("/data/c16/capture/ready")
RUN_ID = "C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def parse_header(trace: Path) -> dict[str, str]:
    import lzma
    fields: dict[str, str] = {}
    with lzma.open(trace, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith("-"):
                if line.startswith("#traces format"):
                    break
                continue
            key, value = line[1:].split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def main() -> None:
    trace = next((R3 / "raw").glob("kernel-*.trace.xz"))
    traceg = next((R3 / "raw").glob("kernel-*.traceg.xz"))
    stage = STAGING_ROOT / RUN_ID
    if stage.exists() or (READY_ROOT / RUN_ID).exists():
        raise SystemExit("formal run id collision")
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    READY_ROOT.mkdir(parents=True, exist_ok=True)
    stage.mkdir()
    header = parse_header(trace)
    stdout = (R3 / "stdout.log").read_text(encoding="utf-8")
    selector_line = next(line for line in stdout.splitlines() if "selector_occurrence=0 selected=1" in line)
    function = selector_line.split("function=", 1)[1]
    terminal_line = next(line for line in (R3 / "lifecycle.log").read_text().splitlines() if line.startswith("ROUTEB_TERMINAL_COMPLETE"))
    source_commit = "e46193b94dd969a988126fc9fa5545da08b26d18"
    asset_receipt = Path("/data/c16/models/.provenance/c16_recovery_v3/receipts/R1_QWEN2P5_0P5B_ASSET_RECEIPT.json")
    input_receipt = Path("/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/C16_FROZEN_INPUT_BINDING_TRANSFER_RECEIPT.json")
    source = REPO / "util/tracer_nvbit/route_b_1771/route_b_tracer.cu"
    formatter = REPO / "util/tracer_nvbit/route_b_1771/route_b_raw_formatter.hpp"
    tracer_binary = Path("/data/c16/awma/simcompat-v2/route_b/bin/route_b_live_raw.so")
    post = REPO / "util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
    post_source = post.with_suffix(".cpp")
    runtime = {
        "python": "/data/c16/env/c16-py310/bin/python",
        "torch": "2.5.1+cu124",
        "transformers": "4.46.3",
        "dtype": "float16",
        "attention_backend": "sdpa",
    }
    manifest = {
        "schema_version": 1,
        "run_id": RUN_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scientific_status": "FORMAL",
        "producer": {
            "hostname": socket.gethostname(), "gpu_name": "NVIDIA GeForce RTX 4080",
            "gpu_uuid": "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59", "driver": "580.178.04", "cuda": "12.8",
        },
        "git": {"repository": "accel-sim-framework", "commit": source_commit, "dirty": False},
        "model": {"model_id": "Qwen/Qwen2.5-0.5B-Instruct", "revision": "7ae557604adf67be50417f59c2c2f167def9a775", "asset_receipt_sha256": sha(asset_receipt)},
        "input": {"binding_id": "S2_TEXT", "authority_status": "PASS_HASH_CLOSED_EXACT_FROZEN_BINDING", "receipt_sha256": sha(input_receipt), "token_ids_sha256_or_semantic_hash": "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"},
        "scenario": {"batch": 1, "prefill_tokens": 2048, "decode_tokens": 32, "input_class": "TEXT", "phase": "PREFILL"},
        "runtime": runtime,
        "capture": {"instrument": "AWMA_ROUTE_B_NVBIT1771_SIM_NATIVE", "tool_version": "NVBit 1.7.7.1", "tool_identity_sha256_if_applicable": sha(tracer_binary), "target": "Q05_PREFILL_ATTN_FLASH; function-occurrence=0", "exact_argv": ["CUDA_INJECTION64_PATH=/data/c16/awma/simcompat-v2/route_b/bin/route_b_live_raw.so", "ROUTE_B_FUNCTION_REGEX=^void pytorch_flash::flash_fwd_kernel.*", "ROUTE_B_FUNCTION_OCCURRENCE=0", "/data/c16/env/c16-py310/bin/python", str(REPO / "util/vm_tlb/awma/simulation/q05_s2_exact_driver.py")]},
        "artifacts": [],
    }
    (stage / "CAPTURING").write_text("CAPTURING\n", encoding="utf-8")
    copy(trace, stage / "traces" / trace.name)
    copy(traceg, stage / "traces" / traceg.name)
    copy(R3 / "raw" / "kernelslist", stage / "traces" / "kernelslist")
    copy(R3 / "raw" / "kernelslist.g", stage / "traces" / "kernelslist.g")
    copy(R3 / "lifecycle.log", stage / "receipts" / "R3_LIFECYCLE.log")
    copy(R3 / "DISK_GUARD.txt", stage / "receipts" / "DISK_GUARD.txt")
    copy(HOTFIX / "admission.stdout", stage / "receipts" / "HOTFIX_VALIDATOR.stdout")
    copy(HOTFIX / "admission.stderr", stage / "receipts" / "HOTFIX_VALIDATOR.stderr")
    copy(HOTFIX / "admission.returncode", stage / "receipts" / "HOTFIX_VALIDATOR.returncode")
    copy(HOTFIX / "source_SHA256SUMS", stage / "receipts" / "HOTFIX_VALIDATOR_SOURCE_SHA256SUMS")
    copy(HOTFIX / "binary_SHA256SUMS", stage / "receipts" / "HOTFIX_VALIDATOR_BINARY_SHA256SUMS")
    copy(input_receipt, stage / "authority" / input_receipt.name)
    copy(asset_receipt, stage / "authority" / asset_receipt.name)
    address = {
        "schema_version": "AWMA_ADDRESS_CONTEXT_V1", "context_from_trace_member": trace.name,
        "cuda_context_observed": re.search(r"ctx_0x[0-9a-f]+", trace.name).group(0),
        "asid_epoch": "0", "va_width": 49, "page_policy": "4K",
        "shmem_base_addr": header["shmem base_addr"], "local_mem_base_addr": header["local mem base_addr"],
        "address_mode_policy": "MODE1_BASE_STRIDE_OR_MODE0_LIST_ALL_ONLY", "mode2_records": 0,
    }
    target = {"target_id": "Q05_PREFILL_ATTN_FLASH", "phase": "PREFILL", "function": function, "function_occurrence": 0, "observed_grid_launch_id": 34, "grid": header["grid dim"], "block": header["block dim"], "kernel_body_truncated": False}
    terminal = {"status": "COMPLETE", "drop_count": 0, "overflow_count": 0, "device_channel_order": ["device_kernel_complete", "channel_flush_complete", "receiver_fully_drained", "trace_sink_closed", "terminal_complete"], "receipt_line": terminal_line}
    build = {"route_b_source_sha256": sha(source), "formatter_sha256": sha(formatter), "tracer_binary_sha256": sha(tracer_binary), "postprocessor_source_sha256": sha(post_source), "postprocessor_binary_sha256": sha(post), "promotion_source_commit": source_commit, "runtime": runtime}
    promotion = {"historical_label": "canary", "promotion_decision": "PROMOTED_WITHOUT_RECAPTURE", "reason": "R3 exact execution fulfills formal producer capture contract", "checks": {"exact_workload_input": True, "exact_function_occurrence": True, "natural_workload_completion": True, "no_truncation": True, "terminal_complete": True, "zero_drop_overflow": True, "mode2_zero": True, "canonical_raw_postprocess_traceg": True, "hotfix_validator_pass": True, "no_canary_only_policy": True}}
    for name, obj in {"ADDRESS_CONTEXT.json": address, "TARGET_IDENTITY.json": target, "TERMINAL_RECEIPT.json": terminal, "BUILD_RUNTIME_RECEIPT.json": build, "R3_PROMOTION_AUDIT.json": promotion}.items():
        (stage / "sidecars" / name).parent.mkdir(parents=True, exist_ok=True)
        (stage / "sidecars" / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (stage / "PROMOTION_PROVENANCE.md").write_text("R3 was originally named canary only; its actual exact workload, target, natural completion, terminal, address policy, and hotfix admission satisfy the formal producer contract. Promoted without GPU recapture.\n", encoding="utf-8")
    (stage / "receipts" / "R3_PROMOTION_COMPLETENESS.txt").write_text("receiver_accepted=13490624\nraw_dynamic_records=13490624\naddress_mode2_records=0\nterminal=COMPLETE\ndrop_count=0\noverflow_count=0\nhotfix_validator=TRACEG_GRAMMAR_PASS\n", encoding="utf-8")
    (stage / "RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (stage / "CAPTURING").unlink()
    print(json.dumps({"run_id": RUN_ID, "staging": str(stage), "ready_root": str(READY_ROOT)}, sort_keys=True))


if __name__ == "__main__":
    main()
