#!/usr/bin/env python3
"""CPU-only source/authority/sequence validation; imports no CUDA runtime."""

import argparse
import ast
import csv
import hashlib
import json
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[4]
SOURCE = pathlib.Path(__file__).resolve().parent
PACK = ROOT / "docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CONTRACT_174NEW_V1"
MODE_PASS = "9122fac5c50dbf19706636fc03978a356ffd800f"
V2_SOURCE = "f63d39c8d90ced038445c264fa8242c524a1aa6f"
AWQ_PASS = "9d5aa2f36e22a1a8fcc253d6df865160b5dba797"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def at(commit, path):
    return git("show", f"{commit}:{path}")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cuda_event_calls(tree):
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr == "Event" and isinstance(fn.value, ast.Attribute) and fn.value.attr == "cuda" and isinstance(fn.value.value, ast.Name) and fn.value.value.id == "torch":
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vllm-repo", required=True, type=pathlib.Path)
    parser.add_argument("--model-config", required=True, type=pathlib.Path)
    args = parser.parse_args()
    contract = json.loads((PACK / "C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1.json").read_text())
    decision = json.loads((PACK / "FINAL_DECISION.json").read_text())
    checks = json.loads((PACK / "CORRECTNESS_AND_NEUTRALITY_CONTRACT.json").read_text())
    runner = (SOURCE / "runner.py").read_text()
    observer = (SOURCE / "observer_v2.py").read_text()
    builder = (SOURCE / "build_expected_sequence.py").read_text()
    for src in (runner, observer, builder):
        ast.parse(src)
    runner_ast, observer_ast = ast.parse(runner), ast.parse(observer)
    hook = next(node for node in observer_ast.body if isinstance(node, ast.ClassDef) and node.name == "HookSession")
    assert cuda_event_calls(hook) == 0
    assert cuda_event_calls(runner_ast) == 2
    assert "torch.cuda.synchronize" not in ast.get_source_segment(observer, hook)
    assert "torch.cuda.nvtx.range_push(label)" in observer
    assert "torch.cuda.nvtx.range_pop()" in observer
    assert all(value in observer for value in ("ordinal", "module_name", "input_shape", "output_shape"))
    assert "CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)" in runner
    assert "enforce_eager=False" in runner
    assert "MODE_A_STRONG" not in runner
    assert "(" + '"OFF", "ON", "ON", "OFF", "OFF", "ON"' + ")" in runner
    assert "--remaining-point-seconds" in runner
    assert contract["status"] == "AUTHORIZED_BY_PROJECT_REVIEW" and contract["execution_authorized"] is True
    assert contract["automatic_gpu_start"] is False
    assert contract["scope"]["points_in_order"] == ["MP02", "MP03"]
    assert contract["budget"]["total_gpu_active_seconds_cap"] == 180
    assert contract["budget"]["per_point_seconds_cap"] == {"MP02": 75, "MP03": 105}
    assert contract["observer_v2"]["expected_semantic_occurrences_per_request"] == 4608
    assert checks["sampled_logprob"]["atol"] == 0.05 and checks["sampled_logprob"]["rtol"] == 0.01
    assert checks["native_protocol"]["sample_order"] == ["OFF", "ON", "ON", "OFF", "OFF", "ON"]
    assert checks["nsys"]["only_after_native_all_gates_pass"] is True
    assert contract["on_full_pass"] == "STAGEA_V2_CONTRACT_REVIEW_ONLY"
    assert contract["automatic_tier0_rerun"] is False
    assert decision["compiled_identity_with_observer_runtime_status"] == "UNKNOWN_PENDING_CANARY"
    assert decision["gpu_used_in_this_goal"] is False and decision["awq_observer_pass_transferred_to_bf16"] is False

    pack_prefix = "docs/vm_tlb/review_packs/"
    runtime_decision = json.loads(at(MODE_PASS, pack_prefix + "C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1/FINAL_DECISION.json"))
    assert runtime_decision["decision"] == "MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY"
    assert runtime_decision["mp02_pass"] is runtime_decision["mp03_pass"] is True
    base_runner = at(MODE_PASS, "util/vm_tlb/c16/qwen_decode_mode_deconflation_canary/runner.py").encode()
    assert hashlib.sha256(base_runner).hexdigest() == contract["source_identity"]["mode_b_base_runner_sha256"]
    configs = json.loads(at(MODE_PASS, pack_prefix + "C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1/EFFECTIVE_MODE_CONFIG.json"))
    mode_b = [item for item in configs if item["mode"] == "B"]
    assert len(mode_b) == 2
    assert all(item["config"]["compilation_mode"] == "VLLM_COMPILE" and item["config"]["backend"] == "inductor" and item["config"]["cudagraph_mode"] == "NONE" and item["config"]["enforce_eager"] is False for item in mode_b)
    v2 = at(V2_SOURCE, "util/vm_tlb/c16/stagea_runtime_qualification/runner.py")
    assert cuda_event_calls(next(node for node in ast.parse(v2).body if isinstance(node, ast.ClassDef) and node.name == "HookSession")) == 0
    assert all(term in v2 and term in observer for term in ("C16_STAGEA_", "torch.cuda.nvtx.range_push", "torch.cuda.nvtx.range_pop", "semantic_order_sha256"))
    awq = json.loads(at(AWQ_PASS, pack_prefix + "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_109_V1/FINAL_DECISION.json"))
    assert awq["status"] == "OBSERVER_V2_NEUTRALITY_PASS"

    vllm = subprocess.check_output(["git", "-C", str(args.vllm_repo), "show", "ced6857afa0ea7b2e3f0846a62e1394e90f15607:vllm/model_executor/models/qwen2.py"], text=True)
    assert "hidden_states = self.self_attn(" in vllm
    assert "positions=positions," in vllm and "hidden_states=hidden_states," in vllm
    assert vllm.index("gate_up, _ = self.gate_up_proj(x)") < vllm.index("x = self.act_fn(gate_up)") < vllm.index("x, _ = self.down_proj(x)")
    config = json.loads(args.model_config.read_text())
    assert (config["num_hidden_layers"], config["hidden_size"], config["intermediate_size"]) == (36, 2048, 11008)
    receipt = json.loads(at("c3f625e46adb8d5c4082ded8b61858c710e1f4e9", pack_prefix + "C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1/QWEN_BF16_ASSET_RECEIPT.json"))
    assert digest(args.model_config) == receipt["config_sha256"]

    sequence_path = PACK / "EXPECTED_SEMANTIC_SEQUENCE.tsv"
    assert digest(sequence_path) == contract["source_identity"]["expected_sequence_sha256"]
    with sequence_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    assert len(rows) == 9216
    for point, batch in (("MP02", 1), ("MP03", 4)):
        selected = [row for row in rows if row["point_id"] == point]
        assert len(selected) == 4608
        assert [int(row["ordinal"]) for row in selected] == list(range(4608))
        for row in selected:
            forward, layer = int(row["forward_index"]), int(row["layer"])
            role_index = ("self_attn", "gate_up_proj", "act_fn", "down_proj").index(row["module_role"])
            assert int(row["ordinal"]) == forward * 144 + layer * 4 + role_index
            tokens = batch * (512 if forward == 0 else 1)
            assert row["generated_step"] == f"D{forward}"
            assert json.loads(row["expected_output_shape"])[0] == tokens
            if role_index == 0:
                assert json.loads(row["expected_input_shape"]) is None
    with tempfile.TemporaryDirectory(prefix="c16-mode-b-v2-static-") as directory:
        regenerated = pathlib.Path(directory) / "sequence.tsv"
        subprocess.check_call(["python3", str(SOURCE / "build_expected_sequence.py"), "--model-config", str(args.model_config), "--output", str(regenerated)])
        assert regenerated.read_bytes() == sequence_path.read_bytes()
    for path_key, sha_key in (("runner_path", "runner_sha256"), ("observer_path", "observer_sha256"), ("sequence_builder_path", "sequence_builder_sha256")):
        assert digest(ROOT / contract["source_identity"][path_key]) == contract["source_identity"][sha_key]
    print("PASS: pinned authority, V2 source port, 0 inner/1 outer Event pair, deterministic 4608-per-point sequence, contract and no GPU")


if __name__ == "__main__":
    main()
