#!/usr/bin/env python3
"""Deterministic non-model CUDA runtime admission fixture for C16 U3."""
import hashlib
import json
import os
import sys

EXPECTED_UUID = "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"


def main() -> int:
    assert os.environ.get("CUDA_MODULE_LOADING") == "EAGER", "CUDA_MODULE_LOADING must be EAGER"
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == EXPECTED_UUID, "GPU UUID binding drift"
    assert os.environ.get("CUBLAS_WORKSPACE_CONFIG") == ":4096:8", "deterministic cuBLAS workspace missing"

    import torch

    assert torch.__version__ == "2.5.1+cu124", torch.__version__
    assert torch.version.cuda == "12.4", torch.version.cuda
    assert torch.cuda.is_available(), "CUDA unavailable"
    assert torch.cuda.device_count() == 1, torch.cuda.device_count()
    device = torch.device("cuda:0")
    properties = torch.cuda.get_device_properties(device)
    assert "RTX 4080" in properties.name, properties.name
    assert (properties.major, properties.minor) == (8, 9), (properties.major, properties.minor)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20260914)
    torch.cuda.manual_seed_all(20260914)

    x = torch.arange(4096, device=device, dtype=torch.float32)
    y = x * 0.25 + 7.0
    z = y - x * 0.25
    assert x.is_cuda and y.is_cuda and z.is_cuda
    assert torch.allclose(z, torch.full_like(z, 7.0), rtol=0.0, atol=0.0)

    left = torch.arange(128 * 128, device=device, dtype=torch.float32).reshape(128, 128) / 128.0
    right = torch.arange(128 * 128, device=device, dtype=torch.float32).reshape(128, 128).T / 64.0
    product = left @ right
    assert left.is_cuda and right.is_cuda and product.is_cuda
    torch.cuda.synchronize(device)
    checksum = float(product.sum().item())
    payload = {
        "status": "C16_U3_PYTORCH_CUDA_CANARY_PASS",
        "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
        "cublas_workspace_config": os.environ["CUBLAS_WORKSPACE_CONFIG"],
        "device": str(device),
        "device_name": properties.name,
        "compute_capability": f"{properties.major}.{properties.minor}",
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "elementwise_checksum": float(z.sum().item()),
        "gemm_checksum": checksum,
        "tensor_residency": "ALL_CUDA",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["result_sha256"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
