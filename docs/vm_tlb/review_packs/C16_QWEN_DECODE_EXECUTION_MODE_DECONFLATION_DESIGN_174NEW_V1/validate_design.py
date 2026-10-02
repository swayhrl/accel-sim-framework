#!/usr/bin/env python3
"""CPU-only checks for the Qwen execution-mode deconflation design."""

import argparse
import csv
import io
import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parent
PRODUCER = "82788c2d587e86f94791d65aaa2bde28929f9303"
CONSUMER = "9d82ff41132e7b1a1fdd18a287c13627fe62e5b7"
TIER0 = "fad9da8116c8ad794f99a93f153b0866162158a4"
VLLM = "ced6857afa0ea7b2e3f0846a62e1394e90f15607"
PACK = "docs/vm_tlb/review_packs/"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)


def source(repo, path):
    return git(repo, "show", f"{VLLM}:{path}")


def from_commit(repo, commit, path):
    return git(repo, "show", f"{commit}:{path}")


def local_tsv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows and all(None not in row for row in rows), name
    assert all(all(value != "" for value in row.values()) for row in rows), name
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vllm-repo", required=True, type=pathlib.Path)
    args = parser.parse_args()
    repo = pathlib.Path.cwd()
    assert git(repo, "cat-file", "-t", PRODUCER).strip() == "commit"
    assert git(repo, "cat-file", "-t", CONSUMER).strip() == "commit"
    assert git(repo, "cat-file", "-t", TIER0).strip() == "commit"
    assert git(args.vllm_repo, "rev-parse", VLLM).strip() == VLLM
    assert git(args.vllm_repo, "rev-parse", f"{VLLM}^{{tree}}").strip() == "22fe534b15542997d37f97a9079b4a1ac7961a18"

    producer = json.loads(from_commit(repo, PRODUCER, PACK + "C16_STAGEA_DENSE_FIRST_TIER0_PRODUCER_109_V1/FINAL_DECISION.json"))
    stops = json.loads(from_commit(repo, PRODUCER, PACK + "C16_STAGEA_DENSE_FIRST_TIER0_PRODUCER_109_V1/CORRECTNESS_STOP_RECEIPT.json"))
    consumer = json.loads(from_commit(repo, CONSUMER, PACK + "C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1/FINAL_DECISION.json"))
    prior_runner = from_commit(repo, PRODUCER, "util/vm_tlb/c16/stagea_dense_first_tier0/runner.py")
    assert producer["status"] == "STAGEA_TIER0_PRODUCER_PARTIAL"
    assert stops["MP02"]["status"] == stops["MP03"]["status"] == "STOP_POINT_CORRECTNESS"
    assert stops["threshold_or_tolerance_changed"] is False
    assert consumer["independent_tier0_survivor_count"] == 0
    assert consumer["no_new_architectural_phenomenon_found_claim_allowed"] is False
    assert set(consumer["question_final_status"].values()) == {"QUESTION_INCOMPLETE"}
    assert 'enforce_eager=args.graph_mode == "off"' in prior_runner
    postprocess = from_commit(repo, PRODUCER, "util/vm_tlb/c16/stagea_dense_first_tier0/postprocess_exact.py")
    assert "ATOL, RTOL = 0.05, 0.01" in postprocess

    vllm_cfg = source(args.vllm_repo, "vllm/config/vllm.py")
    compilation = source(args.vllm_repo, "vllm/config/compilation.py")
    llm = source(args.vllm_repo, "vllm/entrypoints/llm.py")
    decorators = source(args.vllm_repo, "vllm/compilation/decorators.py")
    qwen = source(args.vllm_repo, "vllm/model_executor/models/qwen2.py")
    manager = source(args.vllm_repo, "vllm/v1/worker/gpu/cudagraph_utils.py")
    assert "Enforce eager set, disabling torch.compile and CUDAGraphs" in vllm_cfg
    assert "self.compilation_config.mode = CompilationMode.NONE" in vllm_cfg
    assert "self.compilation_config.cudagraph_mode = CUDAGraphMode.NONE" in vllm_cfg
    assert "self.compilation_config.mode = CompilationMode.VLLM_COMPILE" in vllm_cfg
    assert "optimization_level: OptimizationLevel = OptimizationLevel.O2" in vllm_cfg
    assert "TORCH_COMPILE_DISABLE" in vllm_cfg
    assert "self.compilation_config.mode = CompilationMode.NONE" in vllm_cfg
    assert "Qwen2ForCausalLM" not in vllm_cfg.split("DEFAULT_BREAKABLE_CUDAGRAPH_ARCHITECTURES", 1)[1].split("@lru_cache", 1)[0]
    assert "cudagraph_mode: CUDAGraphMode = None" in compilation
    assert "if cudagraph_mode is None or cudagraph_mode == CUDAGraphMode.NONE:" in compilation
    assert "return CUDAGraphMode.NONE" in compilation
    assert "compilation_config: int | dict[str, Any] | CompilationConfig | None" in llm
    assert "self.do_not_compile = (" in decorators
    assert "get_forward_context().skip_compiled" in decorators
    assert "self.compiled = True" in decorators
    assert "@support_torch_compile(" in qwen
    assert "class Qwen2Model" in qwen
    assert "if not (self.cudagraph_mode and capture_sizes):" in manager

    contract = json.loads((ROOT / "C16_QWEN_DECODE_COMPILED_NO_CUDAGRAPH_CANARY_109_DRAFT.json").read_text())
    final = json.loads((ROOT / "FINAL_DECISION.json").read_text())
    correctness = local_tsv("CORRECTNESS_CONTRACT.tsv")
    backend = local_tsv("BACKEND_IDENTITY_REQUIREMENTS.tsv")
    assert contract["status"] == "DRAFT_FOR_PROJECT_APPROVAL" and contract["execution_authorized"] is False
    assert contract["authority"]["producer_commit"] == PRODUCER
    assert contract["authority"]["consumer_commit"] == CONSUMER
    assert contract["authority"]["tier0_contract_commit"] == TIER0
    assert contract["authority"]["vllm_source_commit"] == VLLM
    assert contract["scope"]["points_in_order"] == ["MP02", "MP03"]
    assert contract["execution"]["gpu_active_seconds_cap"] == 120
    assert contract["execution"]["semantic_observer"] == "FORBIDDEN"
    assert contract["modes"]["MODE_B_DIAGNOSTIC"]["compilation_config_python"] == "CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)"
    assert contract["modes"]["MODE_B_DIAGNOSTIC"]["enforce_eager"] is False
    assert contract["modes"]["MODE_C_HISTORICAL_FAILED"]["execute"] is False
    assert contract["correctness"]["atol"] == 0.05 and contract["correctness"]["rtol"] == 0.01
    assert contract["stage_sequence"]["if_mp02_fail"].startswith("STOP")
    assert len(correctness) == 2 and {r["point_id"] for r in correctness} == {"MP02", "MP03"}
    assert all(r["observer"] == "none" and r["free_running"] == "true" for r in correctness)
    assert any(r["mode"] == "MODE_C_HISTORICAL_FAILED" for r in backend)
    assert final["status"] == "MODE_DECONFLATION_DESIGN_READY_FOR_CANARY_REVIEW"
    assert final["execution_authorized"] is False and final["gpu_used"] is False
    assert final["formal_tier0_survivors"] == 0
    print("PASS: old failures preserved; pinned source mode split; canary correctness, identity, budget and no-execution schema")


if __name__ == "__main__":
    main()
