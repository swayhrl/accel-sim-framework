#!/usr/bin/env python3
"""Locked R21A pinned-package/runtime admission; no energy/force execution yet."""

import hashlib
import importlib.metadata as md
import json
import os
import subprocess
import traceback
from pathlib import Path


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    receipt = {"stage": "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1",
               "requested_model_id": "nequip.net:mir-group/NequIP-OAM-S:0.1",
               "model_package_sha256": sha(MODEL),
               "source_commits": {"nequip": "27d9d2182da918ab7be0017d8300e53278f5e00e",
                                  "OpenEquivariance": "dc9979099c65113adcc016977c5c60974f9ddafb"},
               "TF32": "OFF", "energy_forces_executed": False}
    try:
        import ase
        import e3nn
        import nequip
        import openequivariance as oeq
        import torch
        from nequip.model import ModelFromPackage

        torch.set_default_dtype(torch.float32)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.set_float32_matmul_precision("highest")
        receipt["packages"] = {name: md.version(name) for name in ("torch", "nequip", "openequivariance", "e3nn", "ase", "numpy")}
        receipt["python"] = os.sys.version
        receipt["torch_cuda_runtime"] = torch.version.cuda
        receipt["GPU_name"] = torch.cuda.get_device_name(0)
        receipt["GPU_capability"] = list(torch.cuda.get_device_capability(0))
        receipt["driver_line"] = subprocess.check_output(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True).strip()
        receipt["oeq_module_file"] = str(Path(oeq.__file__).resolve())
        model = ModelFromPackage(str(MODEL), compile_mode="eager")
        model.eval()
        receipt["loaded_model_class"] = f"{type(model).__module__}.{type(model).__qualname__}"
        receipt["loaded_model_training"] = bool(model.training)
        receipt["loaded_module_count"] = len(list(model.named_modules()))
        receipt["loaded_module_class_samples"] = [f"{n}:{type(m).__module__}.{type(m).__qualname__}" for n, m in list(model.named_modules())[:40]]
        receipt["loaded_parameter_count"] = sum(p.numel() for p in model.parameters())
        receipt["loaded_parameter_dtypes"] = sorted({str(p.dtype) for p in model.parameters()})
        receipt["actual_OAM_S_package_loaded"] = not model.training and receipt["loaded_parameter_count"] > 0
        receipt["status"] = "MODEL_RUNTIME_LOADED"
    except Exception as exc:
        receipt["status"] = "MODEL_RUNTIME_LOAD_FAILED"
        receipt["error_type"] = type(exc).__name__
        receipt["error"] = str(exc)
        receipt["traceback_tail"] = traceback.format_exc()[-8000:]
    (RAW / "RUNTIME_ADMISSION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: receipt.get(k) for k in ("status", "GPU_name", "GPU_capability", "torch_cuda_runtime", "loaded_model_class", "loaded_parameter_count", "error_type", "error")}, sort_keys=True), flush=True)
    if receipt["status"] != "MODEL_RUNTIME_LOADED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
