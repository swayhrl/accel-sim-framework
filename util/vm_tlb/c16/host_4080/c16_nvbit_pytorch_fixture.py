#!/usr/bin/env python3
"""Bounded non-model PyTorch CUDA fixtures used only for C16 NVBit U8."""
import argparse
import json
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", choices=("elementwise", "gemm"), required=True)
    args = parser.parse_args()
    assert os.environ.get("CUDA_MODULE_LOADING") == "EAGER"
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"
    assert os.environ.get("CUBLAS_WORKSPACE_CONFIG") == ":4096:8"
    import torch

    assert torch.cuda.is_available() and torch.cuda.device_count() == 1
    device = torch.device("cuda:0")
    torch.use_deterministic_algorithms(True)
    if args.operation == "elementwise":
        x = torch.arange(1 << 20, device=device, dtype=torch.float32)
        result = x * 0.125 + 3.0
        assert result.is_cuda
        checksum = float(result.sum().item())
    else:
        left = torch.arange(256 * 256, device=device, dtype=torch.float32).reshape(256, 256) / 256.0
        right = torch.arange(256 * 256, device=device, dtype=torch.float32).reshape(256, 256).T / 128.0
        result = left @ right
        assert result.is_cuda
        checksum = float(result.sum().item())
    torch.cuda.synchronize(device)
    print(json.dumps({"status": "C16_U8_PYTORCH_FIXTURE_PASS", "operation": args.operation,
                      "checksum": checksum, "device": str(device), "torch": torch.__version__}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
