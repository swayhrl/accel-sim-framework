#!/usr/bin/env python3
"""One-load, six-session GPU runner for C16 OLMoE routing provenance V1."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, __version__ as transformers_version

ROOT = Path("/data/c16/olmoe_routing_provenance_multiround_v1")
MODEL = Path("/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e")
MODEL_ID = "allenai/OLMoE-1B-7B-0125-Instruct"
MODEL_REV = "b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e"
EXPECTED_INPUTS = {
    "P_TEXT": "bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5",
    "P_CODE": "107ef30b6f1bab3052bdd909b734ac538fa5aa4944c5094ac3b66c25fc3247f2",
    "P_STRUCTURED": "ec5cd4d780ee8b16829eb9c71c002996a114bf84b5209511cf75d0c8469fdad4",
    "P_PROSE": "e798d58332299434f0b945238c047340e6070cf881bd677fdfc62c369e24f2e4",
}
SESSIONS = [
    ("T0_NOHOOK_A", "P_TEXT", False),
    ("T1_NOHOOK_B", "P_TEXT", False),
    ("T2_TEXT_ALLLAYER", "P_TEXT", True),
    ("C1_CODE_ALLLAYER", "P_CODE", True),
    ("S1_STRUCTURED_ALLLAYER", "P_STRUCTURED", True),
    ("P1_PROSE_ALLLAYER", "P_PROSE", True),
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(t: torch.Tensor) -> str:
    data = t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return sha_bytes(data)


def atomic_json(path: Path, value) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def cache_len(cache) -> int:
    if hasattr(cache, "get_seq_length"):
        return int(cache.get_seq_length())
    raise RuntimeError(f"CACHE_LENGTH_UNOBSERVABLE {type(cache)}")


def cache_class(cache) -> str:
    return f"{type(cache).__module__}.{type(cache).__qualname__}"


class PassiveRouterCapture:
    def __init__(self, layers):
        self.layers = layers
        self.handles = []
        self.active = False
        self.context = None
        self.pending = {}

    def install(self):
        if self.handles:
            raise RuntimeError("hooks already installed")
        for layer_id, layer in enumerate(self.layers):
            mlp = layer.mlp
            path = f"model.layers.{layer_id}.mlp"

            def pre_hook(module, args, layer_id=layer_id, path=path):
                if not self.active:
                    return None
                hidden = args[0]
                self.pending[layer_id] = {
                    "session_id": self.context["session_id"],
                    "decode_step": self.context["decode_step"],
                    "layer_id": layer_id,
                    "module_path": path,
                    "input_token_id": self.context["input_token_id"],
                    "router_input_dtype": str(hidden.dtype),
                    "router_input_shape": list(hidden.shape),
                    "router_input_sha256": tensor_sha(hidden),
                    "configured_expert_count": int(module.num_experts),
                    "configured_experts_per_token": int(module.top_k),
                    "norm_topk_prob": bool(module.norm_topk_prob),
                    "cache_sequence_length_before": self.context["cache_sequence_length_before"],
                }
                return None

            def gate_hook(module, args, output, layer_id=layer_id):
                if not self.active:
                    return None
                if layer_id not in self.pending:
                    raise RuntimeError(f"missing router input for layer {layer_id}")
                mlp = self.layers[layer_id].mlp
                weights = F.softmax(output, dim=1, dtype=torch.float)
                weights, experts = torch.topk(weights, mlp.top_k, dim=-1)
                if mlp.norm_topk_prob:
                    weights = weights / weights.sum(dim=-1, keepdim=True)
                model_weights = weights.to(args[0].dtype)
                row = self.pending[layer_id]
                row.update({
                    "router_logits_dtype": str(output.dtype),
                    "router_logits_shape": list(output.shape),
                    "router_logits_sha256": tensor_sha(output),
                    "ordered_topk_expert_ids": [int(x) for x in experts[0].detach().cpu().tolist()],
                    "route_weights_float32_pre_cast": [float(x) for x in weights[0].detach().cpu().tolist()],
                    "route_weights_model_dtype_used": [float(x) for x in model_weights[0].detach().cpu().tolist()],
                    "route_weights_model_dtype": str(model_weights.dtype),
                })
                return None

            self.handles.append(mlp.register_forward_pre_hook(pre_hook))
            self.handles.append(mlp.gate.register_forward_hook(gate_hook))

    def begin_step(self, session_id, decode_step, input_token_id, before):
        if self.active:
            raise RuntimeError("capture already active")
        self.pending = {}
        self.context = {
            "session_id": session_id,
            "decode_step": decode_step,
            "input_token_id": input_token_id,
            "cache_sequence_length_before": before,
        }
        self.active = True

    def end_step(self, output_token_id, after, cache_identity_continuous):
        self.active = False
        if len(self.pending) != len(self.layers):
            raise RuntimeError(f"ROUTING_VALUES_INCOMPLETE {len(self.pending)}/{len(self.layers)}")
        rows = []
        for layer_id in range(len(self.layers)):
            row = self.pending[layer_id]
            if len(row["ordered_topk_expert_ids"]) != row["configured_experts_per_token"]:
                raise RuntimeError(f"TOPK_CAPTURE_INCOMPLETE layer={layer_id}")
            row.update({
                "output_token_id": output_token_id,
                "cache_sequence_length_after": after,
                "cache_object_identity_continuous": cache_identity_continuous,
            })
            rows.append(row)
        self.pending = {}
        self.context = None
        return rows

    def close(self):
        self.active = False
        for handle in self.handles:
            handle.remove()
        self.handles = []


def read_prompt(run: Path, prompt_id: str) -> list[int]:
    path = run / "inputs" / f"{prompt_id}.token_ids.json"
    observed = sha_file(path)
    if observed != EXPECTED_INPUTS[prompt_id]:
        raise RuntimeError(f"FROZEN_INPUT_CHANGED {prompt_id} {observed}")
    ids = json.loads(path.read_text())
    if len(ids) != 2048 or not all(isinstance(x, int) for x in ids):
        raise RuntimeError(f"FROZEN_INPUT_INVALID {prompt_id}")
    return ids


def run_session(model, run: Path, session_id: str, prompt_id: str, capture, eos_ids: set[int]):
    prompt_ids = read_prompt(run, prompt_id)
    prompt = torch.tensor([prompt_ids], dtype=torch.long, device="cuda")
    torch.cuda.synchronize()
    with torch.inference_mode():
        prefill = model(input_ids=prompt, use_cache=True, output_router_logits=False, return_dict=True)
        cache = prefill.past_key_values
        prefill_output = int(torch.argmax(prefill.logits[:, -1, :], dim=-1).item())
    prefill_cache_len = cache_len(cache)
    if prefill_cache_len != 2048:
        raise RuntimeError(f"PREFILL_CACHE_LENGTH_FAIL {session_id} {prefill_cache_len}")
    del prompt, prefill
    decode_rows = []
    routing_rows = []
    current = prefill_output
    stop_reason = None
    if current in eos_ids:
        stop_reason = "NATURAL_EOS_AT_PREFILL_OUTPUT"
    else:
        for step in range(1, 65):
            before = cache_len(cache)
            previous_cache_id = id(cache)
            if capture is not None:
                capture.begin_step(session_id, step, current, before)
            token = torch.tensor([[current]], dtype=torch.long, device="cuda")
            with torch.inference_mode():
                out = model(
                    input_ids=token,
                    past_key_values=cache,
                    use_cache=True,
                    output_router_logits=False,
                    return_dict=True,
                )
                next_token = int(torch.argmax(out.logits[:, -1, :], dim=-1).item())
            new_cache = out.past_key_values
            after = cache_len(new_cache)
            identity_continuous = id(new_cache) == previous_cache_id
            if after != before + 1:
                raise RuntimeError(f"CACHE_LENGTH_STEP_FAIL {session_id} {step} {before}->{after}")
            record = {
                "session_id": session_id,
                "decode_step": step,
                "input_token_id": current,
                "output_token_id": next_token,
                "cache_class": cache_class(new_cache),
                "cache_sequence_length_before": before,
                "cache_sequence_length_after": after,
                "cache_object_identity_continuous": identity_continuous,
                "eos": next_token in eos_ids,
            }
            decode_rows.append(record)
            if capture is not None:
                routing_rows.extend(capture.end_step(next_token, after, identity_continuous))
            cache = new_cache
            del token, out
            current = next_token
            if next_token in eos_ids:
                stop_reason = "NATURAL_EOS"
                break
        if stop_reason is None:
            stop_reason = "MAX_DECODE_STEPS_64"
    torch.cuda.synchronize()
    result = {
        "status": "PASS",
        "session_id": session_id,
        "prompt_id": prompt_id,
        "router_capture": capture is not None,
        "prompt_tokens": 2048,
        "prefill_output_token_id": prefill_output,
        "prefill_cache_sequence_length": prefill_cache_len,
        "decode_steps_executed": len(decode_rows),
        "output_token_ids": [r["output_token_id"] for r in decode_rows],
        "input_token_ids": [r["input_token_id"] for r in decode_rows],
        "decode_records": decode_rows,
        "routing_record_count": len(routing_rows),
        "stop_reason": stop_reason,
    }
    sessions_dir = run / "sessions"
    routes_dir = run / "routing"
    sessions_dir.mkdir(exist_ok=True)
    routes_dir.mkdir(exist_ok=True)
    atomic_json(sessions_dir / f"{session_id}.json", result)
    if capture is not None:
        expected = len(decode_rows) * len(capture.layers)
        if len(routing_rows) != expected:
            raise RuntimeError(f"ROUTING_ROW_COUNT_FAIL {session_id} {len(routing_rows)}/{expected}")
        tmp = routes_dir / f"{session_id}.jsonl.tmp"
        final = routes_dir / f"{session_id}.jsonl"
        with tmp.open("x") as f:
            for row in routing_rows:
                f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(final)
    del cache
    torch.cuda.empty_cache()
    return result


def same_sequence(a, b):
    return (
        a["prefill_output_token_id"] == b["prefill_output_token_id"]
        and a["decode_steps_executed"] == b["decode_steps_executed"]
        and a["output_token_ids"] == b["output_token_ids"]
    )


def main() -> None:
    run_id = (ROOT / "ACTIVE_RUN_ID").read_text().strip()
    run = ROOT / "raw" / run_id
    if (run / "GPU_RUN_RECEIPT.json").exists():
        raise SystemExit("refusing to reuse completed GPU run")
    manifest = json.loads((run / "CAMPAIGN_MANIFEST.pre_gpu.json").read_text())
    if manifest["run_id"] != run_id or manifest["status"] != "PREREGISTERED_BEFORE_GPU_EXECUTION":
        raise RuntimeError("PRE_GPU_MANIFEST_INVALID")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA_UNAVAILABLE")
    torch.manual_seed(20260928)
    torch.cuda.manual_seed_all(20260928)
    torch.cuda.reset_peak_memory_stats()
    load_started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    model_load_count = 0
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL),
        torch_dtype=torch.bfloat16,
        local_files_only=True,
    )
    model_load_count += 1
    model = model.to("cuda").eval()
    if next(model.parameters()).dtype != torch.bfloat16:
        raise RuntimeError("MODEL_DTYPE_NOT_BF16")
    if model.config.num_experts != 64 or model.config.num_experts_per_tok != 8 or len(model.model.layers) != 16:
        raise RuntimeError("MODEL_SEMANTICS_MISMATCH")
    eos = model.config.eos_token_id
    eos_ids = {int(eos)} if isinstance(eos, int) else {int(x) for x in eos}
    capture = PassiveRouterCapture(model.model.layers)
    results = {}
    completed = []
    control_state = "PENDING"
    try:
        for session_id, prompt_id, enabled in SESSIONS:
            if enabled and not capture.handles:
                capture.install()
            result = run_session(model, run, session_id, prompt_id, capture if enabled else None, eos_ids)
            results[session_id] = result
            completed.append(session_id)
            atomic_json(run / "SESSION_PROGRESS.json", {"completed": completed, "last_session": session_id})
            if session_id == "T2_TEXT_ALLLAYER":
                t0_t1 = same_sequence(results["T0_NOHOOK_A"], results["T1_NOHOOK_B"])
                t0_t2 = same_sequence(results["T0_NOHOOK_A"], results["T2_TEXT_ALLLAYER"])
                if not t0_t1:
                    control_state = "PROSPECTIVE_GREEDY_REPRODUCIBILITY_NOT_EXACT"
                elif not t0_t2:
                    control_state = "ROUTER_CAPTURE_OUTPUT_NEUTRALITY_FAIL"
                    atomic_json(run / "CONTROL_GATE.json", {"status": control_state, "stop_before": "C1_CODE_ALLLAYER"})
                    raise RuntimeError(control_state)
                else:
                    control_state = "PROSPECTIVE_OUTPUT_REPRODUCIBILITY_AND_HOOK_NEUTRALITY_PASS"
                atomic_json(run / "CONTROL_GATE.json", {
                    "status": control_state,
                    "T0_equals_T1": t0_t1,
                    "T0_equals_T2": t0_t2,
                    "common_steps": min(results[x]["decode_steps_executed"] for x in ("T0_NOHOOK_A", "T1_NOHOOK_B", "T2_TEXT_ALLLAYER")),
                })
    finally:
        capture.close()
    torch.cuda.synchronize()
    gpu_identity = (run / "GPU_IDENTITY.txt").read_text().strip().split(", ")
    receipt = {
        "status": "PASS_SIX_SESSIONS",
        "run_id": run_id,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REV,
        "model_load_count": model_load_count,
        "model_load_started_utc": load_started,
        "completed_sessions": completed,
        "session_count": len(completed),
        "control_state": control_state,
        "runtime": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "transformers": transformers_version,
            "dtype": str(next(model.parameters()).dtype),
            "attention_backend": model.config._attn_implementation,
            "cache_class": results[completed[0]]["decode_records"][0]["cache_class"] if results[completed[0]]["decode_records"] else "NO_DECODE",
        },
        "gpu": {
            "name": gpu_identity[0],
            "uuid": gpu_identity[1],
            "driver": gpu_identity[2],
            "compute_capability": ".".join(map(str, torch.cuda.get_device_capability(0))),
        },
        "generation": {
            "batch_size": 1, "prompt_tokens": 2048, "decode_cap": 64,
            "use_cache": True, "greedy_argmax": True, "sampling": False,
            "temperature": None, "top_p": None, "top_k_sampling": None,
            "beam_search": False, "natural_eos": True, "chat_template": False,
        },
        "peak_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_reserved_bytes": int(torch.cuda.max_memory_reserved()),
    }
    atomic_json(run / "GPU_RUN_RECEIPT.json", receipt)
    print(json.dumps({"status": receipt["status"], "run_id": run_id, "control_state": control_state, "sessions": len(completed)}))


if __name__ == "__main__":
    main()
