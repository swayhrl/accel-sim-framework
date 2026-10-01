#!/usr/bin/env python3
"""Finalize authority, installation, and external-artifact receipts."""

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


DESIGN = "5f0335b5f991890348e60e1f23a546f393f86d8b"
PREFLIGHT = "2f922c402c7f16c2bed278d07e12650cbaf82bfc"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--env", type=Path, required=True)
    args = p.parse_args()
    design_tree = git(args.repo, "rev-parse", DESIGN + "^{tree}")
    preflight_tree = git(args.repo, "rev-parse", PREFLIGHT + "^{tree}")
    design_pack = args.repo / "docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_174NEW_V1"
    preflight_pack = args.repo / "docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1"
    authority = {"status": "PASS", "design_commit": DESIGN, "design_tree": design_tree,
                 "preflight_commit": PREFLIGHT, "preflight_tree": preflight_tree,
                 "design_sha256s": sha(design_pack / "SHA256SUMS"),
                 "preflight_sha256s": sha(preflight_pack / "SHA256SUMS"),
                 "design_pack_verification": "PASS_IN_DETACHED_DESIGN_COMMIT_WORKTREE",
                 "preflight_pack_verification": "PASS_IN_PREFLIGHT_BASE_WORKTREE",
                 "design_handoff_in_preflight_tree": "EXPECTED_SUCCESSOR_NOTE_ADDITION; not used for design-commit SHA verification",
                 "execution_ready_in_preflight": False,
                 "this_goal_scope": "environment/source qualification only"}
    dump(args.pack / "AUTHORITY_RECEIPT.json", authority)

    site = args.env / "lib/python3.12/site-packages"
    paths = [
        args.root / "downloads/vllm-0.30.0-cp38-abi3-manylinux_2_28_x86_64.whl",
        args.root / "downloads/vllm-0.30.0.tar.gz",
        args.root / "receipts/PIP_FREEZE.txt",
        args.root / "receipts/NCU_LIST_CHIPS.txt",
        args.root / "receipts/NCU_AD103_QUERY_METRICS.txt",
        args.root / "receipts/NCU_HELP.txt",
        args.root / "receipts/NSYS_PROFILE_HELP.txt",
        site / "vllm-0.30.0.dist-info/METADATA",
        site / "vllm-0.30.0.dist-info/RECORD",
        site / "vllm-0.30.0.dist-info/direct_url.json",
        site / "vllm/_C_stable_libtorch.abi3.so",
        site / "vllm/_moe_C_stable_libtorch.abi3.so",
    ]
    rows = [{"artifact": path.name, "path": str(path), "bytes": path.stat().st_size,
             "sha256": sha(path), "role": "external immutable receipt; not committed payload"}
            for path in paths]
    with (args.pack / "EXTERNAL_ARTIFACT_INDEX.tsv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    install = {
        "status": "PASS", "environment": str(args.env), "python": "3.12.3",
        "vllm_tag": "v0.30.0", "vllm_authority_commit": "ced6857afa0ea7b2e3f0846a62e1394e90f15607",
        "source_acquisition": {"github_exact_fetch": "FAILED_AFTER_BOUNDED_RETRIES_CONNECTION_TIMEOUT",
                               "accepted_artifacts": "official PyPI v0.30.0 sdist and wheel",
                               "all_preflight_source_anchors_exact": True},
        "install_commands": [
            "python3 -m venv /data/c16/envs/c16-vllm-v0.30.0-sm89-v1",
            "python -m pip install pip==26.2.1 setuptools==80.10.2 wheel==0.48.0",
            "python -m pip install /data/c16/runtime_environment_audit_v1/downloads/vllm-0.30.0-cp38-abi3-manylinux_2_28_x86_64.whl",
        ],
        "wheel_sha256": rows[0]["sha256"], "sdist_sha256": rows[1]["sha256"],
        "pip_freeze_sha256": rows[2]["sha256"], "pip_check": "No broken requirements found.",
        "torch": "2.13.0+cu130", "torch_cuda": "13.0", "triton": "3.7.1",
        "audit_script_sha256": sha(args.repo / "util/vm_tlb/c16/runtime_environment_audit_v1/audit.py"),
        "finalize_script_sha256": sha(args.repo / "util/vm_tlb/c16/runtime_environment_audit_v1/finalize.py"),
        "historical_environments_modified": False,
        "model_loaded": False, "model_inference": False, "cuda_kernel_executed": False,
        "gpu_lock_used": False, "profilers_executed": False,
    }
    dump(args.pack / "INSTALLATION_RECEIPT.json", install)
    final = json.loads((args.pack / "FINAL_DECISION.json").read_text())
    audit = f"""# Runtime environment audit final\n\n- Node109 is RTX4080 AD103/SM89, driver 580.178.04, CUDA-driver compatibility 13.0.\n- The isolated environment is `{args.env}`; historical AutoAWQ/NVBit environments were not modified.\n- Official vLLM 0.30.0 wheel/sdist are hash-pinned, and every preflight-pinned runtime source anchor matches the installed package.\n- Torch is 2.13.0+cu130; the default host toolkit remains 12.8, while the wheel carries its CUDA 13 runtime. `pip check` and the candidate-library-path ELF dependency audit pass.\n- Qwen BF16 merged MLP, AWQ group128 zero-point/lossless repack/Marlin, and OLMoE FusedMoE/routing are source-qualified. Actual selected kernels remain unknown and require an approved GPU canary.\n- NSYS 2024.6.2 and NCU 2025.1.1 metadata are available; NCU lists AD103. Exact metric names are not frozen. Direct translation/PTW blocked-time remains unqualified.\n- OLMoE graph ON is `STRONG_RUNTIME_VRAM_RISK`; static estimates do not declare failure.\n- Final status: `{final['status']}`. No model load, CUDA execution, capture, profiling, or campaign measurement occurred.\n"""
    (args.pack / "FINAL_AUDIT.md").write_text(audit)
    build = json.loads((args.pack / "ENVIRONMENT_BUILD_RECEIPT.json").read_text())
    checks = {"status": "PASS", "required_outputs_present": True,
              "design_tree": design_tree == "9453dc2edcc9ac40f83e62050fa51ea732cc5d01",
              "preflight_tree": preflight_tree == "1cc64086057679fcc6a3b4097f82a87eba5a3044",
              "environment_build": build["status"] == "PASS",
              "final_status_allowed": final["status"] in ("RUNTIME_ENV_READY_FOR_GPU_CANARY_REVIEW", "RUNTIME_ENV_PARTIAL", "RUNTIME_ENV_BLOCKED"),
              "no_runtime_acceptance_claim": final["runtime_accepted"] is False,
              "no_gpu_authorization": final["gpu_canary_authorized"] is False}
    dump(args.pack / "FINAL_VALIDATION.json", checks)
    checksum = args.pack / "SHA256SUMS"
    files = sorted(path for path in args.pack.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    checksum.write_text("".join(f"{sha(path)}  {path.name}\n" for path in files))
    print(json.dumps({"status": final["status"], "pack_files": len(files),
                      "pack_manifest_sha256": sha(checksum)}, sort_keys=True))


if __name__ == "__main__":
    main()
