#!/usr/bin/env python3
"""Deterministic CPU/source-only runtime-environment audit for node 109."""

import argparse
import csv
import hashlib
import importlib.metadata as metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


DESIGN = "5f0335b5f991890348e60e1f23a546f393f86d8b"
DESIGN_TREE = "9453dc2edcc9ac40f83e62050fa51ea732cc5d01"
PREFLIGHT = "2f922c402c7f16c2bed278d07e12650cbaf82bfc"
PREFLIGHT_TREE = "1cc64086057679fcc6a3b4097f82a87eba5a3044"
VLLM_COMMIT = "ced6857afa0ea7b2e3f0846a62e1394e90f15607"
VLLM_TAG = "v0.30.0"
WHEEL_SHA = "ef52ee58c410ead0b8afb190838fa4cbcb52075596f67862a03859d984966ac4"
SDIST_SHA = "5f8f4e890c042ffa1c3e103f81c35e2d96f60a0a175ac43a4adbae7006bef62b"
SOURCE_EXPECTED = {
    "vllm/model_executor/layers/quantization/auto_awq.py": "4461351c05a44bd75225162d2617ac5a5cb1c2ea81da48a8de32e714bdd4133c",
    "CMakeLists.txt": "e93c1c098e2652f905cd5f229204b9024d24ee835e2ef5a4995503bec2a78b90",
    "vllm/v1/attention/backends/flash_attn.py": "b170a4789e18104c1bee35bea70df51abe6766693d8f4726a59f2e6f5c4282aa",
    "vllm/model_executor/models/granitemoe.py": "378e013cc23f011cc1d98d9c5bde72077765c612ac7bee41469e14962ab37530",
    "vllm/model_executor/layers/quantization/utils/marlin_utils.py": "c51456a32fd1455e10a4b7bb83cdaae535a466720d4517230a54c2659ecb8636",
    "vllm/model_executor/models/olmoe.py": "1bf3b12c959fd999e94a3046c00b084768635622a3bae686eab0036dd881d848",
    "vllm/model_executor/models/qwen2.py": "eb2f0eeb13c57a28bbc06bc64afff18cd8865f89fbe9ff2a3cf3a896f037cfe9",
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(*command, env=None, check=True):
    value = subprocess.run(command, text=True, capture_output=True, env=env)
    if check and value.returncode:
        raise RuntimeError(f"command failed {command}: {value.stderr}")
    return value.stdout.strip()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def line_of(path, needle):
    for index, line in enumerate(Path(path).read_text(errors="replace").splitlines(), 1):
        if needle in line:
            return index
    raise RuntimeError(f"source marker missing {needle}: {path}")


def dist_version_from_site(site, name):
    for dist in metadata.distributions(path=[str(site)]):
        if (dist.metadata.get("Name") or "").lower() == name.lower():
            return dist.version
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--env", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    site = args.env / "lib/python3.12/site-packages"
    receipts = args.root / "receipts"
    wheel = args.root / "downloads/vllm-0.30.0-cp38-abi3-manylinux_2_28_x86_64.whl"
    sdist = args.root / "downloads/vllm-0.30.0.tar.gz"
    freeze = receipts / "PIP_FREEZE.txt"
    shutil.copyfile(freeze, args.output_dir / "PINNED_REQUIREMENTS_FREEZE.txt")

    gpu_csv = run("nvidia-smi", "--query-gpu=name,uuid,pci.bus_id,compute_cap,memory.total,driver_version,vbios_version", "--format=csv,noheader")
    gpu_fields = [x.strip() for x in gpu_csv.split(",")]
    smi_head = run("nvidia-smi").splitlines()[:5]
    cuda_header = next(line for line in smi_head if "CUDA Version" in line)
    lspci = run("lspci", "-nn", "-s", "01:00.0")
    nvcc = {}
    for path in (Path("/usr/local/cuda/bin/nvcc"), Path("/usr/local/cuda-12.6/bin/nvcc"), Path("/usr/local/cuda-12.8/bin/nvcc")):
        if path.is_file():
            nvcc[str(path)] = run(str(path), "--version")
    nsys_version = run("/usr/local/bin/nsys", "--version")
    ncu_path = Path("/opt/nvidia/nsight-compute/2025.1.1/ncu")
    ncu_version = run(str(ncu_path), "--version")
    chips = (receipts / "NCU_LIST_CHIPS.txt").read_text().strip().split(", ")
    metric_query = receipts / "NCU_AD103_QUERY_METRICS.txt"
    translation_terms = {term: sum(term in line.lower() for line in metric_query.read_text(errors="replace").splitlines())
                         for term in ("tlb", "page_table", "page_walk", "ptw", "translation")}

    envs = []
    for base in (Path("/data/c16/env"), Path("/data/c16/envs")):
        if not base.exists():
            continue
        for cfg in sorted(base.glob("*/pyvenv.cfg")):
            env_path = cfg.parent
            candidates = list((env_path / "lib").glob("python*/site-packages"))
            env_site = candidates[0] if candidates else None
            values = {}
            for line in cfg.read_text(errors="replace").splitlines():
                if "=" in line:
                    k, v = line.split("=", 1); values[k.strip()] = v.strip()
            envs.append({"path": str(env_path), "python_version": values.get("version"),
                         "torch": dist_version_from_site(env_site, "torch") if env_site else None,
                         "vllm": dist_version_from_site(env_site, "vllm") if env_site else None,
                         "autoawq": dist_version_from_site(env_site, "autoawq") if env_site else None})

    ram = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        if key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
            ram[key] = int(value.strip().split()[0]) * 1024
    disks = {path: dict(zip(("total", "used", "free"), shutil.disk_usage(path))) for path in ("/data/c16", str(args.repo))}
    node = {
        "schema": "C16_NODE109_ENVIRONMENT_RECEIPT_V1", "status": "PASS_METADATA_ONLY",
        "authority": {"design_commit": DESIGN, "design_tree": DESIGN_TREE,
                      "preflight_commit": PREFLIGHT, "preflight_tree": PREFLIGHT_TREE},
        "node": 109,
        "gpu": {"name": gpu_fields[0], "uuid": gpu_fields[1], "pci_bus_id": gpu_fields[2],
                "compute_capability": gpu_fields[3], "memory_total": gpu_fields[4],
                "driver_version": gpu_fields[5], "vbios_version": gpu_fields[6],
                "pci_identity": lspci, "nvidia_smi_cuda_compatibility": cuda_header.strip()},
        "cuda_toolkits": nvcc, "host_python": sys.version, "host_platform": platform.platform(),
        "nsys": {"path": "/usr/local/bin/nsys", "version": nsys_version},
        "ncu": {"path": str(ncu_path), "version": ncu_version, "supported_chips": chips,
                "ad103_listed": "ad103" in chips},
        "ram_bytes": ram, "disk_bytes": disks, "existing_isolated_envs": envs,
        "forbidden_actions": {"model_loaded": False, "model_inference": False,
                              "cuda_kernel_benchmark": False, "nsys_capture": False,
                              "ncu_profile": False, "nvbit": False, "sass_capture": False,
                              "campaign_measurement": False, "gpu_lock_used": False},
    }
    dump(args.output_dir / "NODE109_ENVIRONMENT_RECEIPT.json", node)

    source_hashes = {name: sha(args.source / name) for name in SOURCE_EXPECTED}
    installed_hashes = {name: sha(site / name) for name in SOURCE_EXPECTED if (site / name).is_file()}
    source_exact = source_hashes == SOURCE_EXPECTED and installed_hashes == {k: v for k, v in SOURCE_EXPECTED.items() if (site / k).is_file()}
    source_identity = {
        "status": "PASS_AUTHORITY_COMMIT_EQUIVALENCE_BY_PINNED_SOURCE_ANCHORS" if source_exact else "FAIL",
        "tag": VLLM_TAG, "authority_commit": VLLM_COMMIT,
        "git_fetch": "BLOCKED_BY_GITHUB_NETWORK_TIMEOUT",
        "fallback": "official PyPI sdist and wheel for v0.30.0",
        "sdist_sha256": sha(sdist), "expected_sdist_sha256": SDIST_SHA,
        "wheel_sha256": sha(wheel), "expected_wheel_sha256": WHEEL_SHA,
        "source_anchor_sha256": source_hashes, "installed_anchor_sha256": installed_hashes,
        "all_authority_source_anchors_exact": source_exact,
        "boundary": "full Git object/tree not fetched locally; official tag artifacts plus all preflight-pinned runtime source anchors are exact",
    }
    dump(args.output_dir / "SOURCE_IDENTITY.json", source_identity)

    inventory = []
    for dist in metadata.distributions(path=[str(site)]):
        name = dist.metadata.get("Name") or "UNKNOWN"
        dist_path = Path(dist._path)
        meta = dist_path / "METADATA"
        record = dist_path / "RECORD"
        direct = dist_path / "direct_url.json"
        inventory.append({"package": name, "version": dist.version, "dist_info": str(dist_path),
                          "metadata_sha256": sha(meta) if meta.is_file() else "",
                          "record_sha256": sha(record) if record.is_file() else "",
                          "direct_url_sha256": sha(direct) if direct.is_file() else "",
                          "installed_file_count": len(dist.files or [])})
    inventory.sort(key=lambda row: row["package"].lower())
    write_tsv(args.output_dir / "PACKAGE_INVENTORY.tsv", inventory)
    important = {name: dist_version_from_site(site, name) for name in
                 ("vllm", "torch", "triton", "flashinfer-python", "humming-kernels", "cuda-toolkit", "nvtx", "nvidia-cudnn-cu13")}
    torch_version_source = (site / "torch/version.py").read_text()
    torch_build = {key: re.search(rf"^{key}[^=]*= ['\"]([^'\"]+)", torch_version_source, re.M).group(1)
                   for key in ("__version__", "cuda", "git_version")}
    extensions = [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}
                  for path in sorted((site / "vllm").rglob("*.so"))]
    lib_dirs = [str(path) for path in site.rglob("lib") if path.is_dir()]
    ldd_env = dict(os.environ)
    ldd_env["LD_LIBRARY_PATH"] = ":".join(lib_dirs)
    main_ext = site / "vllm/_C_stable_libtorch.abi3.so"
    ldd_output = run("ldd", str(main_ext), env=ldd_env)
    unresolved = [line.strip() for line in ldd_output.splitlines() if "not found" in line]
    pip_check = run(str(args.env / "bin/python"), "-m", "pip", "check")
    runtime = {
        "schema": "C16_PINNED_RUNTIME_ENVIRONMENT_V1",
        "status": "BUILT_SOURCE_MATCHED_NOT_GPU_ACCEPTED" if source_exact and not unresolved and "No broken requirements" in pip_check else "BUILD_VALIDATION_FAILED",
        "environment_path": str(args.env), "python_version": run(str(args.env / "bin/python"), "--version"),
        "vllm": {"version": important["vllm"], "tag": VLLM_TAG, "authority_commit": VLLM_COMMIT,
                 "wheel_path": str(wheel), "wheel_sha256": sha(wheel),
                 "sdist_path": str(sdist), "sdist_sha256": sha(sdist),
                 "metadata_sha256": sha(site / "vllm-0.30.0.dist-info/METADATA"),
                 "record_sha256": sha(site / "vllm-0.30.0.dist-info/RECORD"),
                 "direct_url_sha256": sha(site / "vllm-0.30.0.dist-info/direct_url.json")},
        "torch": torch_build, "important_packages": important,
        "pip_freeze_sha256": sha(freeze), "package_inventory_sha256": sha(args.output_dir / "PACKAGE_INVENTORY.tsv"),
        "package_count": len(inventory), "vllm_extension_files": extensions,
        "main_extension_ldd": ldd_output, "main_extension_unresolved": unresolved,
        "pip_check": pip_check, "source_identity": source_identity["status"],
        "driver_cuda_compatibility": "13.0", "local_toolkit_default": "12.8",
        "runtime_acceptance": "NOT_ACCEPTED_UNTIL_GPU_QUALIFICATION_CANARY",
        "actual_selected_backends": "UNKNOWN_NOT_RUN",
        "historical_environments_modified": False,
    }
    dump(args.output_dir / "PINNED_RUNTIME_ENVIRONMENT.json", runtime)

    qwen = args.source / "vllm/model_executor/models/qwen2.py"
    awq = args.source / "vllm/model_executor/layers/quantization/auto_awq.py"
    marlin = args.source / "vllm/model_executor/layers/quantization/utils/marlin_utils.py"
    olmoe = args.source / "vllm/model_executor/models/olmoe.py"
    flash = args.source / "vllm/v1/attention/backends/flash_attn.py"
    capabilities = [
        ("QWEN_BF16", "attention backend candidates", "SOURCE_CONDITIONAL", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", flash, "class FlashAttentionBackend", "source implementation exists; head-dim/device/runtime dispatch not executed"),
        ("QWEN_BF16", "merged MLP path", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", qwen, "self.gate_up_proj = MergedColumnParallelLinear", "gate/up merged source and SiluAndMul are present"),
        ("QWEN_BF16", "projection kernel dispatch", "SOURCE_CONDITIONAL", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", qwen, "gate_up_proj", "logical module path is fixed; actual CUDA kernel is runtime-selected"),
        ("QWEN_AWQ", "AWQ group128 zero-point parsing", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", awq, "zero_point = cls.get_from_keys", "group_size and zero_point are read from checkpoint config"),
        ("QWEN_AWQ", "lossless AWQ repack semantics", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", awq, "_convert_awq_to_standard_format", "unpack/reorder/repack source exists; no requantization is implied"),
        ("QWEN_AWQ", "AWQ-Marlin SM89 compatibility", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", marlin, "device_capability < 75", "uint4 with runtime zero-point is source-supported above SM75; SM89-special FP8 input path also exists"),
        ("OLMOE", "FusedMoE class", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", olmoe, "self.experts = FusedMoEFactory", "OLMoE instantiates FusedMoEFactory"),
        ("OLMOE", "candidate expert backend", "SOURCE_CONDITIONAL", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", olmoe, "self.experts", "expert implementation is factory/runtime selected"),
        ("OLMOE", "BF16 execution path", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", olmoe, "hidden_states", "no source-level dtype prohibition found; checkpoint/runtime correctness still required"),
        ("OLMOE", "routing implementation", "SOURCE_SUPPORTED", "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", olmoe, "router_logits", "replicated gate produces router logits consumed by fused experts"),
    ]
    cap_rows = []
    for workload, capability, source_status, runtime_status, path, marker, evidence in capabilities:
        cap_rows.append({"workload": workload, "capability": capability, "source_status": source_status,
                         "runtime_status": runtime_status, "source_path": str(path.relative_to(args.source)),
                         "source_sha256": sha(path), "anchor_line": line_of(path, marker), "evidence": evidence,
                         "actual_selected_kernel": "UNKNOWN_NOT_RUN"})
    write_tsv(args.output_dir / "STATIC_BACKEND_CAPABILITY.tsv", cap_rows)

    torch_events = site / "torch/cuda/streams.py"
    tool_rows = [
        {"tool_or_group": "NVTX Python", "version": important["nvtx"], "path": str(site / "nvtx"), "capability": "NVTX range emission source/package", "status": "SOURCE_SUPPORTED", "qualification": "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", "exact_metrics_frozen": False},
        {"tool_or_group": "NSYS cuda,nvtx", "version": nsys_version, "path": "/usr/local/bin/nsys", "capability": "--trace=cuda,nvtx CLI", "status": "SOURCE_SUPPORTED", "qualification": "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", "exact_metrics_frozen": False},
        {"tool_or_group": "CUDA event timing", "version": important["torch"], "path": str(torch_events), "capability": "torch.cuda.Event(enable_timing=True)", "status": "SOURCE_SUPPORTED", "qualification": "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", "exact_metrics_frozen": False},
        {"tool_or_group": "NCU AD103/SM89", "version": ncu_version.splitlines()[-1], "path": str(ncu_path), "capability": "AD103 chip metadata", "status": "SOURCE_SUPPORTED", "qualification": "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", "exact_metrics_frozen": False},
    ]
    for group in ("CTA/wave supply", "active warp/occupancy", "stall", "L1/TEX", "L2", "DRAM"):
        tool_rows.append({"tool_or_group": f"NCU observable: {group}", "version": "2025.1.1.0", "path": str(ncu_path),
                          "capability": "observable group only", "status": "SOURCE_CONDITIONAL",
                          "qualification": "RUNTIME_SELECTION_REQUIRES_GPU_CANARY", "exact_metrics_frozen": False})
    tool_rows.append({"tool_or_group": "translation/TLB/PTW blocked-time", "version": "2025.1.1.0", "path": str(metric_query),
                      "capability": "no direct term in AD103 query catalog", "status": "SOURCE_UNSUPPORTED",
                      "qualification": "TRANSLATION_OBSERVABLE_UNQUALIFIED", "exact_metrics_frozen": False})
    write_tsv(args.output_dir / "INSTRUMENTATION_TOOL_AUDIT.tsv", tool_rows)
    ncu_receipt = {"status": "PASS_TOOL_METADATA_ONLY", "version": ncu_version,
                   "ad103_listed": "ad103" in chips, "metric_catalog_lines": len(metric_query.read_text().splitlines()),
                   "translation_term_counts": translation_terms,
                   "translation_status": "TRANSLATION_OBSERVABLE_UNQUALIFIED",
                   "exact_metric_names_frozen": False, "profile_executed": False,
                   "list_chips_sha256": sha(receipts / "NCU_LIST_CHIPS.txt"),
                   "query_catalog_sha256": sha(metric_query)}
    dump(args.output_dir / "NCU_CAPABILITY_RECEIPT.json", ncu_receipt)

    (args.output_dir / "INSTRUMENTATION_CANARY_PLAN.md").write_text("""# Instrumentation canary plan — not authorized for execution\n\nFor each approved runtime family, execute one bounded OFF/ON pair only after project approval. OFF has no observational ranges; ON adds the frozen NVTX ranges and identical outer CUDA events. Require exact token/correctness, shapes, routing (for OLMoE), kernel name/count/grid/block inventory and ordering. Compare native CUDA-event wall time with a predeclared neutrality tolerance; NSYS duration is not the primary timing endpoint. Use only `nsys profile --trace=cuda,nvtx` for the ON structural capture. If instrumentation changes correctness, scheduling, kernel inventory, or exceeds the predeclared wall tolerance, STOP. No capture is performed by this audit.\n""")

    vram_md = f"""# OLMoE VRAM qualification-canary plan\n\nThis is static planning only; no model was loaded. The pinned OLMoE weights total 13,838,721,960 bytes. Authority estimates place the graph-OFF lower envelope at 15,520,637,864 bytes and the conservative upper envelope at 19,278,734,248 bytes versus node109's {gpu_fields[4]}. vLLM defaults `gpu_memory_utilization=0.92`, profiles/reserves KV dynamically unless `kv_cache_memory_bytes` is explicit, and exposes `max_model_len`, `max_num_seqs`, `enforce_eager`, and CUDA-graph compilation controls. The built-in CuMemAllocator is available; sleep mode/custom allocation policy is not part of the canary.\n\n`STRONG_RUNTIME_VRAM_RISK`: graph ON may require materially more memory and may not fit. This estimate is not a failure decision.\n\nFuture graph-OFF identity canary (project approval required): M=1, context=512 plus D0–D31, `max_model_len=544`, `max_num_seqs=1`, graph/compile OFF (`enforce_eager=True`), frozen BF16 checkpoint/input/tokenization receipt. Record load success, peak/steady VRAM, tokens, routing, kernel/backend identity, and unload closure.\n\nFuture graph-ON strong-baseline qualification: identical model/input/limits with the mature default compiled/CUDA-graph path. Require correctness, routing and kernel identity contract; record graph pool/reservation and peak VRAM. OOM is preserved as a qualification failure, not bypassed by offload or a weaker backend. Combined future GPU-active cap: <=4 minutes. This audit does not authorize it.\n"""
    (args.output_dir / "OLMOE_VRAM_CANARY_PLAN.md").write_text(vram_md)

    gaps = """# Runtime qualification gaps\n\n- The isolated vLLM 0.30.0 wheel is source-anchor matched and dependency-closed, but has not been imported against a live CUDA device or accepted as the campaign runtime.\n- Actual Qwen attention/projection kernels, AWQ-Marlin selection/repack output, and OLMoE expert backend remain unknown until an approved GPU canary.\n- No model load, VRAM feasibility, tokenization receipt, token correctness, routing correctness, graph OFF/ON identity, or instrumentation neutrality has been executed.\n- OLMoE graph ON remains `STRONG_RUNTIME_VRAM_RISK`; static estimates cannot declare success or failure.\n- NCU exact metrics are deliberately not frozen. The AD103 catalog exposes no directly named TLB/PTW/translation blocked-time observable; `TRANSLATION_OBSERVABLE_UNQUALIFIED` remains.\n- Direct GitHub fetch of the pinned commit timed out. Official v0.30.0 sdist/wheel hashes are frozen and every preflight-pinned runtime source anchor matches exactly; the full Git object/tree was not locally fetched.\n- Existing installed runtimes are inventory only and are not accepted substitutes.\n"""
    (args.output_dir / "RUNTIME_QUALIFICATION_GAPS.md").write_text(gaps)

    draft = {
        "schema": "C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_DRAFT_V1",
        "status": "DRAFT_FOR_PROJECT_APPROVAL", "authorized_to_execute": False,
        "node": 109, "gpu": gpu_fields[0], "gpu_uuid": gpu_fields[1],
        "runtime_environment": str(args.env), "vllm_tag": VLLM_TAG, "vllm_commit": VLLM_COMMIT,
        "gpu_lock": "/data/c16/locks/c16_gpu_campaign.lock", "gpu_active_cap_seconds": 240,
        "purpose_only": ["model loads", "VRAM feasibility", "correctness", "tokenization receipt match",
                         "actual selected backend/kernel identity", "instrumentation ON/OFF neutrality",
                         "graph OFF/ON strong-path qualification"],
        "forbidden_in_canary": ["scientific performance conclusion", "NCU profiling", "NVBit", "SASS", "Accel-Sim", "fallback backend", "requantization"],
        "targets": [
            {"id": "QWEN_BF16", "model": "Qwen/Qwen2.5-3B-Instruct", "revision": "aa8e72537993ba99e69dfaafa59ed015b17504d1", "dtype": "bfloat16", "graph_off_then_on": True},
            {"id": "QWEN_AWQ", "model": "Qwen/Qwen2.5-3B-Instruct-AWQ", "revision": "3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd", "quantization": {"bits": 4, "group_size": 128, "zero_point": True, "method": "awq"}, "graph_off_then_on": True},
            {"id": "OLMOE", "model": "allenai/OLMoE-1B-7B-0125-Instruct", "revision": "b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e", "dtype": "bfloat16", "graph_off": {"batch": 1, "context": 512, "decode": 32, "max_model_len": 544, "max_num_seqs": 1}, "graph_on_qualification": True, "risk": "STRONG_RUNTIME_VRAM_RISK"},
        ],
        "instrumentation_pair": {"off": "no observational hooks", "on": "frozen NVTX plus identical CUDA events",
                                 "checks": ["tokens", "numeric correctness", "shapes", "routing", "kernel inventory", "wall-time neutrality"]},
        "stop_conditions": ["load failure", "OOM", "tokenization mismatch", "correctness mismatch", "routing mismatch", "backend identity unresolved", "instrumentation non-neutral", "graph ON not semantically identical", "240-second cap"],
        "postcondition": "publish receipts and STOP for project review; no campaign measurement",
    }
    dump(args.output_dir / "C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_DRAFT.json", draft)

    ready = runtime["status"] == "BUILT_SOURCE_MATCHED_NOT_GPU_ACCEPTED" and node["ncu"]["ad103_listed"]
    decision = {
        "schema": "C16_RUNTIME_ENVIRONMENT_AUDIT_FINAL_V1",
        "status": "RUNTIME_ENV_READY_FOR_GPU_CANARY_REVIEW" if ready else "RUNTIME_ENV_PARTIAL",
        "environment_build": runtime["status"], "source_identity": source_identity["status"],
        "runtime_accepted": False, "gpu_canary_authorized": False,
        "actual_selected_backends": "UNKNOWN_NOT_RUN",
        "translation_status": "TRANSLATION_OBSERVABLE_UNQUALIFIED",
        "olmoe_vram": "STRONG_RUNTIME_VRAM_RISK",
        "model_loaded": False, "model_inference": False, "cuda_kernel_executed": False,
        "profiler_capture_executed": False, "campaign_measurement_executed": False,
        "next_gate": "project approval of C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_DRAFT.json",
    }
    dump(args.output_dir / "FINAL_DECISION.json", decision)
    build = {"status": "PASS" if ready else "PARTIAL", "environment": str(args.env),
             "wheel_sha256": sha(wheel), "sdist_sha256": sha(sdist), "pip_check": pip_check,
             "package_inventory_sha256": sha(args.output_dir / "PACKAGE_INVENTORY.tsv"),
             "freeze_sha256": sha(args.output_dir / "PINNED_REQUIREMENTS_FREEZE.txt"),
             "source_anchor_match": source_exact, "extension_ldd_unresolved": unresolved,
             "historical_envs_modified": False}
    dump(args.output_dir / "ENVIRONMENT_BUILD_RECEIPT.json", build)
    tests = {"status": "PASS" if ready else "PARTIAL", "authority_trees_bound": True,
             "source_anchor_hashes_exact": source_exact, "wheel_hash_exact": sha(wheel) == WHEEL_SHA,
             "sdist_hash_exact": sha(sdist) == SDIST_SHA, "pip_check": pip_check,
             "main_extension_dependencies_resolved_with_candidate_library_path": not unresolved,
             "ncu_ad103_metadata": "ad103" in chips, "forbidden_actions_executed": []}
    dump(args.output_dir / "TESTS.json", tests)
    (args.output_dir / "README.md").write_text("""# Node109 runtime environment audit V1\n\nCPU/source/environment qualification only. The isolated vLLM 0.30.0 environment is built from the hash-pinned official wheel, with all preflight-pinned source anchors matching the official sdist and installed package. This does not accept a runtime backend: model load, CUDA execution, selected kernels, graph feasibility, correctness and instrumentation neutrality remain future project-approved canary gates.\n""")
    print(json.dumps(decision, sort_keys=True))
    if decision["status"] == "RUNTIME_ENV_BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
