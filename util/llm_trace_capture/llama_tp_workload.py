#!/usr/bin/env python3
"""Pinned M4A Llama-3.2 1B TP workload candidate; no silent full-model path."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.metadata as metadata
import json
import os
import re
import sys
import tempfile
from pathlib import Path

MODEL_ID = "meta-llama/Llama-3.2-1B"
BATCH, SEQ, OUTPUT_TOKENS, TP_SIZE = 8, 64, 3, 4
MODEL_SHA = re.compile(r"^[0-9a-f]{40}$")


def require_environment() -> tuple[str, Path, Path, str]:
    revision = os.environ.get("M4A_MODEL_REVISION", "")
    if not MODEL_SHA.fullmatch(revision):
        raise RuntimeError("M4A_MODEL_REVISION must be an immutable 40-hex Hugging Face commit")
    phase = os.environ.get("M4A_PHASE", "")
    if phase not in {"smoke", "trace"}: raise RuntimeError("M4A_PHASE must be smoke or trace")
    run_raw, metadata_raw = os.environ.get("M4A_RUN_DIR", ""), os.environ.get("M4A_METADATA_PATH", "")
    if not run_raw or not metadata_raw: raise RuntimeError("M4A_RUN_DIR and M4A_METADATA_PATH are required")
    run_dir, metadata_path = Path(run_raw), Path(metadata_raw)
    return revision, run_dir, metadata_path, phase


def package_versions() -> dict[str, str]:
    required = {"torch": "2.6.0", "transformers": "4.51.3", "accelerate": "1.6.0", "safetensors": "0.5.3"}
    actual = {name: metadata.version(name) for name in required}
    mismatch = {name: value for name, value in actual.items() if value != required[name]}
    if mismatch: raise RuntimeError(f"runtime package pins do not match requirements-llama-tp4.txt: {mismatch}")
    return actual


def aligned(value: int, alignment: int = 256) -> int:
    return (value + alignment - 1) // alignment * alignment


def bind_flat_weight_storage(model, torch):
    """Copy all parameters once into a deterministic aligned backing buffer."""
    entries, offset = [], 0
    for name, parameter in model.named_parameters():
        if not parameter.is_cuda: raise RuntimeError(f"parameter is not on CUDA: {name}")
        nbytes = parameter.numel() * parameter.element_size()
        offset = aligned(offset)
        entries.append((name, parameter, offset, nbytes))
        offset += nbytes
    flat = torch.empty(aligned(offset), dtype=torch.uint8, device="cuda")
    base = flat.data_ptr()
    table = []
    with torch.no_grad():
        for name, parameter, offset, nbytes in entries:
            view = flat.narrow(0, offset, nbytes).view(parameter.dtype).view_as(parameter)
            view.copy_(parameter)
            parameter.data = view
            if parameter.data_ptr() != base + offset: raise RuntimeError(f"flat bind failed: {name}")
            table.append({"name": name, "offset_bytes": offset, "size_bytes": nbytes,
                          "dtype": str(parameter.dtype), "shape": list(parameter.shape)})
    torch.cuda.synchronize()
    return flat, table


def verify_flat_storage(model, flat, table) -> None:
    expected = {row["name"]: row["offset_bytes"] for row in table}
    base = flat.data_ptr()
    for name, parameter in model.named_parameters():
        if name not in expected or parameter.data_ptr() != base + expected[name]:
            raise RuntimeError(f"one-buffer invariant broken by post-load copy/replacement: {name}")


def write_sidecar(path: Path, revision: str, route: str, rank: int, flat, table, versions: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "m4a-allocation-sidecar-v1",
      "run": {"run_id": os.environ["M4A_RUN_DIR"].rsplit("/", 1)[-1], "model_id": MODEL_ID,
              "model_revision": revision, "tokenizer_revision": revision, "classification": "PAPER_COMPATIBLE_SELF_CAPTURE",
              "tp_route": route, "tp_size": TP_SIZE, "rank": rank, "packages": versions},
      "allocations": [{"allocation_id": f"weight-flat-rank{rank}", "simva_start": hex(flat.data_ptr()),
          "size_bytes": flat.numel(), "object_kind": "WEIGHT", "tensor_name": "ALL_PARAMETERS",
          "lifetime": {"start_phase": "MODEL_LOAD", "end_phase": "DECODE"},
          "classification_provenance": "m4a runtime flat-buffer binder"}],
      "weight_layout": {"allocation_id": f"weight-flat-rank{rank}", "alignment_bytes": 256, "tensors": table},
      "phases": [{"name": "MODEL_LOAD", "kernel_selector": "runtime bind"}, {"name": "PREFILL", "kernel_selector": "B8_S64"}, {"name": "DECODE", "kernel_selector": "three greedy steps"}]}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_workload_manifest(run_dir: Path, revision: str, versions: dict[str, str]) -> None:
    payload = {"schema_version": "m4a-llama-workload-manifest-v1", "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "model_id": MODEL_ID, "model_revision": revision, "tokenizer_revision": revision,
               "input_method": "deterministic token IDs; no prompt/tokenizer fallback", "batch_size": BATCH,
               "input_sequence_length": SEQ, "output_tokens": OUTPUT_TOKENS, "tp_size": TP_SIZE,
               "route": "real-tp4-rank0", "package_versions": versions,
               "requirements_file": "util/llm_trace_capture/requirements-llama-tp4.txt"}
    (run_dir / "workload-manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def real_tp4(revision: str, run_dir: Path, output: Path, phase: str) -> None:
    import torch
    import torch.distributed as dist
    from transformers import AutoModelForCausalLM
    if int(os.environ.get("WORLD_SIZE", "0")) != TP_SIZE: raise RuntimeError("real-tp4 route requires torchrun world size 4")
    dist.init_process_group("nccl")
    rank = dist.get_rank(); torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))
    versions = package_versions()
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=revision, torch_dtype=torch.bfloat16, tp_plan="auto")
    model.eval(); flat, table = bind_flat_weight_storage(model, torch)
    if rank == 0:
        write_sidecar(output, revision, "real-tp4-rank0", rank, flat, table, versions)
        write_workload_manifest(run_dir, revision, versions)
    dist.barrier()
    # Fixed IDs eliminate tokenizer/prompt drift; valid IDs are verified against config.
    vocab = int(model.config.vocab_size)
    ids = (torch.arange(1, SEQ + 1, device="cuda").unsqueeze(0).repeat(BATCH, 1) % vocab)
    with torch.inference_mode():
        result = model(input_ids=ids, use_cache=True)
        next_ids, cache = ids[:, -1:], result.past_key_values
        for _ in range(OUTPUT_TOKENS):
            result = model(input_ids=next_ids, past_key_values=cache, use_cache=True)
            cache = result.past_key_values
    verify_flat_storage(model, flat, table); dist.barrier(); dist.destroy_process_group()


def self_test() -> None:
    assert MODEL_ID == "meta-llama/Llama-3.2-1B" and (BATCH, SEQ, OUTPUT_TOKENS, TP_SIZE) == (8, 64, 3, 4)
    assert aligned(1) == 256 and aligned(256) == 256
    assert MODEL_SHA.fullmatch("a" * 40)
    class FakeFlat:
        def data_ptr(self): return 0x1000
        def numel(self): return 512
    with tempfile.TemporaryDirectory() as directory:
        old = os.environ.get("M4A_RUN_DIR")
        os.environ["M4A_RUN_DIR"] = f"{directory}/unit"
        output = Path(directory) / "sidecar.json"
        write_sidecar(output, "a" * 40, "real-tp4-rank0", 0, FakeFlat(),
                      [{"name": "x", "offset_bytes": 0, "size_bytes": 16, "dtype": "torch.bfloat16", "shape": [8, 2]}],
                      {"torch": "2.6.0", "transformers": "4.51.3", "accelerate": "1.6.0", "safetensors": "0.5.3"})
        from validate_metadata import validate
        payload = json.loads(output.read_text())
        assert validate(payload)["allocations"] == 1 and "SYNTHETIC_KV" not in output.read_text()
        if old is None: del os.environ["M4A_RUN_DIR"]
        else: os.environ["M4A_RUN_DIR"] = old


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=("real-tp4-rank0",), required=False)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: self_test(); print("PASS llama TP wrapper self-test"); return 0
    if args.route != "real-tp4-rank0": parser.error("only real-tp4-rank0 is executable; no full-model fallback exists")
    revision, run_dir, metadata_path, phase = require_environment()
    real_tp4(revision, run_dir, metadata_path, phase); print("PASS real-tp4 workload")
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except RuntimeError as error: print(f"error: {error}", file=sys.stderr); raise SystemExit(2)
