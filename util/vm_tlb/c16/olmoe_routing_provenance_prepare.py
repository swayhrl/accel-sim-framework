#!/usr/bin/env python3
"""CPU-only authority verification and input freeze for C16 OLMoE routing V1."""
from __future__ import annotations

import datetime
import hashlib
import json
import platform
import secrets
import subprocess
import sys
from pathlib import Path

from transformers import AutoTokenizer, __version__ as transformers_version

REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-routing-provenance-multiround-109-v1")
ROOT = Path("/data/c16/olmoe_routing_provenance_multiround_v1")
MODEL = Path("/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e")
MODEL_ID = "allenai/OLMoE-1B-7B-0125-Instruct"
MODEL_REV = "b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e"
V34 = "ab26365dc663268b0799818db6687ed466e8c925"
ASSET = "ca683527323e26e3415a805c797c53c5edea322c"
PROSE = "a306e1271c3e70c2ee322a3582979b6abd777a72"
V34_PACK = "docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34"
TEXT_SHA = "52761ce278c0e4819f153036e2b93e2b921d7963dda6a1d67a8192503612fa9c"
V34_FROZEN_FILE_SHA = "bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=REPO)


def atomic_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("xb") as f:
        f.write(data)
        f.flush()
    tmp.replace(path)


def atomic_json(path: Path, value) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def compact_ids(ids: list[int]) -> bytes:
    return (json.dumps(ids, separators=(",", ":")) + "\n").encode()


def main() -> None:
    if ROOT.exists():
        raise SystemExit(f"refusing existing root: {ROOT}")
    run_id = "C16R_olmoe-routing-provenance-multiround-v1_" + datetime.datetime.now(
        datetime.timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ") + "_" + secrets.token_hex(6)
    run = ROOT / "raw" / run_id
    inputs = run / "inputs"
    inputs.mkdir(parents=True)
    atomic_bytes(ROOT / "ACTIVE_RUN_ID", (run_id + "\n").encode())

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL), local_files_only=True, use_fast=True)
    v34_input = json.loads(git_bytes(V34, f"{V34_PACK}/S2_INPUT_AUTHORITY.json"))
    v34_ids = v34_input["frozen_ids"]
    if len(v34_ids) != 2048:
        raise RuntimeError("V34 frozen token count is not 2048")

    specs = [
        ("P_TEXT", ASSET, "docs/vm_tlb/assets/c16/prospective_common_input_v1/TEXT.txt", True),
        ("P_CODE", ASSET, "docs/vm_tlb/assets/c16/prospective_common_input_v1/CODE.txt", False),
        ("P_STRUCTURED", ASSET, "docs/vm_tlb/assets/c16/prospective_common_input_v1/STRUCTURED.txt", False),
        ("P_PROSE", PROSE, "docs/vm_tlb/scientific_logs/C16_MOE_EXPLORATION_LOG.md", False),
    ]
    records = []
    for prompt_id, commit, source_path, historical in specs:
        source = git_bytes(commit, source_path)
        source_sha = sha_bytes(source)
        if prompt_id == "P_TEXT" and source_sha != TEXT_SHA:
            raise RuntimeError(f"P_TEXT source authority mismatch: {source_sha}")
        text = source.decode("utf-8")
        tokenized = tokenizer(text, add_special_tokens=False, return_attention_mask=False)["input_ids"]
        if len(tokenized) < 2048:
            raise RuntimeError(f"{prompt_id} has only {len(tokenized)} tokens")
        frozen = list(map(int, tokenized[:2048]))
        if historical and frozen != v34_ids:
            first = next((i for i, (a, b) in enumerate(zip(frozen, v34_ids)) if a != b), None)
            raise RuntimeError(f"P_TEXT_RETOKENIZATION_MISMATCH first_difference={first}")
        destination = inputs / f"{prompt_id}.token_ids.json"
        atomic_bytes(destination, compact_ids(frozen))
        records.append({
            "prompt_id": prompt_id,
            "source_commit": commit,
            "source_path": source_path,
            "source_size_bytes": len(source),
            "source_sha256": source_sha,
            "pre_truncation_token_count": len(tokenized),
            "frozen_token_count": len(frozen),
            "frozen_ids_path": destination.relative_to(run).as_posix(),
            "frozen_ids_file_sha256": sha_file(destination),
            "token_ids_semantic_sha256": sha_bytes(json.dumps(frozen, separators=(",", ":")).encode()),
            "first_16_ids": frozen[:16],
            "last_16_ids": frozen[-16:],
            "add_special_tokens": False,
            "chat_template_applied": False,
            "historical_v34_ids_exact_match": frozen == v34_ids if historical else None,
            "historical_v34_frozen_file_sha256_authority": V34_FROZEN_FILE_SHA if historical else None,
        })

    tokenizer_files = []
    for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"):
        path = MODEL / name
        tokenizer_files.append({"name": name, "bytes": path.stat().st_size, "sha256": sha_file(path)})
    freeze = {
        "status": "PASS_CPU_INPUT_FREEZE",
        "run_id": run_id,
        "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "model_revision": MODEL_REV,
        "model_path": str(MODEL),
        "tokenizer_class": type(tokenizer).__name__,
        "tokenizer_is_fast": bool(tokenizer.is_fast),
        "transformers": transformers_version,
        "python": platform.python_version(),
        "add_special_tokens": False,
        "chat_template_applied": False,
        "prompt_length": 2048,
        "tokenizer_files": tokenizer_files,
        "prompts": records,
    }
    atomic_json(run / "INPUT_FREEZE_MANIFEST.json", freeze)

    v34_routing = git_bytes(V34, f"{V34_PACK}/NATURAL_TOP8_ROUTING.json")
    atomic_bytes(run / "V34_NATURAL_TOP8_ROUTING.reference.json", v34_routing)
    runtime = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"], text=True
    )
    atomic_bytes(run / "RUNTIME_PIP_FREEZE.txt", "".join(sorted(runtime.splitlines(keepends=True))).encode())
    manifest = {
        "status": "PREREGISTERED_BEFORE_GPU_EXECUTION",
        "goal": "C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1",
        "run_id": run_id,
        "gpu_lock": "/data/c16/locks/c16_gpu_campaign.lock",
        "one_outer_lock": True,
        "one_model_load": True,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REV,
        "dtype": "torch.bfloat16",
        "batch_size": 1,
        "prompt_tokens": 2048,
        "decode_cap": 64,
        "use_cache": True,
        "decoding": "greedy exact argmax",
        "sampling": False,
        "natural_eos": True,
        "sessions": [
            {"session_id": "T0_NOHOOK_A", "prompt_id": "P_TEXT", "capture": False},
            {"session_id": "T1_NOHOOK_B", "prompt_id": "P_TEXT", "capture": False},
            {"session_id": "T2_TEXT_ALLLAYER", "prompt_id": "P_TEXT", "capture": True},
            {"session_id": "C1_CODE_ALLLAYER", "prompt_id": "P_CODE", "capture": True},
            {"session_id": "S1_STRUCTURED_ALLLAYER", "prompt_id": "P_STRUCTURED", "capture": True},
            {"session_id": "P1_PROSE_ALLLAYER", "prompt_id": "P_PROSE", "capture": True},
        ],
        "routing": {"layers": "all 16 MoE layers", "experts": 64, "experts_per_token": 8, "natural_only": True},
        "analysis": {"lags": [1, 32], "shuffle_seed": 20260928, "permutations": 1000},
        "source_commits": {"v34": V34, "asset": ASSET, "prose": PROSE},
        "input_freeze_manifest_sha256": sha_file(run / "INPUT_FREEZE_MANIFEST.json"),
    }
    atomic_json(run / "CAMPAIGN_MANIFEST.pre_gpu.json", manifest)
    print(json.dumps({"status": "PASS_CPU_INPUT_FREEZE", "run_id": run_id, "run": str(run)}))


if __name__ == "__main__":
    main()
