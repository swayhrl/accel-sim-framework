#!/usr/bin/env python3
"""Route-E post-bootstrap gate with explicit compiler/runtime provenance."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata as md
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PINS = {"torch": "2.6.0", "transformers": "4.51.3", "accelerate": "1.6.0", "safetensors": "0.5.3", "huggingface_hub": "0.30.2"}
NVBIT_SHA = "dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f"
CUDA_RELEASE = "12.6"
LOCKED_ARTIFACTS = {
    "run_llama_tp4_rank0.sh": "cc38edf0eda9b4498ce639145618770f44e417563799be26b1ac50af29380829",
    "rank0_nvbit_exec.sh": "02d34b01c44d9b11abe281addba7b2bda7488175305c42f9b246c5525ff8bbba",
    "llama_tp_workload.py": "a713f79c39bd0c9038d89f3960e561b258361effb2012fa358586e60cd8a48a1",
    "run_m4a_c.sh": "05dfc2d2b4cef8f66c636b916083735666e997f5c3bdf4cb6a52fad04ce217ec",
    "bootstrap_route_e_nvbit.sh": "b4b73aa9f3c66addb22f24e40059da7e1d36eacab3c14ea636b79d8785f958b7",
    "build_nvbit_with_toolchain.sh": "070a842ec3e0e03f5a6e2a8281a96ab3c051d2f230163a9d6e0d6c351100a5ee",
    "classify_kernels.py": "a23c05ebd1b8494cb9a80d0d65ae153a1a76eeb0f1da98f4a21ef5b386983374",
    "run_generic_nvbit_smoke.sh": "c1c9476258bed94133339b74191595693768b28af3874462e08644165d6ba520",
    "tracer_tool.cu": "414bdeebebf807a1134a53079ed0b7eee47e7fb3eda72250da25b445f5876ab4",
}


def command(*argv: str) -> tuple[int, str]:
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.returncode, result.stdout
    except FileNotFoundError:
        return 127, f"command not found: {argv[0]}\n"


def version_is_locked(text: str) -> bool:
    return bool(re.search(rf"release\s+{re.escape(CUDA_RELEASE)}(?:[,.\s]|$)", text, re.I))


def inspect_toolchain(cuda_home: Path) -> tuple[dict, list[str]]:
    requested = str(cuda_home)
    nvcc, ptxas = cuda_home / "bin/nvcc", cuda_home / "bin/ptxas"
    details = {"requested_cuda_home": requested, "selected_nvcc": str(nvcc), "selected_ptxas": str(ptxas),
               "path_nvcc": shutil.which("nvcc"), "path_ptxas": shutil.which("ptxas")}
    errors = []
    for label, path in (("nvcc", nvcc), ("ptxas", ptxas)):
        if not path.is_file() or not os.access(path, os.X_OK):
            errors.append(f"missing selected {label}: {path}")
            continue
        resolved = str(path.resolve()); details[f"selected_{label}"] = resolved
        rc, output = command(resolved, "--version"); details[f"{label}_version"] = output
        if rc: errors.append(f"selected {label} --version failed")
        elif not version_is_locked(output): errors.append(f"selected {label} is not locked CUDA {CUDA_RELEASE}: {output.strip()}")
    details["path_nvcc_disagrees"] = bool(details["path_nvcc"] and details.get("selected_nvcc") and Path(details["path_nvcc"]).resolve() != Path(details["selected_nvcc"]))
    details["path_ptxas_disagrees"] = bool(details["path_ptxas"] and details.get("selected_ptxas") and Path(details["path_ptxas"]).resolve() != Path(details["selected_ptxas"]))
    return details, errors


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); selected, contaminant = root / "cuda-12.6", root / "cuda-13.0"
        for toolkit, release in ((selected, "12.6"), (contaminant, "13.0")):
            (toolkit / "bin").mkdir(parents=True)
            for name in ("nvcc", "ptxas"):
                path = toolkit / "bin" / name
                path.write_text(f"#!/usr/bin/env bash\necho 'Cuda compilation tools, release {release}, V{release}.0'\n")
                path.chmod(0o755)
        old_path = os.environ.get("PATH", ""); os.environ["PATH"] = f"{contaminant / 'bin'}:{old_path}"
        try:
            info, errors = inspect_toolchain(selected)
            assert not errors and info["path_nvcc_disagrees"] and info["path_ptxas_disagrees"]
            _, missing = inspect_toolchain(root / "absent"); assert any("missing selected nvcc" in x for x in missing)
            _, mismatch = inspect_toolchain(contaminant); assert any("not locked CUDA 12.6" in x for x in mismatch)
        finally:
            os.environ["PATH"] = old_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-root", type=Path)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--cuda-home", type=Path)
    parser.add_argument("--minimum-free-gib", type=int, default=500)
    parser.add_argument("--required-gpu-count", type=int, default=4)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(); print("PASS capture-ready toolchain provenance self-test"); return 0
    if not args.framework_root or not args.work_root or not args.cuda_home:
        parser.error("--framework-root, --work-root, and --cuda-home are required unless --self-test")
    root, work, cuda_home = args.framework_root.resolve(), args.work_root.resolve(), args.cuda_home
    work.mkdir(parents=True, exist_ok=True); errors: list[str] = []
    if args.required_gpu_count != 4: errors.append("Route E requires required-gpu-count=4")
    if sys.version_info[:2] != (3, 10): errors.append(f"Python lock mismatch: {sys.version_info.major}.{sys.version_info.minor} != 3.10")
    for tool in ("python3", "nvidia-smi", "sha256sum", "tar"):
        if not shutil.which(tool): errors.append(f"missing command: {tool}")
    toolchain, toolchain_errors = inspect_toolchain(cuda_home); errors += toolchain_errors
    versions = {}
    for package, pin in PINS.items():
        try: versions[package] = md.version(package)
        except md.PackageNotFoundError: versions[package] = "MISSING"
        if versions[package] != pin: errors.append(f"package pin mismatch: {package}={versions[package]} != {pin}")
    try:
        import torch
        torch_runtime_cuda = torch.version.cuda
        if torch_runtime_cuda != CUDA_RELEASE: errors.append(f"PyTorch CUDA runtime mismatch: {torch_runtime_cuda} != {CUDA_RELEASE}")
    except Exception as error:
        torch_runtime_cuda = "UNAVAILABLE"; errors.append(f"cannot inspect torch.version.cuda: {error}")
    tracer = root / "util/tracer_nvbit/tracer_tool/tracer_tool.so"; post = root / "util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
    for artifact in (tracer, post):
        if not artifact.is_file(): errors.append(f"missing built artifact: {artifact}")
    marker = work / "bootstrap/nvbit-1.7.6.sha256"
    if not marker.is_file() or marker.read_text().strip().split()[0] != NVBIT_SHA: errors.append("missing/mismatched checksum-verified NVBit bootstrap marker")
    provenance = work / "bootstrap/toolchain-provenance.env"
    if not provenance.is_file(): errors.append("missing explicit toolchain bootstrap provenance")
    else:
        value = provenance.read_text()
        if f"selected_nvcc={toolchain.get('selected_nvcc')}" not in value or f"selected_ptxas={toolchain.get('selected_ptxas')}" not in value:
            errors.append("bootstrap toolchain provenance does not match selected toolkit")
    artifact_actual = {}
    for name, expected in LOCKED_ARTIFACTS.items():
        path = root / "util/llm_trace_capture" / name if name != "tracer_tool.cu" else root / "util/tracer_nvbit/tracer_tool/tracer_tool.cu"
        artifact_actual[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
        if artifact_actual[name] != expected: errors.append(f"locked artifact digest mismatch: {name}")
    free_gib = shutil.disk_usage(work).free // 1024**3
    if free_gib < args.minimum_free_gib: errors.append(f"free disk {free_gib} GiB < {args.minimum_free_gib} GiB")
    rc, gpus = command("nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader")
    if rc or len([x for x in gpus.splitlines() if x.strip()]) != 4 or any(x.strip() != "8.6" for x in gpus.splitlines() if x.strip()): errors.append("four visible SM86 GPUs unavailable")
    revision, token_set = os.environ.get("M4A_MODEL_REVISION", ""), bool(os.environ.get("HF_TOKEN"))
    if len(revision) != 40: errors.append("M4A_MODEL_REVISION immutable SHA is not set")
    report = {"schema_version": "m4a-route-e-capture-ready-v2", "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "status": "PASS" if not errors else "BLOCKED", "errors": errors, "python": sys.version,
              "packages": versions, "torch_runtime_cuda": torch_runtime_cuda, "toolchain": toolchain,
              "locked_artifact_sha256": artifact_actual, "nvbit_sha256": NVBIT_SHA, "tracer": str(tracer),
              "postprocessor": str(post), "free_gib": free_gib, "hf_token_present": token_set,
              "model_revision_set": len(revision) == 40}
    output = work / "capture-ready-preflight.json"; output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"{report['status']} report={output}")
    for error in errors: print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
