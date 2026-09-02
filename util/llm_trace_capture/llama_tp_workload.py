#!/usr/bin/env python3
"""Pinned Route-E Llama TP=4 workload; formal ROI is profiler controlled."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata as metadata
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

MODEL_ID = "meta-llama/Llama-3.2-1B"
BATCH, SEQ, OUTPUT_TOKENS, TP_SIZE = 8, 64, 3, 4
MODEL_SHA = re.compile(r"^[0-9a-f]{40}$")
REGIONS = {"prefill", "decode1", "decode_reuse"}
PACKAGE_PINS = {"torch": "2.6.0", "transformers": "4.51.3", "accelerate": "1.6.0",
                "safetensors": "0.5.3", "huggingface_hub": "0.30.2"}
LOCAL_SNAPSHOT_FILES = ("model.safetensors", "config.json", "generation_config.json", "tokenizer.json",
                        "tokenizer_config.json", "special_tokens_map.json")


def require_model_source(revision: str) -> dict:
    """Resolve transport without allowing a configured local snapshot to hit HF."""
    local_raw = os.environ.get("M4A_MODEL_LOCAL_PATH", "")
    if not local_raw:
        return {"transport": "HUGGING_FACE", "load_target": MODEL_ID,
                "provenance": {"canonical_model_id": MODEL_ID, "frozen_revision": revision}}
    root = Path(local_raw).expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError(f"M4A_MODEL_LOCAL_PATH is not a directory: {root}")
    missing = [name for name in LOCAL_SNAPSHOT_FILES if not (root / name).is_file()]
    if missing:
        raise RuntimeError(f"local model snapshot is incomplete: missing {missing}")
    manifest_raw = os.environ.get("M4A_MODEL_LOCAL_MANIFEST", "")
    if not manifest_raw:
        raise RuntimeError("M4A_MODEL_LOCAL_MANIFEST is required with M4A_MODEL_LOCAL_PATH")
    manifest_path = Path(manifest_raw).expanduser().resolve()
    if not manifest_path.is_file():
        raise RuntimeError(f"M4A_MODEL_LOCAL_MANIFEST is not a file: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text())
        identity = manifest["model"]
        rows = {row["path"]: row for row in manifest["files"]}
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise RuntimeError(f"invalid local model manifest: {manifest_path}: {error}") from error
    if manifest.get("schema_version") != "m4a-local-model-snapshot-v1":
        raise RuntimeError("local model manifest schema is not m4a-local-model-snapshot-v1")
    if identity.get("canonical_id") != MODEL_ID or identity.get("revision") != revision:
        raise RuntimeError("local model manifest identity does not match frozen model/revision")
    for name in LOCAL_SNAPSHOT_FILES:
        row = rows.get(name)
        if not isinstance(row, dict) or not isinstance(row.get("sha256"), str):
            raise RuntimeError(f"local model manifest omits SHA256 for {name}")
        if int(row.get("size_bytes", -1)) != (root / name).stat().st_size:
            raise RuntimeError(f"local model file size differs from manifest: {name}")
    return {"transport": "LOCAL_SNAPSHOT", "load_target": str(root),
            "provenance": {"canonical_model_id": MODEL_ID, "frozen_revision": revision,
                           "local_path": str(root), "manifest_path": str(manifest_path),
                           "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                           "manifest_schema": manifest["schema_version"]}}


def model_load_kwargs(source: dict, revision: str) -> dict:
    """Keep the local transport explicit, including Transformers' offline guard."""
    kwargs = {"pretrained_model_name_or_path": source["load_target"], "revision": revision}
    if source["transport"] == "LOCAL_SNAPSHOT":
        kwargs["local_files_only"] = True
    return kwargs


def require_environment() -> tuple[str, Path, Path, str, str, dict]:
    revision = os.environ.get("M4A_MODEL_REVISION", "")
    if not MODEL_SHA.fullmatch(revision):
        raise RuntimeError("M4A_MODEL_REVISION must be an immutable 40-hex Hugging Face commit")
    phase = os.environ.get("M4A_PHASE", "")
    if phase not in {"smoke", "trace"}: raise RuntimeError("M4A_PHASE must be smoke or trace")
    region = os.environ.get("M4A_TRACE_REGION", "")
    if region not in REGIONS: raise RuntimeError("M4A_TRACE_REGION must be prefill, decode1, or decode_reuse")
    run_raw, metadata_raw = os.environ.get("M4A_RUN_DIR", ""), os.environ.get("M4A_METADATA_PATH", "")
    if not run_raw or not metadata_raw: raise RuntimeError("M4A_RUN_DIR and M4A_METADATA_PATH are required")
    return revision, Path(run_raw), Path(metadata_raw), phase, region, require_model_source(revision)


def package_versions() -> dict[str, str]:
    actual = {name: metadata.version(name) for name in PACKAGE_PINS}
    mismatch = {name: value for name, value in actual.items()
                if value != PACKAGE_PINS[name] and not (name == "torch" and value == f"{PACKAGE_PINS[name]}+cu126")}
    if mismatch: raise RuntimeError(f"runtime package pins do not match requirements-llama-tp4.txt: {mismatch}")
    return actual


def aligned(value: int, alignment: int = 256) -> int:
    return (value + alignment - 1) // alignment * alignment


def bind_flat_weight_storage(model, torch):
    """Copy all rank-local parameters once into a deterministic aligned buffer."""
    entries, offset = [], 0
    for name, parameter in model.named_parameters():
        if not parameter.is_cuda: raise RuntimeError(f"parameter is not on CUDA: {name}")
        nbytes = parameter.numel() * parameter.element_size(); offset = aligned(offset)
        entries.append((name, parameter, offset, nbytes)); offset += nbytes
    flat = torch.empty(aligned(offset), dtype=torch.uint8, device="cuda"); base = flat.data_ptr(); table = []
    with torch.no_grad():
        for name, parameter, offset, nbytes in entries:
            view = flat.narrow(0, offset, nbytes).view(parameter.dtype).view_as(parameter)
            view.copy_(parameter); parameter.data = view
            if parameter.data_ptr() != base + offset: raise RuntimeError(f"flat bind failed: {name}")
            table.append({"name": name, "offset_bytes": offset, "size_bytes": nbytes,
                          "dtype": str(parameter.dtype), "shape": list(parameter.shape)})
    torch.cuda.synchronize(); return flat, table


def verify_flat_storage(model, flat, table) -> None:
    expected, base = {row["name"]: row["offset_bytes"] for row in table}, flat.data_ptr()
    for name, parameter in model.named_parameters():
        if name not in expected or parameter.data_ptr() != base + expected[name]:
            raise RuntimeError(f"one-buffer invariant broken by post-load copy/replacement: {name}")


def cache_layers(cache):
    """Return observable legacy (layer, (key, value)) pairs, or no records."""
    if cache is None: return []
    if hasattr(cache, "to_legacy_cache"): cache = cache.to_legacy_cache()
    try: return list(enumerate(cache))
    except TypeError: return []


def observe_kv_cache(cache, previous: dict, region: str, phase_name: str, step: int) -> tuple[list[dict], dict]:
    """Record genuine runtime cache tensors; absent/opaque cache stays unrecorded."""
    events, current = [], {}
    for layer, pair in cache_layers(cache):
        if not isinstance(pair, (tuple, list)) or len(pair) < 2: continue
        for component, tensor in zip(("K", "V"), pair[:2]):
            if not all(hasattr(tensor, field) for field in ("data_ptr", "numel", "element_size")): continue
            pointer, size = int(tensor.data_ptr()), int(tensor.numel()) * int(tensor.element_size())
            if pointer <= 0 or size <= 0: continue
            key = (layer, component); old = previous.get(key)
            if old is None: state = "CREATED"
            elif old["simva_start"] == hex(pointer) and old["size_bytes"] == size: state = "REUSED"
            elif old["simva_start"] == hex(pointer) and size > old["size_bytes"]: state = "GROWN"
            else: state = "REPLACED"
            record = {"allocation_id": f"kv-rank0-layer{layer}-{component.lower()}-{phase_name.lower()}-{step}",
                      "object_kind": "KV_CACHE", "simva_start": hex(pointer), "size_bytes": size,
                      "layer": layer, "component": component, "trace_region": region,
                      "phase": phase_name, "step": step, "state": state,
                      "lifetime": {"start_phase": phase_name, "end_phase": "UNKNOWN_ACTIVE"},
                      "classification_provenance": "runtime past_key_values observation"}
            events.append(record); current[key] = {"simva_start": hex(pointer), "size_bytes": size}
    return events, current


def write_sidecar(path: Path, revision: str, route: str, rank: int, flat, table, versions: dict[str, str], kv_events: list[dict], model_source: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "m4a-allocation-sidecar-v1",
      "run": {"run_id": os.environ["M4A_RUN_DIR"].rsplit("/", 1)[-1], "model_id": MODEL_ID,
              "model_revision": revision, "tokenizer_revision": revision,
              "classification": "PAPER_COMPATIBLE_SELF_CAPTURE", "tp_route": route, "tp_size": TP_SIZE,
              "rank": rank, "packages": versions, "self_capture_dtype": "bfloat16",
              "self_capture_dtype_provenance": "CAPTURE_ENV_LOCK.md explicit self-capture choice",
              "model_transport": model_source["transport"], "model_source": model_source["provenance"]},
      "allocations": [{"allocation_id": f"weight-flat-rank{rank}", "simva_start": hex(flat.data_ptr()),
          "size_bytes": flat.numel(), "object_kind": "WEIGHT", "tensor_name": "ALL_PARAMETERS",
          "lifetime": {"start_phase": "MODEL_LOAD", "end_phase": "DECODE"},
          "classification_provenance": "m4a runtime flat-buffer binder"}],
      "kv_cache_events": kv_events,
      "weight_layout": {"allocation_id": f"weight-flat-rank{rank}", "alignment_bytes": 256, "tensors": table},
      "phases": [{"name": "MODEL_LOAD", "kernel_selector": "runtime bind; tracer inactive"},
                 {"name": "PREFILL", "kernel_selector": "B8_S64"},
                 {"name": "DECODE", "kernel_selector": "three greedy steps"}]}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_workload_manifest(run_dir: Path, revision: str, versions: dict[str, str], region: str, phase: str, model_source: dict) -> None:
    payload = {"schema_version": "m4a-llama-workload-manifest-v2", "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "model_id": MODEL_ID, "model_revision": revision, "tokenizer_revision": revision,
               "input_method": "deterministic token IDs; no prompt/tokenizer fallback", "batch_size": BATCH,
               "input_sequence_length": SEQ, "output_tokens": OUTPUT_TOKENS, "tp_size": TP_SIZE,
               "route": "real-tp4-rank0", "trace_region": region, "phase": phase,
               "roi_control": "ACTIVE_FROM_START=0 plus cuProfilerStart/cuProfilerStop for trace phase only",
               "package_versions": versions, "requirements_file": "util/llm_trace_capture/requirements-llama-tp4.txt",
               "model_transport": model_source["transport"], "model_source": model_source["provenance"]}
    (run_dir / "workload-manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


@contextmanager
def profiler_region(torch, phase: str, region: str):
    """Trace only the chosen inference call; smoke intentionally has no profiler APIs."""
    if phase != "trace": yield; return
    if os.environ.get("ACTIVE_FROM_START") != "0":
        raise RuntimeError("formal trace requires ACTIVE_FROM_START=0")
    try: runtime = torch.cuda.cudart()
    except Exception as error: raise RuntimeError(f"cannot obtain CUDA runtime for ROI {region}: {error}")
    start = runtime.cudaProfilerStart()
    if int(start) != 0: raise RuntimeError(f"cudaProfilerStart failed for {region}: {start}")
    try: yield
    finally:
        stop = runtime.cudaProfilerStop()
        if int(stop) != 0: raise RuntimeError(f"cudaProfilerStop failed for {region}: {stop}")


def real_tp4(revision: str, run_dir: Path, output: Path, phase: str, region: str, model_source: dict) -> None:
    import torch
    import torch.distributed as dist
    from transformers import AutoModelForCausalLM
    if int(os.environ.get("WORLD_SIZE", "0")) != TP_SIZE: raise RuntimeError("real-tp4 route requires torchrun world size 4")
    dist.init_process_group("nccl"); rank = dist.get_rank(); torch.cuda.set_device(int(os.environ["LOCAL_RANK"])); versions = package_versions()
    # The frozen tracer is inactive until profiler_region. Do not move setup inside it.
    model = AutoModelForCausalLM.from_pretrained(**model_load_kwargs(model_source, revision), torch_dtype=torch.bfloat16, tp_plan="auto")
    model.eval(); flat, table = bind_flat_weight_storage(model, torch)
    vocab = int(model.config.vocab_size); ids = (torch.arange(1, SEQ + 1, device="cuda").unsqueeze(0).repeat(BATCH, 1) % vocab)
    with torch.inference_mode():
        model(input_ids=ids, use_cache=True)  # warmup while tracer remains inactive
        kv_events, prior = [], {}
        if region == "prefill":
            with profiler_region(torch, phase, region): result = model(input_ids=ids, use_cache=True)
            observed, prior = observe_kv_cache(result.past_key_values, prior, region, "PREFILL", 0); kv_events += observed
            next_ids, cache = ids[:, -1:], result.past_key_values
        else:
            result = model(input_ids=ids, use_cache=True)
            observed, prior = observe_kv_cache(result.past_key_values, prior, region, "PREFILL", 0); kv_events += observed
            next_ids, cache = ids[:, -1:], result.past_key_values
        profiled = 0
        for step in range(1, OUTPUT_TOKENS + 1):
            selected = (region == "decode1" and step == 1) or (region == "decode_reuse" and step == 2)
            if selected:
                with profiler_region(torch, phase, region): result = model(input_ids=next_ids, past_key_values=cache, use_cache=True)
            else: result = model(input_ids=next_ids, past_key_values=cache, use_cache=True)
            cache = result.past_key_values
            observed, prior = observe_kv_cache(cache, prior, region, "DECODE", step); kv_events += observed
            next_ids = result.logits[:, -1:].argmax(dim=-1); profiled += int(selected)
        if region != "prefill" and profiled != 1: raise RuntimeError("requested decode ROI was not executed exactly once")
    verify_flat_storage(model, flat, table)
    if rank == 0:
        write_sidecar(output, revision, "real-tp4-rank0", rank, flat, table, versions, kv_events, model_source)
        write_workload_manifest(run_dir, revision, versions, region, phase, model_source)
    dist.barrier(); dist.destroy_process_group()


def self_test() -> None:
    assert MODEL_ID == "meta-llama/Llama-3.2-1B" and (BATCH, SEQ, OUTPUT_TOKENS, TP_SIZE) == (8, 64, 3, 4)
    assert aligned(1) == 256 and MODEL_SHA.fullmatch("a" * 40) and REGIONS == {"prefill", "decode1", "decode_reuse"}
    class FakeTensor:
        def __init__(self, ptr, n, width): self.ptr, self.n, self.width = ptr, n, width
        def data_ptr(self): return self.ptr
        def numel(self): return self.n
        def element_size(self): return self.width
    events1, prior = observe_kv_cache([(FakeTensor(0x2000, 8, 2), FakeTensor(0x3000, 8, 2))], {}, "prefill", "PREFILL", 0)
    events2, _ = observe_kv_cache([(FakeTensor(0x2000, 16, 2), FakeTensor(0x4000, 16, 2))], prior, "decode1", "DECODE", 1)
    assert [x["state"] for x in events1] == ["CREATED", "CREATED"] and [x["state"] for x in events2] == ["GROWN", "REPLACED"]
    class FakeFlat:
        def data_ptr(self): return 0x1000
        def numel(self): return 512
    with tempfile.TemporaryDirectory() as directory:
        old = os.environ.get("M4A_RUN_DIR"); os.environ["M4A_RUN_DIR"] = f"{directory}/unit"; output = Path(directory) / "sidecar.json"
        source = {"transport": "HUGGING_FACE", "load_target": MODEL_ID,
                  "provenance": {"canonical_model_id": MODEL_ID, "frozen_revision": "a" * 40}}
        write_sidecar(output, "a" * 40, "real-tp4-rank0", 0, FakeFlat(),
                      [{"name": "x", "offset_bytes": 0, "size_bytes": 16, "dtype": "torch.bfloat16", "shape": [8, 2]}], PACKAGE_PINS, events1 + events2, source)
        from validate_metadata import validate
        assert validate(json.loads(output.read_text()))["kv_cache_events"] == 4 and "SYNTHETIC_KV" not in output.read_text()
        if old is None: del os.environ["M4A_RUN_DIR"]
        else: os.environ["M4A_RUN_DIR"] = old
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "snapshot"; root.mkdir(); revision = "b" * 40
        rows = []
        for name in LOCAL_SNAPSHOT_FILES:
            payload = name.encode(); (root / name).write_bytes(payload)
            rows.append({"path": name, "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
        manifest = Path(directory) / "snapshot-manifest.json"
        manifest.write_text(json.dumps({"schema_version": "m4a-local-model-snapshot-v1",
                                        "model": {"canonical_id": MODEL_ID, "revision": revision}, "files": rows}))
        prior_path, prior_manifest = os.environ.get("M4A_MODEL_LOCAL_PATH"), os.environ.get("M4A_MODEL_LOCAL_MANIFEST")
        os.environ["M4A_MODEL_LOCAL_PATH"], os.environ["M4A_MODEL_LOCAL_MANIFEST"] = str(root), str(manifest)
        try:
            local = require_model_source(revision); kwargs = model_load_kwargs(local, revision)
            assert local["transport"] == "LOCAL_SNAPSHOT" and kwargs["pretrained_model_name_or_path"] == str(root)
            assert kwargs["local_files_only"] is True and kwargs["revision"] == revision
        finally:
            if prior_path is None: os.environ.pop("M4A_MODEL_LOCAL_PATH", None)
            else: os.environ["M4A_MODEL_LOCAL_PATH"] = prior_path
            if prior_manifest is None: os.environ.pop("M4A_MODEL_LOCAL_MANIFEST", None)
            else: os.environ["M4A_MODEL_LOCAL_MANIFEST"] = prior_manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--route", choices=("real-tp4-rank0",)); parser.add_argument("--region", choices=sorted(REGIONS)); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: self_test(); print("PASS llama TP wrapper/KV self-test"); return 0
    if args.route != "real-tp4-rank0" or args.region not in REGIONS: parser.error("only real-tp4-rank0 with an explicit ROI is executable")
    revision, run_dir, metadata_path, phase, environment_region, model_source = require_environment()
    if args.region != environment_region: raise RuntimeError("CLI ROI and M4A_TRACE_REGION disagree")
    real_tp4(revision, run_dir, metadata_path, phase, args.region, model_source); print("PASS real-tp4 workload"); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except RuntimeError as error: print(f"error: {error}", file=sys.stderr); raise SystemExit(2)
