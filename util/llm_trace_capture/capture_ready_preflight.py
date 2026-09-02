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
    "llama_tp_workload.py": "c784e8d0f99ef26aa34c2cfc5201fe463a1322d59f5b1a8f4b8269a7ff739ecb",
    "run_m4a_c.sh": "e81adb8e1da0c2d86cca0aee16d61b7e483feacf9e794d2d0530765e7d56199a",
    "copyback_m4a_bundle.sh": "c1e7c1dfc280312507d019b874a6c70170ffdb03763c1bce1ab8d2e865ec7c91",
    "bootstrap_route_e_nvbit.sh": "de78fcd105d809ff35e4819826435c821e74f7bc5cb50251291fec9f51be19f3",
    "build_nvbit_with_toolchain.sh": "070a842ec3e0e03f5a6e2a8281a96ab3c051d2f230163a9d6e0d6c351100a5ee",
    "classify_kernels.py": "a23c05ebd1b8494cb9a80d0d65ae153a1a76eeb0f1da98f4a21ef5b386983374",
    "run_generic_nvbit_smoke.sh": "a11341806c92113cb9be3b6b8ad31af36902569be89844240fbeb6a59abbf371",
    "tracer_tool.cu": "414bdeebebf807a1134a53079ed0b7eee47e7fb3eda72250da25b445f5876ab4",
}
LOCAL_SNAPSHOT_FILES = ("model.safetensors", "config.json", "generation_config.json", "tokenizer.json",
                        "tokenizer_config.json", "special_tokens_map.json")
MODEL_ID = "meta-llama/Llama-3.2-1B"


def command(*argv: str) -> tuple[int, str]:
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.returncode, result.stdout
    except FileNotFoundError:
        return 127, f"command not found: {argv[0]}\n"


def version_is_locked(text: str) -> bool:
    return bool(re.search(rf"release\s+{re.escape(CUDA_RELEASE)}(?:[,.\s]|$)", text, re.I))


def package_pin_matches(package: str, actual: str, pin: str) -> bool:
    """Accept PyTorch's cu126 local-version suffix; CUDA is checked separately."""
    return actual == pin or (package == "torch" and actual == f"{pin}+cu126")


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


def inspect_model_transport(revision: str) -> tuple[dict, list[str]]:
    """Validate local-snapshot identity without any network access or weight hashing."""
    local_raw, manifest_raw = os.environ.get("M4A_MODEL_LOCAL_PATH", ""), os.environ.get("M4A_MODEL_LOCAL_MANIFEST", "")
    if not local_raw:
        return {"transport": "HUGGING_FACE", "canonical_model_id": MODEL_ID, "frozen_revision": revision}, []
    root = Path(local_raw).expanduser().resolve(); details = {"transport": "LOCAL_SNAPSHOT", "local_path": str(root),
                                                               "canonical_model_id": MODEL_ID, "frozen_revision": revision}
    errors: list[str] = []
    if not root.is_dir(): errors.append(f"M4A_MODEL_LOCAL_PATH is not a directory: {root}")
    else:
        missing = [name for name in LOCAL_SNAPSHOT_FILES if not (root / name).is_file()]
        if missing: errors.append(f"local model snapshot is incomplete: {missing}")
    if not manifest_raw:
        errors.append("M4A_MODEL_LOCAL_MANIFEST is required with M4A_MODEL_LOCAL_PATH")
        return details, errors
    manifest_path = Path(manifest_raw).expanduser().resolve(); details["manifest_path"] = str(manifest_path)
    if not manifest_path.is_file():
        errors.append(f"M4A_MODEL_LOCAL_MANIFEST is not a file: {manifest_path}")
        return details, errors
    details["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    try:
        manifest = json.loads(manifest_path.read_text()); model = manifest["model"]
        file_rows = {row["path"]: row for row in manifest["files"]}
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        errors.append(f"invalid local model manifest: {error}")
        return details, errors
    if manifest.get("schema_version") != "m4a-local-model-snapshot-v1": errors.append("local model manifest schema mismatch")
    if model.get("canonical_id") != MODEL_ID or model.get("revision") != revision: errors.append("local model manifest identity mismatch")
    for name in LOCAL_SNAPSHOT_FILES:
        if not isinstance(file_rows.get(name), dict) or not isinstance(file_rows[name].get("sha256"), str):
            errors.append(f"local model manifest missing SHA256 for {name}")
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
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "snapshot"; root.mkdir(); revision = "c" * 40; rows = []
        for name in LOCAL_SNAPSHOT_FILES:
            payload = name.encode(); (root / name).write_bytes(payload)
            rows.append({"path": name, "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
        manifest = Path(directory) / "snapshot-manifest.json"
        manifest.write_text(json.dumps({"schema_version": "m4a-local-model-snapshot-v1",
                                        "model": {"canonical_id": MODEL_ID, "revision": revision}, "files": rows}))
        old_local, old_manifest = os.environ.get("M4A_MODEL_LOCAL_PATH"), os.environ.get("M4A_MODEL_LOCAL_MANIFEST")
        os.environ["M4A_MODEL_LOCAL_PATH"], os.environ["M4A_MODEL_LOCAL_MANIFEST"] = str(root), str(manifest)
        try:
            details, errors = inspect_model_transport(revision)
            assert not errors and details["transport"] == "LOCAL_SNAPSHOT" and details["manifest_sha256"]
        finally:
            if old_local is None: os.environ.pop("M4A_MODEL_LOCAL_PATH", None)
            else: os.environ["M4A_MODEL_LOCAL_PATH"] = old_local
            if old_manifest is None: os.environ.pop("M4A_MODEL_LOCAL_MANIFEST", None)
            else: os.environ["M4A_MODEL_LOCAL_MANIFEST"] = old_manifest


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
        if not package_pin_matches(package, versions[package], pin): errors.append(f"package pin mismatch: {package}={versions[package]} != {pin} or {pin}+cu126")
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
    model_transport, model_errors = inspect_model_transport(revision); errors += model_errors
    report = {"schema_version": "m4a-route-e-capture-ready-v2", "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "status": "PASS" if not errors else "BLOCKED", "errors": errors, "python": sys.version,
              "packages": versions, "torch_runtime_cuda": torch_runtime_cuda, "toolchain": toolchain,
              "locked_artifact_sha256": artifact_actual, "nvbit_sha256": NVBIT_SHA, "tracer": str(tracer),
              "postprocessor": str(post), "free_gib": free_gib, "hf_token_present": token_set,
              "model_revision_set": len(revision) == 40, "model_transport": model_transport}
    output = work / "capture-ready-preflight.json"; output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"{report['status']} report={output}")
    for error in errors: print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
