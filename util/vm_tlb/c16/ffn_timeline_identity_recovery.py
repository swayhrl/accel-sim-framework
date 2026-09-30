#!/usr/bin/env python3
"""Recover the accepted GUD84 identity and emit the bounded timeline authorization."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import tempfile
from pathlib import Path


PRODUCER = "eae1cc4d831ae8459da558cf1358bb8daf8d76e6"
CONSUMER = "278964bfb243a93adf43e748eb3e067e34b16b8a"
BASE = "75c45a4896e84c49df190aa649416d24aa02ea09"
PATCH_COMMIT = "94bb7b630cb7e11b3576b3bd94f42b417b2af878"
PACK = "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1"
PRODUCER_PACK = "docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_109_V1"
CONSUMER_PACK = "docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_CONSUMER_174NEW_V1"
OLD_PACK = "docs/vm_tlb/review_packs/C16_FFN_HANDOFF_AUTHORITY_RECOVERY_V1"
ARCHIVE_PACK = "docs/vm_tlb/review_packs/C16_OLD174_RECOVERY_ARCHIVE_TO_164_V1"
RUNNER = "util/vm_tlb/c16/e1_operator_family_natural.py"
COMMON = "util/vm_tlb/c16/e1_residency_common.py"
PERSISTENCE = "util/vm_tlb/c16/e1_cuda_persistence.py"
PATCH_NAME = "INSTRUMENTATION_DELTA.patch"
EXPECTED_RUNNER_SHA = "902bd8993483290850072afc37245aa7ba80afd821952c7a91fabec0b8e18ea5"
EXPECTED_PATCH_SHA = "06cc0656125e0d5900330f6576b071637de1d09a7e1c9f501929d5577b1361be"
EXPECTED_PATCHED_SHA = "ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb"
TOKEN_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"
TEXT_SHA = "bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208"
TOKENS = [23578, 11, 323, 3950]
SOURCE_IDS = [34, 16, 21, 93377, 419, 2805, 5810, 43558, 1946, 1573, 894, 9867, 22670, 975, 624, 785, 23172, 9569, 11, 45958, 23578, 11, 323, 3950, 28360, 1969, 7146, 6822, 198, 983, 279, 51572, 1614, 23578, 12433, 553, 21272, 362, 624]
ARCHIVE = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c16_recovery_v3")
TOKEN_FILE = ARCHIVE / "receipts/R2_QWEN2P5_7B_RAW_RUNTIME_BINDINGS/S2_TEXT/token_ids.json"
TOKEN_RECEIPT = ARCHIVE / "staging/qwen2p5_7b_raw_p2_inputs_v1/a_assets/TOKEN_RECEIPTS/c16_qwen25_7b_raw_reference/TEXT_T2048.json"
TEXT_FILE = ARCHIVE / "staging/qwen2p5_7b_raw_p2_inputs_v1/a_assets/inputs/TEXT.txt"
MODEL_RECEIPT = ARCHIVE / "receipts/R1_QWEN2P5_7B_AWQ_ASSET_RECEIPT.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"])


def git_blob(commit: str, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"{commit}:{path}"], text=True).strip()


def file_authority(commit: str, path: str) -> dict[str, str]:
    data = git_bytes(commit, path)
    return {"file": path, "commit": commit, "sha256": sha(data), "git_blob": git_blob(commit, path)}


def compact(value) -> str:
    if isinstance(value, str):
        return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def validate_authority(repo: Path) -> dict:
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != PATCH_COMMIT:
        raise RuntimeError("generator must run from the frozen instrumentation commit")
    runner = git_bytes(PRODUCER, RUNNER)
    if sha(runner) != EXPECTED_RUNNER_SHA:
        raise RuntimeError("accepted runner SHA mismatch")
    patch_path = repo / PACK / PATCH_NAME
    if sha(patch_path.read_bytes()) != EXPECTED_PATCH_SHA:
        raise RuntimeError("instrumentation patch SHA mismatch")
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "e1_operator_family_natural.py"
        target.write_bytes(runner)
        subprocess.run(["patch", "-s", str(target)], input=patch_path.read_bytes(), check=True)
        if sha(target.read_bytes()) != EXPECTED_PATCHED_SHA:
            raise RuntimeError("patched runner SHA mismatch")

    raw_paths = [f"{PRODUCER_PACK}/RAW_NATIVE_CONTROL_GUD84_run{i}.json" for i in range(7)]
    raw = [json.loads(git_bytes(PRODUCER, p)) for p in raw_paths]
    reference_order = raw[0]["call_order"]
    reference_bindings = [(r["layer"], r["role"], r["decode_index"], r["token_id"], r["input_sha256"], r["output_sha256"]) for r in raw[0]["occurrences"]]
    for index, run in enumerate(raw):
        assert run["status"] == "PASS"
        assert run["condition"] == "CONTROL_GUD84" and run["run_index"] == index
        assert run["generated_token_ids_D0_D3"] == TOKENS
        assert len(run["module_census"]) == 84 and len(run["call_order"]) == 420 and len(run["occurrences"]) == 336
        assert run["call_order"] == reference_order
        bindings = [(r["layer"], r["role"], r["decode_index"], r["token_id"], r["input_sha256"], r["output_sha256"]) for r in run["occurrences"]]
        assert bindings == reference_bindings
        assert run["all_84_ffn_instrumented"] and run["no_inner_loop_synchronize"] and run["no_reset_between_transitions"]

    independent = json.loads(git_bytes(CONSUMER, f"{CONSUMER_PACK}/INDEPENDENT_NATURAL_CALL_ORDER.json"))
    assert independent["status"] == "PASS"
    assert independent["generated_token_ids"] == TOKENS
    translated = {
        phase: [
            {"phase": phase, "ordinal": row["natural_order_index"], "layer": row["layer_index"], "role": row["role"]}
            for row in independent["derived_order"][phase]
        ]
        for phase in ["PREFILL", "D0", "D1", "D2", "D3"]
    }
    assert [row for phase in ["PREFILL", "D0", "D1", "D2", "D3"] for row in translated[phase]] == reference_order

    token_bytes = TOKEN_FILE.read_bytes()
    assert sha(token_bytes) == TOKEN_SHA and len(json.loads(token_bytes)) == 2048
    receipt = json.loads(TOKEN_RECEIPT.read_bytes())
    assert sha(TOKEN_RECEIPT.read_bytes()) == "2424297397c48163f850a58928da9414a88def22042dd14d066b38d3b4c1f382"
    assert receipt["source_token_ids"] == SOURCE_IDS and receipt["target_token_ids"] == json.loads(token_bytes)
    assert sha(TEXT_FILE.read_bytes()) == TEXT_SHA
    model_receipt = json.loads(MODEL_RECEIPT.read_bytes())
    assert sha(MODEL_RECEIPT.read_bytes()) == "23a7e5c0107a528853d79e2e63ea6a3a9caa583bc39833bb1c04a83d0ac5b76d"
    assert model_receipt["identity"]["revision"] == "b25037543e9394b818fdfca67ab2a00ecc7dd641"
    manifest = git_bytes(PRODUCER, f"{ARCHIVE_PACK}/SNAPSHOT_MANIFEST.tsv").decode()
    assert TOKEN_SHA in manifest and "23a7e5c0107a528853d79e2e63ea6a3a9caa583bc39833bb1c04a83d0ac5b76d" in manifest

    ncu = git_bytes(PRODUCER, f"{PRODUCER_PACK}/RAW_NCU_L0_GATE_PROJ_D3_CONTROL_GUD84_SESSION.csv").decode()
    for required in ["NVIDIA GeForce RTX 4080", '"multiprocessor_count","76"', '"compute_capability_major","8"', '"compute_capability_minor","9"', "/data/c16/env/c16-awq-v6/bin/python", "--condition CONTROL_GUD84 --run-index 600"]:
        assert required in ncu
    migration = json.loads(git_bytes(PRODUCER, "docs/vm_tlb/codex_handoff/c16/4080_migration/C16_4080_MIGRATION_SOURCE_RECEIPT.json"))
    assert migration["software_environment"]["torch"] == "2.5.1+cu124"
    assert migration["software_environment"]["transformers"] == "4.46.3"
    assert migration["software_environment"]["autoawq"] == "0.2.7.post3"
    return {
        "raw0": raw[0],
        "model_receipt": model_receipt,
        "token_receipt": receipt,
        "authorities": {
            "runner": file_authority(PRODUCER, RUNNER),
            "common": file_authority(PRODUCER, COMMON),
            "persistence": file_authority(PRODUCER, PERSISTENCE),
            "policy": file_authority(PRODUCER, f"{PRODUCER_PACK}/OPERATOR_FAMILY_POLICY_CONTRACT.json"),
            "order": file_authority(PRODUCER, f"{PRODUCER_PACK}/NATURAL_FFN_CALL_ORDER.json"),
            "raw0": file_authority(PRODUCER, raw_paths[0]),
            "ncu": file_authority(PRODUCER, f"{PRODUCER_PACK}/RAW_NCU_L0_GATE_PROJ_D3_CONTROL_GUD84_SESSION.csv"),
            "consumer_order": file_authority(CONSUMER, f"{CONSUMER_PACK}/INDEPENDENT_NATURAL_CALL_ORDER.json"),
            "consumer_sources": file_authority(CONSUMER, f"{CONSUMER_PACK}/SOURCE_ANCHORS.json"),
            "archive": file_authority(PRODUCER, f"{ARCHIVE_PACK}/SNAPSHOT_MANIFEST.tsv"),
            "migration": file_authority(PRODUCER, "docs/vm_tlb/codex_handoff/c16/4080_migration/C16_4080_MIGRATION_SOURCE_RECEIPT.json"),
            "platform": file_authority(PRODUCER, "docs/vm_tlb/chatgpt_handoff/c16/4080_migration/CURRENT_STATE.md"),
            "proposal": file_authority(BASE, f"{OLD_PACK}/MINIMAL_FFN_TIMELINE_CAPTURE_CONTRACT.json"),
        },
    }


def build(repo: Path, out: Path) -> None:
    evidence = validate_authority(repo)
    a = evidence["authorities"]
    model_payloads = {p["filename"]: p["sha256"] for p in evidence["model_receipt"]["payloads"]}
    rows = []

    def add(field, value, auth, status="DIRECT_ACCEPTED_AUTHORITY"):
        rows.append({"field": field, "value": compact(value), "authority_file": auth["file"], "authority_commit": auth["commit"], "authority_sha256_or_blob": f"sha256:{auth['sha256']};blob:{auth['git_blob']}", "status": status})

    add("model.id", "Qwen/Qwen2.5-7B-Instruct-AWQ", a["archive"], "DETERMINISTICALLY_DERIVED")
    add("model.path", "/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641", a["runner"])
    add("model.revision", "b25037543e9394b818fdfca67ab2a00ecc7dd641", a["archive"], "DETERMINISTICALLY_DERIVED")
    add("model.asset_receipt_sha256", "23a7e5c0107a528853d79e2e63ea6a3a9caa583bc39833bb1c04a83d0ac5b76d", a["archive"])
    add("model.payload_sha256", model_payloads, a["archive"], "DETERMINISTICALLY_DERIVED")
    add("model.config_sha256", model_payloads["config.json"], a["archive"], "DETERMINISTICALLY_DERIVED")
    add("model.quantization", {"format": "AWQ", "bits": 4, "group_size": 128, "zero_point": True}, a["archive"], "DETERMINISTICALLY_DERIVED")
    add("model.ffn_module_class", "WQLinear_GEMM", a["raw0"])
    add("input.accepted_path", "/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json", a["runner"])
    add("input.token_file_sha256", TOKEN_SHA, a["runner"])
    add("input.token_count", 2048, a["archive"], "DETERMINISTICALLY_DERIVED")
    add("input.token_ids", {"source_39": SOURCE_IDS, "derivation": "repeat source_39 then trim to 2048", "full_vector_sha256": TOKEN_SHA}, a["archive"], "DETERMINISTICALLY_DERIVED")
    add("input.raw_text", "C16 freezes this short natural-language input before any native GPU work.\nThe deployment identity, tokenizer revision, and token IDs must remain bound\nto the immutable model revision recorded by lane A.\n", a["archive"], "DETERMINISTICALLY_DERIVED")
    add("input.raw_text_sha256", TEXT_SHA, a["archive"])
    add("input.tokenizer", {"runtime_use": "NONE_FROZEN_IDS_ONLY", "derivation_revision": "a09a35458c702b33eeacc393d103063234e8bc28", "tokenizer_json_sha256": model_payloads["tokenizer.json"], "tokenizer_config_sha256": model_payloads["tokenizer_config.json"]}, a["archive"], "DETERMINISTICALLY_DERIVED")
    add("input.seed_sampling", {"seed": "NOT_APPLICABLE", "sampling": "greedy torch.argmax", "random_sampling": False}, a["runner"], "DETERMINISTICALLY_DERIVED")
    add("scenario.batch", 1, a["runner"], "DETERMINISTICALLY_DERIVED")
    add("scenario.prefill_tokens", 2048, a["runner"], "DETERMINISTICALLY_DERIVED")
    add("scenario.decode", {"count": 4, "range": "D0-D3", "fed_token_ids": TOKENS, "past_lengths_before_step": [2048, 2049, 2050, 2051], "use_cache": True}, a["runner"], "DETERMINISTICALLY_DERIVED")
    add("scenario.phases", ["PREFILL", "D0", "D1", "D2", "D3"], a["order"])
    add("scenario.GUD84", {"layers": 28, "roles": ["gate_proj", "up_proj", "down_proj"], "calls_per_phase": 84, "total_calls": 420, "decode_occurrences": 336, "fresh_process_runs": 7}, a["consumer_order"])
    add("scenario.condition", {"name": "CONTROL_GUD84", "mode": "POLICY", "hit_ratio": 1 / 84, "hit_property": "NORMAL", "miss_property": "NORMAL", "persisting": False, "requested_setaside_bytes": 33947648, "expected_actual_setaside_bytes": 37748736}, a["policy"])
    add("runtime.python", "CPython 3.10.12", a["migration"])
    add("runtime.interpreter", "/data/c16/env/c16-awq-v6/bin/python -> /data/c16/env/cpython-3.10.12/bin/python3.10", a["ncu"])
    add("runtime.torch", "2.5.1+cu124", a["migration"])
    add("runtime.transformers", "4.46.3", a["migration"])
    add("runtime.autoawq", "0.2.7.post3", a["migration"])
    add("runtime.torch_cuda_build", "12.4", a["migration"])
    add("runtime.host_cuda_toolkit", "12.8", a["platform"])
    add("runtime.ncu_session_cuda_version", "13.0", a["ncu"])
    add("runtime.driver", "580.178.04", a["platform"])
    add("runtime.gpu_observed", {"name": "NVIDIA GeForce RTX 4080", "cc": "8.9", "sm_count": 76, "memory_bytes": 16718168064}, a["ncu"])
    add("runtime.gpu_uuid", "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59", a["platform"])
    add("runtime.backends", {"model_loader": "AutoAWQForCausalLM.from_quantized", "fuse_layers": False, "ffn_linear": "WQLinear_GEMM", "attention": "Transformers-4.46.3 Qwen2 automatic backend under the frozen config; no override in runner"}, a["runner"], "DETERMINISTICALLY_DERIVED")
    add("runner.path", RUNNER, a["runner"])
    add("runner.source_sha256", EXPECTED_RUNNER_SHA, a["runner"])
    add("runner.dependencies", {COMMON: a["common"]["sha256"], PERSISTENCE: a["persistence"]["sha256"]}, a["runner"], "DETERMINISTICALLY_DERIVED")
    add("runner.accepted_command", "/data/c16/env/c16-awq-v6/bin/python util/vm_tlb/c16/e1_operator_family_natural.py --condition CONTROL_GUD84 --run-index 600", a["ncu"])
    add("runner.semantic_environment", {"explicit": {}, "note": "accepted command records no semantic environment override; model/input/condition are source-bound"}, a["ncu"])
    add("instrumentation.patch", {"path": f"{PACK}/{PATCH_NAME}", "sha256": EXPECTED_PATCH_SHA, "commit": PATCH_COMMIT, "resulting_runner_sha256": EXPECTED_PATCHED_SHA}, {"file": f"{PACK}/{PATCH_NAME}", "commit": PATCH_COMMIT, "sha256": EXPECTED_PATCH_SHA, "git_blob": git_blob(PATCH_COMMIT, f"{PACK}/{PATCH_NAME}")})

    out.mkdir(parents=True, exist_ok=True)
    source_patch = repo / PACK / PATCH_NAME
    destination_patch = out / PATCH_NAME
    if source_patch.resolve() != destination_patch.resolve():
        destination_patch.write_bytes(source_patch.read_bytes())
    with (out / "SCIENTIFIC_IDENTITY_RECOVERY.tsv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field", "value", "authority_file", "authority_commit", "authority_sha256_or_blob", "status"], delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    contract = {
        "schema_version": 1,
        "status": "AUTHORIZED",
        "decision": "IDENTITY_RECOVERED_FROM_ACCEPTED_AUTHORITY",
        "scientific_identity_change": "NONE",
        "purpose": "TIMELINE_AUTHORITY_ONLY",
        "proposal_chain": {"proposal": a["proposal"], "identity_recovery": "this pack", "project_review": "PROJECT_REVIEW.json", "authorized_capture": "this contract"},
        "historical_authority": {"producer": PRODUCER, "independent_consumer": CONSUMER, "accepted_runner": a["runner"], "accepted_call_order": a["order"], "independent_call_order": a["consumer_order"]},
        "model": {"id": "Qwen/Qwen2.5-7B-Instruct-AWQ", "path": "/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641", "revision": "b25037543e9394b818fdfca67ab2a00ecc7dd641", "asset_receipt_sha256": "23a7e5c0107a528853d79e2e63ea6a3a9caa583bc39833bb1c04a83d0ac5b76d", "payload_sha256": model_payloads, "quantization": {"format": "AWQ", "bits": 4, "group_size": 128, "zero_point": True, "fuse_layers": False, "linear_backend": "WQLinear_GEMM"}},
        "input": {"accepted_path": "/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json", "token_count": 2048, "token_file_sha256": TOKEN_SHA, "source_token_ids": SOURCE_IDS, "derivation": "repeat source token IDs then trim exactly to 2048", "raw_text_sha256": TEXT_SHA, "runtime_tokenizer_execution": False, "tokenizer_json_sha256": model_payloads["tokenizer.json"], "tokenizer_config_sha256": model_payloads["tokenizer_config.json"]},
        "natural_scenario": {"batch": 1, "prefill_tokens": 2048, "decode_range": "D0-D3", "decode_steps": 4, "generated_or_fed_token_ids_D0_D3": TOKENS, "past_lengths_before_step": [2048, 2049, 2050, 2051], "greedy_argmax": True, "seed": "NOT_APPLICABLE_NO_SAMPLING", "use_cache": True, "fresh_process": True, "condition": "CONTROL_GUD84", "policy_semantics": {"selected_modules": 84, "hit_ratio": 1 / 84, "NORMAL_NORMAL": True, "persisting": False, "no_reset_between_transitions": True}},
        "runtime": {"python": "3.10.12", "interpreter": "/data/c16/env/c16-awq-v6/bin/python", "torch": "2.5.1+cu124", "transformers": "4.46.3", "autoawq": "0.2.7.post3", "torch_cuda": "12.4", "driver": "580.178.04", "gpu": {"name": "NVIDIA GeForce RTX 4080", "uuid": "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59", "cc": "8.9", "sm_count": 76, "memory_bytes": 16718168064}, "attention_backend": "frozen Transformers-4.46.3 Qwen2 automatic selection; no runner override", "ffn_backend": "AutoAWQ WQLinear_GEMM FP16 activation"},
        "runner": {"source_path": RUNNER, "source_commit": PRODUCER, "source_sha256": EXPECTED_RUNNER_SHA, "source_git_blob": a["runner"]["git_blob"], "instrumentation_patch_path": f"{PACK}/{PATCH_NAME}", "instrumentation_patch_commit": PATCH_COMMIT, "instrumentation_patch_sha256": EXPECTED_PATCH_SHA, "patched_runner_sha256": EXPECTED_PATCHED_SHA, "base_command": "/data/c16/env/c16-awq-v6/bin/python util/vm_tlb/c16/e1_operator_family_natural.py --condition CONTROL_GUD84 --run-index {RUN_INDEX} --output {OUTPUT_JSON} --timeline-nvtx {off|on}"},
        "semantic_target": {"description": "28-layer FFN gate/up/activation/multiply/down timeline for D0-D3", "layers": list(range(28)), "projection_roles": ["gate_proj", "up_proj", "down_proj"], "added_ranges": ["one D0-D3 decode wall", "per-layer/per-step activation", "per-layer/per-step multiply"], "existing_ranges_reused": "accepted per-layer/per-step gate/up/down ranges", "expected_projection_occurrences": 336, "expected_activation_ranges": 112, "expected_multiply_ranges": 112},
        "instrumentation_delta": {"permitted": ["semantic NVTX ranges", "timeline mode flag", "result receipt field", "temporary observational Python MLP forward wrapper preserving expression order"], "kernel_changes": False, "quantization_changes": False, "input_changes": False, "model_or_runtime_backend_changes": False, "natural_decode_semantics_changes": False, "persistence_oracle_or_cache_policy_added": False},
        "tools": {"NSYS": "lightweight --trace=cuda,nvtx only", "NCU": False, "NVBit": False, "SASS": False, "oracle": False, "Accel_Sim": False},
        "gpu_lock": {"required": True, "path": "/data/c16/locks/c16_gpu_campaign.lock", "scope": "one outer lock covering canary and formal capture", "release_receipt_required": True},
        "measurement_protocol": {"preflight": ["verify every bound source/model/input/runtime hash", "record absolute nsys path/version/SHA and GPU UUID", "require clean exclusive GPU state under lock"], "neutrality_canary": {"runs": 2, "fresh_processes": True, "order": ["OFF", "ON"], "same_nsys_cuda_nvtx_capture": True, "required_equal": ["generated token IDs", "420-entry natural call order", "336 occurrence input/output hashes and shapes", "module classes", "CUDA kernel name/count/order", "CONTROL_GUD84 policy semantics"], "timing_not_used_as_scientific_result": True}, "formal": {"runs": 1, "mode": "ON", "fresh_process": True, "nsys_flags": "profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true", "capture_count": 1}, "total_gpu_process_launches_max": 3, "wall_budget_minutes": 20},
        "stop_conditions": ["any model/input/runtime/source hash mismatch", "GPU UUID or backend differs", "OFF/ON output, call-order, occurrence-hash, policy, or kernel-sequence mismatch", "missing decode wall or any required semantic range", "new CUDA kernel introduced by instrumentation", "GPU lock cannot be legally acquired within 45 minutes", "capture exceeds 20-minute GPU budget", "any request to add NCU/NVBit/SASS/oracle/Accel-Sim or new timing sweep"],
        "publication": {"node109_raw_root": "/data/c16/ffn_timeline_capture_v1/raw", "node164_root": "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_ffn_timeline_capture_v1", "required": ["raw .nsys-rep", "sqlite export", "runner/patch/source hashes", "OFF/ON and formal JSON", "command/environment/GPU/lock receipts", "SHA256 manifest", "copy-back byte/SHA verification"], "git_policy": "publish manifests/tables/reports only; do not commit bulk .nsys-rep/sqlite"},
    }
    contract_bytes = (json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    (out / "AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json").write_bytes(contract_bytes)
    contract_sha = sha(contract_bytes)

    project = {"schema_version": 1, "status": "AUTHORIZED", "decision": "IDENTITY_RECOVERED_FROM_ACCEPTED_AUTHORITY", "project_review": "PASS", "required_identity_fields": len(rows), "unknown_required_fields": 0, "direct_fields": sum(r["status"] == "DIRECT_ACCEPTED_AUTHORITY" for r in rows), "deterministically_derived_fields": sum(r["status"] == "DETERMINISTICALLY_DERIVED" for r in rows), "gpu_authorized_for": "Lane7 bounded NSYS cuda,nvtx timeline capture only", "gpu_used_in_this_review": False, "lane4_partial_accessed": False, "old_proposal_modified": False, "old_proposal_sha256": a["proposal"]["sha256"], "authorized_contract_sha256": contract_sha, "instrumentation_patch_sha256": EXPECTED_PATCH_SHA, "risk_controls": ["exact accepted identity", "one OFF/ON neutrality pair", "one formal capture", "single GPU lock", "hard stop on semantic or kernel drift"]}
    (out / "PROJECT_REVIEW.json").write_text(json.dumps(project, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    report = f"""# FFN timeline scientific identity recovery

## Decision

`IDENTITY_RECOVERED_FROM_ACCEPTED_AUTHORITY`. The accepted operator-family producer, its independent consumer, the source-bound model/input constants, the immutable historical snapshot, and the recorded NCU session jointly select one execution identity. No old GUD84 rerun was used or requested.

## Recovered identity

The workload is `Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543e9394b818fdfca67ab2a00ecc7dd641` at the exact `/data/c16/models/.incoming/...` path in the accepted runner. It consumes the frozen 2048-token S2 text vector (`{TOKEN_SHA}`), without runtime tokenization, in batch 1. One prefill builds a 2048-token cache; greedy D0-D3 feed `{TOKENS}` with past lengths 2048-2051. The accepted `CONTROL_GUD84` condition executes 28 layers × gate/up/down in the natural order: 84 calls per phase, 420 including prefill, and 336 measured decode projection occurrences. Seven fresh producer processes and the independent consumer agree on order, tokens, input/output hashes, and shapes.

The runtime is the accepted CPython 3.10.12 / torch 2.5.1+cu124 / Transformers 4.46.3 / AutoAWQ 0.2.7.post3 environment on the RTX 4080 (CC 8.9, 76 SM). The accepted NCU session directly records the interpreter, command, host, GPU, and `CONTROL_GUD84`; the platform authority supplies the UUID and driver. The FFN backend is `WQLinear_GEMM`, `fuse_layers=False`, with FP16 activations.

## Provenance and inference boundary

`SCIENTIFIC_IDENTITY_RECOVERY.tsv` separates direct fields from deterministic recovery. Derived entries are limited to consequences fixed by source plus hash-closed artifacts: the 2048 vector reconstructed from the archived 39-token source rule, context lengths, quantization fields, combined platform identity, and payload values recovered through an accepted immutable-manifest SHA. There are no `UNKNOWN` required fields. In particular, a name like “Qwen AWQ” was never used to guess a missing value.

The attention backend is bound operationally as the automatic Qwen2 selection of the exact frozen Transformers/config tuple; the runner has no attention override. Lane7 must not replace it with an explicit alternate backend. Environment variables not present in the accepted command are not invented; Lane7 must record its environment and stop if it introduces a semantic override.

## Authorization scope

The old proposal remains byte-identical at SHA256 `{a['proposal']['sha256']}` and remains `PROPOSED_NOT_AUTHORIZED`. The new contract SHA256 is `{contract_sha}`. It authorizes only one OFF/ON neutrality pair and one lightweight formal NSYS `cuda,nvtx` capture under the established GPU lock. It does not authorize NCU, NVBit, SASS, oracle work, Accel-Sim, a timing campaign, or any model/input/backend/policy change.

The observational delta is frozen at commit `{PATCH_COMMIT}`, patch SHA256 `{EXPECTED_PATCH_SHA}`, and resulting runner SHA256 `{EXPECTED_PATCHED_SHA}`. It preserves the original gate→activation→up→multiply→down expression order, adds only semantic NVTX/correlation ranges, and is admissible only if the OFF/ON canary preserves output tokens, all occurrence hashes/shapes, natural call order, policy semantics, and CUDA kernel sequence.
"""
    (out / "IDENTITY_RECOVERY_REPORT.md").write_text(report, encoding="utf-8")

    continuation = f"""# Lane7 FFN timeline capture continuation

Read `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json` and require SHA256 `{contract_sha}`.

Create the Lane7 branch/worktree from accepted producer `{PRODUCER}`. Fetch authorization branch `hrl/c16-ffn-timeline-identity-recovery-174new-v1`, copy/apply `{PACK}/{PATCH_NAME}` (SHA256 `{EXPECTED_PATCH_SHA}`), and require patched runner SHA256 `{EXPECTED_PATCHED_SHA}`. Do not reinterpret or reconstruct the scientific identity.

Under one legal `/data/c16/locks/c16_gpu_campaign.lock`, execute exactly the contract's OFF/ON neutrality canary, then the single lightweight NSYS `cuda,nvtx` formal capture only if neutrality passes. Publish raw evidence and SHA receipts to the frozen 164 destination, release the lock, commit/push/fetch-back/clean, and stop. Any contract stop condition means no formal capture or follow-up experiment.
"""
    (out / "LANE7_FFN_TIMELINE_CAPTURE_CONTINUATION.md").write_text(continuation, encoding="utf-8")

    readme = "# C16 FFN timeline identity recovery and authorization\n\nCPU-only recovery from accepted authority. Decision: `IDENTITY_RECOVERED_FROM_ACCEPTED_AUTHORITY`; bounded Lane7 NSYS timeline capture is authorized by the new contract. The historical proposal is unchanged.\n"
    (out / "README.md").write_text(readme, encoding="utf-8")

    names = ["AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json", "IDENTITY_RECOVERY_REPORT.md", PATCH_NAME, "LANE7_FFN_TIMELINE_CAPTURE_CONTINUATION.md", "PROJECT_REVIEW.json", "README.md", "SCIENTIFIC_IDENTITY_RECOVERY.tsv"]
    sums = "".join(f"{sha((out / name).read_bytes())}  {name}\n" for name in sorted(names))
    (out / "SHA256SUMS").write_text(sums, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    out = args.output_dir or repo / PACK
    build(repo, out)


if __name__ == "__main__":
    main()
